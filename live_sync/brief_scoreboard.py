"""SCOREBOARD IN THE BRIEF (Oct 27 2026, Dom): the scoreboard (cand/scoreboard.py) grades Yahoo, Gotham and Sleeper
against real points every build, but it only lived on a Dispatch page. This puts its latest week and the season line at
the end of brief_latest.txt, so the weekly check on whether Gotham is getting more accurate is heard, not hunted for.
usage: python3 brief_scoreboard.py SCOREBOARD.txt BRIEF.txt"""
import sys, re
sb_f, br_f = sys.argv[1:3]
try: sb = open(sb_f).read()
except Exception as e: print(f"SCOREBOARD section skipped: {e}"); sys.exit(0)
rows = {}
for ln in sb.splitlines():
    m = re.match(r"(ALL WEEKS|Week \d+)\s+(\d+) men\s+Yahoo ([\d.]+) pts, (\d+)%\s+Gotham ([\d.]+) pts, (\d+)%\s+Sleeper ([\d.]+) pts, (\d+)%", ln)
    if m: rows[m.group(1)] = dict(n=int(m.group(2)), y=float(m.group(3)), g=float(m.group(5)), s=float(m.group(7)))
weeks = sorted((k for k in rows if k.startswith("Week")), key=lambda k: int(k.split()[1]))
if not weeks: print("SCOREBOARD section skipped: no graded weeks"); sys.exit(0)
def line(lab, r):
    best = min(("Gotham", r["g"]), ("Yahoo", r["y"]), ("Sleeper", r["s"]), key=lambda x: x[1])[0]
    return (f"{lab} ({r['n']} of your starters): Gotham missed by {r['g']} points a player, Yahoo {r['y']}, Sleeper {r['s']} - "
            f"{best} closest.")
last = weeks[-1]
beat = [w for w in weeks if rows[w]["g"] < rows[w]["y"]]
txt = ("Scoreboard - how the projections did (lower miss is better): " + line(last, rows[last]) +
       (" " + line("Season", rows["ALL WEEKS"]) if "ALL WEEKS" in rows else "") +
       f" Gotham beat Yahoo in {len(beat)} of {len(weeks)} graded weeks ({', '.join(w.replace('Week ', 'Wk ') for w in beat) or 'none'}).")
s = open(br_f).read()
s = re.sub(r"\n\nScoreboard - how the projections did.*?(?=\n\n|\Z)", "", s, flags=re.S).rstrip("\n")
open(br_f, "w").write(s + "\n\n" + txt + "\n")
print("SCOREBOARD:", txt[:160])
