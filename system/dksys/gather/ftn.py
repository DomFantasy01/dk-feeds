"""RATCLIFFE (FTN) PROJECTIONS, SCORED FOR EACH LEAGUE (Oct 28 2026, Dom: Jeff Ratcliffe's numbers lead).
Reads yahoo_drop/ftn/ftn_weekly.txt and ftn_ros.txt (the Chrome read of Dom's FTN subscription) and scores every stat line
in each of Dom's four leagues' own rules (scoring_audit_oct1.json) - never FTN's own half-PPR points.
  weekly -> this week's number;  ROS -> rest-of-season total, turned into a per-game rate over the team's remaining games through Week 17.
Writes /home/claude/dksys/data/latest/ftn_scored.csv: key|name|team|pos|lg|wk|ros_pg|ros_total|ros_games|read_pt
Scoring: 25 pass yds/pt, 6/pass TD, INT -2 (DK IV -1), 10 rush+rec yds/pt, 6/TD, 1/catch, fumble lost -2, 0.25/carry
(DK I-III). Kickers: 3 per FG to 39 yds, then each league's 40-49 / 50+ value, 1 per PAT. Defenses: sacks 1, INT 2, fumble
recovery 2, TD 6, safety 2, blocked kick 2, plus each league's points-allowed tiers taken over a spread around FTN's PPG."""
import os, re, sys, json, math
import pandas as pd
sys.path.insert(0, "/home/claude/dksys/gather"); from names import norm

REPO = os.environ.get("DK_REPO", "/home/claude/dk-feeds")
L = "/home/claude/dksys/data/latest/"
OUT = L + "ftn_scored.csv"
LG = {1: "DK I 269381", 2: "DK II 1519795", 3: "DK III 1507991", 4: "DK IV 864215"}
NICK = {"Arizona Cardinals": "ARI", "Atlanta Falcons": "ATL", "Baltimore Ravens": "BAL", "Buffalo Bills": "BUF", "Carolina Panthers": "CAR",
        "Chicago Bears": "CHI", "Cincinnati Bengals": "CIN", "Cleveland Browns": "CLE", "Dallas Cowboys": "DAL", "Denver Broncos": "DEN",
        "Detroit Lions": "DET", "Green Bay Packers": "GB", "Houston Texans": "HOU", "Indianapolis Colts": "IND", "Jacksonville Jaguars": "JAX",
        "Kansas City Chiefs": "KC", "Las Vegas Raiders": "LV", "Los Angeles Chargers": "LAC", "Los Angeles Rams": "LAR", "Miami Dolphins": "MIA",
        "Minnesota Vikings": "MIN", "New England Patriots": "NE", "New Orleans Saints": "NO", "New York Giants": "NYG", "New York Jets": "NYJ",
        "Philadelphia Eagles": "PHI", "Pittsburgh Steelers": "PIT", "San Francisco 49ers": "SF", "Seattle Seahawks": "SEA", "Tampa Bay Buccaneers": "TB",
        "Tennessee Titans": "TEN", "Washington Commanders": "WAS"}
TFIX = {"ARZ": "ARI", "LA": "LAR", "JAC": "JAX", "WSH": "WAS"}

def read(fn):
    p = f"{REPO}/yahoo_drop/ftn/{fn}"
    if not os.path.exists(p): return None, None
    lines = open(p).read().splitlines()
    m = re.search(r"read live (.*?) \(Chrome", lines[0]) if lines else None
    rows = []
    for l in lines[1:]:
        if not l.strip(): continue
        x = l.split("|"); d = {"pos": x[0]}
        for kv in x[1:]:
            if "=" in kv: k, v = kv.split("=", 1); d[k] = v
        nm = re.sub(r"\s+[A-Z]{2,3}\s+·\s+\w+$", "", d.get("Player", "")).strip()
        d["name"] = nm; d["team"] = TFIX.get(d.get("Team", ""), d.get("Team", ""))
        if d["pos"] == "DST": d["team"] = NICK.get(nm, d["team"]); d["name"] = d["team"] + " DEF"
        rows.append(d)
    return rows, (m.group(1) if m else "")

def f(d, k):
    try: return float(d.get(k, 0) or 0)
    except ValueError: return 0.0

def score(d, k, cfg, games=1.0):
    """league k (1-4) points from one FTN stat line; games>1 for ROS totals (defense tiers are per game)."""
    pos = d["pos"]; it = -1 if k == 4 else -2; ra = 0 if k == 4 else .25
    if pos in ("QB", "RB", "WR", "TE"):
        return (f(d, "PaYds") / 25 + 6 * f(d, "PaTD") + it * f(d, "PaINT") + f(d, "RuYds") / 10 + 6 * f(d, "RuTD") + ra * f(d, "RuAtt")
                + f(d, "Rec") + f(d, "ReYds") / 10 + 6 * f(d, "ReTD") - 2 * f(d, "Fum."))
    if pos == "K":
        if cfg.get("no_kicker"): return None
        kc = cfg.get("K", {}); return 3 * f(d, "39M") + kc.get("fg40_49", 4) * f(d, "49M") + kc.get("fg50", 5) * f(d, "50M") + f(d, "XPM")
    if pos == "DST":
        pa = cfg.get("DEF_pa", [10, 7, 4, 1, 0, -1, -4]); ppg = f(d, "PPG") or 21.0
        edges = [(0, .5), (.5, 6.5), (6.5, 13.5), (13.5, 20.5), (20.5, 27.5), (27.5, 34.5), (34.5, 99)]
        def cdf(x): return .5 * (1 + math.erf((x - ppg) / (9.0 * math.sqrt(2))))   # points allowed spread ~9 around the projection
        tier = sum(v * (cdf(b) - cdf(a if a > 0 else -99)) for v, (a, b) in zip(pa, edges))
        return tier * games + f(d, "Sks") + 2 * f(d, "DINT") + 2 * f(d, "FR") + 6 * f(d, "TD") + 2 * f(d, "Sfty") + 2 * f(d, "Blk")
    return None

def remaining_games(now):
    g = pd.read_csv(L + "games.csv", low_memory=False); g = g[(g.season == 2026) & (g.game_type == "REG") & (g.week >= now) & (g.week <= 17)]   # FTN ROS runs through Week 17 (tested: per-game matches the weekly number at 1.03; through 18 it was 0.93)
    c = {}
    for t in pd.concat([g.home_team, g.away_team]): c[TFIX.get(t, t)] = c.get(TFIX.get(t, t), 0) + 1
    return c

def main():
    SC = json.load(open(L + "yahoo/scoring/scoring_audit_oct1.json"))
    wk, wread = read("ftn_weekly.txt"); ros, rread = read("ftn_ros.txt")
    if not wk: print("FTN: no weekly file - Ratcliffe not available this build"); return
    g = pd.read_csv(L + "games.csv", low_memory=False); g = g[(g.season == 2026) & (g.game_type == "REG")]
    now = int(g[g.result.isna()].week.min()); left = remaining_games(now)
    out = []
    for k, key in LG.items():
        cfg = SC[key]; R = {}
        for d in (ros or []):
            n = left.get(d["team"], 0)
            if n: R[(norm(d["name"]), d["pos"])] = (score(d, k, cfg, games=n), n)
        for d in wk:
            v = score(d, k, cfg)
            if v is None: continue
            r = R.get((norm(d["name"]), d["pos"]))
            out.append(dict(key=norm(d["name"]), name=d["name"], team=d["team"], pos=d["pos"], lg=k, wk=round(v, 2),
                            ros_total=round(r[0], 1) if r else None, ros_games=r[1] if r else None,
                            ros_pg=round(r[0] / r[1], 2) if r and r[1] else None, read_pt=wread))
        # ROS-only men (on bye this week, or hurt now but projected later)
        have = {(o["key"], o["pos"]) for o in out if o["lg"] == k}
        for d in (ros or []):
            kk = (norm(d["name"]), d["pos"])
            if kk in have or kk not in R: continue
            tot, n = R[kk]
            out.append(dict(key=kk[0], name=d["name"], team=d["team"], pos=d["pos"], lg=k, wk=None, ros_total=round(tot, 1), ros_games=n,
                            ros_pg=round(tot / n, 2), read_pt=rread))
    df = pd.DataFrame(out); df.to_csv(OUT, index=False)
    print(f"FTN Ratcliffe scored: {len(df)} player-league rows, weekly read {wread}, ROS read {rread}, week {now}")
    return df

if __name__ == "__main__":
    main()
