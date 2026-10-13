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
# ---------- 32 (Dom, Mon Oct 12): three Gotham changes from the morning's tests, each on its own switch so any one can come out.
# Baseline = all four switches off (DK_HANDOFF=off DK_VEGHALF=off DK_ELITEVEG=off DK_PRACTRIM=off) reproduces Gotham as of Oct 11.
# (1) HALF HANDOFF: a ruled-out man's work goes to his position-mates at no more than half (was RB/WR .88, TE .37 stays).
#     Replay Wks 2-5: role-opens men miss 6.84 -> 6.38 (Yahoo 6.50). Live Wk5 overshoot: Swift 23.9 (scored 17.3), McLaurin 16.5 (12.2).
# (2) VEGAS AT HALF STRENGTH: with the matchup factor off, this week's Vegas factor was square-rooted again (quarter strength);
#     it now enters at its own strength, (implied / mean)^.5 held .88-1.12. Replay: quarter vs half within .01 pts - tiny.
# (3a) ELITE LOW-VEGAS CUT: a top-20% man at his position (points a game, 2+ games) whose team's implied total is under the
#     week's mean loses half the gap in points (implied 18.5 vs mean 22.5 -> -2.0). Never raises anyone.
# (3b) PRACTICE TRIM: missed or limited practice this week with no game designation -> his number x .95.
patch(f"{R}/dksys/engine/engine3v.py",[
 ("            g_=VACATE[p]*frac*wl_*WL[k2][0]/tot\n",
  "            g_=(VACATE[p] if os.environ.get('DK_HANDOFF','0.5')=='off' else min(VACATE[p],float(os.environ.get('DK_HANDOFF','0.5'))))*frac*wl_*WL[k2][0]/tot   # Oct 12 (Dom): half handoff\n",1),
 ("            if wk_==WEEK and vfac(team) is not None: m=(m*vfac(team))**.5      # v4: Vegas blended in for this week\n",
  "            if wk_==WEEK and vfac(team) is not None: m=vfac(team) if (os.environ.get('DK_NOMATCH') and os.environ.get('DK_VEGHALF','on')!='off') else (m*vfac(team))**.5      # v4 Vegas; Oct 12 (Dom): matchup off -> Vegas at half strength, not a quarter\n",1),
],"OCT12 handoff and vegas")
patch(f"{R}/dksys/engine/gotham.py",[
 ("    E['eng_fwd']=[bl(v,r_) for v,r_ in zip(E.eng_fwd,E.itertuples())]\n",
  "    E['eng_fwd']=[bl(v,r_) for v,r_ in zip(E.eng_fwd,E.itertuples())]\n"
  "    E['oct12']=''\n"
  "    try:   # Oct 12 (Dom): elite low-Vegas cut + practice trim, this week's number only, each on its own switch\n"
  "        _g=pd.read_csv(D+'games.csv'); _g=_g[(_g.season==2026)&(_g.week==WEEK)&_g.total_line.notna()&_g.spread_line.notna()]\n"
  "        _TF={'LAR':'LA','WSH':'WAS','JAC':'JAX'}; _t=lambda x:_TF.get(str(x).upper(),str(x).upper())\n"
  "        _IMP={**{_t(a):(t_+s_)/2 for a,t_,s_ in zip(_g.home_team,_g.total_line,_g.spread_line)},**{_t(a):(t_-s_)/2 for a,t_,s_ in zip(_g.away_team,_g.total_line,_g.spread_line)}}\n"
  "        _M=float(np.mean(list(_IMP.values()))) if _IMP else None\n"
  "        _pp=S[S.position.isin(['QB','RB','WR','TE'])].groupby(['k','position']).fantasy_points_ppr.agg(['mean','size']).reset_index(); _pp=_pp[_pp['size']>=2]\n"
  "        _pp['pr']=_pp.groupby('position')['mean'].rank(ascending=False,pct=True); _EL={(a,b) for a,b,c in zip(_pp.k,_pp.position,_pp.pr) if c<=.20}\n"
  "        _I=pd.read_csv(D+'injuries.csv'); _I=_I[_I.week==WEEK]\n"
  "        _PR={norm(str(a)) for a,b,c in zip(_I.full_name,_I.practice_status,_I.report_status) if ('Did Not' in str(b) or 'Limited' in str(b)) and str(c)=='nan'}\n"
  "        _ne=_np=0\n"
  "        for i_,r_ in E.iterrows():\n"
  "            v=r_.eng_wk\n"
  "            if pd.isna(v) or v<=0 or bool(r_.played_wk): continue\n"
  "            tm=_t(r_.team); tag=[]\n"
  "            if os.environ.get('DK_ELITEVEG','on')!='off' and _M and (r_.k,r_.pos) in _EL and tm in _IMP and _IMP[tm]<_M:\n"
  "                v=max(0.0,v+.5*(_IMP[tm]-_M)); tag.append(f'elite low-Vegas {.5*(_IMP[tm]-_M):+.1f}'); _ne+=1\n"
  "            if os.environ.get('DK_PRACTRIM','on')!='off' and r_.k in _PR:\n"
  "                v=v*.95; tag.append('practice x.95'); _np+=1\n"
  "            if tag: E.at[i_,'eng_wk']=round(v,2); E.at[i_,'oct12']='; '.join(tag)\n"
  "        _msg=f'OCT12 {lab}: elite low-Vegas cuts {_ne} | practice trims {_np} | handoff {os.environ.get(\"DK_HANDOFF\",\"0.5\")} | vegas half {os.environ.get(\"DK_VEGHALF\",\"on\")}'\n"
  "    except Exception as _e: _msg=f'OCT12 {lab}: adjustments skipped: {_e}'\n"
  "    open(os.path.join(HERE,'gotham_oct12.txt'),'a' if lab!='DKI' else 'w').write(_msg+'\\n')   # no print: the build reads only gotham's first two lines\n",1),
],"OCT12 elite vegas and practice")
# ---------- 33 (Mon Oct 12): two false flags on the Dispatch
# (1) Sleeper "STALE" fired because Sleeper's file only changes when Sleeper changes its numbers (it stops after games);
#     the age now comes from the feed job's last successful check (proj/status.json), not the file's name.
# (2) the "Gotham vs Yahoo - check role/news" note compared a FINAL score to projections once a game was over; played men skip it.
patch(f"{R}/dksys/meter/meter_data.py",[
 ("        if age > 6: sources[key]['status'] = 'STALE'; alarms.append(f'{key}: STALE - GitHub job file is {age} h old (limit 6 h; the job runs every 2 h)')\n",
  "        try:   # Oct 12: the job's last good check counts, not the file name (the file only changes when Sleeper does)\n"
  "            _js = json.load(open(FEEDS + 'proj/status.json')); _ok = str(_js['sources'][{'sleeper_skill':'sleeper','sleeper_kdef':'sleeper_kdef'}[key]].get(f'wk{WEEK}','')); _m = re.match(r'(\\d{4}-\\d{2}-\\d{2})T(\\d{4})Z', _js['run_utc'])\n"
  "            if _m and not _ok.startswith('FAILED'):\n"
  "                age = round((NOW - dt.datetime.strptime(_m.group(1)+_m.group(2), '%Y-%m-%d%H%M').replace(tzinfo=dt.timezone.utc).astimezone(PT)).total_seconds() / 3600, 1)\n"
  "                sources[key]['note'] = f\"GitHub job checked {age} h ago ({_ok})\"\n"
  "        except Exception: pass\n"
  "        if age > 6: sources[key]['status'] = 'STALE'; alarms.append(f'{key}: STALE - GitHub job last checked {age} h ago (limit 6 h; the job runs every 2 h)')\n",1),
 ("            if p['gotham'] is not None and p['sleeper'] is not None and p['yahoo'] is not None and p['pos'] not in ('K','DEF'):\n",
  "            if p['gotham'] is not None and p['sleeper'] is not None and p['yahoo'] is not None and p['pos'] not in ('K','DEF') and p.get('actual') is None:   # Oct 12: a played man's Gotham number is his final score\n",1),
],"OCT12 meter false flags")
# ---------- 34 (Dom, Mon Oct 12): the Scout knows what is true NOW
# (1) The Scout's week is read from the schedule (first week with a game still to play), never typed in - it was fixed at 5.
# (2) News that says a man will miss time (ESPN injuries, RotoWire, PFT/Rotoballer: "may miss some time", "multiple weeks",
#     "week-to-week", "miss N weeks") written AFTER his last game keeps him out: 2 games for open-ended wording, N when a number
#     is given, counted from the week after his last game. Montgomery (groin, Wk 5) and Shipley (plantar fascia) were being
#     planned as healthy from Week 6.
# (3) ROSTER MOVES lead the Scout page: a man out 2+ weeks goes to an open IR slot (best player first), with Yahoo's rule
#     stated (IR only once Yahoo lists him Out); when no IR slot is left he is named a drop candidate - Dom's call, never an order.
# (4) A Questionable man whose game this week is already over gets no "if he sits" box, and the front page / Field Report
#     stop saying "check before kickoff" about him.
patch(f"{R}/dksys/scout/scout_engine.py",[
 ("NOW,LAST=5,17; PLAYOFF={15,16,17}\n",
  "try:   # Oct 12 (Dom): the week comes from the schedule, never typed in\n"
  "    _gm=pd.read_csv(L+'/games.csv',low_memory=False); _gm=_gm[(_gm.season==2026)&(_gm.game_type=='REG')]; NOW=int(_gm[_gm.result.isna()].week.min())\n"
  "except Exception: NOW=5\n"
  "LAST=17; PLAYOFF={15,16,17}\n",1),
 ("def back(p,ytag=\"\"):\n",
  "_NEWSRE=re.compile(r\"week-to-week|week to week|(?:could|may|will|expected to) miss (?:some |significant |extended )?time|miss some time|multiple weeks|several weeks|(?:miss|sidelined|out)(?: for)?(?: about| roughly| at least| the next)? (?:\\w+|\\d+)(?:-to-| to |-)?(?:\\w+|\\d+)? weeks\",re.I)\n"
  "_NUMW={\"one\":1,\"two\":2,\"three\":3,\"four\":4,\"five\":5,\"six\":6,\"seven\":7,\"eight\":8,\"a\":1,\"couple\":2}\n"
  "def _nweeks(t):\n"
  "    m=re.search(r\"(?:miss|sidelined|out)(?: for)?(?: about| roughly| at least| the next)? (\\w+|\\d+)(?:-to-| to |-)?(?:\\w+|\\d+)? weeks\",t,re.I)\n"
  "    if m and \"multiple\" not in m.group(1).lower() and \"several\" not in m.group(1).lower():\n"
  "        w=m.group(1).lower(); return int(w) if w.isdigit() else _NUMW.get(w,2)\n"
  "    return 2\n"
  "NEWSOUT={}\n"
  "try:   # Oct 12 (Dom): news that he will miss time keeps him out - only news written after his last game counts\n"
  "    _FD='/home/claude/domfantasy01/dk-feeds/feeds/'; _IT=[]\n"
  "    try:\n"
  "        for _x in json.load(open(_FD+'espn_injuries.json')).get('players',[]): _IT.append((_x.get('name',''),_x.get('detail',''),_x.get('date',''),'ESPN'))\n"
  "    except Exception: pass\n"
  "    for _fn,_src in (('rotowire_history.jsonl','RotoWire'),('news_extra_history.jsonl','news')):\n"
  "        try:\n"
  "            for _l in open(_FD+_fn):\n"
  "                try: _j=json.loads(_l)\n"
  "                except Exception: continue\n"
  "                _t=str(_j.get('title') or ''); _ts=_j.get('published_utc') or _j.get('first_seen_utc') or ''\n"
  "                if _t.count(',')>=2: continue                                 # a list article names many men - not news about one\n"
  "                _IT.append((_t.split(':')[0] if _src=='RotoWire' else _t,_t+' '+re.sub(r'<[^>]+>',' ',str(_j.get('text') or '')),_ts,_j.get('source',_src)))\n"
  "        except Exception: pass\n"
  "    _GD={}\n"
  "    for _r in _gm.itertuples(): _GD[(tm(_r.home_team),int(_r.week))]=str(_r.gameday); _GD[(tm(_r.away_team),int(_r.week))]=str(_r.gameday)\n"
  "    _NAMES={norm(p['name']):p for p in PL.values() if p.get('pos') in ('QB','RB','WR','TE')}\n"
  "    for _nm,_tx,_ts,_src in _IT:\n"
  "        if not _ts or not _NEWSRE.search(_tx): continue\n"
  "        _when=dt.datetime.fromisoformat(str(_ts).replace('Z','+00:00')) if 'T' in str(_ts) else None\n"
  "        if _when is None or _when.tzinfo is None or (NOWPT-_when).days>10: continue\n"
  "        for _k,_p in _NAMES.items():\n"
  "            if not _p['name'] or _p['name'] not in _nm: continue\n"
  "            _gday=_GD.get((_p['team'],int(_p['last'])),'')\n"
  "            if _gday and _when.strftime('%Y-%m-%d')<_gday: continue           # written before his last game - he has played since\n"
  "            _n=_nweeks(_tx); _ph=_NEWSRE.search(_tx).group(0)\n"
  "            if _k not in NEWSOUT or _n>NEWSOUT[_k][0]: NEWSOUT[_k]=(_n,f'{_src}: \"{_ph}\" ({_when.astimezone(NOWPT.tzinfo).strftime(\"%b %d\")})')\n"
  "except Exception as _e: print('Scout news check skipped:',_e)\n"
  "def _newsback(p):\n"
  "    n=NEWSOUT.get(norm(p['name']))\n"
  "    return int(p['last'])+1+n[0] if n else 0\n"
  "def back(p,ytag=\"\"):\n",1),
 ("    if ytag==\"O\" or p.get(\"rep\") in (\"Out\",\"Doubtful\"): return NOW+1\n    return NOW\n",
  "    if ytag==\"O\" or p.get(\"rep\") in (\"Out\",\"Doubtful\"): return max(NOW+1,_newsback(p))\n    return max(NOW,_newsback(p))   # Oct 12: news that he will miss time\n",1),
 ("    if _m[\"slot\"] in (\"BN\",\"IR\") or _m[\"ytag\"] not in (\"Q\",\"D\"): continue\n",
  "    if _m[\"slot\"] in (\"BN\",\"IR\") or _m[\"ytag\"] not in (\"Q\",\"D\"): continue\n"
  "    if int(PL[_m[\"key\"]][\"last\"])>=NOW: continue      # Oct 12: his game this week is already over\n",1),
 ("json.dump(BOARD,open(f\"{H}/scout_board_{LGK}.json\",\"w\"),indent=1)\n",
  "BOARD[\"moves\"]=[]\n"
  "try:   # Oct 12 (Dom): roster moves - IR first, then drop candidates - stated plainly, Dom decides\n"
  "    _irs=BOARD[\"open\"][\"ir\"]; _hurt=[]\n"
  "    for _m in MINE:\n"
  "        if _m[\"slot\"]==\"IR\" or _m[\"pos\"] in (\"K\",\"DEF\"): continue\n"
  "        _p=PL[_m[\"key\"]]; _b=back(_p,_m[\"ytag\"]); _s=max(NOW,int(_p[\"last\"])+1)\n"
  "        if _b==99 or _b-_s>=2:\n"
  "            _nw=NEWSOUT.get(norm(_p[\"name\"]))\n"
  "            _why=(_nw[1] if _nw else {\"O\":\"Yahoo lists him Out\",\"IR\":\"Yahoo lists him on IR\",\"IR-R\":\"Yahoo lists him on IR\",\"PUP-R\":\"Yahoo lists him on PUP\",\"NA\":\"Yahoo lists him not active\"}.get(_m[\"ytag\"],\"listed out\"))\n"
  "            _hurt.append((_p[\"fwd\"],_m,_p,_b,_why,_s))\n"
  "    _hurt.sort(key=lambda t:-t[0])\n"
  "    for _f,_m,_p,_b,_why,_s in _hurt:\n"
  "        _ret=\"out for the season\" if _b==99 else (f\"out Weeks {_s}-{_b-1}, back about Week {_b}\" if _b-1>_s else f\"out Week {_s}, back about Week {_b}\")\n"
  "        _bw=[w for w in range(_s,(_b if _b!=99 else _s))] ; _by=[w for w in byes.get(_p[\"team\"],[]) if _b!=99 and _s<=w<=_b]\n"
  "        while _b!=99 and _b in byes.get(_p[\"team\"],[]): _b+=1\n"
  "        _ret=\"out for the season\" if _b==99 else (f\"out Weeks {_s}-{_b-1}, back about Week {_b}\" if _b-1>_s else f\"out Week {_s}, back about Week {_b}\")\n"
  "        if _by: _ret+=f\" (Week {_by[0]} is his bye)\"\n"
  "        _elig=_m[\"ytag\"] in (\"O\",\"IR\",\"IR-R\",\"PUP-R\",\"NA\")\n"
  "        _lvl=f\"~{_f:.1f} a game when healthy\"\n"
  "        if _irs>0:\n"
  "            _irs-=1\n"
  "            _t=(f\"Move {_m['name']} ({_p['team']} {_m['pos']}) to IR - {_why}; {_ret}; {_lvl}. \"+(\"Yahoo already allows it.\" if _elig else f\"Yahoo tags him {_m['ytag'] or 'healthy'} today, and IR takes only a player Yahoo lists as Out or IR - move him the day Yahoo flips him; until then he sits on the bench.\"))\n"
  "            BOARD[\"moves\"].append(dict(kind=\"ir\",name=_m[\"name\"],text=_t))\n"
  "        else:\n"
  "            _hk={id(h[1]) for h in _hurt}; _cost=[]\n"
  "            for _j,_o in enumerate(MINE):\n"
  "                if _o[\"slot\"]!=\"BN\" or id(_o) in _hk or _o[\"pos\"] in (\"K\",\"DEF\"): continue\n"
  "                _rest=[x for i,x in enumerate(MINE) if i!=_j]; _cost.append((sum(my[x]-total(_rest,x) for x in WEEKS if x>=_s and x in my),_o))\n"
  "            _cost.sort(key=lambda t:t[0]); _alt=(f\" The cheapest other bench seat to free instead: {_cost[0][1]['name']} ({PL[_cost[0][1]['key']]['team']} {_cost[0][1]['pos']}), worth ~{_cost[0][0]:.0f} pts to the best lineup through Week {LAST}.\" if _cost else \"\")\n"
  "            _t=(f\"Drop candidate: {_m['name']} ({_p['team']} {_m['pos']}) - {_why}; {_ret}; {_lvl}. No IR slot is left\"+(\" after the move above\" if any(x['kind']=='ir' for x in BOARD['moves']) else \"\")+\", so holding him costs a roster seat while he is out.\"+_alt+\" Dom's call - never an order.\")\n"
  "            BOARD[\"moves\"].append(dict(kind=\"drop\",name=_m[\"name\"],text=_t))\n"
  "except Exception as _e: BOARD[\"moves\"]=[dict(kind=\"note\",name=\"\",text=f\"Roster-move check failed: {_e}\")]\n"
  "json.dump(BOARD,open(f\"{H}/scout_board_{LGK}.json\",\"w\"),indent=1)\n",1),
],"OCT12 scout now")
patch(f"{R}/cand/redesign/_oct10_scout.py",[
 ("    for t in _q_txt(B): b.append((t,\"#FFF6E0\",\"#C9A227\"))\n",
  "    for t in _q_txt(B): b.append((t,\"#FFF6E0\",\"#C9A227\"))\n"
  "    _mv=[('<font name=\"PopB\" color=\"#B32020\">'+('Roster Move - IR' if m['kind']=='ir' else 'Roster Move - Drop Candidate' if m['kind']=='drop' else 'Roster Moves')+'</font>  &#8212;  '+_esc(m['text']).replace(' - ',' &#8212; '),\"#FBEDEA\",\"#B32020\") for m in (B.get('moves') or [])]   # Oct 12 (Dom): moves lead the page\n"
  "    b=_mv+b\n",1),
],"OCT12 scout moves box")
patch(f"{R}/cand/global/global33.py",[
 ("    q=[_ln11(p[\"player\"])+\" (\"+p[\"status\"]+\")\" for p in me if p.get(\"status\") in (\"Q\",\"D\")]\n",
  "    q=[_ln11(p[\"player\"])+\" (\"+p[\"status\"]+\")\" for p in me if p.get(\"status\") in (\"Q\",\"D\") and p.get(\"actual\") is None]   # Oct 12: a played man needs no kickoff check\n",1),
],"OCT12 front q played")
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ("    q_=[last(r[1]) for r in S if r[1] and r[2] in (\"Q\",\"D\")]\n",
  "    q_=[last(r[1]) for r in S if r[1] and r[2] in (\"Q\",\"D\") and not any(p[\"player\"]==r[1] and p.get(\"actual\") is not None for p in L[\"starters\"][\"me\"])]   # Oct 12: played men need no kickoff check\n",1),
],"OCT12 field q played")
# ---------- 35 (Mon Oct 12): the DK IV median on the Post-Mortem
# Yahoo's matchup page shows the league median only while the week is being played (it is gone from Monday's page), so a
# Monday or Tuesday read carries none. The Post-Mortem now uses the newest read of that week that has it and says which read.
patch(f"{R}/cand/redesign/_pm_auto.py",[
 ("    D[\"median\"]=MED\n",
  "    D[\"median\"]=MED; D[\"median_at\"]=None\n"
  "    if MED is None:   # Oct 12: the newest read of this week that carries Yahoo's median\n"
  "        _mf=[]\n"
  "        for _f in _gp.glob(_YD+f\"wk{W_}/dom_matchups_*.txt\"):\n"
  "            for _l in open(_f):\n"
  "                _mm=_rp.match(r\"# DK IV league median \\(Yahoo, same read\\): (\\d+\\.\\d+)\",_l)\n"
  "                if _mm and _hdr_time(_f): _mf.append((_hdr_time(_f),float(_mm.group(1))))\n"
  "        if _mf: _t,_v=max(_mf); D[\"median\"]=_v; D[\"median_at\"]=_fmt_t(_t)\n",1),
 ("                if md is None: st+=\"  Median game: not in this read.\"\n",
  "                if md is None: st+=\"  Median game: no Yahoo read this week carried it.\"\n"
  "                elif D.get(\"median_at\"): st+=f\"  League median {md:.1f} as of the {D['median_at']} read (Yahoo stops showing it once the week ends).\"\n",1),
],"OCT12 pm median")
# ---------- 36 (Mon Oct 12): bench and IR tags on the Field Report come from the newest Yahoo read
# Monday's and Tuesday's reads save only the matchup pages, so the bench tags were Sunday's (Shipley showed Q after Yahoo moved
# him to D; Roman Wilson the same). When the Scout's roster read (every team page) is newer, its tags win.
patch(f"{R}/dksys/meter/meter_data.py",[
 ("        LEAGUE_OUT[lab]['bench'] = out\n",
  "        try:   # Oct 12: a newer Scout roster read wins for bench and IR tags\n"
  "            _n = {'DK I': 1, 'DK II': 2, 'DK III': 3, 'DK IV': 4}[lab]; _me = {'DK I': '2', 'DK II': '7', 'DK III': '2', 'DK IV': '6'}[lab]\n"
  "            _f = f'/home/claude/dksys/scout/dk{_n}_rosters_live.txt'\n"
  "            _pt = lambda s: dt.datetime.strptime(s, '%a %b %d %Y %I:%M %p') if s else None\n"
  "            _sm = re.search(r'read live (\\w{3} \\w{3} \\d{1,2} \\d{4} \\d{1,2}:\\d{2} [AP]M) PT', open(_f).readline()) if os.path.exists(_f) else None\n"
  "            _rm = re.search(r'(\\w{3} \\w{3} \\d{1,2} \\d{4} \\d{1,2}:\\d{2} [AP]M) PT', str(RJ.get('pulled_pt', '')))\n"
  "            if _sm and (not _rm or _pt(_sm.group(1)) > _pt(_rm.group(1))):\n"
  "                _tg = {norm(l.split('|')[2]): l.rstrip('\\n').split('|')[5] for l in open(_f) if l.startswith(_me + '|') and l.count('|') >= 5}\n"
  "                for o in out:\n"
  "                    if norm(o['player']) in _tg: o['status'] = _tg[norm(o['player'])]\n"
  "        except Exception as _e: notes.append(f'{lab}: bench tags from the Scout read skipped ({_e})')\n"
  "        LEAGUE_OUT[lab]['bench'] = out\n",1),
],"OCT12 bench tags fresh")
# ---------- 37 (Mon Oct 12): the v8 Field Report and masthead code, written in full on every build (one source, in this file)
open(f"{R}/cand/redesign/_mast_v8.py","w").write(r'''# THE DISPATCH MASTHEAD v8 (Dom, Mon Oct 12 2026) - the approved Field Report masthead (prototype v7) on every page:
# navy band, two mountain ranges in fixed deep colors per league (never the league's own color), the title and logo, the
# section line, the data light, four dark glass buttons with the page's own lit in white. Also prints league names
# DK1-DK4 everywhere in the process. Exec'd by _fr_v8.py (league pages) and by global/_mast33.py (the front page).
import math as _m8, random as _r8, re as _re8, os as _os8, json as _j8, glob as _g8, datetime as _d8, sys as _s8
import pandas as _p8
from zoneinfo import ZoneInfo as _Z8
from reportlab.lib.colors import HexColor as _H8, Color as _C8
from reportlab.platypus import Paragraph as _PG8
from reportlab.lib.styles import ParagraphStyle as _PS8
from reportlab.pdfbase import pdfmetrics as _pm8
from reportlab.pdfbase.ttfonts import TTFont as _TT8
import reportlab.pdfgen.textobject as _rto8
if "MTR" not in globals():   # the front page runs in its own process: read the same meter file
    _mf8=sorted(__import__('glob').glob("/home/claude/dksys/data/latest/meter/meter_wk*.json"),key=lambda p:int(p.split("_wk")[1].split(".")[0]))[-1]
    MTR=__import__('json').load(open(_mf8)); WEEKN=MTR["week"]
if "asof_state" not in globals(): exec(open("/home/claude/cand/redesign/_asof.py").read(),globals())

# ---------------------------------------------------------------- league names: DK1-DK4, everywhere on the page
_DKRX = _re8.compile(r"\bDK (IV|III|II|I)\b"); _DKN = {"I": "1", "II": "2", "III": "3", "IV": "4"}
def dkname(s): return _DKRX.sub(lambda m: "DK" + _DKN[m.group(1)], s) if isinstance(s, str) else s
if not getattr(_rto8.PDFTextObject, "_dk8", False):
    _fmt0 = _rto8.PDFTextObject._formatText
    def _fmt8(self, text): return _fmt0(self, dkname(text))
    _rto8.PDFTextObject._formatText = _fmt8; _rto8.PDFTextObject._dk8 = True

_GF8 = "/usr/share/fonts/truetype/google-fonts/"
for _n, _f in (("PopS", "Poppins-SemiBold"),):
    try: _pm8.getFont(_n)
    except Exception:
        try: _pm8.registerFont(_TT8(_n, _GF8 + _f + ".ttf"))
        except Exception: _pm8.registerFont(_TT8(_n, _GF8 + "Poppins-Bold.ttf"))
from reportlab.lib.fonts import addMapping as _am8
_am8("Pop", 0, 0, "Pop"); _am8("Pop", 1, 0, "PopB"); _am8("Pop", 0, 1, "Pop"); _am8("Pop", 1, 1, "PopB")

K8 = dict(INK=_H8("#14213D"), PAPER=_H8("#FBF7EF"), CARD=_H8("#FFFFFF"), LINE=_H8("#DDD5C5"), GR=_H8("#6B7180"), GR2=_H8("#A9ADB6"),
          GREEN=_H8("#1E9E4A"), GOLD=_H8("#E0A21B"), RED=_H8("#D63A2F"), BAND=_H8("#F6F1E7"), BAR=_H8("#EEF0F4"))
TEAMC8 = {"DK I": _H8("#2F80ED"), "DK II": _H8("#F2711C"), "DK III": _H8("#7B5CE0"), "DK IV": _H8("#2EC4B6")}   # the colors every Dispatch page wears (p12v10 + Oct 10 purple)
# the mountains are fixed decoration: deeper, punchier tones, never the league's own color (Dom, Oct 12)
_FOREST, _BURNT, _DGOLD = _H8("#1F6B43"), _H8("#C2481A"), _H8("#C98A12")
MTN8 = {None: (_DGOLD, _BURNT), "DK I": (_FOREST, _BURNT), "DK II": (_DGOLD, _FOREST), "DK III": (_FOREST, _BURNT), "DK IV": (_DGOLD, _BURNT)}
def _mx8(a, b, t): return _C8(a.red + (b.red - a.red) * t, a.green + (b.green - a.green) * t, a.blue + (b.blue - a.blue) * t)
def _al8(k, a): return _C8(k.red, k.green, k.blue, alpha=a)
def t8(x, y, s, f="Pop", sz=7, col=None, a="l"):
    c.setFont(f, sz); c.setFillColor(col or K8["INK"])
    (c.drawString if a == "l" else c.drawRightString if a == "r" else c.drawCentredString)(x, y, s)
def w8(s, f, sz): return c.stringWidth(dkname(s), f, sz)
def fit8(s, f, sz, wmax):
    while w8(s, f, sz) > wmax and len(s) > 4: s = s[:-2].rstrip(" ,;·") + "…"
    return s
def num8(v, d=1): return "—" if v is None or (isinstance(v, float) and v != v) else f"{v:.{d}f}"
def sgn8(d): return f"{'+' if d >= 0 else '−'}{abs(d):.1f}"
def sfx8(n): return "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
def ln8(nm):
    p = [w for w in str(nm).split() if w not in ("Jr.", "Sr.", "II", "III", "IV", "Jr", "Sr")]; return p[-1] if p else str(nm)
def pill8(x, y, s, fill, col=None, f="PopB", sz=5.6, pad=4, stroke=None, r=2.6):
    w = w8(s, f, sz) + 2 * pad
    c.setFillColor(fill); c.setStrokeColor(stroke or fill); c.setLineWidth(.7)
    c.roundRect(x, y - 2.4, w, sz + 4.2, r, stroke=1 if stroke else 0, fill=1); t8(x + pad, y, s, f, sz, col or K8["CARD"]); return w
_PT8 = _Z8("America/Los_Angeles"); _ET8 = _Z8("America/New_York")
_MON8 = {1: "Jan.", 2: "Feb.", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "Aug.", 9: "Sept.", 10: "Oct.", 11: "Nov.", 12: "Dec."}
def _pt_txt8(s):
    """'Mon Oct 12 09:07 AM PT' -> 'Mon Oct. 12, 9:07 AM PT'"""
    m = _re8.search(r"(\w{3}) (\w{3}) (\d{1,2})\D+?(\d{1,2}):(\d{2}) ([AP]M)", str(s or ""))
    if not m: return str(s or "")
    mo = _d8.datetime.strptime(m.group(2), "%b").month
    return f"{m.group(1)} {_MON8[mo]} {int(m.group(3))}, {int(m.group(4))}:{m.group(5)} {m.group(6)} PT"

# ================================================================ THE MASTHEAD (every page)
def _ridge8(x0, x1, y0, bumps, jit, seed, sc):
    rr = _r8.Random(seed); pts = []; x = x0
    while x <= x1:
        t = (x - x0) / (x1 - x0)
        h = sum(a_ * _m8.exp(-((t - m_) / w_) ** 2) for a_, m_, w_ in bumps) * sc + jit * (rr.random() - .5)
        pts.append((x, y0 + max(0, h))); x += 3.2
    return pts
def _area8(pts, x0, x1, y0, fill, edge, lw):
    p = c.beginPath(); p.moveTo(x0, y0 - 1)
    for q in pts: p.lineTo(*q)
    p.lineTo(x1, y0 - 1); p.close(); c.setFillColor(fill); c.drawPath(p, stroke=0, fill=1)
    e = c.beginPath(); e.moveTo(*pts[0])
    for q in pts[1:]: e.lineTo(*q)
    c.setStrokeColor(edge); c.setLineWidth(lw); c.drawPath(e, stroke=1, fill=0)
MH8_TOP = Ht - 8; MH8_BOT = Ht - 84
def _sect8(section):
    s = dkname(section.replace("  ", " ")); lg = None
    m = _re8.search(r"\bDK ?([1-4])\b", s)
    if m: lg = {"1": "DK I", "2": "DK II", "3": "DK III", "4": "DK IV"}[m.group(1)]
    parts = [p.strip() for p in s.split("·") if p.strip() and not _re8.fullmatch(r"DK ?[1-4]|FANTASY FOOTBALL", p.strip())]
    words = " · ".join(p.title().replace("Post-Mortem", "Post-Mortem").replace("The Marks", "The Marks") for p in parts)
    up = s.upper(); lit = None
    for i, k in enumerate(("OVERVIEW", "CALL", "FIELD REPORT", "POSITIONS")):
        if up.startswith(k): lit = i
    if lit is None and (up.startswith("SCOUT") or "POST-MORTEM" in up): lit = 2
    return words, lg, lit
def masthead(c_, section, sub=""):
    """the v7 masthead: navy, two mountain ranges, title and logo, section line, the data light, four glass buttons"""
    global c
    c = c_
    words, lg, lit = _sect8(section)
    c.setFillColor(K8["PAPER"]); c.rect(0, 0, W, Ht, stroke=0, fill=1)
    x0b, x1b, yb, hb = M, W - M, MH8_BOT, MH8_TOP - MH8_BOT
    c.saveState(); p = c.beginPath(); p.roundRect(x0b, yb, x1b - x0b, hb, 9); c.clipPath(p, stroke=0, fill=0)
    c.setFillColor(K8["INK"]); c.rect(x0b, yb, x1b - x0b, hb, stroke=0, fill=1)
    rs = _r8.Random(11)
    for i in range(34):
        sx, sy = x0b + 160 + rs.random() * (x1b - x0b - 180), yb + hb * .62 + rs.random() * hb * .36
        c.setFillColor(_C8(1, 1, 1, alpha=.2 + .5 * rs.random())); c.circle(sx, sy, .4 + .5 * rs.random(), stroke=0, fill=1)
    back, front = MTN8.get(lg, MTN8[None]); mx0, mx1 = x0b + 196, x1b + 4; sc = hb / 80
    r2 = _ridge8(mx0, mx1, yb, ((16, .20, .09), (14, .48, .10), (48, .78, .10), (40, .98, .06)), 4, 5, sc)
    r1 = _ridge8(mx0, mx1, yb, ((20, .08, .08), (26, .33, .10), (10, .55, .08), (62, .84, .08), (30, .99, .05)), 5, 7, sc)
    _area8(r2, mx0, mx1, yb, _al8(back, .80), _mx8(back, K8["CARD"], .30), 1)
    _area8(r1, mx0, mx1, yb, _al8(front, .92), _mx8(front, K8["CARD"], .38), 1.3)
    for pts in (r1, r2):
        pk = max(pts, key=lambda q: q[1]); c.setFillColor(K8["CARD"]); c.circle(pk[0], pk[1], 1.7, stroke=0, fill=1)
    c.restoreState()
    t8(x0b + 14, yb + 45, "DARK KNIGHT DISPATCH", "Bebas", 32, K8["CARD"])
    if "dk_icon" not in globals(): exec(open("/home/claude/cand/redesign/_dkicon.py").read(), globals())
    dk_icon(c, x0b + 14 + c.stringWidth("DARK KNIGHT DISPATCH", "Bebas", 32) + 8, yb + 42.5, 27)
    sx = x0b + 14; t8(sx, yb + 23, words or "Dispatch", "Bebas", 18, K8["CARD"]); sx += w8(words or "Dispatch", "Bebas", 18) + 7
    if lg:
        tc = TEAMC8[lg]; c.setFillColor(tc); c.circle(sx + 2, yb + 29, 2.2, stroke=0, fill=1); sx += 10
        t8(sx, yb + 23, dkname(lg), "Bebas", 18, tc); sx += w8(dkname(lg), "Bebas", 18) + 10
    bx0 = x1b - 8 - 2 * 84 - 6
    sub2 = _re8.sub(r"\s*·?\s*As of [^·]*", "", sub or "").strip(" ·")   # the data light carries the time
    if WEEKN and not sub2.startswith("Week"): sub2 = f"Week {WEEKN}" + (f"  ·  {sub2}" if sub2 else "")
    t8(sx, yb + 24.5, fit8(sub2, "PopM", 6.8, bx0 - sx - 8), "PopM", 6.8, _H8("#C9CFDB"))
    # the data light: three lamps, the lit one is how fresh the oldest source is; the time is Yahoo's read
    try: _, light, _, _ = asof_state()
    except Exception: light = "amber"
    lx, ly = x0b + 14, yb + 8
    for i, (k, col) in enumerate((("red", K8["RED"]), ("amber", K8["GOLD"]), ("green", K8["GREEN"]))):
        c.setFillColor(col if k == light else _C8(1, 1, 1, alpha=.18)); c.circle(lx + 4 + i * 11, ly + 2.4, 3.5, stroke=0, fill=1)
    yr = MTR["sources"].get("yahoo_matchups", {}).get("pulled_pt")
    t8(lx + 36, ly, "Data  ·  " + (_pt_txt8(yr) if yr else "no Yahoo read"), "PopM", 6.6, K8["CARD"])
    for nm, i, j, k in (("Overview", 0, 1, 0), ("Calls", 1, 1, 1), ("Field", 0, 0, 2), ("Positions", 1, 0, 3)):
        tx, ty = bx0 + i * 90, yb + 9 + j * 30; on = (k == lit)
        c.setFillColor(_C8(.04, .06, .12, alpha=.70) if not on else _C8(.10, .12, .20, alpha=.74))
        c.setStrokeColor(_C8(1, 1, 1, alpha=1 if on else .5)); c.setLineWidth(1.8 if on else .8)
        c.roundRect(tx, ty, 84, 24, 6, stroke=1, fill=1)
        t8(tx + 42, ty + 8, nm.upper(), "Bebas", 13, K8["CARD"], "c")
    c.setFillColor(TEAMC8[lg] if lg else _H8("#F7B32B")); c.rect(x0b, yb - 5, x1b - x0b, 2.2, stroke=0, fill=1)

''')
open(f"{R}/cand/redesign/_fr_v8.py","w").write(r'''# THE FIELD REPORT v8 (Dom, Mon Oct 12 2026) - the approved DK1 prototype (v7) rolled out to all four leagues.
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
                         spre=pr.get("sleeper") if pr.get("sleeper") is not None else p.get("sleeper"),
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
                 spre=p.get("sleeper"), gpre=None if kd or e is None or _p8.isna(e.eng_wk) else ((PRE.get(f"{lab}|me|{k}") or {}).get("gotham") if bool(getattr(e, "played_wk", False)) else float(e.eng_wk)),
                 nxt=None if kd or e is None or _p8.isna(e.eng_fwd) else float(e.eng_fwd), av=None if kd else avg8(lab, p["player"], w),
                 vs=vs8(p["team"], w), bye=bye8(p["team"]))
        (irs if p["slot"] == "IR" else bench).append(d)
    named = [r for r in rows if r["name"]]
    me_sc = sum(r["score"] or 0 for r in rows); op_sc = sum(r["opsc"] or 0 for r in rows)
    started = any(r["score"] is not None for r in rows) or any(r["opsc"] is not None for r in rows)
    settled = started and all(r["final"] or r["name"] is None for r in rows) and all(r["opfinal"] or r["opn"] == "—" for r in rows)
    D = dict(lab=lab, L=L, w=w, rows=rows, bench=bench, irs=irs, me_sc=me_sc, op_sc=op_sc, started=started, settled=settled,
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
    if D["settled"]: state, fill = "FINAL", K8["GREEN"]
    elif D["started"]: state, fill = "LIVE", K8["GOLD"]
    else: state, fill = f"WEEK {D['w']}", deep
    _card8(x, gw, "Scorecard", state, fill, tc)
    y = top - 50
    if D["started"]:
        word = D["result"] or ("LEADING" if me > op else "TRAILING" if me < op else "TIED")
        col = (K8["GREEN"] if word in ("WON", "LEADING") else K8["RED"] if word in ("LOST", "TRAILING") else K8["GOLD"])
        bsz = 56 if D["result"] else 40
        t8(x + 14, y - 22, word, "Bebas", bsz, col); rx = x + 22 + w8(word, "Bebas", bsz)
        a, b = me, op
    else:
        ym, yo = D["tot"][0] or 0, D["tot"][1] or 0; yp = D["nd"].get("yahoo")
        word = "FAVORED" if (yp or 50) > 55 else "UNDERDOG" if (yp or 50) < 45 else "TOSS-UP"
        col = K8["GREEN"] if word == "FAVORED" else K8["RED"] if word == "UNDERDOG" else K8["GOLD"]
        t8(x + 14, y - 22, word, "Bebas", 40, col); rx = x + 22 + w8(word, "Bebas", 40)
        a, b = ym, yo
    t8(rx, y - 4, f"{a:.1f}", "Bebas", 30, K8["INK"]); w1 = w8(f"{a:.1f}", "Bebas", 30)
    t8(rx + w1 + 6, y - 4, "to", "PopM", 8, K8["GR"]); t8(rx + w1 + 20, y - 4, f"{b:.1f}", "Bebas", 30, K8["GR"])
    orr = f"{oppn}  ·  {rec8(L.get('opp_record', ''))}" + (f", {L['opp_rank']}{sfx8(L['opp_rank'])} of {L['teams']}" if L.get("opp_rank") else "")
    if w8(orr, "PopM", 6.8) > x + gw - 12 - rx: orr = f"{fit8(oppn, 'PopM', 6.8, x + gw - 12 - rx - w8('  ·  ' + rec8(L.get('opp_record', '')), 'PopM', 6.8))}  ·  {rec8(L.get('opp_record', ''))}"
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
    _gauge8(x + gw * .22, y, 15, nd.get("gotham"), "GOTHAM"); _gauge8(x + gw * .5, y, 24, nd.get("yahoo"), "YAHOO", True)
    _gauge8(x + gw * .78, y, 15, nd.get("sleeper"), "SLEEPER")
    cap = ("Win chance at the last read" if D["settled"] else "Win chance now — Yahoo center, Gotham left, Sleeper right" if D["started"]
           else "Win chance before kickoff — Yahoo center, Gotham left, Sleeper right")
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
def story8(D, moves):
    """the card's words, generated from the numbers. Returns (lead paragraph, [(label, text)])"""
    L = D["L"]; rows = [r for r in D["rows"] if r["name"]]; me, op = D["me_sc"], D["op_sc"]; lab = D["lab"]
    oppn = _tct(L["opp"]) if "_tct" in globals() else L["opp"]
    if not D["started"]:
        ym, yo = D["tot"]; nd = D["nd"]
        lead = (f"Yahoo has {lab} at {num8(ym)} against {num8(yo)} for {oppn} ({rec8(L.get('opp_record', ''))}"
                + (f", {L['opp_rank']}{sfx8(L['opp_rank'])}" if L.get("opp_rank") else "") + f"). Win chance: Yahoo {num8(nd.get('yahoo'), 0)}%, "
                f"Gotham {num8(nd.get('gotham'), 0)}%, Sleeper {num8(nd.get('sleeper'), 0)}%.")
        vals = [v for v in (nd.get("yahoo"), nd.get("gotham"), nd.get("sleeper")) if v is not None]
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
    mv = [m_["name"] + (" to IR once Yahoo lists him Out" if m_["kind"] == "ir" else " is a drop candidate") for m_ in moves][:2]
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
def marks8(x, y, nm, MK):
    k = norm(nm); RAD, SCO, EN_ = MK; out = []
    if k in RAD: out.append(lambda xx: g_radar8(xx, y, _MCOL8.get(RAD[k].get("color"), K8["GR2"]), RAD[k].get("count", 1)))
    v = SCO.get(k) or next((v for sk, v in SCO.items() if sk and (sk.endswith(" " + k) or k.endswith(" " + sk))), None)
    if v: out.append(lambda xx: g_scout8(xx, y, _MCOL8.get(v[0], K8["GOLD"]), v[1]))
    e = EN_.get(k)
    if e is not None and str(getattr(e, "drift", "")) == "D":
        sw = getattr(e, "drift_swing", 0); out.append(lambda xx: g_drift8(xx, y, (sw if sw == sw else 0) > 0))
    t = getattr(e, "trend", None) if e is not None else None
    if t is not None and t == t and abs(t) >= .15: out.append(lambda xx: g_trend8(xx, y, t > 0))
    for f_ in out[:4]: x += f_(x) + 2

# ================================================================ THE TABLES
def _cols8():
    return [("PLAYER", M + 4, "l"), ("MARKERS", M + 126, "l"), ("POS", M + 180, "l"), ("TEAM", M + 198, "l"), ("SLOT", M + 220, "l"), ("VS", M + 246, "l"),
            ("BYE", M + 282, "r"), ("YAHOO", M + 308, "r"), ("SLEEPER", M + 338, "r"), ("GOTHAM", M + 366, "r"), ("SCORE", M + 396, "r"), ("NEXT 3", M + 422, "r"),
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
    for k, v in (("YAHOO", r["ypre"]), ("SLEEPER", r["spre"]), ("GOTHAM", r["gpre"])):
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
            return "Scout: IR once tagged Out" if m_["kind"] == "ir" else "Scout: drop candidate"
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
    if D["started"] or CAL_DOW not in (0, 1, 2): return D
    try: PM = _j8.load(open(_os8.path.join(_REPO8, "dispatch_out", f"meter_wk{WEEKN - 1}.json")))
    except Exception: return D
    if lab not in PM.get("leagues", {}): return D
    return league8(lab, PM)
def field_report8(c_, pg, lab):
    """draws the league's Field Report; returns the number of pages used"""
    global c
    c = c_; tc = TEAMC8[lab]
    D = league8(lab, MTR); CD = _cardweek8(lab) if not D["started"] else D
    RAD = _radar8(WEEKN).get(lab, {}); SCO, moves = _scout8(lab); MK = (RAD, SCO, eng8(lab))
    print("FIELD v8", dkname(lab), "| cards week", CD["w"], "| started", CD["started"], "settled", CD["settled"], "| me", round(CD["me_sc"], 1), "op", round(CD["op_sc"], 1),
          "| rows", len(D["rows"]), "bench", len(D["bench"]), "ir", len(D["irs"]), "| radar", len(RAD), "scout", len(SCO), "moves", len(moves))
    masthead(c, f"FIELD REPORT  ·  {lab}", "")
    gw = (W - 2 * M - 10) / 2
    scorecard8(M, gw, CD, tc)
    if CAL_DOW in (0, 1, 2) and CD["started"]:
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
''')
print("   oct12: _mast_v8.py and _fr_v8.py written")
# ---------- 37 (Mon Oct 12): THE FIELD REPORT v8 - Dom's approved DK1 design (v7) in all four leagues
# New masthead on every page (mountains in fixed deep colors per league, glass buttons), Scorecard + Post-Mortem/Outlook
# cards, the clean player table with the markers lane. The standalone Post-Mortem page retires (it lives on each Field
# Report now). The Scoreboard becomes CALIBRATION and moves up front. League names print DK1-DK4. Code: redesign/_fr_v8.py.
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ("pg=2        # page 1 is the mountains page, built by global33 and set in front at assembly\n",
  "pg=2        # page 1 is the mountains page, built by global33 and set in front at assembly\n"
  "exec(open(\"/home/claude/cand/redesign/_fr_v8.py\").read())   # Oct 12 (Dom): the v8 Field Report, the new masthead on every page, DK1-DK4\n"
  "exec(open(\"/home/claude/cand/redesign/_scoreboard_page.py\").read()); pg+=1   # Oct 12 (Dom): CALIBRATION, up front\n",1),
 ("if PM_MODE:\n","if False:   # Oct 12 (Dom): the Post-Mortem lives on each Field Report now\n",1),
 ("    field_report17(D);pg+=2\n","    pg+=field_report8(c,pg,L_)   # Oct 12: v8 - one page, two when the roster runs long\n",1),
 ("exec(open(\"/home/claude/cand/redesign/_scoreboard_page.py\").read())   # Oct 11 (Dom): THE SCOREBOARD, the final page\n","",1),
],"OCT12 field v8")
patch(f"{R}/cand/redesign/_scoreboard_page.py",[
 ("masthead(c,\"OVERVIEW  ·  THE SCOREBOARD\",\"Who called it right\")",
  "masthead(c,\"OVERVIEW  ·  CALIBRATION\",\"How each source's projections held up against what actually happened\")",1),
 ("footer(c,SB_PAGE,\"The Scoreboard\")","footer(c,SB_PAGE,\"Calibration\")",1),
],"OCT12 calibration")
patch(f"{R}/cand/_footer_pass.py",[
 ("SEC=re.compile(r\"(OVERVIEW|FIELD REPORT|SCOUT|POSITIONS|THE MARKS|POST-MORTEM|OUTLOOK)(?:\\s*·\\s*(DK I{1,3}V?|DK IV|FANTASY FOOTBALL))?\")",
  "SEC=re.compile(r\"(OVERVIEW|FIELD REPORT|SCOUT|POSITIONS|THE MARKS|POST-MORTEM|OUTLOOK|CALIBRATION)(?:[\\s·]*(DK ?[1-4]|DK I{1,3}V?|DK IV|FANTASY FOOTBALL))?\",re.I)",1),
 ("    a=m.group(1).title().replace(\"Post-Mortem\",\"Post-Mortem\"); b=m.group(2)\n",
  "    a=m.group(1).title().replace(\"Post-Mortem\",\"Post-Mortem\"); b=m.group(2)\n"
  "    if b: b=re.sub(r\"DK ?(IV|III|II|I|[1-4])\\b\",lambda q:\"DK\"+{\"I\":\"1\",\"II\":\"2\",\"III\":\"3\",\"IV\":\"4\"}.get(q.group(1),q.group(1)),b)   # Oct 12: DK1-DK4\n",1),
],"OCT12 footer dk names")
# the front page: the same v8 masthead, and the nickname strip under it retires (league names live on the blocks, DK1-DK4)
patch(f"{R}/cand/global/_mast33.py",[
 ("def draw(c,section,sub): _inset_masthead(c,section,sub)\n",
  "def draw(c,section,sub): _inset_masthead(c,section,sub)\n"
  "def draw(c,section,sub):   # Oct 12 (Dom): the v8 masthead, the same on every page\n"
  "    if \"_v8\" not in _NS: exec(open(\"/home/claude/cand/redesign/_mast_v8.py\").read(),_NS); _NS[\"_v8\"]=_NS[\"masthead\"]\n"
  "    _NS[\"_v8\"](c,section,sub)\n",1),
],"OCT12 front v8 masthead")
patch(f"{R}/cand/global/global33.py",[
 ("bx0=M; bx1=W-M; bh=24; btop=Ht-87-7","bx0=M; bx1=W-M; bh=0; btop=Ht-87-7",1),
 ("        w=txt(sx,y3,U(l),\"Bebas\",fs,LC[l]); txt(sx+w,y3,FULL[l].upper(),\"Bebas\",fs,TXT); sx+=lw(l,fs)+g\n","        pass\n",1),
],"OCT12 front no nicknames")
patch(f"{R}/cand/redesign/_outlook.py",[
 ("        txt(c,x,hy,d[\"full\"],\"PopB\",8.8,PAPER);x+=c.stringWidth(d[\"full\"],\"PopB\",8.8)+6\n","        pass   # Oct 12 (Dom): no league nicknames - the chip says DK1-DK4\n",1),
],"OCT12 outlook no nicknames")
# ---------- 38 (Mon Oct 12): Scorecard - LEADING / TRAILING / FAVORED / UNDERDOG (40 pt) sat a line low; centered on the score now (Dom)
patch(f"{R}/cand/redesign/_fr_v8.py",[
 ('t8(x + 14, y - 22, word, "Bebas", bsz, col)','t8(x + 14, y - (22 if bsz == 56 else 14), word, "Bebas", bsz, col)',1),
 ('t8(x + 14, y - 22, word, "Bebas", 40, col)','t8(x + 14, y - 14, word, "Bebas", 40, col)',1),
],"OCT12 scorecard word up")
# ---------- 39 (Mon Oct 12, Dom): league names print "DK I, DK II, DK III, DK IV" everywhere (replaces DK1-DK4 from patch 37)
patch(f"{R}/cand/redesign/_mast_v8.py",[
 ('def dkname(s): return _DKRX.sub(lambda m: "DK" + _DKN[m.group(1)], s) if isinstance(s, str) else s',
  'def dkname(s): return _re8.sub(r"\\bDK ?([1-4])\\b", lambda m: "DK " + {"1": "I", "2": "II", "3": "III", "4": "IV"}[m.group(1)], s) if isinstance(s, str) else s',1),
 ('    m = _re8.search(r"\\bDK ?([1-4])\\b", s)\n    if m: lg = {"1": "DK I", "2": "DK II", "3": "DK III", "4": "DK IV"}[m.group(1)]\n',
  '    m = _re8.search(r"\\bDK (IV|III|II|I)\\b", s)\n    if m: lg = "DK " + m.group(1)\n',1),
 ('_re8.fullmatch(r"DK ?[1-4]|FANTASY FOOTBALL", p.strip())','_re8.fullmatch(r"DK (IV|III|II|I)|FANTASY FOOTBALL", p.strip())',1),
],"OCT12 roman league names")
patch(f"{R}/cand/_footer_pass.py",[
 ('lambda q:"DK"+{"I":"1","II":"2","III":"3","IV":"4"}.get(q.group(1),q.group(1))','lambda q:"DK "+{"1":"I","2":"II","3":"III","4":"IV"}.get(q.group(1),q.group(1))',1),
],"OCT12 footer roman names")
# ---------- 40 (Mon Oct 12, Dom): the same 12 pt of air under the masthead on every page
# Measured on the 4:27 PM build: Field Report 8, Scout 10, Positions 22, Calibration 23, The Marks 22, Outlook 5, front 12.
# The masthead now shifts the rest of the page by the difference (the shift lasts until the page ends).
patch(f"{R}/cand/redesign/_mast_v8.py",[
 ('    c.setFillColor(TEAMC8[lg] if lg else _H8("#F7B32B")); c.rect(x0b, yb - 5, x1b - x0b, 2.2, stroke=0, fill=1)\n',
  '    c.setFillColor(TEAMC8[lg] if lg else _H8("#F7B32B")); c.rect(x0b, yb - 5, x1b - x0b, 2.2, stroke=0, fill=1)\n'
  '    _u = dkname(section).upper()\n'
  '    _dy = (-4 if "FIELD REPORT" in _u else -2 if _u.startswith("SCOUT") else 10 if _u.startswith("POSITIONS") else 11 if "CALIBRATION" in _u\n'
  '           else 10 if "THE MARKS" in _u else -7 if _u.startswith("OUTLOOK") else 0)\n'
  '    if _dy: c.translate(0, _dy)   # Oct 12: every page starts 12 pt under the masthead\n',1),
],"OCT12 even masthead gap")
# ---------- 41 (Mon Oct 12 night): the week rolls over only when Yahoo's first read of the new week is in
# Monday night after the last game, the NFL schedule says Week 6 but Yahoo has not been read for Week 6 yet (the Tuesday
# 7:50 AM read brings it). Gotham and the meter jumped to Week 6 with no Yahoo data, and the front page crashed
# (build #125, 8:55 PM). Now both hold the week just played until a Week-6 Yahoo matchup read exists.
patch(f"{R}/dksys/engine/gotham.py",[
 ("    return int(g[g.result.isna()].week.min())\n",
  "    w=int(g[g.result.isna()].week.min())\n"
  "    import glob as _gw   # Oct 12: hold the week until Yahoo's first read of the new one is in\n"
  "    return w if (w<=1 or _gw.glob(D+f'yahoo/wk{w}/dom_matchups_*.txt')) else w-1\n",1),
],"OCT12 week holds gotham")
patch(f"{R}/dksys/meter/meter_data.py",[
 ("WEEK = int(sys.argv[1]) if len(sys.argv) > 1 else int(G[G.result.isna()].week.min())\n",
  "WEEK = int(sys.argv[1]) if len(sys.argv) > 1 else int(G[G.result.isna()].week.min())\n"
  "if len(sys.argv) <= 1 and WEEK > 1 and not glob.glob(ROOT + f'yahoo/wk{WEEK}/dom_matchups_*.txt'): WEEK -= 1   # Oct 12: hold the week until Yahoo's first read of it\n",1),
],"OCT12 week holds meter")
# The front page's footnote stopped the whole build when stale-source notes made it run to a 5th line (also seen tonight):
# it now tightens the type a little, and past that keeps the first four lines, instead of crashing.
patch(f"{R}/cand/global/global33.py",[
 ("    foot=FOOT; FFS=4.7; FLD=6.2; FL=simpleSplit(foot,\"Pop\",FFS,W-2*M)\n    assert len(FL)<=4,len(FL)\n",
  "    foot=FOOT; FFS=4.7; FLD=6.2; FL=simpleSplit(foot,\"Pop\",FFS,W-2*M)\n"
  "    while len(FL)>4 and FFS>4.2: FFS-=.1; FL=simpleSplit(foot,\"Pop\",FFS,W-2*M)   # Oct 12: never crash on a long footnote\n"
  "    if len(FL)>4: FL=FL[:3]+[FL[3].rstrip(' .,;')+' \\u2026']\n",1),
],"OCT12 front footnote fits")
# ---------- 42 (Mon Oct 12 night, Dom's list)
# (a) The Scout's drop rule: an injured man worth more to the best lineup after he is back than the cheapest other bench seat
#     is now a HOLD ("hold him; if a seat is needed, free X instead"), not a drop candidate (Montgomery, DK III).
patch(f"{R}/dksys/scout/scout_engine.py",[
 ("            _t=(f\"Drop candidate: {_m['name']} ({_p['team']} {_m['pos']}) - {_why}; {_ret}; {_lvl}. No IR slot is left\"+(\" after the move above\" if any(x['kind']=='ir' for x in BOARD['moves']) else \"\")+\", so holding him costs a roster seat while he is out.\"+_alt+\" Dom's call - never an order.\")\n            BOARD[\"moves\"].append(dict(kind=\"drop\",name=_m[\"name\"],text=_t))\n",
  "            _hi=next(i for i,x in enumerate(MINE) if x is _m); _rh=[x for i,x in enumerate(MINE) if i!=_hi]   # Oct 12: what he is worth once back\n"
  "            _hv=sum(my[x]-total(_rh,x) for x in WEEKS if _b!=99 and x>=_b and x in my)\n"
  "            if _cost and _hv>_cost[0][0]+3:\n"
  "                _t=(f\"Hold {_m['name']} ({_p['team']} {_m['pos']}) - {_why}; {_ret}; {_lvl}. Once back he is worth ~{_hv:.0f} pts to the best lineup through Week {LAST}, more than the cheapest other bench seat, {_cost[0][1]['name']} ({PL[_cost[0][1]['key']]['team']} {_cost[0][1]['pos']}, ~{_cost[0][0]:.0f} pts). If a roster seat is needed while he is out, free that one instead. Dom's call - never an order.\")\n"
  "                BOARD[\"moves\"].append(dict(kind=\"hold\",name=_m[\"name\"],free=_cost[0][1][\"name\"],text=_t))\n"
  "            else:\n"
  "                _t=(f\"Drop candidate: {_m['name']} ({_p['team']} {_m['pos']}) - {_why}; {_ret}; {_lvl}. No IR slot is left\"+(\" after the move above\" if any(x['kind']=='ir' for x in BOARD['moves']) else \"\")+\", so holding him costs a roster seat while he is out.\"+_alt+\" Dom's call - never an order.\")\n"
  "                BOARD[\"moves\"].append(dict(kind=\"drop\",name=_m[\"name\"],text=_t))\n",1),
],"OCT12 scout hold rule")
patch(f"{R}/cand/redesign/_oct10_scout.py",[
 ("('Roster Move - IR' if m['kind']=='ir' else 'Roster Move - Drop Candidate' if m['kind']=='drop' else 'Roster Moves')",
  "('Roster Move - IR' if m['kind']=='ir' else 'Roster Move - Drop Candidate' if m['kind']=='drop' else 'Roster Move - Hold' if m['kind']=='hold' else 'Roster Moves')",1),
],"OCT12 scout hold box")
# (b) Field Report: the hold shows on the card and the bench note; the Outlook card runs Wednesday and Thursday on (Post-Mortem
#     Monday and Tuesday only); a long opponent name is shortened, never the record or rank.
patch(f"{R}/cand/redesign/_fr_v8.py",[
 ("    mv = [m_[\"name\"] + (\" to IR once Yahoo lists him Out\" if m_[\"kind\"] == \"ir\" else \" is a drop candidate\") for m_ in moves][:2]",
  "    mv = [m_[\"name\"] + (\" to IR once Yahoo lists him Out\" if m_[\"kind\"] == \"ir\" else \" - hold him\" + (f\"; free {m_['free']} if a seat is needed\" if m_.get('free') else \"\") if m_[\"kind\"] == \"hold\" else \" is a drop candidate\") for m_ in moves][:2]",1),
 ("            return \"Scout: IR once tagged Out\" if m_[\"kind\"] == \"ir\" else \"Scout: drop candidate\"",
  "            return \"Scout: IR once tagged Out\" if m_[\"kind\"] == \"ir\" else \"Scout: hold him\" if m_[\"kind\"] == \"hold\" else \"Scout: drop candidate\"",1),
 ("    if D[\"started\"] or CAL_DOW not in (0, 1, 2): return D","    if D[\"started\"] or CAL_DOW not in (0, 1): return D   # Oct 12 (Dom): Outlook from Wednesday",1),
 ("    if CAL_DOW in (0, 1, 2) and CD[\"started\"]:","    if CAL_DOW in (0, 1) and CD[\"started\"]:",1),
 ("    if w8(orr, \"PopM\", 6.8) > x + gw - 12 - rx: orr = f\"{fit8(oppn, 'PopM', 6.8, x + gw - 12 - rx - w8('  ·  ' + rec8(L.get('opp_record', '')), 'PopM', 6.8))}  ·  {rec8(L.get('opp_record', ''))}\"",
  "    _tail = orr[len(oppn):]   # Oct 12 (Dom): a long name gives way, the record and rank stay\n"
  "    if w8(orr, \"PopM\", 6.8) > x + gw - 12 - rx: orr = fit8(oppn, 'PopM', 6.8, x + gw - 12 - rx - w8(_tail, 'PopM', 6.8)) + _tail",1),
],"OCT12 field hold outlook names")
# (c) The separate Outlook page retires - each Field Report carries the Outlook card from Wednesday on.
patch(f"{R}/cand/redesign/fieldpos24.py",[
 ("elif OUTLOOK_ON:\n","elif False:   # Oct 12 (Dom): the Outlook lives on each Field Report's card now\n",1),
],"OCT12 outlook page retires")
# ---------- 43 (Tue Oct 13, the Gotham before/after test, Week 5 final): keep what won, switch off what did not
# Graded Weeks 2-5, 560 player-weeks from Dom's matchups, plus the full Week 5 slate (177 men, Sunday and Monday games):
# handoff, Vegas at half strength and the elite low-Vegas cut each helped and together cut Gotham's miss 6.93 -> 6.69 pts a man.
# The practice trim made no difference (+/-0.01) - it is switched off. The injury-exit rule stays on (a hair better).
patch(f"{R}/dksys/engine/gotham.py",[
 ("os.environ.get('DK_PRACTRIM','on')","os.environ.get('DK_PRACTRIM','off')",1),
],"OCT13 practice trim off")
patch(f"{R}/dksys/engine/engine3v.py",[
 ('    """Oct 11 (Dom): remove past games a man left hurt - under 35% of snaps when his usual (median) is 60%+; keeps at least one game"""\n',
  '    """Oct 11 (Dom): remove past games a man left hurt - under 35% of snaps when his usual (median) is 60%+; keeps at least one game"""\n'
  '    if os.environ.get("DK_INJEXIT","on")=="off": return F   # Oct 13: a switch for future before/after tests (on by default)\n',1),
],"OCT13 injury exit switch")
patch(f"{R}/cand/redesign/_scoreboard_page.py",[
 ('    txt(c,M,max(y,40),"Gotham\'s rule since Oct 11: a game a man left hurt (under 35% of snaps when he usually plays 60% or more) no longer counts against his number.","Pop",5.8,GR)',
  '    txt(c,M,max(y,48),"Gotham\'s rule since Oct 11: a game a man left hurt (under 35% of snaps when he usually plays 60% or more) no longer counts against his number.","Pop",5.8,GR)\n'
  '    txt(c,M,max(y,48)-8,"Oct 13 test (Weeks 2-5): handoff, half-strength Vegas and the elite low-Vegas cut kept, Gotham 6.93 to 6.69 pts a man; the practice trim is off.","Pop",5.8,GR)',1),
],"OCT13 scoreboard footnote")
# Patch 40's page shift lifted Calibration's own old footer above the footer band; the footer pass draws the real one.
patch(f"{R}/cand/redesign/_scoreboard_page.py",[
 ('footer(c,SB_PAGE,"Calibration")','pass   # Oct 13: the footer pass draws this page\'s footer',1),
],"OCT13 calibration no double footer")
