# ACTION ITEMS, THE MORNING BRIEF, LIVE'S YAHOO STATE AND THE ADVICE LOG (Dom, Tue Oct 13 2026).
# Exec'd by fieldpos24.py before the Calls & Calibration page (page 2). Everything here comes from this build's own data:
# the meter (Dom's four matchups from the scheduled Yahoo read), the NFL schedule and the Scout boards.
#   ACTIONS   what needs Dom, most urgent first, each with a deadline -> page 2 section + dispatch_out/actions_latest.json
#   BRIEF     the same, spoken-style, one short paragraph a league   -> dispatch_out/brief_latest.txt (offered when Dom opens Claude)
#   LIVE      Dom's four matchups in Dark Knight Live's live/state shape -> dispatch_out/live_state_latest.json (one Yahoo reader)
#   ADVICE    every call logged once, graded when its week is final  -> dispatch_out/advice/advice_log.csv, ADVICE_SUM line
import json as _aj, os as _ao, re as _ar, glob as _ag, csv as _ac, datetime as _ad
import pandas as _apd
_AREPO = _ao.environ.get("GITHUB_WORKSPACE", "/home/claude/domfantasy01/dk-feeds")
_AOUT = _ao.path.join(_AREPO, "dispatch_out"); _ao.makedirs(_ao.path.join(_AOUT, "advice"), exist_ok=True)
_AMW = max(int(_ar.search(r"wk(\d+)", f).group(1)) for f in _ag.glob("/home/claude/dksys/data/latest/meter/meter_wk*.json"))
_AM = _aj.load(open(f"/home/claude/dksys/data/latest/meter/meter_wk{_AMW}.json"))
_ALG = ["DK I", "DK II", "DK III", "DK IV"]
_AKEY = {"DK I": "MOST", "DK II": "WINNERS", "DK III": "HERS&HIS", "DK IV": "NEXTDOOR"}
_APT = _ad.timezone(_ad.timedelta(hours=-7))
_ANOW = _ad.datetime.now(_APT)
_AG = _apd.read_csv("/home/claude/dksys/data/latest/games.csv", low_memory=False)
_AG = _AG[(_AG.season == 2026) & (_AG.game_type == "REG")]
def _a_pt(et):            # nflverse gametime is Eastern -> "10:00 AM" Pacific
    h, m = int(et[:2]), int(et[3:5]); h = (h - 3) % 24
    return f"{h % 12 or 12}:{m:02d} {'AM' if h < 12 else 'PM'}"
def _a_sunday(w):
    g = _AG[(_AG.week == w) & (_AG.weekday == "Sunday")]
    return ("Sunday's first kickoff, " + _a_pt(min(g.gametime))) if len(g) else "Sunday's first kickoff"
def _a_title(s):          # "MALY'S BETTER HALF" -> "Maly's Better Half" (str.title would give "Maly'S")
    return " ".join(w[:1].upper() + w[1:].lower() for w in (s or "").split())
def _a_short(n):
    p = (n or "").split(); return n if len(p) < 2 or n.endswith(" D") else p[-1] if p[-1] not in ("Jr.", "Jr", "Sr.", "II", "III", "IV") else p[-2]
def _a_ko(s):            # meter kickoff "Sun 10:00 am" -> "Sun 10:00 AM"
    return _ar.sub(r"(am|pm)$", lambda m: m.group(1).upper(), (s or "").strip())
_AOUTT = ("O", "IR", "IR-R", "NA", "SUSP", "SUS", "PUP")
_AWORD = {"O": "out", "IR": "on IR", "IR-R": "on IR", "NA": "not active", "SUSP": "suspended", "SUS": "suspended", "PUP": "on PUP",
          "D": "doubtful", "Q": "questionable"}
_APOSW = {"QB": "quarterback", "RB": "running back", "WR": "receiver", "TE": "tight end", "K": "kicker", "DEF": "defense"}

# Oct 21 (Dom): the latest injury note for a tagged starter, from ESPN's injury report (dated, first sentence)
_AINJ = {}
try:
    for _x in _aj.load(open("/home/claude/domfantasy01/dk-feeds/feeds/espn_injuries.json")).get("players", []):
        _AINJ[_x.get("name", "")] = _x
except Exception: pass
def _a_inj(nm):
    x = _AINJ.get(nm) or next((v for k, v in _AINJ.items() if k.replace(" Jr.", "").replace(" II", "") == nm.replace(" Jr.", "").replace(" II", "")), None)
    if not x or not x.get("detail"): return ""
    try: d = _ad.datetime.fromisoformat(str(x.get("date", "")).replace("Z", "+00:00")); ds = f"{d:%b} {d.day}"
    except Exception: return ""
    if (_ad.datetime.now(_ad.timezone.utc) - d).days > 5: return ""   # an old note says nothing about this week
    s = _ar.split(r"(?<=[.!?])\s+", str(x["detail"]).strip())[0]
    if len(s.split()) < 4:   # ESPN sometimes posts only the tag - use the newest RotoWire note on him instead
        try:
            best = None
            for _l in open("/home/claude/domfantasy01/dk-feeds/feeds/rotowire_history.jsonl"):
                _j = _aj.loads(_l); _t = str(_j.get("title") or "")
                if not _t.startswith(nm + ":"): continue
                _w = _ad.datetime.fromisoformat(str(_j.get("published_utc")).replace("Z", "+00:00"))
                if (_ad.datetime.now(_ad.timezone.utc) - _w).days <= 5 and (best is None or _w > best[0]): best = (_w, _t.split(":", 1)[1].strip(), str(_j.get("text") or ""))
            if not best: return ""
            d, s = best[0], best[1] + " - " + _ar.split(r"(?<=[.!?])\s+", best[2].strip())[0]
            return f" - latest (RotoWire, {d:%b} {d.day}): {s.rstrip('.')}"
        except Exception: return ""
    return f" - latest ({'ESPN'}{', ' + ds if ds else ''}): {s.rstrip('.')}"
# ---------------------------------------------------------------- ACTIONS
ACTIONS = []
_SUN = _a_sunday(_AMW)
_AHURT = {}
for _lab in _ALG:
    try: _B = _aj.load(open(f"/home/claude/dksys/scout/scout_board_{_lab.replace(' ', '')}.json"))
    except Exception: _B = {}
    for _mv in _B.get("moves", []):
        _m = _ar.search(r"out Weeks? (\d+)(?:-(\d+))?", _mv.get("text", ""))
        _src = _ar.search(r"- (ESPN|RotoWire|Sleeper|NFL)", _mv.get("text", ""))
        if _m and int(_m.group(1)) <= _AMW <= int(_m.group(2) or _m.group(1)):
            _AHURT[(_lab, _mv["name"])] = f"out Weeks {_m.group(1)}" + (f"-{_m.group(2)}" if _m.group(2) else "") + (f" per {_src.group(1)}" if _src else "")
for _lab in _ALG:
    _L = _AM["leagues"].get(_lab)
    if not _L: continue
    for _p in _L["starters"]["me"]:
        _nm, _st, _gs = _p["player"], (_p.get("status") or "").strip().upper(), _p.get("gs")
        _who = _nm if _p["pos"] != "DEF" else f"{_nm} defense"
        if not _p.get("team"):
            ACTIONS.append(dict(lg=_lab, rank=1, kind="empty", who=_nm, what=f"Fill the empty {_p['slot']} slot", by=f"before {_SUN}"))
        elif _p.get("window") is None and _gs in (None, "nogame"):
            ACTIONS.append(dict(lg=_lab, rank=1, kind="bye", who=_nm,
                                what=f"{_who} has no game this week. Start another {_APOSW.get(_p['pos'], 'player')}", by=f"before {_SUN}"))
        elif (_lab, _nm) in _AHURT and _gs in ("pre", "out", None):
            ACTIONS.append(dict(lg=_lab, rank=1, kind="out", who=_nm, what=f"{_who} is {_AHURT[(_lab, _nm)]}. Bench him", by=f"before his {_a_ko(_p.get('kickoff')) or _SUN} kickoff"))
        elif _st in _AOUTT and _gs in ("pre", "out", None):
            ACTIONS.append(dict(lg=_lab, rank=1, kind="out", who=_nm, what=f"{_who} is {_AWORD[_st]}. Bench him", by=f"before his {_a_ko(_p.get('kickoff')) or _SUN} kickoff"))
        elif _st in ("Q", "D") and _gs in ("pre", None):
            ACTIONS.append(dict(lg=_lab, rank=4, kind="check", who=_nm, what=f"{_who} is {_AWORD[_st]}"+_a_inj(_nm)+". Check his status", by=f"before his {_a_ko(_p.get('kickoff'))} kickoff"))
    try: _B = _aj.load(open(f"/home/claude/dksys/scout/scout_board_{_lab.replace(' ', '')}.json"))
    except Exception: _B = {}
    for _g in _B.get("gate2", []):
        _pk = _g.get("pick") or {}
        if _g.get("mark") != "red" or not _pk.get("name") or _g.get("act") is False: continue   # Oct 21: a Scout watch is not a to-do
        _acq = _pk.get("acq", ""); _m = _ar.search(r"clears (\w{3} \d{1,2})", _acq)
        if _m:
            _d = _ad.datetime.strptime(f"{_m.group(1)} 2026", "%b %d %Y")
            ACTIONS.append(dict(lg=_lab, rank=2, kind="claim", who=_pk["name"], what=f"Claim {_pk['name']} ({_pk.get('team','')} {_pk.get('pos','')}) for {_g.get('title','')}. Scout pick, your call" + ((". " + _pk["now"]) if _pk.get("now") else ""),
                                by=f"before waivers clear {_d:%a %b} {_d.day}"))
        else:
            ACTIONS.append(dict(lg=_lab, rank=5, kind="add", who=_pk["name"], what=f"Add {_pk['name']} ({_pk.get('team','')} {_pk.get('pos','')}), free agent, for {_g.get('title','')}. Scout pick, your call" + ((". " + _pk["now"]) if _pk.get("now") else ""),
                                by="any time"))
    for _mv in _B.get("moves", []):
        if _mv.get("kind") == "ir":
            _ytg = _ar.search(r"Yahoo tags him (\w+) today", _mv.get("text", ""))   # Oct 23 (Dom): Yahoo takes only Out/IR players on IR
            _wait = _ytg and _ytg.group(1) not in ("O", "IR", "IR-R", "PUP-R", "NA")
            ACTIONS.append(dict(lg=_lab, rank=3, kind="ir", who=_mv["name"], what=f"Move {_mv['name']} to IR" + (f" ({_AHURT[(_lab, _mv['name'])]})" if (_lab, _mv["name"]) in _AHURT else "")
                                + (f". Yahoo lists him {_ytg.group(1)} today, and IR takes only a player listed Out or IR - he sits on your bench until Yahoo flips him" if _wait else ". Frees a bench seat"),
                                by="when Yahoo lists him Out" if _wait else "any time"))
        elif _mv.get("kind") == "drop":
            ACTIONS.append(dict(lg=_lab, rank=3, kind="drop", who=_mv["name"], what=f"{_mv['name']} is a drop candidate (hurt, no IR seat). Your call", by="any time"))
ACTIONS.sort(key=lambda a: (a["rank"], _ALG.index(a["lg"])))
_aj.dump(dict(week=_AMW, built_pt=_AM.get("built_pt"), yahoo_read=_AM["sources"].get("yahoo_matchups", {}).get("pulled_pt"), items=ACTIONS),
         open(_ao.path.join(_AOUT, "actions_latest.json"), "w"), indent=1)

# ---------------------------------------------------------------- THE BRIEF (written to be read aloud)
def _a_rec(r):
    p = (r or "").split("-"); return "–".join(p[:2]) + (f"–{p[2]}" if len(p) > 2 and p[2] not in ("0", "") else "") if r else ""
_bl = [f"Morning brief, {_ANOW:%a %b} {_ANOW.day}, {_ANOW.hour % 12 or 12}:{_ANOW:%M} {'AM' if _ANOW.hour < 12 else 'PM'}. Week {_AMW}."]
for _lab in _ALG:
    _L = _AM["leagues"].get(_lab)
    if not _L: continue
    _st = _L.get("state", "UPCOMING"); _y = _L["needles"].get("yahoo"); _t = _L["totals"]["yahoo"]
    _s = f"{_lab}, {_a_rec(_L.get('record'))}, plays {_L.get('opp') or 'TBD'} ({_a_rec(_L.get('opp_record'))})."
    if _st == "FINAL":
        _me = sum(p["actual"] or 0 for p in _L["starters"]["me"]); _op = sum(p["actual"] or 0 for p in _L["starters"]["op"])
        _s += f" Final: {_me:.1f} to {_op:.1f}."
    elif _y is not None:
        _s += f" Yahoo has you at {_y}%, {_t[0]:.0f} to {_t[1]:.0f}" + (" with the game underway." if _st == "LIVE" else ".")
    _mine = [a for a in ACTIONS if a["lg"] == _lab]
    _s += (" To do: " + " ".join(f"{a['what']}, {a['by']}." for a in _mine)) if _mine else " Nothing needs you."
    _pcs = [p_["piece"].split(" - ")[0] for p_ in (_L.get("pieces") or [])]   # Oct 23 (Dom): Missing Pieces, read aloud
    if _pcs: _s += (" Missing piece: " if len(_pcs) == 1 else " Missing pieces: ") + "; ".join(_pcs).lower() + "."
    _bl.append(_s)
_n1 = [a for a in ACTIONS if a["rank"] == 1]
_bl.append(f"That's {len(ACTIONS)} item{'s' if len(ACTIONS) != 1 else ''}" + (f", {len(_n1)} of them lineup holes that score zero if left alone." if _n1 else ".") +
           f" Numbers from the Yahoo read of {_AM['sources'].get('yahoo_matchups', {}).get('pulled_pt', 'unknown')}.")
BRIEF = "\n\n".join(_bl)
open(_ao.path.join(_AOUT, "brief_latest.txt"), "w").write(BRIEF + "\n")

# ---------------------------------------------------------------- LIVE: Dom's four matchups in live/state's shape (one Yahoo reader)
def _a_utc(pt):
    s_ = (pt or "").replace(" PT", "").strip()
    if not _ar.search(r" \d{4} ", s_): s_ = _ar.sub(r"^(\w{3} \w{3} \d{1,2}) ", r"\g<1> " + _AM["built_pt"].split()[3] + " ", s_)   # "Tue Oct 13 05:44 AM" has no year
    try: t = _ad.datetime.strptime(s_, "%a %b %d %Y %I:%M %p")
    except Exception: return None
    return (t + _ad.timedelta(hours=7 if 3 <= t.month <= 10 else 8)).strftime("%Y-%m-%dT%H:%M:%SZ")
def _a_pl(p):
    gs = p.get("gs"); a = p.get("actual")
    when = "Final" if gs == "final" else "Bye" if gs == "nogame" else "In progress" if gs == "playing" else (p.get("kickoff") or "")
    pr = a if gs == "final" and a is not None else (p.get("yahoo") or 0.0)
    return dict(slot=p["slot"], name=p["player"], tm=p.get("team") or "", proj=round(float(pr), 2), actual=a, when=when, status=p.get("status") or "")
_LS = dict(week=_AMW, stamp=_a_utc(_AM["sources"].get("yahoo_matchups", {}).get("pulled_pt", "")),
           source=f"Dispatch Yahoo read {_AM['sources'].get('yahoo_matchups', {}).get('pulled_pt')} (build {_AM.get('built_pt')})", leagues=[])
_EXP = {}
for _lab in _ALG:
    _L = _AM["leagues"].get(_lab)
    if not _L: continue
    me, op = [_a_pl(p) for p in _L["starters"]["me"]], [_a_pl(p) for p in _L["starters"]["op"]]
    _pr, _opr = sum(p["proj"] for p in me), sum(p["proj"] for p in op)
    _LS["leagues"].append(dict(key=_AKEY[_lab], team=_L["me"], league=_L["league"], opp=_L.get("opp") or "", mgr="",
        score=round(sum(p["actual"] or 0 for p in me), 2), oppScore=round(sum(p["actual"] or 0 for p in op), 2),
        proj=round(_pr, 2), oppProj=round(_opr, 2), pct=_L["needles"].get("yahoo"), model=_L["needles"].get("yahoo"),
        margin=round(_pr - _opr, 2), sigma=None, state=_L.get("state"),
        left=sum(1 for p in _L["starters"]["me"] if p.get("gs") in ("pre", "playing")),
        oppLeft=sum(1 for p in _L["starters"]["op"] if p.get("gs") in ("pre", "playing")), players=me, oppPlayers=op))
    for p in _L["starters"]["me"]: _EXP.setdefault(p["player"], dict(starts=[], bench=[]))["starts"].append(_lab)
    for p in _L.get("bench", []): _EXP.setdefault(p["player"], dict(starts=[], bench=[]))["bench"].append(_lab)
_LS["exposure"] = sorted([dict(name=k, starts=len(v["starts"]), where=v["starts"], bench=v["bench"])
                          for k, v in _EXP.items() if len(v["starts"]) + len(v["bench"]) > 1], key=lambda e: (-e["starts"], e["name"]))
_aj.dump(_LS, open(_ao.path.join(_AOUT, "live_state_latest.json"), "w"), ensure_ascii=False)

# ---------------------------------------------------------------- THE ADVICE: log every call once, grade it when its week is final
_ALOGF = _ao.path.join(_AOUT, "advice", "advice_log.csv")
_ACOLS = ["id", "week", "league", "kind", "call", "pick", "versus", "made_pt", "status", "pick_pts", "versus_pts", "graded_pt"]
_ALOG = {}
if _ao.path.exists(_ALOGF):
    for _r in _ac.DictReader(open(_ALOGF)): _ALOG[_r["id"]] = _r
def _a_add(i, **k):
    if i not in _ALOG: _ALOG[i] = dict({c: "" for c in _ACOLS}, id=i, status="open", **k)
_amade = f"{_ANOW:%a %b} {_ANOW.day} {_ANOW.hour % 12 or 12}:{_ANOW:%M} {'AM' if _ANOW.hour < 12 else 'PM'}"
for a in ACTIONS:   # this week's lineup alarms and Scout picks
    if a["kind"] in ("bye", "out", "empty"):
        _a_add(f"{_AMW}|{a['lg']}|lineup|{a['who']}", week=_AMW, league=a["lg"], kind="lineup", call=a["what"], pick="", versus=a["who"], made_pt=_amade)
    elif a["kind"] in ("claim", "add"):
        _a_add(f"{_AMW}|{a['lg']}|pick|{a['who']}", week=_AMW, league=a["lg"], kind="pick", call=a["what"], pick=a["who"], versus="", made_pt=_amade)
def _a_firstko(w):
    g = _AG[_AG.week == w]
    if not len(g): return None
    r = g.sort_values(["gameday", "gametime"]).iloc[0]
    return _ad.datetime.strptime(f"{r.gameday} {r.gametime}", "%Y-%m-%d %H:%M") - _ad.timedelta(hours=3)   # Pacific, naive
_ATEAM = {}
try:
    _ST = _apd.read_csv("/home/claude/dksys/gate/fresh/stats_player_week_2026.csv", usecols=["player_display_name", "week", "team"], low_memory=False)
    for _r in _ST.dropna(subset=["player_display_name"]).itertuples(): _ATEAM[(norm(str(_r.player_display_name)), int(_r.week))] = _r.team
except Exception as _e: print("ADVICE: no team lookup -", _e)
def _a_gameko(w, names):
    ks = []
    for n in names:
        t = _ATEAM.get((norm(n), w))
        g = _AG[(_AG.week == w) & ((_AG.home_team == t) | (_AG.away_team == t))] if t else _AG.iloc[0:0]
        if len(g): ks.append(_ad.datetime.strptime(f"{g.iloc[0].gameday} {g.iloc[0].gametime}", "%Y-%m-%d %H:%M") - _ad.timedelta(hours=3))
    return min(ks) if ks else _a_firstko(w)
# backfill: the Scout's head-to-head calls since Oct 9 - "Wk 5 Montgomery ~11.9" in a red need means its top pick beats that man in Week 5
_AROS = {}
for _lab in _ALG:
    for _f in sorted(_ag.glob("/home/claude/dksys/data/latest/yahoo/wk*/dom_rosters.json")):
        try:
            for _p in _aj.load(open(_f))["leagues"].get(_lab, {}).get("players", []): _AROS.setdefault(_lab, set()).add(_p["player"])
        except Exception: pass
for _lab in _ALG:
    _fa = f"/home/claude/dksys/scout/scout_archive_{_lab.replace(' ', '')}.jsonl"
    if not _ao.path.exists(_fa): continue
    for _ln in open(_fa):
        try: _x = _aj.loads(_ln)
        except Exception: continue
        _run = _ad.datetime.fromisoformat(_x["run"]).replace(tzinfo=None)
        for _g in _x.get("gate1", []):
            if _g.get("mark") != "red" or not _g.get("picks"): continue
            for _wk, _ln_, _pp in _ar.findall(r"Wk (\d+) ([A-Z][\w.'\-]+(?: [A-Z][\w.'\-]+)?) ~([\d.]+)", _g.get("why", "")):
                _wk = int(_wk)
                if _wk > _AMW: continue                                     # calls about weeks not played yet wait until their week
                _full = [n for n in _AROS.get(_lab, ()) if n.split()[-1] == _ln_.split()[-1] or n == _ln_]
                if len(_full) != 1: continue
                _ko = _a_gameko(_wk, (_g["picks"][0], _full[0]))
                if _ko is None or _run >= _ko: continue                      # only calls made before either man's game kicked off
                _a_add(f"{_wk}|{_lab}|h2h|{_g['picks'][0]}|{_full[0]}", week=_wk, league=_lab, kind="h2h",
                       call=f"{_g['picks'][0]} over {_full[0]} at {_g['title'].split(',')[0]}", pick=_g["picks"][0], versus=_full[0],
                       made_pt=f"{_run:%a %b} {_run.day}")
# grade: a week is graded once every game in it has a final score and nflverse has its stat lines
try:
    import fc_model as _AFM
    if _ao.path.exists("/home/claude/dksys/gate/fresh/stats_player_week_2026.csv"): _AFM.STATS = "/home/claude/dksys/gate/fresh/stats_player_week_2026.csv"   # this build's nflverse pull
    _AFS = _AFM.load(); _AFR = {}
    def _a_pts(lab, nm, w):
        k = _ALG.index(lab) + 1
        if k not in _AFR: f = _AFM.frame(k, _AFS); f["k"] = f.player_display_name.map(norm); _AFR[k] = f
        f = _AFR[k]; d = f[(f.k == norm(nm)) & (f.week == int(w))]; return float(d.pts.sum()) if len(d) else 0.0
    _AMAXW = int(_AFR.get(1, _AFM.frame(1, _AFS)).week.max())
except Exception as _e:
    print("ADVICE: no stat lines to grade with -", _e); _a_pts = None; _AMAXW = 0
def _a_lastlineup(lab, w):
    fs = sorted(_ag.glob(f"/home/claude/dksys/data/latest/yahoo/wk{w}/dom_matchups_*.txt"), key=_ao.path.getmtime)
    lid = {"DK I": "269381", "DK II": "1519795", "DK III": "1507991", "DK IV": "864215"}[lab]
    for f in reversed(fs):
        for line in open(f):
            if line.startswith(lid + "#"):
                return [it.split("^")[1] for it in line.split("#", 1)[1].split("##")[0].split("|") if "^" in it]
    return None
for _r in _ALOG.values():
    if _r["status"] != "open": continue
    _w = int(_r["week"]); _g = _AG[_AG.week == _w]
    if not len(_g) or _g.result.isna().any() or _w > _AMAXW or _a_pts is None: continue
    if _r["kind"] == "h2h":
        a, b = _a_pts(_r["league"], _r["pick"], _w), _a_pts(_r["league"], _r["versus"], _w)
        _r.update(pick_pts=f"{a:.1f}", versus_pts=f"{b:.1f}", status="right" if a > b else "wrong" if a < b else "even", graded_pt=_amade)
    elif _r["kind"] == "lineup":
        lu = _a_lastlineup(_r["league"], _w)
        if lu is None: continue
        _r.update(status="followed" if norm(_r["versus"]) not in {norm(n) for n in lu} else "not followed", graded_pt=_amade)
    elif _r["kind"] == "pick":
        _r.update(pick_pts=f"{_a_pts(_r['league'], _r['pick'], _w):.1f}", status="logged", graded_pt=_amade)
with open(_ALOGF, "w", newline="") as _fh:
    _wr = _ac.DictWriter(_fh, fieldnames=_ACOLS); _wr.writeheader()
    for _r in sorted(_ALOG.values(), key=lambda r: (int(r["week"]), r["league"], r["id"])): _wr.writerow(_r)
_AV = list(_ALOG.values())
_h = [r for r in _AV if r["kind"] == "h2h" and r["status"] in ("right", "wrong", "even")]
_hr = sum(r["status"] == "right" for r in _h)
_lu = [r for r in _AV if r["kind"] == "lineup" and r["status"] in ("followed", "not followed")]
_lf = sum(r["status"] == "followed" for r in _lu)
_op = sum(r["status"] == "open" for r in _AV)
ADVICE_SUM = (("Scout head-to-head calls graded: " + (f"{len(_h)}, the pick outscored the man he would replace {_hr} times ({_hr / len(_h):.0%})." if _h else "none final yet.")) +
              (f"  Lineup alarms: {len(_lu)} graded, {_lf} fixed in time." if _lu else "  Lineup alarms: none graded yet.") + f"  Open calls waiting on games: {_op}.")
print("ACTIONS", len(ACTIONS), "| BRIEF", len(BRIEF), "chars | LIVE state", [l["key"] + ":" + str(l["state"]) for l in _LS["leagues"]], "| ADVICE", ADVICE_SUM)

# OCT13 brief count

# OCT14b actions carry the this-week line

# OCT21m brief: no watch to-dos, injury notes
