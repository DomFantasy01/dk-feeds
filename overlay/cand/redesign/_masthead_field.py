# PUZZLE MASTHEAD v8 (Oct 3, Dom): FOUR pieces, one picture - a football field cut into a jigsaw.
# Global, Calls, Field, Positions. Large, bled off the right edge, cropped at the title's cap line on top
# and the section line on the bottom. A Global page lights all four; a section page lights its own piece.
# Freshness stamps: "LAST UPDATED", stacked bottom-up, right-aligned against the puzzle.
PZ_NAME4=("OVERVIEW","CALLS","FIELD","POSITIONS")
PZ_ALL=-1   # v16 (Oct 3 late): was 0 - the same as the Overview piece, so every piece lit on the Overview page   # Oct 3 (Dom): "Global" retired
from reportlab.lib.colors import white, black
PZ_CELL4={0:(0,1),1:(1,1),2:(0,0),3:(1,0)}            # reading order: Global, Calls / Field, Positions
PZ_OFF={0:(-1.2,1.0),1:(1.4,1.2),2:(-1.0,-1.1),3:(1.3,-0.9)}   # a hair apart - a puzzle being put together
TURF=(H("#2C6447"),H("#27593F"))   # v15: turf toned down (Dom: "looks like a circus")
def _field(c,x0,x1,yb,yt,yd,x50,band=None,skip=(),ns=13,dim=1.0):
    """the picture: mown stripes every 5 yd, yard lines, hash marks, painted numbers, a ball."""
    c.setFillColor(TURF[0]);c.rect(x0,yb,x1-x0,yt-yb,stroke=0,fill=1)
    for k in range(-12,13):                              # 5-yard stripes either side of midfield
        xa=x50+k*5*yd
        if k%2==0: c.setFillColor(TURF[1]);c.rect(xa,yb,5*yd,yt-yb,stroke=0,fill=1)
    c.setStrokeColor(white)
    for k in range(-12,13):
        xa=x50+k*5*yd;c.setStrokeAlpha((.88 if k%2==0 else .55)*dim);c.setLineWidth(1.1 if k%2==0 else .6)
        c.line(xa,yb,xa,yt)
    c.setStrokeAlpha(.75*dim);c.setLineWidth(.55);ym=(yb+yt)/2
    for k in range(-60,61):                              # hash marks every yard, two rows
        xa=x50+k*yd
        for hy in (ym-19,ym+19): c.line(xa,hy-ns*.08,xa,hy+ns*.08)
    c.setStrokeAlpha(1)
    c.setFillColor(white);c.setFillAlpha(.92*dim)
    for k in (-3,-2,-1,0,1,2,3):                          # painted numbers, bottom upright, top upside down
        n=50-abs(k)*10;xa=x50+k*10*yd;s=f"{n}"
        if n<=0: continue
        for top in (False,True):
            c.saveState()
            yy=band[1]-ns*1.04 if top else band[0]+ns*.25
            if any(a<xa+12 and xa-12<b and lo<yy+10 and yy<hi for a,b,lo,hi in skip): c.restoreState();continue
            c.translate(xa,yy+ns*.42);c.rotate(180 if top else 0);c.translate(-xa,-(yy+ns*.42))
            c.setFont("Bebas",ns);w=c.stringWidth(s[0],"Bebas",ns);g=ns*.12
            c.drawRightString(xa-g,yy,s[0]);c.drawString(xa+g,yy,s[1])
            if n<50:                                     # the arrow points to the near goal
                d=-1 if k<0 else 1;ax=xa+d*(w+ns*.42);q=ns/13
                p=c.beginPath();p.moveTo(ax+d*2.6*q,yy+4.6*q);p.lineTo(ax,yy+6.4*q);p.lineTo(ax,yy+2.8*q);p.close();c.drawPath(p,stroke=0,fill=1)
            c.restoreState()
    c.setFillAlpha(1)
    bx,by=x50-4.3*yd,ym-14                               # the ball, spotted just past midfield
    c.saveState();c.translate(bx,by);c.rotate(18);c.scale(ns/13,ns/13)
    c.setFillColor(H("#7A3E1D"));c.ellipse(-5.6,-3.2,5.6,3.2,stroke=0,fill=1)
    c.setFillColor(H("#A8582B"));c.ellipse(-4.2,-.6,3.8,2.5,stroke=0,fill=1)
    c.setStrokeColor(white);c.setLineWidth(.5);c.line(-2.2,0,2.2,0)
    for t in (-1.5,-.5,.5,1.5): c.line(t,-.8,t,.8)
    c.restoreState()
PZ_TITLE="DARK KNIGHT FANTASY FOOTBALL"                  # one word changes it everywhere
def _seg(p,a,b,sign,key,S,first=False):
    """one jigsaw edge a->b (sign 0 = straight). Canonical low->high so shared edges match from both sides."""
    if sign==0:
        if first: p.moveTo(*a)
        p.lineTo(*b);return
    rev=(a[0]>b[0]) if abs(a[1]-b[1])<.01 else (a[1]>b[1])
    pts=_edge_segs(*(b if rev else a),*(a if rev else b),sign,key,S)
    _trace(p,pts,rev,first)
def _outline(edges,S):
    p=None
    for n,(a,b,sg,key) in enumerate(edges):
        if n==0:
            from reportlab.pdfgen.pathobject import PDFPathObject
            p=PDFPathObject()
        _seg(p,a,b,sg,key,S,first=(n==0))
    p.close();return p
# v12 (Dom: the pieces that belong together don't look together - relook the whole design).
# A true assembled 2x2: every piece the same size, every shared edge one cut traced from both sides,
# classic round-headed tabs, no nudges, no tilt. The silhouette breaks only where a real edge piece would:
# tabs out on the sides and bottom, notches on the top.
def _tab(a,b,sign,u=26.0,pos=.5,n=10):
    """one cut a->b as points; sign +1 bulges to the left of travel, -1 right, 0 straight. Canonical = low->high."""
    ax,ay=a;bx,by=b;L=((bx-ax)**2+(by-ay)**2)**.5;dx,dy=(bx-ax)/L,(by-ay)/L;nx,ny=-dy,dx
    if sign==0: return [a,b]
    m=pos*L
    def P(t,h): s=m+(t-.5)*u;return (ax+dx*s+nx*h*u*sign, ay+dy*s+ny*h*u*sign)
    C=[((0.0,0),(0.30,0),(0.40,0.00),(0.39,0.10)),          # into the neck
       ((0.39,0.10),(0.37,0.20),(0.33,0.30),(0.50,0.30)),   # left of the head
       ((0.50,0.30),(0.67,0.30),(0.63,0.20),(0.61,0.10)),   # right of the head
       ((0.61,0.10),(0.60,0.00),(0.70,0),(1.0,0))]          # out of the neck
    pts=[(ax,ay)]
    for q in C:
        for k in range(1,n+1):
            t=k/n;w=[(1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3]
            pts.append(P(sum(w[z]*q[z][0] for z in range(4)),sum(w[z]*q[z][1] for z in range(4))))
    pts.append((bx,by));return pts
def _cut(a,b,sign,pos=.5):
    """trace a->b; computed low->high so both neighbours get the identical line."""
    rev=(a[0]>b[0]+.01) if abs(a[1]-b[1])<.01 else (a[1]>b[1])
    pts=_tab(b,a,-sign if False else sign,pos=(1-pos) if False else pos) if False else None
    lo,hi=(b,a) if rev else (a,b)
    pts=_tab(lo,hi,sign,pos=pos)
    return pts[::-1] if rev else pts
def _poly(edges):
    from reportlab.pdfgen.pathobject import PDFPathObject
    p=PDFPathObject();first=True
    for a,b,sg,pos in edges:
        for k,(x,y) in enumerate(_cut(a,b,sg,pos)):
            if first: p.moveTo(x,y);first=False
            elif k: p.lineTo(x,y)
    p.close();return p
def puzzle(c,lit,litcol):
    PW=54;X1=W-M-9;xj=X1-PW;xl=xj-PW;yt,yb=Ht-14,Ht-76;yj=(yt+yb)/2   # v14: bottom tabs sit right on the gold line
    # sign convention on a low->high cut: horizontal +1 = up, vertical +1 = left
    hL=((xl,yj),(xj,yj),+1,.5)      # Field's tab up into Global
    hR=((xj,yj),(X1,yj),-1,.5)      # Calls' tab down into Positions
    vT=((xj,yj),(xj,yt),-1,.36)     # Global's tab right into Calls (low, clear of the name)
    vB=((xj,yb),(xj,yj),+1,.62)     # Positions' tab left into Field
    E={0:[hL,vT,((xj,yt),(xl,yt),-1,.72),((xl,yt),(xl,yj),+1,.5)],        # Global: notch top, tab left
       1:[hR,((X1,yj),(X1,yt),-1,.5),((X1,yt),(xj,yt),-1,.40),vT[::1]],    # Calls: tab right, notch top
       2:[((xl,yb),(xj,yb),-1,.62),vB,hL,((xl,yj),(xl,yb),+1,.5)],          # Field: tab down, notch left
       3:[((xj,yb),(X1,yb),-1,.38),((X1,yb),(X1,yj),+1,.5),hR,vB]}         # Positions: tab down, notch right
    # orient each edge in travel order (CCW) - _cut handles direction, edges just need the right endpoints
    E[0]=[(hL[0],hL[1],hL[2],hL[3]),(vT[0],vT[1],vT[2],vT[3]),((xj,yt),(xl,yt),-1,.72),((xl,yt),(xl,yj),+1,.5)]
    E[1]=[(hR[0],hR[1],hR[2],hR[3]),((X1,yj),(X1,yt),-1,.5),((X1,yt),(xj,yt),-1,.40),(vT[1],vT[0],vT[2],vT[3])]
    E[2]=[((xl,yb),(xj,yb),-1,.62),(vB[0],vB[1],vB[2],vB[3]),(hL[1],hL[0],hL[2],hL[3]),((xl,yj),(xl,yb),+1,.5)]
    E[3]=[((xj,yb),(X1,yb),-1,.38),((X1,yb),(X1,yj),+1,.5),(hR[1],hR[0],hR[2],hR[3]),(vB[1],vB[0],vB[2],vB[3])]
    on=lambda i: lit==PZ_ALL or lit==i
    paths={i:_poly(E[i]) for i in E}
    BOX={0:(xl,yj,xj,yt),1:(xj,yj,X1,yt),2:(xl,yb,xj,yj),3:(xj,yb,X1,yj)}
    x50=xj-11;yd=1.6;NS=6.6;DIM=.42               # v14: field pushed further back and the white paint knocked down
    G=1.5                                          # v14: open seams - each piece eased out from the center
    OFF={0:(-G,G),1:(G,G),2:(-G,-G),3:(G,-G)}
    for i,p in paths.items():                        # one shadow under the assembled picture
        c.saveState();c.translate(1.2+OFF[i][0],-1.8+OFF[i][1]);c.setFillColor(black);c.setFillAlpha(.55);c.drawPath(p,stroke=0,fill=1);c.restoreState()
    for i,p in paths.items():                        # one continuous field, cut four ways
        c.saveState();c.translate(*OFF[i]);c.clipPath(p,stroke=0,fill=0)
        _field(c,xl-30,X1+20,yj-70,yj+70,yd,x50,(yj-9.5,yj+9.5),(),NS,DIM)
        a,b,cx2,d=BOX[i];c.setFillColor(white);c.setFillAlpha(.07);c.rect(a-10,b+(d-b)*.55,cx2-a+20,d-b,stroke=0,fill=1)
        if not on(i): c.setFillColor(INKN);c.setFillAlpha(.80);c.rect(xl-30,yj-80,X1-xl+60,160,stroke=0,fill=1)   # v13: faded further
        c.setFillAlpha(1);c.restoreState()
    for i,p in paths.items():                        # the cuts: one thin dark line, shared by both sides
        c.saveState();c.translate(*OFF[i])
        c.setStrokeColor(H("#0A1226"));c.setLineWidth(1.2);c.drawPath(p,stroke=1,fill=0)
        c.setStrokeColor(white);c.setStrokeAlpha(.22);c.setLineWidth(.5)
        c.saveState();c.translate(-.4,.5);c.drawPath(p,stroke=1,fill=0);c.restoreState();c.setStrokeAlpha(1);c.restoreState()
    for i,p in paths.items():                        # the lit piece(s) drawn last, outline on top
        if not on(i): continue
        c.saveState();c.translate(*OFF[i])
        c.saveState();_q=c.beginPath();_q.rect(-200,-200,W+400,Ht+400);_q._code.extend(p._code)   # Oct 10 (Dom): a gold rim OUTSIDE the lit piece
        from reportlab.pdfgen.canvas import FILL_EVEN_ODD as _EO;c.clipPath(_q,stroke=0,fill=0,fillMode=_EO)
        c.setStrokeColor(SUN[1]);c.setLineWidth(3.4);c.drawPath(p,stroke=1,fill=0);c.restoreState()
        c.setStrokeColor(H("#0A1226"));c.setLineWidth(1.3);c.drawPath(p,stroke=1,fill=0);c.restoreState()   # the black seam stays, on top
    for i in range(4):                               # names: top row up top, bottom row down low
        a,b,cx2,d=BOX[i];nm=PZ_NAME4[i];fs=11.5
        x=a+(9 if i in (0,2) else 8)+OFF[i][0];y=((d-14.0) if i in (0,1) else (b+4.6))+OFF[i][1]
        col=SUN[1] if on(i) else H("#8E98AD");c.setFont("Bebas",fs)   # Oct 10: the lit name in gold
        if on(i):
            tw=c.stringWidth(nm,"Bebas",fs);c.setFillColor(INKN);c.setFillAlpha(.80)
            c.roundRect(x-4,y-2.6,tw+8,12.4,2.4,stroke=0,fill=1);c.setFillAlpha(1)
        c.setFillColor(col);c.drawString(x,y,nm)
    return xl
def stamps(c,xr,ybot,lead=7.6,sz=5.6):
    """LAST UPDATED, stacked from the bottom up; labels on one straight edge, times on the right. Gold = older than a day."""
    lw=max(c.stringWidth(l,"Pop",sz) for l,_ in PZ_STAMPS);tw=max(c.stringWidth(_stamp_txt(t),"PopM",sz) for _,t in PZ_STAMPS)
    xl=xr-tw-lw-6
    for j,(lab,iso) in enumerate(reversed(PZ_STAMPS)):
        y=ybot+j*lead;old=(PZ_NOW-_dt.datetime.fromisoformat(iso)).total_seconds()>86400
        txt(c,xl,y,lab,"Pop",sz,H("#8E98AD"));txt(c,xr,y,_stamp_txt(iso),"PopM",sz,SUN[1] if old else H("#E4E8F0"),"r")
    y=ybot+len(PZ_STAMPS)*lead+1.6
    txt(c,xr,y,"LAST UPDATED","Bebas",8,SUN[1],"r")
    c.setFillColor(SUN[1]);c.rect(xl,y-2.2,xr-xl,.5,stroke=0,fill=1)
def masthead(c,section,sub):
    # Oct 11 (Dom): every page carries the front page's masthead - inside the margins, rounded, the same size
    c.setFillColor(PAPER);c.rect(0,0,W,Ht,stroke=0,fill=1)
    P=12;top=Ht-8;bot=top-MH+8
    c.setFillColor(INKN);c.roundRect(M,bot,W-2*M,top-bot,5,stroke=0,fill=1)
    txt(c,M+P,Ht-44,PZ_TITLE,"Bebas",34,PAPER)
    if "dk_icon" not in globals(): exec(open("/home/claude/cand/redesign/_dkicon.py").read(),globals())
    dk_icon(c,M+P+c.stringWidth(PZ_TITLE,"Bebas",34)+9,Ht-47,29)
    c.setFillColor(SUN[1]);c.rect(M+P,Ht-56,c.stringWidth(section,"Bebas",15),1.6,stroke=0,fill=1)
    txt(c,M+P,Ht-72,section,"Bebas",15,SUN[1])
    _sx=M+P+c.stringWidth(section,"Bebas",15)+10; _wk=globals().get("WEEKN")
    if _wk and not sub.startswith("Week"): sub=f"Week {_wk}  ·  "+sub
    if "FIELD REPORT" in section.upper(): sub=f"Week {_wk}" if _wk else sub.split("  ·  ")[0]   # Oct 11 (Dom): too much up here
    if "asof_line" not in globals(): exec(open("/home/claude/cand/redesign/_asof.py").read(),globals())
    asof_line(c,_sx,Ht-71.5,sub,W-M-9-108-(M+4)-12)   # stops short of the puzzle where it really sits
    i=_pz_idx(section);lg=_pz_league(section);col=LG[lg] if lg else SUN[1]
    c.saveState();p=c.beginPath();p.roundRect(M,bot,W-2*M,top-bot,5);c.clipPath(p,stroke=0)
    c.translate(-(M+4),-4);puzzle(c,i,col);c.restoreState()
    c.setFillColor(SUN[1]);c.rect(M,bot-3,W-2*M,2.2,stroke=0,fill=1)

# OCT10 masthead

# OCT10b masthead asof

# OCT11 icon pages

# OCT11 inset masthead

# OCT11 field report mast
