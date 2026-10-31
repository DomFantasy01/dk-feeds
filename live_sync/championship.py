"""ROAD TO THE CHAMPIONSHIP (Oct 31 2026, Dom: "it's about wins now, how I get placed in the playoffs, and how I do in the
playoffs ... and how does it affect the people I may be playing" / "I want to see the points ... 13 points over the rest of the
year is a waste of time" / "trades have to be powerful for them too, or they won't even respond").

Plays the rest of the season AND the playoff bracket for every team in a league, thousands of times, with PAIRED draws: every
player's random game is fixed by his name and the week, so a move changes only what the move changes (the old engine reshuffled
everyone's luck when one man was added, which hid small moves under noise).
For Dom, per league:
  base      - wins (and the full spread of win totals), playoff odds, the chance of each seed 1-12, and the funnel:
              make it -> reach the semis -> reach the final -> win the title
  moves     - free agents (best rest-of-season, best in the title weeks 15-17, best this week) x his cheapest drops; each with
              wins before/after, playoff odds, likeliest seed, title odds, points per game in the weeks the man would start, and
              "block" - what it would cost Dom if the rival who gains most from that man grabbed him instead
  trades    - one-for-one and two-for-one deals with every rival, screened on both lineups, then played out for BOTH teams;
              only deals that raise both sides' playoff or title odds are kept, each with a one-line pitch for them
  worth     - what each bench man is worth (playoff and title odds lost without him)
Bracket (assumed from the league settings: 6 teams, Weeks 15-17): seeds 1-2 rest in Week 15, 3v6 and 4v5; Week 16 the 1 seed plays
the lowest seed left, the 2 seed the other; Week 17 the final.
Writes dispatch_out/championship.json and rides inside the meter file (leagues[..].champ, and .plan for the card box).
usage: python3 championship.py REPO [DKI DKII DKIII DKIV]"""
import os, sys, json, csv, re, glob, zlib, math, itertools, time
import numpy as np
R = sys.argv[1]; LGS = sys.argv[2:] or ["DKI", "DKII", "DKIII", "DKIV"]
os.environ.setdefault("DK_REPO", R)
os.environ.setdefault("DK_SCOUT_DIR", os.path.join(R, "dispatch_out", "sim", "inputs"))
for d in ("/home/claude/dksys/sim", os.path.join(R, "system", "dksys", "sim")):
    if os.path.exists(os.path.join(d, "sim.py")): sys.path.insert(0, d); break
import sim as SM
N = int(os.environ.get("DK_CHAMP_SIMS", "6000"))
LAB = {"DKI": "DK I", "DKII": "DK II", "DKIII": "DK III", "DKIV": "DK IV"}; LGN = {"DKI": "1", "DKII": "2", "DKIII": "3", "DKIV": "4"}
REG_LAST, PO = 14, (15, 16, 17)
noise = SM.Noise(os.path.join(R, "dispatch_out", "scoreboard", "graded.csv"))
meter_f = sorted(glob.glob(os.path.join(R, "dispatch_out", "meter_wk*.json")), key=lambda p: int(re.search(r"_wk(\d+)", p).group(1)))[-1]
M = json.load(open(meter_f)); BUILT = M.get("built_pt")
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower()))
def crc(*a): return zlib.crc32("|".join(map(str, a)).encode()) & 0xffffffff

class Engine:
    def __init__(self, L):
        self.L = L; self.S = L["S"]; self.me = str(self.S["me"]); self.slots = self.S["slots"]; self.now = int(self.S["now"])
        self.cache = {}; self.tfc = {}
    def tf(self, nfl, wk):
        k = (nfl, wk)
        if k not in self.tfc: self.tfc[k] = np.random.default_rng(crc("tf", nfl, wk)).standard_normal(N)
        return self.tfc[k]
    def pdraw(self, p, wk):
        k = (p["name"], p.get("nfl"), wk, round(p["wk"].get(str(wk), 0.0), 2), p.get("ytag", "") if wk == self.now else "")
        if k in self.cache: return self.cache[k]
        m = p["wk"].get(str(wk), 0.0)
        if m <= 0: s = np.zeros(N)
        else:
            rng = np.random.default_rng(crc(p["name"], p.get("nfl"), wk))
            e = noise.z(p["pos"], rng, N); e = math.sqrt(SM.RHO) * self.tf(p.get("nfl"), wk) + math.sqrt(1 - SM.RHO) * e
            s = m + noise.sd(p["pos"], np.array([m]))[0] * e
            s = np.maximum(s, 0.0 if p["pos"] == "K" else (-4.0 if p["pos"] == "DEF" else -2.0))
            yt = p.get("ytag", "")
            if wk == self.now and yt in SM.ZERO: s = np.where(rng.random(N) < SM.ZERO[yt], 0.0, s)
        self.cache[k] = s; return s
    def score(self, roster, wk):
        lu = SM.best_lineup(roster, self.slots, wk)
        t = np.zeros(N)
        for i in lu:
            if i is not None: t = t + self.pdraw(roster[i], wk)
        return t
    def run(self, rosters):
        L = self.L; teams = sorted(rosters, key=int); n = N
        W = {t: np.full(n, L["rec"].get(t, {}).get("w", 0), float) for t in teams}
        PF = {t: np.full(n, L["rec"].get(t, {}).get("pf", 0.0)) for t in teams}
        week_win = {}
        for wk in range(self.now, REG_LAST + 1):
            sc = {t: self.score(rosters[t], wk) for t in teams}
            med = np.median(np.vstack([sc[t] for t in teams]), axis=0) if L["cfg"]["median"] else None
            for a, b in L["sched"].get(wk, []):
                if a not in sc or b not in sc: continue
                wa = (sc[a] > sc[b]).astype(float) + .5 * (sc[a] == sc[b]); W[a] += wa; W[b] += 1 - wa
                if self.me in (a, b): week_win[wk] = float((wa if a == self.me else 1 - wa).mean())
            if med is not None:
                for t in teams: W[t] += (sc[t] > med).astype(float)
            for t in teams: PF[t] += sc[t]
        T = teams; Wm = np.vstack([W[t] for t in T]); Pm = np.vstack([PF[t] for t in T]); key = Wm * 1e5 + Pm
        # seeds: division winners first where the league does that, then the rest by wins, points
        seeded = np.zeros_like(Wm, dtype=bool)
        if L["cfg"]["division_winners_top_seeds"] and L["divs"]:
            for dv in set(L["divs"].values()):
                idx = [i for i, t in enumerate(T) if L["divs"].get(t) == dv]
                if idx: seeded[np.array(idx)[np.argmax(key[idx], axis=0)], np.arange(n)] = True
        k1 = np.where(seeded, key + 1e12, key)
        order = np.argsort(-k1, axis=0)                     # [12, n] team index by seed
        seed_of = np.argsort(order, axis=0) + 1             # seed (1..12) of each team
        # the bracket
        po = {wk: np.vstack([self.score(rosters[t], wk) for t in T]) for wk in PO}
        cols = np.arange(n)
        def g(ti, wk): return po[wk][ti, cols]
        s = [order[i] for i in range(6)]                    # seed 1..6 team index arrays
        w36 = np.where(g(s[2], 15) >= g(s[5], 15), s[2], s[5]); w45 = np.where(g(s[3], 15) >= g(s[4], 15), s[3], s[4])
        lo_left = np.where(seed_of[w36, cols] > seed_of[w45, cols], w36, w45); hi_left = np.where(lo_left == w36, w45, w36)
        f1 = np.where(g(s[0], 16) >= g(lo_left, 16), s[0], lo_left); f2 = np.where(g(s[1], 16) >= g(hi_left, 16), s[1], hi_left)
        champ = np.where(g(f1, 17) >= g(f2, 17), f1, f2)
        out = {}
        for i, t in enumerate(T):
            sd = seed_of[i]; mk = sd <= 6
            semis = (sd <= 2) | (w36 == i) | (w45 == i)
            out[t] = dict(wins=float(Wm[i].mean()), playoff=float(mk.mean()), semis=float(semis.mean()), final=float(((f1 == i) | (f2 == i)).mean()),
                          title=float((champ == i).mean()), first=float((sd == 1).mean()),
                          seeds=[round(float((sd == k).mean()), 4) for k in range(1, 13)],
                          wins_hist=np.bincount(np.clip(np.round(Wm[i]).astype(int), 0, 28), minlength=15).tolist())   # 28: the median league counts two results a week
        out["_week"] = week_win
        six = Wm[order[5], cols]                            # the 6th seed's final wins in each season = the playoff line
        out["_line"] = dict(median=float(np.median(six)), dist=np.bincount(np.clip(np.round(six).astype(int), 0, 28), minlength=15).tolist())
        mi = T.index(self.me)
        out["_line"]["reach"] = float((Wm[mi] >= np.median(six)).mean())
        return out

def season_val(p, a, b): return sum(v for w, v in p["wk"].items() if a <= int(w) <= b)
def lineup_pts(E, roster, weeks): return sum(sum(roster[i]["wk"].get(str(w), 0.0) for i in SM.best_lineup(roster, E.slots, w) if i is not None) for w in weeks)
def summ(r): return dict(wins=round(r["wins"], 2), playoff=round(r["playoff"], 3), title=round(r["title"], 4), final=round(r["final"], 3), semis=round(r["semis"], 3),
                         seed=int(np.argmax(r["seeds"])) + 1, seeds=r["seeds"], first=round(r["first"], 3))
OUT = {"built": BUILT, "sims": N, "leagues": {}}
for lgk in LGS:
    t0 = time.time()
    try: L = SM.load_league(lgk)
    except Exception as e: print(f"CHAMP {lgk}: not built - {e}"); continue
    E = Engine(L); S = E.S; me = E.me; now = E.now; names = L["names"]
    base_R = {t: list(v) for t, v in S["teams"].items()}
    B = E.run(base_R); Bm = B[me]
    REM = list(range(now, REG_LAST + 1)); ALLW = list(range(now, 18))
    mine = base_R[me]
    def with_(drop_names, adds, t=me, Rbase=None):
        Rm = {k: list(v) for k, v in (Rbase or base_R).items()}
        Rm[t] = [q for q in Rm[t] if q["name"] not in drop_names] + [dict(a, slot="BN") for a in adds]
        return Rm
    def per_game(roster_before, roster_after, weeks):
        d = [lineup_pts(E, roster_after, [w]) - lineup_pts(E, roster_before, [w]) for w in weeks]
        used = [x for x in d if abs(x) > .05]
        return round(sum(d), 1), round(sum(used) / len(used), 1) if used else 0.0, len(used)
    # what each bench man is worth
    worth = []
    for p in mine:
        if p.get("slot") != "BN": continue
        r = E.run(with_([p["name"]], []))[me]
        worth.append(dict(name=p["name"], pos=p["pos"], d_playoff=round(r["playoff"] - Bm["playoff"], 3), d_title=round(r["title"] - Bm["title"], 4), d_wins=round(r["wins"] - Bm["wins"], 2)))
    worth.sort(key=lambda x: x["d_playoff"] + x["d_title"])
    cheap = [w["name"] for w in worth[::-1] if w["d_playoff"] > -0.03][:3]
    # candidate adds: best rest of season, best in the title weeks (the 5-today-20-later men), best this week
    pool = S["pool"]; cand = {}
    for pos in sorted({p["pos"] for p in pool}):
        P = [p for p in pool if p["pos"] == pos]
        for key in (lambda p: -season_val(p, now, 17), lambda p: -season_val(p, 15, 17), lambda p: -p["wk"].get(str(now), 0)):
            for p in sorted(P, key=key)[:2]: cand[p["name"]] = p
    moves = []
    for d in cheap:
        for a in cand.values():
            Rm = with_([d], [a]); rr_ = E.run(Rm); r = rr_[me]
            tot, pg, ng = per_game(mine, Rm[me], ALLW)
            moves.append(dict(add=a["name"], pos=a["pos"], nfl=a.get("nfl"), acq=a.get("acq", ""), drop=d, before=summ(Bm), after=summ(r),
                              d_wins=round(r["wins"] - Bm["wins"], 2), d_playoff=round(r["playoff"] - Bm["playoff"], 3), d_title=round(r["title"] - Bm["title"], 4),
                              pts_total=tot, pts_per_game=pg, games_used=ng, wins_hist=r["wins_hist"], this_week=round(rr_["_week"].get(now, 0) - B["_week"].get(now, 0), 3)))
    # Dom's rule: never drop a man who could come back to hurt him - who would START him (Ratcliffe rest of season, this league)
    RR = {}
    try:
        for r_ in csv.DictReader(open(os.path.join(R, "dispatch_out", "ftn_scored.csv"))):
            if r_["lg"] == LGN[lgk] and r_.get("ros_pg"): RR[nk(r_["name"])] = float(r_["ros_pg"])
    except Exception: pass
    def helps(p):
        v = RR.get(nk(p["name"])) if p else None
        if v is None or p["pos"] in ("K", "DEF"): return []
        out_ = []
        for t, Rt in base_R.items():
            if t == me: continue
            st_ = [RR.get(nk(q["name"]), 0) for q in Rt if q["pos"] == p["pos"] and q.get("slot") not in ("BN", "IR")]
            if st_ and v > min(st_) * 1.15: out_.append(names.get(t, t))
        return out_
    byname = {p["name"]: p for p in mine}
    for m in moves: m["drop_helps"] = helps(byname.get(m["drop"]))
    moves.sort(key=lambda m: -(m["d_wins"] * 0.25 + m["d_playoff"] + 2 * m["d_title"] - 0.004 * len(m["drop_helps"])))
    seen, best = set(), []
    for m in moves:
        if m["add"] in seen: continue
        seen.add(m["add"]); best.append(m)
    # block: for the top moves, the rival who gains most from that man - and what it costs Dom if he grabs him instead
    for m in best[:5]:
        a = next(p for p in pool if p["name"] == m["add"]); top = None
        for t, Rt in base_R.items():
            if t == me: continue
            drop_t = min([q for q in Rt if q.get("slot") not in ("IR",)], key=lambda q: season_val(q, now, 17))
            Ra = [q for q in Rt if q is not drop_t] + [dict(a, slot="BN")]
            gain = lineup_pts(E, Ra, ALLW) - lineup_pts(E, Rt, ALLW)
            if gain > 0.5 and (top is None or gain > top[1]): top = (t, gain, Ra)
        if top:
            Rr = {k: list(v) for k, v in base_R.items()}; Rr[top[0]] = top[2]; rr = E.run(Rr)
            m["block"] = dict(rival=names.get(top[0], top[0]), rival_pts=round(top[1], 1), rival_playoff=round(rr[top[0]]["playoff"] - B[top[0]]["playoff"], 3),
                              my_playoff=round(rr[me]["playoff"] - Bm["playoff"], 3), my_title=round(rr[me]["title"] - Bm["title"], 4))
    # trades: screen every 1-for-1 and 2-for-1 on both lineups (rest of season, title weeks count 1.5x), then play out the best
    def val(roster): return lineup_pts(E, roster, REM) + 1.5 * lineup_pts(E, roster, list(PO))
    # Dom's trade rules (Oct 31 11 AM): (1) a star only comes back for a star - no deal asks for a man clearly better-ranked
    # than the best one Dom gives (Ratcliffe rest of season, within 15%); (2) a handcuff to one of Dom's own starting backs
    # is protected (Kaelon Black behind McCaffrey: "if something happens to McCaffrey, my team's done"); (3) no deals with
    # this week's opponent; (4) nobody who is OUT this week goes either way.
    RRt = {}
    try:
        for r_ in csv.DictReader(open(os.path.join(R, "dispatch_out", "ftn_scored.csv"))):
            if r_["lg"] == LGN[lgk] and r_.get("ros_pg"): RRt[nk(r_["name"])] = float(r_["ros_pg"])
    except Exception: pass
    def rv(p): return RRt.get(nk(p["name"])) or season_val(p, now, 17) / max(1, 17 - now + 1)
    my_rb_teams = {p.get("nfl") for p in mine if p["pos"] == "RB" and rv(p) >= 15}
    protected = {p["name"] for p in mine if p["pos"] == "RB" and p.get("nfl") in my_rb_teams and rv(p) < 15}
    out_now = lambda p: (p.get("ytag") or "").upper() in ("O", "IR") or (p.get("slot") == "IR")
    opp_now = next((b if a == me else a for a, b in L["sched"].get(now, []) if me in (a, b)), None)
    my_v = val(mine); give_pool = [p for p in mine if p.get("slot") != "IR" and p["pos"] not in ("K", "DEF") and p["name"] not in protected and not out_now(p)]
    screened = []
    for t, Rt in base_R.items():
        if t == me or t == opp_now: continue
        their_v = val(Rt); get_pool = [p for p in Rt if p.get("slot") != "IR" and p["pos"] not in ("K", "DEF") and not out_now(p)]
        gives = [(g,) for g in give_pool] + list(itertools.combinations(give_pool, 2))
        for G in gives:
            for gt in get_pool:
                if rv(gt) > 1.15 * max(rv(g) for g in G): continue          # star for star
                mine2 = [q for q in mine if q not in G] + [dict(gt, slot="BN")]
                theirs2 = [q for q in Rt if q is not gt] + [dict(g, slot="BN") for g in G]
                if len(G) == 2:   # they take two for one: they drop their least valuable non-IR man to make room
                    lo = min([q for q in theirs2 if q.get("slot") != "IR" and q["name"] not in {g["name"] for g in G}], key=lambda q: season_val(q, now, 17))
                    theirs2 = [q for q in theirs2 if q is not lo]
                dm, dt = val(mine2) - my_v, val(theirs2) - their_v
                if dm > 4 and dt > 2: screened.append((min(dm, dt * 1.5), dm, dt, t, G, gt, mine2, theirs2))
    screened.sort(key=lambda x: -x[0])
    trades = []
    for sc, dm, dt, t, G, gt, mine2, theirs2 in screened[:30]:
        Rm = {k: list(v) for k, v in base_R.items()}; Rm[me] = mine2; Rm[t] = theirs2
        r = E.run(Rm)
        a_me, a_t = r[me], r[t]
        dpm, dtm = a_me["playoff"] - Bm["playoff"], a_me["title"] - Bm["title"]
        dpt, dtt = a_t["playoff"] - B[t]["playoff"], a_t["title"] - B[t]["title"]
        # Dom: "it needs to be powerful for them too, or they won't even consider it" - both sides must gain for real
        if (dpm >= 0.02 or dtm >= 0.01) and (dpt >= 0.02 or dtt >= 0.01) and dpm >= -0.005 and dpt >= -0.005:   # nobody gives up playoff odds
            need = gt["pos"]; gave = "/".join(g["pos"] for g in G)
            trades.append(dict(partner=names.get(t, t), give=[g["name"] for g in G], get=gt["name"], get_pos=gt["pos"], give_pos=gave,
                               me_before=summ(Bm), me_after=summ(a_me), them_before=summ(B[t]), them_after=summ(a_t),
                               d_wins=round(a_me["wins"] - Bm["wins"], 2), d_playoff=round(dpm, 3), d_title=round(dtm, 4),
                               them_d_playoff=round(dpt, 3), them_d_title=round(dtt, 4), them_d_wins=round(a_t["wins"] - B[t]["wins"], 2),
                               pitch=(f"{' and '.join(g['name'] for g in G)} for {gt['name']}. On 6,000 simulated seasons your playoff odds go {B[t]['playoff']:.0%} to {a_t['playoff']:.0%}"
                                      f" and your title odds {B[t]['title']:.1%} to {a_t['title']:.1%}, and you add about {a_t['wins'] - B[t]['wins']:+.1f} wins - "
                                      f"{' and '.join(g['name'] for g in G)} start{'s' if len(G) == 1 else ''} for you the rest of the way.")))
    trades.sort(key=lambda x: -min(x["d_playoff"] + 2 * x["d_title"], x["them_d_playoff"] + 2 * x["them_d_title"]))
    _p, _t = set(), []
    for x in trades:                                   # one deal per partner, so the list isn't three versions of the same ask
        if x["partner"] in _p: continue
        _p.add(x["partner"]); _t.append(x)
    trades = _t
    # the card box (Road to the Playoffs) fields, kept for the league card
    table = sorted(((B[t]["playoff"], t) for t in base_R), reverse=True)
    games = [dict(wk=wk, opp=names.get(o, o), win=round(B["_week"].get(wk, 0), 3)) for wk in REM
             for o in [next((b if a == me else a for a, b in L["sched"].get(wk, []) if me in (a, b)), None)] if o]
    po_weeks = sorted(((round(lineup_pts(E, Rt, list(PO)) / 3, 1), names.get(t, t), t == me) for t, Rt in base_R.items()), reverse=True)
    funnel = dict(playoff=round(Bm["playoff"], 3), semis=round(Bm["semis"], 3), final=round(Bm["final"], 3), title=round(Bm["title"], 4))
    # a move only headlines if it clears the bar AND its drop wouldn't start for a rival (Dom's rule) - the rest fold away
    rec_now = sorted(((L["rec"].get(t, {}).get("w", 0), L["rec"].get(t, {}).get("pf", 0), t) for t in base_R), reverse=True)
    stand_now = [t for _, _, t in rec_now].index(me) + 1
    left = {o for wk in REM for o in [next((b if a == me else a for a, b in L["sched"].get(wk, []) if me in (a, b)), None)] if o}
    path, cw = [], float(L["rec"].get(me, {}).get("w", 0))
    for g_ in games: cw += g_["win"]; path.append(dict(wk=g_["wk"], opp=g_["opp"], win=g_["win"], cum=round(cw, 2)))
    keep_moves = [m for m in best if not m.get("drop_helps") and (m["d_wins"] >= 0.08 or m["d_playoff"] >= 0.012 or m["d_title"] >= 0.004 or m["this_week"] >= 0.02)]
    OUT["leagues"][LAB[lgk]] = dict(
        week=now, built=BUILT, standings=L["stamp"], base=summ(Bm), funnel=funnel, wins_hist=Bm["wins_hist"],
        race=[dict(team=names.get(t, t), playoff=round(v, 3), title=round(B[t]["title"], 4), me=(t == me), left=(t in left),
                   rec=f"{L['rec'].get(t, {}).get('w', 0)}-{L['rec'].get(t, {}).get('l', 0)}") for v, t in table],
        stand_now=stand_now, median_league=bool(L["cfg"]["median"]), rec_now=f"{L['rec'].get(me, {}).get('w', 0)}-{L['rec'].get(me, {}).get('l', 0)}",
        line=dict(median=round(B["_line"]["median"], 1), reach=round(B[me].get("_reach", B["_line"]["reach"]), 3), dist=B["_line"]["dist"]), path=path,
        protected=sorted(protected), trade_rules="star for star; handcuffs to your starting backs protected; no deals with this week's opponent; nobody who is out this week",
        games=games, po_weeks=[dict(pts=a, team=b, me=c) for a, b, c in po_weeks], worth=worth,
        moves=keep_moves[:5], not_worth=[dict(add=m["add"], drop=m["drop"], d_wins=m["d_wins"], d_playoff=m["d_playoff"]) for m in best if m not in keep_moves][:8],
        trades=trades[:3], trades_screened=len(screened),
        note=f"{N:,} seasons + the playoff bracket per test, paired draws (each man's luck is the same in every test)")
    # the card box keeps working off the same numbers
    OUT["leagues"][LAB[lgk]]["plan"] = dict(week=now, built=BUILT, standings=L["stamp"], playoff=Bm["playoff"], wins=Bm["wins"], first=Bm["first"],
        rank=[t for _, t in table].index(me) + 1, teams=len(table), race=OUT["leagues"][LAB[lgk]]["race"], games=games, week_win=B["_week"].get(now, 0),
        po_weeks=OUT["leagues"][LAB[lgk]]["po_weeks"], worth=[dict(w, d_po=0) for w in worth],
        moves=[dict(add=m["add"], pos=m["pos"], nfl=m["nfl"], acq=m["acq"], drop=m["drop"], d_playoff=m["d_playoff"], d_week=m["this_week"], helps=[]) for m in best[:4]],
        note=OUT["leagues"][LAB[lgk]]["note"])
    print(f"CHAMP {LAB[lgk]}: wins {Bm['wins']:.1f}, playoffs {Bm['playoff']:.0%}, title {Bm['title']:.1%}, likeliest seed {int(np.argmax(Bm['seeds']))+1}; "
          f"{len(keep_moves)} moves worth it, {len(trades)} two-sided trades of {len(screened)} screened ({time.time()-t0:.0f}s)")
json.dump(OUT, open(os.path.join(R, "dispatch_out", "championship.json"), "w"), indent=1, default=float)
try:
    Mm = json.load(open(meter_f))
    for lab, v in OUT["leagues"].items():
        if lab in Mm.get("leagues", {}):
            Mm["leagues"][lab]["champ"] = {k: v[k] for k in v if k != "plan"}; Mm["leagues"][lab]["plan"] = v["plan"]
    json.dump(Mm, open(meter_f, "w"), ensure_ascii=False, default=float)
except Exception as e: print("CHAMP not added to the meter file:", e)
