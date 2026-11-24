"""DRAFT SHARKS ON THE METERS (Nov 24 2026, Dom: "Put him on the meter too. Get rid of Koerner. Move him out of there.").
Koerner (FantasyLabs) hadn't posted Week 12 by Tuesday morning, so Jared Smola's Draft Sharks numbers (FantasyPros 2026 in-season
accuracy #14, free, every week through 18) take Koerner's place as lineup check 2 beside Ratcliffe.
Reads dispatch_out/draftsharks_scored.csv (ds_points.py: Draft Sharks' free PPR projection converted to each league's scoring with
Mike Clay's volume) and fills the meter the same way rotoballer_points.py does:
  "draftsharks" on every starter and bench man (draftsharks_src = "draftsharks", or Ratcliffe's number when Draft Sharks doesn't
  list him), totals/needles["draftsharks"] and needles_set["draftsharks"] (best lineups both sides = Ratcliffe's set moved by the
  per-man difference, same spread as the other needles).
If Draft Sharks has no number for the meter's week, nothing is written - the page then shows DRAFT SHARKS as NOT POSTED.
usage: python3 ds_meter.py REPO METER.json"""
import sys, os, re, csv, json
from statistics import NormalDist, median

R, MF = sys.argv[1], sys.argv[2]
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower().replace("’", "'")))
def f(x):
    try: return float(x)
    except Exception: return None
try: M = json.load(open(MF))
except Exception as e: print("DRAFT SHARKS meter: no meter file -", e); sys.exit(0)
W = int(M.get("week") or 0)
fn = os.path.join(R, "dispatch_out/draftsharks_scored.csv")
if not os.path.exists(fn): print("DRAFT SHARKS meter: no draftsharks_scored.csv"); sys.exit(0)
rows = list(csv.DictReader(open(fn)))
if not rows: print("DRAFT SHARKS meter: empty file"); sys.exit(0)
cols = rows[0].keys()
# the file's 'wk' column is Draft Sharks' first week; the later weeks are w13..w18
first = min([int(c[1:]) for c in cols if re.fullmatch(r"w\d+", c)] or [99]) - 1
col = "wk" if first == W else (f"w{W}" if f"w{W}" in cols else None)
if not col: print(f"DRAFT SHARKS meter: no Week {W} numbers in the file (it starts at Week {first}) - not used"); sys.exit(0)
val = {}
for r in rows:
    v = f(r.get(col))
    if v is None: continue
    key = nk(r["name"]) if r["pos"] != "DEF" else r["key"]
    val[(int(r["lg"]), key)] = v
read = rows[0].get("read", "")
LGN = {"DK I": 1, "DK II": 2, "DK III": 3, "DK IV": 4}; hit = miss = 0
def look(lg, p):
    if p.get("pos") == "DEF" or p.get("slot") == "DEF":
        tm = {"JAC": "JAX", "LAR": "LA", "WSH": "WAS"}.get(p.get("team") or "", p.get("team") or "")
        v = val.get((lg, f"{tm}DEF")) or val.get((lg, nk(tm) + "def"))
        if v is not None: return v
    return val.get((lg, nk(p.get("player"))))
for lab, L in (M.get("leagues") or {}).items():
    lg = LGN.get(lab)
    for side in ("me", "op"):
        for s_ in (L.get("starters") or {}).get(side) or []:
            v = look(lg, s_)
            if v is None: s_["draftsharks"] = s_.get("ratcliffe"); s_["draftsharks_src"] = "ratcliffe (not on Draft Sharks' list)"; miss += 1
            else: s_["draftsharks"] = round(v, 2); s_["draftsharks_src"] = "draftsharks"; hit += 1
    for b in L.get("bench") or []:
        v = look(lg, b); b["draftsharks"] = round(v, 2) if v is not None else b.get("ratcliffe")
        b["draftsharks_src"] = "draftsharks" if v is not None else "ratcliffe (not on Draft Sharks' list)"
ND = NormalDist()
for lab, L in (M.get("leagues") or {}).items():
    T, Nd = L.setdefault("totals", {}), L.setdefault("needles", {})
    sds = []
    for c in ("ratcliffe", "rotoballer", "gotham", "clay"):
        t = T.get(c); n = Nd.get(c)
        if t and n is not None and 2 <= n <= 98 and abs(t[0] - t[1]) > 1: sds.append((t[0] - t[1]) / ND.inv_cdf(n / 100))
    if not T.get("ratcliffe") or not any(x > 0 for x in sds): continue
    sd = median(x for x in sds if x > 0)
    dl = [sum((s_.get("draftsharks") or 0) - (s_.get("ratcliffe") or 0) for s_ in (L.get("starters") or {}).get(side) or [] if s_.get("actual") is None) for side in ("me", "op")]
    a, b = T["ratcliffe"][0] + dl[0], T["ratcliffe"][1] + dl[1]
    T["draftsharks"] = [round(a, 2), round(b, 2)]; Nd["draftsharks"] = round(100 * ND.cdf((a - b) / sd))
    rs = (L.get("needles_set") or {}).get("ratcliffe")
    if rs is not None and 1 <= rs <= 99:
        L.setdefault("needles_set", {})["draftsharks"] = round(100 * ND.cdf(ND.inv_cdf(rs / 100) + (dl[0] - dl[1]) / sd))
    print(f"   {lab}: Draft Sharks {a:.1f} vs {b:.1f} -> {Nd['draftsharks']}% chance to win this week")
M.setdefault("sources", {})["draftsharks"] = dict(status="OK", read=read, pulled_pt=read,
    note="Draft Sharks (Jared Smola) free PPR projection, converted to each league's scoring with Clay's volume; lineup check 2 since Nov 24 (replaced Koerner)")
json.dump(M, open(MF, "w"), ensure_ascii=False)
print(f"DRAFT SHARKS meter: Week {W} from column {col}, starters on Draft Sharks' list {hit}, not on it {miss} (Ratcliffe's number used), read {read}")
