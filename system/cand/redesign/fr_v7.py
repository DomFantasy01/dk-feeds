# ================================================================== FIELD REPORT — DK I (v6, rebuilt from fr_dk1.py)
# Exec'd inside p12v5.py, so every helper and the shared row format are the same objects the front pages use.
# Numbers: the v36d DK I record (page 7) for this week; ROS per game from ESPN season lines (same math as the Call Sheet);
# last two = Weeks 1–2 actuals. Roster as of Saturday: Kamara in, Addison out.
FP_=PG+1
SCH={}
for r in G:
    SCH.setdefault(r['away_team'],{})[int(r['week'])]=r['home_team'];SCH.setdefault(r['home_team'],{})[int(r['week'])]=r['away_team']
def bye(tm): return [w for w in range(1,19) if w not in SCH[tm]][0]
PA_={}                                              # points allowed per game, Weeks 1–2 (the only games played)
for r in G:
    if r['home_score']!='' and int(r['week'])<=2:
        PA_.setdefault(r['home_team'],[]).append(int(r['away_score']));PA_.setdefault(r['away_team'],[]).append(int(r['home_score']))
PA_={k:sum(v)/len(v) for k,v in PA_.items()}
rk=sorted(PA_,key=lambda t:-PA_[t]);SOFTD=set(rk[:11]);TOUGH=set(rk[-11:])
def rosg(nm,tm):
    tot,todate=ESPN[nm];return f"{(tot-todate)/remaining(tm,18):.1f}"


LK=1
ALIAS={"Seahawks":"Seattle","49ers":"San Francisco"}          # some actuals files key a defense by city
def actavg(nm):
    a=ACT[LK].get(nm) or ACT[LK].get(ALIAS.get(nm,""))
    if a and not any(a): a=None                           # never played = a dash, not a zero
    return f"{sum(a)/len(a):.1f}" if a else None

# ---- the one table shape: name leads; opponent pair tight and set apart; delta last
NX=M+22;TX=M+3
C3=(TX,NX,NX+88,NX+102,NX+120,NX+156,None)             # triangle · name · STA · pos · team · MARKER
SLX=NX+186;VS=NX+212;BY=NX+242;B3=NX+278;YH=NX+312;BR=NX+346;AA=NX+382
OPN=NX+402;OPP=NX+470;DL=W-M-12
exec(open("/home/claude/src/mkt/yweek_mine_wk3.py").read())
def yah(nm):
    v=YWK[LK].get(nm);return None if v is None or v==0 else v
PAIR=(OPN-8,OPP+22)                                    # the opponent pair's own lane
def slotchip(c,x,y,s):
    w=c.stringWidth("SFLX","PopB",5.8)+8
    c.setFillColor(alpha(LG["I"],.16));c.roundRect(x,y-2.6,w,9.4,2.5,stroke=0,fill=1)
    txt(c,x+w/2,y,s,"PopB",5.8,H("#1B4F9C"),"c")
def fdec(c,xd,y,v,fin=False,font="PopB",sz=7.4,col=INKN):
    """bare number on its decimal; a banked score gets a soft wash and a capital F — scoreboard style"""
    if fin and v not in (None,""):
        c.setFillColor(alpha(SUN[1],.22));c.roundRect(xd-17,y-3,34,10.5,2.5,stroke=0,fill=1)
    dec(c,xd,y,v,font,sz,col,5.4,"")
    if fin and v not in (None,""):
        b=str(v).split(".")[1] if "." in str(v) else ""
        txt(c,xd+c.stringWidth("."+b,font,sz)+1.6,y,"F","PopB",6.2,INKN)
def lhead(y,title,sub):
    section(c,y,title,sub,None)
    h=y-21;rowhead(c,C3,h)
    hdr(c,SLX,h,"SLOT");hdr(c,VS,h,"VS");hdr(c,BY,h,"BYE","c")
    for x,a,b in ((B3,"BLEND","WEEK 3"),(YH,"YAHOO","WEEK 3"),(BR,"ESPN","ROS"),(AA,"ACTUAL","AVERAGE"),(OPP,"OPPONENT","PTS")):
        hdr(c,x+9,h+6.5,a,"r");hdr(c,x+9,h,b,"r")
    hdr(c,OPN,h,"OPPONENT");hdr(c,DL+9,h,"DELTA","r")
    return h
def lanes(top,bot):
    c.setStrokeColor(LINE);c.setLineWidth(.6)
    for x in PAIR: c.line(x,bot,x,top)
RP_=14
def lrow(j,ry,sl,nm,stt,pos,tm,cl,sg,tr,bl,fin=False):
    if j%2==0: c.setFillColor(SOFT);c.rect(M,ry-4.4,W-2*M,RP_,stroke=0,fill=1)
    prow(c,C3,ry,nm,stt,pos,tm,cl,sg,tr,7.2)
    slotchip(c,SLX,ry,sl)
    if nm is None: return
    op=SCH[tm][3];tier(c,VS,ry,op,7.2)
    txt(c,BY,ry,str(bye(tm)),"PopM",7.2,SUN[0] if bye(tm)<=8 else INKN,"c")
    fdec(c,B3,ry,bl,fin)
    yv=yah(nm)
    if yv is not None:                                   # Yahoo beside the blend; bold when they part by 3 or more
        far=bl not in (None,"") and not fin and abs(float(bl)-yv)>=3
        fdec(c,YH,ry,f"{yv:.1f}",False,"PopB" if far else "PopM",7.2,INKN)
    else: fdec(c,YH,ry,None,False,"PopM",7.2)
    fdec(c,BR,ry,rosg(nm,tm) if (nm in ESPN and stt!="O") else None,False,"PopM",7.2)
    fdec(c,AA,ry,actavg(nm),False,"PopM",7.2)
def sgn(d): return ("+%.1f" % d) if d>=0 else ("%.1f" % d)


# ---- SEASON STRIP: three tables like the Field Report — STARTERS, BENCH, IR. Name block kept; from SLOT right is the season.
SX=NX+186;WK=list(range(4,18));cw=(W-M-SX)/len(WK);rh=12.5
def band_groups(men,key):
    """grey band by position group — consecutive men of the same group share one band, alternate groups skip it"""
    out=[];g=-1;prev=None
    for m in men:
        k=key(m)
        if k!=prev: g+=1;prev=k
        out.append(g%2==1)
    return out
def season_table(y,title,sub,men,key,first=False):
    section(c,y,title,sub,None)
    if first: horizon(c,W-M,y+1.5,"WEEKS 4–17",align="r")
    hy=y-23;rowhead(c,C3,hy)
    for i,w in enumerate(WK): txt(c,SX+i*cw+cw/2,hy,str(w),"PopB",6,GR if w<15 else SUN[0],"c")
    ry=hy-16;top_=ry+rh-3.5
    for bnd,(sl,nm,stt,pos,tm,cl,sg,tr) in zip(band_groups(men,key),men):
        if bnd: c.setFillColor(SOFT);c.rect(M,ry-4.2,W-2*M,rh,stroke=0,fill=1)
        prow(c,C3,ry,nm,stt,pos,tm,cl,sg,tr,6.8)
        for i,w in enumerate(WK):
            x=SX+i*cw;op=SCH[tm].get(w)
            if op is None:                                   # a bye is its own thing — outlined orange, never a color
                c.setStrokeColor(SUN[0]);c.setLineWidth(.8);c.setFillColor(PAPER)
                c.rect(x+1.1,ry-2.8,cw-2.2,rh-2.8,stroke=1,fill=1)
                txt(c,x+cw/2,ry,"BYE","PopB",5.6,SUN[0],"c");continue
            k=alpha(ST["green"],.20) if op in SOFTD else alpha(ST["red"],.18) if op in TOUGH else H("#E6E1D6")
            c.setFillColor(k);c.rect(x+.7,ry-3.2,cw-1.4,rh-2,stroke=0,fill=1)
            txt(c,x+cw/2,ry,op,"PopM",6,INKN,"c")
        ry-=rh
    fx=SX+WK.index(15)*cw;c.setStrokeColor(SUN[1]);c.setLineWidth(1.4)
    c.roundRect(fx-.5,ry+rh-4.5,3*cw+1,top_-(ry+rh-4.5)+1,3,stroke=1,fill=0)
    if first: txt(c,fx+1.5*cw,hy+9,"PLAYOFFS","PopB",5.6,H("#B8860B"),"c")
    return ry
# ------------------------------------------------------------------ ONE FIELD REPORT, FOUR LEAGUES — only the data changes
def short(n):
    if " " not in n: return n                                         # defenses keep their name
    return n.split()[0][0]+". "+" ".join(n.split()[1:]).replace(" Jr.","").replace(" III","").replace(" Sr.","")
def last(n):
    if " " not in n: return n
    parts=[w for w in n.split() if w not in ("Jr.","Sr.","III","II")];return parts[-1]
def byes_note(men):
    by={}
    for m in men:
        b=bye(m[4])
        if b<=8: by.setdefault(b,[]).append(last(m[1]))
    return "Orange = a bye in the next five weeks. "+"; ".join(f"{', '.join(v)} ({k})" for k,v in sorted(by.items()))+"."
def field_report(D):
    global LK,STARTS,BENCH,IRS,RP_
    LK=D["k"];RP_=13.0 if len(D["starts"])+len(D["bench"])+len(D["irs"])>=18 else 14;STARTS,BENCH,IRS=D["starts"],D["bench"],D["irs"];FP=D["page"];LG_=D["name"]
    # ---------------- page 1: the team, this week
    masthead(c,"FIELD REPORT  ·  "+LG_,D["sub"])
    top=Ht-110
    card(c,M,top-gh,gw,gh,L[D["card"]])                 # the SAME card as Global Watch — one record, two views
    px=M+gw+10;pw=gw;c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.6);c.roundRect(px,top-gh,pw,gh,7,stroke=1,fill=1)
    c.setFillColor(INKN);p=c.beginPath();p.roundRect(px,top-27,pw,27,7);c.drawPath(p,stroke=0,fill=1);c.rect(px,top-27,pw,10,stroke=0,fill=1)
    txt(c,px+12,top-20,"THE GAME","Bebas",20,PAPER);txt(c,px+12+c.stringWidth("THE GAME","Bebas",20)+7,top-17.5,"Where it's won and lost","PopM",6.8,H("#C9CFDB"))
    yy=top-40;horizon(c,px+12,yy,"WEEK 3","Blend, both sides at best lineup")
    yy-=18;hdr(c,px+12,yy,"BIGGEST SINGLE MATCHUPS");hdr(c,px+pw-12,yy,"ONE MAN VS ONE MAN — NOT THE TEAM SCORE","r")
    ds=[(float(r[8])-float(r[10]),r[1],r[9]) for r in STARTS if r[1]]
    hi=max(ds);lo=min(ds);sc=max(14,abs(hi[0]),abs(lo[0]))
    pairs=[(LG_,f"{last(hi[1])} over {last(hi[2])}",hi[0],LG["I"])]
    if lo[0]<0: pairs.append(("Opponent",f"{last(lo[2])} over {last(lo[1])}",lo[0],GR2))
    for i,(lab,a,d,k) in enumerate(pairs):
        ly=yy-13-i*14;txt(c,px+12,ly,lab,"PopB",6.8,INKN);txt(c,px+48,ly,a,"Pop",6.8,INKN)
        bw_=min(abs(d)/14*70,56);c.setFillColor(k);c.roundRect(px+pw-100,ly-1.5,bw_,6.5,2,stroke=0,fill=1)
        dec(c,px+pw-22,ly,sgn(d),"PopB",7,ST["green"] if d>0 else ST["red"],5.4,"")
    ny_=yy-52;NXP=px+24                                  # notes indented under the panel's text, not its edge
    for i,(a,b) in enumerate(D["panel"]): note(c,NXP,ny_-11*i,a,b,6.4)
    y=top-gh-22
    h=lhead(y,"STARTERS","Best lineup, set Friday — every slot prints, filled or not")
    ry=h-15;mine=theirs=0;t0=ry+RP_-4.4
    for j,(sl,nm,stt,pos,tm,cl,sg,tr,bl,om,ov,mf,of) in enumerate(STARTS):
        lrow(j,ry,sl,nm,stt,pos,tm,cl,sg,tr,bl,mf)
        if nm is None: ry-=RP_;continue
        txt(c,OPN,ry,om,"Pop",7,INKN);fdec(c,OPP,ry,ov,of,"PopM",7.2)
        d=float(bl)-float(ov);mine+=float(bl);theirs+=float(ov)
        dec(c,DL,ry,sgn(d),"PopB",7.2,ST["green"] if d>=0 else ST["red"],5.4,"")
        ry-=RP_
    lanes(t0,ry+RP_-4.4)
    c.setStrokeColor(INKN);c.setLineWidth(.6);c.line(M,ry+RP_-4.6,W-M,ry+RP_-4.6)
    txt(c,NX,ry+1,"BEST POSSIBLE LINEUP","PopB",6.6,INKN);dec(c,B3,ry+1,f"{mine:.1f}","PopB",8,INKN,5.4,"")
    dec(c,OPP,ry+1,f"{theirs:.1f}","PopB",8,INKN,5.4,"")
    dd=mine-theirs;dec(c,DL,ry+1,sgn(dd),"PopB",8,ST["green"] if dd>=0 else ST["red"],5.4,"")
    print(LG_,"totals",round(mine,1),round(theirs,1))
    def sub_table(y,title,sub,rows):
        h=lhead(y,title,sub);ry=h-15;t0=ry+RP_-4.4
        for j,r in enumerate(rows):
            lrow(j,ry,*r);ry-=RP_
        lanes(t0,ry+RP_-4.4);return ry
    ry=sub_table(ry-(24 if RP_==14 else 20),"BENCH","The same row — no opponent, so those columns stay open",BENCH)
    ry=sub_table(ry-10,"IR",D["irsub"],IRS)
    ny=ry-2
    note(c,NX,ny,"F",D["fnote"],6.2)
    note(c,NX,ny-10,"Bye",D.get("byenote") or byes_note(STARTS+BENCH),6.2)
    note(c,NX,ny-20,"Yahoo","Yahoo's own number for this week, printed beside the blend. Bold = the two part by 3 points or more.",6.2)
    note(c,NX,ny-30,"Trend","The zigzag in MARKER is playing time — snaps, touches, targets, Week 1 to Week 2. Not points. Green up, red down.",6.2)
    print(LG_,"FR1 lowest",ny-30)
    footer(c,FP,"Field Report · "+LG_)
    c.showPage()
    # ---------------- page 2: cuttable players, then the season
    masthead(c,"FIELD REPORT  ·  "+LG_,"Cuttable players  ·  The season ahead, Weeks 4–17")
    y=Ht-124
    h=lhead(y,"CUTTABLE PLAYERS","Who goes first if a move needs room. No triangle = no action — a triangle means it's on the Call Sheet")
    ry=h-15
    for j,(r,lab,nts) in enumerate(D["cut"]):
        lrow(0,ry,*r)
        txt(c,W-M-6,ry,lab,"PopB",6.4,GR,"r")                    # the label parks where the opponent columns sit empty
        nyy=ry-12
        for a,b in nts: note(c,NX+12,nyy,a,b,6.4);nyy-=10
        ry=nyy-6
    cols=[(h_,l_) for h_,l_ in (("BEHIND THEM",D.get("behind",[])),("NOT CUTTABLE",D["notcut"])) if l_]
    low=ry                                               # side by side: the rest of the bench, then the protected
    for ci,(head_,lst) in enumerate(cols):
        x0=NX+ci*262;yy_=ry;txt(c,x0,yy_,head_,"PopB",5.6,GR);yy_-=11
        for nm,why in lst:
            txt(c,x0,yy_,nm,"PopB",6.8,GR);txt(c,x0+74,yy_,why,"Pop",6.6,GR);yy_-=10
        low=min(low,yy_)
    ry=low-3
    note(c,NX,ry+1,"Order",D.get("order","Rest of season per game, lowest first — after taking out handcuffs and anyone added in the last two weeks."),6.4)
    # ---- SEASON STRIP: three tables like the page before — STARTERS, BENCH, IR. From SLOT right is the season.
    y=ry-27
    ry=season_table(y,"THE SEASON AHEAD  ·  STARTERS","Every man, Weeks 4–17 — the playoff weeks framed",[s[:8] for s in STARTS],lambda m:m[0],True)
    ry=season_table(ry-16,"BENCH","The same row, the same season",[b[:8] for b in BENCH],lambda m:m[3])
    ry=season_table(ry-16,"IR",D["irsub"],[b[:8] for b in IRS],lambda m:m[3])
    ny=ry-2
    txt(c,NX,ny,"Color:","PopB",6.4,GR);lx=NX+4+c.stringWidth("Color:","PopB",6.4)
    t="Points the opposing defense has allowed per game."
    txt(c,lx,ny,t,"Pop",6.4,GR);lx+=c.stringWidth(t,"Pop",6.4)+14
    for k,lab,t in ((alpha(ST["green"],.20),"Soft:","Allows the most."),(alpha(ST["red"],.18),"Tough:","Allows the fewest.")):
        c.setFillColor(k);c.rect(lx,ny-1,9,6,stroke=0,fill=1);lx+=13
        txt(c,lx,ny,lab,"PopB",6.4,GR);lx+=c.stringWidth(lab,"PopB",6.4)+4
        txt(c,lx,ny,t,"Pop",6.4,GR);lx+=c.stringWidth(t,"Pop",6.4)+14
    c.setStrokeColor(SUN[0]);c.setLineWidth(.8);c.setFillColor(PAPER);c.rect(lx,ny-1.5,14,7,stroke=1,fill=1)
    txt(c,lx+7,ny,"BYE","PopB",4.4,SUN[0],"c");txt(c,lx+18,ny,"No game.","Pop",6.4,GR)
    note(c,NX,ny-12,"Early","Two games in — colors recalculate every week. Trend mark in MARKER = usage direction, Weeks 1–2.",6.4)
    print(LG_,"FR2 lowest",ny-12)
    footer(c,FP+1,"Field Report · "+LG_)
    c.showPage()
def rosg(nm,tm):
    tot,todate=ESPN[nm];return f"{(tot-todate)/remaining(tm,18):.1f}"
FP0=PG+1
# ================================================================== DK I (the approved build — data unchanged but for Etienne's team, NO)
exec(open("/home/claude/cand/redesign/_fr_dk1rows.py").read())
MG,DG,WG=rosg("Kyle Monangai","CHI"),rosg("Stefon Diggs","WAS"),rosg("Dontayvion Wicks","PHI")
DK1=dict(k=1,card=0,name="DK I",page=FP0,starts=STARTS,bench=BENCH,irs=IRS,irsub="One slot in this league",
  sub="TheMostImportantThingInLife  ·  vs Kraft Beer & TDs  ·  Roster as of Saturday",
  panel=[("Team","163 to 143 — totals in the table below."),("Wire","No free agent beats a starter anywhere."),
         ("Watch","Warren is questionable — Call Sheet 1."),("Byes","Kelce's Week 5 bye — Byes Ahead."),
         ("Cuttable","Three men listed — next page."),("Radar","Warren and Etienne carry news."),("Next","Week 4 is DIKFORE — 2–0, division lead.")],
  fnote="A banked score — Thursday's London and their four Packers. Delta runs on finals where they exist, the blend where they don't.",
  cut=[(BENCH[0],"FIRST OUT",[("Why red",f"Lowest rest of season of the men not protected — {MG} a game."),
                              ("Hold","Not this week. He's Warren's cover until Sunday's inactives settle it.")]),
       (BENCH[1],"NEXT IN LINE",[("Why gold",f"{DG} a game. Third receiver here — starts only on a bye or an injury."),
                                 ("For him","21.7 in Week 2 — the reason he isn't first.")]),
       (BENCH[2],"MARKED",[("Why grey",f"{WG} a game — lower than Diggs on paper, but added Wednesday."),
                           ("Protected","Cutting a player just added is the mistake this list is built to stop.")])],
  notcut=[("Kaelon Black","Handcuff to McCaffrey — a role no projection sees."),
          ("Alvin Kamara","Claimed Saturday — not cut inside two weeks."),
          ("Jayden Daniels","On IR — costs no bench spot.")])

# ================================================================== DK II — Winners and Sinners vs Rated PG-18 (v36d page 13)
#        slot   name                  sta  pos   team  clus  radar            tri   blend   opponent        opp   mineF theirsF
S2=[("QB","Jacoby Brissett","","QB","ARI",None,None,None,"18.1","J. Herbert","20.5",0,0),
    ("RB","David Montgomery","","RB","HOU",None,None,None,"15.9","J. Gibbs","29.4",0,0),
    ("RB","Travis Etienne Jr.","","RB","NO",None,("good","01"),None,"14.5","A. Jeanty","21.1",0,0),
    ("WR","Ja'Marr Chase","","WR","CIN",None,None,None,"18.2","G. Pickens","15.1",0,0),
    ("WR","Drake London","","WR","ATL",None,None,None,"30.4","C. Tate","10.6",1,0),
    ("WR","Courtland Sutton","","WR","DEN",None,None,None,"10.4","J. Meyers","9.2",0,0),
    ("TE","Travis Kelce","","TE","KC",None,None,None,"12.6","D. Schultz","11.3",0,0),
    ("FLX","De'Von Achane","","RB","MIA",None,None,None,"21.8","C. Hubbard","18.3",0,0),
    ("SFLX","Sam Darnold","","QB","SEA",None,None,None,"18.3","C. Loveland","9.3",0,0),
    ("K","Harrison Mevis","","K","LA",None,None,None,"8.0","K. Fairbairn","8.6",0,0),
    ("DEF","49ers","","DEF","SF",None,None,None,"6.9","Texans","6.2",0,0)]
B2=[("BN","Jameis Winston","","QB","NYG",None,None,None,"17.7"),
    ("BN","Mark Andrews","","TE","BAL","gold",None,None,"11.3"),
    ("BN","MarShawn Lloyd","","RB","GB","red",None,None,"10.6"),
    ("BN","Aaron Rodgers","","QB","PIT","grey",None,None,"17.4"),
    ("BN","Alvin Kamara","","RB","NO",None,None,None,"9.6")]
I2=[("IR","Jayden Daniels","O","QB","WAS",None,None,None,None)]
DK2=dict(k=2,card=1,name="DK II",page=FP0+4,starts=S2,bench=B2,irs=I2,irsub="One slot in this league",
  sub="Winners and Sinners  ·  vs Rated PG-18  ·  Roster as of Friday",
  panel=[("Team","175 to 160 — totals in the table below."),("Wire","No free agent beats a starter anywhere."),
         ("Watch","Darnold cleared Friday — he starts at superflex."),("Byes","Kelce's Week 5 bye — Andrews covers."),
         ("Cuttable","Three men listed — next page."),("Radar","Etienne carries news — off the injury report."),
         ("Next","Week 4 is RAIDER FAN — 1–1, 7th.")],
  fnote="A banked score — Thursday's London. Nobody on their side played Thursday. Delta runs on finals where they exist, the blend where they don't.",
  cut=[(B2[2],"FIRST OUT",[("Why red",f"Lowest rest of season of the men not protected — {rosg('MarShawn Lloyd','GB')} a game."),
                           ("Against him","Usage fell in Week 2 — the trend mark is red.")]),
       (B2[1],"NEXT IN LINE",[("Why gold",f"{rosg('Mark Andrews','BAL')} a game."),
                              ("Hold","Not before Week 5 — he covers Kelce's bye.")]),
       (B2[3],"MARKED",[("Why grey",f"{rosg('Aaron Rodgers','PIT')} a game — third quarterback, behind Brissett and Winston."),
                        ("For him","Superflex league — a third quarterback earns his keep in bye weeks.")])],
  behind=[("Jameis Winston",f"{rosg('Jameis Winston','NYG')} a game — Darnold's cover at superflex.")],
  notcut=[("Alvin Kamara","Handcuff to Etienne, and added Wednesday."),
          ("Jayden Daniels","On IR — costs no bench spot.")])

# ================================================================== DK III — Hers and His Version 2.0 vs Dawg Pound Eric (v36d page 19). No kicker slot.
S3=[("QB","Tyler Shough","","QB","NO",None,None,None,"22.9","M. Stafford","19.6",0,0),
    ("RB","De'Von Achane","","RB","MIA",None,None,None,"21.8","C. McCaffrey","24.2",0,0),
    ("RB","David Montgomery","","RB","HOU",None,None,None,"15.9","T. Henderson","13.1",0,0),
    ("WR","George Pickens","","WR","DAL",None,None,None,"15.0","C. Olave","17.9",0,0),
    ("WR","Jaylen Waddle","","WR","DEN",None,None,None,"13.3","C. Sutton","10.4",0,0),
    ("TE","Harold Fannin Jr.","","TE","CLE",None,None,None,"10.1","C. Loveland","9.3",0,0),
    ("FLX","Josh Downs","","WR","IND",None,None,None,"11.7","B. Corum","11.3",0,0),
    ("FLX","Devaughn Vele","","WR","NO",None,None,None,"10.6","Z. Flowers","16.5",0,0),
    ("DEF","Chiefs","","DEF","KC",None,None,None,"9.6","Vikings","8.3",0,0)]
B3_=[("BN","Rachaad White","","RB","WAS","gold",None,None,"9.9"),
     ("BN","Michael Pittman Jr.","Q","WR","PIT","grey",None,None,"10.6"),
     ("BN","Aaron Rodgers","","QB","PIT",None,None,None,"17.4"),
     ("BN","T.J. Hockenson","","TE","MIN",None,None,None,"8.7"),
     ("BN","Steelers","","DEF","PIT","red",None,None,"7.9")]
I3=[("IR","Jayden Daniels","O","QB","WAS",None,None,None,None)]
DK3=dict(k=3,card=2,name="DK III",page=FP0+8,starts=S3,bench=B3_,irs=I3,irsub="One slot in this league",
  sub="Hers and His Version 2.0  ·  vs Dawg Pound Eric  ·  Roster as of Friday",
  panel=[("Team","131 to 131 — a coin flip."),("Wire","No free agent beats a starter anywhere."),
         ("Watch","Pittman is questionable — Vele plays for certain."),("Byes","Chiefs D in Week 5 — the Steelers cover."),
         ("Cuttable","Three men listed — next page."),("Radar","Nothing on this roster carries news."),
         ("Next","Week 4 is Benchdad's Beach — 1–1, 5th.")],
  fnote="No final scores here — nobody on either side played Thursday. Every number is the blend.",
  cut=[(B3_[4],"FIRST OUT",[("Why red",f"Lowest rest of season on the bench — {rosg('Steelers','PIT')} a game."),
                            ("Hold","Not before Week 5 — they cover the Chiefs' bye.")]),
       (B3_[0],"NEXT IN LINE",[("Why gold",f"{rosg('Rachaad White','WAS')} a game."),
                               ("For him","16.1 in Week 2 — usage climbing.")]),
       (B3_[1],"MARKED",[("Why grey",f"{rosg('Michael Pittman Jr.','PIT')} a game — questionable with a foot injury."),
                         ("Against him","Nothing in Week 2 — usage falling.")])],
  behind=[("Aaron Rodgers",f"{rosg('Aaron Rodgers','PIT')} a game — only backup QB; Shough's Week 8 bye.")],
  notcut=[("T.J. Hockenson","Added Wednesday — not cut inside two weeks."),
          ("Jayden Daniels","On IR — costs no bench spot.")])

# ================================================================== DK IV — Murrieta NextDoor vs Bad and Boujee (v36d page 25)
S4=[("QB","Jared Goff","","QB","DET",None,None,None,"22.5","L. Jackson","25.1",0,0),
    ("RB","Bijan Robinson","","RB","ATL",None,None,None,"35.3","S. Barkley","15.4",1,0),
    ("RB","D'Andre Swift","","RB","CHI",None,None,None,"13.3","B. Hall","15.6",0,0),
    ("WR","Justin Jefferson","","WR","MIN",None,None,None,"16.8","C. Lamb","18.4",0,0),
    ("WR","Josh Downs","","WR","IND",None,None,None,"11.7","L. Burden","10.6",0,0),
    ("WR","Romeo Doubs","","WR","NE",None,None,None,"10.8","J. Williams","11.6",0,0),
    ("TE","Tucker Kraft","","TE","GB",None,None,None,"6.6","S. LaPorta","12.0",1,0),
    ("FLX","Travis Kelce","","TE","KC",None,None,None,"12.6","T. Pollard","10.8",0,0),
    ("SFLX","Dak Prescott","","QB","DAL",None,None,None,"22.6","T. Lawrence","21.5",0,0),
    ("K","Tyler Loop","","K","BAL",None,None,None,"8.5","B. Aubrey","8.8",0,0),
    ("DEF","Seahawks","","DEF","SEA",None,None,None,"7.9","Texans","6.2",0,0)]
B4=[("BN","Zay Flowers","Q","WR","BAL",None,None,None,"16.4"),
    ("BN","C.J. Stroud","","QB","HOU",None,None,None,"19.3"),
    ("BN","Terry McLaurin","","WR","WAS","red",None,("gold","2"),"10.9"),
    ("BN","Khalil Shakir","","WR","BUF","grey",None,None,"10.3"),
    ("BN","RJ Harvey","","RB","DEN",None,None,None,"9.7")]
I4=[("IR","James Conner","IR","RB","ARI","gold",None,("gold","2"),None),
    ("IR","Isiah Pacheco","IR","RB","DET",None,None,None,None),
    ("IR","Tank Dell","IR","WR","HOU",None,None,None,None)]
DK4=dict(k=4,card=3,name="DK IV",page=FP0+12,starts=S4,bench=B4,irs=I4,irsub="Three slots in this league — all full",
  sub="Murrieta NextDoor  ·  vs Bad and Boujee  ·  Roster as of Friday",
  panel=[("Team","169 to 156 — totals in the table below."),("Wire","No free agent beats a starter anywhere."),
         ("Watch","Flowers sits, Doubs starts — confirmed."),("Byes","Kelce's Week 5 bye — Byes Ahead."),
         ("Cuttable","McLaurin or Conner — Call Sheet 2."),("Radar","Nothing on this roster carries news."),
         ("Next","Week 4 is Team Other — 4–0, 2nd.")],
  fnote="A banked score — Thursday's Robinson and Kraft. Nobody on their side played Thursday. Delta runs on finals where they exist, the blend where they don't.",
  order="Call Sheet 2 sets the first two. After that, rest of season per game, lowest first — handcuffs and new adds taken out.",
  cut=[(B4[2],"FIRST OUT",[("Why red","Call Sheet 2 names him the drop for the Robinson claim — Mariota at quarterback."),
                           ("Order",f"{rosg('Terry McLaurin','WAS')} a game is higher than Shakir or Harvey — this is the Call Sheet's call, not the numbers.")]),
       (I4[0],"NEXT IN LINE",[("Why gold","The Call Sheet's other choice — no ESPN season line."),
                              ("Check","He's on IR, so dropping him frees no bench spot. Re-tested Sunday.")]),
       (B4[3],"MARKED",[("Why grey",f"{rosg('Khalil Shakir','BUF')} a game — lowest of the rest."),
                        ("Hold","Not before Week 5 — he's Kelce's cover at flex.")])],
  behind=[("RJ Harvey",f"{rosg('RJ Harvey','DEN')} a game — nothing in Week 2; usage falling."),
          ("C.J. Stroud",f"{rosg('C.J. Stroud','HOU')} a game — Goff's Week 6 bye at superflex."),
          ("Zay Flowers",f"{rosg('Zay Flowers','BAL')} a game — sits until he practices fully.")],
  notcut=[("Isiah Pacheco","On IR — back surgery; December return."),
          ("Tank Dell","On IR — December return.")])

exec(open("/home/claude/cand/redesign/_fr_charts.py").read())
exec(open("/home/claude/cand/redesign/_fr_positions.py").read())
exec(open("/home/claude/cand/redesign/_fr_radar.py").read())
for D in (DK1,DK2,DK3,DK4): field_report(D); league_page(D); position_page(D)
