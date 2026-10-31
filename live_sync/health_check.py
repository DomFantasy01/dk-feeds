# Dark Knight system health check (Dom, Oct 14 2026).
# Walks the whole chain - feeds, projections, the Yahoo read, the Dispatch build, Gotham, the Scout, the Radar,
# the scoreboard, alerts, Dark Knight Live and the morning brief - and checks two things for each piece:
#   1. it RAN and is CURRENT (judged against its own schedule, so an overnight gap is not a false alarm), and
#   2. it is LINKED: every piece downstream was built from the same Yahoo read and the same Dispatch build.
# Known open problems (live_sync/known_issues.json) are reported every run until they are marked fixed, so Dom hears
# about them first thing - never only after he asks.
#
# usage: python3 health_check.py <files dir> <db dir> <out.json> [--now ISO]
#   files dir : the repo files below, downloaded with the same relative paths (missing file = that piece failed)
#   db dir    : Live database docs saved by ArtifactData (live/state.json, live/models.json, live/alerts.json, runlog/*.json)
import json, os, re, sys, glob, datetime as dt
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles"); UTC = dt.timezone.utc
A = sys.argv[1:]
F, D, OUT = A[0], A[1], A[2]
NOW = dt.datetime.fromisoformat(A[A.index("--now") + 1]).astimezone(UTC) if "--now" in A else dt.datetime.now(UTC)
NPT = NOW.astimezone(PT)

def load(rel, base=F):
    p = os.path.join(base, rel)
    try:
        with open(p) as f: j = json.load(f)
        return j.get("data", j) if isinstance(j, dict) and "data" in j and len(j) <= 3 else j
    except Exception: return None
def text(rel):
    try: return open(os.path.join(F, rel)).read()
    except Exception: return None
def iso(s):
    if not s: return None
    try:
        s = str(s).replace("Z", "+00:00")
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{4}\+", s): s = s[:13] + ":" + s[13:]
        t = dt.datetime.fromisoformat(s); return (t if t.tzinfo else t.replace(tzinfo=UTC)).astimezone(UTC)
    except Exception: return None
def ptstr(s):
    """'Wed Oct 14 2026 12:18 AM PT' / 'Tue Oct 13 04:52 PM PT' / 'Wed Oct 14, 12:18 AM PT' -> UTC"""
    if not s: return None
    m = re.search(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\w*,? (\w{3}) (\d{1,2}),?(?: (\d{4}))? (\d{1,2}):(\d{2}) ?([AP]M)", str(s))
    if not m: return None
    _, mon, day, yr, hh, mm, ap = m.groups()
    yr = int(yr) if yr else NPT.year
    h = int(hh) % 12 + (12 if ap == "PM" else 0)
    mo = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(mon) + 1
    return dt.datetime(yr, mo, int(day), h, int(mm), tzinfo=PT).astimezone(UTC)
def ago(t):
    if not t: return "never"
    m = (NOW - t).total_seconds() / 60
    if m < 1.5: return "just now"
    if m < 90: return f"{m:.0f} min ago"
    if m < 48 * 60: return f"{m/60:.1f} h ago"
    return f"{m/1440:.1f} days ago"
def at(t): return t.astimezone(PT).strftime("%a %-I:%M %p") if t else "—"

R = []   # one row per check
def row(group, name, status, detail, when=None):
    R.append({"group": group, "name": name, "status": status, "detail": detail, "when": at(when) if when else "", "age": ago(when) if when else ""})

# ---------- the schedules (Pacific) ----------
def read_slots(day):
    """scheduled Yahoo reads for a PT date"""
    # Oct 31: THE CHAIN clock (Oct 30) - Mon-Sat Yahoo read :25 at 3, 9, 13, 18 (+21 Mon & Thu); Sunday 3:50 AM then hourly :50 8-20 (Oct 31).
    # (The old 7:50/12:50/4:50 clock flagged a false "MISSED" read between chain reads.)
    if day.weekday() == 6: return [dt.datetime(day.year, day.month, day.day, h, 50, tzinfo=PT) for h in [3] + list(range(8, 21))]
    hrs = [3, 9, 13, 16, 18, 21]  # Oct 31: matches the Mon-Sat read task (:25 at 3, 9, 13, 16, 18, 21)
    return [dt.datetime(day.year, day.month, day.day, h, 25, tzinfo=PT) for h in hrs]
def last_slot(grace_min=25):
    cands = []
    for d in range(0, 3):
        day = (NPT - dt.timedelta(days=d)).date()
        cands += [s for s in read_slots(day) if s + dt.timedelta(minutes=grace_min) <= NPT]
    return max(cands) if cands else None
def next_slot():
    for d in range(0, 3):
        day = (NPT + dt.timedelta(days=d)).date()
        for s in read_slots(day):
            if s > NPT: return s
SLOT, NEXT = last_slot(), next_slot()
day_hours = 5 <= NPT.hour < 23

# ---------- 1. news feeds (GitHub Actions, every 30 min 5 AM - 11:30 PM PT) ----------
st = load("feeds/status.json")
if not st: row("Feeds", "News feeds", "red", "feeds/status.json missing - the feed pull has not saved")
else:
    t = iso(st.get("run_utc")); lim = 50 if day_hours else 8 * 60
    ok = t and (NOW - t).total_seconds() / 60 <= lim
    row("Feeds", "News feed pull", "green" if ok else "red", "runs every 30 min, 5 AM-11:30 PM" + ("" if ok else " - LATE"), t)
    S = st.get("sources", {}); _fs = {}
    for k, lab in (("espn_injuries", "ESPN injury report"), ("espn_news", "ESPN news"), ("news_extra", "PFT + RotoBaller news"), ("rotowire", "RotoWire news"), ("weather", "Game weather")):
        s = S.get(k) or {}
        if not s: row("Feeds", lab, "red", "missing from the feed pull"); _fs[k] = "red"; continue
        warn = s.get("warning") or (s.get("problems") and str(s["problems"])) or (s.get("errors") and str(s["errors"]))
        newest = s.get("newest_age_hours")
        if newest is None and s.get("newest_item_utc"):
            n = iso(s["newest_item_utc"]); newest = (NOW - n).total_seconds() / 3600 if n else None
        bad = s.get("ok") is False
        stale = newest is not None and newest > 12
        stt = "red" if bad else "yellow" if (warn or stale) else "green"
        d = warn if warn else (f"newest item {newest:.0f} h old" if newest is not None else "")
        if k == "rotowire" and stt != "green":   # Oct 14 (Dom): RotoWire is a backup; while the three main news feeds are green it's information, not a warning
            covered = all(_fs.get(x) == "green" for x in ("espn_injuries", "espn_news", "news_extra"))
            d += " (ESPN and PFT/RotoBaller still cover injuries)"
            if covered and stt == "yellow": stt = "grey"
        _fs[k] = stt
        row("Feeds", lab, stt, d.strip(" -") or "ok")
    sl = S.get("sleeper") or {}
    row("Feeds", "Sleeper trending + injuries", "green" if sl.get("adds") else "yellow", f"{sl.get('adds', 0)} adds, {sl.get('injured_tagged', 0)} injured tagged")

# ---------- 2. projections (GitHub Actions, hourly) ----------
log = text("feeds/proj/status_log.jsonl")
if not log: row("Projections", "Projection pull", "red", "status_log missing")
else:
    last = json.loads(log.strip().splitlines()[-1]); t = iso(last.get("run_utc"))
    ok = t and (NOW - t).total_seconds() / 3600 <= 2.5
    row("Projections", "Projection pull (hourly)", "green" if ok else "red", "Sleeper, ESPN, CBS" + ("" if ok else " - LATE"), t)
    srcs = last.get("sources", {})
    for k in ("sleeper", "sleeper_kdef"):
        v = " ".join(str(x) for x in (srcs.get(k) or {}).values())
        row("Projections", "Sleeper " + ("players" if k == "sleeper" else "kickers & defenses"), "red" if (not v or "FAILED" in v) else "green", v or "missing")
    failed = [k for k, v in srcs.items() if "FAILED" in json.dumps(v) and not k.startswith("sleeper")]
    if failed: row("Projections", "Side sources", "grey", "blocked: " + ", ".join(failed) + " (backtest only - not used by any meter)")

# ---------- 3. the Yahoo read (Dom's Chrome, scheduled) ----------
ls = load("dispatch_out/live_state_latest.json")
read_t = iso(ls.get("stamp")) if ls else None
if not read_t: row("Yahoo", "Yahoo read", "red", "no Yahoo read found in the Dispatch output")
else:
    behind = SLOT and read_t < SLOT - dt.timedelta(minutes=15)
    stt = "green" if not behind else "red"
    det = f"last read {at(read_t)}; next scheduled {at(NEXT)}" if not behind else f"MISSED the {at(SLOT)} read - Live and the Dispatch still show {at(read_t)}"
    row("Yahoo", "Yahoo read (in your Chrome)", stt, det, read_t)
    # waiver night: rosters before the overnight waiver run are out of date until the next read
    if NPT.weekday() == 2 and read_t.astimezone(PT).date() < NPT.date():
        row("Yahoo", "Waiver results", "yellow", f"last night's waiver claims processed after the last read - rosters on Live, the Dispatch and the Scout don't show them until the {at(NEXT)} read")
runs = [load(os.path.relpath(p, D), D) for p in glob.glob(os.path.join(D, "runlog", "*.json"))]
runs = sorted([r for r in runs if r], key=lambda r: r.get("started") or "")
runs = [r for r in runs if r]
recent = [r for r in runs if iso(r.get("started")) and (NOW - iso(r["started"])).total_seconds() <= 30 * 3600]
# Oct 20 (Dom): a failed run that a LATER successful run of the same task has replaced is fixed, not broken - it stays
# listed (grey note) but no longer turns the light red. A run still marked "started" counts only once it is 45+ min old.
def _done_bad(r):
    if r.get("status") == "ok": return False
    if r.get("status") == "started" and (NOW - iso(r["started"])).total_seconds() < 45 * 60: return False
    return True
# Oct 31 (Dom: "Yahoo is broke"): this row used to be labeled "Yahoo" for EVERY read and counted the chain's own
# summary as a read, so a Ratcliffe (FTN) failure showed as a red Yahoo light. Now each source gets its own row
# under its own name, and the chain summary is reported on its own (it is healed by the next good chain run).
def _src(t):
    t = (t or "").lower()
    if "ftn" in t or "ratcliffe" in t: return "Ratcliffe (FTN)"
    if "koerner" in t or "fantasylabs" in t: return "Koerner (FantasyLabs)"
    if "chain" in t: return "Chain"
    return "Yahoo"
fails = [r for r in recent if _done_bad(r)]
healed = [r for r in fails if any(x.get("task") == r.get("task") and x.get("status") == "ok" and (x.get("started") or "") > (r.get("started") or "") for x in runs)]
open_f = [r for r in fails if r not in healed]
if not recent: row("Yahoo", "Read run log", "yellow", "no scheduled read logged in the last 30 h")
else:
    for src in ["Yahoo", "Ratcliffe (FTN)", "Koerner (FantasyLabs)", "Chain"]:
        rr = [r for r in recent if _src(r.get("task")) == src]
        if not rr: continue
        of = [r for r in open_f if r in rr]; hl = [r for r in healed if r in rr]
        last_ok = max([r.get("finished") or r.get("started") or "" for r in runs if _src(r.get("task")) == src and r.get("status") == "ok"] or [""])
        name = "Chain runs (last 30 h)" if src == "Chain" else f"{src} reads (last 30 h)"
        # the chain summary only repeats its reads' results (and the chain emails its own failures) - shown, never red,
        # or one failed chain would turn every later chain's system check red forever
        row(src, name, ("grey" if src == "Chain" else "red") if of else "green",
            f"{len(rr)} runs, {len(of)} failed and not yet redone" + (f"; last good {at(iso(last_ok))}" if last_ok and of else "")
            + (" - " + "; ".join(f"{r.get('task')} {r.get('step')}: {r.get('error')}"[:160] for r in of[-2:]) if of else "")
            + (f" ({len(hl)} earlier failure{'s' if len(hl) > 1 else ''} already fixed by a later good run)" if hl else ""),
            iso(rr[-1].get("finished")))

# ---------- 4. the Dispatch build (GitHub Actions) ----------
me = load("dispatch_out/meter_wk%s.json" % (ls or {}).get("week", ""))
build_t = ptstr(me.get("built_pt")) if me else None
if not me: row("Dispatch", "Dispatch build", "red", "no meter file for this week - the build did not finish")
else:
    stale = (NOW - build_t).total_seconds() / 3600 > (10 if not day_hours or NPT.hour < 8 else 4)
    used = me.get("sources", {}).get("yahoo_matchups", {}).get("pulled_pt")
    linked = ptstr(used) and read_t and abs((ptstr(used) - read_t).total_seconds()) <= 600
    row("Dispatch", "Dispatch build", "yellow" if stale else "green", "builds every 2 h in the day" + (" - no build in a while" if stale else ""), build_t)
    row("Dispatch", "Build used the latest Yahoo read", "green" if linked else "red", f"build read: {used}" + ("" if linked else f" but the latest read is {at(read_t)}"))
    pdf_ok = text("dispatch_out/Dark_Knight_Dispatch_latest.pdf") is not None or os.path.exists(os.path.join(F, "dispatch_out/Dark_Knight_Dispatch_latest.pdf"))
    row("Dispatch", "Dispatch PDF", "green" if pdf_ok else "red", "latest PDF published" if pdf_ok else "PDF missing")

# ---------- 5. Gotham (and its role-drift read) ----------
if me:
    g = me.get("sources", {}).get("gotham", {})
    gt = ptstr(g.get("pulled_pt")) or ptstr(g.get("note"))
    ok = g.get("status") == "OK" and gt and build_t and abs((gt - build_t).total_seconds()) <= 1800
    row("Gotham", "Gotham projections", "green" if ok else "red", (g.get("note") or g.get("status") or "missing")[:140], gt)
    # Oct 20 (Dom): count only starters who actually play this week - a bye / empty seat at 0 is correct, not a miss
    _fbl = [f"{lg_} {'yours' if sd_=='me' else 'opp'}: {p_['player']}" for lg_, L_ in (me.get("leagues") or {}).items()
            for sd_ in ("me", "op") for p_ in (L_.get("starters") or {}).get(sd_, [])
            if p_.get("gotham_src") == "yahoo-fallback" and p_.get("gs") != "nogame"]
    _cfl = [f"{lg_} {'yours' if sd_=='me' else 'opp'}: {p_['player']}" for lg_, L_ in (me.get("leagues") or {}).items()
            for sd_ in ("me", "op") for p_ in (L_.get("starters") or {}).get(sd_, [])
            if p_.get("gotham_src") == "consensus-fallback" and p_.get("gs") != "nogame"]
    fb = len(_fbl)
    # Oct 21 (Dom): a man with no 2026 snaps (a returner, a backup) has no usage for Gotham to read - by design he is priced at the
    # Yahoo/Sleeper average (grey, listed). Yellow only when Sleeper had no number either, so Gotham fell back to Yahoo alone.
    row("Gotham", "Players Gotham couldn't price", "green" if fb == 0 and not _cfl else "grey" if fb == 0 else "yellow",
        ((f"{fb} playing starter(s) on Yahoo's number alone: " + "; ".join(_fbl) + ". ") if fb else "")
        + ((f"{len(_cfl)} with no 2026 usage, priced at the Yahoo/Sleeper average: " + "; ".join(_cfl)) if _cfl else "")[:240]
        if (fb or _cfl) else "every playing starter priced by Gotham (bye-week seats at 0 not counted)")
    row("Gotham", "Role drift (inside Gotham)", "green" if ok else "red", "the climbing-role read runs inside every Gotham run" + ("" if ok else " - Gotham did not run, so neither did drift"))
    for k in ("sleeper_skill", "sleeper_kdef", "nfl_schedule"):
        s = me.get("sources", {}).get(k, {})
        row("Gotham", {"sleeper_skill": "Sleeper needle data", "sleeper_kdef": "Kicker/defense needle data", "nfl_schedule": "NFL schedule"}[k],
            "green" if s.get("status") == "OK" else "red", f"{s.get('rows')} rows, {s.get('age_h')} h old at build" if s else "missing")
    al = me.get("alarms") or []
    if al: row("Gotham", "Build alarms", "grey", f"{len(al)}: " + " | ".join(str(a)[:90] for a in al[:5]))

# ---------- 6. scoreboard (grades the engines against real results) ----------
res = load("feeds/proj/RESULTS.json"); sb = text("dispatch_out/scoreboard/scoreboard.txt"); gc = text("dispatch_out/scoreboard/graded.csv")
wk = (ls or {}).get("week")
if sb and gc:
    counts = {}
    for line in gc.splitlines()[1:]:
        w = line.split(",")[0]
        if w.isdigit(): counts[int(w)] = counts.get(int(w), 0) + 1
    # Oct 16 (Dom): judge the last COMPLETED week, not a week still being played. Mid-week (after Thursday night)
    # the current week holds only the men whose games are final - that is expected, not a partial grade.
    cw = (wk or 0) - 1
    lw = cw if cw in counts else (max((w for w in counts if w <= cw), default=None) if counts else None)
    full = counts.get(lw, 0) >= (120 if lw and lw <= 4 else 50)   # Weeks 2-4: a 500-man seed; Week 5 on: every starter in Dom's four matchups
    stt = "green" if lw == cw and full else "yellow"
    live_n = counts.get(wk or 0, 0)
    row("Checks", "Scoreboard (Yahoo vs Gotham vs Sleeper)", stt,
        f"graded through Week {lw} ({counts.get(lw, 0)} starters from your four matchups)" + ("" if full else " - fewer than expected, a partial grade")
        + (f"; Week {wk} in progress, {live_n} graded so far from finished games" if live_n else ""), ptstr(sb.splitlines()[0]))
else: row("Checks", "Scoreboard", "red", "scoreboard missing from the build")
if res: row("Checks", "Projection grading", "green" if (res.get("actuals_through_week") or 0) >= (wk or 0) - 1 else "yellow", f"actual results through Week {res.get('actuals_through_week')}", iso(res.get("graded_utc")))

# ---------- 7. the Scout (runs inside every Dispatch build, all four leagues) ----------
sc_ok = 0
for lg, lab in (("DKI", "DK I"), ("DKII", "DK II"), ("DKIII", "DK III"), ("DKIV", "DK IV")):
    b = load(f"dispatch_out/scout_state/scout_board_{lg}.json")
    t = iso(b.get("run")) if b else None
    linked = t and build_t and abs((t - build_t).total_seconds()) <= 1800
    sc_ok += bool(linked)
    if not linked: row("Scout", f"Scout {lab}", "red", "no board from the latest build" if b else "board missing", t)
row("Scout", "Scout ran in the latest build", "green" if sc_ok == 4 else "red", f"{sc_ok} of 4 leagues", build_t)
ros = text("yahoo_drop/scout/dk1_rosters_live.txt")
rt = ptstr(ros.splitlines()[0]) if ros else None
row("Scout", "Scout rosters + waiver lists", "green" if rt and read_t and abs((rt - read_t).total_seconds()) <= 1800 else "yellow",
    "read with the Yahoo read" if rt else "missing", rt)
# Oct 16 (Dom): the Yahoo weekly projections read (its own scheduled task) had silently not saved since Wed Oct 14 -
# the task "succeeded" without reaching Chrome - and nothing flagged it. The Scout only uses a file under 36 hours old.
yp = text("yahoo_drop/scout/yproj_dk1.txt")
if not yp:
    try:
        import urllib.request as _ur
        yp = _ur.urlopen("https://raw.githubusercontent.com/DomFantasy01/dk-feeds/main/yahoo_drop/scout/yproj_dk1.txt", timeout=20).read().decode()
    except Exception: yp = None
ypt = ptstr(yp.splitlines()[0]) if yp else None
yph = (NOW - ypt).total_seconds() / 3600 if ypt else None
# Oct 25 (Dom): the read runs every day at 7:38 AM, 12:38 PM and 4:38 PM - green means it has the newest run that should
# have finished (30 min after its start); an age bar alone turned the overnight gap yellow every morning.
def _yp_slot(now):
    t = now.astimezone(PT) - dt.timedelta(minutes=30)
    for d in range(0, 3):
        day = (t - dt.timedelta(days=d)).date()
        for h, m in ((16, 38), (12, 38), (7, 38)):
            c = dt.datetime(day.year, day.month, day.day, h, m, tzinfo=PT)
            if c <= t: return c
    return None
_ys = _yp_slot(NOW)
row("Scout", "Yahoo weekly projections (Scout's Yahoo half)",
    "green" if yph is not None and _ys is not None and ypt >= _ys - dt.timedelta(minutes=5) else ("yellow" if yph is not None and yph <= 36 else "red"),
    ("file missing" if yph is None else f"read {yph:.0f} h ago")
    + ("" if yph is not None and yph <= 36 else " - the Scout is running on its own model only; the projections task isn't saving (it needs Dom's computer)"), ypt)

# ---------- 8. the Radar ----------
ra = load("dispatch_out/radar_wk%s.json" % wk)
rf = text("dispatch_out/RADAR_FAILED.txt")
rtm = iso(ra.get("built_utc")) if ra else None
if rf: row("Radar", "Radar", "red", rf.strip()[:160])
else:
    linked = rtm and build_t and abs((rtm - build_t).total_seconds()) <= 1800
    row("Radar", "Radar (news per league)", "green" if linked else "red", "built with the latest Dispatch" if linked else "older than the latest build", rtm)

# ---------- 9. alerts on Dark Knight Live ----------
al = load("live/alerts.json", D)
if not al: row("Alerts", "Alert feed", "red", "live/alerts missing")
else:
    fc = iso(al.get("feeds_checked")); gen = iso(al.get("generated"))
    in_win = (NPT.hour > 5 or (NPT.hour == 5 and NPT.minute >= 30)) and NPT.hour < 23
    late = fc is None or (in_win and (NOW - fc).total_seconds() / 60 > 80)
    row("Alerts", "Hourly alert check", "red" if late else "green", "hourly at :05, 5 AM-11 PM" + (" - MISSED its last run" if late else ""), fc)
    bt = ptstr(al.get("built"))
    linked = bt and build_t and abs((bt - build_t).total_seconds()) <= 1800
    row("Alerts", "Alerts use the latest build", "green" if linked else "yellow", f"alerts built on {al.get('built')}")
    act = sum(1 for x in al.get("items", []) if x.get("active"))
    row("Alerts", "Live alerts", "grey", f"{act} live alerts on the page")

# ---------- 10. Dark Knight Live ----------
sd = load("live/state.json", D); md = load("live/models.json", D)
if sd:
    lt = iso(sd.get("stamp"))
    same = lt and read_t and lt >= read_t - dt.timedelta(minutes=10)
    # Oct 18 (Dom): a read that landed less than 90 minutes ago hasn't had its Live sync yet (the Sunday 4:52 AM read
    # waits for the 6:04 AM Live run) - that's waiting, not broken. Red only once a sync has had time to run.
    _fresh = read_t and (dt.datetime.now(dt.timezone.utc) - read_t) < dt.timedelta(minutes=90)
    row("Live", "Live shows the latest Yahoo read", "green" if same else "yellow" if _fresh else "red",
        "" if same else f"Live is on {at(lt)}, the latest read is {at(read_t)}" + (" - the next Live sync picks it up" if _fresh else ""), lt)
    if sd.get("alert"): row("Live", "Live read alert", "red", str(sd["alert"])[:160])
if md:
    H = md.get("health") or {}
    ch = (H.get("chain") or {})
    row("Live", "Chain check (read -> build -> Live)", {"ok": "green", "wait": "yellow", "refire": "yellow"}.get(ch.get("state"), "red"), ch.get("msg") or "no chain result", iso(H.get("checked")))
    mb = iso(md.get("stamp"))
    linked = mb and build_t and abs((mb - build_t).total_seconds()) <= 1800
    ck = iso(H.get("checked"))
    if linked: row("Live", "Live meters use the latest build", "green", "Gotham and Sleeper on Live match the latest build")
    elif ck and build_t and ck > build_t + dt.timedelta(minutes=5):
        row("Live", "Live meters use the latest build", "red", f"a chain check ran at {at(ck)} after the {at(build_t)} build but Live still shows {at(mb)}")
    else: row("Live", "Live meters use the latest build", "green", f"Live shows the {at(mb)} build; the {at(build_t)} build syncs at the next chain check (8:25 AM, 1:25 PM, 5:25 PM)")
    if H.get("build_failed"): row("Live", "Build failure flag", "red", str(H["build_failed"])[:160])

# ---------- 11. the morning brief ----------
br = text("dispatch_out/brief_latest.txt")
if not br: row("Brief", "Morning brief", "red", "brief_latest.txt missing")
else:
    bt = ptstr(br.splitlines()[0]); m = re.search(r"Yahoo read of (.+?PT)", br); bread = ptstr(m.group(1)) if m else None
    linked = bread and read_t and abs((bread - read_t).total_seconds()) <= 600
    row("Brief", "Morning brief", "green" if linked else "yellow", "built from the latest Yahoo read" if linked else "built from an older read", bt)
    if "HOLD ON" in br:   # Oct 30 (Dom): a brief on a Yahoo read from before a finished game is broken, not green
        row("Brief", "Brief numbers current", "red", re.search(r"HOLD ON[^\n]*", br).group(0)[:200], bt)
    else: row("Brief", "Brief numbers current", "green", "Yahoo matchup read is newer than every finished game this week", bt)

# ---------- 11b. GitHub's own jobs (Oct 30, Dom: "I'm not trusting anything" - hear about every failure email from us first) ----------
# Every GitHub run in the last 24 hours, including the Pages website step the system doesn't use. A failure the next run of
# the same job fixed is yellow (with both times); a job whose latest run failed is red.
try:
    import urllib.request
    rq = urllib.request.Request("https://api.github.com/repos/DomFantasy01/dk-feeds/actions/runs?per_page=100",
                                headers={"Accept": "application/vnd.github+json", "User-Agent": "dk-health"})
    runs = json.loads(urllib.request.urlopen(rq, timeout=30).read()).get("workflow_runs", [])
    day = [r for r in runs if iso(r.get("created_at")) and iso(r["created_at"]) >= NOW - dt.timedelta(hours=24) and r.get("status") == "completed"]
    byname = {}
    for r in sorted(day, key=lambda r: r["created_at"]): byname.setdefault(r["name"], []).append(r)
    bad = 0
    for nm, rs in byname.items():
        fails = [r for r in rs if r.get("conclusion") == "failure"]
        if not fails: continue
        bad += 1
        last = rs[-1]; side = " (GitHub's website step - your system doesn't use it)" if nm.startswith("pages build") else ""
        if last.get("conclusion") == "failure":
            row("GitHub jobs", nm, "red", f"latest run FAILED at {at(iso(last['created_at']))}{side}; {len(fails)} failure(s) in 24 h", iso(last["created_at"]))
        else:
            f0 = fails[-1]
            row("GitHub jobs", nm, "yellow", f"failed {len(fails)}x in 24 h, last at {at(iso(f0['created_at']))} - fixed itself, latest run OK at {at(iso(last['created_at']))}{side}", iso(f0["created_at"]))
    if not bad: row("GitHub jobs", "Every GitHub job", "green", f"{len(day)} runs in the last 24 hours, no failures")
except Exception as e:
    row("GitHub jobs", "Every GitHub job", "grey", f"couldn't read GitHub's run list ({type(e).__name__}) - check skipped")

# ---------- 12. known open problems (until marked fixed) ----------
ki = load("live_sync/known_issues.json") or {"issues": []}
for i in ki.get("issues", []):
    if not i.get("fixed"): row("Known issues", i.get("piece", "?"), i.get("level", "yellow"), i.get("what", ""))

# ---------- verdict ----------
rank = {"red": 3, "yellow": 2, "grey": 0, "green": 1}
reds = [r for r in R if r["status"] == "red"]; yel = [r for r in R if r["status"] == "yellow"]
worst = "red" if reds else "yellow" if yel else "green"
greens = sum(1 for r in R if r["status"] == "green")
head = (f"All clear - {greens} checks green." if worst == "green" else
        f"{len(reds)} broken, {len(yel)} to watch, {greens} green.")
out = {"checked": NOW.isoformat().replace("+00:00", "Z"), "checked_pt": NPT.strftime("%a %b %-d %-I:%M %p PT"), "worst": worst,
       "headline": head, "counts": {"red": len(reds), "yellow": len(yel), "green": greens},
       "first": [f"{r['group']}: {r['name']} - {r['detail']}" for r in reds + yel][:8], "rows": R,
       "read": read_t.isoformat() if read_t else None, "build": build_t.isoformat() if build_t else None}
json.dump(out, open(OUT, "w"), indent=1)
print("HEALTH", worst.upper(), "|", head)
for r in sorted(R, key=lambda r: -rank[r["status"]]):
    if r["status"] in ("red", "yellow"): print(f"  {r['status'].upper():6s} {r['group']}: {r['name']} - {r['detail']}")
