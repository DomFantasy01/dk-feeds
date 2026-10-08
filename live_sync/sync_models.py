# usage: python3 sync_models.py models_current.json meter.json out.json
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
# stamp = when the Dispatch built these numbers (Pacific text in meter -> UTC ISO)
from datetime import datetime, timedelta
t = datetime.strptime(M['built_pt'].replace(' PT', ''), '%a %b %d %Y %I:%M %p')
cur['stamp'] = (t + timedelta(hours=7 if 3 <= t.month <= 10 else 8)).strftime('%Y-%m-%dT%H:%M:%SZ')
cur['source'] = f"Week {M['week']}: GOTHAM and SLEEPER per player from the Dispatch build of {M['built_pt']} (dispatch_out/meter_wk{M['week']}.json)"
cur['pm_note'] = "Per-player numbers: [GOTHAM, SLEEPER priced in this league's scoring], keyed by norm(name). K and DEF use Sleeper in both."
json.dump(cur, open(sys.argv[3], 'w'), ensure_ascii=False)
print('synced', {k: len(v) for k, v in pm.items()}, 'built', M['built_pt'])
