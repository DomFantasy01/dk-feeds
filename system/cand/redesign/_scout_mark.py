# THE SCOUT MARKER (Oct 9 2026) — a drawn icon, not a typed glyph. Three candidates for Dom to pick from:
#   "spyglass"   a lookout's telescope, angled up-right toward the horizon
#   "binoculars" two barrels on a bridge
#   "compass"    a compass rose with the needle pointing ahead
# Color follows the Radar's law exactly: red = requires action, gold = monitor, green = good / confirmed, grey = gone quiet.
# The icon is drawn from its CENTER (cx, cy) at height s, so it can trail a name on the Scout page or sit beside a dot
# on the Positions scatter chart. Outline in the page's ink keeps it readable at phone scale.
from reportlab.lib.colors import Color as _SMC
SCOUT_MARK_STYLE="spyglass"                     # Dom picked the spyglass ("the flashlight"), Oct 9
_SM_K={"red":"#B32020","gold":"#C8860D","green":"#1E7A3C","grey":"#8B93A1"}   # the Radar's exact inks (marklib INK: bad, caution, good, closed)
def _smh(hx): hx=hx.lstrip("#"); return _SMC(int(hx[0:2],16)/255,int(hx[2:4],16)/255,int(hx[4:6],16)/255)
def _sm_dark(k,f=.62): return _SMC(k.red*f,k.green*f,k.blue*f)
def _sm_light(k,a=.55): return _SMC(1-(1-k.red)*a,1-(1-k.green)*a,1-(1-k.blue)*a)
SCOUT_ANGLE=62                                  # Oct 9 (Dom): stood up straighter so the mark stays on one line
def scout_icon(c,cx,cy,state="red",s=10,style=None,angle=None):
    style=style or SCOUT_MARK_STYLE; k=_smh(_SM_K.get(state,_SM_K["grey"])); dk=_sm_dark(k); lt=_sm_light(k)
    c.saveState(); c.setLineJoin(1); c.setLineCap(1)
    if style=="spyglass":
        import math
        c.translate(cx,cy); c.rotate(SCOUT_ANGLE if angle is None else angle)
        L=s*1.25; h0=s*.30; h1=s*.44                       # tube tapers from eyepiece (left) to objective (right)
        segs=[(-L/2,-L/2+L*.30,h0*.82),(-L/2+L*.30,-L/2+L*.62,h0),(-L/2+L*.62,L/2,h1)]
        for i,(x0,x1,hh) in enumerate(segs):
            c.setFillColor(k if i!=1 else dk); c.setStrokeColor(dk); c.setLineWidth(max(.35,s*.05))
            c.rect(x0,-hh/2,x1-x0,hh,stroke=1,fill=1)
        c.setFillColor(lt); c.rect(-L/2+L*.62,h1*.06,L*.38,h1*.16,stroke=0,fill=1)          # glint along the barrel
        c.setFillColor(_smh("#FFFFFF")); c.setStrokeColor(dk); c.setLineWidth(max(.35,s*.05))
        c.ellipse(L/2-s*.07,-h1*.62,L/2+s*.09,h1*.62,stroke=1,fill=1)                     # the lens
        c.setFillColor(_sm_light(k,.35)); c.ellipse(L/2-s*.03,-h1*.40,L/2+s*.06,h1*.40,stroke=0,fill=1)
    elif style=="binoculars":
        r=s*.27; gap=s*.08
        for dx in (-(r+gap/2),(r+gap/2)):
            c.setFillColor(k); c.setStrokeColor(dk); c.setLineWidth(max(.35,s*.05))
            c.roundRect(cx+dx-r*.82,cy-s*.08,r*1.64,s*.46,r*.35,stroke=1,fill=1)          # barrel
            c.circle(cx+dx,cy-s*.16,r,stroke=1,fill=1)                                   # objective housing
            c.setFillColor(_smh("#FFFFFF")); c.circle(cx+dx,cy-s*.16,r*.58,stroke=0,fill=1)
            c.setFillColor(_sm_light(k,.35)); c.circle(cx+dx-r*.15,cy-s*.10,r*.24,stroke=0,fill=1)
        c.setFillColor(dk); c.rect(cx-gap/2-s*.04,cy+s*.10,gap+s*.08,s*.14,stroke=0,fill=1)  # bridge
    else:  # compass
        import math
        R=s*.48; c.setFillColor(_smh("#FFFFFF")); c.setStrokeColor(k); c.setLineWidth(max(.5,s*.10)); c.circle(cx,cy,R,stroke=1,fill=1)
        c.setStrokeColor(dk); c.setLineWidth(max(.3,s*.04))
        for a in range(0,360,45):
            t=math.radians(a); r0=R*.72 if a%90 else R*.62
            c.line(cx+r0*math.cos(t),cy+r0*math.sin(t),cx+R*.9*math.cos(t),cy+R*.9*math.sin(t))
        p=c.beginPath(); p.moveTo(cx+R*.82,cy); p.lineTo(cx,cy+R*.22); p.lineTo(cx-R*.30,cy); p.lineTo(cx,cy-R*.22); p.close()
        c.setFillColor(k); c.setStrokeColor(dk); c.setLineWidth(max(.3,s*.04)); c.drawPath(p,stroke=1,fill=1)
        c.setFillColor(dk); c.circle(cx,cy,R*.09,stroke=0,fill=1)
    c.restoreState()
def scout_icon_w(s=10,style=None):
    style=style or SCOUT_MARK_STYLE
    import math
    if style=="spyglass": a=math.radians(SCOUT_ANGLE); return s*1.25*math.cos(a)+s*.44*math.sin(a)
    return {"binoculars":s*1.2,"compass":s*1.0}[style]

# THE RADAR'S LIFE CYCLE on the spyglass (Dom, Oct 9): splat the first day it appears, then a zero-padded day count
# centered underneath (01, 02 ...), one locked digit size, same ink as the glass. Grey when it has gone quiet.
def _sm_splat(c,cx,cy,s,k):
    import math
    c.setFillColor(k);p=c.beginPath()
    R=[.27,.20,.24,.18,.29,.21,.23,.17,.26,.20,.28,.18,.22,.19,.25,.21]
    for i in range(16):
        a=2*math.pi*i/16;r=s*R[i];px,py=cx+r*math.cos(a),cy+r*math.sin(a)
        p.moveTo(px,py) if i==0 else p.lineTo(px,py)
    p.close();c.drawPath(p,stroke=0,fill=1)
    for a,d,r in [(.2,.38,.05),(2.5,.37,.042),(4.1,.39,.045)]:
        c.circle(cx+s*d*math.cos(a),cy+s*d*math.sin(a),s*r,stroke=0,fill=1)
def scout_mark(c,cx,cy,state,age,s=9):
    """spyglass centered at (cx,cy); age 0/None = splat under it, else the day count under it"""
    scout_icon(c,cx,cy,state,s)
    k=_smh(_SM_K.get(state,_SM_K["grey"]));c.saveState()
    if not age: _sm_splat(c,cx,cy-s*.80,s*.85,k)
    else:
        sz=s*.50;c.setFillColor(k);c.setFont("Helvetica-Bold",sz);c.drawCentredString(cx,cy-s*.78-sz*.36,f"{age:02d}")
    c.restoreState()

def scout_mark_inline(c,x,ymid,state,age,gap=None,s=8):
    """Oct 9 v2 (Dom): the whole mark on ONE line. Spyglass stood up, then — tight beside it, not under it — the splat
    (first day) or the zero-padded day count; a returner prints its fresh count over the days it was gone (01/04),
    never the splat. Same rule as the Signal. Returns the width used."""
    iw=scout_icon_w(s); scout_icon(c,x+iw/2,ymid+s*.05,state,s)
    k=_smh(_SM_K.get(state,_SM_K["grey"])); x2=x+iw+1.6; c.saveState()
    if gap is None and not age:
        r=s*1.15; _sm_splat(c,x2+r*.30,ymid,r,k); w=iw+1.6+r*.62
    else:
        t=f"{max(age,1):02d}/{gap}" if gap is not None else f"{age:02d}"
        sz=5.6; c.setFillColor(k); c.setFont("Helvetica-Bold",sz); c.drawString(x2,ymid-sz*.36,t); w=iw+1.6+c.stringWidth(t,"Helvetica-Bold",sz)
    c.restoreState(); return w
