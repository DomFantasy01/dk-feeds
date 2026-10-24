"""EXPERT PANEL (Oct 24 2026, Dom: "one expert's not enough - we need multiple experts, and compare").
Six named voices judge every available player against every man on Dom's roster. A name reaches Dom only when
(1) most of the panel agrees he beats one of Dom's men, (2) he is confirmed available (free agent or waivers + clear date),
and (3) the full workup passes: what he's done (usage and points, last 3 games), what he's projected (each voice by name),
rest of season vs Dom's 20-point bar, bye, Weeks 15-17 matchups, kickoff timing, injury tag, and who would have to go.
Nothing is a pick-up order: Dom decides every add and drop after we talk it through.

THE PANEL (each voice kept separate, never averaged into one number):
  Boone   - Justin Boone, Yahoo Sports weekly rankings (rank)          yahoo_drop/morning/boone_rankings.txt
  ESPN    - ESPN weekly projections (Mike Clay's projection model)       feeds/proj/espn/wk<W>_*.csv
  CBS     - CBS Sports weekly projections                                feeds/proj/cbs/wk<W>_*.csv
  FFToday - FFToday weekly projections                                    feeds/proj/fftoday/wk<W>_*.csv
  Sleeper - Sleeper weekly projections                                    feeds/proj/sleeper/wk<W>_*.csv
  Yahoo   - Yahoo weekly projections, this week through Week 17          yahoo_drop/scout/yproj_dk<n>.txt
Projections are put on one yardstick (full PPR, .25 a rush attempt - the leagues that reward carries) so voices compare.

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
FLEX = {"RB", "WR", "TE"}
VOICES = ["Boone", "ESPN", "CBS", "FFToday", "Sleeper", "Yahoo"]
NEED = 4           # voices that must agree
MINV = 4           # voices that must have numbers on both men before a vote counts
EDGE_PTS = 1.0     # a projection voice votes yes when the candidate is at least 1 point better this week
EDGE_RANK = 3      # Boone votes yes when the candidate ranks 3+ spots higher at the position
ROS_BAR = 20.0     # Dom's value bar: a season pickup must add ~20 points over the rest of the season
TEAM_FIX = {"JAC": "JAX", "LA": "LAR", "WSH": "WAS", "WAS": "WAS", "LV": "LV", "OAK": "LV", "SD": "LAC", "STL": "LAR"}
ESPN_TEAM = {1: "ATL", 2: "BUF", 3: "CHI", 4: "CIN", 5: "CLE", 6: "DAL", 7: "DEN", 8: "DET", 9: "GB", 10: "TEN", 11: "IND", 12: "KC", 13: "LV",
             14: "LAR", 15: "MIA", 16: "MIN", 17: "NE", 18: "NO", 19: "NYG", 20: "NYJ", 21: "PHI", 22: "ARI", 23: "PIT", 24: "LAC", 25: "SF",
             26: "SEA", 27: "TB", 28: "WAS", 29: "CAR", 30: "JAX", 33: "BAL", 34: "HOU"}

def K(s):
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower().replace("’", "'"))
    return re.sub(r"[^a-z]", "", s)
def arg(f, d=None):
    a = sys.argv; return a[a.index(f) + 1] if f in a and a.index(f) + 1 < len(a) else d
def num(x): return pd.to_numeric(x, errors="coerce").fillna(0)
def most(py=0, ptd=0, pint=0, ra=0, ry=0, rtd=0, rec=0, rcy=0, rctd=0, fl=0):
    return py / 25 + 6 * ptd - 2 * pint + .25 * ra + ry / 10 + 6 * rtd + rec + rcy / 10 + 6 * rctd - 2 * fl
def pt_str(t): return f"{t:%a %b} {t.day} {t.hour % 12 or 12}:{t:%M} {'AM' if t.hour < 12 else 'PM'}"

# ------------------------------------------------------------------ the voices
def newest(R, src, w):
    fs = sorted(glob.glob(f"{R}/feeds/proj/{src}/wk{w}_2*.csv")); return fs[-1] if fs else None
def stamp_of(fp):
    m = re.search(r"_(\d{4}-\d{2}-\d{2})T(\d{2})(\d{2})Z", fp or "")
    if not m: return None
    return dt.datetime.fromisoformat(f"{m.group(1)}T{m.group(2)}:{m.group(3)}+00:00").astimezone(PT)
def stat_frame(df, namecol, teamcol=None):
    c = lambda k: num(df[k]) if k in df else 0
    p = most(c("pass_yd"), c("pass_td"), c("pass_int"), c("rush_att"), c("rush_yd"), c("rush_td"), c("rec"), c("rec_yd"), c("rec_td"), c("fum_lost"))
    return {K(n): float(v) for n, v in zip(df[namecol], p) if isinstance(n, str)}
def load_espn(fp):  return stat_frame(pd.read_csv(fp), "name")
def load_sleeper(fp): return stat_frame(pd.read_csv(fp), "name")
def load_cbs(fp):
    df = pd.read_csv(fp); col = lambda k: num(df[k]) if k in df else 0
    nm = df.iloc[:, 0].astype(str).str.split(r"\s{2,}").map(lambda p: p[3] if len(p) >= 4 else p[0])
    p = most(col("Passing yds  Passing Yards"), col("Passing td  Touchdowns Passes"), col("Passing int  Interceptions Thrown"),
             col("Rushing att  Rushing Attempts"), col("Rushing yds  Rushing Yards"), col("Rushing td  Rushing Touchdowns"),
             col("Receiving rec  Receptions"), col("Receiving yds  Receiving Yards"), col("Receiving td  Receiving Touchdowns"), col("Misc fl  Fumbles Lost"))
    return {K(n): float(v) for n, v in zip(nm, p)}
def load_fftoday(fp):
    raw = pd.read_csv(fp, header=None, dtype=str).iloc[1:]; out, hdr = {}, None
    for i in range(len(raw)):
        r = raw.iloc[i]
        if "Player" in str(r[1]):
            grp = raw.iloc[i - 1].ffill() if i > 0 else r; hdr = [f"{str(g).strip()} {str(h).strip()}" for g, h in zip(grp, r)]; continue
        if hdr is None or pd.isna(r[1]) or str(r[1]).strip() in ("", "nan") or "Passing" in str(r[4]) or "Rushing" in str(r[4]): continue
        d = dict(zip(hdr, r)); g = lambda k: float(np.nan_to_num(pd.to_numeric(d.get(k), errors="coerce")))
        out[K(r[1])] = most(g("Passing Yard"), g("Passing TD"), g("Passing INT"), g("Rushing Att"), g("Rushing Yard"), g("Rushing TD"),
                            g("Receiving Rec"), g("Receiving Yard"), g("Receiving TD"))
    return out
def load_boone(R):
    f = f"{R}/yahoo_drop/morning/boone_rankings.txt"; B, head = {}, ""
    if not os.path.exists(f): return B, ""
    for ln in open(f):
        if ln.startswith("#"): head = ln.strip("# \n"); continue
        p = ln.rstrip("\n").split("|")
        if len(p) >= 5 and p[0] in POS and p[1].strip().isdigit(): B[K(p[2])] = (p[0], int(p[1]))
    return B, head
def load_yahoo(R, n, week):
    f = f"{R}/yahoo_drop/scout/yproj_dk{n}.txt"; wk, ros, head = {}, {}, ""
    if not os.path.exists(f): return wk, ros, head
    for ln in open(f):
        if ln.startswith("#"): head = ln.strip("# \n"); continue
        p = ln.rstrip("\n").split("|")
        try: w, v = int(p[0]), float(p[4])
        except (ValueError, IndexError): continue
        k = K(p[1])
        if w == week: wk[k] = v
        if w >= week: ros.setdefault(k, {})[w] = v
    return wk, ros, head

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
    f = f"{R}/yahoo_drop/scout/dk{n}_waivers.txt"; W, head = {}, ""
    if os.path.exists(f):
        for ln in open(f):
            if ln.startswith("#"): head = ln; continue
            for x in ln.strip().split("|"):
                if "/" in x: a, c = x.rsplit("/", 1); W[K(a)] = c
    return W, head

# ------------------------------------------------------------------ what he's done, schedule, matchups
class Facts:
    def __init__(s, stats_f, snaps_f, games_f, week):
        s.week = week
        s.st = pd.read_csv(stats_f, low_memory=False) if stats_f and os.path.exists(stats_f) else None
        s.sn = pd.read_csv(snaps_f, low_memory=False) if snaps_f and os.path.exists(snaps_f) else None
        g = pd.read_csv(games_f) if games_f and os.path.exists(games_f) else None
        s.g = g[(g.season == 2026) & (g.game_type == "REG")].copy() if g is not None else None
        if s.st is not None:
            s.st = s.st[s.st.season_type == "REG"].copy(); s.st["k"] = s.st.player_display_name.map(K)
            # points allowed to each position, per game, for the matchup labels
            a = s.st[s.st.position.isin(POS)].groupby(["opponent_team", "position", "week"]).fantasy_points_ppr.sum().reset_index()
            s.allow = a.groupby(["opponent_team", "position"]).fantasy_points_ppr.mean()
        if s.sn is not None:
            s.sn = s.sn[s.sn.game_type == "REG"].copy() if "game_type" in s.sn else s.sn; s.sn["k"] = s.sn.player.map(K)
    def team_of(s, k, fallback=""):
        if s.st is not None:
            x = s.st[s.st.k == k]
            if len(x): return TEAM_FIX.get(x.sort_values("week").team.iloc[-1], x.sort_values("week").team.iloc[-1])
        return TEAM_FIX.get(fallback.upper(), fallback.upper())
    def done(s, k):
        if s.st is None: return None
        x = s.st[s.st.k == k].sort_values("week")
        if not len(x): return dict(games=0, line="no NFL game logged this season")
        l3 = x.tail(3); team_now = x.team.iloc[-1]
        snaps = ""
        if s.sn is not None:
            y = s.sn[s.sn.k == k].sort_values("week").tail(3)
            if len(y) and "offense_pct" in y: snaps = " | snaps " + "/".join(f"{v*100:.0f}%" for v in y.offense_pct)
        use = []
        for _, r in l3.iterrows():
            u = []
            if r.get("carries", 0): u.append(f"{int(r.carries)} car")
            if r.get("targets", 0): u.append(f"{int(r.targets)} tgt")
            if r.get("attempts", 0): u.append(f"{int(r.attempts)} att")
            use.append(f"Wk{int(r.week)} {r.team}: {' '.join(u) or '0 touches'}, {r.fantasy_points_ppr:.1f} pts")
        moved = x.team.nunique() > 1
        trend = ""
        if len(x) >= 3:
            o = (x.carries.fillna(0) + x.targets.fillna(0)).tolist()
            trend = "rising" if o[-1] > np.mean(o[:-1]) * 1.25 else ("falling" if o[-1] < np.mean(o[:-1]) * .75 else "steady")
        return dict(games=len(x), team=team_now, moved=moved, avg=round(x.fantasy_points_ppr.mean(), 1), trend=trend,
                    line="; ".join(use) + snaps + (f" | season {x.fantasy_points_ppr.mean():.1f} a game over {len(x)}" ) + (f" | changed teams this season" if moved else ""))
    def schedule(s, team, pos):
        if s.g is None or not team: return None
        t = TEAM_FIX.get(team, team); weeks = {}
        for _, r in s.g.iterrows():
            if r.home_team == t: weeks[int(r.week)] = ("vs", r.away_team, r.get("gameday"), r.get("weekday"), r.get("gametime"))
            elif r.away_team == t: weeks[int(r.week)] = ("@", r.home_team, r.get("gameday"), r.get("weekday"), r.get("gametime"))
        bye = [w for w in range(1, 19) if w not in weeks]
        def lab(opp):
            if not hasattr(s, "allow"): return ""
            try:
                v = s.allow.loc[(opp, pos)]; col = s.allow.xs(pos, level="position")
                r = int((col > v).sum()) + 1   # 1 = gives up the most
                return "easy" if r <= 10 else ("hard" if r >= 23 else "neutral")
            except Exception: return ""
        po = [f"Wk{w} {weeks[w][0]} {TEAM_FIX.get(weeks[w][1], weeks[w][1])} ({lab(weeks[w][1])})" if w in weeks else f"Wk{w} bye" for w in (15, 16, 17)]
        tw = weeks.get(s.week)
        def ptime(t):
            try: h, m = map(int, str(t).split(":")); h -= 3; return f"{h % 12 or 12}:{m:02d} {'AM' if h < 12 else 'PM'} PT"
            except Exception: return str(t)
        ko = f"{str(tw[3])[:3]} {ptime(tw[4])} {tw[0]} {TEAM_FIX.get(tw[1], tw[1])}" if tw else "bye this week"
        return dict(bye=[b for b in bye if b >= s.week] or bye, playoffs=po, this_week=ko, monday=bool(tw and str(tw[3]).startswith("Mon")),
                    playoff_score=sum({"easy": 1, "hard": -1}.get(lab(weeks[w][1]), 0) for w in (15, 16, 17) if w in weeks))

# ------------------------------------------------------------------ the panel
def panel_values(k, voices, boone, yw):
    v = {}
    for name, d in voices.items():
        if k in d: v[name] = round(d[k], 1)
    if k in yw: v["Yahoo"] = round(yw[k], 1)
    if k in boone: v["Boone"] = f"{boone[k][0]}{boone[k][1]}"
    return v

def vote(c, d, voices, boone, yw):
    yes, no, detail = [], [], {}
    for name, src in list(voices.items()) + [("Yahoo", yw)]:
        if c in src and d in src:
            diff = src[c] - src[d]; detail[name] = f"{src[c]:.1f} v {src[d]:.1f}"
            (yes if diff >= EDGE_PTS else no).append(name)
    if c in boone and d in boone and boone[c][0] == boone[d][0]:
        detail["Boone"] = f"{boone[c][0]}{boone[c][1]} v {boone[d][0]}{boone[d][1]}"
        (yes if boone[d][1] - boone[c][1] >= EDGE_RANK else no).append("Boone")
    return yes, no, detail

def run(R, stats_f, snaps_f, games_f, out_dir):
    inbox = newest_inbox(R); ROS_ = rosters(inbox)
    boone, bhead = load_boone(R)
    week = int((re.search(r"week (\d+)", bhead) or [0, 0])[1]) if bhead else 0
    if not week:
        st = json.load(open(f"{R}/feeds/proj/status.json")); week = int(st.get("current_week", 0))
    files = {s: newest(R, s, week) for s in ("espn", "cbs", "fftoday", "sleeper")}
    load = {"espn": load_espn, "cbs": load_cbs, "fftoday": load_fftoday, "sleeper": load_sleeper}
    voices, vstamp = {}, {}
    for s, fp in files.items():
        label = {"espn": "ESPN", "cbs": "CBS", "fftoday": "FFToday", "sleeper": "Sleeper"}[s]
        if fp:
            try: voices[label] = load[s](fp); vstamp[label] = pt_str(stamp_of(fp)) if stamp_of(fp) else "?"
            except Exception as e: vstamp[label] = f"failed: {e}"
        else: vstamp[label] = "no file this week"
    vstamp["Boone"] = bhead.split("read live ")[-1].split(" (")[0] if bhead else "no file"
    F = Facts(stats_f, snaps_f, games_f, week)
    sl = json.load(open(f"{R}/feeds/sleeper_players_min.json")).get("players", {}) if os.path.exists(f"{R}/feeds/sleeper_players_min.json") else {}
    INJ = {K(p.get("name")): p for p in sl.values() if p.get("name")}
    rep = dict(built=pt_str(dt.datetime.now(PT)), week=week, yahoo_read=inbox.get("read_pt"), voices=vstamp, rules=dict(
        agree=f"{NEED} of the panel", edge=f"{EDGE_PTS} pt this week (Boone: {EDGE_RANK} spots)", season_bar=f"{ROS_BAR:.0f} points rest of season (Yahoo)"), leagues={})
    for lab, n, lid, me in LEAGUES:
        yw, yros, yhead = load_yahoo(R, n, week)
        vstamp.setdefault("Yahoo " + lab, yhead.split("read live ")[-1].split(" (")[0] if yhead else "no file")
        W, whead = waivers(R, n)
        teams = ROS_.get(n, {}); rostered = {K(p) for ps in teams.values() for p in ps}
        srows = scout_rows(R, n); pos_of = {K(r["name"]): (r["pos"], r["nfl"]) for r in srows}
        slots = {K(r["name"]): r["slot"] for r in srows if r["team"] == str(me)}
        mine = [p for p in teams.get(me, []) if slots.get(K(p), "BN") != "IR"]
        def pos(k):
            if k in pos_of: return pos_of[k][0]
            if k in boone: return boone[k][0]
            p = INJ.get(k); return p.get("pos") if p else None
        def name_of(k):
            for p in mine:
                if K(p) == k: return p
            return k
        # every available player any voice has numbers on
        pool = set()
        for d in list(voices.values()) + [yw]: pool |= set(d)
        pool |= set(boone)
        pool = {k for k in pool if k not in rostered and pos(k) in POS}
        names = {}
        for s, fp in files.items():
            if not fp: continue
        for r in srows: names[K(r["name"])] = r["name"]
        # display names for pool players from Boone/Sleeper
        for k, p in INJ.items(): names.setdefault(k, p.get("name"))
        bnames = {}
        try:
            for ln in open(f"{R}/yahoo_drop/morning/boone_rankings.txt"):
                p = ln.split("|")
                if len(p) >= 5 and p[1].strip().isdigit(): bnames[K(p[2])] = p[2]
        except Exception: pass
        names.update(bnames)
        starters = {K(p) for p in mine if slots.get(K(p)) not in ("BN", "IR", None)}
        found = []
        for c in pool:
            cp = pos(c)
            for p in mine:
                d = K(p); dp = pos(d)
                if not (dp == cp or (cp in FLEX and dp in FLEX and slots.get(d) == "W/R/T")): continue
                yes, no, det = vote(c, d, voices, boone, yw)
                if len(yes) + len(no) < MINV or len(yes) < NEED: continue
                rc = sum(yros.get(c, {}).values()) if c in yros else None
                rd = sum(yros.get(d, {}).values()) if d in yros else None
                ros_gain = (rc - rd) if (rc is not None and rd is not None) else None
                kind = "season" if (ros_gain is not None and ros_gain >= ROS_BAR) else ("fill" if d in starters else None)
                if not kind: continue
                found.append(dict(c=c, d=d, yes=yes, no=no, det=det, ros_gain=ros_gain, rc=rc, rd=rd, kind=kind))
        # one line per candidate: keep the man he beats by the most voices, then the biggest season gain
        best = {}
        for f in found:
            b = best.get(f["c"])
            if not b or (len(f["yes"]), f["ros_gain"] or -99) > (len(b["yes"]), b["ros_gain"] or -99): best[f["c"]] = f
        out = []
        for c, f in best.items():
            nm = names.get(c, c); cp = pos(c)
            fact = F.done(c) or {}
            team = fact.get("team") or (pos_of.get(c, ("", ""))[1] if c in pos_of else "")
            team = TEAM_FIX.get(str(team).upper(), str(team).upper())
            sch = F.schedule(team, cp) or {}
            inj = INJ.get(c, {}); tag = inj.get("inj") or ""
            avail = f"on waivers until {W[c]} - takes a claim" if c in W else "free agent - instant add"
            # who would go: Dom's bench man with the least Yahoo rest-of-season, never a starter or IR
            bench = [K(p) for p in mine if slots.get(K(p)) == "BN"]
            drop = min(bench, key=lambda k: sum(yros.get(k, {}).values()) if k in yros else 0, default=None)
            stop = []
            if tag in ("Out", "IR", "Doubtful", "Suspended", "PUP"): stop.append(f"tagged {tag}")
            if f["kind"] == "fill" and sch.get("monday"): stop.append("plays Monday night - no fallback once Sunday's bench locks")
            note = []
            if sch.get("monday"): note.append("plays Monday night: if he starts for you, nobody on Sunday's bench can replace him once those games lock")
            if drop and K(name_of(drop)) == f["d"]: note.append(f"the man he beats, {name_of(drop)}, is also your weakest bench player, so the swap is him for him")
            item = dict(name=nm, pos=cp, team=team, kind=f["kind"], beats=name_of(f["d"]), agree=f"{len(f['yes'])} of {len(f['yes'])+len(f['no'])}",
                        yes=f["yes"], no=f["no"], votes=f["det"], panel=panel_values(c, voices, boone, yw),
                        ros=round(f["rc"], 1) if f["rc"] is not None else None, ros_his=round(f["rd"], 1) if f["rd"] is not None else None,
                        ros_gain=round(f["ros_gain"], 1) if f["ros_gain"] is not None else None, available=avail, injury=tag,
                        done=fact.get("line"), trend=fact.get("trend"), bye=sch.get("bye"), playoffs=sch.get("playoffs"),
                        this_week=sch.get("this_week"), drop_candidate=name_of(drop) if drop else None, stops=stop, notes=note,
                        verdict="worth talking through" if not stop else "fails the workup: " + "; ".join(stop))
            out.append(item)
        out.sort(key=lambda x: (bool(x["stops"]), x["kind"] != "season", -(x["ros_gain"] or 0), -len(x["yes"])))
        rep["leagues"][lab] = dict(waivers_read=whead.strip("# \n")[:80], candidates=out,
                                   passed=[x for x in out if not x["stops"]][:3], failed=[x for x in out if x["stops"]][:5])
    os.makedirs(out_dir, exist_ok=True)
    json.dump(rep, open(f"{out_dir}/expert_panel.json", "w"), indent=1, default=str)
    txt = render(rep); open(f"{out_dir}/expert_panel.txt", "w").write(txt + "\n"); print(txt)
    return rep

def card(x):
    v = "; ".join(f"{k} {s}" for k, s in x["votes"].items())
    lines = [f"  {x['name']} ({x['team']} {x['pos']}) over your {x['beats']} - {x['kind'].upper()} - panel agrees {x['agree']}",
             f"     Available: {x['available']}." + (f" Injury tag: {x['injury']}." if x["injury"] else ""),
             f"     Panel this week (him v yours): {v}.",
             f"     Rest of season (Yahoo, Wk {'-'.join(['now','17'])}): " + (f"{x['ros']:.0f} v {x['ros_his']:.0f}, {x['ros_gain']:+.0f}" if x["ros_gain"] is not None else "not in Yahoo's read") + f" (bar is +{ROS_BAR:.0f}).",
             f"     Done: {x['done'] or 'no stats found'}" + (f" | workload {x['trend']}" if x["trend"] else "") + ".",
             f"     This week: {x['this_week']}. Bye: {', '.join('Wk'+str(b) for b in (x['bye'] or [])) or '?'}. Playoffs: {', '.join(x['playoffs'] or []) or '?'}.",
             f"     If added, the likely drop is {x['drop_candidate']} - we talk it through first." + "".join(f" Note: {n}." for n in x.get("notes", [])),
             f"     Verdict: {x['verdict']}."]
    return "\n".join(lines)

def render(rep):
    o = [f"EXPERT PANEL - Week {rep['week']}, built {rep['built']} PT. Rosters: Yahoo read {rep['yahoo_read']}.",
         "Voices: " + "; ".join(f"{k} {v}" for k, v in rep["voices"].items() if not k.startswith("Yahoo ")) + ".",
         f"A name shows only when {rep['rules']['agree']} agree he beats one of your men by {rep['rules']['edge']}, and he clears {rep['rules']['season_bar']} or fills a starter's slot this week."]
    for lab, L in rep["leagues"].items():
        o.append(f"\n{lab}")
        if not L["passed"]: o.append("  Nobody available clears the panel and the workup.")
        for x in L["passed"]: o.append(card(x))
        for x in L["failed"][:3]: o.append(f"  (Panel liked {x['name']} over {x['beats']}, but he {x['verdict'].replace('fails the workup: ', 'fails: ')}.)")
    return "\n".join(o)

if __name__ == "__main__":
    R = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.getcwd()
    run(R, arg("--stats"), arg("--snaps"), arg("--games"), arg("--out", f"{R}/dispatch_out"))
