"""PLAYERS TO TALK ABOUT (Oct 31 2026, Dom: "show me very clearly up front ... pickups we should consider or should
absolutely do, so we don't miss them"; "what if they're really 10% but their workload is growing"; "bye weeks";
"my competitors, for blocking purposes"). One list per league, built every Dispatch build, four kinds:

  TALK NOW  - clears Dom's bar: 15%+ AND 2+ points a week better (Ratcliffe rest of season, his league's scoring) than the
              weakest starter at the position, or a Scout pick / before-lock flag. Says free agent or waivers-until.
  WATCH     - 10-15% better, or under the bar but RISING (workload/role news from the alert feed). Cheapest now.
  COVER     - a hole in the next three weeks (bye or injury) the Scout found, with the best fill it priced.
  BACKUP    - (Oct 31, Dom) for every starter of Dom's tagged Q / D / O whose game hasn't started: who on his own bench
              can take the seat, and the best free agents at that spot THIS WEEK (Ratcliffe), each with his own kickoff
              (when he locks). No drop is named - "this is live and stuff is happening all the time"; Dom picks it.
  BLOCK     - a free agent who would START for this week's or next week's opponent over one of his starters (15%+, 2+
              pts on Ratcliffe this week / rest of season). Grabbing him first takes points away from that rival.

Nothing here is a move - every line is "let's talk". Every number names its source and read time.
Inputs (all already in the repo after a build): dispatch_out/meter_wk<W>.json, ftn_scored.csv, koerner_scored.csv,
scout_state/scout_board_DK*.json, alerts_build.json, yahoo_drop/scout/dk*_rosters_live.txt + dk*_waivers.txt +
yproj_dk*.txt, yahoo_drop/sim/league_schedule.json.
Writes dispatch_out/talk_list.json and, with --brief, puts "Players to talk about" at the top of brief_latest.txt.
usage: python3 talk_list.py REPO [--brief]"""
import sys, os, json, csv, glob, re

R = sys.argv[1]; BRIEF = "--brief" in sys.argv
O = os.path.join
LG = [("DK I", "DKI", "269381", "1", 2), ("DK II", "DKII", "1519795", "2", 7), ("DK III", "DKIII", "1507991", "3", 2), ("DK IV", "DKIV", "864215", "4", 6)]
BAR, MINPTS, WATCH_LO = 0.15, 2.0, 0.10

def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower()))
def load(p, d=None):
    try: return json.load(open(p))
    except Exception: return d

W = max([int(re.search(r"_wk(\d+)", f).group(1)) for f in glob.glob(O(R, "dispatch_out/meter_wk*.json"))] or [0])
M = load(O(R, f"dispatch_out/meter_wk{W}.json"), {})
ALR = (load(O(R, "dispatch_out/alerts_build.json"), {}) or {}).get("items", [])
SCH = load(O(R, "yahoo_drop/sim/league_schedule.json"), {}) or {}

def scored(fn):
    out = {}
    try:
        for r in csv.DictReader(open(O(R, "dispatch_out", fn))):
            out[(r["lg"], nk(r["name"]))] = r
    except Exception: pass
    return out
RAT, KOE = scored("ftn_scored.csv"), scored("koerner_scored.csv")
RAT_AT = next((r.get("read_pt") for r in RAT.values()), "") or ""
KOE_AT = next((r.get("read_pt") for r in KOE.values()), "") or ""
# kickoffs this week, every team (Pacific) - from the NFL schedule the build downloads
import datetime as _dt
from zoneinfo import ZoneInfo as _ZI
KO = {}
for _gp in ("/home/claude/dksys/gate/fresh/games.csv", "/home/claude/dksys/data/latest/games.csv"):
    if not os.path.exists(_gp): continue
    try:
        for _r in csv.DictReader(open(_gp)):
            if _r.get("game_type") != "REG" or not _r.get("gameday") or not _r.get("gametime"): continue
            if _r["season"] != str(_dt.date.today().year): continue
            _t = _dt.datetime.strptime(_r["gameday"] + " " + _r["gametime"], "%Y-%m-%d %H:%M").replace(tzinfo=_ZI("America/New_York"))
            for _tm in (_r["home_team"], _r["away_team"]): KO[(int(_r["week"]), _tm)] = _t
        break
    except Exception: KO = {}
_FIX = {"LAR": "LA", "JAC": "JAX", "WSH": "WAS"}
def kick(team, wk):
    t = str(team or "").upper(); return KO.get((wk, _FIX.get(t, t)))
def ptlab(t):
    p = t.astimezone(_ZI("America/Los_Angeles")); return p.strftime("%a %-I:%M %p").replace("AM", "AM").replace("PM", "PM")
NOW = _dt.datetime.now(_dt.timezone.utc)
def fnum(x):
    try: return float(x)
    except Exception: return None
def rat(lgn, name):
    r = RAT.get((lgn, nk(name)));
    return (fnum(r["wk"]) if r else None), (fnum(r["ros_pg"]) if r else None), (r["pos"] if r else None), (r["team"] if r else None)
def koe(lgn, name):
    r = KOE.get((lgn, nk(name))); return fnum(r["wk"]) if r else None

out = {"week": W, "built": M.get("built_pt"), "ratcliffe_read": RAT_AT, "koerner_read": KOE_AT, "leagues": {}}
brief = []
for lab, key, lid, lgn, myid in LG:
    L = (M.get("leagues") or {}).get(lab) or {}
    me_st = (L.get("starters") or {}).get("me") or []
    # rosters: every team in the league, from the latest roster read
    rost, owner = {}, {}
    try:
        for ln in open(O(R, f"yahoo_drop/scout/dk{lgn}_rosters_live.txt")):
            if ln.startswith("#") or "|" not in ln: continue
            t, slot, name, tm, pos, st = (ln.rstrip("\n").split("|") + [""] * 6)[:6]
            rost.setdefault(t, []).append(dict(slot=slot, name=name, team=tm, pos=pos, status=st)); owner[nk(name)] = t
    except Exception: pass
    waiv = {}
    try:
        for ln in open(O(R, f"yahoo_drop/scout/dk{lgn}_waivers.txt")):
            if ln.startswith("#"): continue
            for x in ln.strip().split("|"):
                if "/" in x: a, b = x.rsplit("/", 1); waiv[nk(a)] = b
    except Exception: pass
    # the available pool: everyone Ratcliffe projects in this league who is on nobody's roster
    # (no roster read = no pool: without it every rostered star would look "available")
    pool = []
    if not owner: print(f"!! {lab}: no roster read - no pickups, backups or blocks this build")
    for (lg_, k_), r in RAT.items():
        if not owner or lg_ != lgn or k_ in owner: continue
        ros, wk = fnum(r["ros_pg"]), fnum(r["wk"])
        if ros is None and wk is None: continue
        pool.append(dict(name=r["name"], pos=r["pos"], team=r["team"], ros=ros or 0.0, wk=wk or 0.0, acq=(f"waivers until {waiv[k_]}" if k_ in waiv else "free agent")))
    # Dom's weakest starter at each position (this week's lineup, Ratcliffe rest of season, his league's scoring)
    weak = {}
    for s in me_st:
        pos = s.get("pos"); wk, ros, _, _ = rat(lgn, s.get("player"))
        v = ros if ros is not None else s.get("ratcliffe")
        if pos and v is not None and (pos not in weak or v < weak[pos][1]): weak[pos] = (s.get("player"), v, wk)
    talk, watch, cover, block = [], [], [], []
    rising = {nk(a.get("who")): a for a in ALR if a.get("lg") == lab and a.get("kind") == "rising" and a.get("active") is not False}
    prek = [a for a in ALR if a.get("lg") == lab and a.get("kind") == "radar_prekick" and a.get("active") is not False]
    board = load(O(R, f"dispatch_out/scout_state/scout_board_{key}.json"), {}) or {}
    scout_adds = {nk(a.get("name")): a for a in board.get("adds") or []}
    for p in pool:
        if p["pos"] not in weak: continue
        wn, wv, wwk = weak[p["pos"]]
        if not wv: continue
        gain = p["ros"] - wv; pct = gain / wv
        row = dict(name=p["name"], pos=p["pos"], team=p["team"], acq=p["acq"], over=wn, rat_ros=round(p["ros"], 1), over_ros=round(wv, 1),
                   pct=round(100 * pct), gain=round(gain, 1), rat_wk=round(p["wk"], 1), koe_wk=koe(lgn, p["name"]),
                   rising=(rising.get(nk(p["name"])) or {}).get("what"), scout=nk(p["name"]) in scout_adds)
        if pct >= BAR and gain >= MINPTS: talk.append(row)
        elif (pct >= WATCH_LO and gain >= 1.0) or (row["rising"] and pct >= 0): watch.append(row)
    # before-lock flags have their own section right under this one in the brief - not repeated here
    for k_, a in scout_adds.items():   # a Scout pick the simple test above missed - shown, never dropped silently
        if not any(nk(t["name"]) == k_ for t in talk) and (a.get("bar_pct") or 0) >= 100 * BAR and (a.get("gain") or 0) >= MINPTS:
            row = dict(name=a.get("name"), pos=a.get("pos"), team=a.get("team"), acq=a.get("acq"), over=a.get("drop"), pct=round(a.get("bar_pct") or 0),
                       gain=a.get("gain"), note="Scout pick (rest of season): " + (a.get("now") or "")[:200], scout=True)
            # worse than his starter THIS week = a stash for later weeks, not a pickup to make now
            (watch if "WORSE this week" in (a.get("now") or "") else talk).append(row)
    for g in board.get("gate1") or []:
        wks = [int(x) for x in re.findall(r"\b(\d{1,2})\b", (g.get("title") or "").split(",")[-1])]
        if "Fill" not in (g.get("title") or "") or not wks or min(wks) > W + 3: continue
        picks = [f"{p.get('name')} ({p.get('acq','')})" for p in (g.get("picks") or [])[:2]]
        cover.append(dict(title=g.get("title"), target=g.get("target"), mark=g.get("mark"), why=(g.get("why") or "")[:240], picks=picks))
    # opponents this week and next week: who would START for them over one of theirs
    sch = (SCH.get("schedule") or {}).get(lid) or {}; nm = (SCH.get("names") or {}).get(lid) or {}
    for wk_ in (W, W + 1):
        pair = next((x for x in (sch.get(str(wk_)) or "").split() if str(myid) in x.split("-")), None)
        if not pair: continue
        opp = [x for x in pair.split("-") if x != str(myid)][0]
        their = rost.get(opp) or []
        need = {"QB": 1, "RB": 2, "WR": 3, "TE": 1}
        for pos, n in need.items():
            mine = sorted([(rat(lgn, x["name"])[1] or 0, x["name"]) for x in their if x["pos"].split(",")[0] == pos and x["slot"] not in ("IR",)], reverse=True)
            if len(mine) < n: continue
            low_v, low_n = mine[n - 1]
            if low_v <= 0: continue
            for p in sorted([q for q in pool if q["pos"] == pos], key=lambda q: -q["ros"])[:3]:
                if p["ros"] >= low_v * (1 + BAR) and p["ros"] - low_v >= MINPTS:
                    block.append(dict(week=wk_, opp=nm.get(opp, f"team {opp}"), name=p["name"], pos=pos, team=p["team"], acq=p["acq"],
                                      would_start_over=low_n, rat_ros=round(p["ros"], 1), their_ros=round(low_v, 1)))
    # BACKUP: Dom's tagged starters whose game hasn't started - bench men first, then the best free agents this week
    backup = []
    ELIG = {"W/R/T": {"WR", "RB", "TE"}, "W/R": {"WR", "RB"}, "W/T": {"WR", "TE"}, "Q/W/R/T": {"QB", "WR", "RB", "TE"}}
    bench = (L.get("bench") or [])
    for s_ in me_st:
        stt = (s_.get("status") or "").upper()
        if stt not in ("Q", "D", "O") or s_.get("pos") in ("K",): continue
        k0 = kick(s_.get("team"), W)
        if k0 is not None and k0 <= NOW: continue                  # his game already started - nothing to swap
        okp = ELIG.get(s_.get("slot"), {s_.get("pos")})
        sw = s_.get("ratcliffe")
        mine = []
        for b_ in bench:
            if b_.get("pos") not in okp or (b_.get("status") or "").upper() in ("O", "IR", "D") or b_.get("slot") not in ("BN", None): continue
            kb = kick(b_.get("team"), W)
            if kb is None or kb <= NOW: continue                      # on bye or already playing
            mine.append(dict(name=b_.get("player"), pos=b_.get("pos"), team=b_.get("team"), wk=b_.get("ratcliffe"), locks=ptlab(kb), lock_utc=kb.astimezone(_dt.timezone.utc).isoformat()))
        fa = []
        for p_ in sorted([q for q in pool if q["pos"] in okp and q["acq"] == "free agent"], key=lambda q: -q["wk"]):
            kp = kick(p_["team"], W)
            if kp is None or kp <= NOW or p_["wk"] <= 0: continue
            fa.append(dict(name=p_["name"], pos=p_["pos"], team=p_["team"], wk=round(p_["wk"], 1), koe=koe(lgn, p_["name"]), locks=ptlab(kp), lock_utc=kp.astimezone(_dt.timezone.utc).isoformat()))
            if len(fa) >= 3: break
        mine.sort(key=lambda x: -(x.get("wk") or 0))
        backup.append(dict(starter=s_.get("player"), slot=s_.get("slot"), pos=s_.get("pos"), team=s_.get("team"), status=stt, wk=sw,
                           locks=ptlab(k0) if k0 else s_.get("kickoff"), lock_utc=k0.astimezone(_dt.timezone.utc).isoformat() if k0 else None,
                           bench=mine[:2], fa=fa))
    _tn = {nk(t["name"]) for t in talk}; watch = [w_ for w_ in watch if nk(w_["name"]) not in _tn]
    _seen = set(); watch = [w_ for w_ in watch if not (nk(w_["name"]) in _seen or _seen.add(nk(w_["name"])))]
    talk.sort(key=lambda x: -(x.get("pct") or 999)); watch.sort(key=lambda x: (-(1 if x.get("rising") else 0), -(x.get("pct") or 0)))
    out["leagues"][lab] = dict(talk=talk[:6], watch=watch[:6], cover=cover[:4], block=block[:4], backup=backup)
    # the brief, built to be heard
    parts = []
    for t in talk[:4]:
        if t.get("pct") is None: parts.append(f"TALK NOW: {t['name']}, {t['acq']}" + (f", locks {t['deadline']}" if t.get("deadline") else "")); continue
        parts.append(f"TALK NOW: {t['name']} ({t['pos']}, {t['team']}, {t['acq']}) - {t['pct']}% better than your {t['over']} over the rest of the season "
                     f"(Ratcliffe {t['rat_ros']} vs {t['over_ros']} a game, your league's scoring)" if t.get("over_ros") else f"TALK NOW: {t['name']} - {t.get('note','')}")
    for t in watch[:3]:
        if t.get("rat_ros") is None:
            parts.append(f"WATCH: {t['name']} ({t['pos']}, {t['acq']}) - {t.get('note','')}"); continue
        parts.append(f"WATCH: {t['name']} ({t['pos']}, {t['team']}, {t['acq']}) - {t['pct']}% over your {t['over']} (Ratcliffe {t['rat_ros']} vs {t['over_ros']})"
                     + (f"; rising - {t['rising']}" if t.get("rising") else ""))
    for c in cover[:2]:
        parts.append(f"COVER: {c['title']} - {c['target']}" + (f"; best fills {', '.join(c['picks'])}" if c["picks"] else ""))
    for b in backup:
        opts = [f"{x['name']} (your bench, {x['wk']})" for x in b["bench"]] + [f"{x['name']} (free agent, {x['wk']}, locks {x['locks']})" for x in b["fa"][:2]]
        parts.append(f"BACKUP if {b['starter']} ({b['status']}) sits - locks {b['locks']}: " + ("; ".join(opts) if opts else "no healthy option found"))
    for b in block[:2]:
        parts.append(f"BLOCK: {b['name']} ({b['pos']}, {b['acq']}) would start for {b['opp']} (Week {b['week']}) over {b['would_start_over']} - Ratcliffe {b['rat_ros']} vs {b['their_ros']}")
    brief.append(f"{lab}: " + ("; ".join(parts) if parts else "nothing to talk about - no free agent clears or nears the bar, no hole in the next three weeks, nothing to block") + ".")

PREV = load(O(R, "dispatch_out/talk_list.json"), {}) or {}
def _ids(lv):
    for kind in ("talk", "watch", "block"):
        for x in lv.get(kind) or []: yield kind, f"{kind}:{nk(x.get('name'))}", x
    for x in lv.get("cover") or []: yield "cover", "cover:" + nk(x.get("title")), x
    for x in lv.get("backup") or []: yield "backup", "backup:" + nk(x.get("starter")), x
for lab_, lv in out["leagues"].items():
    old = {i: x for _, i, x in _ids((PREV.get("leagues") or {}).get(lab_) or {})}
    for kind, i, x in _ids(lv):
        x["id"] = i; x["first_seen"] = (old.get(i) or {}).get("first_seen") or out.get("built")
json.dump(out, open(O(R, "dispatch_out/talk_list.json"), "w"), indent=1)
# Live reads the meter file the build saved; the talk list rides inside it so the hourly sync carries it with no new download
try:
    _mf = O(R, f"dispatch_out/meter_wk{W}.json"); _m = json.load(open(_mf))
    for _lab, _v in out["leagues"].items():
        if _lab in _m.get("leagues", {}): _m["leagues"][_lab]["talk"] = dict(_v, read=RAT_AT, built=out.get("built"))
    json.dump(_m, open(_mf, "w"), ensure_ascii=False)
except Exception as _e: print("TALK LIST not added to the meter file:", _e)
n = {k: sum(len(v[x]) for x in ("talk", "watch", "cover", "block", "backup")) for k, v in out["leagues"].items()}
print("TALK LIST:", " | ".join(f"{k} talk {len(v['talk'])} watch {len(v['watch'])} cover {len(v['cover'])} block {len(v['block'])} backup {len(v['backup'])}" for k, v in out["leagues"].items()))
if BRIEF:
    bf = O(R, "dispatch_out/brief_latest.txt")
    try: s = open(bf).read()
    except Exception: s = ""
    first, _, rest = s.partition("\n")
    rest = re.sub(r"\n*Players to talk about \(.*?\n\n", "\n\n", rest, count=1, flags=re.S)
    block_txt = (f"Players to talk about (every pickup to consider, the 10-15% watch list, holes in the next three weeks, and players to block; "
                 f"Ratcliffe read {RAT_AT}; nothing is added without your go):\n" + "\n".join(brief) + "\n\n")
    open(bf, "w").write(first + "\n\n" + block_txt + rest.lstrip("\n"))
    print("TALK LIST added to the top of the brief")
