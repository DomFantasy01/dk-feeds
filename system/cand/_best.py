# BEST LINEUP, BOTH SIDES (Dom, Tue Oct 13 2026, 5 PM): "we need to put in our best team as we see it, whether I have it
# filled out or all my spots are empty, and we also need to do it with our opponents, so we're looking apples to apples."
# Exec'd by meter_data.py right after _state.py (uses its globals: LEAGUES, LEAGUE_OUT, MATCH, GOT, POSMAP, TEAMWIN, T,
# norm, chance, sleeper_tables, ROOT, YDIR, _GAME, _NOWU, notes, alarms).
# For each league and each model (Gotham, Sleeper, Yahoo) it sets the best LEGAL lineup for Dom and for his opponent
# from everyone on the roster: a man who is out (O, IR, NA, suspended, PUP), on bye, or in an IR seat can't start; a man
# whose game has kicked off stays where Yahoo has him (locked), and a bench man whose game has kicked off can't come in.
# needles/totals then come from those best lineups; what the lineups say as SET is kept in needles_set/totals_set, and
# every swap is listed in best_moves so a page can say exactly what it assumed.
# Yahoo: bench projections come from the read's dom_benches file when there is one; a bench man with no Yahoo number is
# left out of the Yahoo lineup (never guessed). Yahoo's own posted win % stays as Yahoo posts it (needles.yahoo_posted).
import glob as _bg, os as _bo, math as _bm
_ELIG = {"QB": {"QB"}, "RB": {"RB"}, "WR": {"WR"}, "TE": {"TE"}, "K": {"K"}, "DEF": {"DEF"},
         "W/R/T": {"WR", "RB", "TE"}, "W/R": {"WR", "RB"}, "W/T": {"WR", "TE"}, "R/T": {"RB", "TE"},
         "Q/W/R/T": {"QB", "WR", "RB", "TE"}, "SUPER": {"QB", "WR", "RB", "TE"}}
_OUTS = {"O", "IR", "IR-R", "NA", "SUSP", "SUS", "PUP", "PUP-R"}
def _id(p):   # a defense is its team (Yahoo calls it "Bills" on one page and "Buffalo" on another)
    return "DEF:" + T(p.get("team") or "") if (p.get("pos") == "DEF" or p.get("slot") == "DEF") and p.get("team") else norm(p.get("player") or "")
def _bstart(team):
    g = _GAME.get(T(team or "")); return bool(g and _NOWU >= g[0])
# Yahoo bench projections, when the read carried them: lines "lg#ME bench##OPP bench", same row format as dom_matchups
_BY = {}
_bf = sorted(_bg.glob(YDIR + "dom_benches_*.txt"), key=_bo.path.getmtime)
_mf = sorted(_bg.glob(YDIR + "dom_matchups_*.txt"), key=_bo.path.getmtime)
if _bf and (not _mf or _bo.path.basename(_bf[-1]).split("_")[-1] == _bo.path.basename(_mf[-1]).split("_")[-1]):
    for _ln in open(_bf[-1]):
        if _ln.startswith("#") or "#" not in _ln: continue
        _lg, _rest = _ln.rstrip("\n").split("#", 1); _me, _op = (_rest.split("##") + [""])[:2]
        _BY[_lg] = {"me": {norm(p["player"]): p for p in parse_side(_me) if p["player"]},
                    "op": {norm(p["player"]): p for p in parse_side(_op) if p["player"]}}
else:
    notes.append("best lineup: no Yahoo bench projections in this read - the Yahoo lineup can only use who Yahoo shows starting")
# Oct 23: Dom's own bench Yahoo numbers for this week, from the weekly projections read (yproj_dk*.txt, MINE rows)
_YPW = {}
for _k4 in (1, 2, 3, 4):
    _yf = ROOT.replace("data/latest/", "") + f"scout/yproj_dk{_k4}.txt"
    if not _bo.path.exists(_yf): continue
    for _l in open(_yf):
        if _l.startswith("#"): continue
        _x = _l.rstrip("\n").split("|")
        if len(_x) >= 6 and _x[0] == str(WEEK) and _x[5] == "MINE":
            try: _YPW[(_k4, _id(dict(player=_x[1], team=T(_x[2]), pos=_x[3], slot=_x[3])))] = float(_x[4])
            except ValueError: pass
def _roster_rows(k, team_id):
    f = ROOT.replace("data/latest/", "") + f"scout/dk{k}_rosters_live.txt"
    if not _bo.path.exists(f): return None
    out = []
    for l in open(f):
        if l.startswith("#") or not l.strip(): continue
        x = (l.rstrip("\n").split("|") + [""] * 6)[:6]
        if x[0] == str(team_id): out.append(dict(slot=x[1], player=x[2], team=T(x[3]), pos=x[4], status=x[5]))
    return out
def _team_of(k, names):
    f = ROOT.replace("data/latest/", "") + f"scout/dk{k}_rosters_live.txt"
    if not _bo.path.exists(f): return None
    cnt = {}
    for l in open(f):
        if l.startswith("#") or not l.strip(): continue
        x = l.split("|")
        if len(x) > 2 and norm(x[2]) in names: cnt[x[0]] = cnt.get(x[0], 0) + 1
    return max(cnt, key=cnt.get) if cnt else None
def _best_lineup(starters, pool, col):
    """starters: the side as set (slot order kept). pool: every man on the roster with values. Returns (lineup, moves)."""
    slots = [p["slot"] for p in starters]
    lineup = [None] * len(slots); used = set()
    for i, p in enumerate(starters):                       # locked: his game has started (or finished)
        if p.get("actual") is not None or _bstart(p.get("team")):
            lineup[i] = dict(p, _v=(p["actual"] if p.get("actual") is not None else (p.get(col) or 0)), _lock=True); used.add(_id(p))
    def val(c):
        if c["status"].upper() in _OUTS or c.get("seat") == "IR" or TEAMWIN.get(c["team"]) is None: return None
        if _bstart(c["team"]): return None                 # can't be moved in once his game is on
        v = c["vals"].get(col); return None if v is None else float(v)
    order = sorted(range(len(slots)), key=lambda i: (len(_ELIG.get(slots[i], {slots[i]})), i))   # strict seats first, then flexes
    for i in order:
        if lineup[i] is not None: continue
        el = _ELIG.get(slots[i], {slots[i]})
        best = None
        for c in pool:
            if _id(c["row"]) in used or c["pos"] not in el: continue
            v = val(c)
            if v is None: continue
            if best is None or v > best[0]: best = (v, c)
        if best:
            used.add(_id(best[1]["row"])); lineup[i] = dict(best[1]["row"], slot=slots[i], _v=best[0], _lock=False)
        else:
            lineup[i] = dict(slot=slots[i], player="(nobody eligible)", team="", pos=slots[i], actual=None, _v=0.0, _lock=False,
                             yahoo=0.0, gotham=0.0, sleeper=0.0, ratcliffe=0.0)
    # the swaps, net of reshuffles: who sits that Yahoo has starting, who starts that Yahoo has sitting
    sid = {_id(p) for p in starters}; bid = {_id(p) for p in lineup if p["player"] != "(nobody eligible)"}
    outs = [p for p in starters if _id(p) not in bid]
    ins = [p for p in lineup if _id(p) not in sid]
    moves = []
    for j in range(max(len(outs), len(ins))):
        a = outs[j] if j < len(outs) else None; b = ins[j] if j < len(ins) else None
        moves.append(dict(out=a["player"] if a else None, out_v=round(float(a.get(col) or 0), 1) if a else None,
                          into=b["player"] if b else None, in_v=round(float(b["_v"]), 1) if b else None))
    return lineup, moves
for _lab, _cfg in LEAGUES.items():
    if _lab not in LEAGUE_OUT: continue
    _L = LEAGUE_OUT[_lab]
    try:
        _S, _KD = sleeper_tables(_cfg["k"]); _gm = GOT.get(_lab, {})
        _sides = {}
        for _side in ("me", "op"):
            _st = _L["starters"][_side]
            _names = {norm(p["player"]) for p in _st}
            _tid = {"DK I": 2, "DK II": 7, "DK III": 2, "DK IV": 6}[_lab] if _side == "me" else _team_of(_cfg["k"], _names)
            _rows = _roster_rows(_cfg["k"], _tid) if _tid else None
            if _rows is None:
                notes.append(f"{_lab}: best lineup - no roster for the {'your' if _side == 'me' else 'opponent'} side; using the lineup as set")
                _sides[_side] = None; continue
            _yb = _BY.get(_cfg["id"], {}).get(_side, {})
            _pool = []
            _stmap = {_id(p): p for p in _st}
            for r in _rows:
                k = norm(r["player"]); pos = r["pos"] if r["pos"] in ("K", "DEF") else POSMAP.get(k, r["pos"])
                if _id(dict(r, pos=pos)) in _stmap:
                    p = _stmap[_id(dict(r, pos=pos))]; vals = dict(gotham=p.get("gotham"), sleeper=p.get("sleeper"), yahoo=p.get("yahoo"), ratcliffe=p.get("ratcliffe"))
                    row = p; status = p.get("status") or r["status"]
                else:
                    if pos == "K": sl = _KD.get(("K", k)); go = sl
                    elif pos == "DEF": sl = _KD.get(("DEF", r["team"])); go = sl
                    else:
                        sl = _S.get(k); go = _gm.get(k)
                        go = None if go is None or (isinstance(go, float) and _bm.isnan(go)) else go
                    yb = _yb.get(k); yv = yb["yahoo"] if yb else None
                    if yv is None and _side == "me": yv = _YPW.get((_cfg["k"], _id(dict(r, pos=pos))))   # Oct 23: Dom's bench from the weekly Yahoo projections read
                    _from_gotham = go is not None and pos not in ("K", "DEF")
                    if go is None: go = yv if yv is not None else sl          # a bench man Gotham can't model: Yahoo, then Sleeper
                    # Oct 23 (Dom): the bench gets the SAME Gotham ceiling the starters get (meter_data.py, Oct 21). Without it a
                    # bench man's raw Gotham number (Pitts 14.2 on two touchdown games) beat a starter's capped number (Kelce 9.2)
                    # and the best lineup "started" Pitts over Kelce and Prescott over Stroud against every outside source.
                    if _from_gotham and sl is not None and float(sl) > 0:
                        _cap = (float(yv) + float(sl)) / 2 if yv is not None and float(yv) > 0 else float(sl)
                        if float(go) > _cap: go = _cap
                    _rcv = rc_of(_cfg["k"], r["player"], pos, r["team"])
                    vals = dict(gotham=None if go is None else round(float(go), 2), sleeper=None if sl is None else round(float(sl), 2), yahoo=yv,
                                ratcliffe=round(float(_rcv), 2) if _rcv is not None else (yv if yv is not None else (None if go is None else round(float(go), 2))))   # no Ratcliffe line: Yahoo, then Gotham
                    status = r["status"]
                    row = dict(slot="BN", player=r["player"], team=r["team"], status=status, kickoff="", actual=None, pos=pos,
                               yahoo=vals["yahoo"], gotham=vals["gotham"], gotham_src="bench", sleeper=vals["sleeper"] if vals["sleeper"] is not None else 0.0,
                               ratcliffe=vals["ratcliffe"] if vals["ratcliffe"] is not None else (yv if yv is not None else 0.0),
                               window=TEAMWIN.get(r["team"]))
                _pool.append(dict(player=r["player"], team=r["team"], pos=pos, status=(status or "").upper(), seat=r["slot"], vals=vals, row=row))
            _sides[_side] = _pool
        _best, _moves, _set = {}, {}, {}
        _cols = ("gotham", "sleeper", "yahoo") + (("ratcliffe",) if RC else ())
        for col in _cols:
            lu = {}
            for _side in ("me", "op"):
                if _sides[_side] is None: lu[_side] = [dict(p, _v=p.get(col) or 0) for p in _L["starters"][_side]]; _moves.setdefault(col, {})[_side] = []; continue
                lu[_side], mv = _best_lineup(_L["starters"][_side], _sides[_side], col)
                _moves.setdefault(col, {})[_side] = mv
            a, b, pct = chance([dict(p, **{col: p["_v"]}) for p in lu["me"]], [dict(p, **{col: p["_v"]}) for p in lu["op"]], col)
            _best[col] = (round(a, 2), round(b, 2), pct)
        _L["needles_set"] = dict(_L["needles"]); _L["totals_set"] = {k: (list(v) if v is not None else None) for k, v in _L["totals"].items()}
        _yb_ok = bool(_BY.get(_cfg["id"]))
        _L["needles"] = dict(gotham=_best["gotham"][2], sleeper=_best["sleeper"][2], ratcliffe=_best["ratcliffe"][2] if "ratcliffe" in _best else None,
                             yahoo=_best["yahoo"][2] if _yb_ok else _L["needles_set"].get("yahoo"), yahoo_best=_yb_ok,
                             yahoo_posted=_L["needles_set"].get("yahoo"), yahoo_from_spread=_L["needles_set"].get("yahoo_from_spread"))
        _L["totals"] = {c: [_best[c][0], _best[c][1]] for c in _cols}
        if not _yb_ok: _L["totals"]["yahoo"] = list(_L["totals_set"]["yahoo"]); _moves["yahoo"] = {"me": [], "op": []}
        _L["best_moves"] = _moves
        _L["best_note"] = ("Best legal lineups for both teams from each full roster (out, bye and IR men can't start; men whose game has "
                           "started stay put). Yahoo's own posted win % is for the lineups as set: " + str(_L["needles_set"].get("yahoo")) + "%.")
        print(f"BEST {_lab}: gotham {_L['needles_set'].get('gotham')}->{_L['needles']['gotham']}% | sleeper {_L['needles_set'].get('sleeper')}->{_L['needles']['sleeper']}%"
              f" | ratcliffe {_L['needles_set'].get('ratcliffe')}->{_L['needles'].get('ratcliffe')}% | yahoo set {_L['needles_set'].get('yahoo')}% -> best {_L['needles']['yahoo']}% | moves me {len(_moves['gotham']['me'])} op {len(_moves['gotham']['op'])}")
    except Exception as _e:
        alarms.append(f"{_lab}: best-lineup step failed ({type(_e).__name__}: {str(_e)[:120]}) - meters show the lineups as set")
