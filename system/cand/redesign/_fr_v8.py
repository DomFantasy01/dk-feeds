# THE FIELD REPORT v8 (Dom, Mon Oct 12 2026) - the approved DK1 prototype (v7) rolled out to all four leagues.
# One page per league (two when the roster runs long): the masthead, a Scorecard card and a Post-Mortem / Outlook card,
# then Starters, Bench and IR in one clean table with a markers lane. Exec'd from fieldpos24.py after the old chain,
# so it can use MTR, WEEKN, c, norm. The masthead (every page) lives in _mast_v8.py.
exec(open("/home/claude/cand/redesign/_mast_v8.py").read())
import math as _m8, random as _r8, re as _re8, os as _os8, json as _j8, glob as _g8, datetime as _d8, sys as _s8
import pandas as _p8
from zoneinfo import ZoneInfo as _Z8
from reportlab.lib.colors import HexColor as _H8, Color as _C8
from reportlab.platypus import Paragraph as _PG8
from reportlab.lib.styles import ParagraphStyle as _PS8

# ================================================================ DATA
_REPO8 = _os8.environ.get("GITHUB_WORKSPACE", "/home/claude/domfantasy01/dk-feeds")
_G8 = _p8.read_csv("/home/claude/dksys/data/latest/games.csv", low_memory=False)
_G8 = _G8[(_G8.season == _G8.season.max()) & (_G8.game_type == "REG")]
_TF8 = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX"}
def _T8(t): return _TF8.get(str(t).upper(), str(t).upper())
def _game8(team, w):
    r = _G8[(_G8.week == w) & ((_G8.home_team.map(_T8) == _T8(team)) | (_G8.away_team.map(_T8) == _T8(team)))]
    return None if not len(r) else r.iloc[0]
def vs8(team, w):
    r = _game8(team, w)
    if r is None: return "BYE"
    return ("vs " + r.away_team) if _T8(r.home_team) == _T8(team) else ("@ " + r.home_team)
def bye8(team):
    ws = set(_G8[(_G8.home_team.map(_T8) == _T8(team)) | (_G8.away_team.map(_T8) == _T8(team))].week)
    b = [w for w in range(1, 19) if w not in ws]; return b[0] if b else None
def _ko8(r): return _d8.datetime.strptime(f"{r.gameday} {r.gametime}", "%Y-%m-%d %H:%M").replace(tzinfo=_ET8)
def done8(team, w):
    """his game this week is over (or he has none)"""
    r = _game8(team, w)
    if r is None: return True
    if r.result == r.result: return True
    return _d8.datetime.now(_d8.timezone.utc) > _ko8(r) + _d8.timedelta(hours=4)
def live8(team, w):
    r = _game8(team, w)
    if r is None or r.result == r.result: return False
    now = _d8.datetime.now(_d8.timezone.utc); return _ko8(r) <= now <= _ko8(r) + _d8.timedelta(hours=4)
def last_ko8(w):
    g = _G8[_G8.week == w]; return max(_ko8(r) for r in g.itertuples()) if len(g) else None

_s8.path.insert(0, "/home/claude/src/forecast")
import fc_model as _FM8
for _sf in ("/home/claude/dksys/gate/fresh/stats_player_week_2026.csv", _FM8.STATS):
    if _os8.path.exists(_sf): _FM8.STATS = _sf; break
_FMS8 = _FM8.load(); _FMF8 = {}
def _frame8(lab):
    k = {"DK I": 1, "DK II": 2, "DK III": 3, "DK IV": 4}[lab]
    if k not in _FMF8: f = _FM8.frame(k, _FMS8); f["k"] = f.player_display_name.map(norm); _FMF8[k] = f
    return _FMF8[k]
def avg8(lab, nm, w):
    f = _frame8(lab); d = f[(f.k == norm(nm)) & (f.week < w)]; return float(d.pts.mean()) if len(d) else None
def act8(lab, nm, w):
    f = _frame8(lab); d = f[(f.k == norm(nm)) & (f.week == w)]; return float(d.pts.sum()) if len(d) else None
_EN8 = {}
def eng8(lab):
    if lab not in _EN8:
        try: e = _p8.read_csv(f"/home/claude/dksys/engine/gotham_{lab.replace(' ', '')}.csv"); e["k"] = e.k.astype(str)
        except Exception: e = _p8.DataFrame(columns=["k"])
        _EN8[lab] = {r.k: r for r in e.itertuples()}
    return _EN8[lab]
def _pre8(w):
    try: return _j8.load(open(_os8.path.join(_REPO8, "dispatch_out", "scoreboard", f"pregame_wk{w}.json")))
    except Exception: return {}
def _radar8(w):
    try: R = _j8.load(open(_os8.path.join(_REPO8, "dispatch_out", f"radar_wk{w}.json")))["leagues"]
    except Exception: return {}
    return {lab: {norm(p["name"]): p["marker"] for p in v.get("own", []) if p.get("marker")} for lab, v in R.items()}
def _scout8(lab):
    f = f"/home/claude/dksys/scout/scout_board_{lab.replace(' ', '')}.json"
    try: B = _j8.load(open(f))
    except Exception: return {}, []
    S = {}
    for it in B.get("gate1", []):
        for nm in it.get("rows") or []:
            k = norm(nm)
            if S.get(k, ("", 0))[0] != "red": S[k] = (it.get("mark", "gold"), int(it.get("age") or 0))
    return S, B.get("moves", [])
def _stand_file8(lid, f):
    for line in open(f):
        if line.startswith(lid + "#"):
            rows = []
            for it in line.rstrip("\n").split("#", 1)[1].split("|"):
                fz = it.split("^")
                if len(fz) < 4: continue
                nd = lid == "864215"; rows.append(dict(rank=int(fz[0]), team=fz[1], rec=fz[2], pf=float(fz[3] if nd else fz[4])))
            return rows
    return []
def _hdr8(path):
    m = _re8.search(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (\w{3}) (\d{1,2}),? (\d{1,2}):(\d{2}) ([AP]M) PT", open(path).readline())
    if not m: return None
    yr = _d8.datetime.now(_PT8).year
    return _d8.datetime.strptime(f"{m.group(2)} {m.group(3)} {yr} {m.group(4)}:{m.group(5)} {m.group(6)}", "%b %d %Y %I:%M %p").replace(tzinfo=_PT8)
def after_stand8(lid, w):
    """the newest Yahoo standings read taken after the week's last game ended - the record after the week"""
    lk = last_ko8(w)
    if lk is None: return None, None
    best = None
    for f in _g8.glob(f"/home/claude/dksys/data/latest/yahoo/wk{w}/standings_*.txt") + _g8.glob(f"/home/claude/dksys/data/latest/yahoo/wk{w + 1}/standings_*.txt"):
        t = _hdr8(f)
        if t and t > lk + _d8.timedelta(hours=4) and (best is None or t > best[1]): best = (f, t)
    if not best: return None, None
    return _stand_file8(lid, best[0]), best[1]

def _short8(p):
    if p["slot"] == "DEF": return _T8(p["team"]) + " D"
    n = p["player"]; s = n.split()
    return n if (len(n) > 2 and n[1] == ".") else (s[0][0] + ". " + " ".join(s[1:]) if len(s) > 1 else n)
_SLOT8 = {"W/R/T": "FLEX", "Q/W/R/T": "SFLEX", "W/T": "FLEX", "R/W/T": "FLEX"}
def _tag8(s): return {"IR-R": "IR", "PUP-R": "IR", "NA": "O"}.get(s, s or "")
def league8(lab, MT):
    """every number the page prints, for one league, from one meter read"""
    L = MT["leagues"][lab]; w = MT["week"]; PRE = _pre8(w); EN_ = eng8(lab) if w == WEEKN else {}
    rows = []
    for p, o in zip(L["starters"]["me"], L["starters"]["op"]):
        if not p.get("player"):
            rows.append(dict(name=None, slot=_SLOT8.get(p["slot"], p["slot"]), pos="", team="", tag="", final=False, live=False, score=None,
                             ypre=None, spre=None, gpre=None, nxt=None, av=None, vs="", bye=None, opn=_short8(o) if o.get("player") else "—",
                             opsc=o.get("actual"), opfinal=o.get("actual") is not None and done8(o.get("team"), w), opproj=o.get("yahoo"))); continue
        k = norm(p["player"]); pr = PRE.get(f"{lab}|me|{k}", {}); kd = p["pos"] in ("K", "DEF"); e = EN_.get(k)
        fin = p.get("actual") is not None and done8(p["team"], w)
        gp = pr.get("gotham") if pr else None
        if gp is None and not kd and e is not None and not bool(getattr(e, "played_wk", False)):
            gp = None if _p8.isna(e.eng_wk) else float(e.eng_wk)
        rows.append(dict(name=p["player"], slot=_SLOT8.get(p["slot"], p["slot"]), pos=p["pos"], team=_T8(p["team"]), tag=_tag8(p.get("status")),
                         final=fin, live=live8(p["team"], w) if w == WEEKN else False, score=p.get("actual"),
                         ypre=pr.get("yahoo") if pr.get("yahoo") is not None else p.get("yahoo"),
                         spre=pr.get("ratcliffe") if pr.get("ratcliffe") is not None else p.get("ratcliffe"),   # Oct 28: the middle column is FTN (Ratcliffe), Sleeper off
                         gpre=None if kd else gp, nxt=None if kd or e is None or _p8.isna(e.eng_fwd) else float(e.eng_fwd),
                         av=None if kd else avg8(lab, p["player"], w), vs=vs8(p["team"], w), bye=bye8(p["team"]),
                         opn=_short8(o) if o.get("player") else "—", opsc=o.get("actual"),
                         opfinal=o.get("actual") is not None and done8(o.get("team"), w), opproj=o.get("yahoo")))
    bench, irs = [], []
    for p in L.get("bench", []):
        if p.get("slot") not in ("BN", "IR"): continue
        k = norm(p["player"]); kd = p["pos"] in ("K", "DEF"); e = EN_.get(k)
        a = None if kd else act8(lab, p["player"], w)
        d = dict(name=p["player"], slot=p["slot"], pos=p["pos"], team=_T8(p["team"]), tag=_tag8(p.get("status")),
                 final=a is not None and done8(p["team"], w), live=live8(p["team"], w) if w == WEEKN else False, score=a, ypre=None,
                 spre=p.get("ratcliffe"), gpre=None if kd or e is None or _p8.isna(e.eng_wk) else ((PRE.get(f"{lab}|me|{k}") or {}).get("gotham") if bool(getattr(e, "played_wk", False)) else float(e.eng_wk)),
                 nxt=None if kd or e is None or _p8.isna(e.eng_fwd) else float(e.eng_fwd), av=None if kd else avg8(lab, p["player"], w),
                 vs=vs8(p["team"], w), bye=bye8(p["team"]))
        (irs if p["slot"] == "IR" else bench).append(d)
    named = [r for r in rows if r["name"]]
    me_sc = sum(r["score"] or 0 for r in rows); op_sc = sum(r["opsc"] or 0 for r in rows)
    started = any(r["score"] is not None for r in rows) or any(r["opsc"] is not None for r in rows)
    settled = started and all(r["final"] or r["name"] is None for r in rows) and all(r["opfinal"] or r["opn"] == "—" for r in rows)
    _mst = (MT.get("leagues", {}).get(lab) or {}).get("state")   # Oct 13 (Dom): the one status word, from the meter
    if _mst: settled = (_mst == "FINAL")
    D = dict(mst=_mst, lab=lab, L=L, w=w, rows=rows, bench=bench, irs=irs, me_sc=me_sc, op_sc=op_sc, started=started, settled=settled,
             n=len(rows), done_me=sum(1 for r in named if r["final"]), done_op=sum(1 for r in rows if r["opfinal"]),
             yproj=sum(r["ypre"] or 0 for r in named), tot=L.get("totals", {}).get("yahoo", [None, None]), nd=L.get("needles", {}),
             read=MT["sources"].get("yahoo_matchups", {}).get("pulled_pt"))
    D["result"] = (("WON" if me_sc > op_sc else "LOST" if me_sc < op_sc else "TIED") if settled else None)
    rec0 = L.get("record", "0-0-0"); wl = [int(x) for x in rec0.split("-")] + [0, 0, 0]
    D["rec0"] = rec0
    D["rec1"] = (f"{wl[0] + (D['result'] == 'WON')}–{wl[1] + (D['result'] == 'LOST')}" + (f"–{wl[2] + (D['result'] == 'TIED')}" if wl[2] or D["result"] == "TIED" else "")) if settled else None
    D["after"], D["after_t"] = after_stand8(L["league_id"], w) if settled else (None, None)
    return D
def rec8(r): return (r[:-2] if r.endswith("-0") and r.count("-") == 2 else r).replace("-", "–")

# ================================================================ THE CARDS
_CTOP8 = MH8_BOT - 14; _GH8 = 256
def _card8(x, gw, title, state, fill, tc):
    top = _CTOP8; gh = _GH8; deep = _mx8(tc, K8["INK"], .45)
    c.setFillColor(_H8("#E9E2D3")); c.roundRect(x + 1.5, top - gh - 2, gw, gh, 8, stroke=0, fill=1)
    c.setFillColor(K8["CARD"]); c.setStrokeColor(K8["LINE"]); c.setLineWidth(.6); c.roundRect(x, top - gh, gw, gh, 8, stroke=1, fill=1)
    c.saveState(); pp = c.beginPath(); pp.roundRect(x, top - gh, gw, gh, 8); c.clipPath(pp, stroke=0, fill=0)
    for i in range(28): c.setFillColor(_mx8(tc, deep, i / 27)); c.rect(x + i * gw / 28, top - 28, gw / 28 + .5, 28, stroke=0, fill=1)
    c.restoreState()
    t8(x + 12, top - 20.5, title, "Bebas", 21, K8["CARD"])
    if state:
        w = w8(state, "PopB", 6.2) + 12; pill8(x + gw - 11 - w, top - 18.5, state, fill, K8["CARD"], "PopB", 6.2, 6, r=5)
def _gauge8(cx, cy, r, v, lab, big=False):
    c.setLineWidth(r * .30)
    for a0, a1, col in ((180, 126, K8["RED"]), (126, 72, K8["GOLD"]), (72, 0, K8["GREEN"])):
        c.setStrokeColor(_mx8(col, K8["CARD"], .10)); c.arc(cx - r, cy - r, cx + r, cy + r, a1, a0 - a1)
    for rr, al in ((r * .92, .75), (r * 1.08, .45)):
        c.setStrokeColor(_C8(1, 1, 1, alpha=al)); c.setLineWidth(.45); c.arc(cx - rr, cy - rr, cx + rr, cy + rr, 0, 180)
    for deg in (126, 72):
        a_ = _m8.radians(deg); c.setStrokeColor(K8["CARD"]); c.setLineWidth(.9)
        c.line(cx + r * .84 * _m8.cos(a_), cy + r * .84 * _m8.sin(a_), cx + r * 1.16 * _m8.cos(a_), cy + r * 1.16 * _m8.sin(a_))
    c.setStrokeColor(_mx8(K8["INK"], K8["CARD"], .55)); c.setLineWidth(.4); ro = r * 1.24; c.arc(cx - ro, cy - ro, cx + ro, cy + ro, 0, 180)
    if v is None:
        t8(cx, cy - 13, "—", "Bebas", 15 if big else 12, K8["GR"], "c"); t8(cx, cy - 20.5, lab, "PopB", 5.2, K8["GR"], "c"); return
    ang = _m8.radians(180 - 180 * max(0, min(100, v)) / 100); c.setStrokeColor(K8["INK"]); c.setLineWidth(1.3)
    c.line(cx, cy, cx + .82 * r * _m8.cos(ang), cy + .82 * r * _m8.sin(ang)); c.setFillColor(K8["INK"]); c.circle(cx, cy, 2, stroke=0, fill=1)
    t8(cx, cy - 13, f"{v:.0f}%", "Bebas", 15 if big else 12, K8["INK"], "c"); t8(cx, cy - 20.5, lab, "PopB", 5.2, K8["GR"], "c")

def scorecard8(x, gw, D, tc):
    L = D["L"]; top = _CTOP8; soft = _mx8(tc, K8["CARD"], .86); deep = _mx8(tc, K8["INK"], .45)
    me, op = D["me_sc"], D["op_sc"]; oppn = _tct(L["opp"]) if "_tct" in globals() else L["opp"]
    _sw = D.get("mst") or ("FINAL" if D["settled"] else "LIVE" if D["started"] else "UPCOMING")   # Oct 13: FINAL / LIVE / UPCOMING everywhere
    state, fill = _sw, {"FINAL": K8["GREEN"], "LIVE": K8["GOLD"]}.get(_sw, deep)
    _card8(x, gw, "Scorecard", state, fill, tc)
    y = top - 50
    if D["started"]:
        word = D["result"] or ("LEADING" if me > op else "TRAILING" if me < op else "TIED")
        col = (K8["GREEN"] if word in ("WON", "LEADING") else K8["RED"] if word in ("LOST", "TRAILING") else K8["GOLD"])
        bsz = 44 if D["result"] else 32   # Oct 28 (Dom): smaller (was 56 / 40)
        t8(x + 14, y - (18 if bsz == 44 else 12), word, "Bebas", bsz, col); rx = x + 22 + w8(word, "Bebas", bsz)
        a, b = me, op
    else:
        ym, yo = D["tot"][0] or 0, D["tot"][1] or 0; yp = D["nd"].get("yahoo")
        word = "FAVORED" if (yp or 50) > 55 else "UNDERDOG" if (yp or 50) < 45 else "TOSS-UP"
        col = K8["GREEN"] if word == "FAVORED" else K8["RED"] if word == "UNDERDOG" else K8["GOLD"]
        t8(x + 14, y - 12, word, "Bebas", 32, col); rx = x + 20 + w8(word, "Bebas", 32)   # Oct 28 (Dom): 40 -> 32
        a, b = ym, yo
    _NS = 16   # Oct 28 (Dom): the two scores were too big next to the word - 30 -> 21 -> 16 ("still too big")
    t8(rx, y - 3, f"{a:.1f}", "Bebas", _NS, K8["INK"]); w1 = w8(f"{a:.1f}", "Bebas", _NS)
    t8(rx + w1 + 5, y - 3, "to", "PopM", 7, K8["GR"]); t8(rx + w1 + 17, y - 3, f"{b:.1f}", "Bebas", _NS, K8["GR"])
    orr = f"{oppn}  ·  {rec8(L.get('opp_record', ''))}" + (f", {L['opp_rank']}{sfx8(L['opp_rank'])} of {L['teams']}" if L.get("opp_rank") else "")
    _tail = orr[len(oppn):]   # Oct 12 (Dom): a long name gives way, the record and rank stay
    if w8(orr, "PopM", 6.8) > x + gw - 12 - rx: orr = fit8(oppn, 'PopM', 6.8, x + gw - 12 - rx - w8(_tail, 'PopM', 6.8)) + _tail
    t8(rx, y - 18, fit8(orr, "PopM", 6.8, x + gw - 12 - rx), "PopM", 6.8, K8["GR"])
    if not D["started"]: t8(rx, y - 27, "Yahoo's projection for both lineups", "Pop", 5.8, K8["GR"])
    # the margin bars
    y -= 40; bx0 = x + 14; bwid = gw - 28; big = max(a, b, 1)
    for lb, v, cl, yy in ((D["lab"], a, tc, y), ("Opp", b, K8["GR2"], y - 11)):
        c.setFillColor(K8["BAR"]); c.roundRect(bx0 + 22, yy - 1, bwid - 60, 7, 3.5, stroke=0, fill=1)
        c.setFillColor(cl); c.roundRect(bx0 + 22, yy - 1, max(7, (bwid - 60) * v / big), 7, 3.5, stroke=0, fill=1)
        t8(bx0, yy, lb, "PopB", 6.2, K8["INK"]); t8(bx0 + bwid, yy, f"{v:.1f}", "PopB", 7, K8["INK"], "r")
    if D["settled"]:
        s = f"{'Won' if me > op else 'Lost' if me < op else 'Tied'} by {abs(me - op):.1f}  ·  {me - D['yproj']:+.1f} on Yahoo's projection for the lineup"
    elif D["started"]:
        s = f"{D['done_me']} of {D['n']} played, opponent {D['done_op']} of {D['n']}  ·  Yahoo projects {num8(D['tot'][0])} to {num8(D['tot'][1])}"
    else:
        s = f"Projected margin {sgn8(a - b)}  ·  Yahoo, lineups as set"
    t8(bx0 + bwid, y - 22, fit8(s, "Pop", 6, bwid), "Pop", 6, K8["GR"], "r")
    y -= 60; nd = D["nd"]
    _gauge8(x + gw * .22, y, 15, nd.get("ratcliffe"), "FTN"); _gauge8(x + gw * .5, y, 24, nd.get("yahoo"), "YAHOO", True)
    _gauge8(x + gw * .78, y, 15, nd.get("gotham"), "GOTHAM")
    cap = ("Win chance at the last read" if D["settled"] else "Win chance now — Yahoo center, FTN left, Gotham right" if D["started"]
           else "Win chance before kickoff — Yahoo center, FTN left, Gotham right")
    t8(x + gw / 2, y - 29, cap, "PopM", 6, K8["GR"], "c")
    # facts
    y -= 46; c.setStrokeColor(K8["LINE"]); c.setLineWidth(.5); c.line(x + 12, y + 12, x + gw - 12, y + 12)
    n = D["n"]
    if D["settled"]: pl = f"All {n} of {n} played  ·  Opponent {D['done_op']} of {n}"
    elif D["started"]: pl = f"{D['done_me']} of {n} final  ·  Opponent {D['done_op']} of {n}"
    else:
        tg = [ln8(r["name"]) + f" ({r['tag']})" for r in D["rows"] if r["name"] and r["tag"]]; nob = [ln8(r["name"]) for r in D["rows"] if r["name"] and r["vs"] == "BYE"]
        emp = sum(1 for r in D["rows"] if not r["name"])
        pl = ("; ".join(x_ for x_ in ((("Tagged: " + ", ".join(tg)) if tg else ""), (("On bye: " + ", ".join(nob)) if nob else ""), (f"{emp} empty slot" + ("s" if emp > 1 else "") if emp else "")) if x_)
              or f"All {n} starters set, none tagged")
    rec = rec8(D["rec0"])
    if D["after"]:
        mine = next((r for r in D["after"] if r["team"] == L["me"]), None)
        rl = f"{rec} entering Week {D['w']}, {rec8(mine['rec'])} now" if mine else f"{rec} entering Week {D['w']}"
    elif D["rec1"]:
        rl = (f"{rec} entering Week {D['w']}, {D['rec1']} head to head  ·  median game open" if D["lab"] == "DK IV" else f"{rec} entering Week {D['w']}, {D['rec1']} now")
    else: rl = f"{rec} entering Week {D['w']}" + ("  ·  median game too" if D["lab"] == "DK IV" else "")
    rank = L.get("rank"); pfr = L.get("pf_rank")
    if D["after"]:
        mine = next((r for r in D["after"] if r["team"] == L["me"]), None)
        if mine: rank = mine["rank"]; pfr = sorted([r["pf"] for r in D["after"]], reverse=True).index(mine["pf"]) + 1
    stl = (f"{rank}{sfx8(rank)} of {L['teams']}" + (" now" if D["after"] else " entering the week") + (f"  ·  {pfr}{sfx8(pfr)} in points" if pfr else "")) if rank else "Standings not read"
    for k_, v_ in (("Players", pl), ("Record", rl), ("Standing", stl)):
        t8(x + 14, y, k_, "PopB", 6.6, K8["INK"]); t8(x + 62, y, fit8(v_, "Pop", 6.6, gw - 76), "Pop", 6.6, K8["INK"]); y -= 11
    y -= 4; nt = L.get("teams") or 12; bw = (gw - 28) / nt
    for i in range(nt):
        bx = x + 14 + i * bw; on = (i + 1) == rank; inz = i < 6
        c.setFillColor(tc if on else (soft if inz else K8["BAR"])); c.roundRect(bx, y - 4, bw - 2.2, 13, 2, stroke=0, fill=1)
        t8(bx + bw / 2 - 1, y, str(i + 1), "PopB", 6.2, K8["CARD"] if on else (deep if inz else K8["GR"]), "c")
    px_ = x + 14 + 6 * bw - 1.1; c.setStrokeColor(K8["GOLD"]); c.setLineWidth(1.6); c.line(px_, y - 7, px_, y + 12)
    t8(x + 14 + 3 * bw, y - 13, "Playoff spots", "PopM", 5.6, deep, "c"); t8(px_ + 4, y - 13, "Playoff line", "PopB", 5.6, K8["GOLD"])

_LEAD8 = _PS8("lead8", fontName="Pop", fontSize=7.6, leading=11, textColor=_H8("#14213D"))
_PS8b = _PS8("pm8", fontName="Pop", fontSize=6.9, leading=9.6, textColor=_H8("#14213D"))
def _esc8(s): return str(s).replace("&", "&amp;").replace("<b>", "\x01").replace("</b>", "\x02").replace("<", "&lt;").replace(">", "&gt;").replace("\x01", "<b>").replace("\x02", "</b>")
def _para8(x2, gw, yy, html, st=None, pad=13, ymin=None):
    p_ = _PG8(dkname(_esc8(html)), st or _PS8b); _, h = p_.wrap(gw - 2 * pad, 400)
    if ymin is not None and yy - h < ymin: return yy
    p_.drawOn(c, x2 + pad, yy - h); return yy - h - 6
def _lst8(xs): return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
def _outlook14(D, moves):
    """Oct 14 (Dom): the Outlook reads as paragraphs - the matchup and what's at stake, where the week is won and lost
    slot by slot, and what can still change before kickoff - all generated from the meter's numbers."""
    L = D["L"]; lab = D["lab"]; rows = [r for r in D["rows"] if r["name"]]; nd = D["nd"]
    oppn = _tct(L["opp"]) if "_tct" in globals() else L["opp"]
    ym, yo = D["tot"]; ym = ym or 0; yo = yo or 0; mg = ym - yo
    g_, y_, s_ = nd.get("gotham"), nd.get("yahoo"), nd.get("ratcliffe")
    word = "as the favorite" if (y_ or 50) > 55 else "as the underdog" if (y_ or 50) < 45 else "in a toss-up"
    orr = rec8(L.get("opp_record", "")) + (f", {L['opp_rank']}{sfx8(L['opp_rank'])} of {L['teams']}" if L.get("opp_rank") else "")
    lead = (f"{lab} goes in {word}. Yahoo projects {ym:.1f} to {yo:.1f} against {oppn} ({orr}), a {abs(mg):.1f}-point "
            f"{'edge' if mg >= 0 else 'gap'}. Win chance: Yahoo {num8(y_, 0)}%, FTN {num8(s_, 0)}%, Gotham {num8(g_, 0)}%.")
    vals = [v for v in (y_, g_, s_) if v is not None]
    BM = L.get("best_moves") or {}
    opbest = (BM.get("gotham") or {}).get("op") or []
    opbest = [m for m in opbest if m.get("into") and not m["into"].startswith("(") and (m.get("in_v") or 0) - (m.get("out_v") or 0) >= 1]
    if len(vals) > 1 and max(vals) - min(vals) >= 10:
        lead += (f" The engines split by {max(vals) - min(vals):.0f}: Yahoo uses the lineups as set, FTN and Gotham the best ones"
                 + (f" - and {oppn}'s best adds {'; '.join(m['into'] + (' in an empty seat' if str(m['out']).startswith('(') else ' for ' + ln8(m['out'])) + ' (' + sgn8(m['in_v'] - m['out_v']) + ')' for m in opbest[:2])}." if opbest else "."))
    elif len(vals) > 1: lead += " The three engines agree."
    rk = L.get("rank"); tm_ = L.get("teams") or 12
    if rk:
        lead += (f" At {rec8(L.get('record', ''))}, {rk}{sfx8(rk)} of {tm_}: " +
                 (f"{rk - 6} spot{'s' if rk - 6 > 1 else ''} below the playoff line, so this week counts." if rk > 6 else
                  "on the playoff line, with no room to give back." if rk == 6 else f"{6 - rk} spot{'s' if 6 - rk > 1 else ''} inside the playoff line."))
    # slot by slot, Yahoo projections
    pairs = [(r["slot"], r["name"], r["ypre"], r["opn"], r["opproj"]) for r in D["rows"] if r["name"] and r["ypre"] is not None and r.get("opproj") is not None and r["slot"] not in ("K", "DEF")]
    ed = sorted(pairs, key=lambda p: -(p[2] - p[4]))
    good = [p for p in ed if p[2] - p[4] >= 2][:2]; bad = [p for p in reversed(ed) if p[2] - p[4] <= -2][:2]
    p2 = ""
    _vs = lambda p: f"an empty {p[0]}" if str(p[3]).startswith("(") or p[3] in ("—", "") else f"{p[3]} at {p[0]}"
    if good: p2 += "Your edges: " + "; ".join(f"{ln8(p[1])} over {_vs(p)} ({sgn8(p[2] - p[4])})" for p in good) + ". "
    if bad: p2 += "Theirs: " + "; ".join(f"{p[3]} over {ln8(p[1])} at {p[0]} ({sgn8(p[2] - p[4])})" for p in bad) + ". "
    cool = sorted([r for r in rows if r["ypre"] and r.get("gpre") is not None and r["ypre"] - r["gpre"] >= 3], key=lambda r: r["gpre"] - r["ypre"])[:2]
    if cool: p2 += ("Gotham is cooler than Yahoo on " + _lst8([f"{ln8(r['name'])} ({r['gpre']:.1f} vs {r['ypre']:.1f})" for r in cool])
                    + " - his workload doesn't support Yahoo's number, so lean on him less.")
    # before kickoff: tags, byes, empty seats, the engines' lineup calls, and whether they can close the gap
    todo = [f"{ln8(r['name'])} is {r['tag']}" for r in rows if r["tag"] in ("Q", "D", "O", "IR")] + [f"{ln8(r['name'])} is on bye" for r in rows if r["vs"] == "BYE"]
    emp = sum(1 for r in D["rows"] if not r["name"])
    if emp: todo.append(f"{emp} starting slot{'s' if emp > 1 else ''} empty")
    p3 = ("; ".join(todo) + ". ") if todo else "Lineup set, no starter tagged. "
    mine = {}
    for eng in ("ratcliffe", "gotham"):
        for m in (BM.get(eng) or {}).get("me") or []:
            if m.get("into") and not m["into"].startswith("(") and (m.get("in_v") or 0) - (m.get("out_v") or 0) >= .5:
                mine.setdefault((m["out"], m["into"]), []).append((eng, m["in_v"] - m["out_v"]))
    lift = 0.0
    if mine:
        calls = []
        for (o, i), v in sorted(mine.items(), key=lambda kv: -max(x[1] for x in kv[1]))[:2]:
            who = "FTN and Gotham both" if len(v) > 1 else {"ratcliffe": "FTN"}.get(v[0][0], v[0][0].capitalize())
            calls.append(f"{who} would start {ln8(i)} over {ln8(o)} ({sgn8(max(x[1] for x in v))})"); lift += max(x[1] for x in v)
        p3 += "; ".join(calls) + ". "
    if mg < 0:
        p3 += (f"The best lineup closes about {lift:.1f} of the {abs(mg):.1f}-point gap, so the rest has to come from the starters beating their projections - check the Scout for an add that lifts this week."
               if lift < abs(mg) - 1 else f"Making {'that move' if len(mine) == 1 else 'those moves'} roughly closes the gap.")
    out = [("Before kickoff", p3.strip())]
    if p2: out.append(("Where it's won and lost", p2.strip()))
    mv = [m_["text"].split(" - ")[0].split(" — ")[0] for m_ in moves][:2]
    if mv: out.append(("Scout", "; ".join(mv) + ". Dom's call."))
    return lead, out

def story8(D, moves):
    """the card's words, generated from the numbers. Returns (lead paragraph, [(label, text)])"""
    L = D["L"]; rows = [r for r in D["rows"] if r["name"]]; me, op = D["me_sc"], D["op_sc"]; lab = D["lab"]
    oppn = _tct(L["opp"]) if "_tct" in globals() else L["opp"]
    if not D["started"]:
        return _outlook14(D, moves)   # Oct 14 (Dom): paragraphs, not a few lines
        ym, yo = D["tot"]; nd = D["nd"]
        lead = (f"Yahoo has {lab} at {num8(ym)} against {num8(yo)} for {oppn} ({rec8(L.get('opp_record', ''))}"
                + (f", {L['opp_rank']}{sfx8(L['opp_rank'])}" if L.get("opp_rank") else "") + f"). Win chance: Yahoo {num8(nd.get('yahoo'), 0)}%, "
                f"FTN {num8(nd.get('ratcliffe'), 0)}%, Gotham {num8(nd.get('gotham'), 0)}%.")
        vals = [v for v in (nd.get("yahoo"), nd.get("gotham"), nd.get("ratcliffe")) if v is not None]
        if len(vals) > 1: lead += " The three agree." if max(vals) - min(vals) < 10 else f" They split by {max(vals) - min(vals):.0f} points — read the tags below."
        car = sorted([r for r in rows if r["ypre"]], key=lambda r: -r["ypre"])[:3]
        out = [("Carrying the load", "; ".join(f"{ln8(r['name'])} {r['ypre']:.1f}" for r in car) + ".")] if car else []
        op_ = sorted([(r["opproj"], r["opn"]) for r in D["rows"] if r.get("opproj")], reverse=True)[:2]
        if op_: out.append(("Their best", "; ".join(f"{n_} {v:.1f}" for v, n_ in op_) + "."))
        todo = [f"{ln8(r['name'])} is {r['tag']}" for r in rows if r["tag"] in ("Q", "D", "O", "IR")] + [f"{ln8(r['name'])} is on bye" for r in rows if r["vs"] == "BYE"]
        emp = sum(1 for r in D["rows"] if not r["name"])
        if emp: todo.append(f"{emp} starting slot{'s' if emp > 1 else ''} empty")
        out.append(("Before kickoff", ("; ".join(todo) + ".") if todo else "Nothing to fix. Lineup set, no starter tagged."))
        mv = [m_["text"].split(" - ")[0].split(" — ")[0] for m_ in moves][:2]
        if mv: out.append(("Scout", "; ".join(mv) + ". Dom's call."))
        return lead, out
    ypj = D["yproj"]; done = D["settled"]
    deltas = sorted([(r["score"] - r["opsc"], r) for r in D["rows"] if r["name"] and r["score"] is not None and r["opsc"] is not None and r["final"] and r["opfinal"]], key=lambda t: -t[0])
    beat = sorted([r for r in rows if r["final"] and r["score"] is not None and r["ypre"] and r["score"] - r["ypre"] >= 6], key=lambda r: r["ypre"] - r["score"])
    short = sorted([r for r in rows if r["final"] and r["score"] is not None and r["ypre"] and r["score"] - r["ypre"] <= -4], key=lambda r: r["score"] - r["ypre"])
    ob = max([r for r in D["rows"] if r["opsc"] is not None], key=lambda r: r["opsc"], default=None)
    mg = me - op
    if done:
        kind = ("A blowout." if abs(mg) >= 40 else "A clear win." if mg >= 15 else "A close win." if mg > 0 else "A close loss." if mg > -15 else "A clear loss." if mg > -40 else "A beating.")
        lead = f"<b>{kind}</b> {lab} scored {me:.1f}, {abs(me - ypj):.1f} {'more' if me >= ypj else 'less'} than Yahoo projected for the lineup ({ypj:.1f}), and {'beat' if mg > 0 else 'lost to' if mg < 0 else 'tied'} {oppn} {'by ' + f'{abs(mg):.1f}' if mg else ''}. "
    else:
        left = D["n"] - D["done_me"]; oleft = D["n"] - D["done_op"]
        lead = (f"<b>{'Ahead' if mg > 0 else 'Behind' if mg < 0 else 'Level'}, {me:.1f} to {op:.1f}.</b> {left} of {lab}'s {D['n']} still to finish, {oleft} of theirs. "
                f"Yahoo projects {num8(D['tot'][0])} to {num8(D['tot'][1])} at the end; win chance {num8(D['nd'].get('yahoo'), 0)}%. ")
    if deltas and deltas[0][0] > 0:
        d0, r0 = deltas[0]; lead += f"{r0['name']} led the way: {r0['score']:.1f} points, {d0:.1f} more than the man across from him. "
    oth = [r for r in beat if not deltas or r is not deltas[0][1]]
    if oth: lead += f"{_lst8([f'{ln8(r['name'])} ({r['score']:.1f})' for r in oth])} beat {'their projections' if len(oth) > 1 else 'his projection'} by 6 or more. "
    if short: lead += f"The soft spot: {_lst8([f'{ln8(r['name'])} {r['score']:.1f} on {r['ypre']:.1f}' for r in short[:2]])}. "
    if ob: lead += f"{oppn}'s best was {ob['opn']} at {ob['opsc']:.1f}."
    if done and D["rec1"]: lead += f" {lab} moves to {rec8(next((r['rec'] for r in (D['after'] or []) if r['team'] == L['me']), D['rec1']))}."
    out = []
    top3 = [d for d in deltas if d[0] > 0][:3]; bot3 = sorted([d for d in deltas if d[0] < 0], key=lambda t: t[0])[:3]
    if mg >= 0 and top3: out.append(("What decided it", "; ".join(f"{ln8(r['name'])} {r['score']:.1f} vs {r['opn']} {r['opsc']:.1f} ({sgn8(d)})" for d, r in top3) + "."))
    elif bot3: out.append(("Where it was lost" if done else "Where it is slipping", "; ".join(f"{ln8(r['name'])} {r['score']:.1f} vs {r['opn']} {r['opsc']:.1f} ({sgn8(d)})" for d, r in bot3) + "."))
    bm = [b for b in D["bench"] if b["score"] is not None and any(r["score"] is not None and r["final"] and b["score"] > r["score"] and (r["pos"] == b["pos"] or (r["slot"] in ("FLEX", "SFLEX") and b["pos"] in ("RB", "WR", "TE"))) for r in rows)]
    fs = ("; ".join(f"{ln8(r['name'])} {r['score']:.1f} on a {r['ypre']:.1f} projection" for r in short) + ". ") if short else "Nobody 4 or more under his projection. "
    fs += ("Bench check: " + _lst8([f"{ln8(b['name'])} ({b['score']:.1f})" for b in bm]) + " outscored a starter he could have replaced." if bm
           else "Nobody on the bench outscored a starter he could have replaced.")
    out.append(("Fell short", fs))
    hurt = [f"{ln8(r['name'])} ({r['tag']}) " + (f"played and scored {r['score']:.1f}" if r["score"] is not None else "has not played") for r in rows if r["tag"]]
    hurt += [f"{ln8(b['name'])} ({b['tag']}) on the bench" for b in D["bench"] if b["tag"]]
    mv = [m_["name"] + (" to IR once Yahoo lists him Out" if m_["kind"] == "ir" else " - hold him" + (f"; free {m_['free']} if a seat is needed" if m_.get('free') else "") if m_["kind"] == "hold" else " is a drop candidate") for m_ in moves][:2]
    out.append(("Injuries", ("; ".join(hurt) + "." if hurt else "None among the starters.") + (" Scout: " + "; ".join(mv) + " — Dom's call." if mv else "")))
    if lab == "DK IV":
        md = globals().get("_MED8")
        out.append(("Median game", "Unknown until Monday night ends — Yahoo settles it with the last game." if not done or CAL_DOW == 0 else
                    (f"League median {md:.1f}; {lab} {'beat' if me > md else 'fell short of'} it." if md else "Settled in Tuesday's standings.")))
    return lead, out

def pmcard8(x2, gw, D, tc, title, state, fill, moves):
    top = _CTOP8; _card8(x2, gw, title, state, fill, tc)
    lead, parts = story8(D, moves)
    ymin = top - _GH8 + 18
    yy = _para8(x2, gw, top - 42, lead, _LEAD8)
    c.setStrokeColor(K8["LINE"]); c.setLineWidth(.5); c.line(x2 + 13, yy + 2, x2 + gw - 13, yy + 2); yy -= 6
    for k_, v_ in parts: yy = _para8(x2, gw, yy, f"<b>{k_}.</b> {v_}", ymin=ymin)
    if title == "Post-Mortem" and CAL_DOW == 0: foot = "Final edition Tuesday, after stat fixes"
    elif title == "Post-Mortem" and state == "FINAL": foot = "Final — stat corrections in"
    elif title == "Post-Mortem": foot = f"Week {D['w']}, looking back"
    else: foot = f"Week {D['w']}, looking ahead"
    t8(x2 + 13, top - _GH8 + 7, foot, "PopM", 5.6, K8["GR"])
    if D.get("read"): t8(x2 + gw - 11, top - _GH8 + 7, "Yahoo read " + _pt_txt8(D["read"]), "PopM", 5.6, K8["GR"], "r")

# ================================================================ MARKERS
_MCOL8 = {"red": K8["RED"], "gold": K8["GOLD"], "green": K8["GREEN"], "grey": K8["GR2"]}
def g_radar8(x, y, col, n_):
    c.setStrokeColor(col); c.setFillColor(col); c.setLineWidth(1); c.circle(x + 1.5, y + 1, 1.1, stroke=0, fill=1)
    for r_ in (3.2, 5.4): c.arc(x + 1.5 - r_, y + 1 - r_, x + 1.5 + r_, y + 1 + r_, 10, 70)
    t8(x + 7.2, y - .4, str(n_), "PopB", 5, col); return 12
def g_scout8(x, y, col, age):
    c.setStrokeColor(col); c.setLineWidth(1.1); c.circle(x + 3, y + 2.4, 2.6, stroke=1, fill=0); c.line(x + 4.9, y + .5, x + 7, y - 1.6)
    t8(x + 8.4, y - .4, f"{age:02d}", "PopB", 4.8, col); return 16
def g_drift8(x, y, up): t8(x, y, "D", "PopB", 7.2, K8["GREEN"] if up else K8["RED"]); return 9
def g_trend8(x, y, up):
    col = K8["GREEN"] if up else K8["RED"]; c.setStrokeColor(col); c.setFillColor(col); c.setLineWidth(1.1)
    p_ = c.beginPath()
    if up: c.line(x + 3, y - 1.2, x + 3, y + 4.2); p_.moveTo(x + .4, y + 3); p_.lineTo(x + 3, y + 6); p_.lineTo(x + 5.6, y + 3)
    else: c.line(x + 3, y + 5.6, x + 3, y + .4); p_.moveTo(x + .4, y + 1.6); p_.lineTo(x + 3, y - 1.4); p_.lineTo(x + 5.6, y + 1.6)
    p_.close(); c.drawPath(p_, stroke=0, fill=1); return 9

_ALURL8 = "https://claude.ai/code/artifact/2342ca1f-956b-4342-b3d0-f801496c1ed2"
_AL8 = None
def _alerts8(lab):
    global _AL8
    if _AL8 is None:
        _AL8 = {}
        try:
            _now = _d8.datetime.now(_d8.timezone.utc)
            for _x in _j8.load(open(_os8.path.join(_REPO8, "dispatch_out", "alerts_build.json"))).get("items", []):
                _t = _x.get("first_seen") if _x.get("active") else (_x.get("resolved_at") or _x.get("last_seen"))
                if not _t or (_now - _d8.datetime.fromisoformat(str(_t).replace("Z", "+00:00"))).days >= 7: continue
                _c = _x.get("color", "grey") if _x.get("active") else "green"
                _k = (_x.get("lg"), norm(_x.get("who") or ""))
                _r = {"red": 4, "gold": 3, "grey": 1, "green": 2}
                if _r.get(_c, 0) > _r.get(_AL8.get(_k), 0): _AL8[_k] = _c
        except Exception as _e: print("alert marks skipped:", _e)
    return {k[1]: v for k, v in _AL8.items() if k[0] == lab}
def g_alert8(x, y, col):
    c.setFillColor(col); p_ = c.beginPath()
    p_.moveTo(x + .4, y - .4); p_.lineTo(x + 6.6, y - .4); p_.lineTo(x + 5.7, y + .9); p_.lineTo(x + 5.7, y + 3.4)
    p_.curveTo(x + 5.7, y + 6.9, x + 1.3, y + 6.9, x + 1.3, y + 3.4); p_.lineTo(x + 1.3, y + .9); p_.close()
    c.drawPath(p_, stroke=0, fill=1); c.circle(x + 3.5, y - 1.5, .95, stroke=0, fill=1); return 8
def marks8(x, y, nm, MK):
    k = norm(nm); RAD, SCO, EN_ = MK; out = []
    _ac = _alerts8(globals().get("_MKLAB8", "")).get(k)   # Oct 14 (Dom): the alert mark leads the column
    if _ac: out.append(lambda xx: g_alert8(xx, y, {"red": K8["RED"], "gold": K8["GOLD"], "green": K8["GREEN"]}.get(_ac, K8["GR2"])))
    if k in RAD: out.append(lambda xx: g_radar8(xx, y, _MCOL8.get(RAD[k].get("color"), K8["GR2"]), RAD[k].get("count", 1)))
    v = SCO.get(k) or next((v for sk, v in SCO.items() if sk and (sk.endswith(" " + k) or k.endswith(" " + sk))), None)
    if v: out.append(lambda xx: g_scout8(xx, y, _MCOL8.get(v[0], K8["GOLD"]), v[1]))
    e = EN_.get(k)
    if e is not None and str(getattr(e, "drift", "")) == "D":
        sw = getattr(e, "drift_swing", 0); out.append(lambda xx: g_drift8(xx, y, (sw if sw == sw else 0) > 0))
    t = getattr(e, "trend", None) if e is not None else None
    if t is not None and t == t and abs(t) >= .15: out.append(lambda xx: g_trend8(xx, y, t > 0))
    _dest = {"g_radar8": "scout", "g_scout8": "scout", "g_drift8": "pos", "g_trend8": "pos"}   # Oct 14 (Dom): every mark links to its source
    for f_ in out[:4]:
        w_ = f_(x); nm_ = next((n for n in f_.__code__.co_names if n in _dest), None); lab_ = globals().get("_MKLAB8")
        if nm_ is None and "g_alert8" in f_.__code__.co_names:
            try: c.linkURL(_ALURL8, (x - 1, y - 3, x + w_ + 1, y + 8), relative=0, thickness=0)
            except Exception: pass
        if nm_ and lab_:
            try: c.linkRect("", "dk_" + _dest[nm_] + "_" + lab_.replace(" ", ""), (x - 1, y - 3, x + w_ + 1, y + 8), relative=0, thickness=0)
            except Exception: pass
        x += w_ + 2

# ================================================================ THE TABLES
def _cols8():
    return [("PLAYER", M + 4, "l"), ("MARKERS", M + 126, "l"), ("POS", M + 180, "l"), ("TEAM", M + 198, "l"), ("SLOT", M + 220, "l"), ("VS", M + 246, "l"),
            ("BYE", M + 282, "r"), ("YAHOO", M + 308, "r"), ("FTN", M + 338, "r"), ("GOTHAM", M + 366, "r"), ("SCORE", M + 396, "r"), ("NEXT 3", M + 422, "r"),
            ("AVG", M + 444, "r"), ("OPPONENT", M + 454, "l"), ("SCORE", M + 510, "r"), ("DELTA", W - M - 4, "r")]
RH8 = 12.8
def head8(y, title, sub, tc, opp=True, right=None):
    cols = _cols8(); CX = {k + (str(i) if k == "SCORE" else ""): xx for i, (k, xx, a) in enumerate(cols)}
    c.setFillColor(tc); c.rect(M, y - 1, 3, 13, stroke=0, fill=1)
    t8(M + 8, y, title, "Bebas", 19, K8["INK"]); t8(M + 14 + w8(title, "Bebas", 19), y + 1, sub, "Pop", 6.6, K8["GR"])
    c.setStrokeColor(K8["INK"]); c.setLineWidth(.9); c.line(M, y - 5, W - M, y - 5)
    c.setStrokeColor(K8["GR2"]); c.setLineWidth(.5); c.line(CX["YAHOO"] - 24, y - 14.5, CX["GOTHAM"], y - 14.5)
    t8((CX["YAHOO"] - 24 + CX["GOTHAM"]) / 2, y - 12.6, "PROJECTED BEFORE KICKOFF", "PopB", 4.6, K8["GR"], "c")
    for i, (k, xx, a) in enumerate(cols):
        if not opp and (k in ("OPPONENT", "DELTA") or (k == "SCORE" and i == 14)): continue
        t8(xx, y - 21, k, "PopB", 5.4, K8["GR"], a)
    if right: t8(CX["OPPONENT"], y - 21, right, "PopB", 5.4, _mx8(tc, K8["INK"], .45))
    return y - 33
def row8(y, r, i, tc, MK, opp=True, why=None):
    cols = _cols8(); CX = {k + (str(i_) if k == "SCORE" else ""): xx for i_, (k, xx, a) in enumerate(cols)}
    s9, s13 = CX["SCORE10"], CX["SCORE14"]
    if i % 2 == 0: c.setFillColor(K8["BAND"]); c.rect(M, y - 4, (W - 2 * M) if opp else (CX["AVG"] + 6 - M), RH8, stroke=0, fill=1)
    if r.get("live") and not r.get("final"): c.setStrokeColor(tc); c.setLineWidth(1.4); c.roundRect(M + .7, y - 4, W - 2 * M - 1.4, RH8, 3, stroke=1, fill=0)
    if not r.get("name"):
        t8(M + 4, y, "OPEN", "PopB", 7, K8["RED"]); t8(CX["SLOT"], y, r.get("slot") or "", "Pop", 6.8, K8["INK"])
        if why: c.setFillColor(_mx8(tc, K8["CARD"], .86)); c.roundRect(CX["OPPONENT"] - 4, y - 3.4, W - M - CX["OPPONENT"] + 4, RH8 - 1.2, 3, stroke=0, fill=1); t8(CX["OPPONENT"], y, why, "PopM", 6.2, _mx8(tc, K8["INK"], .45))
        if opp and r.get("opn"):
            t8(CX["OPPONENT"], y, r["opn"], "Pop", 6.5, K8["INK"]); t8(s13, y, num8(r.get("opsc")), "PopS", 7.2, K8["INK"], "r")
        return
    tag = r["tag"]; pw = (w8("INJ " + tag, "PopB", 5.2) + 8) if tag else 0; fw = 6 if r["final"] else 0
    room = CX["MARKERS"] - 6 - (M + 4) - pw - fw
    nm = r["name"]
    if w8(nm, "PopS", 7.2) > room:
        s = nm.split(); nm = (s[0][0] + ". " + " ".join(s[1:])) if len(s) > 1 else nm
        nm = fit8(nm, "PopS", 7.2, room)
    t8(M + 4, y, nm, "PopS", 7.2, K8["INK"]); nx_ = M + 6 + w8(nm, "PopS", 7.2)
    if r["final"]: t8(nx_, y + 2.4, "F", "PopB", 5, K8["GR"]); nx_ += 6
    if tag: pill8(nx_ + 2, y + .4, "INJ " + tag, K8["CARD"], K8["RED"], "PopB", 5.2, 3, K8["RED"])
    marks8(CX["MARKERS"], y, r["name"], MK)
    for k in ("POS", "TEAM", "SLOT", "VS"):
        v = str(r[k.lower()] if k != "SLOT" else r["slot"]); t8(CX[k], y, v, "Pop", 6.8, K8["RED"] if v == "BYE" else K8["INK"])
    t8(CX["BYE"], y, str(r["bye"] or ""), "Pop", 6.8, K8["GR"], "r")
    for k, v in (("YAHOO", r["ypre"]), ("FTN", r["spre"]), ("GOTHAM", r["gpre"])):
        t8(CX[k], y, num8(v), "Pop", 6.9, K8["INK"] if k == "YAHOO" else K8["GR"], "r")
    sc = r["score"]; good = sc is not None and r["final"] and r.get("ypre") and sc - r["ypre"] >= 3; bad = sc is not None and r["final"] and r.get("ypre") and sc - r["ypre"] <= -4
    t8(s9, y, num8(sc), "PopB", 7.4, K8["GREEN"] if good else (K8["RED"] if bad else K8["INK"]), "r")
    t8(CX["NEXT 3"], y, num8(r["nxt"]), "Pop", 6.9, K8["INK"], "r"); t8(CX["AVG"], y, num8(r["av"]), "Pop", 6.9, K8["INK"], "r")
    if opp:
        t8(CX["OPPONENT"], y, fit8(r["opn"], "Pop", 6.5, s13 - CX["OPPONENT"] - 22), "Pop", 6.5, K8["INK"])
        if r["opsc"] is not None:
            t8(s13, y, num8(r["opsc"]), "PopS", 7.2, K8["INK"], "r")
            if r["opfinal"]: t8(s13 + 1.5, y + 2.4, "F", "PopB", 5, K8["GR"])
        elif r.get("opproj") is not None: t8(s13, y, num8(r["opproj"]), "Pop", 6.4, K8["GR2"], "r")
        if sc is not None and r["opsc"] is not None:
            d = sc - r["opsc"]; t8(CX["DELTA"], y, sgn8(d), "PopB", 7.2, K8["GREEN"] if d >= 0 else K8["RED"], "r")
    if why:
        c.setFillColor(_mx8(tc, K8["CARD"], .86)); c.roundRect(CX["OPPONENT"] - 4, y - 3.4, W - M - CX["OPPONENT"] + 4, RH8 - 1.2, 3, stroke=0, fill=1)
        wmax = W - M - CX["OPPONENT"] - 4; opts = why.split("|"); why = next((o for o in opts if w8(o, "PopM", 6.2) <= wmax), opts[-1])
        t8(CX["OPPONENT"], y, fit8(why, "PopM", 6.2, wmax), "PopM", 6.2, _mx8(tc, K8["INK"], .45))
def why8(b, D, moves):
    """why a bench or IR man is held - from the roster itself and the Scout's moves"""
    w = D["w"]; rows = [r for r in D["rows"] if r["name"]]
    for m_ in moves:
        if norm(m_.get("name", "")) == norm(b["name"]):
            return "Scout: IR once tagged Out" if m_["kind"] == "ir" else "Scout: hold him" if m_["kind"] == "hold" else "Scout: drop candidate"
    if b["slot"] == "IR": return "On IR  ·  holds no roster seat"
    if b["tag"] in ("O",): return f"Out this week  ·  {b['pos']} depth"
    if b["vs"] == "BYE": return f"On bye  ·  back Wk {w + 1}"
    same = [r for r in rows if r["pos"] == b["pos"] == "RB" and r["team"] == b["team"]]
    if same: return f"Handcuff to {ln8(same[0]['name'])}"
    cover = [r for r in rows if r["pos"] == b["pos"] and r["bye"] and w < r["bye"] <= w + 4 and r["bye"] != b["bye"]]
    if cover:
        r0 = min(cover, key=lambda r: r["bye"]); n0 = ln8(r0["name"]); ps = n0 + ("'" if n0.endswith("s") else "'s")
        return f"Covers {ps} Wk {r0['bye']} bye|Covers {n0}, Wk {r0['bye']}|Wk {r0['bye']} bye cover"
    if b["pos"] == "QB" and any(r["slot"] == "SFLEX" for r in rows): return "Superflex depth at QB"
    return (f"Depth at {b['pos']}  ·  {b['nxt']:.1f} next 3|" if b.get("nxt") else "") + f"Depth at {b['pos']}"
def legend8(y, tc):
    col1 = [("F", "game final, SCORE is real. No F: still a projection."), ("INJ", "Yahoo's tag: Q questionable, D doubtful, O out, IR."),
            ("Score", "green = beat Yahoo's projection by 3+; red = 4+ short."), ("Projected", "each source before kickoff; Gotham skips K and DEF.")]
    for i, (k, v) in enumerate(col1): t8(M + 4, y - i * 9, k, "PopB", 5.8, K8["INK"]); t8(M + 40, y - i * 9, v, "Pop", 5.8, K8["GR"])
    kx = M + 268
    t8(kx, y, "Band", "PopB", 5.8, K8["INK"]); c.setStrokeColor(tc); c.setLineWidth(1.3); c.roundRect(kx + 34, y - 3, 36, 9, 2.5, stroke=1, fill=0)
    t8(kx + 76, y, "around a whole row: he is playing right now.", "Pop", 5.8, K8["GR"])
    yy = y - 9; t8(kx, yy, "Markers", "PopB", 5.8, K8["INK"]); mx = kx + 34
    mx += g_radar8(mx, yy, K8["RED"], 2) + 1; t8(mx, yy, "Radar news (count)", "Pop", 5.8, K8["GR"]); mx += w8("Radar news (count)", "Pop", 5.8) + 7
    mx += g_scout8(mx, yy, K8["RED"], 3) + 1; t8(mx, yy, "Scout need (days)", "Pop", 5.8, K8["GR"])
    yy -= 9; mx = kx + 34
    mx += g_drift8(mx, yy, True) + 1; t8(mx, yy, "role drift", "Pop", 5.8, K8["GR"]); mx += w8("role drift", "Pop", 5.8) + 7
    mx += g_trend8(mx, yy, True) + 1; t8(mx, yy, "playing time up / down", "Pop", 5.8, K8["GR"])
    yy -= 9; t8(kx + 34, yy, "Red = act, gold = watch, green = good. Up to four per man, news first.", "Pop", 5.8, K8["GR"])
    return y - 36

def legend8s(y, tc):
    x = M + 4
    for k, v in (("F", "final"), ("INJ", "Yahoo tag"), ("Score", "green beat Yahoo by 3+, red 4+ short"), ("Band", "playing now")):
        t8(x, y, k, "PopB", 5.8, K8["INK"]); x += w8(k, "PopB", 5.8) + 3; t8(x, y, v, "Pop", 5.8, K8["GR"]); x += w8(v, "Pop", 5.8) + 9
    t8(x, y, "Markers", "PopB", 5.8, K8["INK"]); x += w8("Markers", "PopB", 5.8) + 4
    x += g_alert8(x, y, K8["RED"]) + 1; t8(x, y, "alert", "Pop", 5.8, K8["GR"]); x += w8("alert", "Pop", 5.8) + 6
    x += g_radar8(x, y, K8["RED"], 2) + 1; t8(x, y, "news", "Pop", 5.8, K8["GR"]); x += w8("news", "Pop", 5.8) + 6
    x += g_scout8(x, y, K8["RED"], 3) + 1; t8(x, y, "Scout need", "Pop", 5.8, K8["GR"]); x += w8("Scout need", "Pop", 5.8) + 6
    x += g_drift8(x, y, True) + 1; t8(x, y, "drift", "Pop", 5.8, K8["GR"]); x += w8("drift", "Pop", 5.8) + 6
    x += g_trend8(x, y, True) + 1; t8(x, y, "playing time", "Pop", 5.8, K8["GR"])
    return y - 10

# ================================================================ THE PAGE
_YLIM8 = 32
def _cardweek8(lab):
    """which week the two cards speak about: the current one once it has started or before it starts Thu-Sun;
    Monday-Wednesday with nothing played yet, the week just finished (the last saved read of it)"""
    D = league8(lab, MTR)
    if D["started"] or CAL_DOW not in (0, 1): return D   # Oct 12 (Dom): Outlook from Wednesday
    try: PM = _j8.load(open(_os8.path.join(_REPO8, "dispatch_out", f"meter_wk{WEEKN - 1}.json")))
    except Exception: return D
    if lab not in PM.get("leagues", {}): return D
    return league8(lab, PM)
def field_report8(c_, pg, lab):
    """draws the league's Field Report; returns the number of pages used"""
    global c
    c = c_; tc = TEAMC8[lab]
    D = league8(lab, MTR); CD = _cardweek8(lab) if not D["started"] else D
    RAD = _radar8(WEEKN).get(lab, {}); SCO, moves = _scout8(lab); MK = (RAD, SCO, eng8(lab)); globals()["_MKLAB8"] = lab   # Oct 14: marks link to this league's pages
    print("FIELD v8", dkname(lab), "| cards week", CD["w"], "| started", CD["started"], "settled", CD["settled"], "| me", round(CD["me_sc"], 1), "op", round(CD["op_sc"], 1),
          "| rows", len(D["rows"]), "bench", len(D["bench"]), "ir", len(D["irs"]), "| radar", len(RAD), "scout", len(SCO), "moves", len(moves))
    masthead(c, f"FIELD REPORT  ·  {lab}", "")
    gw = (W - 2 * M - 10) / 2
    scorecard8(M, gw, CD, tc)
    if CAL_DOW in (0, 1) and CD["started"]:
        title = "Post-Mortem"; st, fl = (("PROVISIONAL", K8["GOLD"]) if CAL_DOW == 0 or not CD["settled"] else ("FINAL", K8["GREEN"])) if CAL_DOW in (0, 1) else (None, None)
    else:
        title = "Outlook"; st, fl = (("LIVE", K8["GOLD"]) if CD["started"] and not CD["settled"] else ("FINAL", K8["GREEN"]) if CD["settled"] else (f"WEEK {CD['w']}", _mx8(tc, K8["INK"], .45)))
    pmcard8(M + gw + 10, gw, CD, tc, title, st, fl, moves)
    # tables
    O = open_counts(lab) if "open_counts" in globals() else dict(bench=0, ir=0)
    bench = D["bench"] + [dict(name=None, slot="BN")] * O.get("bench", 0); irs = D["irs"] + [dict(name=None, slot="IR")] * O.get("ir", 0)
    y = _CTOP8 - _GH8 - 18
    y = head8(y, "Starters", f"Lineup as set on Yahoo  ·  Week {D['w']}", tc)
    for i, r in enumerate(D["rows"]): row8(y, r, i, tc, MK); y -= RH8
    cols = _cols8(); CX = {k + (str(i) if k == "SCORE" else ""): xx for i, (k, xx, a) in enumerate(cols)}
    c.setStrokeColor(K8["INK"]); c.setLineWidth(.6); c.line(M, y + RH8 - 4.4, W - M, y + RH8 - 4.4); y -= 2
    t8(M + 4, y, "TOTAL", "PopB", 6.6, K8["INK"]); t8(CX["YAHOO"], y, f"{D['yproj']:.1f}", "PopB", 7.2, K8["INK"], "r")
    if D["started"]:
        t8(CX["SCORE10"], y, f"{D['me_sc']:.1f}", "PopB", 7.6, K8["INK"], "r"); t8(CX["SCORE14"], y, f"{D['op_sc']:.1f}", "PopB", 7.6, K8["INK"], "r")
        t8(CX["DELTA"], y, sgn8(D["me_sc"] - D["op_sc"]), "PopB", 7.6, K8["GREEN"] if D["me_sc"] >= D["op_sc"] else K8["RED"], "r")
    elif D["tot"][1] is not None: t8(CX["SCORE14"], y, f"{D['tot'][1]:.1f}", "Pop", 6.8, K8["GR2"], "r")
    need_b = 22 + 33 + len(bench) * RH8; need_i = 8 + 33 + len(irs) * RH8; need_l = 44
    pages = 1
    def _bench_ir(y):
        y = head8(y, "Bench", "Yahoo projects only the lineup", tc, False, "VALUE")
        for i, r in enumerate(bench): row8(y, r, i, tc, MK, False, why8(r, D, moves) if r.get("name") else "Open seat — see the Scout"); y -= RH8
        y -= 8
        if irs:
            cap = (_CAPS.get(lab, (0, len(irs)))[1] if "_CAPS" in globals() else len(irs))
            y = head8(y, "IR", f"{len(D['irs'])} of {cap} slot{'s' if cap != 1 else ''} used", tc, False, "VALUE")
            for i, r in enumerate(irs): row8(y, r, i, tc, MK, False, why8(r, D, moves) if r.get("name") else "Open IR slot"); y -= RH8
        return y
    if y - need_b - need_i - need_l >= _YLIM8:
        y -= 22; y = _bench_ir(y); y -= 4; legend8(y, tc)
    elif y - need_b - need_i - 12 >= _YLIM8:   # Oct 12: the long rosters keep one page - the key folds to one line
        y -= 22; y = _bench_ir(y); legend8s(y - 2, tc)
    else:
        if y - 22 - need_l >= _YLIM8: legend8(y - 22, tc); lg_done = True
        else: lg_done = False
        c.showPage(); pages = 2
        masthead(c, f"FIELD REPORT  ·  {lab}", "Bench and IR")
        y = MH8_BOT - 24; y = _bench_ir(y)
        if not lg_done: y -= 4; legend8(y, tc)
    c.showPage()
    return pages

# OCT12 scorecard word up

# OCT12 field hold outlook names

# OCT13 scorecard state word

# OCT14 outlook paragraphs

# OCT14 marks link to their source

# OCT14 alert mark
