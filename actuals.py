"""ACTUAL weekly fantasy points from nflverse (free, reachable from GitHub Actions), priced in MOST scoring.
Returns {(normalized_name, week): points} for regular-season weeks."""
import pandas as pd, urllib.request, io, re
URL = 'https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_2026.csv'
def norm(s):
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', str(s).lower())
    s = re.sub(r'[^a-z ]', '', s); return re.sub(r'\s+', ' ', s).strip()
def actuals():
    raw = urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': 'dk'}), timeout=90).read()
    s = pd.read_csv(io.BytesIO(raw), low_memory=False)
    s = s[(s.season_type == 'REG') & s.position.isin(['QB', 'RB', 'WR', 'TE'])].copy()
    f = lambda c: pd.to_numeric(s[c], errors='coerce').fillna(0) if c in s else 0
    s['act'] = (f('passing_yards')/25 + 6*f('passing_tds') - 2*f('passing_interceptions') + f('rushing_yards')/10 + 6*f('rushing_tds')
                + .25*f('carries') + f('receptions') + f('receiving_yards')/10 + 6*f('receiving_tds')
                - 2*(f('rushing_fumbles_lost') + f('receiving_fumbles_lost') + f('sack_fumbles_lost'))
                + 2*(f('passing_2pt_conversions') + f('rushing_2pt_conversions') + f('receiving_2pt_conversions')))
    s['k'] = s.player_display_name.map(norm)
    return {(r.k, int(r.week)): r.act for r in s.itertuples()}, int(s.week.max())
