import sys, math, random; sys.path.insert(0,'/home/claude/cand')
from marklib import *
from batch5 import team, cluster, triangle, head, label  # reuse v5 pieces (importing runs v5 build; harmless)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
W,Ht=letter;LM=40;SIG=16
LOCK=0.50   # digit size as fraction of mark size — never shrinks, whatever the length

def count_txt(cur,prev=None):
    return f"{cur}/{prev}" if prev is not None else f"{cur:02d}"

def _arcs(c,cx,cy,s,k,radii=(0.46,0.72),lw=0.11):
    c.setStrokeColor(k);c.setLineCap(1)
    for r in radii: c.setLineWidth(s*lw);c.arc(cx-r*s,cy-r*s,cx+r*s,cy+r*s,40,100)

def splat(c,cx,cy,s,k):
    rnd=random.Random(5);c.setFillColor(k);p=c.beginPath();N=16
    R=[.27,.20,.24,.18,.29,.21,.23,.17,.26,.20,.28,.18,.22,.19,.25,.21]
    for i in range(N):
        a=2*math.pi*i/N;r=s*R[i];px,py=cx+r*math.cos(a),cy+r*math.sin(a)
        p.moveTo(px,py) if i==0 else p.lineTo(px,py)
    p.close();c.drawPath(p,stroke=0,fill=1)
    for a,d,r in [(.2,.38,.05),(2.5,.37,.042),(4.1,.39,.045)]:
        c.circle(cx+s*d*math.cos(a),cy+s*d*math.sin(a),s*r,stroke=0,fill=1)

def signal(c,x,y,s,g,txt):
    """Left edge fixed at x. txt=None -> splat (brand new). Width follows the content; arcs ride above its center."""
    k=INK[g];c.saveState()
    if txt is None:
        w=s*.62;cx=x+w/2;cy=y+s*.18;splat(c,cx,cy,s,k);_arcs(c,cx,cy,s,k,(.52,.76))
    else:
        sz=s*LOCK;c.setFont(FB,sz);w=c.stringWidth(txt,FB,sz);cx=x+w/2;cy=y+s*.14
        c.setFillColor(k);c.drawString(x,cy-sz*.34,txt);_arcs(c,cx,cy,s,k)
    c.restoreState();return w

def foot(c,n):
    c.setFillColor(GREY);c.setFont(F,6.4)
    c.drawString(40,32,"Sample names and grades only — not this week's reads.  Candidate only — v36d untouched.")
    c.drawRightString(572,32,f"Mark Batch v6 · {n} of 2")

c=canvas.Canvas("/mnt/user-data/outputs/Mark_Batch_Mockup_v6.pdf",pagesize=letter)
# ========== PAGE 1
head(c,"THE COUNT, SETTLED","Splat means never seen before. Counts are zero-padded. Returners carry two numbers. The digits never shrink.")
y=Ht-92;label(c,LM,y,"BRAND NEW = SPLAT, NO NUMBER","Bigger and bolder — fewer, larger droplets with clear gaps so it holds at row size. Only ever on day zero of a first sighting.")
by=y-80
for j,g in enumerate(("good","caution","bad")):
    signal(c,LM+10+j*80,by,48,g,None)
c.setFillColor(MID);c.setFont(F,6.4);[c.drawString(LM+10+j*80,by-26,t) for j,t in enumerate(("good news","caution","bad news"))]
for j,g in enumerate(("good","caution","bad")): signal(c,LM+290+j*26,by+8,SIG,g,None)
c.setFillColor(MID);c.drawString(LM+290,by-26,"actual size")

y=by-40;label(c,LM,y,"THE COUNT GROWS","Left to right: a man's life on the page. Padded so '01' reads as a counter, never as first place.")
seq=[(None,"new today"),(count_txt(1),"day 1"),(count_txt(3),"day 3"),(count_txt(9),"day 9"),(count_txt(14),"day 14"),(count_txt(30),"day 30")]
sy=y-70;x=LM+6
for i,(t,lab) in enumerate(seq):
    g="closed" if t=="30" else "good"
    w=signal(c,x,sy,34,g,t);c.setFillColor(MID);c.setFont(F,6.2);c.drawString(x,sy-22,lab);x+=max(w,40)+26
y=sy-40;label(c,LM,y,"RETURNERS — TWO NUMBERS, THE MOST CURRENT PAIR","Left: days since he came back. Right: the gap before that. A third sighting pushes the old gap off.")
ret=[(count_txt(1,40),"back today-ish, gone 40"),(count_txt(5,60),"5 days back, gone 60"),(count_txt(11,30),"worst likely case"),(count_txt(20,100),"never expected — still fits")]
sy=y-70;x=LM+6
for t,lab in ret:
    w=signal(c,x,sy,34,"caution",t);c.setFillColor(MID);c.setFont(F,6.2);c.drawString(x,sy-14,lab);x+=max(w,70)+34
c.setFillColor(GREY);c.setFont(F,7);c.drawString(LM,sy-30,"No returner ever gets the splat — the splat means one thing only: never seen before.")

y=sy-62;label(c,LM,y,"THE DIGIT NO LONGER SHRINKS","Mockup 5 squeezed long counts down to fit the dot. Now the number holds one size and the mark widens under the arcs.")
sy=y-60
signal_B(c,LM+6,sy,34,"caution","0/40");c.setFillColor(MID);c.setFont(F,6.2);c.drawString(LM+6,sy-14,"v5 — squeezed")
signal(c,LM+100,sy,34,"caution","1/40");c.setFillColor(MID);c.drawString(LM+100,sy-14,"v6 — full size")
c.setFillColor(GREY);c.setFont(F,7);c.drawString(LM+220,sy+10,"Same type size as the '06' beside it:");signal(c,LM+360,sy,34,"good","06")

y=sy-44;label(c,LM,y,"ACTUAL SIZE","Every state in one striped strip, as it will print on a roster row.")
sy=y-34;c.setFillColor(STRIPE);c.rect(LM-4,sy-7,W-2*LM+8,19,stroke=0,fill=1);x=LM+4
for g,t in [("good",None),("bad",None),("good","01"),("good","03"),("caution","09"),("good","14"),("closed","30"),("caution","1/40"),("caution","5/60"),("caution","11/30"),("caution","20/100")]:
    w=signal(c,x,sy-4.5,SIG,g,t);x+=w+18
foot(c,1);c.showPage()

# ========== PAGE 2
head(c,"ONE ROSTER  ·  THE NEW COUNT","Your row order: triangle · name · position · team · cluster · Signal. Signal column is fixed, so wide counts just run right.")
ROSTER=[(None,"Jahmyr Gibbs","RB","DET","top",("good","06"),None),
        (None,"De'Von Achane","RB","MIA","bot",("good","11/30"),None),
        ("gold","Garrett Wilson","WR","NYJ","mid",("caution","1/40"),None),
        (None,"Jaxon Smith-Njigba","WR","SEA","mid",("good",None),None),
        ("red","Jaylen Warren","RB","PIT","mid",("caution","01"),"red"),
        (None,"Tony Pollard","RB","TEN","bot",("closed","30"),"gold"),
        (None,"Travis Etienne Jr.","RB","JAX","mid",None,"grey"),
        (None,"Mark Andrews","TE","BAL","top",("bad",None),None)]
def row(c,x,y,tri,nm,pos,tm,tier,sig,cl,namew,sz=7.2,k=1.0):
    if tri: triangle(c,x,y+sz*0.34,tri,6.2*k)
    nx=x+10*k;c.setFillColor(NAVY);c.setFont(FB,sz);c.drawString(nx,y,nm)
    w=nx+namew+6*k;c.setFillColor(GREY);c.setFont(F,sz);c.drawString(w,y,pos);w+=c.stringWidth("WR",F,sz)+4*k
    team(c,w,y,tm,tier,sz);w+=c.stringWidth("WAS",F,sz)+8*k
    if cl: cluster(c,w,y+sz*0.34,SIG*k,cl)
    if sig: signal(c,w+SIG*k+8*k,y-sz*0.62,SIG*k,sig[0],sig[1])
def roster(x0,y0,k,title):
    sz=7.2*k;nw=max(c.stringWidth(r[1],FB,sz) for r in ROSTER);rh=19*k
    c.setFillColor(NAVY);c.setFont(FB,9.5);c.drawString(x0,y0,title)
    for i,r in enumerate(ROSTER):
        ry=y0-22*k-i*rh
        if i%2==0: c.setFillColor(STRIPE);c.rect(x0-4,ry-7*k,nw+150*k,rh,stroke=0,fill=1)
        row(c,x0,ry,*r,namew=nw,sz=sz,k=k)
roster(LM,Ht-100,1.0,"ACTUAL SIZE")
roster(LM,Ht-300,1.6,"1.6×  — for reading the detail")
c.setFillColor(GREY);c.setFont(F,7.2)
notes=["Smith-Njigba and Andrews are brand new — splat only, green and red.",
       "Wilson came back after 40 days away: 1/40. Achane is 11 days back after a 30-day gap: 11/30.",
       "Gibbs 06 and Warren 01 are padded counts — Warren's red triangle no longer sits beside a lone '1'."]
for i,t in enumerate(notes): c.drawString(LM,110-i*11,t)
foot(c,2);c.save()
