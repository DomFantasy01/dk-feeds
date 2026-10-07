#!/usr/bin/env python3
"""DK FEED JOB — runs on GitHub on a timer, hands-off.
Pulls what the build machine can't reach: RotoWire news, ESPN news, Sleeper trending + injury tags, weather.\nv3 Oct 7: adds ESPN news, Sleeper injury tags, and a probe of candidate news sources (counts only).
RULE: assume nothing. Every source writes a status line — ok/failed, how many items, newest item,
and the exact error. A failed source NEVER leaves an empty file that looks like 'quiet'."""
from zoneinfo import ZoneInfo
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
    # v2 Oct 7: pull EVERY address and merge — RotoWire's own feed returned only 5 items, 7 hr stale;
    # the mirror carried 100 items up to the minute. Stopping at the first success threw the mirror away.
    per, tried, allitems = {}, [], {}
    for u in ROTO_URLS:
        try:
            root = ET.fromstring(get(u)); n = 0
            for it in root.iter('item'):
                t = (it.findtext('title') or '').strip(); d = (it.findtext('description') or '').strip()
                try: ts = parsedate_to_datetime(it.findtext('pubDate')).astimezone(dt.timezone.utc).isoformat(timespec='seconds')
                except Exception: ts = None
                n += 1; key = (t, ts)
                if key not in allitems or (d and not allitems[key]['text']):
                    allitems[key] = {'title': t, 'text': d, 'published_utc': ts, 'link': it.findtext('link'), 'via': u}
            per[u] = n
            if n == 0: tried.append(f'{u}: answered but 0 items')
        except Exception as e:
            per[u] = 0; tried.append(f'{u}: {type(e).__name__}: {e}'[:200])
    items = sorted(allitems.values(), key=lambda i: i['published_utc'] or '', reverse=True)
    if not items:
        mark('rotowire', False, error='every address failed', tried=tried, per_source=per); return
    newest = max((i['published_utc'] for i in items if i['published_utc']), default=None)
    write('rotowire_latest.json', {'source': 'merged', 'per_source': per, 'pulled_utc': NOW.isoformat(timespec='seconds'), 'items': items})
    hp = os.path.join(OUT, 'rotowire_history.jsonl'); seen = set()
    if os.path.exists(hp):
        for line in open(hp):
            try: j = json.loads(line); seen.add((j['title'], j['published_utc']))
            except Exception: pass
    new = [i for i in items if (i['title'], i['published_utc']) not in seen]
    with open(hp, 'a') as f:
        for i in new: f.write(json.dumps({**i, 'first_seen_utc': NOW.isoformat(timespec='seconds')}) + '\n')
    age_h = round((NOW - dt.datetime.fromisoformat(newest)).total_seconds() / 3600, 1) if newest else None
    warn = []
    if age_h and age_h > 4: warn.append(f'newest item {age_h} hr old — feed may be stale')
    if len(items) < 20: warn.append(f'only {len(items)} items across all addresses — thin')
    mark('rotowire', True, source='merged', per_source=per, items=len(items), new_items=len(new), newest_item_utc=newest,
         newest_age_hours=age_h, fallbacks_failed=tried, warning='; '.join(warn) or None)

# ---------- 2. Sleeper trending adds + drops (official public API) ----------
def sleeper():
    try:
        pdb_path = os.path.join(OUT, 'sleeper_players_min.json')
        # v3: the pull time is stored INSIDE the file. GitHub resets file timestamps on every checkout,
        # so v1/v2 thought the file was always fresh and never refreshed it after the first run.
        blob = json.load(open(pdb_path)) if os.path.exists(pdb_path) else {}
        pulled = blob.get('_pulled_utc') if isinstance(blob.get('_pulled_utc'), str) else None
        pdb = blob.get('players', {}) if pulled else {}
        stale_db = (not pdb) or (NOW - dt.datetime.fromisoformat(pulled) > dt.timedelta(hours=23, minutes=30))
        if stale_db:   # big file (~5 MB) — Sleeper asks for no more than once a day
            full = json.loads(get('https://api.sleeper.app/v1/players/nfl', timeout=90))
            pdb = {k: {'name': v.get('full_name') or f"{v.get('first_name','')} {v.get('last_name','')}".strip(),
                       'pos': v.get('position'), 'team': v.get('team'), 'inj': v.get('injury_status'),
                       'inj_body': v.get('injury_body_part'), 'inj_notes': v.get('injury_notes'),
                       'practice': v.get('practice_participation'), 'practice_note': v.get('practice_description'),
                       'news_updated': v.get('news_updated'), 'espn_id': v.get('espn_id'), 'rotowire_id': v.get('rotowire_id')}
                   for k, v in full.items() if v.get('position') in ('QB', 'RB', 'WR', 'TE', 'K', 'DEF') or k.isalpha()}
            pulled = NOW.isoformat(timespec='seconds')
            write('sleeper_players_min.json', {'_pulled_utc': pulled, 'players': pdb})
        res = {}
        for kind in ('add', 'drop'):
            rows = json.loads(get(f'https://api.sleeper.app/v1/players/nfl/trending/{kind}?lookback_hours=24&limit=50'))
            res[kind] = [{'rank': n + 1, 'player_id': r['player_id'], 'count': r.get('count'), **pdb.get(r['player_id'], {'name': r['player_id']})}
                         for n, r in enumerate(rows)]
        inj = {k: v for k, v in pdb.items() if v.get('inj') and v.get('team')}
        write('sleeper_injuries.json', {'db_pulled_utc': pulled,
                                        'note': 'every rostered player with an injury tag; refreshed once a day', 'players': inj})
        write('sleeper_trending.json', {'pulled_utc': NOW.isoformat(timespec='seconds'), 'lookback_hours': 24, **res})
        mark('sleeper', True, player_db_pulled_utc=pulled, injured_tagged=len(inj), adds=len(res['add']), drops=len(res['drop']), player_db_refreshed=stale_db,
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
        row = {'game_id': g['game_id'], 'gameday': g['gameday'], 'kick_et': g['gametime'], 'stadium': g['stadium'], 'roof': roof}
        if roof in ('dome', 'closed'):
            out.append({**row, 'weather': 'indoors — not pulled'}); continue
        q = PLACE.get(g['stadium'])
        if not q:
            problems.append(f"{g['game_id']}: no location on file for {g['stadium']}")
            out.append({**row, 'weather': 'NO LOCATION — not pulled'}); continue
        try:
            geo = json.loads(get('https://geocoding-api.open-meteo.com/v1/search?count=1&name=' + urllib.parse.quote(q)))['results'][0]
            p = urllib.parse.urlencode({'latitude': geo['latitude'], 'longitude': geo['longitude'], 'timezone': 'UTC',
                 'hourly': 'temperature_2m,precipitation_probability,precipitation,wind_speed_10m,wind_gusts_10m',
                 'temperature_unit': 'fahrenheit', 'wind_speed_unit': 'mph', 'start_date': g['gameday'], 'end_date': (dt.date.fromisoformat(g['gameday']) + dt.timedelta(days=1)).isoformat()})
            w = json.loads(get('https://api.open-meteo.com/v1/forecast?' + p))
            h = w['hourly']
            kick = dt.datetime.fromisoformat(g['gameday'] + 'T' + g['gametime']).replace(tzinfo=ZoneInfo('America/New_York')).astimezone(dt.timezone.utc)
            idx = [i for i, t in enumerate(h['time']) if kick <= dt.datetime.fromisoformat(t).replace(tzinfo=dt.timezone.utc) <= kick + dt.timedelta(hours=3)]
            pick = lambda k, f: round(f(h[k][i] for i in idx if h[k][i] is not None), 1) if idx else None
            out.append({**row, 'roof_note': ('retractable — roof may be closed' if roof=='retractable/unknown' else None), 'resolved_place': f"{geo['name']}, {geo.get('admin1','')}, {geo.get('country_code','')}",
                        'temp_f_min': pick('temperature_2m', min), 'wind_mph_max': pick('wind_speed_10m', max),
                        'gust_mph_max': pick('wind_gusts_10m', max), 'rain_chance_max': pick('precipitation_probability', max),
                        'precip_in_total_mm': pick('precipitation', sum),
                        'kickoff_utc': kick.isoformat(timespec='minutes'), 'note': 'nflverse kick time is US Eastern; converted to UTC; window = kickoff to +3h'})
        except Exception as e:
            problems.append(f"{g['game_id']}: {type(e).__name__}: {e}"[:200])
            out.append({**row, 'weather': 'PULL FAILED'})
    write('weather.json', {'pulled_utc': NOW.isoformat(timespec='seconds'), 'games': out})
    pulled = sum(1 for o in out if 'wind_mph_max' in o)
    need = sum(1 for o in out if o.get('weather') != 'indoors — not pulled')
    mark('weather', pulled == need and need > 0 or (need == 0 and len(out) > 0),
         games_in_window=len(out), outdoor_needed=need, outdoor_pulled=pulled, problems=problems)

# ---------- 4. ESPN NFL news (free JSON; items carry ESPN athlete ids, matched to nflverse espn_id) ----------
def espn():
    try:
        d = json.loads(get('https://site.api.espn.com/apis/site/v2/sports/football/nfl/news?limit=100'))
        items = []
        for a in d.get('articles', []):
            ath = [str(c.get('athleteId') or (c.get('athlete') or {}).get('id')) for c in a.get('categories', []) if c.get('type') == 'athlete']
            items.append({'title': a.get('headline'), 'text': a.get('description'), 'published_utc': a.get('published'),
                          'type': a.get('type'), 'espn_athletes': [x for x in ath if x and x != 'None'],
                          'link': ((a.get('links') or {}).get('web') or {}).get('href')})
        hp = os.path.join(OUT, 'espn_news_history.jsonl'); seen = set()
        if os.path.exists(hp):
            for line in open(hp):
                try: j = json.loads(line); seen.add((j['title'], j['published_utc']))
                except Exception: pass
        new = [i for i in items if (i['title'], i['published_utc']) not in seen]
        with open(hp, 'a') as f:
            for i in new: f.write(json.dumps({**i, 'first_seen_utc': NOW.isoformat(timespec='seconds')}) + '\n')
        write('espn_news.json', {'pulled_utc': NOW.isoformat(timespec='seconds'), 'items': items})
        newest = max((i['published_utc'] for i in items if i['published_utc']), default=None)
        mark('espn_news', bool(items), items=len(items), new_items=len(new), newest_item_utc=newest,
             with_player_tag=sum(1 for i in items if i['espn_athletes']))
    except Exception as e:
        mark('espn_news', False, error=f'{type(e).__name__}: {e}'[:200])

# ---------- 5. PROBE — candidate news sources. Counts only, nothing merged. One run tells us which answer GitHub. ----------
PROBES = {
 'espn_injuries_team1': 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/1/injuries',
 'espn_core_injuries_team1': 'https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/1/injuries',
 'espn_fantasy_player_news': 'https://site.api.espn.com/apis/fantasy/v2/games/ffl/news/players?limit=50',
 'cbs_nfl_rss': 'https://www.cbssports.com/rss/headlines/nfl/',
 'yahoo_nfl_rss': 'https://sports.yahoo.com/nfl/rss/',
 'pft_rss': 'https://www.nbcsports.com/profootballtalk.rss',
 'pft_rss_old': 'https://profootballtalk.nbcsports.com/feed/',
 'rotoballer_nfl_rss': 'https://www.rotoballer.com/category/nfl/feed',
 'fantasypros_news_rss': 'https://www.fantasypros.com/nfl/news/feed/',
 'google_news_nfl_injury': 'https://news.google.com/rss/search?q=NFL+injury+practice+when:1d&hl=en-US&gl=US&ceid=US:en',
 'rotowire_mirror': 'https://rss-parrot.net/web/feeds/rotowire.com',
}
def probe():
    out = {}
    for k, u in PROBES.items():
        try:
            raw = get(u, 20); n, newest = None, None
            try:
                root = ET.fromstring(raw); its = list(root.iter('item')) or list(root.iter('{http://www.w3.org/2005/Atom}entry'))
                n = len(its); ds = []
                for it in its:
                    p = it.findtext('pubDate') or it.findtext('{http://www.w3.org/2005/Atom}updated')
                    try: ds.append(parsedate_to_datetime(p).astimezone(dt.timezone.utc))
                    except Exception:
                        try: ds.append(dt.datetime.fromisoformat(p.replace('Z', '+00:00')))
                        except Exception: pass
                newest = max(ds).isoformat(timespec='minutes') if ds else None
                kind = 'rss'
            except ET.ParseError:
                j = json.loads(raw); kind = 'json'
                n = len(j.get('items') or j.get('articles') or j.get('feed') or j.get('injuries') or j.get('athletes') or j) if isinstance(j, dict) else len(j)
            out[k] = {'answered': True, 'kind': kind, 'items': n, 'newest_utc': newest, 'bytes': len(raw)}
        except Exception as e:
            out[k] = {'answered': False, 'error': f'{type(e).__name__}: {e}'[:150]}
    write('probe.json', {'pulled_utc': NOW.isoformat(timespec='seconds'), 'probes': out})
    mark('probe', True, answered=[k for k, v in out.items() if v['answered']], failed=[k for k, v in out.items() if not v['answered']])


if __name__ == '__main__':
    for fn in (rotowire, sleeper, weather, espn, probe):
        try: fn()
        except Exception as e: mark(fn.__name__, False, error=f'crashed: {e}'[:200])
    write('status.json', STATUS)
    print('status written; failures:', [k for k, v in STATUS['sources'].items() if not v['ok']])
