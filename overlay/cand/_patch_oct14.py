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
