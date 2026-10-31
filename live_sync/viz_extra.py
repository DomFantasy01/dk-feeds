# Oct 31 (Dom: "add them all and make this look advanced") - the chart extras for Dark Knight Live.
# Runs at the end of every Dispatch build (GitHub has the open internet; the Live sync does not) and writes
# dispatch_out/viz_extra.json:
#   work    - every starter's (both sides, all four leagues) and every Dom-rostered player's carries + targets and PPR points
#             per regular-season week, from nflverse's weekly player stats (None = no game: bye, injury, inactive)
#   rosters - Dom's four Yahoo rosters as [name, slot] (the exposure map), from this build's Yahoo API read
# The Live sync copies both into live/models. A failed pull leaves the last file in place.
import csv, io, json, os, sys, urllib.request, datetime as dt

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
OUT = os.path.join(ROOT, 'dispatch_out', 'viz_extra.json')
SK = {'DKI': 'DK I', 'DKII': 'DK II', 'DKIII': 'DK III', 'DKIV': 'DK IV'}

state = json.load(open(os.path.join(ROOT, 'dispatch_out', 'live_state_latest.json')))
W = int(state['week'])
meter = json.load(open(os.path.join(ROOT, 'dispatch_out', f'meter_wk{W}.json')))
names = set()
for L in meter['leagues'].values():
    for side in ('me', 'op'):
        for s in L['starters'][side]:
            if s.get('pos') not in ('K', 'DEF'): names.add(s['player'])

rosters, read = {}, None
try:
    Y = json.load(open(os.path.join(ROOT, 'yahoo_api', 'latest.json')))
    read = Y.get('read_pt')
    for k, lab in SK.items():
        lg = Y['leagues'].get(k)
        if not lg: continue
        me = [t for t in lg['teams'] if str(t['id']) == str(lg['me'])][0]
        rosters[lab] = [[p['name'], p['slot'], p.get('pos', '')] for p in me['players']]
        names.update(p['name'] for p in me['players'] if p.get('pos') not in ('K', 'DEF'))
except Exception as e:
    print('!! rosters not read:', e)

url = 'https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_2026.csv'
raw = urllib.request.urlopen(url, timeout=60).read().decode()
rows = [r for r in csv.DictReader(io.StringIO(raw)) if r.get('season_type') == 'REG']
maxw = max(int(r['week']) for r in rows)
f = lambda v: float(v) if v not in (None, '', 'NA') else 0.0
got = {}
for r in rows:
    n = r['player_display_name']
    if n in names:
        got.setdefault(n, {})[int(r['week'])] = [int(f(r.get('carries')) + f(r.get('targets'))), round(f(r.get('fantasy_points_ppr')), 1)]
work = {n: [got[n].get(w) for w in range(1, maxw + 1)] for n in sorted(got)}
out = dict(built=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), weeks=maxw, work=work,
           rosters=rosters, rosters_read=read, source='nflverse weekly player stats + Yahoo API rosters')
json.dump(out, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':'))
print(f'viz extras: {len(work)} players, weeks 1-{maxw}, rosters {list(rosters)}')
