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
  workload  15  carries+targets and snap share, last 3 games played, rising = more; OR (Nov 11) already holding the top role -
                WR1/TE1 by targets (30%+) or the lead back (45%+ of carries, no split) = full 15, a clear #2 = 9; the higher counts (K/DEF: 7.5).
                Nov 12: no top-role credit when his snaps fell 10+ points over 3 games; at most 7 when he's on this week's injury report
  playoffs  15  Weeks 15-17 matchups: opponents' points allowed to his position (RB/WR/TE); for DEF and K when the schedule
                file carries this season's scores, opponents' points scored (DEF, fewer = better) / allowed (K, more = better),
                otherwise 7.5
  team       5  his NFL team's win percentage
  path      10  a coach on record about a bigger role (6), the starter ahead of him fading or hurt (4) - live_sync/pickup_notes.json
  Out or Doubtful on the latest injury report: minus 10.
KIND (Nov 11, Dom): BUILD = Clay has him 12+ a game in Weeks 15-17 (this league's scoring); CLIMBING = 9.5+ there and his snaps
  rose 10+ points over his last 3 games; 1-WEEK = a win-now fill (11+ this week, under 10 in the playoffs). Flags: split backfield,
  his QB is out, hurt. BUILD and CLIMBING lead the top five; a flagged man never takes a top-five spot from a clean one.
TEAM (Nov 11, Dom): last game's QB (flagged when he's out), his rank in his position group by targets (RB: carries, split flagged),
  the offense's points a game (season and last 3), this week's opponent and matchup rank.
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

import unicodedata as _ud   # Nov 12: accents stripped - "Audric Estimé" showed as a free agent while rostered as "Audric Estime"
def norm(n):
    n = "".join(c for c in _ud.normalize("NFKD", str(n)) if not _ud.combining(c))
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
    if s["game_type"] == "REG":
        snaps[(s["game_id"], norm(s["player"]))] = f(s["offense_pct"])
        # Nov 12: the snap file uses legal names (Zonovan Knight) where the stats use the playing name (Bam Knight) -
        # also keep game + team + position + last name, used only when it points at one man
        _sk = (s["game_id"], s["team"], s["position"], norm(s["player"]).split()[-1] if norm(s["player"]) else "")
        snaps[_sk] = None if _sk in snaps else f(s["offense_pct"])
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
    if sp is None and norm(x["player_display_name"]):
        sp = snaps.get((x["game_id"], x["team"], x["position"], norm(x["player_display_name"]).split()[-1]))
    if o > 0 or (sp or 0) > 0: use[norm(x["player_display_name"])].append((int(x["week"]), o, sp))
INJ = {}
try:
    for x in csv.DictReader(open(os.path.join(NFL, "injuries_2026.csv"))):
        if x.get("game_type", "REG") == "REG": INJ[norm(x["full_name"])] = (int(x["week"]), x["report_status"] or "", x["report_primary_injury"] or "")
except Exception: pass
# Nov 9 10:11 AM (Dom: "these need to be pickups that meet our criteria"): a man on injured reserve, PUP, NFI or suspended is not a
# Diamond - De'Von Achane (IR, ACL surgery, season over) graded HOT in three leagues because only this week's Out/Doubtful counted.
# Sleeper's status is read fresh by every build (feeds/sleeper_injuries.json). He comes back the moment the status clears.
SIDELINED = {}
try:
    for _v in (json.load(open(os.path.join(ROOT, "feeds", "sleeper_injuries.json"))).get("players") or {}).values():
        if isinstance(_v, dict) and str(_v.get("inj") or "").upper() in ("IR", "PUP", "NFI", "SUS", "SUSPENDED", "DNR"):
            SIDELINED[norm(_v.get("name", ""))] = f"{_v['inj']}" + (f" - {_v['inj_body']}" if _v.get("inj_body") else "") + (f" ({_v['inj_notes']})" if _v.get("inj_notes") else "")
except Exception as _e: print("sidelined list skipped:", str(_e)[:100])

# ---- TEAM FIRST (Dom, Nov 10-11: "you have to look at the whole team ... who the quarterback is and who the players are ... is this
# guy a W1, a W2, a W3, a W4 ... the defense he faces"): every Diamond carries his team's quarterback (flagged when the starter is
# out), where he sits in his own position group by targets (RB: share of the backfield's carries - a split backfield is flagged),
# the offense's scoring (season and last 3 games), and this week's matchup rank.
RECENT = sorted({int(x["week"]) for x in stats})[-3:]
QB = {}
for tm_ in {x["team"] for x in stats if x.get("team")}:
    qs = [x for x in stats if x.get("team") == tm_ and x["position"] == "QB" and f(x.get("attempts")) > 0]
    if not qs: continue
    lw = max(int(x["week"]) for x in qs)
    q = max((x for x in qs if int(x["week"]) == lw), key=lambda x: f(x["attempts"]))
    nm = q["player_display_name"]; k_ = norm(nm); inj_ = INJ.get(k_)
    out_ = SIDELINED.get(k_) or (f"{inj_[1]} ({inj_[2]})" if inj_ and inj_[0] >= last_week and inj_[1] in ("Out", "Doubtful") else "")
    QB[tm_] = dict(name=nm, out=out_, starts=len({x["week"] for x in qs if x["player_display_name"] == nm and f(x["attempts"]) >= 15}))
GRP = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0]))   # (team, pos) -> player -> [targets, carries] last 3 weeks
for x in stats:
    if x["position"] in SKILL and int(x["week"]) in RECENT and x.get("team"):
        g_ = GRP[(x["team"], x["position"])][norm(x["player_display_name"])]; g_[0] += f(x["targets"]); g_[1] += f(x["carries"])
DNAME = {norm(x["player_display_name"]): x["player_display_name"] for x in stats}
def role(key, tm, pos):
    G = GRP.get((tm, pos)) or {}
    if not G or key not in G: return None
    if pos == "RB":
        tot = sum(v[1] for v in G.values()) or 1; order = sorted(G, key=lambda k: -G[k][1]); me_ = G[key][1] / tot
        other = [k for k in order if k != key]; o_ = G[other[0]][1] / tot if other else 0
        split = me_ >= .25 and o_ >= .30 and abs(me_ - o_) < .30
        lab = (f"RB{order.index(key) + 1}: {me_ * 100:.0f}% of the carries last {len(RECENT)} games"
               + (f" - SPLIT with {DNAME.get(other[0], other[0])} ({o_ * 100:.0f}%)" if split else ""))
        return dict(rank=order.index(key) + 1, share=round(me_, 2), split=split, txt=lab)
    tot = sum(v[0] for v in G.values()) or 1; order = sorted(G, key=lambda k: -G[k][0])
    return dict(rank=order.index(key) + 1, share=round(G[key][0] / tot, 2), split=False,
                txt=f"{pos}{order.index(key) + 1} on his team: {G[key][0] / tot * 100:.0f}% of the {pos} targets last {len(RECENT)} games")
ROLE_OF = role                                         # grade() has its own local 'role' text
PPG = {t: sum(v) / len(v) for t, v in pf.items() if v}; L3 = {t: sum(v[-3:]) / len(v[-3:]) for t, v in pf.items() if v}
ORANK = {t: i + 1 for i, t in enumerate(sorted(PPG, key=lambda t: -PPG[t]))}
def team_line(key, tm, pos):
    q = QB.get(tm); r = role(key, tm, pos) if pos in SKILL else None; opp = sched.get(tm, {}).get(START)
    bits = {}
    if q: bits["qb"] = (f"QB {q['name']} is OUT - {q['out']}; a backup starts" if q["out"] else f"QB last game {q['name']}" + (f" ({q['starts']} starts)" if q["starts"] < 4 else ""))
    if r: bits["role"] = r["txt"]
    if tm in PPG: bits["offense"] = f"offense {PPG[tm]:.1f} a game (#{ORANK[tm]} of {len(PPG)}), last 3 games {L3[tm]:.1f}" + (" - falling" if L3[tm] < PPG[tm] - 3 else " - rising" if L3[tm] > PPG[tm] + 3 else "")
    if opp: bits["week"] = f"Week {START} vs {opp}" + (f" (#{rank[(opp, pos)]} matchup)" if rank.get((opp, pos)) else "")
    else: bits["week"] = f"Week {START}: BYE"
    sh = []                                            # the one-line version for the row: "WR1 · QB Rodgers · vs CIN"
    if r: sh.append(("RB%d" % r["rank"] if pos == "RB" else f"{pos}{r['rank']}") + (" split" if r.get("split") else ""))
    if q: sh.append(("QB OUT" if q["out"] else "QB " + re.sub(r" (Jr\.?|Sr\.?|II|III|IV|V)$", "", q["name"]).split(" ")[-1]))
    sh.append(f"vs {opp}" if opp else "bye")
    bits["short"] = " · ".join(sh)
    return bits, r, q

# ---- the experts, every one already scored in each league's rules
def load(fn):
    try: return list(csv.DictReader(open(os.path.join(ROOT, "dispatch_out", fn))))
    except Exception: return []
EXP = {}; READ = {}
def slot(r):
    pos = "DST" if r["pos"] in ("DEF", "DST", "D/ST") else r["pos"]
    if pos not in ALLPOS: return None
    return EXP.setdefault((int(r["lg"]), pkey(r["name"], pos, r["team"])), {"_name": r["name"], "_team": tm_of(r["team"], r["name"]), "_pos": pos})
RATWK = {}   # Nov 12: Ratcliffe's THIS-WEEK number, for the checks line
for r in load("ftn_scored.csv"):
    if f(r.get("wk")) > 0 and r.get("pos") in ALLPOS: RATWK[(int(r["lg"]), pkey(r["name"], r["pos"], r["team"]))] = f(r["wk"])
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
# Nov 9 8:07 AM (Dom): every pickup is priced on the TOP 3 by accuracy (last graded week), not Ratcliffe alone - live_sync/panel.py.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from panel import Panel, NAME as PNAME, ROLES, PO_ROLES
PAN = Panel(ROOT)
START = PAN.start                                  # first week still ahead
# the expert check, listed by accuracy: the four forward sources in the panel's order, then the this-week-only experts by their own last grade
def _wk_only_order():
    try:
        M = json.load(open(sorted(__import__("glob").glob(os.path.join(ROOT, "dispatch_out", "meter_wk*.json")), key=lambda p: int(re.search(r"_wk(\d+)", p).group(1)))[-1]))
        A = (M.get("acc") or {}).get("src") or {}
    except Exception: A = {}
    def last(s):
        w = sorted((A.get(s) or {}).items(), key=lambda x: int(x[0])); return (w[-1][1][0], int(w[-1][0])) if w else (99, None)
    return sorted(("koerner", "vegas", "rotoballer"), key=lambda s: last(s)[0]), {s: last(s) for s in ("koerner", "vegas", "rotoballer")}
WKO, WKG = _wk_only_order()
# Nov 9 (Dom): the bar only decides MUST - 10% (was 15%); nobody is screened out by it, rising men still show HOT / STASH
MUSTBAR = .10
for (lg_, k_), (nm_, tm_, ps_) in PAN.meta.items():     # a man only Yahoo or Gotham sees still gets graded (Gotham is the early spotter)
    if ps_ in ALLPOS and (lg_, k_) not in EXP: EXP[(lg_, k_)] = {"_name": nm_, "_team": tm_, "_pos": ps_}
# Nov 12 (Dom: "Go"): a source that writes a short first name ("J. Croskey-Merritt") made a second, Yahoo-only copy of the man -
# priced on one source and shown as a free agent (the waiver list uses his full name). Fold each short name into the one full name it matches.
ABBR = {}
for (lg_, k_) in list(EXP):
    t_ = k_.split()
    if len(t_) < 2 or len(t_[0]) != 1: continue
    c_ = [k2 for (l2, k2) in EXP if l2 == lg_ and k2 != k_ and len(k2.split()[0]) > 1 and k2.split()[0][0] == t_[0] and k2.split()[1:] == t_[1:]]
    if len(c_) != 1: continue
    for kk, vv in EXP[(lg_, k_)].items():
        if kk[0] != "_": EXP[(lg_, c_[0])].setdefault(kk, vv)
    ABBR[(lg_, c_[0])] = k_; del EXP[(lg_, k_)]
XNAME = dict(PNAME, koerner="Koerner", vegas="Vegas", rotoballer="RotoBaller")
# Nov 9 8:55 AM: all seven are ranked together in the panel now - its order IS the list, most to least accurate
WKO = [x for x in WKO if x not in PAN.order]
EXPERTS = tuple(PAN.order) + tuple(WKO)
SPAN = {"ratcliffe": "rest of season", "clay": f"Wks {START}-17", "yahoo": f"Wks {START}-17", "gotham": "a game ahead", "koerner": "this week", "vegas": "this week", "rotoballer": "this week"}
XREAD = dict(ratcliffe=READ.get("Ratcliffe", ""), clay=READ.get("Clay", ""), yahoo=PAN.read.get("yahoo", ""), gotham=PAN.read.get("gotham", ""),
             koerner=READ.get("Koerner", ""), vegas=READ.get("Vegas", ""), rotoballer=READ.get("RotoBaller", ""))
def xval(n, key, ex):
    if ex in PAN.V and PAN.V[ex]:
        v = PAN.V[ex].get((n, key))
        return v if v is not None or (n, key) not in ABBR else PAN.V[ex].get((n, ABBR[(n, key)]))
    return (EXP.get((n, key)) or {}).get(XNAME[ex])
def xrank(ex):
    if ex in PAN.ranked:
        m = PAN.grades["miss"].get(ex); sw = (PAN.grades.get("src_weeks") or {}).get(ex) or PAN.grades["weeks"]
        wl = (f"Wks {sw[0]}-{sw[-1]}" if len(sw) > 1 else f"Wk {sw[0]}") if sw else ""
        return f"#{PAN.ranked.index(ex) + 1}" + (f" ({m:.2f} missed a player, {wl})" if m is not None and wl else "") + (f", Week {PAN.waiting[ex]} numbers only - not counted" if ex in PAN.waiting else "")
    if ex in PAN.order: return "not graded yet"
    g, w = WKG.get(ex, (99, None)); return "this week only" + (f" ({g:.2f} missed Wk {w})" if w else "")

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
    left = [w for w in range(START, 18) if sched.get(tm, {}).get(w)]
    avg, got = PAN.rate(n, key)
    if not avg: return None
    pts = round(avg * len(left), 1); full = 100 if pos in SKILL else 80 if pos == "DST" else 70
    pts_src = f"{PAN.label(list(got))} {avg:.2f} a game x {len(left)} games"   # Nov 12 (Dom): Ratcliffe decides - no average
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
    rep = None; gain = None
    if pool:
        rep = dict(min(pool, key=lambda m: PAN.rate(n, m["key"])[0] or 0))
        if pos == "DST": rep["name"] = TEAMNAME.get(rep["key"].split()[0].upper(), rep["name"]) + " DEF"
        cp, rp, both = PAN.compare(n, key, rep["key"])
        if rp and cp and rp > 0:
            gain = (cp - rp) / rp; g_fit += max(0, min(gain / 0.30, 1)) * 10
            fit_why.append(f"vs your {role} {rep['name']} ({PAN.label(both)}: {rp:.1f} a game vs {cp:.1f}): {'+' if gain >= 0 else ''}{gain * 100:.0f}%"
                           + (" - clears the 10% MUST bar" if gain >= MUSTBAR else " - under the 10% MUST bar"))
    if pos not in SKILL:
        rtm = (rep["key"].split()[0].upper() if pos == "DST" else rep["team"]) if rep else ""
        rw = (PAN.rate(n, rep["key"])[0] or 0) * len([w for w in range(START, 18) if sched.get(rtm, {}).get(w)]) if rep else 0
        g_val = min(max(0, pts - rw) / 30, 1) * 30 if rep else min(pts / full, 1) * 30
        if rep: fit_why.insert(0, f"{pts - rw:+.0f} pts over your {P} {rep['name']} in Weeks {START}-17 (Value: full marks at +30)")
    U = sorted(use.get(key, []))[-3:]; o = [u[1] for u in U]; s = [round((u[2] or 0) * 100) for u in U]
    if pos in SKILL:
        g_work = 0.0
        if len(U) == 3:
            do = (o[2] - o[0]) / max(o[0], 3); dsn = (s[2] - s[0]) / 100
            g_work = max(0, min(1, 0.5 * max(0, do) + 1.5 * max(0, dsn) + (0.25 if o[2] >= 10 else 0))) * 15
        # Nov 11 (Dom: Metcalf "only a 60"): a man who ALREADY holds the top role - WR1 / TE1 by targets, the lead back (not a split) -
        # gets full workload credit; the climb still scores for everyone else. The higher of the two counts.
        RW = ROLE_OF(key, tm, pos)
        if RW and not RW.get("split"):
            hold = 15 if RW["rank"] == 1 and RW["share"] >= (.45 if pos == "RB" else .30) else 9 if RW["rank"] <= 2 and RW["share"] >= .22 else 0
            if hold and len(U) and (s[-1] if s else 0) < 50: hold = min(hold, 9)          # top of a thin group but on the field under half the snaps
            # Nov 12 (Dom, Kincaid: "why were we going to use him?"): the top-role credit is for a role that is HOLDING. Snaps down
            # 10+ points over his last 3 games = the role is slipping, no credit for it; on this week's injury report = half credit
            if hold and len(s) >= 3 and s[0] - s[-1] >= 10: hold = 0
            inj_ = INJ.get(key)
            if hold and inj_ and inj_[0] >= START and inj_[1] in ("Questionable", "Doubtful", "Out"): hold = min(hold, 7)
            g_work = max(g_work, hold)
    else: g_work = 7.5
    opp = [(w, sched.get(tm, {}).get(w)) for w in (15, 16, 17)]
    rk = [rank.get((op, pos)) for w, op in opp if op and rank.get((op, pos))]
    g_play = (32 - (sum(rk) / len(rk))) / 31 * 15 if rk else 7.5
    wp = winpct(tm); g_team = (wp if wp is not None else .5) * 5
    nt = notes["players"].get(key, {}); g_path = (6 if nt.get("coach") else 0) + (4 if nt.get("star") else 0)
    inj = INJ.get(key); hurt = bool(inj and inj[0] >= last_week and inj[1] in ("Out", "Doubtful"))
    # Nov 11 (Dom): "a player that's going to give me more than 12 points ... sometime during the playoffs, or working his way up
    # to that point with the additional workload" - and keep win-now rentals separate from build players.
    TB, RL, QQ = team_line(key, tm, pos)
    cw = d.get("_clay_wks") or {}; po_w = [cw.get(w) for w in (15, 16, 17) if cw.get(w)]
    po = round(sum(po_w) / len(po_w), 1) if po_w else None
    now_ = xval(n, key, "koerner") or xval(n, key, "vegas") or (cw.get(START) if cw else None)
    rising = len(U) == 3 and (s[2] - s[0] >= 10) and s[2] >= 55
    split = bool(RL and RL.get("split")); qb_out = bool(QQ and QQ.get("out"))
    if pos not in SKILL: build = None
    elif po is not None and po >= 12 and not split: build = "BUILD"
    elif po is not None and po >= 9.5 and rising and not split: build = "CLIMBING"
    elif now_ and po is not None and now_ >= 11 and po < 10: build = "1-WEEK"
    else: build = None
    flags = (["split backfield"] if split else []) + (["his QB is out"] if qb_out else []) + (["hurt"] if hurt else [])
    total = max(0, min(100, round(g_val + g_fit + g_work + g_play + g_team + g_path - (10 if hurt else 0))))
    # expert check - noted, never used to drop anyone
    xc, agree, had = [], 0, 0
    used = PAN.compare(n, key, rep["key"])[2] if rep else list(got)
    for ex in EXPERTS:
        cv = xval(n, key, ex); rv = xval(n, rep["key"], ex) if rep else None
        base = dict(ex=XNAME[ex], rank=xrank(ex), check=ex in ROLES, role=(ROLES.index(ex) + 1 if ex in ROLES else None), read=XREAD.get(ex, ""))   # Nov 12 (Dom): ✓1 Ratcliffe, ✓2 RotoBaller, ✓3 Vegas
        if cv is None: xc.append(dict(base, txt="no number for him", ok=None)); continue
        if rv:
            had += 1; up = cv > rv; agree += up
            xc.append(dict(base, txt=f"{cv:.1f} vs {rep['name']} {rv:.1f} ({SPAN[ex]})", ok=up))
        else: xc.append(dict(base, txt=f"{cv:.1f} ({SPAN[ex]}; no number for {rep['name'] if rep else 'your man'})", ok=None))
    verdict = (f"{agree} of {had} sources have him ahead of {rep['name']}" if had else f"no expert has numbers for both him and {rep['name']}") if rep else "nobody on your roster to compare"
    why = [f"{pts:.0f} pts rest of season in {LEAGUES[n].replace('DK ', 'DK').replace('III', '3').replace('II', '2').replace('IV', '4').replace('I', '1')} scoring ({pts_src})"]
    if hurt: why.append(f"Injury: {inj[1]} ({inj[2]}) on the Week {inj[0]} report - minus 10")
    why += fit_why
    if pos in SKILL and len(U) == 3: why.append(f"Workload last 3 games: touches {' > '.join(str(int(x)) for x in o)}, snaps {' > '.join(str(x) + '%' for x in s)}")
    if nt.get("coach"): why.append(f"Coach: {nt['coach']}")
    if nt.get("star"): why.append(f"Path: {nt['star']}")
    why.append("Playoffs: " + ", ".join(f"W{w} {op or 'BYE'}" + (f" (#{rank.get((op, pos))})" if op and rank.get((op, pos)) else "") for w, op in opp)
               + ("" if rk else " (matchup ranks need this season's scores - scored even)"))
    if wp is not None: why.append(f"{tm} {REC[tm]}")
    why.insert(1, "Team: " + " · ".join(v for v in (TB.get("qb"), TB.get("role"), TB.get("offense"), TB.get("week")) if v))
    if pos in SKILL: why.insert(1, (f"Playoffs (Clay, Weeks 15-17 in this league's scoring): {po:.1f} a game" if po is not None else "Playoffs: no Clay number for Weeks 15-17")
                     + (" - meets the 12+ target" if build == "BUILD" else " - climbing toward it (snaps up 10+ points in 3 games)" if build == "CLIMBING"
                        else " - a one-week fill, fades after this week" if build == "1-WEEK" else ""))
    # Nov 12 4:10 PM (Dom): a pickup is a playoff decision - Ratcliffe's rest-of-season number decides, Clay's Weeks 15-17 is the check;
    # 2+ points apart = stop and talk (never a filter). The this-week checks (Koerner, Vegas) still show, for a one-week fill.
    chk_flag = None; rros = PAN.V["ratcliffe"].get((int(n), key))
    if pos in SKILL and rros and po is not None:
        gap_ = po - rros
        why.append(f"Playoff check: Ratcliffe rest of season {rros:.1f} a game · Clay Weeks 15-17 {po:.1f}"
                   + (f" - STOP AND TALK: Clay {'higher' if gap_ > 0 else 'lower'} by {abs(gap_):.1f}" if abs(gap_) >= 2 else " - check agrees"))
        chk_flag = abs(gap_) >= 2
    rwk = RATWK.get((n, key)); ck = PAN.checks(n, key); wk_flag = None
    if rwk is not None and ck:
        far = {XNAME[s2]: v for s2, v in ck.items() if abs(v - rwk) >= 2}
        why.append("This week: Ratcliffe " + f"{rwk:.1f}" + "".join(f" · {XNAME[s2]} {v:.1f}" for s2, v in ck.items())
                   + (" - " + ", ".join(f"{k2} {'higher' if v > rwk else 'lower'} by {abs(v - rwk):.1f}" for k2, v in far.items()) if far else " - checks agree"))
        wk_flag = bool(far)
    # TIER (Dom, Nov 9: "top line indicators, must, hot, watch ... blink and alert to those to pick up asap")
    maj = had >= 2 and agree * 2 >= had
    clears = gain is not None and gain >= MUSTBAR
    if not hurt and not split and maj and ((clears and total >= 60) or (hit and total >= 70)):
        tier = "MUST"; tw = (f"+{gain * 100:.0f}% over {rep['name']}" if clears else "fills your missing piece") + f", {agree} of {had} sources agree, grade {total}"
    elif total >= 60 or clears:
        tier = "HOT"; tw = (f"grade {total}" if total >= 60 else f"+{gain * 100:.0f}% over {rep['name']}") + (f", but only {agree} of {had} sources agree" if had and not maj else f", {agree} of {had} sources agree" if had else "")
    elif g_path >= 4:
        tier = "STASH"; tw = "the starter ahead of him is fading or a coach has talked up his role - worth a bench spot before he breaks out"
    else:
        tier = "WATCH"; tw = f"grade {total}; not yet an upgrade worth a roster spot"
    if hurt: tw += f" ({inj[1]} on the injury report)"
    return dict(tier=tier, tier_why=tw, gain=round(gain * 100) if gain is not None else None, key=key, name=(TEAMNAME.get(tm, tm) + " DEF") if pos == "DST" else name, team=tm, pos=P,
                pts=pts, grade=total, parts=dict(value=round(g_val), fit=round(g_fit), workload=round(g_work), playoffs=round(g_play), team=round(g_team), path=g_path),
                why=why, experts=dict(verdict=verdict, agree=agree, of=had, lines=xc), replaces=rep["name"] if rep else "",
                build=build, po=po, flags=flags, check_stop=chk_flag, week_stop=wk_flag, teamctx=TB)

out = {"built": datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%a %b %-d %Y %-I:%M %p PT"),
       "panel": {"order": [PNAME[s] for s in PAN.ranked], "check": [PNAME[s] for s in PAN.members], "check_po": [PNAME.get(s, s.title()) for s in PO_ROLES], "miss": {PNAME[s]: v for s, v in PAN.grades["miss"].items()},
                 "waiting": {PNAME[s]: w for s, w in PAN.waiting.items()}, "bias": {PNAME[s]: v for s, v in (PAN.grades.get("bias") or {}).items()}, "pct": {PNAME[s]: v for s, v in (PAN.grades.get("pct") or {}).items()}, "basis": PAN.grades.get("basis", ""), "ungraded": [PNAME[s] for s in PAN.order if s not in PAN.ranked],
                 "week": ("-".join(map(str, [PAN.grades["weeks"][0], PAN.grades["weeks"][-1]])) if PAN.grades["weeks"] else None), "players": PAN.grades["players"], "weeks_ahead": f"{START}-17", "notes": PAN.notes,
                 "others": [dict(name=XNAME[s], miss=WKG[s][0] if WKG[s][1] else None, week=WKG[s][1]) for s in WKO],
                 "reads": {PNAME[s]: XREAD.get(s, "") for s in PAN.order}},
       "sources": {"ratcliffe_read": READ.get("Ratcliffe", ""), "expert_reads": READ, "nflverse_through_week": last_week, "standings": STAND_ASOF,
                   "rank_note": "#1 = best matchup: the defense that gives up the most to his position (RB/WR/TE), the offense that scores the least (DEF), the defense that allows the most points (K)"},
       "leagues": {}}
for n in LEAGUES:
    taken, MY, has_k, wv, rpt = league(n); NEED = needs(n); rows = []
    for (lg, key), d in EXP.items():
        if lg != n or key in taken: continue
        if key in SIDELINED: continue              # IR / PUP / suspended - can't help, not a Diamond
        if d["_pos"] == "K" and not has_k: continue
        g = grade(n, key, d, MY, NEED)
        if not g: continue
        lv = LIVE["status"].get(f"{n}|{key}")
        if lv: g["status"] = ("Waivers until " + lv[3:-1] if lv.startswith("W (") else "Free agent" if lv == "FA" else lv) + " (Yahoo live " + LIVE["checked"] + ")"
        else: g["status"] = (("Waivers until " + wv[key]) if key in wv else "Free agent") + f" (per {rpt} read - confirm live)"
        rows.append(g)
    TO = {"MUST": 0, "HOT": 1, "STASH": 2, "WATCH": 3}
    BO = {"BUILD": 0, "CLIMBING": 1}
    rows.sort(key=lambda g: -g["grade"])
    # Nov 11 (Dom): the players he's looking for first - BUILD (12+ in the playoffs) and CLIMBING - then the best of the rest;
    # a split backfield, a hurt man or one whose QB is out never takes a top-five spot from a clean one
    rows.sort(key=lambda g: (BO.get(g.get("build"), 2), bool(g.get("flags")), -g["grade"]))
    top = sorted(rows[:5], key=lambda g: (BO.get(g.get("build"), 2), TO[g["tier"]], -g["grade"]))
    musts = [g for g in rows[5:] if g["tier"] == "MUST"]       # a MUST is never cut off the list
    rows = top + musts + rows[5:]
    out["leagues"][str(n)] = {"read": rpt, "top": top + musts, "needs": [nd[2] + (f" (short Weeks {', '.join(map(str, nd[1]))})" if nd[1] else "") for nd in NEED],
                              "pieces_built": PCHK.get("built", ""), "kicker_slot": has_k,
                              "pool": {g["key"]: [g["grade"], g["name"]] for g in rows},     # every man still available, for the change notes
                              "best": {p: next(({"name": g["name"], "grade": g["grade"]} for g in rows if g["pos"] == p), None) for p in ("RB", "WR", "TE", "K", "DEF")}}
json.dump(out, open(OUT, "w"), indent=1)
for n, L in out["leagues"].items():
    print("DK" + n, L["read"], "| best K", L["best"]["K"], "| best DEF", L["best"]["DEF"])
    for g in L["top"]: print("  ", g["tier"], g["grade"], g["name"], g["pos"], g["team"], g["pts"], g["parts"], "|", g["experts"]["verdict"])
