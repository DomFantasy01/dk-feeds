# THE SCOREBOARD (Dom, Sun Oct 11 2026) - the checks-and-balances engine. Runs at the end of every Dispatch build.
# 1. FREEZE: every starter in Dom's four matchups keeps the last Yahoo / Gotham / Sleeper / Ratcliffe (Oct 28) number seen BEFORE his game
#    kicks off (dispatch_out/scoreboard/pregame_wk<N>.json). Once his game starts, his entry never changes again.
# 2. GRADE: once a game is final, each frozen number is graded against what the man actually scored, priced in that
#    league's own scoring from the nflverse stat line - reality is the judge, not Yahoo and not Gotham.
# 3. REPORT: dispatch_out/scoreboard/graded.csv (every man, every week) and scoreboard.txt (the table):
#    average miss in points, and "start/sit calls right" = of every pair of same-position men in the same week,
#    how often the source put the better scorer first. Plus the disagreement test: when the three sources split
#    by 4+ points, how big the misses get and who was closer.
# Weeks 2-4 were graded by hand on Oct 8 (seed file below); from Week 5 on everything is automatic.
import sys, os, json, glob, itertools, datetime as dt
import pandas as pd
sys.path.insert(0, '/home/claude/dksys/gather'); from names import norm
sys.path.insert(0, '/home/claude/src/forecast'); import fc_model as FM
from zoneinfo import ZoneInfo
REPO = sys.argv[1]; OUT = f"{REPO}/dispatch_out/scoreboard"; os.makedirs(OUT, exist_ok=True)
D = '/home/claude/dksys/data/latest'; LGK = {'DK I': 1, 'DK II': 2, 'DK III': 3, 'DK IV': 4}
now = dt.datetime.fromisoformat(os.environ['DK_SB_NOW']) if os.environ.get('DK_SB_NOW') else dt.datetime.now(dt.timezone.utc)   # override only for seeding
G = pd.read_csv(f'{D}/games.csv', low_memory=False); G = G[G.season == G.season.max()]
def kick(r):
    try: return dt.datetime.strptime(f"{r.gameday} {r.gametime}", "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("America/New_York"))
    except Exception: return None
G['ko'] = G.apply(kick, axis=1)
TEAMFIX = {'LAR': 'LA', 'JAC': 'JAX', 'WSH': 'WAS'}
def game_of(team, week):
    t = TEAMFIX.get(team, team); g = G[(G.week == week) & ((G.home_team == t) | (G.away_team == t))]
    return g.iloc[0] if len(g) else None
# ---- 1. freeze pregame numbers from this build's meter
mf = [os.environ['DK_SB_METER']] if os.environ.get('DK_SB_METER') else sorted(glob.glob(f'{D}/meter/meter_wk*.json'), key=lambda p: int(p.split('_wk')[1].split('.')[0]))
if mf:
    M = json.load(open(mf[-1])); W = int(M['week']); pf = f"{OUT}/pregame_wk{W}.json"
    P = json.load(open(pf)) if os.path.exists(pf) else {}
    n = 0
    for lab, L in M['leagues'].items():
        for side in ('me', 'op'):
            for s in L['starters'][side]:
                if s.get('pos') in ('K', 'DEF') or not s.get('player'): continue
                g = game_of(s.get('team'), W)
                if g is None or g.ko is None or now >= g.ko.astimezone(dt.timezone.utc): continue   # kicked off: frozen
                P[f"{lab}|{side}|{norm(s['player'])}"] = dict(league=lab, side=side, player=s['player'], pos=s['pos'], team=s.get('team'),
                    yahoo=s.get('yahoo'), gotham=s.get('gotham'), gotham_raw=s.get('gotham_raw', s.get('gotham')), sleeper=s.get('sleeper'), ratcliffe=s.get('ratcliffe') if s.get('ratcliffe_src') == 'ftn' else None, koerner=s.get('koerner') if s.get('koerner_src') == 'flabs' else None, brenton=s.get('brenton') if s.get('brenton_src') == 'brenton' else None, status=s.get('status'), at=M['built_pt'], game=g.game_id)   # Oct 21: injury tag kept, so Q/D calls can be graded
                n += 1
        for s in L.get('bench', []):            # Oct 21 (Dom): Dom's bench too - graded on its own, never mixed into the starters' table
            if s.get('slot') != 'BN' or s.get('pos') in ('K', 'DEF') or not s.get('player'): continue
            g = game_of(s.get('team'), W)
            if g is None or g.ko is None or now >= g.ko.astimezone(dt.timezone.utc): continue
            P[f"{lab}|bench|{norm(s['player'])}"] = dict(league=lab, side='bench', player=s['player'], pos=s['pos'], team=s.get('team'),
                yahoo=None, gotham=s.get('gotham'), gotham_raw=s.get('gotham'), sleeper=s.get('sleeper'), ratcliffe=s.get('ratcliffe'), koerner=s.get('koerner'), at=M['built_pt'], game=g.game_id)
            n += 1
    json.dump(P, open(pf, 'w'), indent=0); print(f"   scoreboard: week {W} pregame numbers held for {len(P)} men ({n} refreshed this build)")
# ---- 2. grade every week that has finished games
S = pd.read_csv(f'{D}/stats_week.csv', low_memory=False); S = S[(S.season == G.season.max()) & (S.season_type == 'REG')].fillna(0)
S['k'] = S.player_display_name.astype(str).map(norm)
fin = set(G[G.result.notna()].game_id)
rows = []
seed = f"{REPO}/backtest/history_wk2to4.csv"
if os.path.exists(seed):
    for r in pd.read_csv(seed).itertuples(): rows.append(dict(week=int(r.W), league='seed', pos=r.pos, player=r.k, yahoo=r.yahoo, gotham_raw=r.gotham_rec, sleeper=r.sleeper, actual=r.act))
for pf in sorted(glob.glob(f"{OUT}/pregame_wk*.json")):
    W = int(pf.split('_wk')[1].split('.')[0]); P = json.load(open(pf))
    if W <= 4: continue
    SW = S[S.week == W]
    for key, v in P.items():
        if v.get('game') not in fin: continue
        x = SW[SW.k == norm(v['player'])]
        act = float(FM.price(x, LGK[v['league']]).iloc[0]) if len(x) else 0.0      # final game, no stat line = 0 (inactive)
        rows.append(dict(side=v.get('side', 'me'), week=W, league=v['league'], pos=v['pos'], player=v['player'], yahoo=v['yahoo'], gotham_raw=v.get('gotham_raw', v.get('gotham')), sleeper=v['sleeper'], ratcliffe=v.get('ratcliffe'), koerner=v.get('koerner'), brenton=v.get('brenton'), actual=round(act, 2)))
R = pd.DataFrame(rows)
if 'side' not in R: R['side'] = None
R['side'] = R['side'].fillna('seed')
RB_ = R[R.side == 'bench'].copy(); RS_ = R[R.side == 'me'].copy(); R = R[R.side != 'bench'].copy()   # Oct 21: the bench is graded apart
# Oct 21 (Dom): THE GOTHAM CEILING - Gotham never sits above the Yahoo/Sleeper average (its high calls ran 9.0 pts off vs 5.8 for
# the other two; its low calls were the sharp ones). The meter applies it live from Oct 21; every past week is graded the same
# way here so the record is one rule, and Gotham's own uncapped number is still graded on its own line.
_ok = (R.yahoo > 0) & (R.sleeper > 0); _c = (R.yahoo + R.sleeper) / 2
R['gotham'] = R.gotham_raw.where(~_ok | R.gotham_raw.isna() | (R.gotham_raw <= _c), _c).round(2)
if 'ratcliffe' not in R: R['ratcliffe'] = None
R['ratcliffe'] = pd.to_numeric(R['ratcliffe'], errors='coerce')
if 'koerner' not in R: R['koerner'] = None   # Oct 29 (Dom): Sean Koerner frozen pregame from Week 8, graded the same way
R['koerner'] = pd.to_numeric(R['koerner'], errors='coerce')
if 'brenton' not in R: R['brenton'] = None   # Oct 31 (Dom): Paul Brenton's rank-based number, frozen pregame from Week 8
R['brenton'] = pd.to_numeric(R['brenton'], errors='coerce')
R = R[['week', 'league', 'pos', 'player', 'yahoo', 'gotham', 'sleeper', 'actual', 'gotham_raw', 'ratcliffe', 'koerner', 'brenton']]
if not len(R): print("   scoreboard: nothing graded yet"); sys.exit(0)
R.to_csv(f"{OUT}/graded.csv", index=False)
SRC = ['yahoo', 'gotham', 'sleeper']
SRC4 = ['ratcliffe'] + SRC   # Oct 28 (Dom): Jeff Ratcliffe (FTN) graded from Week 8 on - his frozen pregame number, same rules
def pairs(df, c):
    ok = n = 0
    for _, g in df.dropna(subset=[c]).groupby(['week', 'pos']):
        v = g[c].values; t = g.actual.values
        for i, j in itertools.combinations(range(len(g)), 2):
            if t[i] == t[j] or v[i] == v[j]: continue
            n += 1; ok += (v[i] > v[j]) == (t[i] > t[j])
    return ok / n if n else float('nan')
def line(df, label):
    cells = []
    for c in SRC4:
        x = df.dropna(subset=[c]); cells.append(f"{c.title()} {(x[c]-x.actual).abs().mean():.1f} pts, {pairs(df, c):.0%}" if len(x) else f"{c.title()} -")
    return f"{label:<14} {len(df):>4} men   " + "   ".join(cells)
pt = dt.datetime.now(ZoneInfo("America/Los_Angeles"))
out = [f"THE SCOREBOARD - graded {pt:%a %b %d %Y %I:%M %p} PT. Average miss in points (lower is better) and start/sit calls right (higher is better).",
       "Reality is the judge: each man's final stat line priced in his league's scoring. Weeks 2-4 graded Oct 8; Week 5 on is automatic.", ""]
out.append(line(R, "ALL WEEKS"))
_rc = R.dropna(subset=['ratcliffe'])
if len(_rc):   # head to head on the same men, so the comparison is fair while Ratcliffe has fewer weeks
    out.append(line(_rc, "RATCLIFFE MEN") + "   <- only the men Ratcliffe projected, all four sources on the same men")
for w, g in R.groupby('week'): out.append(line(g, f"Week {w}"))
for p, g in R.groupby('pos'): out.append(line(g, f"  {p}"))
R['spread'] = R[SRC].max(axis=1) - R[SRC].min(axis=1)
hi = R[R.spread >= 4]; lo = R[R.spread < 4]
if len(hi):
    closer = {c: ((hi[c] - hi.actual).abs() == hi[SRC].sub(hi.actual, axis=0).abs().min(axis=1)).mean() for c in SRC}
    out += ["", f"DISAGREEMENT: when the three split by 4+ points ({len(hi)} men), the average Yahoo miss is {(hi.yahoo-hi.actual).abs().mean():.1f} pts "
            f"(vs {(lo.yahoo-lo.actual).abs().mean():.1f} when they agree). Closest of the three on those men: "
            + ", ".join(f"{c.title()} {v:.0%}" for c, v in closer.items()) + "."]
_x = R.dropna(subset=['gotham_raw']); _g = R.rename(columns={'gotham': '_gc', 'gotham_raw': 'gotham'})
out += ["", f"GOTHAM CEILING (Oct 21): Gotham is shown capped at the Yahoo/Sleeper average. Without the cap it misses by {(_x.gotham_raw-_x.actual).abs().mean():.1f} pts, "
        f"{pairs(_g, 'gotham'):.0%} start/sit calls right ({len(_x)} men)."]
# Oct 31 (Dom: "it's okay if they swing, as long as there's something behind it ... that makes us better") - GOTHAM VS THE
# EXPERTS. Only the men where Gotham's own number sat 4+ points from the experts' average (Ratcliffe, Koerner, Brenton - whoever
# had him, frozen pregame). Who was closer to what he really scored? If Gotham wins at least 55% of those calls over 20+ men, it
# has earned a voice back on the meters; until then it stays an early-warning tool (alerts, workload, the Scout).
try:
    _E = R.copy(); _E['expert'] = _E[['ratcliffe', 'koerner', 'brenton']].mean(axis=1, skipna=True)
    _E = _E.dropna(subset=['gotham_raw', 'expert']); _E['gap'] = _E.gotham_raw - _E.expert
    _D = _E[_E.gap.abs() >= 4].copy()
    if not len(_D):
        out += ["", f"GOTHAM VS THE EXPERTS (from Week 8): {len(_E)} men graded with an expert number, none where Gotham split from the experts by 4+ points yet."]
    else:
        _D['gwin'] = (_D.gotham_raw - _D.actual).abs() < (_D.expert - _D.actual).abs()
        n_, w_ = len(_D), _D.gwin.mean()
        verdict = ("earned a voice back" if n_ >= 20 and w_ >= .55 else "stays off the meters" if n_ >= 20 else f"too few calls to judge (needs 20, has {n_})")
        ex = _D.reindex(_D.gap.abs().sort_values(ascending=False).index).head(5)
        out += ["", f"GOTHAM VS THE EXPERTS (from Week 8): {n_} men where Gotham split from the experts by 4+ points. Gotham closer {w_:.0%} of the time; "
                f"average miss Gotham {(_D.gotham_raw-_D.actual).abs().mean():.1f} vs experts {(_D.expert-_D.actual).abs().mean():.1f} pts. Verdict: {verdict}. Biggest splits: "
                + " | ".join(f"Wk {r.week} {r.player}: Gotham {r.gotham_raw:.1f}, experts {r.expert:.1f}, scored {r.actual:.1f} ({'Gotham' if r.gwin else 'experts'})" for r in ex.itertuples()) + "."]
except Exception as _e: out += ["", f"GOTHAM VS THE EXPERTS: not graded - {_e}"]
# Oct 21 (Dom): THE BENCH - points Dom's bench outscored a starter at the same position (same league, same week)
try:
    _FLX = {'RB', 'WR', 'TE'}; _lines = []; _tot = 0.0
    for (lg_, w_), b_ in RB_.groupby(['league', 'week']):
        st_ = RS_[(RS_.league == lg_) & (RS_.week == w_)]
        if not len(st_): continue
        for r_ in b_.itertuples():
            same = st_[st_.pos == r_.pos]
            if not len(same): continue
            lo = same.loc[same.actual.idxmin()]
            if r_.actual > lo.actual + .5:
                _tot += r_.actual - lo.actual; _lines.append(f"Wk {w_} {lg_}: {r_.player} {r_.actual:.1f} on the bench, {lo.player} {lo.actual:.1f} started")
    out += ["", f"THE BENCH (Oct 21): {len(RB_)} bench men graded"
            + (f"; {len(_lines)} times a bench man beat a starter at his position, {_tot:.1f} pts left on the bench" if _lines else "; no bench man beat a starter at his position")
            + (" - " + " | ".join(_lines[:6]) if _lines else "") + "."]
    if len(RB_): RB_.to_csv(f"{OUT}/bench_graded.csv", index=False)
except Exception as _e: out += ["", f"THE BENCH: not graded - {_e}"]
open(f"{OUT}/scoreboard.txt", "w").write("\n".join(out) + "\n"); print("   " + "\n   ".join(out[:5]))
# Oct 21 (Dom): the Scout's report card rides on the Scoreboard - grades every pickup call against the man it would replace
try:
    import subprocess; subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scout_card.py'), REPO], check=True)
except Exception as _e: print('!! SCOUT CARD FAILED -', _e)
