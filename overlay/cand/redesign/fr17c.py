# FIELD REPORT v17 — Week 4. Rebuilt from fr_v7.py's field_report(): same card, panel, three tables, season strip.
# Changes: live Friday rosters; Week-4 numbers; ENGINE NEXT 3 replaces ESPN ROS; actual averages Weeks 1–4;
# defense colors off Weeks 1–4 (was frozen at Weeks 1–2); trend mark off the engine's workload direction;
# the cut list is held (not printed) until it's set with Dom.
exec(open("/home/claude/cand/redesign/fr17bdata.py").read())
# ---- defense softness off every game played so far (fixes the frozen Weeks 1–2 rating)
PA_={}
for r in G:
    if r['home_score']!='' and int(r['week'])<=4:
        PA_.setdefault(r['home_team'],[]).append(int(r['away_score']));PA_.setdefault(r['away_team'],[]).append(int(r['home_score']))
PA_={k:sum(v)/len(v) for k,v in PA_.items()}
rk=sorted(PA_,key=lambda t:-PA_[t]);SOFTD=set(rk[:11]);TOUGH=set(rk[-11:])
WK17=4
def footer(c,n,label):
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,20,W-M,20)
    txt(c,M,11,"DARK KNIGHT FANTASY FOOTBALL","PopB",6.4,INKN)
    txt(c,M+c.stringWidth("DARK KNIGHT FANTASY FOOTBALL","PopB",6.4)+8,11,"Week 4  ·  Field Report  ·  "+built_str(),"Pop",5.8,GR)
    txt(c,W-M,11,label+"  ·  page "+str(n),"Pop",5.8,GR,"r")
def lhead(y,title,sub):
    section(c,y,title,sub,None)
    h=y-21;rowhead(c,C3,h)
    hdr(c,SLX,h,"SLOT");hdr(c,VS,h,"VS");hdr(c,BY,h,"BYE","c")
    for x,a,b in ((B3,"BLEND","WEEK 4"),(YH,"YAHOO","WEEK 4"),(BR,"ENGINE","NEXT 3"),(AA,"ACTUAL","AVERAGE"),(OPP,"OPPONENT","PTS")):
        hdr(c,x+9,h+6.5,a,"r");hdr(c,x+9,h,b,"r")
    hdr(c,OPN,h,"OPPONENT");hdr(c,DL+9,h,"DELTA","r")
    return h
def lrow(j,ry,sl,nm,stt,pos,tm,cl,sg,tr,bl,fin=False):
    if j%2==0: c.setFillColor(SOFT);c.rect(M,ry-4.4,W-2*M,RP_,stroke=0,fill=1)
    prow(c,C3,ry,nm,stt,pos,tm,cl,_signal(nm) if nm else None,tr,7.2)
    slotchip(c,SLX,ry,sl)
    if nm is None: return
    op=SCH[tm].get(WK17)
    if op: tier(c,VS,ry,op,7.2)
    else: txt(c,VS,ry,"BYE","PopB",6.2,SUN[0])
    txt(c,BY,ry,str(bye(tm)),"PopM",7.2,SUN[0] if bye(tm)<=8 else INKN,"c")
    fdec(c,B3,ry,bl,fin)
    yv=yah17(nm,LAB17) if stt not in ("O","IR") else None
    if yv is not None and not fin:
        far=bl not in (None,"") and abs(float(bl)-yv)>=3
        fdec(c,YH,ry,f"{yv:.1f}",False,"PopB" if far else "PopM",7.2,INKN)
    else: fdec(c,YH,ry,None,False,"PopM",7.2)
    fdec(c,BR,ry,fwd17(nm,LAB17) if stt not in ("O","IR") else None,False,"PopM",7.2)
    fdec(c,AA,ry,actavg17(nm,LAB17),False,"PopM",7.2)
_gsrc=open("/home/claude/cand/redesign/p12v9.py").read()
_gi=_gsrc.index("def gauge(");_gj=_gsrc.index("\nRECW=None",_gi)
exec(_gsrc[_gi:_gj].replace('f"Dashed = {last}% before kickoff"','f"Dashed = {last}% on Friday"'))   # v17b: last = Friday's read
GH17=216                                   # v17c: cards 12pt taller - the room comes from the Trend note, which the legend already carries
def card17(c,x,y,w,h,d):
    """v17c: same content, re-spaced - every block gets its own air; nothing said twice."""
    col=LG[d["k"]];T=y+h
    c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.6);c.roundRect(x,y,w,h,7,stroke=1,fill=1)
    c.setFillColor(col);p=c.beginPath();p.roundRect(x,T-27,w,27,7);c.drawPath(p,stroke=0,fill=1);c.rect(x,T-27,w,10,stroke=0,fill=1)
    txt(c,x+12,T-20,"DK "+d["k"],"Bebas",20,PAPER);txt(c,x+12+c.stringWidth("DK "+d["k"],"Bebas",20)+7,T-17.5,d["team"],"PopM",6.8,PAPER)
    pill(c,x+w-10,T-17,STW[d["st"]],STB[d["st"]],PAPER,6.2,"PopB",5,"r")
    # ---- THIS WEEK: gauge left, opponent and projection right
    horizon(c,x+12,T-42,"THIS WEEK","Win chance — Yahoo, read Sat morning")
    gauge(c,x+54,T-84,30,d["win"],d["last"],col,False,d["me"]>d["opp"])
    rx=x+114
    hdr(c,rx,T-56,"OPPONENT");txt(c,rx,T-66,d["oppn"],"PopB",8.2);txt(c,rx,T-75,d["oppr"],"Pop",6.6,GR)
    hdr(c,rx,T-89,"PROJECTED — BEST LINEUPS")
    mx=max(d["me"],d["opp"]);bw=w-(rx-x)-44
    for i,(lab,v,k) in enumerate((("DK "+d["k"],d["me"],col),("OPP",d["opp"],GR2))):
        yy=T-100-i*11;hdr(c,rx,yy,lab);c.setFillColor(k);c.roundRect(rx+24,yy-1.5,bw*v/mx*.86,6.5,2,stroke=0,fill=1)
        txt(c,rx+24+bw*v/mx*.86+4,yy,f"{v:.1f}","PopB",7.2,INKN)
    gap=d["me"]-d["opp"]
    txt(c,rx,T-123,("Ahead by %.1f" % gap) if gap>0 else ("Behind by %.1f" % -gap),"PopM",6.6,ST["green"] if gap>0 else ST["red"])
    # ---- SEASON: record chip, place and distance to the line on one row, points under it
    sy=T-134;horizon(c,x+12,sy,"SEASON",d["shead"],gap=9)
    RECW=c.stringWidth("0–0","Bebas",22)+14
    c.setFillColor(SOFT);c.roundRect(x+12,sy-29,RECW,20,4,stroke=0,fill=1)
    txt(c,x+12+RECW/2,sy-25,d["rec"],"Bebas",22,INKN,"c")
    tx2=x+12+RECW+9;suf={1:"st",2:"nd",3:"rd"}.get(d["place"],"th")
    a=f"{d['place']}{suf} of {d['of']}";txt(c,tx2,sy-17,a,"PopB",8)
    ln=d["line"];inn=ln.startswith("In");ln=ln.split("— ",1)[-1]
    txt(c,tx2+c.stringWidth(a,"PopB",8)+6,sy-17,ln,"PopM",6.6,ST["green"] if inn else GR)
    txt(c,tx2,sy-26.5,d["pts"],"Pop",6.4,GR)
    n=d["of"];sx=x+12;sw=w-24;cw=sw/n;yy=sy-42
    for i in range(n):
        c.setFillColor(col if i+1==d["place"] else alpha(col,.16));c.rect(sx+i*cw+.6,yy,cw-1.2,8.5,stroke=0,fill=1)
        if i+1==d["place"]: txt(c,sx+i*cw+cw/2,yy+2,str(d["place"]),"PopB",5.6,PAPER,"c")
    c.setStrokeColor(SUN[1]);c.setLineWidth(1.8);c.line(sx+6*cw,yy-3,sx+6*cw,yy+11.5)
    txt(c,sx+6*cw,yy-9.5,"Playoff line","PopM",5.6,H("#B8860B"),"c")
    # ---- the verdict: what to do, not a repeat of the gauge
    vy=y+6;c.setFillColor(alpha(ST[d["st"]],.12));c.roundRect(x+8,vy,w-16,20,5,stroke=0,fill=1)
    c.setFillColor(ST[d["st"]]);c.roundRect(x+8,vy,3.5,20,1.5,stroke=0,fill=1)
    txt(c,x+18,vy+11.5,d["verdict"],"PopB",7.1,INKN);txt(c,x+18,vy+3.6,d["when"],"Pop",6.3,GR)
def field_report17(D):
    global LK,STARTS,BENCH,IRS,RP_,LAB17,TREND,SX,WK,cw,rh,STMODE
    STMODE="week"
    LAB17=D["name"];STARTS,BENCH,IRS=D["starts"],D["bench"],D["irs"];LG_=D["name"];FP=D["page"]
    _CL=clu17(LG_,_E10.run(LG_)[0])            # v17b: the drop cluster prints on the bench rows - the cut order itself
    BENCH=[r[:5]+(_CL.get(r[1]),)+r[6:] for r in BENCH]
    _n=len(STARTS)+len(BENCH)+len(IRS);RP_=12.2 if _n>=20 else 13.0 if _n>=18 else 14
    TREND={r[1]:dir17(r[1],LG_) for r in STARTS+BENCH+IRS if r[1] and dir17(r[1],LG_)}
    masthead(c,"FIELD REPORT  ·  "+LG_,D["sub"])
    top=Ht-110
    gh=GH17;card17(c,M,top-gh,gw,gh,D["cardd"])
    stamp(c,M+gw-4,top+5,["yahoo"])                 # the league card: Yahoo standings, win chance, projections
    px=M+gw+10;pw=gw;c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.6);c.roundRect(px,top-gh,pw,gh,7,stroke=1,fill=1)
    c.setFillColor(INKN);p=c.beginPath();p.roundRect(px,top-27,pw,27,7);c.drawPath(p,stroke=0,fill=1);c.rect(px,top-27,pw,10,stroke=0,fill=1)
    txt(c,px+12,top-20,"THE GAME","Bebas",20,PAPER);txt(c,px+12+c.stringWidth("THE GAME","Bebas",20)+7,top-17.5,"Where it's won and lost","PopM",6.8,H("#C9CFDB"))
    yy=top-42;horizon(c,px+12,yy,"WEEK 4","Blend, both sides at best lineup")
    stamp(c,px+pw-4,top+5,["market","news"])        # THE GAME: blend matchups, injury notes
    yy=top-62;hdr(c,px+12,yy,"BIGGEST ONE-ON-ONE MATCHUPS")
    ds=[(float(r[8])-float(r[10]),r[1],r[9]) for r in STARTS if r[1] and r[8] and r[10]]
    hi=max(ds);lo=min(ds)
    pairs=[("DK "+D["k"],f"{last(hi[1])} over {last(hi[2])}",hi[0],LG[D['k']])]
    if lo[0]<0: pairs.append(("Opponent",f"{last(lo[2])} over {last(lo[1])}",lo[0],GR2))
    for i,(lab,a,d,k) in enumerate(pairs):
        ly=yy-16-i*16;txt(c,px+12,ly,lab,"PopB",6.8,INKN);txt(c,px+62,ly,a,"Pop",6.8,INKN)
        bw_=min(abs(d)/14*70,56);c.setFillColor(k);c.roundRect(px+pw-98,ly-1.5,bw_,6.5,2,stroke=0,fill=1)
        dec(c,px+pw-22,ly,sgn(d),"PopB",7,ST["green"] if d>0 else ST["red"],5.4,"")
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(px+12,top-112,px+pw-12,top-112)
    ny_=top-128;NXP=px+16
    for i,(a,b) in enumerate(D["panel"]): note(c,NXP,ny_-16*i,a,b,6.4)
    y=top-gh-22
    h=lhead(y,"STARTERS","Every slot prints, filled or not")
    ry=h-15;mine=theirs=0;t0=ry+RP_-4.4
    for j,(sl,nm,stt,pos,tm,cl,sg,tr,bl,om,ov,mf,of) in enumerate(STARTS):
        lrow(j,ry,sl,nm,stt,pos,tm,cl,sg,tr,bl,mf)
        if nm is None: ry-=RP_;continue
        txt(c,OPN,ry,om,"Pop",7,INKN);fdec(c,OPP,ry,ov,of,"PopM",7.2)
        if bl and ov:
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
        for j,r in enumerate(rows): lrow(j,ry,*r);ry-=RP_
        lanes(t0,ry+RP_-4.4);return ry
    ry=sub_table(ry-(24 if RP_==14 else 20),"BENCH","The same row — no opponent, so those columns stay open",BENCH)
    ry=sub_table(ry-10,"IR",D["irsub"],IRS)
    ny=ry-2
    _ns=10 if ny-40>=29 else max(7.2,(ny-29)/4.0)   # Oct 11: all five notes fit above the footer
    note(c,NX,ny,"Final",D["fnote"],6.2)
    note(c,NX,ny-_ns,"Opponent","Their best lineup off the Saturday-night roster read (Sat Oct 3).",6.2);ny-=_ns
    note(c,NX,ny-_ns,"Bye",byes_note(STARTS+BENCH),6.2)
    note(c,NX,ny-2*_ns,"Numbers","Blend = Yahoo, Rotowire, CBS and ESPN, all read Sat Oct 3 night — Yahoo beside it, bold when they part by 3. Next 3 = points a game, his next three.",6.2)
    note(c,NX,ny-3*_ns,"Weather",WX_NOTE,6.2)   # Oct 11 (Dom): the game weather
    print(LG_,"FR1 lowest",ny-30)                # v17c: the Trend note moved out - the legend explains the zigzag
    footer(c,FP,"Field Report · "+LG_)
    c.showPage()
    # ---------------- page 2: the season ahead (the cut list is held until it's set with Dom)
    masthead(c,"FIELD REPORT  ·  "+LG_,"The season ahead, Weeks 4–17")
    SX=NX+186;WK=list(range(4,18));cw=(W-M-SX)/len(WK);rh=12.5
    y=Ht-124
    STMODE="season"
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
    note(c,NX,ny-12,"Games","Colors run off every game played so far — Weeks 1–3, plus Thursday's Pittsburgh–Cleveland — and recalculate every week.",6.4)
    print(LG_,"FR2 lowest",ny-12)
    footer(c,FP+1,"Field Report · "+LG_)
    c.showPage()

# OCT10d fr final

# OCT11 fr weather
