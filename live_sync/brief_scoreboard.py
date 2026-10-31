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
    m = re.match(r"(ALL WEEKS|Week \d+)\s+(\d+) men\s+(.*)$", ln)
    if not m: continue
    src = {k.lower(): float(v) for k, v in re.findall(r"(Ratcliffe|Yahoo|Gotham|Sleeper|Koerner|Brenton) ([\d.]+) pts", m.group(3))}
    if src: rows[m.group(1)] = dict(n=int(m.group(2)), **src)
weeks = sorted((k for k in rows if k.startswith("Week")), key=lambda k: int(k.split()[1]))
if not weeks: print("SCOREBOARD section skipped: no graded weeks"); sys.exit(0)
NM = {"ratcliffe": "Ratcliffe", "koerner": "Koerner", "brenton": "Brenton", "yahoo": "Yahoo", "gotham": "Gotham", "sleeper": "Sleeper"}
def line(lab, r):
    have = [(NM[k], r[k]) for k in NM if k in r]
    best = min(have, key=lambda x: x[1])[0]
    return f"{lab} ({r['n']} starters graded): " + ", ".join(f"{n} {v}" for n, v in have) + f" points missed a player - {best} closest."
last = weeks[-1]
beat = [w for w in weeks if "gotham" in rows[w] and "yahoo" in rows[w] and rows[w]["gotham"] < rows[w]["yahoo"]]
gx = re.search(r"^GOTHAM VS THE EXPERTS.*$", sb, flags=re.M)   # Oct 31 (Dom): does Gotham's disagreement ever pay off?
txt = ("Scoreboard - how the projections did (lower miss is better): " + line(last, rows[last]) +
       (" " + line("Season", {k: v for k, v in rows["ALL WEEKS"].items() if k != "ratcliffe"}) if "ALL WEEKS" in rows else "") +   # Ratcliffe only from Week 8 - not a fair season line
       f" Gotham beat Yahoo in {len(beat)} of {len(weeks)} graded weeks ({', '.join(w.replace('Week ', 'Wk ') for w in beat) or 'none'})." +
       (" " + gx.group(0) if gx else ""))
s = open(br_f).read()
s = re.sub(r"\n\nScoreboard - how the projections did.*?(?=\n\n|\Z)", "", s, flags=re.S).rstrip("\n")
open(br_f, "w").write(s + "\n\n" + txt + "\n")
print("SCOREBOARD:", txt[:160])
