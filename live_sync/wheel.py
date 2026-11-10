"""THE WHEEL - a five-spoke check on every Diamonds in the Rough pick (Dom, Nov 10).

TEST ONLY. It runs beside the system and is never used to make a pickup, drop or claim, or to set a MUST/HOT tag.
We compare it with the regular calls and talk about whether it helps.

Five spokes, 0-20 each (100 total):
  1 TEAM        the team around him: offense points a game (season and last 3 games - shows a quarterback change),
                record, his workload trend, injury
  2 CONSENSUS   top-3-by-accuracy average vs the starter he'd replace, and how many sources have him ahead
  3 UPSIDE      every game left: rest-of-season points, the Weeks 15-17 matchups, a path to a bigger role
  4 DROP COST   the cheapest drop, played out in the season simulator: what it costs the playoff odds,
                and whether a rival would start the man let go
  5 STAKES & OPPONENTS   the move played out: this week's win chance (weighted by how much this game matters),
                playoff odds, and who it keeps him from - this week's opponent and the rivals he'd start for
Red flag: any spoke under 5 = no move, however good the rest looks.

Usage: python3 live_sync/wheel.py <repo> [games.csv]
"""
import json, os, sys, csv, subprocess, collections, datetime, urllib.request
from zoneinfo import ZoneInfo

R = sys.argv[1]
OUT = os.path.join(R, "dispatch_out", "wheel.json")
PK = json.load(open(os.path.join(R, "dispatch_out", "pickups.json")))
CH = json.load(open(os.path.join(R, "dispatch_out", "championship.json")))
LAB = {"1": "DK I", "2": "DK II", "3": "DK III", "4": "DK IV"}
LGK = {"DK I": "DKI", "DK II": "DKII", "DK III": "DKIII", "DK IV": "DKIV"}
clamp = lambda v: max(0.0, min(20.0, v))
pc = lambda v: f"{v * 100:+.1f}".replace("-0.0", "+0.0")

# ---- the NFL teams: points a game (season + last 3), points allowed, records
gpath = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.environ.get("DK_ROOT", "/home/claude"), "dksys", "gate", "fresh", "games.csv")
def _good(p):
    try: return sum(1 for g in csv.DictReader(open(p)) if g["season"] == "2026" and g["home_score"] not in ("", "NA")) >= 100
    except Exception: return False
if not _good(gpath):
    gpath = os.path.join(os.path.dirname(OUT), "..", "live_sync", ".games_cache.csv")
    try: open(gpath, "wb").write(urllib.request.urlopen("https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv", timeout=40).read())
    except Exception as e: print("WHEEL: schedule download failed -", e)
pf, pa, res = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)
for g in csv.DictReader(open(gpath)):
    if g["season"] != "2026" or g["game_type"] != "REG" or g["home_score"] in ("", "NA"): continue
    w = int(g["week"]); h, a, hs, as_ = g["home_team"], g["away_team"], int(float(g["home_score"])), int(float(g["away_score"]))
    pf[h].append((w, hs)); pf[a].append((w, as_)); pa[h].append((w, as_)); pa[a].append((w, hs))
    res[h].append(1 if hs > as_ else .5 if hs == as_ else 0); res[a].append(1 if as_ > hs else .5 if hs == as_ else 0)
ppg = {t: sum(s for _, s in v) / len(v) for t, v in pf.items()}
l3 = {t: sum(s for _, s in sorted(v)[-3:]) / len(sorted(v)[-3:]) for t, v in pf.items()}
pag = {t: sum(s for _, s in v) / len(v) for t, v in pa.items()}
rank = lambda d, t, rev=True: (sorted(d, key=lambda k: -d[k] if rev else d[k]).index(t) + 1) if t in d else None
TEAMS = len(ppg)

# ---- every pick goes through the season simulator (test hook in championship.py - championship.json is not touched)
want = {LAB[n]: [dict(name=g["name"], pos=g["pos"], team=g["team"]) for g in L["top"]] for n, L in PK["leagues"].items()}
tmp_in, tmp_out = OUT + ".in", OUT + ".sim"
json.dump(want, open(tmp_in, "w"))
env = dict(os.environ, DK_WHEEL=tmp_in, DK_WHEEL_OUT=tmp_out)
sim = {}
try:
    p = subprocess.run([sys.executable, os.path.join(R, "live_sync", "championship.py"), R] + [LGK[l] for l in want], env=env, capture_output=True, text=True, timeout=1500)
    print("\n".join(l for l in p.stdout.splitlines() if l.startswith("WHEEL")) or p.stdout[-500:] + p.stderr[-800:])
    sim = json.load(open(tmp_out))
except Exception as e: print("WHEEL: simulator run failed -", e)
for f_ in (tmp_in, tmp_out):
    try: os.remove(f_)
    except Exception: pass

def wheel(n, g, S, C):
    lab = LAB[n]; pos, tm = g["pos"], g["team"]; parts = g.get("parts", {}); hurt = any(w.startswith("Injury:") for w in g.get("why", []))
    sp, why = {}, {}
    # 1 TEAM
    if pos == "DEF":
        r_ = rank(pag, tm, rev=False); base = (TEAMS - r_) / max(1, TEAMS - 1) * 12 if r_ else 6
        why1 = f"{tm} defense allows {pag.get(tm, 0):.1f} a game (#{r_} of {TEAMS})" if r_ else f"no scores for {tm}"
    else:
        r1, r3 = rank(ppg, tm), rank(l3, tm)
        base = ((TEAMS - r1) / max(1, TEAMS - 1) * 6 + (TEAMS - r3) / max(1, TEAMS - 1) * 6) if r1 else 6
        why1 = (f"{tm} offense {ppg[tm]:.1f} a game (#{r1}), last 3 games {l3[tm]:.1f} (#{r3})" + (" - trending down" if l3[tm] < ppg[tm] - 3 else " - trending up" if l3[tm] > ppg[tm] + 3 else "")) if r1 else f"no scores for {tm}"
    wp = sum(res[tm]) / len(res[tm]) if res.get(tm) else .5
    work = parts.get("workload", 7.5) / 15 * 5 if pos in ("RB", "WR", "TE") else 2.5
    sp["team"] = clamp(base + wp * 3 + work); why["team"] = why1 + f"; team {wp * 100:.0f}% wins; workload {parts.get('workload', '-')}/15"
    if hurt: sp["team"] = min(sp["team"], 4); why["team"] += "; on the injury report"
    # 2 CONSENSUS
    gain, ex = g.get("gain"), g.get("experts", {}); agree, of = ex.get("agree", 0), ex.get("of", 0)
    sp["consensus"] = clamp((max(-30, min(30, gain)) + 30) / 60 * 10 if gain is not None else 5) + (agree / of * 10 if of else 5)
    sp["consensus"] = clamp(sp["consensus"])
    why["consensus"] = (f"{gain:+d}% vs {g.get('replaces') or 'your starter'} (top-3 average); " if gain is not None else "no starter to compare; ") + (f"{agree} of {of} sources have him ahead" if of else "no source has both")
    # 3 UPSIDE - every game left + the playoffs
    sp["upside"] = clamp(parts.get("value", 15) / 30 * 8 + parts.get("playoffs", 7.5) / 15 * 8 + min(parts.get("path", 0), 10) / 10 * 4)
    po = next((w for w in g.get("why", []) if w.startswith("Playoffs:")), "")
    why["upside"] = f"{g.get('pts', 0):.0f} pts rest of season; {po.replace('Playoffs: ', 'Weeks 15-17 ')}" + ("; path to a bigger role" if parts.get("path") else "")
    # 4 DROP COST and 5 STAKES & OPPONENTS - from the simulator
    P = next((p for p in (S or {}).get("picks", []) if p.get("name") == g["name"]), None)
    sw = next((s for s in C.get("swing", []) if s["wk"] == C.get("week")), None)
    lev = (sw["po_w"] - sw["po_l"]) if sw else 0
    if P and P.get("best"):
        b = P["best"]; cost = b.get("drop_cost", 0); dh = b.get("drop_helps") or []
        sp["drop"] = clamp(20 + cost * 400 - 2 * min(3, len(dh)))
        why["drop"] = f"drop {b['drop']}: his loss alone {pc(cost)} playoff odds" + (f"; a rival would start him ({', '.join(dh[:2])})" if dh else "; no rival would start him")
        riv = P.get("helps_rivals") or []; block = 2 if P.get("opp_gain") else 0
        sp["stakes"] = clamp(8 + b["d_playoff"] * 400 + b["d_week"] * 40 * min(1, lev / .3) + block + (2 if len(riv) >= 3 else 0))
        why["stakes"] = (f"chance to win this week {pc(b['d_week'])}; playoff odds for the season {pc(b['d_playoff'])}"
                         + (f"; this week's game swings the playoff odds {sw['po_l'] * 100:.0f}% to {sw['po_w'] * 100:.0f}%" if sw else "")
                         + (f"; keeps him from this week's opponent {P['opp_now']}" if block else "")
                         + (f"; {len(riv)} rivals would start him" if riv else ""))
        move = dict(drop=b["drop"], d_week=b["d_week"], d_playoff=b["d_playoff"], d_title=b["d_title"], ppg=b["pts_per_game"], games=b["games_used"])
    else:
        sp["drop"] = sp["stakes"] = 10; why["drop"] = why["stakes"] = "not in the simulator's pool - scored even"; move = None
    sp = {k: round(v, 1) for k, v in sp.items()}; tot = round(sum(sp.values()))
    red = [k for k, v in sp.items() if v < 5]
    NM = dict(team="Team", consensus="Experts", upside="Upside", drop="Drop cost", stakes="Stakes & opponents")
    if red: verdict = "NO MOVE"; vwhy = "red flag (under 5): " + ", ".join(NM[k] for k in red)
    elif tot >= 70: verdict, vwhy = "GO", f"{tot}/100, every spoke 5+"
    elif tot >= 55: verdict, vwhy = "LEAN", f"{tot}/100"
    elif sp["upside"] >= 14 and sp["drop"] >= 14: verdict, vwhy = "STASH", "big upside, cheap drop"
    else: verdict, vwhy = "PASS", f"{tot}/100"
    return dict(name=g["name"], pos=pos, team=tm, tier=g.get("tier"), grade=g.get("grade"), spokes=sp, total=tot, verdict=verdict, vwhy=vwhy, why=why, move=move)

out = dict(built=datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%a %b %-d %Y %-I:%M %p PT"), test=True,
           note="TEST ONLY - runs beside the system; never used for pickups, drops, claims or MUST/HOT tags",
           pickups_built=PK.get("built"), champ_built=CH.get("built"), leagues={})
for n, L in PK["leagues"].items():
    lab = LAB[n]; C = CH["leagues"].get(lab, {}); S = sim.get(lab)
    out["leagues"][n] = dict(base=(S or {}).get("base", {}).get("playoff"), week=(S or {}).get("week"), picks=[wheel(n, g, S, C) for g in L["top"]])
json.dump(out, open(OUT, "w"), indent=1)
for n, L in out["leagues"].items():
    print(f"WHEEL DK{n}: playoff odds now {(L['base'] or 0) * 100:.1f}%")
    for w in L["picks"]: print(f"   {w['verdict']:7} {w['total']:3} {w['name']:22} {w['tier']:5} {w['spokes']}  {w['vwhy']}")
