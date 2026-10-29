import math, zlib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor as H, Color
from reportlab.lib.utils import simpleSplit
from gdata2 import *
from gdata2 import _SLOT
from reportlab.pdfgen.canvas import FILL_EVEN_ODD
pdfmetrics.registerFont(TTFont("Bebas","/home/claude/cand/fonts/BebasNeue-Regular.ttf"))
GF="/usr/share/fonts/truetype/google-fonts/"
for n,f in (("Pop","Poppins-Regular"),("PopM","Poppins-Medium"),("PopB","Poppins-Bold")): pdfmetrics.registerFont(TTFont(n,GF+f+".ttf"))
W,Ht=letter; M=30
BG=H("#0E1628"); BG2=H("#16213A"); TXT=H("#EEF1F6"); GR=H("#8C94A6"); GR2=H("#5E6679"); GRID=H("#2A3654"); TRACK=H("#26365A")
UP=H("#4FD08A"); DN=H("#FF6B72"); HOLD=H("#F7B32B"); FLAT=H("#9AA2B5"); OPPC=H("#9AA2B5")
LC={"DK I":H("#5B9BF5"),"DK II":H("#F0763A"),"DK III":H("#A98BFF"),"DK IV":H("#4FD6CA")}
FULL={"DK I":"Most Important","DK II":"Winners Sinners","DK III":"Hers His Ver 2.0","DK IV":"Murrieta NXTDR"}   # Oct 11 (Dom): short one-line names, same as Dark Knight Live
YAH={"DK I":(158.69,153.02),"DK II":(158.7,163.0),"DK III":(125.7,125.8),"DK IV":(170.5,143.7)}   # Yahoo matchup pages, Wed Sep 30 evening
def mix(a,b,t): return Color(a.red*(1-t)+b.red*t,a.green*(1-t)+b.green*t,a.blue*(1-t)+b.blue*t)
def txt(x,y,s,f,sz,col=TXT,al="l"):
    c.setFont(f,sz); c.setFillColor(col)
    {"l":c.drawString,"r":c.drawRightString,"c":c.drawCentredString}[al](x,y,s); return c.stringWidth(s,f,sz)
def verdict(p):
    for lo,w in ((95,"ALMOST WON"),(70,"ON TRACK"),(56,"HOLDING"),(52,"SLIGHT EDGE"),(49,"DEAD EVEN"),(45,"SLIGHT UNDERDOG"),(5,"LOSING")):
        if p>=lo: return w,TXT
    return "ALMOST LOST",TXT
def _wl(w):
    h,m=map(int,w["et"].split(":")); h-=3
    return f"{w['day'][:3].upper()} {h%12 or 12}:{m:02d} {'PM' if h>=12 else 'AM'}"
WLAB=[_wl(w) for w in WINS]
def ordn(n): return f"{n}{'th' if 10<=n%100<=20 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')}"
def svar(L):
    s=[SIG.get(p["slot"],8.0) for p in L]; ss=sum(x*x for x in s); st=sum(s); return ss+RHO*(st*st-ss)
# ---------- the gauge: Dark Knight Live geometry (r 78, stroke 20, ticks 25/50/75), scaled ----------
def gauge(cx,cy,r,v,col,big=True,ghost=None):
    sw=r*20/78
    def pt(t,rr): a=math.pi*(1-t/100); return cx+rr*math.cos(a), cy+rr*math.sin(a)
    c.setLineCap(0); c.setLineWidth(sw); c.setStrokeColor(TRACK); c.arc(cx-r,cy-r,cx+r,cy+r,0,180)
    if v>0: c.setStrokeColor(col); c.arc(cx-r,cy-r,cx+r,cy+r,180-1.8*min(v,99.9),1.8*min(v,99.9))
    c.setStrokeColor(BG2); c.setLineWidth(max(1.2,sw*.15))
    for t in (25,50,75):
        a=pt(t,r-sw/2-.5); b=pt(t,r+sw/2+.5); c.line(*a,*b)
    if big:
        for t,s in ((0,"0"),(50,"50"),(100,"100")):
            x,y=pt(t,r+sw/2+5.5); txt(x,y-2,s,"Pop",5.2,GR,"c")
    if ghost is not None:
        x,y=pt(ghost,r*.96); c.setDash(3,2); c.setStrokeColor(GR); c.setLineWidth(1.2); c.line(cx,cy,x,y); c.setDash()
    x,y=pt(v,r*1.02); c.setLineCap(1); c.setStrokeColor(TXT); c.setLineWidth(max(1.6,r*.07)); c.line(cx,cy,x,y)
    c.setFillColor(TXT); c.circle(cx,cy,max(2.2,r*.1),fill=1,stroke=0); c.setLineCap(0)
# ---------- the seat sphere: glass ball, league-colored fluid at a tilt, filling by place; the tilted line is the playoff cut ----------
TILT=math.radians(11)          # Claude's own choice: the whole instrument leans like a gyro, fluid and cut line parallel
def _level(cx,cy,r,frac,x,wave):
    yb=cy-r+2*r*frac; return yb+(x-cx)*math.tan(TILT)+wave*math.sin((x-cx)/r*math.pi*1.5)
def ring(cx,cy,r,n,me,cut,col,lab):
    frac=(n-me+1)/n
    c.saveState(); c.setFillColor(BG); c.setFillAlpha(.55); c.ellipse(cx-r*.8,cy-r-3.2,cx+r*.8,cy-r+1.2,fill=1,stroke=0); c.restoreState()
    c.saveState(); p=c.beginPath(); p.circle(cx,cy,r); c.clipPath(p,stroke=0)
    c.radialGradient(cx-r*.35,cy+r*.4,r*1.6,(mix(TXT,BG2,.04),mix(TXT,BG2,.30)),(0,1),extend=True)   # frosted empty glass
    q=c.beginPath(); xs=[cx-r+k*(2*r/40) for k in range(41)]
    q.moveTo(cx-r,cy-r-2)
    for x in xs: q.lineTo(x,_level(cx,cy,r,frac,x,.9))
    q.lineTo(cx+r,cy-r-2); q.close()
    c.saveState(); c.clipPath(q,stroke=0)
    c.linearGradient(cx,cy-r,cx,cy+r,(mix(col,BG,.30),col,mix(col,TXT,.18)),(0,.6,1),extend=True)    # fluid, darker at the bottom
    c.restoreState()
    s_=c.beginPath(); s_.moveTo(xs[0],_level(cx,cy,r,frac,xs[0],.9))
    for x in xs[1:]: s_.lineTo(x,_level(cx,cy,r,frac,x,.9))
    c.setStrokeColor(mix(col,TXT,.45)); c.setLineWidth(.7); c.drawPath(s_,fill=0,stroke=1)                 # the fluid's lit surface
    c.saveState(); c.setFillColor(TXT); c.setFillAlpha(.55); c.ellipse(cx-r*.62,cy+r*.30,cx-r*.10,cy+r*.68,fill=1,stroke=0); c.restoreState()   # gloss
    c.restoreState()
    c.setStrokeColor(mix(col,BG2,.25)); c.setLineWidth(.9); c.circle(cx,cy,r,fill=0,stroke=1)
    tw=max(c.stringWidth(ordn(me).upper(),"Bebas",13),c.stringWidth("PLACE","PopB",4.2))/2+2.5
    if cut:                                   # the cut, between the last seat in and the first seat out: solid outside the glass, dotted through it
        cf=(n-cut+.5)/n; ext=r+6
        def P(x): return x,_level(cx,cy,r,cf,x,0)
        half=math.sqrt(max(0,r*r-0)); xa,xb=cx-r,cx+r
        c.setLineCap(1); c.setStrokeColor(TXT); c.setLineWidth(1.3)
        c.line(*P(cx-ext),*P(xa+.4)); c.line(*P(xb-.4),*P(cx+ext))
        c.setStrokeColor(BG); c.setLineWidth(1.15); c.setDash(.1,2.3)
        c.line(*P(xa+2.2),*P(xb-2.2)); c.setDash(); c.setLineCap(0)
    txt(cx,cy-8.4,ordn(me).upper(),"Bebas",12,BG,"c")
    txt(cx,cy-12.5,"PLACE","PopB",3.9,BG,"c")
    txt(cx,cy+r+5,lab,"PopB",5.2,GR,"c")
# ---------- the scoring meter: centre-zero LED bar, one light per 1% off the league average ----------
def ledmeter(x,y,tr):
    seg,gap,hh,N=4.1,1.3,6.2,10; mid=x+N*(seg+gap)+1.5; on=min(N,int(round(abs(tr)))); cc=UP if tr>=0 else DN
    for k in range(N):
        for side in (-1,1):
            sx=(mid+1.5+k*(seg+gap)) if side>0 else (mid-1.5-(k+1)*(seg+gap)+gap)
            lit=(side>0)==(tr>=0) and k<on
            if lit:
                c.saveState(); c.setFillColor(cc); c.setFillAlpha(.22); c.roundRect(sx-1,y-1,seg+2,hh+2,1.4,fill=1,stroke=0); c.restoreState()
            c.setFillColor(mix(cc,TXT,.15*(k/N)) if lit else TRACK); c.roundRect(sx,y,seg,hh,.8,fill=1,stroke=0)
    c.setStrokeColor(TXT); c.setLineWidth(.9); c.line(mid,y-2.2,mid,y+hh+2.2)
    txt(mid,y-7.6,"LEAGUE AVG","Pop",4.3,GR2,"c")
    ex=x+2*N*(seg+gap)+3+6
    _tri(ex+3,y+hh/2,tr>=0,cc)
    txt(ex+9,y+.6,f"{abs(tr):.0f}% {'ABOVE' if tr>=0 else 'BELOW'}","Bebas",10,cc)
    return mid
# ---------- the quarter lights: four per window, lit by the share of that window's quarters played ----------
import datetime as _dt
QEND=(45,90,148,190)          # minutes after kickoff at which quarters 1-4 end, halftime inside the third
NOWUTC=_dt.datetime.utcnow()
def qlit(i):
    gs=[r for r in G.itertuples() if _SLOT[(r.weekday,r.gametime)]==i]; done=0
    for r in gs:
        k=_dt.datetime.strptime(f"{r.gameday} {r.gametime}","%Y-%m-%d %H:%M")+_dt.timedelta(hours=4)   # Eastern daylight to UTC
        el=(NOWUTC-k).total_seconds()/60; done+=sum(el>=q for q in QEND)
    return int(4*done/(4*len(gs))) if gs else 0
# ---------- jagged ridges, deterministic so the shape never reads as movement (options v14/v15 grammar) ----------
JAMP=2.6; JSTEP=4.5
def _seed(*k): return zlib.crc32("|".join(map(str,k)).encode())
def jag(key,x): return ((_seed(key,round(x,1))%1000)/1000-.5)*2*JAMP
def ridge(key,xs,ys,x0,x1,base):
    """true values at xs kept exactly; between them a cosine ease plus a small deterministic jag"""
    X=[x0]+xs+[x1]; Y=[0]+ys+[0]; P=[]
    for i in range(len(X)-1):
        a,b=X[i],X[i+1]; n=max(2,int((b-a)/JSTEP))
        for k in range(n):
            u=k/n; x=a+(b-a)*u; e=(1-math.cos(math.pi*u))/2; y=Y[i]+(Y[i+1]-Y[i])*e
            if 0<k: y=max(0,y+jag(key,x)*min(1,y/6))
            P.append((x,base+y))
    P.append((x1,base)); return P
def fill_ridge(P,base,col,al):
    p=c.beginPath(); p.moveTo(P[0][0],base)
    for x,y in P: p.lineTo(x,y)
    p.lineTo(P[-1][0],base); p.close()
    c.saveState(); c.setFillColor(col); c.setFillAlpha(al); c.drawPath(p,fill=1,stroke=0); c.restoreState()
    for lw,cc in ((2.0,BG),(1.0 if col is OPPC else 0.7,TXT if col is OPPC else mix(col,TXT,.25))):      # the shared top line: dark halo, light edge (opponent brighter)
        q=c.beginPath(); q.moveTo(*P[0])
        for x,y in P[1:]: q.lineTo(x,y)
        c.setStrokeColor(cc); c.setLineWidth(lw); c.drawPath(q,fill=0,stroke=1)
# ---------- data per league ----------
def prep(lab):
    cfg,T,st=league(lab); me,op=T[cfg["me"]],T[cfg["opp"]]
    ym,yo=YAH[lab]; sd=math.sqrt(svar(me["lineup"])+svar(op["lineup"]))
    pct=round(100*phi((ym-yo)/sd))
    s=st.copy(); s["w"]=s.record.str.split("-").str[0].astype(int); s["l"]=s.record.str.split("-").str[1].astype(int)
    mine=s[s.team==me["name"]].iloc[0]; n=len(s); cut=6
    sixth=s[s["rank"]==cut].iloc[0]; seventh=s[s["rank"]==cut+1].iloc[0]
    if mine["rank"]<=cut:
        gb=mine.w-seventh.w; head=("IN",UP,f"{gb} GAME{'S' if gb!=1 else ''} CLEAR OF 7TH" if gb>0 else "IN ON POINTS, LEVEL WITH 7TH")
    else:
        gb=sixth.w-mine.w; head=("OUT",DN,f"{gb} GAME{'S' if gb!=1 else ''} BACK OF 6TH" if gb>0 else f"LEVEL WITH 6TH, {sixth.pf-mine.pf:.0f} BEHIND ON POINTS")
    avgpf=s.pf.mean(); tr=(mine.pf/avgpf-1)*100
    if isinstance(mine.division,str) and mine.division:
        d=s[s.division==mine.division].sort_values("rank"); dplace=list(d.team).index(me["name"])+1
        dv=(len(d),dplace,"DIVISION",f"{ordn(dplace)} OF {len(d)}")
        divteams=[T[o] for o in T if T[o]["name"] in set(d.team)]; band3=("division",divteams)
    else:
        r2=int(s.pf.rank(ascending=False)[s.team==me["name"]].iloc[0])
        dv=(n,r2,"POINTS FOR",f"{ordn(r2)} OF {n}")
        top=[T[o] for o in T if T[o]["name"] in set(s[s["rank"]<=6].team)]; band3=("top six",top)
    oppdiv=(st[st.team==op["name"]].division.iloc[0]==mine.division) if isinstance(mine.division,str) else False
    avg=lambda L:[sum(t["win"][i] for t in L)/len(L) for i in range(NW)]
    bands=[("league",avg(list(T.values()))),band3[0:1]+(avg(band3[1]),),("opp",op["win"]),("you",me["win"])]
    return dict(lab=lab,cfg=cfg,me=me,op=op,ym=ym,yo=yo,pct=pct,sd=sd,rec=mine.record,rank=int(mine["rank"]),n=n,cut=cut,
                head=head,tr=tr,dv=dv,bands=bands,oppdiv=oppdiv,oppname=op["name"].replace(" ☠️",""),opprec=st[st.team==op["name"]].record.iloc[0])
PROSE={
 "DK I":"A slight edge on Wednesday's numbers, 158.7 to 153.0, in a division game: DIKFORE leads the Marriage at 3-0, and a win pulls Dark Knight I to one game back of them. Their trade (Love in; Olave, Price out) processes today, so it is read again at the refresh. On the page: Monangai over Kamara, +2.2 a game.",
 "DK II":"A slight underdog, 4.3 behind on Yahoo. At 2-1, level with 6th on record and out only on season points, 43 behind. The open call on the page: Willis or Darnold at quarterback, too close to separate.",
 "DK III":"Dead even, 125.7 to 125.8, in a division game against a 1-2 team. One game back of 6th. Friday's job is Rachaad White's shoulder: Washington plays in London at 6:30 a.m. PT Sunday, so there is no Sunday-morning fix.",
 "DK IV":"Ahead by 26.8 against Team Other, the league's only unbeaten side at 6-0. Third, one game clear of 7th. The open question on the page: Odunze over Doubs reads +1.6, but both forecasts run ahead of their actual usage.",
}
BANDLAB={"league":"LEAGUE AVG","division":"DIVISION AVG","top six":"TOP-SIX AVG","opp":"OPPONENT","you":"MINE"}
def block(D,top,h,VMAX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h
    c.setFillColor(BG2); c.roundRect(x0,bot,x1-x0,h,5,fill=1,stroke=0)
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    # --- the mountain: projected points by game window; its key sits at its own left edge ---
    pb=bot+42; mh=38; mx0=x0+8; mx1=x1-8; rx0=mx0+52
    xs=[mx0+(mx1-mx0)*(.17+.77*i/(NW-1)) for i in range(NW)]
    tint={"league":(mix(col,BG2,.66),.65),"division":(mix(col,BG2,.45),.55),"top six":(mix(col,BG2,.45),.55),"opp":(OPPC,.48),"you":(col,.70)}
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=ridge(D["lab"]+k,xs,[mh*min(1,y/VMAX) for y in v],rx0,mx1,pb); fill_ridge(P,pb,*tint[k])
    c.restoreState()
    for j,(k,v) in enumerate(reversed(D["bands"])):          # key: front layer first
        cc,al=tint[k]; ly=pb+mh-8-j*8.5
        c.setFillColor(cc); c.rect(x0+10,ly+.3,4.5,4.5,fill=1,stroke=0)
        txt(x0+18,ly,BANDLAB[k],"PopM",5,col if k=="you" else mix(cc,TXT,.35))
    for i,x in enumerate(xs):                                  # each window: day and time, quarters played, starters mine vs opponent
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,GR,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(col if q<lit else TRACK); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
        txt(x,pb-21.5,f"{D['me']['cnt'][i]} vs {D['op']['cnt'][i]}","PopM",5.6,TXT,"c")
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    nx=rx0+(xs[0]-rx0)*.45; nh=mh*.55; c.setStrokeColor(GOLDISH); c.setLineWidth(.8); c.line(nx,pb,nx,pb+nh)
    txt(nx,pb+nh+3,"nothing banked","Pop",4.6,GOLDISH,"c"); txt(nx,pb+nh+9.5,"NOW","PopB",5,GOLDISH,"c")
    # --- identity column: title, league name, the matchup on one line, the scoring meter ---
    y=top-24; lw_=txt(x0+10,y,D["lab"],"Bebas",24,TXT)
    txt(x0+10+lw_+7,y+2,FULL[D["lab"]],"PopM",6.2,GR)
    gx=x0+238; gr=29; gy=top-45
    a_,b_=D["rec"],f"{D['oppname'].upper()} {D['opprec']}"; fs=16
    while c.stringWidth(a_+b_,"Bebas",fs)+c.stringWidth("  vs  ","PopM",fs*.45)>gx-gr-14-(x0+10): fs-=.25
    w1=txt(x0+10,y-20,a_,"Bebas",fs,TXT); w2=txt(x0+10+w1,y-20,"  vs  ","PopM",fs*.45,GR); txt(x0+10+w1+w2,y-20,b_,"Bebas",fs,TXT)
    txt(x0+10,y-33.5,"SCORING","PopB",5.2,GR)
    ledmeter(x0+40,y-36,D["tr"])
    # --- the big meter, the verdict, Yahoo's numbers right under it ---
    gauge(gx,gy,gr,D["pct"],col)
    vtxt,_=verdict(D["pct"])
    txt(gx,gy-22,f"{D['pct']}%","Bebas",20,TXT,"c")
    txt(gx,gy-28.5,"WIN PROBABILITY","PopB",5.0,GR,"c")
    bx=gx+gr+16
    txt(bx,top-29,vtxt,"Bebas",18,TXT)
    w_=txt(bx,top-43,f"{D['ym']:.1f}","Bebas",14,TXT); w_+=txt(bx+w_,top-43,"  vs  ","PopM",6.2,GR)
    w_+=txt(bx+w_,top-43,f"{D['yo']:.1f}","Bebas",14,TXT); txt(bx+w_+5,top-43,f"({D['ym']-D['yo']:+.1f})","Bebas",11.5,TXT)
    txt(bx,top-51.5,"Yahoo projections, Wed Sep 30"+("  ·  division game" if D["oppdiv"] else ""),"PopM",5.4,GR)
    # --- standings, right: two seat rings, then playoffs in or out ---
    n,me_,cut=D["n"],D["rank"],D["cut"]; hx=x1-84; ry=top-37
    ring(hx,ry,15,n,me_,cut,col,"LEAGUE")
    dn,dp,dlab,dsub=D["dv"]; ring(hx+50,ry,15,dn,dp,None,col,dlab)
    pin,_,pt_=D["head"]
    txt(hx+25,top-64,f"PLAYOFFS {pin}","Bebas",11,TXT,"c")
    txt(hx+25,top-71,pt_.lower().replace("6th","6th").capitalize(),"PopM",5.4,GR,"c")
    # --- prose, behind the paper-sheet mark ---
    sw_=sheet(x0+10,bot+11.5,6.5,GR)
    for j,l in enumerate(simpleSplit(PROSE[D["lab"]],"Pop",6.5,x1-x0-26-sw_)[:3]): txt(x0+14+sw_,bot+11.5-j*8,l,"Pop",6.5,TXT)
def sheet(x,yb,fs,col):
    """the paper-sheet mark (options pages): a small sideways note sheet, folded corner, two ruled lines"""
    w_=fs*1.12; h_=fs*.80; y0=yb-.3; f_c=h_*.34
    p=c.beginPath(); p.moveTo(x,y0); p.lineTo(x,y0+h_); p.lineTo(x+w_-f_c,y0+h_); p.lineTo(x+w_,y0+h_-f_c); p.lineTo(x+w_,y0); p.close()
    c.setFillColor(mix(col,BG,.72)); c.setStrokeColor(col); c.setLineWidth(.55); c.drawPath(p,fill=1,stroke=1)
    c.setLineWidth(.4); c.line(x+w_*.2,y0+h_*.62,x+w_*.66,y0+h_*.62); c.line(x+w_*.2,y0+h_*.32,x+w_*.8,y0+h_*.32)
    return w_
GOLDISH=H("#EFD23E"); BOX=H("#1C2A47")
def _tri(x,y,up,col):
    p=c.beginPath()
    if up: p.moveTo(x-3,y-2.2); p.lineTo(x+3,y-2.2); p.lineTo(x,y+2.6)
    else:  p.moveTo(x-3,y+2.2); p.lineTo(x+3,y+2.2); p.lineTo(x,y-2.6)
    p.close(); c.setFillColor(col); c.drawPath(p,fill=1,stroke=0); return 6
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-18; txt(M,y,"DARK KNIGHT","Bebas",30); txt(M+c.stringWidth("DARK KNIGHT","Bebas",30)+8,y,"WHERE EACH TEAM STANDS · WEEK 4","Bebas",18,GOLDISH)
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    txt(W-M,y+10,f"Rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","PopM",6,GR,"r")
    txt(W-M,y+2,"Yahoo matchups, lineups, standings: pulled Wed Sep 30 evening","Pop",5.6,GR2,"r")
    txt(W-M,y-6,"Kickoffs: nflverse schedule  ·  rosters not yet refreshed","Pop",5.6,GR2,"r")
    thu=", ".join(f"{D['lab']} {D['me']['cnt'][0]}" for D in DS if D['me']['cnt'][0])
    txt(M,y-16,f"Thursday tonight: PIT at CLE, 8:15 p.m. ET = 5:15 p.m. PT.  Starters in it: {thu}.  London Sunday: IND vs WAS, 9:30 a.m. ET = 6:30 a.m. PT.","PopM",6.3,TXT)
    sx=M; sw=(W-2*M)/4; TEAM={"DK I":"Dark Knight I","DK II":"Dark Knight II","DK III":"Dark Knight III","DK IV":"Dark Knight IV"}
    for D in DS:
        L=D["lab"]; c.setFillColor(LC[L]); c.rect(sx,y-36,sw-4,2.4,fill=1,stroke=0)
        a=L+"  "; b=FULL[L]; d_=" · "+TEAM[L]; fs=6.0
        while c.stringWidth(a,"Bebas",fs*1.55)+c.stringWidth(b+d_,"PopM",fs)>sw-6: fs-=.1
        w1=txt(sx,y-30,a,"Bebas",fs*1.55,TXT); w2=txt(sx+w1,y-30,b,"PopM",fs,LC[L]); txt(sx+w1+w2,y-30,d_,"PopM",fs,GR)
        sx+=sw
    y-=11
    top=y-34; h=(top-40)/4-6
    for D in DS: block(D,top,h,VMAX); top-=h+6
    foot=("WIN PROBABILITY: Dark Knight Live's gauge and math on Yahoo's projections, before anything is banked. "
          "LEAGUE: the ball fills by place, first full; the tilted line through it is the playoff cut, between 6th and 7th. DIVISION: place in the division (DK IV has none: points-for rank). "
          "SCORING: points for against the league average, Weeks 1-3, one light per 1%. "
          "THE MOUNTAIN: projected points by game window from each layer's best lineup, one scale for the page; white dots are true heights, the jag between them is drawn. "
          "Under each window: kickoff, Pacific; quarters played; starters, mine first. Yahoo's own win % not pulled.")
    FW=W-2*M-150
    for j,l in enumerate(simpleSplit(foot,"Pop",4.5,FW)): txt(W/2,30-j*5.8,l,"Pop",4.5,GR2,"c")
    txt(M,9,"DARK KNIGHT FANTASY SCAN","Bebas",9,GR); txt(W-M,9,"Global page · v6","Pop",5.6,GOLDISH,"r")
    c.save(); return DS

# ======================= v7 block (Thu Oct 1 evening, Dom's voice walk of v6) =======================
# Header: one line, page name hard right like OPTIONS. Key, Thursday and London notes gone.
# LED meter gone. Identity column: tag + record, vs, opponent + record; Yahoo line under it; age stamp.
# Gauge slid into the freed space, verdict word gone, WIN PROBABILITY white and bigger.
# Balls: division then league, ordinal centered, PLACE gone, outside strokes gone, cut only on league.
PROSE={
 "DK I":"A division game against the Marriage leader. DIKFORE's trade (Love in; Olave and Price out) processes today, so their side is read again at the refresh. The lineup call: Monangai over Kamara, +2.2 a game.",
 "DK II":"Level with 6th on record, out only on season points, 43 behind. Open call at quarterback: Willis or Darnold, too close to separate.",
 "DK III":"One game back of 6th. Both London starters are yours, White and Downs, at 6:30 a.m. PT Sunday, so there is no Sunday-morning fix. Friday's job: Rachaad White's shoulder.",
 "DK IV":"One game clear of 7th, against the league's only unbeaten side. Odunze over Doubs reads +1.6, but both forecasts run ahead of their actual usage; that call is still open.",
}
def ring(cx,cy,r,n,me,cut,col,lab):
    frac=(n-me+1)/n
    c.saveState(); c.setFillColor(BG); c.setFillAlpha(.55); c.ellipse(cx-r*.8,cy-r-3.4,cx+r*.8,cy-r+1.2,fill=1,stroke=0); c.restoreState()
    c.saveState(); p=c.beginPath(); p.circle(cx,cy,r); c.clipPath(p,stroke=0)
    c.radialGradient(cx-r*.35,cy+r*.4,r*1.6,(mix(TXT,BG2,.04),mix(TXT,BG2,.30)),(0,1),extend=True)
    q=c.beginPath(); xs=[cx-r+k*(2*r/40) for k in range(41)]
    q.moveTo(cx-r,cy-r-2)
    for x in xs: q.lineTo(x,_level(cx,cy,r,frac,x,.9))
    q.lineTo(cx+r,cy-r-2); q.close()
    c.saveState(); c.clipPath(q,stroke=0)
    c.linearGradient(cx,cy-r,cx,cy+r,(mix(col,BG,.30),col,mix(col,TXT,.18)),(0,.6,1),extend=True)
    c.restoreState()
    s_=c.beginPath(); s_.moveTo(xs[0],_level(cx,cy,r,frac,xs[0],.9))
    for x in xs[1:]: s_.lineTo(x,_level(cx,cy,r,frac,x,.9))
    c.setStrokeColor(mix(col,TXT,.45)); c.setLineWidth(.7); c.drawPath(s_,fill=0,stroke=1)
    if cut:                                   # the qualifying line, inside the glass only, behind the number
        cf=(n-cut+.5)/n
        def P(x): return x,_level(cx,cy,r,cf,x,0)
        c.setLineCap(1); c.setStrokeColor(BG); c.setLineWidth(1.4); c.setDash(.1,2.4)
        c.line(*P(cx-r),*P(cx+r)); c.setDash(); c.setLineCap(0)
    c.saveState(); c.setFillColor(TXT); c.setFillAlpha(.55); c.ellipse(cx-r*.62,cy+r*.34,cx-r*.12,cy+r*.70,fill=1,stroke=0); c.restoreState()
    c.restoreState()
    c.setStrokeColor(mix(col,BG2,.25)); c.setLineWidth(.9); c.circle(cx,cy,r,fill=0,stroke=1)
    txt(cx,cy-r*.30,ordn(me).upper(),"Bebas",r*.95,BG,"c")          # dead center of the glass
    txt(cx,cy+r+6,lab,"PopB",6.4,TXT,"c")
def idwidth(D):
    f=lambda s,fn,sz: c.stringWidth(s,fn,sz)
    return f(D["lab"],"Bebas",24)+6+f(D["rec"],"Bebas",16)+f("  vs  ","PopM",7)+f(f"{D['oppname'].upper()} {D['opprec']}","Bebas",16)
def block(D,top,h,VMAX,GX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h
    c.setFillColor(BG2); c.roundRect(x0,bot,x1-x0,h,5,fill=1,stroke=0)
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    # --- the mountain ---
    pb=bot+46; mh=40; mx0=x0+8; mx1=x1-8; rx0=mx0+52
    xs=[mx0+(mx1-mx0)*(.17+.77*i/(NW-1)) for i in range(NW)]
    tint={"league":(mix(col,BG2,.66),.65),"division":(mix(col,BG2,.45),.55),"top six":(mix(col,BG2,.45),.55),"opp":(OPPC,.48),"you":(col,.70)}
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=ridge(D["lab"]+k,xs,[mh*min(1,y/VMAX) for y in v],rx0,mx1,pb); fill_ridge(P,pb,*tint[k])
    c.restoreState()
    for j,(k,v) in enumerate(reversed(D["bands"])):
        cc,al=tint[k]; ly=pb+mh-8-j*8.5
        c.setFillColor(cc); c.rect(x0+10,ly+.3,4.5,4.5,fill=1,stroke=0)
        txt(x0+18,ly,BANDLAB[k],"PopM",5,col if k=="you" else mix(cc,TXT,.35))
    for i,x in enumerate(xs):                  # window stack, one grey unit: kickoff, quarters, players mine vs his
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,GR,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(col if q<lit else TRACK); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
        txt(x,pb-21.5,f"PLAYERS {D['me']['cnt'][i]} vs {D['op']['cnt'][i]}","PopB",5.2,GR,"c")
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    nx=rx0+(xs[0]-rx0)*.45; nh=mh*.55; c.setStrokeColor(GOLDISH); c.setLineWidth(.8); c.line(nx,pb,nx,pb+nh)
    txt(nx,pb+nh+3,"nothing banked","Pop",4.6,GOLDISH,"c"); txt(nx,pb+nh+9.5,"NOW","PopB",5,GOLDISH,"c")
    # --- identity column: tag + record vs opponent + record; Yahoo's numbers; age stamp ---
    lx=x0+12; y=top-27
    w=txt(lx,y,D["lab"],"Bebas",24,col); w+=6
    w+=txt(lx+w,y,D["rec"],"Bebas",16,TXT); w+=txt(lx+w,y,"  vs  ","PopM",7,GR)
    txt(lx+w,y,f"{D['oppname'].upper()} {D['opprec']}","Bebas",16,TXT)
    y2=y-18
    w=txt(lx,y2,f"{D['ym']:.1f}","Bebas",15,col); w+=txt(lx+w,y2,"  vs  ","PopM",6.6,GR)
    w+=txt(lx+w,y2,f"{D['yo']:.1f}","Bebas",15,OPPC); txt(lx+w+5,y2,f"({D['ym']-D['yo']:+.1f})","Bebas",12,TXT)
    txt(lx,y2-9.5,FULL[D["lab"]]+"  ·  Yahoo projections, Wed Sep 30"+("  ·  division game" if D["oppdiv"] else ""),"PopM",5.4,GR)
    # --- the gauge, centered in the freed space ---
    gr=30; gy=top-52
    gauge(GX,gy,gr,D["pct"],col)
    txt(GX,gy-21,f"{D['pct']}%","Bebas",21,TXT,"c")
    txt(GX,gy-30,"WIN PROBABILITY","PopB",6.4,TXT,"c")
    # --- standings: division, then league (the wider circle) ---
    br=18; ry=top-50; lgx=x1-38; dvx=lgx-52
    dn,dp,dlab,dsub=D["dv"]
    ring(dvx,ry,br,dn,dp,None,col,dlab)
    ring(lgx,ry,br,D["n"],D["rank"],D["cut"],col,"LEAGUE")
    # --- prose, behind the paper-sheet mark, with room both sides ---
    px0=x0+64; px1=x1-64; fs=6.5
    L=simpleSplit(PROSE[D["lab"]],"Pop",fs,px1-px0-12)[:2]
    yb=bot+15 if len(L)>1 else bot+11.5
    sw_=sheet(px0,yb,5.4,GR)
    for j,l in enumerate(L): txt(px0+sw_+5,yb-j*8,l,"Pop",fs,TXT)
    return dvx-br
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT","Bebas",24); txt(W-M,y,"STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    txt(M,y-15,"ALL FOUR LEAGUES","Bebas",13,GR)
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    st_=f"Rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT  ·  Yahoo matchups, lineups, standings pulled Wed Sep 30 evening, a day old  ·  "
    wq="refresh before kickoff"
    xr=W-M-c.stringWidth(wq,"Pop",5.6); txt(W-M,y-14,wq,"Pop",5.6,GOLDISH,"r"); txt(xr,y-14,st_,"Pop",5.6,GR2,"r")
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-27,W,y-27)
    # gauge x: centered between the widest identity line and the division ball, nudged left (Dom)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-38-52-18
    GX=(idr+balll)/2-8
    top=y-40; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("WIN PROBABILITY: math on Yahoo's projections before anything is banked; Yahoo's own win % not yet pulled.  "
          "DIVISION, LEAGUE: the ball fills by place, first is full; the dotted line in the league ball is the playoff cut, 6th and 7th (DK IV has no divisions: points-for rank).  "
          "THE MOUNTAIN: this week's projected points by game window, best lineups, one scale for the page, filling as games are played.  "
          "Under each window: kickoff in Pacific time, quarters played, players mine vs his.")
    for j,l in enumerate(simpleSplit(foot,"Pop",4.6,W-2*M-120)): txt(W/2,38-j*5.8,l,"Pop",4.6,GR2,"c")
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,25,W-M,25)
    txt(M,15,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,15,"STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v7","Bebas",10,GR,"r")
    c.save(); return DS,GX,idr
# ======================= v8 block (Thu Oct 1 evening, Dom's voice walk of v7) =======================
# Header: DARK KNIGHT FANTASY / GLOBAL STANDINGS · WEEK 4, four league · team pairs under the title.
# One top line per block: the gauge's "50", the DK tag's cap height and the ball labels all level.
# Yahoo line pivots on the same "vs" as the record line; DIVISION GAME rides the number line.
# Balls are scales: ticks and numbers inside the glass down the left edge, fluid to your place,
# thin dotted cut line edge to edge (division: under 1st; league: under 6th). Superscript ordinals.
# Mountain: league color is "you", everything else steps grey. Window PLAYERS stacks gone; the
# gold NOW line carries the counts as two down-pointing triangles, mine left, his right.
# One sentence per block, flush left on the block spine behind a small paper mark.
PROSE={
 "DK I":"DIKFORE's trade (Love in; Olave and Price out) processes today and is re-read at the refresh; the lineup call is Monangai over Kamara, +2.2 a game.",
 "DK II":"Level with 6th on record and out only on season points, 43 behind; the open call is Willis or Darnold at quarterback, too close to separate.",
 "DK III":"Both London starters are yours, White and Downs at 6:30 a.m. PT Sunday, so there is no Sunday-morning fix; Friday's job is Rachaad White's shoulder.",
 "DK IV":"One game clear of 7th against the league's only unbeaten side; Odunze over Doubs reads +1.6, but that call is still open.",
}
TEAMN={"DK I":"Dark Knight I","DK II":"Dark Knight II","DK III":"Dark Knight III","DK IV":"Dark Knight IV"}
STEEL=H("#8A93A6")
def tints(col):
    # v41: yours is near-opaque so it never tints the greys underneath; the three context layers carry their
    # separation in distinct, darker ridge LINES, since on a level league (DK IV) their fills sit at nearly one height
    return {"you":(col,.90,mix(col,TXT,.30)),
            "opp":(H("#C9CFDB"),.46,H("#7F8BA3")),
            "division":(H("#8792A8"),.50,H("#4E586F")),
            "top six":(H("#76829C"),.50,H("#3C465C")),
            "league":(H("#424B63"),.60,H("#222A3D"))}
def fill_ridge(P,base,col,al,edge):
    p=c.beginPath(); p.moveTo(P[0][0],base)
    for x,y in P: p.lineTo(x,y)
    p.lineTo(P[-1][0],base); p.close()
    c.saveState(); c.setFillColor(col); c.setFillAlpha(al); c.drawPath(p,fill=1,stroke=0); c.restoreState()
    for lw,cc in ((2.0,BG),(.8,edge)):
        q=c.beginPath(); q.moveTo(*P[0])
        for x,y in P[1:]: q.lineTo(x,y)
        c.setStrokeColor(cc); c.setLineWidth(lw); c.drawPath(q,fill=0,stroke=1)
def ridge_at(P,x):
    for (xa,ya),(xb,yb) in zip(P,P[1:]):
        if xa<=x<=xb: return ya+(yb-ya)*((x-xa)/(xb-xa) if xb>xa else 0)
    return P[-1][1]
def dtri(x,ytip,w,hh,fill,edge):
    p=c.beginPath(); p.moveTo(x-w/2,ytip+hh); p.lineTo(x+w/2,ytip+hh); p.lineTo(x,ytip); p.close()
    c.setFillColor(fill); c.setStrokeColor(edge); c.setLineWidth(.7); c.setLineJoin(1); c.drawPath(p,fill=1,stroke=1); c.setLineJoin(0)
def ordinal(cx,yb,n,fs,col):
    """numeral in Bebas, suffix lowercase in Poppins Bold, raised to the cap line; centered on cx"""
    num=str(n); suf='th' if 10<=n%100<=20 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th'); ss=fs*.36
    wn=c.stringWidth(num,"Bebas",fs); ws=c.stringWidth(suf,"PopB",ss); x=cx-(wn+.6+ws)/2
    txt(x,yb,num,"Bebas",fs,col); txt(x+wn+.6,yb+fs*.70-ss*.72,suf,"PopB",ss,col)
def scalelabels(n):
    if n<=7: return set(range(1,n+1))
    return {1,n}|{round(1+(n-1)*k/3) for k in (1,2)} if n not in (12,) else {1,4,8,12}
def ring(cx,cy,r,n,me,cut,col,lab):
    fm=lambda u: .09+.82*u                                            # places use the inner 82% of the glass
    lvl=lambda k,x,wave=0: _level(cx,cy,r,fm((n-k+.5)/n),x,wave)      # the level of place k (1st at the top)
    frac=fm((n-me+.5)/n)
    c.saveState(); c.setFillColor(BG); c.setFillAlpha(.55); c.ellipse(cx-r*.8,cy-r-3.4,cx+r*.8,cy-r+1.2,fill=1,stroke=0); c.restoreState()
    c.saveState(); p=c.beginPath(); p.circle(cx,cy,r); c.clipPath(p,stroke=0)
    c.radialGradient(cx-r*.35,cy+r*.4,r*1.6,(mix(TXT,BG2,.04),mix(TXT,BG2,.30)),(0,1),extend=True)
    q=c.beginPath(); xs=[cx-r+k*(2*r/40) for k in range(41)]
    q.moveTo(cx-r,cy-r-2)
    for x in xs: q.lineTo(x,_level(cx,cy,r,frac,x,.9))
    q.lineTo(cx+r,cy-r-2); q.close()
    c.saveState(); c.clipPath(q,stroke=0)
    c.linearGradient(cx,cy-r,cx,cy+r,(mix(col,BG,.30),col,mix(col,TXT,.18)),(0,.6,1),extend=True)
    c.restoreState()
    s_=c.beginPath(); s_.moveTo(xs[0],_level(cx,cy,r,frac,xs[0],.9))
    for x in xs[1:]: s_.lineTo(x,_level(cx,cy,r,frac,x,.9))
    c.setStrokeColor(mix(col,TXT,.45)); c.setLineWidth(.7); c.drawPath(s_,fill=0,stroke=1)
    # the scale: one tick per place, running down the inside of the glass along its left edge
    LB=scalelabels(n); sc=mix(BG,col,.10)
    for k in range(1,n+1):
        y=cy-r+2*r*fm((n-k+.5)/n); dy=y-cy
        xe=cx-math.sqrt(max(0,r*r-dy*dy))+1.1; y=lvl(k,xe)
        tl=2.6 if k in LB else 1.5
        c.setStrokeColor(sc); c.setLineWidth(.45); c.line(xe,y,xe+tl,y)
        if k in LB: txt(xe+tl+1.0,y-1.3,str(k),"PopB",3.7,sc)
    if cut:                                    # the cut: between the last seat in and the first seat out, edge to edge
        cf=fm((n-cut)/n)
        def P(x): return x,_level(cx,cy,r,cf,x,0)
        oc=cx+r*.22; ow=c.stringWidth(str(me),"Bebas",14)+c.stringWidth("th","PopB",14*.36)+.6; oy=cy-r*.30
        c.saveState(); k_=c.beginPath(); k_.rect(cx-r-2,cy-r-2,2*r+4,2*r+4); k_.rect(oc-ow/2-1.6,oy-1.6,ow+3.2,14*CAP+3.2)
        c.clipPath(k_,stroke=0,fillMode=FILL_EVEN_ODD)          # the line breaks around the ordinal
        c.setLineCap(1); c.setStrokeColor(BG); c.setLineWidth(.75); c.setDash(.1,1.7)
        c.line(*P(cx-r),*P(cx+r)); c.setDash(); c.setLineCap(0); c.restoreState()
    c.saveState(); c.setFillColor(TXT); c.setFillAlpha(.50); c.ellipse(cx-r*.30,cy+r*.40,cx+r*.18,cy+r*.72,fill=1,stroke=0); c.restoreState()
    c.restoreState()
    c.setStrokeColor(mix(col,BG2,.25)); c.setLineWidth(.9); c.circle(cx,cy,r,fill=0,stroke=1)
    ordinal(cx+r*.22,cy-r*.30,me,14,BG)        # moved right of center to clear the scale
    return cy+r+6                              # label baseline (drawn by the block, on the top line)
def idwidth(D):
    f=lambda s,fn,sz: c.stringWidth(s,fn,sz)
    l1=f(D["lab"],"Bebas",24)+6+f(D["rec"],"Bebas",16)+f("  vs  ","PopM",7)+f(f"{D['oppname'].upper()} {D['opprec']}","Bebas",16)
    vs=f(D["lab"],"Bebas",24)+6+f(D["rec"],"Bebas",16)+f("  vs  ","PopM",7)
    l2=vs+f(f"{D['yo']:.1f}","Bebas",15)+5+f(f"({D['ym']-D['yo']:+.1f})","Bebas",12)+(7+f("DIVISION GAME","PopB",5.2) if D["oppdiv"] else 0)
    return max(l1,l2)
CAP=.70                                         # Bebas and Poppins cap height, share of the em
def block(D,top,h,VMAX,GX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h; T=tints(col)
    c.setFillColor(BG2); c.roundRect(x0,bot,x1-x0,h,5,fill=1,stroke=0)
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    lx=x0+12                                    # the block's spine: tag, Yahoo stamp, layer key, paper mark
    TL=top-12                                   # the top line: "50", DK tag cap, ball labels
    # --- the gauge, its "50" capping the top line ---
    gr=30; sw=gr*20/78; gy=TL-(5.2*CAP)-(gr+sw/2+5.5-2)
    gauge(GX,gy,gr,D["pct"],col)
    txt(GX,gy-17.5,f"{D['pct']}%","Bebas",17,TXT,"c")
    txt(GX,gy-25,"WIN PROBABILITY","PopB",5.8,TXT,"c")
    # --- identity column ---
    y=TL-24*CAP
    w=txt(lx,y,D["lab"],"Bebas",24,col); w+=6
    w+=txt(lx+w,y,D["rec"],"Bebas",16,TXT); vs0=lx+w
    w+=txt(lx+w,y,"  vs  ","PopM",7,GR); vs1=lx+w
    txt(lx+w,y,f"{D['oppname'].upper()} {D['opprec']}","Bebas",16,TXT)
    y2=y-18                                     # Yahoo line pivots on the same "vs"
    txt(vs0,y2,f"{D['ym']:.1f}","Bebas",15,col,"r"); txt(vs0,y2,"  vs  ","PopM",7,GR)
    w=vs1+txt(vs1,y2,f"{D['yo']:.1f}","Bebas",15,OPPC)
    w+=5+txt(w+5,y2,f"({D['ym']-D['yo']:+.1f})","Bebas",12,TXT)
    if D["oppdiv"]: txt(w+7,y2+.6,"DIVISION GAME","PopB",5.2,GR)
    txt(lx,y2-9.5,"Yahoo projections, Wed Sep 30","PopM",5.4,GR)
    # --- standings: division, then league; labels on the top line ---
    br=18; lgx=x1-38; dvx=lgx-52; ry=TL-6.4*CAP-6-br
    dn,dp,dlab,dsub=D["dv"]
    ring(dvx,ry,br,dn,dp,1 if dlab=="DIVISION" else None,col,dlab)
    ring(lgx,ry,br,D["n"],D["rank"],D["cut"],col,"LEAGUE")
    for x,l in ((dvx,dlab),(lgx,"LEAGUE")): txt(x,TL-6.4*CAP,l,"PopB",6.4,TXT,"c")
    # --- the mountain, down into the room the players stacks gave back ---
    pb=bot+31; mh=min(46,(gy-31)-pb); mx0=x0+8; mx1=x1-8; rx0=mx0+54
    xs=[mx0+(mx1-mx0)*(.18+.76*i/(NW-1)) for i in range(NW)]
    PS={}
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=ridge(D["lab"]+k,xs,[mh*min(1,y_/VMAX) for y_ in v],rx0,mx1,pb); fill_ridge(P,pb,*T[k]); PS[k]=P
    c.restoreState()
    for j,(k,v) in enumerate(reversed(D["bands"])):          # key, flush on the spine, front layer first
        cc,al,ed=T[k]; ly=pb+mh-6-j*8.5
        c.setFillColor(cc); c.rect(lx,ly+.3,4.5,4.5,fill=1,stroke=0)
        txt(lx+8,ly,BANDLAB[k],"PopM",5,col if k=="you" else mix(cc,TXT,.40))
    for i,x in enumerate(xs):                                  # each window: kickoff, Pacific; quarter lights
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,GR,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(col if q<lit else TRACK); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    # --- NOW: the gold line is where the week stands; the triangles are how much of each side has played ---
    done=0                                     # windows complete as of the data on this page (Wednesday: none)
    nx=rx0+(xs[0]-rx0)*.5 if done==0 else xs[done-1]+6
    nh=mh*.66; c.setStrokeColor(GOLDISH); c.setLineWidth(.8); c.line(nx,pb,nx,pb+nh)
    txt(nx,pb+nh+3,"nothing banked" if done==0 else "","Pop",4.6,GOLDISH,"c"); txt(nx,pb+nh+9.5,"NOW","PopB",5,GOLDISH,"c")
    pm=sum(D["me"]["cnt"][:done]); po=sum(D["op"]["cnt"][:done]); nm=sum(D["me"]["cnt"]); no=sum(D["op"]["cnt"])
    for side,(k,pl,nn) in ((-1,("you",pm,nm)),(1,("opp",po,no))):
        tx=nx+side*5.2; cc,al,ed=T[k]
        yt=max(ridge_at(PS[k],tx),ridge_at(PS["you"],tx) if k=="opp" else 0)+1.2
        dtri(tx,yt,5.2,4.6,cc,ed)
        cc2=col if k=="you" else mix(STEEL,TXT,.25); parts=((str(pl),"Bebas",7.6),(" of ","Pop",4.8),(str(nn),"Bebas",7.6))
        tw=sum(c.stringWidth(t,f,z) for t,f,z in parts); px=nx+side*2.6-(tw if side<0 else 0)
        for t,f,z in parts: px+=txt(px,yt+7.4,t,f,z,cc2)
    # --- one sentence, flush on the spine, behind the paper mark ---
    yb=bot+8; sw_=sheet(lx,yb,4.5,GR); sx=lx+sw_+4; fs=6.5
    while c.stringWidth(PROSE[D["lab"]],"Pop",fs)>x1-12-sx: fs-=.05
    txt(sx,yb,PROSE[D["lab"]],"Pop",fs,TXT)
    return dvx-br
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    # the four leagues under the title: Yahoo league name, a dot, the Dark Knight team in its league color
    cw=(W-2*M)/4; fs=6.6
    while max(c.stringWidth(FULL[l]+"  ·  ","PopM",fs)+c.stringWidth(TEAMN[l],"PopB",fs) for l in LG)>cw-8: fs-=.05
    for i,l in enumerate(LG):
        sx=M+i*cw; w=txt(sx,y-14,FULL[l]+"  ·  ","PopM",fs,GR); txt(sx+w,y-14,TEAMN[l],"PopB",fs,LC[l])
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    st_=f"Rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT  ·  Yahoo matchups, lineups, standings pulled Wed Sep 30 evening, a day old  ·  "
    wq="refresh before Sunday"
    xr=W-M-c.stringWidth(wq,"Pop",5.6); txt(W-M,y-24,wq,"Pop",5.6,GOLDISH,"r"); txt(xr,y-24,st_,"Pop",5.6,GR2,"r")
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-31,W,y-31)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-38-52-18
    GX=(idr+balll)/2-8
    top=y-42; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("WIN PROBABILITY: math on Yahoo's projections before anything is banked; Yahoo's own win % not yet pulled.  "
          "DIVISION, LEAGUE: places inside the glass, 1st at the top, fluid at your place; dotted line = the cut (win the division and you are in; league, 6th and 7th). DK IV: points-for rank.  "
          "MOUNTAIN: this week's projected points by kickoff window, Pacific, best lineups, one scale.  NOW: where the week stands; triangles = starters played, mine left, his right.")
    for j,l in enumerate(simpleSplit(foot,"Pop",4.6,W-2*M-120)): txt(W/2,38-j*5.8,l,"Pop",4.6,GR2,"c")
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v8","Bebas",10,GR,"r")
    c.save(); return DS,GX,idr

# ======================= v9 block (Thu Oct 1 night, Dom's voice walk of v8) =======================
# Identity: front slot under the tag = PROJECTED (always, bottom) with DIVISION GAME stacked above it
#   on division weeks; date stamp moves to the back after the bracket; third grey line gone.
# Mountain: gold NOW line and "nothing banked" gone. Two down-pointing triangles pinned to their own
#   ridges at the last finished window; over each, points banked (big, own color) on top of starters
#   played (small grey). Bare counts, print at zero. Layer key drops to the caption row, "MINE" gone.
# Caption: one line, grey, smaller, starting where the mountain starts.
# Knockout halo (page background) on every mark the mountain can rise behind.
# Balls: level scale, fluid fills from 1st DOWN to your place, cut line dead, big ordinal, 3D glass.
BANDLAB={"league":"LEAGUE AVG","division":"DIVISION AVG","top six":"TOP-SIX AVG","opp":"OPPONENT"}
ACT={}            # points banked per league per finished window: {lab:{"me":[..],"op":[..]}}; empty until a refresh
HALO=BG
def htxt(x,y,s,f,sz,col=TXT,al="l",hw=1.8):
    """text with a page-background knockout around it, so nothing behind can swallow it"""
    w=c.stringWidth(s,f,sz); x0=x-w if al=="r" else x-w/2 if al=="c" else x
    t=c.beginText(x0,y); t.setFont(f,sz); t.setTextRenderMode(1); t.textOut(s)
    c.saveState(); c.setStrokeColor(HALO); c.setLineWidth(hw); c.setLineJoin(1); c.drawText(t); c.restoreState()
    txt(x0,y,s,f,sz,col); return w
_gauge8=gauge
def gauge(cx,cy,r,v,col,big=True,ghost=None):
    sw=r*20/78
    c.setLineCap(0); c.setStrokeColor(HALO); c.setLineWidth(sw+3.2); c.arc(cx-r,cy-r,cx+r,cy+r,-1.5,183)
    c.setFillColor(HALO); c.circle(cx,cy,max(2.2,r*.1)+1.6,fill=1,stroke=0)
    _gauge8(cx,cy,r,v,col,big,ghost)
def dtri(x,ytip,w,hh,fill,edge):
    p=c.beginPath(); p.moveTo(x-w/2,ytip+hh); p.lineTo(x+w/2,ytip+hh); p.lineTo(x,ytip); p.close()
    c.setLineJoin(1); c.setStrokeColor(HALO); c.setLineWidth(2.4); c.drawPath(p,fill=0,stroke=1)
    c.setFillColor(fill); c.setStrokeColor(edge); c.setLineWidth(.7); c.drawPath(p,fill=1,stroke=1); c.setLineJoin(0)
def ordinal(cx,yb,n,fs,col):
    num=str(n); suf='th' if 10<=n%100<=20 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th'); ss=fs*.38
    wn=c.stringWidth(num,"Bebas",fs); ws=c.stringWidth(suf,"PopB",ss); x=cx-(wn+.7+ws)/2
    htxt(x,yb,num,"Bebas",fs,col,hw=2.2); htxt(x+wn+.7,yb+fs*CAP-ss*.72,suf,"PopB",ss,col,hw=1.6)
def ring(cx,cy,r,n,me,cut,col,lab):
    fm=lambda u: .09+.82*u                                   # places use the inner 82% of the glass
    yk=lambda k: cy-r+2*r*fm((n-k+.5)/n)                     # centre of place k, 1st at the top, dead level
    yfl=cy-r+2*r*fm((n-me)/n)                                # lower edge of the fluid = bottom of your place
    c.saveState(); c.setFillColor(BG); c.setFillAlpha(.6); c.ellipse(cx-r*.82,cy-r-3.6,cx+r*.82,cy-r+1.2,fill=1,stroke=0); c.restoreState()
    c.saveState(); p=c.beginPath(); p.circle(cx,cy,r); c.clipPath(p,stroke=0)
    # glass: a lit sphere, bright upper left, falling to a steel rim
    c.radialGradient(cx-r*.38,cy+r*.42,r*1.75,(mix(TXT,BG2,.06),mix(STEEL,BG2,.15),mix(STEEL,BG2,.62)),(0,.55,1),extend=True)
    # fluid hangs from the top of the glass down to your place, flat lower surface
    c.saveState(); q=c.beginPath(); q.rect(cx-r-1,yfl,2*r+2,cy+r-yfl+1); c.clipPath(q,stroke=0)
    c.radialGradient(cx-r*.30,cy+r*.45,r*1.7,(mix(col,TXT,.38),col,mix(col,BG,.45)),(0,.5,1),extend=True)
    c.restoreState()
    c.setStrokeColor(mix(col,TXT,.55)); c.setLineWidth(.8); c.line(cx-r,yfl,cx+r,yfl)     # meniscus
    c.setStrokeColor(mix(col,BG,.55)); c.setLineWidth(.5); c.line(cx-r,yfl-.7,cx+r,yfl-.7)
    for i in range(7):                                       # rim shading: the edge falls away
        c.saveState(); c.setStrokeColor(BG); c.setStrokeAlpha(.07); c.setLineWidth(1.4); c.circle(cx,cy,r-.3-i*.75,fill=0,stroke=1); c.restoreState()
    # the scale, level, down the inside left edge
    LB=scalelabels(n)
    for k in range(1,n+1):
        y=yk(k); dy=y-cy; xe=cx-math.sqrt(max(0,r*r-dy*dy))+1.2
        sc=mix(BG,col,.12) if y>=yfl else mix(BG,STEEL,.20)
        tl=2.6 if k in LB else 1.5
        c.setStrokeColor(sc); c.setLineWidth(.45); c.line(xe,y,xe+tl,y)
        if k in LB: txt(xe+tl+.9,y-1.1,str(k),"PopB",3.2,sc)
    # gloss: a soft sheen and a sharp specular point, upper left; a faint bounce light lower right
    c.saveState(); c.setFillColor(TXT); c.setFillAlpha(.30); c.ellipse(cx-r*.42,cy+r*.36,cx+r*.12,cy+r*.74,fill=1,stroke=0)
    c.setFillAlpha(.75); c.ellipse(cx-r*.30,cy+r*.52,cx-r*.10,cy+r*.66,fill=1,stroke=0)
    c.setFillAlpha(.10); c.ellipse(cx+r*.15,cy-r*.86,cx+r*.70,cy-r*.60,fill=1,stroke=0); c.restoreState()
    c.restoreState()
    c.setStrokeColor(mix(col,BG2,.25)); c.setLineWidth(.9); c.circle(cx,cy,r,fill=0,stroke=1)
    fs=r*1.12; ordinal(cx+r*.08,cy-fs*CAP/2,me,fs,TXT)
    return cy+r+6
def idwidth(D):
    f=lambda s,fn,sz: c.stringWidth(s,fn,sz)
    l1=f(D["lab"],"Bebas",24)+6+f(D["rec"],"Bebas",16)+f("  vs  ","PopM",7)+f(f"{D['oppname'].upper()} {D['opprec']}","Bebas",16)
    vs=f(D["lab"],"Bebas",24)+6+f(D["rec"],"Bebas",16)+f("  vs  ","PopM",7)
    l2=vs+f(f"{D['yo']:.1f}","Bebas",15)+5+f(f"({D['ym']-D['yo']:+.1f})","Bebas",12)+6+f(YDATE,"PopM",5.4)
    return max(l1,l2)
YDATE="Wed Sep 30"
def block(D,top,h,VMAX,GX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h; T=tints(col)
    c.setFillColor(BG2); c.roundRect(x0,bot,x1-x0,h,5,fill=1,stroke=0)
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    lx=x0+12; TL=top-12
    # --- the mountain first, so every mark above it lands on top ---
    gr=30; sw=gr*20/78; gy=TL-(5.2*CAP)-(gr+sw/2+5.5-2)
    pb=bot+31; mh=min(46,(gy-31)-pb); mx0=x0+8; mx1=x1-8; rx0=mx0+54
    xs=[mx0+(mx1-mx0)*(.18+.76*i/(NW-1)) for i in range(NW)]
    PS={}
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=ridge(D["lab"]+k,xs,[mh*min(1,y_/VMAX) for y_ in v],rx0,mx1,pb); fill_ridge(P,pb,*T[k]); PS[k]=P
    c.restoreState()
    for i,x in enumerate(xs):
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,GR,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(col if q<lit else TRACK); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    # --- the gauge ---
    gauge(GX,gy,gr,D["pct"],col)
    htxt(GX,gy-17.5,f"{D['pct']}%","Bebas",17,TXT,"c",hw=2.4)
    htxt(GX,gy-25,"WIN PROBABILITY","PopB",5.8,TXT,"c",hw=1.6)
    # --- identity column ---
    y=TL-24*CAP
    w=txt(lx,y,D["lab"],"Bebas",24,col); w+=6
    w+=txt(lx+w,y,D["rec"],"Bebas",16,TXT); vs0=lx+w
    w+=txt(lx+w,y,"  vs  ","PopM",7,GR); vs1=lx+w
    txt(lx+w,y,f"{D['oppname'].upper()} {D['opprec']}","Bebas",16,TXT)
    y2=y-18
    wm=txt(vs0,y2,f"{D['ym']:.1f}","Bebas",15,col,"r"); txt(vs0,y2,"  vs  ","PopM",7,GR)
    w=vs1+txt(vs1,y2,f"{D['yo']:.1f}","Bebas",15,OPPC)
    w+=5+txt(w+5,y2,f"({D['ym']-D['yo']:+.1f})","Bebas",12,TXT)
    txt(w+6,y2+.6,YDATE,"PopM",5.4,GR)
    # front slot: PROJECTED always on the number's baseline; DIVISION GAME stacked above on division weeks
    ls=LS
    txt(lx,y2+.4,"PROJECTED","PopB",ls,GR)
    if D["oppdiv"]: txt(lx,y2+.4+ls*1.25,"DIVISION GAME","PopB",ls,GR)
    # --- standings ---
    br=18; lgx=x1-38; dvx=lgx-52; ry=TL-6.4*CAP-6-br
    dn,dp,dlab,dsub=D["dv"]
    ring(dvx,ry,br,dn,dp,None,col,dlab)
    ring(lgx,ry,br,D["n"],D["rank"],None,col,"LEAGUE")
    for x,l in ((dvx,dlab),(lgx,"LEAGUE")): txt(x,TL-6.4*CAP,l,"PopB",6.4,TXT,"c")
    # --- the pair: pinned to their own ridges at the last finished window ---
    done=0                                     # windows complete as of the data on this page (Wednesday: none)
    nx=rx0+(xs[0]-rx0)*.5 if done==0 else xs[done-1]
    a=ACT.get(D["lab"]); assert done==0 or a, "banked points needed before the pair can move"
    pm=sum(a["me"][:done]) if done else 0.0; po=sum(a["op"][:done]) if done else 0.0
    cm=sum(D["me"]["cnt"][:done]); co=sum(D["op"]["cnt"][:done])
    for side,k,pts,cn in ((-1,"you",pm,cm),(1,"opp",po,co)):
        tx=nx+side*6.0; cc,al,ed=T[k]
        yt=(ridge_at(PS[k],tx) if done else pb)+1.0          # nothing banked: both sit on the floor
        dtri(tx,yt,5.6,5.0,cc,ed)
        ax=tx-side*2.8; aa="r" if side<0 else "l"             # labels open outward from the pair, never collide
        htxt(ax,yt+7.4,str(cn),"PopB",4.8,GR,aa,hw=1.4)
        htxt(ax,yt+13.4,f"{pts:.1f}","Bebas",10,col if k=="you" else mix(STEEL,TXT,.30),aa,hw=2.0)
    # --- layer key on the spine, bottom entry level with the caption ---
    yb=bot+8; ks=[k for k,v in reversed(D["bands"]) if k!="you"]
    for j,k in enumerate(ks):
        cc,al,ed=T[k]; ly=yb+j*7.2
        c.setFillColor(cc); c.rect(lx,ly+.2,4.2,4.2,fill=1,stroke=0)
        txt(lx+7,ly,BANDLAB[k],"PopM",4.7,mix(cc,TXT,.40))
    # --- the caption: one line, grey, from where the mountain starts ---
    sw_=sheet(rx0,yb,4.2,GR); sx=rx0+sw_+3.5; fs=5.8
    while c.stringWidth(PROSE[D["lab"]],"Pop",fs)>x1-12-sx: fs-=.05
    txt(sx,yb,PROSE[D["lab"]],"Pop",fs,GR)
    return dvx-br
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    cw=(W-2*M)/4; fs=6.6
    while max(c.stringWidth(FULL[l]+"  ·  ","PopM",fs)+c.stringWidth(TEAMN[l],"PopB",fs) for l in LG)>cw-8: fs-=.05
    for i,l in enumerate(LG):
        sx=M+i*cw; w=txt(sx,y-14,FULL[l]+"  ·  ","PopM",fs,GR); txt(sx+w,y-14,TEAMN[l],"PopB",fs,LC[l])
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    st_=f"Rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT  ·  Yahoo matchups, lineups, standings pulled Wed Sep 30 evening, a day old  ·  "
    wq="refresh before Sunday"
    xr=W-M-c.stringWidth(wq,"Pop",5.6); txt(W-M,y-24,wq,"Pop",5.6,GOLDISH,"r"); txt(xr,y-24,st_,"Pop",5.6,GR2,"r")
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-31,W,y-31)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-38-52-18
    GX=(idr+balll)/2-8
    top=y-42; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=5.4                          # one front-slot label size for all four blocks, set by the tightest
    def _room(D):
        w=c.stringWidth(D["lab"],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-5
    while any(c.stringWidth("DIVISION GAME" if D["oppdiv"] else "PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED: Yahoo projections, pulled Wed Sep 30.  WIN PROBABILITY: math on those projections before anything is banked; Yahoo's own win % not yet pulled.  "
          "DIVISION, LEAGUE: places down the glass, 1st at the top; the fluid fills from 1st down to your place. DK IV: points-for rank.  "
          "MOUNTAIN: this week's projected points by kickoff window, Pacific, best lineups, one scale.  TRIANGLES: at the last finished window, on each side's own layer, mine left, his right; large = points banked, small = starters played.")
    for j,l in enumerate(simpleSplit(foot,"Pop",4.6,W-2*M-120)): txt(W/2,38-j*5.8,l,"Pop",4.6,GR2,"c")
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v9","Bebas",10,GR,"r")
    c.save(); return DS,GX,idr

# ======================= v10 block (Thu Oct 1 night, Dom's voice walk of v9) =======================
# Balls: division (and DK IV points-for) fluid rises from the BOTTOM; league fluid hangs from the TOP.
#   Where blue meets grey is the qualifying cut (division: under 1st; league: under 6th) - no drawn line.
#   The surface is a gentle wave. The ordinal carries your place; your place is lit on the scale.
# Gauge: graduated tick ring, league-color glow under the fill, recessed inner shadow, hatched empty arc.
#   Centered between the identity text and the division ball, one position for all four blocks.
# Identity: per-block date dead; PROJECTED enlarged to fill the front slot; DIVISION GAME on its own row beneath.
# Layer key: floats above the mountain floor, OPPONENT on top, clear of the caption row.
# Header: sources under DARK KNIGHT FANTASY, pulled + rebuilt under WEEK 4, league names larger, spread edge to edge.
GCUT={"DIVISION":1,"POINTS FOR":1,"LEAGUE":6}       # place a team must hold to qualify; DK IV points-for borrows the division rule
def _surf(cx,y0,r,x):
    return y0+r*.045*math.sin((x-cx)/r*math.pi*1.6+.7)+r*.022*math.sin((x-cx)/r*math.pi*3.9)
def ring(cx,cy,r,n,me,cut,col,lab):
    up=lab!="LEAGUE"; k=GCUT.get(lab,1)
    fm=lambda u: .09+.82*u
    yk=lambda q: cy-r+2*r*fm((n-q+.5)/n)
    yb=cy-r+2*r*fm((n-k)/n)                                  # boundary just under the qualifying place
    xs=[cx-r-1+i*(2*r+2)/48 for i in range(49)]
    c.saveState(); c.setFillColor(BG); c.setFillAlpha(.6); c.ellipse(cx-r*.82,cy-r-3.6,cx+r*.82,cy-r+1.2,fill=1,stroke=0); c.restoreState()
    c.saveState(); p=c.beginPath(); p.circle(cx,cy,r); c.clipPath(p,stroke=0)
    c.radialGradient(cx-r*.38,cy+r*.42,r*1.75,(mix(TXT,BG2,.06),mix(STEEL,BG2,.15),mix(STEEL,BG2,.62)),(0,.55,1),extend=True)
    c.saveState(); q=c.beginPath(); q.moveTo(xs[0],_surf(cx,yb,r,xs[0]))
    for x in xs[1:]: q.lineTo(x,_surf(cx,yb,r,x))
    ye=cy-r-2 if up else cy+r+2
    q.lineTo(xs[-1],ye); q.lineTo(xs[0],ye); q.close(); c.clipPath(q,stroke=0)
    c.radialGradient(cx-r*.30,cy+r*.45,r*1.7,(mix(col,TXT,.38),col,mix(col,BG,.45)),(0,.5,1),extend=True)
    c.restoreState()
    def wline(dy,colr,lw):
        pp=c.beginPath(); pp.moveTo(xs[0],_surf(cx,yb,r,xs[0])+dy)
        for x in xs[1:]: pp.lineTo(x,_surf(cx,yb,r,x)+dy)
        c.setStrokeColor(colr); c.setLineWidth(lw); c.drawPath(pp,fill=0,stroke=1)
    wline(0,mix(col,TXT,.55),.8)                              # meniscus on the fluid's open face
    wline(-.7 if up else .7,mix(col,BG,.5),.45)
    for i in range(7):
        c.saveState(); c.setStrokeColor(BG); c.setStrokeAlpha(.07); c.setLineWidth(1.4); c.circle(cx,cy,r-.3-i*.75,fill=0,stroke=1); c.restoreState()
    LB=scalelabels(n)|{me}
    for q_ in range(1,n+1):
        y=yk(q_); dy=y-cy; xe=cx-math.sqrt(max(0,r*r-dy*dy))+1.2
        inf=(y<yb) if up else (y>yb)
        sc=mix(BG,col,.12) if inf else mix(BG,STEEL,.20)
        if q_==me: sc=TXT
        tl=3.4 if q_==me else 2.6 if q_ in LB else 1.5
        c.setStrokeColor(sc); c.setLineWidth(.6 if q_==me else .45); c.line(xe,y,xe+tl,y)
        if q_ in LB: txt(xe+tl+.9,y-1.1,str(q_),"PopB",3.2,sc)
    c.saveState(); c.setFillColor(TXT); c.setFillAlpha(.30); c.ellipse(cx-r*.42,cy+r*.36,cx+r*.12,cy+r*.74,fill=1,stroke=0)
    c.setFillAlpha(.75); c.ellipse(cx-r*.30,cy+r*.52,cx-r*.10,cy+r*.66,fill=1,stroke=0)
    c.setFillAlpha(.10); c.ellipse(cx+r*.15,cy-r*.86,cx+r*.70,cy-r*.60,fill=1,stroke=0); c.restoreState()
    c.restoreState()
    c.setStrokeColor(mix(col,BG2,.25)); c.setLineWidth(.9); c.circle(cx,cy,r,fill=0,stroke=1)
    fs=r*1.12; ordinal(cx+r*.08,cy-fs*CAP/2,me,fs,TXT)
    return cy+r+6
GLAB=8.5                                                    # label radius beyond the arc's outer edge
def gauge(cx,cy,r,v,col,big=True,ghost=None):
    sw0=r*20/78; ro=r+sw0/2; sw=sw0*1.38; ri=ro-sw; rc=(ro+ri)/2; vv=min(max(v,0),99.9)   # v37: band thickened inward, outer edge fixed
    def pt(t,rr): a=math.pi*(1-t/100); return cx+rr*math.cos(a), cy+rr*math.sin(a)
    c.setLineCap(0)
    c.setStrokeColor(HALO); c.setLineWidth(sw+12); c.arc(cx-rc-2,cy-rc-2,cx+rc+2,cy+rc+2,-3,186)       # knockout under the whole dial
    c.setFillColor(HALO); c.circle(cx,cy,max(2.2,r*.1)+1.8,fill=1,stroke=0)
    c.saveState()                                            # glow under the filled portion
    for i in range(5,0,-1):
        c.setStrokeColor(col); c.setStrokeAlpha(.055); c.setLineWidth(sw+i*1.5); c.arc(cx-rc,cy-rc,cx+rc,cy+rc,180-1.8*vv,1.8*vv)
    c.restoreState()
    c.setStrokeColor(TRACK); c.setLineWidth(sw); c.arc(cx-rc,cy-rc,cx+rc,cy+rc,0,180)
    c.saveState()                                            # faint hatch on the unfilled arc
    a0=math.pi*(1-vv/100); p=c.beginPath(); N=40
    for i in range(N+1):
        a=a0*(1-i/N); x,y=cx+ro*math.cos(a),cy+ro*math.sin(a); (p.moveTo if i==0 else p.lineTo)(x,y)
    for i in range(N+1):
        a=a0*i/N; p.lineTo(cx+ri*math.cos(a),cy+ri*math.sin(a))
    p.close(); c.clipPath(p,stroke=0)
    c.setStrokeColor(mix(TRACK,TXT,.13)); c.setLineWidth(.35)
    d=-ro
    while d<3*ro: c.line(cx-ro+d,cy-1,cx-ro+d+ro+2,cy+ro+1); d+=2.3
    c.restoreState()
    if vv>0:
        c.setStrokeColor(col); c.setLineWidth(sw); c.arc(cx-rc,cy-rc,cx+rc,cy+rc,180-1.8*vv,1.8*vv)
        # v37 (Dom): ruled lines that follow the arc - darkest and heaviest at the inner edge, lightening outward,
        # so the band carries structure even when the page is full of the same color
        c.saveState()
        for f_,lw_,al_ in ((.13,1.0,.62),(.33,.78,.44),(.53,.58,.28),(.73,.40,.15)):
            rr_=ri+sw*f_; c.setStrokeColor(BG); c.setStrokeAlpha(al_); c.setLineWidth(lw_)
            c.arc(cx-rr_,cy-rr_,cx+rr_,cy+rr_,180-1.8*vv,1.8*vv)
        c.restoreState()
        c.setStrokeColor(mix(col,TXT,.45)); c.setLineWidth(.8); c.arc(cx-ro+.6,cy-ro+.6,cx+ro-.6,cy+ro-.6,180-1.8*vv,1.8*vv)
    c.saveState(); c.setStrokeColor(BG); c.setStrokeAlpha(.55); c.setLineWidth(1.6)      # recessed: shadow along the inner edge
    c.arc(cx-ri+.8,cy-ri+.8,cx+ri-.8,cy+ri-.8,0,180); c.restoreState()
    c.setStrokeColor(BG2); c.setLineWidth(max(1.2,sw*.15))
    for t in (25,50,75): c.line(*pt(t,ri-.5),*pt(t,ro+.5))
    for t in range(0,101,5):                                 # graduated ring
        lng=t%25==0; c.setStrokeColor(mix(col,TXT,.25) if t<=vv else GR2); c.setLineWidth(.55 if lng else .35)
        c.line(*pt(t,ro+1.6),*pt(t,ro+(4.8 if lng else 3.2)))
    if big:
        x,y=pt(50,ro+GLAB); txt(x,y-2,"50","Pop",5.2,GR,"c")
        txt(cx-ro-6.2,cy-1.8,"0","Pop",5.2,GR,"r"); txt(cx+ro+6.2,cy-1.8,"100","Pop",5.2,GR,"l")
    if ghost is not None:
        x,y=pt(ghost,r*.96); c.setDash(3,2); c.setStrokeColor(GR); c.setLineWidth(1.2); c.line(cx,cy,x,y); c.setDash()
    x,y=pt(vv,r*1.02); c.setLineCap(1); c.setStrokeColor(TXT); c.setLineWidth(max(1.6,r*.07)); c.line(cx,cy,x,y)
    hr=max(2.2,r*.1); c.setFillColor(col); c.circle(cx,cy,hr+.9,fill=1,stroke=0); c.setFillColor(TXT); c.circle(cx,cy,hr,fill=1,stroke=0); c.setLineCap(0)
def idwidth(D):
    f=lambda s,fn,sz: c.stringWidth(s,fn,sz)
    vs=f(D["lab"],"Bebas",16)+6+f(D["rec"],"Bebas",16)+f("  vs  ","PopM",7)
    l1=vs+f(f"{D['oppname'].upper()} {D['opprec']}","Bebas",16)
    l2=vs+f(f"{D['yo']:.1f}","Bebas",15)+5+f(f"({D['ym']-D['yo']:+.1f})","Bebas",12)
    return max(l1,l2)
def block(D,top,h,VMAX,GX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h; T=tints(col)
    c.setFillColor(BG2); c.roundRect(x0,bot,x1-x0,h,5,fill=1,stroke=0)
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    lx=x0+12; TL=top-12
    gr=30; sw=gr*20/78; gy=TL-(5.2*CAP)-(gr+sw/2+GLAB-2)
    pb=bot+31; mh=min(46,(gy-31)-pb); mx0=x0+8; mx1=x1-8; rx0=mx0+54
    xs=[mx0+(mx1-mx0)*(.18+.76*i/(NW-1)) for i in range(NW)]
    PS={}
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=ridge(D["lab"]+k,xs,[mh*min(1,y_/VMAX) for y_ in v],rx0,mx1,pb); fill_ridge(P,pb,*T[k]); PS[k]=P
    c.restoreState()
    for i,x in enumerate(xs):
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,GR,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(col if q<lit else TRACK); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    gauge(GX,gy,gr,D["pct"],col)
    htxt(GX,gy-17.5,f"{D['pct']}%","Bebas",17,TXT,"c",hw=2.4)
    htxt(GX,gy-25,"WIN PROBABILITY","PopB",5.8,TXT,"c",hw=1.6)
    y=TL-24*CAP
    w=txt(lx,y,D["lab"],"Bebas",24,col); w+=6
    w+=txt(lx+w,y,D["rec"],"Bebas",16,TXT); vs0=lx+w
    w+=txt(lx+w,y,"  vs  ","PopM",7,GR); vs1=lx+w
    txt(lx+w,y,f"{D['oppname'].upper()} {D['opprec']}","Bebas",16,TXT)
    y2=y-18
    txt(vs0,y2,f"{D['ym']:.1f}","Bebas",15,col,"r"); txt(vs0,y2,"  vs  ","PopM",7,GR)
    w=vs1+txt(vs1,y2,f"{D['yo']:.1f}","Bebas",15,OPPC)
    txt(w+5,y2,f"({D['ym']-D['yo']:+.1f})","Bebas",12,TXT)
    txt(lx,y2,"PROJECTED","PopB",LS,GR)                      # fills the front slot, on the number's baseline
    if D["oppdiv"]: txt(lx,y2-LS*1.45,"DIVISION GAME","PopB",LS,GR)
    br=18; lgx=x1-38; dvx=lgx-52; ry=TL-6.4*CAP-6-br
    dn,dp,dlab,dsub=D["dv"]
    ring(dvx,ry,br,dn,dp,None,col,dlab)
    ring(lgx,ry,br,D["n"],D["rank"],None,col,"LEAGUE")
    for x,l in ((dvx,dlab),(lgx,"LEAGUE")): txt(x,TL-6.4*CAP,l,"PopB",6.4,TXT,"c")
    done=0
    nx=rx0+(xs[0]-rx0)*.5 if done==0 else xs[done-1]
    a=ACT.get(D["lab"]); assert done==0 or a, "banked points needed before the pair can move"
    pm=sum(a["me"][:done]) if done else 0.0; po=sum(a["op"][:done]) if done else 0.0
    cm=sum(D["me"]["cnt"][:done]); co=sum(D["op"]["cnt"][:done])
    for side,k,pts,cn in ((-1,"you",pm,cm),(1,"opp",po,co)):
        tx=nx+side*6.0; cc,al,ed=T[k]
        yt=(ridge_at(PS[k],tx) if done else pb)+1.0
        dtri(tx,yt,5.6,5.0,cc,ed)
        ax=tx-side*2.8; aa="r" if side<0 else "l"
        htxt(ax,yt+7.4,str(cn),"PopB",4.8,GR,aa,hw=1.4)
        htxt(ax,yt+13.4,f"{pts:.1f}","Bebas",10,col if k=="you" else mix(STEEL,TXT,.30),aa,hw=2.0)
    # layer key: floats above the floor line, OPPONENT on top, out of the caption row
    ks=[k for k,v in reversed(D["bands"]) if k!="you"]; kb=pb+4
    for j,k in enumerate(ks):
        cc,al,ed=T[k]; ly=kb+(len(ks)-1-j)*7.0
        c.setFillColor(cc); c.rect(lx,ly+.2,4.2,4.2,fill=1,stroke=0)
        txt(lx+7,ly,BANDLAB[k],"PopM",4.7,mix(cc,TXT,.40))
    yb=bot+8
    sw_=sheet(rx0,yb,4.2,GR); sx=rx0+sw_+3.5; fs=5.8
    while c.stringWidth(PROSE[D["lab"]],"Pop",fs)>x1-12-sx: fs-=.05
    txt(sx,yb,PROSE[D["lab"]],"Pop",fs,GR)
    return dvx-br
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    # second row: sources left, ages right
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Yahoo matchups, lineups, standings  ·  ","Pop",sf,GR2); txt(M+w,y2,"refresh before Sunday","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Yahoo pulled Wed Sep 30 evening  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    # third row: the four leagues, larger, spread edge to edge, sitting on the rule
    span=W-2*M; fs=10.0
    fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-38-52-18
    GX=(idr+balll)/2
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(D["lab"],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED: Yahoo projections, pulled Wed Sep 30.  WIN PROBABILITY: math on those projections before anything is banked; Yahoo's own win % not yet pulled.  "
          "DIVISION, LEAGUE: the number is your place, 1st at the top; where blue meets grey is the cut, under 1st (division) and 6th (league). DK IV: points-for rank.  "
          "MOUNTAIN: this week's projected points by kickoff window, Pacific, best lineups, one scale.  TRIANGLES: at the last finished window, on each side's own layer, mine left, his right; large = points banked, small = starters played.")
    for j,l in enumerate(simpleSplit(foot,"Pop",4.6,W-2*M-120)): txt(W/2,38-j*5.8,l,"Pop",4.6,GR2,"c")
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v10","Bebas",10,GR,"r")
    print("LS",round(LS,2),"LGFS",round(LGFS,2))
    c.save(); return DS,GX,idr

# ======================= v11 block (Thu Oct 1 night, Dom's voice walk of v10) =======================
# Balls: the fluid surface sits on YOUR place (division rises from the bottom, league hangs from the top).
#   The cut is a drawn white line across the glass on the qualifying place: 1st (division), 6th (league).
#   Reach the line and you're in; the gap between surface and line is how far you are from qualifying.
# Gauge: eight points left of v10.
def ring(cx,cy,r,n,me,cut,col,lab):
    up=lab!="LEAGUE"; k=GCUT.get(lab,1)
    fm=lambda u: .09+.82*u
    yk=lambda q: cy-r+2*r*fm((n-q+.5)/n)
    yb=yk(me)                                                # fluid surface sits on YOUR place
    ycut=yk(k)                                               # the cut: drawn line across the glass on the qualifying place
    xs=[cx-r-1+i*(2*r+2)/48 for i in range(49)]
    c.saveState(); c.setFillColor(BG); c.setFillAlpha(.6); c.ellipse(cx-r*.82,cy-r-3.6,cx+r*.82,cy-r+1.2,fill=1,stroke=0); c.restoreState()
    c.saveState(); p=c.beginPath(); p.circle(cx,cy,r); c.clipPath(p,stroke=0)
    c.radialGradient(cx-r*.38,cy+r*.42,r*1.75,(mix(TXT,BG2,.06),mix(STEEL,BG2,.15),mix(STEEL,BG2,.62)),(0,.55,1),extend=True)
    c.saveState(); q=c.beginPath(); q.moveTo(xs[0],_surf(cx,yb,r,xs[0]))
    for x in xs[1:]: q.lineTo(x,_surf(cx,yb,r,x))
    ye=cy-r-2 if up else cy+r+2
    q.lineTo(xs[-1],ye); q.lineTo(xs[0],ye); q.close(); c.clipPath(q,stroke=0)
    c.radialGradient(cx-r*.30,cy+r*.45,r*1.7,(mix(col,TXT,.38),col,mix(col,BG,.45)),(0,.5,1),extend=True)
    c.restoreState()
    def wline(dy,colr,lw):
        pp=c.beginPath(); pp.moveTo(xs[0],_surf(cx,yb,r,xs[0])+dy)
        for x in xs[1:]: pp.lineTo(x,_surf(cx,yb,r,x)+dy)
        c.setStrokeColor(colr); c.setLineWidth(lw); c.drawPath(pp,fill=0,stroke=1)
    wline(0,mix(col,TXT,.55),.8)                              # meniscus on the fluid's open face
    wline(-.7 if up else .7,mix(col,BG,.5),.45)
    for i in range(7):
        c.saveState(); c.setStrokeColor(BG); c.setStrokeAlpha(.07); c.setLineWidth(1.4); c.circle(cx,cy,r-.3-i*.75,fill=0,stroke=1); c.restoreState()
    LB=scalelabels(n)|{me}
    LB=(LB-{k-1,k+1,me-1,me+1})|{me,k}                     # keep the cut and your place labels clear of neighbours
    for q_ in range(1,n+1):
        y=yk(q_); dy=y-cy; xe=cx-math.sqrt(max(0,r*r-dy*dy))+1.2
        inf=(y<yb) if up else (y>yb)
        sc=mix(BG,col,.12) if inf else mix(BG,STEEL,.20)
        if q_==me: sc=TXT
        if q_==k: sc=TXT
        tl=3.4 if q_ in (me,k) else 2.6 if q_ in LB else 1.5
        c.setStrokeColor(sc); c.setLineWidth(.6 if q_==me else .45); c.line(xe,y,xe+tl,y)
        if q_ in LB: txt(xe+tl+.9,y-1.1,str(q_),"PopB",3.2,sc)
    dy=ycut-cy; hx=math.sqrt(max(0,r*r-dy*dy)); xl=cx-hx+1.2+3.4+.9+c.stringWidth(str(k),"PopB",3.2)+1.4
    c.setLineCap(0); c.setStrokeColor(BG); c.setStrokeAlpha(.55); c.setLineWidth(1.9); c.line(xl,ycut,cx+hx,ycut)
    c.setStrokeAlpha(1); c.setStrokeColor(TXT); c.setLineWidth(.75); c.line(xl,ycut,cx+hx,ycut)
    c.saveState(); c.setFillColor(TXT); c.setFillAlpha(.30); c.ellipse(cx-r*.42,cy+r*.36,cx+r*.12,cy+r*.74,fill=1,stroke=0)
    c.setFillAlpha(.75); c.ellipse(cx-r*.30,cy+r*.52,cx-r*.10,cy+r*.66,fill=1,stroke=0)
    c.setFillAlpha(.10); c.ellipse(cx+r*.15,cy-r*.86,cx+r*.70,cy-r*.60,fill=1,stroke=0); c.restoreState()
    c.restoreState()
    c.setStrokeColor(mix(col,BG2,.25)); c.setLineWidth(.9); c.circle(cx,cy,r,fill=0,stroke=1)
    fs=r*1.12; ordinal(cx+r*.08,cy-fs*CAP/2,me,fs,TXT)
    return cy+r+6
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    # second row: sources left, ages right
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Yahoo matchups, lineups, standings  ·  ","Pop",sf,GR2); txt(M+w,y2,"refresh before Sunday","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Yahoo pulled Wed Sep 30 evening  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    # third row: the four leagues, larger, spread edge to edge, sitting on the rule
    span=W-2*M; fs=10.0
    fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-38-52-18
    GX=(idr+balll)/2-8                                       # Dom: eight points left of v10 (back to 356)
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(D["lab"],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED: Yahoo projections, pulled Wed Sep 30.  WIN PROBABILITY: math on those projections before anything is banked; Yahoo's own win % not yet pulled.  "
          "DIVISION, LEAGUE: the number is your place, 1st at the top; the fluid stops at your place; the white line is the cut, 1st (division), 6th (league). DK IV: points-for rank.  "
          "MOUNTAIN: this week's projected points by kickoff window, Pacific, best lineups, one scale.  TRIANGLES: at the last finished window, on each side's own layer, mine left, his right; large = points banked, small = starters played.")
    for j,l in enumerate(simpleSplit(foot,"Pop",4.6,W-2*M-120)): txt(W/2,38-j*5.8,l,"Pop",4.6,GR2,"c")
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v11","Bebas",10,GR,"r")
    print("LS",round(LS,2),"LGFS",round(LGFS,2))
    c.save(); return DS,GX,idr


# ======================= v12 block (Dom: footer runs margin to margin, justified, not centered) =======================
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    # second row: sources left, ages right
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Yahoo matchups, lineups, standings  ·  ","Pop",sf,GR2); txt(M+w,y2,"refresh before Sunday","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Yahoo pulled Wed Sep 30 evening  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    # third row: the four leagues, larger, spread edge to edge, sitting on the rule
    span=W-2*M; fs=10.0
    fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-38-52-18
    GX=(idr+balll)/2-8                                       # Dom: eight points left of v10 (back to 356)
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(D["lab"],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED: Yahoo projections, pulled Wed Sep 30.  WIN PROBABILITY: math on those projections before anything is banked; Yahoo's own win % not yet pulled.  "
          "DIVISION, LEAGUE: the number is your place, 1st at the top; the fluid stops at your place; the white line is the cut, 1st (division), 6th (league). DK IV: points-for rank.  "
          "MOUNTAIN: this week's projected points by kickoff window, Pacific, best lineups, one scale.  TRIANGLES: at the last finished window, on each side's own layer, mine left, his right; large = points banked, small = starters played.")
    FL=simpleSplit(foot,"Pop",4.6,W-2*M)
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=38-j*5.8
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",4.6,GR2); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",4.6) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",4.6,GR2); x_+=c.stringWidth(w,"Pop",4.6)+g
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v12","Bebas",10,GR,"r")
    print("LS",round(LS,2),"LGFS",round(LGFS,2))
    c.save(); return DS,GX,idr



# ======================= v13 block (Dom: meter 6 more points left; footer two sentences) =======================
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    # second row: sources left, ages right
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Yahoo matchups, lineups, standings  ·  ","Pop",sf,GR2); txt(M+w,y2,"refresh before Sunday","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Yahoo pulled Wed Sep 30 evening  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    # third row: the four leagues, larger, spread edge to edge, sitting on the rule
    span=W-2*M; fs=10.0
    fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-38-52-18
    GX=(idr+balll)/2-14                                      # Dom: eight points left of v10 (back to 356)
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(D["lab"],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED, WIN PROBABILITY and the MOUNTAIN run on Yahoo projections pulled Wed Sep 30 (best lineups, kickoff windows Pacific, one scale); Yahoo's own win % is not yet pulled.  "
          "In the balls the fluid stops at your place and the white line is the cut, 1st division and 6th league (DK IV left ball: points-for rank), and the TRIANGLES mark points banked (large) and starters played (small) at the last finished window, mine left, his right.")
    FL=simpleSplit(foot,"Pop",4.6,W-2*M)
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=38-j*5.8
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",4.6,GR2); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",4.6) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",4.6,GR2); x_+=c.stringWidth(w,"Pop",4.6)+g
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v13","Bebas",10,GR,"r")
    print("LS",round(LS,2),"LGFS",round(LGFS,2))
    c.save(); return DS,GX,idr




# ======================= v14 block (Dom: meniscus strokes removed, they competed with the cut line) =======================
def ring(cx,cy,r,n,me,cut,col,lab):
    up=lab!="LEAGUE"; k=GCUT.get(lab,1)
    fm=lambda u: .09+.82*u
    yk=lambda q: cy-r+2*r*fm((n-q+.5)/n)
    yb=yk(me)                                                # fluid surface sits on YOUR place
    ycut=yk(k)                                               # the cut: drawn line across the glass on the qualifying place
    xs=[cx-r-1+i*(2*r+2)/48 for i in range(49)]
    c.saveState(); c.setFillColor(BG); c.setFillAlpha(.6); c.ellipse(cx-r*.82,cy-r-3.6,cx+r*.82,cy-r+1.2,fill=1,stroke=0); c.restoreState()
    c.saveState(); p=c.beginPath(); p.circle(cx,cy,r); c.clipPath(p,stroke=0)
    c.radialGradient(cx-r*.38,cy+r*.42,r*1.75,(mix(TXT,BG2,.06),mix(STEEL,BG2,.15),mix(STEEL,BG2,.62)),(0,.55,1),extend=True)
    c.saveState(); q=c.beginPath(); q.moveTo(xs[0],_surf(cx,yb,r,xs[0]))
    for x in xs[1:]: q.lineTo(x,_surf(cx,yb,r,x))
    ye=cy-r-2 if up else cy+r+2
    q.lineTo(xs[-1],ye); q.lineTo(xs[0],ye); q.close(); c.clipPath(q,stroke=0)
    c.radialGradient(cx-r*.30,cy+r*.45,r*1.7,(mix(col,TXT,.38),col,mix(col,BG,.45)),(0,.5,1),extend=True)
    c.restoreState()
    def wline(dy,colr,lw):
        pp=c.beginPath(); pp.moveTo(xs[0],_surf(cx,yb,r,xs[0])+dy)
        for x in xs[1:]: pp.lineTo(x,_surf(cx,yb,r,x)+dy)
        c.setStrokeColor(colr); c.setLineWidth(lw); c.drawPath(pp,fill=0,stroke=1)
    for i in range(7):
        c.saveState(); c.setStrokeColor(BG); c.setStrokeAlpha(.07); c.setLineWidth(1.4); c.circle(cx,cy,r-.3-i*.75,fill=0,stroke=1); c.restoreState()
    LB=scalelabels(n)|{me}
    LB=(LB-{k-1,k+1,me-1,me+1})|{me,k}                     # keep the cut and your place labels clear of neighbours
    for q_ in range(1,n+1):
        y=yk(q_); dy=y-cy; xe=cx-math.sqrt(max(0,r*r-dy*dy))+1.2
        inf=(y<yb) if up else (y>yb)
        sc=mix(BG,col,.12) if inf else mix(BG,STEEL,.20)
        if q_==me: sc=TXT
        if q_==k: sc=TXT
        tl=3.4 if q_ in (me,k) else 2.6 if q_ in LB else 1.5
        c.setStrokeColor(sc); c.setLineWidth(.6 if q_==me else .45); c.line(xe,y,xe+tl,y)
        if q_ in LB: txt(xe+tl+.9,y-1.1,str(q_),"PopB",3.2,sc)
    dy=ycut-cy; hx=math.sqrt(max(0,r*r-dy*dy)); xl=cx-hx+1.2+3.4+.9+c.stringWidth(str(k),"PopB",3.2)+1.4
    c.setLineCap(0); c.setStrokeColor(BG); c.setStrokeAlpha(.55); c.setLineWidth(1.9); c.line(xl,ycut,cx+hx,ycut)
    c.setStrokeAlpha(1); c.setStrokeColor(TXT); c.setLineWidth(.75); c.line(xl,ycut,cx+hx,ycut)
    c.saveState(); c.setFillColor(TXT); c.setFillAlpha(.30); c.ellipse(cx-r*.42,cy+r*.36,cx+r*.12,cy+r*.74,fill=1,stroke=0)
    c.setFillAlpha(.75); c.ellipse(cx-r*.30,cy+r*.52,cx-r*.10,cy+r*.66,fill=1,stroke=0)
    c.setFillAlpha(.10); c.ellipse(cx+r*.15,cy-r*.86,cx+r*.70,cy-r*.60,fill=1,stroke=0); c.restoreState()
    c.restoreState()
    c.setStrokeColor(mix(col,BG2,.25)); c.setLineWidth(.9); c.circle(cx,cy,r,fill=0,stroke=1)
    fs=r*1.12; ordinal(cx+r*.08,cy-fs*CAP/2,me,fs,TXT)
    return cy+r+6
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    # second row: sources left, ages right
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Yahoo matchups, lineups, standings  ·  ","Pop",sf,GR2); txt(M+w,y2,"refresh before Sunday","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Yahoo pulled Wed Sep 30 evening  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    # third row: the four leagues, larger, spread edge to edge, sitting on the rule
    span=W-2*M; fs=10.0
    fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-38-52-18
    GX=(idr+balll)/2-14                                      # Dom: eight points left of v10 (back to 356)
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(D["lab"],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED, WIN PROBABILITY and the MOUNTAIN run on Yahoo projections pulled Wed Sep 30 (best lineups, kickoff windows Pacific, one scale); Yahoo's own win % is not yet pulled.  "
          "In the balls the fluid stops at your place and the white line is the cut, 1st division and 6th league (DK IV left ball: points-for rank), and the TRIANGLES mark points banked (large) and starters played (small) at the last finished window, mine left, his right.")
    FL=simpleSplit(foot,"Pop",4.6,W-2*M)
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=38-j*5.8
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",4.6,GR2); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",4.6) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",4.6,GR2); x_+=c.stringWidth(w,"Pop",4.6)+g
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v14","Bebas",10,GR,"r")
    print("LS",round(LS,2),"LGFS",round(LGFS,2))
    c.save(); return DS,GX,idr





# ======================= v15 block (Dom: projected gap green when ahead, red when behind) =======================
def block(D,top,h,VMAX,GX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h; T=tints(col)
    c.setFillColor(BG2); c.roundRect(x0,bot,x1-x0,h,5,fill=1,stroke=0)
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    lx=x0+12; TL=top-12
    gr=30; sw=gr*20/78; gy=TL-(5.2*CAP)-(gr+sw/2+GLAB-2)
    pb=bot+31; mh=min(46,(gy-31)-pb); mx0=x0+8; mx1=x1-8; rx0=mx0+54
    xs=[mx0+(mx1-mx0)*(.18+.76*i/(NW-1)) for i in range(NW)]
    PS={}
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=ridge(D["lab"]+k,xs,[mh*min(1,y_/VMAX) for y_ in v],rx0,mx1,pb); fill_ridge(P,pb,*T[k]); PS[k]=P
    c.restoreState()
    for i,x in enumerate(xs):
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,GR,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(col if q<lit else TRACK); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    gauge(GX,gy,gr,D["pct"],col)
    htxt(GX,gy-17.5,f"{D['pct']}%","Bebas",17,TXT,"c",hw=2.4)
    htxt(GX,gy-25,"WIN PROBABILITY","PopB",5.8,TXT,"c",hw=1.6)
    y=TL-24*CAP
    w=txt(lx,y,D["lab"],"Bebas",24,col); w+=6
    w+=txt(lx+w,y,D["rec"],"Bebas",16,TXT); vs0=lx+w
    w+=txt(lx+w,y,"  vs  ","PopM",7,GR); vs1=lx+w
    txt(lx+w,y,f"{D['oppname'].upper()} {D['opprec']}","Bebas",16,TXT)
    y2=y-18
    txt(vs0,y2,f"{D['ym']:.1f}","Bebas",15,col,"r"); txt(vs0,y2,"  vs  ","PopM",7,GR)
    w=vs1+txt(vs1,y2,f"{D['yo']:.1f}","Bebas",15,OPPC)
    _g=round(D['ym']-D['yo'],1); txt(w+5,y2,f"({_g:+.1f})","Bebas",12,UP if _g>0 else DN if _g<0 else TXT)
    txt(lx,y2,"PROJECTED","PopB",LS,GR)                      # fills the front slot, on the number's baseline
    if D["oppdiv"]: txt(lx,y2-LS*1.45,"DIVISION GAME","PopB",LS,GR)
    br=18; lgx=x1-38; dvx=lgx-52; ry=TL-6.4*CAP-6-br
    dn,dp,dlab,dsub=D["dv"]
    ring(dvx,ry,br,dn,dp,None,col,dlab)
    ring(lgx,ry,br,D["n"],D["rank"],None,col,"LEAGUE")
    for x,l in ((dvx,dlab),(lgx,"LEAGUE")): txt(x,TL-6.4*CAP,l,"PopB",6.4,TXT,"c")
    done=0
    nx=rx0+(xs[0]-rx0)*.5 if done==0 else xs[done-1]
    a=ACT.get(D["lab"]); assert done==0 or a, "banked points needed before the pair can move"
    pm=sum(a["me"][:done]) if done else 0.0; po=sum(a["op"][:done]) if done else 0.0
    cm=sum(D["me"]["cnt"][:done]); co=sum(D["op"]["cnt"][:done])
    for side,k,pts,cn in ((-1,"you",pm,cm),(1,"opp",po,co)):
        tx=nx+side*6.0; cc,al,ed=T[k]
        yt=(ridge_at(PS[k],tx) if done else pb)+1.0
        dtri(tx,yt,5.6,5.0,cc,ed)
        ax=tx-side*2.8; aa="r" if side<0 else "l"
        htxt(ax,yt+7.4,str(cn),"PopB",4.8,GR,aa,hw=1.4)
        htxt(ax,yt+13.4,f"{pts:.1f}","Bebas",10,col if k=="you" else mix(STEEL,TXT,.30),aa,hw=2.0)
    # layer key: floats above the floor line, OPPONENT on top, out of the caption row
    ks=[k for k,v in reversed(D["bands"]) if k!="you"]; kb=pb+4
    for j,k in enumerate(ks):
        cc,al,ed=T[k]; ly=kb+(len(ks)-1-j)*7.0
        c.setFillColor(cc); c.rect(lx,ly+.2,4.2,4.2,fill=1,stroke=0)
        txt(lx+7,ly,BANDLAB[k],"PopM",4.7,mix(cc,TXT,.40))
    yb=bot+8
    sw_=sheet(rx0,yb,4.2,GR); sx=rx0+sw_+3.5; fs=5.8
    while c.stringWidth(PROSE[D["lab"]],"Pop",fs)>x1-12-sx: fs-=.05
    txt(sx,yb,PROSE[D["lab"]],"Pop",fs,GR)
    return dvx-br
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    # second row: sources left, ages right
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Yahoo matchups, lineups, standings  ·  ","Pop",sf,GR2); txt(M+w,y2,"refresh before Sunday","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Yahoo pulled Wed Sep 30 evening  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    # third row: the four leagues, larger, spread edge to edge, sitting on the rule
    span=W-2*M; fs=10.0
    fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-38-52-18
    GX=(idr+balll)/2-14                                      # Dom: eight points left of v10 (back to 356)
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(D["lab"],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED, WIN PROBABILITY and the MOUNTAIN run on Yahoo projections pulled Wed Sep 30 (best lineups, kickoff windows Pacific, one scale); Yahoo's own win % is not yet pulled.  "
          "In the balls the fluid stops at your place and the white line is the cut, 1st division and 6th league (DK IV left ball: points-for rank), and the TRIANGLES mark points banked (large) and starters played (small) at the last finished window, mine left, his right.")
    FL=simpleSplit(foot,"Pop",4.6,W-2*M)
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=38-j*5.8
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",4.6,GR2); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",4.6) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",4.6,GR2); x_+=c.stringWidth(w,"Pop",4.6)+g
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v15","Bebas",10,GR,"r")
    print("LS",round(LS,2),"LGFS",round(LGFS,2))
    c.save(); return DS,GX,idr







# ===================== v16: Thursday-night refresh — Yahoo's set lineups, live projections, banked points =====================
# pulled from the four Yahoo matchup pages Thu Oct 1 ~8:45 p.m. PT, after PIT-CLE went final. (player, team, pos, proj, actual or None)
YL={
 "DK I":dict(me=[("Shough","NO","QB",23.25,None),("Warren","PIT","RB",22.68,19.85),("Kamara","NO","RB",13.15,None),("London","ATL","WR",16.70,None),
   ("Pickens","DAL","WR",14.97,None),("Kelce","KC","TE",11.80,None),("McCaffrey","SF","RB",23.85,None),("Henderson","NE","RB",12.40,None),
   ("Boswell","PIT","K",6.89,4.00),("Vikings","MIN","DEF",11.58,None)],
  op=[("Burrow","CIN","QB",24.16,None),("Irving","TB","RB",17.38,None),("B. Allen","NYJ","RB",15.95,None),("Chase","CIN","WR",21.28,None),
   ("P. Washington","JAX","WR",15.05,None),("J. Johnson","NO","TE",10.60,None),("Tate","TEN","WR",10.33,None),("Love","ARI","RB",20.14,None),
   ("Reichard","MIN","K",8.14,None),("Ravens","BAL","DEF",10.71,None)],live=(151.55,153.74),ypct=48),
 "DK II":dict(me=[("Darnold","SEA","QB",19.51,None),("Montgomery","HOU","RB",16.81,None),("Kamara","NO","RB",13.22,None),("Chase","CIN","WR",21.41,None),
   ("London","ATL","WR",16.85,None),("Sutton","DEN","WR",11.07,None),("Kelce","KC","TE",11.85,None),("B. Allen","NYJ","RB",16.04,None),
   ("Brissett","ARI","QB",20.73,None),("Mevis","LA","K",7.98,None),("49ers","SF","DEF",5.35,None)],
  op=[("Lawrence","JAX","QB",23.15,None),("Love","ARI","RB",20.26,None),("Tuten","JAX","RB",14.15,None),("Smith-Njigba","SEA","WR",21.35,None),
   ("Metcalf","PIT","WR",11.07,17.50),("K. Allen","IND","WR",10.09,None),("Bowers","LV","TE",16.62,None),("Corum","LA","RB",10.41,None),
   ("Stafford","LA","QB",19.91,None),("Bates","DET","K",8.32,None),("Seahawks","SEA","DEF",8.30,None)],live=(160.82,170.06),ypct=44),
 "DK III":dict(me=[("Shough","NO","QB",23.25,None),("Montgomery","HOU","RB",16.70,None),("White","WAS","RB",10.42,None),("Pickens","DAL","WR",14.97,None),
   ("Waddle","DEN","WR",14.18,None),("Fannin","CLE","TE",11.93,11.70),("Downs","IND","WR",13.71,None),("Vele","NO","WR",10.46,None),("Steelers","PIT","DEF",11.31,7.00)],
  op=[("Darnold","SEA","QB",19.50,None),("Walker","KC","RB",22.72,None),("Hampton","LAC","RB",14.27,None),("Watson","GB","WR",15.53,None),
   ("McConkey","LAC","WR",11.93,None),("J. Johnson","NO","TE",10.60,None),("Burden","CHI","WR",12.92,None),("Bryant","DEN","WR",7.24,None),("Packers","GB","DEF",10.20,None)],
  live=(122.39,124.91),ypct=48),
 "DK IV":dict(me=[("Goff","DET","QB",22.61,None),("Robinson","ATL","RB",21.90,None),("Swift","CHI","RB",14.21,None),("Jefferson","MIN","WR",17.24,None),
   ("Downs","IND","WR",13.68,None),("McLaurin","WAS","WR",12.16,None),("Kelce","KC","TE",11.80,None),("Flowers","BAL","WR",16.90,None),
   ("Stroud","HOU","QB",23.21,None),("Loop","BAL","K",8.72,None),("Seahawks","SEA","DEF",8.30,None)],
  op=[("Stafford","LA","QB",20.18,None),("Hampton","LAC","RB",10.69,None),("McCaffrey","SF","RB",19.88,None),("Pickens","DAL","WR",14.96,None),
   ("Watson","GB","WR",15.50,None),("McConkey","LAC","WR",11.92,None),("Kincaid","BUF","TE",11.58,None),("A. Jones","MIN","RB",14.15,None),
   ("Stevenson","NE","RB",11.06,None),("Boswell","PIT","K",7.70,4.00),("49ers","SF","DEF",5.35,None)],live=(170.73,139.27),ypct=71),
}
DONE=3            # v47: Thursday, London and the 10 a.m. games are final
YAH={l:YL[l]["live"] for l in YL}
def _side(L):
    win=[0.0]*NW; cnt=[0]*NW; act=[0.0]*NW; rest=[]
    for n,t,p,pr,a in L:
        w=window(t); assert w is not None,(n,t)
        if w<DONE: win[w]+=a; act[w]+=a; cnt[w]+=1
        else: win[w]+=pr; rest.append(dict(player=n,slot=p))
    return win,cnt,act,rest
ACT={}
_prep15=prep
def prep(lab):
    D=_prep15(lab); y=YL[lab]
    mw,mc,ma,mr=_side(y["me"]); ow,oc,oa,orr=_side(y["op"])
    for t in [s_ for s_ in (sum(p[3] for p in y["me"]),) ]: pass
    assert abs(sum(a if a is not None else p for _,_,_,p,a in y["me"])-y["live"][0])<.02, lab
    assert abs(sum(a if a is not None else p for _,_,_,p,a in y["op"])-y["live"][1])<.02, lab
    D["me"]=dict(D["me"],win=mw,cnt=mc,lineup=mr); D["op"]=dict(D["op"],win=ow,cnt=oc,lineup=orr)
    D["bands"]=[(k,(ow if k=="opp" else mw if k=="you" else v)) for k,v in D["bands"]]
    D["ym"],D["yo"]=y["live"]; D["sd"]=math.sqrt(svar(mr)+svar(orr)); D["pct"]=round(100*phi((D["ym"]-D["yo"])/D["sd"]))
    D["ypct"]=y["ypct"]; ACT[lab]=dict(me=ma,op=oa)
    return D
PROSE={
 "DK I":"DIKFORE's trade has processed and Love starts for them; Warren and Boswell banked 23.9 Thursday against nothing, and Monangai over Kamara still reads +2.2 a game.",
 "DK II":"Metcalf put 17.5 on the board for Raider Fan Thursday; Darnold is set at quarterback, and at 2-1 you are level with 6th on record, 43 behind on points.",
 "DK III":"Fannin and the Steelers defense banked 18.7 Thursday; White and Downs play in London at 6:30 a.m. PT Sunday, so Friday's job is White's shoulder.",
 "DK IV":"Team Other banked 4.0 from Boswell; Jefferson still carries the Q on Yahoo, and Odunze over Doubs is still open.",
}
def block(D,top,h,VMAX,GX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h; T=tints(col)
    c.setFillColor(BG2); c.roundRect(x0,bot,x1-x0,h,5,fill=1,stroke=0)
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    lx=x0+12; TL=top-12
    gr=30; sw=gr*20/78; gy=TL-(5.2*CAP)-(gr+sw/2+GLAB-2)
    pb=bot+31; mh=min(46,(gy-31)-pb); mx0=x0+8; mx1=x1-8; rx0=mx0+54
    xs=[mx0+(mx1-mx0)*(.18+.76*i/(NW-1)) for i in range(NW)]
    PS={}
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=ridge(D["lab"]+k,xs,[mh*min(1,y_/VMAX) for y_ in v],rx0,mx1,pb); fill_ridge(P,pb,*T[k]); PS[k]=P
    c.restoreState()
    for i,x in enumerate(xs):
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,GR,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(col if q<lit else TRACK); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    gauge(GX,gy,gr,D["pct"],col,ghost=D.get("ypct"))
    htxt(GX,gy-17.5,f"{D['pct']}%","Bebas",17,TXT,"c",hw=2.4)
    htxt(GX,gy-25,"WIN PROBABILITY","PopB",5.8,TXT,"c",hw=1.6)
    y=TL-24*CAP
    w=txt(lx,y,D["lab"],"Bebas",24,col); w+=6
    w+=txt(lx+w,y,D["rec"],"Bebas",16,TXT); vs0=lx+w
    w+=txt(lx+w,y,"  vs  ","PopM",7,GR); vs1=lx+w
    txt(lx+w,y,f"{D['oppname'].upper()} {D['opprec']}","Bebas",16,TXT)
    y2=y-18
    txt(vs0,y2,f"{D['ym']:.1f}","Bebas",15,col,"r"); txt(vs0,y2,"  vs  ","PopM",7,GR)
    w=vs1+txt(vs1,y2,f"{D['yo']:.1f}","Bebas",15,OPPC)
    _g=round(D['ym']-D['yo'],1); txt(w+5,y2,f"({_g:+.1f})","Bebas",12,UP if _g>0 else DN if _g<0 else TXT)
    txt(lx,y2,"PROJECTED","PopB",LS,GR)                      # fills the front slot, on the number's baseline
    if D["oppdiv"]: txt(lx,y2-LS*1.45,"DIVISION GAME","PopB",LS,GR)
    br=18; lgx=x1-38; dvx=lgx-52; ry=TL-6.4*CAP-6-br
    dn,dp,dlab,dsub=D["dv"]
    ring(dvx,ry,br,dn,dp,None,col,dlab)
    ring(lgx,ry,br,D["n"],D["rank"],None,col,"LEAGUE")
    for x,l in ((dvx,dlab),(lgx,"LEAGUE")): txt(x,TL-6.4*CAP,l,"PopB",6.4,TXT,"c")
    done=DONE
    nx=rx0+(xs[0]-rx0)*.5 if done==0 else xs[done-1]
    a=ACT.get(D["lab"]); assert done==0 or a, "banked points needed before the pair can move"
    pm=sum(a["me"][:done]) if done else 0.0; po=sum(a["op"][:done]) if done else 0.0
    cm=sum(D["me"]["cnt"][:done]); co=sum(D["op"]["cnt"][:done])
    for side,k,pts,cn in ((-1,"you",pm,cm),(1,"opp",po,co)):
        tx=nx+side*6.0; cc,al,ed=T[k]
        yt=(ridge_at(PS[k],tx) if done else pb)+1.0
        dtri(tx,yt,5.6,5.0,cc,ed)
        ax=tx-side*2.8; aa="r" if side<0 else "l"
        htxt(ax,yt+7.4,str(cn),"PopB",4.8,GR,aa,hw=1.4)
        htxt(ax,yt+13.4,f"{pts:.1f}","Bebas",10,col if k=="you" else mix(STEEL,TXT,.30),aa,hw=2.0)
    # layer key: floats above the floor line, OPPONENT on top, out of the caption row
    ks=[k for k,v in reversed(D["bands"]) if k!="you"]; kb=pb+4
    for j,k in enumerate(ks):
        cc,al,ed=T[k]; ly=kb+(len(ks)-1-j)*7.0
        c.setFillColor(cc); c.rect(lx,ly+.2,4.2,4.2,fill=1,stroke=0)
        txt(lx+7,ly,BANDLAB[k],"PopM",4.7,mix(cc,TXT,.40))
    yb=bot+8
    sw_=sheet(rx0,yb,4.2,GR); sx=rx0+sw_+3.5; fs=5.8
    while c.stringWidth(PROSE[D["lab"]],"Pop",fs)>x1-12-sx: fs-=.05
    txt(sx,yb,PROSE[D["lab"]],"Pop",fs,GR)
    return dvx-br
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    # second row: sources left, ages right
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Yahoo matchups, lineups, standings  ·  ","Pop",sf,GR2); txt(M+w,y2,"refresh Friday and before Sunday","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Yahoo pulled Thu Oct 1 night, after PIT-CLE  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    # third row: the four leagues, larger, spread edge to edge, sitting on the rule
    span=W-2*M; fs=10.0
    fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-38-52-18
    GX=(idr+balll)/2-14                                      # Dom: eight points left of v10 (back to 356)
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(D["lab"],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED is Yahoo's live projection pulled Thursday night (banked plus still to play), the MOUNTAIN runs on the lineups as set in Yahoo with finished windows at actual points (league and division layers still Wednesday's), and the dotted needle is Yahoo's own win %.  "
          "In the balls the fluid stops at your place and the white line is the cut, 1st division and 6th league (DK IV left ball: points-for rank), and the TRIANGLES mark points banked (large) and starters played (small) at the last finished window, mine left, his right.")
    FL=simpleSplit(foot,"Pop",4.6,W-2*M)
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=38-j*5.8
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",4.6,GR2); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",4.6) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",4.6,GR2); x_+=c.stringWidth(w,"Pop",4.6)+g
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v16","Bebas",10,GR,"r")
    print("LS",round(LS,2),"LGFS",round(LGFS,2))
    c.save(); return DS,GX,idr








# ===================== v17: league / division / top-six layers refreshed from every team's set lineup =====================
# Yahoo matchup pages for every team, Thu Oct 1 ~9:30 p.m. PT (after PIT-CLE final). THU window at actual, the rest projected.
# Dom's opponents come from YL (their mid1 page shows Dom's side).
_LWF="/home/claude/dksys/data/latest/yahoo/wk4/league_windows_thu.txt"
LW={}
for _l in open(_LWF):
    if _l.startswith("#") or not _l.strip(): continue
    _p=_l.strip().split("~"); LW.setdefault(int(_p[0]),{})[int(_p[1])]=[float(x) for x in _p[2].split()]
_prep16=prep
def prep(lab):
    D=_prep16(lab); cfg,T,st=league(lab); Wd=dict(LW[cfg["id"]])
    assert max(abs(a-b) for a,b in zip(Wd[cfg["me"]],D["me"]["win"]))<.02, lab
    Wd[cfg["opp"]]=D["op"]["win"]; assert set(Wd)==set(T),(lab,sorted(Wd),sorted(T))
    avg=lambda ids:[sum(Wd[o][k] for o in ids)/len(ids) for k in range(NW)]
    s=st; mine=s[s.team==T[cfg["me"]]["name"]].iloc[0]
    if isinstance(mine.division,str) and mine.division: ids3=[o for o in T if T[o]["name"] in set(s[s.division==mine.division].team)]
    else: ids3=[o for o in T if T[o]["name"] in set(s[s["rank"]<=6].team)]
    nb={"league":avg(list(T)),"division":avg(ids3),"top six":avg(ids3)}
    D["bands"]=[(k,nb.get(k,v)) for k,v in D["bands"]]; D["n3"]=len(ids3)
    return D
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    # second row: sources left, ages right
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Yahoo matchups, lineups, standings  ·  ","Pop",sf,GR2); txt(M+w,y2,"refresh Friday and before Sunday","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Yahoo pulled Thu Oct 1 night, after PIT-CLE  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    # third row: the four leagues, larger, spread edge to edge, sitting on the rule
    span=W-2*M; fs=10.0
    fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-38-52-18
    GX=(idr+balll)/2-14                                      # Dom: eight points left of v10 (back to 356)
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(D["lab"],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED is Yahoo's live projection pulled Thursday night (banked plus still to play), the MOUNTAIN runs on the lineups as set in Yahoo with finished windows at actual points (league and division layers from every team's set lineup, same pull), and the dotted needle is Yahoo's own win %.  "
          "In the balls the fluid stops at your place and the white line is the cut, 1st division and 6th league (DK IV left ball: points-for rank), and the TRIANGLES mark points banked (large) and starters played (small) at the last finished window, mine left, his right.")
    FL=simpleSplit(foot,"Pop",4.6,W-2*M)
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=38-j*5.8
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",4.6,GR2); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",4.6) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",4.6,GR2); x_+=c.stringWidth(w,"Pop",4.6)+g
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v17","Bebas",10,GR,"r")
    print("LS",round(LS,2),"LGFS",round(LGFS,2))
    c.save(); return DS,GX,idr











# ===================== v18: league ball inverted - fluid rises from the bottom in every ball, white cut line unchanged =====================
def ring(cx,cy,r,n,me,cut,col,lab):
    up=True; k=GCUT.get(lab,1)                      # v18: every ball fills from the bottom up
    fm=lambda u: .09+.82*u
    yk=lambda q: cy-r+2*r*fm((n-q+.5)/n)
    yb=yk(me)                                                # fluid surface sits on YOUR place
    ycut=yk(k)                                               # the cut: drawn line across the glass on the qualifying place
    xs=[cx-r-1+i*(2*r+2)/48 for i in range(49)]
    c.saveState(); c.setFillColor(BG); c.setFillAlpha(.6); c.ellipse(cx-r*.82,cy-r-3.6,cx+r*.82,cy-r+1.2,fill=1,stroke=0); c.restoreState()
    c.saveState(); p=c.beginPath(); p.circle(cx,cy,r); c.clipPath(p,stroke=0)
    c.radialGradient(cx-r*.38,cy+r*.42,r*1.75,(mix(TXT,BG2,.06),mix(STEEL,BG2,.15),mix(STEEL,BG2,.62)),(0,.55,1),extend=True)
    c.saveState(); q=c.beginPath(); q.moveTo(xs[0],_surf(cx,yb,r,xs[0]))
    for x in xs[1:]: q.lineTo(x,_surf(cx,yb,r,x))
    ye=cy-r-2 if up else cy+r+2
    q.lineTo(xs[-1],ye); q.lineTo(xs[0],ye); q.close(); c.clipPath(q,stroke=0)
    c.radialGradient(cx-r*.30,cy+r*.45,r*1.7,(mix(col,TXT,.38),col,mix(col,BG,.45)),(0,.5,1),extend=True)
    c.restoreState()
    def wline(dy,colr,lw):
        pp=c.beginPath(); pp.moveTo(xs[0],_surf(cx,yb,r,xs[0])+dy)
        for x in xs[1:]: pp.lineTo(x,_surf(cx,yb,r,x)+dy)
        c.setStrokeColor(colr); c.setLineWidth(lw); c.drawPath(pp,fill=0,stroke=1)
    for i in range(7):
        c.saveState(); c.setStrokeColor(BG); c.setStrokeAlpha(.07); c.setLineWidth(1.4); c.circle(cx,cy,r-.3-i*.75,fill=0,stroke=1); c.restoreState()
    LB=scalelabels(n)|{me}
    LB=(LB-{k-1,k+1,me-1,me+1})|{me,k}                     # keep the cut and your place labels clear of neighbours
    for q_ in range(1,n+1):
        y=yk(q_); dy=y-cy; xe=cx-math.sqrt(max(0,r*r-dy*dy))+1.2
        inf=(y<yb) if up else (y>yb)
        sc=mix(BG,col,.12) if inf else mix(BG,STEEL,.20)
        if q_==me: sc=TXT
        if q_==k: sc=TXT
        tl=3.4 if q_ in (me,k) else 2.6 if q_ in LB else 1.5
        c.setStrokeColor(sc); c.setLineWidth(.6 if q_==me else .45); c.line(xe,y,xe+tl,y)
        if q_ in LB: txt(xe+tl+.9,y-1.1,str(q_),"PopB",3.2,sc)
    dy=ycut-cy; hx=math.sqrt(max(0,r*r-dy*dy)); xl=cx-hx+1.2+3.4+.9+c.stringWidth(str(k),"PopB",3.2)+1.4
    c.setLineCap(0); c.setStrokeColor(BG); c.setStrokeAlpha(.55); c.setLineWidth(1.9); c.line(xl,ycut,cx+hx,ycut)
    c.setStrokeAlpha(1); c.setStrokeColor(TXT); c.setLineWidth(.75); c.line(xl,ycut,cx+hx,ycut)
    c.saveState(); c.setFillColor(TXT); c.setFillAlpha(.30); c.ellipse(cx-r*.42,cy+r*.36,cx+r*.12,cy+r*.74,fill=1,stroke=0)
    c.setFillAlpha(.75); c.ellipse(cx-r*.30,cy+r*.52,cx-r*.10,cy+r*.66,fill=1,stroke=0)
    c.setFillAlpha(.10); c.ellipse(cx+r*.15,cy-r*.86,cx+r*.70,cy-r*.60,fill=1,stroke=0); c.restoreState()
    c.restoreState()
    c.setStrokeColor(mix(col,BG2,.25)); c.setLineWidth(.9); c.circle(cx,cy,r,fill=0,stroke=1)
    fs=r*1.12; ordinal(cx+r*.08,cy-fs*CAP/2,me,fs,TXT)
    return cy+r+6
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    # second row: sources left, ages right
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Yahoo matchups, lineups, standings  ·  ","Pop",sf,GR2); txt(M+w,y2,"refresh Friday and before Sunday","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Yahoo pulled Thu Oct 1 night, after PIT-CLE  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    # third row: the four leagues, larger, spread edge to edge, sitting on the rule
    span=W-2*M; fs=10.0
    fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-38-52-18
    GX=(idr+balll)/2-14                                      # Dom: eight points left of v10 (back to 356)
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(D["lab"],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED is Yahoo's live projection pulled Thursday night (banked plus still to play), the MOUNTAIN runs on the lineups as set in Yahoo with finished windows at actual points (league and division layers from every team's set lineup, same pull), and the dotted needle is Yahoo's own win %.  "
          "In the balls the fluid stops at your place and the white line is the cut, 1st division and 6th league (DK IV left ball: points-for rank), and the TRIANGLES mark points banked (large) and starters played (small) at the last finished window, mine left, his right.")
    FL=simpleSplit(foot,"Pop",4.6,W-2*M)
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=38-j*5.8
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",4.6,GR2); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",4.6) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",4.6,GR2); x_+=c.stringWidth(w,"Pop",4.6)+g
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v18","Bebas",10,GR,"r")
    print("LS",round(LS,2),"LGFS",round(LGFS,2))
    c.save(); return DS,GX,idr











# ===================== v19: Friday-morning refresh + redesign (Dom's voice walk, Fri Oct 2 ~8:15 a.m. PT) =====================
# Meter is the hero: larger, on its own translucent arc-shaped scrim, drawn IN FRONT of the mountain.
# Mountain is NOT capped (Dom): it runs the full card width and rises behind the meter and balls.
# Balls sit in front on the same kind of soft scrim; the fluid's top edge gets a stroke in a darker shade of its own color.
# Previous reading: a tick on the dial where the meter stood last time, the arc between shaded green (gain) or red (loss).
# Layer key moved up into the identity block. DK1-DK4 in print, no Roman numerals. Note line = who decides it.
import json as _json
DISP={"DK I":"DK1","DK II":"DK2","DK III":"DK3","DK IV":"DK4"}
# Yahoo matchup pages, Fri Oct 2 ~8:20-8:35 a.m. PT. Finished (THU) players at actual; sums match Yahoo's LIVE PROJ to the cent.
YL={
 "DK I":dict(me=[("Shough","NO","QB",23.30,None),("Warren","PIT","RB",22.68,19.85),("McCaffrey","SF","RB",23.79,None),("Pickens","DAL","WR",15.05,None),
   ("Diggs","WAS","WR",11.24,None),("Kelce","KC","TE",11.82,None),("London","ATL","WR",16.71,None),("Kamara","NO","RB",13.18,None),
   ("Boswell","PIT","K",6.89,4.00),("Vikings","MIN","DEF",11.64,None)],
  op=[("Burrow","CIN","QB",24.18,None),("B. Allen","NYJ","RB",16.34,None),("Love","ARI","RB",20.19,None),("Chase","CIN","WR",21.35,None),
   ("P. Washington","JAX","WR",15.11,None),("J. Johnson","NO","TE",10.62,None),("Tate","TEN","WR",10.34,None),("Lemon","PHI","WR",8.48,None),
   ("Reichard","MIN","K",8.14,None),("Ravens","BAL","DEF",10.74,None)],live=(150.58,145.49),ypct=54),
 "DK II":dict(me=[("Darnold","SEA","QB",19.53,None),("Montgomery","HOU","RB",16.82,None),("Kamara","NO","RB",13.25,None),("Chase","CIN","WR",21.48,None),
   ("London","ATL","WR",16.86,None),("Sutton","DEN","WR",11.12,None),("Kelce","KC","TE",11.87,None),("B. Allen","NYJ","RB",16.44,None),
   ("Brissett","ARI","QB",20.59,None),("Mevis","LA","K",8.01,None),("49ers","SF","DEF",5.31,None)],
  op=[("Lawrence","JAX","QB",23.13,None),("Love","ARI","RB",20.31,None),("Tuten","JAX","RB",14.14,None),("Smith-Njigba","SEA","WR",21.40,None),
   ("Metcalf","PIT","WR",11.06,17.50),("K. Allen","IND","WR",10.09,None),("Bowers","LV","TE",16.56,None),("Corum","LA","RB",10.45,None),
   ("Stafford","LA","QB",19.85,None),("Bates","DET","K",8.32,None),("Seahawks","SEA","DEF",8.30,None)],live=(161.28,170.05),ypct=44),
 "DK III":dict(me=[("Shough","NO","QB",23.30,None),("Montgomery","HOU","RB",16.71,None),("White","WAS","RB",10.53,None),("Pickens","DAL","WR",15.05,None),
   ("Waddle","DEN","WR",14.26,None),("Fannin","CLE","TE",11.96,11.70),("Downs","IND","WR",13.74,None),("Vele","NO","WR",10.48,None),("Steelers","PIT","DEF",11.32,7.00)],
  op=[("Darnold","SEA","QB",19.51,None),("Walker","KC","RB",22.74,None),("Hampton","LAC","RB",14.16,None),("Watson","GB","WR",15.48,None),
   ("McConkey","LAC","WR",12.01,None),("J. Johnson","NO","TE",10.62,None),("Burden","CHI","WR",13.01,None),("Bryant","DEN","WR",7.29,None),("Packers","GB","DEF",10.22,None)],
  live=(122.77,125.04),ypct=48),
 "DK IV":dict(me=[("Goff","DET","QB",22.64,None),("Robinson","ATL","RB",21.91,None),("Swift","CHI","RB",14.20,None),("Jefferson","MIN","WR",17.23,None),
   ("Downs","IND","WR",13.71,None),("McLaurin","WAS","WR",12.25,None),("Kelce","KC","TE",11.82,None),("Flowers","BAL","WR",16.98,None),
   ("Stroud","HOU","QB",23.19,None),("Loop","BAL","K",8.72,None),("Seahawks","SEA","DEF",8.30,None)],
  op=[("Stafford","LA","QB",20.13,None),("Hampton","LAC","RB",10.63,None),("McCaffrey","SF","RB",19.87,None),("Pickens","DAL","WR",15.04,None),
   ("Watson","GB","WR",15.46,None),("McConkey","LAC","WR",11.99,None),("Kincaid","BUF","TE",11.61,None),("A. Jones","MIN","RB",14.16,None),
   ("Stevenson","NE","RB",11.19,None),("Boswell","PIT","K",7.70,4.00),("49ers","SF","DEF",5.31,None)],live=(170.95,139.39),ypct=71),
}
YAH={l:YL[l]["live"] for l in YL}
HIST="/home/claude/dksys/data/state/winprob_history.json"
PREV={l:v for l,v in _json.load(open(HIST))["readings"][-1]["model"].items()}; PREVLAB=_json.load(open(HIST))["readings"][-1]["label"]
# what-if swaps for the note line: (side, starter out, replacement proj, replacement name)
WHATIF={"DK III":("me","White",6.40,"Holani"),"DK IV":("me","Swift",10.95,"RJ Harvey")}
def prep(lab):
    D=_prep16(lab); cfg,T,st=league(lab); Wd=dict(LW[cfg["id"]])
    Wd[cfg["me"]]=D["me"]["win"]; Wd[cfg["opp"]]=D["op"]["win"]          # v19: both sides from Friday's pull; other teams still Thursday night
    avg=lambda ids:[sum(Wd[o][k] for o in ids)/len(ids) for k in range(NW)]
    s=st; mine=s[s.team==T[cfg["me"]]["name"]].iloc[0]
    if isinstance(mine.division,str) and mine.division: ids3=[o for o in T if T[o]["name"] in set(s[s.division==mine.division].team)]
    else: ids3=[o for o in T if T[o]["name"] in set(s[s["rank"]<=6].team)]
    nb={"league":avg(list(T)),"division":avg(ids3),"top six":avg(ids3)}
    D["bands"]=[(k,nb.get(k,v)) for k,v in D["bands"]]; D["n3"]=len(ids3)
    D["prev"]=PREV.get(lab)
    if lab in WHATIF:
        side,out,rp,rn=WHATIF[lab]; pr=[p for n,_,_,p,_ in YL[lab][side] if n==out][0]; d=(rp-pr)*(1 if side=="me" else -1)
        D["whatif"]=(out,rn,round(100*phi((D["ym"]-D["yo"]+d)/D["sd"])))
    return D
PROSE={
 "DK I":"DIKFORE benched Bucky Irving (Q) for Makai Lemon, and that swing is your lead. No questionable starter on either side; Diggs is in for Henderson.",
 "DK II":"Metcalf's 17.5 for Raider Fan is already banked. No questionable starter on your side; Rodgers (17.3) sits on the bench behind Darnold and Brissett.",
 "DK III":"WHITE DECIDES IT: questionable, no practice Wednesday or Thursday, London 6:30 a.m. PT Sunday. If he sits, Holani (also Q) starts and the meter reads {w}%.",
 "DK IV":"Swift (Q) is the only open question. If he sits, RJ Harvey starts and the meter reads {w}%; Odunze over Doubs is still open.",
}
def scrim(path_fn,al=.62,steps=7,feather=7.0):
    """soft translucent plate: the same shape drawn several times, shrinking, low alpha each, so the edge feathers out"""
    c.saveState()
    for i in range(steps):
        g=feather*(1-i/(steps-1)); c.setFillColor(BG); c.setFillAlpha(1-(1-al)**(1/steps)); p=path_fn(g); c.drawPath(p,fill=1,stroke=0)
    c.restoreState()
def _dome(cx,cy,R,dn):
    def f(g):
        p=c.beginPath(); rr=R+g; N=36
        for i in range(N+1):
            a=math.pi*i/N; x,y=cx+rr*math.cos(a),cy+rr*math.sin(a); (p.moveTo if i==0 else p.lineTo)(x,y)
        rb=min(rr,dn+g)*.98
        p.lineTo(cx-rr,cy-dn-g+rb); p.curveTo(cx-rr,cy-dn-g,cx-rr,cy-dn-g,cx-rr+rb,cy-dn-g)
        p.lineTo(cx+rr-rb,cy-dn-g); p.curveTo(cx+rr,cy-dn-g,cx+rr,cy-dn-g,cx+rr,cy-dn-g+rb); p.close(); return p
    return f
def _capsule(x0,y0,x1,y1,rad):
    def f(g):
        p=c.beginPath(); p.roundRect(x0-g,y0-g,(x1-x0)+2*g,(y1-y0)+2*g,rad+g); return p
    return f
def change_mark(cx,cy,r,v,prev,col):
    """previous reading: a tick outside the dial, the arc between it and now in green (gain) or red (loss)"""
    if prev is None: return 0
    sw=r*20/78; ro=r+sw/2; a=lambda t: 180-1.8*min(max(t,0),99.9)
    d=v-prev; cc=UP if d>0 else DN if d<0 else FLAT
    if d:
        lo,hi=sorted((v,prev)); rb=ro+3.4
        c.setLineCap(0); c.setStrokeColor(BG2); c.setLineWidth(4.4); c.arc(cx-rb,cy-rb,cx+rb,cy+rb,a(hi),a(lo)-a(hi))
        c.setStrokeColor(cc); c.setLineWidth(2.6); c.arc(cx-rb,cy-rb,cx+rb,cy+rb,a(hi),a(lo)-a(hi))
    t=math.pi*(1-prev/100); c.setStrokeColor(TXT); c.setLineWidth(1.1); c.setLineCap(1)
    c.line(cx+(ri:=r-sw/2)*math.cos(t),cy+ri*math.sin(t),cx+(ro+6.5)*math.cos(t),cy+(ro+6.5)*math.sin(t)); c.setLineCap(0)
    return d
def ring19(cx,cy,r,n,me,cut,col,lab):
    """v18 ball, plus a stroke on the fluid's top edge in a darker shade of the league's own color (Dom, Fri)"""
    out=ring(cx,cy,r,n,me,cut,col,lab)
    fm=lambda u: .09+.82*u; yb=cy-r+2*r*fm((n-me+.5)/n)
    xs=[cx-r-1+i*(2*r+2)/48 for i in range(49)]
    c.saveState(); p=c.beginPath(); p.circle(cx,cy,r-.4); c.clipPath(p,stroke=0)
    pp=c.beginPath(); pp.moveTo(xs[0],_surf(cx,yb,r,xs[0]))
    for x in xs[1:]: pp.lineTo(x,_surf(cx,yb,r,x))
    c.setStrokeColor(mix(col,BG,.42)); c.setLineWidth(1.15); c.drawPath(pp,fill=0,stroke=1); c.restoreState()
    fs=r*1.12; ordinal(cx+r*.08,cy-fs*CAP/2,me,fs,TXT)           # re-print the ordinal over the new stroke
    return out
def block(D,top,h,VMAX,GX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h; T=tints(col); lab=DISP[D["lab"]]
    c.setFillColor(BG2); c.roundRect(x0,bot,x1-x0,h,5,fill=1,stroke=0)
    lx=x0+12; TL=top-12
    gr=38; sw=gr*20/78; ro=gr+sw/2; gy=top-14-GLAB-ro
    pb=bot+31; mh=(top-10)-pb; mx0=x0+4; mx1=x1-4; rx0=mx0
    xs=[mx0+(mx1-mx0)*(.12+.83*i/(NW-1)) for i in range(NW)]
    PS={}
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=ridge(D["lab"]+k,xs,[mh*min(1,y_/VMAX) for y_ in v],rx0,mx1,pb); fill_ridge(P,pb,*T[k]); PS[k]=P
    c.restoreState()
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    for i,x in enumerate(xs):
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,GR,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(col if q<lit else TRACK); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    # ---- the meter: scrim, dial, change mark, number ----
    dn=31.0
    scrim(_dome(GX,gy,ro+GLAB+2,dn),al=.78,steps=12,feather=15.0)
    gauge(GX,gy,gr,D["pct"],col,ghost=D.get("ypct"))
    d=change_mark(GX,gy,gr,D["pct"],D.get("prev"),col)
    htxt(GX,gy-21,f"{D['pct']}%","Bebas",23,TXT,"c",hw=2.4)
    htxt(GX,gy-29,"WIN PROBABILITY","PopB",6.2,TXT,"c",hw=1.6)
    if D.get("prev") is not None:
        cc=UP if d>0 else DN if d<0 else FLAT
        s_=(f"UP {d}" if d>0 else f"DOWN {-d}" if d<0 else "NO CHANGE")+f" SINCE {PREVLAB}"
        wv=c.stringWidth(s_,"PopB",5.4); tx=GX-wv/2+4
        if d: _tri(tx-6.5,gy-37.2+(.6 if d>0 else 3.4),d>0,cc)
        htxt(tx,gy-38.4,s_,"PopB",5.4,cc,"l",hw=1.6)
    # ---- identity ----
    y=TL-24*CAP
    w=htxt(lx,y,lab,"Bebas",24,col,hw=2.4) or c.stringWidth(lab,"Bebas",24); w+=6
    w+=htxt(lx+w,y,D["rec"],"Bebas",16,TXT,hw=2.2) or c.stringWidth(D["rec"],"Bebas",16); vs0=lx+w
    w+=c.stringWidth("  vs  ","PopM",7); htxt(vs0,y,"  vs  ","PopM",7,GR,hw=1.6); vs1=lx+w
    htxt(lx+w,y,f"{D['oppname'].upper()} {D['opprec']}","Bebas",16,TXT,hw=2.2)
    y2=y-18
    htxt(vs0,y2,f"{D['ym']:.1f}","Bebas",15,col,"r",hw=2.2); htxt(vs0,y2,"  vs  ","PopM",7,GR,hw=1.6)
    htxt(vs1,y2,f"{D['yo']:.1f}","Bebas",15,OPPC,hw=2.2); w=vs1+c.stringWidth(f"{D['yo']:.1f}","Bebas",15)
    _g=round(D['ym']-D['yo'],1); htxt(w+5,y2,f"({_g:+.1f})","Bebas",12,UP if _g>0 else DN if _g<0 else TXT,hw=2.0)
    htxt(lx,y2,"PROJECTED","PopB",LS,GR,hw=1.6)
    yk_=y2-LS*1.45
    if D["oppdiv"]: htxt(lx,yk_,"DIVISION GAME","PopB",LS,GR,hw=1.6); yk_-=LS*1.5
    # layer key, one row, moved up out of the mountain (Dom)
    ks=[k for k,v in reversed(D["bands"]) if k!="you"]; kx=lx; ky=yk_-3
    for k in ks:
        cc,al,ed=T[k]; c.setFillColor(cc); c.rect(kx,ky+.2,4.2,4.2,fill=1,stroke=0)
        htxt(kx+7,ky,BANDLAB[k],"PopM",4.7,mix(cc,TXT,.40),hw=1.4); kx+=7+c.stringWidth(BANDLAB[k],"PopM",4.7)+9
    # ---- balls: on their own scrim, in front of the mountain ----
    br=19; lgx=x1-40; dvx=lgx-50; ry=TL-6.4*CAP-7-br
    scrim(_capsule(dvx-br-4,ry-br-6,lgx+br+4,TL+1,14),al=.70,steps=12,feather=12.0)
    dn_,dp,dlab,dsub=D["dv"]
    ring19(dvx,ry,br,dn_,dp,None,col,dlab)
    ring19(lgx,ry,br,D["n"],D["rank"],None,col,"LEAGUE")
    for x,l in ((dvx,dlab),(lgx,"LEAGUE")): txt(x,TL-6.4*CAP,l,"PopB",6.4,TXT,"c")
    # ---- banked triangles at the last finished window ----
    done=DONE
    nx=rx0+(xs[0]-rx0)*.5 if done==0 else xs[done-1]
    a=ACT.get(D["lab"]); pm=sum(a["me"][:done]) if done else 0.0; po=sum(a["op"][:done]) if done else 0.0
    cm=sum(D["me"]["cnt"][:done]); co=sum(D["op"]["cnt"][:done])
    for side,k,pts,cn in ((-1,"you",pm,cm),(1,"opp",po,co)):
        tx=nx+side*6.0; cc,al,ed=T[k]
        yt=(ridge_at(PS[k],tx) if done else pb)+1.0
        dtri(tx,yt,5.6,5.0,cc,ed)
        ax=tx-side*2.8; aa="r" if side<0 else "l"
        htxt(ax,yt+7.4,str(cn),"PopB",4.8,GR,aa,hw=1.4)
        htxt(ax,yt+13.4,f"{pts:.1f}","Bebas",10,col if k=="you" else mix(STEEL,TXT,.30),aa,hw=2.0)
    # ---- note line: who decides it ----
    pr=PROSE[D["lab"]].format(w=D["whatif"][2] if "whatif" in D else "")
    yb=bot+8; sw_=sheet(lx,yb,4.2,GR); sx=lx+sw_+3.5; fs=6.0
    while c.stringWidth(pr,"Pop",fs)>x1-12-sx: fs-=.05
    if pr.startswith("WHITE DECIDES IT"):
        hd="WHITE DECIDES IT:"; ww=txt(sx,yb,hd,"PopB",fs,HOLD); txt(sx+ww,yb,pr[len(hd):],"Pop",fs,GR)
    else: txt(sx,yb,pr,"Pop",fs,GR)
    return dvx-br
_tints18=tints
def tints(col):
    return _tints18(col)
_htxt0=htxt
def htxt(x,y,s,f,sz,col=TXT,al="l",hw=1.8):
    _htxt0(x,y,s,f,sz,col,al,hw); return c.stringWidth(s,f,sz)
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Yahoo matchups and lineups  ·  ","Pop",sf,GR2); txt(M+w,y2,"refresh after Friday's injury reports","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Yahoo pulled Fri Oct 2 morning (league layers Thu night)  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    span=W-2*M; fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-40-50-26
    GX=(idr+balll)/2-6
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(DISP[D["lab"]],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED is Yahoo's live projection pulled Friday morning (banked plus still to play). WIN PROBABILITY is the system's own model; the dotted needle is Yahoo's own win %, and the tick outside the dial is where the meter stood "+PREVLAB.lower()+", the arc between it green for a gain, red for a loss.  "
          "The MOUNTAIN runs on the lineups as set in Yahoo, finished windows at actual points (league and division layers from Thursday night's pull). In the balls the fluid stops at your place and the white line is the cut, 1st division and 6th league (DK4 left ball: points-for rank).")
    FL=simpleSplit(foot,"Pop",4.6,W-2*M)
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=38-j*5.8
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",4.6,GR2); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",4.6) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",4.6,GR2); x_+=c.stringWidth(w,"Pop",4.6)+g
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v19","Bebas",10,GR,"r")
    c.save(); return DS,GX,idr

# ===================== v20: all 44 teams re-pulled Friday + Dom's voice batch (Fri Oct 2 ~8:40 a.m. PT) =====================
# 1. League / division / top-six layers from every team's Friday matchup page (league_windows_fri.txt, 44 of 44, 0 errors).
# 2. Roman numerals back in print (Dom); spoken as DK one..four.
# 3. Note line: paper mark stays left, colored by urgency (red = a decision you must make, gold = watch, grey = info);
#    the sentence is one font, one color, capitals only for the lead, right-justified against the card edge, more room above.
# 4. Both translucent plates pulled in tight to the meter and the balls.
# 5. NEW: players-left pips under the meter -- one pip per starter, filled once he has played, mine above, his below.
_LWF="/home/claude/dksys/data/latest/yahoo/wk4/league_windows_fri.txt"
LW={}
for _l in open(_LWF):
    if _l.startswith("#") or not _l.strip(): continue
    _p=_l.strip().split("~"); LW.setdefault(int(_p[0]),{})[int(_p[1])]=[float(x) for x in _p[2].split()]
DISP={"DK I":"DK I","DK II":"DK II","DK III":"DK III","DK IV":"DK IV"}
_H=_json.load(open(HIST))["readings"]; _B=[r for r in _H if r["label"]=="THU NIGHT"][-1]
PREV=dict(_B["model"]); PREVLAB=_B["label"]          # baseline stays Thursday night: Friday's 44-team pull matched this morning's to the cent
URG={"DK IV":"watch"}
PROSE={
 "DK I":"DIKFORE (3-0) is the hardest draw of the four. Warren's 19.85 is already banked from Thursday; Diggs starts over Henderson.",
 "DK II":"Metcalf's 17.5 for Raider Fan is already banked. No questionable starter on your side; Rodgers (17.3) sits on the bench behind Darnold and Brissett.",
 "DK III":"White is out, so Holani starts. He was limited all week with the rib, but he plays. Nothing left to decide here.",
 "DK IV":"FLOWERS: questionable, Friday was a rest day and there is no Saturday downgrade. Baltimore inactives 8:30 a.m. PT; Kraft goes in if he sits.",
}
_prep19=prep
def prep(lab):
    D=_prep19(lab); cfg,T,st=league(lab)
    import json as _jw; D["mypct"]=D["pct"]; D["pct"]=_jw.load(open("/home/claude/dksys/data/latest/yahoo/wk4/yahoo_winprob_1420.json"))["pct"][lab]   # v42: the center needle is Yahoo's own win probability, as on his phone
    pass   # v33: Dom's side now comes from the live scan; the all-team pull (league averages) is still Saturday night's
    return D
def pips(cx,y,D,col):
    """players left: one pip per starter, filled once he has played; mine on top in league color, his below in steel"""
    Y=YL[D["lab"]]; cnt=lambda side:(len(Y[side]),sum(1 for r in Y[side] if r[4] is not None))
    rows=((*cnt("me"),col),(*cnt("op"),mix(STEEL,TXT,.15)))
    pw,ph,pg=4.0,2.6,1.3; n=max(r[0] for r in rows); wd=n*pw+(n-1)*pg; x0=cx-wd/2-12
    for j,(tot,pl,cc) in enumerate(rows):
        yy=y-j*5.6
        lv=_livecount(Y["me" if j==0 else "op"])   # Oct 11 (Dom): men playing right now
        for k in range(tot):
            x=x0+k*(pw+pg)
            if k<pl: c.setFillColor(cc); c.roundRect(x,yy,pw,ph,.8,fill=1,stroke=0)
            elif k<pl+lv:
                c.saveState(); c.setFillColor(H("#3FB36A"))
                for e_,a_ in ((1.6,.18),(.8,.32)): c.setFillAlpha(a_); c.roundRect(x-e_,yy-e_,pw+2*e_,ph+2*e_,.8+e_,fill=1,stroke=0)
                c.setFillAlpha(1); c.setFillColor(H("#4FD08A")); c.roundRect(x,yy,pw,ph,.8,fill=1,stroke=0); c.restoreState()
            else: c.setStrokeColor(mix(cc,BG2,.35)); c.setLineWidth(.6); c.roundRect(x+.3,yy+.3,pw-.6,ph-.6,.7,fill=0,stroke=1)
        htxt(x0+wd+4,yy-.2,f"{tot-pl} TO PLAY","PopB",4.6,cc,"l",hw=1.3)
def block(D,top,h,VMAX,GX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h; T=tints(col); lab=DISP[D["lab"]]
    c.setFillColor(BG2); c.roundRect(x0,bot,x1-x0,h,5,fill=1,stroke=0)
    lx=x0+12; TL=top-12
    gr=38; sw=gr*20/78; ro=gr+sw/2; gy=top-14-GLAB-ro
    pb=bot+34; mh=(top-10)-pb; mx0=x0+4; mx1=x1-4; rx0=mx0
    xs=[mx0+(mx1-mx0)*(.12+.83*i/(NW-1)) for i in range(NW)]
    PS={}
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=ridge(D["lab"]+k,xs,[mh*min(1,y_/VMAX) for y_ in v],rx0,mx1,pb); fill_ridge(P,pb,*T[k]); PS[k]=P
    c.restoreState()
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    for i,x in enumerate(xs):
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,GR,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(col if q<lit else TRACK); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    # ---- the meter: scrim, dial, change mark, number ----
    dn=40.5                                     # v20: plate runs down over the players-left pips
    scrim(_dome(GX,gy,ro+GLAB+1,dn),al=.74,steps=9,feather=6.0); scrim(_capsule(GX-44,gy-dn-17,GX+44,gy-dn+2,7),al=.74,steps=9,feather=5.0)
    gauge(GX,gy,gr,D["pct"],col,ghost=D.get("ypct"))
    d=change_mark(GX,gy,gr,D["pct"],D.get("prev"),col)
    htxt(GX,gy-21,f"{D['pct']}%","Bebas",23,TXT,"c",hw=2.4)
    htxt(GX,gy-29,"WIN PROBABILITY","PopB",6.2,TXT,"c",hw=1.6)
    if D.get("prev") is not None:
        cc=UP if d>0 else DN if d<0 else FLAT
        s_=(f"UP {d}" if d>0 else f"DOWN {-d}" if d<0 else "NO CHANGE")+f" SINCE {PREVLAB}"
        wv=c.stringWidth(s_,"PopB",5.4); tx=GX-wv/2+4
        if d: _tri(tx-6.5,gy-37.2+(.6 if d>0 else 3.4),d>0,cc)
        htxt(tx,gy-38.4,s_,"PopB",5.4,cc,"l",hw=1.6)
    pips(GX,gy-47.5,D,col)
    # ---- identity ----
    y=TL-24*CAP
    w=htxt(lx,y,lab,"Bebas",24,col,hw=2.4) or c.stringWidth(lab,"Bebas",24); w+=6
    w+=htxt(lx+w,y,D["rec"],"Bebas",16,TXT,hw=2.2) or c.stringWidth(D["rec"],"Bebas",16); vs0=lx+w
    w+=c.stringWidth("  vs  ","PopM",7); htxt(vs0,y,"  vs  ","PopM",7,GR,hw=1.6); vs1=lx+w
    htxt(lx+w,y,f"{D['oppname'].upper()} {D['opprec']}","Bebas",16,TXT,hw=2.2)
    y2=y-18
    htxt(vs0,y2,f"{D['ym']:.1f}","Bebas",15,col,"r",hw=2.2); htxt(vs0,y2,"  vs  ","PopM",7,GR,hw=1.6)
    htxt(vs1,y2,f"{D['yo']:.1f}","Bebas",15,OPPC,hw=2.2); w=vs1+c.stringWidth(f"{D['yo']:.1f}","Bebas",15)
    _g=round(D['ym']-D['yo'],1); htxt(w+5,y2,f"({_g:+.1f})","Bebas",12,UP if _g>0 else DN if _g<0 else TXT,hw=2.0)
    htxt(lx,y2,"PROJECTED","PopB",LS,GR,hw=1.6)
    yk_=y2-LS*1.45
    if D["oppdiv"]: htxt(lx,yk_,"DIVISION GAME","PopB",LS,GR,hw=1.6); yk_-=LS*1.5
    # layer key, one row, moved up out of the mountain (Dom)
    ks=[k for k,v in reversed(D["bands"]) if k!="you"]; kx=lx; ky=yk_-3
    for k in ks:
        cc,al,ed=T[k]; c.setFillColor(cc); c.rect(kx,ky+.2,4.2,4.2,fill=1,stroke=0)
        htxt(kx+7,ky,BANDLAB[k],"PopM",4.7,mix(cc,TXT,.40),hw=1.4); kx+=7+c.stringWidth(BANDLAB[k],"PopM",4.7)+9
    # ---- balls: on their own scrim, in front of the mountain ----
    br=19; lgx=x1-40; dvx=lgx-50; ry=TL-6.4*CAP-7-br
    scrim(_capsule(dvx-br-2,ry-br-3,lgx+br+2,TL+1,12),al=.74,steps=9,feather=5.0)
    dn_,dp,dlab,dsub=D["dv"]
    ring19(dvx,ry,br,dn_,dp,None,col,dlab)
    ring19(lgx,ry,br,D["n"],D["rank"],None,col,"LEAGUE")
    for x,l in ((dvx,dlab),(lgx,"LEAGUE")): txt(x,TL-6.4*CAP,l,"PopB",6.4,TXT,"c")
    # ---- banked triangles at the last finished window ----
    done=DONE
    nx=rx0+(xs[0]-rx0)*.5 if done==0 else xs[done-1]
    a=ACT.get(D["lab"]); pm=sum(a["me"][:done]) if done else 0.0; po=sum(a["op"][:done]) if done else 0.0
    cm=sum(D["me"]["cnt"][:done]); co=sum(D["op"]["cnt"][:done])
    for side,k,pts,cn in ((-1,"you",pm,cm),(1,"opp",po,co)):
        tx=nx+side*6.0; cc,al,ed=T[k]
        yt=(ridge_at(PS[k],tx) if done else pb)+1.0
        dtri(tx,yt,5.6,5.0,cc,ed)
        ax=tx-side*2.8; aa="r" if side<0 else "l"
        htxt(ax,yt+7.4,str(cn),"PopB",4.8,GR,aa,hw=1.4)
        htxt(ax,yt+13.4,f"{pts:.1f}","Bebas",10,col if k=="you" else mix(STEEL,TXT,.30),aa,hw=2.0)
    # ---- note line: mark on the left, colored by urgency; sentence right-justified, one font, one color ----
    pr=PROSE[D["lab"]].format(w=D["whatif"][2] if "whatif" in D else "")
    yb=bot+7.5; urg=URG.get(D["lab"],"info"); mc={"act":DN,"watch":HOLD,"info":GR}[urg]
    sw_=sheet(lx,yb,4.2,mc); fs=6.0; rx=x1-12; lim=rx-(lx+sw_+40)
    while c.stringWidth(pr,"Pop",fs)>lim: fs-=.05
    txt(rx,yb,pr,"Pop",fs,mix(GR,TXT,.25),"r")
    return dvx-br
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Yahoo matchups and lineups  ·  ","Pop",sf,GR2); txt(M+w,y2,"Friday injury reports not yet pulled","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Yahoo pulled Fri Oct 2 morning, all 44 teams  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    span=W-2*M; fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-40-50-26
    GX=(idr+balll)/2-6
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(DISP[D["lab"]],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED is Yahoo's live projection pulled Friday morning (banked plus still to play). WIN PROBABILITY is the system's own model; the dotted needle is Yahoo's own win %, and the tick outside the dial is where the meter stood "+PREVLAB.lower()+", the arc between it green for a gain, red for a loss.  "
          "The MOUNTAIN runs on the lineups as set in Yahoo, finished windows at actual points (league and division layers from every team's set lineup, same Friday pull). In the balls the fluid stops at your place and the white line is the cut, 1st division and 6th league (DK IV left ball: points-for rank). The PIPS under the meter are starters, filled once played, mine above, his below.")
    FL=simpleSplit(foot,"Pop",4.6,W-2*M)
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=38-j*5.8
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",4.6,GR2); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",4.6) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",4.6,GR2); x_+=c.stringWidth(w,"Pop",4.6)+g
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v20","Bebas",10,GR,"r")
    c.save(); return DS,GX,idr

# ===================== v21: now-band + banked-mark redesign (Dom's voice batch, Fri Oct 2 morning) =====================
# 6. NOW-BAND: narrow translucent dark band, thin white edge, between the last finished window and the next one;
#    its height follows the tallest mountain layer at that x, so it grows and shrinks as the week advances.
# 7. BANKED MARKS: the band is the divider -- mine left, his right. Each mark is a triangle pointing at its own ridge,
#    with a two-line stack: points (large; league color mine, steel his) over "N OF M" starters played (small grey caps,
#    sized to the points' width so both edges line up). Above the ridge if it clears the ceiling and every plate;
#    otherwise flipped below the ridge (pointing up) on a small scrim; otherwise both step outward, mine left, his right.
#    CEILING = top of the DIVISION / LEAGUE label: the reserved strip under the card's top edge holds all the way across,
#    for the marks and the mountain both.
PTS_FS=11.0
def nowband(bx,bw,pb,ytop,ceil):
    yt=min(ceil,ytop+2.0)
    if yt<=pb+1: yt=pb+6
    c.saveState(); c.setFillColor(BG); c.setFillAlpha(.62); c.rect(bx-bw/2,pb,bw,yt-pb,fill=1,stroke=0)
    c.setFillAlpha(1); c.setStrokeColor(TXT); c.setStrokeAlpha(.78); c.setLineWidth(.45); c.setLineCap(0)
    p=c.beginPath(); p.moveTo(bx-bw/2,pb); p.lineTo(bx-bw/2,yt); p.lineTo(bx+bw/2,yt); p.lineTo(bx+bw/2,pb)
    c.drawPath(p,fill=0,stroke=1); c.restoreState()
def stack_dims(ps,ls):
    pw=c.stringWidth(ps,"Bebas",PTS_FS); u=c.stringWidth(ls,"PopB",1.0)
    lf=max(3.8,min(4.6,pw/u)); lw_=u*lf
    return dict(ps=ps,ls=ls,lf=lf,sw=max(pw,lw_),pw=pw,lw=lw_)
TRI_W,TRI_H,G1,G2=5.6,5.0,2.2,2.0
def _rect(mode,x,yr,d):
    """box of the whole mark (triangle + stack) for a tip on the ridge at yr"""
    ph=PTS_FS*CAP; lh=d["lf"]*CAP; hh=TRI_H+G1+lh+G2+ph
    hw=max(d["sw"],TRI_W)/2+1.0
    return (x-hw,yr+.8,x+hw,yr+.8+hh) if mode=="above" else (x-hw,yr-.8-hh,x+hw,yr-.8)
def _hit(r,o): return not (r[2]<=o[0] or r[0]>=o[2] or r[3]<=o[1] or r[1]>=o[3])
def place_marks(S,bx,bw,PS,ceil,pb,OBS,xmin,xmax):
    """each side independently: nearest spot to the band, above the ridge first, then below; step outward only as far as needed"""
    CLR=2.5; plan=[]
    for d in S:
        got=None
        for step in range(0,80):
            x=bx+d["side"]*(bw/2+CLR+max(d["sw"],TRI_W)/2+step*2.0); yr=ridge_at(PS[d["k"]],x)
            for mode in ("above","below"):
                r=_rect(mode,x,yr,d)
                if r[0]<xmin or r[2]>xmax or r[3]>ceil or (mode=="below" and r[1]<pb+1.5) or any(_hit(r,o) for o in OBS): continue
                got=(mode,x,yr); break
            if got: break
        plan.append(got or ("above",bx+d["side"]*(bw/2+CLR+max(d["sw"],TRI_W)/2),ridge_at(PS[d["k"]],bx)))
    return plan
def draw_mark(d,mode,x,yr,Tk):
    cc,al,ed=Tk; ph=PTS_FS*CAP; lh=d["lf"]*CAP
    if mode=="above":
        dtri(x,yr+.8,TRI_W,TRI_H,cc,ed)
        yl=yr+.8+TRI_H+G1; yp=yl+lh+G2
    else:
        utri(x,yr-.8,TRI_W,TRI_H,cc,ed)
        yp=yr-.8-TRI_H-G1-ph; yl=yp-G2-lh
    hw=d["sw"]/2+2.0; scrim(_capsule(x-hw,yl-1.5,x+hw,yp+ph+1.5,2.5),al=.72,steps=6,feather=2.0)   # every stack on its own small plate
    htxt(x,yp,d["ps"],"Bebas",PTS_FS,d["pc"],"c",hw=2.0)
    htxt(x,yl,d["ls"],"PopB",d["lf"],GR,"c",hw=1.3)
    d["placed"]=(mode,round(x,1),round(yr,1))
def utri(x,ytip,w,hh,fill,edge):
    """triangle pointing UP, tip at ytip"""
    p=c.beginPath(); p.moveTo(x-w/2,ytip-hh); p.lineTo(x+w/2,ytip-hh); p.lineTo(x,ytip); p.close()
    c.setLineJoin(1); c.setStrokeColor(HALO); c.setLineWidth(2.4); c.drawPath(p,fill=0,stroke=1)
    c.setFillColor(fill); c.setStrokeColor(edge); c.setLineWidth(.7); c.drawPath(p,fill=1,stroke=1); c.setLineJoin(0)
def block(D,top,h,VMAX,GX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h; T=tints(col); lab=DISP[D["lab"]]
    c.setFillColor(BG2); c.roundRect(x0,bot,x1-x0,h,5,fill=1,stroke=0)
    lx=x0+12; TL=top-12
    gr=38; sw=gr*20/78; ro=gr+sw/2; gy=top-14-GLAB-ro
    pb=bot+34; CEIL=TL; mh=CEIL-pb; mx0=x0+4; mx1=x1-4; rx0=mx0
    xs=[mx0+(mx1-mx0)*(.12+.83*i/(NW-1)) for i in range(NW)]
    PS={}
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=[(x_,min(y_,CEIL)) for x_,y_ in ridge(D["lab"]+k,xs,[mh*min(1,y_/VMAX) for y_ in v],rx0,mx1,pb)]; fill_ridge(P,pb,*T[k]); PS[k]=P
    c.restoreState()
    done=globals().get("TESTDONE") or DONE; BW=4.6
    bx=(xs[done-1]+xs[done])/2 if 0<done<NW else (rx0+xs[0])/2 if done==0 else (xs[-1]+mx1)/2
    nowband(bx,BW,pb,max(ridge_at(P,bx) for P in PS.values()),CEIL)
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    for i,x in enumerate(xs):
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,GR,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(col if q<lit else TRACK); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    # ---- the meter: scrim, dial, change mark, number ----
    dn=40.5                                     # v20: plate runs down over the players-left pips
    scrim(_dome(GX,gy,ro+GLAB+1,dn),al=.74,steps=9,feather=6.0); scrim(_capsule(GX-44,gy-dn-17,GX+44,gy-dn+2,7),al=.74,steps=9,feather=5.0)
    gauge(GX,gy,gr,D["pct"],col,ghost=D.get("ypct"))
    d=change_mark(GX,gy,gr,D["pct"],D.get("prev"),col)
    htxt(GX,gy-21,f"{D['pct']}%","Bebas",23,TXT,"c",hw=2.4)
    htxt(GX,gy-29,"WIN PROBABILITY","PopB",6.2,TXT,"c",hw=1.6)
    if D.get("prev") is not None:
        cc=UP if d>0 else DN if d<0 else FLAT
        s_=(f"UP {d}" if d>0 else f"DOWN {-d}" if d<0 else "NO CHANGE")+f" SINCE {PREVLAB}"
        wv=c.stringWidth(s_,"PopB",5.4); tx=GX-wv/2+4
        if d: _tri(tx-6.5,gy-37.2+(.6 if d>0 else 3.4),d>0,cc)
        htxt(tx,gy-38.4,s_,"PopB",5.4,cc,"l",hw=1.6)
    pips(GX,gy-47.5,D,col)
    # ---- identity ----
    y=TL-24*CAP
    w=htxt(lx,y,lab,"Bebas",24,col,hw=2.4) or c.stringWidth(lab,"Bebas",24); w+=6
    w+=htxt(lx+w,y,D["rec"],"Bebas",16,TXT,hw=2.2) or c.stringWidth(D["rec"],"Bebas",16); vs0=lx+w
    w+=c.stringWidth("  vs  ","PopM",7); htxt(vs0,y,"  vs  ","PopM",7,GR,hw=1.6); vs1=lx+w
    htxt(lx+w,y,f"{D['oppname'].upper()} {D['opprec']}","Bebas",16,TXT,hw=2.2)
    y2=y-18
    htxt(vs0,y2,f"{D['ym']:.1f}","Bebas",15,col,"r",hw=2.2); htxt(vs0,y2,"  vs  ","PopM",7,GR,hw=1.6)
    htxt(vs1,y2,f"{D['yo']:.1f}","Bebas",15,OPPC,hw=2.2); w=vs1+c.stringWidth(f"{D['yo']:.1f}","Bebas",15)
    _g=round(D['ym']-D['yo'],1); htxt(w+5,y2,f"({_g:+.1f})","Bebas",12,UP if _g>0 else DN if _g<0 else TXT,hw=2.0)
    htxt(lx,y2,"PROJECTED","PopB",LS,GR,hw=1.6)
    yk_=y2-LS*1.45
    if D["oppdiv"]: htxt(lx,yk_,"DIVISION GAME","PopB",LS,GR,hw=1.6); yk_-=LS*1.5
    # layer key, one row, moved up out of the mountain (Dom)
    ks=[k for k,v in reversed(D["bands"]) if k!="you"]; kx=lx; ky=yk_-3; IDBOX=(lx-3,ky-3,lx+idwidth(D)+3,top)
    for k in ks:
        cc,al,ed=T[k]; c.setFillColor(cc); c.rect(kx,ky+.2,4.2,4.2,fill=1,stroke=0)
        htxt(kx+7,ky,BANDLAB[k],"PopM",4.7,mix(cc,TXT,.40),hw=1.4); kx+=7+c.stringWidth(BANDLAB[k],"PopM",4.7)+9
    # ---- balls: on their own scrim, in front of the mountain ----
    br=19; lgx=x1-40; dvx=lgx-50; ry=TL-6.4*CAP-7-br
    scrim(_capsule(dvx-br-2,ry-br-3,lgx+br+2,TL+1,12),al=.74,steps=9,feather=5.0); BALLBOX=(dvx-br-2-5,ry-br-3-5,lgx+br+2+5,top)
    dn_,dp,dlab,dsub=D["dv"]
    ring19(dvx,ry,br,dn_,dp,None,col,dlab)
    ring19(lgx,ry,br,D["n"],D["rank"],None,col,"LEAGUE")
    for x,l in ((dvx,dlab),(lgx,"LEAGUE")): txt(x,TL-6.4*CAP,l,"PopB",6.4,TXT,"c")
    # ---- banked marks: mine left of the now-band, his right; point at the ridge; above, else below, else step outward ----
    a=ACT.get(D["lab"]); pm=sum(v_ for v_ in a["me"][:done] if v_) if done else 0.0; po=sum(v_ for v_ in a["op"][:done] if v_) if done else 0.0
    cm=sum(D["me"]["cnt"][:done]); co=sum(D["op"]["cnt"][:done]); Y=YL[D["lab"]]
    METERBOX=(GX-(ro+GLAB+1)-6,gy-dn-17-5,GX+(ro+GLAB+1)+6,top)
    OBS=[IDBOX,BALLBOX,METERBOX]
    S=[dict(side=-1,k="you",pts=pm,lab=f"{cm} OF {len(Y['me'])}",pc=col),
       dict(side=1,k="opp",pts=po,lab=f"{co} OF {len(Y['op'])}",pc=mix(STEEL,TXT,.30))]
    for d_ in S: d_.update(stack_dims(f"{d_['pts']:.1f}",d_["lab"]))
    plan=place_marks(S,bx,BW,PS,CEIL,pb,OBS,x0+6,x1-6)
    for d_,(mode,x,yr) in zip(S,plan): draw_mark(d_,mode,x,yr,T[d_["k"]])
    D["marks"]=[(d_["k"],d_["ps"],d_["ls"])+d_["placed"] for d_ in S]
    # ---- note line: mark on the left, colored by urgency; sentence right-justified, one font, one color ----
    pr=PROSE[D["lab"]].format(w=D["whatif"][2] if "whatif" in D else "")
    yb=bot+7.5; urg=URG.get(D["lab"],"info"); mc={"act":DN,"watch":HOLD,"info":GR}[urg]
    sw_=sheet(lx,yb,4.2,mc); fs=6.0; rx=x1-12; lim=rx-(lx+sw_+40)
    while c.stringWidth(pr,"Pop",fs)>lim: fs-=.05
    txt(rx,yb,pr,"Pop",fs,mix(GR,TXT,.25),"r")
    return dvx-br
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT FANTASY","Bebas",24); txt(W-M,y,"GLOBAL STANDINGS  ·  WEEK 4","Bebas",24,TXT,"r")
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Yahoo matchups and lineups  ·  ","Pop",sf,GR2); txt(M+w,y2,"Friday injury reports not yet pulled","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Yahoo pulled Fri Oct 2 morning, all 44 teams  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    span=W-2*M; fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-40-50-26
    GX=(idr+balll)/2-6
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(DISP[D["lab"]],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED is Yahoo's live projection pulled Friday morning (banked plus still to play). WIN PROBABILITY is the system's own model; the dotted needle is Yahoo's own win %, and the tick outside the dial is where the meter stood "+PREVLAB.lower()+", the arc between it green for a gain, red for a loss.  "
          "The MOUNTAIN runs on the lineups as set in Yahoo, finished windows at actual points (league and division layers from every team's set lineup, same Friday pull). In the balls the fluid stops at your place and the white line is the cut, 1st division and 6th league (DK IV left ball: points-for rank). The PIPS under the meter are starters, filled once played, mine above, his below. The BAND is now: banked points beside it, yours left, his right.")
    FL=simpleSplit(foot,"Pop",4.6,W-2*M)
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=(38+2.5*(len(FL)-2))-j*5.5
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",4.6,GR2); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",4.6) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",4.6,GR2); x_+=c.stringWidth(w,"Pop",4.6)+g
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,21,W-M,21)
    txt(M,11,"DARK KNIGHT FANTASY SCAN","Bebas",10,GR)
    txt(W-M,11,"GLOBAL STANDINGS  ·  WEEK 4  ·  GLOBAL PAGE v21","Bebas",10,GR,"r")
    c.save(); return DS,GX,idr



# ===================== v22: Dom's voice batch (Fri Oct 2 morning, after seeing v21) =====================
# 1. Banked stack carries the points only -- the starters-played count line is gone (the squares carry it).
# 2. Starter squares move out from under the dial into the left column: layer key, a hairline, then the squares,
#    with the to-play count beside each row. Opaque, no plate (the mountain never reaches that corner).
# 3. DK I: DIVISION sits above PROJECTED; the layer key tucks straight under PROJECTED, same as the other three.
# 4. Now-band becomes one crisp white edge, the shadow trailing LEFT over what has been played; nothing on top or right.
# 5. Banked marks hold one fixed, equal distance from the edge on both sides; each sits on its own ridge,
#    flipping below only on its own side. They move vertically, never sideways.
# 6. The edge runs up to the top of the higher mark and never past it.
# 7. Fixed stacking order: meter in front, edge + marks second, everything else behind.
#    Every layer's ridge line draws through the other mountains' fills; nothing draws through the meter, edge or marks.
FADE=12.0; EDGE_LW=1.0; MGAP=3.0
# ===================== v23: Dom's voice batch (Fri Oct 2, after seeing v22) =====================
PTS_FS=9.5     # banked number trimmed so it no longer competes with the projected scores
PIN_R=1.7      # pin head on the now-edge
PLATE_A=.50    # one translucency for the meter plate and both ball plates
OPP_SQ=OPPC    # his squares and his banked number: the flat opponent grey
CNT_FS=4.1     # the "N TO PLAY" footnote
def nowedge(bx,pb,yt):
    if yt<=pb+1: yt=pb+6
    c.saveState(); N=14
    for i in range(N):                                   # shadow: darkest at the edge, gone by FADE to the left
        xa=bx-FADE*(i+1)/N; xb=bx-FADE*i/N
        c.setFillColor(BG); c.setFillAlpha(.62*(1-i/N)); c.rect(xa,pb,xb-xa+.05,yt-pb,fill=1,stroke=0)
    c.setFillAlpha(1); c.setStrokeColor(TXT); c.setStrokeAlpha(.97); c.setLineWidth(EDGE_LW); c.setLineCap(0)
    c.line(bx,pb,bx,yt)
    c.setFillColor(TXT); c.setFillAlpha(.97); c.circle(bx,yt,PIN_R,fill=1,stroke=0); c.restoreState()
def stack_dims(ps,ls=None):
    pw=c.stringWidth(ps,"Bebas",PTS_FS); return dict(ps=ps,sw=pw,pw=pw)
def _rect(mode,x,yr,d):
    ph=PTS_FS*CAP; hh=TRI_H+G1+ph; hw=max(d["sw"],TRI_W)/2+1.0
    return (x-hw,yr+.8,x+hw,yr+.8+hh) if mode=="above" else (x-hw,yr-.8-hh,x+hw,yr-.8)
def place_marks(S,bx,PS,ceil,pb,OBS,xmin,xmax):
    """one offset for both sides, measured edge-to-centre, sized by the wider stack; each side picks above or below on its own"""
    off=MGAP+c.stringWidth("00.0","Bebas",PTS_FS)/2+2.0; plan=[]       # one distance, every card, every week
    for d in S:
        x=bx+d["side"]*off; yr=ridge_at(PS[d["k"]],x); got=None
        for strict in (True,False):
            for mode in ("above","below"):
                r=_rect(mode,x,yr,d)
                if r[0]<xmin or r[2]>xmax or r[3]>ceil or (mode=="below" and r[1]<pb+1.5): continue
                if strict and any(_hit(r,o) for o in OBS): continue
                got=(mode,x,yr); break
            if got: break
        plan.append(got or ("above",x,yr))
    return plan,off
def draw_mark(d,mode,x,yr,Tk):
    cc,al,ed=Tk; ph=PTS_FS*CAP
    if mode=="above": dtri(x,yr+.8,TRI_W,TRI_H,cc,ed); yp=yr+.8+TRI_H+G1
    else: utri(x,yr-.8,TRI_W,TRI_H,cc,ed); yp=yr-.8-TRI_H-G1-ph
    hw=d["sw"]/2+1.0; scrim(_capsule(x-hw,yp-.6,x+hw,yp+ph+.6,2.0),al=.42,steps=10,feather=3.2)
    htxt(x,yp,d["ps"],"Bebas",PTS_FS,d["pc"],"c",hw=1.2)
    d["placed"]=(mode,round(x,1),round(yr,1))
def _livecount(rows):
    """starters whose game has kicked off and is not final (NFL schedule), not yet banked"""
    import datetime as _ld; from zoneinfo import ZoneInfo as _lz
    now=_ld.datetime.now(_ld.timezone.utc); n=0
    for r in rows:
        if r[4] is not None or not r[1]: continue
        t={"LAR":"LA","JAC":"JAX","WSH":"WAS"}.get(r[1],r[1]); g=G[(G.home_team==t)|(G.away_team==t)]
        if g.empty or g.result.notna().iloc[0]: continue
        try: ko=_ld.datetime.strptime(f"{g.gameday.iloc[0]} {g.gametime.iloc[0]}","%Y-%m-%d %H:%M").replace(tzinfo=_lz("America/New_York"))
        except Exception: continue
        if ko<=now<=ko+_ld.timedelta(hours=4): n+=1
    return n
def pips22(x0,y,D,col):
    Y=YL[D["lab"]]; cnt=lambda side:(len(Y[side]),sum(1 for r in Y[side] if r[4] is not None))
    rows=((*cnt("me"),col),(*cnt("op"),OPP_SQ))
    pw,ph,pg=5.0,3.0,2.0; n=max(r[0] for r in rows); wd=n*pw+(n-1)*pg
    _cp=COMP[D["lab"]]; _pc=(_cp["me_pct"],_cp["op_pct"])
    for j,(tot,pl,cc) in enumerate(rows):
        yy=y-j*6.4
        lv=_livecount(Y["me" if j==0 else "op"])   # Oct 11 (Dom): men playing right now
        for k in range(tot):
            x=x0+k*(pw+pg)
            if k<pl: c.setFillColor(cc); c.roundRect(x,yy,pw,ph,.8,fill=1,stroke=0)
            elif k<pl+lv:
                c.saveState(); c.setFillColor(H("#3FB36A"))
                for e_,a_ in ((1.6,.18),(.8,.32)): c.setFillAlpha(a_); c.roundRect(x-e_,yy-e_,pw+2*e_,ph+2*e_,.8+e_,fill=1,stroke=0)
                c.setFillAlpha(1); c.setFillColor(H("#4FD08A")); c.roundRect(x,yy,pw,ph,.8,fill=1,stroke=0); c.restoreState()
            else: c.setStrokeColor(mix(cc,BG2,.35)); c.setLineWidth(.6); c.roundRect(x+.3,yy+.3,pw-.6,ph-.6,.7,fill=0,stroke=1)
        txt(x0+wd+3.5,yy+.1,f"{_pc[j]}% PLAYED","PopB",CNT_FS,mix(GR,cc,.30))   # v34: share of projected points already banked
    return y-6.4-ph
def ridges(P,base,col,al,edge):
    p=c.beginPath(); p.moveTo(P[0][0],base)
    for x,y in P: p.lineTo(x,y)
    p.lineTo(P[-1][0],base); p.close()
    c.saveState(); c.setFillColor(col); c.setFillAlpha(al); c.drawPath(p,fill=1,stroke=0); c.restoreState()
def rline(P,edge,ew=.8,halo=True):
    for lw,cc,a in (((ew+1.4,BG,.55),(ew,edge,1)) if halo else ((ew,edge,1),)):
        q=c.beginPath(); q.moveTo(*P[0])
        for x,y in P[1:]: q.lineTo(x,y)
        c.saveState(); c.setStrokeColor(cc); c.setStrokeAlpha(a); c.setLineWidth(lw); c.drawPath(q,fill=0,stroke=1); c.restoreState()
def block(D,top,h,VMAX,GX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h; T=tints(col); lab=DISP[D["lab"]]
    c.setFillColor(BG2); c.roundRect(x0,bot,x1-x0,h,5,fill=1,stroke=0)
    lx=x0+12; TL=top-12
    gr=38; sw=gr*20/78; ro=gr+sw/2; gy=top-14-GLAB-ro
    pb=bot+34; CEIL=TL; mh=CEIL-pb; mx0=x0+4; mx1=x1-4; rx0=mx0
    xs=[mx0+(mx1-mx0)*(.12+.83*i/(NW-1)) for i in range(NW)]
    PS={}
    # ---- layer 3 (back): mountain fills, then every ridge line over every fill ----
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=[(x_,min(y_,CEIL)) for x_,y_ in ridge(D["lab"]+k,xs,[mh*min(1,y_/VMAX) for y_ in v],rx0,mx1,pb)]; ridges(P,pb,*T[k]); PS[k]=P
    for k,v in D["bands"]: rline(PS[k],T[k][2])
    c.restoreState()
    done=globals().get("TESTDONE") or DONE
    bx=(xs[done-1]+xs[done])/2 if 0<done<NW else (rx0+xs[0])/2 if done==0 else (xs[-1]+mx1)/2
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    for i,x in enumerate(xs):
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,GR,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(col if q<lit else TRACK); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    # ---- identity ----
    y=TL-24*CAP
    w=htxt(lx,y,lab,"Bebas",24,col,hw=2.4) or c.stringWidth(lab,"Bebas",24); w+=6
    w+=htxt(lx+w,y,D["rec"],"Bebas",16,TXT,hw=2.2) or c.stringWidth(D["rec"],"Bebas",16); vs0=lx+w
    w+=c.stringWidth("  vs  ","PopM",7); htxt(vs0,y,"  vs  ","PopM",7,GR,hw=1.6); vs1=lx+w
    htxt(lx+w,y,f"{D['oppname'].upper()} {D['opprec']}","Bebas",16,TXT,hw=2.2)
    y2=y-18
    if D["oppdiv"]: htxt(lx,y2+LS*1.25,"DIVISION","PopB",LS,GR,hw=1.6)
    htxt(vs0,y2,f"{D['ym']:.1f}","Bebas",15,col,"r",hw=2.2); htxt(vs0,y2,"  vs  ","PopM",7,GR,hw=1.6)
    htxt(vs1,y2,f"{D['yo']:.1f}","Bebas",15,OPPC,hw=2.2); w=vs1+c.stringWidth(f"{D['yo']:.1f}","Bebas",15)
    _g=round(D['ym']-D['yo'],1); htxt(w+5,y2,f"({_g:+.1f})","Bebas",12,UP if _g>0 else DN if _g<0 else TXT,hw=2.0)
    htxt(lx,y2,"PROJECTED","PopB",LS,GR,hw=1.6)
    ks=[k for k,v in reversed(D["bands"]) if k!="you"]; kx=lx; ky=y2-LS*1.45-3
    for k in ks:
        cc,al,ed=T[k]; c.setFillColor(cc); c.rect(kx,ky+.2,4.2,4.2,fill=1,stroke=0)
        htxt(kx+7,ky,BANDLAB[k],"PopM",4.7,mix(cc,TXT,.40),hw=1.4); kx+=7+c.stringWidth(BANDLAB[k],"PopM",4.7)+9
    hy=ky-3.6; Y_=YL[D["lab"]]; nmax=max(len(Y_["me"]),len(Y_["op"])); pr_=nmax*5.0+(nmax-1)*2.0+3.5+c.stringWidth("100% PLAYED","PopB",CNT_FS)
    c.setStrokeColor(mix(GR2,BG2,.15)); c.setLineWidth(.4); c.line(lx,hy,lx+max(kx-9-lx,pr_),hy)
    ylow=pips22(lx,hy-7.8,D,col)   # v23: a little air between the rule and the squares
    IDBOX=(lx-3,ylow-3,lx+idwidth(D)+3,top)
    # ---- balls ----
    br=19; lgx=x1-40; dvx=lgx-50; ry=TL-6.4*CAP-7-br
    scrim(_capsule(dvx-br-2,ry-br-3,lgx+br+2,TL+1,12),al=PLATE_A,steps=9,feather=5.0); BALLBOX=(dvx-br-2-5,ry-br-3-5,lgx+br+2+5,top)
    dn_,dp,dlab,dsub=D["dv"]
    ring19(dvx,ry,br,dn_,dp,None,col,dlab)
    ring19(lgx,ry,br,D["n"],D["rank"],None,col,"LEAGUE")
    for x,l in ((dvx,dlab),(lgx,"LEAGUE")): txt(x,TL-6.4*CAP,l,"PopB",6.4,TXT,"c")
    # ---- note line ----
    pr=PROSE[D["lab"]].format(w=D["whatif"][2] if "whatif" in D else "")
    yb=bot+7.5; urg=URG.get(D["lab"],"info"); mc={"act":DN,"watch":HOLD,"info":GR}[urg]
    sw_=4.2*1.12; fs=6.0; rx=x1-12; lim=rx-(lx+sw_+40)
    while c.stringWidth(pr,"Pop",fs)>lim: fs-=.05
    txt(rx,yb,pr,"Pop",fs,mix(GR,TXT,.25),"r"); tx0=rx-c.stringWidth(pr,"Pop",fs)
    sheet(tx0-sw_-3.5,yb,4.2,mc)                         # the mark travels with the first word
    # ---- layer 2: the now edge and the banked marks ----
    a=ACT.get(D["lab"]); pm=sum(v_ for v_ in a["me"][:done] if v_) if done else 0.0; po=sum(v_ for v_ in a["op"][:done] if v_) if done else 0.0
    S=[dict(side=-1,k="you",pts=pm,pc=col),dict(side=1,k="opp",pts=po,pc=OPP_SQ)]
    for d_ in S: d_.update(stack_dims(f"{d_['pts']:.1f}"))
    plan,off=place_marks(S,bx,PS,CEIL,pb,[IDBOX,BALLBOX],x0+6,x1-6)
    tops=[_rect(m,x,yr,d_)[3] for d_,(m,x,yr) in zip(S,plan)]
    yt=min(CEIL,max(tops)+2)   # Oct 11 (Dom): the pole ends just above the flags, not at the tallest ridge
    dn=31.5   # v24: meter plates go down BEFORE the now-edge and banked marks, so the marks print over them
    scrim(_dome(GX,gy,ro+GLAB+1,dn),al=PLATE_A,steps=9,feather=6.0); scrim(_capsule(GX-44,gy-dn-12,GX+44,gy-dn,7),al=PLATE_A,steps=9,feather=5.0)
    nowedge(bx,pb,yt)
    for d_,(mode,x,yr) in zip(S,plan): draw_mark(d_,mode,x,yr,T[d_["k"]])
    D["marks"]=[(d_["k"],d_["ps"])+d_["placed"] for d_ in S]; D["edge"]=(round(bx,1),round(yt,1),round(off,1))
    # ---- layer 1 (front): the meter (plates already drawn behind the marks) ----
    gauge(GX,gy,gr,D["pct"],col,ghost=D.get("ypct"))
    d=change_mark(GX,gy,gr,D["pct"],D.get("prev"),col)
    htxt(GX,gy-23,f"{D['pct']}%","Bebas",23,TXT,"c",hw=2.4)
    htxt(GX,gy-31,"WIN PROBABILITY","PopB",6.2,TXT,"c",hw=1.6)
    if D.get("prev") is not None:
        cc=UP if d>0 else DN if d<0 else FLAT
        s_=(f"UP {d}" if d>0 else f"DOWN {-d}" if d<0 else "NO CHANGE")+f" SINCE {PREVLAB}"
        wv=c.stringWidth(s_,"PopB",5.4); tx=GX-wv/2+4
        if d: _tri(tx-6.5,gy-39.2+(.6 if d>0 else 3.4),d>0,cc)
        htxt(tx,gy-40.4,s_,"PopB",5.4,cc,"l",hw=1.6)
    return dvx-br
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    c.setFillColor(BG); c.rect(0,0,W,Ht,fill=1,stroke=0)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    y=Ht-M-10
    txt(M,y,"DARK KNIGHT DISPATCH","Bebas",24); txt(W-M,y,"OVERVIEW  ·  WEEK 4","Bebas",24,TXT,"r")
    pt=NOWUTC-_dt.timedelta(hours=7); hh=pt.hour%12 or 12; mm=int(round(pt.minute/5)*5)
    if mm==60: hh,mm=hh%12+1,0
    sf=5.8; y2=y-13
    w=txt(M,y2,"Rosters, injuries and the market re-pulled Sat Oct 3 night  ·  ","Pop",sf,GR2); txt(M+w,y2,"mountains and meters: Friday's 44-team lineup pull","Pop",sf,GOLDISH)
    txt(W-M,y2,f"Lineups Fri Oct 2 morning, all 44 teams  ·  rebuilt {pt.strftime('%a %b')} {pt.day}, ~{hh}:{mm:02d} {'p.m.' if pt.hour>=12 else 'a.m.'} PT","Pop",sf,GR2,"r")
    span=W-2*M; fs=13.0; U=lambda l: FULL[l].upper()+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(TEAMN[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=y-28
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,GR); txt(sx+w,y3,TEAMN[l].upper(),"Bebas",fs,LC[l]); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(0,y-33,W,y-33)
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-40-50-26
    GX=(idr+balll)/2-6
    top=y-43; gap=10; bottom=48; h=(top-bottom-3*gap)/4
    global LS; LS=9.0
    def _room(D):
        w=c.stringWidth(DISP[D["lab"]],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("PROJECTED","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("PROJECTED is Yahoo's live projection, pulled Friday morning (banked plus still to play). WIN PROBABILITY is the system's own model; the dotted needle is Yahoo's win %, "
          "the outside tick where it stood "+PREVLAB.capitalize()+", green arc a gain, red a loss. The MOUNTAIN uses lineups as set in Yahoo, finished windows at actual points. "
          "In the balls the fluid stops at your place and the white line is the cut: 1st in division, 6th in league (DK IV left ball: points-for rank). "
          "SQUARES are starters, filled once played, yours above, his below. The white pin is now, shading back over what has played; banked points beside it, yours left, his right.")
    FFS=4.7; FLD=6.4; FL=simpleSplit(foot,"Pop",FFS,W-2*M)
    assert len(FL)<=3,len(FL)
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=40.2-j*FLD
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",FFS,GR2); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",FFS) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",FFS,GR2); x_+=c.stringWidth(w,"Pop",FFS)+g
    print("FOOTLINES",len(FL))
    c.setStrokeColor(mix(GR2,BG,.2)); c.setLineWidth(.5); c.line(M,20,W-M,20)
    txt(M,10,"DARK KNIGHT DISPATCH","Bebas",10,GR)
    txt(W-M,10,"OVERVIEW  ·  WEEK 4","Bebas",10,GR,"r")
    c.save(); return DS,GX,idr





# ===================== v26: Saturday-night refresh + one masthead for every page (Dom's voice batch, Sat Oct 3 ~10 p.m. PT) =====================
# 1. All 44 set lineups re-pulled from Yahoo matchup pages Sat Oct 3 ~10:20 p.m. PT (league_windows_sat.txt, 44 of 44, 0 errors);
#    Dom's four matchups (both sides, player by player) in yl_sat.json. Yahoo's own win % did not parse - the ghost needle is off.
# 2. Labels say whose number it is: YAHOO PROJECTED; MODELED WIN CHANCE (our math on Yahoo's projections); the balls are STANDINGS.
# 3. The page no longer draws its own title or background: it is merged onto the document's own masthead page (same puzzle,
#    same paper, same footer as every other page). The four league names sit in a strip under the masthead, above DK I.
import json as _json2
_Y=_json2.load(open("/home/claude/dksys/data/latest/yahoo/wk4/yl_sun.json"))   # v33: live scan
YL={l:dict(me=[tuple(r) for r in v["me"]],op=[tuple(r) for r in v["op"]],live=tuple(v["live"]),ypct=None) for l,v in _Y["YL"].items()}
YAH={l:YL[l]["live"] for l in YL}
LW={}
for _l in open("/home/claude/dksys/data/latest/yahoo/wk4/league_windows_sun1420.txt"):
    if _l.startswith("#") or not _l.strip(): continue
    _p=_l.strip().split("~"); LW.setdefault(int(_p[0]),{})[int(_p[1])]=[float(x) for x in _p[2].split()]
WHATIF={}
PREV={"DK I":54,"DK II":43,"DK III":48,"DK IV":72}; PREVLAB="FRI MORNING"     # the model's Friday-morning readings
URG={"DK IV":"watch"}
PROSE={
 "DK I":"DIKFORE put Bucky Irving back in their lineup, which erases Friday's edge. Warren and Boswell banked 23.9 for you Thursday.",
 "DK II":"Metcalf's 17.5 is banked for Raider Fan. Your lineup is set; Bills defense starts. You trail by 7.6 on Yahoo's numbers.",
 "DK III":"White is out, so Holani starts. Fannin and the Steelers defense banked 18.7 for you Thursday.",
 "DK IV":"Wan'Dale Robinson is in for Romeo Doubs. Flowers (Q): Baltimore inactives about 8:30 a.m. PT Sunday; Kraft if he sits.",
}
PAPERC=Color(0xFB/255,0xF7/255,0xEF/255); INKC=Color(0x14/255,0x21/255,0x3D/255); GREYC=Color(0x55/255,0x5B/255,0x68/255)
def _dark(col,t=.30): return mix(col,Color(0,0,0),t)
def block(D,top,h,VMAX,GX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h; T=tints(col); lab=DISP[D["lab"]]
    c.setFillColor(BG2); c.roundRect(x0,bot,x1-x0,h,5,fill=1,stroke=0)
    lx=x0+12; TL=top-12
    gr=38; sw=gr*20/78; ro=gr+sw/2; gy=top-14-GLAB-ro
    pb=bot+34; CEIL=TL; mh=CEIL-pb; mx0=x0+4; mx1=x1-4; rx0=mx0
    xs=[mx0+(mx1-mx0)*(.12+.83*i/(NW-1)) for i in range(NW)]
    PS={}
    # ---- layer 3 (back): mountain fills, then every ridge line over every fill ----
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=[(x_,min(y_,CEIL)) for x_,y_ in ridge(D["lab"]+k,xs,[mh*min(1,y_/VMAX) for y_ in v],rx0,mx1,pb)]; ridges(P,pb,*T[k]); PS[k]=P
    for k,v in D["bands"]: rline(PS[k],T[k][2])
    c.restoreState()
    done=globals().get("TESTDONE") or DONE
    bx=(xs[done-1]+xs[done])/2 if 0<done<NW else (rx0+xs[0])/2 if done==0 else (xs[-1]+mx1)/2
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    for i,x in enumerate(xs):
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,GR,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(col if q<lit else TRACK); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    # ---- identity ----
    y=TL-24*CAP
    w=htxt(lx,y,lab,"Bebas",24,col,hw=2.4) or c.stringWidth(lab,"Bebas",24); w+=6
    w+=htxt(lx+w,y,D["rec"],"Bebas",16,TXT,hw=2.2) or c.stringWidth(D["rec"],"Bebas",16); vs0=lx+w
    w+=c.stringWidth("  vs  ","PopM",7); htxt(vs0,y,"  vs  ","PopM",7,GR,hw=1.6); vs1=lx+w
    htxt(lx+w,y,f"{D['oppname'].upper()} {D['opprec']}","Bebas",16,TXT,hw=2.2)
    y2=y-18
    if D["oppdiv"]: htxt(lx,y2+LS*1.25,"DIVISION","PopB",LS,GR,hw=1.6)
    htxt(vs0,y2,f"{D['ym']:.1f}","Bebas",15,col,"r",hw=2.2); htxt(vs0,y2,"  vs  ","PopM",7,GR,hw=1.6)
    htxt(vs1,y2,f"{D['yo']:.1f}","Bebas",15,OPPC,hw=2.2); w=vs1+c.stringWidth(f"{D['yo']:.1f}","Bebas",15)
    _g=round(D['ym']-D['yo'],1); htxt(w+5,y2,f"({_g:+.1f})","Bebas",12,UP if _g>0 else DN if _g<0 else TXT,hw=2.0)
    htxt(lx,y2,"YAHOO","PopB",LS,GR,hw=1.6)
    ks=[k for k,v in reversed(D["bands"]) if k!="you"]; kx=lx; ky=y2-LS*1.45-3
    for k in ks:
        cc,al,ed=T[k]; c.setFillColor(cc); c.rect(kx,ky+.2,4.2,4.2,fill=1,stroke=0)
        htxt(kx+7,ky,BANDLAB[k],"PopM",4.7,mix(cc,TXT,.40),hw=1.4); kx+=7+c.stringWidth(BANDLAB[k],"PopM",4.7)+9
    hy=ky-3.6; Y_=YL[D["lab"]]; nmax=max(len(Y_["me"]),len(Y_["op"])); pr_=nmax*5.0+(nmax-1)*2.0+3.5+c.stringWidth("100% PLAYED","PopB",CNT_FS)
    c.setStrokeColor(mix(GR2,BG2,.15)); c.setLineWidth(.4); c.line(lx,hy,lx+max(kx-9-lx,pr_),hy)
    ylow=pips22(lx,hy-7.8,D,col)   # v23: a little air between the rule and the squares
    IDBOX=(lx-3,ylow-3,lx+idwidth(D)+3,top)
    # ---- balls ----
    br=19; lgx=x1-40; dvx=lgx-50; ry=TL-6.4*CAP-7-br
    scrim(_capsule(dvx-br-2,ry-br-12,lgx+br+2,TL+1,12),al=PLATE_A,steps=9,feather=5.0); BALLBOX=(dvx-br-2-5,ry-br-3-5,lgx+br+2+5,top)
    dn_,dp,dlab,dsub=D["dv"]
    ring19(dvx,ry,br,dn_,dp,None,col,dlab)
    ring19(lgx,ry,br,D["n"],D["rank"],None,col,"LEAGUE")
    for x,l in ((dvx,dlab),(lgx,"LEAGUE")): txt(x,TL-6.4*CAP,l,"PopB",6.4,TXT,"c")
    txt((dvx+lgx)/2,ry-br-9.2,"STANDINGS  ·  AFTER WEEK 3","PopB",4.6,mix(GR,TXT,.45),"c")
    # ---- note line ----
    pr=PROSE[D["lab"]].format(w=D["whatif"][2] if "whatif" in D else "")
    yb=bot+7.5; urg=URG.get(D["lab"],"info"); mc={"act":DN,"watch":HOLD,"info":GR}[urg]
    sw_=4.2*1.12; fs=6.0; rx=x1-12; lim=rx-(lx+sw_+40)
    while c.stringWidth(pr,"Pop",fs)>lim: fs-=.05
    txt(rx,yb,pr,"Pop",fs,mix(GR,TXT,.25),"r"); tx0=rx-c.stringWidth(pr,"Pop",fs)
    sheet(tx0-sw_-3.5,yb,4.2,mc)                         # the mark travels with the first word
    # ---- layer 2: the now edge and the banked marks ----
    a=ACT.get(D["lab"]); pm=sum(v_ for v_ in a["me"][:done] if v_) if done else 0.0; po=sum(v_ for v_ in a["op"][:done] if v_) if done else 0.0
    S=[dict(side=-1,k="you",pts=pm,pc=col),dict(side=1,k="opp",pts=po,pc=OPP_SQ)]
    for d_ in S: d_.update(stack_dims(f"{d_['pts']:.1f}"))
    plan,off=place_marks(S,bx,PS,CEIL,pb,[IDBOX,BALLBOX],x0+6,x1-6)
    tops=[_rect(m,x,yr,d_)[3] for d_,(m,x,yr) in zip(S,plan)]
    yt=min(CEIL,max(tops)+2)   # Oct 11 (Dom): the pole ends just above the flags, not at the tallest ridge
    dn=31.5   # v24: meter plates go down BEFORE the now-edge and banked marks, so the marks print over them
    scrim(_dome(GX,gy,ro+GLAB+1,dn),al=PLATE_A,steps=9,feather=6.0); scrim(_capsule(GX-44,gy-dn-12,GX+44,gy-dn,7),al=PLATE_A,steps=9,feather=5.0)
    nowedge(bx,pb,yt)
    for d_,(mode,x,yr) in zip(S,plan): draw_mark(d_,mode,x,yr,T[d_["k"]])
    D["marks"]=[(d_["k"],d_["ps"])+d_["placed"] for d_ in S]; D["edge"]=(round(bx,1),round(yt,1),round(off,1))
    # ---- layer 1 (front): the meter (plates already drawn behind the marks) ----
    gauge(GX,gy,gr,D["pct"],col,ghost=D.get("ypct"))
    d=change_mark(GX,gy,gr,D["pct"],D.get("prev"),col)
    htxt(GX,gy-23,f"{D['pct']}%","Bebas",23,TXT,"c",hw=2.4)
    htxt(GX,gy-31,"MODELED WIN CHANCE","PopB",5.6,TXT,"c",hw=1.6)
    if D.get("prev") is not None:
        cc=UP if d>0 else DN if d<0 else FLAT
        s_=(f"UP {d}" if d>0 else f"DOWN {-d}" if d<0 else "NO CHANGE")+f" SINCE {PREVLAB}"
        wv=c.stringWidth(s_,"PopB",5.4); tx=GX-wv/2+4
        if d: _tri(tx-6.5,gy-39.2+(.6 if d>0 else 3.4),d>0,cc)
        htxt(tx,gy-40.4,s_,"PopB",5.4,cc,"l",hw=1.6)
    return dvx-br

def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    # league strip: under the masthead's gold rule (Ht-87), above DK I's card
    span=W-2*M; fs=12.0; U=lambda l: l+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(FULL[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*14>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=M; y3=Ht-87-15
    for l in LG:
        w=txt(sx,y3,U(l),"Bebas",fs,INKC); txt(sx+w,y3,FULL[l].upper(),"Bebas",fs,_dark(LC[l])); sx+=lw(l,fs)+g
    global LGFS; LGFS=fs
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-40-50-26
    GX=(idr+balll)/2-6
    top=y3-9; gap=8; bottom=50; h=(top-bottom-3*gap)/4
    global LS; LS=7.0
    def _room(D):
        w=c.stringWidth(DISP[D["lab"]],"Bebas",24)+6+c.stringWidth(D["rec"],"Bebas",16)+c.stringWidth("  vs  ","PopM",7)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",15)-3.2
    while any(c.stringWidth("YAHOO","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("YAHOO: Yahoo's own live projection for each lineup as set, pulled Sat Oct 3 night, banked points plus still to play. "
          "MODELED WIN CHANCE: our own math on those Yahoo numbers; the outside tick is where it stood "+PREVLAB.capitalize()+", green arc a gain, red a loss (Yahoo's own win % did not read). "
          "MOUNTAIN: the same Yahoo projections by kickoff window, Pacific, for you, him, your division and the league - finished windows at actual points. "
          "STANDINGS balls: the fluid stops at your place, the white line is the cut (1st in division, 6th in league; DK IV left ball: points-for rank). "
          "SQUARES are starters, filled once played, yours above, his below.")
    FFS=4.7; FLD=6.2; FL=simpleSplit(foot,"Pop",FFS,W-2*M)
    assert len(FL)<=4,len(FL)
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=43.5-j*FLD
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",FFS,GREYC); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",FFS) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",FFS,GREYC); x_+=c.stringWidth(w,"Pop",FFS)+g
    print("FOOTLINES",len(FL),"LS",round(LS,2),"h",round(h,1))
    c.save(); return DS,GX,idr



# ===================== v27: both reads on every card + quiet mountain tag (Dom's voice batch, Sat Oct 3 ~11 p.m. PT) =====================
# MODELED line under the YAHOO line: engine2 week-4 modeled points for each starter (Thursday players at actual; K and DEF at
# Yahoo, which the engine does not model; a man the engine cannot model falls back to Yahoo). Win chance from each, same spread.
# Meter: solid needle = win chance on Yahoo's numbers, dotted needle = modeled, read out beside the big number.
MOD=_json2.load(open("/home/claude/dksys/data/latest/yahoo/wk4/yl_sun.json"))["MOD"]   # v33: workload, live scan
PROSE={
 "DK I":"DIKFORE put Bucky Irving back in. With Breece Hall out, modeled now hands his work to DIKFORE's Braelon Allen, and the two reads sit a point apart.",
 "DK II":"Braelon Allen is active with Hall out. Modeled now discounts Raider Fan's one-game Brock Bowers; the two reads sit a point apart. Metcalf's 17.5 is banked.",
 "DK III":"White is out, so Holani starts. Modeled sits lower: it rates Benchdad's Kenneth Walker III well above Yahoo. Fannin and the Steelers banked 18.7 Thursday.",
 "DK IV":"Wan'Dale Robinson is in for Romeo Doubs. Both reads have you ahead. Flowers is active (Ravens and ESPN, Sunday morning).",
}
# ===================== v29: Dom's voice batch (Sat Oct 3 late) =====================
# 1. Banked marks: the total is cumulative through the last finished window (Thursday carries forward, never resets).
# 2. Triangles grow so a three-digit total and the margin fit; MY triangle carries the signed margin inside it,
#    filled green when ahead, red when behind, grey when even. HIS triangle is the same size, plain grey.
# 3. Meter has two states: PROJECTED WIN PROBABILITY while games remain; FINAL with WON / LOST once every window is played.
TRI_W,TRI_H=14.5,9.6   # v30: smaller - the inside margin is a whole number now
MARG_FS=6.0
def stack_dims(ps,ls=None):
    pw=c.stringWidth(ps,"Bebas",PTS_FS); return dict(ps=ps,sw=max(pw,TRI_W),pw=pw)
def place_marks(S,bx,PS,ceil,pb,OBS,xmin,xmax):
    off=MGAP+TRI_W/2+3.5; plan=[]   # v30: held at the v29 distance from the edge after the triangle shrank
    for d in S:
        x=bx+d["side"]*off; yr=ridge_at(PS[d["k"]],x); got=None
        for strict in (True,False):
            for mode in ("above","below"):
                r=_rect(mode,x,yr,d)
                if r[0]<xmin or r[2]>xmax or r[3]>ceil or (mode=="below" and r[1]<pb+1.5): continue
                if strict and any(_hit(r,(o[0],o[1]+3.2,o[2],o[3])) for o in OBS): continue   # v30: the boxes carry 3pt of padding; a mark may use it
                got=(mode,x,yr); break
            if got: break
        plan.append(got or ("above",x,yr))
    return plan,off
def _rect(mode,x,yr,d):
    """v29: banked number sits beside the triangle on the outward side, level with its wide edge"""
    sd=d["side"]; hw=TRI_W/2+.8; nw=d["pw"]+2.6
    xa,xb=(x-hw-nw,x+hw) if sd<0 else (x-hw,x+hw+nw)
    return (xa,yr+.8,xb,yr+.8+TRI_H+.6) if mode=="above" else (xa,yr-.8-TRI_H-.6,xb,yr-.8)
def draw_mark(d,mode,x,yr,Tk):
    cc,al,ed=Tk; ph=PTS_FS*CAP; mg=d.get("marg")
    if mg is not None: fill=UP if mg>=0.5 else DN if mg<=-0.5 else FLAT; edge=mix(fill,BG,.35)
    else: fill=mix(OPP_SQ,BG2,.25); edge=mix(OPP_SQ,BG,.35)
    if mode=="above":
        dtri(x,yr+.8,TRI_W,TRI_H,fill,edge); yp=yr+.8+TRI_H-ph; mb=yr+.8+TRI_H-1.6-MARG_FS*CAP
    else:
        utri(x,yr-.8,TRI_W,TRI_H,fill,edge); yp=yr-.8-TRI_H; mb=yr-.8-TRI_H+1.6
    if mg is not None:
        ms=("+" if mg>=0.5 else "-" if mg<=-0.5 else "")+(f"{abs(round(mg)):.0f}" if abs(mg)>=0.5 else "EVEN")
        fs=MARG_FS
        while c.stringWidth(ms,"Bebas",fs)>TRI_W*.78 and fs>4.6: fs-=.1
        txt(x,mb,ms,"Bebas",fs,BG,"c")
    nx=x+d["side"]*(TRI_W/2+1.6+d["pw"]/2); hw=d["pw"]/2+1.0
    scrim(_capsule(nx-hw,yp-.6,nx+hw,yp+ph+.6,2.0),al=.42,steps=10,feather=3.2)
    htxt(nx,yp,d["ps"],"Bebas",PTS_FS,d["pc"],"c",hw=1.2)
    d["placed"]=(mode,round(x,1),round(yr,1))

# ===================== v33: Dom's Sunday batch =====================
# Meter = three reads: WORKLOAD (left) . YAHOO (center, the headline) . EFFICIENCY (right).
# Needle weight = how much we trust the read: Yahoo boldest; workload toned and thinner; efficiency (new) thinnest, dotted.
# Outer ticks = how much of the matchup is already played (points on the board / projected total, both sides).
LITE=Color(0xE9/255,0xE4/255,0xD9/255); LOWINK=Color(0x1B/255,0x22/255,0x33/255); LOWPIP=Color(0xC9/255,0xC2/255,0xB4/255)
_YS=_json2.load(open("/home/claude/dksys/data/latest/yahoo/wk4/yl_sun.json"))
EFF=_YS["EFF"]; COMP=_YS["COMP"]
NEED={"y":dict(w=1.0,a=1.0,dash=None),"w":dict(w=.62,a=.70,dash=None),"e":dict(w=.40,a=.52,dash=(1.6,1.3))}
def _needle(cx,cy,r,v,kind,col):
    # v35: every needle stays readable when they overlap. Yahoo goes down first and runs the full length;
    # the two models print OVER it on a dark halo, each shorter, each ending in its own tip
    # (workload: solid dot; efficiency: open ring), so two needles on the same spot still read as two.
    n=NEED[kind]; vv=min(max(v,0),99.9); a=math.pi*(1-vv/100); ca,sa=math.cos(a),math.sin(a)
    L=r*{"y":1.02,"w":.86,"e":.70}[kind]; ink=mix(BG2,TXT,n["a"]) if kind=="y" else mix(BG2,TXT,{"w":.88,"e":.78}[kind])
    lw=max(.8,r*.07*n["w"])
    c.saveState(); c.setLineCap(1)
    if kind!="y":
        c.setStrokeColor(BG); c.setLineWidth(lw+1.6); c.line(cx,cy,cx+L*ca,cy+L*sa)          # halo
    c.setStrokeColor(ink); c.setLineWidth(lw)
    if n["dash"]: c.setDash(*n["dash"])
    c.line(cx,cy,cx+L*ca,cy+L*sa); c.setDash()
    tx,ty=cx+L*ca,cy+L*sa
    if kind=="w":
        c.setFillColor(BG); c.circle(tx,ty,2.5,fill=1,stroke=0); c.setFillColor(ink); c.circle(tx,ty,1.7,fill=1,stroke=0)
    elif kind=="e":
        c.setFillColor(BG); c.circle(tx,ty,2.6,fill=1,stroke=0); c.setStrokeColor(ink); c.setLineWidth(.8); c.circle(tx,ty,1.7,fill=0,stroke=1)
    c.restoreState()
def _fit(t,room):
    f=LS
    while c.stringWidth(t,"PopB",f)>room and f>3.6: f-=.05
    return f
def gauge3(cx,cy,r,vy,vw,ve,col,comp):
    gauge(cx,cy,r,vy,col)                                   # the dial as before: arc filled to Yahoo, Yahoo needle
    sw=r*20/78; ro=r+sw/2
    def pt(t,rr): a=math.pi*(1-t/100); return cx+rr*math.cos(a), cy+rr*math.sin(a)
    for t in range(0,101,5):                                # outer ticks re-lit: how much of the matchup is played
        lng=t%25==0; on=t<=comp and comp>0
        c.setStrokeColor(GOLDISH if on else mix(GR2,BG2,.35)); c.setLineWidth((.9 if lng else .7) if on else (.55 if lng else .35))
        c.line(*pt(t,ro+1.6),*pt(t,ro+(4.8 if lng else 3.2)))
    _needle(cx,cy,r,vy,"y",col); _needle(cx,cy,r,vw,"w",col); _needle(cx,cy,r,ve,"e",col)   # v35: Yahoo under, models over
    hr=max(2.2,r*.1); c.setFillColor(col); c.circle(cx,cy,hr+.9,fill=1,stroke=0); c.setFillColor(TXT); c.circle(cx,cy,hr,fill=1,stroke=0)
def _key(x,y,kind,ln=16):
    n=NEED[kind]; ink=mix(BG2,TXT,n["a"]) if kind=="y" else mix(BG2,TXT,{"w":.88,"e":.78}[kind])
    c.saveState(); c.setStrokeColor(ink); c.setLineWidth(max(.6,1.9*n["w"])); c.setLineCap(1)
    if n["dash"]: c.setDash(*n["dash"])
    c.line(x-ln/2,y,x+ln/2-(2 if kind!="y" else 0),y); c.setDash()
    if kind=="w": c.setFillColor(ink); c.circle(x+ln/2,y,1.5,fill=1,stroke=0)
    elif kind=="e": c.setLineWidth(.7); c.circle(x+ln/2,y,1.5,fill=0,stroke=1)
    c.restoreState()
_STW=[""]
KORC=(1.0,.478,.851)   # Oct 29 (Dom): Koerner's pink, the same as Live
def readout3(GX,gy,vy,vw,ve,CP,vk=None):
    # Oct 29 (Dom): Yahoo tight under the needle, then one row of three - Ratcliffe (FTN), Koerner (F Labs), Gotham
    htxt(GX,gy-17.0,f"{vy}%","Bebas",18,TXT,"c",hw=2.4); htxt(GX,gy-21.6,"YAHOO","PopB",4.2,TXT,"c",hw=1.3)
    for x,v,k,lab in ((GX-38,vw,"w","RATCLIFFE · FTN"),(GX,vk,"k","KOERNER · F LABS"),(GX+38,ve,"e","GOTHAM")):
        htxt(x,gy-31.0,("–" if v is None else f"{v}%"),"Bebas",9.5,mix(BG2,TXT,.85),"c",hw=1.6)
        if k=="k": c.saveState(); c.setStrokeColorRGB(*KORC); c.setLineWidth(1.6); c.setLineCap(1); c.line(x-6,gy-33.0,x+5,gy-33.0); c.restoreState()
        else: _key(x,gy-33.0,k,11)
        htxt(x,gy-36.8,lab,"PopB",3.6,mix(BG2,TXT,.78),"c",hw=1.1)
    htxt(GX,gy-41.6,(_STW[0]+"  ·  " if _STW[0] else "")+"PROJECTED WIN PROBABILITY","PopB",4.8,TXT,"c",hw=1.5)
PROSE={
 "DK I":"DIKFORE are done but for Juwan Johnson Monday and their kicker. Your Vikings defense has 21. McCaffrey and Kelce are playing; Shough, London and Kamara go Monday.",
 "DK II":"Chase finished at 5.7. Raider Fan has Smith-Njigba, Bowers and Jennings playing now, Bates tonight. You have Darnold, Sutton and Kelce on now; Kamara and London Monday.",
 "DK III":"Benchdad's has Walker, Hampton, Darnold, Wilson and McConkey playing now. You have Holani and Waddle on now; Shough and Vele go Monday.",
 "DK IV":"Stroud finished at 27.1 and Flowers at 25.8. Team Other has McCaffrey and Aaron Jones playing now. You still have Goff tonight and Bijan Robinson Monday.",
}
URG={"DK II":"watch"}
def block(D,top,h,VMAX,GX):
    col=LC[D["lab"]]; x0=M; x1=W-M; bot=top-h; T=tints(col); lab=DISP[D["lab"]]
    c.saveState(); _p=c.beginPath(); _p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(_p,stroke=0)   # v33: light at the bottom, deep at the top
    c.linearGradient(x0,bot,x0,top,(LITE,LITE,mix(LITE,BG2,.55),BG2,BG),(0,.13,.24,.42,1),extend=False); c.restoreState()
    lx=x0+12; TL=top-12
    gr=38; sw=gr*20/78; ro=gr+sw/2; gy=top-14-GLAB-ro
    pb=bot+34; CEIL=TL; mh=CEIL-pb; mx0=x0+4; mx1=x1-4; rx0=mx0
    xs=[mx0+(mx1-mx0)*(.12+.83*i/(NW-1)) for i in range(NW)]
    PS={}
    # ---- layer 3 (back): mountain fills, then every ridge line over every fill ----
    c.saveState(); p=c.beginPath(); p.roundRect(x0,bot,x1-x0,h,5); c.clipPath(p,stroke=0)
    for k,v in D["bands"]:
        P=[(x_,min(y_,CEIL)) for x_,y_ in ridge(D["lab"]+k,xs,[mh*min(1,y_/VMAX) for y_ in v],rx0,mx1,pb)]; ridges(P,pb,*T[k]); PS[k]=P
    for k,v in D["bands"]: rline(PS[k],T[k][2],0.8 if k!="you" else 1.0,halo=(k=="you"))   # v44: halo on your ridge only   # v37: context ridges bolder so each layer can be traced under yours
    c.restoreState()
    done=globals().get("TESTDONE") or DONE
    bx=(xs[done-1]+xs[done])/2 if 0<done<NW else (rx0+xs[0])/2 if done==0 else (xs[-1]+mx1)/2
    if done>=NW: bx=min(bx,x1-6-(MGAP+TRI_W*1.5+1.0+c.stringWidth("000.0","Bebas",PTS_FS)+3))   # v29: week over, keep his mark on the card
    c.setFillColor(col); c.rect(x0+2,top-3,x1-x0-4,3,fill=1,stroke=0)
    for i,x in enumerate(xs):
        c.setFillColor(TXT); c.circle(x,pb+mh*min(1,D["me"]["win"][i]/VMAX),1.4,fill=1,stroke=0)
        txt(x,pb-8,WLAB[i],"PopB",5.2,LOWINK,"c")
        lit=qlit(i)
        for q in range(4):
            qx=x-7.5+q*5; c.setFillColor(_dark(col,.15) if q<lit else LOWPIP); c.circle(qx,pb-13.6,1.7,fill=1,stroke=0)
    c.setStrokeColor(mix(GR2,BG2,.3)); c.setLineWidth(.4); c.line(rx0,pb,mx1,pb)
    # ---- identity ----
    y=TL-13.5*CAP   # v44b lift; v44 (Dom): DK label at the record size; color, not size, sets it apart
    w=htxt(lx,y,lab,"Bebas",16,col,hw=2.2) or c.stringWidth(lab,"Bebas",16); w+=6
    w+=htxt(lx+w,y,D["rec"],"Bebas",16,TXT,hw=2.2) or c.stringWidth(D["rec"],"Bebas",16); vs0=lx+w
    w+=c.stringWidth("  vs  ","PopM",7); htxt(vs0,y,"  vs  ","PopM",7,GR,hw=1.6); vs1=lx+w
    htxt(lx+w,y,f"{D['oppname'].upper()} {D['opprec']}","Bebas",16,TXT,hw=2.2)
    y2=y-13.5
    # v36 (Dom, Sun Oct 4): tighter, quieter left block. Yahoo stays big; workload and efficiency drop to the meter size,
    # equal to each other; the (+/-) shrinks and goes neutral grey; DIVISION moves into the band key; rows close up.
    TD=True; FY,FM,FP=11,11,8;   # v44: one size for all three rows
    PC=mix(GR,TXT,.30)
    # v39 (Dom): tighten left to right - the numbers no longer hang off the title's width; they sit one short gap
    # past the longest label, and the "vs" closes up
    MD=MOD[D["lab"]]; EF=EFF[D["lab"]]
    LW=max(c.stringWidth(t,"PopB",LS) for t in ("YAHOO","FTN","KOERNER","GOTHAM"))
    NWm=c.stringWidth("000.0","Bebas",FY)   # one column for all four leagues, so the blocks line up down the page
    NC=lx+LW+4+NWm; VW=c.stringWidth("vs","PopM",6.2); OC=NC+3+VW+3
    def _row(yy,name,me,op,fs,cm,co,hw):
        htxt(lx,yy,name,"PopB",LS,GR,hw=1.6)
        htxt(NC,yy,f"{me:.1f}","Bebas",fs,cm,"r",hw=hw); htxt(NC+3,yy,"vs","PopM",6.2,GR,hw=1.4)
        htxt(OC,yy,f"{op:.1f}","Bebas",fs,co,hw=hw); w_=OC+c.stringWidth(f"{op:.1f}","Bebas",fs)
        d_=round(round(me,1)-round(op,1),1); g_=int(math.floor(abs(d_)+.5+1e-9))*(1 if d_>=0 else -1)   # v38 (Dom): whole points, half rounds away from zero
        htxt(w_+4,yy,f"({'+' if g_>0 else '-' if g_<0 else ''}{abs(g_)})","Bebas",FP,PC,hw=1.4)
    _row(y2,"YAHOO",D['ym'],D['yo'],FY,col,OPPC,1.8)
    _sp=7.8 if D["lab"] in KOR else 10.0   # Oct 29 (Dom): with Koerner the four rows close up so nothing below moves much
    MD=MOD[D["lab"]]; y2m=y2-_sp; mc_=mix(GR,TXT,.45); oc_=mix(GR,TXT,.45)
    _row(y2m,"FTN",MD['me'],MD['op'],FM,mc_,oc_,1.8)
    EF=EFF[D["lab"]]; y2e=y2m-_sp
    if D["lab"] in KOR: _row(y2e,"KOERNER",KOR[D["lab"]]['me'],KOR[D["lab"]]['op'],FM,mc_,oc_,1.8); y2e-=_sp
    _row(y2e,"GOTHAM",EF['me'],EF['op'],FM,mc_,oc_,1.8)
    ks=[k for k,v in reversed(D["bands"]) if k!="you"]; kx=lx; ky=y2e-LS*1.2-0.2
    for k in ks:
        cc,al,ed=T[k]; c.setFillColor(cc); c.rect(kx,ky+.2,4.2,4.2,fill=1,stroke=0)
        _bl=BANDLAB[k]+("  ·  DIVISION RIVAL" if TD and k=="opp" and D["oppdiv"] else "")
        htxt(kx+7,ky,_bl,"PopM",4.7,mix(cc,TXT,.40),hw=1.4); kx+=7+c.stringWidth(_bl,"PopM",4.7)+9
    hy=ky-3.6; Y_=YL[D["lab"]]; nmax=max(len(Y_["me"]),len(Y_["op"])); pr_=nmax*5.0+(nmax-1)*2.0+3.5+c.stringWidth("100% PLAYED","PopB",CNT_FS)
    c.setStrokeColor(mix(GR2,BG2,.15)); c.setLineWidth(.4); c.line(lx,hy,lx+max(kx-9-lx,pr_),hy)
    ylow=pips22(lx,hy-7.0,D,col)   # v23: a little air between the rule and the squares
    IDBOX=(lx-3,ylow-3,lx+idwidth(D)+3,top)
    txt(x1-10,pb+3.2,"YAHOO PROJECTIONS","PopB",4.2,mix(GR2,BG2,.15),"r")
    # ---- balls ----
    br=19; lgx=x1-40; dvx=lgx-50; ry=TL-6.4*CAP-7-br
    scrim(_capsule(dvx-br-2,ry-br-12,lgx+br+2,TL+1,12),al=PLATE_A,steps=9,feather=5.0); BALLBOX=(dvx-br-2-5,ry-br-3-5,lgx+br+2+5,top)
    dn_,dp,dlab,dsub=D["dv"]
    ring19(dvx,ry,br,dn_,dp,None,col,dlab)
    ring19(lgx,ry,br,D["n"],D["rank"],None,col,"LEAGUE")
    for x,l in ((dvx,dlab),(lgx,"LEAGUE")): txt(x,TL-6.4*CAP,l,"PopB",6.4,TXT,"c")
    txt((dvx+lgx)/2,ry-br-9.2,STAND_LAB,"PopB",4.6,mix(GR,TXT,.45),"c")
    # ---- note line ----
    pr=PROSE[D["lab"]].format(w=D["whatif"][2] if "whatif" in D else "")
    yb=bot+7.5; urg=URG.get(D["lab"],"info"); mc={"act":DN,"watch":HOLD,"info":GR}[urg]
    sw_=4.2*1.12; fs=6.0; rx=x1-12; lim=rx-(lx+sw_+c.stringWidth(ASOF,'PopM',5.2)+16)
    while c.stringWidth(pr,"Pop",fs)>lim: fs-=.05
    txt(rx,yb,pr,"Pop",fs,LOWINK,"r"); tx0=rx-c.stringWidth(pr,"Pop",fs)
    sheet(tx0-sw_-3.5,yb,4.2,mc)
    txt(lx,yb,ASOF,"PopM",5.2,DN if MTR["alarms"] else LOWINK)   # v33: the stamp sits on the block                         # the mark travels with the first word
    # ---- layer 2: the now edge and the banked marks ----
    a=ACT.get(D["lab"]); pm=sum(v_ for v_ in a["me"][:done] if v_) if done else 0.0; po=sum(v_ for v_ in a["op"][:done] if v_) if done else 0.0
    S=[dict(side=-1,k="you",pts=pm,pc=col,marg=round(pm-po,1),fill=col),dict(side=1,k="opp",pts=po,pc=OPP_SQ,marg=None,fill=mix(OPP_SQ,BG2,.25))]   # v32: one margin only, on Dom's triangle (Dom, Sun Oct 4)   # v31: each triangle in its team color, each carries its own signed lead
    for d_ in S: d_.update(stack_dims(f"{d_['pts']:.1f}"))
    MBOX=(GX-METERBOX[0],gy-31.5-12.0,GX+METERBOX[0],top)   # v47: the marks keep off the meter (Oct 29: taller for the row of three)
    plan,off=place_marks(S,bx,PS,CEIL,pb,[IDBOX,BALLBOX,MBOX],x0+6,x1-6)
    tops=[_rect(m,x,yr,d_)[3] for d_,(m,x,yr) in zip(S,plan)]
    yt=min(CEIL,max(tops)+2)   # Oct 11 (Dom): the pole ends just above the flags, not at the tallest ridge
    dn=31.5   # v24: meter plates go down BEFORE the now-edge and banked marks, so the marks print over them
    scrim(_dome(GX,gy,ro+GLAB+1,dn),al=PLATE_A,steps=9,feather=4.5); scrim(_capsule(GX-56,gy-dn-12.0,GX+56,gy-dn,5),al=PLATE_A,steps=9,feather=3.0)   # v46 (Dom): shadow pulled in under the dial; Oct 29 taller
    nowedge(bx,pb,yt)
    for d_,(mode,x,yr) in zip(S,plan): draw_mark(d_,mode,x,yr,T[d_["k"]])
    D["marks"]=[(d_["k"],d_["ps"])+d_["placed"] for d_ in S]; D["edge"]=(round(bx,1),round(yt,1),round(off,1))
    # ---- layer 1 (front): the meter (plates already drawn behind the marks) ----
    _mst_=MTR["leagues"].get(D["lab"],{}).get("state"); FIN=(_mst_=="FINAL") if _mst_ else (done>=NW or DEC.get(D["lab"],False))   # Oct 13: the one status word   # Oct 11 (Dom): WON / LOST once decided
    if FIN:
        fm=sum(v_ for v_ in a["me"] if v_); fo=sum(v_ for v_ in a["op"] if v_)
        res,rc=(("WON",UP) if fm>fo else ("LOST",DN) if fm<fo else ("TIED",FLAT))
        gauge(GX,gy,gr,100 if fm>fo else 0.6 if fm<fo else 50,rc)
        htxt(GX,gy-23,res,"Bebas",23,rc,"c",hw=2.4)
        htxt(GX,gy-31,"FINAL","PopB",5.6,TXT,"c",hw=1.6)
        return dvx-br
    MW_,ME_=MOD[D["lab"]]["pct"],EFF[D["lab"]]["pct"]; CP=COMP[D["lab"]]
    METER_NOW[D["lab"]]=dict(yahoo=D["pct"],ratcliffe=MW_,gotham=ME_,koerner=KOR.get(D["lab"],{}).get("pct"),comp=CP)   # the field cards read these
    gauge3(GX,gy,gr,D["pct"],MW_,ME_,col,CP["all_pct"])
    _STW[0]=MTR["leagues"].get(D["lab"],{}).get("state") or ""; readout3(GX,gy,D["pct"],MW_,ME_,CP,KOR.get(D["lab"],{}).get("pct"))
    return dvx-br

METER_NOW={}; METERBOX=[54.0]
def build(fn):
    global c; c=canvas.Canvas(fn,pagesize=letter)
    for f_ in list(globals().values()):
        if callable(f_) and getattr(f_,"__globals__",None) is not None: f_.__globals__["c"]=c
    import _mast33                                       # v33b (Oct 8): the Dispatch masthead, like every other page
    _mast33.draw(c,"OVERVIEW  ·  FANTASY FOOTBALL",MASTSUB)
    DS=[prep(l) for l in LG]
    VMAX=max(max(v) for D in DS for k,v in D["bands"])*1.08
    # league strip v42 (Dom): one color for all four, boxed in the blocks' own fade, inset from the edges with room to breathe
    bx0=M; bx1=W-M; bh=0; btop=Ht-87-7; bbot=btop-bh   # v43: full chart width, matching the blocks
    c.saveState(); _p=c.beginPath(); _p.roundRect(bx0,bbot,bx1-bx0,bh,5); c.clipPath(_p,stroke=0)
    c.linearGradient(bx0,bbot,bx0,btop,(LITE,mix(LITE,BG2,.55),BG2,BG),(0,.10,.30,1),extend=False); c.restoreState()
    span=bx1-bx0-2*18; fs=11.5; U=lambda l: l+"  ·  "
    def lw(l,f): return c.stringWidth(U(l),"Bebas",f)+c.stringWidth(FULL[l].upper(),"Bebas",f)
    while sum(lw(l,fs) for l in LG)+3*22>span: fs-=.05
    g=(span-sum(lw(l,fs) for l in LG))/3; sx=bx0+18; y3=bbot+bh*.42
    for l in LG:
        pass
    y3=bbot+1   # blocks start 8pt under the box
    global LGFS; LGFS=fs
    idr=M+12+max(idwidth(D) for D in DS); balll=W-M-40-50-26
    # v40 (Dom): with the rows tightened, center the meter between the end of the rows and the standings balls,
    # but never let the top of the dial crowd the widest title line
    lx_=M+12; rowR=lx_+max(c.stringWidth(t,"PopB",7) for t in ("YAHOO","FTN","GOTHAM"))+4+c.stringWidth("000.0","Bebas",11)+6+c.stringWidth("vs","PopM",6.2)+c.stringWidth("000.0","Bebas",11)+4+c.stringWidth("(+00)","Bebas",8)
    ballL=W-M-40-50-19-2; _gr=38; _ro=_gr+_gr*20/78/2; R_=_ro+GLAB+1; dy_=GLAB+_ro+14-29
    clear=lx_+max(idwidth(D) for D in DS)+math.sqrt(max(R_**2-dy_**2,0))+8
    GX=max((rowR+ballL)/2,clear)
    # v47 (Dom): the meter moves out of the now-edge's way, all four together, inside a fenced lane --
    # left wall = the nameplate stack (clear), right wall = the standings globes. Overlap is accepted only when the lane runs out.
    _HW=max(R_,54.0); _lo=clear; _hi=(W-M-40-50-19-2-5)-_HW-6
    _mx0=M+4; _mx1=W-M-4; _xs=[_mx0+(_mx1-_mx0)*(.12+.83*i/(NW-1)) for i in range(NW)]; _d=globals().get("TESTDONE") or DONE
    _bx=(_xs[_d-1]+_xs[_d])/2 if 0<_d<NW else (_mx0+_xs[0])/2 if _d==0 else (_xs[-1]+_mx1)/2
    _PR,_PL=26.0,26.0+FADE                     # room for his mark right of the edge; yours plus the edge's shadow on the left
    def _clr(g): return max(g-_HW-_bx-_PR if g>=_bx else _bx-_PL-(g+_HW),-999)
    if _clr(GX)<0:
        _cand=[min(max(_bx+_PR+_HW,_lo),_hi),min(max(_bx-_PL-_HW,_lo),_hi)]
        GX=max(_cand,key=lambda g:(min(_clr(g),0),-abs(g-GX)))
    GX=min(max(GX,_lo),_hi); METERBOX[0]=_HW
    print("GX",round(GX,1),"clear",round(clear,1),"mid",round((rowR+ballL)/2,1),"edge",round(_bx,1),"lane",round(_lo,1),round(_hi,1),"gap",round(_clr(GX),1))
    top=y3-9; gap=8; h=142.0; bottom=top-4*h-3*gap   # v44 (Dom): blocks shorter, the stack ends higher
    global LS; LS=7.0
    def _room(D):
        w=c.stringWidth(DISP[D["lab"]],"Bebas",16)+6+c.stringWidth(D["rec"],"Bebas",16)+c.stringWidth("  vs  ","PopM",7)
        return w-c.stringWidth(f"{D['ym']:.1f}","Bebas",11)-3.2
    while any(c.stringWidth("YAHOO","PopB",LS)>_room(D) for D in DS): LS-=.05
    for D in DS: block(D,top,h,VMAX,GX); top-=h+gap
    foot=("YAHOO: Yahoo's projection for each lineup as set, from one sweep of every matchup page Sun 2:20-2:29 p.m. PT: final games at actual, games in progress at Yahoo's live projected final, the rest as projected. "
          "WORKLOAD: our engine, from usage (carries, targets, red-zone touches, role). EFFICIENCY, new and unproven: his points a game x what this defense allows his position x his team's Vegas total. K and DEF at Yahoo in both. "
          "METER: center = Yahoo's own win chance (matchup page, same sweep); fainter needle = less proven; gold ticks = share of the matchup already played; % PLAYED by the squares = share of each side's projected points banked. TRIANGLES: points banked in finished windows, yours left, his right; inside yours, your lead (+) or deficit (-). "
          "MOUNTAIN: Yahoo by kickoff window, Pacific; division and league layers from the same sweep. BALLS: your place and the cut. SQUARES: starters, filled once played.")
    foot=FOOT; FFS=4.7; FLD=6.2; FL=simpleSplit(foot,"Pop",FFS,W-2*M)
    while len(FL)>4 and FFS>4.2: FFS-=.1; FL=simpleSplit(foot,"Pop",FFS,W-2*M)   # Oct 12: never crash on a long footnote
    if len(FL)>4: FL=FL[:3]+[FL[3].rstrip(' .,;')+' \u2026']
    for j,l in enumerate(FL):
        ws=l.split(" "); y_=bottom-12-j*FLD   # v44: footnote follows the stack up
        if j==len(FL)-1 or len(ws)<2: txt(M,y_,l,"Pop",FFS,GREYC); continue
        g=(W-2*M-sum(c.stringWidth(w,"Pop",FFS) for w in ws))/(len(ws)-1); x_=M
        for w in ws: txt(x_,y_,w,"Pop",FFS,GREYC); x_+=c.stringWidth(w,"Pop",FFS)+g
    print("FOOTLINES",len(FL),"LS",round(LS,2),"h",round(h,1))
    import json as _jm; _jm.dump(dict(week=MW,built=MTR["built_pt"],needles=METER_NOW),open(f"/home/claude/dksys/data/state/meter_now_wk{MW}.json","w"),indent=1)
    c.save(); return DS,GX,idr





# ===================== v31: Dom's voice batch (Sun Oct 4, ~midnight) =====================
# 1. Each triangle keeps its TEAM color - the color says whose number it is. No green / red.
# 2. The signed lead sits inside each triangle (+24 in mine, -24 in his); the inside ink picks whichever of navy / white reads best.
# 3. The banked total sits ON TOP of the triangle by default. Only where that crashes into something does it fall back
#    to beside the triangle, mine to the left, his to the right (the v30 layout). Both triangles the same size, as low as they go.
TGAP=1.2
def _lum(cl):
    f=lambda v:(v/12.92 if v<=.03928 else ((v+.055)/1.055)**2.4)
    return .2126*f(cl.red)+.7152*f(cl.green)+.0722*f(cl.blue)
def _ink(fill):
    L=_lum(fill); cw=1.05/(L+.05); cb=(L+.05)/(_lum(BG)+.05)
    return white if cw>=cb else BG
def _rect(mode,x,yr,d):
    pl,tm=mode
    hw=TRI_W/2+.8; ph=PTS_FS*CAP
    if tm=="top":
        w=max(hw,d["pw"]/2+1.4)
        return (x-w,yr+.8,x+w,yr+.8+TRI_H+TGAP+ph+.8) if pl=="above" else (x-w,yr-.8-TRI_H-TGAP-ph-.8,x+w,yr-.8)
    sd=d["side"]; nw=d["pw"]+2.6
    xa,xb=(x-hw-nw,x+hw) if sd<0 else (x-hw,x+hw+nw)
    return (xa,yr+.8,xb,yr+.8+TRI_H+.6) if pl=="above" else (xa,yr-.8-TRI_H-.6,xb,yr-.8)
MODES=(("above","top"),("above","side"),("below","top"),("below","side"))
def place_marks(S,bx,PS,ceil,pb,OBS,xmin,xmax):
    off=MGAP+TRI_W/2+3.5; plan=[]
    for d in S:
        x=bx+d["side"]*off; yr=ridge_at(PS[d["k"]],x); got=None
        for strict in (True,False):
            for mode in MODES:
                r=_rect(mode,x,yr,d)
                if r[0]<xmin or r[2]>xmax or r[3]>ceil or (mode[0]=="below" and r[1]<pb+1.5): continue
                if strict and any(_hit(r,(o[0],o[1]+3.2,o[2],o[3])) for o in OBS): continue
                got=(mode,x,yr); break
            if got: break
        plan.append(got or (("above","top"),x,yr))
    return plan,off
def draw_mark(d,mode,x,yr,Tk):
    pl,tm=mode; ph=PTS_FS*CAP; mg=d.get("marg"); fill=d["fill"]; edge=mix(fill,BG,.35)
    if pl=="above":
        dtri(x,yr+.8,TRI_W,TRI_H,fill,edge); top_=yr+.8+TRI_H; mb=top_-1.6-MARG_FS*CAP
        yp=top_+TGAP if tm=="top" else top_-ph
    else:
        utri(x,yr-.8,TRI_W,TRI_H,fill,edge); bot_=yr-.8-TRI_H; mb=bot_+1.6
        yp=bot_-TGAP-ph if tm=="top" else bot_
    if mg is not None:
        ms=("+" if mg>=0.5 else "-" if mg<=-0.5 else "")+(f"{abs(round(mg)):.0f}" if abs(mg)>=0.5 else "EVEN")
        fs=MARG_FS
        while c.stringWidth(ms,"Bebas",fs)>TRI_W*.78 and fs>4.6: fs-=.1
        txt(x,mb,ms,"Bebas",fs,_ink(fill),"c")
    nx=x if tm=="top" else x+d["side"]*(TRI_W/2+1.6+d["pw"]/2); hw=d["pw"]/2+1.0
    scrim(_capsule(nx-hw,yp-.6,nx+hw,yp+ph+.6,2.0),al=.42,steps=10,feather=3.2)
    htxt(nx,yp,d["ps"],"Bebas",PTS_FS,d["pc"],"c",hw=1.2)
    d["placed"]=(pl+"/"+tm,round(x,1),round(yr,1))



# ===================== v33 DATA LAYER (Thu Oct 8 2026, Dom: "permanent and automatic, never hand-patched weekly") =====================
# Everything on this page now comes from ONE file built by /home/claude/dksys/meter/meter_data.py:
#   /home/claude/dksys/data/latest/meter/meter_wk<W>.json   (the newest week on disk, or DK_WEEK=<n>)
# Meter: LEFT = RATCLIFFE (Oct 28; Gotham before), CENTER = YAHOO (Yahoo's own posted win %), RIGHT = GOTHAM (Sleeper retired Oct 28). Efficiency and workload retired.
# Week, kickoff windows, records, standings, opponents, notes, stamps and the footnote are all read or generated from that file.
import json as _jm2, glob as _gm2, os as _om2, datetime as _dtm2
_MFS=sorted(_gm2.glob("/home/claude/dksys/data/latest/meter/meter_wk*.json"),key=lambda p:int(p.split("_wk")[1].split(".")[0]))
_MFP=(f"/home/claude/dksys/data/latest/meter/meter_wk{_om2.environ['DK_WEEK']}.json" if _om2.environ.get("DK_WEEK") else _MFS[-1])
MTR=_jm2.load(open(_MFP)); MW=MTR["week"]
YMISS={}                                                    # Oct 9: Yahoo's posted win % missing for a league -> the dial uses the win %
for _lb,_L in MTR["leagues"].items():                       # implied by Yahoo's own projected totals, and the card says so
    _n=_L["needles"]
    if _n.get("yahoo") is None and _n.get("yahoo_from_spread") is not None: _n["yahoo"]=_n["yahoo_from_spread"]; YMISS[_lb]=True
_LBL={"DK I":"269381","DK II":"1519795","DK III":"1507991","DK IV":"864215"}
# ---- kickoff windows and the clock (qlit lights the quarter pips from these) ----
G=pd.read_csv("/home/claude/dksys/data/latest/games.csv",low_memory=False); G=G[(G.season==2026)&(G.game_type=="REG")&(G.week==MW)]
_DO={"Thursday":0,"Friday":1,"Saturday":2,"Sunday":3,"Monday":4}
def _mn(t): return int(t[:2])*60+int(t[3:5])
_sl=sorted({(r.weekday,r.gametime) for r in G.itertuples()},key=lambda k:(_DO[k[0]],_mn(k[1]))); _WS=[]
for d_,t_ in _sl:
    if _WS and _WS[-1][0]==d_ and _mn(t_)-_mn(_WS[-1][1][-1])<=45: _WS[-1][1].append(t_)
    else: _WS.append((d_,[t_]))
_SLOT={(d_,t_):i for i,(d_,ts) in enumerate(_WS) for t_ in ts}
WLAB=list(MTR["windows"]); NW=len(WLAB); WIN=WLAB
NOWUTC=_dtm2.datetime.utcnow()
def _final(i): return all(r.result==r.result for r in G.itertuples() if _SLOT[(r.weekday,r.gametime)]==i)   # result filled = game final
DONE=0
while DONE<NW and _final(DONE): DONE+=1
# ---- per-league data in the shapes the drawing code already reads ----
YL,YAH,MOD,EFF,COMP,ACT,DEC,KOR={},{},{},{},{},{},{},{}
for lab,L in MTR["leagues"].items():
    sm,so=L["starters"]["me"],L["starters"]["op"]
    row=lambda p:(p["player"],p["team"],p["slot"],p["yahoo"] or 0.0,p["actual"])
    YL[lab]=dict(me=[row(p) for p in sm],op=[row(p) for p in so],live=tuple(L["totals"]["yahoo"]),ypct=L["needles"]["yahoo"])
    YAH[lab]=YL[lab]["live"]
    _rk="ratcliffe" if L["needles"].get("ratcliffe") is not None and L["totals"].get("ratcliffe") else "gotham"   # Oct 28 (Dom): Ratcliffe leads; Sleeper off the meters
    MOD[lab]=dict(me=L["totals"][_rk][0],op=L["totals"][_rk][1],pct=L["needles"][_rk])
    EFF[lab]=dict(me=L["totals"]["gotham"][0],op=L["totals"]["gotham"][1],pct=L["needles"]["gotham"])
    if L["needles"].get("koerner") is not None and L["totals"].get("koerner"): KOR[lab]=dict(me=L["totals"]["koerner"][0],op=L["totals"]["koerner"][1],pct=L["needles"]["koerner"])   # Oct 29 (Dom): Koerner
    def _bank(S):
        w=[0.0]*NW
        for p in S:
            if p["actual"] is not None and p["window"] is not None: w[p["window"]]+=p["actual"]
        return w
    ACT[lab]=dict(me=_bank(sm),op=_bank(so))
    DEC[lab]=all(p["window"] is None or p["window"]<DONE for p in sm+so)   # Oct 11 (Dom): nobody left to play on either side
    bm,bo=sum(ACT[lab]["me"]),sum(ACT[lab]["op"]); pm,po=L["totals"]["yahoo"]
    COMP[lab]=dict(me_board=bm,op_board=bo,me_pct=round(100*bm/pm) if pm else 0,op_pct=round(100*bo/po) if po else 0,
                   all_pct=round(100*(bm+bo)/(pm+po)) if pm+po else 0)
# ---- the all-teams sweep: league / division / top-six layers ----
_WF=sorted(_gm2.glob(f"/home/claude/dksys/data/latest/yahoo/wk{MW}/league_windows_*.txt"),key=_om2.path.getmtime)[-1]
_AW={}
for _l in open(_WF):
    if _l.startswith("#") or not _l.strip(): continue
    _p=_l.rstrip("\n").split("~"); _AW.setdefault(_p[0],{})[_p[1]]=[float(x) for x in _p[4].split()]
_SF=sorted(_gm2.glob(f"/home/claude/dksys/data/latest/yahoo/wk{MW}/standings_*.txt"),key=_om2.path.getmtime)[-1]
_STD={}
for _l in open(_SF):
    if _l.startswith("#") or "#" not in _l: continue
    lg_,rest=_l.rstrip("\n").split("#",1); dv_=None; out=[]
    for it in rest.split("|"):
        f_=it.split("^")
        if len(f_)==1: dv_=f_[0]; continue
        out.append(dict(rank=int(f_[0]),team=f_[1],div=dv_))
    _STD[lg_]=out
def _avg(lists): return [sum(x)/len(lists) for x in zip(*lists)] if lists else [0.0]*NW
def ordn(n): return f"{n}{'th' if 10<=n%100<=20 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')}"
def prep(lab):
    L=MTR["leagues"][lab]; lg=_LBL[lab]; tb=_STD[lg]; aw=_AW[lg]
    mine=[t for t in tb if t["team"]==L["me"]][0]; opp=[t for t in tb if t["team"]==L["opp"]]
    def _win(S): 
        w=[0.0]*NW; c_=[0]*NW
        for p in S:
            if p["window"] is None: continue
            w[p["window"]]+=(p["actual"] if p["actual"] is not None else (p["yahoo"] or 0)); c_[p["window"]]+=1
        return w,c_
    wm,cm=_win(L["starters"]["me"]); wo,co=_win(L["starters"]["op"])
    bands=[("league",_avg(list(aw.values())))]
    if mine["div"]:
        dvt=[t["team"] for t in tb if t["div"]==mine["div"]]; bands.append(("division",_avg([aw[t] for t in dvt if t in aw])))
        dvn=len(dvt); dvr=[t["team"] for t in tb if t["div"]==mine["div"]].index(L["me"])+1
        dv=(dvn,dvr,"DIVISION",f"{ordn(dvr)} OF {dvn}")
    else:
        bands.append(("top six",_avg([aw[t["team"]] for t in tb if t["rank"]<=6 and t["team"] in aw])))
        dv=(len(tb),L["pf_rank"],"POINTS FOR",f"{ordn(L['pf_rank'])} OF {len(tb)}")
    bands+= [("opp",wo),("you",wm)]
    oppdiv=bool(mine["div"] and opp and opp[0]["div"]==mine["div"])
    ym,yo=L["totals"]["yahoo"]
    return dict(lab=lab,me=dict(name=L["me"],lineup=[],tot=ym,win=wm,cnt=cm),op=dict(name=L["opp"],lineup=[],tot=yo,win=wo,cnt=co),
                ym=ym,yo=yo,pct=L["needles"]["yahoo"],rec=L["record"],rank=L["rank"],n=L["teams"],cut=6,dv=dv,bands=bands,
                oppdiv=oppdiv,oppname=L["opp"],opprec=L["opp_record"],ypct=None,n3=dv[0],prev=None,mypct=L["needles"]["gotham"])
# ---- the note on each card: written from the data, never typed ----
def _short(n): return n.split()[-1] if n else n
PROSE,URG={},{}
for lab,L in MTR["leagues"].items():
    n=L["needles"]; g_,y_,s_=(n.get("ratcliffe") if n.get("ratcliffe") is not None else n["gotham"]),n["yahoo"],n["gotham"]
    bye=[p["player"] for p in L["starters"]["me"] if p["window"] is None]
    gaps=[x for x in MTR.get("notes",[]) if x.startswith(lab+":") and "Gotham" in x]
    thu=[_short(p["player"]) for p in L["starters"]["me"] if p["window"]==0 and p["actual"] is None and WLAB and WLAB[0].startswith("THU")]
    if lab in YMISS:
        PROSE[lab]="Yahoo's posted win % was missing this run, so the Yahoo dial is worked from Yahoo's own projected totals."; URG[lab]="watch"
    elif bye:
        PROSE[lab]=f"Starter {bye[0]} has no game this week."; URG[lab]="act"
    elif max(g_,y_,s_)-min(g_,y_,s_)>=10:
        import re as _re2
        m_=_re2.search(r"Gotham ([\d.]+) vs Yahoo ([\d.]+) / Sleeper ([\d.]+) on (.+?) -",gaps[0]) if gaps else None
        PROSE[lab]=f"The three meters split by {max(g_,y_,s_)-min(g_,y_,s_)} points: FTN {g_}, Yahoo {y_}, Gotham {s_}."; URG[lab]="watch"
    else:
        PROSE[lab]="All three meters agree."+(f" Thursday: {', '.join(thu)}." if thu else ""); URG[lab]="info"
    for k_ in list(PROSE): PROSE[k_]=PROSE[k_].replace("{","(").replace("}",")")
def _ln11(n):
    w=[x for x in str(n).split() if x.rstrip(".") not in ("Jr","Sr","II","III","IV","V")]
    return w[-1] if w else str(n)
def _v11(p): return p["actual"] if p.get("actual") is not None else (p.get("yahoo") or 0.0)
for lab,L in MTR["leagues"].items():
    if lab in YMISS: continue
    me=L["starters"]["me"]; op=L["starters"]["op"]
    bad=[_ln11(p["player"]) for p in me if p["window"] is None or (p.get("status") in ("O","IR","IR-R","PUP-R","NA") and p.get("actual") is None)]
    q=[_ln11(p["player"])+" ("+p["status"]+")" for p in me if p.get("status") in ("Q","D") and p.get("actual") is None]   # Oct 12: a played man needs no kickoff check
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
MASTSUB=None   # set after the stamps below
_src=MTR["sources"]
def _hm(k):
    p=_src.get(k,{}).get("pulled_pt") or "?"; return " ".join(p.split()[-3:-1]) if p!="?" else "?"
exec(open("/home/claude/cand/redesign/_dstamp.py").read()); _DSL=ds_line   # Oct 10: honest dates on the read stamps
_al=MTR["alarms"]+MTR.get("lineup",[])   # Oct 21: lineup problems still print here; only data alarms set the data verdict
ASOF=(f"ALARM ({len(_al)}): {_al[0][:70]}" if _al else
      "All data as of "+_DSL([("Yahoo",_src.get("yahoo_matchups",{}).get("pulled_pt")),("Gotham",_src.get("gotham",{}).get("pulled_pt")),("Sleeper",_src.get("sleeper_skill",{}).get("pulled_pt"))]))
FOOT=(f"WEEK {MW}, built {MTR['built_pt']}. YAHOO: each lineup as set on Yahoo's matchup pages (pulled {_src['yahoo_matchups'].get('pulled_pt')}); final games at actual, the rest as projected. "
      f"GOTHAM: our engine (usage x rate x status, 2025 prior; run {_src['gotham'].get('pulled_pt')}). SLEEPER: Sleeper's public projections priced in each league's scoring, from the GitHub job ({_src['sleeper_skill'].get('pulled_pt')}). "
      f"Kickers and defenses: Sleeper's number in both Gotham and Sleeper (no source beats a flat average there). METER: center = Yahoo's own posted win chance; left Gotham, right Sleeper, same spread math; gold ticks = share played. "
      f"MOUNTAIN: Yahoo by kickoff window, Pacific; league and division layers from every team's matchup page ({_src['yahoo_all_teams'].get('pulled_pt')}). "
      +(f"ALARMS: {'; '.join(_al)}." if _al else "Every source checked: none missing, stale or short."))
MASTSUB=f"Week {MW}"
print("V33 DATA",_MFP,"week",MW,"done windows",DONE,"alarms",len(_al))
import os as _os
TIDY=_os.environ.get("TIDY")=="1"
if __name__=="__main__":
    import sys
    if len(sys.argv)>1 and sys.argv[1].endswith(".pdf"):
        DS,GX,idr=build(sys.argv[1]); raise SystemExit
    if len(sys.argv)>1:                                    # band test: same data, band moved to window N
        TESTDONE=int(sys.argv[1]); DS,GX,idr=build(f"/home/claude/cand/global/out/_test_{TESTDONE}.pdf")
    else:
        DS,GX,idr=build(f"/home/claude/cand/global/out/DK_Mountains_wk{MW}.pdf")
    for D in DS: print(D["lab"],D["ym"],D["yo"],"model",D["pct"],"prev",D["prev"],"yahoo",D["ypct"],D.get("whatif"))
    for D in DS: print(" ",D["lab"],D["marks"])
    print([D["edge"] for D in DS]); print("GX",round(GX),"idr",round(idr))

# OCT10 front page

# OCT10b front feet

# OCT10c front title

# OCT11 short names front

# OCT11 pole and decided

# OCT11 alarm played front

# OCT11 played squares glow

# OCT12 front q played

# OCT12 front no nicknames

# OCT12 front footnote fits

# OCT13 front state word
