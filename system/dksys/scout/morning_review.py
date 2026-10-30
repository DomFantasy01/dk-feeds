"""MORNING REVIEW (Oct 24 2026, Dom) - three checks that sit beside the Scout, in their own lane, so the Scout's
workload filters can never throw a name out of them. Built after the Marvin Harrison Jr. miss (DK III, Oct 21-23):
the Scout only looks for climbing workload, Harrison failed that test, and nothing else was watching.

  1. EXPERT CHECK   - every available player the named-expert panel (Ciallela, Ratcliffe, Thorman, Koerner; Jahnke backup; median rank) puts ahead of someone on Dom's roster
                      at the same position. Each flag carries the expert's name and both ranks. No workload test.
  2. NEW-ARRIVAL GATE - every player traded, signed, released or dropped in the last 72 hours who is available in one of
                      Dom's leagues gets a full line the day it happens: expert rank, Yahoo rest-of-season, how he can be had.
  3. TRANSACTION REVIEW - every move in all four leagues since the last review, sorted into: your own moves (with the
                      warning that a drop cancels any pending claim that listed that player), moves that hurt you (this
                      week's opponent got better), players we missed (a rival took someone the expert ranks above your man),
                      and openings (a rival dropped someone who beats your man).

Inputs (all read-only): yahoo_drop/morning/txn_dk1..4.txt + boone_rankings.txt (the 5 AM Chrome read),
the newest yahoo_drop/_inbox/pull_*.json (rosters, matchups), yahoo_drop/scout/dk*_rosters_live.txt + dk*_waivers.txt +
yproj_dk*.txt, feeds/rotowire_latest.json + feeds/espn_news.json (trade/sign/release news).
Outputs: dispatch_out/morning_review.json, dispatch_out/morning_review.txt, and a "Morning check" section in brief_latest.txt.

usage: python3 morning_review.py REPO [--since "2026-10-21T00:00"] [--asof "2026-10-23T13:00"] [--out DIR] [--no-brief]
  --since / --asof replay a past window (used to test: Oct 21-23 must flag Harrison in DK III).
"""
import sys, os, re, json, glob, datetime as dt
try:
    from zoneinfo import ZoneInfo; PT = ZoneInfo("America/Los_Angeles")
except Exception:
    PT = dt.timezone(dt.timedelta(hours=-7))

LEAGUES = [("DK I", 1, "269381", 2), ("DK II", 2, "1519795", 7), ("DK III", 3, "1507991", 2), ("DK IV", 4, "864215", 6)]
POS = ("QB", "RB", "WR", "TE")

def norm(n):
    n = (n or "").lower().replace("’", "'")
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", n)
    return re.sub(r"[^a-z]", "", n)

def arg(flag, default=None):
    a = sys.argv
    return a[a.index(flag) + 1] if flag in a and a.index(flag) + 1 < len(a) else default

def parse_when(s, year=2026):
    m = re.match(r"(\w{3}) (\d{1,2}), (\d{1,2}):(\d{2}) (am|pm)", s.strip())
    if not m: return None
    mo = dt.datetime.strptime(m.group(1), "%b").month
    h = int(m.group(3)) % 12 + (12 if m.group(5) == "pm" else 0)
    return dt.datetime(year, mo, int(m.group(2)), h, int(m.group(4)), tzinfo=PT)

def pt_str(t):
    return f"{t:%a %b} {t.day} {t.hour % 12 or 12}:{t:%M} {'AM' if t.hour < 12 else 'PM'}"

# ------------------------------------------------------------------ loaders
def load_boone(R):
    """Oct 24 (Dom): named experts only. Was Boone's list alone; now the panel's median rank (Ciallela, Ratcliffe,
    Thorman, Koerner) from expert_panel.resolved_ranks, so one expert never decides a line on his own."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import expert_panel as EP
    ranks, stamps = EP.resolved_ranks(R); B = {}
    for k, d in ranks.items():
        v = [x for e, x in d.items() if e in EP.active_panel(ranks)]
        if not v: continue
        pos = max(set(x[0] for x in v), key=[x[0] for x in v].count)
        rs = sorted(x[1] for x in v if x[0] == pos)
        B[norm(d["_name"])] = dict(name=d["_name"], pos=pos, rank=rs[len(rs) // 2], team="")
    head = "named-expert panel (median of " + ", ".join(EP.SHOW[e] for e in EP.active_panel(ranks)) + "), read live " + (stamps[0].replace("pulled ", "") if stamps else "?")
    return B, head

def load_txns(R, n):
    f = f"{R}/yahoo_drop/morning/txn_dk{n}.txt"
    rows, head = [], ""
    if not os.path.exists(f): return rows, "missing"
    for ln in open(f):
        if ln.startswith("#"): head = ln.strip("# \n"); continue
        p = ln.rstrip("\n").split("|")
        if len(p) < 7: continue
        t = parse_when(p[0])
        if not t: continue
        tp = p[5].split(" - ")
        rows.append(dict(t=t, team_id=p[1], team=p[2], action=p[3], player=p[4], nfl=tp[0].strip(),
                         pos=(tp[1].strip() if len(tp) > 1 else ""), detail=p[6]))
    return rows, head

def newest_inbox(R, asof=None):
    fs = sorted(glob.glob(f"{R}/yahoo_drop/_inbox/pull_*.json"))
    if asof:   # replay: the newest read taken at or before asof
        cut = asof.strftime("%Y%m%d_%H%M"); fs = [f for f in fs if os.path.basename(f)[5:18] <= cut]
    for f in reversed(fs):
        d = json.load(open(f))
        if any("all_rosters" in k for k in d["files"]): return d, f
    return None, None

def rosters_from_inbox(d):
    """league n -> team id -> [names]"""
    out = {}
    k = [k for k in d["files"] if "all_rosters" in k][0]
    for ln in d["files"][k].splitlines():
        if ln.startswith("#") or "~" not in ln: continue
        lg, tid, names = ln.split("~", 2)
        out.setdefault(int(lg), {})[int(tid)] = [x for x in names.split("|") if x]
    return out

def opponents_from_inbox(d):
    """league id -> (my team name, opponent name), from the matchup-window file (pairs listed consecutively)."""
    out = {}
    ks = [k for k in d["files"] if "league_windows" in k]
    if not ks: return out
    rows = [ln.split("~") for ln in d["files"][ks[0]].splitlines() if ln and not ln.startswith("#")]
    by = {}
    for r in rows: by.setdefault(r[0], []).append(r[1])
    for lid, names in by.items():
        for i in range(0, len(names) - 1, 2):
            a, b = names[i], names[i + 1]
            if a.startswith("Dark Knight"): out[lid] = (a, b)
            elif b.startswith("Dark Knight"): out[lid] = (b, a)
    return out

def scout_positions(R):
    P = {}
    for f in glob.glob(f"{R}/yahoo_drop/scout/dk*_rosters_live.txt"):
        for ln in open(f):
            p = ln.rstrip("\n").split("|")
            if len(p) >= 5 and not ln.startswith("#"): P[norm(p[2])] = (p[4], p[3], p[5] if len(p) > 5 else "")
    return P

def my_slots(R, n):
    """name -> slot for Dom's own team (BN/IR matter: IR players are not 'your man' at a position)."""
    f = f"{R}/yahoo_drop/scout/dk{n}_rosters_live.txt"; me = dict((x[1], x[3]) for x in LEAGUES)[n]
    S = {}
    if os.path.exists(f):
        for ln in open(f):
            p = ln.rstrip("\n").split("|")
            if len(p) >= 5 and not ln.startswith("#") and p[0] == str(me): S[norm(p[2])] = p[1]
    return S

def waivers(R, n):
    f = f"{R}/yahoo_drop/scout/dk{n}_waivers.txt"; W = {}
    if os.path.exists(f):
        for ln in open(f):
            if ln.startswith("#"): continue
            for x in ln.strip().split("|"):
                if "/" in x: nm, c = x.rsplit("/", 1); W[norm(nm)] = c
    return W

def yahoo_ros(R, n, week):
    f = f"{R}/yahoo_drop/scout/yproj_dk{n}.txt"; Y = {}
    if os.path.exists(f):
        for ln in open(f):
            p = ln.rstrip("\n").split("|")
            if ln.startswith("#") or len(p) < 5: continue
            try: w, v = int(p[0]), float(p[4])
            except ValueError: continue
            if w >= week: Y[norm(p[1])] = Y.get(norm(p[1]), 0.0) + v
    return Y

# ---------- Oct 30 (Dom): a REAL VERDICT on every pickup a rival makes ----------
# "I have no idea whether I need to pick up Lemon or not. Names never even come up, and somebody picked him up. Maybe he's
# just a one-game pickup." Every add by another team now says: what he is worth this week and the rest of the season
# (Ratcliffe first, Koerner and Yahoo beside him), his Weeks 15-17 games, whether he would have started for Dom (the
# 15%-and-2-points bar against the man he'd replace), and whether our system put him in front of Dom before he was taken.
import csv as _csv
_ROOT = os.environ.get("DK_ROOT", "/home/claude")
def _ldcsv(R, f):
    for p in (f"{_ROOT}/dksys/data/latest/{f}", f"{R}/dispatch_out/{f}"):
        if os.path.exists(p): return list(_csv.DictReader(open(p)))
    return []
def _fl(v):
    try: return float(v) if v not in ("", None, "nan") else None
    except Exception: return None
def expert_nums(R):
    RAT, KOR = {}, {}
    for r in _ldcsv(R, "ftn_scored.csv"): RAT[(str(r.get("lg")), norm(r.get("name")))] = (_fl(r.get("wk")), _fl(r.get("ros_pg")))
    for r in _ldcsv(R, "koerner_scored.csv"): KOR[(str(r.get("lg")), norm(r.get("name")))] = _fl(r.get("wk"))
    return RAT, KOR
def yahoo_weeks(R, n):
    f = f"{R}/yahoo_drop/scout/yproj_dk{n}.txt"; Y = {}
    if os.path.exists(f):
        for ln in open(f):
            p = ln.rstrip("\n").split("|")
            if ln.startswith("#") or len(p) < 5: continue
            try: Y.setdefault(norm(p[1]), {})[int(p[0])] = float(p[4])
            except ValueError: pass
    return Y
def sched(R):
    G = {}
    for f in (f"{_ROOT}/dksys/data/latest/games.csv",):
        if not os.path.exists(f): continue
        for r in _csv.DictReader(open(f)):
            if r.get("season") != "2026" or r.get("game_type") != "REG": continue
            w = int(r["week"]); G[(r["home_team"], w)] = "vs " + r["away_team"]; G[(r["away_team"], w)] = "at " + r["home_team"]
    return G
def flagged_before(R, nm, t):
    """Did any alert or Scout board show him to Dom before the claim went through?"""
    hits = []
    try:
        for x in json.load(open(f"{R}/dispatch_out/alerts_build.json")).get("items", []):
            if norm(x.get("who")) != norm(nm): continue
            fs = dt.datetime.fromisoformat(x.get("first_seen")).astimezone(PT)
            if fs < t: hits.append(f"{x.get('lg')} {x.get('kind')} alert {pt_str(fs)}")
    except Exception: pass
    return hits
NEWS_RX = re.compile(r"\b(trade[sd]?|traded to|acquire[sd]?|sign(s|ed)|re-sign|released?|waive[sd]|claimed off waivers|promoted)\b", re.I)
def news_arrivals(R, since):
    """player name -> short reason, from the news feeds (trade/sign/release words in the headline or first line)."""
    out = {}
    for f in ("feeds/rotowire_latest.json", "feeds/espn_news.json", "feeds/news_extra.json"):
        try: d = json.load(open(f"{R}/{f}"))
        except Exception: continue
        items = d.get("items") if isinstance(d, dict) else d
        for it in items or []:
            title = it.get("title") or it.get("headline") or ""; txt = (it.get("text") or it.get("description") or "")[:240]
            ts = it.get("published_utc") or it.get("published") or ""
            try: t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception: continue
            if t < since or not NEWS_RX.search(title + " " + txt): continue
            nm = title.split(":")[0].strip()
            if 1 < len(nm.split()) <= 4: out.setdefault(norm(nm), (nm, f"news {t.astimezone(PT):%b %d}: {title[:90]}"))
    return out

# ------------------------------------------------------------------ the review
def run(R, since, asof, out_dir, write_brief):
    B, bhead = load_boone(R)
    inbox, inbox_f = newest_inbox(R, asof)
    if not inbox: raise SystemExit("no Yahoo read with rosters in yahoo_drop/_inbox")
    ROS = rosters_from_inbox(inbox); OPP = opponents_from_inbox(inbox); SP = scout_positions(R)
    week = int((re.search(r"Week (\d+)", bhead) or re.search(r"week (\d+)", bhead) or [0, 0])[1] or 0) if bhead else 0
    def posof(nm):
        b = B.get(norm(nm))
        if b and b.get("pos"): return b["pos"]
        s = SP.get(norm(nm)); return s[0] if s else None
    def rk(nm):
        b = B.get(norm(nm)); return b.get("rank") if b else None
    def rtxt(nm):
        b = B.get(norm(nm))
        return f"panel {b['pos']}{b['rank']}" if b and b.get("rank") else "not ranked by the expert panel this week (bye, hurt or deep)"

    news = news_arrivals(R, since)
    RAT, KOR = expert_nums(R); GS = sched(R)
    TEAMOF = {}
    for k_, v_ in scout_positions(R).items(): TEAMOF[k_] = v_[1].upper()
    report = dict(built=pt_str(dt.datetime.now(PT)), window=dict(since=pt_str(since.astimezone(PT)), asof=pt_str(asof.astimezone(PT))),
                  sources=dict(boone=bhead, yahoo_read=inbox.get("read_pt"), yahoo_file=os.path.basename(inbox_f)), leagues={})
    for lab, n, lid, me in LEAGUES:
        txns, thead = load_txns(R, n)
        txns = [x for x in txns if x["t"] <= asof]
        teams = ROS.get(n, {})
        rostered = {norm(p) for tid, ps in teams.items() for p in ps}
        # replay: a player added inside the window was still available before that moment - put dropped men back out
        mine_names = teams.get(me, [])
        slots = my_slots(R, n)
        mine = [p for p in mine_names if slots.get(norm(p), "BN") != "IR"]
        W = waivers(R, n); Y = yahoo_ros(R, n, week or 1)
        # Dom's worst-ranked man at each position (only men the panel ranks this week - a bye-week player is not 'worst')
        worst = {}
        for p in mine:
            ps, r = posof(p), rk(p)
            if ps in POS and r and (ps not in worst or r > worst[ps][1]): worst[ps] = (p, r)
        def beats(nm):
            ps, r = posof(nm), rk(nm)
            if ps in POS and r and ps in worst and r <= worst[ps][1] - 3: return worst[ps]   # 3+ spots better, so a coin-flip rank gap is not a flag
            return None
        recent_drop = {norm(x["player"]): x["t"] for x in reversed(txns) if x["action"] == "Dropped" and asof - x["t"] < dt.timedelta(hours=60)}
        def how(nm):
            c = W.get(norm(nm))
            if c: return f"on waivers until {c}"
            if norm(nm) in recent_drop: return f"just dropped {pt_str(recent_drop[norm(nm)])} - on waivers about two days, so it takes a claim"
            return "free agent - add any time"
        YW = yahoo_weeks(R, n); WK = min((w for d in YW.values() for w in d), default=week or 0)   # the read starts at the current week
        def verdict(nm, pos, t=None):
            """One line: worth this week / rest of season, Weeks 15-17, vs the man he'd replace on Dom's roster, flagged or not."""
            k = norm(nm); rw, rr = RAT.get((str(n), k), (None, None)); kw = KOR.get((str(n), k)); yw = (YW.get(k) or {})
            elig = {"QB": {"QB"}, "RB": {"RB"}, "WR": {"WR"}, "TE": {"TE"}}[pos]
            flexok = pos in ("RB", "WR", "TE")
            st = [p for p in mine if posof(p) == pos or (flexok and posof(p) in ("RB", "WR", "TE") and slots.get(norm(p), "BN") in ("W/R/T", "W/R", "W/T"))]
            st = [p for p in st if slots.get(norm(p), "BN") not in ("BN", "IR")]
            bn = [p for p in mine if posof(p) == pos and slots.get(norm(p), "BN") == "BN"]
            ros = lambda p: (RAT.get((str(n), norm(p)), (None, None))[1])
            wkv = lambda p: (RAT.get((str(n), norm(p)), (None, None))[0])
            weak = min([p for p in st if ros(p) is not None], key=ros, default=None)
            clr = lambda a, b: a is not None and b is not None and a - b >= 2 and a >= b * 1.15
            if weak and clr(rr, ros(weak)): tag = f"STARTER UPGRADE over your {weak} the rest of the season ({rr:.1f} vs {ros(weak):.1f} a game, Ratcliffe)"
            elif weak and clr(rw, wkv(weak)): tag = f"ONE-WEEK FILL: beats your {weak} this week ({rw:.1f} vs {wkv(weak):.1f}) but not over the season ({rr if rr is None else round(rr,1)} vs {ros(weak) if ros(weak) is None else round(ros(weak),1)} a game)"
            elif bn and rr is not None and any(ros(b) is not None and rr > ros(b) for b in bn):
                b = min([b for b in bn if ros(b) is not None], key=ros); tag = f"BENCH DEPTH only: better than your {b} ({rr:.1f} vs {ros(b):.1f} a game) but would not start"
            elif rr is None and rw is None: tag = "NO EXPERT NUMBER: Ratcliffe has no projection for him (deep or hurt) - not an upgrade on what we know"
            else: tag = "NOT AN UPGRADE: would not start or beat your bench" + (f" ({rr:.1f} a game vs your weakest {weak} {ros(weak):.1f})" if weak and rr is not None and ros(weak) is not None else "")
            nums = f"Ratcliffe {('%.1f' % rw) if rw is not None else '-'} this week / {('%.1f' % rr) if rr is not None else '-'} a game rest of season; Koerner {('%.1f' % kw) if kw is not None else '-'}; Yahoo {('%.1f' % yw[WK]) if WK in yw else '-'}"
            tm = TEAMOF.get(k, "")
            po = ", ".join(f"Wk{w} {GS.get((tm, w), '?')}" + (f" (Yahoo {yw[w]:.1f})" if w in yw else "") for w in (15, 16, 17)) if tm else "playoff schedule unknown"
            fb = flagged_before(R, nm, t) if t else []
            seen = ("We showed him to you first: " + "; ".join(fb[:2]) + ".") if fb else ("No alert fired on him in this league before he was taken." if t else "")
            return f"VERDICT: {tag}. {nums}. Playoffs: {po}. {seen}".strip()
        L = dict(opponent=(OPP.get(lid) or ("", ""))[1], expert=[], arrivals=[], review=dict(yours=[], hurts=[], missed=[], openings=[], others=[], quiet=0),
                 worst={k: f"{v[0]} ({k}{v[1]})" for k, v in worst.items()}, txn_read=thead)
        # 1 EXPERT CHECK
        for key, b in B.items():
            if key in rostered or not b.get("rank") or b.get("pos") not in POS: continue
            w = beats(b["name"])
            if w: L["expert"].append(dict(name=b["name"], team=b["team"], pos=b["pos"], boone=b["rank"], over=w[0], over_rank=w[1],
                                          margin=w[1] - b["rank"], how=how(b["name"]), yahoo_ros=round(Y[key], 1) if key in Y else None,
                                          line=f"The expert panel ranks {b['name']} ({b['team']} {b['pos']}) {b['pos']}{b['rank']} this week, ahead of your {w[0]} ({b['pos']}{w[1]}). {how(b['name'])}."))
        L["expert"].sort(key=lambda x: -x["margin"]); L["expert"] = L["expert"][:8]
        # 2 NEW-ARRIVAL GATE (dropped in a league, or traded/signed/released in the news, in the window, and available here)
        cand = {}
        for x in txns:
            if x["t"] >= since and x["action"] in ("Dropped", "Traded") and x["pos"] in POS:
                cand.setdefault(norm(x["player"]), (x["player"], f"dropped by {x['team']} {pt_str(x['t'])}"))
        for k, v in news.items(): cand.setdefault(k, v)
        for key, (nm, why) in cand.items():
            if key in rostered: continue
            ps = posof(nm)
            if ps not in POS: continue
            w = beats(nm)
            if not w and why.startswith("dropped by " + (OPP.get(lid) or ("",))[0]) and (OPP.get(lid) or ("",))[0]: continue   # your own cut that doesn't beat anyone
            L["arrivals"].append(dict(name=nm, pos=ps, why=why, boone=rk(nm), beats=w[0] if w else None, how=how(nm),
                                      yahoo_ros=round(Y[key], 1) if key in Y else None,
                                      line=f"{nm} ({ps}) - {why}. Experts: {rtxt(nm)}" + (f", ahead of your {w[0]} ({ps}{w[1]})" if w else "")
                                           + (f". Yahoo rest of season {Y[key]:.0f}" if key in Y else "") + f". {how(nm)}. {verdict(nm, ps)}"))
        L["arrivals"].sort(key=lambda a: (a["beats"] is None, a["boone"] or 999)); L["arrivals"] = L["arrivals"][:10]
        # 3 TRANSACTION REVIEW
        myname, opp = OPP.get(lid, ("", ""))
        for x in [x for x in txns if x["t"] >= since]:
            who = f"{x['player']} ({x['nfl']} {x['pos']})"
            if x["team_id"] == str(me):
                ln = f"You {x['action'].lower()} {who}, {pt_str(x['t'])}" + (f" ({x['detail']})" if x['detail'] else "") + "."
                claim = any(y["team_id"] == str(me) and y["t"] == x["t"] and y["action"] == "Added" and "Waiver" in y["detail"] for y in txns)
                if x["action"] == "Dropped" and not claim:   # a free-agent move or a straight cut, not a claim that just processed
                    ln += f" If any pending waiver claim listed {x['player']} as its drop, Yahoo cancelled that claim - re-enter it with a new drop."
                L["review"]["yours"].append(ln); continue
            if x["action"] == "Added" and x["pos"] in POS:
                w = beats(x["player"])
                vd = verdict(x["player"], x["pos"], x["t"])
                if opp and x["team"] == opp:
                    L["review"]["hurts"].append(f"Your opponent {opp} added {who}, {pt_str(x['t'])} ({x['detail']}). Experts: {rtxt(x['player'])}. {vd}")
                elif w and ("STARTER UPGRADE" in vd or "ONE-WEEK FILL" in vd):   # Oct 30: 'we missed' only when he'd have started for Dom
                    L["review"]["missed"].append(f"{x['team']} took {who}, {pt_str(x['t'])} ({x['detail']}). the expert panel has him {x['pos']}{rk(x['player'])}, ahead of your {w[0]} ({x['pos']}{w[1]}). {vd}")
                else: L["review"]["others"].append(f"{x['team']} took {who}, {pt_str(x['t'])} ({x['detail']}). {vd}")   # Oct 30 (Dom): no more silent 'quiet' adds
            elif x["action"] == "Dropped" and x["pos"] in POS and norm(x["player"]) not in rostered:
                w = beats(x["player"])
                if w: L["review"]["openings"].append(f"{x['team']} dropped {who}, {pt_str(x['t'])}. the expert panel has him {x['pos']}{rk(x['player'])}, ahead of your {w[0]}. {how(x['player'])}. {verdict(x['player'], x['pos'])}")
                else: L["review"]["quiet"] += 1
            else: L["review"]["quiet"] += 1
        report["leagues"][lab] = L

    stale = []
    for lab_, n_, _, _ in LEAGUES:
        a = read_age(load_txns(R, n_)[1], asof)
        if a is None or a > 30: stale.append(f"{lab_} transaction read is " + ("missing" if a is None else f"{a:.0f} hours old")); 
    a = read_age(bhead, asof)
    if a is None or a > 36: stale.append("expert rankings are " + ("missing" if a is None else f"{a:.0f} hours old"))
    report["stale"] = stale
    os.makedirs(out_dir, exist_ok=True)
    json.dump(report, open(f"{out_dir}/morning_review.json", "w"), indent=1)
    txt = render(report)
    open(f"{out_dir}/morning_review.txt", "w").write(txt + "\n")
    if write_brief:
        add_to_brief(f"{R}/dispatch_out/brief_latest.txt", report)
        # the Scout's own lane: the boards carry these lists too, so Live and the gauntlet see them
        for lab, L in report["leagues"].items():
            bf = f"{R}/dispatch_out/scout_state/scout_board_{lab.replace(' ', '')}.json"
            try: b = json.load(open(bf))
            except Exception: continue
            try: P = json.load(open(f"{R}/dispatch_out/expert_panel.json")); pl = P["leagues"][lab]
            except Exception: P, pl = None, {"passed": [], "failed": []}
            b["expert_lane"] = dict(experts=(P or {}).get("panel"), read=(P or {}).get("experts_read"), flags=pl["passed"], failed=pl["failed"])
            b["arrivals"] = L["arrivals"]; b["txn_review"] = L["review"]
            json.dump(b, open(bf, "w"), indent=1)
    print(txt)
    return report

def read_age(head, now):
    m = re.search(r"read live (\w{3} \w{3} \d{1,2} \d{4} \d{1,2}:\d{2} [AP]M)", head or "")
    if not m: return None
    t = dt.datetime.strptime(m.group(1), "%a %b %d %Y %I:%M %p").replace(tzinfo=PT)
    return (now - t).total_seconds() / 3600

def render(rep):
    warn = rep.get("stale") or []
    out = [f"!! STALE: {w}" for w in warn] + [f"MORNING CHECK - built {rep['built']} PT. Moves reviewed {rep['window']['since']} to {rep['window']['asof']} PT.",
           f"Experts: {rep['sources']['boone'] or 'no expert file'}. Rosters: Yahoo read {rep['sources']['yahoo_read']}."]
    for lab, L in rep["leagues"].items():
        out.append(f"\n{lab} (plays {L['opponent'] or '?'})")
        r = L["review"]
        for k, title in (("yours", "Your moves"), ("hurts", "Hurts you"), ("missed", "We missed"), ("openings", "Openings"), ("others", "Rival pickup")):
            for ln in r[k]: out.append(f"  {title}: {ln}")
        out.append(f"  {r['quiet']} other move(s) in the window don't touch you.")
        for e in L["expert"]: out.append(f"  EXPERT PANEL: {e['line']}")
        for a in L["arrivals"]: out.append(f"  NEW ARRIVAL: {a['line']}")
        if not L["expert"] and not L["arrivals"]: out.append("  Expert check and new-arrival gate: nobody available beats your men.")
    return "\n".join(out)

def add_to_brief(path, rep):
    """Oct 24 (Dom): no raw flags in the brief. A pickup name reaches the brief only after the expert panel and the full
    workup passed it (expert_panel.json). New arrivals that did not pass are listed by name only, as checked."""
    if not os.path.exists(path): return
    s = open(path).read().split("\n\nMorning check")[0].rstrip("\n")
    try: P = json.load(open(os.path.join(os.path.dirname(path), "expert_panel.json")))
    except Exception: P = None
    parts = []
    if rep.get("stale"): parts.append("Warning, the morning read is stale: " + "; ".join(rep["stale"]) + ".")
    if P is None: parts.append("Warning, the expert panel did not run this build, so no pickup names are listed.")
    if P and P.get("experts_stale"): parts.append("Expert panel: " + P["experts_stale"] + ".")
    for lab, L in rep["leagues"].items():
        r = L["review"]; bits = r["yours"][:3] + r["hurts"][:2] + r["missed"][:3] + r.get("others", [])[:4] + r["openings"][:2]
        passed = (P or {}).get("leagues", {}).get(lab, {}).get("passed", [])
        for x in passed:
            bits.append(f"Expert flag to analyze: {x['name']} ({x['team']} {x['pos']}) over your {x['beats']} - {', '.join(x['yes'])} rank him higher this week"
                        + (f" ({', '.join(x['no'])} " + ("doesn't" if len(x['no']) == 1 else "don't") + ")" if x.get("no") else "") + f"; {x['available']}.")
        checked = [a["name"] for a in L["arrivals"] if a["name"] not in {x["name"] for x in passed}]
        if checked: bits.append("New arrivals checked, not upgrades for you: " + ", ".join(checked[:6]) + ".")
        if bits: parts.append(f"{lab}: " + " ".join(bits))
    body = "\n\n".join(parts) if parts else "Nothing in last night's moves or the expert panel touches your teams."
    open(path, "w").write(s + f"\n\nMorning check (moves since {rep['window']['since']}; expert panel: Ciallela, Orginski, Ratcliffe, Thorman, Koerner):\n\n{body}\n")

if __name__ == "__main__":
    R = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.getcwd()
    asof = dt.datetime.fromisoformat(arg("--asof")).replace(tzinfo=PT) if arg("--asof") else dt.datetime.now(PT)
    if arg("--since"): since = dt.datetime.fromisoformat(arg("--since")).replace(tzinfo=PT)
    else:   # the review covers the 24 hours up to this morning's 5 AM Pacific, plus anything since
        five = asof.replace(hour=5, minute=0, second=0, microsecond=0)
        if asof < five: five -= dt.timedelta(days=1)
        since = five - dt.timedelta(hours=24)
    run(R, since, asof, arg("--out", f"{R}/dispatch_out"), "--no-brief" not in sys.argv)
