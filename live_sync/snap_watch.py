# SNAP WATCH (Nov 27 2026, Dom: "Points aren't everything ... I'm looking at growth. Players that are taking over for other players"
# - "Yeah, do it all"). Points lag the role; snaps and targets move first. Free nflverse data (snap counts + weekly target share),
# every player at RB/WR/TE, and for each of Dom's four leagues:
#   RISER  - free agent / waiver man whose offensive snap share jumped (last 2 games vs the 2 before: +15 points, 50%+ last game,
#            20+ snaps) or whose target share jumped (+7 points, 15%+ last game). Names the teammate he is taking work from.
#   FALLER - one of Dom's own men losing snaps (-15 points, under 65% last game) while still playing - the role shrinking
#            before the points show it.
# Writes dispatch_out/snap_watch.json. The Radar, the alerts and Dark Knight Live read it. It flags; it never decides.
# True route share is not in any free feed - target share stands in for it, and the cards say so.
# usage: python3 snap_watch.py <repo> <snap_counts_2026.csv> <stats_player_week_2026.csv>
import sys, os, json, re, datetime as dt
from zoneinfo import ZoneInfo
import pandas as pd

REPO, SNAPS, STATS = sys.argv[1], sys.argv[2], sys.argv[3]
PT = ZoneInfo("America/Los_Angeles"); NOW = dt.datetime.now(dt.timezone.utc)
def norm(n): return re.sub(r"[^a-z ]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(n or "").lower().replace("-", " ").replace(".", ""))).strip().replace("  ", " ")
LG = {1: ("DK I", "2"), 2: ("DK II", "7"), 3: ("DK III", "2"), 4: ("DK IV", "6")}
POS = ("RB", "WR", "TE")

s = pd.read_csv(SNAPS, low_memory=False)
s = s[(s.season == 2026) & (s.game_type == "REG") & s.position.isin(POS)]
t = pd.read_csv(STATS, low_memory=False)
t = t[(t.season == 2026) & (t.season_type == "REG")]
THRU = int(s.week.max())
# team games played (a man with no row in a game his team played logged 0 snaps or was out)
tg = {}
for tm, w in s[["team", "week"]].drop_duplicates().itertuples(index=False): tg.setdefault(tm, set()).add(int(w))
ts = {(norm(r.player_display_name), int(r.week)): (float(r.target_share or 0), int(r.targets or 0), int(r.carries or 0))
      for r in t[["player_display_name", "week", "target_share", "targets", "carries"]].itertuples(index=False) if isinstance(r.player_display_name, str)}

P = {}
for r in s.itertuples(index=False):
    k = norm(r.player)
    p = P.setdefault(k, dict(n=r.player, pos=r.position, tm=r.team, wk={}))
    p["wk"][int(r.week)] = (round(float(r.offense_pct) * 100), int(r.offense_snaps))
    p["tm"] = r.team if int(r.week) >= max(p["wk"]) else p["tm"]          # latest team (trades)
def series(p, n=6):
    ws = sorted(w for w in tg.get(p["tm"], set()))[-n:]
    return [(w, *(p["wk"].get(w, (0, 0))), *(ts.get((norm(p["n"]), w), (0.0, 0, 0)))) for w in ws]   # (wk, snap%, snaps, tshare, tgt, car)
def avg(v): return sum(v) / len(v) if v else 0

# ownership from the Yahoo roster reads the Dispatch just made
OWN = {}
for k, (lab, me) in LG.items():
    o = {}
    try:
        for ln in open(os.path.join(REPO, f"yahoo_drop/scout/dk{k}_rosters_live.txt")):
            if ln.startswith("#"): continue
            x = ln.rstrip("\n").split("|")
            if len(x) >= 5: o[norm(x[2])] = ("mine" if x[0] == me else "team" + x[0], x[1])
    except FileNotFoundError: pass
    wv = set()
    try:
        body = "|".join(l for l in open(os.path.join(REPO, f"yahoo_drop/scout/dk{k}_waivers.txt")) if not l.startswith("#"))
        wv = {norm(x.split("/")[0]) for x in body.replace("\n", "|").split("|") if x.strip()}
    except FileNotFoundError: pass
    OWN[lab] = (o, wv)

def fmt(sr): return " · ".join(f"W{w} {sp}%" for w, sp, *_ in sr[-4:])
def tfmt(sr): return " · ".join(f"W{w} {round(tsh * 100)}%" for w, sp, sn, tsh, *_ in sr[-4:])

rise, fall = [], []
for k, p in P.items():
    sr = series(p)
    if len(sr) < 4: continue
    last2, prev2 = sr[-2:], sr[-4:-2]
    d_s = avg([x[1] for x in last2]) - avg([x[1] for x in prev2])
    d_t = avg([x[3] for x in last2]) - avg([x[3] for x in prev2])
    lw = sr[-1]
    p.update(sr=sr, d_s=round(d_s), d_t=round(d_t * 100))
    snap_up = d_s >= 15 and lw[1] >= 50 and lw[2] >= 20
    tgt_up = d_t >= .07 and lw[3] >= .15 and lw[4] >= 4
    if snap_up or tgt_up: rise.append(k)
    # fallers: only games he actually played count (a missed game is an injury, not a role change)
    pl = [x for x in sr if x[2] > 0]
    if len(pl) >= 4 and sr[-1][2] > 0:
        f_s = avg([x[1] for x in pl[-2:]]) - avg([x[1] for x in pl[-4:-2]])
        if f_s <= -15 and pl[-1][1] < 65: p["f_s"] = round(f_s); fall.append(k)
# INJURY OPENING (one game is enough): a man who jumped to 70%+ of snaps last game, 30+ points over his usual, while a teammate
# at his position who normally played 60%+ fell under 25% the same game (got hurt / left early) - the role just changed hands
OPEN = {}
for k, p in P.items():
    if "sr" not in p: continue
    sr = p["sr"]; lw = sr[-1]; before = [x[1] for x in sr[:-1] if x[2] > 0]
    if lw[1] < 70 or not before or lw[1] - avg(before[-3:]) < 30: continue
    for k2, q in P.items():
        if q is p or q["tm"] != p["tm"] or q["pos"] != p["pos"] or "sr" not in q: continue
        qb = [x[1] for x in q["sr"][:-1] if x[2] > 0]
        if q["sr"][-1][0] == lw[0] and q["sr"][-1][1] < 25 and qb and avg(qb[-3:]) >= 60:
            OPEN[k] = (q["n"], round(avg(qb[-3:])), q["sr"][-1][1]); break
for k in OPEN:
    if k not in rise: rise.append(k)

def took_from(p):   # the same-team, same-position man whose share fell (or who stopped playing) over the same games
    best = None
    for k2, q in P.items():
        if q is p or q["tm"] != p["tm"] or q["pos"] != p["pos"] or "sr" not in q: continue
        if q["d_s"] <= -15 and (best is None or q["d_s"] < best[1]): best = (q["n"], q["d_s"], q["sr"][-1][1])
    return best

def ratcliffe():
    R = {}
    try:
        for r in pd.read_csv(os.path.join(REPO, "dispatch_out/ftn_scored.csv")).itertuples(index=False):
            R[(str(r.lg), norm(r.name))] = (r.wk, r.ros_pg)
    except Exception: pass
    C = {}
    try:
        for r in pd.read_csv(os.path.join(REPO, "dispatch_out/clay_scored.csv")).itertuples(index=False):
            C[(str(r.lg), norm(r.name))] = [r.w15, r.w16, r.w17]
    except Exception: pass
    return R, C
RAT, CLAY = ratcliffe()
def f1(x):
    try: return None if x is None or x != x else round(float(x), 1)
    except Exception: return None

FLAGS = {}
for n_, (lab, me) in LG.items():
    o, wv = OWN[lab]; out = []
    for k in rise:
        p = P[k]
        if k in o: continue
        tf = took_from(p); lw = p["sr"][-1]
        why = []
        if k in OPEN:
            q = OPEN[k]; why.append(f"injury opening: {lw[1]}% of snaps last game (W{lw[0]}) while {q[0]} fell to {q[2]}% from his usual {q[1]}%")
        if p["d_s"] >= 15: why.append(f"snap share up {p['d_s']} points ({fmt(p['sr'])})")
        if p["d_t"] >= 7: why.append(f"target share up {p['d_t']} points ({tfmt(p['sr'])})")
        rp = RAT.get((str(n_), k)); cl = CLAY.get((str(n_), k))
        out.append(dict(kind="riser", opening=OPEN.get(k, [None])[0], name=p["n"], pos=p["pos"], tm=p["tm"], avail="waivers" if k in wv else "free agent",
                        why=why, took=(f"{OPEN[k][0]} ({OPEN[k][2]}% of snaps last game, usually {OPEN[k][1]}%)" if k in OPEN else f"{tf[0]} (snaps down {abs(tf[1])} points, {tf[2]}% last game)" if tf else None),
                        snaps=fmt(p["sr"]), tshare=tfmt(p["sr"]), last=lw[1], d_s=p["d_s"], d_t=p["d_t"],
                        ratcliffe_wk=f1(rp[0]) if rp else None, ratcliffe_ros=f1(rp[1]) if rp else None,
                        clay_po=[f1(x) for x in cl] if cl else None))
    out.sort(key=lambda x: (not x["opening"], -P[norm(x["name"])]["sr"][-1][0], -(max(x["d_s"], 0) + 2 * max(x["d_t"], 0))))   # newest openings first
    mine = []
    for k in fall:
        if o.get(k, ("",))[0] != "mine": continue
        p = P[k]; rp = RAT.get((str(n_), k))
        mine.append(dict(kind="faller", name=p["n"], pos=p["pos"], tm=p["tm"], slot=o[k][1], snaps=fmt(p["sr"]), tshare=tfmt(p["sr"]),
                         last=p["sr"][-1][1], d_s=p.get("f_s", p["d_s"]), d_t=p["d_t"], ratcliffe_ros=f1(rp[1]) if rp else None))
    FLAGS[lab] = out[:6] + mine

# a compact line for every man on any of Dom's rosters or this week's opponents (DK Live's player sheet)
LINES = {}
for lab, (o, wv) in OWN.items():
    for k in o:
        p = P.get(k)
        if p and "sr" in p: LINES[k] = dict(s=fmt(p["sr"]), t=tfmt(p["sr"]), d=p["d_s"], dt=p["d_t"])
for lab, v in FLAGS.items():          # the flagged men too (a riser isn't on a roster yet)
    for x in v:
        p = P.get(norm(x["name"]))
        if p and "sr" in p: LINES[norm(x["name"])] = dict(s=fmt(p["sr"]), t=tfmt(p["sr"]), d=p["d_s"], dt=p["d_t"])
J = dict(built=NOW.astimezone(PT).strftime("%a %b %-d %Y %-I:%M %p PT"), through_week=THRU,
         source="nflverse snap counts + weekly target share (free); route share is not in a free feed - target share stands in",
         rule="riser: free/waiver man, snaps +15 pts (last 2 games vs 2 before, 50%+ and 20+ snaps last game) or target share +7 pts (15%+, 4+ targets); faller: your man, snaps -15 pts and under 65%",
         flags=FLAGS, lines=LINES)
json.dump(J, open(os.path.join(REPO, "dispatch_out/snap_watch.json"), "w"), indent=1)
print(f"SNAP WATCH through week {THRU}: " + " | ".join(f"{lab} {sum(1 for x in v if x['kind']=='riser')} risers, {sum(1 for x in v if x['kind']=='faller')} fallers" for lab, v in FLAGS.items()))
for lab, v in FLAGS.items():
    for x in v: print(f"  {lab} {x['kind']:6} {x['name']:22} {x['pos']} {x['tm']:3} {x['snaps']} | tgt {x['tshare']}" + (f" | took from {x['took']}" if x.get("took") else ""))
