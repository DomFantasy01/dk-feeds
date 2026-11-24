"""THE EXPERT PANEL SIMULATOR (Nov 24 2026, Dom: "If he's off, the whole thing's done ... We need a comparison so our checks
and balances make sense" and "you're going to include the 15th through the 17th").

The same season simulator (sim.py), run once per expert, side by side:
  Ratcliffe   this week + his rest-of-season per-game number for Weeks 13-17 (ftn_scored.csv, each league's scoring)
  Clay        week by week through Week 17 (clay_scored.csv)
  DraftSharks week by week (draftsharks_scored.csv)
  Koerner, Vegas, RotoBaller   this week only (they publish nothing later); later weeks use the system's number
Every player on every roster and on the wire takes that expert's number; where the expert has no number for a man,
the system's own value (the Scout's, Ratcliffe-led) fills in, and the report says how many were filled.

New over sim.py: the playoffs are played. Six seeds (division winners on top where the league does that), seeds 1-2
sit out Week 15, 3v6 and 4v5 in Week 15, reseeded semifinal Week 16 (top seed left plays the lowest), final Week 17.
So every number is three numbers: make the playoffs, reach the final, win the title.

Move scan: every wire player (free agent or waiver) is tested in Dom's dead roster spot (default: his lowest-value
bench man), on the same draws, under every expert. A move is GREEN when it raises title odds under at least two experts
with weekly numbers through Week 17 and lowers it under none of them by more than the gain; SPLIT when experts disagree.
Nothing here is a move - Dom decides.

  python3 sim_experts.py DKI [DKII ...]       env: DK_REPO, DK_SCOUT_DIR, DK_SIMS (default 3000), DK_DROP (name, optional)
"""
import os, sys, json, re, copy, math
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim

REPO = sim.REPO
N = int(os.environ.get("DK_SIMS", "3000"))
LGN = {"DKI": 1, "DKII": 2, "DKIII": 3, "DKIV": 4}
WEEKS = [str(w) for w in range(12, 18)]
PLAYOFF = (15, 16, 17)
DEFKEY = {"49ers": "SF", "Bears": "CHI", "Bengals": "CIN", "Bills": "BUF", "Broncos": "DEN", "Browns": "CLE", "Buccaneers": "TB",
          "Cardinals": "ARI", "Chargers": "LAC", "Chiefs": "KC", "Colts": "IND", "Commanders": "WAS", "Cowboys": "DAL", "Dolphins": "MIA",
          "Eagles": "PHI", "Falcons": "ATL", "Giants": "NYG", "Jaguars": "JAX", "Jets": "NYJ", "Lions": "DET", "Packers": "GB",
          "Panthers": "CAR", "Patriots": "NE", "Raiders": "LV", "Rams": "LA", "Ravens": "BAL", "Saints": "NO", "Seahawks": "SEA",
          "Steelers": "PIT", "Texans": "HOU", "Titans": "TEN", "Vikings": "MIN"}

def k_(n): return re.sub(r"[^a-z]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(n).lower()))

def _read(name):
    f = f"{REPO}/dispatch_out/{name}"
    return pd.read_csv(f) if os.path.exists(f) and os.path.getsize(f) > 60 else pd.DataFrame()

def expert_tables(lgk):
    """{expert: {(key, pos): {week: value}}} in that league's scoring, plus when each was read."""
    lg = LGN[lgk]; out = {}; read = {}
    def keyed(df, namecol="name", poscol="pos", teamcol="team"):
        df = df[df.lg == lg]
        for r in df.itertuples(index=False):
            d = r._asdict(); pos = "DEF" if str(d[poscol]) in ("DST", "DEF", "D/ST") else str(d[poscol])
            key = str(d.get(teamcol, "")) if pos == "DEF" else k_(d[namecol])
            yield key, pos, d
    C = _read("clay_scored.csv")
    if len(C):
        T = {}
        for key, pos, d in keyed(C):
            T[(key, pos)] = {"12": d["wk"], "13": d["w13"], "14": d["w14"], "15": d["w15"], "16": d["w16"], "17": d["w17"]}
        out["Clay"] = T; read["Clay"] = str(C.read.iloc[0])
    D = _read("draftsharks_scored.csv")
    if len(D):
        T = {}
        for key, pos, d in keyed(D):
            T[(key, pos)] = {"12": d["wk"], "13": d["w13"], "14": d["w14"], "15": d["w15"], "16": d["w16"], "17": d["w17"]}
        out["DraftSharks"] = T; read["DraftSharks"] = str(D.read.iloc[0])
    F = _read("ftn_scored.csv")
    if len(F):
        T = {}
        for key, pos, d in keyed(F):
            ros = d.get("ros_pg"); v = {"12": d["wk"]}
            for w in WEEKS[1:]: v[w] = ros if ros == ros else None       # bye weeks are zeroed later from the system's calendar
            T[(key, pos)] = v
        out["Ratcliffe"] = T; read["Ratcliffe"] = str(F.read_pt.iloc[0])
    for nm, f in (("Koerner", "koerner_scored.csv"), ("Vegas", "vegas_scored.csv"), ("RotoBaller", "rotoballer_scored.csv")):
        X = _read(f)
        if len(X):
            T = {}
            for key, pos, d in keyed(X): T[(key, pos)] = {"12": d["wk"]}
            out[nm] = T; read[nm] = str(X.read_pt.iloc[0] if "read_pt" in X else X.read.iloc[0])
    return out, read

def apply_expert(S, table):
    """returns (teams, pool) with every man's weekly values from this expert; system value where the expert is silent.
    A week the system has at 0 (bye, out, IR) stays 0."""
    filled = [0, 0]
    def fix(p):
        p = dict(p); key = DEFKEY.get(p["name"], p["nfl"]) if p["pos"] == "DEF" else k_(p["name"])
        v = table.get((key, p["pos"])); wk = dict(p["wk"])
        for w in WEEKS:
            sysv = wk.get(w, 0.0)
            ev = None if v is None else v.get(w)
            if ev is None or not (ev == ev) or sysv <= 0:
                filled[1] += 1
                continue
            wk[w] = float(ev); filled[0] += 1
        p["wk"] = wk; return p
    teams = {t: [fix(p) for p in R] for t, R in S["teams"].items()}
    pool = [fix(p) for p in S["pool"]]
    return teams, pool, filled

# ---------------------------------------------------------------- the season with the playoffs played
def season_full(L, noise, rosters, n=N, seed=7):
    S = L["S"]; slots = S["slots"]; now = int(S["now"]); me = str(S["me"])
    teams = sorted(rosters, key=int)
    rng = np.random.default_rng(seed)
    nfl = sorted({p["nfl"] for t in teams for p in rosters[t]} | {p["nfl"] for p in S["pool"]})
    W = {t: np.full(n, L["rec"].get(t, {}).get("w", 0), float) for t in teams}
    PF = {t: np.full(n, L["rec"].get(t, {}).get("pf", 0.0)) for t in teams}
    week_win = {}
    def scores(wk, tf, zero):
        sc = {}
        for t in teams:
            lu = sim.best_lineup(rosters[t], slots, wk)
            pl = [rosters[t][i] for i in lu if i is not None]
            arr = sim.draw(noise, rng, [(p["wk"].get(str(wk), 0.0), p["pos"], p["nfl"], p.get("ytag", "")) for p in pl], n, zero_now=zero, tf=tf)
            sc[t] = arr.sum(axis=1)
        return sc
    for wk in range(now, sim.REG_LAST + 1):
        tf = {k: v for k, v in zip(nfl, rng.standard_normal((len(nfl), n)))}
        sc = scores(wk, tf, wk == now)
        med = np.median(np.vstack([sc[t] for t in teams]), axis=0) if L["cfg"]["median"] else None
        for a, b in L["sched"].get(wk, []):
            if a not in sc or b not in sc: continue
            wa = (sc[a] > sc[b]).astype(float) + .5 * (sc[a] == sc[b]); W[a] += wa; W[b] += 1 - wa
            if me in (a, b): week_win[wk] = float((wa if a == me else 1 - wa).mean())
        if med is not None:
            for t in teams: W[t] += (sc[t] > med).astype(float)
        for t in teams: PF[t] += sc[t]
    T = np.array(teams); key = np.vstack([W[t] for t in teams]) * 1e5 + np.vstack([PF[t] for t in teams])
    # seeds 1-6 per simulation
    order = np.argsort(-key, axis=0)                    # [team, sim] ranks by record
    seeds = np.zeros((6, n), dtype=int)
    divwin = L["cfg"]["division_winners_top_seeds"] and L["divs"]
    dv_idx = {}
    if divwin:
        for i, t in enumerate(teams): dv_idx.setdefault(L["divs"].get(t), []).append(i)
    for c in range(n):
        picked = []
        if divwin:
            winners = [max(idx, key=lambda i: key[i, c]) for d, idx in dv_idx.items() if d is not None]
            picked = sorted(winners, key=lambda i: -key[i, c])
        for i in order[:, c]:
            if len(picked) >= 6: break
            if i not in picked: picked.append(i)
        seeds[:, c] = picked[:6]
    mi = teams.index(me)
    made = (seeds == mi).any(axis=0)
    # playoff weeks
    tfp = {wk: {k: v for k, v in zip(nfl, rng.standard_normal((len(nfl), n)))} for wk in PLAYOFF}
    PS = {wk: scores(wk, tfp[wk], False) for wk in PLAYOFF}
    P = {wk: np.vstack([PS[wk][t] for t in teams]) for wk in PLAYOFF}     # [team, sim]
    cols = np.arange(n)
    def game(wk, a, b):          # a, b: team index arrays per sim -> winner index array
        sa = P[wk][a, cols]; sb = P[wk][b, cols]
        return np.where(sa >= sb, a, b)
    w36 = game(15, seeds[2], seeds[5]); w45 = game(15, seeds[3], seeds[4])
    # reseed: top seed plays the lowest seed left
    seedpos = np.full((len(teams), n), 9)
    for s in range(6): seedpos[seeds[s], cols] = s
    lo = np.where(seedpos[w36, cols] > seedpos[w45, cols], w36, w45); hi = np.where(lo == w36, w45, w36)
    f1 = game(16, seeds[0], lo); f2 = game(16, seeds[1], hi)
    champ = game(17, f1, f2)
    final = (f1 == mi) | (f2 == mi)
    return dict(playoffs=float(made.mean()), final=float(final.mean()), title=float((champ == mi).mean()),
                week_win=week_win, seed_bye=float(((seeds[0] == mi) | (seeds[1] == mi)).mean()))

def run_league(lgk, noise, n=N, scan=True, top=None):
    L = sim.load_league(lgk); L["live"] = L.get("live") or {}
    S = L["S"]; me = str(S["me"])
    tables, read = expert_tables(lgk)
    order = ["Ratcliffe", "Clay", "DraftSharks", "Koerner", "Vegas", "RotoBaller"]
    tables = {k: tables[k] for k in order if k in tables}
    res = dict(league=sim.LAB[lgk], read=read, experts={}, moves=[])
    built = {}
    for ex, T in tables.items():
        teams, pool, filled = apply_expert(S, T)
        built[ex] = (teams, pool)
        b = season_full(L, noise, teams, n)
        b["filled"] = filled
        res["experts"][ex] = b
        print(f"  {lgk} {ex:11s} this week {b['week_win'].get(int(S['now']), 0):.0%}  playoffs {b['playoffs']:.1%}  final {b['final']:.1%}  title {b['title']:.1%}  (expert numbers {filled[0]}, system fill {filled[1]})", flush=True)
    if not scan: return res
    # dead spot: Dom's lowest-value bench man by the system's Weeks 12-17 (DK_DROP overrides)
    mine = S["teams"][me]
    named = {k: v for k, v in (x.split("=", 1) for x in os.environ.get("DK_DROPS", "").split(";") if "=" in x)}
    # default dead spot: his lowest-value skill player (not K/DEF, not IR), starter or bench - e.g. Jennings, Kincaid, Kiner
    drop = named.get(lgk) or os.environ.get("DK_DROP") or min((p for p in mine if p["pos"] not in ("K", "DEF") and p.get("slot") != "IR"),
                                                              key=lambda p: sum(p["wk"].get(w, 0) for w in WEEKS))["name"]
    def worth(p): return sum(p["wk"].get(w, 0) for w in WEEKS)
    cands = sorted(S["pool"], key=worth, reverse=True)[:top] if top else list(S["pool"])
    for p in cands:
        dp = drop
        if p["pos"] in ("DEF", "K"):        # a defense or kicker replaces Dom's weaker one, not the dead bench spot
            same = [q for q in mine if q["pos"] == p["pos"]]
            if same: dp = min(same, key=worth)["name"]
        row = dict(add=p["name"], pos=p["pos"], nfl=p["nfl"], acq=p.get("acq", ""), drop=dp, by={})
        for ex in tables:
            teams, pool = built[ex]
            pa = next(q for q in pool if q["name"] == p["name"])
            R = {t: list(v) for t, v in teams.items()}
            R[me] = [q for q in R[me] if q["name"] != dp] + [dict(pa, slot="BN")]
            a = season_full(L, noise, R, n)
            base = res["experts"][ex]
            row["by"][ex] = dict(playoffs=a["playoffs"] - base["playoffs"], title=a["title"] - base["title"],
                                 week=a["week_win"].get(int(S["now"]), 0) - base["week_win"].get(int(S["now"]), 0),
                                 vals={w: round(pa["wk"].get(w, 0), 1) for w in WEEKS})
        res["moves"].append(row)
        print(f"   {p['name']:24s} {p['pos']:3s} drop {dp:20s} " +" | ".join(f"{ex[:5]} t{v['title']*100:+.1f} p{v['playoffs']*100:+.1f}" for ex, v in row["by"].items()), flush=True)
    return res

if __name__ == "__main__":
    noise = sim.Noise(f"{REPO}/dispatch_out/scoreboard/graded.csv")
    out = {}
    for lgk in sys.argv[1:] or ["DKI", "DKII", "DKIII", "DKIV"]:
        out[lgk] = run_league(lgk, noise)
    od = f"{REPO}/dispatch_out/sim"; os.makedirs(od, exist_ok=True)
    json.dump(out, open(f"{od}/sim_experts_latest.json", "w"), indent=1, default=str)
