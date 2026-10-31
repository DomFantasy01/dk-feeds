"""BRENTON ON THE NEEDLES (Oct 31 2026, Dom: "I want another expert ... I don't want to pay for another one ... I don't
need to have the engine on my needle pages if I have another expert").
Paul Brenton (Points Over Hype) is FantasyPros' most accurate in-season ranker of 2026 and his weekly lists are free -
but he publishes RANKS, not points. To put him on a needle, each of his ranks is turned into points on Ratcliffe's
scale in that league's scoring: Brenton's RB12 gets the points of the 12th-best RB in Ratcliffe's weekly numbers.
So the needle shows Brenton's ORDER (who he thinks beats whom) at Ratcliffe's point level - said plainly on Live.
K and DEF: Brenton's feed here has no kicker/defense list, so those use Ratcliffe's own number.
Reads yahoo_drop/morning/expert_rankings.txt (pull_experts.py) and dispatch_out/ftn_scored.csv; writes
dispatch_out/brenton_scored.csv and adds "brenton" to every player in dispatch_out/meter_wk<W>.json (Live reads it).
usage: python3 brenton_points.py REPO [METER.json FTN_SCORED.csv]
Oct 31 (Dom: the Dispatch's one graphic page): it now also writes needles["brenton"] and totals["brenton"] into the meter, so the
printed page shows Brenton where Gotham was. Totals = Ratcliffe's best-lineup totals moved by Brenton's difference on every man
still to play; the needle uses the same spread the meter uses for every other source (read back from those sources)."""
import sys, os, re, csv, json, glob

R = sys.argv[1]; O = os.path.join
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower().replace("’", "'")))
rk, read = {}, ""
try:
    for ln in open(O(R, "yahoo_drop/morning/expert_rankings.txt")):
        if ln.startswith("#"):
            m = re.search(r"read live (.*?) \(", ln); read = read or (m.group(1) if m else ""); continue
        f = ln.rstrip("\n").split("|")
        if len(f) >= 7 and f[1] == "Paul Brenton" and f[3].isdigit(): rk[(f[2], nk(f[4]))] = int(f[3])
except Exception as e: print("BRENTON skipped:", e); sys.exit(0)
if not rk: print("BRENTON: no Brenton list in the expert file this build - needles keep the engine in his slot"); sys.exit(0)
FTN = sys.argv[3] if len(sys.argv) > 3 else O(R, "dispatch_out/ftn_scored.csv")
rat = {}
for r in csv.DictReader(open(FTN)):
    try: rat.setdefault((r["lg"], r["pos"]), []).append((float(r["wk"]), r["name"]))
    except Exception: pass
ladder = {k: sorted((v for v, _ in xs), reverse=True) for k, xs in rat.items()}
rows, val = [], {}
for (pos, k_), n in rk.items():
    for lg in ("1", "2", "3", "4"):
        L = ladder.get((lg, pos)) or []
        if not L: continue
        v = L[min(n, len(L)) - 1]; val[(lg, k_)] = round(v, 2); rows.append([lg, pos, k_, n, round(v, 2)])
with open(O(R, "dispatch_out/brenton_scored.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["lg", "pos", "key", "brenton_rank", "brenton_pts"]); w.writerows(rows)
if len(sys.argv) > 2: mf = sys.argv[2]
else:
    W = max([int(re.search(r"_wk(\d+)", f).group(1)) for f in glob.glob(O(R, "dispatch_out/meter_wk*.json"))] or [0])
    mf = O(R, f"dispatch_out/meter_wk{W}.json")
M = json.load(open(mf)); LGN = {"DK I": "1", "DK II": "2", "DK III": "3", "DK IV": "4"}
hit = miss = 0
for lab, L in (M.get("leagues") or {}).items():
    lg = LGN.get(lab)
    for side in ("me", "op"):
        for s in (L.get("starters") or {}).get(side) or []:
            if s.get("pos") in ("K", "DEF"): s["brenton"] = s.get("ratcliffe"); s["brenton_src"] = "ratcliffe (no K/DEF list)"; continue
            v = val.get((lg, nk(s.get("player"))))
            if v is None: s["brenton"] = s.get("ratcliffe"); s["brenton_src"] = "ratcliffe (Brenton has no rank for him)"; miss += 1
            else: s["brenton"] = v; s["brenton_src"] = "brenton"; hit += 1
    for b in L.get("bench") or []:
        v = val.get((lg, nk(b.get("player")))); b["brenton"] = v if v is not None else b.get("ratcliffe")
from statistics import NormalDist, median
ND = NormalDist()
for lab, L in (M.get("leagues") or {}).items():
    T, N = L.get("totals") or {}, L.get("needles") or {}
    sds = []
    for c in ("ratcliffe", "koerner", "gotham", "sleeper", "yahoo_from_spread"):
        t = T.get(c if c != "yahoo_from_spread" else "yahoo"); n = N.get(c)
        if t and n is not None and 2 <= n <= 98 and abs(t[0] - t[1]) > 1: sds.append((t[0] - t[1]) / ND.inv_cdf(n / 100))
    if not T.get("ratcliffe") or not sds: continue
    sd = median(x for x in sds if x > 0) if any(x > 0 for x in sds) else None
    if not sd: continue
    dl = [sum((s.get("brenton") or 0) - (s.get("ratcliffe") or 0) for s in (L.get("starters") or {}).get(side) or [] if s.get("actual") is None) for side in ("me", "op")]
    a, b = T["ratcliffe"][0] + dl[0], T["ratcliffe"][1] + dl[1]
    T["brenton"] = [round(a, 2), round(b, 2)]; N["brenton"] = round(100 * ND.cdf((a - b) / sd))
    print(f"   {lab}: Brenton {a:.1f} vs {b:.1f} -> {N['brenton']}% chance to win this week (spread {sd:.1f})")
M.setdefault("sources", {})["brenton"] = dict(status="OK", read=read, note="Paul Brenton (Points Over Hype) weekly ranks, turned into points on Ratcliffe's scale in each league's scoring")
json.dump(M, open(mf, "w"), ensure_ascii=False)
print(f"BRENTON: {len(rk)} ranks (read {read}); starters with his rank {hit}, without {miss} (Ratcliffe's number used)")
