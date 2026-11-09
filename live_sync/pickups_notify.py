"""Top 5 pickups - what changed since the list Dom last saw (Dom, Nov 9 2026: "updated three times a day and notified of changes").
Usage: python3 pickups_notify.py <old.json | -> <new.json>
Prints JSON {"changed": bool, "push": "<one line, under 200 chars>", "lines": ["DK2: + Kenny Gainwell (RB, 57) in at #5", ...]}
A man who drops out of a top 5 is explained: on a roster now (gone from the available pool), injury report, or grade fell."""
import json, sys
old = json.load(open(sys.argv[1])) if sys.argv[1] != "-" else {}
try: old = old if old.get("leagues") else {}
except Exception: old = {}
new = json.load(open(sys.argv[2]))
lines, short = [], []
for n in sorted(new.get("leagues", {})):
    O = {g["key"]: (i + 1, g) for i, g in enumerate(old.get("leagues", {}).get(n, {}).get("top", []))}
    N = {g["key"]: (i + 1, g) for i, g in enumerate(new["leagues"][n]["top"])}
    pool = new["leagues"][n].get("pool", {})
    if not O: continue
    for k, (r, g) in N.items():
        if k not in O:
            lines.append(f"DK{n}: + {g['name']} ({g['pos']}, grade {g['grade']}) in at #{r} - {g['experts']['verdict']}"); short.append(f"DK{n} +{g['name'].split()[-1]}")
        else:
            og = O[k][1]["grade"]
            if abs(g["grade"] - og) >= 3: lines.append(f"DK{n}: {g['name']} grade {og} -> {g['grade']} (#{O[k][0]} -> #{r})")
            if O[k][1].get("status", "").split(" (")[0] != g.get("status", "").split(" (")[0]:
                lines.append(f"DK{n}: {g['name']} now {g['status'].split(' (')[0]}")
    for k, (r, g) in O.items():
        if k in N: continue
        if k not in pool: why = "taken in your league, or the experts dropped him"
        else: why = f"grade {g['grade']} -> {pool[k][0]}, passed by others"
        lines.append(f"DK{n}: - {g['name']} out of the top 5 ({why})"); short.append(f"DK{n} -{g['name'].split()[-1]}")
push = ("Top 5 pickups changed: " + ", ".join(short)) if short else ("Top 5 pickups: grades moved" if lines else "")
if len(push) > 190: push = push[:187] + "..."
print(json.dumps({"changed": bool(lines), "first": not old, "push": push, "lines": lines}, indent=1))
