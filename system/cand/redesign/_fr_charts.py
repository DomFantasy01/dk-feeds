# ================================================================== THE LEAGUE — race + market, one page per league (v7 charts)
# Standings, divisions and every team's Weeks 3–14 schedule read live from Yahoo, Sat Sep 26 evening.
# Schedule strength = average points per week of the opponents still to play (Weeks 3–14), ranked within the league.
# Workload = nflverse snap share + carries/targets, Week 1 to Week 2 (the two complete weeks) — same score as Role Watch.
import re as _re
exec(open("/home/claude/src/market/sweep_wk3_fri.py").read())
import pandas as _pd
# (name, W, L, PF, division, schedule-strength raw)   ours = "Dark Knight …"
RACE={
1:[("DIKFORE",2,0,303.79,"Marriage",142.68),("Coin Toss Mike",1,1,284.84,"Marriage",140.90),("Dark Knight I",0,2,231.78,"Marriage",144.00),
   ("Raider nation",0,2,230.58,"Marriage",145.42),("JD",2,0,300.13,"Is a",141.65),("Rolling With Romo",2,0,292.43,"Is a",143.63),
   ("Remember the Tutens",1,1,349.41,"Is a",140.39),("Kraft Beer & TDs",0,2,252.07,"Is a",142.31),("Punching Bag",2,0,371.81,"Scam",139.00),
   ("World Of Pain",1,1,282.98,"Scam",145.93),("RoadDogg",1,1,272.08,"Scam",147.31),("Mr. Rodgers' Neighborhood",0,2,263.89,"Scam",144.67)],
2:[("F—ing Cowboys",2,0,353.64,"Division 1",154.52),("Daejon Love Special",1,1,294.92,"Division 1",155.80),("Dark Knight II",1,1,260.15,"Division 1",157.64),
   ("Rated PG-18",0,2,289.91,"Division 1",155.16),("How 'Bout Them Points",2,0,345.54,"Division 2",150.89),("Diddys Booty Butter",1,1,308.35,"Division 2",158.29),
   ("RAIDER FAN",1,1,290.34,"Division 2",159.13),("Hector Football",0,2,280.40,"Division 2",157.01),("Trophy Hunter",2,0,415.13,"Division 3",153.54),
   ("RFFR",2,0,355.89,"Division 3",153.67),("Rams house",0,2,346.31,"Division 3",159.27),("Ground Game evan",0,2,213.10,"Division 3",161.92)],
3:[("Mr. Bobo",2,0,276.78,"The His",127.23),("The Deer Hunter Part Deux",2,0,261.53,"The His",124.35),("Benchdad's Beach",1,1,322.98,"The His",118.46),
   ("Dawg Pound Eric",1,1,218.78,"The His",135.66),("And A Goedert To You Sir",1,1,192.69,"The His",131.29),("Maly's Better Half",0,2,263.97,"The His",128.05),
   ("Dark Knight III",0,2,235.50,"The His",129.46),("Dominique by 6",2,0,354.34,"The Hers",127.35),("Derek's Better Half",1,1,338.66,"The Hers",127.77),
   ("Rushin Roulette",1,1,310.36,"The Hers",128.22),("Beachmom's Bench",1,1,264.38,"The Hers",129.16),("Press Coverage steph",1,1,256.23,"The Hers",136.90),
   ("Mrs. Bobo",1,1,207.79,"The Hers",140.43),("Bad and Bougie 2.0",0,2,163.36,"The Hers",149.33)],
4:[("Dream Killers",4,0,351.46,"",79.75),("Team Other",4,0,333.06,"",80.87),("Killer Ko-Gees",3,1,330.32,"",79.08),("Fly Eagles Fly",2,2,353.48,"",79.40),
   ("Dark Knight IV",2,2,347.52,"",78.20),("Mr. Irrelevant",2,2,336.16,"",76.50),("Alan's Team",1,3,309.24,"",77.55),("Brad's Ballers",1,3,302.94,"",76.84),
   ("Bad and Boujee",1,3,269.62,"",80.82),("Lin's Team",0,4,228.68,"",80.88)]}
NEXT4={1:["DIKFORE","Raider nation","World Of Pain","RoadDogg"],2:["RAIDER FAN","F—ing Cowboys","RFFR","Ground Game evan"],
       3:["Benchdad's Beach","And A Goedert To You Sir","Maly's Better Half","The Deer Hunter Part Deux"],4:["Team Other","Mr. Irrelevant","Fly Eagles Fly","Brad's Ballers"]}
THIS3={1:"Kraft Beer & TDs",2:"Rated PG-18",3:"Dawg Pound Eric",4:"Bad and Boujee"}
# Playoff field, read live from each league's Yahoo settings page, Sun Sep 27: all four send 6 teams (Weeks 15-17).
# DK I and DK III award division winners the top seeds; DK II and DK IV seed on overall standings.
PLAYOFFS={1:6,2:6,3:6,4:6};DIVSEED={1:True,2:False,3:True,4:False};SPOTS=6
RN={1:"I",2:"II",3:"III",4:"IV"}
def _ord(n): return f"{n}{'th' if 10<=n%100<=20 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')}"
def _place(rows):                                    # Yahoo's order: wins, then points for
    return sorted(rows,key=lambda r:(-r[1]/(r[1]+r[2]),-r[3]))
def _sn(n,k=18): return n if len(n)<=k else n[:k-1].rstrip()+"…"

# ---------------- workload, every RB/WR/TE, Week 1 -> Week 2
import sys as _sys; _sys.path.insert(0,"/home/claude/src/role_watch")
from rw_core import norm as _norm
_s=_pd.read_csv("/home/claude/src/role_watch/data/snap_counts_2026.csv");_s=_s[(_s.game_type=="REG")&_s.week.isin([1,2])&_s.player.notna()]
_p=_pd.read_csv("/home/claude/src/role_watch/data/stats_player_week_2026.csv",low_memory=False)
_p=_p[(_p.season_type=="REG")&_p.week.isin([1,2])&_p.player_display_name.notna()]
_s=_s.assign(key=_s.player.map(_norm));_p=_p.assign(key=_p.player_display_name.map(_norm),opps=_p.carries.fillna(0)+_p.targets.fillna(0))
WORK={}
for k_,g_ in _s.groupby("key"):
    a=g_[g_.week==1];b=g_[g_.week==2]
    if b.empty: continue
    s0=float(a.offense_pct.iloc[0]) if not a.empty else 0.0;s1=float(b.offense_pct.iloc[0])
    pp=_p[_p.key==k_];o0=float(pp[pp.week==1].opps.sum());o1=float(pp[pp.week==2].opps.sum())
    WORK[k_]=round((s1-s0)*100+2*(o1-o0),1)
def work(nm): return WORK.get(_norm(nm))
def po_soft(tm): return sum(1 for w in (15,16,17) if SCH[tm].get(w) in SOFTD)
def po_tough(tm): return sum(1 for w in (15,16,17) if SCH[tm].get(w) in TOUGH)

def _dot(x,y,r,fill,stroke=None,lw=.9):
    if fill is not None: c.setFillColor(fill)
    if stroke is not None: c.setStrokeColor(stroke);c.setLineWidth(lw)
    c.circle(x,y,r,stroke=1 if stroke is not None else 0,fill=1 if fill is not None else 0)

OBST=[]
BOUND=[0,0,0,0];DOTS=[]
def place_label(x,y,r,lab,font="Pop",sz=5.8,col=INKN):
    w=c.stringWidth(lab,font,sz);h=sz
    cands=[]
    for d in (0,5,10,15,20,26,33,40,48):
        cands+=[(x+r+2.5,y-h/2+.6+s_*d) for s_ in ((1,) if d==0 else (1,-1))]
        cands+=[(x-r-2.5-w,y-h/2+.6+s_*d) for s_ in ((1,) if d==0 else (1,-1))]
        cands+=[(x-w/2,y+r+2.2+d),(x-w/2,y-r-2.2-h-d)]
    def nearest_other(bx,by):
        cxl,cyl=bx+w/2,by+h/2;dm=(cxl-x)**2+(cyl-y)**2
        return any(((cxl-ox)**2+(cyl-oy)**2)<dm*.8 for ox,oy in DOTS if (ox,oy)!=(x,y))
    def hit(bx,by):
        if nearest_other(bx,by): return True
        if bx<BOUND[0] or bx+w>BOUND[1] or by<BOUND[2] or by+h>BOUND[3]: return True
        for (ox,oy,ow,oh) in OBST:
            if bx<ox+ow+1 and bx+w>ox-1 and by<oy+oh+1 and by+h>oy-1: return True
        return False
    for bx,by in cands:
        if not hit(bx,by): break
    else: bx,by=cands[0]
    cx_,cy_=min(max(x,bx),bx+w),min(max(y,by),by+h)          # far from its dot: a hairline leads back
    if ((cx_-x)**2+(cy_-y)**2)**.5>r+12:
        c.setStrokeColor(GR2);c.setLineWidth(.5);c.line(x,y,cx_,cy_)
    OBST.append((bx,by,w,h));txt(c,bx,by+.4,lab,font,sz,col);return bx,by
def swarm(items,rpitch):
    """items: (x,y,r,payload) -> nudge dots sharing a row apart vertically so none overlap"""
    out=[]
    for x,y,r,pl in sorted(items,key=lambda t:t[0]):
        for off in (0,1,-1,2,-2,3,-3):
            yy=y+off*rpitch
            if all((x-ox)**2+(yy-oy)**2>(r+orr+1.5)**2 for ox,oy,orr,_ in out): break
        out.append((x,yy,r,pl))
    return out
def panel_note(x,y,w,lab,s,sz=6.8,lead=9.2):
    """bold label + colon, wrapped text under it — the Field Report note voice"""
    txt(c,x,y,lab+":","PopB",sz,INKN);y-=lead
    words=s.split();line=""
    for wd in words:
        t=(line+" "+wd).strip()
        if c.stringWidth(t,"Pop",sz)>w: txt(c,x,y,line,"Pop",sz,INKN);y-=lead;line=wd
        else: line=t
    if line: txt(c,x,y,line,"Pop",sz,INKN);y-=lead
    return y-4

def league_page(D):
    """Dom Sun, playoff split: the league's playoff field halved — green = the top half of the field, gold = the
    bottom half (the playoff cut is the gold's bottom edge), plain paper = out. Bands cut by standings place (wins,
    then points), so they step. Each band is labeled where it sits; one LEGEND line under the frame."""
    k=D["k"];LC=LG[RN[k]];FP=D["page"]+2;LG_=D["name"];me="Dark Knight "+RN[k]
    rows=RACE[k];pl=_place(rows);n=len(rows)
    SP=PLAYOFFS[k];HF=(SP+1)//2
    R={r[0]:r for r in rows};place={r[0]:i+1 for i,r in enumerate(pl)}
    if DIVSEED[k]:                                    # division winners take the top seeds — say so if that ever
        lead={};[lead.setdefault(r[4],r[0]) for r in pl]   # disagrees with plain standings order
        seeds=[t for t in (r[0] for r in pl) if t in lead.values()][:SP];seeds+=[r[0] for r in pl if r[0] not in seeds][:SP-len(seeds)]
        if set(seeds[:HF])!={r[0] for r in pl[:HF]} or set(seeds)!={r[0] for r in pl[:SP]}:
            print(f"WARNING DK {RN[k]}: division seeding differs from standings order — bands drawn by standings")
    hard=sorted(rows,key=lambda r:-r[5]);hardrank={r[0]:i+1 for i,r in enumerate(hard)}
    mydiv=R[me][4]
    masthead(c,"THE LEAGUE  ·  "+LG_,LG_+" in the race for the playoffs  ·  Yahoo standings read Saturday night")
    y=Ht-122;section(c,y,"THE LEAGUE RACE","Every team — points scored against record",None)
    horizon(c,W-M,y+1.5,"AFTER "+("WEEK 2" if k<4 else "TWO WEEKS · 4 GAMES"),align="r")
    gmax=max(r[1]+r[2] for r in rows)
    x0=M;mx0,mx1=M+30,M+352;my1=y-18;my0=Ht/2+46
    L,R_,B,T=mx0-4,mx1+4,my0-2,my1+2;RH=(T-B)/(gmax+1)
    pfs=[r[3] for r in rows];st_=_tstep(.8*(max(pfs)-min(pfs)))
    xlo=_math.floor((min(pfs)-.25*st_)/st_)*st_;xhi=_math.ceil((max(pfs)+.25*st_)/st_)*st_
    XM=lambda v:mx0+(v-xlo)/(xhi-xlo)*(mx1-mx0);YR=lambda w:B+(w+.5)*RH
    c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.6);c.rect(L,B,R_-L,T-B,stroke=1,fill=1)
    def edge(w,spots):
        """left edge of the top-`spots` region in record row w (None = row not in it), cut halfway between the
        last team in and the first team out on points — i.e. by standings place"""
        above=sum(1 for r in rows if r[1]>w);need=spots-above
        if need<=0: return None
        rw=sorted((r[3] for r in rows if r[1]==w),reverse=True)
        if len(rw)<=need: return L
        return max(L,min(R_,XM((rw[need-1]+rw[need])/2)))
    DKG=H("#A8740A")
    for w in range(gmax+1):
        yb=B+w*RH;ge=edge(w,SP);gr=edge(w,HF)
        if ge is not None: c.setFillColor(alpha(GOLD,.20));c.rect(ge,yb,R_-ge,RH,stroke=0,fill=1)
        if gr is not None:
            c.setFillColor(CARD);c.rect(gr,yb,R_-gr,RH,stroke=0,fill=1)
            c.setFillColor(alpha(GREEN,.17));c.rect(gr,yb,R_-gr,RH,stroke=0,fill=1)
    for w in range(1,gmax+1):
        c.setStrokeColor(LINE);c.setLineWidth(.4);c.line(L,B+w*RH,R_,B+w*RH)
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.rect(L,B,R_-L,T-B,stroke=1,fill=0)
    def stepline(spots,col,lw):
        es=[(edge(w,spots) if edge(w,spots) is not None else R_) for w in range(gmax+1)]
        cut=min((w for w,e in enumerate(es) if e<R_),default=gmax)
        c.saveState();c.setStrokeColor(col);c.setLineWidth(lw);c.setLineCap(1);c.setLineJoin(1);p_=c.beginPath()
        p_.moveTo(R_-1,B+cut*RH)
        for w in range(cut,gmax+1):
            e=es[w];yb=B+w*RH;p_.lineTo(max(e,L+1),yb)
            if e<=L+1: break
            p_.lineTo(e,yb+RH)
        c.drawPath(p_,stroke=1,fill=0);c.restoreState()
    stepline(HF,GREEN,1.25)          # top half of the field
    stepline(SP,DKG,1.25)            # the playoff cut
    # ---- axes, real numbers
    v=xlo
    while v<=xhi+1e-9:
        if L<=XM(v)<=R_:
            txt(c,XM(v),B-8.5,_fmt(v),"PopM",5.2,GR,"c");c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(XM(v),B,XM(v),B-2)
        v+=st_
    hdr(c,(mx0+mx1)/2,B-16,"POINTS SCORED SO FAR","c")
    for w in range(gmax+1):
        txt(c,L-3,YR(w)-1.9,f"{w}–{gmax-w}","PopM",5.2,GR,"r")
    c.saveState();c.translate(x0+5,(B+T)/2);c.rotate(90);hdr(c,0,0,"RECORD — WINS UP","c");c.restoreState()
    # ---- teams placed first, so the band labels can keep clear of them
    OBST.clear();BOUND[:]=[L+1,R_-1,B+1,T-1]
    MD=swarm([(XM(r[3]),YR(r[1]),3.4,r) for r in rows],4.6)
    DOTS[:]=[(x,yy) for x,yy,_,_ in MD]
    for x,yy,r_,r in MD: OBST.append((x-r_-2,yy-r_-2,2*r_+4,2*r_+4))
    # ---- band labels, sitting in their own band
    def zone(w,x_):          # 'g' / 'y' / 'w' for a point in row w
        gr=edge(w,HF);ge=edge(w,SP)
        if gr is not None and x_>=gr: return "g"
        if ge is not None and x_>=ge: return "y"
        return "w"
    def band_label(lab,col,z,right):
        sz=5.6;wl=c.stringWidth(lab,"PopB",sz);h=sz
        rws=range(gmax,-1,-1) if z!="w" else range(0,gmax+1)
        for w in rws:
            for dy in (RH-h-3,3,(RH-h)/2):
                by=B+w*RH+dy
                xs_=[R_-4-wl-s for s in range(0,int(R_-L),6)] if right else [L+4+s for s in range(0,int(R_-L),6)]
                for bx in xs_:
                    if bx<L+3 or bx+wl>R_-3: continue
                    if not all(zone(w,xx)==z for xx in (bx-2,bx+wl+2)): continue
                    if any(bx-1<ox+ow and bx+wl+1>ox and by-1<oy+oh and by+h+1>oy for ox,oy,ow,oh in OBST): continue
                    txt(c,bx,by+.6,lab,"PopB",sz,col);OBST.append((bx-1,by-1,wl+2,h+2));return
    band_label(f"PLAYOFFS · TOP {HF}",GREEN,"g",True)
    band_label(f"PLAYOFFS · LAST {SP-HF} IN",DKG,"y",True)
    def pin_noplay(lab="NO PLAYOFFS"):
        sz=5.6;wl=c.stringWidth(lab,"PopB",sz);h=sz
        for w in range(gmax,-1,-1):
            if zone(w,L+4)!="w": continue
            if w<gmax and zone(w+1,L+4)=="w": continue       # must sit directly under a band
            for dy in (RH-h-3,(RH-h)/2,3):
                by=B+w*RH+dy
                for bx in [L+4+s_ for s_ in range(0,int(R_-L),4)]:
                    if bx+wl>R_-3 or not all(zone(w,xx)=="w" for xx in (bx-2,bx+wl+2)): break
                    if any(bx-1<ox+ow and bx+wl+1>ox and by-1<oy+oh and by+h+1>oy for ox,oy,ow,oh in OBST): continue
                    txt(c,bx,by+.6,lab,"PopB",sz,GR);OBST.append((bx-1,by-1,wl+2,h+2));return
            break
        band_label(lab,GR,"w",False)                          # fallback: the old placer
    pin_noplay()
    DIVS=[];[DIVS.append(r[4]) for r in rows if r[4] and r[4] not in DIVS]
    DNUM={d:i+1 for i,d in enumerate(DIVS)}
    leaders=set()
    if DIVSEED[k]:
        seen=set()
        for r in pl:
            if r[4] not in seen: seen.add(r[4]);leaders.add(r[0])
    for x,yy,r_,r in MD:
        ours=r[0]==me
        _blot(x,yy,r_,LC if ours else FAG)                    # every ball the same size — color alone says yours
        if r[0] in leaders:                                   # division leader = holds a top seed, wherever it sits
            c.saveState();c.setStrokeColor(DKG);c.setLineWidth(1.1);c.circle(x,yy,r_+2.0,stroke=1,fill=0);c.restoreState()
    for x,yy,r_,r in MD:
        ours=r[0]==me;nm=("Dark Knight "+RN[k]) if ours else _sn(r[0],16 if DIVSEED[k] else 22)
        dn=f"  ·  Div {DNUM[r[4]]}" if DIVSEED[k] and r[4] else ""
        _plate(x,yy,r_+(2.0 if r[0] in leaders else 0),f"{nm}  {_ord(place[r[0]])}{dn}",None,None,None,None)
    # ---- LEGEND, one line under the frame, starting at the axis
    ky=B-30;x=L;f6=6.0
    txt(c,x,ky,"Legend:","PopB",6.2,INKN);x+=c.stringWidth("Legend:  ","PopB",6.2)
    _blot(x+3.4,ky+2,3.4,LC);txt(c,x+10,ky,D["name"],"Pop",f6,GR);x+=18+c.stringWidth(D["name"],"Pop",f6)
    _blot(x+3.4,ky+2,3.4,FAG);txt(c,x+10,ky,"Rivals","Pop",f6,GR);x+=42
    if DIVSEED[k]:
        _blot(x+3.4,ky+2,3.4,FAG);c.saveState();c.setStrokeColor(DKG);c.setLineWidth(1.1);c.circle(x+3.4,ky+2,5.4,stroke=1,fill=0);c.restoreState()
        tl=f"Division leader — the {len(DIVS)} leaders take seeds 1 to {len(DIVS)}, wherever they sit"
        txt(c,x+12,ky,tl,"Pop",f6,GR)
    # ---- the read, right column
    px=M+382;pw=W-M-px;py=y-26
    cutr=pl[SP-1];me_r=R[me];gb=cutr[1]-me_r[1];pfrank=1+sum(r[3]>me_r[3] for r in rows)
    if place[me]<=HF: stn=f"{_ord(place[me])} of {n} — in the green, the top half of the playoff field."
    elif place[me]<=SP: stn=f"{_ord(place[me])} of {n} — in the gold: in the playoffs today, but one of the last {SP-HF} in."
    elif gb==0: stn=f"{_ord(place[me])} of {n} — level on wins with {_ord(SP)}; points decide it."
    else: stn=f"{_ord(place[me])} of {n} — {gb} win{'s' if gb>1 else ''} behind {_ord(SP)} place, the last playoff spot."
    py=panel_note(px,py,pw,"Standing",stn)
    py=panel_note(px,py,pw,"Scoring",f"{_ord(pfrank)} in points of {n}. "+("Points say this team is better than its record." if pfrank<place[me] else "Record and points agree." if pfrank==place[me] else "The record is ahead of the scoring — some luck banked."))
    hr=hardrank[me];ez=n+1-hr
    py=panel_note(px,py,pw,"Road ahead",(f"{_ord(hr)} hardest of {n}." if hr<=n/2 else f"{_ord(ez)} easiest of {n}.")+" Opponents still to play, by what they score a week.")
    if mydiv: py=panel_note(px,py,pw,"Division",(f"{LG_} is in Division {DNUM[mydiv]} of {len(DIVS)}. The gold-ringed balls lead their divisions — the winners take seeds 1 to {len(DIVS)}, the rest are filled by record." if DIVSEED[k] else f"{len(DIVS)} divisions, but seeds go by overall standings — divisions don't decide who gets in."))
    else: py=panel_note(px,py,pw,"Division",f"None in this league — {SP} of {n} go through.")
    hdr(c,px,py,"THIS WEEK AND NEXT FOUR");py-=11
    for i,nm in enumerate([THIS3[k]]+NEXT4[k]):
        r=R[nm];txt(c,px,py,f"Week {3+i}","PopB",6.4,GR);txt(c,px+34,py,_sn(nm,20),"PopB" if i==0 else "Pop",6.6,INKN)
        txt(c,px+pw,py,f"{r[1]}–{r[2]}  {_ord(place[nm])}","PopM",6.4,INKN,"r");py-=10.5
    _sp=radar(D,k,LC,Ht/2-40)
    note(c,M,32,"How to read it",f"{SP} of {n} make the playoffs. Green = the top {HF}. Gold = the last {SP-HF} in — the dark gold line is the playoff cut. Plain = out. Wins rank first, points break ties, so the edges step.",6.0)
    footer(c,FP,"The League · "+LG_)
    c.showPage()
    if _sp: radar_cont(D,k,LC,_sp,FP)
