"""
Fetches 4 years of national team stats for all WC 2026 teams.
Aggregates 2022-2025 seasons, weighted by recency.
Club stats (from squads) used to supplement.

Run this script once per day — it saves progress and resumes automatically.
"""
import requests, json, os, time

KEY = "e157d9a7a00d8284c3447c1a3fa54e24"
BASE = "https://v3.football.api-sports.io"
H = {"x-apisports-key": KEY}
CACHE = "cache"
os.makedirs(CACHE, exist_ok=True)

def save(f, d): json.dump(d, open(f"{CACHE}/{f}", "w"), indent=2)
def load(f):
    p = f"{CACHE}/{f}"
    return json.load(open(p)) if os.path.exists(p) else None

# Verified API-Football national team IDs
# These are the actual IDs from API-Football's national team database
TEAM_IDS = {
    "Algeria": 160,
    # All IDs verified from API-Football WC 2026 league endpoint
    "Algeria": 1532,
    "Argentina": 26,
    "Australia": 20,
    "Austria": 775,
    "Belgium": 1,
    "Bosnia & Herzegovina": 1113,
    "Brazil": 6,
    "Canada": 5529,
    "Cape Verde": 1533,
    "Colombia": 8,
    "Croatia": 3,
    "Curaçao": 5530,
    "Czech Republic": 770,
    "DR Congo": 1508,
    "Ecuador": 2382,
    "Egypt": 32,
    "England": 10,
    "France": 2,
    "Germany": 25,
    "Ghana": 1504,
    "Haiti": 2386,
    "Iran": 22,
    "Iraq": 1567,
    "Ivory Coast": 1501,
    "Japan": 12,
    "Jordan": 1548,
    "Mexico": 16,
    "Morocco": 31,
    "Netherlands": 1118,
    "New Zealand": 4673,
    "Norway": 1090,
    "Panama": 11,
    "Paraguay": 2380,
    "Portugal": 27,
    "Qatar": 1569,
    "Saudi Arabia": 23,
    "Scotland": 1108,
    "Senegal": 13,
    "South Africa": 1531,
    "South Korea": 17,
    "Spain": 9,
    "Sweden": 5,
    "Switzerland": 15,
    "Tunisia": 28,
    "Turkey": 777,
    "USA": 2384,
    "Uruguay": 7,
    "Uzbekistan": 1568,
}

# Season weights: past 1 year focused (2025 = current year, 2024 = last year)
WEIGHTS = {2022: 0.02, 2023: 0.05, 2024: 0.18, 2025: 0.50, 2026: 0.25}

call_count = 0

def fb(endpoint, params):
    global call_count
    r = requests.get(f"{BASE}/{endpoint}", headers=H, params=params)
    call_count += 1
    time.sleep(0.4)
    return r.json()

def get_api_status():
    global call_count
    r = requests.get(f"{BASE}/status", headers=H)
    call_count += 1
    data = r.json()
    if isinstance(data, dict) and isinstance(data.get("response"), dict):
        return data["response"].get("requests", {}).get("current", 0)
    return 0

def fetch_team_season(team_id, season):
    """Fetch all pages of national team stats for one season"""
    all_players = {}
    for page in range(1, 5):  # Max 4 pages
        data = fb("players", {"team": team_id, "season": season, "page": page})
        response = data.get("response", [])
        if not response:
            break
        for p in response:
            pid = str(p["player"]["id"])
            pstats = p["statistics"][0] if p["statistics"] else {}
            shots = pstats.get("shots", {}) or {}
            games = pstats.get("games", {}) or {}
            mins = games.get("minutes") or 0
            if mins < 45:
                continue
            all_players[pid] = {
                "name": p["player"]["name"],
                "pos": games.get("position") or "Unknown",
                "apps": games.get("appearences") or 0,
                "minutes": mins,
                "shots": shots.get("total") or 0,
                "sot": shots.get("on") or 0,
            }
        paging = data.get("paging", {})
        if page >= paging.get("total", 1):
            break
    return all_players

def fetch_all(max_calls=7000):
    """Fetch national stats across 4 seasons, resume from cache"""
    raw = load("national_stats_raw.json") or {}
    seasons = [2022, 2023, 2024, 2025, 2026]
    used = get_api_status()
    budget = max_calls - used
    print(f"API calls used today: {used} | Budget remaining: {budget}")

    spent = 1  # count the status call
    for team_name, team_id in TEAM_IDS.items():
        if not team_id:
            continue
        if team_name not in raw:
            raw[team_name] = {}

        for season in seasons:
            key = str(season)
            if key in raw[team_name]:
                continue  # already fetched

            if spent >= budget - 5:
                print(f"\nStopping: budget used. Run again tomorrow.")
                save("national_stats_raw.json", raw)
                return raw

            players = fetch_team_season(team_id, season)
            raw[team_name][key] = players
            spent += 2  # approximate (1-2 pages per team per season)
            if players:
                print(f"  {team_name} {season}: {len(players)} players")
            save("national_stats_raw.json", raw)

    return raw

def aggregate():
    """
    Combine 4 seasons of national team data per player.
    Weight by recency. Returns per-team player stats.
    """
    raw = load("national_stats_raw.json") or {}
    agg = {}

    for team, seasons in raw.items():
        players = {}
        for season_str, season_players in seasons.items():
            season = int(season_str)
            w = WEIGHTS.get(season, 0.2)
            for pid, s in season_players.items():
                mins = s["minutes"]
                sot_per90 = (s["sot"] / mins * 90) if mins > 0 else 0
                shots_per90 = (s["shots"] / mins * 90) if mins > 0 else 0

                if pid not in players:
                    players[pid] = {
                        "name": s["name"], "pos": s["pos"],
                        "w_sot": 0, "w_shots": 0, "total_w": 0,
                        "total_mins": 0, "total_sot": 0, "total_shots": 0, "apps": 0,
                    }
                p = players[pid]
                p["w_sot"] += sot_per90 * w
                p["w_shots"] += shots_per90 * w
                p["total_w"] += w
                p["total_mins"] += mins
                p["total_sot"] += s["sot"]
                p["total_shots"] += s["shots"]
                p["apps"] += s.get("apps", 0)

        for pid, p in players.items():
            if p["total_w"] > 0:
                p["sot_per90"] = round(p["w_sot"] / p["total_w"], 4)
                p["shots_per90"] = round(p["w_shots"] / p["total_w"], 4)

        if players:
            agg[team] = players

    save("national_stats_agg.json", agg)
    total = sum(len(v) for v in agg.values())
    print(f"Aggregated: {len(agg)} teams, {total} players")
    return agg

def fetch_club_stats():
    """
    Fetch club stats (2024-25 season) for all WC squad players.
    Uses player IDs from wc_squads.json.
    Blends with national stats: 60% national, 40% club.
    """
    import json as _json
    squads = _json.load(open(f"{CACHE}/wc_squads.json")) if os.path.exists(f"{CACHE}/wc_squads.json") else {}
    existing = _json.load(open(f"{CACHE}/club_stats_raw.json")) if os.path.exists(f"{CACHE}/club_stats_raw.json") else {}

    # Collect all unique player IDs
    all_players = {}
    for team_name, squad in squads.items():
        for p in squad:
            pid = str(p["id"])
            if pid not in all_players:
                all_players[pid] = {"name": p["name"], "team": team_name}

    print(f"Fetching club stats for {len(all_players)} players (2025+2026 seasons)...")
    fetched = 0
    for pid, info in all_players.items():
        if pid in existing:
            continue
        if get_api_status() < 50:
            print("  API limit approaching, stopping")
            break

        # Try 2026 first (current season), fall back to 2025
        data = fb("players", {"id": pid, "season": 2026})
        if not data.get("response"):
            data = fb("players", {"id": pid, "season": 2025})
        resp = data.get("response", [])
        if resp:
            p = resp[0]
            stats = p["statistics"][0] if p["statistics"] else {}
            shots = stats.get("shots", {}) or {}
            games = stats.get("games", {}) or {}
            mins = games.get("minutes") or 0
            existing[pid] = {
                "name": info["name"],
                "nat_team": info["team"],
                "club": stats.get("team", {}).get("name", "") if stats else "",
                "minutes": mins,
                "shots": shots.get("total") or 0,
                "sot": shots.get("on") or 0,
                "sot_per90": round((shots.get("on") or 0) / mins * 90, 4) if mins > 0 else 0,
                "shots_per90": round((shots.get("total") or 0) / mins * 90, 4) if mins > 0 else 0,
            }
        else:
            existing[pid] = {"name": info["name"], "nat_team": info["team"], "minutes": 0, "sot": 0, "sot_per90": 0}
        fetched += 1
        if fetched % 50 == 0:
            print(f"  ...{fetched}/{len(all_players)} players fetched")
            save("club_stats_raw.json", existing)
        time.sleep(0.15)

    save("club_stats_raw.json", existing)
    with_data = sum(1 for v in existing.values() if v.get("minutes", 0) > 0)
    print(f"Club stats: {len(existing)} players total, {with_data} with minutes played")
    return existing


def merge_club_and_national():
    """
    Merge club stats into national stats aggregation.
    For each player: final_sot_per90 = 0.6 * national + 0.4 * club
    """
    import json as _json
    nat_agg = _json.load(open(f"{CACHE}/national_stats_agg.json"))
    club_raw = _json.load(open(f"{CACHE}/club_stats_raw.json")) if os.path.exists(f"{CACHE}/club_stats_raw.json") else {}

    # Build club lookup: player_name_lower -> club stats
    club_by_name = {}
    for pid, cs in club_raw.items():
        name = cs.get("name", "").lower()
        if name and cs.get("minutes", 0) >= 200:
            club_by_name[name] = cs

    merged = 0
    for team, players in nat_agg.items():
        for pid, p in players.items():
            pname = p.get("name", "").lower()
            club = club_by_name.get(pname)
            if club and club.get("sot_per90", 0) > 0:
                nat_sot = p.get("sot_per90", 0)
                club_sot = club["sot_per90"]
                # 60% national (national team role is primary), 40% club (recent form)
                p["sot_per90"] = round(0.60 * nat_sot + 0.40 * club_sot, 4)
                p["club_sot_per90"] = club_sot
                p["has_club"] = True
                merged += 1
            else:
                p["has_club"] = False

    save("national_stats_agg.json", nat_agg)
    print(f"Merged club stats for {merged} players")
    return nat_agg


if __name__ == "__main__":
    print("=== Fetching Stats (Past 1 Year: Club + National) ===\n")
    fetch_all()
    print("\nFetching club stats...")
    fetch_club_stats()
    print("\nAggregating national stats...")
    aggregate()
    print("\nMerging club + national...")
    merge_club_and_national()
    print("\nDone! Run build_site.py to regenerate the website.")
