"""THE SIMULATOR (Oct 28 2026, Dom: "run sims as another test of my teams ... use it with possible pickups or drops").
Plays every remaining regular-season game in each of Dom's four leagues thousands of times, then the playoff cut.

Inputs (all already made by the Dispatch build):
  /home/claude/dksys/scout/sim_input_DK*.json   every team's players with the Scout's value for each week (byes, men out,
                                                backups losing work when a starter returns, Yahoo blended in) + the best
                                                free agents and waiver players, same numbers
  dispatch_out/scoreboard/graded.csv            every projection we have graded against what really happened - this is
                                                where each player's range of outcomes comes from (how far real scores
                                                land from the projection, by position, bigger misses for bigger numbers)
  yahoo_drop/sim/league_schedule.json           each league's matchups through Week 14, playoff settings, team names
  yahoo_drop/_inbox/pull_*.json (latest)        standings: record, points for, divisions

How one season is played: every team starts its best lineup each week (Dom's rule: assume rivals play their best).
Each starter's score = his weekly value + a miss drawn from real graded misses for his position, sized to his value;
men on the same NFL team move together a little (a shared game factor). Questionable this week: 15% chance of a zero,
doubtful 60%. Wins, points for, the weekly median game (DK IV), division winners (DK I, DK III) decide the 6 seeds.

What-if: the same random draws are replayed with a roster change, so the difference is the move, not luck.
Lineup check: for this week, each legal bench-for-starter swap is replayed to see if it raises the chance to win.
"""
import json, glob, os, re, sys, math, datetime as dt
import numpy as np, pandas as pd

REPO = os.environ.get("DK_REPO", "/home/claude/dk-feeds")
SCOUT = os.environ.get("DK_SCOUT_DIR", "/home/claude/dksys/scout")
N = int(os.environ.get("DK_SIMS", "10000"))
LG = {"DKI": "269381", "DKII": "1519795", "DKIII": "1507991", "DKIV": "864215"}
LAB = {"DKI": "DK I", "DKII": "DK II", "DKIII": "DK III", "DKIV": "DK IV"}
REG_LAST = 14
RHO = 0.20                     # same-NFL-team pull (QB with his receivers, a backfield with its offense)
ZERO = {"Q": .15, "D": .60}    # this week only: chance a questionable / doubtful man scores nothing
KDEF_SD = {"K": 4.5, "DEF": 6.5}
FLEX = {"FLEX": ("RB", "WR", "TE"), "SUPERFLEX": ("QB", "RB", "WR", "TE")}
def ok(slot): return FLEX.get(slot, (slot,))

# ---------------------------------------------------------------- the range of outcomes, from graded projections
class Noise:
    def __init__(self, graded, weeks=None):
        g = pd.read_csv(graded)
        if weeks is not None: g = g[g.week.isin(weeks)]
        g = g.dropna(subset=["actual"]).copy()
        g["p"] = g[["gotham", "sleeper", "yahoo"]].mean(axis=1)
        g = g[g.p > 0]
        self.fit, self.pool = {}, {}
        for pos, d in g.groupby("pos"):
            r = (d.actual - d.p).values; p = d.p.values
            # spread grows with the projection: |miss| * sqrt(pi/2) estimates the sd; least squares on a + b*p
            y = np.abs(r) * math.sqrt(math.pi / 2); A = np.vstack([np.ones_like(p), p]).T
            a, b = np.linalg.lstsq(A, y, rcond=None)[0]; a = max(a, 1.5); b = max(b, 0.0)
            z = r / (a + b * p); z = (z - z.mean()) / z.std()
            self.fit[pos] = (float(a), float(b)); self.pool[pos] = z
        self.n = {pos: len(z) for pos, z in self.pool.items()}
    def sd(self, pos, m):
        if pos in KDEF_SD: return np.full_like(m, KDEF_SD[pos], dtype=float)
        a, b = self.fit.get(pos, self.fit.get("WR")); return a + b * m
    def z(self, pos, rng, shape):
        if pos in KDEF_SD or pos not in self.pool: return rng.standard_normal(shape)
        return rng.choice(self.pool[pos], size=shape)

def draw(noise, rng, players, n, zero_now=False, tf=None):
    """players: list of (mean, pos, nfl, ytag). returns array [n, len(players)] of scores."""
    out = np.zeros((n, len(players)))
    for j, (m, pos, nfl, yt) in enumerate(players):
        if m <= 0: continue
        e = noise.z(pos, rng, n)
        if tf is not None and nfl in tf: e = math.sqrt(RHO) * tf[nfl] + math.sqrt(1 - RHO) * e
        s = m + noise.sd(pos, np.array([m]))[0] * e
        s = np.maximum(s, 0.0 if pos == "K" else (-4.0 if pos == "DEF" else -2.0))
        if zero_now and yt in ZERO: s = np.where(rng.random(n) < ZERO[yt], 0.0, s)
        out[:, j] = s
    return out

# ---------------------------------------------------------------- lineups
def best_lineup(players, slots, wk):
    """players: list of dicts with wk values; greedy the way the Scout fills seats (fixed slots first, flex last)."""
    pool = sorted(((p["wk"].get(str(wk), 0.0), p["pos"], i) for i, p in enumerate(players) if p.get("slot") != "IR" or p["wk"].get(str(wk), 0) > 0),
                  reverse=True)
    used, out = set(), []
    order = sorted(range(len(slots)), key=lambda i: slots[i] in FLEX)
    pick = {}
    for si in order:
        s = slots[si]
        c = next(((v, i) for v, pos, i in pool if i not in used and pos in ok(s)), None)
        if c: used.add(c[1]); pick[si] = c[1]
    return [pick.get(si) for si in range(len(slots))]

# ---------------------------------------------------------------- league data
def latest_pull():
    fs = sorted(glob.glob(f"{REPO}/yahoo_drop/_inbox/pull_*.json"))
    return json.load(open(fs[-1])) if fs else None

def standings(lid, names):
    d = latest_pull(); rec = {}; divs = {}
    if not d: return rec, divs, "no standings file"
    f = next((v for k, v in d["files"].items() if "standings" in k), "")
    inv = {v.replace("’", "'"): k for k, v in names.items()}
    for line in f.splitlines():
        if not line.startswith(lid + "#"): continue
        div = None
        for item in line.split("#", 1)[1].split("|"):
            x = item.split("^")
            if len(x) < 4: div = item.strip(); continue
            nm = x[1].replace("’", "'"); tid = inv.get(nm)
            if tid is None and nm.startswith("Dark Knight"): tid = next((k for k, v in names.items() if v.startswith("Dark Knight")), None)
            if tid is None: continue
            w, l, t = (int(a) for a in x[2].split("-"))
            pf = float(x[4] if lid != "864215" else x[3])
            rec[tid] = dict(w=w, l=l, t=t, pf=pf, name=names[tid]); divs[tid] = div
    return rec, divs, d.get("read_pt", "")

def load_league(lgk):
    S = json.load(open(f"{SCOUT}/sim_input_{lgk}.json"))
    f = float(S.get("yb_factor", 1.0))
    for t, R in S["teams"].items():          # even out model-only rivals vs Yahoo-blended Dom (see the Scout's note)
        for p in R:
            if not p.get("yb") and f != 1.0: p["wk"] = {w: round(v * f, 2) for w, v in p["wk"].items()}
    SCH = json.load(open(f"{REPO}/yahoo_drop/sim/league_schedule.json"))
    lid = LG[lgk]; names = SCH["names"][lid]; cfg = SCH["settings"][lid]
    sched = {int(w): [tuple(p.split("-")) for p in s.split()] for w, s in SCH["schedule"][lid].items()}
    rec, divs, stamp = standings(lid, names)
    # this week, for the two teams in Dom's game: the average of Gotham, Sleeper and Yahoo (the most accurate single
    # number on the scoreboard so far) replaces the Scout's value where the meter has all of them
    now = int(S["now"]); me = str(S["me"]); used = 0
    mf = next((f for f in (os.path.join(os.environ.get("DK_METER", ""), f"meter_wk{now}.json"), f"{REPO}/dispatch_out/meter_wk{now}.json") if f and os.path.exists(f)), None)
    if mf:
        M = json.load(open(mf))["leagues"].get(LAB[lgk])
        opp = next((b if a == me else a for a, b in sched.get(now, []) if me in (a, b)), None)
        if M and opp:
            def k_(n): return re.sub(r"[^a-z]", "", re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", "", n.lower()))
            for side, tid in (("me", me), ("op", opp)):
                blend = {}
                rows = list((M.get("starters") or {}).get(side, [])) + (list(M.get("bench") or []) if side == "me" else [])
                for p in rows:
                    if True:
                        v = [p.get(c) for c in ("gotham", "sleeper", "yahoo") if isinstance(p.get(c), (int, float))]
                        if len(v) >= 2: blend[k_(p["player"])] = sum(v) / len(v)
                for p in S["teams"][tid]:
                    b = blend.get(k_(p["name"]))
                    if b is not None and p["wk"].get(str(now), 0) > 0: p["wk"][str(now)] = round(b, 2); used += 1
    return dict(lgk=lgk, S=S, lid=lid, names=names, cfg=cfg, sched=sched, rec=rec, divs=divs, stamp=stamp, blend_used=used)

# ---------------------------------------------------------------- one league, all remaining games
def season(L, noise, n=N, seed=7, rosters=None, lineups_override=None):
    """returns dict with per-team playoff %, wins, Dom's weekly win %, score samples for this week."""
    S = L["S"]; slots = S["slots"]; now = int(S["now"]); me = str(S["me"])
    rosters = rosters or S["teams"]
    teams = sorted(rosters, key=int)
    rng = np.random.default_rng(seed)
    nfl_teams = sorted({p["nfl"] for t in teams for p in rosters[t]} | {p["nfl"] for p in S["pool"]})
    W = {t: np.full(n, L["rec"].get(t, {}).get("w", 0), float) for t in teams}
    PF = {t: np.full(n, L["rec"].get(t, {}).get("pf", 0.0)) for t in teams}
    out = dict(week_win={}, week_scores={}, lineups={})
    for wk in range(now, REG_LAST + 1):
        tf = {k: v for k, v in zip(nfl_teams, rng.standard_normal((len(nfl_teams), n)))}
        score = {}
        for t in teams:
            lu = (lineups_override or {}).get((t, wk)) or best_lineup(rosters[t], slots, wk)
            pl = [rosters[t][i] for i in lu if i is not None]
            arr = draw(noise, rng, [(p["wk"].get(str(wk), 0.0), p["pos"], p["nfl"], p.get("ytag", "")) for p in pl], n, zero_now=(wk == now), tf=tf)
            score[t] = arr.sum(axis=1)
            if t == me and wk == now: out["lineups"][wk] = [(slots[k], rosters[t][i]["name"] if i is not None else None) for k, i in enumerate(lu)]
        med = np.median(np.vstack([score[t] for t in teams]), axis=0) if L["cfg"]["median"] else None
        for a, b in L["sched"].get(wk, []):
            if a not in score or b not in score: continue
            wa = (score[a] > score[b]).astype(float) + .5 * (score[a] == score[b])
            W[a] += wa; W[b] += 1 - wa
            if me in (a, b):
                mine = wa if a == me else 1 - wa; out["week_win"][wk] = float(mine.mean())
                if wk == now: out["week_scores"] = dict(me=score[me], opp=score[b if a == me else a], opp_id=(b if a == me else a))
        if med is not None:
            for t in teams: W[t] += (score[t] > med).astype(float)
        for t in teams: PF[t] += score[t]
    # playoff cut: 6 teams; division winners first where the league seeds them on top
    T = np.array(teams); Wm = np.vstack([W[t] for t in teams]); Pm = np.vstack([PF[t] for t in teams])
    key = Wm * 1e5 + Pm                      # wins, then points for
    inn = np.zeros_like(Wm, dtype=bool); seed1 = np.zeros_like(Wm)
    if L["cfg"]["division_winners_top_seeds"] and L["divs"]:
        for dv in set(L["divs"].values()):
            idx = [i for i, t in enumerate(teams) if L["divs"].get(t) == dv]
            if not idx: continue
            wi = np.array(idx)[np.argmax(key[idx], axis=0)]
            inn[wi, np.arange(n)] = True
    order = np.argsort(-key, axis=0)
    for c in range(n):
        k = int(inn[:, c].sum())
        for i in order[:, c]:
            if k >= 6: break
            if not inn[i, c]: inn[i, c] = True; k += 1
    rank = np.argsort(np.argsort(-key, axis=0), axis=0) + 1
    out["teams"] = {t: dict(name=L["names"].get(t, t), playoff=float(inn[i].mean()), wins=float(Wm[i].mean()),
                            first=float((rank[i] == 1).mean())) for i, t in enumerate(teams)}
    out["me"] = me
    return out

def whatif(L, noise, drop, add, n=N, seed=7):
    """replay the same draws with Dom's roster changed: drop a name, add a pool player."""
    S = L["S"]; me = str(S["me"]); R = {t: list(v) for t, v in S["teams"].items()}
    pa = next((p for p in S["pool"] if p["name"] == add), None)
    if pa is None: return None
    R[me] = [p for p in R[me] if p["name"] != drop] + [dict(pa, slot="BN")]
    return season(L, noise, n, seed, rosters=R)

def lineup_swaps(L, noise, n=N, seed=11):
    """this week only: draw every man on Dom's roster and the opponent's best lineup ONCE, then score each legal
    bench-for-starter swap on the same draws (so the difference is the swap, not luck)."""
    S = L["S"]; me = str(S["me"]); now = int(S["now"]); slots = S["slots"]; R = S["teams"][me]
    opp = next((b if a == me else a for a, b in L["sched"].get(now, []) if me in (a, b)), None)
    if opp is None: return None, []
    rng = np.random.default_rng(seed)
    nfl = sorted({p["nfl"] for p in R} | {p["nfl"] for p in S["teams"][opp]})
    tf = {k: v for k, v in zip(nfl, rng.standard_normal((len(nfl), n)))}
    mine = draw(noise, rng, [(p["wk"].get(str(now), 0.0), p["pos"], p["nfl"], p.get("ytag", "")) for p in R], n, zero_now=True, tf=tf)
    olu = [i for i in best_lineup(S["teams"][opp], slots, now) if i is not None]
    OP = S["teams"][opp]
    theirs = draw(noise, rng, [(OP[i]["wk"].get(str(now), 0.0), OP[i]["pos"], OP[i]["nfl"], OP[i].get("ytag", "")) for i in olu], n, zero_now=True, tf=tf).sum(axis=1)
    lu = best_lineup(R, slots, now); idx = [i for i in lu if i is not None]
    def win(ix): s_ = mine[:, ix].sum(axis=1); return float(((s_ > theirs) + .5 * (s_ == theirs)).mean())
    base = win(idx)
    starters = set(idx); bench = [i for i, p in enumerate(R) if i not in starters and p["wk"].get(str(now), 0) > 0 and p.get("slot") != "IR"]
    res = []
    for k, si in enumerate(lu):
        if si is None: continue
        for b in bench:
            if R[b]["pos"] not in ok(slots[k]): continue
            alt = [b if i == si else i for i in idx]
            w = win(alt)
            res.append(dict(out=R[si]["name"], into=R[b]["name"], slot=slots[k], win=w, delta=w - base,
                            mean_out=R[si]["wk"][str(now)], mean_in=R[b]["wk"][str(now)]))
    return base, sorted(res, key=lambda x: -x["delta"])

# ---------------------------------------------------------------- run all four, write the report
def main():
    noise = Noise(f"{REPO}/dispatch_out/scoreboard/graded.csv")
    od = f"{REPO}/dispatch_out/sim"; os.makedirs(od, exist_ok=True)
    now_pt = dt.datetime.now(dt.timezone(dt.timedelta(hours=-7)))
    stamp = f"{now_pt:%a %b} {now_pt.day}, {now_pt.hour % 12 or 12}:{now_pt:%M} {'AM' if now_pt.hour < 12 else 'PM'} PT"
    J = dict(run=stamp, sims=N, noise={p: dict(a=round(a, 2), b=round(b, 3), n=noise.n[p]) for p, (a, b) in noise.fit.items()}, leagues={})
    T = [f"THE SIMULATOR - {stamp} - {N:,} seasons per league, best lineups for everyone, misses drawn from {sum(noise.n.values())} graded projections"]
    for lgk in LG:
        try: L = load_league(lgk)
        except Exception as e:
            T.append(f"\n{LAB[lgk]}: NOT RUN - {e}"); continue
        S = L["S"]; me = str(S["me"]); now = int(S["now"])
        base = season(L, noise)
        mt = base["teams"][me]; ws = base["week_scores"]
        wk_win = base["week_win"].get(now, float("nan"))
        p10, p50, p90 = (np.percentile(ws["me"], q) for q in (10, 50, 90)) if ws else (0, 0, 0)
        o10, o50, o90 = (np.percentile(ws["opp"], q) for q in (10, 50, 90)) if ws else (0, 0, 0)
        lw, allswaps = lineup_swaps(L, noise)
        swaps = [s for s in allswaps if s["delta"] >= .005][:3]
        # pickups: the Scout's pool players that would start for Dom some week, each with the Scout-style drop (lowest season value)
        mine = S["teams"][me]
        def season_val(p): return sum(v for w, v in p["wk"].items() if int(w) <= REG_LAST)
        drops = sorted([p for p in mine if p.get("slot") != "IR" and p["pos"] not in ("K",)], key=season_val)
        tests = []
        # men the Scout itself flags as unbacked (no Yahoo or Sleeper number agrees) are not tested - garbage in, garbage out
        try:
            wl = json.load(open(f"{SCOUT}/scout_board_{lgk}.json")).get("watch", [])
            unbacked = {m.group(1) for w in wl for m in [re.match(r"Watch: (.+?) \(", w)] if m and ("isn't backed" in w or "only the Scout's model" in w)}
        except Exception: unbacked = set()
        for pa in [p for p in sorted(S["pool"], key=lambda p: -season_val(p)) if p["name"] not in unbacked][:12]:
            same = [d for d in drops if d["pos"] == pa["pos"]] or drops
            dr = same[0]
            r = whatif(L, noise, dr["name"], pa["name"])
            if r is None: continue
            tests.append(dict(add=pa["name"], pos=pa["pos"], nfl=pa["nfl"], acq=pa.get("acq", ""), drop=dr["name"],
                              playoff=r["teams"][me]["playoff"], d_playoff=r["teams"][me]["playoff"] - mt["playoff"],
                              d_week=r["week_win"].get(now, 0) - wk_win))
        tests.sort(key=lambda x: -x["d_playoff"])
        oppid = ws.get("opp_id") if ws else None
        J["leagues"][lgk] = dict(league=LAB[lgk], week=now, standings_read=L["stamp"], week_win=wk_win, playoff=mt["playoff"], wins=mt["wins"],
                                 first=mt["first"], opp=L["names"].get(oppid, oppid), scores=dict(me=[p10, p50, p90], opp=[o10, o50, o90]),
                                 weeks=base["week_win"], swaps=swaps, tests=tests,
                                 table=sorted(base["teams"].values(), key=lambda x: -x["playoff"]))
        T.append(f"\n{LAB[lgk]} - Week {now} vs {L['names'].get(oppid, oppid)}: win {wk_win:.0%}  |  playoffs {mt['playoff']:.0%}, about {mt['wins']:.1f} wins")
        T.append(f"  Your score: 10% chance under {p10:.0f}, middle {p50:.0f}, 10% chance over {p90:.0f}  |  theirs {o10:.0f} / {o50:.0f} / {o90:.0f}")
        T.append("  Rest of the regular season, chance to win each game: " + ", ".join(f"Wk {w} {v:.0%}" for w, v in sorted(base["week_win"].items()) if w > now))
        for s in swaps: T.append(f"  Lineup: start {s['into']} over {s['out']} ({s['slot']}) - win {lw:.0%} -> {s['win']:.0%} (same draws)")
        if not swaps: T.append("  Lineup: no bench swap raises your chance this week")
        good = [t for t in tests if t["d_playoff"] >= .01]
        for t in good[:4]: T.append(f"  Move test: add {t['add']} ({t['pos']} {t['nfl']}, {t['acq']}), drop {t['drop']} - playoffs {mt['playoff']:.0%} -> {t['playoff']:.0%}")
        if not good: T.append("  Move test: no free agent or waiver player tested raises your playoff odds by 1 point or more")
    json.dump(J, open(f"{od}/sim_latest.json", "w"), indent=1, default=float)
    open(f"{od}/sim_latest.txt", "w").write("\n".join(T) + "\n")
    print("\n".join(T))

if __name__ == "__main__":
    main()
