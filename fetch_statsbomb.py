"""
Fetches WC 2018 + 2022 shot event data from StatsBomb open data (GitHub).
Free, structured JSON — no scraping, no API key needed.

Extracts per player:
  - Total shots on target
  - Minutes of each shot (to calculate early-game tendency)
  - % of shots in first 15 mins
  - Average minute of first SOT per game
  - National team they played for

Output: cache/statsbomb_shot_timing.json
"""
import requests, json, os, time
from collections import defaultdict

CACHE = "cache"
os.makedirs(CACHE, exist_ok=True)
BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

def fetch_json(url, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            if i == retries - 1: print(f"  Failed: {url} — {e}")
            time.sleep(1)
    return None

def get_matches(competition_id, season_id):
    url = f"{BASE}/matches/{competition_id}/{season_id}.json"
    return fetch_json(url) or []

def get_events(match_id):
    url = f"{BASE}/events/{match_id}.json"
    return fetch_json(url) or []

def process_match_shots(events, match_info):
    """Extract shot events from a match, return list of shot records"""
    shots = []
    home_team = match_info.get("home_team", {}).get("home_team_name", "")
    away_team = match_info.get("away_team", {}).get("away_team_name", "")

    for evt in events:
        if evt.get("type", {}).get("name") != "Shot":
            continue

        player = evt.get("player", {}).get("name", "")
        team = evt.get("team", {}).get("name", "")
        minute = evt.get("minute", 0)
        period = evt.get("period", 1)
        outcome = evt.get("shot", {}).get("outcome", {}).get("name", "")
        technique = evt.get("shot", {}).get("technique", {}).get("name", "")
        body_part = evt.get("shot", {}).get("body_part", {}).get("name", "")
        xg = evt.get("shot", {}).get("statsbomb_xg", 0) or 0

        # Only first half minute timing for first-SOT model
        # In period 2 onwards, shots don't count for "first SOT" market
        is_sot = outcome in ("Saved", "Goal", "Saved To Post", "Saved Off Target")

        shots.append({
            "player": player,
            "team": team,
            "minute": minute,
            "period": period,
            "is_sot": is_sot,
            "outcome": outcome,
            "technique": technique,
            "body_part": body_part,
            "xg": xg,
        })

    return shots

def build_player_timing_stats(all_shots_by_match):
    """
    For each player, calculate:
    - Total shots
    - Total SOT
    - % shots in first 15 mins (across all their matches)
    - Average minute of first shot per match
    - Average minute of first SOT per match
    - Early shot score (shots 0-15 / total shots)
    """
    # player_name -> team -> list of match shot data
    player_data = defaultdict(lambda: defaultdict(lambda: {
        "total_shots": 0, "total_sot": 0,
        "shots_0_15": 0, "sot_0_15": 0,
        "shots_0_10": 0, "sot_0_10": 0,
        "first_shot_minutes": [],  # minute of first shot per match
        "first_sot_minutes": [],   # minute of first SOT per match
        "matches_played": 0,
    }))

    for match_shots in all_shots_by_match:
        # Group shots by player for this match
        match_player_shots = defaultdict(list)
        for shot in match_shots:
            match_player_shots[(shot["player"], shot["team"])].append(shot)

        for (player, team), shots in match_player_shots.items():
            if not player:
                continue
            d = player_data[player][team]
            d["matches_played"] += 1

            # Sort by minute
            shots_sorted = sorted(shots, key=lambda s: s["minute"])
            sot_shots = [s for s in shots_sorted if s["is_sot"]]

            d["total_shots"] += len(shots)
            d["total_sot"] += len(sot_shots)
            d["shots_0_15"] += sum(1 for s in shots if s["minute"] <= 15 and s["period"] == 1)
            d["sot_0_15"]   += sum(1 for s in sot_shots if s["minute"] <= 15 and s["period"] == 1)
            d["shots_0_10"] += sum(1 for s in shots if s["minute"] <= 10 and s["period"] == 1)
            d["sot_0_10"]   += sum(1 for s in sot_shots if s["minute"] <= 10 and s["period"] == 1)

            if shots_sorted:
                d["first_shot_minutes"].append(shots_sorted[0]["minute"])
            if sot_shots:
                d["first_sot_minutes"].append(sot_shots[0]["minute"])

    # Flatten to summary stats
    result = {}
    for player, teams in player_data.items():
        for team, d in teams.items():
            ts = d["total_shots"]
            tsot = d["total_sot"]
            mp = max(d["matches_played"], 1)

            early_shot_pct = d["shots_0_15"] / ts if ts > 0 else 0
            early_sot_pct  = d["sot_0_15"] / tsot if tsot > 0 else 0

            avg_first_shot_min = (
                sum(d["first_shot_minutes"]) / len(d["first_shot_minutes"])
                if d["first_shot_minutes"] else None
            )
            avg_first_sot_min = (
                sum(d["first_sot_minutes"]) / len(d["first_sot_minutes"])
                if d["first_sot_minutes"] else None
            )

            result[f"{player}|{team}"] = {
                "player": player,
                "team": team,
                "matches": mp,
                "shots_per_game": round(ts / mp, 3),
                "sot_per_game": round(tsot / mp, 3),
                "early_shot_pct_15": round(early_shot_pct, 3),   # % shots in 0-15 mins
                "early_sot_pct_15":  round(early_sot_pct, 3),    # % SOT in 0-15 mins
                "shots_0_10_per_game": round(d["shots_0_10"] / mp, 3),
                "sot_0_10_per_game":   round(d["sot_0_10"] / mp, 3),
                "avg_first_shot_min": round(avg_first_shot_min, 1) if avg_first_shot_min else None,
                "avg_first_sot_min":  round(avg_first_sot_min, 1) if avg_first_sot_min else None,
            }
    return result

def run():
    # WC 2022 + WC 2018
    competitions = [
        (43, 106, "WC 2022"),
        (43, 3,   "WC 2018"),
    ]

    all_shots_by_match = []

    for comp_id, season_id, label in competitions:
        print(f"\nFetching {label} matches...")
        matches = get_matches(comp_id, season_id)
        print(f"  {len(matches)} matches found")

        for i, match in enumerate(matches):
            mid = match["match_id"]
            home = match.get("home_team", {}).get("home_team_name", "")
            away = match.get("away_team", {}).get("away_team_name", "")
            stage = match.get("competition_stage", {}).get("name", "")
            print(f"  [{i+1}/{len(matches)}] {home} vs {away} ({stage})")

            events = get_events(mid)
            if events:
                shots = process_match_shots(events, match)
                all_shots_by_match.append(shots)
                print(f"    {len(shots)} shots extracted")
            time.sleep(0.2)

    print(f"\nBuilding player timing stats from {len(all_shots_by_match)} matches...")
    stats = build_player_timing_stats(all_shots_by_match)
    print(f"  {len(stats)} player-team combinations")

    # Save raw
    json.dump(stats, open(f"{CACHE}/statsbomb_shot_timing.json", "w"), indent=2)

    # Print top early shooters (sorted by early SOT %)
    print("\nTop 20 early shooters (% SOT in first 15 mins, min 3 games):")
    ranked = [(k, v) for k, v in stats.items() if v["matches"] >= 2 and v.get("sot_per_game", 0) > 0]
    ranked.sort(key=lambda x: x[1]["early_sot_pct_15"], reverse=True)
    for k, v in ranked[:20]:
        print(f"  {v['player']:30s} ({v['team']:20s}) | {v['matches']}g | {v['early_sot_pct_15']:.0%} SOT in 0-15 | avg 1st SOT: {v['avg_first_sot_min']}min")

    return stats

if __name__ == "__main__":
    run()
