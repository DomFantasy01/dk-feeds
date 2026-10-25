"""BEFORE LOCK in the brief (Oct 25 2026, Dom): the Radar's free-agent flags whose game hasn't kicked off go at the TOP of
brief_latest.txt, right under its first line, so they are heard first - the window to add a man free (no bid) closes at
his kickoff. Reads the alerts file the build just wrote (alerts.py, kind radar_prekick).
usage: python3 brief_prekick.py ALERTS.json BRIEF.txt"""
import sys, json, datetime as dt
al_f, br_f = sys.argv[1:3]
try: items = json.load(open(al_f)).get("items", [])
except Exception as e: print(f"BEFORE LOCK skipped: {e}"); sys.exit(0)
now = dt.datetime.now(dt.timezone.utc)
live = []
for a in items:
    if a.get("kind") != "radar_prekick" or a.get("active") is False: continue
    try:
        if dt.datetime.fromisoformat(a["deadline_utc"]) <= now: continue
    except Exception: continue
    live.append(a)
s = open(br_f).read()
# drop an earlier Before lock block (it sits right after the first line)
first, _, rest = s.partition("\n")
if rest.lstrip("\n").startswith("Before lock"):
    rest = rest.lstrip("\n").split("\n\n", 1)[1] if "\n\n" in rest.lstrip("\n") else ""
    rest = "\n" + rest
if live:
    by = {}
    for a in live: by.setdefault(a["lg"], []).append(a)
    lines = ["Before lock - free agents the Radar flagged whose games haven't started (free to add, no bid, until kickoff; nothing is added without your go): "
             + " ".join(f"{lg}: " + "; ".join(f"{a['who']} - {a['title'].split(' is a FREE AGENT now - Radar: ')[-1]}, locks {a['by'].replace('before ', '')}. {a.get('tie','')}" for a in xs)
                        for lg, xs in by.items())]
    s = first + "\n\n" + lines[0] + "\n" + rest
else:
    s = first + "\n" + rest
open(br_f, "w").write(s)
print(f"BEFORE LOCK: {len(live)} free-agent flag(s) in the brief")
