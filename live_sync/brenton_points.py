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
# Oct 31 2:50 PM (Dom: "we don't know what that means"): Brenton is RANKING-ONLY now - no points, off the needles (Mike Clay took
# the slot, clay_points.py). His order is a check: when he ranks one of Dom's men (or a man on the talk list) far from where
# Ratcliffe ranks him at the same position this week, it is flagged to dig into. Nothing here drives a number.
M = json.load(open(mf)); LGN = {"DK I": "1", "DK II": "2", "DK III": "3", "DK IV": "4"}
rrank = {}
for (lg, pos), xs in rat.items():
    for i, (v, n) in enumerate(sorted(xs, reverse=True)): rrank[(lg, pos, nk(n))] = i + 1
nflag = 0
for lab, L in (M.get("leagues") or {}).items():
    lg = LGN.get(lab); seen, fl = set(), []
    T = L.get("talk") or {}
    men = [(s, "your starter") for s in (L.get("starters") or {}).get("me") or []] + [(b, "your bench") for b in L.get("bench") or []] + \
          [(dict(player=t.get("name"), pos=t.get("pos")), "free agent on your talk list") for t in (T.get("talk") or []) + (T.get("watch") or [])]
    for s, who in men:
        pos, k_ = s.get("pos"), nk(s.get("player"))
        for key in ("brenton", "brenton_src"): s.pop(key, None)
        if not pos or pos in ("K", "DEF") or (pos, k_) in seen: continue
        seen.add((pos, k_)); b = rk.get((pos, k_)); r = rrank.get((lg, pos, k_))
        if not b or not r or min(b, r) > 40 or abs(b - r) < 8: continue
        fl.append(dict(player=s.get("player"), pos=pos, who=who, brenton=b, ratcliffe=r, higher="Brenton" if b < r else "Ratcliffe"))
    for t in (L.get("totals") or {}, L.get("needles") or {}): t.pop("brenton", None)
    L["brenton_flags"] = sorted(fl, key=lambda x: -abs(x["brenton"] - x["ratcliffe"]))[:6]; nflag += len(fl)
M.setdefault("sources", {})["brenton"] = dict(status="OK", read=read, note="Paul Brenton (Points Over Hype) weekly ranks - ranking check only, no points")
json.dump(M, open(mf, "w"), ensure_ascii=False)
print(f"BRENTON: {len(rk)} ranks (read {read}); ranking check only - {nflag} men ranked 8+ spots from Ratcliffe")
