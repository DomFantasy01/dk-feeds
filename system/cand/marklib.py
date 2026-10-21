from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor as H
NAVY=H("#1A2740");GREY=H("#6B7280");MID=H("#8B93A1");PAPER=H("#FFFFFF");STRIPE=H("#F4F6F9");RULE=H("#D4D8E0")
INK={"good":H("#1E7A3C"),"caution":H("#C8860D"),"bad":H("#B32020"),"closed":H("#8B93A1")}
GREEN=INK["good"];RED=INK["bad"]
FB="Helvetica-Bold";F="Helvetica"

def arcs(c,cx,cy,s,k,radii=(0.40,0.66)):
    c.setStrokeColor(k);c.setLineCap(1)
    for r in radii:
        c.setLineWidth(s*0.11);c.arc(cx-r*s,cy-r*s,cx+r*s,cy+r*s,40,100)

def ring(c,cx,cy,rad,k):
    c.setStrokeColor(k);c.setLineWidth(max(0.6,rad*0.10));c.circle(cx,cy,rad,stroke=1,fill=0)

def fit(c,txt,font,maxw,maxsz):
    sz=maxsz
    while c.stringWidth(txt,font,sz)>maxw and sz>2: sz-=0.1
    return sz

# A: count rides inside the bowl of the arcs, dot kept
def signal_A(c,x,y,s,g,age,ring_on=False):
    k=INK[g];c.saveState();cx,cy=x+s*0.5,y+s*0.08
    c.setFillColor(k);c.circle(cx,cy,s*0.08,stroke=0,fill=1)
    arcs(c,cx,cy,s,k,(0.62,0.88))
    sz=fit(c,age,FB,s*0.70,s*0.36);c.setFont(FB,sz);c.drawCentredString(cx,cy+s*0.17,age)
    if ring_on: ring(c,cx,cy+s*0.42,s*0.66,k)
    c.restoreState()

# B: the count IS the dot — the signal radiates from the number
def signal_B(c,x,y,s,g,age,ring_on=False):
    k=INK[g];c.saveState();cx,cy=x+s*0.5,y+s*0.14
    sz=fit(c,age,FB,s*0.80,s*0.42);c.setFillColor(k);c.setFont(FB,sz)
    c.drawCentredString(cx,cy-sz*0.34,age)
    arcs(c,cx,cy,s,k,(0.46,0.72))
    if ring_on: ring(c,cx,cy+s*0.30,s*0.70,k)
    c.restoreState()

# C: postmark — mark on top, count set as a baseline underneath
def signal_C(c,x,y,s,g,age,ring_on=False):
    k=INK[g];c.saveState();cx,cy=x+s*0.5,y+s*0.40
    c.setFillColor(k);c.circle(cx,cy,s*0.08,stroke=0,fill=1)
    arcs(c,cx,cy,s,k,(0.30,0.52))
    sz=fit(c,age,FB,s*0.90,s*0.34);c.setFont(FB,sz);c.drawCentredString(cx,y+s*0.02,age)
    if ring_on: ring(c,cx,cy,s*0.72,k)
    c.restoreState()

def team(c,x,y,abbr,tier,sz=7.2):
    c.setFillColor(GREY);c.setFont(F,sz);c.drawString(x,y,abbr);w=c.stringWidth(abbr,F,sz)
    c.setLineWidth(max(1.3,sz*0.08))
    if tier=="top": c.setStrokeColor(GREEN);c.line(x,y+sz*0.92,x+w,y+sz*0.92)
    if tier=="bot": c.setStrokeColor(RED);c.line(x,y-sz*0.32,x+w,y-sz*0.32)
    return w

