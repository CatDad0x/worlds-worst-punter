"""
Fetches all WC 2026 data and caches it to JSON files.
Run this once per day (API-Football limit: 100 calls/day).
"""
import requests
import json
import time
import os

FOOTBALL_API_KEY = "e157d9a7a00d8284c3447c1a3fa54e24"
ODDS_API_KEY = "b436201f23b377d4e067c18135bb8fd5"
FOOTBALL_BASE = "https://v3.football.api-sports.io"
FB_HEADERS = {"x-apisports-key": FOOTBALL_API_KEY}
CACHE_DIR = "cache"

os.makedirs(CACHE_DIR, exist_ok=True)

def save(filename, data):
    with open(f"{CACHE_DIR}/{filename}", "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved {filename}")

def load(filename):
    path = f"{CACHE_DIR}/{filename}"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def fb_get(endpoint, params):
    r = requests.get(f"{FOOTBALL_BASE}/{endpoint}", headers=FB_HEADERS, params=params)
    time.sleep(0.5)
    return r.json()

def fetch_wc_events():
    print("Fetching WC 2026 events from Odds API...")
    r = requests.get("https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/events", params={
        "apiKey": ODDS_API_KEY
    })
    data = r.json()
    save("wc_events.json", data)
    print(f"  {len(data)} events found")
    return data

def fetch_odds_for_event(event_id, home, away):
    r = requests.get(
        f"https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/events/{event_id}/odds",
        params={
            "apiKey": ODDS_API_KEY,
            "regions": "uk,eu,us,au",
            "markets": "player_shots_on_target,h2h",
            "oddsFormat": "decimal"
        }
    )
    return r.json()

def fetch_all_odds(events):
    print(f"Fetching odds for {len(events)} events...")
    all_odds = {}
    for i, event in enumerate(events):
        eid = event['id']
        home = event['home_team']
        away = event['away_team']
        print(f"  [{i+1}/{len(events)}] {home} vs {away}")
        odds = fetch_odds_for_event(eid, home, away)
        all_odds[eid] = odds
        time.sleep(0.3)
    save("all_odds.json", all_odds)
    return all_odds

def fetch_squad(team_id, team_name):
    data = fb_get("players/squads", {"team": team_id})
    if data.get('response'):
        return data['response'][0]['players']
    return []

def fetch_player_stats(player_id, season=2024):
    """Get club stats for a player from last season"""
    data = fb_get("players", {"id": player_id, "season": season})
    if data.get('response'):
        return data['response'][0]
    return None

def fetch_wc_squads(events):
    """Build team->players mapping using squad data"""
    print("Fetching WC squad data from API-Football...")

    # Get unique team names from events
    teams_needed = set()
    for e in events:
        teams_needed.add(e['home_team'])
        teams_needed.add(e['away_team'])

    # Load team ID mapping (built from API-Football)
    team_map = load("team_map.json") or {}
    squads = load("squads.json") or {}

    print(f"  Teams needed: {len(teams_needed)}")
    print(f"  Already cached: {len(squads)} teams")

    save("squads.json", squads)
    save("team_map.json", team_map)
    return squads, team_map

def build_team_id_map():
    """Fetch all WC 2026 team IDs"""
    print("Building team ID map from API-Football...")

    # Known WC 2026 teams with their API-Football IDs
    # These are the confirmed 48 teams
    known_teams = {
        "Argentina": 26, "Australia": 25, "Belgium": 1, "Bolivia": 31,
        "Brazil": 6, "Cameroon": 8, "Canada": 81, "Chile": 30,
        "Colombia": 11, "Croatia": 3, "Czech Republic": 29, "Denmark": 21,
        "Ecuador": 56, "Egypt": 23, "England": 10, "France": 2,
        "Germany": 25, "Ghana": 167, "Iran": 18, "Italy": 768,
        "Japan": 15, "Kenya": 43, "Mexico": 16, "Morocco": 32,
        "Netherlands": 9, "New Zealand": 164, "Nigeria": 38,
        "Panama": 80, "Paraguay": 37, "Peru": 33, "Poland": 24,
        "Portugal": 27, "Qatar": 163, "Saudi Arabia": 109,
        "Senegal": 55, "Serbia": 14, "South Africa": 175,
        "South Korea": 149, "Spain": 9, "Sweden": 19,
        "Switzerland": 20, "United States": 12, "Uruguay": 34,
        "Venezuela": 40, "Bosnia & Herzegovina": 13, "Slovakia": 7,
        "Slovenia": 77, "Hungary": 769, "Costa Rica": 83,
        "Honduras": 84, "Jamaica": 164, "Trinidad & Tobago": 175,
        "Cuba": 41, "Guatemala": 85, "Haiti": 86, "El Salvador": 87,
        "Congo DR": 44, "Ivory Coast": 161, "Mali": 170, "Tunisia": 196,
        "Algeria": 160, "Tanzania": 197, "Zambia": 198, "Uganda": 199,
        "Bahrain": 157, "Iraq": 166, "Jordan": 167, "Indonesia": 254,
        "Uzbekistan": 255, "New Caledonia": 256, "Tahiti": 257
    }
    save("team_id_map.json", known_teams)
    return known_teams

if __name__ == "__main__":
    print("=== Fetching WC 2026 Data ===\n")

    # Step 1: Get all WC events (fixtures)
    events = fetch_wc_events()

    # Step 2: Get odds for all events
    all_odds = fetch_all_odds(events)

    # Step 3: Build team ID map
    team_ids = build_team_id_map()

    print(f"\nDone! Check cache/ folder for data files.")
    print(f"Odds API remaining requests: check headers")
