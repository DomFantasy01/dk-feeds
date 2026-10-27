"""EXPERT PANEL (Oct 24 2026, Dom). NAMED EXPERTS ONLY - no projection sites, no consensus averages
("you're just going to give me an average crappy team"). The panel's job is flags for analysis: show us what we
didn't see so we can dig in and learn. It never picks up a player; every add and drop is talked through with Dom.

THE PANEL - each expert's own weekly rankings from FantasyPros' public partner feed (pull_experts.py, GitHub, no browser):
  Mick Ciallela (Fantrax)            - FantasyPros in-season accuracy 2026: 1st of 167
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
    PT = dt.timezone(dt.timedelta(hours=-7))

LEAGUES = [("DK I", 1, "269381", 2), ("DK II", 2, "1519795", 7), ("DK III", 3, "1507991", 2), ("DK IV", 4, "864215", 6)]
POS = ("QB", "RB", "WR", "TE")
PANEL = ["Mick Ciallela", "Jeff Ratcliffe", "Patrick Thorman", "Sean Koerner"]
BACKUP = "Nathan Jahnke"
SHOW = {"Mick Ciallela": "Ciallela", "Jeff Ratcliffe": "Ratcliffe", "Patrick Thorman": "Thorman", "Sean Koerner": "Koerner", "Nathan Jahnke": "Jahnke"}
NEED = 3          # experts that must agree
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

def run(R, stats_f, snaps_f, games_f, out_dir):
    ranks, stamps = resolved_ranks(R)
    global PANEL_NOW
    PANEL_NOW = active_panel(ranks)
    inbox = newest_inbox(R); ROS = rosters(inbox)
    ef = f"{R}/yahoo_drop/morning/expert_rankings.txt"
    hd = open(ef).readline() if os.path.exists(ef) else ""
    week = int((re.search(r"week (\d+)", hd) or [0, 0])[1] or 0) if hd else 0
    F = Facts(stats_f, snaps_f, games_f, week)
    sl = json.load(open(f"{R}/feeds/sleeper_players_min.json")).get("players", {}) if os.path.exists(f"{R}/feeds/sleeper_players_min.json") else {}
    INJ = {K(p.get("name")): p for p in sl.values() if p.get("name")}
    rep = dict(built=pt_str(dt.datetime.now(PT)), week=week, yahoo_read=inbox.get("read_pt"), experts_read=stamps, experts_stale=EXPERT_STALE,
               panel=[SHOW.get(e, e) for e in PANEL_NOW], rule=f"{NEED} of {len(PANEL_NOW)} experts rank him {EDGE}+ spots above one of your men at his position", leagues={})
    for lab, n, lid, me in LEAGUES:
        teams = ROS.get(n, {}); rostered = {K(p) for ps in teams.values() for p in ps}
        srows = scout_rows(R, n); W = waivers(R, n)
        slots = {K(r["name"]): r["slot"] for r in srows if r["team"] == str(me)}
        mine = [K(p) for p in teams.get(me, []) if slots.get(K(p), "BN") != "IR"]
        nm = lambda k: (ranks.get(k, {}).get("_name") or next((p for p in teams.get(me, []) if K(p) == k), k))
        best = {}
        for c, cr in ranks.items():
            if c in rostered: continue
            for d in mine:
                dr = ranks.get(d, {}); yes, no, det = [], [], {}
                for e in PANEL_NOW:
                    if e in cr and e in dr and cr[e][0] == dr[e][0]:
                        det[SHOW[e]] = f"{cr[e][0]}{cr[e][1]} v {dr[e][0]}{dr[e][1]}"
                        (yes if dr[e][1] - cr[e][1] >= EDGE else no).append(SHOW[e])
                if len(yes) >= NEED:
                    b = best.get(c)
                    if not b or len(yes) > len(b["yes"]): best[c] = dict(d=d, yes=yes, no=no, det=det)
        def worst_rank(d):   # higher number = weaker in the experts' eyes; unranked counts as weakest
            v = [x[1] for k, x in ranks.get(d, {}).items() if k != "_name"]
            return sum(v) / len(v) if v else 999
        items = []
        for c, f in best.items():
            pos = next(v[0] for k, v in ranks[c].items() if k != "_name")
            fact = F.done(c); team = fact.get("team", "")
            sch = F.schedule(team, pos); tag = (INJ.get(c) or {}).get("inj") or ""
            # likely drop: the bench man the experts rank lowest - same position first; a bench man they don't rank at all
            # (on bye, hurt) is left out, because "unranked this week" is not the same as "worst"
            bench = [d for d in mine if slots.get(d) == "BN" and worst_rank(d) < 999]
            same = [d for d in bench if any(k != "_name" and v[0] == pos for k, v in ranks.get(d, {}).items())]
            drop = max(same or bench, key=worst_rank, default=None)
            stops, notes = [], []
            if tag in ("Out", "IR", "Doubtful", "Suspended", "PUP"): stops.append(f"tagged {tag}")
            if sch.get("monday"): notes.append("plays Monday night - once Sunday's games lock, nobody on your bench can replace him")
            if drop and f["d"] == drop: notes.append(f"the man he beats, {nm(drop)}, is also your weakest bench player")
            others = {SHOW.get(e, e): f"{v[0]}{v[1]}" for e, v in ranks[c].items() if e != "_name" and e not in PANEL_NOW}
            items.append(dict(name=nm(c), pos=pos, team=team, beats=nm(f["d"]), agree=f"{len(f['yes'])} of {len(f['yes'])+len(f['no'])}",
                              yes=f["yes"], no=f["no"], votes=f["det"], other_experts=others,
                              available=f"on waivers until {W[c]} - takes a claim" if c in W else "free agent - instant add",
                              injury=tag, done=fact.get("line"), trend=fact.get("trend"), bye=sch.get("bye"), playoffs=sch.get("playoffs"),
                              this_week=sch.get("this_week"), drop_candidate=nm(drop) if drop else None, notes=notes, stops=stops,
                              verdict=("flag - worth analyzing" if not stops else "fails the workup: " + "; ".join(stops))))
        items.sort(key=lambda x: (bool(x["stops"]), -len(x["yes"]), x["name"]))
        rep["leagues"][lab] = dict(passed=[x for x in items if not x["stops"]][:4], failed=[x for x in items if x["stops"]][:4])
    os.makedirs(out_dir, exist_ok=True)
    json.dump(rep, open(f"{out_dir}/expert_panel.json", "w"), indent=1, default=str)
    txt = render(rep); open(f"{out_dir}/expert_panel.txt", "w").write(txt + "\n"); print(txt)
    return rep

def card(x):
    o = ", ".join(f"{k} {v}" for k, v in x["other_experts"].items())
    return "\n".join([
        f"  {x['name']} ({x['team']} {x['pos']}) over your {x['beats']} - {x['agree']} panel experts agree",
        f"     Panel (him v yours): " + "; ".join(f"{k} {v}" for k, v in x["votes"].items()) + "." + (f" Off-panel experts on him: {o}." if o else ""),
        f"     Available: {x['available']}." + (f" Injury tag: {x['injury']}." if x["injury"] else ""),
        f"     Done: {x['done'] or 'no stats found'}" + (f" | workload {x['trend']}" if x["trend"] else "") + ".",
        f"     This week: {x['this_week']}. Bye: {', '.join('Wk'+str(b) for b in (x['bye'] or [])) or 'none left'}. Playoffs: {', '.join(x['playoffs'] or []) or '?'}.",
        f"     If it came to a move, the likely drop is {x['drop_candidate']} - we talk it through first." + "".join(f" Note: {n}." for n in x["notes"]),
        f"     {x['verdict'][0].upper() + x['verdict'][1:]}."])

def render(rep):
    o = [f"EXPERT PANEL (named experts only) - Week {rep['week']}, built {rep['built']} PT. Rosters: Yahoo read {rep['yahoo_read']}.",
         *([f"NOT CURRENT: {rep['experts_stale']}."] if rep.get("experts_stale") else []),
         f"Panel: {', '.join(rep['panel'])}. Experts read: {'; '.join(rep['experts_read']) or 'MISSING'}.",
         f"A flag needs {rep['rule']}. Flags are for analysis - nothing here is a pickup order."]
    for lab, L in rep["leagues"].items():
        o.append(f"\n{lab}")
        if not L["passed"]: o.append("  No flags: " + (rep["experts_stale"] + "." if rep.get("experts_stale") else "the panel doesn't rank anyone available clearly above your men."))
        for x in L["passed"]: o.append(card(x))
        for x in L["failed"]: o.append(f"  (Panel liked {x['name']} over {x['beats']}, but he {x['verdict'].replace('fails the workup: ', 'fails: ')}.)")
    return "\n".join(o)

if __name__ == "__main__":
    R = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.getcwd()
    run(R, arg("--stats"), arg("--snaps"), arg("--games"), arg("--out", f"{R}/dispatch_out"))
