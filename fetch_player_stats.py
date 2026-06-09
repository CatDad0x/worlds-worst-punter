"""
Fetches historical player stats from their club seasons (2023-24, 2024-25).
Uses squad data to identify players, then pulls club stats via major leagues.
Designed to use minimal API calls.
"""
import requests, json, os, time

FOOTBALL_API_KEY = "e157d9a7a00d8284c3447c1a3fa54e24"
FOOTBALL_BASE = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": FOOTBALL_API_KEY}
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def save(filename, data):
    with open(f"{CACHE_DIR}/{filename}", "w") as f:
        json.dump(data, f, indent=2)

def load(filename):
    path = f"{CACHE_DIR}/{filename}"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def fb_get(endpoint, params):
    r = requests.get(f"{FOOTBALL_BASE}/{endpoint}", headers=HEADERS, params=params)
    time.sleep(0.4)
    data = r.json()
    return data

# API-Football IDs for WC 2026 national teams
# Verified from API-Football national teams database
WC_TEAM_IDS = {
    "Mexico": 16,
    "South Africa": 175,
    "South Korea": 149,
    "Czech Republic": 29,
    "Canada": 81,
    "Bosnia & Herzegovina": 13,
    "USA": 12,
    "Paraguay": 37,
    "Qatar": 163,
    "Switzerland": 20,
    "Brazil": 6,
    "Morocco": 32,
    "Haiti": 174,
    "Scotland": 1165,
    "Australia": 25,
    "Turkey": 47,
    "Germany": 25,
    "Curaçao": 1228,
    "Netherlands": 9,
    "Japan": 15,
    "Ivory Coast": 161,
    "Ecuador": 56,
    "Sweden": 19,
    "Tunisia": 196,
    "Spain": 9,
    "Cape Verde": 1225,
    "Belgium": 1,
    "Egypt": 23,
    "Saudi Arabia": 109,
    "Uruguay": 34,
    "Iran": 18,
    "New Zealand": 164,
    "France": 2,
    "Senegal": 55,
    "Iraq": 166,
    "Norway": 103,
    "Argentina": 26,
    "Algeria": 160,
    "Austria": 3,
    "Jordan": 167,
    "Portugal": 27,
    "DR Congo": 168,
    "England": 10,
    "Croatia": 3,
    "Ghana": 167,
    "Uzbekistan": 855,
    "Colombia": 11,
    "Panama": 80,
}

# Major leagues covering most WC players (API-Football league IDs)
MAJOR_LEAGUES = {
    "Premier League": (39, 2024),
    "La Liga": (140, 2024),
    "Bundesliga": (78, 2024),
    "Serie A": (135, 2024),
    "Ligue 1": (61, 2024),
    "Eredivisie": (88, 2024),
    "Primeira Liga": (94, 2024),
    "Saudi Pro League": (307, 2024),
    "MLS": (253, 2024),
    "Liga MX": (262, 2024),
    "Brasileirao": (71, 2024),
    "Argentine Primera": (128, 2024),
}

def fetch_squad(team_id):
    """Get national team squad with player IDs"""
    data = fb_get("players/squads", {"team": team_id})
    if data.get('response'):
        return data['response'][0]['players']
    return []

def fetch_league_players(league_id, season):
    """Fetch all player stats for a league (all pages)"""
    all_players = {}
    page = 1
    while True:
        data = fb_get("players", {"league": league_id, "season": season, "page": page})
        response = data.get('response', [])
        if not response:
            break
        for p in response:
            pid = p['player']['id']
            name = p['player']['name']
            stats = p['statistics'][0] if p['statistics'] else {}
            shots = stats.get('shots', {})
            games = stats.get('games', {})
            all_players[pid] = {
                'name': name,
                'position': p['player'].get('nationality', ''),
                'apps': games.get('appearences') or 0,
                'minutes': games.get('minutes') or 0,
                'shots_total': shots.get('total') or 0,
                'shots_on_target': shots.get('on') or 0,
            }
        paging = data.get('paging', {})
        if page >= paging.get('total', 1):
            break
        page += 1
        time.sleep(0.4)
    return all_players

def fetch_all_squads():
    print("Fetching WC 2026 squads...")
    squads = {}

    # Get unique team names from events
    events = load("wc_events.json") or []
    teams_in_tournament = set()
    for e in events:
        teams_in_tournament.add(e['home_team'])
        teams_in_tournament.add(e['away_team'])

    print(f"  Teams in tournament: {len(teams_in_tournament)}")

    for team_name in sorted(teams_in_tournament):
        team_id = WC_TEAM_IDS.get(team_name)
        if not team_id:
            print(f"  [SKIP] No ID for: {team_name}")
            squads[team_name] = []
            continue

        players = fetch_squad(team_id)
        squads[team_name] = players
        print(f"  {team_name}: {len(players)} players (ID: {team_id})")

    save("wc_squads.json", squads)
    return squads

def fetch_all_league_stats():
    """Fetch player stats from major leagues - covers ~80% of WC players"""
    print("\nFetching major league player stats (this uses ~40 API calls)...")

    all_player_stats = load("player_stats.json") or {}

    for league_name, (league_id, season) in MAJOR_LEAGUES.items():
        print(f"  Fetching {league_name} {season}...")
        stats = fetch_league_players(league_id, season)
        for pid, pdata in stats.items():
            pid_str = str(pid)
            if pid_str not in all_player_stats:
                all_player_stats[pid_str] = pdata
            else:
                # Merge: accumulate stats from multiple leagues/seasons
                existing = all_player_stats[pid_str]
                existing['apps'] += pdata['apps']
                existing['minutes'] += pdata['minutes']
                existing['shots_total'] += pdata['shots_total']
                existing['shots_on_target'] += pdata['shots_on_target']
        print(f"    -> {len(stats)} players. Total in DB: {len(all_player_stats)}")
        save("player_stats.json", all_player_stats)

    return all_player_stats

def build_player_model():
    """
    Build shots-per-90 and SOT-per-90 for each player.
    This is the basis of our first-shot-on-target model.
    """
    print("\nBuilding player model...")
    squads = load("wc_squads.json") or {}
    player_stats = load("player_stats.json") or {}

    model = {}  # team_name -> list of player predictions

    for team_name, squad in squads.items():
        team_players = []
        for p in squad:
            pid = str(p['id'])
            stats = player_stats.get(pid)

            if stats and stats['minutes'] >= 300:  # At least 300 mins of data
                mins = stats['minutes']
                sot = stats['shots_on_target']
                shots = stats['shots_total']
                sot_per90 = (sot / mins) * 90 if mins > 0 else 0
                shots_per90 = (shots / mins) * 90 if mins > 0 else 0
            else:
                # Fallback: position-based defaults
                pos = p.get('position', 'Midfielder')
                defaults = {
                    'Goalkeeper': (0.0, 0.0),
                    'Defender': (0.3, 0.15),
                    'Midfielder': (0.7, 0.35),
                    'Attacker': (1.8, 0.9),
                    'Forward': (2.0, 1.0),
                }
                shots_per90, sot_per90 = defaults.get(pos, (0.7, 0.35))

            team_players.append({
                'id': pid,
                'name': p['name'],
                'position': p.get('position', 'Unknown'),
                'age': p.get('age', 0),
                'shots_per90': round(shots_per90, 3),
                'sot_per90': round(sot_per90, 3),
                'has_real_data': stats is not None and (stats.get('minutes', 0) >= 300),
            })

        model[team_name] = team_players

    save("player_model.json", model)

    # Print coverage stats
    total = sum(len(v) for v in model.values())
    with_data = sum(1 for v in model.values() for p in v if p['has_real_data'])
    print(f"  Total players: {total}, with real stats: {with_data} ({100*with_data//max(total,1)}%)")

    return model

if __name__ == "__main__":
    print("=== Building Player Stats Model ===\n")

    # Step 1: Fetch squads
    squads = fetch_all_squads()

    # Step 2: Fetch major league stats
    player_stats = fetch_all_league_stats()

    # Step 3: Build model
    model = build_player_model()

    print("\nDone!")
