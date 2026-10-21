# PUZZLE MASTHEAD v3 (Oct 3, Dom): FOUR pieces, 2x2 - Global, Call Sheet, Field Report, Positions.
# Post-Mortem (history) and The Marks (the legend) are not pieces; on those pages nothing is lit.
# Real jigsaw shapes: every piece a different silhouette - tabs and holes on different sides, outer edges shaped too,
# each tab its own size and position. Glossy: gradient body, bevel rims, glint; lit piece glows in its color.
# Under the block, right-aligned: freshness stamps, one per source, Pacific time; older than 24 hours prints gold.
import math as _pm, datetime as _dt, random as _rnd
PZ_SECT=("OVERVIEW","CALL SHEET","FIELD REPORT","POSITIONS")
PZ_CELL={1:(1,1),2:(1,0),3:(0,0)}                    # Oct 3 (Dom): no Global piece - a Global page lights them ALL
PZ_ALL=0            # section -> (col,row); turned 45 deg: top, right, bottom, left = document order clockwise
PZ_NAME=("OVERVIEW","CALLS","FIELD","POSITIONS")
PZ_NFS=(9.0,9.0,9.0,7.6)
# edge signs: + bumps toward +x / +y. Chosen so all four pieces differ (see notes).
PZ_V={(0,1):+1,(0,0):-1,(1,1):+1,(1,0):-1,(2,1):-1,(2,0):+1}     # vertical line x, row
PZ_H={(0,0):+1,(1,0):+1,(0,1):+1,(1,1):-1,(0,2):-1,(1,2):+1}     # horizontal line col, y
def _pt(iso): return _dt.datetime.fromisoformat(iso)-_dt.timedelta(hours=7)      # UTC -> Pacific (PDT)
PZ_NOW=_dt.datetime.utcnow()
PZ_STAMPS=[("Rosters",  "2026-10-03T17:45"),          # Yahoo
           ("Injuries", "2026-10-03T17:40"),          # NFL injury report via nflverse
           ("Market",   "2026-10-01T16:37")]          # Rotowire / ESPN / CBS blend
def _stamp_txt(iso):
    t=_pt(iso);return f"{t.strftime('%a')} {t.strftime('%I').lstrip('0')}:{t.strftime('%M')} {t.strftime('%p')}"
PZ_SUB={"THE MARKS":0,"POST-MORTEM":2}    # subsections ride their parent: the legend under Global, the look-back under Field Report
def _pz_idx(section):
    s=section.upper()
    if s.startswith("GLOBAL"): return 0                 # older pages still say Global Watch
    for i,k in enumerate(PZ_SECT):
        if s.startswith(k): return i
    for k,i in PZ_SUB.items():
        if k in s: return i
def _pz_league(section):
    m=re.search(r"DK (IV|III|II|I)\b",section);return m.group(1) if m else None
def _mix(a,b,t): return Color(a.red*(1-t)+b.red*t,a.green*(1-t)+b.green*t,a.blue*(1-t)+b.blue*t)
_JIT={}
def _jit(key):
    if key not in _JIT:
        r=_rnd.Random(hash(key)%9973+17)
        _JIT[key]=(r.uniform(.42,.58),r.uniform(.25,.31),r.uniform(.060,.080),r.uniform(.135,.165))
    return _JIT[key]
def _edge_segs(ax,ay,bx,by,sign,key,S):
    """cubic segments for one edge in page coords, a->b. sign bumps toward +x/+y (global)."""
    L=_pm.hypot(bx-ax,by-ay);ux,uy=(bx-ax)/L,(by-ay)/L
    nx,ny=(0,1) if abs(uy)<.5 else (1,0)                       # global +y for horizontal, +x for vertical
    cu,h,n,w=_jit(key)
    def P(u,v):
        a=cu*L+(u-cu)*S if 0<u<1 else u*L
        return (ax+ux*a+nx*v*S*sign, ay+uy*a+ny*v*S*sign)
    pts=[P(0,0),
         P(cu-.20,0),P(cu-n+.02,.03),P(cu-n,h*.34),
         P(cu-n-.04,h*.64),P(cu-w,h),P(cu,h),
         P(cu+w,h),P(cu+n+.04,h*.64),P(cu+n,h*.34),
         P(cu+n-.02,.03),P(cu+.20,0),P(1,0)]
    return pts                                                  # P0, then 4 cubics of 3 points
def _trace(p,pts,rev,first):
    if rev: pts=pts[::-1]
    if first: p.moveTo(*pts[0])
    for i in range(1,len(pts),3): p.curveTo(*pts[i],*pts[i+1],*pts[i+2])
def _piece(c,x,y,pw,ph,k,r,dx=0,dy=0):
    X=lambda i:x+i*pw+dx;Y=lambda j:y+j*ph+dy;S=ph
    p=c.beginPath()
    _trace(p,_edge_segs(X(k),Y(r),X(k+1),Y(r),PZ_H[(k,r)],("h",k,r),S),False,True)       # bottom, +x
    _trace(p,_edge_segs(X(k+1),Y(r),X(k+1),Y(r+1),PZ_V[(k+1,r)],("v",k+1,r),S),False,False)  # right, +y
    _trace(p,_edge_segs(X(k),Y(r+1),X(k+1),Y(r+1),PZ_H[(k,r+1)],("h",k,r+1),S),True,False)  # top, -x
    _trace(p,_edge_segs(X(k),Y(r),X(k),Y(r+1),PZ_V[(k,r)],("v",k,r),S),True,False)         # left, -y
    p.close();return p
PZ_ROT=45                                            # the block turned onto its point: a diamond
def _f(dx,dy,a=PZ_ROT):                               # a page-space offset expressed in the turned frame
    r=_pm.radians(a);return (dx*_pm.cos(r)-dy*_pm.sin(r), dx*_pm.sin(r)+dy*_pm.cos(r))
def _pz_glyph(c,i,x,y,s,col,on):
    """each piece carries the mark of its page: Calls the triangle, Field the win-chance gauge, Positions the scatter."""
    u=s/30.0;c.saveState();c.setStrokeColor(col);c.setFillColor(col);c.setLineCap(1);c.setLineJoin(1)
    if i==1:                                           # CALL SHEET - the triangle that points at a call
        p=c.beginPath();p.moveTo(x-4.2*u,y+4.6*u);p.lineTo(x+5.4*u,y);p.lineTo(x-4.2*u,y-4.6*u);p.close();c.drawPath(p,stroke=0,fill=1)
    elif i==2:                                         # FIELD REPORT - the gauge, needle in
        c.setLineWidth(1.9*u);c.arc(x-6*u,y-4.6*u,x+6*u,y+7.4*u,0,180)
        c.setLineWidth(1.3*u);c.line(x,y+1.4*u,x+3.4*u,y+5.2*u);c.circle(x,y+1.4*u,1.2*u,stroke=0,fill=1)
    elif i==3:                                         # POSITIONS - balls on the scatter, one ringed
        for dx,dy,r in ((-5.2,-2.6,1.6),(-1.2,2.4,1.9),(3.6,-.6,1.6)): c.circle(x+dx*u,y+dy*u,r*u,stroke=0,fill=1)
        c.setLineWidth(.8*u);c.circle(x+5.4*u,y+3.8*u,2.0*u,stroke=1,fill=0)
        c.setLineWidth(.6*u);c.line(x-7.2*u,y-5.4*u,x+7.6*u,y-5.4*u)
    c.restoreState()
def puzzle(c,cx,cy,s,lit,litcol):
    """2x2 block of s-sized pieces, turned PZ_ROT degrees about (cx,cy). Clockwise from the top: Global, Calls, Field, Positions."""
    x=-s;y=-s;pw=ph=s
    c.saveState();c.translate(cx,cy);c.rotate(-PZ_ROT)
    cells=sorted(PZ_CELL.items(),key=lambda q:q[0]==lit)
    sx,sy=_f(1.6,-2.6)
    for i,(k,r) in cells:
        c.setFillColor(H("#060B17"));c.drawPath(_piece(c,x,y,pw,ph,k,r,sx,sy),stroke=0,fill=1)
    ux,uy=_f(0,1)                                     # page "up" inside the turned frame - light comes from above
    lx,ly=_f(.7,-.7);dx_,dy_=_f(-.7,.7)
    for i,(k,r) in cells:
        on=(i==lit) or (lit==PZ_ALL);p=_piece(c,x,y,pw,ph,k,r)
        base=litcol if on else H("#2E3C5C")
        top=_mix(base,PAPER,.45 if on else .17);bot=_mix(base,H("#050A16"),.40 if on else .44)
        mx,my=x+k*pw+pw/2,y+r*ph+ph/2;R=s*.85
        if on:
            for wdt,a in ((8,.10),(5,.16),(2.8,.24)):
                c.setStrokeColor(litcol);c.setStrokeAlpha(a);c.setLineWidth(wdt);c.setLineJoin(1);c.drawPath(p,stroke=1,fill=0)
            c.setStrokeAlpha(1)
        c.saveState();c.clipPath(p,stroke=0,fill=0)
        c.linearGradient(mx+ux*R,my+uy*R,mx-ux*R,my-uy*R,(top,base,bot),(0,.48,1),extend=True)
        c.setStrokeColor(PAPER);c.setStrokeAlpha(.40 if on else .12);c.setLineWidth(1.0)
        c.drawPath(_piece(c,x,y,pw,ph,k,r,lx,ly),stroke=1,fill=0)
        c.setStrokeColor(H("#050A16"));c.setStrokeAlpha(.40 if on else .30)
        c.drawPath(_piece(c,x,y,pw,ph,k,r,dx_,dy_),stroke=1,fill=0)
        if on:
            gx_,gy_=_f(-s*.10,s*.24)
            for a,rr in ((.10,.30),(.16,.19),(.26,.10)):
                c.setFillColor(PAPER);c.setFillAlpha(a)
                c.ellipse(mx+gx_-s*rr,my+gy_-s*rr*.5,mx+gx_+s*rr,my+gy_+s*rr*.5,stroke=0,fill=1)
        c.setStrokeAlpha(1);c.setFillAlpha(1);c.restoreState()
        c.setStrokeColor(H("#0A1020"));c.setLineWidth(1.1);c.setLineJoin(1);c.drawPath(p,stroke=1,fill=0)
    c.restoreState()
    for i,(k,r) in PZ_CELL.items():                   # names: upright, set on each piece's center, letterspaced caps
        fx,fy=-s+k*s+s/2,-s+r*s+s/2;t=_pm.radians(-PZ_ROT)
        px_=cx+fx*_pm.cos(t)-fy*_pm.sin(t);py_=cy+fx*_pm.sin(t)+fy*_pm.cos(t)
        on=(i==lit) or (lit==PZ_ALL);nm=PZ_NAME[i];fs=PZ_NFS[i]
        ink=PAPER if on else H("#93A0BA");gy=py_+s*.17;ny=py_-s*.20
        if on: _pz_glyph(c,i,px_+.5,gy-.6,s,H("#050A16"),True)
        _pz_glyph(c,i,px_,gy,s,ink,on)
        if on: txt(c,px_+.5,ny-.6,nm,"Bebas",fs,H("#050A16"),"c")
        txt(c,px_,ny,nm,"Bebas",fs,ink,"c")
def stamps(c,xr,ytop,lead=8.4,sz=6.0):
    """top-right, top-down: labels on one straight left edge, times on the right margin. Gold when older than a day."""
    lw=max(c.stringWidth(l,"Pop",sz) for l,_ in PZ_STAMPS);tw=max(c.stringWidth(_stamp_txt(t),"PopM",sz) for _,t in PZ_STAMPS)
    xl=xr-tw-lw-8
    for i,(lab,iso) in enumerate(PZ_STAMPS):
        y=ytop-i*lead;old=(PZ_NOW-_dt.datetime.fromisoformat(iso)).total_seconds()>86400
        txt(c,xl,y,lab,"Pop",sz,H("#8E98AD"));txt(c,xr,y,_stamp_txt(iso),"PopM",sz,SUN[1] if old else H("#E4E8F0"),"r")
    return xl
MH=84                                                 # masthead band: was 92 - the gold rides up, the page gets air
def masthead(c,section,sub):
    c.setFillColor(PAPER);c.rect(0,0,W,Ht,stroke=0,fill=1)
    c.setFillColor(INKN);c.rect(0,Ht-MH,W,MH,stroke=0,fill=1)
    txt(c,M,Ht-44,"DARK KNIGHT FANTASY FOOTBALL","Bebas",34,PAPER)
    c.setFillColor(SUN[1]);c.rect(M,Ht-56,30,1.6,stroke=0,fill=1)
    txt(c,M,Ht-74,section,"Bebas",15,SUN[1])
    txt(c,M+c.stringWidth(section,"Bebas",15)+10,Ht-73.5,sub,"Pop",7.2,H("#C9CFDB"))
    i=_pz_idx(section);lg=_pz_league(section);col=LG[lg] if lg else SUN[1]
    xl=stamps(c,W-M,Ht-26)                            # freshness: top right, reading down, inside the title band
    s=27;puzzle(c,xl-s*1.70,Ht-29,s,i,col)            # moved left, beside the stamps; nothing drops below the section line
    c.setFillColor(SUN[1]);c.rect(0,Ht-MH-3,W,3,stroke=0,fill=1)      # gold rule, edge to edge - raised with the band
