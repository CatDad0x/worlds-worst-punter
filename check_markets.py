import requests
import json

ODDS_API_KEY = "b436201f23b377d4e067c18135bb8fd5"
FOOTBALL_API_KEY = "e157d9a7a00d8284c3447c1a3fa54e24"
FOOTBALL_BASE = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": FOOTBALL_API_KEY}

def check_all_markets():
    """Check all available markets for WC on Odds API"""
    print("Checking available markets for WC...")
    r = requests.get("https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds", params={
        "apiKey": ODDS_API_KEY,
        "regions": "uk",
        "markets": "player_shots_on_target,player_first_goalscorer,player_anytime_goalscorer,player_shots",
        "oddsFormat": "decimal"
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    if isinstance(data, list) and data:
        game = data[0]
        print(f"Game: {game['home_team']} vs {game['away_team']}")
        for bm in game.get('bookmakers', []):
            print(f"  Bookmaker: {bm['title']}")
            for mkt in bm.get('markets', []):
                print(f"    Market: {mkt['key']}")
                for outcome in mkt.get('outcomes', [])[:3]:
                    print(f"      {outcome['name']}: {outcome['price']}")
    else:
        print("Response:", json.dumps(data, indent=2)[:500])

def get_player_stats_from_club(player_id, season=2024):
    """Get player shots stats from their club matches"""
    r = requests.get(f"{FOOTBALL_BASE}/players", headers=HEADERS, params={
        "id": player_id,
        "season": season
    })
    return r.json()

def search_player(name):
    """Search for a player"""
    r = requests.get(f"{FOOTBALL_BASE}/players", headers=HEADERS, params={
        "search": name,
        "league": 39,  # Premier League as example
        "season": 2024
    })
    data = r.json()
    for p in data.get('response', [])[:3]:
        player = p['player']
        stats = p['statistics'][0] if p['statistics'] else {}
        shots = stats.get('shots', {})
        games = stats.get('games', {})
        print(f"  {player['name']} (ID:{player['id']}) | Apps: {games.get('appearences')} | Shots: {shots.get('total')} | On target: {shots.get('on')}")
    return data

def get_wc_squads():
    """Get WC 2026 squads"""
    print("\nChecking WC 2026 squad data...")
    # Try getting squads for a known team
    r = requests.get(f"{FOOTBALL_BASE}/players/squads", headers=HEADERS, params={
        "team": 6  # Brazil
    })
    data = r.json()
    print(f"Status: {r.status_code}, Results: {data.get('results', 0)}")
    if data.get('response'):
        squad = data['response'][0]
        print(f"Team: {squad['team']['name']}")
        for p in squad['players'][:5]:
            print(f"  {p['name']} | Pos: {p['position']} | Age: {p['age']}")
    return data

def get_wc_teams():
    """Get all WC 2026 teams"""
    print("\nFetching WC 2026 teams...")
    r = requests.get(f"{FOOTBALL_BASE}/teams", headers=HEADERS, params={
        "league": 1,
        "season": 2026
    })
    data = r.json()
    print(f"Status: {r.status_code}, Teams: {data.get('results', 0)}")
    for t in data.get('response', [])[:10]:
        print(f"  {t['team']['name']} (ID: {t['team']['id']})")
    return data

if __name__ == "__main__":
    check_all_markets()
    get_wc_squads()
    get_wc_teams()
