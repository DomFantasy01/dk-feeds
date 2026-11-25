"""EXPERT PANEL - since Nov 25 2026 (Dom): built on POINT PROJECTIONS, not ranking lists - see load_points/run below.
The history below is the Oct 24 ranking design, kept for the record (resolved_ranks still feeds expert_moves).
(Oct 24 2026, Dom). NAMED EXPERTS ONLY - no projection sites, no consensus averages
("you're just going to give me an average crappy team"). The panel's job is flags for analysis: show us what we
didn't see so we can dig in and learn. It never picks up a player; every add and drop is talked through with Dom.

THE PANEL - each expert's own weekly rankings from FantasyPros' public partner feed (pull_experts.py, GitHub, no browser):
  Mick Ciallela (Fantrax)            - FantasyPros in-season accuracy 2026: 1st of 167 (2nd of 165 on Oct 29)
  Tyler Orginski (FTN)               - added Oct 29 (Dom): 3rd of 165 through Week 7; lists every week, updated Sunday morning
  Jeff Ratcliffe (FTN)               - 4th
  Patrick Thorman (Establish the Run)- 5th
  Sean Koerner (Action Network)      - 7th
  Nathan Jahnke (PFF)                - 8th, BACKUP: votes only when one of the four has no list this week
Checked Oct 24: free, full QB/RB/WR/TE lists (110+ WRs each), PPR, a list every week (Weeks 5-7), and each made a final
update Sunday morning before kickoff in Weeks 5 and 6. Boone, Winks, Harmon, Eisenberg and the rest were removed.

A FLAG needs 3 of the panel (each with a rank on both men) to rank an available player 3+ spots above one of Dom's men
at the same position. Then the workup, from free data: available (free agent / waivers + clear date), injury tag,
last 3 games (touches, snaps, points) and workload trend, bye, this week's kickoff, Weeks 15-17 matchups, and the
bench man who would be the likely drop. Anything that fails the workup is listed as failed, never as a move.

usage: python3 expert_panel.py REPO [--stats stats_player_week_2026.csv] [--snaps snap_counts_2026.csv] [--games games.csv] [--out DIR]
"""
import sys, os, re, json, glob, datetime as dt
import pandas as pd, numpy as np
try:
    from zoneinfo import ZoneInfo; PT = ZoneInfo("America/Los_Angeles")
except Exception:
    PT = __import__("zoneinfo").ZoneInfo("America/Los_Angeles")

LEAGUES = [("DK I", 1, "269381", 2), ("DK II", 2, "1519795", 7), ("DK III", 3, "1507991", 2), ("DK IV", 4, "864215", 6)]
POS = ("QB", "RB", "WR", "TE")
PANEL = ["Jeff Ratcliffe", "Sean Koerner"]   # Nov 4: Brenton, Ciallela, Orginski, Thorman and Jahnke removed (Dom, Nov 3: "all useless")   # was:   # Oct 29 (Dom): Orginski added; Oct 31: Brenton (2026 accuracy #1) added
BACKUP = None   # Nov 4: Jahnke removed with the other four ranking experts
SHOW = {"Paul Brenton": "Brenton", "Mick Ciallela": "Ciallela", "Tyler Orginski": "Orginski", "Jeff Ratcliffe": "Ratcliffe", "Patrick Thorman": "Thorman", "Sean Koerner": "Koerner", "Nathan Jahnke": "Jahnke"}
NEED = 2          # experts that must agree (Nov 4: the panel is Ratcliffe + Koerner, so both must agree)
EDGE = 3          # ranks better by at least this many spots
TEAM_FIX = {"JAC": "JAX", "LA": "LAR", "WSH": "WAS", "OAK": "LV", "SD": "LAC", "STL": "LAR"}

def K(s):
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower().replace("’", "'"))
    return re.sub(r"[^a-z]", "", s)
def IK(name, team):
    """first initial + last name(s) + team - how Yahoo's tables ('M. Harrison Jr.') and full names meet."""
    parts = str(name).replace(".", ". ").split()
    if not parts: return ""
    return parts[0][0].lower() + K(" ".join(parts[1:])) + "|" + TEAM_FIX.get(str(team).upper(), str(team).upper())
def arg(f, d=None):
    a = sys.argv; return a[a.index(f) + 1] if f in a and a.index(f) + 1 < len(a) else d
def pt_str(t): return f"{t:%a %b} {t.day} {t.hour % 12 or 12}:{t:%M} {'AM' if t.hour < 12 else 'PM'}"

# ------------------------------------------------------------------ the experts' ranks, resolved to full names
EXPERT_STALE = ""   # set by load_experts when the saved lists are for an earlier NFL week than this one
def nfl_week_now():
    """The NFL week by the calendar: 2026 Week 1 began Tue Sep 8; each week runs Tuesday to Monday (Pacific)."""
    now = dt.datetime.now(PT)
    return max(1, (now.date() - dt.date(2026, 9, 8)).days // 7 + 1)
def load_experts(R):
    """Oct 27 (Dom): the experts publish each week's lists midweek. Until they do, the saved file still holds LAST
    week's lists - and those were being compared with this week's rosters as if current (a Week 7 rank calling Adonai
    Mitchell an upgrade over Tank Dell in Week 8). Now an earlier week's file gives no ranks at all, and every page
    that uses the panel says the new lists aren't out yet."""
    global EXPERT_STALE
    f = f"{R}/yahoo_drop/morning/expert_rankings.txt"; rows, heads = [], []
    if not os.path.exists(f): return rows, heads
    for ln in open(f):
        if ln.startswith("#"): heads.append(ln.strip("# \n")); continue
        p = ln.rstrip("\n").split("|")
        if len(p) >= 7 and p[3].isdigit() and p[2] in POS: rows.append(dict(site=p[0], expert=p[1], pos=p[2], rank=int(p[3]), name=p[4], team=p[5]))
    m = re.search(r"week (\d+)", heads[0]) if heads else None
    fw, nw = (int(m.group(1)) if m else 0), nfl_week_now()
    if fw and fw < nw and not os.environ.get("DK_EXPERTS_ANY_WEEK"):
        EXPERT_STALE = f"the experts' Week {nw} lists aren't out yet (the saved lists are Week {fw}), so no expert flags this build"
        return [], heads + [f"STALE: {EXPERT_STALE}"]
    EXPERT_STALE = ""
    return rows, heads

def name_index(R):
    """IK -> full name, from every Yahoo roster row and the Sleeper player list."""
    # Oct 24 fix: two players can share a key (Bijan and Brian Robinson, both ATL). A shared key is marked
    # ambiguous (None) so it can never hand one player's rank to the other; exact full names are matched first.
    idx, seen = {}, {}
    def put(name, team):
        k = IK(name, team)
        seen.setdefault(k, set()).add(K(name))
        idx[k] = name if len(seen[k]) == 1 else None
    try:
        sl = json.load(open(f"{R}/feeds/sleeper_players_min.json")).get("players", {})
        for p in sl.values():
            if p.get("name") and p.get("team") and p.get("pos") in POS: put(p["name"], p["team"])
    except Exception: pass
    for f in glob.glob(f"{R}/yahoo_drop/scout/dk*_rosters_live.txt"):
        for ln in open(f):
            q = ln.rstrip("\n").split("|")
            if len(q) >= 5 and not ln.startswith("#"): put(q[2], q[3])
    return idx

def _same(a, b):
    """same person, spelled differently ('D.J. Moore' / 'DJ Moore', 'Kenneth Walker III' / 'Kenneth Walker')"""
    return K(a) == K(b) or (K(a.split()[-1] if a.split() else a) == K(b.split()[-1] if b.split() else b) and K(a)[:2] == K(b)[:2])

def resolved_ranks(R):
    """K(full name) -> {expert: (pos, rank), '_name': full name}; plus the read stamps. Shared with morning_review."""
    rows, heads = load_experts(R); idx = name_index(R); out = {}
    for r in rows:
        k = IK(r["name"], r["team"])   # FantasyPros gives full names; keep our roster spelling when it is the same person
        full = idx.get(k) if k in idx else r["name"]
        if not full or K(full) != K(r["name"]) and not _same(full, r["name"]): full = r["name"]   # never another player's name
        if not full: continue
        d = out.setdefault(K(full), {}); d[r["expert"]] = (r["pos"], r["rank"]); d["_name"] = full
    stamps = []
    for h in heads:
        m = re.search(r"read live (\w{3} \w{3} \d{1,2} \d{4} \d{1,2}:\d{2} [AP]M)", h)
        if m: stamps.append(f"pulled {m.group(1)} PT")
        m = re.match(r"(.+?): .*last updated (\S+ \S+)", h)
        if m: stamps.append(f"{m.group(1)} updated {m.group(2)}")
    return out, stamps

# ------------------------------------------------------------------ Yahoo rosters, waivers, positions
def newest_inbox(R):
    for f in reversed(sorted(glob.glob(f"{R}/yahoo_drop/_inbox/pull_*.json"))):
        d = json.load(open(f))
        if any("all_rosters" in k for k in d["files"]): return d
    return None
def rosters(d):
    out = {}; k = [k for k in d["files"] if "all_rosters" in k][0]
    for ln in d["files"][k].splitlines():
        if "~" in ln and not ln.startswith("#"):
            lg, tid, names = ln.split("~", 2); out.setdefault(int(lg), {})[int(tid)] = [x for x in names.split("|") if x]
    return out
def scout_rows(R, n):
    f = f"{R}/yahoo_drop/scout/dk{n}_rosters_live.txt"; rows = []
    if os.path.exists(f):
        for ln in open(f):
            p = ln.rstrip("\n").split("|")
            if not ln.startswith("#") and len(p) >= 5: rows.append(dict(team=p[0], slot=p[1], name=p[2], nfl=p[3], pos=p[4], status=p[5] if len(p) > 5 else ""))
    return rows
def waivers(R, n):
    f = f"{R}/yahoo_drop/scout/dk{n}_waivers.txt"; W = {}
    if os.path.exists(f):
        for ln in open(f):
            if ln.startswith("#"): continue
            for x in ln.strip().split("|"):
                if "/" in x: a, c = x.rsplit("/", 1); W[K(a)] = c
    # Nov 17 (Dom): the API list stops at 400 names; a full list all clearing one future day = Yahoo's weekly waiver period,
    # when EVERY unrostered player is on waivers - so nobody missing from it is a free agent.
    try:
        import collections as _co, datetime as _dt2, zoneinfo as _zi2
        if len(W) >= 300:
            _d, _n = _co.Counter(W.values()).most_common(1)[0]
            _np = _dt2.datetime.now(_zi2.ZoneInfo("America/Los_Angeles"))
            if _n >= 0.9 * len(W) and _np.date() < _dt2.datetime.strptime(f"{_d} {_np.year}", "%b %d %Y").date():
                class _Blanket(dict):
                    def __contains__(s, k): return True
                    def __missing__(s, k): return _d
                    def get(s, k, default=None): return dict.get(s, k, _d)
                W = _Blanket(W)
    except Exception: pass
    return W

# ------------------------------------------------------------------ what he's done, schedule, matchups (free nflverse data)
class Facts:
    def __init__(s, stats_f, snaps_f, games_f, week):
        s.week = week
        s.st = pd.read_csv(stats_f, low_memory=False) if stats_f and os.path.exists(stats_f) else None
        s.sn = pd.read_csv(snaps_f, low_memory=False) if snaps_f and os.path.exists(snaps_f) else None
        g = pd.read_csv(games_f) if games_f and os.path.exists(games_f) else None
        s.g = g[(g.season == 2026) & (g.game_type == "REG")].copy() if g is not None else None
        if s.st is not None:
            s.st = s.st[s.st.season_type == "REG"].copy(); s.st["k"] = s.st.player_display_name.map(K)
            a = s.st[s.st.position.isin(POS)].groupby(["opponent_team", "position", "week"]).fantasy_points_ppr.sum().reset_index()
            s.allow = a.groupby(["opponent_team", "position"]).fantasy_points_ppr.mean()
        if s.sn is not None:
            if "game_type" in s.sn: s.sn = s.sn[s.sn.game_type == "REG"].copy()
            s.sn["k"] = s.sn.player.map(K)
    def done(s, k):
        if s.st is None: return {}
        x = s.st[s.st.k == k].sort_values("week")
        if not len(x): return dict(line="no NFL game logged this season")
        snaps = ""
        if s.sn is not None:
            y = s.sn[s.sn.k == k].sort_values("week").tail(3)
            if len(y) and "offense_pct" in y: snaps = " | snaps " + "/".join(f"{v*100:.0f}%" for v in y.offense_pct)
        use = []
        for _, r in x.tail(3).iterrows():
            u = [f"{int(r[c])} {lab}" for c, lab in (("carries", "car"), ("targets", "tgt"), ("attempts", "att")) if r.get(c, 0)]
            use.append(f"Wk{int(r.week)} {r.team}: {' '.join(u) or '0 touches'}, {r.fantasy_points_ppr:.1f} pts")
        trend = ""
        if len(x) >= 3:
            o = (x.carries.fillna(0) + x.targets.fillna(0)).tolist()
            trend = "rising" if o[-1] > np.mean(o[:-1]) * 1.25 else ("falling" if o[-1] < np.mean(o[:-1]) * .75 else "steady")
        team = TEAM_FIX.get(x.team.iloc[-1], x.team.iloc[-1])
        return dict(team=team, trend=trend, games=len(x),
                    line="; ".join(use) + snaps + f" | season {x.fantasy_points_ppr.mean():.1f} a game over {len(x)}" + (" | changed teams this season" if x.team.nunique() > 1 else ""))
    def schedule(s, team, pos):
        if s.g is None or not team: return {}
        t = "LA" if team == "LAR" else team; weeks = {}
        for _, r in s.g.iterrows():
            if r.home_team == t: weeks[int(r.week)] = ("vs", r.away_team, r.get("weekday"), r.get("gametime"))
            elif r.away_team == t: weeks[int(r.week)] = ("@", r.home_team, r.get("weekday"), r.get("gametime"))
        def lab(opp):
            try:
                v = s.allow.loc[(opp, pos)]; col = s.allow.xs(pos, level="position"); r = int((col > v).sum()) + 1
                return "easy" if r <= 10 else ("hard" if r >= 23 else "neutral")
            except Exception: return "?"
        def ptime(t):
            try: h, m = map(int, str(t).split(":")); h -= 3; return f"{h % 12 or 12}:{m:02d} {'AM' if h < 12 else 'PM'} PT"
            except Exception: return str(t)
        show = lambda o: TEAM_FIX.get(o, o)
        tw = weeks.get(s.week)
        return dict(bye=[w for w in range(s.week, 19) if w not in weeks],
                    playoffs=[f"Wk{w} {weeks[w][0]} {show(weeks[w][1])} ({lab(weeks[w][1])})" if w in weeks else f"Wk{w} bye" for w in (15, 16, 17)],
                    this_week=(f"{str(tw[2])[:3]} {ptime(tw[3])} {tw[0]} {show(tw[1])}" if tw else "bye this week"),
                    monday=bool(tw and str(tw[2]).startswith("Mon")))

# ------------------------------------------------------------------ the panel
def active_panel(ranks):
    have = {e for d in ranks.values() for e in d if e != "_name"}
    act = [e for e in PANEL if e in have]
    if len(act) < len(PANEL) and BACKUP in have: act.append(BACKUP)
    return act

# ------------------------------------------------------------------ POINTS, not rankings (Nov 25, Dom: "everything should be
# based on the point projections"). Each expert's own projected points, already converted to each league's scoring by the
# build (dispatch_out/*_scored.csv). Ratcliffe decides (his rest-of-season points per game, and this week); the others are
# shown beside him, never averaged. Any expert 2+ points off Ratcliffe on a flagged man = TALK mark (Nov 20 rule).
BAR_PTS, BAR_PCT = 2.0, 0.10   # flag: 2+ points AND 10%+ better than one of Dom's men at the position (value bar, Nov 9)
def _f(v):
    try: return float(v) if str(v).strip() not in ("", "nan", "None") else None
    except Exception: return None
def _avg(xs):
    xs = [x for x in xs if x is not None]; return sum(xs) / len(xs) if xs else None
def load_points(R):
    """{league n: {K(name): {'_name','_pos','_team', 'R': (wk, ros), 'Clay': (wk, ros), 'Draft Sharks': (wk, ros), 'Dr. Roto': (wk, None), 'Koerner': (wk, None)}}}"""
    import csv
    D, reads = {}, {}
    def put(n, name, team, pos, who, wk, ros):
        if pos not in POS or not name: return
        d = D.setdefault(int(n), {}).setdefault(K(name), {"_name": name, "_pos": pos, "_team": TEAM_FIX.get(str(team).upper(), str(team).upper())})
        d[who] = (wk, ros)
    src = [("ftn", "R", "read_pt"), ("clay", "Clay", "read"), ("draftsharks", "Draft Sharks", "read"), ("drroto", "Dr. Roto", "read"), ("koerner", "Koerner", "read_pt")]
    for f, who, rk in src:
        fp = f"{R}/dispatch_out/{f}_scored.csv"
        if not os.path.exists(fp): continue
        for r in csv.DictReader(open(fp)):
            wk = _f(r.get("wk"))
            if who == "R": ros = _f(r.get("ros_pg"))
            elif who in ("Clay", "Draft Sharks"): ros = _avg([_f(r.get(f"w{w}")) for w in range(13, 18)])
            else: ros = None
            put(r.get("lg"), r.get("name"), r.get("team"), r.get("pos"), who, wk, ros)
            reads.setdefault(who, r.get(rk))
    return D, reads

def run(R, stats_f, snaps_f, games_f, out_dir):
    global PANEL_NOW
    PANEL_NOW = ["Ratcliffe"]
    PTS, reads = load_points(R)
    inbox = newest_inbox(R); ROS = rosters(inbox) if inbox else {}
    # Nov 25: the Chrome inbox can miss a team page (DK II team 4) and its players then read as free agents
    # (Watson, DJ Moore, Bo Nix were flagged as pickups). The Yahoo API roster file covers every team - it wins when present.
    api_read = None
    for _lab, _n, _lid, _me in LEAGUES:
        _rows = scout_rows(R, _n)
        if _rows:
            _t = {}
            for _r in _rows: _t.setdefault(int(_r["team"]), []).append(_r["name"])
            ROS[_n] = _t
            try:
                _h = open(f"{R}/yahoo_drop/scout/dk{_n}_rosters_live.txt").readline()
                api_read = api_read or (re.search(r"read (\w{3} \w{3} \d{1,2} \d{1,2}:\d{2} [AP]M PT)", _h) or [None, None])[1]
            except Exception: pass
    week = nfl_week_now()
    F = Facts(stats_f, snaps_f, games_f, week)
    sl = json.load(open(f"{R}/feeds/sleeper_players_min.json")).get("players", {}) if os.path.exists(f"{R}/feeds/sleeper_players_min.json") else {}
    INJ = {K(p.get("name")): p for p in sl.values() if p.get("name")}
    stale = "" if reads.get("R") else "Ratcliffe's points file is missing - no flags until it is read"
    rep = dict(built=pt_str(dt.datetime.now(PT)), week=week, yahoo_read=api_read or (inbox or {}).get("read_pt"),
               experts_read=[f"{'Ratcliffe' if k == 'R' else k} {v}" for k, v in reads.items()], experts_stale=stale,
               panel=["Ratcliffe (points)"], basis="points",
               rule=f"Ratcliffe has him {BAR_PTS:.0f}+ points AND {BAR_PCT:.0%}+ better than one of your men at his position - rest of season per game, or this week - in this league's scoring; the other experts are shown beside him, never averaged",
               leagues={})
    fmt = lambda v: "-" if v is None else f"{v:.1f}"
    for lab, n, lid, me in LEAGUES:
        P = PTS.get(n, {})
        teams = ROS.get(n, {}); rostered = {K(p) for ps in teams.values() for p in ps}
        srows = scout_rows(R, n); W = waivers(R, n)
        slots = {K(r["name"]): r["slot"] for r in srows if r["team"] == str(me)}
        mine = [K(p) for p in teams.get(me, []) if slots.get(K(p), "BN") not in ("IR", "IR-R")]
        nm = lambda k: (P.get(k, {}).get("_name") or next((p for p in teams.get(me, []) if K(p) == k), k))
        rv = lambda k, i: (P.get(k, {}).get("R") or (None, None))[i]
        items = []
        for c, cd in P.items():
            if c in rostered or "R" not in cd: continue
            pos = cd["_pos"]; c_wk, c_ros = cd["R"]
            same = [d for d in mine if P.get(d, {}).get("_pos") == pos]
            best = None
            for d in same:
                d_wk, d_ros = rv(d, 0), rv(d, 1)
                why = []
                if c_ros is not None and d_ros is not None and c_ros - d_ros >= BAR_PTS and c_ros >= d_ros * (1 + BAR_PCT): why.append("rest of season")
                if c_wk is not None and d_wk is not None and c_wk - d_wk >= BAR_PTS and c_wk >= d_wk * (1 + BAR_PCT): why.append("this week")
                if not why: continue
                gain = (c_ros - d_ros) if "rest of season" in why else (c_wk - d_wk)
                if not best or gain > best["gain"]: best = dict(d=d, why=why, gain=gain)
            if not best: continue
            d = best["d"]
            others, talk = {}, []
            for who in ("Clay", "Draft Sharks", "Dr. Roto", "Koerner"):
                if who not in cd: continue
                wk, ros = cd[who]; dw, dr = (P.get(d, {}).get(who) or (None, None))
                others[who] = f"this week {fmt(wk)} v {fmt(dw)}" + (f", rest of season {fmt(ros)} v {fmt(dr)}" if ros is not None else "")
                if wk is not None and c_wk is not None and abs(wk - c_wk) >= 2: talk.append(f"{who} {wk:.1f} vs Ratcliffe {c_wk:.1f} this week")
                if ros is not None and c_ros is not None and abs(ros - c_ros) >= 2: talk.append(f"{who} {ros:.1f} vs Ratcliffe {c_ros:.1f} rest of season")
            fact = F.done(c); team = fact.get("team") or cd["_team"]
            sch = F.schedule(team, pos); tag = (INJ.get(c) or {}).get("inj") or ""
            bench = [b for b in mine if slots.get(b) == "BN" and rv(b, 1) is not None]
            same_b = [b for b in bench if P.get(b, {}).get("_pos") == pos]
            drop = min(same_b or bench, key=lambda b: rv(b, 1), default=None)
            stops, notes = [], []
            if tag in ("Out", "IR", "Doubtful", "Suspended", "PUP"): stops.append(f"tagged {tag}")
            if sch.get("monday"): notes.append("plays Monday night - once Sunday's games lock, nobody on your bench can replace him")
            if drop and d == drop: notes.append(f"the man he beats, {nm(drop)}, is also your weakest bench player")
            if talk: notes.append("TALK - experts split: " + "; ".join(talk))
            items.append(dict(name=cd["_name"], pos=pos, team=team, beats=nm(d), basis=best["why"], gain=round(best["gain"], 1),
                              agree="Ratcliffe", yes=["Ratcliffe"], no=[],
                              votes={"Ratcliffe": f"this week {fmt(c_wk)} v {fmt(rv(d, 0))}, rest of season {fmt(c_ros)} v {fmt(rv(d, 1))} a game"},
                              other_experts=others, talk=bool(talk),
                              available=f"on waivers until {W[c]} - takes a claim" if c in W else "free agent - instant add",
                              injury=tag, done=fact.get("line"), trend=fact.get("trend"), bye=sch.get("bye"), playoffs=sch.get("playoffs"),
                              this_week=sch.get("this_week"), drop_candidate=nm(drop) if drop else None, notes=notes, stops=stops,
                              verdict=("flag - worth analyzing" if not stops else "fails the workup: " + "; ".join(stops))))
        items.sort(key=lambda x: (bool(x["stops"]), -x["gain"], x["name"]))
        rep["leagues"][lab] = dict(passed=[x for x in items if not x["stops"]][:8], failed=[x for x in items if x["stops"]][:4])
    os.makedirs(out_dir, exist_ok=True)
    json.dump(rep, open(f"{out_dir}/expert_panel.json", "w"), indent=1, default=str)
    txt = render(rep); open(f"{out_dir}/expert_panel.txt", "w").write(txt + "\n"); print(txt)
    return rep

def card(x):
    o = "; ".join(f"{k} {v}" for k, v in x["other_experts"].items())
    return "\n".join([
        f"  {x['name']} ({x['team']} {x['pos']}) over your {x['beats']} - Ratcliffe +{x['gain']:.1f} a game ({' and '.join(x['basis'])})" + ("  [TALK]" if x.get("talk") else ""),
        f"     Ratcliffe (him v yours): {x['votes']['Ratcliffe']}." + (f" Beside him: {o}." if o else ""),
        f"     Available: {x['available']}." + (f" Injury tag: {x['injury']}." if x["injury"] else ""),
        f"     Done: {x['done'] or 'no stats found'}" + (f" | workload {x['trend']}" if x["trend"] else "") + ".",
        f"     This week: {x['this_week']}. Bye: {', '.join('Wk'+str(b) for b in (x['bye'] or [])) or 'none left'}. Playoffs: {', '.join(x['playoffs'] or []) or '?'}.",
        f"     If it came to a move, the likely drop is {x['drop_candidate']} - we talk it through first." + "".join(f" Note: {n}." for n in x["notes"]),
        f"     {x['verdict'][0].upper() + x['verdict'][1:]}."])

def render(rep):
    o = [f"EXPERT PANEL (point projections, each league's scoring) - Week {rep['week']}, built {rep['built']} PT. Rosters: Yahoo read {rep['yahoo_read']}.",
         *([f"NOT CURRENT: {rep['experts_stale']}."] if rep.get("experts_stale") else []),
         f"Ratcliffe decides; beside him: Clay, Draft Sharks, Dr. Roto, Koerner. Read: {'; '.join(rep['experts_read']) or 'MISSING'}.",
         f"A flag needs: {rep['rule']}. Flags are for analysis - nothing here is a pickup order."]
    for lab, L in rep["leagues"].items():
        o.append(f"\n{lab}")
        if not L["passed"]: o.append("  No flags: " + (rep["experts_stale"] + "." if rep.get("experts_stale") else "Ratcliffe has nobody available clearly above your men."))
        for x in L["passed"]: o.append(card(x))
        for x in L["failed"]: o.append(f"  (Ratcliffe liked {x['name']} over {x['beats']}, but he {x['verdict'].replace('fails the workup: ', 'fails: ')}.)")
    return "\n".join(o)

if __name__ == "__main__":
    R = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.getcwd()
    run(R, arg("--stats"), arg("--snaps"), arg("--games"), arg("--out", f"{R}/dispatch_out"))
