import sys, math, random; sys.path.insert(0,'/home/claude/cand')
from marklib import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import white
CL={"red":INK["bad"],"gold":INK["caution"],"grey":INK["closed"]}
TRI={"red":INK["bad"],"gold":INK["caution"]}

def team(c,x,y,abbr,tier,sz=7.2):
    c.setFillColor(GREY);c.setFont(F,sz);c.drawString(x,y,abbr);w=c.stringWidth(abbr,F,sz)
    c.setLineWidth(max(0.5,sz*0.07))
    if tier=="top": c.setStrokeColor(GREEN);c.line(x,y+sz*0.92,x+w,y+sz*0.92)
    if tier=="bot": c.setStrokeColor(RED);c.line(x,y-sz*0.32,x+w,y-sz*0.32)
    return w

# ---------- DRIFT: original proportions (big, medium, small), now falling down-right
DR=[(0,.12,.30),(.44,-.12,.12),(.66,-.28,.07)]
def drift_down(c,x,y,s):
    for i,(dx,dy,r) in enumerate(DR):
        c.setLineWidth(max(0.4,s*r*(0.25 if i==0 else 0.30)));c.circle(x+s*(.30+dx),y+s*dy,s*r,stroke=1,fill=0)
    return s*.96
def drift_up_old(c,x,y,s):
    for i,(dx,dy,r) in enumerate([(0,0,.30),(.44,.24,.12),(.66,.40,.07)]):
        c.setLineWidth(max(0.4,s*r*(0.25 if i==0 else 0.30)));c.circle(x+s*(.30+dx),y+s*dy,s*r,stroke=1,fill=0)
    return s*.96
def cluster(c,x,y,s,col,fn=drift_down):
    c.saveState();c.setStrokeColor(CL[col]);w=fn(c,x,y,s);c.restoreState();return w

# ---------- SIGNAL variants. All share the plain mark (count is the dot, two arcs).
def _arcs(c,cx,cy,s,k,radii=(0.46,0.72),lw=0.11):
    c.setStrokeColor(k);c.setLineCap(1)
    for r in radii: c.setLineWidth(s*lw);c.arc(cx-r*s,cy-r*s,cx+r*s,cy+r*s,40,100)
def _digit(c,cx,cy,s,k,age):
    sz=fit(c,age,FB,s*0.80,s*0.42);c.setFillColor(k);c.setFont(FB,sz);c.drawCentredString(cx,cy-sz*0.34,age)

def plain(c,x,y,s,g,age):
    k=INK[g];c.saveState();cx,cy=x+s*.5,y+s*.14;_digit(c,cx,cy,s,k,age);_arcs(c,cx,cy,s,k);c.restoreState()

# 1 SHRUNK RING — whole mark 85%, ring pulled in tight
def v_ring(c,x,y,s,g,age="0"):
    s2=s*.85;k=INK[g];c.saveState();cx,cy=x+s*.5,y+s*.20
    _digit(c,cx,cy,s2,k,age);_arcs(c,cx,cy,s2,k)
    c.setStrokeColor(k);c.setLineWidth(max(0.6,s2*.06));c.circle(cx,cy+s2*.28,s2*.60,stroke=1,fill=0);c.restoreState()
# 2 ARC COUNT — three arcs new, two current, one fading
def v_arcs(c,x,y,s,g,age="0",n=3):
    k=INK[g];c.saveState();cx,cy=x+s*.5,y+s*.14;_digit(c,cx,cy,s,k,age)
    radii={3:(.40,.58,.76),2:(.46,.72),1:(.52,)}[n];_arcs(c,cx,cy,s,k,radii,0.085 if n==3 else 0.11);c.restoreState()
# 3 BURST — dot with spikes radiating, no digit
def burst_center(c,cx,cy,s,k,rays=10,rin=.08,rout=.27):
    c.setFillColor(k);c.circle(cx,cy,s*rin,stroke=0,fill=1);c.setStrokeColor(k);c.setLineCap(1);c.setLineWidth(max(0.5,s*.045))
    for i in range(rays):
        a=2*math.pi*i/rays+.2;r2=rout if i%2==0 else rout*.72
        c.line(cx+s*(rin+.03)*math.cos(a),cy+s*(rin+.03)*math.sin(a),cx+s*r2*math.cos(a),cy+s*r2*math.sin(a))
def v_burst(c,x,y,s,g,age=None):
    k=INK[g];c.saveState();cx,cy=x+s*.5,y+s*.20;burst_center(c,cx,cy,s,k);_arcs(c,cx,cy,s,k);c.restoreState()
# 4 SPLATTER — bullet-hit blot with droplets
def splat_center(c,cx,cy,s,k):
    rnd=random.Random(7);c.setFillColor(k);p=c.beginPath();N=14
    for i in range(N):
        a=2*math.pi*i/N;r=s*(.15 if i%2 else .24)*rnd.uniform(.85,1.1);px,py=cx+r*math.cos(a),cy+r*math.sin(a)
        p.moveTo(px,py) if i==0 else p.lineTo(px,py)
    p.close();c.drawPath(p,stroke=0,fill=1)
    for a,d,r in [(.3,.33,.04),(2.1,.31,.032),(3.9,.34,.035),(5.2,.30,.028)]:
        c.circle(cx+s*d*math.cos(a),cy+s*d*math.sin(a),s*r,stroke=0,fill=1)
def v_splat(c,x,y,s,g,age=None):
    k=INK[g];c.saveState();cx,cy=x+s*.5,y+s*.20;splat_center(c,cx,cy,s,k);_arcs(c,cx,cy,s,k,(.50,.74));c.restoreState()
# 5 SPARK — four-point star (my alternative)
def v_spark(c,x,y,s,g,age=None):
    k=INK[g];c.saveState();cx,cy=x+s*.5,y+s*.20;c.setFillColor(k);p=c.beginPath()
    for i in range(8):
        a=math.pi/2+i*math.pi/4;r=s*(.27 if i%2==0 else .075);px,py=cx+r*math.cos(a),cy+r*math.sin(a)
        p.moveTo(px,py) if i==0 else p.lineTo(px,py)
    p.close();c.drawPath(p,stroke=0,fill=1);_arcs(c,cx,cy,s,k,(.46,.72));c.restoreState()
# 6 SOLID — the dot fills in, zero knocked out in white (my alternative)
def v_solid(c,x,y,s,g,age="0"):
    k=INK[g];c.saveState();cx,cy=x+s*.5,y+s*.18;c.setFillColor(k);c.circle(cx,cy,s*.20,stroke=0,fill=1)
    sz=s*.30;c.setFillColor(white);c.setFont(FB,sz);c.drawCentredString(cx,cy-sz*.36,age);_arcs(c,cx,cy,s,k,(.48,.74));c.restoreState()

OPTS=[("1 · SHRUNK RING",v_ring,"Your ring, whole mark cut 15%, ring pulled tight."),
      ("2 · ARC COUNT",v_arcs,"Three arcs new, two current, one fading. No ring."),
      ("3 · BURST",v_burst,"Zero replaced by a starburst. Same height as every mark."),
      ("4 · SPLATTER",v_splat,"Bullet-hit blot with droplets in place of the zero."),
      ("5 · SPARK",v_spark,"My alternative — a four-point twinkle in the center."),
      ("6 · SOLID",v_solid,"My alternative — the dot fills in, zero knocked out white.")]

def triangle(c,x,y,col,h=6.2):
    c.setFillColor(TRI[col]);p=c.beginPath();p.moveTo(x,y-h/2);p.lineTo(x+h*0.9,y);p.lineTo(x,y+h/2);p.close();c.drawPath(p,stroke=0,fill=1)

SIG=16
def row(c,x,y,tri,nm,pos,tm,tier,sig,cl,namew,newfn,sz=7.2,scale=1.0):
    if tri: triangle(c,x,y+sz*0.34,tri,6.2*scale)
    nx=x+10*scale;c.setFillColor(NAVY);c.setFont(FB,sz);c.drawString(nx,y,nm)
    w=nx+namew+6*scale;c.setFillColor(GREY);c.setFont(F,sz);c.drawString(w,y,pos);w+=c.stringWidth("WR",F,sz)+4*scale
    team(c,w,y,tm,tier,sz);w+=c.stringWidth("WAS",F,sz)+8*scale
    if cl: cluster(c,w,y+sz*0.34,SIG*scale,cl)
    sx=w+SIG*scale+8*scale
    if sig:
        g,a,new=sig;yy=y-sz*0.62
        if new: newfn(c,sx,yy,SIG*scale,g)
        elif newfn is v_arcs: v_arcs(c,sx,yy,SIG*scale,g,a,1 if g=="closed" else 2)
        else: plain(c,sx,yy,SIG*scale,g,a)
def namecol(c,rows,sz=7.2): return max(c.stringWidth(r[1],FB,sz) for r in rows)

def head(c,t,sub):
    W,Ht=letter;c.setFillColor(NAVY);c.rect(0,Ht-60,W,60,stroke=0,fill=1)
    c.setFillColor(PAPER);c.setFont(FB,17);c.drawString(40,Ht-35,t);c.setFont(F,8.4);c.drawString(40,Ht-50,sub)
def foot(c,n):
    c.setFillColor(GREY);c.setFont(F,6.4)
    c.drawString(40,32,"Sample names and grades only — not this week's reads.  Candidate only — v36d untouched.")
    c.drawRightString(572,32,f"Mark Batch v5 · {n} of 2")
def label(c,x,y,t,sub=None):
    c.setFillColor(NAVY);c.setFont(FB,11.5);c.drawString(x,y,t)
    if sub: c.setFillColor(GREY);c.setFont(F,8);c.drawString(x,y-13,sub)

W,Ht=letter;LM=40
c=canvas.Canvas("/mnt/user-data/outputs/Mark_Batch_Mockup_v5.pdf",pagesize=letter)

# ============ PAGE 1
head(c,"DRIFT FALLS  ·  SIX WAYS TO SAY 'BRAND NEW'","Drift back to big-plus-two-small, now falling down and away. Six options for a new Signal that stays inside the row.")
y=Ht-92;label(c,LM,y,"DRIFT, FALLING","Original proportions restored — one big bubble, two smaller ones dropping down and to the right.")
by=y-58;c.setFillColor(MID);c.setFont(F,6.6);c.drawString(LM,by+34,"BEFORE — rising")
cluster(c,LM+4,by,44,"red",drift_up_old);c.setFillColor(MID);c.drawString(LM+110,by+34,"AFTER — falling")
for j,col in enumerate(("red","gold","grey")):
    bx=LM+112+j*95;cluster(c,bx,by,44,col);c.setFillColor(MID);c.setFont(F,6.4)
    c.drawString(bx,by-28,{"red":"first out","gold":"next in line","grey":"marked"}[col])
for j,col in enumerate(("red","gold","grey")): cluster(c,LM+420+j*28,by-4,16,col)
c.setFillColor(MID);c.setFont(F,6);c.drawString(LM+420,by-28,"actual size")

y=by-58;label(c,LM,y,"'BRAND NEW' — SIX OPTIONS","Each shown big in green, gold and red, beside today's 2-day mark, then at actual size between two striped rows.")
top=y-30;colw=(W-2*LM)/2
for i,(t,fn,sub) in enumerate(OPTS):
    cx0=LM+(i%2)*colw;cy0=top-(i//2)*170
    c.setFillColor(NAVY);c.setFont(FB,9.5);c.drawString(cx0,cy0,t)
    c.setFillColor(GREY);c.setFont(F,7);c.drawString(cx0,cy0-11,sub)
    gy=cy0-72
    for j,g in enumerate(("good","caution","bad")):
        fn(c,cx0+j*62,gy,38,g)
    plain(c,cx0+196,gy,38,"good","2");c.setFillColor(MID);c.setFont(F,6);c.drawString(cx0+198,gy-10,"normal, day 2")
    # actual size test strip: striped 19pt rows above and below
    sy=gy-52
    for k in range(3):
        if k!=1: c.setFillColor(STRIPE);c.rect(cx0-4,sy-7-(k-1)*19,colw-16,19,stroke=0,fill=1)
    c.setStrokeColor(RULE);c.setLineWidth(.3);c.line(cx0-4,sy+12,cx0+colw-20,sy+12);c.line(cx0-4,sy-7,cx0+colw-20,sy-7)
    c.setFillColor(NAVY);c.setFont(FB,7.2);c.drawString(cx0,sy,"Jaxon Smith-Njigba");c.setFillColor(GREY);c.setFont(F,7.2);c.drawString(cx0+76,sy,"WR");team(c,cx0+92,sy,"SEA","mid")
    fn(c,cx0+134,sy-4.5,SIG,"good");plain(c,cx0+160,sy-4.5,SIG,"good","2")
    if fn is v_arcs: v_arcs(c,cx0+186,sy-4.5,SIG,"closed","30",1)
    c.setFillColor(MID);c.setFont(F,6);c.drawString(cx0+(212 if fn is v_arcs else 186),sy,"actual size")
foot(c,1);c.showPage()

# ============ PAGE 2: one roster, drawn with each option
head(c,"ONE ROSTER  ·  SIX WAYS","Same eight men each time. Two are brand new — Smith-Njigba (good news) and Andrews (bad news). Look for which one your eye finds first.")
ROSTER=[(None,"Jahmyr Gibbs","RB","DET","top",("good","6",False),None),
        (None,"De'Von Achane","RB","MIA","bot",("good","2",False),None),
        ("gold","Garrett Wilson","WR","NYJ","mid",("caution","0/40",False),None),
        (None,"Jaxon Smith-Njigba","WR","SEA","mid",("good","0",True),None),
        ("red","Jaylen Warren","RB","PIT","mid",("caution","1",False),"red"),
        (None,"Tony Pollard","RB","TEN","bot",("closed","30",False),"gold"),
        (None,"Travis Etienne Jr.","RB","JAX","mid",None,"grey"),
        (None,"Mark Andrews","TE","BAL","top",("bad","0",True),None)]
nw=namecol(c,ROSTER);top=Ht-92
for i,(t,fn,sub) in enumerate(OPTS):
    x0=LM+(i%2)*colw;y0=top-(i//2)*218
    c.setFillColor(NAVY);c.setFont(FB,9.5);c.drawString(x0,y0,t)
    for k,r in enumerate(ROSTER):
        ry=y0-22-k*19
        if k%2==0: c.setFillColor(STRIPE);c.rect(x0-4,ry-7,colw-16,19,stroke=0,fill=1)
        row(c,x0,ry,*r,namew=nw,newfn=fn)
c.setFillColor(GREY);c.setFont(F,7)
c.drawString(LM,top-3*218+30,"Wilson is a returner — prints 0/40 plainly in every version. The new-mark only goes on a man we have never seen before.")
foot(c,2);c.save()
