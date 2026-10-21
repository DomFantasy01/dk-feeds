# THE SCOUT REPORT CARD (Dom, Wed Oct 21 2026) - grades the Scout's pickup calls against reality.
# The Scoreboard grades weekly points; this grades the pickups. Every add the Scout puts on a board is logged the first
# time it shows up (league, week, the gain the Scout claimed, and the man on Dom's roster it would replace). Once games
# are final, both men are priced week by week in that league's scoring from the nflverse stat line (no stat line = 0,
# because a man who doesn't play scores nothing for Dom), and the add is graded: did he outscore the man he'd replace?
# Calls over Dom's 20-point bar are graded separately from the rest. Runs at the end of the Scoreboard on every build.
# Files: dispatch_out/scoreboard/scout_log.json (every call, kept), scout_card.csv (every call graded), scout_card.txt.
# Backfill: python3 scout_card.py REPO --from board1.json board2.json ...  (older boards, oldest first)
import sys, os, json, glob, re, warnings, datetime as dt
import pandas as pd
warnings.simplefilter('ignore')
R = os.environ.get("DK_ROOT", "/home/claude")
sys.path.insert(0, f"{R}/dksys/gather"); from names import norm
sys.path.insert(0, f"{R}/src/forecast"); import fc_model as FM
REPO = sys.argv[1]; OUT = f"{REPO}/dispatch_out/scoreboard"; os.makedirs(OUT, exist_ok=True)
D = os.environ.get("DK_SC_DATA", f"{R}/dksys/data/latest")
LGK = {'DK I': 1, 'DK II': 2, 'DK III': 3, 'DK IV': 4}
G = pd.read_csv(f"{D}/games.csv", low_memory=False); G = G[(G.season == G.season.max()) & (G.game_type == "REG")].copy()
G['ko'] = pd.to_datetime(G.gameday + ' ' + G.gametime.fillna('13:00'), errors='coerce').dt.tz_localize('America/New_York')
LASTKO = G.groupby('week').ko.max()
def week_at(t):
    """The NFL week being played at time t: the first week whose last game hasn't finished (kickoff + 4 hours)."""
    for w, k in LASTKO.sort_index().items():
        if t <= k + pd.Timedelta(hours=4): return int(w)
    return int(LASTKO.index.max())
FINAL = [int(w) for w, g in G.groupby('week') if g.result.notna().all()]
LOGF = f"{OUT}/scout_log.json"
LOG = json.load(open(LOGF)) if os.path.exists(LOGF) else {}
NOWRX = re.compile(r"vs your [A-Z0-9/]+ (.+?):")

def ingest(b):
    lab = b.get('league'); run = b.get('run')
    if lab not in LGK or not run: return 0
    t = pd.Timestamp(run); t = t.tz_localize('America/Los_Angeles') if t.tzinfo is None else t
    W = week_at(t); rows_of = {}
    for gk in ('gate1', 'gate2', 'gate3'):
        for c in b.get(gk) or []:
            for p in (c.get('picks') or ([c['pick']] if c.get('pick') else [])):
                if p and p.get('name') and c.get('rows'): rows_of.setdefault(p['name'], c['rows'][0])
    n = 0
    for a in b.get('adds') or []:
        if not a.get('name') or a.get('pos') in ('K', 'DEF'): continue
        k = f"{lab}|{norm(a['name'])}"; m = NOWRX.search(a.get('now') or '')
        rep = m.group(1).strip() if m else rows_of.get(a['name'])
        e = LOG.get(k)
        if e is None:
            LOG[k] = e = dict(league=lab, player=a['name'], pos=a.get('pos'), team=a.get('team'), first_week=W, first_seen=str(t),
                              gain=a.get('gain'), pgain=a.get('pgain'), best_gain=a.get('gain'), acq=a.get('acq'), replaced=rep, times=0); n += 1
        e['times'] += 1; e['last_seen'] = str(t); e['last_week'] = W
        if (a.get('gain') or 0) > (e.get('best_gain') or 0): e['best_gain'] = a.get('gain')
        if not e.get('replaced') and rep: e['replaced'] = rep
    return n

boards = sys.argv[sys.argv.index('--from') + 1:] if '--from' in sys.argv else sorted(glob.glob(f"{REPO}/dispatch_out/scout_state/scout_board_DK*.json"))
new = 0
for f in boards:
    try: new += ingest(json.load(open(f)))
    except Exception as ex: print("   scout card: skipped", os.path.basename(f), ex)
json.dump(LOG, open(LOGF, 'w'), indent=0)

# ---- grade
S = pd.read_csv(f"{D}/stats_week.csv", low_memory=False)
S = S[(S.season == G.season.max()) & (S.season_type == 'REG')].fillna(0).copy(); S['k'] = S.player_display_name.astype(str).map(norm)
PTS = {}
for lab, n_ in LGK.items():
    x = S.assign(p=FM.price(S, n_)); PTS[lab] = x.groupby(['k', 'week']).p.sum().to_dict()
def pts(lab, name, w): return float(PTS[lab].get((norm(name), w), 0.0))
rows = []
for k, e in LOG.items():
    wks = [w for w in FINAL if w >= e['first_week']]
    if not wks or not e.get('replaced'): continue
    a = [pts(e['league'], e['player'], w) for w in wks]; r = [pts(e['league'], e['replaced'], w) for w in wks]
    rows.append(dict(league=e['league'], player=e['player'], pos=e['pos'], replaced=e['replaced'], first_week=e['first_week'],
                     claimed_gain=e.get('gain'), over_bar=(e.get('best_gain') or 0) >= 20, weeks=len(wks),
                     add_ppg=round(sum(a) / len(wks), 2), rep_ppg=round(sum(r) / len(wks), 2), net=round(sum(a) - sum(r), 2)))
C = pd.DataFrame(rows)
pt = dt.datetime.now(dt.timezone(dt.timedelta(hours=-7)))
out = [f"THE SCOUT REPORT CARD - graded {pt:%a %b %d %Y} {pt.hour % 12 or 12}:{pt:%M} {'AM' if pt.hour < 12 else 'PM'} PT. Every add the Scout put on a board,",
       "graded against the man on Dom's roster it would replace, in that league's scoring, every final week since the call.", ""]
if not len(C):
    out.append(f"Nothing to grade yet: {len(LOG)} calls logged, waiting for their games to go final.")
else:
    C.to_csv(f"{OUT}/scout_card.csv", index=False)
    for lab_, g in (("OVER THE 20-POINT BAR", C[C.over_bar]), ("UNDER THE BAR", C[~C.over_bar])):
        if not len(g): out.append(f"{lab_}: no calls graded yet"); continue
        out.append(f"{lab_}: {len(g)} calls, the add outscored the man he'd replace in {int((g.net > 0).sum())} "
                   f"({(g.net > 0).mean():.0%}) - average {g.net.sum() / g.weeks.sum():+.1f} pts a week for the add.")
    out.append("")
    out.append("BEST CALLS:  " + " | ".join(f"{r.league} {r.player} over {r.replaced} {r.net:+.1f} ({r.weeks} wk)" for r in C.sort_values('net', ascending=False).head(5).itertuples()))
    out.append("WORST CALLS: " + " | ".join(f"{r.league} {r.player} over {r.replaced} {r.net:+.1f} ({r.weeks} wk)" for r in C.sort_values('net').head(5).itertuples()))
    out.append(f"\n{len(LOG)} calls logged; {len(C)} graded (the rest are this week's, or have no roster match to compare).")
open(f"{OUT}/scout_card.txt", "w").write("\n".join(out) + "\n")
print(f"   scout card: {new} new calls logged, {len(LOG)} total, {len(C)} graded"); print("   " + "\n   ".join(out[3:6]))
