"""
Scrapes national team shooting stats from FBref.com (StatsBomb data).
FBref is free - no API key needed.

For each WC 2026 team, fetches player shooting stats from their
national team page: shots, shots on target, minutes played.
Covers multiple years of international fixtures.

Data URL pattern:
  https://fbref.com/en/squads/{team_id}/shooting/

Run: python3 scrape_fbref.py
Output: cache/fbref_stats.json
"""
import requests, json, os, time, re
from html.parser import HTMLParser

CACHE = "cache"
os.makedirs(CACHE, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# FBref national team IDs for WC 2026 teams
# These are the squad IDs used in FBref URLs
FBREF_TEAM_IDS = {
    "Argentina":           "f9fddd6e",
    "Australia":           "26c7d896",
    "Austria":             "fb08dbb3",
    "Belgium":             "fb09ae29",
    "Bosnia & Herzegovina":"f4bb6634",
    "Brazil":              "4e0b0a37",
    "Canada":              "70b5b5e3",
    "Cape Verde":          "2739f5ef",
    "Colombia":            "f4a6ab33",
    "Croatia":             "2589779b",
    "Czech Republic":      "e8c6f4d5",
    "DR Congo":            "3b6c4b9e",
    "Ecuador":             "8756e7cd",
    "Egypt":               "f6a9ee9b",
    "England":             "cce3e92c",
    "France":              "3ea84082",
    "Germany":             "adccbe82",
    "Ghana":               "38e19e63",
    "Haiti":               "edd0bbb8",
    "Iran":                "9b4a2f64",
    "Iraq":                "e1d48893",
    "Ivory Coast":         "d2c6a075",
    "Japan":               "21f90d17",
    "Jordan":              "7a2a6d5b",
    "Mexico":              "8d4af8e0",
    "Morocco":             "afc33984",
    "Netherlands":         "d1f8b78b",
    "New Zealand":         "0a52a757",
    "Norway":              "57b63c8c",
    "Panama":              "c4b5d6e7",
    "Paraguay":            "9a3d5f2b",
    "Portugal":            "fdc4b3c6",
    "Qatar":               "2b75cb2d",
    "Saudi Arabia":        "e22f0e4b",
    "Scotland":            "47c39f8c",
    "Senegal":             "db1c4d79",
    "South Africa":        "81ec3f6f",
    "South Korea":         "43bc72b2",
    "Spain":               "e00e7fd3",
    "Sweden":              "9e4a7b2c",
    "Switzerland":         "0cf2f2c0",
    "Tunisia":             "c4e35624",
    "Turkey":              "b5c68ead",
    "Uruguay":             "ece9b8ee",
    "USA":                 "7c21e445",
    "Uzbekistan":          "a3d5c7e9",
    "Algeria":             "5780b7e4",
    "Curaçao":             "c7b4e3f1",
    "South Korea":         "43bc72b2",
}

def fetch_team_shooting(team_name, fbref_id):
    """
    Fetch shooting stats table from FBref national team page.
    Returns list of player stat dicts.
    """
    url = f"https://fbref.com/en/squads/{fbref_id}/shooting/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code} for {team_name}")
            return []
        return parse_shooting_table(r.text, team_name)
    except Exception as e:
        print(f"  Error fetching {team_name}: {e}")
        return []

def parse_shooting_table(html, team_name):
    """Parse the shooting stats table from FBref HTML"""
    players = []

    # Find the shooting stats table
    # FBref uses id="stats_shooting" or similar
    table_pattern = r'<table[^>]*id="[^"]*shooting[^"]*"[^>]*>(.*?)</table>'
    match = re.search(table_pattern, html, re.DOTALL | re.IGNORECASE)

    if not match:
        # Try alternate table ID patterns
        table_pattern2 = r'<table[^>]*class="[^"]*stats_table[^"]*"[^>]*>(.*?)</table>'
        match = re.search(table_pattern2, html, re.DOTALL | re.IGNORECASE)

    if not match:
        print(f"  No shooting table found for {team_name}")
        return []

    table_html = match.group(1)

    # Find all rows
    row_pattern = r'<tr[^>]*>(.*?)</tr>'
    rows = re.findall(row_pattern, table_html, re.DOTALL)

    for row in rows:
        # Skip header rows
        if '<th' in row and 'data-stat="player"' not in row:
            continue

        # Extract player name
        player_match = re.search(r'data-stat="player"[^>]*>(?:<[^>]+>)*([^<]+)', row)
        if not player_match:
            continue
        player_name = player_match.group(1).strip()
        if not player_name or player_name in ('Player', ''):
            continue

        def get_stat(stat_name):
            pattern = rf'data-stat="{stat_name}"[^>]*>(?:<[^>]+>)*([^<]*)'
            m = re.search(pattern, row)
            if m:
                val = m.group(1).strip()
                try: return float(val) if val and val != '' else 0.0
                except: return 0.0
            return 0.0

        mins = get_stat("minutes")
        shots = get_stat("shots")
        sot = get_stat("shots_on_target")
        pos = ""
        pos_m = re.search(r'data-stat="position"[^>]*>(?:<[^>]+>)*([^<]*)', row)
        if pos_m: pos = pos_m.group(1).strip()

        if mins < 45: continue

        players.append({
            "name": player_name,
            "pos": pos,
            "minutes": mins,
            "shots": shots,
            "sot": sot,
            "shots_per90": round(shots / mins * 90, 3) if mins > 0 else 0,
            "sot_per90": round(sot / mins * 90, 3) if mins > 0 else 0,
        })

    return players

def scrape_all():
    """Scrape FBref for all WC 2026 teams"""
    existing = json.load(open(f"{CACHE}/fbref_stats.json")) if os.path.exists(f"{CACHE}/fbref_stats.json") else {}

    results = dict(existing)
    teams_done = set(existing.keys())

    for team_name, fbref_id in FBREF_TEAM_IDS.items():
        if team_name in teams_done:
            print(f"  [CACHED] {team_name}")
            continue

        print(f"  Fetching {team_name}...")
        players = fetch_team_shooting(team_name, fbref_id)
        results[team_name] = players

        if players:
            top = sorted(players, key=lambda x: x["sot_per90"], reverse=True)[:3]
            for p in top:
                print(f"    {p['name']}: {p['sot_per90']:.2f} SOT/90 ({p['minutes']:.0f} mins)")
        else:
            print(f"    No data")

        json.dump(results, open(f"{CACHE}/fbref_stats.json", "w"), indent=2)
        time.sleep(4)  # Be polite to FBref — don't hammer their servers

    return results

def test_single_team():
    """Quick test with England"""
    print("Testing FBref scrape with England...")
    players = fetch_team_shooting("England", FBREF_TEAM_IDS["England"])
    print(f"England: {len(players)} players")
    for p in sorted(players, key=lambda x: x["sot_per90"], reverse=True)[:8]:
        print(f"  {p['name']:25s} | {p['pos']:4s} | {p['minutes']:5.0f} mins | {p['shots_per90']:.2f} shots/90 | {p['sot_per90']:.2f} SOT/90")
    return players

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        test_single_team()
    else:
        print("Scraping FBref national team stats...")
        print("(4 second delay between requests to be polite)\n")
        results = scrape_all()
        teams_with_data = sum(1 for v in results.values() if v)
        print(f"\nDone: {teams_with_data}/{len(FBREF_TEAM_IDS)} teams with data")
        print("Run: python3 build_site.py to regenerate the website")
