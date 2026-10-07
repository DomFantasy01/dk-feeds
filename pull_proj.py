"""DK projection-source test pull (Oct 7 2026). Separate from pull_feeds.py so it can't break the news feed.
Every run: snapshot the CURRENT week from every source. First run (or BACKFILL=1): also pull past weeks
from sources that keep archives. A snapshot is saved ONLY when it changed, so the file list itself shows
when each source first publishes and how often it updates during the week. Each source fails alone, loudly."""
import json, os, io, hashlib, datetime as dt, urllib.request, urllib.parse, traceback
import pandas as pd
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
OUT = 'feeds/proj'; SEASON = 2026
NOW = dt.datetime.utcnow().strftime('%Y-%m-%dT%H%MZ')
STATUS = {'run_utc': NOW, 'sources': {}}
def get(url, headers=None, timeout=40):
    h = dict(UA); h.update(headers or {})
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
        return r.read().decode('utf-8', 'replace')
def save(src, week, df):
    if df is None or len(df) == 0: raise RuntimeError('empty table')
    d = f'{OUT}/{src}'; os.makedirs(d, exist_ok=True)
    body = df.to_csv(index=False); hsh = hashlib.md5(body.encode()).hexdigest()[:10]
    last = f'{d}/wk{week}_latest.hash'
    if os.path.exists(last) and open(last).read().strip() == hsh: return 'unchanged', len(df)
    open(f'{d}/wk{week}_{NOW}.csv', 'w').write(body); open(last, 'w').write(hsh)
    return 'saved', len(df)
def current_week():
    s = json.loads(get('https://api.sleeper.app/v1/state/nfl')); return int(s['week'])
# ---------------- sources ----------------
def sleeper(w):
    rows = []
    for p in ['QB', 'RB', 'WR', 'TE']:
        for r in json.loads(get(f'https://api.sleeper.app/projections/nfl/{SEASON}/{w}?season_type=regular&position[]={p}')):
            pl = r.get('player') or {}; st = r.get('stats') or {}
            rows.append(dict(name=f"{pl.get('first_name','')} {pl.get('last_name','')}".strip(), pos=p, team=r.get('team') or pl.get('team'),
                **{k: st.get(k) for k in ['pts_ppr', 'pass_yd', 'pass_td', 'pass_int', 'rush_att', 'rush_yd', 'rush_td', 'rec', 'rec_tgt', 'rec_yd', 'rec_td', 'fum_lost']}))
    return pd.DataFrame(rows)
ESPN_POS = {1: 'QB', 2: 'RB', 3: 'WR', 4: 'TE'}
ESPN_STAT = {'3': 'pass_yd', '4': 'pass_td', '20': 'pass_int', '23': 'rush_att', '24': 'rush_yd', '25': 'rush_td', '53': 'rec', '58': 'rec_tgt', '42': 'rec_yd', '43': 'rec_td'}
def espn(w):
    flt = {"players": {"filterSlotIds": {"value": [0, 2, 4, 6]}, "filterStatsForSourceIds": {"value": [1]},
           "filterStatsForSplitTypeIds": {"value": [1]}, "limit": 1200, "sortPercOwned": {"sortAsc": False, "sortPriority": 1}}}
    url = f'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{SEASON}/segments/0/leaguedefaults/3?scoringPeriodId={w}&view=kona_player_info'
    js = json.loads(get(url, {'X-Fantasy-Filter': json.dumps(flt), 'Accept': 'application/json'}))
    rows = []
    for e in js.get('players', []):
        pl = e.get('player', {}); pos = ESPN_POS.get(pl.get('defaultPositionId'))
        if not pos: continue
        for s in pl.get('stats', []):
            if s.get('statSourceId') == 1 and s.get('scoringPeriodId') == w and s.get('statSplitTypeId') == 1:
                st = s.get('stats', {})
                rows.append(dict(name=pl.get('fullName'), pos=pos, team=pl.get('proTeamId'), pts_ppr=s.get('appliedTotal'),
                                 **{v: st.get(k) for k, v in ESPN_STAT.items()}))
    return pd.DataFrame(rows)
def fftoday(w):
    out = []
    for pos, pid in [('QB', 10), ('RB', 20), ('WR', 30), ('TE', 40)]:
        for page in range(0, 3):
            html = get(f'https://www.fftoday.com/rankings/playerwkproj.php?Season={SEASON}&GameWeek={w}&PosID={pid}&LeagueID=107644&order_by=FFPts&sort_order=DESC&cur_page={page}')
            t = [x for x in pd.read_html(io.StringIO(html)) if x.shape[1] >= 6 and x.shape[0] > 10]
            if not t: break
            df = t[-1]; df['pos'] = pos; out.append(df)
    return pd.concat(out, ignore_index=True) if out else None
def nflcom(w):
    out = []
    for off in range(1, 401, 25):
        html = get(f'https://fantasy.nfl.com/research/projections?offset={off}&position=O&sort=projectedPts&statCategory=projectedStats&statSeason={SEASON}&statType=weekProjectedStats&statWeek={w}')
        t = [x for x in pd.read_html(io.StringIO(html)) if x.shape[0] > 5]
        if not t: break
        out.append(t[0])
    return pd.concat(out, ignore_index=True) if out else None
def fantasypros(w):
    out = []
    for pos in ['qb', 'rb', 'wr', 'te']:
        html = get(f'https://www.fantasypros.com/nfl/projections/{pos}.php?week={w}&scoring=PPR')
        t = [x for x in pd.read_html(io.StringIO(html)) if x.shape[0] > 10]
        if t:
            df = t[0]; df.columns = [' '.join(map(str, c)) if isinstance(c, tuple) else str(c) for c in df.columns]; df['pos'] = pos.upper(); out.append(df)
    return pd.concat(out, ignore_index=True) if out else None
def cbs(w):
    out = []
    for pos in ['QB', 'RB', 'WR', 'TE']:
        html = get(f'https://www.cbssports.com/fantasy/football/stats/{pos}/{SEASON}/{w}/projections/ppr/')
        t = [x for x in pd.read_html(io.StringIO(html)) if x.shape[0] > 10]
        if t:
            df = t[0]; df.columns = [' '.join(map(str, c)) if isinstance(c, tuple) else str(c) for c in df.columns]; df['pos'] = pos; out.append(df)
    return pd.concat(out, ignore_index=True) if out else None
SOURCES = {'sleeper': sleeper, 'espn': espn, 'fftoday': fftoday, 'nflcom': nflcom, 'fantasypros': fantasypros, 'cbs': cbs}
def run(src, fn, w):
    try:
        res, n = save(src, w, fn(w)); STATUS['sources'].setdefault(src, {})[f'wk{w}'] = f'{res} {n} rows'
    except Exception as e:
        STATUS['sources'].setdefault(src, {})[f'wk{w}'] = 'FAILED: ' + repr(e)[:200]
if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    try: W = current_week()
    except Exception as e: W = int(os.environ.get('DK_WEEK', '6')); STATUS['week_note'] = 'Sleeper state failed, used DK_WEEK: ' + repr(e)[:100]
    STATUS['current_week'] = W
    weeks = [W]
    if os.environ.get('BACKFILL') == '1' or not os.path.exists(f'{OUT}/.backfilled'):
        weeks = list(range(2, W + 1)); open(f'{OUT}/.backfilled', 'w').write(NOW)
    for w in weeks:
        for src, fn in SOURCES.items(): run(src, fn, w)
    hist = f'{OUT}/status_log.jsonl'
    open(hist, 'a').write(json.dumps(STATUS) + '\n'); json.dump(STATUS, open(f'{OUT}/status.json', 'w'), indent=1)
    print(json.dumps(STATUS, indent=1))
