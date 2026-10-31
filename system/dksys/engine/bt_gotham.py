"""Gotham back-test (Oct 31, Dom: "the numbers look way off on some of them").
Runs Gotham for past weeks with DK_BT=1 (the week being tested is never seen), then compares this-week numbers
to what each player actually scored, in each league's own scoring.
Run: python3 bt_gotham.py 4 7 [tag]   -> prints miss per league and overall; writes bt_<tag>.csv
Variants are chosen with environment switches (DK_DRIFT, DK_DRIFT_MODE ...) set by the caller.
Only players who actually played the tested week, at QB/RB/WR/TE, with 2+ earlier games, are graded."""
import os, sys, subprocess, shutil, pandas as pd
sys.path.insert(0, '/home/claude/src/forecast'); import fc_model as FM
FM.STATS = os.environ.get('DK_STATS', '/home/claude/dksys/data/latest/stats_week.csv')   # the same stats file the engine uses
HERE = os.path.dirname(os.path.abspath(__file__))
w0, w1 = int(sys.argv[1]), int(sys.argv[2]); tag = sys.argv[3] if len(sys.argv) > 3 else 'run'
LG = {'DKI': 1, 'DKII': 2, 'DKIII': 3, 'DKIV': 4}
rows = []
env = dict(os.environ, DK_BT='1')
for W in range(w0, w1 + 1):
    r = subprocess.run([sys.executable, os.path.join(HERE, 'gotham.py'), str(W)], cwd=HERE, env=env, capture_output=True, text=True)
    if r.returncode: print(r.stdout[-500:], r.stderr[-1500:]); raise SystemExit('gotham failed week %d' % W)
    for lab, k in LG.items():
        E = pd.read_csv(os.path.join(HERE, f'gotham_{lab}.csv'))
        F = FM.frame(k); A = F[F.week == W].groupby('key').pts.sum()
        E = E[E.pos.isin(['QB', 'RB', 'WR', 'TE']) & (E.n_games >= 2)]
        for e in E.itertuples():
            if e.k in A.index and pd.notna(e.eng_wk):
                rows.append(dict(week=W, lg=lab, k=e.k, pos=e.pos, drift=str(e.drift) if 'drift' in E.columns else '', proj=float(e.eng_wk), act=float(A[e.k])))
R = pd.DataFrame(rows); R['miss'] = (R.proj - R.act).abs()
R.to_csv(os.path.join(HERE, f'bt_{tag}.csv'), index=False)
print(f'BT {tag}: weeks {w0}-{w1}, {len(R)} player-weeks, miss {R.miss.mean():.3f}')
print('  by league: ' + ', '.join(f'{l} {g.miss.mean():.3f}' for l, g in R.groupby('lg')))
d = R[R.drift == 'D']
if len(d): print(f'  drift-marked rows: {len(d)}, their miss {d.miss.mean():.3f}, bias {(d.proj - d.act).mean():+.2f}')
