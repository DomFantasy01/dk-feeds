def _foursrc_panel(yy):
    # THE FOUR SOURCES — Call Sheet panel. For every man named in a call: what FantasyPros, CBS, ESPN and Yahoo
    # each said, the blend (their plain average), and — once his game is final — what he actually scored.
    # One shared points scale down the whole panel. Grey ticks = the four sources, navy dot = the blend,
    # orange tick = ACTUAL (same meaning as the Radar). Range line turns gold when the sources part by 3 or more.
    FS_ORG=H("#F7801E");FS_ADK=H("#C25E0E");FS_CRM=H("#FBF7EF")
    # RETRO COLOR (Dom Mon Sep 28): each source owns one color, used ONLY for that source — header, underline bar, tick, CLOSEST.
    # Picked to clear every league color, the orange actual, the gold split line and the green/red status colors.
    FSC=(H("#E84A7F"),H("#8C3B5E"),H("#6A5BB0"),H("#3E5A7A"))   # Dom: stay close to the existing palette — sunset pink (SUN) · berry (pink deepened) · dusk violet · twilight slate (navy lifted)
    FS_LGC={1:H("#2F80ED"),2:H("#F2711C"),3:H("#12A150"),4:H("#2EC4B6")}
    def fs_ball(x,y,r,fill):
        """glossy ball — same finish as the Positions standard, here in navy for the blend"""
        c.saveState();c.setFillColor(fill);c.setStrokeColor(FS_CRM);c.setLineWidth(.7);c.circle(x,y,r,stroke=1,fill=1)
        c.setFillColor(H("#FFFFFF"));c.setFillAlpha(.55);c.circle(x-r*.33,y+r*.33,r*.32,stroke=0,fill=1);c.restoreState()
    FS_ROWS=[  # (league, call heading, [(name, pos, team)])  — same order as the calls above
     (1,"Warren or Monangai at RB",[("Jaylen Warren","RB","PIT"),("Kyle Monangai","RB","CHI")]),
     (4,"Robinson in, McLaurin or Conner out",[("Brian Robinson Jr.","RB","ATL"),("Terry McLaurin","WR","WAS"),("James Conner","RB","ARI")]),
     (2,"Kelce over Andrews at TE",[("Travis Kelce","TE","KC"),("Mark Andrews","TE","BAL")]),
     (2,"Brissett over Rodgers at QB",[("Jacoby Brissett","QB","ARI"),("Aaron Rodgers","QB","PIT")]),
     (4,"Doubs over Flowers",[("Romeo Doubs","WR","NE"),("Zay Flowers","WR","BAL")]),
     (1,"Etienne starts",[("Travis Etienne Jr.","RB","NO")]),
    ]
    _RN={1:"I",2:"II",3:"III",4:"IV"};FSS=("FP","CBS","ESPN","YAHOO")   # CLOSEST uses the column heads, so the eye goes straight up
    y=yy-22;section(c,y,"THE FOUR SOURCES","What each source said for the men in these calls — and what they scored",None)
    horizon(c,W-M,y+1.5,"SOURCES READ SEP 23–26 · ACTUALS THROUGH SUN SEP 27",align="r")
    # columns
    NX=BX;SC=[M+196,M+232,M+262,M+292];BLX=M+326;S0,S1=M+346,M+462;AXX=M+500;CLX=W-M-4
    FMX=35.0;SX=lambda v:S0+max(0,min(v,FMX))/FMX*(S1-S0)
    hy=y-22
    hdr(c,NX,hy,"PLAYER");hdr(c,NX+110,hy,"POS  TEAM")
    for x,t,col in zip(SC,("FP","CBS","ESPN","YAHOO"),FSC):
        txt(c,x,hy,t,"PopB",5.4,col,"r");c.setFillColor(col);c.roundRect(x-18,hy-4.2,18,2.0,1.0,stroke=0,fill=1)
    hdr(c,BLX,hy,"BLEND","r");hdr(c,S0,hy+8,"POINTS — ONE SCALE, EVERY ROW")
    for v in range(0,int(FMX)+1,5): hdr(c,SX(v),hy,f"{v}","c")
    hdr(c,AXX,hy,"ACTUAL","r");hdr(c,CLX,hy,"CLOSEST","r")
    ry=hy-15;tally={s:0 for s in FSS};bvy=[0,0];spl=0
    for gi,(k,head,men) in enumerate(FS_ROWS):
        gh=12+len(men)*15+3
        c.saveState();c.setFillColor(FS_LGC[k]);c.setFillAlpha(.08);c.rect(M,ry-gh+11,W-2*M,gh,stroke=0,fill=1)
        c.setFillAlpha(1);c.rect(M,ry-gh+11,2.6,gh,stroke=0,fill=1);c.restoreState()
        x=NX+lgchip(c,NX,ry,_RN[k])+7;txt(c,x,ry,head,"PopB",7.0,INKN)
        ry-=13
        for (n,pos,tm) in men:
            r=fsrow(k,n,tm);v=r["v"];g=[q for q in v if q is not None]
            txt(c,NX+8,ry,n,"PopB",7.4,INKN);txt(c,NX+110,ry,pos,"Pop",6.6,GR);txt(c,NX+128,ry,tm,"Pop",6.6,GR)
            for x,q in zip(SC,v): txt(c,x,ry,"—" if q is None else f"{q:.1f}","PopM" if q is not None else "Pop",7.0,INKN if q is not None else GR2,"r")
            txt(c,BLX,ry-.6,"—" if r["bl"] is None else f"{r['bl']:.1f}","Bebas",11.5,INKN if r["bl"] is not None else GR2,"r")
            # the strip: frame, sources, blend, actual
            my=ry+2.2
            c.setFillColor(H("#FFFFFF"));c.setStrokeColor(LINE);c.setLineWidth(.5);c.roundRect(S0-3,my-4.6,S1-S0+6,9.2,4.6,stroke=1,fill=1)
            c.saveState();c.setStrokeColor(LINE);c.setLineWidth(.4);c.setStrokeAlpha(.75)
            for gv in range(5,int(FMX),5): c.line(SX(gv),my-3.2,SX(gv),my+3.2)
            c.restoreState()
            if len(g)>=2:
                sp=max(g)-min(g);wide=sp>=3;spl+=wide
                c.setStrokeColor(ST["gold"] if wide else GR2);c.setLineWidth(2.4 if wide else 1.6);c.setLineCap(1)
                c.line(SX(min(g)),my,SX(max(g)),my);c.setLineCap(0)
            c.setLineWidth(1.3);c.setLineCap(1)
            for q,col in zip(v,FSC):
                if q is not None: c.setStrokeColor(col);c.line(SX(q),my-4.3,SX(q),my+4.3)
            c.setLineCap(0)
            a=r["act"]
            if a is not None:                       # soft glow, then the tick — it sits above the track
                c.saveState();c.setFillColor(FS_ORG)
                for rr,al in ((5.2,.10),(3.6,.16)): c.setFillAlpha(al);c.roundRect(SX(a)-rr/2-.6,my-6.2-rr*.25,rr+1.2,12.4+rr*.5,rr/2,stroke=0,fill=1)
                c.restoreState()
                c.setStrokeColor(FS_ORG);c.setLineWidth(2.0);c.setLineCap(1);c.line(SX(a),my-5.6,SX(a),my+5.6);c.setLineCap(0)
                if a>FMX: txt(c,S1+2,my-1.6,"›","PopB",7,FS_ADK)
                txt(c,AXX,ry,f"{a:.1f}","PopB",7.4,FS_ADK,"r")
                if a>FMX: pass
                if g:
                    d=[abs(q-a) if q is not None else 99 for q in v];best=min(d)
                    who=[FSS[i] for i in range(4) if d[i]==best]
                    for w_ in who: tally[w_]+=1
                    xx=CLX
                    for i_,w_ in enumerate(reversed(who)):
                        if i_: t_=" · ";txt(c,xx,ry,t_,"PopM",6.6,GR,"r");xx-=c.stringWidth(t_,"PopM",6.6)
                        txt(c,xx,ry,w_,"PopB",6.6,FSC[FSS.index(w_)],"r");xx-=c.stringWidth(w_,"PopB",6.6)
                    if r["bl"] is not None and v[3] is not None:
                        bvy[0 if abs(r["bl"]-a)<abs(v[3]-a) else 1]+=1
                else: txt(c,CLX,ry,"no source","Pop",6.6,GR2,"r")
            else:
                txt(c,AXX,ry,"MON" if r["mnf"] else "—","PopM" if r["mnf"] else "Pop",6.6,GR if r["mnf"] else GR2,"r")
                txt(c,CLX,ry,"—","Pop",6.6,GR2,"r")
            if r["bl"] is not None: fs_ball(SX(r["bl"]),my,2.3,INKN)
            ry-=15
        ry-=5
    # the read, then the legend
    ny=ry-4
    lead=max(tally.values());tops=[s for s in FSS if tally[s]==lead]
    nfin=sum(bvy)
    note(c,BX+10,ny,"Read",f"Closest most often: {' and '.join(tops)}, {lead} of {nfin}. The blend beat Yahoo alone {bvy[0]} of {nfin}. Gold lines: {spl} men the sources split on.")
    note(c,BX+10,ny-10,"Blend","The plain average of whichever of the four projected him — none weighted above another yet.")
    note(c,BX+10,ny-20,"Dashes","DK II bench men show no actual — DK II scores bonuses not yet read, so only Yahoo's own final is trusted there.")
    ky=ny-34;x=BX+10
    txt(c,x,ky,"Legend:","PopB",6.2,INKN);x+=c.stringWidth("Legend:  ","PopB",6.2)
    c.setLineWidth(1.3);c.setLineCap(1)
    for i_,(t_,col) in enumerate(zip(("FP","CBS","ESPN","Yahoo"),FSC)):
        c.setStrokeColor(col);c.line(x+2,ky-.6,x+2,ky+5);txt(c,x+6,ky,t_,"PopB",6.0,col);x+=12+c.stringWidth(t_,"PopB",6.0)
    c.setLineCap(0);x+=2
    fs_ball(x+3,ky+2.1,2.3,INKN);txt(c,x+9,ky,"Blend","Pop",6.0,GR);x+=16+c.stringWidth("Blend","Pop",6.0)
    c.setStrokeColor(FS_ORG);c.setLineWidth(1.8);c.line(x+2,ky-2,x+2,ky+6.2);txt(c,x+7,ky,"Actual","Pop",6.0,GR);x+=14+c.stringWidth("Actual","Pop",6.0)
    c.setStrokeColor(ST["gold"]);c.setLineWidth(2.4);c.setLineCap(1);c.line(x+2,ky+2.1,x+14,ky+2.1);c.setLineCap(0)
    t_="Sources 3+ points apart";txt(c,x+19,ky,t_,"Pop",6.0,GR);x+=26+c.stringWidth(t_,"Pop",6.0)
    c.setStrokeColor(GR2);c.setLineWidth(1.6);c.setLineCap(1);c.line(x+2,ky+2.1,x+14,ky+2.1);c.setLineCap(0);txt(c,x+19,ky,"Sources agree","Pop",6.0,GR)
    print("foursrc lowest y",ky)

_foursrc_panel(yy)
