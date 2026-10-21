# THE MARKS — the legend, last page of the scan (added Sep 30, Dom: "it travels with the document").
# Every mark at the size it prints on the league pages, every color it takes, what it means, and where it sends.
# Draws with the LIVE helpers (ntri, tight, sig7, trend, tier, _cap) so the legend can never drift from the pages.
from batch7 import arcs7, LOCK
from marklib import INK as SIGINK

def sig_hollow(c,cx,cy,s,g,t):
    """One-origin Signal: same glyph, same place, same solid digits (digits never get harder to read).
    Only the arcs go hollow — a colored outline with paper inside. Nothing moved."""
    k=SIGINK[g];c.saveState();c.setLineCap(1)
    for r in (.40,.60):
        c.setStrokeColor(k);c.setLineWidth(s*.10);c.arc(cx-r*s,cy+s*.08-r*s,cx+r*s,cy+s*.08+r*s,40,100)
        c.setStrokeColor(PAPER);c.setLineWidth(s*.045);c.arc(cx-r*s,cy+s*.08-r*s,cx+r*s,cy+s*.08+r*s,43,94)
    sz=s*LOCK;c.setFillColor(k);c.setFont("Helvetica-Bold",sz);c.drawCentredString(cx,cy-sz*.36,t);c.restoreState()

def amark_leg(x,mid,how,LC_=LG["I"]):
    rh_=4.7;bw=9.8;top_=mid+rh_*1.5
    for i,lab in enumerate(("F","W","T")):
        ry=top_-(i+1)*rh_;on=(lab==how)
        if on:
            c.saveState();c.setFillColor(LC_);c.setFillAlpha(.35);c.rect(x,ry,bw,rh_,stroke=0,fill=1);c.restoreState()
            c.setStrokeColor(INKN);c.setLineWidth(.8);c.setLineCap(1);c.setLineJoin(1)
            p_=c.beginPath();p_.moveTo(x+bw+1.4,ry+2.3);p_.lineTo(x+bw+2.6,ry+1.0);p_.lineTo(x+bw+4.8,ry+3.9);c.drawPath(p_,stroke=1,fill=0)
        txt(c,x+bw/2,ry+1.0,lab,"PopB" if on else "Pop",4.4,INKN if on else GR2,"c")
        if i: c.setStrokeColor(LINE);c.setLineWidth(.3);c.line(x,ry+rh_,x+bw,ry+rh_)
    c.setStrokeColor(GR);c.setLineWidth(.5);c.rect(x,top_-3*rh_,bw,3*rh_,stroke=1,fill=0)

LEG_PAGE=c.getPageNumber()
masthead(c,"THE MARKS","Every mark at print size  ·  every color it takes  ·  what it means  ·  where it sends")
GX=M+8; SX=M+34; MX=M+150; DX=W-M          # glyph · swatch label · meaning · destination (right)
y=Ht-122
def lhd(y,title,sub):
    txt(c,M,y,title,"Bebas",14,INKN);txt(c,M+c.stringWidth(title,"Bebas",14)+8,y+.5,sub,"Pop",6.4,GR)
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,y-5,W-M,y-5)
def lrow_(y,draw,lab,mean,dest,labcol=INKN):
    draw(y+2.6);txt(c,SX,y,lab,"PopB",7,labcol);txt(c,MX,y,mean,"Pop",6.8,INKN);txt(c,DX,y,dest,"PopM",6.2,GR,"r")
RH=17

lhd(y,"TRIANGLE","Points at the man it concerns and travels with him  ·  bare digit = the Call Sheet item");y-=19
for col,lab,mean in (("red","RED","Urgent — look now and act."),("gold","GOLD","Worth doing — monitor, act when the trigger hits."),
                     ("green","GREEN","Confirmed — the move is agreed and dated.")):
    lrow_(y,lambda m,col=col:ntri(c,GX-3,m,col,"1"),lab,mean,"Call Sheet, item by number",TRI[col]);y-=RH
y-=6

lhd(y,"THE SIGNAL","The news mark  ·  color = what the news is  ·  digits = days since first seen");y-=19
for g,lab,mean in (("good","GREEN","Good news — full practice, off the report, back."),("caution","GOLD","Caution — questionable, limited, or a role change."),
                   ("bad","RED","Bad — out, doubtful, or did not practice with an injury."),("closed","GREY","Closed — nothing new; the story has gone quiet.")):
    lrow_(y,lambda m,g=g:sig7(c,GX+2,m-.26*11,11,g,"04"),lab,mean,"League page, The Radar",SIGINK[g]);y-=RH
lrow_(y,lambda m:(sig7(c,GX+2,m-.26*11,11,"caution",None)),"SPLAT","A man never seen before — first day on the Radar.","League page, The Radar");y-=RH
lrow_(y,lambda m:sig7(c,GX+2,m-.26*11,11,"caution","1/40"),"1/40","A returner: 1 day back, after a 40-day gap.","League page, The Radar");y-=RH+2
# filled vs hollow — the two-source rule, side by side
lrow_(y,lambda m:sig7(c,GX+2,m-.26*11,11,"bad","02"),"FILLED","Two independent origins confirm it — the rule fired and the number moved.","Reason line under the number",SIGINK["bad"]);y-=RH
lrow_(y,lambda m:sig_hollow(c,GX+2,m-.26*11,11,"bad","02"),"HOLLOW","One origin only — arcs hollow, digits solid. No number moves until a second confirms.","Reason line under the number",SIGINK["bad"]);y-=RH
note(c,SX,y+3,"Origin","the reporter or document a story traces to, not the outlet. Five outlets repeating one beat writer is one origin.",6.2);y-=RH
y-=2

lhd(y,"DISPOSABLE CLUSTER","The man who goes when a pickup needs room  ·  usually one per roster");y-=19
for col,lab,mean in (("red","RED","First out."),("gold","GOLD","Next in line."),("grey","GREY","Marked — nothing urgent.")):
    lrow_(y,lambda m,col=col:tight(c,GX,m,MK_S,col,True),lab,mean,"Field Report, the cut order",CL[col]);y-=RH
y-=6

lhd(y,"TREND","Direction of usage, opportunity and production  ·  flat = no mark");y-=19
lrow_(y,lambda m:trend(c,GX+2,m,MK_S*.95,1),"CLIMBING","Usage rising.","Positions page",ST["green"]);y-=RH
lrow_(y,lambda m:trend(c,GX+2,m,MK_S*.95,-1),"FALLING","Usage falling.","Positions page",ST["red"]);y-=RH+6

lhd(y,"SCHEDULE CAPSULE","Left half = rest of season  ·  right half = fantasy playoffs, Weeks 15–17");y-=19
lrow_(y,lambda m:_cap(GX-4,m,"green","red"),"GREEN / RED","Soft schedule the rest of the way, hard in the playoffs.","Positions page");y-=RH
lrow_(y,lambda m:_cap(GX-4,m,"gold","green"),"GOLD / GREEN","Average rest of season, soft in the playoffs.","Positions page");y-=RH+6

lhd(y,"ACQUISITION MARKER","Inbound men only  ·  the three ways onto a roster, easiest to hardest");y-=19
for how,lab,mean in (("F","FREE AGENT","Available now — no claim, no wait."),("W","WAIVER WIRE","Needs a claim — processes on the league's waiver run."),
                     ("T","TRADE","Only by trade — enters only when Dom raises him.")):
    lrow_(y,lambda m,how=how:amark_leg(GX-4,m,how),lab,mean,"The Radar, Positions page");y-=RH+1
y-=5

lhd(y,"TEAM TIER","Hairline on the NFL abbreviation  ·  ranked across all 32 teams by points scored");y-=19
lrow_(y,lambda m:tier(c,GX-4,m-2.6,"KC",7.4),"RULE ABOVE","Top third of the league.","Everywhere a team prints",ST["green"]);y-=RH
lrow_(y,lambda m:tier(c,GX-4,m-2.6,"PIT",7.4),"RULE BELOW","Bottom third — the whole bad-team warning.","Everywhere a team prints",ST["red"]);y-=RH
lrow_(y,lambda m:tier(c,GX-4,m-2.6,"WAS",7.4),"CLEAN","Middle third.","Everywhere a team prints");y-=RH+6

lhd(y,"REASON LINE","Prints under any number the news rules touched — or chose not to touch");y-=17
for s_ in ("HELD: Did not practice, no designation — no cut, mark only. One origin only (Tashan Reed); this week unchanged at 10.3 until a",
           "second origin confirms. Rest of season untouched. Week number from 2 of 4 sources (Yahoo, Rotowire; CBS and ESPN week not gathered)."):
    txt(c,SX,y,s_,"Pop",6.2,GR);y-=8.4
txt(c,SX,y-1,"Sample: Rachaad White, DK III, as the news layer printed it Wednesday. A rule that fires and changes nothing still says so.","PopM",5.8,GR2)
print("legend lowest y",y)
footer(c,LEG_PAGE,"The Marks · legend")
c.showPage()
