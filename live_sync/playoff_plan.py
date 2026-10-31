"""ROAD TO THE PLAYOFFS (Oct 31 2026, Dom: "I'm working my way to a championship ... we got to look at this whole puzzle. And what
pieces do we need to make it to the playoffs? And possibly win." / "incremental improvements").
One plan per league, built every Dispatch build from the simulator's own inputs (dispatch_out/sim/inputs) and the same
10,000-season engine (dksys/sim/sim.py):
  where he stands   - playoff odds for the season, projected wins, rank among the 12 by playoff odds, each remaining game's
                      chance to win with the opponent's name
  playoff strength  - his best lineup's average projected points over Weeks 15-17 vs every other team's (the title rounds)
  what each bench man is worth - playoff odds lost if he were simply dropped (shows who is safe to let go)
  ranked moves      - free agents tested against the cheapest drops, each with playoff odds and this week's chance, flagged
                      when the man let go would start for a rival. Every move is "let's talk" - Dom makes every move.
Numbers move about 1 point run to run from the random draws, so anything under +1 is a wash and is said so.
usage: python3 playoff_plan.py REPO [DKI DKII ...]   (default DKI - the first league, as Dom asked)"""
import os, sys, json, csv, re, glob
import numpy as np
R = sys.argv[1]; LGS = sys.argv[2:] or ["DKI"]
os.environ.setdefault("DK_REPO", R)
os.environ.setdefault("DK_SCOUT_DIR", os.path.join(R, "dispatch_out", "sim", "inputs"))
for d in ("/home/claude/dksys/sim", os.path.join(R, "system", "dksys", "sim")):
    if os.path.exists(os.path.join(d, "sim.py")): sys.path.insert(0, d); break
import sim as SM
N = int(os.environ.get("DK_PLAN_SIMS", "8000"))
LAB = {"DKI": "DK I", "DKII": "DK II", "DKIII": "DK III", "DKIV": "DK IV"}; LGN = {"DKI": "1", "DKII": "2", "DKIII": "3", "DKIV": "4"}
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower()))
def rat_ros(lgn):
    out = {}
    try:
        for r in csv.DictReader(open(os.path.join(R, "dispatch_out", "ftn_scored.csv"))):
            if r["lg"] == lgn and r.get("ros_pg"): out[nk(r["name"])] = float(r["ros_pg"])
    except Exception: pass
    return out
noise = SM.Noise(os.path.join(R, "dispatch_out", "scoreboard", "graded.csv"))
meter_f = sorted(glob.glob(os.path.join(R, "dispatch_out", "meter_wk*.json")), key=lambda p: int(re.search(r"_wk(\d+)", p).group(1)))[-1]
M = json.load(open(meter_f)); BUILT = M.get("built_pt")
out = {"built": BUILT, "sims": N, "leagues": {}}
for lgk in LGS:
    try: L = SM.load_league(lgk)
    except Exception as e: print(f"PLAN {lgk}: not built - {e}"); continue
    S = L["S"]; me = str(S["me"]); slots = S["slots"]; now = int(S["now"]); last = min(17, int(S.get("last") or 17))
    def po_pts(Rm): return float(np.mean([sum(Rm[i]["wk"].get(str(w), 0) for i in SM.best_lineup(Rm, slots, w) if i is not None) for w in (15, 16, 17)]))
    base = SM.season(L, noise, N); B = base["teams"][me]; w0 = base["week_win"].get(now, 0.0)
    table = sorted(((v["playoff"], t) for t, v in base["teams"].items()), reverse=True)
    rank = [t for _, t in table].index(me) + 1
    opp_of = {wk: next((b if a == me else a for a, b in L["sched"].get(wk, []) if me in (a, b)), None) for wk in range(now, 15)}
    games = [dict(wk=wk, opp=L["names"].get(opp_of[wk], opp_of[wk]), win=round(base["week_win"].get(wk, 0), 3)) for wk in range(now, 15) if opp_of.get(wk)]
    po = sorted(((round(po_pts(Rm), 1), L["names"].get(t, t), t == me) for t, Rm in S["teams"].items()), reverse=True)
    mine = S["teams"][me]; base_po = po_pts(mine)
    # what each bench man (and the weakest starters) is worth: playoff odds lost without him
    lu_now = set(i for i in SM.best_lineup(mine, slots, now) if i is not None)
    worth = []
    for i, p in enumerate(mine):
        if p.get("slot") != "BN": continue                       # bench men only - a starter dropped just leaves a hole
        Rm = {t: list(v) for t, v in S["teams"].items()}; Rm[me] = [q for q in mine if q["name"] != p["name"]]
        r = SM.season(L, noise, N, rosters=Rm)
        worth.append(dict(name=p["name"], pos=p["pos"], bench=p.get("slot") == "BN", d_playoff=round(r["teams"][me]["playoff"] - B["playoff"], 3),
                          d_week=round(r["week_win"].get(now, 0) - w0, 3), d_po=round(po_pts(Rm[me]) - base_po, 1)))
    worth.sort(key=lambda x: x["d_playoff"])
    # does the man let go help a rival? his Ratcliffe rest-of-season vs each rival's weakest starter at his position
    RR = rat_ros(LGN[lgk]); help_ = {}
    for p in mine:
        v = RR.get(nk(p["name"]))
        if v is None or p["pos"] in ("K", "DEF"): continue
        who = []
        for t, Rm in S["teams"].items():
            if t == me: continue
            st = [RR.get(nk(q["name"]), 0) for q in Rm if q["pos"] == p["pos"] and q.get("slot") not in ("BN", "IR")]
            if st and v > min(st): who.append(L["names"].get(t, t))
        help_[p["name"]] = who
    # moves: the cheapest bench drops x the best free agents at each position (rest of season), plus this week's best
    cheap = [w for w in worth if w["bench"] and w["d_playoff"] > -0.05][:3]
    def sv(p): return sum(v for w, v in p["wk"].items() if now < int(w) <= last)
    bypos = {}
    for p in sorted(S["pool"], key=lambda p: -sv(p)): bypos.setdefault(p["pos"], []).append(p)
    adds = {p["name"]: p for ps in bypos.values() for p in ps[:3]}
    # this week's fill-ins too: the best free agents at each position for THIS week (a hurt or questionable starter's cover)
    for pos in ("RB", "WR", "TE", "QB", "DEF"):
        for p in sorted([q for q in S["pool"] if q["pos"] == pos], key=lambda p: -p["wk"].get(str(now), 0))[:2]: adds.setdefault(p["name"], p)
    moves = []
    for d in cheap:
        for a in adds.values():
            Rm = {t: list(v) for t, v in S["teams"].items()}; Rm[me] = [q for q in mine if q["name"] != d["name"]] + [dict(a, slot="BN")]
            r = SM.season(L, noise, N, rosters=Rm)
            moves.append(dict(add=a["name"], pos=a["pos"], nfl=a["nfl"], acq=a.get("acq", ""), drop=d["name"],
                              d_playoff=round(r["teams"][me]["playoff"] - B["playoff"], 3), d_week=round(r["week_win"].get(now, 0) - w0, 3),
                              d_po=round(po_pts(Rm[me]) - base_po, 1), add_week=a["wk"].get(str(now), 0), helps=help_.get(d["name"], [])))
    moves.sort(key=lambda x: -(x["d_playoff"] + x["d_week"] / 4))
    seen, top = set(), []
    for m in moves:
        if m["add"] in seen: continue
        seen.add(m["add"]); top.append(m)
    out["leagues"][LAB[lgk]] = dict(week=now, standings=L["stamp"], playoff=round(B["playoff"], 3), wins=round(B["wins"], 2), first=round(B["first"], 3),
                                    rank=rank, teams=len(table), race=[dict(team=L["names"].get(t, t), playoff=round(v, 3), me=(t == me)) for v, t in table], week_win=round(w0, 3), games=games,
                                    po_weeks=[dict(pts=a, team=b, me=c) for a, b, c in po], worth=worth, moves=top[:6], built=BUILT,
                                    note="Simulator, " + f"{N:,}" + " seasons per test, same draws; under +1 point is a wash")
    print(f"PLAN {LAB[lgk]}: playoffs {B['playoff']:.0%} (#{rank}), Wk15-17 lineup {base_po:.1f}, best move: "
          + (f"add {top[0]['add']} drop {top[0]['drop']} {top[0]['d_playoff']*100:+.1f} pts" if top else "none"))
json.dump(out, open(os.path.join(R, "dispatch_out", "playoff_plan.json"), "w"), indent=1, default=float)
try:   # ride inside the meter so the hourly Live sync carries it (same as the talk list)
    Mm = json.load(open(meter_f))
    for lab, v in out["leagues"].items():
        if lab in Mm.get("leagues", {}): Mm["leagues"][lab]["plan"] = v
    json.dump(Mm, open(meter_f, "w"), ensure_ascii=False)
except Exception as e: print("PLAN not added to the meter file:", e)
