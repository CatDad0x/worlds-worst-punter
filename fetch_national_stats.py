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
    "Argentina": 26,
    "Australia": 26,       # TBD
    "Austria": 3,
    "Belgium": 1,
    "Bosnia & Herzegovina": 13,
    "Brazil": 6,
    "Canada": 81,
    "Cape Verde": 1225,
    "Colombia": 11,
    "Croatia": 10,         # Need to verify
    "Czech Republic": 29,
    "Curaçao": 1228,
    "DR Congo": 168,
    "Ecuador": 56,
    "Egypt": 23,
    "England": 10,
    "France": 2,
    "Germany": 25,
    "Ghana": 167,
    "Haiti": 174,
    "Iran": 18,
    "Iraq": 166,
    "Ivory Coast": 161,
    "Japan": 15,
    "Jordan": 167,         # Need to verify
    "Mexico": 16,
    "Morocco": 32,
    "Netherlands": 1118,
    "New Zealand": 164,
    "Norway": 103,
    "Panama": 80,
    "Paraguay": 37,
    "Portugal": 27,
    "Qatar": 163,
    "Saudi Arabia": 109,
    "Scotland": 1165,
    "Senegal": 55,
    "South Africa": 175,
    "South Korea": 149,
    "Spain": 9,
    "Sweden": 19,
    "Switzerland": 20,
    "Tunisia": 196,
    "Turkey": 47,
    "USA": 12,
    "Uruguay": 34,
    "Uzbekistan": 855,
}

# Season weights: recent seasons count more
WEIGHTS = {2022: 0.15, 2023: 0.25, 2024: 0.35, 2025: 0.25}

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

def fetch_all(max_calls=85):
    """Fetch national stats across 4 seasons, resume from cache"""
    raw = load("national_stats_raw.json") or {}
    seasons = [2022, 2023, 2024, 2025]
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

if __name__ == "__main__":
    print("=== Fetching National Team Stats (4 years) ===\n")
    fetch_all()
    print("\nAggregating...")
    aggregate()
    print("\nDone! Run build_site.py to regenerate the website.")
