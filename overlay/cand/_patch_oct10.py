# THE OCT 10 BATCH (Dom, Sat Oct 10 2026) - applied to the bundle's page code on every build, after the overlay.
# Safe to run twice: each file carries a marker once patched. Every anchor must match exactly once or the build stops,
# so a changed file can never be half-patched into a page.
#  1  Gold bar under DARK KNIGHT DISPATCH runs the full width of the section name on every page.
#  2  Mastheads carry no read stamps (each block carries its own); the subline is a step brighter and heavier.
#  3  Lit puzzle piece: gold name, gold rim outside the black seam - the same gold as the section name.
#  4  Front page: "Week 5 · All Four Leagues"; each chart's foot line carries the three meter reads with honest dates
#     (one date up front when all three share it, a date on each read when they don't); the right side says what the
#     meters do ("All three meters agree") without repeating the numbers the meter already shows.
#  5  Front page: a little more air under the meter for PROJECTED WIN PROBABILITY.
#  6  Field Report: one stamp above the cards and tables governs the page - the masthead, the card's status line and
#     the opponent note stop repeating it. "1 of 10 starters played", never "of yours". Team names get capital letters.
#  7  Field Report: the DELTA column moves clear of its divider line.
#  8  The Scout's spyglass joins the MARKER column on the man a live Scout need is about (red = act now, gold = watch).
#  9  The Scout's DK I footer drops the Mahomes claim (it went to another team Fri night).
# 10  Stamps everywhere read "Oct." with its period.
import sys
import os
R=os.environ.get("DK_ROOT","/home/claude")
def patch(path,pairs,mark):
    s=open(path).read()
    if mark in s: print("   oct10:",path.split("/")[-1],"already in"); return
    for a,b,n in pairs:
        k=s.count(a); assert k==n,f"oct10 patch: {path.split('/')[-1]}: anchor found {k}x, expected {n}: {a[:80]}"
        s=s.replace(a,b)
    open(path,"w").write(s+f"\n# {mark}\n"); print("   oct10:",path.split("/")[-1],"patched")

# ---------- 1-3 the Dispatch masthead (league pages) ----------
patch(f"{R}/cand/redesign/_masthead_field.py",[
 ('c.setFillColor(SUN[1]);c.rect(M,Ht-56,30,1.6,stroke=0,fill=1)',
  'c.setFillColor(SUN[1]);c.rect(M,Ht-56,c.stringWidth(section,"Bebas",15),1.6,stroke=0,fill=1)   # Oct 10: the bar spans the section name',1),
 ('txt(c,M+c.stringWidth(section,"Bebas",15)+10,Ht-73.5,sub,"Pop",7.2,H("#C9CFDB"))',
  'txt(c,M+c.stringWidth(section,"Bebas",15)+10,Ht-73.5,sub,"PopM",7.6,H("#E4E8F0"))',1),
 ('        c.setStrokeColor(H("#0A1226"));c.setLineWidth(1.4);c.drawPath(p,stroke=1,fill=0);c.restoreState()   # v15: no colored ring - a thin navy seam only',
  '        c.saveState();_q=c.beginPath();_q.rect(-200,-200,W+400,Ht+400);_q._code.extend(p._code)   # Oct 10 (Dom): a gold rim OUTSIDE the lit piece\n'
  '        from reportlab.pdfgen.canvas import FILL_EVEN_ODD as _EO;c.clipPath(_q,stroke=0,fill=0,fillMode=_EO)\n'
  '        c.setStrokeColor(SUN[1]);c.setLineWidth(3.4);c.drawPath(p,stroke=1,fill=0);c.restoreState()\n'
  '        c.setStrokeColor(H("#0A1226"));c.setLineWidth(1.3);c.drawPath(p,stroke=1,fill=0);c.restoreState()   # the black seam stays, on top',1),
 ('col=white if on(i) else H("#8E98AD");c.setFont("Bebas",fs)','col=SUN[1] if on(i) else H("#8E98AD");c.setFont("Bebas",fs)   # Oct 10: the lit name in gold',1),
],"OCT10 masthead")
patch(f"{R}/cand/global/_mast33.py",[
 ('c.setFillColor(SUN[1]); c.rect(M+P,Ht-56,30,1.6,stroke=0,fill=1)',
  'c.setFillColor(SUN[1]); c.rect(M+P,Ht-56,c.stringWidth(section,"Bebas",15),1.6,stroke=0,fill=1)   # Oct 10: spans the section name',1),
 ('txt(c,M+P+c.stringWidth(section,"Bebas",15)+10,Ht-71.5,sub,"Pop",7.2,H("#C9CFDB"))',
  'txt(c,M+P+c.stringWidth(section,"Bebas",15)+10,Ht-71.5,sub,"PopM",7.6,H("#E4E8F0"))',1),
],"OCT10 front masthead")

# ---------- 4-5 the front page ----------
patch(f"{R}/cand/global/global33.py",[
 ('MASTSUB=f"Week {MW}  ·  all four leagues  ·  Yahoo read {_hm(\'yahoo_matchups\')}  ·  Gotham {_hm(\'gotham\')}  ·  Sleeper {_hm(\'sleeper_skill\')} PT"',
  'MASTSUB=f"Week {MW}  ·  All Four Leagues"',1),
 ('      f"WK {MW}  ·  YAHOO {_hm(\'yahoo_matchups\')}  ·  GOTHAM {_hm(\'gotham\')}  ·  SLEEPER {_hm(\'sleeper_skill\')} PT")',
  '      f"Week {MW}  ·  Meters read "+_DSL([("Yahoo",_src.get("yahoo_matchups",{}).get("pulled_pt")),("Gotham",_src.get("gotham",{}).get("pulled_pt")),("Sleeper",_src.get("sleeper_skill",{}).get("pulled_pt"))]))',1),
 ('_al=MTR["alarms"]\n','exec(open("/home/claude/cand/redesign/_dstamp.py").read()); _DSL=ds_line   # Oct 10: honest dates on the read stamps\n_al=MTR["alarms"]\n',1),
 ('        PROSE[lab]=f"Yahoo\'s posted win % was missing this run, so the Yahoo dial shows {y_}% from Yahoo\'s own projected totals. Gotham {g_}%, Sleeper {s_}%."; URG[lab]="watch"',
  '        PROSE[lab]="Yahoo\'s posted win % was missing this run, so the Yahoo dial is worked from Yahoo\'s own projected totals."; URG[lab]="watch"',1),
 ('        PROSE[lab]=f"YOUR STARTER {bye[0].upper()} HAS NO GAME THIS WEEK. Gotham {g_}%, Yahoo {y_}%, Sleeper {s_}%."; URG[lab]="act"',
  '        PROSE[lab]=f"Starter {bye[0]} has no game this week."; URG[lab]="act"',1),
 ('        PROSE[lab]=f"Reads split: Gotham {g_}%, Yahoo {y_}%, Sleeper {s_}%."+(f" Gotham has {m_.group(4)} at {m_.group(1)}, Yahoo {m_.group(2)}." if m_ else ""); URG[lab]="watch"',
  '        PROSE[lab]=f"The three meters split by {max(g_,y_,s_)-min(g_,y_,s_)} points."+(f" Gotham has {m_.group(4)} at {m_.group(1)}, Yahoo {m_.group(2)}." if m_ else ""); URG[lab]="watch"',1),
 ('        PROSE[lab]=f"All three reads agree: Gotham {g_}%, Yahoo {y_}%, Sleeper {s_}%."+(f" Thursday: {\', \'.join(thu)}." if thu else ""); URG[lab]="info"',
  '        PROSE[lab]="All three meters agree."+(f" Thursday: {\', \'.join(thu)}." if thu else ""); URG[lab]="info"',1),
 ("    sw_=4.2*1.12; fs=6.0; rx=x1-12; lim=rx-(lx+sw_+c.stringWidth(ASOF,'PopB',4.6)+16)",
  "    sw_=4.2*1.12; fs=6.0; rx=x1-12; lim=rx-(lx+sw_+c.stringWidth(ASOF,'PopM',5.2)+16)",1),
 ('    txt(lx,yb,ASOF,"PopB",4.6,DN if MTR["alarms"] else LOWINK)',
  '    txt(lx,yb,ASOF,"PopM",5.2,DN if MTR["alarms"] else LOWINK)',1),
 ('    MBOX=(GX-METERBOX[0],gy-31.5-8.5,GX+METERBOX[0],top)','    MBOX=(GX-METERBOX[0],gy-31.5-10.5,GX+METERBOX[0],top)',1),
 ('scrim(_capsule(GX-54,gy-dn-8.5,GX+54,gy-dn,5),al=PLATE_A,steps=9,feather=3.0)','scrim(_capsule(GX-54,gy-dn-10.5,GX+54,gy-dn,5),al=PLATE_A,steps=9,feather=3.0)',1),
 ('    htxt(GX,gy-37.4,"PROJECTED WIN PROBABILITY","PopB",5.2,TXT,"c",hw=1.5)','    htxt(GX,gy-39.0,"PROJECTED WIN PROBABILITY","PopB",5.2,TXT,"c",hw=1.5)   # Oct 10: more air under YAHOO',1),
],"OCT10 front page")

# ---------- 6-8 the Field Report ----------
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ('f"Whoever Yahoo shows across from you, same read as the meter ({YREAD})."','"Whoever Yahoo shows across the matchup — the same read as the meter."',1),
 ('''    played=L["played"]; when=(f"{YREAD}  ·  first kickoff {MTR['windows'][0].title().replace(' Am',' AM').replace(' Pm',' PM')} PT" if played["me"]+played["op"]==0
          else f"{YREAD}  ·  {played['me']} of {played['of'][0]} of yours played")''',
  '''    played=L["played"]; when=(f"First kickoff {MTR['windows'][0].title().replace(' Am',' AM').replace(' Pm',' PM')} PT" if played["me"]+played["op"]==0
          else f"{played['me']} of {played['of'][0]} starters played")''',1),
 ('oppn=L["opp"],','oppn=_tct(L["opp"]),',1),
 ('''out.append(("Opponent",f"{L['opp']} is {L['opp_record']}"''','''out.append(("Opponent",f"{_tct(L['opp'])} is {L['opp_record']}"''',1),
 ('''           sub=f"{_TEAMS[L_]}  ·  vs {L['opp']}  ·  {YREAD}")''','''           sub=f"{_TEAMS[L_]}  ·  vs {_tct(L['opp'])}")''',1),
 ('OPN=NX_+414;OPP=NX_+478;PAIR=(OPN-8,OPP+22)\n',
  'OPN=NX_+414;OPP=NX_+478;PAIR=(OPN-8,OPP+15)\nDL=W-M-13   # Oct 10: DELTA clear of its divider\n'
  'exec(open("/home/claude/cand/redesign/_oct10_fr.py").read())   # Oct 10: team-name capitals, the Scout mark in the MARKER column\n',1),
 ('    field_report17(D);pg+=2\n','    SCOUTMK.clear(); SCOUTMK.update(scout_rows(L_))\n    field_report17(D);pg+=2\n',1),
 ('    r_=position_page10(L_,T_,S_,"Positions · "+L_);pg+=1\n','    SCOUTMK.clear(); SCOUTMK.update(scout_rows(L_))\n    r_=position_page10(L_,T_,S_,"Positions · "+L_);pg+=1\n',1),
],"OCT10 field report")
patch(f"{R}/cand/redesign/_scout_page.py",[
 ('masthead(c,f"FIELD — SCOUT  ·  {lab}",f"Week {WEEKN}  ·  Run {B[\'run_str\']}  ·  {warn}")',
  'masthead(c,f"FIELD — SCOUT  ·  {lab}",f"Week {WEEKN}  ·  {warn}")   # Oct 10: the run time lives in the footer, not the masthead',1),
],"OCT10 scout page")
patch(f"{R}/cand/redesign/_fr_positions18.py",[
 ('"What each man is for — your players, and the free agents who came through a door"','"What each man is for — the roster, and the free agents who came through a door"',1),
],"OCT10 positions")
patch(f"{R}/cand/redesign/_fresh.py",[
 ('    return (t.strftime("%a %b ")+str(t.day)+", "+h).upper()',
  '    _mo={9:"Sept.",3:"March",4:"April",5:"May",6:"June",7:"July"}.get(t.month,t.strftime("%b")+".")   # Oct 10: "Oct." with its period\n'
  '    return (t.strftime("%a ")+_mo+" "+str(t.day)+", "+h).upper()',1),
],"OCT10 fresh")

# ---------- 8-9 the Scout engine: which roster men each live need is about; the Mahomes claim is gone ----------
patch(f"{R}/dksys/scout/scout_engine.py",[
 ('pending="Mahomes claim, clears Oct 10"','pending=""',1),
 ('        kill=("Drops Off After Wk "+str(max(w))) if nd["kind"]!="season-long" else "Drops Off When Filled"))',
  '        kill=("Drops Off After Wk "+str(max(w))) if nd["kind"]!="season-long" else "Drops Off When Filled",\n'
  '        rows=sorted({n_ for n_ in ([FULL[nd["lab"]][0]] if nd["kind"]=="season-long" and nd["lab"] in FULL else [])+\n'
  '                     [(h["fullname"] if h["kind"]=="empty" else h["who"]) for h in nd["holes"] if h["week"]<=NOW+1] if n_})))   # Oct 10: the men a live need is about',1),
],"OCT10 scout rows")

# ---------- 11 (Dom, Sat Oct 10 11:36 AM) the chart foot line, second pass ----------
# Left: one date stamp for everything in the block ("All data as of ..."), not "Week 5 · Meters read".
# Right: no echo of what the chart already shows (agree/split). It says what to do or what decides the game:
#   red   a starter with no game or ruled out - fix the lineup
#   gold  a questionable starter - check before kickoff, then the biggest edge
#   grey  the biggest edge and the biggest gap of the one-on-one matchups (Yahoo now, actual once played)
patch(f"{R}/cand/global/global33.py",[
 ('f"Week {MW}  ·  Meters read "+_DSL(','"All data as of "+_DSL(',1),
 ('STAND_LAB=f"STANDINGS  ·  AFTER WEEK {MW-1}"\n',
  '''def _ln11(n):
    w=[x for x in str(n).split() if x.rstrip(".") not in ("Jr","Sr","II","III","IV","V")]
    return w[-1] if w else str(n)
def _v11(p): return p["actual"] if p.get("actual") is not None else (p.get("yahoo") or 0.0)
for lab,L in MTR["leagues"].items():
    if lab in YMISS: continue
    me=L["starters"]["me"]; op=L["starters"]["op"]
    bad=[_ln11(p["player"]) for p in me if p["window"] is None or p.get("status") in ("O","IR","IR-R","PUP-R","NA")]
    q=[_ln11(p["player"])+" ("+p["status"]+")" for p in me if p.get("status") in ("Q","D")]
    ds=[(_v11(a)-_v11(b),a,b) for a,b in zip(me,op) if a.get("player") and b.get("player")]
    edge=gap=""
    if ds:
        hi=max(ds,key=lambda t:t[0]); lo=min(ds,key=lambda t:t[0])
        if hi[0]>0: edge=f"Edge: {_ln11(hi[1]['player'])} over {_ln11(hi[2]['player'])}, +{hi[0]:.1f}"
        if lo[0]<0: gap=f"Gap: {_ln11(lo[2]['player'])} over {_ln11(lo[1]['player'])}, −{abs(lo[0]):.1f}"
    if bad: PROSE[lab]="Fix the lineup: "+", ".join(bad)+(" has" if len(bad)==1 else " have")+" no game or is out."; URG[lab]="act"
    elif q: PROSE[lab]="Check before kickoff: "+", ".join(q)+"."+(f"  ·  {edge}" if edge else ""); URG[lab]="watch"
    else: PROSE[lab]="  ·  ".join(x for x in (edge,gap) if x) or "Even matchup, slot for slot."; URG[lab]="info"
STAND_LAB=f"STANDINGS  ·  AFTER WEEK {MW-1}"
''',1),
],"OCT10b front feet")

# ---------- 12 (Dom, Sat Oct 10 evening) one masthead and one footer for the whole Dispatch; open seats shown ----------
#  - every masthead: section title, then one subhead line: Week N · page detail · As of <build time> · stoplight
#    (stoplight: green while the oldest of Yahoo / Gotham / Sleeper is under 3 hours old, amber to 6, red past 6)
#  - Overview reads OVERVIEW · FANTASY FOOTBALL; the Scout page reads SCOUT · DK I (was FIELD — SCOUT)
#  - the footer is redrawn on every page after assembly (_footer_pass.py): same words, page N of M
#  - Field Report: every roster slot prints; an empty bench, IR or starting slot reads OPEN; the card's Watch line says so
#  - the Scout: each pick shows the points it adds through Week 17; open seats lead the page with the best uses ranked
patch(f"{R}/cand/redesign/_masthead_field.py",[
 ('    txt(c,M+c.stringWidth(section,"Bebas",15)+10,Ht-73.5,sub,"PopM",7.6,H("#E4E8F0"))',
  '    _sx=M+c.stringWidth(section,"Bebas",15)+10; _wk=globals().get("WEEKN")\n'
  '    if _wk and not sub.startswith("Week"): sub=f"Week {_wk}  ·  "+sub\n'
  '    if "asof_line" not in globals(): exec(open("/home/claude/cand/redesign/_asof.py").read(),globals())\n'
  '    asof_line(c,_sx,Ht-73.5,sub,W-M-9-108-10)   # Oct 10: As of + stoplight on every page',1),
],"OCT10b masthead asof")
patch(f"{R}/cand/global/_mast33.py",[
 ('    txt(c,M+P+c.stringWidth(section,"Bebas",15)+10,Ht-71.5,sub,"PopM",7.6,H("#E4E8F0"))',
  '    if "asof_line" not in N: exec(open("/home/claude/cand/redesign/_asof.py").read(),N)\n'
  '    N["asof_line"](c,M+P+c.stringWidth(section,"Bebas",15)+10,Ht-71.5,sub,W-M-9-108-10-P)   # Oct 10: As of + stoplight',1),
],"OCT10b front asof")
patch(f"{R}/cand/global/global33.py",[
 ('MASTSUB=f"Week {MW}  ·  All Four Leagues"','MASTSUB=f"Week {MW}"',1),
 ('_mast33.draw(c,"OVERVIEW",MASTSUB)','_mast33.draw(c,"OVERVIEW  ·  FANTASY FOOTBALL",MASTSUB)',1),
],"OCT10c front title")
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ('    S,Bn,Ir=rows17(L_)\n','    S,Bn,Ir=rows17(L_)\n    Bn,Ir,_OPN=open_rows(L_,Bn,Ir)   # Oct 10: empty slots print as OPEN\n',1),
 ('    out.append(("Watch",(','    out.append(("Watch",_open_note(lab)+(',1),
 ('           irsub={0:"No IR slot used",1:"One slot in this league",2:"Two slots in this league",3:"Three slots in this league — all full"}.get(nIR,f"{nIR} slots"),',
  '           irsub=_irsub(L_,Ir),',1),
],"OCT10c field open")
patch(f"{R}/cand/redesign/_scout_page.py",[
 ('masthead(c,f"FIELD — SCOUT  ·  {lab}",','masthead(c,f"SCOUT  ·  {lab}",',1),
 ('exec(open("/home/claude/cand/redesign/_scout_mark.py").read())\n',
  'exec(open("/home/claude/cand/redesign/_scout_mark.py").read())\nexec(open("/home/claude/cand/redesign/_oct10_scout.py").read())   # Oct 10: points added, open seats first\n',1),
 ('{_esc(_sent(p["why"]+"; helps "+p["when"]))}\'','{_esc(_sent(p["why"]+"; helps "+p["when"]))}\'+_gain(p)',2),
 ('    room=TOP-BOT-HEAD-g2h-g3h-chh-6-(_ph(_SUMMARY,_SCI,W-2*M)+12)','    room=TOP-BOT-HEAD-g2h-g3h-chh-6-(_ph(_SUMMARY,_SCI,W-2*M)+12)-_open_h(B)',1),
 ('    y-=_para(c,_SUMMARY,_SCI,M,y,W-2*M)+20 ','    y-=_para(c,_SUMMARY,_SCI,M,y,W-2*M)+20; y=_open_box(c,y,B) ',1),
],"OCT10c scout page")
patch(f"{R}/dksys/scout/scout_engine.py",[
 ('                why=why[0].upper()+why[1:],when=wk(fw).replace("Week","Wk").replace("Weeks","Wks"),urg=urg)',
  '                why=why[0].upper()+why[1:],when=wk(fw).replace("Week","Wk").replace("Weeks","Wks"),urg=urg,\n'
  '                gain=round(sum(max(0.0,v) for v in e["g"].values()),1),pgain=round(sum(max(0.0,e["g"].get(x,0.0)) for x in PLAYOFF),1))   # Oct 10: points added through Wk 17',1),
 ('json.dump(BOARD,open(f"{H}/scout_board_{LGK}.json","w"),indent=1)',
  '# Oct 10 (Dom): open seats lead the page - empty starting slots, open bench seats, open IR slots - and the best uses of them,\n'
  '# ranked by points the player adds to the best lineup through Week 17 (playoffs included). Caps from each league\'s Yahoo settings.\n'
  '_CAP={"DKI":(5,1),"DKII":(5,2),"DKIII":(5,1),"DKIV":(5,3)}[LGK]; _me=ROS[ROS.tid==ME]\n'
  '_nst=int((~_me.slot.isin(["BN","IR"])).sum())\n'
  'BOARD["open"]=dict(start=max(0,len(SLOTS)-_nst),bench=max(0,_CAP[0]-int((_me.slot=="BN").sum())),ir=max(0,_CAP[1]-int((_me.slot=="IR").sum())))\n'
  'BOARD["adds"]=[dict(name=e["p"]["name"].replace(" defense"," DEF"),team=e["p"]["team"],pos=e["p"]["pos"],acq=e["acq"].replace("free agent","Free agent").replace("waivers,","Waivers,"),\n'
  '                    gain=round(sum(max(0.0,v) for v in e["g"].values()),1),pgain=round(sum(max(0.0,e["g"].get(x,0.0)) for x in PLAYOFF),1))\n'
  '               for e in sorted([e for e in G2 if e["act"] and not killed(e["p"]["name"])],key=lambda e:-sum(max(0.0,v) for v in e["g"].values()))[:6]]\n'
  'json.dump(BOARD,open(f"{H}/scout_board_{LGK}.json","w"),indent=1)',1),
],"OCT10c scout open")
patch(f"{R}/cand/redesign/_fr_positions18.py",[
 ('"What each man is for — the roster, and the free agents who came through a door"','"What each man is for, and the free agents worth a look"',1),
],"OCT10c positions sub")

# ---------- 13 (Dom, Sat Oct 10 night) the Positions chart and the Scout must agree on who is available ----------
#  - the Positions engine took ownership from the Oct 1 blend (plus an Oct 2 spot check): a man rostered since then
#    (Roman Wilson and Marvin Harrison Jr. in DK II) still showed as a free agent on the chart. Ownership now comes from
#    the newest Yahoo read of every team in the league (the Scout's roster read), waivers from the same read.
patch(f"{R}/dksys/engine/engine3v.py",[
 ("OF=json.load(open('/home/claude/dksys/engine/own_fresh_oct2.json')); OFCHK={norm(n) for n in OF['_checked']}\n",
  "OF=json.load(open('/home/claude/dksys/engine/own_fresh_oct2.json')); OFCHK={norm(n) for n in OF['_checked']}\n"
  "# Oct 10 night (Dom): who owns whom = the newest Yahoo read of every team in the league, not the Oct 1 blend\n"
  "_LIVE={};_WV={}\n"
  "for _n,_lb in ((1,'DK I'),(2,'DK II'),(3,'DK III'),(4,'DK IV')):\n"
  "    _f=f'/home/claude/dksys/scout/dk{_n}_rosters_live.txt'\n"
  "    if os.path.exists(_f): _LIVE[_lb]={norm(l.split('|')[2]):l.split('|')[0] for l in open(_f) if l.strip() and not l.startswith('#') and l.count('|')>=4}\n"
  "    _w=f'/home/claude/dksys/scout/dk{_n}_waivers.txt'\n"
  "    if os.path.exists(_w): _WV[_lb]={norm(x.split('/')[0]) for l in open(_w) if not l.startswith('#') for x in l.strip().split('|') if x}\n",1),
 ("        rows.append(dict(player=r.player,k=r.k,pos=r.pos,team=team,own=own,",
  "        if _LIVE.get(lab) and r.k not in mine: own=('T'+_LIVE[lab][r.k]) if r.k in _LIVE[lab] else ('W' if r.k in _WV.get(lab,()) else 'FA')   # Oct 10 night: live Yahoo read wins\n"
  "        rows.append(dict(player=r.player,k=r.k,pos=r.pos,team=team,own=own,",1),
],"OCT10d live ownership")
#  - the Scout now prices every free agent the Positions chart shows (its "doors" list), even below its own 6-a-game
#    floor, so a man on the chart is never missing from the Scout's board without a stated reason. Anyone on the chart
#    the Scout does not recommend is named under "Checked, Not Assumed" with his points added and real level.
#  - every Scout pick carries its position.
#  - a Questionable (or Doubtful) starter gets a contingency: what the lineup loses if he sits, whether the open IR slot
#    can hold him, and the best free-agent fills for this week and next, by points added.
patch(f"{R}/dksys/scout/scout_engine.py",[
 ('cands=[k for k in PL if k not in taken and PL[k]["fwd"]>=(5 if PL[k]["pos"] in ("K","DEF") else 6) and norm(PL[k]["name"]) not in SEASON_OUT]\n',
  'cands=[k for k in PL if k not in taken and PL[k]["fwd"]>=(5 if PL[k]["pos"] in ("K","DEF") else 6) and norm(PL[k]["name"]) not in SEASON_OUT]\n'
  '# Oct 10 night (Dom): the Positions chart\'s free agents (its doors list) are priced here too, floor or not\n'
  'DOORS={}\n'
  'try:\n'
  '    import io as _io, contextlib as _cl\n'
  '    sys.path.insert(0,"/home/claude/dksys/engine"); _av=sys.argv[:]; sys.argv=["engine3v.py",str(NOW)]; _cwd=os.getcwd(); os.chdir("/home/claude/dksys/engine")\n'
  '    with _cl.redirect_stdout(_io.StringIO()):\n'
  '        import engine3v as _E3\n'
  '        _R3,_O3,_=_E3.run(CF["lab"])\n'
  '    os.chdir(_cwd); sys.argv=_av\n'
  '    for _o in _O3.itertuples():\n'
  '        _k=find(_o.player,_o.team,_o.pos)\n'
  '        if _k and _k not in taken: DOORS[_k]=dict(why=_o.why.split(" (")[0],doors=_o.doors)\n'
  '    cands=list(dict.fromkeys(cands+[k for k in DOORS if norm(PL[k]["name"]) not in SEASON_OUT]))\n'
  'except Exception as _ex: print("   scout: Positions doors not read -",_ex)\n',1),
 ('    return dict(name=p["name"].replace(" defense"," DEF"),team=p["team"],scores=sc,',
  '    return dict(name=p["name"].replace(" defense"," DEF"),team=p["team"],pos=p["pos"],scores=sc,',1),
 ('json.dump(BOARD,open(f"{H}/scout_board_{LGK}.json","w"),indent=1)',
  '_named={p["name"] for it in BOARD["gate1"] for p in it["picks"]}|{it["pick"]["name"] for it in BOARD["gate2"]}\n'
  '_chk=[]\n'
  'for _k,_d in DOORS.items():\n'
  '    _p=PL[_k]\n'
  '    if _p["name"] in _named or killed(_p["name"]): continue\n'
  '    _e=next((e for e in G2 if e["k"]==_k),None); _gn=round(sum(max(0.0,v) for v in _e["g"].values()),1) if _e else 0.0\n'
  '    _chk.append((-_gn,f"{_p[\'name\']} ({_p[\'team\']} {_p[\'pos\']}) is on the Positions chart ({_d[\'why\'].rstrip(\'; \')}) — "+\n'
  '        (f"adds ~{_gn:.0f} pts through Wk 17" if _gn>=1 else "adds nothing to the best lineup through Wk 17")+f", real level ~{_p[\'fwd\']:.1f} a game; ranks below the picks above"))\n'
  'BOARD["checked"]+=[t for _,t in sorted(_chk)[:4]]   # the four with the most points added; the rest are on the chart\n'
  '# Oct 10 night (Dom): a Questionable starter gets his contingency named - if he sits, what it costs and who fills it\n'
  'BOARD["qcont"]=[]\n'
  'for _i,_m in enumerate(MINE):                       # every man Yahoo has STARTING (the lineup as set) with a Q or D tag\n'
  '    if _m["slot"] in ("BN","IR") or _m["ytag"] not in ("Q","D"): continue\n'
  '    _v=vals(_m,NOW); _lab=next((l for l,j,v in LU[NOW] if j==_i),_m["pos"])\n'
  '    _rest=[m for j,m in enumerate(MINE) if j!=_i]; _base=total(_rest,NOW); _loss=my[NOW]-_base; _fl=[]\n'
  '    _okp=okfor(re.sub(r"\\d+$","",_lab))\n'
  '    for _k in [k for k in cands if PL[k]["pos"] in _okp and not killed(PL[k]["name"])]:\n'
  '        _nm=dict(key=_k,name=PL[_k]["name"],pos=PL[_k]["pos"],ytag="",slot="BN")\n'
  '        _g0=total(_rest+[_nm],NOW)-_base; _g1=(total(MINE+[_nm],NOW+1)-my[NOW+1]) if NOW+1 in my else 0.0\n'
  '        if _g0>=1: _fl.append(dict(name=PL[_k]["name"],team=PL[_k]["team"],pos=PL[_k]["pos"],now=round(_g0,1),nxt=round(_g1,1),fwd=round(PL[_k]["fwd"],1),\n'
  '                                   acq=("Waivers, clears "+WAIV[_k[0]]) if _k[0] in WAIV else "Free agent"))\n'
  '    _fl.sort(key=lambda d:-(d["now"]+d["nxt"]))\n'
  '    BOARD["qcont"].append(dict(name=MINE[_i]["name"],slot=_lab,tag=MINE[_i]["ytag"],val=round(_v,1),loss=round(_loss,1),fills=_fl[:3],\n'
  '                               ir=BOARD["open"]["ir"]>0,bench=BOARD["open"]["bench"]>0))\n'
  'json.dump(BOARD,open(f"{H}/scout_board_{LGK}.json","w"),indent=1)',1),
],"OCT10d scout doors qcont")
#  - the Scout page: name, team and position on every pick; the contingency box rides under Open Seats; the page
#    measures exactly what it draws (item spacing, the Also on the Board line), so Checked, Not Assumed can never be
#    pushed up into Gate 3 (the DK II overlap Dom found).
patch(f"{R}/cand/redesign/_scout_page.py",[
 ("""picks.append((p.get("urg","gold") if j==0 else None,f'<font name="PopB">{_esc(p["name"])}</font>, {_esc(p["team"])}  ·  Scored""",
  """picks.append((p.get("urg","gold") if j==0 else None,f'{_pt(p)}  ·  Scored""",1),
 ("""t=(f'<font name="PopB">{_esc(it["title"])}  ·  {_esc(p["name"])}</font>, {_esc(p["team"])}  ·  Scored""",
  """t=(f'<font name="PopB">{_esc(it["title"])}</font>  ·  {_pt(p)}  ·  Scored""",1),
 ("sum(_ph(t,_SCP,IW) for _,t in picks)+9","sum(_ph(t,_SCP,IW) for _,t in picks)+11",1),
 ("-_open_h(B)\n","-_open_h(B)-(30 if len(B['gate1'])>3 else 0)   # Oct 10 night: room for the Also on the Board line\n",1),
 ("    _para(c,chk,_SCS,M,max(y,BOT+chh),W-2*M)",
  "    if y-chh<BOT: import sys as _sy; print('   SCOUT PAGE OVERFLOW',lab,round(BOT-(y-chh),1),'pt',file=_sy.stderr)   # never silently: the build log says so\n"
  "    _para(c,chk,_SCS,M,max(y,BOT+chh),W-2*M)",1),
],"OCT10d scout page fit")
#  - the Positions page: full names on every ball; the Scout's picks plotted beside the doors' men; plates in words;
#    the legend spells out the color scale (pale = a little, deep = a lot) and every plate word.
patch(f"{R}/cand/redesign/_fr_positions18.py",[
 ("PROT17={}\n","PROT17={}\nexec(open('/home/claude/cand/redesign/_oct11_pos.py').read())   # Oct 10 night: full names, Scout picks, plates in words\n",1),
 ("        Op=O[O.pos==pos] if len(O) else O\n","        Op=_with_scout(O[O.pos==pos] if len(O) else O,R,pos,lab)\n",1),
 ('            lb=last(p["nm"]) if lastc[last(p["nm"])]==1 else p["nm"].split()[0][0]+". "+last(p["nm"])\n','            lb=_fullnm(p["nm"])\n',1),
 ('(TGRN,"rising — pale to deep by how hard")','(TGRN,"rising (pale = a little, deep = a lot)")',1),
 ('(TRED,"falling")','(TRED,"falling (pink = a little, red = a lot)")',1),
 ('"Movement = his last two games, the latest counting most, against his own earlier average.   How long:  ROS = rest of season · 3 WK = weeks · ? WK = unclear · BYE / INJ = cover"',
  '"Movement = his last two games, the latest counting most, against his own earlier average.        SCOUT PICK = recommended on the Scout page"',1),
 ('ph=(top-88)/2','ph=(top-98)/2',1),
 ('LX=PM+19;ky=78;x=LX;f6=6.0','LX=PM+19;ky=88;x=LX;f6=6.0',1),
 ('    _blot(x+5,ky+2,3.4,CARD,alpha(INKN,.55),.6);c.saveState();c.setStrokeColor(DOMV)',
  '    ky-=10;x=LX+c.stringWidth("Legend:  ","PopB",6.2)   # Oct 10 night: the rings get their own line\n    _blot(x+5,ky+2,3.4,CARD,alpha(INKN,.55),.6);c.saveState();c.setStrokeColor(DOMV)',1),
 ('"violet ring = yours"','"violet ring = on this roster"',2),
 ('"gold ring = best at the position"','"gold ring = best at the position        BYE FILL / INJURY FILL = covers a bye or an injury on this roster"',1),
 ('"What each man is for, and the free agents worth a look"','"Roles, and the free agents worth a look"',1),
 ('    txt(c,x4,ky,"Why he\'s here:","Pop",f6,GR);x4+=c.stringWidth("Why he\'s here:  ","Pop",f6)\n    for g_,lb in (("USAGE","usage up"),("EVENT","role opened"),("EVENT?","role may open"),("COVER","fills a hole"),("MARKET","market rising")):\n        dglyph(x4+GS/2,ky+2,g_);txt(c,x4+GS+3,ky,lb,"Pop",f6,GR);x4+=GS+11+c.stringWidth(lb,"Pop",f6)\n',
  '    txt(c,x4,ky,"Plate words:  USAGE UP = workload jumped  ·  ROLE OPENED = a teammate ahead of him is out (MAY OPEN = unconfirmed)  ·  MARKET UP = sources well above Gotham","Pop",f6,GR)\n',1),
],"OCT10d positions words")
#  - the Field Report: "F" is spelled out - the note is labeled Final and the banked number says FINAL.
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ('fn="NOW = Yahoo\'s projection for the lineup as set (F = final). Sleeper and Gotham are pre-game reads of the same men."',
  'fn="a gold number marked FINAL is a game already played. NOW = Yahoo\'s projection for the lineup as set. Sleeper and Gotham are pre-game reads of the same men."',1),
],"OCT10d field final")
patch(f"{R}/cand/redesign/fr17c.py",[
 ('note(c,NX,ny,"F",D["fnote"],6.2)','note(c,NX,ny,"Final",D["fnote"],6.2)',1),
],"OCT10d fr final")
#  - The Marks page: WHY HE'S HERE lists the plate words (the glyphs are gone from the plates); the Scout's spyglass gets
#    its own rows - splat on the first day, then the day count, the Signal's rule.
patch(f"{R}/cand/redesign/_fr_legend4.py",[
 ('lhd(y,"WHY HE\'S HERE","Positions page  ·  how a free agent got onto your page  ·  one fact, one door");y-=19\nfor code,lab,mean in (("USAGE","USAGE UP","His playing time last game ran well above his earlier games."),\n                      ("EVENT","ROLE OPENED","The man ahead of him is out or moved, confirmed."),\n                      ("EVENT?","ROLE MAY OPEN","Same, but only a missed practice so far, no designation. Watch it."),\n                      ("COVER","FILLS A HOLE","He beats your best cover for a starter on bye or out, Weeks 4-7."),\n                      ("MARKET","MARKET RISING","The forecasters rate him well above what his usage says.")):\n    lrow_(y,lambda m,code=code:dglyph(GX+2,m,code,GS*1.6),lab,mean,"Positions page, on his plate");y-=RH\nnote(c,SX,y+3,"How long","ROS = rest of season; 2 WK = about two weeks; ? WK = unclear. BYE or INJ = what hole he covers.",6.2);y-=RH\n',
  'lhd(y,"WHY HE\'S HERE","Positions page  ·  the words on a free agent\'s plate  ·  why he is on the chart, what he is for, how long");y-=19\nfor lab,mean in (("USAGE UP","His workload last game ran well above his earlier games."),\n                 ("ROLE OPENED","A teammate ahead of him is out or moved, confirmed."),\n                 ("ROLE MAY OPEN","Same, but only a missed practice so far, no designation. Watch it."),\n                 ("MARKET UP","The forecasters rate him well above what Gotham says."),\n                 ("BYE / INJURY FILL","He beats this roster\'s best cover for a starter on bye or out, Weeks 4-7."),\n                 ("ALL SEASON · 3 WEEKS","How long he should help. HOW LONG UNCLEAR when the opening has no end date."),\n                 ("SCOUT PICK","Recommended on the Scout page, plotted beside the men here.")):\n    lrow_(y,lambda m:None,lab,mean,"Positions page, on his plate");y-=RH\ny-=6\nlhd(y,"THE SCOUT\'S SPYGLASS","On the man a live Scout need is about  ·  color = how urgent the need is  ·  the Signal\'s life cycle: splat, then a day count");y-=19\ntry:\n    lrow_(y,lambda m:(scout_mark(c,GX-3,m+2.5,"red",0,7.2),scout_mark(c,GX+9,m+2.5,"gold",3,7.2)),"RED · GOLD","Red = act now, gold = watch. Splat = new today; 03 = three days on.","Field Report, Scout page");y-=RH+3\nexcept Exception as _ex: print("legend spyglass rows skipped:",_ex)\n',1),
 ("RH=17\n","RH=15.4\n",1),
],"OCT10d marks words")
# ---------- 15 (Oct 10 late) the chart and the Scout list the same men: the Scout prices the WHOLE doors list (no cap)
# and hands every price to the page; the Scout page then names, from the very list the Positions chart draws, each man on
# the chart it does not recommend - so a man on the chart is never missing from the Scout without his numbers. The chart
# shows up to eight door men a position (was six) before the Scout's own picks.
patch(f"{R}/dksys/engine/engine3v.py",[
 ("groupby('pos').head(6)","groupby('pos').head(int(os.environ.get('DK_DOORCAP','8')))",1),
],"OCT10e doorcap")
patch(f"{R}/dksys/scout/scout_engine.py",[
 ('        _R3,_O3,_=_E3.run(CF["lab"])\n','        os.environ["DK_DOORCAP"]="99"; _R3,_O3,_=_E3.run(CF["lab"]); os.environ.pop("DK_DOORCAP",None)\n',1),
 ('BOARD["checked"]+=[t for _,t in sorted(_chk)[:4]]   # the four with the most points added; the rest are on the chart\n',
  'BOARD["priced"]={re.sub(r"[^a-z]","",re.sub(r"\\b(jr|sr|ii|iii|iv|v)\\b","",PL[_k]["name"].lower())):dict(fwd=round(PL[_k]["fwd"],1),gain=next((round(sum(max(0.0,v) for v in e["g"].values()),1) for e in G2 if e["k"]==_k),0.0)) for _k in DOORS}   # the page names the chart men\n',1),
],"OCT10e scout prices doors")
patch(f"{R}/cand/redesign/_scout_page.py",[
 ("""    chk=('<font name="PopB">Checked, Not Assumed</font>  '+"  ·  ".join(_esc(s) for s in B["checked"])+""",
  """    chk=('<font name="PopB">Checked, Not Assumed</font>  '+"  ·  ".join(_esc(s) for s in B["checked"]+_chart_lines(lab,B))+""",1),
],"OCT10e scout chart lines")
# ---------- 16 (Oct 10 late) a game a man left hurt is not his level: the Scout drops any week he played under 35% of the
# snaps when he normally plays 60% or more (Jefferson Wk 3 at 12%, Chase Wk 4 at 20%) - those games were dragging his
# number down and the Scout's best lineup was benching him for it. Gotham (the meters) has the same flaw - left for Dom's call.
patch(f"{R}/dksys/scout/scout_engine.py",[
 ('    g=g.sort_values("week"); name=g.player_display_name.iloc[-1]; team=g.team.iloc[-1]; pos=g.position.iloc[-1]\n',
  '    g=g.sort_values("week"); name=g.player_display_name.iloc[-1]; team=g.team.iloc[-1]; pos=g.position.iloc[-1]\n'
  '    _sp=sn[(sn.player==name)&(sn.team==team)].set_index("week").offense_pct   # Oct 10 late: drop a game he left hurt\n'
  '    if len(_sp)>=2 and _sp.median()>=.6:\n'
  '        _ex=[w for w in g.week if _sp.get(w,1)<.35]\n'
  '        if _ex and len(g)>len(_ex): g=g[~g.week.isin(_ex)]\n',1),
],"OCT10f scout exit games")
# ---------- 17 (Oct 10 late) the slot chip reads FLEX and S-FLEX (superflex), not FLX / SFLX
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ('_SLOTN={"W/R/T":"FLX","Q/W/R/T":"SFLX"}','_SLOTN={"W/R/T":"FLEX","Q/W/R/T":"S-FLEX"}',1),
 ('\'(OPP,"OPP","NOW")\'','\'(OPP,"THEIR MAN","NOW")\'',1),
],"OCT10f slot words")
# ---------- 18 (Dom, Sun Oct 11) game weather on the Field Report: a picture beside each opponent, and one note line
patch(f"{R}/cand/redesign/fr17c.py",[
 ('    print(LG_,"FR1 lowest",ny-20)','    note(c,NX,ny-30,"Weather",WX_NOTE,6.2)   # Oct 11 (Dom): the game weather\n    print(LG_,"FR1 lowest",ny-30)',1),
 ('    note(c,NX,ny,"Final",D["fnote"],6.2)\n','    _ns=10 if ny-40>=29 else max(7.2,(ny-29)/4.0)   # Oct 11: all five notes fit above the footer\n    note(c,NX,ny,"Final",D["fnote"],6.2)\n',1),
 ('note(c,NX,ny-10,"Opponent"','note(c,NX,ny-_ns,"Opponent"',1),
 (',6.2);ny-=10\n',',6.2);ny-=_ns\n',1),
 ('note(c,NX,ny-10,"Bye"','note(c,NX,ny-_ns,"Bye"',1),
 ('note(c,NX,ny-20,"Numbers"','note(c,NX,ny-2*_ns,"Numbers"',1),
 ('note(c,NX,ny-30,"Weather"','note(c,NX,ny-3*_ns,"Weather"',1),
],"OCT11 fr weather")
# ---------- 19 (Dom, Sun Oct 11) the Dispatch matches Dark Knight Live: his icon right after the title on every page
# (no ring), and the short one-line league names he chose - Most Important, Winners Sinners, Hers His Ver 2.0, Murrieta NXTDR
patch(f"{R}/cand/redesign/_masthead_field.py",[
 ('txt(c,M,Ht-44,PZ_TITLE,"Bebas",34,PAPER)',
  'txt(c,M,Ht-44,PZ_TITLE,"Bebas",34,PAPER)\n'
  '    if "dk_icon" not in globals(): exec(open("/home/claude/cand/redesign/_dkicon.py").read(),globals())\n'
  '    dk_icon(c,M+c.stringWidth(PZ_TITLE,"Bebas",34)+9,Ht-47,29)   # Oct 11 (Dom): the icon after the title',1),
],"OCT11 icon pages")
patch(f"{R}/cand/global/_mast33.py",[
 ('txt(c,M+P,Ht-44,N["PZ_TITLE"],"Bebas",34,PAPER)',
  'txt(c,M+P,Ht-44,N["PZ_TITLE"],"Bebas",34,PAPER)\n'
  '    if "dk_icon" not in N: exec(open("/home/claude/cand/redesign/_dkicon.py").read(),N)\n'
  '    N["dk_icon"](c,M+P+c.stringWidth(N["PZ_TITLE"],"Bebas",34)+9,Ht-47,29)   # Oct 11 (Dom): the icon after the title',1),
],"OCT11 icon front")
_SHORT='{"DK I":"Most Important","DK II":"Winners Sinners","DK III":"Hers His Ver 2.0","DK IV":"Murrieta NXTDR"}'
patch(f"{R}/cand/global/global33.py",[
 ('FULL={"DK I":"TheMostImportantThingInLife","DK II":"Winners and Sinners","DK III":"Hers and His Version 2.0","DK IV":"Murrieta NextDoor"}',
  'FULL='+_SHORT+'   # Oct 11 (Dom): short one-line names, same as Dark Knight Live',1),
],"OCT11 short names front")
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ('_TEAMS={"DK I":"TheMostImportantThingInLife","DK II":"Winners and Sinners","DK III":"Hers and His Version 2.0","DK IV":"Murrieta NextDoor"}',
  '_TEAMS='+_SHORT+'   # Oct 11 (Dom): short one-line names, same as Dark Knight Live',1),
],"OCT11 short names pages")
# ---------- 20 (Dom, Sun Oct 11) front page, two fixes matching Dark Knight Live:
#  a. the flagpole (the white now edge) stops just above the higher of the two flags, wherever the ridges are now -
#     it no longer climbs to the tallest mountain at that hour and stays up there.
#  b. a meter says WON or LOST (FINAL) as soon as the matchup is decided: every starter on both sides has a final game,
#     even if Monday night still has games for other teams. Same gauge, same room as the end-of-week result.
patch(f"{R}/cand/global/global33.py",[
 ('yt=min(CEIL,max(max(tops),max(ridge_at(P,bx) for P in PS.values())+2))',
  'yt=min(CEIL,max(tops)+2)   # Oct 11 (Dom): the pole ends just above the flags, not at the tallest ridge',3),
 ('    ACT[lab]=dict(me=_bank(sm),op=_bank(so))',
  '    ACT[lab]=dict(me=_bank(sm),op=_bank(so))\n'
  '    DEC[lab]=all(p["window"] is None or p["window"]<DONE for p in sm+so)   # Oct 11 (Dom): nobody left to play on either side',1),
 ('YL,YAH,MOD,EFF,COMP,ACT={},{},{},{},{},{}','YL,YAH,MOD,EFF,COMP,ACT,DEC={},{},{},{},{},{},{}',1),
 ('    FIN=done>=NW\n','    FIN=done>=NW or DEC.get(D["lab"],False)   # Oct 11 (Dom): WON / LOST once decided\n',1),
],"OCT11 pole and decided")
# ---------- 21 (Dom, Sun Oct 11) one masthead on every page: the inner pages get the front page's band -
# inside the margins, rounded corners, the same height, the same gold rule under it.
patch(f"{R}/cand/redesign/_masthead_field.py",[
 ('def masthead(c,section,sub):\n    c.setFillColor(PAPER);c.rect(0,0,W,Ht,stroke=0,fill=1)\n    c.setFillColor(INKN);c.rect(0,Ht-MH,W,MH,stroke=0,fill=1)\n    txt(c,M,Ht-44,PZ_TITLE,"Bebas",34,PAPER)\n    if "dk_icon" not in globals(): exec(open("/home/claude/cand/redesign/_dkicon.py").read(),globals())\n    dk_icon(c,M+c.stringWidth(PZ_TITLE,"Bebas",34)+9,Ht-47,29)   # Oct 11 (Dom): the icon after the title\n    c.setFillColor(SUN[1]);c.rect(M,Ht-56,c.stringWidth(section,"Bebas",15),1.6,stroke=0,fill=1)   # Oct 10: the bar spans the section name\n    txt(c,M,Ht-74,section,"Bebas",15,SUN[1])\n    _sx=M+c.stringWidth(section,"Bebas",15)+10; _wk=globals().get("WEEKN")\n    if _wk and not sub.startswith("Week"): sub=f"Week {_wk}  ·  "+sub\n    if "asof_line" not in globals(): exec(open("/home/claude/cand/redesign/_asof.py").read(),globals())\n    asof_line(c,_sx,Ht-73.5,sub,W-M-9-108-10)   # Oct 10: As of + stoplight on every page\n    i=_pz_idx(section);lg=_pz_league(section);col=LG[lg] if lg else SUN[1]\n    puzzle(c,i,col)                                   # Last Updated retired from the masthead - freshness moves to each block\n    c.setFillColor(SUN[1]);c.rect(0,Ht-MH-3,W,3,stroke=0,fill=1)',
  'def masthead(c,section,sub):\n    # Oct 11 (Dom): every page carries the front page\'s masthead - inside the margins, rounded, the same size\n    c.setFillColor(PAPER);c.rect(0,0,W,Ht,stroke=0,fill=1)\n    P=12;top=Ht-8;bot=top-MH+8\n    c.setFillColor(INKN);c.roundRect(M,bot,W-2*M,top-bot,5,stroke=0,fill=1)\n    txt(c,M+P,Ht-44,PZ_TITLE,"Bebas",34,PAPER)\n    if "dk_icon" not in globals(): exec(open("/home/claude/cand/redesign/_dkicon.py").read(),globals())\n    dk_icon(c,M+P+c.stringWidth(PZ_TITLE,"Bebas",34)+9,Ht-47,29)\n    c.setFillColor(SUN[1]);c.rect(M+P,Ht-56,c.stringWidth(section,"Bebas",15),1.6,stroke=0,fill=1)\n    txt(c,M+P,Ht-72,section,"Bebas",15,SUN[1])\n    _sx=M+P+c.stringWidth(section,"Bebas",15)+10; _wk=globals().get("WEEKN")\n    if _wk and not sub.startswith("Week"): sub=f"Week {_wk}  ·  "+sub\n    if "asof_line" not in globals(): exec(open("/home/claude/cand/redesign/_asof.py").read(),globals())\n    asof_line(c,_sx,Ht-71.5,sub,W-M-9-108-(M+4)-12)   # stops short of the puzzle where it really sits\n    i=_pz_idx(section);lg=_pz_league(section);col=LG[lg] if lg else SUN[1]\n    c.saveState();p=c.beginPath();p.roundRect(M,bot,W-2*M,top-bot,5);c.clipPath(p,stroke=0)\n    c.translate(-(M+4),-4);puzzle(c,i,col);c.restoreState()\n    c.setFillColor(SUN[1]);c.rect(M,bot-3,W-2*M,2.2,stroke=0,fill=1)',1),
],"OCT11 inset masthead")
patch(f"{R}/cand/global/_mast33.py",[
 ('sub,W-M-9-108-10-P)','sub,W-M-9-108-(M+4)-12)   # Oct 11: stops short of the puzzle where it really sits',1),
],"OCT11 front asof room")
# ---------- 22 (Sun Oct 11) "Fix the lineup" only for a man who can still hurt you: a starter tagged Out whose game is
# already final with points on the board (Henderson, Week 5: O tag, 5.8 final) is not a lineup problem.
patch(f"{R}/cand/global/global33.py",[
 ('bad=[_ln11(p["player"]) for p in me if p["window"] is None or p.get("status") in ("O","IR","IR-R","PUP-R","NA")]',
  'bad=[_ln11(p["player"]) for p in me if p["window"] is None or (p.get("status") in ("O","IR","IR-R","PUP-R","NA") and p.get("actual") is None)]',1),
],"OCT11 alarm played front")
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ('out_=[r[1] for r in S if r[1] and r[2] in ("O","IR")]',
  'out_=[r[1] for r in S if r[1] and r[2] in ("O","IR") and not any(p["player"]==r[1] and p.get("actual") is not None for p in L["starters"]["me"])]',1),
],"OCT11 alarm played pages")
# ---------- 23 (Dom, Sun Oct 11) the Field Report masthead says only the week and the As of - the league and the
# opponent are already on the card right under it.
patch(f"{R}/cand/redesign/_masthead_field.py",[
 ('    if _wk and not sub.startswith("Week"): sub=f"Week {_wk}  ·  "+sub',
  '    if _wk and not sub.startswith("Week"): sub=f"Week {_wk}  ·  "+sub\n'
  '    if "FIELD REPORT" in section.upper(): sub=f"Week {_wk}" if _wk else sub.split("  ·  ")[0]   # Oct 11 (Dom): too much up here',1),
],"OCT11 field report mast")
# ---------- 24 (Sun Oct 11) a last-name fallback must also match the first initial: bench man Wan'Dale Robinson was
# picking up starter Bijan Robinson's Yahoo number (22.9) on the Field Report. A bench man not in the live read stays blank.
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ('        if len(hit)>1 and team: hit=[d for d in hit if d["team"]==team] or hit',
  '        _fi=norm(key)[:1]; hit=[d for d in hit if norm(d["name"])[:1]==_fi]   # Oct 11: same first initial, or no match\n'
  '        if len(hit)>1 and team: hit=[d for d in hit if d["team"]==team] or hit',1),
],"OCT11 lastname initial")
# ---------- 25 (Dom, Sun Oct 11) THE DISAGREEMENT FLAG: on the Field Report, a starter whose Gotham number and Yahoo's
# part by 4 points or more gets his Gotham cell boxed in red. The Scoreboard showed those are the hard calls (misses run
# bigger) - the box does not say who is right, it says look at this man.
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ('fdec(c,GW,ry,wkm17(nm,LAB17) if stt not in ("O","IR") else None,False,"PopM",7.2)','_gwcell(c,GW,ry,nm,stt)',1),
 ('_SLOTN={"W/R/T":"FLEX","Q/W/R/T":"S-FLEX"}',
  'def _gw_started(nm):\n'
  '    import datetime as _gd; from zoneinfo import ZoneInfo as _gz\n'
  '    p=_mrow(nm,LAB17); t=(p or {}).get("team")\n'
  '    if not t: return True\n'
  '    g=_pd.read_csv("/home/claude/dksys/data/latest/games.csv",low_memory=False); t={"LAR":"LA","JAC":"JAX","WSH":"WAS"}.get(t,t)\n'
  '    g=g[(g.season==g.season.max())&(g.week==WEEKN)&((g.home_team==t)|(g.away_team==t))]\n'
  '    if g.empty: return True\n'
  '    ko=_gd.datetime.strptime(f"{g.gameday.iloc[0]} {g.gametime.iloc[0]}","%Y-%m-%d %H:%M").replace(tzinfo=_gz("America/New_York"))\n'
  '    return _gd.datetime.now(_gd.timezone.utc)>=ko\n'
  'def _gwcell(c,x,y,nm,stt):\n'
  '    from reportlab.lib.colors import HexColor as _HX\n'
  '    v=wkm17(nm,LAB17) if stt not in ("O","IR") else None\n'
  '    n=_NOWME(nm) if v is not None else None\n'
  '    flag=bool(n) and not n[1] and abs(float(v)-float(n[0]))>=4 and not _gw_started(nm)   # pregame only: after kickoff the numbers mean other things\n'
  '    if flag: c.setStrokeColor(_HX("#C62828")); c.setLineWidth(.8); c.roundRect(x-17,y-3,34,10.5,2.5,stroke=1,fill=0)\n'
  '    fdec(c,x,y,v,False,"PopB" if flag else "PopM",7.2,_HX("#C62828") if flag else INKN)\n'
  '_SLOTN={"W/R/T":"FLEX","Q/W/R/T":"S-FLEX"}',1),
 ('Actual = his average, Weeks 1–{WEEKN-1}."','Actual = his average, Weeks 1–{WEEKN-1}. Red box = Gotham, Yahoo 4+ apart."',1),
],"OCT11 disagreement flag")
# ---------- 26 (Dom, Sun Oct 11) the GOTHAM WEEK column stays a projection all week: once a man's game is played, Gotham's
# row turns into his actual points (the Yahoo NOW column already shows those, marked FINAL). It now keeps showing what
# Gotham said BEFORE his kickoff - the number the Scoreboard grades - so the row reads: Gotham said X, he scored Y.
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ('    return None if m.empty or _pd.isna(m.eng_wk.iloc[0]) else f"{float(m.eng_wk.iloc[0]):.1f}"',
  '    if not m.empty and bool(m.played_wk.iloc[0]):          # Oct 11: game played - show Gotham\'s pregame number, not the actual\n'
  '        pv=_pregame_g(nm,lab); return None if pv is None else f"{pv:.1f}"\n'
  '    return None if m.empty or _pd.isna(m.eng_wk.iloc[0]) else f"{float(m.eng_wk.iloc[0]):.1f}"\n'
  '_PREG={}\n'
  'def _pregame_g(nm,lab):\n'
  '    import os as _po, json as _pj\n'
  '    if "d" not in _PREG:\n'
  '        f=_po.path.join(_po.environ.get("GITHUB_WORKSPACE","/nonexistent"),"dispatch_out","scoreboard",f"pregame_wk{WEEKN}.json")\n'
  '        try: _PREG["d"]=_pj.load(open(f))\n'
  '        except Exception: _PREG["d"]={}\n'
  '    for v in _PREG["d"].values():\n'
  '        if v.get("league")==lab and norm(v.get("player",""))==norm(nm) and v.get("gotham") is not None: return float(v["gotham"])\n'
  '    return None',1),
 ('NUMBERS_NOTE=f"Sleeper = Sleeper, league scoring. Yahoo = Yahoo now. Gotham = our engine, this week and a game over his next three. Actual = his average, Weeks 1–{WEEKN-1}. Red box = Gotham, Yahoo 4+ apart."',
  'NUMBERS_NOTE=f"Gotham = ours: this week (pregame once played), next 3. Yahoo = now. Sleeper = league scoring. Actual = avg Wks 1–{WEEKN-1}. Red box: Gotham, Yahoo 4+ apart."',1),
],"OCT11 gotham pregame")
# ---------- 27 (Dom, Sun Oct 11) A MAN WHOSE GAME IS ON GLOWS: on the Field Report, the NOW number of any starter (his or
# the man across from him) whose game has kicked off and is not final sits in a soft green glow with a small LIVE tag -
# the same idea as the gold FINAL wash, one step earlier. Kickoff and final come from the NFL schedule each build.
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ('if _n: fdec(c,YH,ry,f"{_n[0]:.1f}",_n[1],"PopB",7.2,INKN)','if _n: _nowcell(c,YH,ry,_n,(_mrow(nm,LAB17) or {}).get("team"),"PopB")',1),
 ('fdec(c,OPP,ry,(f"{_b[0]:.1f}" if _b else None),bool(_b and _b[1]),"PopM",7.2)',
  '(_nowcell(c,OPP,ry,_b,(OPMAP.get(om) or {}).get("team"),"PopM") if _b else fdec(c,OPP,ry,None,False,"PopM",7.2))',1),
 ('_SLOTN={"W/R/T":"FLEX","Q/W/R/T":"S-FLEX"}',
  'def _team_live(t):\n'
  '    import datetime as _ld; from zoneinfo import ZoneInfo as _lz\n'
  '    if not t: return False\n'
  '    if "g" not in _PREG: _PREG["g"]=_pd.read_csv("/home/claude/dksys/data/latest/games.csv",low_memory=False)\n'
  '    g=_PREG["g"]; t={"LAR":"LA","JAC":"JAX","WSH":"WAS"}.get(t,t)\n'
  '    g=g[(g.season==g.season.max())&(g.week==WEEKN)&((g.home_team==t)|(g.away_team==t))]\n'
  '    if g.empty or g.result.notna().iloc[0]: return False\n'
  '    ko=_ld.datetime.strptime(f"{g.gameday.iloc[0]} {g.gametime.iloc[0]}","%Y-%m-%d %H:%M").replace(tzinfo=_lz("America/New_York"))\n'
  '    now=_ld.datetime.now(_ld.timezone.utc); return ko<=now<=ko+_ld.timedelta(hours=4)\n'
  'def _nowcell(c,x,y,n,team,font):\n'
  '    from reportlab.lib.colors import HexColor as _HX\n'
  '    if n and not n[1] and _team_live(team):\n'
  '        G=_HX("#3FB36A"); c.saveState()\n'
  '        for k,a in ((2.4,.10),(1.5,.16),(.7,.24)): c.setFillColor(G); c.setFillAlpha(a); c.roundRect(x-17-k,y-3-k,34+2*k,10.5+2*k,2.5+k,stroke=0,fill=1)\n'
  '        c.restoreState()\n'
  '        fdec(c,x,y,f"{n[0]:.1f}",False,font,7.2,INKN)\n'
  '        b=f"{n[0]:.1f}".split(".")[1]; txt(c,x+c.stringWidth("."+b,font,7.2)+1.6,y,"LIVE","PopB",4.6,_HX("#1E7A45"))\n'
  '    else: fdec(c,x,y,(f"{n[0]:.1f}" if n else None),bool(n and n[1]),font,7.2,INKN)\n'
  '_SLOTN={"W/R/T":"FLEX","Q/W/R/T":"S-FLEX"}',1),
 ('Red box: Gotham, Yahoo 4+ apart."','Red box: Gotham, Yahoo 4+ apart. Green glow: game on now."',1),
],"OCT11 live glow")
# ---------- 28 (Dom, Sun Oct 11) the PLAYED squares on the front page: a starter whose game is on right now gets a glowing
# green square between the solid (played) and the empty (still to go) ones - played, playing, to go, at a glance.
patch(f"{R}/cand/global/global33.py",[
 ('''        for k in range(tot):
            x=x0+k*(pw+pg)
            if k<pl: c.setFillColor(cc); c.roundRect(x,yy,pw,ph,.8,fill=1,stroke=0)
            else: c.setStrokeColor(mix(cc,BG2,.35)); c.setLineWidth(.6); c.roundRect(x+.3,yy+.3,pw-.6,ph-.6,.7,fill=0,stroke=1)''',
  '''        lv=_livecount(Y["me" if j==0 else "op"])   # Oct 11 (Dom): men playing right now
        for k in range(tot):
            x=x0+k*(pw+pg)
            if k<pl: c.setFillColor(cc); c.roundRect(x,yy,pw,ph,.8,fill=1,stroke=0)
            elif k<pl+lv:
                c.saveState(); c.setFillColor(H("#3FB36A"))
                for e_,a_ in ((1.6,.18),(.8,.32)): c.setFillAlpha(a_); c.roundRect(x-e_,yy-e_,pw+2*e_,ph+2*e_,.8+e_,fill=1,stroke=0)
                c.setFillAlpha(1); c.setFillColor(H("#4FD08A")); c.roundRect(x,yy,pw,ph,.8,fill=1,stroke=0); c.restoreState()
            else: c.setStrokeColor(mix(cc,BG2,.35)); c.setLineWidth(.6); c.roundRect(x+.3,yy+.3,pw-.6,ph-.6,.7,fill=0,stroke=1)''',2),
 ('def pips22(x0,y,D,col):',
  'def _livecount(rows):\n'
  '    """starters whose game has kicked off and is not final (NFL schedule), not yet banked"""\n'
  '    import datetime as _ld; from zoneinfo import ZoneInfo as _lz\n'
  '    now=_ld.datetime.now(_ld.timezone.utc); n=0\n'
  '    for r in rows:\n'
  '        if r[4] is not None or not r[1]: continue\n'
  '        t={"LAR":"LA","JAC":"JAX","WSH":"WAS"}.get(r[1],r[1]); g=G[(G.home_team==t)|(G.away_team==t)]\n'
  '        if g.empty or g.result.notna().iloc[0]: continue\n'
  '        try: ko=_ld.datetime.strptime(f"{g.gameday.iloc[0]} {g.gametime.iloc[0]}","%Y-%m-%d %H:%M").replace(tzinfo=_lz("America/New_York"))\n'
  '        except Exception: continue\n'
  '        if ko<=now<=ko+_ld.timedelta(hours=4): n+=1\n'
  '    return n\n'
  'def pips22(x0,y,D,col):',1),
],"OCT11 played squares glow")
# ---------- 29 (Dom, Sun Oct 11) GOTHAM DROPS A GAME A MAN LEFT HURT - the same rule the Scout has used since Oct 10 (#16):
# a game where he played under 35% of the offense's snaps, when he normally plays 60% or more, is not his level (Jefferson
# Wk 3 at 12%, Chase Wk 4 at 20%, Achane Wk 3 at 5%). It no longer drags his workload down. Past weeks only; the game being
# played this week still counts as his actual. Every dropped game is printed in the build log.
patch(f"{R}/dksys/engine/engine3v.py",[
 ('def run(lab):\n',
  'def _drop_exits(F):\n'
  '    """Oct 11 (Dom): remove past games a man left hurt - under 35% of snaps when his usual (median) is 60%+; keeps at least one game"""\n'
  '    try: sn=pd.read_csv("/home/claude/dksys/gate/fresh/snap_counts_2026.csv",low_memory=False)\n'
  '    except Exception as ex: print("INJURY-EXIT: no snap counts, nothing dropped -",ex); return F\n'
  '    sn=sn[(sn.game_type=="REG")&(sn.week<WEEK)&sn.position.isin(POS)].copy(); sn["k"]=sn.player.astype(str).map(FM.norm)\n'
  '    drop=set(); seen=[]\n'
  '    for (k_,p_),g_ in sn.groupby(["k","position"]):\n'
  '        if len(g_)<2 or g_.offense_pct.median()<.6: continue\n'
  '        ex=[int(w) for w,v in zip(g_.week,g_.offense_pct) if v<.35]\n'
  '        if ex and len(ex)<len(g_):\n'
  '            drop.update((k_,w) for w in ex); seen.append(f"{g_.player.iloc[0]} Wk "+",".join(map(str,ex)))\n'
  '    if not drop: return F\n'
  '    m=[(k_,int(w)) in drop and w<WEEK for k_,w in zip(F.key,F.week)]\n'
  '    if "_EXITSHOWN" not in globals(): print("INJURY-EXIT games dropped:",len(drop),"|","; ".join(sorted(seen))); globals()["_EXITSHOWN"]=1\n'
  '    return F[~pd.Series(m,index=F.index)]\n'
  'def run(lab):\n',1),
 ("    F['team']=F.team.map(T)\n","    F['team']=F.team.map(T)\n    F=_drop_exits(F)   # Oct 11 (Dom): a game he left hurt is not his level\n",1),
],"OCT11 gotham injury exits")
# ---------- 30 (Dom, Sun Oct 11) THE SCOREBOARD gets its own page, the last one, after The Marks: this week, the running
# total from Week 2, the trend by week, by position, the disagreement test, and the week's biggest misses.
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ('   # THE MARKS travels as the last page\n',
  '   # THE MARKS travels as the last page\nexec(open("/home/claude/cand/redesign/_scoreboard_page.py").read())   # Oct 11 (Dom): THE SCOREBOARD, the final page\n',1),
],"OCT11 scoreboard page")
# ---------- 31 (Dom, Sun Oct 11, his call on the Oct 7 engine questions - yes to both):
# (1) A MAN RULED OUT ZEROES HIMSELF on one source: ESPN or Sleeper alone saying Out now makes his own number 0 (it was
#     cut to a quarter as if Doubtful). Moving his work to teammates still needs both sources or the NFL report.
# (2) WEEK-TO-WEEK = DOUBTFUL: no feed carries "week-to-week" as a status - it lives in ESPN's news line ("expected to miss
#     three to four weeks", "week-to-week", "sidelined about eight weeks"). A man with such a line in the last 10 days and
#     no Out/Doubtful/Questionable on the NFL report is treated as Doubtful (a quarter of his number).
patch(f"{R}/dksys/engine/engine3v.py",[
 ("            if src5 in ('ESPN only','Sleeper only','ESPN+Sleeper DISAGREE') and st5=='Out': st5='Doubtful'   # one source saying Out = treat as Doubtful until confirmed",
  "            if src5=='ESPN+Sleeper DISAGREE' and st5=='Out': st5='Doubtful'   # Oct 11 (Dom): one source alone saying Out now zeroes him; a real disagreement still softens",1),
 ("for k,v in _IRS.items():\n    if v in ('Out','Doubtful','Questionable'): STATUS[k]=(v,'NFL report')\n",
  "for k,v in _IRS.items():\n    if v in ('Out','Doubtful','Questionable'): STATUS[k]=(v,'NFL report')\n"
  "try:   # Oct 11 (Dom): week-to-week = Doubtful, read from ESPN's news line\n"
  "    import re as _wre, datetime as dt\n"
  "    _WTW=_wre.compile(r'week-to-week|week to week|(expected to|will|could|set to|slated to) miss (about |roughly |at least |the next )?(\\w+|\\d+)(-to-| to |-)?(\\w+|\\d+)? weeks|sidelined (for )?(about |roughly |at least )?(\\w+|\\d+)(-to-| to |-)?(\\w+|\\d+)? weeks',_wre.I)\n"
  "    _now=dt.datetime.now(dt.timezone.utc); _wtw=[]\n"
  "    for it in (_EJ.values() if isinstance(_EJ,dict) else _EJ):\n"
  "        if not isinstance(it,dict) or not it.get('name') or not _WTW.search(str(it.get('detail',''))): continue\n"
  "        try: _age=(_now-dt.datetime.strptime(str(it.get('date',''))[:16],'%Y-%m-%dT%H:%M').replace(tzinfo=dt.timezone.utc)).days\n"
  "        except Exception: continue\n"
  "        k=norm(it['name'])\n"
  "        if _age<=10 and _IRS.get(k) not in ('Out','Doubtful','Questionable') and STATUS.get(k,('',''))[0] not in ('Out','Doubtful'):\n"
  "            STATUS[k]=('Doubtful','week-to-week (ESPN news)'); _wtw.append(it['name'])\n"
  "    print('WEEK-TO-WEEK -> Doubtful:',len(_wtw),'|',', '.join(_wtw[:20]))\n"
  "except Exception as _e: print('week-to-week rule skipped:',_e)\n",1),
],"OCT11 selfout and week-to-week")
