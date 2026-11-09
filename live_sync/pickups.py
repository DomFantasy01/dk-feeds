"""Dark Knight - TOP 5 PICKUPS (Dom, Nov 9 2026: "a section on DK Live with top 5 pickups moving forward and why,
potential points rest of season, and a grade on a scale to 100").

For each league: every RB / WR / TE NOT on a roster in that league (Yahoo read, dk<n>_rosters_live.txt), scored and graded,
top 5 kept.  K / DEF / QB stay out (Dom keeps K/DEF out of pickup sweeps).

POTENTIAL POINTS = Ratcliffe's rest-of-season points per game, ALREADY CONVERTED to that league's scoring
(dispatch_out/ftn_scored.csv), times the games the player's team has left in Weeks 10-17 (byes taken out).

GRADE (0-100) - built for EACH of Dom's teams (Nov 9, Dom: "they all have different needs and requirements"):
  value     30  potential points, 100+ = full marks
  fit       25  this team's needs: fills an OPEN Missing Piece or a new gap at his position (10, +2 more if he plays in the
                short weeks), beats the man he'd replace on Dom's roster (up to 10 at +30%; Dom's bar is +15%),
                and depth (5 if Dom has no healthy bench man at the position, 2.5 if one)
  workload  15  carries+targets and snap share over his last 3 games played (rising = more)
  playoffs  15  Weeks 15-17 opponents' points allowed to his position this season (rank 1 = gives up most)
  team       5  his NFL team's win percentage (Dom: winning teams)
  path      10  a coach on record about a bigger role (6) and/or the starter ahead of him fading or hurt (4) - notes file

Inputs: nflverse weekly stats + snap counts + schedule (data dir arg), dispatch_out/ftn_scored.csv,
yahoo_drop/scout/dk<n>_rosters_live.txt and dk<n>_waivers.txt, live_sync/pickup_notes.json (standings + coach quotes).
Output: JSON for the Live page's `live/pickups` document.
Usage: python3 live_sync/pickups.py <nflverse_dir> <out.json> [live_status.json]
live_status.json (optional): {"checked": "<when>", "status": {"<league>|<normalized name>": "W (Nov 11)" | "FA"}} from a live
Yahoo player search. Without it the status comes from the 5:30 AM roster read, which misses that Yahoo puts every player whose
game has been played on waivers until Wednesday - so the page labels that status "per <read time>, confirm live".
"""
import csv, json, re, sys, os, collections, datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NFL = sys.argv[1]; OUT = sys.argv[2]
LIVE = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {"checked": "", "status": {}}
POS = ("RB", "WR", "TE")
LEAGUES = {1: "DK I", 2: "DK II", 3: "DK III", 4: "DK IV"}

def norm(n):
    n = n.replace("-", " ").lower().replace(".", "").replace("'", "").replace("’", "")
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return re.sub(r"[^a-z ]", "", re.sub(r"\s+", " ", n)).strip()
f = lambda v: float(v) if v not in ("", None) else 0.0

notes = json.load(open(os.path.join(ROOT, "live_sync", "pickup_notes.json")))
def _ok(p):
    try: return os.path.exists(p) and open(p).readline().startswith("game_id,season")
    except Exception: return False
GAMES = os.path.join(NFL, "games.csv") if _ok(os.path.join(NFL, "games.csv")) else os.path.join(ROOT, "system", "src", "role_watch", "data", "games.csv")
# records: from the fresh nflverse schedule when it has this season's scores, else the hand-kept standings in the notes file
REC, STAND_ASOF = dict(notes["standings"]["records"]), notes["standings"]["asof"]
_wl = collections.defaultdict(lambda: [0, 0, 0]); _n = 0
for g in csv.DictReader(open(GAMES)):
    if g["season"] == "2026" and g["game_type"] == "REG" and g["home_score"] not in ("", "NA"):
        h, a, hs, as_ = g["home_team"], g["away_team"], int(float(g["home_score"])), int(float(g["away_score"])); _n += 1
        if hs > as_: _wl[h][0] += 1; _wl[a][1] += 1
        elif as_ > hs: _wl[a][0] += 1; _wl[h][1] += 1
        else: _wl[h][2] += 1; _wl[a][2] += 1
if _n >= 100:   # a real mid-season schedule file, not the stale Week 4 copy
    REC = {t: f"{w}-{l}" + (f"-{d}" if d else "") for t, (w, l, d) in _wl.items()}
    STAND_ASOF = f"nflverse schedule, {_n} games scored"
def winpct(tm):
    r = REC.get(tm)
    if not r: return None
    p = [int(x) for x in r.split("-")]; w, l, t = (p + [0])[:3]
    return (w + t / 2) / max(1, w + l + t)

# ---- usage + matchups from nflverse
stats = [x for x in csv.DictReader(open(os.path.join(NFL, "stats_player_week_2026.csv"))) if x["season_type"] == "REG"]
snaps = {}
for s in csv.DictReader(open(os.path.join(NFL, "snap_counts_2026.csv"))):
    if s["game_type"] == "REG": snaps[(s["game_id"], norm(s["player"]))] = f(s["offense_pct"])
last_week = max(int(x["week"]) for x in stats)
games_by_team = collections.defaultdict(set)
for x in stats: games_by_team[x["opponent_team"]].add(x["game_id"])
allow = collections.defaultdict(float)
for x in stats:
    if x["position"] in POS: allow[(x["opponent_team"], x["position"])] += f(x["fantasy_points_ppr"])
rank = {}
for pos in POS:
    ds = sorted({d for (d, p) in allow if p == pos}, key=lambda d: -allow[(d, pos)] / len(games_by_team[d]))
    for i, d in enumerate(ds): rank[(d, pos)] = i + 1
use = collections.defaultdict(list)
for x in stats:
    if x["position"] not in POS: continue
    o = f(x["carries"]) + f(x["targets"]); sp = snaps.get((x["game_id"], norm(x["player_display_name"])))
    if o > 0 or (sp or 0) > 0:
        use[norm(x["player_display_name"])].append((int(x["week"]), o, sp, x["team"]))
sched = collections.defaultdict(dict)
for g in csv.DictReader(open(GAMES)):
    if g["season"] == "2026" and g["game_type"] == "REG":
        w = int(g["week"]); sched[g["home_team"]][w] = g["away_team"]; sched[g["away_team"]][w] = g["home_team"]

# ---- latest injury report line per player (nflverse injuries): Out / Doubtful / IR costs 10 grade points and is said
INJ = {}
try:
    for x in csv.DictReader(open(os.path.join(NFL, "injuries_2026.csv"))):
        if x.get("game_type", "REG") == "REG": INJ[norm(x["full_name"])] = (int(x["week"]), x["report_status"] or "", x["report_primary_injury"] or "")
except Exception: pass

# ---- Ratcliffe, converted to each league's scoring
ftn = {}
read_pt = ""
for r in csv.DictReader(open(os.path.join(ROOT, "dispatch_out", "ftn_scored.csv"))):
    if r["pos"] in POS: ftn[(int(r["lg"]), norm(r["name"]))] = r; read_pt = r["read_pt"]

ME = {1: 2, 2: 7, 3: 2, 4: 6}          # Dom's team id in each league (same map as the Yahoo readers)
PIECE_DEF = json.load(open(os.path.join(ROOT, "system", "cand", "missing_pieces.json")))["leagues"]
try: PCHK = json.load(open(os.path.join(ROOT, "dispatch_out", "pieces_check.json")))
except Exception: PCHK = {"leagues": {}}
def needs(n):
    """OPEN Missing Pieces + new gaps for league n: list of (positions, short weeks, label)."""
    lab = LEAGUES[n]; out = []
    defs = {d["piece"]: d for d in PIECE_DEF.get(lab, [])}
    for pc in PCHK["leagues"].get(lab, {}).get("pieces", []):
        if pc.get("status") == "open" and pc["piece"] in defs: out.append((defs[pc["piece"]]["pos"], pc.get("short", []), pc["piece"]))
    for g in PCHK["leagues"].get(lab, {}).get("gaps", []): out.append(([g["pos"]], g.get("weeks", []), f"new gap at {g['pos']}"))
    return out
def my_roster(n):
    L = open(os.path.join(ROOT, "yahoo_drop", "scout", f"dk{n}_rosters_live.txt")).read().splitlines()[1:]
    R = []
    for l in L:
        p = l.split("|")
        if len(p) >= 6 and p[0] == str(ME[n]): R.append(dict(slot=p[1], name=p[2], pos=p[4], status=p[5].strip()))
    return R
OUTST = ("O", "IR", "IR-R", "NA", "SUSP", "PUP", "D")

def taken_and_waivers(n):
    L = open(os.path.join(ROOT, "yahoo_drop", "scout", f"dk{n}_rosters_live.txt")).read().splitlines()
    head = L[0]; taken = {norm(l.split("|")[2]) for l in L[1:] if l.count("|") >= 4}
    W = open(os.path.join(ROOT, "yahoo_drop", "scout", f"dk{n}_waivers.txt")).read().splitlines()
    wv = {}
    for t in (W[1].split("|") if len(W) > 1 else []):
        if "/" in t: a, b = t.split("/", 1); wv[norm(a)] = b
    m = re.search(r"read (.+?PT)", head)
    return taken, wv, (m.group(1) if m else "")

def grade(n, key, r, MY, NEED):
    tm = r["team"]; pos = r["pos"]
    left = [w for w in range(10, 18) if sched.get(tm, {}).get(w)]
    pts = round(f(r["ros_pg"]) * len(left), 1)
    g_val = min(pts / 100, 1) * 30
    # --- fit to THIS team
    fit_why = []; g_fit = 0.0
    hit = [nd for nd in NEED if pos in nd[0]]
    if hit:
        g_fit += 10; sw = sorted({w for nd in hit for w in nd[1]}); plays = [w for w in sw if sched.get(tm, {}).get(w)]
        if sw and len(plays) == len(sw): g_fit += 2
        fit_why.append("Fills your missing piece: " + "; ".join(nd[2] for nd in hit) + (f" (short Weeks {', '.join(map(str, sw))}" + ("; he plays all of them)" if sw and len(plays) == len(sw) else ")") if sw else ""))
    pg = lambda nm: f((ftn.get((n, norm(nm))) or {}).get("ros_pg"))
    flex = ("RB", "WR", "TE")
    same = [m for m in MY if m["pos"] == pos and m["status"] not in OUTST]
    starters = [m for m in MY if m["slot"] not in ("BN", "IR") and m["pos"] in flex and m["status"] not in OUTST]
    pool = [m for m in starters if m["pos"] == pos] or [m for m in starters]
    if pool:
        rep = min(pool, key=lambda m: pg(m["name"])); rp = pg(rep["name"]); cp = f(r["ros_pg"])
        gain = (cp - rp) / rp if rp > 0 else 1.0
        g_fit += max(0, min(gain / 0.30, 1)) * 10
        fit_why.append(f"vs your weakest {pos if pool[0]['pos'] == pos else 'flex'} starter {rep['name']} ({rp:.1f} a game): {'+' if gain >= 0 else ''}{gain * 100:.0f}%" + (" - clears your 15% bar" if gain >= .15 else " - under your 15% bar"))
    bench = [m for m in same if m["slot"] == "BN"]
    g_fit += 5 if not bench else 2.5 if len(bench) == 1 else 0
    if len(bench) <= 1: fit_why.append(f"Depth: {len(bench)} healthy {pos} on your bench")
    U = sorted(use.get(key, []))[-3:]
    o = [u[1] for u in U]; s = [round((u[2] or 0) * 100) for u in U]
    g_work = 0.0
    if len(U) == 3:
        do = (o[2] - o[0]) / max(o[0], 3); ds = (s[2] - s[0]) / 100
        g_work = max(0, min(1, 0.5 * max(0, do) + 1.5 * max(0, ds) + (0.25 if o[2] >= 10 else 0))) * 15
    opp = [(w, sched.get(tm, {}).get(w)) for w in (15, 16, 17)]
    rk = [rank.get((op, pos)) for w, op in opp if op and rank.get((op, pos))]
    avg_rk = sum(rk) / len(rk) if rk else 16.5
    g_play = (32 - avg_rk) / 31 * 15
    wp = winpct(tm); g_team = (wp if wp is not None else .5) * 5
    nt = notes["players"].get(key, {})
    g_path = (6 if nt.get("coach") else 0) + (4 if nt.get("star") else 0)
    inj = INJ.get(key); hurt = inj and inj[0] >= last_week and inj[1] in ("Out", "Doubtful")
    total = max(0, round(g_val + g_fit + g_work + g_play + g_team + g_path - (10 if hurt else 0)))
    why = []
    why.append(f"Ratcliffe: {pts:.0f} pts rest of season in {LEAGUES[n]} scoring ({r['ros_pg']} a game x {len(left)} games)")
    if hurt: why.append(f"Injury: {inj[1]} ({inj[2]}) on the Week {inj[0]} report - minus 10")
    why += fit_why
    if len(U) == 3: why.append(f"Workload last 3 games: touches {' > '.join(str(int(x)) for x in o)}, snaps {' > '.join(str(x) + '%' for x in s)}")
    if nt.get("coach"): why.append(f"Coach: {nt['coach']}")
    if nt.get("star"): why.append(f"Path: {nt['star']}")
    why.append("Playoffs: " + ", ".join(f"W{w} {op or 'BYE'}" + (f" ({rank.get((op, pos))})" if op and rank.get((op, pos)) else "") for w, op in opp))
    if wp is not None: why.append(f"Team {tm} {REC[tm]}")
    return dict(name=r["name"], team=tm, pos=pos, pts=pts, grade=total,
                parts=dict(value=round(g_val), fit=round(g_fit), workload=round(g_work), playoffs=round(g_play), team=round(g_team), path=g_path),
                why=why, use=dict(touches=o, snaps=s, weeks=[u[0] for u in U]))

out = {"built": datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%a %b %-d %Y %-I:%M %p PT"),
       "sources": {"ratcliffe_read": read_pt, "nflverse_through_week": last_week,
                   "standings": STAND_ASOF, "rank_note": "rank 1 = that defense gives up the most points to the position this season (PPR)"},
       "leagues": {}}
for n in LEAGUES:
    taken, wv, rpt = taken_and_waivers(n)
    MY, NEED = my_roster(n), needs(n)
    rows = []
    for (lg, key), r in ftn.items():
        if lg != n or key in taken: continue
        if f(r["ros_pg"]) < 4: continue
        g = grade(n, key, r, MY, NEED)
        lv = LIVE["status"].get(f"{n}|{key}")
        if lv: g["status"] = ("Waivers until " + lv[3:-1] if lv.startswith("W (") else "Free agent" if lv == "FA" else lv) + " (Yahoo live " + LIVE["checked"] + ")"
        else: g["status"] = (("Waivers until " + wv[key]) if key in wv else "Free agent") + f" (per {rpt} read - confirm live)"
        rows.append(g)
    rows.sort(key=lambda g: -g["grade"])
    out["leagues"][str(n)] = {"read": rpt, "top": rows[:5], "needs": [nd[2] + (f" (short Weeks {', '.join(map(str, nd[1]))})" if nd[1] else "") for nd in NEED],
                              "pieces_built": PCHK.get("built", "")}
json.dump(out, open(OUT, "w"), indent=1)
for n, L in out["leagues"].items():
    print("DK" + n, L["read"]); [print("  ", g["grade"], g["name"], g["pos"], g["team"], g["pts"], g["parts"], g["status"]) for g in L["top"]]
