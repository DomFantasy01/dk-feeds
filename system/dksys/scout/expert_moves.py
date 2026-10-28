"""EXPERT MOVES (Oct 25 2026, Dom). "We need to know what players are moving up and what players are moving down."
Every expert pull saves a snapshot (pull_experts.py -> yahoo_drop/morning/expert_history/wk<W>_<UTC>.txt). This compares
the newest snapshot with (a) the previous pull this week - news-driven moves, e.g. a teammate ruled out - and (b) last
week's final list - the week-to-week trend. Same named panel as expert_panel.py (Ciallela, Ratcliffe, Thorman, Koerner;
Jahnke only fills in for a missing one). Ranks are each expert's own position rank (RB12 = 12).

A player MOVES when the panel's middle rank (median of the experts who rank him both times) shifts 3+ spots week to week,
or 2+ spots since the last pull, and at least 2 experts moved the same way. Weekly lists include the matchup, so a
week-to-week move is partly schedule - the line says how many experts moved and by how much, so it can be weighed.
Wire players: not rostered in that league, now inside the startable range (QB/TE top 15, RB/WR top 36), and climbing
5+ spots week to week - flags for analysis only, never a pickup order (Dom, Oct 24).

Outputs: dispatch_out/expert_moves.json (+ a copy in DK_ROOT/dksys/data/latest/), the per-league "experts" block in the
meter file (the Live page shows it), and with --brief an "Expert movement" section at the end of brief_latest.txt.
usage: python3 expert_moves.py REPO [--meter METER.json] [--brief] [--out DIR]"""
import sys, os, re, json, glob, statistics, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import expert_panel as EP

PANEL, BACKUP, SHOW, POS, K = EP.PANEL, EP.BACKUP, EP.SHOW, EP.POS, EP.K
TOPN = {"QB": 15, "TE": 15, "RB": 36, "WR": 36}

def arg(f, d=None):
    a = sys.argv; return a[a.index(f) + 1] if f in a and a.index(f) + 1 < len(a) else d

def load(path):
    """K(name) -> {'_name','_team','_pos', expert: rank}; plus the header (read time, week)."""
    out, head = {}, ""
    for ln in open(path):
        if ln.startswith("#"):
            head = head or ln; continue
        p = ln.rstrip("\n").split("|")
        if len(p) >= 7 and p[3].isdigit() and p[2] in POS:
            d = out.setdefault(K(p[4]), {"_name": p[4], "_team": EP.TEAM_FIX.get(p[5], p[5]), "_pos": p[2]})
            if p[2] == d["_pos"]: d[p[1]] = int(p[3])
    m = re.search(r"read live (\w{3} \w{3} \d{1,2} \d{4} \d{1,2}:\d{2} [AP]M)", head)
    w = re.search(r"week (\d+)", head)
    return out, (m.group(1) + " PT" if m else "?"), (int(w.group(1)) if w else 0)

def snapshots(R):
    """[(week, utc stamp, path)] oldest first. Duplicates (same rows as the one before) are already skipped by the puller."""
    S = []
    for f in glob.glob(f"{R}/yahoo_drop/morning/expert_history/wk*_*.txt"):
        m = re.match(r"wk(\d+)_(\w+)\.txt$", os.path.basename(f))
        if m: S.append((int(m.group(1)), m.group(2), f))
    return sorted(S)

def panel_of(*dicts):
    have = {e for D in dicts for d in D.values() for e in d if not e.startswith("_")}
    act = [e for e in PANEL if e in have]
    if len(act) < len(PANEL) and BACKUP in have: act.append(BACKUP)
    return act

def move(now, old, panel):
    """median rank now, then, and how many experts moved each way (only experts who rank him both times)."""
    if not now or not old: return None
    both = [e for e in panel if e in now and e in old]
    if not both: return None
    a, b = [now[e] for e in both], [old[e] for e in both]
    up = [SHOW[e] for e in both if old[e] - now[e] >= 1]; dn = [SHOW[e] for e in both if now[e] - old[e] >= 1]
    return dict(now=statistics.median(a), then=statistics.median(b), d=statistics.median(b) - statistics.median(a),
                up=up, down=dn, per={SHOW[e]: f"{old[e]}->{now[e]}" for e in both})

def fmt_rank(pos, r): return f"{pos} {int(round(r + 1e-9))}"   # Oct 28 (Dom): position rank, whole number - "WR 15"

def run(R, meter_f=None, brief=False, out_dir=None):
    S = snapshots(R)
    cur_f = f"{R}/yahoo_drop/morning/expert_rankings.txt"
    if not os.path.exists(cur_f): print("EXPERT MOVES: no expert file"); return None
    NOW, now_read, W = load(cur_f)
    same_wk = [s for s in S if s[0] == W]; prev_wk = [s for s in S if s[0] == W - 1]
    # previous pull = the newest snapshot of this week whose read time differs from the current file's
    PULL = None; pull_read = None
    for s in reversed(same_wk):
        d, rd, _ = load(s[2])
        if rd != now_read: PULL, pull_read = d, rd; break
    LAST, last_read = (load(prev_wk[-1][2])[:2] if prev_wk else (None, None))
    if LAST is not None: last_read = f"Week {W - 1} final list"
    panel = panel_of(NOW)
    inbox = EP.newest_inbox(R); ROS = EP.rosters(inbox) if inbox else {}
    rep = dict(built=EP.pt_str(dt.datetime.now(EP.PT)) + " PT", week=W, panel=[SHOW[e] for e in panel], now_read=now_read,
               prev_pull_read=pull_read, last_week_read=last_read, yahoo_read=(inbox or {}).get("read_pt"),
               rule="moves: middle panel rank shifts 3+ spots week to week (2+ since the last pull) with 2+ experts moving the same way",
               leagues={})
    if LAST is None: rep["missing"] = f"no Week {W - 1} list saved yet - week-to-week moves start once it is (the next expert pull backfills it)"
    if PULL is None: rep["missing_pull"] = "no earlier pull this week to compare with"
    for lab, n, lid, me in EP.LEAGUES:
        srows = EP.scout_rows(R, n); W_ = EP.waivers(R, n)
        mine = [r for r in srows if r["team"] == str(me) and r["pos"] in POS]
        rostered = {K(p) for ps in ROS.get(n, {}).values() for p in ps} | {K(r["name"]) for r in srows}
        def find(D, name, team):
            if D is None: return None
            k = K(name)
            if k in D: return D[k]
            ik = EP.IK(name, team)
            return next((v for v in D.values() if EP.IK(v["_name"], v["_team"]) == ik), None)
        players, rising, sliding = [], [], []
        for r in mine:
            nw = find(NOW, r["name"], r["nfl"]); pos = r["pos"]
            row = dict(name=r["name"], team=r["nfl"], pos=pos, slot=r["slot"])
            if nw is None: row["note"] = "not ranked this week (bye, hurt or off the lists)"; players.append(row); continue
            mid = statistics.median([nw[e] for e in panel if e in nw]) if any(e in nw for e in panel) else None
            row["rank_now"] = fmt_rank(pos, mid) if mid is not None else None
            for tag, D in (("week", LAST), ("pull", PULL)):
                mv = move(nw, find(D, r["name"], r["nfl"]), panel)
                if mv: row[tag] = dict(mv, then_s=fmt_rank(pos, mv["then"]), now_s=fmt_rank(pos, mv["now"]))
            wk, pl = row.get("week"), row.get("pull")
            big = lambda m, t: m and abs(m["d"]) >= t and len(m["up" if m["d"] > 0 else "down"]) >= 2
            # Oct 28 (Dom): only moves big enough to matter - 5+ spots at his position - shown as the rank before and after
            if big(wk, 5) or big(pl, 5):
                m = wk if big(wk, 5) else pl
                line = (f"{r['name']} ({r['slot']}): {m['then_s']} \u2192 {m['now_s']}, {'up' if m['d'] > 0 else 'down'} {int(round(abs(m['d'])))} spots "
                        f"{'since last week' if m is wk else 'since the last pull (' + str(pull_read) + ')'} \u00b7 {len(m['up'] if m['d'] > 0 else m['down'])} of {len(m['per'])} experts")
                (rising if m["d"] > 0 else sliding).append(dict(name=r["name"], d=m["d"], line=line))
            players.append(row)
        wire = []
        if LAST is not None:
            for k, nw in NOW.items():
                if k in rostered: continue
                pos = nw["_pos"]; ranks = [nw[e] for e in panel if e in nw]
                if len(ranks) < 2: continue
                mid = statistics.median(ranks)
                if mid > TOPN.get(pos, 36): continue
                mv = move(nw, LAST.get(k), panel)
                if not mv or mv["d"] < 5 or len(mv["up"]) < 2: continue
                av = f"on waivers until {W_[k]}" if k in W_ else "free agent"
                wire.append(dict(name=nw["_name"], team=nw["_team"], pos=pos, d=mv["d"], avail=av,
                                 line=f"{nw['_name']} ({nw['_team']}): {fmt_rank(pos, mv['then'])} \u2192 {fmt_rank(pos, mv['now'])}, up {int(round(mv['d']))} spots \u00b7 "
                                      f"{len(mv['up'])} of {len(mv['per'])} experts; {av} - flag for analysis, not a move"))
            wire.sort(key=lambda x: -x["d"]); wire = wire[:3]
        rising.sort(key=lambda x: -x["d"]); sliding.sort(key=lambda x: x["d"])
        rep["leagues"][lab] = dict(players=players, rising=rising, sliding=sliding, wire=wire)
    out_dir = out_dir or f"{R}/dispatch_out"; os.makedirs(out_dir, exist_ok=True)
    json.dump(rep, open(f"{out_dir}/expert_moves.json", "w"), indent=1)
    root = os.environ.get("DK_ROOT", "/home/claude")
    if os.path.isdir(f"{root}/dksys/data/latest"): json.dump(rep, open(f"{root}/dksys/data/latest/expert_moves.json", "w"), indent=1)
    if meter_f and os.path.exists(meter_f):   # the Live page reads the meter file's leagues
        M = json.load(open(meter_f))
        for lab, L in rep["leagues"].items():
            if lab in M.get("leagues", {}):
                M["leagues"][lab]["experts"] = dict(read=now_read, vs_pull=pull_read, vs_week=last_read, panel=rep["panel"],
                                                    rising=[x["line"] for x in L["rising"][:4]], sliding=[x["line"] for x in L["sliding"][:4]],
                                                    wire=[x["line"] for x in L["wire"]], missing=rep.get("missing"))
        json.dump(M, open(meter_f, "w"), indent=1)
    txt = render(rep); open(f"{out_dir}/expert_moves.txt", "w").write(txt + "\n")
    if brief: add_to_brief(f"{R}/dispatch_out/brief_latest.txt", rep)
    print(txt)
    return rep

def render(rep):
    o = [f"EXPERT MOVES - Week {rep['week']}, built {rep['built']}. Panel: {', '.join(rep['panel'])}.",
         f"Experts read {rep['now_read']}; compared with the pull of {rep['prev_pull_read'] or 'none'} and last week's list ({rep['last_week_read'] or 'none saved'})."]
    for k in ("missing", "missing_pull"):
        if rep.get(k): o.append(f"!! {rep[k]}")
    for lab, L in rep["leagues"].items():
        o.append(f"\n{lab}")
        for x in L["rising"]: o.append(f"  RISING  {x['line']}")
        for x in L["sliding"]: o.append(f"  SLIDING {x['line']}")
        if not L["rising"] and not L["sliding"]: o.append("  No big moves on your roster.")
        for x in L["wire"]: o.append(f"  WIRE    {x['line']}")
        o.append("  Your men now: " + "; ".join(f"{p['name']} {p.get('rank_now') or '-'}" for p in L["players"] if p["slot"] != "IR"))
    return "\n".join(o)

def add_to_brief(path, rep):
    if not os.path.exists(path): return
    s = open(path).read().split("\n\nExpert movement")[0].rstrip("\n")
    parts = []
    for k in ("missing",):
        if rep.get(k): parts.append(f"Note: {rep[k]}.")
    for lab, L in rep["leagues"].items():
        bits = [f"Rising: {x['line']}." for x in L["rising"][:3]] + [f"Sliding: {x['line']}." for x in L["sliding"][:3]] + \
               [f"Climbing on the wire: {x['line']}." for x in L["wire"][:2]]
        parts.append(f"{lab}: " + (" ".join(bits) if bits else "no big moves on your roster."))
    head = (f"Expert movement (panel {', '.join(rep['panel'])}; read {rep['now_read']}, vs the pull of {rep['prev_pull_read'] or 'none'}"
            f" and {rep['last_week_read'] or 'no list from last week saved yet'}):")
    open(path, "w").write(s + "\n\n" + head + "\n\n" + "\n\n".join(parts) + "\n")

if __name__ == "__main__":
    R = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.getcwd()
    run(R, arg("--meter"), "--brief" in sys.argv, arg("--out"))
