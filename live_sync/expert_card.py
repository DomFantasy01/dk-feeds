"""EVERY EXPERT ON EVERY PLAYER (Oct 31 2026, Dom: "how the experts are ranking each of these guys ... put all the experts we use ...
guys that give the points and guys that just provide the ranks"; "any of the players you put forth to pick up or drop, include those").
For every man that matters in each league - Dom's starters and bench, the talk/watch list, the injury-call fills and drops, the
simulator's moves and trades - one card:
  POINTS (each in that league's own scoring): Ratcliffe (FTN) this week + rest of season a game, Koerner (FantasyLabs) this week,
          Clay (ESPN) this week + his average over the weeks ahead
  RANKS  (position rank this week, FantasyPros partner feed): Brenton #1, Ciallela #2, Orginski #3, Jahnke #4, Thorman #11 -
          the accuracy leaders who publish ranks, not points. Shown as ranks only, never turned into points.
Writes leagues[..].xp into the meter (the Live sync carries it). Nothing here is a move.
usage: python3 expert_card.py REPO [METER.json]"""
import sys, os, re, csv, json, glob

R = sys.argv[1]; O = os.path.join
if len(sys.argv) > 2: MF = sys.argv[2]
else:
    W = max([int(re.search(r"_wk(\d+)", f).group(1)) for f in glob.glob(O(R, "dispatch_out/meter_wk*.json"))] or [0]); MF = O(R, f"dispatch_out/meter_wk{W}.json")
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower().replace("’", "'")))
def fnum(x):
    try: return round(float(x), 1)
    except Exception: return None
RANKERS = []   # Nov 4 (Dom, Nov 3: the five ranking experts are "all useless"): Brenton, Ciallela, Orginski, Jahnke, Thorman removed
pts = {}   # (lg, key) -> dict
def put(lg, key, **kw): pts.setdefault((lg, key), {}).update({k: v for k, v in kw.items() if v is not None})
for r in csv.DictReader(open(O(R, "dispatch_out/ftn_scored.csv"))) if os.path.exists(O(R, "dispatch_out/ftn_scored.csv")) else []:
    put(r["lg"], nk(r["name"]), r=fnum(r.get("wk")), rr=fnum(r.get("ros_pg")))
for r in csv.DictReader(open(O(R, "dispatch_out/koerner_scored.csv"))) if os.path.exists(O(R, "dispatch_out/koerner_scored.csv")) else []:
    put(r["lg"], nk(r["name"]), k=fnum(r.get("wk")))
for r in csv.DictReader(open(O(R, "dispatch_out/clay_scored.csv"))) if os.path.exists(O(R, "dispatch_out/clay_scored.csv")) else []:
    fut = [float(v) for k, v in r.items() if re.fullmatch(r"w\d+", k or "") and v not in ("", None) and float(v) > 0]
    key = r["key"] if r["pos"] == "DST" else nk(r["name"])
    put(r["lg"], key, c=fnum(r.get("wk")), cr=round(sum(fut) / len(fut), 1) if fut else None)
for r in csv.DictReader(open(O(R, "dispatch_out/vegas_scored.csv"))) if os.path.exists(O(R, "dispatch_out/vegas_scored.csv")) else []:   # Nov 7 (Dom): Vegas props
    put(r["lg"], nk(r["name"]), v=fnum(r.get("wk")), vrk=int(r["rank"]) if (r.get("rank") or "").isdigit() else None, vgap=int(r["ecr_gap"]) if re.fullmatch(r"-?\d+", r.get("ecr_gap") or "") else None,
        vsh=fnum(r.get("vegas_share")), vfill=(r.get("model_fill") or None))
rk, rk_read = {}, ""
try:
    for ln in open(O(R, "yahoo_drop/morning/expert_rankings.txt")):
        if ln.startswith("#"):
            m = re.search(r"read live (.*?) \(", ln); rk_read = rk_read or (m.group(1) if m else ""); continue
        f = ln.rstrip("\n").split("|")
        if len(f) >= 5 and f[3].isdigit(): rk.setdefault(nk(f[4]), {})[f[1]] = (f[2], int(f[3]))
        if len(f) >= 6 and f[3].isdigit() and f[2] == "DST": rk.setdefault(str(f[5]).upper().replace("WSH", "WAS").replace("JAC", "JAX").replace("LAR", "LA") + "DEF", {})[f[1]] = ("DEF", int(f[3]))   # Nov 1: defense ranks, keyed by team
except Exception: pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from outlist import out_now
OUTL = out_now(R, int(re.search(r"_wk(\d+)", MF).group(1)) if re.search(r"_wk(\d+)", MF) else None)
M = json.load(open(MF)); LGN = {"DK I": "1", "DK II": "2", "DK III": "3", "DK IV": "4"}
NICK = {"cardinals": "ARI", "falcons": "ATL", "ravens": "BAL", "bills": "BUF", "panthers": "CAR", "bears": "CHI", "bengals": "CIN", "browns": "CLE",
        "cowboys": "DAL", "broncos": "DEN", "lions": "DET", "packers": "GB", "texans": "HOU", "colts": "IND", "jaguars": "JAX", "chiefs": "KC",
        "raiders": "LV", "chargers": "LAC", "rams": "LA", "dolphins": "MIA", "vikings": "MIN", "patriots": "NE", "saints": "NO", "giants": "NYG",
        "jets": "NYJ", "eagles": "PHI", "steelers": "PIT", "49ers": "SF", "seahawks": "SEA", "buccaneers": "TB", "titans": "TEN", "commanders": "WAS"}
def deft(name, team):
    t = str(team or "").upper().replace("WSH", "WAS").replace("LAR", "LA")
    if not t: t = NICK.get(str(name).lower().split()[-1].replace("d/st", "").strip(), "") or NICK.get(str(name).lower().split()[0], "")
    return t
def look(lg, name, pos, team):
    if pos in ("DEF", "DST") or str(name).lower().split()[-1] in NICK:
        t = deft(name, team); d = dict(pts.get((lg, t + "DEF")) or {}); d.update(pts.get((lg, nk(t + " DEF"))) or {}); return d, "DEF"
    return pts.get((lg, nk(name))) or {}, pos
n_all = 0
for lab, L in (M.get("leagues") or {}).items():
    lg = LGN.get(lab); want = {}
    def add(name, pos=None, team=None, why=""):
        if not name: return
        n = str(name)
        if n not in want: want[n] = dict(pos=pos, team=team, why=why)
    for s in (L.get("starters") or {}).get("me") or []: add(s.get("player"), s.get("pos"), s.get("team"), "starter")
    for b in L.get("bench") or []: add(b.get("player"), b.get("pos"), b.get("team"), "bench")
    T = L.get("talk") or {}
    for t in (T.get("talk") or []) + (T.get("watch") or []): add(t.get("name"), t.get("pos"), t.get("team"), "pickup idea")
    for bk in T.get("backup") or []:
        for x in (bk.get("bench") or []) + (bk.get("fa") or []): add(x.get("name"), x.get("pos"), x.get("team"), "injury fill")
    C = L.get("champ") or {}
    for c in C.get("calls") or []:
        for o in c.get("options") or []: add(o.get("add"), None, None, "injury fill"); add(o.get("drop"), o.get("drop_pos"), None, "possible drop")
    for m in C.get("moves") or []: add(m.get("add"), m.get("pos"), m.get("nfl"), "pickup idea"); add(m.get("drop"), None, None, "possible drop")
    for t in C.get("trades") or []:
        add(t.get("get"), t.get("get_pos"), None, "trade target")
        for g in t.get("give") or []: add(g, None, None, "trade piece")
    out = {}
    for name, meta in want.items():
        pos = meta["pos"]; team = meta["team"]; k_ = nk(name)
        p, pos = look(lg, name, pos, team)
        r_ = {}
        for full, short, fp in RANKERS:
            x = (rk.get(deft(name, team) + "DEF" if pos == "DEF" else k_) or {}).get(full)
            if x: r_[short] = x[1]; pos = pos or x[0]
        if not p and not r_: continue
        p = dict(p)
        if nk(name) in OUTL:   # Oct 31 (Dom): ruled out = zero this week for every expert, until their files catch up
            p.update({x: 0.0 for x in ("r", "k", "c", "v") if x in p or x != "v"}); p["out"] = OUTL[nk(name)]
        out[name] = dict(pos=pos, why=meta["why"], **p, rk=r_)
    L["xp"] = dict(players=out, rankers=[[s, fp] for _, s, fp in RANKERS], ranks_read=rk_read,
                   points_note="Ratcliffe, Koerner, Clay: each expert's own projection in this league's scoring; Vegas: prop stat lines, same scoring (a check, not an expert)")
    n_all += len(out)
    for side in ("me", "op"):   # the meter's own copies too, so no page shows a stale number for a man who is out
        for s in (L.get("starters") or {}).get(side) or []:
            if s.get("actual") is None and nk(s.get("player")) in OUTL:
                for x in ("ratcliffe", "koerner", "clay", "vegas", "gotham", "sleeper"):
                    if s.get(x) is not None: s[x] = 0.0
                s["out_zero"] = OUTL[nk(s.get("player"))]
    for b in L.get("bench") or []:
        if nk(b.get("player")) in OUTL:
            for x in ("ratcliffe", "koerner", "clay", "vegas", "gotham", "sleeper"):
                if b.get(x) is not None: b[x] = 0.0
            b["out_zero"] = OUTL[nk(b.get("player"))]
# Oct 31 (Dom: "is Clay earning his spot?"): every source's miss against what players actually scored, week by week (the
# scoreboard freezes each number pregame). Average points missed per player - lower is better - and how many players graded.
try:
    G = list(csv.DictReader(open(O(R, "dispatch_out/scoreboard/graded.csv"))))
    acc = {}
    for s_ in ("ratcliffe", "koerner", "clay", "vegas", "yahoo", "gotham"):
        for w_ in sorted({int(r["week"]) for r in G}):
            d = [abs(float(r[s_]) - float(r["actual"])) for r in G if int(r["week"]) == w_ and r.get(s_) not in ("", None) and r.get("actual") not in ("", None)]
            if d: acc.setdefault(s_, {})[str(w_)] = [round(sum(d) / len(d), 2), len(d)]
    M["acc"] = dict(src=acc, note="average points missed per player (lower is better), each source's number frozen before kickoff")
except Exception as _e: print("accuracy skipped:", _e)
json.dump(M, open(MF, "w"), ensure_ascii=False)
print(f"EXPERT CARDS: {n_all} player cards across four leagues (ranks read {rk_read})")
