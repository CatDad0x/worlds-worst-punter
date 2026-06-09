import requests
import json

FOOTBALL_API_KEY = "e157d9a7a00d8284c3447c1a3fa54e24"
ODDS_API_KEY = "b436201f23b377d4e067c18135bb8fd5"

FOOTBALL_BASE = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": FOOTBALL_API_KEY}

def get_wc_fixtures():
    print("Fetching WC 2026 fixtures...")
    r = requests.get(f"{FOOTBALL_BASE}/fixtures", headers=HEADERS, params={
        "league": 1,
        "season": 2026,
    })
    data = r.json()
    print(f"Total fixtures: {data.get('results', 0)}")
    for f in data.get('response', [])[:5]:
        fixture = f['fixture']
        teams = f['teams']
        print(f"  {fixture['date'][:10]} | {teams['home']['name']} vs {teams['away']['name']} | Round: {f['league']['round']}")
    return data

def get_wc_odds():
    print("\nFetching WC 2026 odds markets...")
    r = requests.get("https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds", params={
        "apiKey": ODDS_API_KEY,
        "regions": "uk",
        "markets": "h2h",
        "oddsFormat": "decimal"
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    if isinstance(data, list):
        print(f"Games with odds: {len(data)}")
        for g in data[:3]:
            print(f"  {g['home_team']} vs {g['away_team']} | {g['commence_time'][:10]}")
            for bm in g.get('bookmakers', [])[:1]:
                print(f"    Bookmaker: {bm['title']}")
                for mkt in bm.get('markets', []):
                    print(f"    Market: {mkt['key']}")
    else:
        print("Response:", json.dumps(data, indent=2))
    return data

def check_player_stats_sample():
    """Check player shot stats for a WC team"""
    print("\nFetching player stats for Brazil in WC 2026...")
    r = requests.get(f"{FOOTBALL_BASE}/players", headers=HEADERS, params={
        "league": 1,
        "season": 2026,
        "team": 6  # Brazil
    })
    data = r.json()
    print(f"Status: {r.status_code}, Results: {data.get('results', 0)}")
    for p in data.get('response', [])[:5]:
        player = p['player']
        stats = p['statistics'][0] if p['statistics'] else {}
        shots = stats.get('shots', {})
        print(f"  {player['name']} | Shots total: {shots.get('total')} | On target: {shots.get('on')}")
    return data

if __name__ == "__main__":
    fixtures = get_wc_fixtures()
    odds = get_wc_odds()
    check_player_stats_sample()
