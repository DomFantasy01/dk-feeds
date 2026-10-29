"""KOERNER (FantasyLabs) PROJECTIONS, SCORED FOR EACH LEAGUE (Oct 29 2026, Dom: Sean Koerner goes in next to Ratcliffe everywhere).
Reads yahoo_drop/flabs/koerner_weekly.txt (the Chrome read of Dom's FantasyLabs subscription, live_sync/dk_flabs_read.js) and
scores every stat line in each league's own rules with the same scorer as Ratcliffe (gather/ftn.py score()) - never the site's
own PPR points. Weekly only: FantasyLabs has no rest-of-season or future-week numbers.
Writes /home/claude/dksys/data/latest/koerner_scored.csv: key|name|team|pos|lg|wk|read_pt|site_pts
Koerner is a SECOND OPINION: Ratcliffe still leads every number that drives a decision; Koerner is shown beside him and his
disagreements are flagged."""
import os, re, sys, json
import pandas as pd
sys.path.insert(0, "/home/claude/dksys/gather"); from names import norm
from ftn import score, TFIX, LG, L, REPO

OUT = L + "koerner_scored.csv"

def read(fn="koerner_weekly.txt"):
    p = f"{REPO}/yahoo_drop/flabs/{fn}"
    if not os.path.exists(p): return None, None, None
    lines = open(p).read().splitlines()
    m = re.search(r"read live (.*?) \(Chrome", lines[0]) if lines else None
    w = re.search(r"Weekly, Week (\d+)", lines[0]) if lines else None
    rows = []
    for l in lines[1:]:
        if not l.strip(): continue
        x = l.split("|"); d = {"pos": x[0]}
        for kv in x[1:]:
            if "=" in kv: k, v = kv.split("=", 1); d[k] = v
        d["team"] = TFIX.get(d.get("Team", ""), d.get("Team", "")); d["name"] = d.get("Player", "").strip()
        if d["pos"] == "DST": d["name"] = d["team"] + " DEF"
        rows.append(d)
    return rows, (m.group(1) if m else ""), (int(w.group(1)) if w else None)

def main():
    rows, at, week = read()
    if not rows: print("KOERNER: no FantasyLabs file - Koerner not available this build"); return
    SC = json.load(open(L + "yahoo/scoring/scoring_audit_oct1.json"))
    g = pd.read_csv(L + "games.csv", low_memory=False); g = g[(g.season == 2026) & (g.game_type == "REG")]
    now = int(g[g.result.isna()].week.min())
    out = []
    for k, key in LG.items():
        cfg = SC[key]
        for d in rows:
            v = score(d, k, cfg)
            if v is None: continue
            out.append(dict(key=norm(d["name"]), name=d["name"], team=d["team"], pos=d["pos"], lg=k, wk=round(v, 2), read_pt=at,
                            read_week=week, site_pts=d.get("FPTS")))
    df = pd.DataFrame(out)
    if week is not None and week != now:
        print(f"KOERNER: file is Week {week} but the current week is {now} - not used"); df = df.iloc[0:0]
    df.to_csv(OUT, index=False)
    print(f"KOERNER (FantasyLabs) scored: {len(df)} player-league rows, read {at}, week {week}")
    return df

if __name__ == "__main__":
    main()
