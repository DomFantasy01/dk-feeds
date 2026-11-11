"""WIRE BUDGET (Nov 11 3 PM, Dom: "put what my FAAB budget is in each of my leagues" on Live's front page; DK IV has no FAAB -
it runs on waiver order, so show where he is in the order). Reads Dom's row from the newest Yahoo standings: the Yahoo API
read (yahoo_api/latest.json, every build) when it carries the numbers, else the newest scheduled Chrome read
(yahoo_drop/_inbox/pull_*.json, standings rows ...^FAAB^waiver^moves). Writes dispatch_out/wire_budget.json:
  {"DK I": {"faab": 30, "wp": 7, "n": 12, "read": "Wed Nov 11 1:32 PM PT", "src": "chrome"}, ..., "DK IV": {"faab": null, "wp": 4, ...}}
usage: python3 wire_budget.py REPO"""
import json, sys, os, glob, re
R = sys.argv[1]
LID = {'269381': 'DK I', '1519795': 'DK II', '1507991': 'DK III', '864215': 'DK IV'}
ALAB = {'DKI': 'DK I', 'DKII': 'DK II', 'DKIII': 'DK III', 'DKIV': 'DK IV'}
num = lambda s: int(re.sub(r'[^\d]', '', s)) if s and re.sub(r'[^\d]', '', s) else None
out = {}
# 1) newest scheduled Chrome read
fs = sorted(glob.glob(os.path.join(R, 'yahoo_drop/_inbox/pull_*.json')))
for f in reversed(fs):
    try: d = json.load(open(f))
    except Exception: continue
    sk = [k for k in (d.get('files') or {}) if '/standings_' in k]
    if not sk: continue
    for line in d['files'][sk[-1]].splitlines():
        if line.startswith('#') or '#' not in line: continue
        lid, rest = line.split('#', 1); lab = LID.get(lid)
        if not lab: continue
        rows = [it.split('^') for it in rest.split('|') if '^' in it]
        me = next((r for r in rows if re.match(r'^Dark Knight', r[1])), None)
        if not me: continue
        if lab == 'DK IV': out[lab] = dict(faab=None, wp=num(me[6]), n=len(rows), read=d.get('read_pt'), src='chrome')
        else: out[lab] = dict(faab=num(me[7]), wp=num(me[8]), n=len(rows), read=d.get('read_pt'), src='chrome')
    break
# 2) the Yahoo API read, when it has the numbers and is the newer read (it runs every build)
try:
    A = json.load(open(os.path.join(R, 'yahoo_api/latest.json')))
    for k, L in (A.get('leagues') or {}).items():
        lab = ALAB.get(k); st = L.get('standings') or []; me = next((x for x in st if x.get('id') == L.get('me')), None)
        if not lab or not me: continue
        fa, wp = num(me.get('faab') or ''), num(me.get('wp') or '')
        if wp is None and fa is None: continue
        if lab == 'DK IV': fa = None
        out[lab] = dict(faab=fa if fa is not None else (out.get(lab) or {}).get('faab'), wp=wp if wp is not None else (out.get(lab) or {}).get('wp'),
                        n=len(st), read=A.get('read_pt'), src='api')
except Exception as e: print('wire budget: API read not used -', e)
json.dump(out, open(os.path.join(R, 'dispatch_out/wire_budget.json'), 'w'), indent=1)
print('wire budget:', {k: (v.get('faab'), v.get('wp')) for k, v in out.items()})
