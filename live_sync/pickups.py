"""Dark Knight - TOP 5 PICKUPS FOR EACH TEAM (Dom, Nov 9 2026).
  "a section on DK Live with top 5 pickups moving forward and why, potential points rest of season, and a grade on a scale to 100"
  "I want this set up for each team, they all have different needs and requirements"
  "updated three times a day and notified of changes ... up to five players, DEF, or kickers for each team. Check with my experts
   to confirm potential. Don't exclude anyone based on that, just note it."

For each league: every RB / WR / TE / K / DEF NOT on a roster in that league (Yahoo read, dk<n>_rosters_live.txt) is graded for
Dom's team there; the top 5 are kept (kickers only where the league has a K slot - DK III has none).

POTENTIAL POINTS (rest of season, already in that league's scoring):
  RB/WR/TE - Ratcliffe's rest-of-season points per game x games his team has left in Weeks 10-17 (dispatch_out/ftn_scored.csv)
  K / DEF  - Ratcliffe has no rest-of-season numbers for them, so Mike Clay's Week 10-17 lines (dispatch_out/clay_scored.csv)

GRADE (0-100), built for THIS team:
  value     30  potential points vs a full-marks line (100 for RB/WR/TE, 80 for DEF, 70 for K)
  fit       25  fills an OPEN Missing Piece or a new gap at his position (10, +2 if he plays in the short weeks), beats the man
                he'd replace on Dom's roster (up to 10 at +30%; Dom's bar is +15%), depth (5 with no healthy bench man there,
                2.5 with one; K/DEF: 5 if Dom's starter is on bye in Weeks 10-11, hurt, or missing)
  workload  15  carries+targets and snap share, last 3 games played, rising = more (K/DEF: 7.5, not measured)
  playoffs  15  Weeks 15-17 matchups: opponents' points allowed to his position (RB/WR/TE); for DEF and K when the schedule
                file carries this season's scores, opponents' points scored (DEF, fewer = better) / allowed (K, more = better),
                otherwise 7.5
  team       5  his NFL team's win percentage
  path      10  a coach on record about a bigger role (6), the starter ahead of him fading or hurt (4) - live_sync/pickup_notes.json
  Out or Doubtful on the latest injury report: minus 10.
EXPERT CHECK (noted, never used to drop anyone): each expert's number for him vs the man he'd replace, same expert, same scoring -
  Ratcliffe (rest of season per game), Clay (Weeks 10-17 per game), Koerner, Vegas and RotoBaller (their current week).

Usage: python3 live_sync/pickups.py <nflverse_dir> <out.json> [live_status.json]
live_status.json (optional) = {"checked": "<when>", "status": {"<league>|<key>": "W (Nov 11)" | "FA"}} from a live Yahoo search.
Without it the status comes from the roster read, labelled "confirm live" (Yahoo puts every man whose game has been played on
waivers until Wednesday, which the roster read does not show).
"""
import csv, json, re, sys, os, collections, datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NFL = sys.argv[1]; OUT = sys.argv[2]
LIVE = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {"checked": "", "status": {}}
SKILL = ("RB", "WR", "TE"); ALLPOS = SKILL + ("K", "DST")
LEAGUES = {1: "DK I", 2: "DK II", 3: "DK III", 4: "DK IV"}
ME = {1: 2, 2: 7, 3: 2, 4: 6}          # Dom's team id in each league (same map as the Yahoo readers)
OUTST = ("O", "IR", "IR-R", "NA", "SUSP", "PUP", "D")
TEAMNAME = {"ARI": "Cardinals", "ATL": "Falcons", "BAL": "Ravens", "BUF": "Bills", "CAR": "Panthers", "CHI": "Bears", "CIN": "Bengals",
    "CLE": "Browns", "DAL": "Cowboys", "DEN": "Broncos", "DET": "Lions", "GB": "Packers", "HOU": "Texans", "IND": "Colts", "JAX": "Jaguars",
    "KC": "Chiefs", "LV": "Raiders", "LAC": "Chargers", "LA": "Rams", "MIA": "Dolphins", "MIN": "Vikings", "NE": "Patriots", "NO": "Saints",
    "NYG": "Giants", "NYJ": "Jets", "PHI": "Eagles", "PIT": "Steelers", "SF": "49ers", "SEA": "Seahawks", "TB": "Buccaneers", "TEN": "Titans", "WAS": "Commanders"}
NAME2TM = {v.lower(): k for k, v in TEAMNAME.items()}
FIX = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX"}

def norm(n):
    n = n.replace("-", " ").lower().replace(".", "").replace("'", "").replace("’", "")
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return re.sub(r"[^a-z ]", "", re.sub(r"\s+", " ", n)).strip()
def tm_of(team, name=""):
    t = FIX.get(team.upper(), team.upper())
    if t in TEAMNAME: return t
    for w in norm(name).split():
        if w in NAME2TM: return NAME2TM[w]
    return t
def pkey(name, pos, team):      # one key for every source: "jax def" for a defense, the normalized name otherwise
    return (tm_of(team, name) + " def").lower() if pos in ("DST", "DEF") else norm(name)
f = lambda v: float(v) if v not in ("", None, "NA") else 0.0

notes = json.load(open(os.path.join(ROOT, "live_sync", "pickup_notes.json")))
def _ok(p):
    try: return os.path.exists(p) and open(p).readline().startswith("game_id,season")
    except Exception: return False
GAMES = os.path.join(NFL, "games.csv") if _ok(os.path.join(NFL, "games.csv")) else os.path.join(ROOT, "system", "src", "role_watch", "data", "games.csv")

# ---- schedule, records, team scoring
sched = collections.defaultdict(dict); wl = collections.defaultdict(lambda: [0, 0, 0]); pf = collections.defaultdict(list); pa = collections.defaultdict(list); scored = 0
for g in csv.DictReader(open(GAMES)):
    if g["season"] != "2026" or g["game_type"] != "REG": continue
    w = int(g["week"]); h, a = g["home_team"], g["away_team"]; sched[h][w] = a; sched[a][w] = h
    if g["home_score"] not in ("", "NA"):
        hs, as_ = int(float(g["home_score"])), int(float(g["away_score"])); scored += 1
        pf[h].append(hs); pa[h].append(as_); pf[a].append(as_); pa[a].append(hs)
        if hs > as_: wl[h][0] += 1; wl[a][1] += 1
        elif as_ > hs: wl[a][0] += 1; wl[h][1] += 1
        else: wl[h][2] += 1; wl[a][2] += 1
if scored >= 100:
    REC = {t: f"{w}-{l}" + (f"-{d}" if d else "") for t, (w, l, d) in wl.items()}; STAND_ASOF = f"nflverse schedule, {scored} games scored"
else:
    REC, STAND_ASOF = dict(notes["standings"]["records"]), notes["standings"]["asof"]
def winpct(tm):
    r = REC.get(tm)
    if not r: return None
    p = [int(x) for x in r.split("-")]; w, l, t = (p + [0])[:3]
    return (w + t / 2) / max(1, w + l + t)

# ---- usage, matchups, injuries from nflverse
stats = [x for x in csv.DictReader(open(os.path.join(NFL, "stats_player_week_2026.csv"))) if x["season_type"] == "REG"]
snaps = {}
for s in csv.DictReader(open(os.path.join(NFL, "snap_counts_2026.csv"))):
    if s["game_type"] == "REG": snaps[(s["game_id"], norm(s["player"]))] = f(s["offense_pct"])
last_week = max(int(x["week"]) for x in stats)
gms = collections.defaultdict(set)
for x in stats: gms[x["opponent_team"]].add(x["game_id"])
allow = collections.defaultdict(float)
for x in stats:
    if x["position"] in SKILL: allow[(x["opponent_team"], x["position"])] += f(x["fantasy_points_ppr"])
rank = {}
for pos in SKILL:
    ds = sorted({d for (d, p) in allow if p == pos}, key=lambda d: -allow[(d, pos)] / max(1, len(gms[d])))
    for i, d in enumerate(ds): rank[(d, pos)] = i + 1
if scored >= 100:
    for i, t in enumerate(sorted(pf, key=lambda t: sum(pf[t]) / len(pf[t]))): rank[(t, "DST")] = i + 1
    for i, t in enumerate(sorted(pa, key=lambda t: -sum(pa[t]) / len(pa[t]))): rank[(t, "K")] = i + 1
use = collections.defaultdict(list)
for x in stats:
    if x["position"] not in SKILL: continue
    o = f(x["carries"]) + f(x["targets"]); sp = snaps.get((x["game_id"], norm(x["player_display_name"])))
    if o > 0 or (sp or 0) > 0: use[norm(x["player_display_name"])].append((int(x["week"]), o, sp))
INJ = {}
try:
    for x in csv.DictReader(open(os.path.join(NFL, "injuries_2026.csv"))):
        if x.get("game_type", "REG") == "REG": INJ[norm(x["full_name"])] = (int(x["week"]), x["report_status"] or "", x["report_primary_injury"] or "")
except Exception: pass

# ---- the experts, every one already scored in each league's rules
def load(fn):
    try: return list(csv.DictReader(open(os.path.join(ROOT, "dispatch_out", fn))))
    except Exception: return []
EXP = {}; READ = {}
def slot(r):
    pos = "DST" if r["pos"] in ("DEF", "DST", "D/ST") else r["pos"]
    if pos not in ALLPOS: return None
    return EXP.setdefault((int(r["lg"]), pkey(r["name"], pos, r["team"])), {"_name": r["name"], "_team": tm_of(r["team"], r["name"]), "_pos": pos})
for r in load("ftn_scored.csv"):
    d = slot(r)
    if d is None: continue
    if f(r["ros_pg"]) > 0: d["Ratcliffe"] = f(r["ros_pg"])
    READ["Ratcliffe"] = r["read_pt"]
for r in load("clay_scored.csv"):
    d = slot(r)
    if d is None: continue
    wks = {w: f(r.get(f"w{w}")) for w in range(10, 18) if r.get(f"w{w}") not in ("", None)}
    played = [v for v in wks.values() if v]
    if played: d["_clay_wks"] = wks; d["Clay"] = round(sum(played) / len(played), 2)
    READ["Clay"] = r["read"]
for fn, ex, rd in (("koerner_scored.csv", "Koerner", "read_pt"), ("vegas_scored.csv", "Vegas", "read"), ("rotoballer_scored.csv", "RotoBaller", "read")):
    for r in load(fn):
        d = slot(r)
        if d is None: continue
        if f(r["wk"]) > 0: d[ex] = f(r["wk"])
        READ[ex] = r.get(rd, "")
EXPERTS = ("Ratcliffe", "Clay", "Koerner", "Vegas", "RotoBaller")
SPAN = {"Ratcliffe": "rest of season", "Clay": "Wks 10-17", "Koerner": "this week", "Vegas": "this week", "RotoBaller": "this week"}

# ---- Missing Pieces (open needs) and the league
PIECE_DEF = json.load(open(os.path.join(ROOT, "system", "cand", "missing_pieces.json")))["leagues"]
try: PCHK = json.load(open(os.path.join(ROOT, "dispatch_out", "pieces_check.json")))
except Exception: PCHK = {"leagues": {}}
def needs(n):
    lab = LEAGUES[n]; out = []; defs = {d["piece"]: d for d in PIECE_DEF.get(lab, [])}
    for pc in PCHK["leagues"].get(lab, {}).get("pieces", []):
        if pc.get("status") == "open" and pc["piece"] in defs:
            out.append(([("DST" if p == "DEF" else p) for p in defs[pc["piece"]]["pos"]], pc.get("short", []), pc["piece"]))
    for g in PCHK["leagues"].get(lab, {}).get("gaps", []): out.append((["DST" if g["pos"] == "DEF" else g["pos"]], g.get("weeks", []), f"new gap at {g['pos']}"))
    return out
def league(n):
    L = open(os.path.join(ROOT, "yahoo_drop", "scout", f"dk{n}_rosters_live.txt")).read().splitlines()
    m = re.search(r"read (.+?PT)", L[0]); taken = set(); mine = []; has_k = False
    for l in L[1:]:
        p = l.split("|")
        if len(p) < 6: continue
        pos = "DST" if p[4] == "DEF" else p[4]
        key = pkey(p[2], pos, p[3]); taken.add(key); has_k = has_k or p[1] == "K"
        if p[0] == str(ME[n]): mine.append(dict(slot=p[1], name=p[2], pos=pos, key=key, team=tm_of(p[3], p[2]), status=p[5].strip()))
    W = open(os.path.join(ROOT, "yahoo_drop", "scout", f"dk{n}_waivers.txt")).read().splitlines()
    wv = {}
    for t in (W[1].split("|") if len(W) > 1 else []):
        if "/" in t:
            a, b = t.split("/", 1); k = norm(a)
            wv[(NAME2TM[k].lower() + " def") if k in NAME2TM else k] = b
    return taken, mine, has_k, wv, (m.group(1) if m else "")

def grade(n, key, d, MY, NEED):
    pos, tm, name = d["_pos"], d["_team"], d["_name"]; P = "DEF" if pos == "DST" else pos
    left = [w for w in range(10, 18) if sched.get(tm, {}).get(w)]
    if pos in SKILL:
        if not d.get("Ratcliffe"): return None
        pts = round(d["Ratcliffe"] * len(left), 1); pts_src = f"Ratcliffe {d['Ratcliffe']:.2f} a game x {len(left)} games"; full = 100; src = "Ratcliffe"
    else:
        cw = d.get("_clay_wks")
        if not cw: return None
        pts = round(sum(cw.values()), 1); pts_src = f"Clay's Week 10-17 lines, {len([v for v in cw.values() if v])} games"
        full = 80 if pos == "DST" else 70; src = "Clay"
    if pts <= 0: return None
    g_val = min(pts / full, 1) * 30          # K / DEF: replaced below by points over Dom's own starter (they are easy to replace)
    fit_why, g_fit = [], 0.0
    hit = [nd for nd in NEED if pos in nd[0]]
    if hit:
        g_fit += 10; sw = sorted({w for nd in hit for w in nd[1]}); plays = [w for w in sw if sched.get(tm, {}).get(w)]
        allp = bool(sw) and len(plays) == len(sw); g_fit += 2 if allp else 0
        fit_why.append("Fills your missing piece: " + "; ".join(nd[2] for nd in hit)
                       + ((f" (short Weeks {', '.join(map(str, sw))}; " + ("he plays all of them)" if allp else "he misses some)")) if sw else ""))
    healthy = lambda m: m["status"] not in OUTST
    if pos in SKILL:
        starters = [m for m in MY if m["slot"] not in ("BN", "IR") and m["pos"] in SKILL and healthy(m)]
        same = [m for m in starters if m["pos"] == pos]; pool = same or starters
        bench = [m for m in MY if m["pos"] == pos and m["slot"] == "BN" and healthy(m)]
        g_fit += 5 if not bench else 2.5 if len(bench) == 1 else 0
        if len(bench) <= 1: fit_why.append(f"Depth: {len(bench)} healthy {pos} on your bench")
        role = f"weakest {pos} starter" if same else "weakest flex starter"
    else:
        pool = [m for m in MY if m["pos"] == pos]; role = f"{P}"
        if pool:
            st = pool[0]; stm = st["key"].split()[0].upper() if pos == "DST" else st["team"]
            soon = [w for w in (10, 11) if not sched.get(stm, {}).get(w)]
            if soon or not healthy(st): g_fit += 5; fit_why.append(f"Your {P} {st['name']} " + (f"is on bye Week {soon[0]}" if soon else "is hurt"))
        else: g_fit += 5; fit_why.append(f"You have no {P} on the roster")
    rep = None
    if pool:
        rep = dict(min(pool, key=lambda m: (EXP.get((n, m["key"])) or {}).get(src, 0)))
        if pos == "DST": rep["name"] = TEAMNAME.get(rep["key"].split()[0].upper(), rep["name"]) + " DEF"
        rp = (EXP.get((n, rep["key"])) or {}).get(src, 0); cp = d.get(src, 0)
        if rp > 0 and cp > 0:
            gain = (cp - rp) / rp; g_fit += max(0, min(gain / 0.30, 1)) * 10
            fit_why.append(f"vs your {role} {rep['name']} ({src} {rp:.1f} a game vs {cp:.1f}): {'+' if gain >= 0 else ''}{gain * 100:.0f}%"
                           + (" - clears your 15% bar" if gain >= .15 else " - under your 15% bar"))
    if pos not in SKILL:
        rw = sum(((EXP.get((n, rep["key"])) or {}).get("_clay_wks") or {}).values()) if rep else 0
        g_val = min(max(0, pts - rw) / 30, 1) * 30 if rep else min(pts / full, 1) * 30
        if rep: fit_why.insert(0, f"{pts - rw:+.0f} pts over your {P} {rep['name']} in Weeks 10-17 (Value: full marks at +30)")
    U = sorted(use.get(key, []))[-3:]; o = [u[1] for u in U]; s = [round((u[2] or 0) * 100) for u in U]
    if pos in SKILL:
        g_work = 0.0
        if len(U) == 3:
            do = (o[2] - o[0]) / max(o[0], 3); dsn = (s[2] - s[0]) / 100
            g_work = max(0, min(1, 0.5 * max(0, do) + 1.5 * max(0, dsn) + (0.25 if o[2] >= 10 else 0))) * 15
    else: g_work = 7.5
    opp = [(w, sched.get(tm, {}).get(w)) for w in (15, 16, 17)]
    rk = [rank.get((op, pos)) for w, op in opp if op and rank.get((op, pos))]
    g_play = (32 - (sum(rk) / len(rk))) / 31 * 15 if rk else 7.5
    wp = winpct(tm); g_team = (wp if wp is not None else .5) * 5
    nt = notes["players"].get(key, {}); g_path = (6 if nt.get("coach") else 0) + (4 if nt.get("star") else 0)
    inj = INJ.get(key); hurt = bool(inj and inj[0] >= last_week and inj[1] in ("Out", "Doubtful"))
    total = max(0, min(100, round(g_val + g_fit + g_work + g_play + g_team + g_path - (10 if hurt else 0))))
    # expert check - noted, never used to drop anyone
    xc, agree, had = [], 0, 0
    for ex in EXPERTS:
        cv = d.get(ex); rv = (EXP.get((n, rep["key"])) or {}).get(ex) if rep else None
        if cv is None: xc.append(dict(ex=ex, txt="no number for him", ok=None, read=READ.get(ex, ""))); continue
        if rv:
            had += 1; up = cv > rv; agree += up
            xc.append(dict(ex=ex, txt=f"{cv:.1f} vs {rep['name']} {rv:.1f} ({SPAN[ex]})", ok=up, read=READ.get(ex, "")))
        else: xc.append(dict(ex=ex, txt=f"{cv:.1f} ({SPAN[ex]}; no number for {rep['name'] if rep else 'your man'})", ok=None, read=READ.get(ex, "")))
    verdict = (f"{agree} of {had} experts have him ahead of {rep['name']}" if had else f"no expert has numbers for both him and {rep['name']}") if rep else "nobody on your roster to compare"
    why = [f"{pts:.0f} pts rest of season in {LEAGUES[n].replace('DK ', 'DK').replace('III', '3').replace('II', '2').replace('IV', '4').replace('I', '1')} scoring ({pts_src})"]
    if hurt: why.append(f"Injury: {inj[1]} ({inj[2]}) on the Week {inj[0]} report - minus 10")
    why += fit_why
    if pos in SKILL and len(U) == 3: why.append(f"Workload last 3 games: touches {' > '.join(str(int(x)) for x in o)}, snaps {' > '.join(str(x) + '%' for x in s)}")
    if nt.get("coach"): why.append(f"Coach: {nt['coach']}")
    if nt.get("star"): why.append(f"Path: {nt['star']}")
    why.append("Playoffs: " + ", ".join(f"W{w} {op or 'BYE'}" + (f" (#{rank.get((op, pos))})" if op and rank.get((op, pos)) else "") for w, op in opp)
               + ("" if rk else " (matchup ranks need this season's scores - scored even)"))
    if wp is not None: why.append(f"{tm} {REC[tm]}")
    return dict(key=key, name=(TEAMNAME.get(tm, tm) + " DEF") if pos == "DST" else name, team=tm, pos=P,
                pts=pts, grade=total, parts=dict(value=round(g_val), fit=round(g_fit), workload=round(g_work), playoffs=round(g_play), team=round(g_team), path=g_path),
                why=why, experts=dict(verdict=verdict, agree=agree, of=had, lines=xc), replaces=rep["name"] if rep else "")

out = {"built": datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%a %b %-d %Y %-I:%M %p PT"),
       "sources": {"ratcliffe_read": READ.get("Ratcliffe", ""), "expert_reads": READ, "nflverse_through_week": last_week, "standings": STAND_ASOF,
                   "rank_note": "#1 = best matchup: the defense that gives up the most to his position (RB/WR/TE), the offense that scores the least (DEF), the defense that allows the most points (K)"},
       "leagues": {}}
for n in LEAGUES:
    taken, MY, has_k, wv, rpt = league(n); NEED = needs(n); rows = []
    for (lg, key), d in EXP.items():
        if lg != n or key in taken: continue
        if d["_pos"] == "K" and not has_k: continue
        g = grade(n, key, d, MY, NEED)
        if not g: continue
        lv = LIVE["status"].get(f"{n}|{key}")
        if lv: g["status"] = ("Waivers until " + lv[3:-1] if lv.startswith("W (") else "Free agent" if lv == "FA" else lv) + " (Yahoo live " + LIVE["checked"] + ")"
        else: g["status"] = (("Waivers until " + wv[key]) if key in wv else "Free agent") + f" (per {rpt} read - confirm live)"
        rows.append(g)
    rows.sort(key=lambda g: -g["grade"])
    out["leagues"][str(n)] = {"read": rpt, "top": rows[:5], "needs": [nd[2] + (f" (short Weeks {', '.join(map(str, nd[1]))})" if nd[1] else "") for nd in NEED],
                              "pieces_built": PCHK.get("built", ""), "kicker_slot": has_k,
                              "pool": {g["key"]: [g["grade"], g["name"]] for g in rows},     # every man still available, for the change notes
                              "best": {p: next(({"name": g["name"], "grade": g["grade"]} for g in rows if g["pos"] == p), None) for p in ("RB", "WR", "TE", "K", "DEF")}}
json.dump(out, open(OUT, "w"), indent=1)
for n, L in out["leagues"].items():
    print("DK" + n, L["read"], "| best K", L["best"]["K"], "| best DEF", L["best"]["DEF"])
    for g in L["top"]: print("  ", g["grade"], g["name"], g["pos"], g["team"], g["pts"], g["parts"], "|", g["experts"]["verdict"])
