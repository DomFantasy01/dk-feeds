"""The Dispatch masthead for the front page (Oct 8 2026): the same banner every other Dispatch page carries
(_masthead_puzzle + _masthead_field, title DARK KNIGHT DISPATCH per Dom Oct 5), drawn in its own namespace so its
helper names never collide with the mountains page. Call draw(c, section, sub) FIRST - it paints the paper background."""
from reportlab.lib.colors import HexColor as H, Color
from reportlab.lib.pagesizes import letter
_NS={"H":H,"Color":Color}
_NS.update(W=letter[0],Ht=letter[1],M=30)
_NS.update(INKN=H("#14213D"),PAPER=H("#FBF7EF"),GR=H("#7A7F8C"),
           SUN=[H("#F26B38"),H("#F7B32B"),H("#2EC4B6"),H("#E84A7F")],
           LG={"I":H("#2F80ED"),"II":H("#F2711C"),"III":H("#12A150"),"IV":H("#2EC4B6")})
def _txt(c,x,y,s,font="Pop",sz=8,col=_NS["INKN"],align="l"):
    c.setFont(font,sz);c.setFillColor(col);{"l":c.drawString,"c":c.drawCentredString,"r":c.drawRightString}[align](x,y,s)
_NS["txt"]=_txt
exec("import re, math, sys, json, datetime\nfrom reportlab.lib.colors import white, black",_NS)
for _f in ("/home/claude/cand/redesign/_masthead_puzzle.py","/home/claude/cand/redesign/_masthead_field.py"):
    exec(compile(open(_f).read(),_f,"exec"),_NS)
_NS["PZ_TITLE"]="DARK KNIGHT DISPATCH"
def draw(c,section,sub): _NS["masthead"](c,section,sub)

# v33c (Dom, Oct 8 2:11 PM): the banner sits INSIDE the page margins, lined up with the league strip and blocks below
# (was edge to edge). Same band, same title, same puzzle tabs - only the band, the gold rule and the text move in.
def _inset_masthead(c,section,sub):
    N=_NS; W,Ht,M,MH=N["W"],N["Ht"],N["M"],N["MH"]; PAPER,INKN,SUN=N["PAPER"],N["INKN"],N["SUN"]; txt=N["txt"]; P=12
    c.setFillColor(PAPER); c.rect(0,0,W,Ht,stroke=0,fill=1)
    top=Ht-8; bot=top-MH+8
    c.setFillColor(INKN); c.roundRect(M,bot,W-2*M,top-bot,5,stroke=0,fill=1)
    txt(c,M+P,Ht-44,N["PZ_TITLE"],"Bebas",34,PAPER)
    if "dk_icon" not in N: exec(open("/home/claude/cand/redesign/_dkicon.py").read(),N)
    N["dk_icon"](c,M+P+c.stringWidth(N["PZ_TITLE"],"Bebas",34)+9,Ht-47,29)   # Oct 11 (Dom): the icon after the title
    c.setFillColor(SUN[1]); c.rect(M+P,Ht-56,c.stringWidth(section,"Bebas",15),1.6,stroke=0,fill=1)   # Oct 10: spans the section name
    txt(c,M+P,Ht-72,section,"Bebas",15,SUN[1])
    if "asof_line" not in N: exec(open("/home/claude/cand/redesign/_asof.py").read(),N)
    N["asof_line"](c,M+P+c.stringWidth(section,"Bebas",15)+10,Ht-71.5,sub,W-M-9-108-(M+4)-12)   # Oct 11: stops short of the puzzle where it really sits   # Oct 10: As of + stoplight
    i=N["_pz_idx"](section); lg=N["_pz_league"](section); col=N["LG"][lg] if lg else SUN[1]
    c.saveState(); p=c.beginPath(); p.roundRect(M,bot,W-2*M,top-bot,5); c.clipPath(p,stroke=0)
    c.translate(-(M+4),-4); N["puzzle"](c,i,col); c.restoreState()     # tabs pulled in from the right edge with the band
    c.setFillColor(SUN[1]); c.rect(M,bot-3,W-2*M,2.2,stroke=0,fill=1)   # gold rule, margin to margin
def draw(c,section,sub): _inset_masthead(c,section,sub)
def draw(c,section,sub):   # Oct 12 (Dom): the v8 masthead, the same on every page
    if "_v8" not in _NS: exec(open("/home/claude/cand/redesign/_mast_v8.py").read(),_NS); _NS["_v8"]=_NS["masthead"]
    _NS["_v8"](c,section,sub)

# OCT10 front masthead

# OCT10b front asof

# OCT11 icon front

# OCT11 front asof room

# OCT12 front v8 masthead
