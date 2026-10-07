#!/usr/bin/env python3
"""DK FEED JOB — runs on GitHub on a timer, hands-off.
Pulls the three sources the build machine can't reach: RotoWire news, Sleeper trending, weather.
RULE: assume nothing. Every source writes a status line — ok/failed, how many items, newest item,
and the exact error. A failed source NEVER leaves an empty file that looks like 'quiet'."""
import json, os, sys, time, csv, io, datetime as dt, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feeds')
os.makedirs(OUT, exist_ok=True)
NOW = dt.datetime.now(dt.timezone.utc)
UA = {'User-Agent': 'DK-feed-job/1.0 (personal fantasy research, non-commercial)'}
STATUS = {'run_utc': NOW.isoformat(timespec='seconds'), 'sources': {}}

def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def mark(name, ok, **kw):
    kw.update(ok=ok, checked_utc=NOW.isoformat(timespec='seconds'))
    STATUS['sources'][name] = kw
    print(('OK   ' if ok else 'FAIL ') + name + ' ' + json.dumps({k: v for k, v in kw.items() if k != 'checked_utc'}))

def write(name, obj):
    with open(os.path.join(OUT, name), 'w') as f:
        json.dump(obj, f, indent=1)

# ---------- 1. RotoWire NFL news (straight from RotoWire; mirror is the fallback) ----------
ROTO_URLS = ['https://www.rotowire.com/rss/news.php',            # the address the mirror itself relays (NFL news)
             'https://www.rotowire.com/rss/news.php?sport=NFL',
             'https://www.rotowire.com/rss/news.htm?sport=nfl',
             'https://rss-parrot.net/web/feeds/rotowire.com']
def rotowire():
    tried = []
    for u in ROTO_URLS:
        try:
            raw = get(u)
            root = ET.fromstring(raw)
            items = []
            for it in root.iter('item'):
                t = (it.findtext('title') or '').strip()
                d = (it.findtext('description') or '').strip()
                p = it.findtext('pubDate')
                try: ts = parsedate_to_datetime(p).astimezone(dt.timezone.utc).isoformat(timespec='seconds')
                except Exception: ts = None
                items.append({'title': t, 'text': d, 'published_utc': ts, 'link': it.findtext('link')})
            if not items:
                tried.append(f'{u}: answered but 0 items'); continue
            newest = max((i['published_utc'] for i in items if i['published_utc']), default=None)
            write('rotowire_latest.json', {'source': u, 'pulled_utc': NOW.isoformat(timespec='seconds'), 'items': items})
            # history: keep every item ever seen, so a replay test is possible later
            hp = os.path.join(OUT, 'rotowire_history.jsonl'); seen = set()
            if os.path.exists(hp):
                for line in open(hp):
                    try: j = json.loads(line); seen.add((j['title'], j['published_utc']))
                    except Exception: pass
            new = [i for i in items if (i['title'], i['published_utc']) not in seen]
            with open(hp, 'a') as f:
                for i in new: f.write(json.dumps({**i, 'first_seen_utc': NOW.isoformat(timespec='seconds')}) + '\n')
            age_h = round((NOW - dt.datetime.fromisoformat(newest)).total_seconds() / 3600, 1) if newest else None
            mark('rotowire', True, source=u, items=len(items), new_items=len(new), newest_item_utc=newest,
                 newest_age_hours=age_h, fallbacks_failed=tried,
                 warning=('newest item over 12 hours old — feed may be stale' if age_h and age_h > 12 else None))
            return
        except Exception as e:
            tried.append(f'{u}: {type(e).__name__}: {e}'[:200])
    mark('rotowire', False, error='every address failed', tried=tried)

# ---------- 2. Sleeper trending adds + drops (official public API) ----------
def sleeper():
    try:
        pdb_path = os.path.join(OUT, 'sleeper_players_min.json')
        pdb = json.load(open(pdb_path)) if os.path.exists(pdb_path) else {}
        stale_db = (not pdb) or (time.time() - os.path.getmtime(pdb_path) > 86400 * 3)
        if stale_db:   # big file (~5 MB), refresh every 3 days only
            full = json.loads(get('https://api.sleeper.app/v1/players/nfl', timeout=90))
            pdb = {k: {'name': v.get('full_name') or f"{v.get('first_name','')} {v.get('last_name','')}".strip(),
                       'pos': v.get('position'), 'team': v.get('team'), 'inj': v.get('injury_status')}
                   for k, v in full.items()}
            write('sleeper_players_min.json', pdb)
        res = {}
        for kind in ('add', 'drop'):
            rows = json.loads(get(f'https://api.sleeper.app/v1/players/nfl/trending/{kind}?lookback_hours=24&limit=50'))
            res[kind] = [{'rank': n + 1, 'player_id': r['player_id'], 'count': r.get('count'), **pdb.get(r['player_id'], {'name': r['player_id']})}
                         for n, r in enumerate(rows)]
        write('sleeper_trending.json', {'pulled_utc': NOW.isoformat(timespec='seconds'), 'lookback_hours': 24, **res})
        mark('sleeper', True, adds=len(res['add']), drops=len(res['drop']), player_db_refreshed=stale_db,
             note='trust the ORDER; raw counts are Sleeper-wide and may not respect the 24h window')
    except Exception as e:
        mark('sleeper', False, error=f'{type(e).__name__}: {e}'[:200])

# ---------- 3. Weather at every open-air game in the next 8 days ----------
# Geocode queries are city-level on purpose (wind/rain/cold is a city fact). The job prints the place
# it resolved so a wrong match is visible, never silent. Unknown stadium -> loud 'no location' line.
PLACE = {'Lambeau Field':'Green Bay','Gillette Stadium':'Foxborough','MetLife Stadium':'East Rutherford',
 'Acrisure Stadium':'Pittsburgh','Nissan Stadium':'Nashville','Northwest Stadium':'Landover','Lumen Field':'Seattle',
 'Hard Rock Stadium':'Miami Gardens','Empower Field at Mile High':'Denver','Huntington Bank Field':'Cleveland',
 'Lincoln Financial Field':'Philadelphia','Raymond James Stadium':'Tampa','GEHA Field at Arrowhead Stadium':'Kansas City',
 "Levi's Stadium":'Santa Clara','Highmark Stadium':'Orchard Park','Soldier Field':'Chicago','M&T Bank Stadium':'Baltimore',
 'Paycor Stadium':'Cincinnati','EverBank Stadium':'Jacksonville','Bank of America Stadium':'Charlotte',
 'AT&T Stadium':'Arlington, Texas','State Farm Stadium':'Glendale, Arizona',
 'Mercedes-Benz Stadium':'Atlanta','Lucas Oil Stadium':'Indianapolis','NRG Stadium':'Houston',
 'Tottenham Hotspur Stadium':'London','Wembley Stadium':'London'}
def weather():
    try:
        games = list(csv.DictReader(io.StringIO(get('https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv', 60).decode())))
    except Exception as e:
        mark('weather', False, error=f'schedule not reached: {e}'[:200]); return
    today, horizon = NOW.date(), NOW.date() + dt.timedelta(days=8)
    out, problems = [], []
    for g in games:
        try: day = dt.date.fromisoformat(g['gameday'])
        except Exception: continue
        if not (today <= day <= horizon) or g.get('away_score'): continue
        roof = (g.get('roof') or '').strip() or 'retractable/unknown'
        row = {'game_id': g['game_id'], 'gameday': g['gameday'], 'kick_local': g['gametime'], 'stadium': g['stadium'], 'roof': roof}
        if roof in ('dome', 'closed'):
            out.append({**row, 'weather': 'indoors — not pulled'}); continue
        q = PLACE.get(g['stadium'])
        if not q:
            problems.append(f"{g['game_id']}: no location on file for {g['stadium']}")
            out.append({**row, 'weather': 'NO LOCATION — not pulled'}); continue
        try:
            geo = json.loads(get('https://geocoding-api.open-meteo.com/v1/search?count=1&name=' + urllib.parse.quote(q)))['results'][0]
            p = urllib.parse.urlencode({'latitude': geo['latitude'], 'longitude': geo['longitude'], 'timezone': 'auto',
                 'hourly': 'temperature_2m,precipitation_probability,precipitation,wind_speed_10m,wind_gusts_10m',
                 'temperature_unit': 'fahrenheit', 'wind_speed_unit': 'mph', 'start_date': g['gameday'], 'end_date': g['gameday']})
            w = json.loads(get('https://api.open-meteo.com/v1/forecast?' + p))
            h = w['hourly']; hr = int(g['gametime'][:2])
            idx = [i for i, t in enumerate(h['time']) if hr <= int(t[11:13]) <= hr + 3]
            pick = lambda k, f: round(f(h[k][i] for i in idx if h[k][i] is not None), 1) if idx else None
            out.append({**row, 'roof_note': ('retractable — roof may be closed' if roof=='retractable/unknown' else None), 'resolved_place': f"{geo['name']}, {geo.get('admin1','')}, {geo.get('country_code','')}",
                        'temp_f_min': pick('temperature_2m', min), 'wind_mph_max': pick('wind_speed_10m', max),
                        'gust_mph_max': pick('wind_gusts_10m', max), 'rain_chance_max': pick('precipitation_probability', max),
                        'precip_in_total_mm': pick('precipitation', sum),
                        'note': 'kick time is local to the stadium per nflverse; window = kickoff to +3h'})
        except Exception as e:
            problems.append(f"{g['game_id']}: {type(e).__name__}: {e}"[:200])
            out.append({**row, 'weather': 'PULL FAILED'})
    write('weather.json', {'pulled_utc': NOW.isoformat(timespec='seconds'), 'games': out})
    pulled = sum(1 for o in out if 'wind_mph_max' in o)
    need = sum(1 for o in out if o.get('weather') != 'indoors — not pulled')
    mark('weather', pulled == need and need > 0 or (need == 0 and len(out) > 0),
         games_in_window=len(out), outdoor_needed=need, outdoor_pulled=pulled, problems=problems)

if __name__ == '__main__':
    for fn in (rotowire, sleeper, weather):
        try: fn()
        except Exception as e: mark(fn.__name__, False, error=f'crashed: {e}'[:200])
    write('status.json', STATUS)
    print('status written; failures:', [k for k, v in STATUS['sources'].items() if not v['ok']])
