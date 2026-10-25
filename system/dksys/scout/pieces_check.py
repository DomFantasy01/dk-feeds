"""MISSING PIECES CHECK (Oct 25 2026, Dom): "the missing pieces ... I got to make sure that that's always correct."
Every build re-checks each team's Missing Pieces (cand/missing_pieces.json) against the LIVE roster (the latest Yahoo
roster read) and Yahoo's own weekly projections (yahoo_drop/scout/yproj_dk<n>.txt, the MINE rows), week by week
through Week 17. For each piece it says FILLED (every remaining week has enough men at that position over the bar),
or OPEN with the short weeks named. It also scans every starting position for NEW GAPS - weeks where the roster can't
fill its fixed starting slots with a man over the bar (byes, injuries). It only reports; it never edits the pieces
file. A change is put to Dom in the morning brief and he confirms it.

Bars (Yahoo points, league scoring): QB 16, RB 10, WR 10, TE 8 - roughly a startable week. A piece's own test sets its bar.
Outputs: dispatch_out/pieces_check.json, the 'pieces_check' block per league in the meter file (Live shows it), and with
--brief a "Missing pieces check" section at the end of brief_latest.txt.
usage: python3 pieces_check.py REPO [--pieces FILE] [--meter METER.json] [--brief] [--out DIR]"""
import sys, os, re, json, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import expert_panel as EP

BAR = {"QB": 16, "RB": 10, "WR": 10, "TE": 8}
LAST = 17

def arg(f, d=None):
    a = sys.argv; return a[a.index(f) + 1] if f in a and a.index(f) + 1 < len(a) else d

def proj(R, n):
    """(name, pos) -> {week: pts} for Dom's own men, plus the read stamp and the first week in the file."""
    f = f"{R}/yahoo_drop/scout/yproj_dk{n}.txt"; P = collections.defaultdict(dict); head = ""
    if not os.path.exists(f): return P, None, None
    for ln in open(f):
        if ln.startswith("#"): head = head or ln; continue
        r = ln.rstrip("\n").split("|")
        if len(r) >= 6 and r[5] == "MINE" and r[0].isdigit():
            try: P[(r[1], r[3])][int(r[0])] = float(r[4])
            except ValueError: pass
    m = re.search(r"read live (.+?) \(", head); w = re.search(r"weeks (\d+)", head)
    return P, (m.group(1) if m else "?"), (int(w.group(1)) if w else None)

def run(R, pieces_f, meter_f=None, brief=False, out_dir=None):
    MP = json.load(open(pieces_f)); rep = dict(built=EP.pt_str(dt.datetime.now(EP.PT)) + " PT", pieces_set=MP.get("set"), leagues={})
    for lab, n, lid, me in EP.LEAGUES:
        P, read, w0 = proj(R, n)
        rows = EP.scout_rows(R, n); mine = [r for r in rows if r["team"] == str(me)]
        onroster = {(EP.K(r["name"]), r["pos"]) for r in mine}
        P = {k: v for k, v in P.items() if (EP.K(k[0]), k[1]) in onroster}   # only men still on the roster now
        slots = collections.Counter(r["slot"] for r in mine)
        roster_read = next((l for l in open(f"{R}/yahoo_drop/scout/dk{n}_rosters_live.txt") if l.startswith("#")), "") if os.path.exists(f"{R}/yahoo_drop/scout/dk{n}_rosters_live.txt") else ""
        roster_read = (re.search(r"read live (.+?) \(", roster_read) or [None, "?"])[1]
        L = dict(proj_read=read, roster_read=roster_read, pieces=[], gaps=[])
        if not w0: L["error"] = "no Yahoo weekly projections file"; rep["leagues"][lab] = L; continue
        # this week's lineup is set once Sunday arrives (Sun/Mon) - judge from next week then
        w1 = w0 + 1 if dt.datetime.now(EP.PT).weekday() in (6, 0) else w0
        weeks = list(range(w1, LAST + 1))
        def who(pos, w, mn): return sorted(((nm, v.get(w, 0)) for (nm, p), v in P.items() if p in pos and v.get(w, 0) >= mn), key=lambda x: -x[1])
        for pc in MP["leagues"].get(lab, []):
            t = pc.get("test") or {}; need, mn, frm = t.get("need", 1), t.get("min", BAR.get(pc["pos"][0], 10)), max(t.get("from", w1), w1)
            short = []; cover = collections.Counter()
            for w in range(frm, LAST + 1):
                ok = who(pc["pos"], w, mn)
                for nm, _ in ok[:need]: cover[nm] += 1
                if len(ok) < need: short.append(w)
            status = "filled" if not short else "open"
            line = (f"{pc['piece']}: " + (f"looks FILLED - every week from {frm} to {LAST} has {need} {'/'.join(pc['pos'])} at {mn}+ "
                    f"({', '.join(nm for nm, _ in cover.most_common(4))}). Confirm to close it." if status == "filled" else
                    f"still OPEN - short in Week{'s' if len(short) > 1 else ''} {', '.join(map(str, short))} (needs {need} {'/'.join(pc['pos'])} at {mn}+"
                    + (f"; covering the other weeks: {', '.join(nm for nm, _ in cover.most_common(3))}" if cover else "") + ")."))
            L["pieces"].append(dict(piece=pc["piece"], status=status, short=short, test=dict(need=need, min=mn, start=frm), line=line))
        # new gaps: fixed starting slots this roster can't fill over the bar (flex slots are left out)
        piece_pos = {p for pc in MP["leagues"].get(lab, []) for p in pc["pos"]}
        for pos in ("QB", "RB", "WR", "TE"):
            need = slots.get(pos, 0)
            if not need: continue
            short = [w for w in weeks if len(who([pos], w, BAR[pos])) < need]
            if short and pos not in piece_pos:
                L["gaps"].append(dict(pos=pos, weeks=short, line=f"New gap at {pos}: Week{'s' if len(short) > 1 else ''} {', '.join(map(str, short))} - fewer than {need} {pos} projecting {BAR[pos]}+ (byes or injuries). Not on the Missing Pieces list."))
        rep["leagues"][lab] = L
    out_dir = out_dir or f"{R}/dispatch_out"; os.makedirs(out_dir, exist_ok=True)
    json.dump(rep, open(f"{out_dir}/pieces_check.json", "w"), indent=1)
    if meter_f and os.path.exists(meter_f):
        M = json.load(open(meter_f))
        for lab, L in rep["leagues"].items():
            if lab in M.get("leagues", {}):
                M["leagues"][lab]["pieces_check"] = dict(read=L.get("proj_read"), roster=L.get("roster_read"),
                                                         lines=[p["line"] for p in L["pieces"]] + [g["line"] for g in L["gaps"]])
        json.dump(M, open(meter_f, "w"), indent=1)
    txt = render(rep); open(f"{out_dir}/pieces_check.txt", "w").write(txt + "\n")
    if brief: add_to_brief(f"{R}/dispatch_out/brief_latest.txt", rep)
    print(txt); return rep

def render(rep):
    o = [f"MISSING PIECES CHECK - built {rep['built']}; pieces list set {rep['pieces_set']}."]
    for lab, L in rep["leagues"].items():
        o.append(f"\n{lab} (rosters read {L.get('roster_read')}, Yahoo weekly projections read {L.get('proj_read')})")
        if L.get("error"): o.append(f"  !! {L['error']}"); continue
        if not L["pieces"]: o.append("  No missing pieces on the list.")
        for p in L["pieces"]: o.append(f"  {p['status'].upper():6s} {p['line']}")
        for g in L["gaps"]: o.append(f"  GAP    {g['line']}")
    return "\n".join(o)

def add_to_brief(path, rep):
    if not os.path.exists(path): return
    s = open(path).read()
    head_i = s.find("\n\nMissing pieces check")
    if head_i >= 0:   # replace our old section, keep anything after it
        nxt = s.find("\n\nExpert movement", head_i + 1); s = s[:head_i] + (s[nxt:] if nxt >= 0 else "")
    parts = []
    for lab, L in rep["leagues"].items():
        bits = [p["line"] for p in L.get("pieces", [])] + [g["line"] for g in L.get("gaps", [])]
        if not L.get("pieces"): bits.insert(0, "No missing pieces on the list.")
        parts.append(f"{lab}: " + " ".join(bits))
    sec = (f"\n\nMissing pieces check (each piece re-tested against your live roster and Yahoo's weekly projections; "
           f"list set {rep['pieces_set']} - nothing changes until you confirm):\n\n" + "\n\n".join(parts) + "\n")
    i = s.find("\n\nExpert movement")
    s = (s[:i] + sec.rstrip("\n") + s[i:]) if i >= 0 else (s.rstrip("\n") + sec)
    open(path, "w").write(s)

if __name__ == "__main__":
    R = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.getcwd()
    run(R, arg("--pieces", f"{R}/system/cand/missing_pieces.json"), arg("--meter"), "--brief" in sys.argv, arg("--out"))
