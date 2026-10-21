"""THE FORECAST MODEL — groundwork (Mon Sep 28). Predicts a man's points and workload for his next game from the weeks on record.
Workload = the scan's own measure (QB throws + w*runs, RB carries + w*targets, WR/TE targets). Points priced in the league's scoring.
Three pieces, each tested on real weeks before it is trusted:
  1. EXPECTED WORKLOAD  — recency-weighted mean of his workload (latest game counts most), games he left early down-weighted.
  2. POINTS PER TOUCH   — his own rate, shrunk toward the position's rate by how few touches he has (small samples lie).
  3. FORECAST           — workload x rate. News adjusts workload only (good = back toward his best game, out = 0).
"""
import sys, pandas as pd, numpy as np
sys.path.insert(0, "/home/claude/src/role_watch"); from rw_core import norm
STATS = "/home/claude/src/role_watch/data/stats_player_week_2026.csv"
SC = {1: dict(ptd=6, it=-2, ra=.25), 2: dict(ptd=6, it=-2, ra=.25), 3: dict(ptd=6, it=-2, ra=.25), 4: dict(ptd=6, it=-1, ra=0.0)}
WT = {1: (1.8, 1.9), 2: (1.8, 1.9), 3: (1.8, 1.9), 4: (1.3, 2.7)}          # the Positions page's derived weights
def load():
    s = pd.read_csv(STATS, low_memory=False)
    s = s[(s.season_type == "REG") & s.position.isin(["QB", "RB", "WR", "TE"]) & s.player_display_name.notna()].copy()
    sys.path.insert(0, "/home/claude/dksys/gather"); from names import norm as _dknorm   # Oct 20 (Dom): same key as Gotham and the meter
    s["key"] = s.player_display_name.map(_dknorm)
    return s.fillna(0)
def price(d, k):
    p = SC[k]
    return (.04*d.passing_yards + p["ptd"]*d.passing_tds + p["it"]*d.passing_interceptions + .1*d.rushing_yards + 6*d.rushing_tds
            + p["ra"]*d.carries + d.receptions + .1*d.receiving_yards + 6*d.receiving_tds - 2*(d.rushing_fumbles_lost + d.receiving_fumbles_lost + d.sack_fumbles_lost)
            + 2*(d.passing_2pt_conversions + d.rushing_2pt_conversions + d.receiving_2pt_conversions))
def work(d, k):
    qw, rw = WT[k]
    return np.where(d.position == "QB", d.attempts + qw*d.carries, np.where(d.position == "RB", d.carries + rw*d.targets, d.targets))
def frame(k, s=None):
    s = load() if s is None else s
    s = s.assign(pts=price(s, k), wl=work(s, k)); return s
DECAY = .65          # each older game counts 65% of the one after it
SHRINK = 40          # touches of "position average" mixed into his own rate
def forecast(f, key, thru, news=None):
    """points and workload for the game after week `thru`, from weeks <= thru. None if he has no game on record."""
    g = f[(f.key == key) & (f.week <= thru)].sort_values("week")
    if not len(g): return None
    pos = g.position.iloc[-1]
    w = DECAY ** (thru - g.week.values); w = w / w.sum()
    wl = float((g.wl.values * w).sum())
    pool = f[(f.position == pos) & (f.week <= thru)]
    prate = pool.pts.sum() / max(pool.wl.sum(), 1)
    own = g.pts.sum(); touches = g.wl.sum()
    rate = (own + SHRINK*prate) / (touches + SHRINK)
    if news == "good": wl = max(wl, float(g.wl.max()))
    if news == "out": wl = 0.0
    return dict(pts=wl*rate, wl=wl, rate=rate, pos=pos, games=len(g))
# ------------------------------------------------------------------ the old "sample forecast" rule, for comparison
def sample_rule(f, key, thru, news=None):
    g = f[(f.key == key) & (f.week <= thru)].sort_values("week")
    if not len(g): return None
    wl = float(g.wl.iloc[-1]); rate = g.pts.sum()/max(g.wl.sum(), 1)
    if news == "good": wl = float(g.wl.max())
    if news == "out": wl = 0.0
    return dict(pts=wl*rate, wl=wl)
def backtest(k=1, weeks=(2, 3), min_wl=3):
    f = frame(k); rows = []
    for wk in weeks:
        tgt = f[(f.week == wk) & (f.wl >= min_wl)]
        for _, r in tgt.iterrows():
            m = forecast(f, r.key, wk-1); o = sample_rule(f, r.key, wk-1)
            if m is None: continue
            prev = f[(f.key == r.key) & (f.week < wk)]
            rows.append(dict(week=wk, key=r.key, pos=r.position, act=r.pts, act_wl=r.wl, model=m["pts"], model_wl=m["wl"],
                             rule=o["pts"], rule_wl=o["wl"], last=float(prev.sort_values("week").pts.iloc[-1]), avg=float(prev.pts.mean())))
    return pd.DataFrame(rows)
if __name__ == "__main__":
    bt = backtest(1)
    mae = lambda a, b: float((bt[a]-bt[b]).abs().mean())
    print("men tested:", len(bt), "by week", bt.groupby("week").size().to_dict())
    for m in ("model", "rule", "last", "avg"): print(f"points MAE  {m:6s} {mae(m,'act'):.2f}")
    for m in ("model_wl", "rule_wl"): print(f"workload MAE {m:8s} {mae(m,'act_wl'):.2f}")
    print(bt.groupby("pos").apply(lambda d: pd.Series({m: (d[m]-d.act).abs().mean() for m in ("model","rule","last","avg")})).round(2))

# OCT20a hyphenated names join Gotham
