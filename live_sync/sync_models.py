# usage: python3 sync_models.py models_current.json meter.json out.json [state_current.json live_state.json state_out.json]
# Oct 13 (Dom): ONE YAHOO READER. With the three extra file names it also turns the Dispatch's own Yahoo read
# (dispatch_out/live_state_latest.json, written by every build) into Live's live/state - but only when that read is newer
# than what Live already shows, so a game-night Live read is never replaced by an older one. It prints STATE WRITE or STATE SKIP.
# Every run also adds `health` to the models document: the Dispatch's last Yahoo read, its last build, and a failed build if
# one happened since - Live's status light reads it.
# Oct 13 (Dom): THE CHAIN CHECK. With --runlog <folder of the artifact's runlog documents> it also checks the chain by
# success, not by the clock: did the scheduled Yahoo read that should have landed by now actually finish (the read writes
# its runlog), and has a build used it? It prints one line: CHAIN OK / CHAIN WAIT (read done, build not caught up yet) /
# CHAIN REFIRE (the read failed or stalled - start it again, once per slot) / CHAIN BROKEN (it already got its second try).
import json, sys, re, unicodedata
cur = json.load(open(sys.argv[1])); cur = cur.get('data', cur)
M = json.load(open(sys.argv[2]))
KEY = {'DK I':'MOST','DK II':'WINNERS','DK III':'HERS&HIS','DK IV':'NEXTDOOR'}
def norm(n):
    n = unicodedata.normalize('NFKD', n or ''); n = ''.join(c for c in n if not unicodedata.combining(c))
    n = re.sub(r"[.']", '', n).replace('-', ' ').strip(); n = re.sub(r'\s+(jr|sr|ii|iii|iv|v)\.?$', '', n, flags=re.I)
    return ' '.join(n.lower().split())
o = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1:'st',2:'nd',3:'rd'}.get(n % 10, 'th')}"
pm = {}
for lab, k in KEY.items():
    L = M['leagues'][lab]; d = {}
    for s in L['starters']['me'] + L['starters']['op']:
        g = s['gotham'] if s['gotham'] is not None else s['sleeper']; sl = s['sleeper']
        if s['pos'] in ('K', 'DEF'): g = sl
        if g is None and sl is None: continue
        d[norm(s['player'])] = [g, sl]
    pm[k] = d
    lg = cur['leagues'].setdefault(k, {})
    lg['rec'] = L['record']; lg['oppRec'] = L['opp_record']; lg['opp'] = L['opp'].upper()
    lg['std'] = ([["DIVISION", o(L['div_rank'])], ["LEAGUE", o(L['rank'])]] if L.get('div_rank')
                 else [["POINTS FOR", o(L['pf_rank'])], ["LEAGUE", o(L['rank'])]])
cur['pm'] = pm
# Oct 13 5 PM (Dom): BEST LINEUP, BOTH SIDES - the meter now sets each team's best legal lineup from its whole roster.
# Live gets the swaps (out man -> in man, per model) so its Gotham and Sleeper needles count the same best lineups.
best = {}
for lab, k in KEY.items():
    L = M['leagues'][lab]; bm = L.get('best_moves') or {}
    if not bm: continue
    ent = {}
    for col, tag in (('gotham', 'g'), ('sleeper', 's')):
        ent[tag] = {side: {norm(mv['out']): mv['in_v'] for mv in (bm.get(col) or {}).get(side, []) if mv.get('out')}
                    for side in ('me', 'op')}
    def _lines(side):
        mv = (bm.get('gotham') or {}).get(side, [])
        ins = [f"{m['into']} ({m['in_v']:.1f})" for m in mv if m.get('into') and m['into'] != '(nobody eligible)']
        outs = [f"{m['out']} ({(m['out_v'] or 0):.1f})" for m in mv if m.get('out') and not m['out'].startswith('(Empty')]
        holes = sum(1 for m in mv if m.get('into') == '(nobody eligible)')
        t = []
        if ins: t.append("start " + ", ".join(ins))
        if outs: t.append("sit " + ", ".join(outs))
        if holes: t.append(f"{holes} seat{'s' if holes > 1 else ''} nobody on the roster can fill")
        return t
    ent['lines'] = {'me': _lines('me'), 'op': _lines('op')}
    ent['set'] = {'gotham': (L.get('needles_set') or {}).get('gotham'), 'sleeper': (L.get('needles_set') or {}).get('sleeper')}
    best[k] = ent
cur['best'] = best
# stamp = when the Dispatch built these numbers (Pacific text in meter -> UTC ISO)
from datetime import datetime, timedelta, timezone
t = datetime.strptime(M['built_pt'].replace(' PT', ''), '%a %b %d %Y %I:%M %p')
cur['stamp'] = (t + timedelta(hours=7 if 3 <= t.month <= 10 else 8)).strftime('%Y-%m-%dT%H:%M:%SZ')
cur['source'] = f"Week {M['week']}: GOTHAM and SLEEPER per player from the Dispatch build of {M['built_pt']} (dispatch_out/meter_wk{M['week']}.json)"
cur['pm_note'] = "Per-player numbers: [GOTHAM, SLEEPER priced in this league's scoring], keyed by norm(name). K and DEF use Sleeper in both."
# game weather (Oct 11): the Dispatch build's kickoff forecast, passed through for the Live page's sky pictures.
# A failed fetch or another week's file leaves the last good weather in place.
try:
    import subprocess
    r = subprocess.run(['curl', '-sfL', f"https://raw.githubusercontent.com/DomFantasy01/dk-feeds/main/dispatch_out/weather_wk{M['week']}.json"],
                       capture_output=True, timeout=25)
    Wx = json.loads(r.stdout) if r.returncode == 0 else None
    if Wx and int(Wx.get('week', -1)) == int(M['week']): cur['wx'] = Wx
    else: print('weather not synced (no file for week', M['week'], ')')
except Exception as ex: print('weather not synced:', str(ex)[:60])
# ---- the status light (Oct 13): last good Yahoo read, last build, last failed build
def _raw(path):
    try:
        r = subprocess.run(['curl', '-sfL', 'https://raw.githubusercontent.com/DomFantasy01/dk-feeds/main/' + path], capture_output=True, timeout=25)
        return r.stdout.decode() if r.returncode == 0 else None
    except Exception: return None
def _utc(pt):
    s_ = (pt or '').replace(' PT', '').strip()
    if not re.search(r' \d{4} ', s_): s_ = re.sub(r'^(\w{3} \w{3} \d{1,2}) ', r'\g<1> ' + M['built_pt'].split()[3] + ' ', s_)   # "Tue Oct 13 05:44 AM" has no year
    try: t = datetime.strptime(s_, '%a %b %d %Y %I:%M %p')
    except Exception: return None
    return (t + timedelta(hours=7 if 3 <= t.month <= 10 else 8)).strftime('%Y-%m-%dT%H:%M:%SZ')
H = dict(read=_utc(M['sources'].get('yahoo_matchups', {}).get('pulled_pt', '')), build=cur['stamp'], week=M['week'],
         alarms=len(M.get('alarms', [])), checked=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
bf = _raw('dispatch_out/build_failed.json')
try: H['build_failed'] = json.loads(bf) if bf else None
except Exception: H['build_failed'] = None
rf = _raw('dispatch_out/RADAR_FAILED.txt'); H['radar_failed'] = rf.strip()[:160] if rf else None
# ---- THE CHAIN CHECK (Oct 13)
import glob as _g, os as _os
from zoneinfo import ZoneInfo as _ZI
_PTZ = _ZI('America/Los_Angeles'); _now = datetime.now(timezone.utc)
_prev = (cur.get('health') or {}) if isinstance(cur.get('health'), dict) else {}
H['refired'] = {k: v for k, v in (_prev.get('refired') or {}).items() if k[:10] >= (_now - timedelta(days=2)).strftime('%Y-%m-%d')}
def _slots(day):   # the scheduled Yahoo reads for the Dispatch, Pacific: Mon-Sat 7:50 AM, 12:50 PM, 4:50 PM; Sunday 4:50 AM then hourly 8:50 AM-8:50 PM
    hm = [(4, 50)] + [(h, 50) for h in range(8, 21)] if day.weekday() == 6 else [(7, 50), (12, 50), (16, 50)]
    return [datetime(day.year, day.month, day.day, h, m, tzinfo=_PTZ) for h, m in hm]
def _iso(t): return t.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def _p(s):
    try: return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except Exception: return None
_lp = _now.astimezone(_PTZ)
_all = sorted(_slots(_lp - timedelta(days=1)) + _slots(_lp))
_due = [t for t in _all if t + timedelta(minutes=20) <= _now]          # a read needs ~15 minutes to read Yahoo and save
_slot = _due[-1] if _due else None
_nxt = [t for t in _all if t > (_slot or _now)]
CH = dict(state='ok', msg='', slot=_iso(_slot) if _slot else None,
          trigger=('trig_01WgYXc4XEj9XbbVThwSAwDV' if _slot and _slot.weekday() == 6 else 'trig_015hLaehaGcf27tiUKipvF9C'))   # which scheduled read to start again
if '--runlog' in sys.argv and _slot:
    _runs = []
    for f in _g.glob(_os.path.join(sys.argv[sys.argv.index('--runlog') + 1], '**', '*.json'), recursive=True):
        try:
            d = json.load(open(f)); d = d.get('data', d)
            if 'Yahoo read' in d.get('task', '') and _p(d.get('started', '')): _runs.append(d)
        except Exception: pass
    _end = _nxt[0] - timedelta(minutes=5) if _nxt else _now
    mine = sorted([r for r in _runs if _slot - timedelta(minutes=5) <= _p(r['started']) < _end], key=lambda r: r['started'])
    lab = _slot.strftime('%-I:%M %p').replace(':00', '') ; key = _iso(_slot)
    last = mine[-1] if mine else None
    rd = _p(H.get('read') or ''); bt = _p(H.get('build') or '')
    if last and last.get('status') == 'ok':
        if rd and rd >= _slot - timedelta(minutes=5): CH.update(state='ok', msg=f'{lab} read in and built')
        elif _now - (_p(last.get('finished', '')) or _now) > timedelta(minutes=45):
            CH.update(state='broken', msg=f'{lab} read saved, but no build has used it in 45 minutes')
        else: CH.update(state='wait', msg=f'{lab} read saved, waiting for the build')
    else:
        why = ('never started' if not last else
               f"failed at {last.get('step', '?')}: {last.get('error', '')[:120]}" if last.get('status') == 'failed' else
               'stalled (started, never finished)' if _now - _p(last['started']) > timedelta(minutes=35) else None)
        if why is None: CH.update(state='wait', msg=f'{lab} read still running')
        elif key in H['refired']: CH.update(state='broken', msg=f'{lab} read {why}, after a second try at {H["refired"][key]}')
        else: CH.update(state='refire', msg=f'{lab} read {why}'); H['refired'][key] = _iso(_now)   # the task starts the read again now - once per slot
H['chain'] = CH
bf_at = _p(((H.get('build_failed') or {}).get('at')) or '')
if bf_at and (not _p(H['build']) or bf_at > _p(H['build'])) and CH['state'] in ('ok', 'wait'):
    CH.update(state='broken', msg='the last Dispatch build failed at ' + _iso(bf_at))
print('CHAIN', CH['state'].upper(), '-', CH['msg'] or 'no read due yet', ('| start scheduled task ' + CH['trigger']) if CH['state'] == 'refire' else '')
cur['health'] = H
json.dump(cur, open(sys.argv[3], 'w'), ensure_ascii=False)
print('synced', {k: len(v) for k, v in pm.items()}, 'built', M['built_pt'], '| health', {k: v for k, v in H.items() if k != 'checked'})
# ---- ONE YAHOO READER (Oct 13): Live's live/state from the Dispatch's read, when that read is newer
if len(sys.argv) >= 7:
    st = json.load(open(sys.argv[4])); st = st.get('data', st)
    try: ls = json.load(open(sys.argv[5]))
    except Exception as ex: print('STATE SKIP - no Dispatch read file:', str(ex)[:80]); raise SystemExit(0)
    old_w, new_w = int(st.get('week') or 0), int(ls.get('week') or 0)
    old_t, new_t = st.get('stamp') or '', ls.get('stamp') or ''
    if not ls.get('leagues') or not new_t or new_w < old_w or (new_w == old_w and new_t <= old_t):
        print(f'STATE SKIP - Live already shows week {old_w} read {old_t}; the Dispatch read is week {new_w} {new_t}')
    else:
        prev = {L.get('key'): L for L in st.get('leagues', [])}
        for L in ls['leagues']:
            p = prev.get(L['key']) or {}
            if p.get('opp') == L.get('opp') and new_w == old_w:
                L['mgr'] = p.get('mgr') or L.get('mgr') or ''
                if L.get('sigma') is None: L['sigma'] = p.get('sigma')
            if L.get('sigma') is None: L['sigma'] = 0
        ls.pop('alert', None)
        json.dump(ls, open(sys.argv[6], 'w'), ensure_ascii=False)
        print(f'STATE WRITE - week {new_w} read {new_t} replaces week {old_w} read {old_t}')
