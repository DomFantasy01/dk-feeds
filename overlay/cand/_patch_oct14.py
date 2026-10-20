# THE OCT 14 SCOUT FIXES (Dom, Wed Oct 14 2026) - applied to the Scout on every build, after the Oct 10 batch.
# Safe to run twice (marker). Every anchor must match exactly once or the build stops - the Scout is never half-patched.
#  1  INJURED FREE AGENTS: the Scout read injury status only from Yahoo tags (rostered men) and nflverse's weekly files,
#     which lag - it ranked Tyquan Thornton first after he went on IR. Now ESPN's injury list and Sleeper's injury list
#     (both pulled every 30 min by the feed job) count too: IR/PUP/reserve = on IR, Out/Doubtful/Suspended = out this week.
#     The worse of the two sources wins. A Yahoo tag still wins for a man Yahoo has tagged.
#  2  ONE-GAME SPIKES: one bad game was already lifted to his next-worst; now one big game is also cut to his next-best
#     (4+ games). Calibrated Oct 14 against ESPN + Sleeper Week 6 projections: spike players read +1.3 pts a game too high
#     before, -0.1 after (183 players; everyone else's error also went down).
#  4  THE OUTLOOK on each Field Report card reads in paragraphs: the matchup and what's at stake, where the week is won
#     and lost slot by slot (and where Gotham doubts Yahoo), and what can still change before kickoff.
#  3  NAMES WITH INITIALS: "D.K. Metcalf" and "DK Metcalf" were two different men to the Scout (snap share read 0%).
#     Initials now join up ("d k metcalf" -> "dk metcalf") everywhere the Scout matches names.
import os
R=os.environ.get("DK_ROOT","/home/claude")
def patch(path,pairs,mark):
    s=open(path).read()
    if mark in s: print("   oct14:",path.split("/")[-1],"already in"); return
    for a,b,n in pairs:
        k=s.count(a); assert k==n,f"oct14 patch: {path.split('/')[-1]}: anchor found {k}x, expected {n}: {a[:80]}"
        s=s.replace(a,b)
    open(path,"w").write(s+f"\n# {mark}\n"); print("   oct14:",path.split("/")[-1],"patched -",mark)

patch(f"{R}/dksys/scout/scout_engine.py",[
 # 3 initials join up
 ('return " ".join(n.split())',
  'return re.sub(r"\\b([a-z])\\s+(?=[a-z]\\b)",r"\\1"," ".join(n.split()))   # Oct 14: "d k metcalf" -> "dk metcalf"',1),
 ('sn=pd.read_csv(f"{D}/snap_counts_2026.csv"); sn=sn[sn.game_type=="REG"]',
  'sn=pd.read_csv(f"{D}/snap_counts_2026.csv"); sn=sn[sn.game_type=="REG"].copy(); sn["_nk"]=sn.player.map(norm)',1),
 ('_sp=sn[(sn.player==name)&(sn.team==team)]',
  '_sp=sn[(sn._nk==norm(name))&(sn.team==team)]',1),
 # 2 one big game cut to his next-best
 ('    if len(v)>=4: lo=sorted(v)[1]; i=v.index(min(v)); v=v[:i]+[lo]+v[i+1:]\n',
  '    if len(v)>=4: lo=sorted(v)[1]; i=v.index(min(v)); v=v[:i]+[lo]+v[i+1:]\n'
  '    if len(v)>=4: hi=sorted(v)[-2]; i=v.index(max(v)); v=v[:i]+[hi]+v[i+1:]   # Oct 14 (Dom): one big game is cut to his next-best\n',1),
 # 1 injured free agents
 ('def _newsback(p):\n',
  'EXTINJ={}\n'
  'try:   # Oct 14 (Dom): ESPN + Sleeper injury lists, so a hurt free agent is never ranked as available\n'
  '    _FDX=globals().get("_FD","/home/claude/domfantasy01/dk-feeds/feeds/"); _SEV={"O":1,"IR":2,"NA":3}\n'
  '    def _xadd(nm,pos,t):\n'
  '        if t and nm: k=(norm(nm),str(pos).upper()); EXTINJ[k]=t if _SEV[t]>_SEV.get(EXTINJ.get(k),0) else EXTINJ[k]\n'
  '    for _x in json.load(open(_FDX+"espn_injuries.json")).get("players",[]):\n'
  '        _s=str(_x.get("status","")).lower()\n'
  '        _xadd(_x.get("name"),_x.get("pos"),"NA" if "ret" in _s else "IR" if ("reserve" in _s or "pup" in _s or "physically" in _s) else "O" if _s in ("out","doubtful","suspension","suspended") else "")\n'
  '    _sl=json.load(open(_FDX+"sleeper_injuries.json")).get("players",{}); _sl=_sl.values() if isinstance(_sl,dict) else _sl\n'
  '    for _x in _sl:\n'
  '        _s=str(_x.get("inj") or "").upper()\n'
  '        _xadd(_x.get("name"),_x.get("pos"),"IR" if _s in ("IR","PUP","COV") else "O" if _s in ("OUT","SUS","DOUBTFUL") else "")\n'
  '    if not QUIET: print(f"Scout injury lists: {len(EXTINJ)} men out or on IR (ESPN + Sleeper)")\n'
  'except Exception as _e: print("Scout injury lists skipped:",_e)\n'
  'def _newsback(p):\n',1),
 ('def back(p,ytag=""):\n',
  'def back(p,ytag=""):\n'
  '    if not ytag: ytag=EXTINJ.get((norm(p["name"]),p.get("pos","")),"")   # Oct 14: no Yahoo tag -> ESPN/Sleeper status\n',1),
 ('if ytag in ("IR","IR-R","PUP-R") or p.get("nflstat")=="RES": return max(p["last"]+5,NOW+1)',
  'if ytag in ("IR","IR-R","PUP-R") or p.get("nflstat")=="RES": return max(p["last"]+5,NOW+1,_newsback(p))',1),
 ("({'IR minimum' if p['nflstat']=='RES' else 'listed Out'})",
  "({'IR minimum' if (p['nflstat']=='RES' or EXTINJ.get((norm(p['name']),p['pos']))=='IR') else 'listed Out'})",1),
],"OCT14 scout injured FAs + spikes + initials")

# ---------- 4  THE OUTLOOK reads as paragraphs (Field Report card, Wednesday on) ----------
_OUTLOOK_FN = 'def _outlook14(D, moves):\n    """Oct 14 (Dom): the Outlook reads as paragraphs - the matchup and what\'s at stake, where the week is won and lost\n    slot by slot, and what can still change before kickoff - all generated from the meter\'s numbers."""\n    L = D["L"]; lab = D["lab"]; rows = [r for r in D["rows"] if r["name"]]; nd = D["nd"]\n    oppn = _tct(L["opp"]) if "_tct" in globals() else L["opp"]\n    ym, yo = D["tot"]; ym = ym or 0; yo = yo or 0; mg = ym - yo\n    g_, y_, s_ = nd.get("gotham"), nd.get("yahoo"), nd.get("sleeper")\n    word = "as the favorite" if (y_ or 50) > 55 else "as the underdog" if (y_ or 50) < 45 else "in a toss-up"\n    orr = rec8(L.get("opp_record", "")) + (f", {L[\'opp_rank\']}{sfx8(L[\'opp_rank\'])} of {L[\'teams\']}" if L.get("opp_rank") else "")\n    lead = (f"{lab} goes in {word}. Yahoo projects {ym:.1f} to {yo:.1f} against {oppn} ({orr}), a {abs(mg):.1f}-point "\n            f"{\'edge\' if mg >= 0 else \'gap\'}. Win chance: Yahoo {num8(y_, 0)}%, Gotham {num8(g_, 0)}%, Sleeper {num8(s_, 0)}%.")\n    vals = [v for v in (y_, g_, s_) if v is not None]\n    BM = L.get("best_moves") or {}\n    opbest = (BM.get("gotham") or {}).get("op") or []\n    opbest = [m for m in opbest if m.get("into") and not m["into"].startswith("(") and (m.get("in_v") or 0) - (m.get("out_v") or 0) >= 1]\n    if len(vals) > 1 and max(vals) - min(vals) >= 10:\n        lead += (f" The engines split by {max(vals) - min(vals):.0f}: Yahoo uses the lineups as set, Gotham and Sleeper the best ones"\n                 + (f" - and {oppn}\'s best adds {\'; \'.join(m[\'into\'] + (\' in an empty seat\' if str(m[\'out\']).startswith(\'(\') else \' for \' + ln8(m[\'out\'])) + \' (\' + sgn8(m[\'in_v\'] - m[\'out_v\']) + \')\' for m in opbest[:2])}." if opbest else "."))\n    elif len(vals) > 1: lead += " The three engines agree."\n    rk = L.get("rank"); tm_ = L.get("teams") or 12\n    if rk:\n        lead += (f" At {rec8(L.get(\'record\', \'\'))}, {rk}{sfx8(rk)} of {tm_}: " +\n                 (f"{rk - 6} spot{\'s\' if rk - 6 > 1 else \'\'} below the playoff line, so this week counts." if rk > 6 else\n                  "on the playoff line, with no room to give back." if rk == 6 else f"{6 - rk} spot{\'s\' if 6 - rk > 1 else \'\'} inside the playoff line."))\n    # slot by slot, Yahoo projections\n    pairs = [(r["slot"], r["name"], r["ypre"], r["opn"], r["opproj"]) for r in D["rows"] if r["name"] and r["ypre"] is not None and r.get("opproj") is not None and r["slot"] not in ("K", "DEF")]\n    ed = sorted(pairs, key=lambda p: -(p[2] - p[4]))\n    good = [p for p in ed if p[2] - p[4] >= 2][:2]; bad = [p for p in reversed(ed) if p[2] - p[4] <= -2][:2]\n    p2 = ""\n    _vs = lambda p: f"an empty {p[0]}" if str(p[3]).startswith("(") or p[3] in ("—", "") else f"{p[3]} at {p[0]}"\n    if good: p2 += "Your edges: " + "; ".join(f"{ln8(p[1])} over {_vs(p)} ({sgn8(p[2] - p[4])})" for p in good) + ". "\n    if bad: p2 += "Theirs: " + "; ".join(f"{p[3]} over {ln8(p[1])} at {p[0]} ({sgn8(p[2] - p[4])})" for p in bad) + ". "\n    cool = sorted([r for r in rows if r["ypre"] and r.get("gpre") is not None and r["ypre"] - r["gpre"] >= 3], key=lambda r: r["gpre"] - r["ypre"])[:2]\n    if cool: p2 += ("Gotham is cooler than Yahoo on " + _lst8([f"{ln8(r[\'name\'])} ({r[\'gpre\']:.1f} vs {r[\'ypre\']:.1f})" for r in cool])\n                    + " - his workload doesn\'t support Yahoo\'s number, so lean on him less.")\n    # before kickoff: tags, byes, empty seats, the engines\' lineup calls, and whether they can close the gap\n    todo = [f"{ln8(r[\'name\'])} is {r[\'tag\']}" for r in rows if r["tag"] in ("Q", "D", "O", "IR")] + [f"{ln8(r[\'name\'])} is on bye" for r in rows if r["vs"] == "BYE"]\n    emp = sum(1 for r in D["rows"] if not r["name"])\n    if emp: todo.append(f"{emp} starting slot{\'s\' if emp > 1 else \'\'} empty")\n    p3 = ("; ".join(todo) + ". ") if todo else "Lineup set, no starter tagged. "\n    mine = {}\n    for eng in ("gotham", "sleeper"):\n        for m in (BM.get(eng) or {}).get("me") or []:\n            if m.get("into") and not m["into"].startswith("(") and (m.get("in_v") or 0) - (m.get("out_v") or 0) >= .5:\n                mine.setdefault((m["out"], m["into"]), []).append((eng, m["in_v"] - m["out_v"]))\n    lift = 0.0\n    if mine:\n        calls = []\n        for (o, i), v in sorted(mine.items(), key=lambda kv: -max(x[1] for x in kv[1]))[:2]:\n            who = "Gotham and Sleeper both" if len(v) > 1 else v[0][0].capitalize()\n            calls.append(f"{who} would start {ln8(i)} over {ln8(o)} ({sgn8(max(x[1] for x in v))})"); lift += max(x[1] for x in v)\n        p3 += "; ".join(calls) + ". "\n    if mg < 0:\n        p3 += (f"The best lineup closes about {lift:.1f} of the {abs(mg):.1f}-point gap, so the rest has to come from the starters beating their projections - check the Scout for an add that lifts this week."\n               if lift < abs(mg) - 1 else f"Making {\'that move\' if len(mine) == 1 else \'those moves\'} roughly closes the gap.")\n    out = [("Before kickoff", p3.strip())]\n    if p2: out.append(("Where it\'s won and lost", p2.strip()))\n    mv = [m_["text"].split(" - ")[0].split(" — ")[0] for m_ in moves][:2]\n    if mv: out.append(("Scout", "; ".join(mv) + ". Dom\'s call."))\n    return lead, out\n\n'
patch(f"{R}/cand/redesign/_fr_v8.py",[
 ('def story8(D, moves):\n', _OUTLOOK_FN + 'def story8(D, moves):\n', 1),
 ('    if not D["started"]:\n        ym, yo = D["tot"]; nd = D["nd"]\n',
  '    if not D["started"]:\n        return _outlook14(D, moves)   # Oct 14 (Dom): paragraphs, not a few lines\n        ym, yo = D["tot"]; nd = D["nd"]\n', 1),
],"OCT14 outlook paragraphs")

# ---------- 5  EVERY MARK LINKS TO ITS SOURCE (Dom, Oct 14) ----------
# Tap a mark on a Field Report row and the PDF jumps to where it comes from: the Radar signal and the Scout's spyglass
# to that league's Scout page (the Radar lives there), the D (drift) and the trend arrow to that league's Positions page.
# A mark exists only while its source does, so a link always lands on something real.
patch(f"{R}/cand/redesign/_fr_v8.py",[
 ('    RAD = _radar8(WEEKN).get(lab, {}); SCO, moves = _scout8(lab); MK = (RAD, SCO, eng8(lab))',
  '    RAD = _radar8(WEEKN).get(lab, {}); SCO, moves = _scout8(lab); MK = (RAD, SCO, eng8(lab)); globals()["_MKLAB8"] = lab   # Oct 14: marks link to this league\'s pages', 1),
 ('    for f_ in out[:4]: x += f_(x) + 2',
  '    _dest = {"g_radar8": "scout", "g_scout8": "scout", "g_drift8": "pos", "g_trend8": "pos"}   # Oct 14 (Dom): every mark links to its source\n'
  '    for f_ in out[:4]:\n'
  '        w_ = f_(x); nm_ = next((n for n in f_.__code__.co_names if n in _dest), None); lab_ = globals().get("_MKLAB8")\n'
  '        if nm_ and lab_:\n'
  '            try: c.linkRect("", "dk_" + _dest[nm_] + "_" + lab_.replace(" ", ""), (x - 1, y - 3, x + w_ + 1, y + 8), relative=0, thickness=0)\n'
  '            except Exception: pass\n'
  '        x += w_ + 2', 1),
],"OCT14 marks link to their source")
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ('    pg+=scout_page(c,pg,L_,_KK[L_])',
  '    c.bookmarkPage("dk_scout_"+L_.replace(" ",""))   # Oct 14: where the Radar and Scout marks land\n    pg+=scout_page(c,pg,L_,_KK[L_])', 1),
 ('    r_=position_page10(L_,T_,S_,"Positions · "+L_);pg+=1',
  '    c.bookmarkPage("dk_pos_"+L_.replace(" ",""))   # Oct 14: where the drift and trend marks land\n    r_=position_page10(L_,T_,S_,"Positions · "+L_);pg+=1', 1),
],"OCT14 mark link targets")

# ---------- 6  THE ALERT MARK (Dom, Oct 14) ----------
# A bell in the marker column on a man with a live alert, in the alert's color right now: red act now, gold monitor,
# grey noted, green resolved. It rides the alert's week: it shows for 7 days from when the alert first landed (a resolved
# alert shows green for 7 days from resolving), then it is gone - no counts, nothing to manage. Tapping it opens
# Dark Knight Live, where the alert lives. The build computes the alerts itself (dispatch_out/alerts_build.json, kept
# build to build) from the same feeds and code the Live page's alerts come from.
_ALERT_FN = '''
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
'''
patch(f"{R}/cand/redesign/_fr_v8.py",[
 ('def marks8(x, y, nm, MK):\n', _ALERT_FN + 'def marks8(x, y, nm, MK):\n', 1),
 ('    k = norm(nm); RAD, SCO, EN_ = MK; out = []\n',
  '    k = norm(nm); RAD, SCO, EN_ = MK; out = []\n'
  '    _ac = _alerts8(globals().get("_MKLAB8", "")).get(k)   # Oct 14 (Dom): the alert mark leads the column\n'
  '    if _ac: out.append(lambda xx: g_alert8(xx, y, {"red": K8["RED"], "gold": K8["GOLD"], "green": K8["GREEN"]}.get(_ac, K8["GR2"])))\n', 1),
 ('        if nm_ and lab_:\n',
  '        if nm_ is None and "g_alert8" in f_.__code__.co_names:\n'
  '            try: c.linkURL(_ALURL8, (x - 1, y - 3, x + w_ + 1, y + 8), relative=0, thickness=0)\n'
  '            except Exception: pass\n'
  '        if nm_ and lab_:\n', 1),
 ('    t8(x, y, "Markers", "PopB", 5.8, K8["INK"]); x += w8("Markers", "PopB", 5.8) + 4\n',
  '    t8(x, y, "Markers", "PopB", 5.8, K8["INK"]); x += w8("Markers", "PopB", 5.8) + 4\n'
  '    x += g_alert8(x, y, K8["RED"]) + 1; t8(x, y, "alert", "Pop", 5.8, K8["GR"]); x += w8("alert", "Pop", 5.8) + 6\n', 1),
],"OCT14 alert mark")

# ======================= Oct 14 afternoon (Dom): THE THIS-WEEK GUARD + THE DEFENSE FIX =======================
#  5  DEFENSE / KICKER THIS WEEK: the Scout valued a defense this week from its own past games x a mild matchup factor.
#     The Colts' last five (-1, -1, 8, 17, -2 in DK I scoring) gave ~4.3 vs Tennessee while Yahoo had 10.1 and Sleeper
#     11.1, so it pushed the Browns (Yahoo 7.2) over a better defense Dom already had. This week's number for a defense
#     or kicker now comes from Sleeper's projection for this week in the league's own scoring (the same math the meter
#     uses). Later weeks are unchanged.
#  6  THE THIS-WEEK GUARD: the Scout ranks pickups by rest of season (Dom's rule, unchanged). Every pick now also
#     carries this week's numbers next to the starter he'd replace - Gotham, Sleeper and Yahoo side by side - and says
#     plainly when he's worse this week, so a downgrade can never reach Dom unflagged (Hutchinson 4.5 vs Sutton 8.6).
#     The line goes on the Scout card, the open-seat adds, the action list, the morning brief and Live's alerts.
_GUARD_DEFS = r'''
# Oct 14 afternoon (Dom): this week's Sleeper numbers + the this-week guard
import glob as _glb
_FDG = globals().get("_FD", "/home/claude/domfantasy01/dk-feeds/feeds/")
def _lastcsv(sub):
    fs = sorted(_glb.glob(os.path.join(_FDG, "proj", sub, f"wk{NOW}_*.csv")))
    return pd.read_csv(fs[-1]) if fs else None
_SLKD, _SLPPR = {}, {}
try:
    _kd = _lastcsv("sleeper_kdef")
    if _kd is not None:
        for _r in _kd.itertuples():
            _s = json.loads(_r.stats) if isinstance(_r.stats, str) else {}
            if _r.pos == "DEF":
                _v = (_s.get("sack", 0) + 2 * (_s.get("int", 0) + _s.get("fum_rec", 0) + _s.get("safe", 0) + _s.get("blk_kick", 0))
                      + 6 * _s.get("def_td", 0) + pa_pts(_s.get("pts_allow", 20)))
                _SLKD[("DEF", tm(str(_r.team)))] = round(_v, 2)
            elif _r.pos == "K" and CF["kick"]:
                f40, f50 = (3, 4) if CF["kick"] == "flat" else (4, 5)
                _v = (3 * (_s.get("fgm_0_19", 0) + _s.get("fgm_20_29", 0) + _s.get("fgm_30_39", 0)) + f40 * _s.get("fgm_40_49", 0)
                      + f50 * _s.get("fgm_50p", 0) + _s.get("xpm", 0) - _s.get("xpmiss", 0))
                _SLKD[("K", norm(_r.name))] = round(_v, 2)
    _pp = _lastcsv("sleeper")
    if _pp is not None:
        for _r in _pp.itertuples():
            if pd.notna(_r.pts_ppr): _SLPPR[norm(_r.name)] = float(_r.pts_ppr)
except Exception as _e: print("Scout: Sleeper this-week numbers skipped:", _e)
def _kdkey(p): return ("DEF", p["team"]) if p["pos"] == "DEF" else ("K", norm(p["name"]))
'''
try:
  patch(f"{R}/dksys/scout/scout_engine.py",[
 ('def weekly(p,x,ytag=""):\n    if x in byes.get(p["team"],[]) or x<back(p,ytag): return 0.0\n',
  _GUARD_DEFS + 'def weekly(p,x,ytag=""):\n    if x in byes.get(p["team"],[]) or x<back(p,ytag): return 0.0\n'
  '    if x==NOW and p["pos"] in ("DEF","K") and _SLKD.get(_kdkey(p)) is not None: return _SLKD[_kdkey(p)]   # Oct 14: this week = Sleeper, league scoring\n', 1),
 ('def _pick(e,need_red,w):\n',
  r'''# Oct 14 afternoon (Dom): THE THIS-WEEK GUARD - this week's numbers for a pickup next to the starter he'd replace
_MET = {}
try:
    for _m in json.load(open(f"{L}/meter/meter_wk{NOW}.json"))["leagues"][CF["lab"]]["starters"]["me"]:
        _MET[("DEF", tm(_m.get("team") or "")) if _m.get("pos") == "DEF" else (_m.get("pos"), norm(_m["player"]))] = _m
except Exception as _e: print("Scout: meter numbers for the this-week guard skipped:", _e)
_GOT = {}
try:
    _gc = pd.read_csv(os.path.join(os.path.dirname(H), "engine", f"gotham_{LGK}.csv"))
    if "week" in _gc and int(_gc.week.iloc[0]) == NOW:          # only a Gotham run for THIS week counts
        for _r in _gc.itertuples():
            if pd.notna(_r.eng_wk): _GOT[norm(_r.player)] = float(_r.eng_wk)
    else: print("Scout: Gotham file is not for Week", NOW, "- the guard shows Gotham as not read")
except Exception as _e: print("Scout: Gotham numbers for the this-week guard skipped:", _e)
def _f(v): return "not read" if v is None else f"{v:.1f}"
def thisweek(p):
    try:
        if NOW not in LU: return ""
        el = [(lab, i, v) for lab, i, v in LU[NOW] if i is not None and p["pos"] in okfor(re.sub(r"\d+$", "", lab))]
        if not el: return ""
        lab, i, v = min(el, key=lambda t: t[2]); st = MINE[i]; sp = PL[st["key"]]
        kd = p["pos"] in ("DEF", "K")
        if v <= 0:                                            # nobody playing in that seat this week (bye / out)
            return f"This week: your {lab} seat has nobody playing ({st['name']} {'on bye' if NOW in byes.get(sp['team'], []) else 'out'}), so any healthy {p['pos']} who plays helps this week"
        mk = ("DEF", sp["team"]) if sp["pos"] == "DEF" else (sp["pos"], norm(st["name"]))
        sm = _MET.get(mk, {})
        if x_bye := (NOW in byes.get(p["team"], [])): return f"This week: {p['name'].replace(' defense',' DEF')} has a bye - no help this week"
        if NOW < back(p): return f"This week: {p['name']} is out (due back Wk {back(p)}) - no help this week"
        a = dict(Gotham=(None if kd else _GOT.get(norm(p["name"]))),
                 Sleeper=(_SLKD.get(_kdkey(p)) if kd else _SLPPR.get(norm(p["name"]))), Yahoo=None)
        b = dict(Gotham=(sm.get("gotham") if not kd else None) if sm else (None if kd else _GOT.get(norm(st["name"]))),
                 Sleeper=(_SLKD.get(_kdkey(sp)) if kd else _SLPPR.get(norm(st["name"]))), Yahoo=sm.get("yahoo"))
        pairs = [(k, a[k], b[k]) for k in ("Gotham", "Sleeper", "Yahoo") if not (kd and k == "Gotham")]
        both = [(x, y) for _, x, y in pairs if x is not None and y is not None]
        verdict = ("WORSE this week" if both and all(x < y for x, y in both) else "better this week" if both and all(x > y for x, y in both)
                   else "mixed this week" if both else "this week unknown")
        nm = st["name"] if sp["pos"] != "DEF" else st["name"] + " DEF"
        return (f"This week vs your {lab} {nm}: " + " · ".join(f"{k} {_f(x)} vs {_f(y)}" for k, x, y in pairs)
                + (" (Sleeper PPR)" if not kd else "") + f" - {verdict}")
    except Exception as _e:
        return ""
def _pick(e,need_red,w):
''', 1),
 ('urg=urg,', 'urg=urg,now=thisweek(p),', 1),
 ('gain=round(sum(max(0.0,v) for v in e["g"].values()),1),pgain=round(sum(max(0.0,e["g"].get(x,0.0)) for x in PLAYOFF),1))\n               for e in sorted(',
  'gain=round(sum(max(0.0,v) for v in e["g"].values()),1),pgain=round(sum(max(0.0,e["g"].get(x,0.0)) for x in PLAYOFF),1),now=thisweek(e["p"]))\n               for e in sorted(', 1),
],"OCT14b this-week guard + defense this week")
except AssertionError as _e: print("!! OCT14b Scout guard NOT applied:", _e)
try:
  patch(f"{R}/cand/_actions.py",[
 ('Scout pick, your call",', 'Scout pick, your call" + ((". " + _pk["now"]) if _pk.get("now") else ""),', 2),
],"OCT14b actions carry the this-week line")
except AssertionError as _e: print("!! OCT14b page patch NOT applied:", _e)
_NOWTXT = """('  ·  <font name="PopB" color="#B32020">'+_esc(p["now"])+'</font>' if "WORSE" in p.get("now","") else ('  ·  <font name="PopB">'+_esc(p["now"])+'</font>' if p.get("now") else ''))"""
try:
  patch(f"{R}/cand/redesign/_scout_page.py",[
 ('+_gain(p)))', '+_gain(p)+' + _NOWTXT + '))', 1),
 ('+_gain(p))\n        if not it.get("act",True)', '+_gain(p)+' + _NOWTXT + ')\n        if not it.get("act",True)', 1),
],"OCT14b the this-week guard on every Scout pick")
except AssertionError as _e: print("!! OCT14b page patch NOT applied:", _e)
try:
  patch(f"{R}/cand/redesign/_oct10_scout.py",[
 ('''_tc(a["acq"]))})\'''', '''_tc(a["acq"]))})\'+(f\' - {a["now"].rsplit(" - ",1)[-1]}\' if a.get("now") else "")''', 1),
],"OCT14b open-seat adds say better / worse this week")
except AssertionError as _e: print("!! OCT14b page patch NOT applied:", _e)

# ======================= Oct 14 2 PM (Dom): YAHOO'S WEEKLY PROJECTIONS INSIDE THE SCOUT =======================
#  7  The Scout valued every week from a player's own past games x a mild matchup factor, and never saw Yahoo's number
#     for a free agent - so a pick could rank high on season level while Yahoo had him far below the man he'd replace.
#     A Chrome read (DKP, in the scheduled projections task) now saves Yahoo's weekly projections - this week, the next
#     two and the playoff weeks 15-17 - for Dom's roster and the top available players in all four leagues
#     (yahoo_drop/scout/yproj_dkN.txt). For any week Yahoo has a number, the Scout's value is half its own model, half
#     Yahoo (this week's defense/kicker: half Sleeper, half Yahoo). Yahoo never decides alone (Dom's rule), the
#     ranking is still points added through Week 17, and the this-week guard now shows Yahoo for the pickup too.
#     A file older than 36 hours is ignored and the Scout says so.
_YP_DEFS = r'''
# Oct 14 2 PM (Dom): Yahoo's weekly projections (Chrome read) - blended half and half into the Scout's weekly values
_YP = {}
def _ypk(p): return ("DEF", tm(p["team"])) if p["pos"] == "DEF" else (p["pos"], norm(p["name"]))
try:
    _yf = f"{H}/yproj_dk{CF['n']}.txt"
    if os.path.exists(_yf):
        _yl = open(_yf).read().splitlines()
        _ym = re.search(r"read live (\w{3} \w{3} \d{1,2} \d{4} \d{1,2}:\d{2} [AP]M) PT", _yl[0] if _yl else "")
        _yt = dt.datetime.strptime(_ym.group(1), "%a %b %d %Y %I:%M %p").replace(tzinfo=NOWPT.tzinfo) if _ym else None
        if _yt and (NOWPT - _yt).total_seconds() <= 36 * 3600:
            for _l in _yl[1:]:
                _x = _l.split("|")
                if len(_x) < 5: continue
                try: _YP[((("DEF", tm(_x[2])) if _x[3] == "DEF" else (_x[3], norm(_x[1]))), int(_x[0]))] = float(_x[4])
                except Exception: pass
            print(f"Scout: Yahoo weekly projections in ({len(_YP)} player-weeks, read {_ym.group(1)} PT)")
        else: print("Scout: Yahoo projections file is older than 36 hours - not used")
    else: print("Scout: no Yahoo projections file - the Scout runs on its own model")
except Exception as _e: print("Scout: Yahoo projections skipped:", _e)
'''
try:
  patch(f"{R}/dksys/scout/scout_engine.py",[
 ('def _kdkey(p): return ("DEF", p["team"]) if p["pos"] == "DEF" else ("K", norm(p["name"]))\n',
  'def _kdkey(p): return ("DEF", p["team"]) if p["pos"] == "DEF" else ("K", norm(p["name"]))\n' + _YP_DEFS, 1),
 ('    if x==NOW and p["pos"] in ("DEF","K") and _SLKD.get(_kdkey(p)) is not None: return _SLKD[_kdkey(p)]   # Oct 14: this week = Sleeper, league scoring\n',
  '    _y=_YP.get((_ypk(p),x))\n'
  '    if x==NOW and p["pos"] in ("DEF","K") and _SLKD.get(_kdkey(p)) is not None: return _SLKD[_kdkey(p)] if _y is None else (_SLKD[_kdkey(p)]+_y)/2   # Oct 14: this week = Sleeper (+ Yahoo), league scoring\n', 1),
 ('    return v*RATIO.get((sched[p["team"]].get(x),p["pos"]),1.0)\n',
  '    _mv=v*RATIO.get((sched[p["team"]].get(x),p["pos"]),1.0)\n'
  '    return _mv if _y is None else (_mv+_y)/2   # Oct 14 2 PM (Dom): half the Scout\'s model, half Yahoo\'s projection for that week\n', 1),
 ('Sleeper=(_SLKD.get(_kdkey(p)) if kd else _SLPPR.get(norm(p["name"]))), Yahoo=None)',
  'Sleeper=(_SLKD.get(_kdkey(p)) if kd else _SLPPR.get(norm(p["name"]))), Yahoo=_YP.get((_ypk(p), NOW)))', 1),
 ('Yahoo=sm.get("yahoo"))',
  'Yahoo=sm.get("yahoo") if sm.get("yahoo") is not None else _YP.get((_ypk(sp), NOW)))', 1),
],"OCT14c Yahoo weekly projections in the Scout")
except AssertionError as _e: print("!! OCT14c Yahoo projections NOT applied:", _e)

# ======================= Oct 20 (Dom): HYPHENATED NAMES WERE INVISIBLE TO GOTHAM =======================
#  8  The forecast frame keyed every player with role_watch's name cleaner, which squeezes "Smith-Njigba" into
#     "smithnjigba"; Gotham and the meter join with dksys names.norm, which reads "smith njigba". The join missed, so every
#     hyphenated name (Jaxon Smith-Njigba, Amon-Ra St. Brown, Jacory Croskey-Merritt, JuJu Smith-Schuster...) showed
#     0 games and Gotham couldn't price him - the meter quietly used Yahoo's number instead. The frame now keys with the
#     same names.norm everything else uses.
try:
  patch(f"{R}/src/forecast/fc_model.py",[
 ('    s["key"] = s.player_display_name.map(norm)\n',
  '    sys.path.insert(0, "/home/claude/dksys/gather"); from names import norm as _dknorm   # Oct 20 (Dom): same key as Gotham and the meter\n'
  '    s["key"] = s.player_display_name.map(_dknorm)\n', 1),
],"OCT20a hyphenated names join Gotham")
except AssertionError as _e: print("!! OCT20a hyphen fix NOT applied:", _e)
#  9  ...and the role_watch name cleaner itself now reads a hyphen as a space, so every page that still matches names with
#     it (the Positions page crashed on a hyphenated name at 3:01 PM) agrees with Gotham and the meter.
try:
  patch(f"{R}/src/role_watch/rw_core.py",[
 ('def norm(n):\n    n = n.lower()',
  'def norm(n):\n    n = n.replace("-", " ")   # Oct 20 (Dom): hyphen = space, same as names.norm\n    n = n.lower()', 1),
],"OCT20b role_watch names read hyphens as spaces")
except AssertionError as _e: print("!! OCT20b rw_core hyphen fix NOT applied:", _e)
