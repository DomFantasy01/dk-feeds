# LINE MOVES (Nov 27 2026, Dom: "Yeah, do it all" - track how the Vegas numbers move during the week, the signal Dr. Roto talks
# about: a team total going from 45 to 50 means that offense is heating up). Every Dispatch build reads the betting lines in the
# free nflverse schedule (spread + game total), works out each team's implied points (total/2 +- spread/2), and keeps a history
# (dispatch_out/vegas_lines_history.jsonl - one line whenever a game's line changes). line_moves.json then shows, for this week and
# next, each team's implied total when we first saw it and now. A move of 2+ points is flagged. It flags; it never decides.
# usage: python3 line_moves.py <repo> <games.csv>
import sys, os, json, datetime as dt
from zoneinfo import ZoneInfo
import pandas as pd

REPO, GAMES = sys.argv[1], sys.argv[2]
PT = ZoneInfo("America/Los_Angeles"); NOW = dt.datetime.now(dt.timezone.utc)
HIST = os.path.join(REPO, "dispatch_out/vegas_lines_history.jsonl")
FIX = {"LA": "LAR", "WSH": "WAS", "JAC": "JAX"}
g = pd.read_csv(GAMES, low_memory=False)
g = g[(g.season == 2026) & (g.game_type == "REG")]
weeks = sorted(int(w) for w in g[g.result.isna()].week.unique())[:2]          # this week (games still to play) and next
g = g[g.week.isin(weeks) & g.total_line.notna() & g.spread_line.notna()]

last = {}
if os.path.exists(HIST):
    for ln in open(HIST):
        try: j = json.loads(ln); last.setdefault(j["gid"], []).append(j)
        except Exception: pass
new = []
for r in g.itertuples(index=False):
    tot, spr = float(r.total_line), float(r.spread_line)        # nflverse spread_line: + = home favored
    rec = dict(gid=r.game_id, wk=int(r.week), home=FIX.get(r.home_team, r.home_team), away=FIX.get(r.away_team, r.away_team),
               total=tot, spread=spr, home_tt=round(tot / 2 + spr / 2, 1), away_tt=round(tot / 2 - spr / 2, 1), at=NOW.isoformat(timespec="minutes"))
    h = last.get(r.game_id)
    if not h or (h[-1]["total"], h[-1]["spread"]) != (tot, spr):
        new.append(rec); last.setdefault(r.game_id, []).append(rec)
if new:
    with open(HIST, "a") as f:
        for x in new: f.write(json.dumps(x) + "\n")

def ptxt(iso): return dt.datetime.fromisoformat(iso).astimezone(PT).strftime("%a %b %-d %-I:%M %p PT")
TEAMS, MOVES = {}, []
for gid, h in last.items():
    if not h or h[-1]["wk"] not in weeks: continue
    a, b = h[0], h[-1]
    for side, opp_side, ha in (("home", "away", "vs"), ("away", "home", "@")):
        tm = b[side]; d = round(b[side + "_tt"] - a[side + "_tt"], 1)
        TEAMS[f"{tm}:{b['wk']}"] = dict(team=tm, wk=b["wk"], opp=f"{ha} {b[opp_side]}", first=a[side + "_tt"], now=b[side + "_tt"], move=d,
                                       first_at=ptxt(a["at"]), total_first=a["total"], total_now=b["total"])
        if abs(d) >= 2: MOVES.append(TEAMS[f"{tm}:{b['wk']}"])
MOVES.sort(key=lambda x: -abs(x["move"]))
J = dict(built=NOW.astimezone(PT).strftime("%a %b %-d %Y %-I:%M %p PT"), weeks=[int(w) for w in weeks],
         source="nflverse schedule betting lines (free) - implied team points = total/2 +- spread/2",
         note="History starts Nov 27 2026; a team's 'first' is the first line this system saw that week, not the opening line.",
         flag_rule="implied team total moved 2+ points since first seen", moves=MOVES, teams=TEAMS)
json.dump(J, open(os.path.join(REPO, "dispatch_out/line_moves.json"), "w"), indent=1)
print(f"LINE MOVES weeks {weeks}: {len(new)} line changes recorded, {len(MOVES)} teams moved 2+ points")
for m in MOVES[:12]: print(f"  W{m['wk']} {m['team']:3} {m['opp']:7} {m['first']} -> {m['now']} ({m['move']:+})")
