"""METER DATA — the one data layer behind the mountains page (Dark Knight Dispatch page 1). Built Thu Oct 8 2026.
Run:  python3 meter_data.py            (week read from the NFL schedule: first week with unplayed games)
      python3 meter_data.py 5          (force a week)
Writes  /home/claude/dksys/data/latest/meter/meter_wk<W>.json   and   alarm_wk<W>.json
Nothing in here is typed by hand per week. Every number carries whose it is and when it was pulled.

THREE NEEDLES per league (Dom, Oct 8):
  CENTER = Yahoo's own posted win %, exactly as on Yahoo's matchup page.
  LEFT   = GOTHAM: Gotham's points for every starter on both sides, through the win-probability math below.
  RIGHT  = SLEEPER: Sleeper's public projections, priced in the league's own scoring, through the same math.
  Kickers and defenses: Sleeper's numbers in both Gotham and Sleeper totals (Oct 8 test: nobody beats a flat average there).
  A starter Gotham cannot model (no NFL games on record) falls back to Yahoo's number and is counted as a fallback.
WIN-PROBABILITY MATH (unchanged from the page): banked points count as banked; for everyone still to play, the spread is
  each slot's sigma (QB 8, RB 8, WR 8.5, TE 6.5, K 4.5, DEF 6.5) with correlation .14 inside a side; chance = Phi(gap / spread).
ALARM: any source missing, older than its limit, or short on rows/teams -> listed in alarm_wk<W>.json and on the page.
"""
import os, sys, re, json, glob, math, datetime as dt
import pandas as pd
sys.path.insert(0, '/home/claude/dksys/gather'); from names import norm
sys.path.insert(0, '/home/claude/src/forecast'); import fc_model as FM

ROOT = '/home/claude/dksys/data/latest/'
FEEDS = '/home/claude/domfantasy01/dk-feeds/feeds/'
ENGINE = '/home/claude/dksys/engine/'
OUT = ROOT + 'meter/'
PT = dt.timezone(dt.timedelta(hours=-7))          # Pacific daylight time until Nov 1
NOW = dt.datetime.now(PT)

LEAGUES = {   # league facts that do not change week to week
 'DK I':   dict(id='269381',  me='Dark Knight I',   k=1, full='TheMostImportantThingInLife', slots=10),
 'DK II':  dict(id='1519795', me='Dark Knight II',  k=2, full='Winners and Sinners',         slots=11),
 'DK III': dict(id='1507991', me='Dark Knight III', k=3, full='Hers and His Version 2.0',    slots=9),
 'DK IV':  dict(id='864215',  me='Dark Knight IV',  k=4, full='Murrieta NextDoor',           slots=11),
}
SIG = {'QB': 8.0, 'RB': 8.0, 'WR': 8.5, 'TE': 6.5, 'K': 4.5, 'DEF': 6.5}; RHO = .14
SCORING = json.load(open(ROOT + 'yahoo/scoring/scoring_audit_oct1.json'))
TEAMFIX = {'WSH': 'WAS', 'JAC': 'JAX', 'LA': 'LAR'}
def T(t): t = str(t).upper(); return TEAMFIX.get(t, t)

alarms, sources, notes = [], {}, []
lineup = []   # Oct 21 (Dom): lineup problems on Dom's side (a starter on bye, an empty slot) - real, but not a broken data source
def stamp(key, path, limit_h, rows=None, need=None, note=''):
    """record a source with its age; raise an alarm if missing, stale or short"""
    if not path or not os.path.exists(path):
        alarms.append(f'{key}: MISSING ({path})'); sources[key] = dict(status='MISSING', path=path); return
    m = file_time(path) or dt.datetime.fromtimestamp(os.path.getmtime(path), PT)
    age = (NOW - m).total_seconds() / 3600
    st = 'OK'
    if age > limit_h: st = 'STALE'; alarms.append(f'{key}: STALE - {age:.1f} h old (limit {limit_h} h)')
    if need is not None and rows is not None and rows < need:
        st = 'SHORT'; alarms.append(f'{key}: SHORT - {rows} of {need}')
    sources[key] = dict(status=st, path=path, pulled_pt=m.strftime('%a %b %d %I:%M %p PT'), age_h=round(age, 1), rows=rows, need=need, note=note)

def file_time(path):
    """the pull time written inside the file (header line, or "pulled_pt" in a JSON) beats the disk time when present"""
    try:
        head = open(path, errors="ignore").read(400)
        m = re.search(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (\w{3}) (\d{1,2}),?(?: (\d{4}))? (\d{1,2}):(\d{2}) ([AP]M) PT", head)
        if not m: return None
        t = dt.datetime.strptime(f"{m.group(2)} {m.group(3)} {m.group(4) or NOW.year} {m.group(5)}:{m.group(6)} {m.group(7)}", "%b %d %Y %I:%M %p")
        return t.replace(tzinfo=PT)
    except Exception: return None

# ---------------------------------------------------------------- the week
G = pd.read_csv(ROOT + 'games.csv', low_memory=False); G = G[(G.season == 2026) & (G.game_type == 'REG')]
WEEK = int(sys.argv[1]) if len(sys.argv) > 1 else int(G[G.result.isna()].week.min())
if len(sys.argv) <= 1 and WEEK > 1 and not glob.glob(ROOT + f'yahoo/wk{WEEK}/dom_matchups_*.txt'): WEEK -= 1   # Oct 12: hold the week until Yahoo's first read of it
GW = G[G.week == WEEK]
stamp('nfl_schedule', ROOT + 'games.csv', 30, rows=len(GW), need=len(GW), note=f'week {WEEK}: {len(GW)} games')

# game windows from this week's real kickoffs (nflverse gametime is Eastern); same rules as the page always used
DORD = {'Thursday': 0, 'Friday': 1, 'Saturday': 2, 'Sunday': 3, 'Monday': 4}
DAB = {'Thursday': 'THU', 'Friday': 'FRI', 'Saturday': 'SAT', 'Sunday': 'SUN', 'Monday': 'MON'}
def mins(t): return int(t[:2]) * 60 + int(t[3:5])
slots = sorted({(r.weekday, r.gametime) for r in GW.itertuples()}, key=lambda k: (DORD[k[0]], mins(k[1])))
WINS = []
for d, t in slots:
    if WINS and WINS[-1]['day'] == d and mins(t) - mins(WINS[-1]['slots'][-1]) <= 45: WINS[-1]['slots'].append(t)
    else: WINS.append(dict(day=d, et=t, slots=[t]))
for w in WINS:
    m = mins(w['et']) - 180; h = (m // 60) % 24; w['pt'] = f"{h % 12 or 12}:{m % 60:02d} {'PM' if h >= 12 else 'AM'}"
    w['lab'] = f"{DAB[w['day']]} {w['pt']}"
SLOTW = {(w['day'], t): i for i, w in enumerate(WINS) for t in w['slots']}
TEAMWIN = {}
for r in GW.itertuples():
    for tm in (r.home_team, r.away_team): TEAMWIN[T(tm)] = SLOTW[(r.weekday, r.gametime)]

# ---------------------------------------------------------------- Yahoo: Dom's four matchups (latest pull for this week)
def latest(pattern):
    f = sorted(glob.glob(pattern), key=lambda q: (file_time(q) or dt.datetime.fromtimestamp(os.path.getmtime(q), PT))); return f[-1] if f else None
YDIR = ROOT + f'yahoo/wk{WEEK}/'
MF = latest(YDIR + 'dom_matchups_*.txt'); SF = latest(YDIR + 'standings_*.txt'); WF = latest(YDIR + 'league_windows_*.txt')
def parse_side(s):
    out = []
    for it in s.split('|'):
        slot, name, team, st, ko, proj, pts = (it.split('^') + [''] * 7)[:7]
        name = re.sub(r'(No new player Notes|New Player Note|Player Notes?)$', '', name).strip()
        m = re.match(r"^(.*?)(Q|D|O|IR|SUS|PUP)$", name)
        if m and slot not in ('DEF',) and not name.endswith(('Jr', 'Sr', 'II', 'III', 'IV')): name, st = m.group(1), m.group(2)
        out.append(dict(slot=slot, player=name, team=T(team), status=st, kickoff=ko,
                        yahoo=float(proj) if proj not in ('', '–', '-') else None,
                        actual=float(pts) if pts not in ('', '–', '-') else None))
    return out
MATCH = {}
if MF:
    for line in open(MF):
        if line.startswith('#') or '#' not in line: continue
        lg, rest = line.rstrip('\n').split('#', 1); me, op = rest.split('##')
        MATCH[lg] = dict(me=parse_side(me), op=parse_side(op))
stamp('yahoo_matchups', MF, 26, rows=sum(len(v['me']) for v in MATCH.values()), need=sum(v['slots'] for v in LEAGUES.values()),
      note="Dom's four matchup pages, both sides, Yahoo proj + points")
# Yahoo's own win % and opponents from the all-teams sweep
YWIN, OPP, REC = {}, {}, {}
if WF:
    rows = [l.rstrip('\n').split('~') for l in open(WF) if not l.startswith('#') and l.strip()]
    for i in range(0, len(rows) - 1, 2):
        a, b = rows[i], rows[i + 1]
        for x, y in ((a, b), (b, a)):
            YWIN[(x[0], x[1])] = (int(x[3]) if x[3].strip() else None); OPP[(x[0], x[1])] = y[1]; REC[(x[0], x[1])] = x[2]
stamp('yahoo_all_teams', WF, 26, rows=len(YWIN), need=48, note='every team in all four leagues: Yahoo win %, record')
# standings: league rank, division rank, points for
STAND = {}
if SF:
    for line in open(SF):
        if line.startswith('#') or '#' not in line: continue
        lg, rest = line.rstrip('\n').split('#', 1); div = None; pos_in_div = 0; tbl = []
        for it in rest.split('|'):
            f = it.split('^')
            if len(f) == 1: div = f[0]; pos_in_div = 0; continue
            pos_in_div += 1
            nd = lg == '864215'
            tbl.append(dict(rank=int(f[0]), team=f[1], rec=f[2], div=div, div_rank=pos_in_div if div else None,
                            pf=float(f[3] if nd else f[4]), pa=float(f[4] if nd else f[5])))
        tb = pd.DataFrame(tbl); tb['pf_rank'] = tb.pf.rank(ascending=False, method='min').astype(int)
        STAND[lg] = tb
stamp('yahoo_standings', SF, 30, rows=sum(len(v) for v in STAND.values()), need=48, note='rank, division rank, points for')

# ---------------------------------------------------------------- Gotham
GST = ENGINE + 'gotham_status.json'
gs = json.load(open(GST)) if os.path.exists(GST) else {}
stamp('gotham', GST, 26, rows=gs.get('week'), need=WEEK, note=f"Gotham run {gs.get('run')} for week {gs.get('week')}")
if gs.get('week') != WEEK: alarms.append(f"gotham: built for week {gs.get('week')}, page is week {WEEK}")
GOT = {}
for lab in LEAGUES:
    f = ENGINE + f"gotham_{lab.replace(' ', '')}.csv"
    if os.path.exists(f):
        d = pd.read_csv(f); GOT[lab] = dict(zip(d.k.astype(str), d.eng_wk))

# ---------------------------------------------------------------- RATCLIFFE (Oct 28, Dom: the expert leads; FTN read in Dom's Chrome)
RC = {}   # (league k, key) -> this week's points in that league's scoring; key = norm(name), or ('DEF', team)
try:
    import subprocess as _sp
    _fr = _sp.run([sys.executable, '/home/claude/dksys/gather/ftn.py'], check=False, capture_output=True, text=True, timeout=120)
    if _fr.returncode != 0: alarms.append('ratcliffe: scoring failed - ' + (_fr.stderr or _fr.stdout).strip().splitlines()[-1][:160])
    _ftn = ROOT + 'ftn_scored.csv'
    if os.path.exists(_ftn):
        _fd = pd.read_csv(_ftn)
        for _r in _fd.itertuples():
            if pd.isna(_r.wk): continue
            RC[(int(_r.lg), ('DEF', T(_r.team)) if _r.pos == 'DST' else ('K', _r.key) if _r.pos == 'K' else _r.key)] = float(_r.wk)
        _rp = str(_fd.read_pt.dropna().iloc[0]) if _fd.read_pt.notna().any() else ''
        _rt = None
        try: _rt = dt.datetime.strptime(_rp.replace(' PT', ''), '%a %b %d %Y %I:%M %p').replace(tzinfo=PT)
        except Exception: pass
        _age = round((NOW - _rt).total_seconds() / 3600, 1) if _rt else None
        sources['ratcliffe'] = dict(status='OK' if _age is not None and _age <= 36 else 'STALE', path=_ftn, pulled_pt=_rp, age_h=_age, rows=len(_fd), note="Jeff Ratcliffe (FTN), scored in each league's rules")
        if _age is None or _age > 36: alarms.append(f"ratcliffe: STALE - FTN read {_rp or 'unknown'} ({_age} h old, limit 36 h)")
    else: alarms.append('ratcliffe: MISSING - no FTN read yet (yahoo_drop/ftn/)'); sources['ratcliffe'] = dict(status='MISSING', path=_ftn)
except Exception as _e: alarms.append(f'ratcliffe: read failed ({_e})')
def rc_of(k, name, pos, team):
    if pos == 'DEF': return RC.get((k, ('DEF', T(team))))
    if pos == 'K': return RC.get((k, ('K', norm(name))))
    return RC.get((k, norm(name)))
RC_FALL = {}

# ---------------------------------------------------------------- Sleeper (from Dom's GitHub feed job)
def newest_by_name(pattern):
    f = sorted(glob.glob(pattern)); return f[-1] if f else None      # job files carry their run time in the name
SKF = newest_by_name(FEEDS + f'proj/sleeper/wk{WEEK}_*.csv'); SKD = newest_by_name(FEEDS + f'proj/sleeper_kdef/wk{WEEK}_*.csv')
def ztime(p):
    m = re.search(r'_(\d{4}-\d{2}-\d{2})T(\d{4})Z', p or '')
    return dt.datetime.strptime(m.group(1) + m.group(2), '%Y-%m-%d%H%M').replace(tzinfo=dt.timezone.utc).astimezone(PT) if m else None
for key, p, need in (('sleeper_skill', SKF, 400), ('sleeper_kdef', SKD, 60)):
    n = len(pd.read_csv(p)) if p else 0
    stamp(key, p, 9999, rows=n, need=need, note='GitHub job run ' + (ztime(p).strftime('%a %I:%M %p PT') if p and ztime(p) else '?'))
    if p and ztime(p):
        age = round((NOW - ztime(p)).total_seconds() / 3600, 1)
        sources[key].update(pulled_pt=ztime(p).strftime('%a %b %d %I:%M %p PT'), age_h=age)
        try:   # Oct 12: the job's last good check counts, not the file name (the file only changes when Sleeper does)
            _js = json.load(open(FEEDS + 'proj/status.json')); _ok = str(_js['sources'][{'sleeper_skill':'sleeper','sleeper_kdef':'sleeper_kdef'}[key]].get(f'wk{WEEK}','')); _m = re.match(r'(\d{4}-\d{2}-\d{2})T(\d{4})Z', _js['run_utc'])
            if _m and not _ok.startswith('FAILED'):
                age = round((NOW - dt.datetime.strptime(_m.group(1)+_m.group(2), '%Y-%m-%d%H%M').replace(tzinfo=dt.timezone.utc).astimezone(PT)).total_seconds() / 3600, 1)
                sources[key]['note'] = f"GitHub job checked {age} h ago ({_ok})"
        except Exception: pass
        if age > 6: sources[key]['status'] = 'STALE'; alarms.append(f'{key}: STALE - GitHub job last checked {age} h ago (limit 6 h; the job runs every 2 h)')
BLANK = set()
SLAST = {}
def sleeper_tables(k):
    sc = FM.SC[k]; key = [s for s in SCORING if s.startswith(['', 'DK I ', 'DK II ', 'DK III ', 'DK IV '][k])][0]; cfg = SCORING[key]
    sk = pd.read_csv(SKF); sk.columns = [c.lower() for c in sk.columns]
    _blank = sk.drop(columns=[c for c in ('name', 'pos', 'team') if c in sk]).isna().all(axis=1)   # Oct 21: Sleeper lists him with no projection at all
    BLANK.update(sk[_blank].name.astype(str).map(norm)); sk = sk[~_blank].fillna(0)   # (it does that for hurt players) - not a 0, no number
    sk['pts'] = (.04 * sk.pass_yd + sc['ptd'] * sk.pass_td + sc['it'] * sk.pass_int + .1 * sk.rush_yd + 6 * sk.rush_td + sc['ra'] * sk.rush_att
                 + sk.rec + .1 * sk.rec_yd + 6 * sk.rec_td - 2 * sk.fum_lost)
    S = dict(zip(sk.name.astype(str).map(norm), sk.pts))
    # Oct 23 (Dom): Yahoo and Sleeper sometimes use different first names (Yahoo "Bam Knight" = Sleeper "Zonovan Knight").
    # Second key: last name + team + position, kept only when exactly one Sleeper player fits it.
    _lk = {}
    for _n, _t, _p, _v in zip(sk.name.astype(str), sk.team.astype(str), sk.pos.astype(str), sk.pts):
        _key = (norm(_n).split()[-1] if norm(_n) else '', T(_t), _p.upper()); _lk.setdefault(_key, []).append(_v)
    SLAST.update({kk: vv[0] for kk, vv in _lk.items() if len(vv) == 1})
    kd = pd.read_csv(SKD); KD = {}
    kc = cfg.get('K', {}); f40 = kc.get('fg40_49', 4); f50 = kc.get('fg50', 5); pm = kc.get('pat_miss', 0)
    pa = cfg.get('DEF_pa', [10, 7, 4, 1, 0, -1, -4])
    tiers = ('pts_allow_0', 'pts_allow_1_6', 'pts_allow_7_13', 'pts_allow_14_20', 'pts_allow_21_27', 'pts_allow_28_34', 'pts_allow_35p')
    for r in kd.itertuples():
        st = json.loads(r.stats)
        if r.pos == 'K':
            v = 3 * (st.get('fgm_0_19', 0) + st.get('fgm_20_29', 0) + st.get('fgm_30_39', 0)) + f40 * st.get('fgm_40_49', 0) + f50 * st.get('fgm_50p', 0) + st.get('xpm', 0) + pm * st.get('xpmiss', 0)
            KD[('K', norm(r.name))] = v
        else:
            v = sum(pa[i] * st.get(t, 0) for i, t in enumerate(tiers)) + st.get('sack', 0) + 2 * st.get('int', 0) + 2 * st.get('fum_rec', 0) + 6 * st.get('def_td', 0) + 2 * st.get('blk_kick', 0) + 2 * st.get('safe', 0)
            KD[('DEF', T(r.team))] = v
    return S, KD

# ---------------------------------------------------------------- per league
def pos_of(p):
    if p['slot'] in ('K', 'DEF'): return p['slot']
    return None
def side_var(players):
    s = [SIG.get(p['pos'], 8.0) for p in players if p['actual'] is None]
    ss = sum(x * x for x in s); st = sum(s); return ss + RHO * (st * st - ss)
def phi(z): return .5 * (1 + math.erf(z / math.sqrt(2)))
def chance(me, op, col):
    a = sum((p['actual'] if p['actual'] is not None else (p[col] or 0)) for p in me)
    b = sum((p['actual'] if p['actual'] is not None else (p[col] or 0)) for p in op)
    v = side_var(me) + side_var(op)
    if v <= 0: return a, b, (100 if a > b else 0 if a < b else 50)
    return a, b, round(100 * phi((a - b) / math.sqrt(v)))

POSMAP = {}
for f in glob.glob(ENGINE + 'gotham_*.csv'):
    d = pd.read_csv(f); POSMAP.update(dict(zip(d.k.astype(str), d.pos)))
RN = pd.read_csv(ROOT + 'rosters_nfl.csv', low_memory=False)
RN = RN[RN.week == RN.week.max()] if 'week' in RN else RN
POSMAP.update({norm(str(a)): b for a, b in zip(RN.full_name, RN.position) if str(a) != 'nan' and norm(str(a)) not in POSMAP})

LEAGUE_OUT, fallback_total = {}, 0
for lab, cfg in LEAGUES.items():
    if cfg['id'] not in MATCH: alarms.append(f'{lab}: no Yahoo matchup data for week {WEEK}'); continue
    S, KD = sleeper_tables(cfg['k']); gm = GOT.get(lab, {})
    sides = {}
    for side in ('me', 'op'):
        L = []
        for p in MATCH[cfg['id']][side]:
            k = norm(p['player']); pos = p['slot'] if p['slot'] in ('K', 'DEF') else POSMAP.get(k, p['slot'] if p['slot'] in SIG else 'WR')
            if pos in ('K', 'DEF'):
                sl = KD.get(('K', k)) if pos == 'K' else KD.get(('DEF', p['team']))
                go, gsrc = sl, 'sleeper'
                _rkd = rc_of(cfg['k'], p['player'], pos, p.get('team'))   # Oct 28 (Dom): Sleeper off the meters - kickers and defenses take Ratcliffe's number on the Gotham needle too
                if _rkd is not None: go, gsrc = _rkd, 'ratcliffe'
            else:
                sl = S.get(k); go = gm.get(k); gsrc = 'gotham'
                if sl is None and k and k not in BLANK: sl = SLAST.get((k.split()[-1], T(p.get('team') or ''), pos))   # Oct 23: same man, different first name
                if go is None or (isinstance(go, float) and math.isnan(go)):   # Gotham has no usage rows for him (no 2026 snaps yet: a returner, a backup)
                    if sl is not None and p.get('yahoo') is not None and float(sl) > 0 and float(p['yahoo']) > 0:
                        go, gsrc = (float(p['yahoo']) + float(sl)) / 2, 'consensus-fallback'   # Oct 21: the Yahoo/Sleeper average - the same line as the Gotham ceiling
                    else:
                        go, gsrc = p['yahoo'], 'yahoo-fallback'
                    fallback_total += 1
            graw = go
            if gsrc == 'gotham' and sl is not None and p.get('yahoo') is not None and float(sl) > 0 and float(p['yahoo']) > 0:   # Oct 21 (Dom): the Gotham ceiling
                _gc = (float(p['yahoo']) + float(sl)) / 2
                if float(go) > _gc: go, gsrc = _gc, 'gotham-capped'
            win = TEAMWIN.get(p['team'])
            _empty = not p.get('team') or str(p['player']).strip().lower() in ('(empty)', 'empty', '')
            if sl is None and not _empty and win is not None:   # Oct 21: an empty slot or a team on bye has no number to find - that is not a data failure
                if k in BLANK: notes.append(f"{lab}: Sleeper lists {p['player']} with no projection (it blanks players it doubts) - Yahoo used on the Sleeper needle")
                else: notes.append(f"{lab}: no Sleeper number for {p['player']} ({pos}) - Sleeper is off the meters (Oct 28), noted only")
            _rc = rc_of(cfg['k'], p['player'], pos, p.get('team'))
            if _rc is None and not _empty and win is not None and RC: RC_FALL.setdefault(lab, []).append(p['player'])
            L.append(dict(p, pos=pos, gotham=None if go is None else round(float(go), 2), gotham_raw=None if graw is None else round(float(graw), 2), gotham_src=gsrc,
                          sleeper=round(float(sl if sl is not None else (p['yahoo'] or 0)), 2), window=win,
                          ratcliffe=round(float(_rc if _rc is not None else (p['yahoo'] or 0)), 2), ratcliffe_src='ftn' if _rc is not None else 'yahoo-fallback'))
        sides[side] = L
    me, op = sides['me'], sides['op']
    yt = chance(me, op, 'yahoo'); gt = chance(me, op, 'gotham'); st_ = chance(me, op, 'sleeper'); rt = chance(me, op, 'ratcliffe')
    if RC_FALL.get(lab): notes.append(f"{lab}: no Ratcliffe number for {', '.join(RC_FALL[lab])} - Yahoo used on the Ratcliffe needle")
    def wins(L, col):
        w = [0.0] * len(WINS); c = [0] * len(WINS)
        for p in L:
            if p['window'] is None: continue
            w[p['window']] += (p['actual'] if p['actual'] is not None else (p[col] or 0)); c[p['window']] += 1
        return [round(x, 2) for x in w], c
    tb = STAND.get(cfg['id']); mine = tb[tb.team == cfg['me']].iloc[0].to_dict() if tb is not None and (tb.team == cfg['me']).any() else {}
    opp = OPP.get((cfg['id'], cfg['me'])); theirs = tb[tb.team == opp].iloc[0].to_dict() if tb is not None and opp and (tb.team == opp).any() else {}
    LEAGUE_OUT[lab] = dict(
        league=cfg['full'], league_id=cfg['id'], me=cfg['me'], opp=opp,
        record=mine.get('rec'), opp_record=theirs.get('rec'), rank=mine.get('rank'), div=mine.get('div'), div_rank=mine.get('div_rank'),
        pf_rank=mine.get('pf_rank'), teams=len(tb) if tb is not None else None, opp_rank=theirs.get('rank'),
        needles=dict(gotham=gt[2], yahoo=YWIN.get((cfg['id'], cfg['me'])), sleeper=st_[2], yahoo_from_spread=yt[2], ratcliffe=rt[2] if RC else None),
        totals=dict(yahoo=[round(yt[0], 2), round(yt[1], 2)], gotham=[round(gt[0], 2), round(gt[1], 2)], sleeper=[round(st_[0], 2), round(st_[1], 2)],
                    ratcliffe=[round(rt[0], 2), round(rt[1], 2)] if RC else None),
        windows=dict(me=wins(me, 'yahoo'), op=wins(op, 'yahoo')),
        played=dict(me=sum(1 for p in me if p['actual'] is not None), op=sum(1 for p in op if p['actual'] is not None), of=[len(me), len(op)]),
        starters=dict(me=me, op=op))
    if len(me) != cfg['slots'] or len(op) != cfg['slots']:
        alarms.append(f"{lab}: starters {len(me)}/{len(op)} - league starts {cfg['slots']}")   # the read itself came back short or long
    for side, L in (('me', me), ('op', op)):
        for p in L:
            if not p.get('team') or str(p['player']).strip().lower() in ('(empty)', 'empty', ''):
                (lineup if side == 'me' else notes).append(f"{lab}: {'YOUR' if side == 'me' else 'opponent'} {p.get('slot') or p.get('pos')} slot is EMPTY")
    for side, L in (('me', me), ('op', op)):
        for p in L:
            if p['window'] is None and p['team'] not in ('', None):
                (lineup if side == 'me' else notes).append(f"{lab}: {'YOUR' if side=='me' else 'opponent'} starter {p['player']} ({p['team']}) has no game this week")
            if p['gotham'] is not None and p['sleeper'] is not None and p['yahoo'] is not None and p['pos'] not in ('K','DEF') and p.get('actual') is None:   # Oct 12: a played man's Gotham number is his final score
                outside = (p['yahoo'] + p['sleeper']) / 2
                if abs((p.get('gotham_raw') or p['gotham']) - outside) >= 6:
                    notes.append(f"{lab}: Gotham {(p.get('gotham_raw') or p['gotham']):.1f} vs Yahoo {p['yahoo']:.1f} / Sleeper {p['sleeper']:.1f} on {p['player']} - check role/news")

# ---- Dom's bench and IR (Field Report): from the latest Yahoo roster pull, numbers from the same sources as the starters
RF = latest(YDIR + 'dom_rosters.json')
if RF:
    RJ = json.load(open(RF)); stamp('yahoo_rosters', RF, 30, rows=sum(v['count'] for v in RJ['leagues'].values()), need=None, note="Dom's four rosters")
    TEAMOF = {}
    for f in glob.glob(ENGINE + 'gotham_*.csv'):
        d = pd.read_csv(f); TEAMOF.update(dict(zip(d.k.astype(str), d.team)))
    TEAMOF.update({norm(str(a)): T(b) for a, b in zip(RN.full_name, RN.team) if str(a) != 'nan' and norm(str(a)) not in TEAMOF})
    for lab, cfg in LEAGUES.items():
        if lab not in LEAGUE_OUT or lab not in RJ['leagues']: continue
        S, KD = sleeper_tables(cfg['k']); gm = GOT.get(lab, {})
        startk = {norm(p['player']) for p in LEAGUE_OUT[lab]['starters']['me']}
        out = []
        for p in RJ['leagues'][lab]['players']:
            if p['slot'] not in ('BN', 'IR'): continue
            k = norm(p['player']); pos = POSMAP.get(k, 'WR'); tm = TEAMOF.get(k, '')
            go = gm.get(k); go = None if go is None or (isinstance(go, float) and math.isnan(go)) else round(float(go), 2)
            sl = S.get(k)
            _rcb = rc_of(cfg['k'], p['player'], pos, tm)
            out.append(dict(slot=p['slot'], player=p['player'], team=tm, status=p['status'], pos=pos, yahoo=None, actual=None,
                            gotham=go, sleeper=None if sl is None else round(float(sl), 2), window=TEAMWIN.get(tm),
                            ratcliffe=None if _rcb is None else round(float(_rcb), 2)))
        try:   # Oct 12: a newer Scout roster read wins for bench and IR tags
            _n = {'DK I': 1, 'DK II': 2, 'DK III': 3, 'DK IV': 4}[lab]; _me = {'DK I': '2', 'DK II': '7', 'DK III': '2', 'DK IV': '6'}[lab]
            _f = f'/home/claude/dksys/scout/dk{_n}_rosters_live.txt'
            _pt = lambda s: dt.datetime.strptime(s, '%a %b %d %Y %I:%M %p') if s else None
            _sm = re.search(r'read live (\w{3} \w{3} \d{1,2} \d{4} \d{1,2}:\d{2} [AP]M) PT', open(_f).readline()) if os.path.exists(_f) else None
            _rm = re.search(r'(\w{3} \w{3} \d{1,2} \d{4} \d{1,2}:\d{2} [AP]M) PT', str(RJ.get('pulled_pt', '')))
            if _sm and (not _rm or _pt(_sm.group(1)) > _pt(_rm.group(1))):
                _tg = {norm(l.split('|')[2]): l.rstrip('\n').split('|')[5] for l in open(_f) if l.startswith(_me + '|') and l.count('|') >= 5}
                for o in out:
                    if norm(o['player']) in _tg: o['status'] = _tg[norm(o['player'])]
        except Exception as _e: notes.append(f'{lab}: bench tags from the Scout read skipped ({_e})')
        LEAGUE_OUT[lab]['bench'] = out

try:   # Oct 23 (Dom): MISSING PIECES - the one or two pieces that would push each team over the top (cand/missing_pieces.json)
    _MP = json.load(open('/home/claude/cand/missing_pieces.json'))
    for _lab, _L in LEAGUE_OUT.items(): _L['pieces'] = _MP['leagues'].get(_lab, []); _L['pieces_set'] = _MP.get('set')
except Exception as _e: notes.append(f'missing pieces not read: {_e}')
exec(open('/home/claude/cand/_state.py').read())   # Oct 13 (Dom): FINAL / LIVE / UPCOMING, one rule for every page
exec(open('/home/claude/cand/_best.py').read())   # Oct 13 5 PM (Dom): best legal lineup for both teams before any needle
os.makedirs(OUT, exist_ok=True)
meta = dict(week=WEEK, built_pt=NOW.strftime('%a %b %d %Y %I:%M %p PT'), windows=[w['lab'] for w in WINS],
            gotham_fallbacks=fallback_total, sources=sources, alarms=alarms, lineup=lineup, notes=notes, leagues=LEAGUE_OUT)
json.dump(meta, open(OUT + f'meter_wk{WEEK}.json', 'w'), indent=1, default=str)
json.dump(dict(week=WEEK, built_pt=meta['built_pt'], alarms=alarms, lineup=lineup, notes=notes, sources=sources), open(OUT + f'alarm_wk{WEEK}.json', 'w'), indent=1, default=str)
print(f'METER week {WEEK} built {meta["built_pt"]} | windows {meta["windows"]} | gotham fallbacks {fallback_total}')
for lab, v in LEAGUE_OUT.items():
    n = v['needles']; t = v['totals']
    print(f"{lab}: vs {v['opp']} ({v['opp_record']}) | {v['record']} rank {v['rank']} div {v['div_rank']} | GOTHAM {n['gotham']}% ({t['gotham'][0]}-{t['gotham'][1]})"
          f" | YAHOO {n['yahoo']}% ({t['yahoo'][0]}-{t['yahoo'][1]}) | SLEEPER {n['sleeper']}% ({t['sleeper'][0]}-{t['sleeper'][1]})")
for k, s in sources.items(): print(f"  source {k}: {s.get('status')} | {s.get('pulled_pt')} | age {s.get('age_h')} h | rows {s.get('rows')}/{s.get('need')}")
print('ALARMS:', len(alarms)); [print('  !', a) for a in alarms]
print('LINEUP:', len(lineup)); [print('  !', a) for a in lineup]
print('NOTES:', len(notes)); [print('  -', a) for a in notes]

# OCT12 meter false flags

# OCT12 bench tags fresh

# OCT12 week holds meter

# OCT13 meter state word

# OCT13 best lineup

# OCT21a the Gotham ceiling
