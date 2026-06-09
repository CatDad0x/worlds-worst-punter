"""
Builds the WC 2026 First Shot On Target Edge Finder website.
UI matches the design spec exactly.
"""
import json, math, os
from datetime import datetime, timezone

CACHE = "cache"

def load(f):
    p = f"{CACHE}/{f}"
    return json.load(open(p)) if os.path.exists(p) else {}

POS_TIMING = {
    "Attacker": 1.18, "Forward": 1.18,
    "Midfielder": 1.0, "Defender": 0.80,
    "Goalkeeper": 0.20, "Unknown": 1.0,
}

# Known set-piece / free kick specialists per national team
# These players get a +12% boost — FK takers get early direct shots
FK_SPECIALISTS = {
    "Trent Alexander-Arnold", "Phil Foden", "James Maddison",
    "Antoine Griezmann", "Kylian Mbappé", "Ousmane Dembélé",
    "Bruno Fernandes", "Cristiano Ronaldo", "Bernardo Silva",
    "Lionel Messi", "Rodrigo De Paul", "Angel Di Maria",
    "Neymar", "Casemiro", "Lucas Paquetá",
    "Florian Wirtz", "Kai Havertz", "Jamal Musiala",
    "Kevin De Bruyne", "Yannick Carrasco",
    "Heung-Min Son", "Lee Kang-in",
    "Takumi Minamino", "Ritsu Doan",
    "Hakim Ziyech", "Sofiane Boufal",
    "Christian Pulisic", "Weston McKennie",
    "Federico Valverde", "Luis Suárez", "Darwin Núñez",
    "James Rodríguez", "Luis Díaz",
    "Enner Valencia", "Moisés Caicedo",
    "Luka Modrić", "Ivan Perišić",
    "Granit Xhaka", "Xherdan Shaqiri",
    "Martin Ødegaard", "Erling Haaland",
    "Emil Forsberg", "Dejan Kulusevski",
    "Hakan Çalhanoğlu", "Arda Güler",
    "Patrik Schick", "Tomáš Souček",
    "Memphis Depay", "Frenkie de Jong",
    "Mehdi Taremi", "Sardar Azmoun",
    "Saleh Al-Shehri", "Firas Al-Buraikan",
    "Jonathan David", "Tajon Buchanan",
    "Hirving Lozano", "Alexis Vega",
}

COUNTRY_FLAGS = {
    "Mexico":"🇲🇽","South Africa":"🇿🇦","South Korea":"🇰🇷","Czech Republic":"🇨🇿",
    "Canada":"🇨🇦","Bosnia & Herzegovina":"🇧🇦","USA":"🇺🇸","Paraguay":"🇵🇾",
    "Qatar":"🇶🇦","Switzerland":"🇨🇭","Brazil":"🇧🇷","Morocco":"🇲🇦",
    "Haiti":"🇭🇹","Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","Australia":"🇦🇺","Turkey":"🇹🇷",
    "Germany":"🇩🇪","Curaçao":"🇨🇼","Netherlands":"🇳🇱","Japan":"🇯🇵",
    "Ivory Coast":"🇨🇮","Ecuador":"🇪🇨","Sweden":"🇸🇪","Tunisia":"🇹🇳",
    "Spain":"🇪🇸","Cape Verde":"🇨🇻","Belgium":"🇧🇪","Egypt":"🇪🇬",
    "Saudi Arabia":"🇸🇦","Uruguay":"🇺🇾","Iran":"🇮🇷","New Zealand":"🇳🇿",
    "France":"🇫🇷","Senegal":"🇸🇳","Iraq":"🇮🇶","Norway":"🇳🇴",
    "Argentina":"🇦🇷","Algeria":"🇩🇿","Austria":"🇦🇹","Jordan":"🇯🇴",
    "Portugal":"🇵🇹","DR Congo":"🇨🇩","England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","Croatia":"🇭🇷",
    "Ghana":"🇬🇭","Uzbekistan":"🇺🇿","Colombia":"🇨🇴","Panama":"🇵🇦",
}

TEAM_ABBR = {
    "Mexico":"MEX","South Africa":"RSA","South Korea":"KOR","Czech Republic":"CZE",
    "Canada":"CAN","Bosnia & Herzegovina":"BIH","USA":"USA","Paraguay":"PAR",
    "Qatar":"QAT","Switzerland":"SUI","Brazil":"BRA","Morocco":"MAR",
    "Haiti":"HAI","Scotland":"SCO","Australia":"AUS","Turkey":"TUR",
    "Germany":"GER","Curaçao":"CUW","Netherlands":"NED","Japan":"JPN",
    "Ivory Coast":"CIV","Ecuador":"ECU","Sweden":"SWE","Tunisia":"TUN",
    "Spain":"ESP","Cape Verde":"CPV","Belgium":"BEL","Egypt":"EGY",
    "Saudi Arabia":"KSA","Uruguay":"URU","Iran":"IRN","New Zealand":"NZL",
    "France":"FRA","Senegal":"SEN","Iraq":"IRQ","Norway":"NOR",
    "Argentina":"ARG","Algeria":"ALG","Austria":"AUT","Jordan":"JOR",
    "Portugal":"POR","DR Congo":"COD","England":"ENG","Croatia":"CRO",
    "Ghana":"GHA","Uzbekistan":"UZB","Colombia":"COL","Panama":"PAN",
}

BM_STYLES = {
    "William Hill": '<span class="bm wh">William <strong>HILL</strong></span>',
    "Unibet":       '<span class="bm un">UNIBET<span class="un-dots">••••</span></span>',
    "Paddy Power":  '<span class="bm pp">PADDY POWER.</span>',
    "LeoVegas":     '<span class="bm lv">LeoVegas</span>',
    "Betfair":      '<span class="bm bf">betfair</span>',
}

def bm_html(name):
    return BM_STYLES.get(name, f'<span class="bm generic">{name}</span>')

def implied_lambda(price):
    p = min(1 / price, 0.9999)
    return -math.log(1 - p)

def avatar_color(name):
    colors = ["#3b82f6","#10b981","#8b5cf6","#f59e0b","#ef4444","#06b6d4","#ec4899","#84cc16"]
    return colors[hash(name) % len(colors)]

def initials(name):
    parts = name.split()
    if len(parts) >= 2:
        return parts[0][0].upper() + parts[-1][0].upper()
    return name[:2].upper()

def get_squad_pos(name, team, squads):
    squad = squads.get(team, [])
    nl = name.lower()
    for p in squad:
        if p["name"].lower() == nl or nl in p["name"].lower() or p["name"].lower() in nl:
            return p.get("position", "Unknown")
    return "Unknown"

def get_nat_stats(name, team, nat_agg):
    team_data = nat_agg.get(team, {})
    nl = name.lower()
    for pid, s in team_data.items():
        sname = s.get("name", "").lower()
        if sname == nl or nl in sname or sname in nl:
            return s
    return None

def confidence(has_nat, edge):
    if has_nat and abs(edge) >= 1.0: return "High"
    if has_nat or abs(edge) >= 0.5:  return "Medium"
    return "Low"

def build_predictions(event_odds, home, away, nat_agg, squads):
    bookie_data = {}
    for bm in event_odds.get("bookmakers", []):
        for mkt in bm.get("markets", []):
            if mkt["key"] != "player_shots_on_target": continue
            for o in mkt["outcomes"]:
                if o.get("point") == 0.5 and o.get("name") == "Over":
                    nm = o["description"]
                    pr = o["price"]
                    if nm not in bookie_data or pr < bookie_data[nm]["price"]:
                        bookie_data[nm] = {"price": pr, "bm": bm["title"]}

    if not bookie_data: return []

    players = []
    for name, bi in bookie_data.items():
        bm_lam = implied_lambda(bi["price"])
        nat = get_nat_stats(name, home, nat_agg) or get_nat_stats(name, away, nat_agg)
        pos = (nat.get("pos","Unknown") if nat else None) or get_squad_pos(name, home, squads) or get_squad_pos(name, away, squads) or "Unknown"

        if nat and nat.get("sot_per90", 0) > 0:
            nat_lam = max(nat["sot_per90"], 0.001)
            comb_lam = 0.60 * nat_lam + 0.40 * bm_lam
            has_nat = True
            nat_apps = nat.get("apps", 0)
            nat_sot = nat.get("sot_per90", 0)
        else:
            comb_lam = bm_lam
            has_nat = False
            nat_apps = nat_sot = None

        timing = POS_TIMING.get(pos, 1.0)
        fk_boost = 1.12 if name in FK_SPECIALISTS else 1.0
        model_lam = comb_lam * timing * fk_boost
        is_fk = name in FK_SPECIALISTS

        # Determine team — only assign if we can positively confirm, else leave blank
        team = ""
        nl = name.lower()
        # Check home squad data
        for p2 in squads.get(home, []):
            if nl == p2["name"].lower() or nl in p2["name"].lower() or p2["name"].lower() in nl:
                team = home; break
        # Check away squad data
        if not team:
            for p2 in squads.get(away, []):
                if nl == p2["name"].lower() or nl in p2["name"].lower() or p2["name"].lower() in nl:
                    team = away; break
        # Fall back to nat stats
        if not team:
            if get_nat_stats(name, home, nat_agg): team = home
            elif get_nat_stats(name, away, nat_agg): team = away

        players.append({
            "name": name, "pos": pos, "price": bi["price"], "bm": bi["bm"],
            "bm_lam": bm_lam, "model_lam": model_lam, "has_nat": has_nat,
            "nat_apps": nat_apps, "nat_sot": nat_sot, "is_fk": is_fk,
            "team": team,
        })

    if not players: return []
    tb = sum(p["bm_lam"] for p in players)
    tm = sum(p["model_lam"] for p in players)
    for p in players:
        p["bm_pct"]    = round(p["bm_lam"]    / tb * 100, 1) if tb > 0 else 0
        p["model_pct"] = round(p["model_lam"] / tm * 100, 1) if tm > 0 else 0
        p["edge"]      = round(p["model_pct"] - p["bm_pct"], 1)
        p["conf"]      = confidence(p["has_nat"], p["edge"])

    players.sort(key=lambda x: x["model_pct"], reverse=True)
    return players

def edge_pill(edge):
    if edge >= 1.5:  cls,lbl = "e-strong-val", f"+{edge}% Strong"
    elif edge >= 0.5:cls,lbl = "e-slight-val", f"+{edge}% Slight"
    elif edge <= -1.5:cls,lbl= "e-strong-fad", f"{edge}% Fade"
    elif edge <= -0.5:cls,lbl= "e-slight-fad", f"{edge}% Slight"
    else:             cls,lbl = "e-neutral",    "Neutral"
    return f'<span class="epill {cls}">{lbl}</span>'

def conf_badge(c):
    cls = {"High":"conf-hi","Medium":"conf-med","Low":"conf-lo"}.get(c,"conf-lo")
    icon = {"High":"✦","Medium":"◉","Low":"○"}.get(c,"○")
    return f'<span class="cbadge {cls}">{icon} {c}</span>'

def fmt_date(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z","+00:00"))
        return dt.strftime("%a %d %b · %H:%M UTC")
    except: return iso[:10]

def fmt_date_short(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z","+00:00"))
        return dt.strftime("%a %d %b")
    except: return iso[:10]

def fmt_time(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z","+00:00"))
        return dt.strftime("%H:%M")
    except: return ""

def best_edges_rows(all_games):
    candidates = []
    for g in all_games:
        if not g["has_data"]: continue
        for p in g["players"][:5]:
            if p["edge"] > 0:
                candidates.append({**p, "home": g["home"], "away": g["away"], "date_short": g["date_short"], "time": g["time"]})
    candidates.sort(key=lambda x: x["edge"], reverse=True)
    rows = []
    for i, p in enumerate(candidates[:5]):
        ha = TEAM_ABBR.get(p["home"], p["home"][:3].upper())
        aa = TEAM_ABBR.get(p["away"], p["away"][:3].upper())
        flag = COUNTRY_FLAGS.get(p["home"], "") # rough guess
        col = avatar_color(p["name"])
        ini = initials(p["name"])
        rows.append(f"""            <tr class="be-row">
              <td><span class="rank-circle">{i+1}</span></td>
              <td>
                <div class="be-player">
                  <div class="avatar" style="background:{col}">{ini}</div>
                  <div>
                    <div class="be-name">{p["name"]} {"<span class='fk-tag'>FK</span>" if p.get("is_fk") else ""}</div>
                    <div class="be-country">{COUNTRY_FLAGS.get(p.get("team", p["home"]),"")} {p.get("team", p["home"])}</div>
                  </div>
                </div>
              </td>
              <td>
                <div class="be-match">{ha} vs {aa}</div>
                <div class="be-date">{p["date_short"]} · {p["time"]}</div>
              </td>
              <td class="td-model">{p["model_pct"]}%</td>
              <td class="td-bm">{p["bm_pct"]}%</td>
              <td>{edge_pill(p["edge"])}</td>
              <td><span class="odds-val">{p["price"]:.2f}</span> {bm_html(p["bm"])}</td>
              <td>{conf_badge(p["conf"])}</td>
            </tr>""")
    return "\n".join(rows)

def match_player_rows(players):
    if not players:
        return '<tr><td colspan="7" class="no-data">Odds not yet available — check back closer to kick-off</td></tr>'
    medals = ["🥇","🥈","🥉","",""]
    rows = []
    for i, p in enumerate(players[:5]):
        med = f'<span class="medal">{medals[i]}</span>' if medals[i] else f'<span class="rank-sm">{i+1}</span>'
        rows.append(f"""              <tr>
                <td>{med}</td>
                <td class="td-pname"><span class="p-flag">{COUNTRY_FLAGS.get(p.get("team",""),"")}</span> {p["name"]} {"<span class='fk-tag'>FK</span>" if p.get("is_fk") else ""}</td>
                <td class="td-model">{p["model_pct"]}%</td>
                <td class="td-bm">{p["bm_pct"]}%</td>
                <td>{edge_pill(p["edge"])}</td>
                <td><span class="odds-val">{p["price"]:.2f}</span> {bm_html(p["bm"])}</td>
                <td>{conf_badge(p["conf"])}</td>
              </tr>""")
    return "\n".join(rows)

def match_cards(games):
    cards = []
    for g in games:
        uid = g["id"][:8]
        hf = COUNTRY_FLAGS.get(g["home"],"🏳")
        af = COUNTRY_FLAGS.get(g["away"],"🏳")
        has = g["has_data"]
        nat_c = g["nat_count"]
        badge = '<span class="mbadge nat-badge">★ Intl data</span>' if nat_c > 0 else ('<span class="mbadge bk-badge">Bookie-only</span>' if has else '<span class="mbadge tbc-badge">Odds TBC</span>')
        dim = "" if has else " card-dim"

        cards.append(f"""    <div class="mcard{dim}" id="mc-{uid}">
      <div class="mcard-header" onclick="tog('{uid}')">
        <div class="mcard-left">
          <span class="mflag">{hf}</span>
          <span class="mteam">{g["home"]}</span>
          <span class="mvs">vs</span>
          <span class="mteam">{g["away"]}</span>
          <span class="mflag">{af}</span>
          {badge}
        </div>
        <div class="mcard-right">
          <span class="mdate">{g["date_fmt"]}</span>
          <span class="mchev" id="chev-{uid}">▾</span>
        </div>
      </div>
      <div class="mcard-body" id="mb-{uid}">
        <table class="mtable">
          <thead>
            <tr>
              <th>RANK</th><th>PLAYER</th>
              <th class="th-m">CAT DAD MODEL</th>
              <th class="th-b">BOOKIE</th>
              <th>EDGE <span class="th-info">ⓘ</span></th>
              <th>BEST ODDS <span class="th-info">ⓘ</span></th>
              <th>CONFIDENCE</th>
            </tr>
          </thead>
          <tbody>
{match_player_rows(g["players"])}
          </tbody>
        </table>
        <p class="mfootnote">First SOT prob = λ<sub>player</sub>/Σλ. Model: 60% intl SOT rate + 40% bookie λ · position timing · FK specialist +12%. <span class="fk-tag">FK</span> = known free kick taker. Odds: William Hill "Over 0.5 SOT".</p>
      </div>
    </div>""")
    return "\n".join(cards)

def build_html(games, updated, nat_cov, total, with_odds):
    be_rows = best_edges_rows(games)
    mcards  = match_cards(games)
    nat_pct = round(nat_cov / 48 * 100)
    odds_pct = round(with_odds / total * 100)

    # Donut SVG helper
    def donut(pct, color):
        r = 16; c = 20; circ = 2*3.14159*r
        dash = pct/100*circ
        return f'<svg width="40" height="40" viewBox="0 0 40 40"><circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="#1e2d3d" stroke-width="4"/><circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{color}" stroke-width="4" stroke-dasharray="{dash:.1f} {circ:.1f}" stroke-dashoffset="{circ/4:.1f}" stroke-linecap="round"/><text x="{c}" y="{c}" text-anchor="middle" dy=".35em" fill="{color}" font-size="9" font-weight="700">{pct}%</text></svg>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>World's Worst Punter · First Shot On Target Edge Finder</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#080d18;color:#e2e8f0;min-height:100vh;font-size:12px}}

/* ── TOPBAR ── */
.topbar{{display:flex;justify-content:space-between;align-items:center;padding:10px 20px;background:#0d1424;border-bottom:1px solid #1a2540}}
.topbar-left{{display:flex;align-items:center;gap:10px}}
.trophy{{font-size:1.35rem}}
.site-title{{font-size:1.08rem;font-weight:800;letter-spacing:-.3px}}
.site-title .wc{{color:#22c55e}}
.site-title .rest{{color:#f1f5f9}}
.site-title .accent{{color:#4ade80}}
.site-subtitle{{color:#64748b;font-size:.68rem;margin-top:2px}}
.topbar-right{{display:flex;align-items:center;gap:10px;text-align:right}}
.last-upd-label{{color:#64748b;font-size:.6rem;text-transform:uppercase;letter-spacing:.4px}}
.last-upd-val{{color:#94a3b8;font-size:.68rem;font-weight:600}}
.refresh-btn{{width:26px;height:26px;background:#1a2540;border:1px solid #2a3a5c;border-radius:5px;display:flex;align-items:center;justify-content:center;cursor:pointer;color:#64748b;font-size:.75rem}}
.refresh-btn:hover{{background:#1e2d4a;color:#e2e8f0}}

/* ── KPI BAR ── */
.kpi-bar{{display:flex;gap:0;background:#0d1424;border-bottom:1px solid #1a2540}}
.kpi{{flex:1;display:flex;align-items:center;gap:10px;padding:12px 16px;border-right:1px solid #1a2540}}
.kpi:last-child{{border-right:none}}
.kpi-icon{{width:34px;height:34px;border-radius:8px;background:#22c55e18;display:flex;align-items:center;justify-content:center;font-size:.95rem;flex-shrink:0}}
.kpi-icon.blue{{background:#3b82f618}}
.kpi-icon.purple{{background:#8b5cf618}}
.kpi-icon.amber{{background:#f59e0b18}}
.kpi-n{{font-size:1.3rem;font-weight:800;color:#f1f5f9;line-height:1}}
.kpi-sub{{font-size:.6rem;color:#64748b;margin-top:3px}}
.kpi-sub .dim{{color:#4b5563;font-size:.57rem}}

/* ── MAIN LAYOUT ── */
.main{{display:flex;gap:0;min-height:calc(100vh - 100px)}}
.content{{flex:1;padding:16px 16px 32px;min-width:0;border-right:1px solid #1a2540}}
.sidebar{{width:248px;flex-shrink:0;padding:16px 13px;background:#0b1020}}

/* ── SECTION HEADERS ── */
.sec-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}}
.sec-title{{display:flex;align-items:center;gap:7px;font-weight:700;font-size:.83rem;color:#f1f5f9}}
.sec-title .ico{{color:#22c55e}}
.sec-subtitle{{color:#64748b;font-size:.63rem;font-weight:400;margin-left:4px}}
.view-all{{background:#1a2540;border:1px solid #2a3a5c;color:#94a3b8;font-size:.67rem;padding:5px 10px;border-radius:5px;cursor:pointer;display:flex;align-items:center;gap:4px;text-decoration:none}}
.view-all:hover{{background:#1e2d4a;color:#e2e8f0}}

/* ── BEST EDGES TABLE ── */
.be-card{{background:#0f1929;border:1px solid #1a2540;border-radius:9px;overflow:hidden;margin-bottom:16px}}
.be-table{{width:100%;border-collapse:collapse}}
.be-table th{{padding:8px 10px;font-size:.58rem;color:#4b5563;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid #1a2540;text-align:left;white-space:nowrap}}
.be-table th.th-m{{color:#3b82f6}}
.be-table th.th-b{{color:#f59e0b}}
.be-row td{{padding:9px 10px;border-bottom:1px solid #111d30;vertical-align:middle}}
.be-row:last-child td{{border-bottom:none}}
.be-row:hover td{{background:#111e33}}

.rank-circle{{display:inline-flex;width:19px;height:19px;background:#22c55e;border-radius:50%;align-items:center;justify-content:center;font-size:.63rem;font-weight:800;color:#000}}
.avatar{{width:29px;height:29px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.63rem;font-weight:700;color:#fff;flex-shrink:0}}
.be-player{{display:flex;align-items:center;gap:7px}}
.be-name{{font-weight:600;color:#f1f5f9;font-size:.77rem}}
.be-country{{font-size:.6rem;color:#64748b;margin-top:1px}}
.be-match{{font-weight:700;font-size:.72rem;color:#f1f5f9}}
.be-date{{font-size:.6rem;color:#64748b;margin-top:1px}}
.td-model{{color:#3b82f6;font-weight:800;font-size:.82rem}}
.td-bm{{color:#f59e0b;font-weight:700;font-size:.77rem}}
.odds-val{{font-weight:800;color:#f1f5f9;margin-right:3px}}

/* ── FK TAG ── */
.fk-tag{{font-size:.55rem;font-weight:800;background:#f59e0b22;color:#f59e0b;border:1px solid #f59e0b44;padding:1px 4px;border-radius:3px;letter-spacing:.3px;vertical-align:middle}}

/* ── FILTER BAR ── */
.filter-bar{{display:flex;align-items:center;gap:7px;margin-bottom:12px;flex-wrap:wrap}}
.ftab{{background:#0f1929;border:1px solid #1a2540;color:#94a3b8;font-size:.67rem;padding:6px 12px;border-radius:5px;cursor:pointer;display:flex;align-items:center;gap:4px;white-space:nowrap}}
.ftab:hover{{background:#162038;color:#e2e8f0}}
.ftab.active{{background:#22c55e18;border-color:#22c55e55;color:#22c55e}}
.ftab .fi{{font-size:.72rem}}
.search-wrap{{flex:1;min-width:160px;position:relative}}
.search-wrap input{{width:100%;padding:6px 10px 6px 28px;background:#0f1929;border:1px solid #1a2540;border-radius:5px;color:#e2e8f0;font-size:.7rem;outline:none}}
.search-wrap input:focus{{border-color:#22c55e55}}
.search-wrap input::placeholder{{color:#4b5563}}
.search-icon{{position:absolute;left:9px;top:50%;transform:translateY(-50%);color:#4b5563;font-size:.72rem}}
.filter-btn{{background:#0f1929;border:1px solid #1a2540;color:#94a3b8;font-size:.67rem;padding:6px 10px;border-radius:5px;cursor:pointer;display:flex;align-items:center;gap:4px}}

/* ── MATCH CARDS ── */
.mcard{{background:#0f1929;border:1px solid #1a2540;border-radius:9px;margin-bottom:7px;overflow:hidden}}
.mcard:hover{{border-color:#2a3a5c}}
.card-dim{{opacity:.45}}
.mcard-header{{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;cursor:pointer;flex-wrap:wrap;gap:5px}}
.mcard-header:hover{{background:#111d30}}
.mcard-left{{display:flex;align-items:center;gap:7px;flex-wrap:wrap}}
.mflag{{font-size:1rem}}
.mteam{{font-weight:700;font-size:.82rem;color:#f1f5f9}}
.mvs{{color:#4b5563;font-size:.63rem;font-weight:700;background:#1a2540;padding:2px 5px;border-radius:3px}}
.mbadge{{font-size:.58rem;font-weight:600;padding:2px 7px;border-radius:3px}}
.nat-badge{{background:#22c55e18;color:#22c55e;border:1px solid #22c55e33}}
.bk-badge{{background:#1a2540;color:#64748b}}
.tbc-badge{{background:#f59e0b18;color:#f59e0b}}
.mcard-right{{display:flex;align-items:center;gap:9px}}
.mdate{{color:#64748b;font-size:.65rem}}
.mchev{{color:#4b5563;font-size:.72rem;transition:transform .2s}}
.mchev.open{{transform:rotate(180deg)}}

.mcard-body{{display:none;padding:0 14px 12px}}
.mcard.open .mcard-body{{display:block}}
.mcard.open .mcard-header{{border-bottom:1px solid #1a2540}}

.mtable{{width:100%;border-collapse:collapse;margin-top:5px}}
.mtable th{{padding:7px 9px;font-size:.57rem;color:#4b5563;text-transform:uppercase;letter-spacing:.4px;border-bottom:1px solid #1a2540;text-align:left;white-space:nowrap}}
.mtable th.th-m{{color:#3b82f6}}
.mtable th.th-b{{color:#f59e0b}}
.th-info{{color:#2a3a5c;cursor:help}}
.mtable td{{padding:8px 9px;border-bottom:1px solid #111d30;vertical-align:middle;font-size:.77rem}}
.mtable tr:last-child td{{border-bottom:none}}
.mtable tr:hover td{{background:#111e33}}
.medal{{font-size:.85rem}}
.rank-sm{{display:inline-flex;width:16px;height:16px;background:#1a2540;border-radius:50%;align-items:center;justify-content:center;font-size:.58rem;color:#64748b;font-weight:700}}
.td-pname{{font-weight:600;color:#f1f5f9}}
.p-flag{{font-size:.9rem;margin-right:2px}}
.no-data{{text-align:center;color:#4b5563;padding:16px!important;font-style:italic;font-size:.72rem}}
.mfootnote{{color:#2a3a5c;font-size:.58rem;margin-top:9px;padding-top:7px;border-top:1px solid #111d30;line-height:1.6}}
.mfootnote sub{{font-size:.54rem;vertical-align:sub}}

/* ── EDGE PILLS ── */
.epill{{font-size:.72rem;font-weight:700;padding:3px 8px;border-radius:4px;white-space:nowrap;display:inline-flex;align-items:center;gap:3px}}
.e-strong-val{{background:#22c55e22;color:#22c55e;border:1px solid #22c55e44}}
.e-slight-val{{background:#22c55e11;color:#4ade80}}
.e-neutral{{background:#1a2540;color:#64748b}}
.e-slight-fad{{background:#ef444411;color:#fca5a5}}
.e-strong-fad{{background:#ef444422;color:#ef4444;border:1px solid #ef444444}}

/* ── CONFIDENCE ── */
.cbadge{{font-size:.7rem;font-weight:600;padding:3px 8px;border-radius:4px;white-space:nowrap}}
.conf-hi{{background:#22c55e18;color:#22c55e}}
.conf-med{{background:#f59e0b18;color:#f59e0b}}
.conf-lo{{background:#ef444418;color:#ef4444}}

/* ── BOOKMAKER LOGOS ── */
.bm{{font-size:.68rem;font-weight:700;white-space:nowrap}}
.wh{{color:#f1f5f9;background:#111;padding:2px 5px;border-radius:3px;font-size:.63rem}}
.wh strong{{font-size:.7rem}}
.un{{color:#f59e0b;font-size:.65rem;letter-spacing:.5px}}
.un-dots{{color:#f59e0b44;font-size:.5rem;margin-left:1px}}
.pp{{color:#22c55e;font-size:.65rem}}
.lv{{color:#c084fc;font-size:.65rem}}
.bf{{color:#f97316;font-size:.65rem}}
.generic{{color:#94a3b8;font-size:.65rem;background:#1a2540;padding:2px 5px;border-radius:3px}}

/* ── SIDEBAR ── */
.sb-section{{background:#0f1929;border:1px solid #1a2540;border-radius:9px;padding:11px 13px;margin-bottom:10px}}
.sb-title{{display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:.73rem;color:#f1f5f9;margin-bottom:10px}}
.sb-title .sb-ico{{color:#22c55e;margin-right:5px}}
.sb-toggle{{color:#64748b;cursor:pointer;font-size:.67rem}}

.model-item{{display:flex;align-items:center;gap:8px;margin-bottom:8px}}
.model-item:last-child{{margin-bottom:0}}
.mi-circle{{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:middle;justify-content:center;font-size:.62rem;font-weight:800;flex-shrink:0}}
.mi-green{{background:#22c55e22;color:#22c55e;border:2px solid #22c55e44}}
.mi-blue{{background:#3b82f622;color:#3b82f6;border:2px solid #3b82f644}}
.mi-purple{{background:#8b5cf622;color:#8b5cf6;border:2px solid #8b5cf644}}
.mi-amber{{background:#f59e0b22;color:#f59e0b;border:2px solid #f59e0b44}}
.mi-label{{font-weight:700;font-size:.7rem;color:#f1f5f9;line-height:1.2}}
.mi-sub{{font-size:.6rem;color:#64748b;margin-top:1px}}
.show-details{{color:#22c55e;font-size:.65rem;cursor:pointer;display:flex;align-items:center;gap:4px;margin-top:7px}}

.sb-stat{{display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #111d30}}
.sb-stat:last-child{{border-bottom:none}}
.sb-stat-label{{color:#64748b;font-size:.67rem}}
.sb-stat-val{{font-weight:700;color:#f1f5f9;font-size:.73rem}}
.sb-upd{{color:#4b5563;font-size:.6rem;margin-top:7px}}
.sb-upd span{{color:#22c55e}}

.cov-item{{display:flex;align-items:center;gap:8px;margin-bottom:9px}}
.cov-item:last-child{{margin-bottom:0}}
.cov-label{{font-size:.67rem;color:#94a3b8;font-weight:600}}
.cov-sub{{font-size:.6rem;color:#4b5563}}

.leg-item{{display:flex;align-items:center;gap:7px;padding:4px 0;font-size:.65rem;color:#94a3b8}}
.leg-dot{{width:9px;height:9px;border-radius:50%;flex-shrink:0}}
.leg-range{{color:#4b5563;font-size:.6rem;margin-left:auto}}

.disclaimer{{background:#1a2540;border:1px solid #2a3a5c;border-left:3px solid #3b82f6;border-radius:5px;padding:8px 10px;margin-top:7px;color:#64748b;font-size:.62rem;line-height:1.6}}

/* ── MODAL ── */
.modal-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:1000;align-items:center;justify-content:center;padding:20px}}
.modal-overlay.open{{display:flex}}
.modal{{background:#0f1929;border:1px solid #2a3a5c;border-radius:14px;width:100%;max-width:580px;max-height:88vh;overflow-y:auto;box-shadow:0 25px 60px rgba(0,0,0,.6)}}
.modal-head{{display:flex;justify-content:space-between;align-items:center;padding:18px 20px 14px;border-bottom:1px solid #1a2540;position:sticky;top:0;background:#0f1929;z-index:1}}
.modal-head h2{{font-size:.95rem;font-weight:800;color:#f1f5f9;display:flex;align-items:center;gap:8px}}
.modal-close{{width:28px;height:28px;background:#1a2540;border:1px solid #2a3a5c;border-radius:6px;color:#64748b;cursor:pointer;font-size:1rem;display:flex;align-items:center;justify-content:center;line-height:1}}
.modal-close:hover{{background:#2a3a5c;color:#f1f5f9}}
.modal-body{{padding:18px 20px}}
.modal-section{{margin-bottom:20px}}
.modal-section:last-child{{margin-bottom:0}}
.modal-section h3{{font-size:.72rem;text-transform:uppercase;letter-spacing:.6px;color:#22c55e;font-weight:700;margin-bottom:10px;display:flex;align-items:center;gap:6px}}
.modal-section p,.modal-section li{{font-size:.78rem;color:#94a3b8;line-height:1.75}}
.modal-section ul{{padding-left:16px;margin-top:6px}}
.modal-section li{{margin-bottom:4px}}
.modal-section strong{{color:#f1f5f9}}
.modal-formula{{background:#080d18;border:1px solid #1a2540;border-radius:7px;padding:12px 14px;font-family:monospace;font-size:.75rem;color:#22c55e;margin:10px 0;line-height:1.8}}
.modal-factor{{display:flex;align-items:flex-start;gap:12px;padding:10px 0;border-bottom:1px solid #1a2540}}
.modal-factor:last-child{{border-bottom:none}}
.mf-circle{{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.65rem;font-weight:800;flex-shrink:0;margin-top:1px}}
.mf-title{{font-weight:700;font-size:.8rem;color:#f1f5f9;margin-bottom:3px}}
.mf-desc{{font-size:.72rem;color:#64748b;line-height:1.6}}
.modal-divider{{border:none;border-top:1px solid #1a2540;margin:16px 0}}

/* ── BEST EDGES COLLAPSE ── */
.be-toggle{{display:flex;align-items:center;gap:6px;cursor:pointer;user-select:none}}
.be-chev{{color:#64748b;font-size:.75rem;transition:transform .2s}}
.be-chev.closed{{transform:rotate(-90deg)}}
.be-body{{overflow:hidden;transition:max-height .25s ease}}
.be-body.collapsed{{display:none}}

@media(max-width:900px){{
  .sidebar{{display:none}}
  .kpi{{padding:12px 14px}}
}}
@media(max-width:600px){{
  .be-table th:nth-child(3),.be-row td:nth-child(3),
  .be-table th:nth-child(8),.be-row td:nth-child(8){{display:none}}
  .kpi-bar{{flex-wrap:wrap}}
  .kpi{{min-width:50%}}
}}
</style>
</head>
<body>

<!-- TOPBAR -->
<div class="topbar">
  <div class="topbar-left">
    <span class="trophy">🏆</span>
    <div>
      <div class="site-title"><span class="wc">WC 2026</span>&nbsp;&nbsp;<span class="rest">World's Worst Punter's <span class="accent">First Shot On Target Edge Finder</span></span></div>
      <div class="site-subtitle">Cat Dad Model probabilities vs bookmaker-implied odds for every group-stage match.</div>
    </div>
  </div>
  <div class="topbar-right">
    <div>
      <div class="last-upd-label">Last updated</div>
      <div class="last-upd-val">{updated}</div>
    </div>
    <div class="refresh-btn" onclick="location.reload()">↻</div>
  </div>
</div>

<!-- KPI BAR -->
<div class="kpi-bar">
  <div class="kpi">
    <div class="kpi-icon">📅</div>
    <div><div class="kpi-n">{total}</div><div class="kpi-sub">Matches<br><span class="dim">Group Stage</span></div></div>
  </div>
  <div class="kpi">
    <div class="kpi-icon blue">📈</div>
    <div><div class="kpi-n">{with_odds}</div><div class="kpi-sub">With Live Odds<br><span class="dim">{odds_pct}% of matches</span></div></div>
  </div>
  <div class="kpi">
    <div class="kpi-icon purple">👥</div>
    <div><div class="kpi-n">48</div><div class="kpi-sub">Teams<br><span class="dim">Qualified</span></div></div>
  </div>
  <div class="kpi">
    <div class="kpi-icon amber">🕐</div>
    <div><div class="kpi-n">{updated.split()[0]} {updated.split()[1]} {updated.split()[2]}</div><div class="kpi-sub">Last Updated<br><span class="dim">{updated.split("·")[1].strip() if "·" in updated else ""}</span></div></div>
  </div>
</div>

<!-- MAIN -->
<div class="main">

  <!-- CONTENT -->
  <div class="content">

    <!-- BEST EDGES -->
    <div class="be-card">
      <div style="padding:14px 16px 0;display:flex;justify-content:space-between;align-items:center">
        <div class="sec-title">
          <span class="ico">📊</span> Best Edges
          <span class="sec-subtitle">Top value opportunities across all matches</span>
        </div>
        <div class="be-toggle" onclick="toggleBE()">
          <a class="view-all" href="#all-matches" onclick="event.stopPropagation()">View all matches →</a>
          <span style="margin-left:6px;color:#64748b;font-size:.67rem" id="be-label">▲ Collapse</span>
        </div>
      </div>
      <div class="be-body" id="be-body">
      <table class="be-table" style="margin-top:10px">
        <thead>
          <tr>
            <th>RANK</th><th>PLAYER</th><th>MATCH</th>
            <th class="th-m">CAT DAD MODEL</th>
            <th class="th-b">BOOKIE</th>
            <th>EDGE ⓘ</th>
            <th>BEST ODDS ⓘ</th>
            <th>CONFIDENCE</th>
          </tr>
        </thead>
        <tbody>
{be_rows}
        </tbody>
      </table>
      </div>
    </div>

    <!-- FILTER BAR -->
    <div class="filter-bar" id="all-matches">
      <button class="ftab active" onclick="filterMatches('all',this)"><span class="fi">📅</span> All Matches</button>
      <button class="ftab" onclick="filterMatches('value',this)"><span class="fi">⭐</span> Value Only</button>
      <button class="ftab" onclick="filterMatches('live',this)"><span class="fi">📡</span> With Live Odds</button>
      <button class="ftab" onclick="filterMatches('high',this)"><span class="fi">🛡</span> High Confidence</button>
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input type="text" placeholder="Search player or team..." oninput="searchMatches(this.value)">
      </div>
      <button class="filter-btn">⚙ Filters</button>
    </div>

    <!-- MATCH CARDS -->
    <div id="match-list">
{mcards}
    </div>

  </div><!-- /content -->

  <!-- SIDEBAR -->
  <div class="sidebar">

    <!-- How it works -->
    <div class="sb-section">
      <div class="sb-title"><span><span class="sb-ico">🐱</span> How the Cat Dad Model Works</span><span class="sb-toggle">▾</span></div>
      <p style="color:#64748b;font-size:.63rem;margin-bottom:9px">Four factors combined to estimate which player has the first shot on target.</p>
      <div class="model-item">
        <div class="mi-circle mi-green">60%</div>
        <div><div class="mi-label">National Team SOT Rate</div><div class="mi-sub">SOT per 90 mins across 2022–2025 intl fixtures</div></div>
      </div>
      <div class="model-item">
        <div class="mi-circle mi-blue">40%</div>
        <div><div class="mi-label">Bookmaker Implied Rate</div><div class="mi-sub">William Hill "Over 0.5 SOT" → Poisson λ</div></div>
      </div>
      <div class="model-item">
        <div class="mi-circle mi-purple">⚡</div>
        <div><div class="mi-label">Position Timing</div><div class="mi-sub">Forwards/attackers +18% (shoot earlier in games)</div></div>
      </div>
      <div class="model-item">
        <div class="mi-circle mi-amber">FK</div>
        <div><div class="mi-label">Free Kick Specialist</div><div class="mi-sub">Known FK takers +12% (direct shot from set pieces)</div></div>
      </div>
      <div class="show-details" onclick="openModal()">Show full details ▾</div>
    </div>

    <!-- Model Status -->
    <div class="sb-section">
      <div class="sb-title"><span><span class="sb-ico">📈</span> Model Status</span></div>
      <div class="sb-stat"><span class="sb-stat-label">Total Matches</span><span class="sb-stat-val">{total}</span></div>
      <div class="sb-stat"><span class="sb-stat-label">With Live Odds</span><span class="sb-stat-val">{with_odds}</span></div>
      <div class="sb-stat"><span class="sb-stat-label">Teams with National Data</span><span class="sb-stat-val">{nat_cov}</span></div>
      <p class="sb-upd">Last Updated <span>{updated}</span></p>
    </div>

    <!-- Data Coverage -->
    <div class="sb-section">
      <div class="sb-title"><span><span class="sb-ico">📊</span> Data Coverage</span></div>
      <div class="cov-item">
        {donut(nat_pct, "#22c55e")}
        <div>
          <div class="cov-label">National Team Data</div>
          <div class="cov-sub">{nat_cov} / 48 teams</div>
        </div>
      </div>
      <div class="cov-item">
        {donut(odds_pct, "#3b82f6")}
        <div>
          <div class="cov-label">Bookmaker Odds</div>
          <div class="cov-sub">{with_odds} / {total} matches</div>
        </div>
      </div>
    </div>

    <!-- Edge Legend -->
    <div class="sb-section">
      <div class="sb-title"><span><span class="sb-ico">📋</span> Edge Legend</span></div>
      <div class="leg-item"><span class="leg-dot" style="background:#22c55e;border:2px solid #22c55e66"></span> Strong Value <span class="leg-range">(≥ +1.5%)</span></div>
      <div class="leg-item"><span class="leg-dot" style="background:#4ade80"></span> Slight Value <span class="leg-range">(+0.5% to +1.5%)</span></div>
      <div class="leg-item"><span class="leg-dot" style="background:#2a3a5c"></span> Neutral <span class="leg-range">(−0.5% to +0.5%)</span></div>
      <div class="leg-item"><span class="leg-dot" style="background:#fca5a5"></span> Slight Fade <span class="leg-range">(−0.5% to −1.5%)</span></div>
      <div class="leg-item"><span class="leg-dot" style="background:#ef4444;border:2px solid #ef444466"></span> Strong Fade <span class="leg-range">(≤ −1.5%)</span></div>
    </div>

    <div class="disclaimer">
      ⓘ This is a modelling tool, not betting advice. Bookmaker odds move quickly. Always check live prices before placing a bet.
    </div>

  </div><!-- /sidebar -->

</div><!-- /main -->

<script>
// Toggle match cards
// ── MODAL ──
function openModal() {{
  document.getElementById('model-modal').classList.add('open');
  document.body.style.overflow = 'hidden';
}}
function closeModal() {{
  document.getElementById('model-modal').classList.remove('open');
  document.body.style.overflow = '';
}}
document.addEventListener('keydown', function(e) {{ if(e.key==='Escape') closeModal(); }});

// ── BEST EDGES COLLAPSE ──
var beOpen = true;
function toggleBE() {{
  beOpen = !beOpen;
  var body = document.getElementById('be-body');
  var lbl  = document.getElementById('be-label');
  body.classList.toggle('collapsed', !beOpen);
  lbl.textContent = beOpen ? '▲ Collapse' : '▼ Expand';
}}

// ── MATCH CARDS ──
function tog(id) {{
  var c = document.getElementById('mc-'+id);
  var ch = document.getElementById('chev-'+id);
  var open = c.classList.contains('open');
  c.classList.toggle('open', !open);
  if(ch) ch.classList.toggle('open', !open);
}}

// Filter tabs
var activeFilter = 'all';
function filterMatches(type, btn) {{
  activeFilter = type;
  document.querySelectorAll('.ftab').forEach(function(b){{ b.classList.remove('active'); }});
  if(btn) btn.classList.add('active');
  applyFilters();
}}

function searchMatches(q) {{
  document.getElementById('search-query', q);
  applyFilters(q);
}}

function applyFilters(searchQ) {{
  var q = (searchQ || document.querySelector('.search-wrap input').value || '').toLowerCase();
  document.querySelectorAll('.mcard').forEach(function(card) {{
    var txt = card.textContent.toLowerCase();
    var matchSearch = !q || txt.includes(q);
    var matchFilter = true;
    if(activeFilter === 'value') matchFilter = card.querySelector('.e-strong-val, .e-slight-val') !== null;
    if(activeFilter === 'live')  matchFilter = !card.classList.contains('card-dim');
    if(activeFilter === 'high')  matchFilter = card.querySelector('.conf-hi') !== null;
    card.style.display = (matchSearch && matchFilter) ? '' : 'none';
  }});
}}

// Auto-open first 3 matches with data
var n=0;
document.querySelectorAll('.mcard:not(.card-dim)').forEach(function(c){{
  if(n<3){{ var id=c.id.replace('mc-',''); tog(id); n++; }}
}});
</script>

<!-- ── MODEL DETAIL MODAL ── -->
<div class="modal-overlay" id="model-modal" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <div class="modal-head">
      <h2>🐱 How the Cat Dad Model Works</h2>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">

      <div class="modal-section">
        <h3>🎯 What We're Predicting</h3>
        <p>For each WC 2026 group stage match, we estimate which player is most likely to have the <strong>first shot on target</strong> — a specific prop betting market offered by bookmakers like William Hill and Unibet.</p>
      </div>

      <div class="modal-section">
        <h3>⚙️ The Core Formula</h3>
        <p>We model shots as a <strong>Poisson process</strong> — a way to describe random events happening over time. Each player has a rate λ (lambda) representing how many shots on target they're expected to take per game. The player who shoots fastest on average is most likely to be first.</p>
        <div class="modal-formula">
          P(player X is first SOT) = λ<sub>X</sub> / Σλ<sub>all players</sub>
        </div>
        <p>So if Son has λ=1.33 and all other players combined have Σλ=18.5, his first-SOT probability is 1.33/18.5 = <strong>7.2%</strong>.</p>
      </div>

      <div class="modal-section">
        <h3>📊 The Four Factors</h3>
        <div class="modal-factor">
          <div class="mf-circle mi-green">60%</div>
          <div>
            <div class="mf-title">National Team SOT Rate</div>
            <div class="mf-desc">We pull each player's shots on target per 90 minutes across <strong>4 years of international fixtures</strong> (2022–2025: World Cup, UEFA Nations League, qualifiers, friendlies). National stats are prioritised over club stats because players operate in different tactical systems for their country — a striker who shoots 3× per game at club level might play wider or deeper for their national team.</div>
          </div>
        </div>
        <div class="modal-factor">
          <div class="mf-circle mi-blue">40%</div>
          <div>
            <div class="mf-title">Bookmaker Implied Rate</div>
            <div class="mf-desc">William Hill's "Over 0.5 shots on target" odds are converted into a Poisson rate using <strong>λ = −ln(1 − p)</strong> where p is the implied probability (1/odds). This fills gaps where we have no stat data and grounds the model in market consensus — bookmakers have access to team news, form data, and injury information we don't.</div>
          </div>
        </div>
        <div class="modal-factor">
          <div class="mf-circle mi-purple">⚡</div>
          <div>
            <div class="mf-title">Position Timing Adjustment</div>
            <div class="mf-desc">The first-shot market is about <em>timing</em>, not just volume. Forwards and attackers tend to attempt shots in the opening minutes when teams press high. Defenders rarely shoot early. We apply a multiplier: <strong>Attackers/Forwards +18%</strong>, Midfielders neutral, Defenders −20%, Goalkeepers −80%.</div>
          </div>
        </div>
        <div class="modal-factor">
          <div class="mf-circle mi-amber">FK</div>
          <div>
            <div class="mf-title">Free Kick Specialist Boost</div>
            <div class="mf-desc">Players who regularly take free kicks get a <strong>+12% boost</strong>. A direct free kick in a good position is one of the most common sources of early shots on target in international football. We maintain a curated list of known FK takers per national team (e.g. Son, Griezmann, Bruno Fernandes, Messi, De Bruyne).</div>
          </div>
        </div>
      </div>

      <hr class="modal-divider">

      <div class="modal-section">
        <h3>📐 Edge Calculation</h3>
        <p>The <strong>Edge</strong> column shows where our model disagrees with the bookmaker's implied ranking:</p>
        <ul>
          <li><strong>Edge = Cat Dad Model % − Bookmaker Implied %</strong></li>
          <li><span style="color:#22c55e">Green (positive edge)</span> — our model rates this player higher than the market. The bookmaker may be undervaluing them relative to their international shot rate or set-piece involvement.</li>
          <li><span style="color:#ef4444">Red (negative edge)</span> — the market rates them higher than we do. Consider fading them in the first-shot market.</li>
        </ul>
        <p style="margin-top:8px">Positive edge does not guarantee a winning bet — it indicates potential value worth investigating.</p>
      </div>

      <div class="modal-section">
        <h3>⚠️ Limitations</h3>
        <ul>
          <li>National team stats are <strong>sparse</strong> — most players have 5–15 appearances. Small samples create noise.</li>
          <li>We do not currently model <strong>expected lineups</strong> — a player listed may not start.</li>
          <li>Bookmaker odds reflect the closest available market to "first SOT" — not the exact market.</li>
          <li>FK specialist list is manually curated and may be incomplete.</li>
        </ul>
      </div>

    </div>
  </div>
</div>

</body>
</html>"""

if __name__ == "__main__":
    print("Loading data...")
    events   = load("wc_events.json") or []
    all_odds = load("all_odds.json") or {}
    squads   = load("wc_squads.json") or {}
    nat_agg  = load("national_stats_agg.json") or {}

    updated = datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M UTC")
    nat_cov = len(nat_agg)
    print(f"  Events: {len(events)}, Teams with nat stats: {nat_cov}")

    games = []
    for event in sorted(events, key=lambda e: e["commence_time"]):
        eid = event["id"]
        home, away = event["home_team"], event["away_team"]
        players = build_predictions(all_odds.get(eid,{}), home, away, nat_agg, squads)
        nat_c = sum(1 for p in players[:5] if p.get("has_nat"))
        games.append({
            "id": eid, "home": home, "away": away,
            "date_fmt": fmt_date(event["commence_time"]),
            "date_short": fmt_date_short(event["commence_time"]),
            "time": fmt_time(event["commence_time"]),
            "players": players,
            "has_data": bool(players),
            "nat_count": nat_c,
        })

    total = len(games)
    with_odds = sum(1 for g in games if g["has_data"])
    odds_pct = round(with_odds / total * 100) if total else 0
    print(f"  {total} games, {with_odds} with odds")

    html = build_html(games, updated, nat_cov, total, with_odds)
    with open("index.html","w") as f: f.write(html)
    print("Built → index.html")
