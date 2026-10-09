# THE RADAR v3 — data layer (Oct 8 2026). Built from live sources only; no hand-typed news.
# Per league it answers the Radar's jobs: (1) Dom's own men in the news (every grade), (2) COMING IN — men free in
# that league with good news, an opening (the man ahead of him has bad news), or heavy Sleeper add-trending,
# (3) OPPONENT WATCH — this week's opponent's starters in the news. Every source is stamped with its age; a thin,
# stale or failed source prints as a loud line, never a silent gap. It flags; it does not decide.
import json, re, glob, os, sys, unicodedata, datetime as dt
from zoneinfo import ZoneInfo
import pandas as pd

PT = ZoneInfo('America/Los_Angeles'); NOW = dt.datetime.now(dt.timezone.utc)
ROOT = os.environ.get('DK_ROOT', '/home/claude')
FEEDS = f'{ROOT}/domfantasy01/dk-feeds/feeds/'
DATA = f'{ROOT}/dksys/data/latest/'
ENG = f'{ROOT}/dksys/engine/'
OUTD = f'{ROOT}/dksys/data/latest/radar/'; os.makedirs(OUTD, exist_ok=True)
LG = {1: dict(lab='DK I', key='MOST', id='269381', me=2), 2: dict(lab='DK II', key='WINNERS', id='1519795', me=7),
      3: dict(lab='DK III', key='HERS&HIS', id='1507991', me=2), 4: dict(lab='DK IV', key='NEXTDOOR', id='864215', me=6)}
QUIET_GREY, QUIET_DROP = 2, 7          # Dom Oct 8: grey after 2 quiet days, off after 7 ("for now")

def norm(n):
    n = unicodedata.normalize('NFKD', str(n or '')); n = ''.join(c for c in n if not unicodedata.combining(c))
    n = re.sub(r"[.']", '', n).replace('-', ' ').strip(); n = re.sub(r'\s+(jr|sr|ii|iii|iv|v)\.?$', '', n, flags=re.I)
    return ' '.join(n.lower().split())
def ts(s):
    try: return dt.datetime.fromisoformat(str(s).replace('Z', '+00:00'))
    except Exception: return None
def ago(t):
    h = (NOW - t).total_seconds() / 3600
    return f'{h*60:.0f} min ago' if h < 1 else f'{h:.1f} h ago' if h < 48 else f'{h/24:.1f} days ago'
def ptxt(t): return t.astimezone(PT).strftime('%a %b %-d %-I:%M %p PT')

# ------------------------------------------------------------------ sources, each stamped
sources, alarms = {}, []
def src(key, label, pulled, items, newest=None, warn=None, failed=None):
    d = dict(label=label, pulled=ptxt(pulled) if pulled else None, pulled_ago=ago(pulled) if pulled else None,
             items=items, newest=ago(newest) if newest else None, warn=warn, failed=failed)
    sources[key] = d
    if failed: alarms.append(f'{label}: FAILED — {failed}')
    elif warn: alarms.append(f'{label}: {warn}')
    return d
try: STATUS = json.load(open(FEEDS + 'status.json'))
except Exception as e: STATUS = {'sources': {}}; alarms.append(f'feed job status.json unreadable: {e}')
run = ts(STATUS.get('run_utc'))
if run and (NOW - run).total_seconds() > 3 * 3600:
    alarms.append(f'feed job last ran {ago(run)} — the GitHub job may be down (it runs every 30 min)')

ITEMS = []      # (time, source, title, text)
def load_hist(fn, label, key):
    seen, n, newest = set(), 0, None
    for f in (FEEDS + fn + '_history.jsonl', FEEDS + fn + ('_latest.json' if fn == 'rotowire' else '.json')):
        if not os.path.exists(f): continue
        rows = [json.loads(l) for l in open(f) if l.strip()] if f.endswith('.jsonl') else json.load(open(f)).get('items', [])
        for it in rows:
            k = (it.get('title'), it.get('published_utc'))
            if k in seen: continue
            seen.add(k); t = ts(it.get('published_utc'))
            if not t: continue
            ITEMS.append((t, it.get('source') or label, it.get('title') or '', it.get('text') or '')); n += 1
            newest = max(newest, t) if newest else t
    st = STATUS.get('sources', {}).get(key, {})
    warn = st.get('warning') or (None if newest and (NOW - newest).total_seconds() < 12 * 3600 else 'newest item over 12 h old')
    src(key, label, ts(st.get('checked_utc')) or run, n, newest, warn, None if st.get('ok', True) else 'job reported a failure')
load_hist('rotowire', 'RotoWire news', 'rotowire')
load_hist('news_extra', 'PFT + RotoBaller news', 'news_extra')
load_hist('espn_news', 'ESPN news', 'espn_news')

INJ = {}
try:
    ej = json.load(open(FEEDS + 'espn_injuries.json'))
    for p in ej['players']:
        if p.get('pos') in ('QB', 'RB', 'WR', 'TE', 'K', 'FB'):
            INJ[norm(p['name'])] = p
    src('espn_inj', 'ESPN injury report', ts(ej.get('pulled_utc')), len(INJ), max((ts(p['date']) for p in INJ.values() if ts(p.get('date'))), default=None))
except Exception as e: src('espn_inj', 'ESPN injury report', None, 0, failed=str(e))

TREND = {}
try:
    sj = json.load(open(FEEDS + 'sleeper_trending.json'))
    for r in sj['add']: TREND[norm(r['name'])] = r
    src('sleeper_trend', 'Sleeper trending adds', ts(sj.get('pulled_utc')), len(TREND))
except Exception as e: src('sleeper_trend', 'Sleeper trending adds', None, 0, failed=str(e))

# ------------------------------------------------------------------ rosters (Yahoo, read by hand in Chrome — the one manual step)
RF = sorted(glob.glob(DATA + 'yahoo/wk*/all_rosters_*.txt'), key=os.path.getmtime)
OWN = {k: {} for k in LG}; UNREAD = {k: [] for k in LG}
if RF:
    rf = RF[-1]
    for ln in open(rf):
        if ln.startswith('#') or not ln.strip(): continue
        lg, tm, names = ln.rstrip('\n').split('~', 2); lg, tm = int(lg), int(tm)
        if not names: UNREAD[lg].append(tm); continue
        for n in names.split('|'): OWN[lg][norm(n)] = tm
    rt = dt.datetime.fromtimestamp(os.path.getmtime(rf), dt.timezone.utc)
    src('yahoo_rosters', 'Yahoo rosters, all 48 teams', rt, sum(len(v) for v in OWN.values()),
        warn=('unread team pages: ' + ', '.join(f"{LG[k]['lab']} team {t}" for k in LG for t in UNREAD[k])) if any(UNREAD.values()) else None)
    if (NOW - rt).total_seconds() > 30 * 3600: alarms.append(f'Yahoo rosters read {ago(rt)} — free-agent status may be wrong; re-read in Chrome')
else: src('yahoo_rosters', 'Yahoo rosters', None, 0, failed='no all_rosters file — run the Chrome roster read')

# ------------------------------------------------------------------ numbers: Gotham (engine) + Sleeper, per league scoring
sys.path.insert(0, f'{ROOT}/dksys/meter')
_src = open(f'{ROOT}/dksys/meter/meter_data.py').read()
_ns = {'__name__': 'radar'}; exec(compile(_src[:_src.index('# ---------------------------------------------------------------- per league')], 'meter_part', 'exec'), _ns)
GOT, SLP, PL = {}, {}, {}
for k in LG:
    g = pd.read_csv(f"{ENG}gotham_DK{['', 'I', 'II', 'III', 'IV'][k]}.csv")
    GOT[k] = {norm(r.player): r for r in g.itertuples()}
    SLP[k], _ = _ns['sleeper_tables'](k)
    for r in g.itertuples(): PL.setdefault(norm(r.player), (r.player, r.pos, r.team))
grun = g.gotham_run.iloc[0]
src('gotham', 'Gotham engine', None, len(PL)); sources['gotham']['pulled'] = grun
SKF = _ns['SKF']; m = re.search(r'_(\d{4}-\d{2}-\d{2})T(\d{4})Z', SKF or '')
skt = dt.datetime.strptime(m.group(1) + m.group(2), '%Y-%m-%d%H%M').replace(tzinfo=dt.timezone.utc) if m else None
src('sleeper_proj', 'Sleeper projections', skt, len(SLP[1]), warn='over 6 h old' if skt and (NOW - skt).total_seconds() > 6 * 3600 else None)
METER = json.load(open(sorted(glob.glob(DATA + 'meter/meter_wk*.json'), key=os.path.getmtime)[-1]))
WEEK = METER['week']

# ------------------------------------------------------------------ match news to players, grade it
BAD = r"\bout (\d+ |several |multiple |a few )?weeks?\b|\bout indefinitely\b|\bruled out\b|\bwon't play\b|\bwill not play\b|\bwill miss\b|\bplaced on (injured reserve|ir)\b|\bto ir\b|\bdid not practice\b|\bdidn't practice\b|\bdnp\b|\bdoubtful\b|season-ending|\btorn\b|\bsurgery\b|\breleased\b|\bwaived\b|\bsuspended\b|\bbenched\b|\bnot expected to play\b|\bout for\b|\bset to miss\b|\bunlikely to play\b|\bwon't suit up\b|\binactive\b"
CAUT = r"\blimited\b|\bquestionable\b|\bday-to-day\b|\bgame-time\b|\buncertain\b|\bmanaging\b|\bnursing\b|\btweaked\b|\bsore\b|\bpopped up\b|\bnew injury\b|\bcommittee\b|\bsplit\b|\bless work\b|\breduced role\b"
GOOD = r"\bfull practice\b|\bfully practiced\b|\bfull participant\b|\bpracticed fully\b|\bcleared\b|\bactivated\b|\bexpected to play\b|\bwill play\b|\bwill start\b|\bstarting\b|\bpromoted\b|\belevated\b|\bsigned\b|\blead back\b|\bbellcow\b|\bworkhorse\b|\bexpanded role\b|\bbigger role\b|\bincreased role\b|\bmore snaps\b|\btake over\b|\btaking over\b|\bin line for\b|\bno injury designation\b|\bremoved from injury report\b|\bon track to play\b|\bset to return\b|\breturn(ed|s)? to practice\b"
def grade(text):
    t = text.lower()
    if re.search(BAD, t): return 'bad'
    if re.search(GOOD, t) and not re.search(r'\blimited\b', t): return 'good'
    if re.search(CAUT, t): return 'caution'
    return 'note'
NAMES = sorted(PL, key=len, reverse=True)
NREG = re.compile(r'\b(' + '|'.join(re.escape(n) for n in NAMES if ' ' in n) + r')\b')
# roundups and listicles name dozens of men and say nothing new about any of them — they are mentions, not news
LISTICLE = re.compile(r"start 'em|sit 'em|who should i start|start/sit|waiver wire|rankings|bold predictions|sleepers|\bdfs\b|picks|matchups|preview|odds|props|\bvs\.? |power rankings|mailbag|takeaways|winners and losers|overreactions", re.I)
def clause(h, title, text):
    """the clause that names him: split on sentences, then on ',', ';', ' while ', ' but '"""
    for x in re.split(r'(?<=[.!?])\s+', title + '. ' + text):
        if h not in norm(x): continue
        for y in re.split(r',|;|\bwhile\b|\bbut\b|\band\b', x):
            if h in norm(y): return y
        return x
    return title
NEWS = {}          # key -> list of dict(t, src, title, grade)
for t, s, title, text in ITEMS:
    if (NOW - t).days > 14: continue
    hay = norm(title + ' ' + text)
    hits = set(NREG.findall(hay))
    head = norm(title.split(':')[0])                       # RotoWire titles lead with the name
    if head in PL: hits = {head} | hits
    roundup = bool(LISTICLE.search(title)) or len(hits) > 3
    for h in hits:
        g = 'mention' if roundup else grade(clause(h, title, text))
        NEWS.setdefault(h, []).append(dict(t=t, src=s, title=title.strip(), text=text.strip()[:260], grade=g))
for key, p in INJ.items():                                 # the injury report counts as news on its own date
    t = ts(p.get('date'))
    if not t or key not in PL or (NOW - t).days > 14: continue
    stt = (p.get('status') or '').lower(); det = (p.get('detail') or '').strip()
    if stt == 'active': continue        # the report lists every man recently mentioned; "Active" plus a box score is not news
    g = 'bad' if stt in ('out', 'doubtful', 'injured reserve') else 'caution' if stt == 'questionable' else grade(det)
    NEWS.setdefault(key, []).append(dict(t=t, src='ESPN injury report', title=f"{p['name']}: {p.get('status')}" + (f" ({p.get('type')})" if p.get('type') else ''),
                                         text=det[:260], grade=g))
for v in NEWS.values():
    v.sort(key=lambda d: d['t'], reverse=True)
    dd, out = set(), []
    for d in v:
        k = (d['title'][:60], d['t'].date())
        if k not in dd: dd.add(k); out.append(d)
    v[:] = out

def marker(items, own):
    """Dom Oct 8: LEFT = items on the newest news day only; RECENCY = days since that day; colour by the day's worst
    (own man) or best (incoming) grade; grey after 2 quiet days; off the sheet after 7."""
    items = [d for d in items if d['grade'] != 'mention']
    if not items: return None
    newest = items[0]['t'].astimezone(PT).date(); today = NOW.astimezone(PT).date()
    day = [d for d in items if d['t'].astimezone(PT).date() == newest]; rec = (today - newest).days
    if rec > QUIET_DROP: return None
    gs = {d['grade'] for d in day}
    col = 'grey' if rec > QUIET_GREY else ('red' if 'bad' in gs else 'gold' if 'caution' in gs else 'green' if 'good' in gs else 'grey') if own \
        else ('grey' if rec > QUIET_GREY else 'green' if 'good' in gs else 'gold')
    return dict(count=len(day), recency=rec, color=col, grades=sorted(gs))

def nums(k, key):
    r = GOT[k].get(key); s = SLP[k].get(key)
    return dict(gotham=None if r is None or pd.isna(r.eng_wk) else round(float(r.eng_wk), 1),
                gotham_ros=None if r is None or pd.isna(r.eng_fwd) else round(float(r.eng_fwd), 1),
                sleeper=None if s is None else round(float(s), 1), workload=None if r is None else r.wseq,
                trend=None if r is None or pd.isna(r.trend) else round(float(r.trend), 2))

# ------------------------------------------------------------------ per league
CANDS = {}
OUT = dict(week=WEEK, built=ptxt(NOW), built_utc=NOW.isoformat(), sources=sources, alarms=alarms, leagues={})
for k, L in LG.items():
    lab = L['lab']; ML = METER['leagues'][lab]
    slots = {norm(s['player']): s.get('slot') for s in ML['starters']['me'] + ML.get('bench', [])}
    mine = {n: {'player': PL[n][0], 'slot': slots.get(n, 'BN'), 'team': PL[n][2], 'pos': PL[n][1]} for n, t in OWN[k].items() if t == L['me'] and n in PL}
    opp = {norm(s['player']): s for s in ML['starters']['op']}
    floor = {}
    for s in ML['starters']['me']:
        gv = nums(k, norm(s['player']))['gotham']
        if gv is not None and s['pos'] in ('QB', 'RB', 'WR', 'TE') and (s['pos'] not in floor or gv < floor[s['pos']][1]): floor[s['pos']] = (s['player'], gv)
    rows = {'own': [], 'in': [], 'opp': []}
    for key, items in NEWS.items():
        name, pos, team = PL[key]
        if key in mine:
            mk = marker(items, True)
            if mk: rows['own'].append(dict(name=name, pos=pos, team=team, slot=mine[key].get('slot'), marker=mk, news=[d for d in items if d['grade'] != 'mention'][:3], **nums(k, key)))
        elif key in opp:
            mk = marker(items, True)
            if mk and mk['color'] in ('red', 'gold', 'green'): rows['opp'].append(dict(name=name, pos=pos, team=team, marker=mk, news=[d for d in items if d['grade'] != 'mention'][:2], **nums(k, key)))
    # COMING IN: free in this league, positive news / an opening / trending
    free = lambda n: n not in OWN[k] and n in PL and PL[n][1] in ('QB', 'RB', 'WR', 'TE')
    cand = {}
    for key, items in NEWS.items():
        if free(key):
            good = [d for d in items if d['grade'] == 'good']
            if good:
                mk = marker(good, False)
                if mk: cand.setdefault(key, dict(why=[], news=good[:2], marker=mk))['why'].append('good news')
    # openings: a man with bad/caution news ahead of a free teammate at the same position
    for key, items in NEWS.items():
        items = [d for d in items if d['grade'] != 'mention']
        if not items: continue
        top = items[0]
        if top['grade'] not in ('bad', 'caution') or (NOW - top['t']).days > 3: continue
        name, pos, team = PL[key]; gv = nums(k, key)['gotham'] or 0
        if pos not in ('QB', 'RB', 'WR', 'TE') or gv < 8: continue
        mates = sorted([n for n in PL if PL[n][2] == team and PL[n][1] == pos and n != key and free(n)],
                       key=lambda n: -(SLP[k].get(n) or 0))[:2]
        for n in mates:
            c = cand.setdefault(n, dict(why=[], news=list(NEWS.get(n, [])[:1]), marker=dict(count=1, recency=(NOW.astimezone(PT).date() - top['t'].astimezone(PT).date()).days, color='gold', grades=['opening'])))
            c['why'].append(f"opening: {name} — {'bad news' if top['grade']=='bad' else 'questionable/limited'} ({top['src']})")
    for key, r in TREND.items():
        if free(key) and r['rank'] <= 25:
            c = cand.setdefault(key, dict(why=[], news=list(NEWS.get(key, [])[:1]), marker=marker(NEWS.get(key, []), False) or dict(count=0, recency=None, color='gold', grades=['trend'])))
            c['why'].append(f"Sleeper adds #{r['rank']} ({r['count']:,} in 24 h)")
    VF = sorted(glob.glob(DATA + f'yahoo/wk{WEEK}/radar_verify_*.json'), key=os.path.getmtime)
    VER = json.load(open(VF[-1])).get(lab, {}) if VF else {}
    for key, c in cand.items():
        name, pos, team = PL[key]; nm = nums(k, key); fl = floor.get(pos)
        v = VER.get(key)
        if v and v.get('owner') not in ('FA', None) and not str(v.get('owner')).startswith('W'): continue   # someone owns him
        nm['yahoo'] = v.get('proj') if v else None; nm['acq'] = ('waivers' if v and str(v.get('owner')).startswith('W') else 'free agent') if v else 'unverified'
        best = max([x for x in (nm['gotham'], nm['sleeper'], nm.get('yahoo')) if x is not None], default=None)
        rows['in'].append(dict(name=name, pos=pos, team=team, why=c['why'], marker=c['marker'], news=c['news'],
                               floor=dict(name=fl[0], gotham=fl[1]) if fl else None,
                               beats_floor=bool(fl and best is not None and best >= fl[1]), **nm))
    rank = {'red': 0, 'gold': 1, 'green': 2, 'grey': 3}
    rows['own'].sort(key=lambda r: (rank[r['marker']['color']], r['marker']['recency'], -(r['gotham'] or 0)))
    rows['opp'].sort(key=lambda r: (rank[r['marker']['color']], -(r['gotham'] or 0)))
    rows['in'].sort(key=lambda r: (not r['beats_floor'], -max([x for x in (r['gotham'], r['sleeper']) if x is not None], default=0)))
    rows['in'] = rows['in'][:12]
    CANDS[lab] = [{'key': norm(r['name']), 'name': r['name']} for r in rows['in']]
    OUT['leagues'][lab] = dict(key=L['key'], opponent=ML['opp'], unread=UNREAD[k], **rows)

def enc(o):
    if isinstance(o, dt.datetime): return ptxt(o)
    raise TypeError(type(o))
json.dump(CANDS, open(f'{OUTD}radar_candidates_wk{WEEK}.json', 'w'))
fn = f'{OUTD}radar_wk{WEEK}.json'; json.dump(OUT, open(fn, 'w'), default=enc, indent=1)
print('RADAR wk', WEEK, 'built', OUT['built'])
for lab, L in OUT['leagues'].items():
    print(f"{lab}: own {len(L['own'])} | coming in {len(L['in'])} | opponent {len(L['opp'])}")
print('ALARMS', len(alarms)); [print('  !', a) for a in alarms]
