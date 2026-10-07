"""In-job grader (Oct 7). Runs after pull_proj.py inside GitHub. Writes feeds/proj/RESULTS.txt (plain English) + RESULTS.json.
For every source and the CONSENSUS (average of all sources): miss vs ACTUAL, on the SAME players Yahoo projected
(baseline/yahoo_engine_wk2_4.csv), so 'beat Yahoo' is apples to apples. Two snapshots per week:
EARLY = first one saved (what you'd have before waivers), LATE = last before games. Also reports timing:
when each source first had numbers for each week and how many times it changed."""
import glob, os, re, json, datetime as dt
import pandas as pd, numpy as np
from actuals import actuals, norm
OUT = 'feeds/proj'; SRC = ['sleeper', 'espn', 'fantasypros', 'nflcom', 'fftoday', 'cbs']
def price(df):
    c = lambda k: pd.to_numeric(df[k], errors='coerce').fillna(0) if k in df else 0
    if 'rush_yd' in df.columns and pd.to_numeric(df['rush_yd'], errors='coerce').notna().any():
        return c('pass_yd')/25 + 6*c('pass_td') - 2*c('pass_int') + c('rush_yd')/10 + 6*c('rush_td') + .25*c('rush_att') + c('rec') + c('rec_yd')/10 + 6*c('rec_td')
    for k in df.columns:   # web-page sources: use their own fantasy-points column
        if re.search(r'(fpts|ffpts|fantasy ?p|^pts$|points)', str(k), re.I): return pd.to_numeric(df[k], errors='coerce')
    return None
def namecol(df):
    for k in df.columns:
        if re.search(r'(player|^name)', str(k), re.I): return k
def load(fp, w):
    df = pd.read_csv(fp); nc = namecol(df); p = price(df)
    if nc is None or p is None: return None
    nm = df[nc].astype(str).str.replace(r'\s+(QB|RB|WR|TE|FA)\b.*$', '', regex=True).str.replace(r'\s{2,}.*$', '', regex=True)
    return pd.DataFrame({'k': nm.map(norm), 'W': w, 'p': p}).dropna().drop_duplicates('k')
def stamp(fp): return os.path.basename(fp).split('_', 1)[1].replace('.csv', '')
def main():
    ACT, last_wk = actuals()
    B = pd.read_csv('baseline/yahoo_engine_wk2_4.csv'); B['k'] = B.k.map(norm)
    B['ACT'] = [ACT.get((k, w)) for k, w in zip(B.k, B.W)]; B = B.dropna(subset=['ACT'])
    res = {'graded_utc': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%MZ'), 'actuals_through_week': last_wk, 'sources': {}, 'timing': {}}
    lines = []
    for snap in ('early', 'late'):
        G = B.copy(); have = []
        for s in SRC:
            parts = []
            for w in sorted(B.W.unique()):
                fs = sorted(glob.glob(f'{OUT}/{s}/wk{w}_2*.csv'))
                if fs:
                    x = load(fs[0] if snap == 'early' else fs[-1], w)
                    if x is not None: parts.append(x.rename(columns={'p': s}))
            if parts:
                G = G.merge(pd.concat(parts), on=['k', 'W'], how='left'); have.append(s)
        if have: G['CONSENSUS'] = G[have].mean(axis=1)
        for c in have + (['CONSENSUS'] if have else []):
            d = G[G[c].notna()]
            if len(d) < 50:
                res['sources'].setdefault(c, {})[snap] = f'only {len(d)} matched players - not enough to grade'; continue
            r = dict(rows=len(d), miss=round((d[c] - d.ACT).abs().mean(), 2), yahoo_miss_same_rows=round((d.YAHOO - d.ACT).abs().mean(), 2),
                     engine_miss_same_rows=round((d.ENGINE - d.ACT).abs().mean(), 2), corr=round(float(np.corrcoef(d[c], d.ACT)[0, 1]), 3),
                     weeks_beat_yahoo=int(sum((g[c] - g.ACT).abs().mean() < (g.YAHOO - g.ACT).abs().mean() for _, g in d.groupby('W'))),
                     weeks=int(d.W.nunique()))
            r['beats_yahoo_by'] = round(r['yahoo_miss_same_rows'] - r['miss'], 2)
            res['sources'].setdefault(c, {})[snap] = r
    for s in SRC:   # timing: first snapshot per week + number of changes
        for fp in sorted(glob.glob(f'{OUT}/{s}/wk*_2*.csv')):
            w = os.path.basename(fp).split('_')[0]
            t = res['timing'].setdefault(s, {}).setdefault(w, {'first_seen_utc': stamp(fp), 'versions': 0}); t['versions'] += 1
    st = json.load(open(f'{OUT}/status.json')) if os.path.exists(f'{OUT}/status.json') else {}
    json.dump(res, open(f'{OUT}/RESULTS.json', 'w'), indent=1)
    # ---- plain-English report ----
    L = [f"DK PROJECTION TEST  -  graded {res['graded_utc']} UTC  -  actual points through Week {last_wk}  -  MOST scoring",
         "Miss = average points off per player vs what he really scored. Lower is better.",
         "Each source is compared to Yahoo ON THE SAME PLAYERS, Weeks 2-4.", ""]
    for snap, title in (('early', 'EARLY numbers (first snapshot - what you would have before waivers)'), ('late', 'LATE numbers (last snapshot before games)')):
        L.append(title)
        rows = [(c, v[snap]) for c, v in res['sources'].items() if snap in v and isinstance(v[snap], dict)]
        for c, r in sorted(rows, key=lambda x: x[1]['miss']):
            verdict = 'BEATS Yahoo' if r['beats_yahoo_by'] >= 0.10 else ('ties Yahoo' if r['beats_yahoo_by'] > -0.10 else 'LOSES to Yahoo')
            L.append(f"  {c:12} miss {r['miss']:5.2f}  vs Yahoo {r['yahoo_miss_same_rows']:5.2f}  -> {verdict} by {abs(r['beats_yahoo_by']):.2f}"
                     f"   (won {r['weeks_beat_yahoo']} of {r['weeks']} weeks, {r['rows']} players)")
        for c, v in res['sources'].items():
            if isinstance(v.get(snap), str): L.append(f"  {c:12} {v[snap]}")
        L.append("")
    L.append("NOT GRADED (no usable Weeks 2-4 data - source keeps no past weeks, blocked, or page format not read):")
    for s in SRC:
        if s not in res['sources']:
            why = '; '.join(f'{w}: {m}' for w, m in st.get('sources', {}).get(s, {}).items() if 'FAILED' in str(m)) or 'no past-week files'
            L.append(f"  {s:12} {why[:160]}")
    L += ["", "TIMING (first time each source had numbers for a week, in UTC; Pacific = UTC minus 7 until Nov 1).",
          "  NOTE: weeks pulled on the first run carry the first-run date, so timing is only real for weeks that start after the job is live."]
    for s, wk in res['timing'].items():
        L.append(f"  {s:12} " + '  '.join(f"{w}: {t['first_seen_utc']} ({t['versions']} version{'s' if t['versions'] != 1 else ''})" for w, t in sorted(wk.items())))
    L += ["", "Bar to go on the meter: beats Yahoo by 0.10+ AND wins at least 2 of 3 weeks AND publishes before waivers clear (Wed)."]
    open(f'{OUT}/RESULTS.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
if __name__ == '__main__':
    try: main()
    except Exception as e:
        os.makedirs(OUT, exist_ok=True); open(f'{OUT}/RESULTS.txt', 'w').write('GRADING FAILED: ' + repr(e)[:300] + '\n'); print('GRADING FAILED', e)
