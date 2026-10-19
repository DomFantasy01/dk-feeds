# DARK KNIGHT STATE FILE (Dom, Oct 19 2026)
# One file that holds everything Claude needs to answer a question about Dom's four teams in a single read,
# instead of scraping Yahoo live every conversation. Built at the end of every Dispatch build from files the
# build already made - it adds no new Yahoo reads and no new cost.
#
#   dispatch_out/dk_state_latest.json  - the full state (machine-readable)
#   dispatch_out/dk_state_latest.txt   - the same, compact and readable; Claude reads this one first
#
# What is in it, per league: score now, Yahoo/Gotham/Sleeper totals and win %, every starter still to play
# (kickoff, injury tag, the three projections, latest news), the whole bench and IR with whether each man can
# still be moved in, LATE-SWAP RISKS (a hurt or bye starter whose game has not started, with every legal
# replacement and when the decision is due), the points needed, open actions and live alerts.
# Up top: SYSTEM HEALTH, broken first - every source with its age, stale or failed feeds, build failures and the
# open known issues - so nothing is ever reported only after Dom asks.
#
# usage: python3 state/build_state.py <repo dir> [<root dir>] [--now ISO-UTC]
# Standard library only. Never stops the build: any problem is written into the file as a health line.
import json, os, re, sys, glob, datetime as dt
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles"); UTC = dt.timezone.utc
ARGS = [a for a in sys.argv[1:]]
NOW = dt.datetime.now(UTC)
if "--now" in ARGS:
    i = ARGS.index("--now"); NOW = dt.datetime.fromisoformat(ARGS[i + 1].replace("Z", "+00:00")).astimezone(UTC); del ARGS[i:i + 2]
REPO = ARGS[0] if ARGS else "."
ROOT = ARGS[1] if len(ARGS) > 1 else "/home/claude"
OUT = os.path.join(REPO, "dispatch_out")
HEALTH = []          # (level, piece, what) - level: red / gold / grey

LEAGUES = [  # DK tag, Yahoo key used by the build, full name, league id, Dom's team number
    ("DK I", "MOST", "TheMostImportantThingInLife", "269381", "2", 1),
    ("DK II", "WINNERS", "Winners and Sinners", "1519795", "7", 2),
    ("DK III", "HERS&HIS", "Hers and His Version 2.0", "1507991", "2", 3),
    ("DK IV", "NEXTDOOR", "Murrieta NextDoor", "864215", "6", 4),
]
SLOT_OK = {"QB": {"QB"}, "RB": {"RB"}, "WR": {"WR"}, "TE": {"TE"}, "K": {"K"}, "DEF": {"DEF"},
           "W/R/T": {"WR", "RB", "TE"}, "Q/W/R/T": {"QB", "WR", "RB", "TE"}}
HURT = {"Q": "questionable", "D": "doubtful", "O": "out", "IR": "injured reserve", "NA": "not active",
        "PUP-R": "PUP", "SUSP": "suspended", "Out": "out", "Doubtful": "doubtful", "Questionable": "questionable"}

# ---------------------------------------------------------------- helpers
def load(p, default=None):
    try:
        with open(p) as f: return json.load(f)
    except FileNotFoundError: return default
    except Exception as e:
        HEALTH.append(("red", os.path.basename(p), f"could not be read ({type(e).__name__})")); return default
def iso(s):
    if not s: return None
    try:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return (t if t.tzinfo else t.replace(tzinfo=UTC)).astimezone(UTC)
    except Exception: return None
def ptstr(s):
    """'Mon Oct 19 2026 10:08 AM PT' / 'Mon Oct 19 08:55 AM PT' / 'Mon Oct 19 8:55 AM PT' -> aware UTC"""
    m = re.search(r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\w*,? (\w{3}) (\d{1,2}),?(?: (\d{4}))? (\d{1,2}):(\d{2}) ?([AP]M)", str(s or ""))
    if not m: return None
    mon, day, yr, hh, mm, ap = m.groups(); yr = int(yr) if yr else NOW.astimezone(PT).year
    h = int(hh) % 12 + (12 if ap == "PM" else 0)
    try: return dt.datetime.strptime(f"{yr} {mon} {day} {h}:{mm}", "%Y %b %d %H:%M").replace(tzinfo=PT).astimezone(UTC)
    except Exception: return None
def pt(t, day=True):
    if not t: return "unknown time"
    t = t.astimezone(PT); s = f"{t.hour % 12 or 12}:{t:%M} {'AM' if t.hour < 12 else 'PM'}"
    return f"{t:%a %b} {t.day}, {s} PT" if day else s + " PT"
def age(t):
    """elapsed time in Dom's style: '12 min ago', '3.4 hr ago', '2 days ago'"""
    if not t: return "age unknown"
    m = (NOW - t).total_seconds() / 60
    if m < 0: return "in the future"
    if m < 90: return f"{int(round(m))} min ago"
    if m < 48 * 60: return f"{m / 60:.1f} hr ago"
    return f"{m / 1440:.0f} days ago"
def norm(n):
    n = re.sub(r"[^a-z ]", "", str(n).lower().replace("-", " ").replace(".", " "))
    return " ".join(re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n).split())
def f1(x): return None if x is None else round(float(x), 1)

# ---------------------------------------------------------------- the week and its kickoff windows
meters = sorted(glob.glob(os.path.join(OUT, "meter_wk*.json")), key=lambda p: int(re.search(r"wk(\d+)", p).group(1)))
if not meters:
    HEALTH.append(("red", "Meter", "no meter_wk*.json in dispatch_out - the build did not get far enough; state file is empty"))
M = load(meters[-1], {}) if meters else {}
WEEK = M.get("week")
BUILT = ptstr(M.get("built_pt"))
# kickoff per NFL team from the nflverse schedule the build just pulled; window labels are the fallback
KO_TEAM = {}
games = os.path.join(ROOT, "dksys/data/latest/games.csv")
if WEEK and os.path.exists(games):
    import csv
    for r in csv.DictReader(open(games)):
        if r.get("week") == str(WEEK) and r.get("season") == str(NOW.astimezone(PT).year) and r.get("game_type", "REG") == "REG":
            try:
                t = dt.datetime.strptime(f"{r['gameday']} {r['gametime'] or '13:00'}", "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("America/New_York")).astimezone(UTC)
                KO_TEAM[r["away_team"]] = KO_TEAM[r["home_team"]] = t
            except Exception: pass
ALIAS = {"LA": "LAR", "WSH": "WAS", "JAC": "JAX"}
def win_time(i):
    """window label 'MON 5:15 PM' -> datetime in this NFL week (weeks run Thu to Mon)"""
    try: lab = M["windows"][i]
    except Exception: return None
    d0 = (BUILT or NOW).astimezone(PT).date(); wd = d0.weekday()
    thu = d0 - dt.timedelta(days=wd - 3) if wd >= 3 else (d0 - dt.timedelta(days=wd + 4) if wd <= 1 else d0 + dt.timedelta(days=1))
    off = {"THU": 0, "FRI": 1, "SAT": 2, "SUN": 3, "MON": 4, "TUE": 5, "WED": 6}
    m = re.match(r"(\w{3}) (\d{1,2}):(\d{2}) ([AP]M)", lab)
    if not m: return None
    day = thu + dt.timedelta(days=off.get(m.group(1), 0)); h = int(m.group(2)) % 12 + (12 if m.group(4) == "PM" else 0)
    return dt.datetime(day.year, day.month, day.day, h, int(m.group(3)), tzinfo=PT).astimezone(UTC)
def kickoff(p):
    t = KO_TEAM.get(ALIAS.get(str(p.get("team", "")).upper(), str(p.get("team", "")).upper()))
    return t or (win_time(p["window"]) if p.get("window") is not None else None)

# ---------------------------------------------------------------- news and injuries, keyed by player name
NEWS = {}   # norm name -> list of (time, source, line)
INJ = {}    # norm name -> {source: text}
def add_news(name, t, src, line):
    if not name or not line: return
    if t and (NOW - t).total_seconds() > 72 * 3600: return
    NEWS.setdefault(norm(name), []).append((t, src, re.sub(r"\s+", " ", line).strip()[:220]))
FEEDS = os.path.join(REPO, "feeds")
FAST = os.path.join(FEEDS, "fast")   # Oct 19: the inactives watch writes here every 5 minutes around each inactives list
def feed(name):
    """the newer of feeds/<name> and feeds/fast/<name>, judged by the file's own pull time"""
    best, bt = None, None
    for d in (FEEDS, FAST):
        j = load(os.path.join(d, name))
        if not isinstance(j, dict): continue
        t = iso(j.get("pulled_utc") or j.get("run_utc") or j.get("db_pulled_utc"))
        if best is None or (t and (bt is None or t > bt)): best, bt = j, t
    return best or {}
espn_inj = feed("espn_injuries.json")
for r in espn_inj.get("players", []):
    INJ.setdefault(norm(r.get("name")), {})["ESPN"] = f"{r.get('status')}" + (f" ({r.get('type')})" if r.get("type") else "") + (f", posted {age(iso(r.get('date')))}" if r.get("date") else "")
slp = load(os.path.join(FEEDS, "sleeper_injuries.json"), {}) or {}
for r in (slp.get("players") or {}).values():
    s = f"{r.get('inj')}" + (f" ({r.get('inj_body')})" if r.get("inj_body") else "") + (f", practice {r.get('practice')}" if r.get("practice") else "")
    INJ.setdefault(norm(r.get("name")), {})["Sleeper"] = s
ALL_NAMES = set()
def collect_names():
    for L in (M.get("leagues") or {}).values():
        for side in ("me", "op"):
            for p in (L.get("starters") or {}).get(side, []): ALL_NAMES.add(p.get("player"))
        for p in L.get("bench") or []: ALL_NAMES.add(p.get("player"))
collect_names()
ALL_NAMES.discard(None)
def scan_items(items, src, title="title", text="text", when="published_utc"):
    for it in items or []:
        blob = f"{it.get(title, '')} {it.get(text, '')}"
        if sum(1 for n in ALL_NAMES if n and n in str(it.get(title, ""))) >= 3: continue   # a roundup, not news about one man
        for n in ALL_NAMES:
            if n and n in blob:
                add_news(n, iso(it.get(when)), src, it.get(title) or it.get(text))
for f, src in (("rotowire_latest.json", "RotoWire"), ("espn_news.json", "ESPN"), ("news_extra.json", None)):
    d = feed(f)
    if src: scan_items(d.get("items"), src)
    else:
        for it in d.get("items") or []: scan_items([it], {"pft": "ProFootballTalk", "rotoballer": "RotoBaller"}.get(it.get("source"), it.get("source", "news")))
# the history files keep items that scrolled off the live feeds (RotoWire only holds ~5 at a time)
for f, src in (("rotowire_history.jsonl", "RotoWire"), ("news_extra_history.jsonl", None), ("espn_news_history.jsonl", "ESPN")):
    lines = []
    for d in (FEEDS, FAST):
        p = os.path.join(d, f)
        if not os.path.exists(p): continue
        try: lines += open(p).read().splitlines()[-1500:]
        except Exception: pass
    for ln in lines:
        try: it = json.loads(ln)
        except Exception: continue
        scan_items([it], src or {"pft": "ProFootballTalk", "rotoballer": "RotoBaller"}.get(it.get("source"), it.get("source", "news")))
def news_for(name, n=2):
    seen, out = set(), []
    for t, src, line in sorted(NEWS.get(norm(name), []), key=lambda x: x[0] or dt.datetime.min.replace(tzinfo=UTC), reverse=True):
        k = line[:60].lower()
        if k in seen: continue
        seen.add(k); out.append({"src": src, "at": pt(t), "age": age(t), "line": line})
        if len(out) >= n: break
    return out

# ---------------------------------------------------------------- SYSTEM HEALTH: every source with its age
SOURCES = []
def source(name, t, schedule_hours, note="", level_if_old="gold"):
    a = age(t); lvl = "green"
    if t is None: lvl = "red"; note = (note + "; " if note else "") + "no timestamp - treat as missing"
    elif (NOW - t).total_seconds() / 3600 > schedule_hours: lvl = level_if_old; note = (note + "; " if note else "") + f"older than its {schedule_hours:g}-hour schedule"
    SOURCES.append({"source": name, "as_of": pt(t), "age": a, "level": lvl, "note": note})
    if lvl in ("red", "gold"): HEALTH.append((lvl, name, f"as of {pt(t)} ({a}) - {note}"))
for k, v in (M.get("sources") or {}).items():
    hrs = {"yahoo_matchups": 6, "yahoo_rosters": 6, "yahoo_all_teams": 24, "yahoo_standings": 24, "nfl_schedule": 24}.get(k, 12)
    lvl_old = "red" if k in ("yahoo_matchups", "yahoo_rosters") else "gold"
    st = v.get("status", "")
    source({"yahoo_matchups": "Yahoo matchups (scores, starters)", "yahoo_rosters": "Yahoo rosters (all teams)",
            "yahoo_all_teams": "Yahoo win % (all teams)", "yahoo_standings": "Yahoo standings", "nfl_schedule": "NFL schedule",
            "gotham": "Gotham projections", "sleeper_skill": "Sleeper projections", "sleeper_kdef": "Sleeper K/DEF projections"}.get(k, k),
           ptstr(v.get("pulled_pt")), hrs, (v.get("note") or "") + ("" if st in ("OK", "") else f"; build says {st}"), lvl_old)
    if st not in ("OK", ""): HEALTH.append(("red", k, f"build marked it {st}: {v.get('note', '')}"))
FS = load(os.path.join(FEEDS, "status.json"), {}) or {}
run = iso(FS.get("run_utc"))
_fs = load(os.path.join(FAST, "status.json"), {}) or {}
for _k, _v in (_fs.get("sources") or {}).items():          # a newer reading from the inactives watch wins, source by source
    _old = (FS.get("sources") or {}).get(_k)
    _t0 = dt.datetime.min.replace(tzinfo=UTC)
    if not _old or (iso(_v.get("checked_utc")) or _t0) > (iso(_old.get("checked_utc")) or run or _t0):
        FS.setdefault("sources", {})[_k] = dict(_v, via="inactives watch")
for k, v in (FS.get("sources") or {}).items():
    if k == "probe": continue
    nice = {"rotowire": "RotoWire news", "sleeper": "Sleeper injuries/trending", "weather": "Game weather",
            "espn_news": "ESPN news", "news_extra": "PFT + RotoBaller news", "espn_injuries": "ESPN injury report"}.get(k, k)
    note = v.get("warning") or ""
    if not v.get("ok", True): HEALTH.append(("red", nice, "feed FAILED on its last pull" + (f": {note}" if note else "")))
    elif note: HEALTH.append(("gold", nice, note))
    source(nice, iso(v.get("checked_utc")) or run, 1.5, f"newest item {v['newest_age_hours']} hr old" if "newest_age_hours" in v and not v.get("rss_note") else "")
for f, what in (("build_failed.json", "the last Dispatch build FAILED"), ("RADAR_FAILED.txt", "the last Radar build FAILED")):
    if os.path.exists(os.path.join(OUT, f)): HEALTH.append(("red", "Build", what + " - the pages may be older than they look"))
for a in (M.get("alarms") or []): HEALTH.append(("red", "Meter alarm", str(a)))
for n in (M.get("notes") or []): HEALTH.append(("grey", "Meter note", str(n)))
KI = load(os.path.join(REPO, "live_sync/known_issues.json"), {}) or {}
for it in KI.get("issues", []):
    if not it.get("fixed"):
        HEALTH.append(({"red": "red", "yellow": "gold"}.get(it.get("level"), "grey"), "Known issue: " + it.get("piece", ""), it.get("what", "")))

# ---------------------------------------------------------------- full rosters (bench + IR) from the live roster read
def roster_read(n, team):
    p = os.path.join(REPO, f"yahoo_drop/scout/dk{n}_rosters_live.txt")
    rows, stamp = [], None
    try:
        for ln in open(p):
            if ln.startswith("#"):
                stamp = stamp or ptstr(ln); continue
            x = ln.rstrip("\n").split("|")
            if len(x) >= 6 and x[0] == team: rows.append({"slot": x[1], "player": x[2], "team": x[3].upper(), "pos": x[4], "status": x[5]})
    except FileNotFoundError: HEALTH.append(("red", f"DK roster file {n}", "missing - bench and IR come from the meter only"))
    return rows, stamp

# ---------------------------------------------------------------- Yahoo weekly projections (this week, next two, playoff weeks)
def yproj_read(n):
    d, stamp = {}, None
    p = os.path.join(REPO, f"yahoo_drop/scout/yproj_dk{n}.txt")
    if not os.path.exists(p): return d, None
    for ln in open(p):
        if ln.startswith("#"): stamp = stamp or ptstr(ln); continue
        x = ln.rstrip("\n").split("|")
        if len(x) >= 6 and x[5] == "MINE":
            try: d.setdefault(norm(x[1]), {})[int(x[0])] = float(x[4])
            except ValueError: pass
    return d, stamp

# ---------------------------------------------------------------- the leagues
ACT = load(os.path.join(OUT, "actions_latest.json"), {}) or {}
ALR = load(os.path.join(OUT, "alerts_build.json"), {}) or {}
STATE = {"what": "Dark Knight state file - read this before answering anything about Dom's four teams",
         "built_utc": NOW.isoformat(timespec="seconds"), "built_pt": pt(NOW), "week": WEEK,
         "dispatch_built_pt": M.get("built_pt"), "leagues": [], "health": [], "sources": SOURCES, "exposure": []}
ORDER = {"red": 0, "gold": 1, "grey": 2}
ROSTER_CHECK = []   # (league, newer live roster read matches the meter's roster)
for dk, key, full, lid, team, n in LEAGUES:
    L = (M.get("leagues") or {}).get(dk)
    if not L:
        HEALTH.append(("red", dk, "not in the meter - no state for this league")); continue
    me_st, op_st = L["starters"]["me"], L["starters"]["op"]
    rr, rstamp = roster_read(n, team)
    YP, ystamp = yproj_read(n)
    YWEEKS = sorted({k for v in YP.values() for k in v})   # the weeks the read covers; a man missing one is on bye
    if rstamp and (NOW - rstamp).total_seconds() > 6 * 3600:
        HEALTH.append(("gold", f"{dk} roster read", f"from {pt(rstamp)} ({age(rstamp)}) - a move made since then is not in this file"))
    def row(p, side):
        ko = kickoff(p); gs = p.get("gs")
        if gs is None: gs = "nogame" if ko is None else ("pre" if ko > NOW else ("final" if (NOW - ko).total_seconds() > 4 * 3600 else "started"))
        if gs == "pre" and ko and ko <= NOW: gs = "started"           # the read is older than the kickoff
        st = p.get("status") or ""
        d = {"slot": p.get("slot"), "name": p.get("player"), "pos": p.get("pos"), "nfl": p.get("team"),
             "kickoff": pt(ko) if ko else ("no game this week" if gs == "nogame" else "unknown"), "ko_utc": ko.isoformat() if ko else None,
             "game": {"pre": "not started", "final": "played", "started": "started", "nogame": "no game"}.get(gs, gs),
             "status": HURT.get(st, st) if st else "", "actual": f1(p.get("actual")),
             "proj": {"yahoo": f1(p.get("yahoo")), "gotham": f1(p.get("gotham")), "sleeper": f1(p.get("sleeper"))}}
        if side == "me":
            yp = YP.get(norm(p.get("player")), {})
            if d["proj"]["yahoo"] is None and WEEK in yp:
                d["proj"]["yahoo"] = f1(yp[WEEK]); d["proj"]["yahoo_from"] = "Yahoo projections read " + (pt(ystamp) if ystamp else "")
            ahead = {f"wk{k}": (f1(yp[k]) if k in yp else "bye") for k in YWEEKS if WEEK and k > WEEK} if yp else {}
            if ahead: d["yahoo_weeks_ahead"] = ahead
        if side == "me" or gs == "pre":
            inj = INJ.get(norm(p.get("player")))
            if inj: d["injury_feeds"] = inj
            nw = news_for(p.get("player"))
            if nw: d["news"] = nw
        return d
    me = [row(p, "me") for p in me_st]; op = [row(p, "op") for p in op_st]
    bench = [row(p, "me") for p in (L.get("bench") or [])]
    # the roster read is the truth for who is on the bench/IR; the meter supplies projections and windows
    known = {norm(x["name"]) for x in me + bench}
    for r in rr:
        if norm(r["player"]) not in known:
            bench.append(row({"slot": r["slot"], "player": r["player"], "team": r["team"], "pos": r["pos"], "status": r["status"]}, "me"))
            HEALTH.append(("gold", f"{dk} roster", f"{r['player']} is on the live roster read but not in the meter - added from the roster read"))
    mstamp = ptstr(((M.get("sources") or {}).get("yahoo_rosters") or {}).get("pulled_pt"))
    if rstamp and mstamp and rstamp > mstamp:
        added = [r for r in rr if norm(r["player"]) not in known]
        ROSTER_CHECK.append((dk, not added))
    for b in bench:   # fix the meter's position tag from the roster read (e.g. a bench DEF tagged WR)
        rp = next((r for r in rr if norm(r["player"]) == norm(b["name"])), None)
        if rp and rp["pos"] and rp["pos"] != b["pos"]:
            HEALTH.append(("grey", f"{dk} meter", f"{b['name']} tagged {b['pos']} in the meter, {rp['pos']} on Yahoo - using Yahoo"))
            b["pos"] = rp["pos"]
    # empty starting slots
    for s in me:
        if not s["name"] or s["name"] in ("(Empty)", "Empty"): HEALTH.append(("red", dk, f"starting slot {s['slot']} is EMPTY"))
    # scores and what is needed
    sc_me = round(sum(p.get("actual") or 0 for p in me_st if p.get("gs") in ("final", None) or p.get("actual") is not None), 2)
    sc_op = round(sum(p.get("actual") or 0 for p in op_st if p.get("gs") in ("final", None) or p.get("actual") is not None), 2)
    left_me = [x for x in me if x["game"] == "not started"]; left_op = [x for x in op if x["game"] == "not started"]
    def rem(rows, src): return round(sum((x["proj"][src] or 0) for x in rows), 1)
    need = {src: {"my_remaining": rem(left_me, src), "their_remaining": rem(left_op, src),
                  "projected_margin": round(sc_me + rem(left_me, src) - sc_op - rem(left_op, src), 1)} for src in ("yahoo", "gotham", "sleeper")}
    need_pts = round(sc_op + need["yahoo"]["their_remaining"] - sc_me, 1)
    # LATE-SWAP RISKS: a starter who may score zero (hurt tag or no game) while a legal swap still exists
    risks = []
    for s in me:
        tag = s["status"]; danger = (tag in ("questionable", "doubtful", "out", "injured reserve", "not active", "suspended", "PUP")) or s["game"] == "no game"
        if not danger or s["game"] in ("played", "started"): continue
        opts = []
        for b in bench:
            if b["slot"] == "IR" or b["status"] in ("out", "injured reserve", "not active", "suspended"): continue
            if b["pos"] not in SLOT_OK.get(s["slot"], {s["slot"]}): continue
            if b["game"] != "not started": continue
            opts.append({"name": b["name"], "pos": b["pos"], "nfl": b["nfl"], "kickoff": b["kickoff"], "status": b["status"] or "healthy",
                         "proj": b["proj"], "decide_by": b["kickoff"]})
        opts.sort(key=lambda o: -((o["proj"]["yahoo"] or o["proj"]["gotham"] or 0)))
        ko = iso(s["ko_utc"])
        inactives = ko - dt.timedelta(minutes=90) if ko else None
        r = {"starter": s["name"], "slot": s["slot"], "why": tag or "no game this week", "kickoff": s["kickoff"],
             "inactives_list_at": pt(inactives) if inactives and s["game"] != "no game" else None,
             "proj": s["proj"], "bench_options": opts,
             "free_agent_options": "not in this file - the roster read does not list free agents playing later in the week; ask Claude to read the wire"}
        if not opts: r["warning"] = "NO legal bench swap left - only a free-agent add (needs a drop) can cover a zero"
        else:
            best = opts[0]; dy = (s["proj"]["yahoo"] or 0) - (best["proj"]["yahoo"] if best["proj"]["yahoo"] is not None else (best["proj"]["gotham"] or 0))
            r["plan"] = (f"If {s['name']} is ruled out, start {best['name']} ({best['pos']}, {best['nfl']}) - no drop needed. "
                         f"Yahoo gap if he sits: about {dy:.1f} pts." + (f" Decision due when the inactives post, about {pt(inactives, False)}." if inactives and s["game"] != "no game" else ""))
        risks.append(r)
        HEALTH.append(("red" if not opts else "gold", dk, f"{s['name']} ({s['slot']}) {r['why']}, kickoff {s['kickoff']} - " + (r.get("plan") or r["warning"])))
    acts = [a for a in ACT.get("items", []) if a.get("lg") == dk]
    alerts = sorted([a for a in ALR.get("items", []) if a.get("lg") == dk and a.get("active")], key=lambda a: ORDER.get(a.get("color"), 3))
    STATE["leagues"].append({
        "dk": dk, "league": full, "league_id": lid, "team_no": team, "team": L.get("me"), "record": L.get("record"),
        "rank": L.get("rank"), "teams": L.get("teams"), "division": L.get("div"), "div_rank": L.get("div_rank"),
        "opponent": L.get("opp"), "opp_record": L.get("opp_record"), "opp_rank": L.get("opp_rank"),
        "game_state": L.get("state"), "state_note": L.get("state_note"),
        "score": {"me": sc_me, "opp": sc_op}, "totals_projected": L.get("totals"), "win_pct": L.get("needles"),
        "points_needed_to_pass_yahoo": need_pts, "remaining": need,
        "late_swap_risks": risks, "still_to_play": {"me": left_me, "opp": left_op},
        "starters": me, "bench_and_ir": bench, "opp_starters": op,
        "actions": [{"what": a.get("what"), "by": a.get("by"), "kind": a.get("kind")} for a in acts],
        "alerts": [{"color": a.get("color"), "title": a.get("title"), "who": a.get("who"), "kind": a.get("kind"), "src": a.get("src")} for a in alerts[:8]],
        "roster_read_pt": pt(rstamp) if rstamp else None})

if ROSTER_CHECK and all(ok for _, ok in ROSTER_CHECK):
    for i, h in enumerate(HEALTH):
        if h[1].startswith("Yahoo rosters") and h[0] == "red":
            HEALTH[i] = ("grey", h[1], h[2] + " - but the newer live roster read matches it in all four leagues, so nothing is missing")
    for s in SOURCES:
        if s["source"].startswith("Yahoo rosters") and s["level"] == "red":
            s["level"] = "grey"; s["note"] += "; the newer live roster read matches it"

# exposure across leagues: one injury can hit several teams
EXP = {}
for lg in STATE["leagues"]:
    for s in lg["starters"]: EXP.setdefault(s["name"], {"starts": [], "bench": []})["starts"].append(lg["dk"])
    for b in lg["bench_and_ir"]: EXP.setdefault(b["name"], {"starts": [], "bench": []})["bench"].append(lg["dk"])
STATE["exposure"] = [{"name": k, **v} for k, v in sorted(EXP.items(), key=lambda kv: -len(kv[1]["starts"]) - len(kv[1]["bench"])) if len(v["starts"]) + len(v["bench"]) > 1]
seen = set(); H = []
for lvl, piece, what in sorted(HEALTH, key=lambda h: ORDER.get(h[0], 3)):
    k = (piece, what)
    if k in seen: continue
    seen.add(k); H.append({"level": lvl, "piece": piece, "what": what})
STATE["health"] = H
STATE["verdict"] = "NO-GO" if any(h["level"] == "red" and not h["piece"].startswith(("DK ", "Known issue")) for h in H) else "GO"

os.makedirs(OUT, exist_ok=True)
json.dump(STATE, open(os.path.join(OUT, "dk_state_latest.json"), "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- the readable copy (what Claude reads first)
T = []; w = T.append
def pj(p): return "Y {0} / G {1} / S {2}".format(*[("-" if p[k] is None else p[k]) for k in ("yahoo", "gotham", "sleeper")])
w(f"DARK KNIGHT STATE - Week {WEEK} - built {pt(NOW)} from the Dispatch build of {M.get('built_pt')}")
w(f"Data verdict: {STATE['verdict']}  (NO-GO = a data source is broken or stale; fix before deciding)")
w("")
w("== SYSTEM HEALTH (broken first)")
for h in H:
    if h["level"] == "grey": continue
    w(f"  [{h['level'].upper()}] {h['piece']}: {h['what']}")
w("  -- sources and their age --")
for s in SOURCES: w(f"  {s['level']:5} {s['source']}: as of {s['as_of']} ({s['age']})" + (f" - {s['note']}" if s["note"] else ""))
for lg in STATE["leagues"]:
    w(""); w(f"== {lg['dk']} - {lg['league']} - {lg['team']} ({lg['record']}, #{lg['rank']} of {lg['teams']}) vs {lg['opponent']} ({lg['opp_record']})")
    wp = lg["win_pct"] or {}
    w(f"  Score now {lg['score']['me']} to {lg['score']['opp']} | {lg['state_note']} | win %: Yahoo {wp.get('yahoo')}, Gotham {wp.get('gotham')}, Sleeper {wp.get('sleeper')}")
    r = lg["remaining"]
    w(f"  Needs {lg['points_needed_to_pass_yahoo']} more to pass them (Yahoo). Projected margin: Yahoo {r['yahoo']['projected_margin']:+}, Gotham {r['gotham']['projected_margin']:+}, Sleeper {r['sleeper']['projected_margin']:+}")
    for rk in lg["late_swap_risks"]:
        w(f"  !! LATE-SWAP RISK: {rk['starter']} ({rk['slot']}) {rk['why']}, kickoff {rk['kickoff']}" + (f", inactives ~{rk['inactives_list_at']}" if rk.get("inactives_list_at") else ""))
        w(f"     {rk.get('plan') or rk.get('warning')}")
        for o in rk["bench_options"]: w(f"     option: {o['name']} {o['pos']} {o['nfl']} {o['kickoff']} {o['status']} - {pj(o['proj'])}")
    w("  Still to play - mine:" + ("" if lg["still_to_play"]["me"] else " none"))
    for x in lg["still_to_play"]["me"]:
        w(f"    {x['slot']:7} {x['name']} ({x['pos']} {x['nfl']}) {x['kickoff']}" + (f" [{x['status'].upper()}]" if x["status"] else "") + f" - {pj(x['proj'])}")
        if x.get("yahoo_weeks_ahead"): w("       Yahoo ahead: " + ", ".join(f"{k} {v}" for k, v in x["yahoo_weeks_ahead"].items()))
        for k, v in (x.get("injury_feeds") or {}).items(): w(f"       {k} injury: {v}")
        for nw in x.get("news", []): w(f"       {nw['src']} ({nw['age']}): {nw['line']}")
    w("  Still to play - theirs:" + ("" if lg["still_to_play"]["opp"] else " none"))
    for x in lg["still_to_play"]["opp"]:
        w(f"    {x['slot']:7} {x['name']} ({x['pos']} {x['nfl']}) {x['kickoff']}" + (f" [{x['status'].upper()}]" if x["status"] else "") + f" - {pj(x['proj'])}")
        for nw in x.get("news", [])[:1]: w(f"       {nw['src']} ({nw['age']}): {nw['line']}")
    w("  Bench and IR:")
    for b in lg["bench_and_ir"]:
        w(f"    {b['slot']:3} {b['name']} ({b['pos']} {b['nfl']}) - {b['game']}" + (f", {b['kickoff']}" if b["game"] == "not started" else "") + (f" [{b['status'].upper()}]" if b["status"] else "")
          + (f" - Yahoo {b['proj']['yahoo']}" if b["game"] == "not started" and b["proj"]["yahoo"] is not None else ""))
    for a in lg["actions"]: w(f"  TO DO: {a['what']} ({a['by']})")
    for a in lg["alerts"]:
        if a["color"] != "grey": w(f"  ALERT [{a['color']}]: {a['title']}")
    if lg.get("roster_read_pt"): w(f"  (roster read {lg['roster_read_pt']})")
w(""); w("== EXPOSURE (one injury, several teams)")
for e in STATE["exposure"][:12]: w(f"  {e['name']}: starts {', '.join(e['starts']) or '-'}" + (f"; bench {', '.join(e['bench'])}" if e["bench"] else ""))
open(os.path.join(OUT, "dk_state_latest.txt"), "w").write("\n".join(T) + "\n")
print(f"   state file: week {WEEK}, {len(STATE['leagues'])} leagues, {sum(len(l['late_swap_risks']) for l in STATE['leagues'])} late-swap risks, "
      f"{sum(1 for h in H if h['level'] == 'red')} red health lines, verdict {STATE['verdict']}")
