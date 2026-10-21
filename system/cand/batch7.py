import sys, math, random; sys.path.insert(0,'/home/claude/cand')
from marklib import *
from batch5 import team, triangle, head, label, drift_down, CL
from batch6 import splat, signal as signal_v6
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
W,Ht=letter;LM=40;SIG=16;LOCK=0.50
ARC=(.40,.60);ALW=.10

def ctxt(cur,prev=None): return f"{cur}/{prev}" if prev is not None else f"{cur:02d}"

def arcs7(c,cx,cy,s,k):
    c.setStrokeColor(k);c.setLineCap(1)
    for r in ARC: c.setLineWidth(s*ALW);c.arc(cx-r*s,cy-r*s,cx+r*s,cy+r*s,40,100)

def sig7(c,cx,cy,s,g,txt):
    """Glyph never moves or resizes: arcs centered on cx. cy = middle of the digits.
    Digits one locked size, centered under the arcs. txt None = splat (brand new)."""
    k=INK[g];c.saveState()
    if txt is None: splat(c,cx,cy+s*.02,s*.92,k)
    else:
        sz=s*LOCK;c.setFillColor(k);c.setFont(FB,sz);c.drawCentredString(cx,cy-sz*.36,txt)
    arcs7(c,cx,cy+s*.08,s,k);c.restoreState()

def colw(s): # width reserved for the Signal column: the widest count we expect
    return max(s*.9, canvas.Canvas("/tmp/x.pdf").stringWidth("20/100",FB,s*LOCK))

# ---------- TIGHT CLUSTER: big, medium beside it, small tucked in the pocket underneath
TIGHT=[(0,0,.30),(.50,.08,.14),(.41,-.23,.08)]
def tint(k,a=.28): return Color(k.red,k.green,k.blue,alpha=a)
def tight(c,cx,cy,s,col,fill=False):
    k=CL[col];c.saveState();c.setStrokeColor(k)
    for i,(dx,dy,r) in enumerate(TIGHT):
        c.setLineWidth(max(0.45,s*r*(0.24 if i==0 else 0.30)))
        if i==0 and fill: c.setFillColor(tint(k));c.circle(cx+s*dx,cy+s*dy,s*r,stroke=1,fill=1)
        else: c.circle(cx+s*dx,cy+s*dy,s*r,stroke=1,fill=0)
    c.restoreState()
def drift7(c,cx,cy,s,col,fill=False):  # current drift falling, big bubble centered on cx,cy
    k=CL[col];c.saveState();c.setStrokeColor(k)
    for i,(dx,dy,r) in enumerate([(0,0,.30),(.44,-.24,.12),(.66,-.40,.07)]):
        c.setLineWidth(max(0.4,s*r*(0.25 if i==0 else 0.30)))
        if i==0 and fill: c.setFillColor(tint(k));c.circle(cx+s*dx,cy+s*dy,s*r,stroke=1,fill=1)
        else: c.circle(cx+s*dx,cy+s*dy,s*r,stroke=1,fill=0)
    c.restoreState()

def foot(c,n,N=3):
    c.setFillColor(GREY);c.setFont(F,6.4)
    c.drawString(40,32,"Sample names and grades only — not this week's reads.  Candidate only — v36d untouched.")
    c.drawRightString(572,32,f"Mark Batch v7 · {n} of {N}")
def small(c,x,y,t,col=MID,sz=6.4,centre=False):
    c.setFillColor(col);c.setFont(F,sz);(c.drawCentredString if centre else c.drawString)(x,y,t)
def guide(c,x,y0,y1):
    c.saveState();c.setStrokeColor(RULE);c.setLineWidth(.5);c.setDash(2,2);c.line(x,y0,x,y1);c.restoreState()

c=canvas.Canvas("/mnt/user-data/outputs/Mark_Batch_Mockup_v7.pdf",pagesize=letter)
# ================= PAGE 1 — THE SIGNAL, LOCKED
head(c,"THE SIGNAL, LOCKED","The arcs never move and never change size. The digits hold one size and sit centered underneath. Color = how loud. Count = how old.")
y=Ht-92;label(c,LM,y,"STOPPED ROAMING","Same five counts stacked in a column. Dashed line runs through the center of the arcs.")
ys=[y-48-i*34 for i in range(5)];cnt=["06","1/40","11/30","20/100",None]
# v6 left: roams
x6=LM+40;small(c,x6-20,y-24,"v6 — the arcs follow the number",GREY,7)
for yy,t in zip(ys,cnt): signal_v6(c,x6,yy-6,26,"caution",t)
guide(c,x6+10,ys[-1]-14,ys[0]+24)
x7=LM+300;small(c,x7-60,y-24,"v7 — arcs fixed, number centered under them",GREY,7)
for yy,t in zip(ys,cnt): sig7(c,x7,yy,26,"caution",t)
guide(c,x7,ys[-1]-14,ys[0]+24)

y=ys[-1]-40;label(c,LM,y,"A MAN'S LIFE ON THE PAGE — FIRST TIME EVER","Splat on the day he arrives. Next day 01. Padded until there's a slash.")
sy=y-44;seq=[(None,"arrives today"),("01","day 1"),("02","day 2"),("09","day 9"),("14","day 14"),("30","day 30")]
for i,(t,lab) in enumerate(seq):
    cx=LM+30+i*80;g="closed" if t=="30" else "good";sig7(c,cx,sy,34,g,t);small(c,cx,sy-26,lab,centre=True)
y=sy-52;label(c,LM,y,"A MAN'S LIFE ON THE PAGE — COMING BACK","Back today reads 0/40: here today, gone 40 days before that. Then the left number ticks up.")
sy=y-44;seq=[("0/40","back today"),("1/40","day 1 back"),("10/40","day 10 back"),("5/60","5 back, gone 60"),("20/100","extreme — still fits")]
for i,(t,lab) in enumerate(seq):
    cx=LM+36+i*96;sig7(c,cx,sy,34,"caution",t);small(c,cx,sy-26,lab,centre=True)
small(c,LM,sy-44,"No returner ever gets the splat. The count only moves with time; the color can change any day the news does.",GREY,7.2)

y=sy-72;label(c,LM,y,"ACTUAL SIZE, ON THE ROW LINE","Digits now sit on the same line as the name — the Signal no longer drops below the row.")
sy=y-36;c.setFillColor(STRIPE);c.rect(LM-4,sy-5.5,W-2*LM+8,19,stroke=0,fill=1)
c.setFillColor(NAVY);c.setFont(FB,7.2);c.drawString(LM+2,sy,"Name line")
st=[("good",None),("bad",None),("good","01"),("good","02"),("caution","09"),("good","14"),("closed","30"),("caution","0/40"),("caution","1/40"),("bad","10/40"),("caution","20/100")]
for i,(g,t) in enumerate(st): sig7(c,LM+70+i*43,sy+2.6,SIG,g,t)
foot(c,1);c.showPage()

# ================= PAGE 2 — THE CLUSTER, TIGHTENED
head(c,"THE CLUSTER, TIGHTENED","Your idea: small bubble tucked in underneath, between the big one and the medium one. Less width, reads as a cluster.")
y=Ht-92;label(c,LM,y,"DRIFT FALLING vs TIGHT","Large, so you can see the geometry. Top row hollow, bottom row with a light tint in the big bubble.")
for r,fill in enumerate((False,True)):
    by=y-66-r*80
    for j,col in enumerate(("red","gold","grey")):
        drift7(c,LM+80+j*80,by,50,col,fill)
        tight(c,LM+360+j*72,by,50,col,fill)
    small(c,LM-4,by-3,("hollow" if r==0 else "tinted"),GREY,7)
small(c,LM+140,y-30,"DRIFT FALLING — today",NAVY,7.5);small(c,LM+430,y-30,"TIGHT — your idea",NAVY,7.5)

y=y-222;label(c,LM,y,"SMALLER — AT ACTUAL ROW SIZE","Three sizes of the tight cluster. 16 is today's size; 13 and 11 are smaller so it stops rhyming with the Signal.")
for r,fill in enumerate((False,True)):
    by=y-40-r*34;c.setFillColor(STRIPE);c.rect(LM-4,by-8,W-2*LM+8,19,stroke=0,fill=1)
    small(c,LM,by-2,"hollow" if not fill else "tinted",GREY,7)
    for gi,s in enumerate((16,13,11)):
        for j,col in enumerate(("red","gold","grey")):
            tight(c,LM+70+gi*160+j*34,by+1.5,s,col,fill)
        if r==0: small(c,LM+70+gi*160,by+16,f"size {s}"+("  (today)" if s==16 else ""),GREY,6.6)

y=y-128;label(c,LM,y,"BESIDE THE SIGNAL","Size 13 tight cluster in its own fixed cell, then the locked Signal. Compare to v6's drift at 16.")
by=y-40
for r,(nm,fn,s,fill) in enumerate([("v6 drift, 16",drift7,16,False),("tight, 13, hollow",tight,13,False),("tight, 13, tinted",tight,13,True)]):
    yy=by-r*24;c.setFillColor(STRIPE if r%2==0 else PAPER);c.rect(LM-4,yy-5.5,300,19,stroke=0,fill=1)
    small(c,LM,yy+1,nm,GREY,7);fn(c,LM+120,yy+2.6,s,"red",fill);sig7(c,LM+170,yy+2.6,SIG,"caution","01")
foot(c,2);c.showPage()

# ================= PAGE 3 — ONE ROSTER
head(c,"ONE ROSTER  ·  LOCKED COLUMNS","Triangle · name · position · team · cluster · Signal. Cluster cell and Signal column are fixed — same place on every row.")
ROSTER=[(None,"Jahmyr Gibbs","RB","DET","top",("good","06"),None),
        (None,"De'Von Achane","RB","MIA","bot",("good","11/30"),None),
        ("gold","Garrett Wilson","WR","NYJ","mid",("caution","0/40"),None),
        (None,"Jaxon Smith-Njigba","WR","SEA","mid",("good",None),None),
        ("red","Jaylen Warren","RB","PIT","mid",("caution","01"),"red"),
        (None,"Tony Pollard","RB","TEN","bot",("closed","30"),"gold"),
        (None,"Travis Etienne Jr.","RB","JAX","mid",None,"grey"),
        (None,"Mark Andrews","TE","BAL","top",("bad",None),None)]
CL_S=13
def roster(x0,y0,k,title,fill,guides=False):
    sz=7.2*k;nw=max(c.stringWidth(r[1],FB,sz) for r in ROSTER);rh=19*k
    posx=x0+10*k+nw+6*k;tmx=posx+c.stringWidth("WR",F,sz)+4*k
    clx=tmx+c.stringWidth("WAS",F,sz)+10*k+CL_S*k*.30          # big-bubble center, fixed
    sgx=clx+CL_S*k*.70+10*k+colw(SIG*k)/2                       # Signal center, fixed
    c.setFillColor(NAVY);c.setFont(FB,9.5);c.drawString(x0,y0,title)
    top=y0-22*k;tw=sgx+colw(SIG*k)/2+6*k-x0
    for i in range(0,len(ROSTER),2):
        c.setFillColor(STRIPE);c.rect(x0-4,top-i*rh-5.5*k,tw+4,rh,stroke=0,fill=1)
    if guides:
        guide(c,sgx,top-len(ROSTER)*rh+8*k,top+16*k);guide(c,clx,top-len(ROSTER)*rh+8*k,top+16*k)
    for i,(tri,nm,pos,tm,tier,sig,cl) in enumerate(ROSTER):
        ry=top-i*rh;mid=ry+sz*.36
        if tri: triangle(c,x0,mid,tri,6.2*k)
        c.setFillColor(NAVY);c.setFont(FB,sz);c.drawString(x0+10*k,ry,nm)
        c.setFillColor(GREY);c.setFont(F,sz);c.drawString(posx,ry,pos);team(c,tmx,ry,tm,tier,sz)
        if cl: tight(c,clx,mid,CL_S*k,cl,fill)
        if sig: sig7(c,sgx,mid,SIG*k,sig[0],sig[1])
    return tw
roster(LM,Ht-96,1.0,"ACTUAL SIZE — tight cluster, hollow",False)
roster(LM+300,Ht-96,1.0,"ACTUAL SIZE — tight cluster, tinted",True)
roster(LM,Ht-290,1.6,"1.6×, tinted  — dashed lines show the two fixed columns",True,guides=True)
notes=["Wilson is back today after 40 days away: 0/40. Tomorrow he reads 1/40.",
       "Smith-Njigba and Andrews are brand new today — splat only. Tomorrow each reads 01.",
       "Every Signal's arcs sit on the same vertical line; long counts spread evenly both sides.",
       "Cluster drawn at size 13, down from 16, in a fixed cell — empty on rows without one."]
for i,t in enumerate(notes): small(c,LM,112-i*11,t,GREY,7.2)
foot(c,3);c.save()
