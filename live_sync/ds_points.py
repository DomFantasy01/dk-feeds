"""DRAFT SHARKS - FREE LOOK-AHEAD CHECK (Nov 18 2026, Dom: "add them ... to my DK Live").
Draft Sharks' free Rankings page gives a PPR projection (3D), floor, consensus and ceiling for ~250 players, this week and every
week through 18. Their stat lines are paid (Insider) - never read. So the conversion to OUR scoring is APPROXIMATE:
    league pts = DS 3D (PPR, 4-pt pass TD)  + 2 x Clay's pass TDs  (+ 0.25 x Clay's carries in DK1-3)
using Mike Clay's stat line for the same player and week for the volume (no Clay line -> DS number unchanged, flagged).
Draft Sharks is a CHECK beside Clay for the weeks ahead (playoff weeks especially) - it never decides a move.
Writes dispatch_out/draftsharks_scored.csv: lg,key,name,team,pos,wk,w12..w18,floor,ceil,adj,read
usage: python3 ds_points.py REPO"""
import sys, os, re, csv, json
R = sys.argv[1]; O = os.path.join
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower().replace("’", "'")))
D = json.load(open(O(R, "yahoo_drop/draftsharks/ds_weekly.json")))
try: C = json.load(open(O(R, "yahoo_drop/clay/clay_weekly.json")))
except Exception: C = {"players": []}
clay = {}
for p in C.get("players", []):
    if p.get("pos") != "DST": clay[nk(p["name"])] = p
W = sorted(int(w) for w in D["weeks"]); NOW = W[0]
TM = {"JAC": "JAX", "LAR": "LA", "WSH": "WAS"}
pl = {}
for w in W:
    for r in D["weeks"][str(w)]:
        pos = "DEF" if r["pos"] in ("DST", "D/ST", "DEF") else r["pos"]
        if pos not in ("QB", "RB", "WR", "TE", "K", "DEF"): continue
        k = (TM.get(r["tm"], r["tm"]) + "DEF") if pos == "DEF" else nk(r["n"])
        e = pl.setdefault(k, dict(name=r["n"], team=TM.get(r["tm"], r["tm"]), pos=pos, wk={}))
        e["wk"][w] = r
rows, nadj = [], 0
for lg in (1, 2, 3, 4):
    for k, e in pl.items():
        cp = clay.get(k) if e["pos"] in ("QB", "RB", "WR", "TE") else None
        A = {}
        for w_, st in ((cp or {}).get("wk") or {}).items():
            g = lambda i: float(st.get(str(i), 0) or 0); A[int(w_)] = 2 * g(4) + (0 if lg == 4 else .25 * g(23))
        avg = sum(A.values()) / len(A) if A else 0   # Week 18 (Clay stops at 17): his average adjustment
        def conv(w, v):
            if v is None: return ""
            return round(v + A.get(w, avg), 2)
        cur = e["wk"].get(NOW) or {}
        adj = "clay volume" if cp else ("none (K/DEF)" if e["pos"] in ("K", "DEF") else "none (no Clay line)")
        if cp and lg == 1: nadj += 1
        rows.append([lg, k, e["name"], e["team"], e["pos"], conv(NOW, cur.get("p3d"))] +
                    [conv(w, (e["wk"].get(w) or {}).get("p3d")) for w in range(NOW + 1, 19)] +
                    [conv(NOW, cur.get("floor")), conv(NOW, cur.get("ceil")), adj, D.get("read", "")])
os.makedirs(O(R, "dispatch_out"), exist_ok=True)
with open(O(R, "dispatch_out/draftsharks_scored.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["lg", "key", "name", "team", "pos", "wk"] + [f"w{x}" for x in range(NOW + 1, 19)] + ["floor", "ceil", "adj", "read"])
    w.writerows(rows)
print(f"DRAFT SHARKS: weeks {NOW}-{W[-1]}, {len(pl)} players, {nadj} converted with Clay volume, read {D.get('read')}")
