"""DR. ROTO - SECOND PILLAR ON THE METER (Nov 24 2026, Dom subscribed to Dr. Roto All Access and said: "we could use both of them
as the top pillars as far as experts are concerned. And when they disagree, we're going to talk about it. When anyone else
disagrees, they're ... less of a concern"). Ratcliffe still decides; Dr. Roto is the pillar beside him on the big Live dial.

Graded first (Weeks 8-11, the same 308 rostered player-weeks the other experts are graded on): start/sit calls right 69.1%
(Ratcliffe 71.5, Yahoo 71.1, Clay 68.5, Koerner 68.3); typical miss 6.5 pts (Ratcliffe 6.5). Best at QB/WR, weakest at TE.
When he and Ratcliffe ordered a pair differently, Dr. Roto was right 41%.

Source: yahoo_drop/drroto/drroto_weekly.json, read in Chrome by dk_drroto_read.js from his NFL Dashboard ("Full week" slate,
every game). Projections are DraftKings scoring and come as a TOTAL only (no stat line), so the conversion to OUR scoring is
APPROXIMATE, done the same way as Draft Sharks (ds_points.py) with Mike Clay's stat line for the same player and week:
    league = DK  + 2 x pass TD  - (it+1) x INT   (+0.25 x carries in DK I-III)  - 1 x fumbles lost  - expected DK yardage bonuses
    (it = -2 in DK I-III, -1 in DK IV; bonuses +3 at 300 pass / 100 rush / 100 rec yds, chance from Clay's yards)
No Clay line -> DK number unchanged, flagged. DST: DK's defense scoring = Yahoo's default; left as is. No kickers on his board.
Writes dispatch_out/drroto_scored.csv (lg,key,name,team,pos,wk,floor,ceil,tgt,ra,snap,adj,read) and keeps the FIRST read of
each week in dispatch_out/drroto_history/wk<N>_first.json (for the weekly grade and the meter's "since first posting" line).
With a meter file: "drroto" on every starter and bench man, totals/needles["drroto"] and needles_set["drroto"], exactly like
ds_meter.py (best lineups both sides = Ratcliffe's set moved by the per-man difference, same spread as the other needles).
If the saved read is not for the meter's week, nothing is written - the page then shows DR. ROTO as NOT POSTED.
usage: python3 drroto_points.py REPO [METER.json]"""
import sys, os, re, csv, json, math
from statistics import NormalDist, median

R = sys.argv[1]; MF = sys.argv[2] if len(sys.argv) > 2 else None; O = os.path.join
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower().replace("’", "'")))
def f(x):
    try: return float(x)
    except Exception: return None
TM = {"JAC": "JAX", "LAR": "LA", "WSH": "WAS"}
try: D = json.load(open(O(R, "yahoo_drop/drroto/drroto_weekly.json")))
except Exception as e: print("DR. ROTO: no saved read -", e); sys.exit(0)
W = int(D.get("week") or 0); READ = D.get("read", "")
try: C = json.load(open(O(R, "yahoo_drop/clay/clay_weekly.json")))
except Exception: C = {"players": []}
clay = {nk(p["name"]): (p.get("wk") or {}).get(str(W)) for p in C.get("players", []) if p.get("pos") != "DST"}

ND = NormalDist()
def p_over(mean, thr, cv):
    if not mean or mean <= 0: return 0.0
    return 1 - ND.cdf((thr - mean) / max(1.0, cv * mean))
def adjust(st, lg):
    g = lambda i: float(st.get(str(i), 0) or 0)
    it = -1 if lg == 4 else -2; ra = 0 if lg == 4 else .25
    bonus = 3 * p_over(g(3), 300, .28) + 3 * p_over(g(24), 100, .55) + 3 * p_over(g(42), 100, .55)
    return 2 * g(4) + (it + 1) * g(20) + ra * g(23) - g(72) - bonus

rows, val, nadj = [], {}, 0
for lg in (1, 2, 3, 4):
    for p in D.get("players", []):
        pos = "DEF" if p.get("pos") in ("DST", "D/ST", "DEF") else p.get("pos")
        if pos not in ("QB", "RB", "WR", "TE", "DEF"): continue
        tm = TM.get(p.get("tm"), p.get("tm"))
        key = tm + "DEF" if pos == "DEF" else nk(p["n"])
        st = clay.get(key) if pos != "DEF" else None
        a = adjust(st, lg) if st else 0.0
        adj = "clay volume" if st else ("none (DEF - DK = Yahoo default)" if pos == "DEF" else "none (no Clay line)")
        if st and lg == 1: nadj += 1
        cv = lambda v: "" if v is None else round(v + a, 2)
        dk = f(p.get("dk"))
        rows.append([lg, key, p["n"], tm, pos, cv(dk), cv(f(p.get("floor"))), cv(f(p.get("ceil"))), p.get("tgt"), p.get("ra"), p.get("snap"), adj, READ])
        if dk is not None: val[(lg, key)] = round(dk + a, 2)
os.makedirs(O(R, "dispatch_out/drroto_history"), exist_ok=True)
with open(O(R, "dispatch_out/drroto_scored.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["lg", "key", "name", "team", "pos", "wk", "floor", "ceil", "tgt", "ra", "snap", "adj", "read"]); w.writerows(rows)
hf = O(R, f"dispatch_out/drroto_history/wk{W}_first.json")
if not os.path.exists(hf): json.dump(D, open(hf, "w"))
json.dump(D, open(O(R, f"dispatch_out/drroto_history/wk{W}_last.json"), "w"))
print(f"DR. ROTO: Week {W}, {len(D.get('players', []))} players, {nadj} converted with Clay volume, read {READ}")

# ---------------------------------------------------------------- meter
if not MF: sys.exit(0)
try: M = json.load(open(MF))
except Exception as e: print("DR. ROTO meter: no meter file -", e); sys.exit(0)
MW = int(M.get("week") or 0)
src = M.setdefault("sources", {})
if MW != W:
    src["drroto"] = dict(status="NOT POSTED", read=READ, note=f"Dr. Roto's saved read is Week {W}; the meter is Week {MW}")
    json.dump(M, open(MF, "w"), ensure_ascii=False); print(f"DR. ROTO meter: saved read is Week {W}, meter is Week {MW} - not used"); sys.exit(0)
LGN = {"DK I": 1, "DK II": 2, "DK III": 3, "DK IV": 4}; hit = miss = 0
def look(lg, p):
    if p.get("pos") == "DEF" or p.get("slot") == "DEF":
        tm = TM.get(p.get("team") or "", p.get("team") or "")
        v = val.get((lg, f"{tm}DEF"))
        if v is not None: return v
    return val.get((lg, nk(p.get("player"))))
for lab, L in (M.get("leagues") or {}).items():
    lg = LGN.get(lab)
    for side in ("me", "op"):
        for s_ in (L.get("starters") or {}).get(side) or []:
            if s_.get("slot") == "K" or s_.get("pos") == "K":
                s_["drroto"] = s_.get("ratcliffe"); s_["drroto_src"] = "ratcliffe (Dr. Roto has no kickers)"; continue
            v = look(lg, s_)
            if v is None: s_["drroto"] = s_.get("ratcliffe"); s_["drroto_src"] = "ratcliffe (not on Dr. Roto's board)"; miss += 1
            else: s_["drroto"] = round(v, 2); s_["drroto_src"] = "drroto"; hit += 1
    for b in L.get("bench") or []:
        v = look(lg, b); b["drroto"] = round(v, 2) if v is not None else b.get("ratcliffe")
        b["drroto_src"] = "drroto" if v is not None else "ratcliffe (not on Dr. Roto's board)"
for lab, L in (M.get("leagues") or {}).items():
    T, Nd = L.setdefault("totals", {}), L.setdefault("needles", {})
    sds = []
    for c in ("ratcliffe", "rotoballer", "gotham", "clay"):
        t = T.get(c); n = Nd.get(c)
        if t and n is not None and 2 <= n <= 98 and abs(t[0] - t[1]) > 1: sds.append((t[0] - t[1]) / ND.inv_cdf(n / 100))
    if not T.get("ratcliffe") or not any(x > 0 for x in sds): continue
    sd = median(x for x in sds if x > 0)
    dl = [sum((s_.get("drroto") or 0) - (s_.get("ratcliffe") or 0) for s_ in (L.get("starters") or {}).get(side) or [] if s_.get("actual") is None) for side in ("me", "op")]
    a, b = T["ratcliffe"][0] + dl[0], T["ratcliffe"][1] + dl[1]
    T["drroto"] = [round(a, 2), round(b, 2)]; Nd["drroto"] = round(100 * ND.cdf((a - b) / sd))
    rs = (L.get("needles_set") or {}).get("ratcliffe")
    if rs is not None and 1 <= rs <= 99:
        L.setdefault("needles_set", {})["drroto"] = round(100 * ND.cdf(ND.inv_cdf(rs / 100) + (dl[0] - dl[1]) / sd))
    print(f"   {lab}: Dr. Roto {a:.1f} vs {b:.1f} -> {Nd['drroto']}% chance to win this week")
src["drroto"] = dict(status="OK", read=READ, pulled_pt=READ,
    note="Dr. Roto (NFL Dashboard, DraftKings scoring) converted to each league's scoring with Clay's volume - approximate; pillar 2 beside Ratcliffe since Nov 24")
json.dump(M, open(MF, "w"), ensure_ascii=False)
print(f"DR. ROTO meter: Week {W}, starters on his board {hit}, not on it {miss} (Ratcliffe's number used), read {READ}")
