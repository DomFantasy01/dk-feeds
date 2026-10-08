"""In-job grader (Oct 7). Runs after pull_proj.py inside GitHub. Writes feeds/proj/RESULTS.txt (plain English) + RESULTS.json.
For every source and the CONSENSUS (average of all sources): miss vs ACTUAL, on the SAME players Yahoo projected
(baseline/yahoo_engine_wk2_4.csv), so 'beat Yahoo' is apples to apples. Two snapshots per week:
EARLY = first one saved (what you'd have before waivers), LATE = last before games. Also reports timing:
when each source first had numbers for each week and how many times it changed."""
import glob, os, re, json, datetime as dt
import pandas as pd, numpy as np
from actuals import actuals, norm
OUT = 'feeds/proj'; SRC = ['sleeper', 'espn', 'nflcom', 'fftoday', 'cbs']   # sleeper_kdef collected only; K/DEF graded outside the job vs Yahoo K/DEF
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
def most(py=0, ptd=0, pint=0, ra=0, ry=0, rtd=0, rec=0, rcy=0, rctd=0, fl=0):
    return py/25 + 6*ptd - 2*pint + .25*ra + ry/10 + 6*rtd + rec + rcy/10 + 6*rctd - 2*fl
def num(x): return pd.to_numeric(x, errors='coerce').fillna(0)
def load_cbs(fp, w):
    df = pd.read_csv(fp); col = lambda k: num(df[k]) if k in df else 0
    # name cell looks like "D. Prescott  QB  DAL  Dak Prescott  QB  DAL" -> full name is the 4th chunk
    parts = df.iloc[:, 0].astype(str).str.split(r'\s{2,}')
    nm = parts.map(lambda p: p[3] if len(p) >= 4 else p[0])
    p = most(col('Passing yds  Passing Yards'), col('Passing td  Touchdowns Passes'), col('Passing int  Interceptions Thrown'),
             col('Rushing att  Rushing Attempts'), col('Rushing yds  Rushing Yards'), col('Rushing td  Rushing Touchdowns'),
             col('Receiving rec  Receptions'), col('Receiving yds  Receiving Yards'), col('Receiving td  Receiving Touchdowns'), col('Misc fl  Fumbles Lost'))
    return pd.DataFrame({'k': nm.map(norm), 'W': w, 'p': p}).dropna().drop_duplicates('k')
def load_fftoday(fp, w):
    raw = pd.read_csv(fp, header=None, dtype=str).iloc[1:]   # row 0 = pandas index labels
    out, hdr = [], None
    for i in range(len(raw)):
        r = raw.iloc[i]
        if 'Player' in str(r[1]):                            # header row; the row above holds Passing/Rushing/Receiving
            grp = raw.iloc[i - 1].ffill() if i > 0 else r
            hdr = [f'{str(g).strip()} {str(h).strip()}' for g, h in zip(grp, r)]; continue
        if hdr is None or pd.isna(r[1]) or str(r[1]).strip() in ('', 'nan') or 'Passing' in str(r[4]) or 'Rushing' in str(r[4]): continue
        d = dict(zip(hdr, r)); g = lambda k: float(np.nan_to_num(pd.to_numeric(d.get(k), errors='coerce')))
        out.append(dict(k=norm(r[1]), W=w, p=most(g('Passing Yard'), g('Passing TD'), g('Passing INT'), g('Rushing Att'), g('Rushing Yard'),
                                                 g('Rushing TD'), g('Receiving Rec'), g('Receiving Yard'), g('Receiving TD'))))
    return pd.DataFrame(out).drop_duplicates('k') if out else None
LOADERS = {'cbs': load_cbs, 'fftoday': load_fftoday}
def load(fp, w):
    for s, f in LOADERS.items():
        if f'/{s}/' in fp: return f(fp, w)
    # generic path (sleeper, espn, others)
    df = pd.read_csv(fp); nc = namecol(df); p = price(df)
    if nc is None or p is None: return None
    nm = df[nc].astype(str).str.replace(r'\s+(QB|RB|WR|TE|FA)\b.*$', '', regex=True).str.replace(r'\s{2,}.*$', '', regex=True)
    return pd.DataFrame({'k': nm.map(norm), 'W': w, 'p': p}).dropna().drop_duplicates('k')
def stamp(fp): return os.path.basename(fp).split('_', 1)[1].replace('.csv', '')

def ignores_week(s):
    """Tripwire (added after the Oct 7 CBS finding): if a source's saved Week 2/3/4 numbers are the same as each
    other, it is handing back one week's projections for every week -> its past weeks are hindsight, not a test."""
    xs = []
    for w in (2, 3, 4):
        fs = sorted(glob.glob(f'{OUT}/{s}/wk{w}_2*.csv'))
        if fs:
            x = load(fs[0], w)
            if x is not None and len(x): xs.append(x.set_index('k').p)
    for a, b in zip(xs, xs[1:]):
        j = a.index.intersection(b.index)
        if len(j) > 30 and (a[j] - b[j]).abs().lt(.01).mean() > .9: return True
    return False
def kickoffs():
    """First kickoff of each week in UTC, from the free nflverse schedule."""
    import urllib.request, io
    from zoneinfo import ZoneInfo
    g = pd.read_csv(io.BytesIO(urllib.request.urlopen('https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv', timeout=60).read()))
    g = g[(g.season == 2026) & (g.game_type == 'REG')].copy()
    g['ko'] = pd.to_datetime(g.gameday + ' ' + g.gametime).dt.tz_localize(ZoneInfo('America/New_York')).dt.tz_convert('UTC')
    return g.groupby('week').ko.min().to_dict()
def snap_time(fp): return pd.Timestamp(dt.datetime.strptime(stamp(fp), '%Y-%m-%dT%H%MZ'), tz='UTC')
def live_weeks(ACT, last_wk, voided):
    """Weeks the job watched live (snapshot saved BEFORE first kickoff). Graded vs Yahoo if baseline/yahoo_wk<W>.csv
    exists (k,YAHOO), else vs Sleeper's pre-kickoff number as the stand-in (Sleeper tied Yahoo exactly, Wks 2-4)."""
    KO = kickoffs(); L = []; out = {}
    for w in range(5, last_wk + 1):
        pre = {}
        for s in SRC:
            fs = [f for f in sorted(glob.glob(f'{OUT}/{s}/wk{w}_2*.csv')) if snap_time(f) < KO.get(w, pd.Timestamp.max.tz_localize('UTC'))]
            if fs:
                x = load(fs[0], w)
                if x is not None: pre[s] = x.set_index('k').p
        yb = f'baseline/yahoo_wk{w}.csv'
        ref_name, ref = ('Yahoo', pd.read_csv(yb).assign(k=lambda d: d.k.map(norm)).set_index('k').YAHOO) if os.path.exists(yb) else ('Sleeper (Yahoo stand-in)', pre.get('sleeper'))
        if ref is None: L.append(f'  Week {w}: no pre-kickoff reference numbers saved - not graded'); continue
        keys = ref[ref >= 5].index                                    # fantasy-relevant players only
        a = pd.Series({k: ACT.get((k, w)) for k in keys}).dropna()
        L.append(f'  Week {w} (pre-kickoff snapshots, {len(a)} players, compared with {ref_name} miss {(ref[a.index] - a).abs().mean():.2f}):')
        for s, x in pre.items():
            j = a.index.intersection(x.index)
            if len(j) < 50: L.append(f'    {s:12} only {len(j)} matched players'); continue
            m = (x[j] - a[j]).abs().mean(); r = (ref[j] - a[j]).abs().mean(); out.setdefault(s, {})[w] = round(r - m, 2)
            L.append(f'    {s:12} miss {m:5.2f} vs {r:5.2f} -> {"better" if r - m >= .10 else ("about even" if r - m > -.10 else "worse")} by {abs(r - m):.2f}')
    return L, out
def main():
    ACT, last_wk = actuals()
    B = pd.read_csv('baseline/yahoo_engine_wk2_4.csv'); B['k'] = B.k.map(norm)
    B['ACT'] = [ACT.get((k, w)) for k, w in zip(B.k, B.W)]; B = B.dropna(subset=['ACT'])
    res = {'graded_utc': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%MZ'), 'actuals_through_week': last_wk, 'sources': {}, 'timing': {}}
    lines = []
    voided = [s for s in SRC if ignores_week(s)]
    res['voided_ignores_week'] = voided
    for snap in ('early', 'late'):
        G = B.copy(); have = []
        for s in [x for x in SRC if x not in voided]:
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
    for v in voided: L.append(f"VOIDED  {v}: hands back the same numbers for every past week asked for -> its Weeks 2-4 would be hindsight. Graded live-only from now on.")
    LW, res['live'] = live_weeks(ACT, last_wk, voided)
    L += ["", "LIVE WEEKS (numbers saved before that week's first kickoff - the only fair test for live-only sources):"] + (LW or ["  none yet - first live week is Week 5; it grades once Week 5 stats post (Tue)"]) + [""]
    L.append("NOT GRADED (no usable Weeks 2-4 data - source keeps no past weeks, blocked, or page format not read):")
    for s in SRC:
        if s not in res['sources'] and s not in voided:
            why = '; '.join(f'{w}: {m}' for w, m in st.get('sources', {}).get(s, {}).items() if 'FAILED' in str(m)) or 'no past-week files'
            L.append(f"  {s:12} {why[:160]}")
    L += ["", "TIMING (first time each source had numbers for a week, in UTC; Pacific = UTC minus 7 until Nov 1).",
          "  NOTE: weeks pulled on the first run carry the first-run date, so timing is only real for weeks that start after the job is live."]
    for s, wk in res['timing'].items():
        L.append(f"  {s:12} " + '  '.join(f"{w}: {t['first_seen_utc']} ({t['versions']} version{'s' if t['versions'] != 1 else ''})" for w, t in sorted(wk.items())))
    L += ["", "Bar to go on the meter: beats Yahoo by 0.10+ AND wins at least 2 of 3 weeks AND publishes before waivers clear (Wed)."]
    json.dump(res, open(f'{OUT}/RESULTS.json', 'w'), indent=1, default=str)
    open(f'{OUT}/RESULTS.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
if __name__ == '__main__':
    try: main()
    except Exception as e:
        os.makedirs(OUT, exist_ok=True); open(f'{OUT}/RESULTS.txt', 'w').write('GRADING FAILED: ' + repr(e)[:300] + '\n'); print('GRADING FAILED', e)
