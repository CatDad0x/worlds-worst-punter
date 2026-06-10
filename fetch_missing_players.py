"""
Fetches club/league stats for the ~400 bookmaker players with no data.
Uses API-Football Pro plan: search by surname + national team ID.
Run this once to fill gaps, then rebuild the site.
"""
import requests, json, os, time, sys, unicodedata, re

KEY  = "e157d9a7a00d8284c3447c1a3fa54e24"
BASE = "https://v3.football.api-sports.io"
H    = {"x-apisports-key": KEY}
CACHE = "cache"

# National team IDs in API-Football
NAT_TEAM_IDS = {
    "Algeria": 1532, "Argentina": 26, "Australia": 20, "Austria": 775,
    "Belgium": 1, "Bosnia & Herzegovina": 1113, "Brazil": 6, "Canada": 5529,
    "Cape Verde": 1533, "Colombia": 8, "Croatia": 3, "Curaçao": 5530,
    "Czech Republic": 770, "DR Congo": 1508, "Ecuador": 2382, "Egypt": 32,
    "England": 10, "France": 2, "Germany": 25, "Ghana": 1504, "Haiti": 2386,
    "Iran": 22, "Iraq": 1567, "Ivory Coast": 1501, "Japan": 12, "Jordan": 1548,
    "Mexico": 16, "Morocco": 31, "Netherlands": 1118, "New Zealand": 4673,
    "Norway": 1090, "Panama": 11, "Paraguay": 2380, "Portugal": 27,
    "Qatar": 1569, "Saudi Arabia": 23, "Scotland": 1108, "Senegal": 13,
    "South Africa": 1531, "South Korea": 17, "Spain": 9, "Sweden": 5,
    "Switzerland": 15, "Tunisia": 28, "Turkey": 777, "USA": 2384,
    "Uruguay": 7, "Uzbekistan": 1568,
}

def _norm(s):
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[-'\.]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def fb(endpoint, params):
    r = requests.get(f"{BASE}/{endpoint}", headers=H, params=params, timeout=15)
    time.sleep(0.25)
    return r.json()

def get_api_remaining():
    d = fb("status", {})
    used = d.get("response", {}).get("requests", {}).get("current", 0)
    return 7500 - used

def search_player(name, nat_team_id, seasons=(2026, 2025, 2024)):
    """Search API-Football for a player by surname + national team ID."""
    words = _norm(name).split()
    # Try longest words first as search terms (avoids short common words)
    search_terms = sorted(set(words), key=len, reverse=True)

    for term in search_terms[:3]:
        if len(term) < 4:
            continue
        for season in seasons:
            data = fb("players", {"search": term, "team": nat_team_id, "season": season})
            results = data.get("response", [])
            if results:
                # Find best match by name similarity
                best = None
                best_score = 0
                nl = set(_norm(name).split())
                for entry in results:
                    pname = _norm(entry["player"].get("name", ""))
                    score = len(nl & set(pname.split()))
                    if score > best_score:
                        best_score = score
                        best = entry
                if best and best_score >= 1:
                    return best, season
    return None, None

def extract_stats(entry, name, nat_team):
    """Pull shots/minutes from API-Football player entry."""
    pl = entry["player"]
    # Use best stats entry (most minutes)
    best_stats = None
    best_mins = 0
    for s in entry.get("statistics", []):
        mins = s.get("games", {}).get("minutes") or 0
        if mins > best_mins:
            best_mins = mins
            best_stats = s

    if not best_stats or best_mins < 90:
        return None

    shots_obj = best_stats.get("shots", {}) or {}
    games_obj = best_stats.get("games", {}) or {}
    mins = games_obj.get("minutes") or 0
    sot  = shots_obj.get("on") or 0
    sh   = shots_obj.get("total") or 0
    club = best_stats.get("team", {}).get("name", "")

    return {
        "name": name,
        "nat_team": nat_team,
        "api_name": pl.get("name", ""),
        "api_id": pl.get("id"),
        "club": club,
        "minutes": mins,
        "shots": sh,
        "sot": sot,
        "sot_per90": round(sot / mins * 90, 4) if mins > 0 else 0,
        "shots_per90": round(sh / mins * 90, 4) if mins > 0 else 0,
    }

def main():
    # Load existing data
    club_raw = json.load(open(f"{CACHE}/club_stats_raw.json")) if os.path.exists(f"{CACHE}/club_stats_raw.json") else {}
    nat_agg  = json.load(open(f"{CACHE}/national_stats_agg.json")) if os.path.exists(f"{CACHE}/national_stats_agg.json") else {}
    all_odds = json.load(open(f"{CACHE}/all_odds.json")) if os.path.exists(f"{CACHE}/all_odds.json") else {}
    events   = json.load(open(f"{CACHE}/wc_events.json")) if os.path.exists(f"{CACHE}/wc_events.json") else []

    # Add build_site to path for helper functions
    sys.path.insert(0, ".")
    import build_site as bs

    # Identify all bookmaker players missing data
    missing = {}
    for event in events:
        eid = event["id"]
        ev  = all_odds.get(eid, {})
        home, away = event["home_team"], event["away_team"]
        for bm in ev.get("bookmakers", []):
            for mkt in bm.get("markets", []):
                if mkt["key"] != "player_shots_on_target": continue
                for o in mkt["outcomes"]:
                    if o.get("point") == 0.5 and o.get("name") == "Over":
                        nm = o["description"]
                        if nm in missing:
                            continue
                        team = bs.find_player_team(nm)
                        if not team:
                            team = home  # best guess
                        nat = bs.get_nat_stats(nm, team, nat_agg)
                        club = bs.get_club_stats(nm, team, club_raw)
                        nat_ok  = nat and nat.get("sot_per90", 0) > 0
                        club_ok = club and club.get("sot_per90", 0) > 0
                        if not nat_ok and not club_ok:
                            missing[nm] = team

    print(f"Players missing data: {len(missing)}")
    print(f"API calls remaining: {get_api_remaining()}\n")

    found = 0
    not_found = []
    extras = {}  # pid -> stats dict, keyed by str(api_id) or name

    for i, (name, team) in enumerate(missing.items()):
        nat_id = NAT_TEAM_IDS.get(team)
        if not nat_id:
            not_found.append((name, team, "no team ID"))
            continue

        entry, season = search_player(name, nat_id)

        if entry:
            stats = extract_stats(entry, name, team)
            if stats:
                key = str(stats["api_id"]) if stats.get("api_id") else f"extra_{i}"
                extras[key] = stats
                found += 1
                print(f"  [{i+1}/{len(missing)}] FOUND {name} ({team}) → {stats['api_name']} | "
                      f"sot/90={stats['sot_per90']:.3f} mins={stats['minutes']} club={stats['club']}")
            else:
                not_found.append((name, team, "no usable stats"))
                print(f"  [{i+1}/{len(missing)}] LOW DATA {name} ({team})")
        else:
            not_found.append((name, team, "not found"))
            print(f"  [{i+1}/{len(missing)}] MISS {name} ({team})")

        # Save progress every 25 players
        if (i + 1) % 25 == 0:
            club_raw.update(extras)
            json.dump(club_raw, open(f"{CACHE}/club_stats_raw.json", "w"), indent=2)
            rem = get_api_remaining()
            print(f"\n  -- Progress saved. Found {found}/{i+1}. API remaining: {rem} --\n")
            if rem < 200:
                print("  API limit low — stopping early")
                break

    # Final save
    club_raw.update(extras)
    json.dump(club_raw, open(f"{CACHE}/club_stats_raw.json", "w"), indent=2)

    print(f"\n=== DONE ===")
    print(f"Found: {found}/{len(missing)}")
    print(f"Not found: {len(not_found)}")
    if not_found:
        print("\nStill missing (no API data exists for these players):")
        for name, team, reason in not_found[:20]:
            print(f"  {name} ({team}) — {reason}")

if __name__ == "__main__":
    main()
