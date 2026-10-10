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
