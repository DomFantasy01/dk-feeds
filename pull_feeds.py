#!/usr/bin/env python3
"""DK FEED JOB — runs on GitHub on a timer, hands-off.
Pulls what the build machine can't reach: RotoWire news, ESPN news, Sleeper trending + injury tags, weather.\nv4 Oct 7: one retry on timeouts; merges ProFootballTalk, RotoBaller, ESPN injury list.\nv3 Oct 7: adds ESPN news, Sleeper injury tags, and a probe of candidate news sources (counts only).
RULE: assume nothing. Every source writes a status line — ok/failed, how many items, newest item,
and the exact error. A failed source NEVER leaves an empty file that looks like 'quiet'."""
from zoneinfo import ZoneInfo
import json, os, sys, time, csv, io, datetime as dt, urllib.request, urllib.error, urllib.parse, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feeds')
os.makedirs(OUT, exist_ok=True)
NOW = dt.datetime.now(dt.timezone.utc)
UA = {'User-Agent': 'DK-feed-job/1.0 (personal fantasy research, non-commercial)'}
STATUS = {'run_utc': NOW.isoformat(timespec='seconds'), 'sources': {}}

def get(url, timeout=30, tries=2):
    # v4: one retry on a timeout / connection drop. A real refusal (403, 404) is not retried.
    for n in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            # Oct 16: a busy server (429, 5xx - Open-Meteo returned 503s) is worth another try; a refusal is not
            if e.code < 500 and e.code != 429 or n == tries - 1: raise
            time.sleep(5 * (n + 1))
        except Exception:
            if n == tries - 1: raise
            time.sleep(3)

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

# ---------- 1b. RotoWire's own news pages (Oct 19, Dom: "improve the roto feed") ----------
# The RSS holds only ~5 items, so news that arrives between pulls (and all night) was lost. Two fixes:
#  (a) the main news page and the injury view carry 25 items each - five times the RSS;
#  (b) EVERY player Dom rosters, every opponent starter this week and the Scout's targets get their own
#      RotoWire player page read (latest ~7 items each), so news on the men that matter can never scroll off.
# Player pages are found through Sleeper's rotowire_id. Items are merged into rotowire_history.jsonl, keyed
# by RotoWire's headline id, so nothing is written twice. Pages show a date only, not a time: an item first
# seen today is stamped with the time this job first saw it.
import re as _re, html as _html, glob as _glob
RW = 'https://www.rotowire.com'
def _strip(x): return _re.sub(r'\s+', ' ', _html.unescape(_re.sub(r'<[^>]+>', ' ', x or ''))).strip()
def rw_blocks(page, player=None):
    out = []
    starts = [m.start() for m in _re.finditer(r'<div class="news-update(?: [^"]*)?">', page)]
    for i, a in enumerate(starts):
        b = page[a: starts[i + 1] if i + 1 < len(starts) else a + 8000]
        h = _re.search(r'href="(/football/headlines/[^"]*?-(\d+))"[^>]*>(.*?)</a>', b, _re.S)
        if not h: continue
        who = _re.search(r'news-update__player-link"[^>]*>(.*?)</a>', b, _re.S)
        day = _re.search(r'news-update__timestamp">(.*?)<', b, _re.S)
        txt = _re.search(r'news-update__news">(.*?)</div>', b, _re.S)
        inj = _re.search(r'news-update__inj">(.*?)<', b, _re.S)
        out.append({'id': h.group(2), 'player': _strip(who.group(1)) if who else player, 'headline': _strip(h.group(3)),
                    'date': _strip(day.group(1)) if day else None, 'text': _strip(txt.group(1)) if txt else '',
                    'injury': _strip(inj.group(1)) if inj else None, 'link': RW + h.group(1)})
    return out
def _watch_list():
    """Dom's four rosters + this week's opponent starters + the Scout's targets -> {name: rotowire_id}"""
    R = os.path.dirname(OUT); names, why = [], {}
    for n, team in ((1, '2'), (2, '7'), (3, '2'), (4, '6')):
        try:
            for ln in open(os.path.join(R, f'yahoo_drop/scout/dk{n}_rosters_live.txt')):
                x = ln.rstrip('\n').split('|')
                if len(x) >= 6 and x[0] == team and x[4] not in ('DEF', 'K'): names.append(x[2]); why.setdefault(x[2], 'mine')
        except FileNotFoundError: pass
    try:
        st = json.load(open(os.path.join(R, 'dispatch_out/dk_state_latest.json')))
        for lg in st.get('leagues', []):
            for p in lg.get('opp_starters', []):
                if p.get('pos') not in ('DEF', 'K') and not str(p.get('name', '')).endswith(' DEF'): names.append(p['name']); why.setdefault(p['name'], 'opponent')
    except Exception: pass
    for f in _glob.glob(os.path.join(R, 'dispatch_out/scout_state/scout_board_DK*.json')):
        try:
            for a in (json.load(open(f)).get('adds') or [])[:10]:
                nm = a.get('name') or a.get('player') or a.get('who') if isinstance(a, dict) else None
                if nm and not str(nm).endswith(' DEF'): names.append(nm); why.setdefault(nm, 'scout target')   # defenses have no player page
        except Exception: pass
    try: db = json.load(open(os.path.join(OUT, 'sleeper_players_min.json')))
    except Exception: db = {}
    db = db.get('players', db) if isinstance(db, dict) else {}
    def key(x): return ' '.join(_re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', _re.sub(r'[^a-z ]', '', x.lower().replace('.', ' ').replace('-', ' '))).split())
    ids = {}
    for v in db.values():
        if isinstance(v, dict) and v.get('rotowire_id'): ids.setdefault(key(v.get('name', '')), v['rotowire_id'])
    out, missing = {}, []
    for nm in dict.fromkeys(names):
        rid = ids.get(key(nm))
        if rid: out[nm] = (rid, why[nm])
        else: missing.append(nm)
    return out, missing
def rotowire_pages():
    hp = os.path.join(OUT, 'rotowire_history.jsonl'); seen_id, seen_title = set(), set()
    if os.path.exists(hp):
        for line in open(hp):
            try:
                j = json.loads(line); seen_title.add(j.get('title'))
                if j.get('rw_id'): seen_id.add(j['rw_id'])
            except Exception: pass
    today_pt = NOW.astimezone(ZoneInfo('America/Los_Angeles')).date()
    def stamp(day):
        try: d = dt.datetime.strptime(day, '%B %d, %Y').date()
        except Exception: return None
        if d >= today_pt: return NOW.isoformat(timespec='seconds')        # first seen today: our own clock
        return dt.datetime(d.year, d.month, d.day, 23, 59, tzinfo=ZoneInfo('America/Los_Angeles')).astimezone(dt.timezone.utc).isoformat(timespec='seconds')
    got, fails, new, per_player = [], [], [], {}
    for u in (RW + '/football/news.php', RW + '/football/news.php?view=injuries'):
        try: got += [(b, 'news page') for b in rw_blocks(get(u).decode('utf-8', 'replace'))]
        except Exception as e: fails.append(f'{u}: {type(e).__name__}: {e}'[:160])
    watch, missing = _watch_list()
    ok_pages = 0
    for nm, (rid, why) in watch.items():
        u = f"{RW}/football/player/{_re.sub(r'[^a-z0-9]+', '-', nm.lower()).strip('-')}-{rid}"
        try:
            bl = rw_blocks(get(u, timeout=20, tries=1).decode('utf-8', 'replace'), nm); ok_pages += 1
            per_player[nm] = {'rotowire_id': rid, 'why': why, 'url': u,
                              'items': [{k: b[k] for k in ('date', 'headline', 'text', 'injury', 'link')} for b in bl[:5]]}
            got += [(b, 'player page') for b in bl]
        except Exception as e: fails.append(f'{nm}: {type(e).__name__}: {e}'[:120])
        time.sleep(0.4)                                                    # be polite to RotoWire
    with open(hp, 'a') as f:
        for b, via in got:
            title = f"{b['player']}: {b['headline']}"
            if b['id'] in seen_id or title in seen_title: continue
            seen_id.add(b['id']); seen_title.add(title)
            row = {'title': title, 'text': b['text'], 'published_utc': stamp(b['date']), 'date_only': b['date'], 'link': b['link'],
                   'via': 'rotowire ' + via, 'rw_id': b['id'], 'injury': b['injury'], 'first_seen_utc': NOW.isoformat(timespec='seconds')}
            f.write(json.dumps(row) + '\n'); new.append(row)
    write('rotowire_players.json', {'pulled_utc': NOW.isoformat(timespec='seconds'), 'players': per_player, 'no_rotowire_id': missing})
    page_ok = ok_pages > 0 or any(v == 'news page' for _, v in got)
    warn = []
    if fails: warn.append(f'{len(fails)} page reads failed')
    if missing: warn.append(f'{len(missing)} watched players have no RotoWire id: ' + ', '.join(missing[:8]))
    mark('rotowire_pages', page_ok, news_page_items=sum(1 for _, v in got if v == 'news page'), players_watched=len(watch),
         player_pages_read=ok_pages, new_items=len(new), failures=fails[:10], warning='; '.join(warn) or None)
    r = STATUS['sources'].get('rotowire')
    if page_ok and r and r.get('warning'):   # the thin RSS no longer matters once the pages are read
        r['rss_note'] = r.pop('warning'); r['warning'] = None
        r['note'] = 'RSS is thin by design (5 items); RotoWire news now comes from the news pages and player pages - see rotowire_pages'

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
 'Tottenham Hotspur Stadium':'London','Wembley Stadium':'London',
 # Oct 16 (Dom): nflverse still files some games under old or short names
 'Reliant Stadium':'Houston','Bernabeu':'Madrid','Estadio Banorte':'Mexico City','Maracana Stadium':'Rio de Janeiro'}
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
            geo = json.loads(get('https://geocoding-api.open-meteo.com/v1/search?count=1&name=' + urllib.parse.quote(q), tries=3))['results'][0]
            p = urllib.parse.urlencode({'latitude': geo['latitude'], 'longitude': geo['longitude'], 'timezone': 'UTC',
                 'hourly': 'temperature_2m,precipitation_probability,precipitation,wind_speed_10m,wind_gusts_10m',
                 'temperature_unit': 'fahrenheit', 'wind_speed_unit': 'mph', 'start_date': g['gameday'], 'end_date': (dt.date.fromisoformat(g['gameday']) + dt.timedelta(days=1)).isoformat()})
            w = json.loads(get('https://api.open-meteo.com/v1/forecast?' + p, tries=3))
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
 'pft_rss_old': 'https://profootballtalk.nbcsports.com/feed/',
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


# ---------- 6. Extra news — ProFootballTalk + RotoBaller (both answered GitHub in the Oct 7 probe) ----------
EXTRA = {'pft': 'https://www.nbcsports.com/profootballtalk.rss',
         'rotoballer': 'https://www.rotoballer.com/category/nfl/feed'}
def extra_news():
    items, per, errs = [], {}, []
    for src, u in EXTRA.items():
        try:
            root = ET.fromstring(get(u, 25)); n = 0
            for it in root.iter('item'):
                p = it.findtext('pubDate')
                try: pu = parsedate_to_datetime(p).astimezone(dt.timezone.utc).isoformat(timespec='seconds')
                except Exception: pu = None
                items.append({'source': src, 'title': (it.findtext('title') or '').strip(), 'published_utc': pu,
                              'text': (it.findtext('description') or '')[:600], 'link': it.findtext('link')}); n += 1
            per[src] = n
        except Exception as e:
            per[src] = 0; errs.append(f'{src}: {type(e).__name__}: {e}'[:150])
    hp = os.path.join(OUT, 'news_extra_history.jsonl'); seen = set()
    if os.path.exists(hp):
        for line in open(hp):
            try: j = json.loads(line); seen.add((j['source'], j['title'], j['published_utc']))
            except Exception: pass
    new = [i for i in items if (i['source'], i['title'], i['published_utc']) not in seen]
    with open(hp, 'a') as f:
        for i in new: f.write(json.dumps({**i, 'first_seen_utc': NOW.isoformat(timespec='seconds')}) + '\n')
    write('news_extra.json', {'pulled_utc': NOW.isoformat(timespec='seconds'), 'per_source': per, 'items': items})
    newest = max((i['published_utc'] for i in items if i['published_utc']), default=None)
    mark('news_extra', all(per.values()), per_source=per, items=len(items), new_items=len(new),
         newest_item_utc=newest, errors=errs)

# ---------- 7. ESPN injury list, all teams (one league-wide call; probe said team pages answer) ----------
def espn_injuries():
    try:
        d = json.loads(get('https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries', 40))
        rows = []
        def walk(o, team=None):
            if isinstance(o, dict):
                team = o.get('displayName') if 'injuries' in o and o.get('displayName') else team
                if 'athlete' in o and 'status' in o:
                    a = o.get('athlete') or {}
                    rows.append({'team': team, 'name': a.get('displayName'), 'espn_id': str(a.get('id') or ''),
                                 'pos': (a.get('position') or {}).get('abbreviation'), 'status': o.get('status'),
                                 'date': o.get('date'), 'detail': (o.get('shortComment') or o.get('longComment') or '')[:300],
                                 'type': ((o.get('details') or {}).get('type'))})
                for v in o.values(): walk(v, team)
            elif isinstance(o, list):
                for v in o: walk(v, team)
        walk(d)
        write('espn_injuries.json', {'pulled_utc': NOW.isoformat(timespec='seconds'), 'players': rows})
        mark('espn_injuries', bool(rows), players=len(rows), teams=len({r['team'] for r in rows}),
             warning=None if rows else 'answered but no injury rows found — format may differ, needs a look')
    except Exception as e:
        mark('espn_injuries', False, error=f'{type(e).__name__}: {e}'[:200])

if __name__ == '__main__':
    for fn in (rotowire, sleeper, rotowire_pages, weather, espn, extra_news, espn_injuries, probe):   # pages after Sleeper: it needs the id table
        try: fn()
        except Exception as e: mark(fn.__name__, False, error=f'crashed: {e}'[:200])
    write('status.json', STATUS)
    print('status written; failures:', [k for k, v in STATUS['sources'].items() if not v['ok']])
