"""Candidate redesign v6 (rebuilt from p12v5.py; v6 = Dom's live review batch: smaller digits, one MARKER column, bare-letter STA, TREND mark, Field Report column set). Was: v5 — Global Watch, The Call Sheet, and a first-pass DK I Field Report. Week 3 data from v36d.
Rebuilt from p12v4.py. v5 batch: bare digits (no letters), one triangle size, one digit size,
banded bye weeks, document name in the running header with the page name set apart. v36d untouched."""
import sys, math, re, csv; sys.path.insert(0,'/home/claude/cand')
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor as H, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from batch7 import sig7, tight     # the locked Signal glyph; the tight three-bubble Drift cluster
    from batch5 import CL
pdfmetrics.registerFont(TTFont("Bebas","/home/claude/cand/fonts/BebasNeue-Regular.ttf"))
GF="/usr/share/fonts/truetype/google-fonts/"
for n,f in (("Pop","Poppins-Regular"),("PopM","Poppins-Medium"),("PopB","Poppins-Bold"),("PopL","Poppins-Light")):
    pdfmetrics.registerFont(TTFont(n,GF+f+".ttf"))
W,Ht=letter; M=34
INKN=H("#14213D"); PAPER=H("#FBF7EF"); CARD=H("#FFFFFF"); SOFT=H("#EFE9DD"); LINE=H("#DDD5C5"); GR=H("#7A7F8C"); GR2=H("#A9ADB6")
SUN=[H("#F26B38"),H("#F7B32B"),H("#2EC4B6"),H("#E84A7F")]
LG={"I":H("#2F80ED"),"II":H("#F2711C"),"III":H("#12A150"),"IV":H("#2EC4B6")}     # DK IV now teal
ST={"green":H("#1E9E4A"),"gold":H("#E0A21B"),"red":H("#D63A2F")}
TRI={"gold":H("#E0A21B"),"red":H("#D63A2F"),"green":H("#1E9E4A")}
NEUTRAL=H("#5C677D")                                   # every action-type pill: one color
TOP={"BUF","CAR","KC","SF","DET","CHI","BAL","DAL","NO","LV","IND"}
BOT={"LA","NYG","ATL","CLE","ARI","TEN","NE","DEN","LAC","MIA","PIT"}
def alpha(k,a): return Color(k.red,k.green,k.blue,alpha=a)
def txt(c,x,y,s,font="Pop",sz=8,col=INKN,align="l"):
    c.setFont(font,sz);c.setFillColor(col)
    {"l":c.drawString,"c":c.drawCentredString,"r":c.drawRightString}[align](x,y,s)
def tier(c,x,y,ab,sz=7.5,col=GR):
    txt(c,x,y,ab,"PopM",sz,col);w=c.stringWidth(ab,"PopM",sz);c.setLineWidth(max(.5,sz*.07))
    # Dom Fri Oct 2: the line lives UNDER the abbreviation only, never over it - green strong, red weak, none middle
    if ab in TOP: c.setStrokeColor(ST["green"]);c.line(x,y-sz*.28,x+w,y-sz*.28)
    if ab in BOT: c.setStrokeColor(ST["red"]);c.line(x,y-sz*.28,x+w,y-sz*.28)
    return w

TRI_H=14; TRI_D=7.0          # ONE triangle size and ONE digit size, on every page, in every section
def ntri(c,x,ym,col,num,h=None):
    """The call-sheet triangle: points right at the player. Bare digit only — a multi-man item shares one number."""
    h=TRI_H
    c.setFillColor(TRI[col]);p=c.beginPath();p.moveTo(x,ym-h/2);p.lineTo(x+h*.95,ym);p.lineTo(x,ym+h/2);p.close()
    c.drawPath(p,stroke=0,fill=1)
    ink=INKN if col=="gold" else PAPER
    cap=TRI_D*.70
    txt(c,x+h*.33,ym-cap/2,num,"PopB",TRI_D,ink,"c")

def pill(c,x,y,s,bg,fg=PAPER,sz=6.4,font="PopB",pad=4.5,align="l"):
    w=c.stringWidth(s,font,sz)+2*pad;h=sz+5
    if align=="r": x-=w
    c.setFillColor(bg);c.roundRect(x,y-3,w,h,h/2,stroke=0,fill=1);txt(c,x+pad,y-.3,s,font,sz,fg);return w
def horizon(c,x,y,s,src=None,align="l",gap=8):
    w=pill(c,x,y,s,INKN,PAPER,5.8,"PopB",4,align)
    if src: txt(c,(x+w+gap) if align=="l" else x-w-gap,y-.2,src,"PopM",6,GR,"l" if align=="l" else "r")
    return w
def masthead(c,section,sub):
    c.setFillColor(PAPER);c.rect(0,0,W,Ht,stroke=0,fill=1)
    c.setFillColor(INKN);c.rect(0,Ht-92,W,92,stroke=0,fill=1)
    # the four league colors, running off the right edge — a key to every chip below
    for i,k in enumerate(("I","II","III","IV")):
        c.setFillColor(LG[k]);p=c.beginPath();x0=W-190+i*22
        p.moveTo(x0,Ht-92);p.lineTo(x0+14,Ht-92);p.lineTo(x0+14+60,Ht);p.lineTo(x0+60,Ht);p.close();c.drawPath(p,stroke=0,fill=1)
    txt(c,M,Ht-44,"DARK KNIGHT FANTASY FOOTBALL","Bebas",34,PAPER)          # the DOCUMENT — same on every page
    c.setFillColor(SUN[1]);c.rect(M,Ht-56,30,1.6,stroke=0,fill=1)          # short gold rule sets the page name apart
    txt(c,M,Ht-74,section,"Bebas",15,SUN[1])                               # the PAGE — smaller, its own line
    txt(c,M+c.stringWidth(section,"Bebas",15)+10,Ht-73.5,sub,"Pop",7.2,H("#C9CFDB"))
    c.setFillColor(SUN[0]);c.rect(0,Ht-95,W,3,stroke=0,fill=1)
def footer(c,n,label):
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,20,W-M,20)
    txt(c,M,11,"DARK KNIGHT FANTASY FOOTBALL","PopB",6.4,INKN)
    txt(c,M+c.stringWidth("DARK KNIGHT FANTASY FOOTBALL","PopB",6.4)+8,11,"Week 3  ·  Design sample on Week 3 finals — the Week 4 scan follows Tuesday","Pop",5.8,GR)
    txt(c,W-M,11,f"{label}  ·  page {n}","Pop",5.8,GR,"r")
def note(c,x,y,label,s,sz=6.8):
    """flat grey note: the slanted-page glyph, a label, a colon, then the text. No color."""
    c.saveState();c.setStrokeColor(GR2);c.setLineWidth(.7);c.translate(x,y-1);c.rotate(12)
    c.rect(0,0,5.2,6.6,stroke=1,fill=0)
    for yy in (1.8,3.3,4.8): c.line(1.1,yy,4.1,yy)
    c.restoreState();lab=label+":";txt(c,x+10,y,lab,"PopB",sz,GR)
    txt(c,x+10+c.stringWidth(lab,"PopB",sz)+3,y,s,"Pop",sz,GR)
def hdr(c,x,y,s,align="l"): txt(c,x,y,s,"PopB",5.4,GR,align)      # ALL-CAPS column furniture
def dec(c,xd,y,v,font="PopB",sz=7,col=INKN,usz=5.4,unit="pts"):
    """every number sits on its decimal point at xd; the unit rides after it; missing = light dash, never zeros"""
    if v in (None,"","—"):
        txt(c,xd,y,"—",font,sz,GR2,"c");return
    v=str(v);a,b=(v.split(".")+[""])[:2]
    txt(c,xd,y,a,font,sz,col,"r");bb="."+b if b else ""
    txt(c,xd,y,bb,font,sz,col);ex=xd+c.stringWidth(bb,font,sz)+1.6
    if unit: txt(c,ex,y,unit,"Pop",usz,GR)

# ------------------------------------------------------------------ THE ONE PLAYER ROW (every page, every appearance)
# triangle · name · status · position · team(tier) · cluster(Drift) · Signal
SLET={"Q":"Q","O":"O","D":"D","IR":"IR","IR-R":"IR","I":"IR"}   # bare letter, plain ink, no highlight; healthy = blank
# ---- TREND: the third mark. Usage/opportunity/production direction. Green climbing, red falling, flat = no mark.
TREND={"Tyler Shough":-1,"Travis Etienne Jr.":-1,"George Pickens":1,"Travis Kelce":1,"Christian McCaffrey":-1,
       "TreVeyon Henderson":1,"Stefon Diggs":-1,"Kaelon Black":-1,"Dontayvion Wicks":1,
       "Jacoby Brissett":-1,"David Montgomery":-1,"Ja'Marr Chase":1,"De'Von Achane":1,"Sam Darnold":-1,"Jameis Winston":1,
       "MarShawn Lloyd":-1,"Alvin Kamara":1,"Jaylen Waddle":1,"Harold Fannin Jr.":1,"Josh Downs":1,"Devaughn Vele":-1,
       "Rachaad White":1,"Michael Pittman Jr.":-1,"Bijan Robinson":-1,"Justin Jefferson":-1,"Tucker Kraft":-1,
       "Zay Flowers":-1,"C.J. Stroud":1,"Terry McLaurin":1,"RJ Harvey":-1}      # Weeks 1-2 usage
def trend(c,cx,cy,s,d):
    """A sparkline that breaks out: dot, jag, run, chevron. Same stroke family as the Radar arcs."""
    k=ST["green"] if d>0 else ST["red"];f=1 if d>0 else -1
    pts=[(-.44,-.24),(-.14,.04),(.04,-.10),(.38,.24)]
    P=[(cx+s*x,cy+s*y*f) for x,y in pts]
    c.saveState();c.setStrokeColor(k);c.setFillColor(k);c.setLineCap(1);c.setLineJoin(1);c.setLineWidth(s*.12)
    p=c.beginPath();p.moveTo(*P[0])
    for q in P[1:]: p.lineTo(*q)
    c.drawPath(p,stroke=1,fill=0)
    ex,ey=P[-1];h=s*.26                                  # open chevron riding the end of the line
    c.line(ex-h,ey,ex,ey);c.line(ex,ey,ex,ey-h*f)
    c.circle(P[0][0],P[0][1],s*.075,stroke=0,fill=1)
    c.restoreState()
MK_S=12; MK_P=17            # marker glyph size, and the pitch between marks — column holds two today
DMK={}                      # v10 (Oct 6): name -> True (role rising) / False (fading) for men the workload engine's DRIFT moved (engine3 drift=D)
DREPLACE=True               # v10: when D prints, it stands in for the trend mark - both say playing time moved; D says the engine acted on it
def dmark(c,cx,cy,s,up):
    """D MARK (Dom Oct 6): drift changed his workload number. Stem + bowl, trend-mark stroke weight, light tint. Green rising, red fading."""
    k=ST["green"] if up else ST["red"]; h=s*.62; w=s*.50; x0=cx-w*.45; yb=cy-h/2; yt=cy+h/2
    c.saveState(); c.setStrokeColor(k); c.setLineWidth(s*.12); c.setLineCap(1); c.setLineJoin(1)
    p=c.beginPath(); p.moveTo(x0,yb); p.lineTo(x0,yt); p.lineTo(x0+w*.35,yt)
    p.curveTo(x0+w*1.08,yt, x0+w*1.08,yb, x0+w*.35,yb); p.close()
    c.drawPath(p,stroke=1,fill=0); c.setFillColor(Color(k.red,k.green,k.blue,alpha=.16)); c.drawPath(p,stroke=0,fill=1)
    c.restoreState()
def markers(c,x,mid,cl=None,sg=None,tr=None,dm=None):
    """ONE MARKER column. Order is fixed: cluster, Radar signal, D, then Trend (D replaces Trend when DREPLACE)."""
    i=0
    if dm is not None and DREPLACE: tr=None
    if cl: tight(c,x+i*MK_P,mid,MK_S,cl,True);i+=1
    if sg: sig7(c,x+i*MK_P,mid-.26*11,11,sg[0],sg[1]);i+=1
    if dm is not None: dmark(c,x+i*MK_P,mid,MK_S,dm);i+=1
    if tr: trend(c,x+i*MK_P,mid,MK_S*.95,tr);i+=1
def prow(c,cols,y,nm,stt,pos,tm,cl=None,sg=None,tri=None,sz=7.4,sig=12,tri_h=13):
    tx,cn,cs,cp,ct,ccl,csg=cols                          # csg retired: the MARKER column starts at ccl
    mid=y+sz*.36
    if tri: ntri(c,tx,mid,*tri)
    if nm is None:                                        # an empty slot still prints: a dash across the row
        txt(c,cn,y,"—","PopB",sz,GR2);return
    txt(c,cn,y,nm,"PopB",sz)
    if stt: txt(c,cs,y,SLET[stt],"PopM",sz,INKN)
    txt(c,cp,y,pos,"Pop",sz,GR);tier(c,ct,y,tm,sz)
    markers(c,ccl,mid,cl,sg,TREND.get(nm),DMK.get(nm))
def rowhead(c,cols,y,drift=True):
    tx,cn,cs,cp,ct,ccl,csg=cols
    hdr(c,cn,y,"PLAYER");hdr(c,cs,y,"STA");hdr(c,cp,y,"POS");hdr(c,ct,y,"TEAM")
    hdr(c,ccl-6,y,"MARKER")

# ------------------------------------------------------------------ DATA (Week 3, from v36d)
L=[dict(k="I",team="TheMostImportantThingInLife",win=91,last=74,me=176,opp=135,oppn="Kraft Beer & TDs",oppr="0-2 · 10th",
        rec="0–2",place=11,of=12,line="Out — 1 game back of 6th",pts="232 pts · 11th of 12",
        st="gold",verdict="Warren questionable. Monangai starts if he's inactive.",when="Inactives Sun 8:30 AM"),
   dict(k="II",team="Winners and Sinners",win=85,last=68,me=190,opp=160,oppn="Rated PG-18",oppr="0-2 · 10th",
        rec="1–1",place=8,of=12,line="Out — level with 6th on record",pts="260 pts · 11th of 12",
        st="green",verdict="Lineup set: Kelce back at TE, Brissett at QB.",when="Nothing to do"),
   dict(k="III",team="Hers and His Version 2.0",win=50,last=50,me=131,opp=131,oppn="Dawg Pound Eric",oppr="1-1 · 9th",
        rec="0–2",place=13,of=14,line="Out — 1 game back of 6th",pts="236 pts · 10th of 14",
        st="green",verdict="Dead level. Nothing on the wire moves it.",when="Nothing to do"),
   dict(k="IV",team="Murrieta NextDoor",win=78,last=65,me=179,opp=156,oppn="Bad and Boujee",oppr="1-3 · 9th",
        rec="2–2",place=5,of=10,line="In — 1 game clear of 7th",pts="348 pts · 3rd of 10",
        st="gold",verdict="Robinson claim held by you. Re-test Sunday.",when="Sun 8:30 AM re-test")]
LIVE={'I': {'pct': 100, 'me': 185.9, 'opp': 135.98, 'ml': 0, 'ol': 0, 'mw': [], 'ow': []}, 'II': {'pct': 100, 'me': 182.46, 'opp': 167.34, 'ml': 0, 'ol': 0, 'mw': [], 'ow': []}, 'III': {'pct': 95, 'me': 126.6, 'opp': 102.55, 'ml': 0, 'ol': 1, 'mw': [], 'ow': ['Colston Loveland']}, 'IV': {'pct': 68, 'me': 139.9, 'opp': 118.22, 'ml': 1, 'ol': 3, 'mw': ["D'Andre Swift"], 'ow': ['Saquon Barkley', 'Luther Burden III', 'Dallas Goedert']}}   # Dark Knight Live, Yahoo read 2026-09-28T04:25Z (Sun 9:25 PM PT)
LIVE_AT="Sun 9:25 PM"
def _last_(n):
    w_=n.split();return w_[-2] if w_[-1].rstrip(".") in ("Jr","Sr","II","III","IV") else w_[-1]
for d in L:
    v=LIVE[d["k"]];d["pre"]=d["win"];d["win"]=int(round(v["pct"]));d["last"]=d["pre"]
    d["me"]=v["me"];d["opp"]=v["opp"];d["final"]=v["ml"]==0 and v["ol"]==0;g_=v["me"]-v["opp"]
    if d["final"]:
        d["st"]="green" if g_>0 else "red";d["verdict"]=f"{'Won' if g_>0 else 'Lost'} {v['me']:.1f} to {v['opp']:.1f}.";d["when"]="Final"
    else:
        w_=[_last_(n)+" (DK "+d["k"]+")" for n in v["mw"]]+[_last_(n) for n in v["ow"]]
        d["st"]="gold";d["verdict"]=f"Up {g_:.1f} with Monday night to play." if g_>0 else f"Down {-g_:.1f} with Monday night to play."
        d["when"]="Still to play: "+", ".join(w_)
STW={"green":"COMPLETE","gold":"MONITOR","red":"ACTION"}
STB={"green":INKN,"gold":ST["gold"],"red":ST["red"]}

def gauge(c,cx,cy,r,v,last,col,final=False,won=True):
    c.setLineCap(0)
    c.setStrokeColor(SOFT);c.setLineWidth(r*.26);c.arc(cx-r,cy-r,cx+r,cy+r,0,180)
    c.setStrokeColor(col);c.arc(cx-r,cy-r,cx+r,cy+r,180-180*v/100,180*v/100)
    for t in range(0,101,25):
        a=math.radians(180-1.8*t);c.setStrokeColor(PAPER if t not in (0,100) else SOFT);c.setLineWidth(1.2)
        c.line(cx+(r-r*.13)*math.cos(a),cy+(r-r*.13)*math.sin(a),cx+(r+r*.13)*math.cos(a),cy+(r+r*.13)*math.sin(a))
    a=math.radians(180-1.8*v);ex,ey=math.cos(a),math.sin(a)
    if v!=last:
        al=math.radians(180-1.8*last);c.saveState();c.setDash(2,1.6);c.setStrokeColor(GR2);c.setLineWidth(1.3)
        c.line(cx,cy,cx+r*.98*math.cos(al),cy+r*.98*math.sin(al));c.restoreState()
        c.setStrokeColor(INKN);c.setLineWidth(2.2);c.setLineCap(1);c.line(cx,cy,cx+r*1.02*ex,cy+r*1.02*ey)
    else:
        c.setStrokeColor(INKN);c.setLineWidth(2.2);c.setLineCap(1);c.line(cx,cy,cx+r*.5*ex,cy+r*.5*ey)
        c.saveState();c.setDash(2.2,1.8);c.setLineCap(0);c.line(cx+r*.5*ex,cy+r*.5*ey,cx+r*1.02*ex,cy+r*1.02*ey);c.restoreState()
    c.setFillColor(INKN);c.circle(cx,cy,3,stroke=0,fill=1)
    txt(c,cx,cy-20,("WON" if won else "LOST") if final else f"{v}%","Bebas",23,INKN,"c")
    s=f"Dashed = {last}% before kickoff"
    txt(c,cx,cy-28.5,s,"PopM",6,GR,"c")

RECW=None
def card(c,x,y,w,h,d):
    global RECW
    col=LG[d["k"]]
    c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.6);c.roundRect(x,y,w,h,7,stroke=1,fill=1)
    c.setFillColor(col);p=c.beginPath();p.roundRect(x,y+h-27,w,27,7);c.drawPath(p,stroke=0,fill=1);c.rect(x,y+h-27,w,10,stroke=0,fill=1)
    txt(c,x+12,y+h-20,"DK "+d["k"],"Bebas",20,PAPER);txt(c,x+12+c.stringWidth("DK "+d["k"],"Bebas",20)+7,y+h-17.5,d["team"],"PopM",6.8,PAPER)
    pill(c,x+w-10,y+h-17,STW[d["st"]],STB[d["st"]],PAPER,6.2,"PopB",5,"r")
    top=y+h-38;horizon(c,x+12,top,"THIS WEEK","Final" if d["final"] else "Live — Yahoo, read "+LIVE_AT)
    gauge(c,x+56,top-44,32,d["win"],d["last"],col,d["final"],d["me"]>d["opp"])
    rx=x+112;hdr(c,rx,top-14,"OPPONENT");txt(c,rx,top-24,d["oppn"],"PopB",8.2);txt(c,rx,top-32.5,d["oppr"],"Pop",6.8,GR)
    hdr(c,rx,top-45,"FINAL SCORE" if d["final"] else "SCORE NOW")
    mx=max(d["me"],d["opp"]);bw=w-(rx-x)-40
    for i,(lab,v,k) in enumerate((("DK "+d["k"],d["me"],col),("OPP",d["opp"],GR2))):
        yy=top-55-i*10;hdr(c,rx,yy,lab);c.setFillColor(k);c.roundRect(rx+24,yy-1.5,bw*v/mx*.86,6.5,2,stroke=0,fill=1)
        txt(c,rx+24+bw*v/mx*.86+4,yy,f"{v:.1f}","PopB",7.2,INKN)
    gap=d["me"]-d["opp"];txt(c,rx,top-74,(("Won by %.1f" if d["final"] else "Ahead by %.1f") % gap) if gap>0 else (("Lost by %.1f" if d["final"] else "Behind by %.1f") % -gap),"PopM",6.6,ST["green"] if gap>0 else ST["red"])
    # ---- SEASON: more air above and after the pill
    sy=top-84;horizon(c,x+12,sy,"SEASON","Standings before Week 3  ·  Top six make playoffs",gap=9)
    RECW=c.stringWidth("0–0","Bebas",22)+14                 # fixed record chip: 1–1, 2–2, 3–0 all the same size
    c.setFillColor(SOFT);c.roundRect(x+12,sy-27,RECW,20,4,stroke=0,fill=1)
    txt(c,x+12+RECW/2,sy-23,d["rec"],"Bebas",22,INKN,"c")
    tx2=x+12+RECW+8
    txt(c,tx2,sy-15,f"{d['place']}{'st' if d['place']==1 else 'th'} of {d['of']}","PopB",8)
    txt(c,tx2,sy-24,d["pts"],"Pop",6.4,GR)
    n=d["of"];sx=x+12;sw=w-24;cw=sw/n;yy=sy-36
    for i in range(n):
        c.setFillColor(col if i+1==d["place"] else alpha(col,.16));c.rect(sx+i*cw+.6,yy,cw-1.2,8.5,stroke=0,fill=1)
        if i+1==d["place"]: txt(c,sx+i*cw+cw/2,yy+2,str(d["place"]),"PopB",5.6,PAPER,"c")
    c.setStrokeColor(SUN[1]);c.setLineWidth(1.8);c.line(sx+6*cw,yy-3,sx+6*cw,yy+11.5)
    txt(c,sx+6*cw,yy-8.5,"Playoff line","PopM",5.6,H("#B8860B"),"c")          # marker on its own line …
    txt(c,sx,yy-17,d["line"],"PopB",6.4,ST["green"] if d["line"].startswith("In") else INKN)   # … standing on the next
    vy=y+4;c.setFillColor(alpha(ST[d["st"]],.12));c.roundRect(x+8,vy,w-16,20,5,stroke=0,fill=1)
    c.setFillColor(ST[d["st"]]);c.roundRect(x+8,vy,3.5,20,1.5,stroke=0,fill=1)
    txt(c,x+18,vy+11.5,d["verdict"],"PopB",7.1,INKN);txt(c,x+18,vy+3.5,d["when"],"Pop",6.3,GR)

# ------------------------------------------------------------------ EXPOSURE DATA
def acts(k):
    out={}
    for e in open(f"/home/claude/src/mkt/actuals_dk{k}.txt").read().strip().split(";"):
        p=e.split(":")
        if len(p)>=3: out[p[0]]=[float(v) for v in p[1:]]
    return out
ACT={k:acts(k) for k in (1,2,3,4)}
ESPN={}
for e in open("/home/claude/src/mkt/espn_season_wk3_fri.txt").read().strip().split(";"):
    p=e.split("|");ESPN.setdefault(p[0],(float(p[2]),float(p[3])))       # full-season total, points to date
YROS={}
for k in (2,3,4):
    for e in open(f"/home/claude/src/mkt/yros_dk{k}.txt").read().strip().split(";"):
        p=e.split("|")
        if len(p)==2: YROS.setdefault(p[0],[]).append(float(p[1]))
G=[r for r in csv.DictReader(open('/home/claude/src/role_watch/data/games.csv')) if r['season']=='2026' and r['game_type']=='REG']
def remaining(tm,thru=18):
    return sum(1 for r in G if r['home_score']=='' and int(r['week'])<=thru and tm in (r['home_team'],r['away_team']))
EXP=[("Travis Kelce","",  "TE","KC", ("I","II","IV"),None,("green","1")),
     ("Jayden Daniels","O","QB","WAS",("I","II","III"),None,None),
     ("Travis Etienne Jr.","","RB","NO",("I","II"),("good","01"),("green","4")),
     ("Drake London","",  "WR","ATL",("I","II"),None,None),
     ("Tyler Shough","",  "QB","NO", ("I","III"),None,None),
     ("George Pickens","","WR","DAL",("I","III"),None,None),
     ("De'Von Achane","", "RB","MIA",("II","III"),None,None),
     ("David Montgomery","","RB","HOU",("II","III"),None,None),
     ("Aaron Rodgers","", "QB","PIT",("II","III"),None,("green","2")),
     ("Josh Downs","",    "WR","IND",("III","IV"),None,None)]
NUM={"I":1,"II":2,"III":3,"IV":4}
def actual(nm,on):
    for k in on:
        a=ACT[NUM[k]].get(nm)
        if a: gp=len(a);return round(sum(a)/gp,1),gp            # HIS OWN games played, not a flat count
def projected(nm,tm):
    tot,todate=ESPN[nm];e=(tot-todate)/remaining(tm,18)          # ESPN: season total less points to date
    y=sorted(YROS[nm]);y=y[len(y)//2]/remaining(tm,17)            # Yahoo rest of season runs through Week 17
    return round((e+y)/2,1)

def track(c,x,y,w,act,prj,mx=30):
    """open tick = projected, solid dot = actual; the span between them colored by direction"""
    c.setStrokeColor(LINE);c.setLineWidth(1);c.line(x,y+2.5,x+w,y+2.5)
    xa=x+w*min(act,mx)/mx;xf=x+w*min(prj,mx)/mx;k=ST["green"] if act>=prj else ST["red"]
    c.setStrokeColor(alpha(k,.55));c.setLineWidth(3.2);c.line(min(xa,xf),y+2.5,max(xa,xf),y+2.5)
    c.setStrokeColor(INKN);c.setLineWidth(1.2);c.line(xf,y-1.5,xf,y+6.5)
    c.setFillColor(k);c.circle(xa,y+2.5,2.6,stroke=0,fill=1)

# ================================================================== PAGE 1 — GLOBAL WATCH
c=canvas.Canvas("/mnt/user-data/outputs/DK_Redesign_Sample_v9.pdf",pagesize=letter)
c.setTitle("Dark Knight Fantasy — Redesign Sample v7")
masthead(c,"GLOBAL WATCH","Week 3  ·  Scores from Yahoo, read Sun Sep 27, 9:25 PM  ·  Two final, two finish Monday night")
ry=Ht-122;c.setFillColor(INKN);c.roundRect(M,ry-10,W-2*M,26,6,stroke=0,fill=1)
items=[("SEASON","3–7–0","Before Week 3"),("THIS WEEK","2 won · 2 ahead","None behind"),("PLAYOFFS","1 of 4 in","DK IV holds a spot"),("CALL SHEET","2 open · 4 set","Nothing red")]
cw_=(W-2*M)/4
for i,(a,b,cc) in enumerate(items):
    x=M+12+i*cw_;txt(c,x,ry+4.5,a,"PopB",5.6,SUN[1]);txt(c,x,ry-5.5,b,"PopB",8.4,PAPER)
    txt(c,x+c.stringWidth(b,"PopB",8.4)+5,ry-5.5,cc,"Pop",6.2,H("#C9CFDB"))
    if i: c.setStrokeColor(H("#34405C"));c.setLineWidth(.6);c.line(M+i*cw_,ry-6,M+i*cw_,ry+12)
gw=(W-2*M-10)/2;gh=204
for i,d in enumerate(L):
    x=M+(i%2)*(gw+10);y=ry-16-gh-(i//2)*(gh+8);card(c,x,y,gw,gh,d)
ey=ry-16-2*gh-8-17
txt(c,M,ey,"EXPOSURE","Bebas",17,INKN);txt(c,M+64,ey+1,"Every player on two or more Dark Knight rosters — One bad week lands everywhere at once","Pop",7,GR)
hy=ey-16;X0=M+17
C1=(M+2,X0,X0+77,X0+97,X0+113,X0+145,X0+167)          # triangle · name · STA · pos · team · bubble · radar
ch=X0+184;cx_a=X0+292;tx=cx_a+14;tw=W-M-tx-60
rowhead(c,C1,hy)
hdr(c,ch,hy,"ON DARK KNIGHT ROSTERS")
hdr(c,cx_a,hy+6.5,"ACTUAL","r");hdr(c,cx_a,hy,"AVG / GAME","r")
# chart header: sits directly over the chart, legend built in
c.setFillColor(ST["green"]);c.circle(tx+2,hy+2,2.2,stroke=0,fill=1);hdr(c,tx+7,hy,"ACTUAL")
c.setStrokeColor(INKN);c.setLineWidth(1.1);c.line(tx+40,hy-1,tx+40,hy+5);hdr(c,tx+44,hy,"PROJECTED ROS · ESPN + YAHOO")
hdr(c,tx+tw+8,hy,"GAP")
P=14;gy0=hy-20;glast=gy0-(len(EXP)-1)*P
for j in range(len(EXP)):
    if j%2==0: c.setFillColor(SOFT);c.rect(M,gy0-j*P-4.4,W-2*M,P,stroke=0,fill=1)
# gridlines behind the rows: labeled at 0/10/20/30, faint unlabeled at the fives
for t in range(0,31,5):
    gx=tx+tw*t/30;major=t%10==0
    c.setStrokeColor(LINE if major else alpha(LINE,.55));c.setLineWidth(.6 if major else .4)
    c.line(gx,glast-4.4,gx,gy0+P-4.4)
    if major: txt(c,gx,hy-9,str(t),"Pop",5.4,GR,"c")
for j,(nm,stt,pos,tm,on,sg,tr) in enumerate(EXP):
    yy=gy0-j*P
    prow(c,C1,yy,nm,stt,pos,tm,None,sg,tr,7.2,11.5,13)
    for q,k in enumerate(("I","II","III","IV")):
        bx=ch+q*20;c.setFillColor(LG[k] if k in on else alpha(GR2,.22));c.roundRect(bx,yy-2.4,17,9.5,2.5,stroke=0,fill=1)
        txt(c,bx+8.5,yy,k,"PopB",5.8,PAPER if k in on else GR2,"c")
    a,gp=actual(nm,on);f=projected(nm,tm);track(c,tx,yy,tw,a,f)
    dec(c,cx_a-11,yy,f"{a:.1f}")
    dd=a-f;k=ST["green"] if dd>=0 else ST["red"];dec(c,tx+tw+22,yy,("+%.1f" % dd) if dd>=0 else ("%.1f" % dd),"PopB",7,k)
    txt(c,W-M-2,yy,f"{gp} gp","Pop",5.4,GR2,"r")                  # audit only — no header
ny=glast-P+1;half=(W-2*M)/2
NI=X0+10
note(c,NI,ny,"Bye","Kelce's Week 5 bye hits three rosters at once — see Byes Ahead.",6.4)
note(c,NI+half-8,ny,"Projected","ESPN and Yahoo rest of season, averaged per remaining game.",6.4)
note(c,NI,ny-9.5,"Games","London's Thursday Week 3 game isn't in the actuals yet.",6.4)
note(c,NI+half-8,ny-9.5,"Win chance","Yahoo live. Dashed = the pre-kickoff blend of four sources.",6.4)
print("page1 lowest note y",ny-9.5)
footer(c,1,"Global Watch")
c.showPage()

# ================================================================== THE CALL SHEET
SUB2="Recommended  ·  Confirmed with its day  ·  Closed  ·  Byes ahead"
def section(c,y,title,sub,col):
    txt(c,M,y,title,"Bebas",17,INKN)
    txt(c,M+c.stringWidth(title,"Bebas",17)+8,y+1,sub,"Pop",7,GR)
    c.setStrokeColor(INKN);c.setLineWidth(.5);c.line(M,y-5,W-M,y-5)
CHW=None
def lgchip(c,x,y,k):
    global CHW
    CHW=c.stringWidth("DK III","PopB",6.6)+9
    c.setFillColor(LG[k]);c.roundRect(x,y-3,CHW,11,3,stroke=0,fill=1);txt(c,x+CHW/2,y,"DK "+k,"PopB",6.6,PAPER,"c");return CHW
def block_head(c,y,lg,kind,sub,dl,dlab):
    c.setFillColor(INKN);c.roundRect(M,y-5,W-2*M,17,5,stroke=0,fill=1)
    x=M+8;x+=lgchip(c,x,y,lg)+6;x+=pill(c,x,y,kind,NEUTRAL,PAPER,6.4,"PopB",5)+8
    txt(c,x,y,sub,"PopM",7,H("#C9CFDB"))
    txt(c,W-M-8,y,dl,"PopB",7.6,SUN[1],"r");txt(c,W-M-12-c.stringWidth(dl,"PopB",7.6),y,dlab,"Pop",6.4,H("#C9CFDB"),"r")
BX=M+24
C2=(M+7,BX,BX+76,BX+97,BX+115,BX+150,BX+176)
MV=BX+200                       # MOVE column: one tag per row
WX=W-M-196;WS=72                # time windows, source named once in the header
def whead(c,y,cols):
    for i,s in enumerate(cols): hdr(c,WX+i*WS,y,s)
def wvals(c,y,vals):
    for i,v in enumerate(vals):
        dec(c,WX+i*WS+17,y-1.5,v,"Bebas",14,INKN,6)
def mv(c,y,tag,col=INKN): txt(c,MV,y,tag,"PopB",6.6,col)
def boxed(c,top,h):
    c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.6);c.roundRect(M,top-h,W-2*M,h,6,stroke=1,fill=1)

def callsheet_top():
    masthead(c,"THE CALL SHEET",SUB2)
exec(open("/home/claude/cand/redesign/_fr_fsdata.py").read())   # one blend feeds both the calls and the four-sources panel
masthead(c,"THE CALL SHEET",SUB2)
y=Ht-124;section(c,y,"RECOMMENDED","Waiting on a decision — Nothing here is an order",ST["gold"])
RP=18
# ---- item 1: LINEUP CHANGE, DK I
yy=y-24;bh=112;boxed(c,yy+12,bh)
block_head(c,yy,"I","LINEUP CHANGE","Both players are on the DK I roster — Who starts at RB","Sun 8:30 AM","Inactives")
h1=yy-19;rowhead(c,C2,h1);hdr(c,MV,h1,"MOVE");whead(c,h1,["THIS WEEK (BLEND)","ROS PER GAME (ESPN)","WEEKS 15–17"])
r1=h1-15;prow(c,C2,r1,"Jaylen Warren","Q","RB","PIT",None,("caution","01"),("gold","1"),7.6,13,14)
mv(c,r1,"START",ST["green"]);wvals(c,r1,[FB(1,"Jaylen Warren"),"11.7","—"])
r2=r1-RP;prow(c,C2,r2,"Kyle Monangai","","RB","CHI","red",None,("gold","1"),7.6,13,14)
mv(c,r2,"BENCH",GR);wvals(c,r2,[FB(1,"Kyle Monangai"),"6.8","—"])
n=r2-18
note(c,BX+10,n,"Why","Dowdle didn't practice, so the Steelers backfield is Warren's if he plays. Monangai starts only if Warren sits.")
note(c,BX+10,n-10,"Move","Nothing is dropped — this is a start, not a roster move.")
note(c,BX+10,n-20,"Weeks 15–17","The player playoff blend isn't built yet — it's on the build list.")
yy=yy-bh-12
# ---- item 2: PICKUP + DROP, DK IV
bh=150;boxed(c,yy+12,bh)
block_head(c,yy,"IV","PICKUP + DROP","Irreversible — Held Saturday; it returns only if something changed","Sun 8:30 AM","Re-test")
h1=yy-19;rowhead(c,C2,h1);hdr(c,MV,h1,"MOVE");whead(c,h1,["THIS WEEK (BLEND)","ROS PER GAME (ESPN)","WEEKS 15–17"])
r1=h1-15;prow(c,C2,r1,"Brian Robinson Jr.","","RB","ATL",None,("good","04"),("gold","2"),7.6,13,14)
mv(c,r1,"IN",ST["green"]);wvals(c,r1,["—","4.8","—"])
r2=r1-RP;prow(c,C2,r2,"Terry McLaurin","","WR","WAS","red",None,("gold","2"),7.6,13,14)
mv(c,r2,"OUT",ST["red"]);wvals(c,r2,[FB(4,"Terry McLaurin"),"11.4","—"])
r3=r2-RP;prow(c,C2,r3,"James Conner","IR","RB","ARI","gold",None,("gold","2"),7.6,13,14)
mv(c,r3,"ALT",GR);wvals(c,r3,["0.0","—","—"])
n=r3-18
note(c,BX+10,n,"Drop","One man goes, not both. The Call Sheet named McLaurin; DK IV's page named Conner. ALT = the other choice.")
note(c,BX+10,n-10,"Room","IR is full — Conner, Pacheco, Dell. No free slot absorbs the claim, so someone has to go.")
note(c,BX+10,n-20,"Missing","Robinson has no this-week projection in any DK IV source; Conner has no ESPN season line.")
note(c,BX+10,n-30,"Team","Atlanta carries a red rule — bottom third on points. A warning, not a wall.")
note(c,BX+10,n-40,"Steelman","Both halves are irreversible — Steelman it before anything is placed.")
yy=yy-bh-6
# ---- CONFIRMED — the same player rows, quieter: banded, not boxed
y=yy-10;section(c,y,"CONFIRMED","Agreed and set — each carries its day, then drops off once it's played",ST["green"])
C=[("II","Kelce over Andrews at TE","1",[("Travis Kelce","","TE","KC","START",FB(2,"Travis Kelce"),FY(2,"Travis Kelce")),("Mark Andrews","","TE","BAL","BENCH",FB(2,"Mark Andrews"),FY(2,"Mark Andrews"))],
     ("Sources","Three of four put Kelce ahead; only Yahoo flips it.")),
   ("II","Brissett over Rodgers at QB","2",[("Jacoby Brissett","","QB","ARI","START",FB(2,"Jacoby Brissett"),FY(2,"Jacoby Brissett")),("Aaron Rodgers","","QB","PIT","BENCH",FB(2,"Aaron Rodgers"),FY(2,"Aaron Rodgers"))],None),
   ("IV","Doubs over Flowers","3",[("Romeo Doubs","","WR","NE","START",FB(4,"Romeo Doubs"),FY(4,"Romeo Doubs")),("Zay Flowers","Q","WR","BAL","BENCH",FB(4,"Zay Flowers"),FY(4,"Zay Flowers"))],
     ("Why",f"The blend prefers Flowers by {fsrow(4,'Zay Flowers','BAL')['bl']-fsrow(4,'Romeo Doubs','NE')['bl']:.1f} — sitting him is the injury rule (full practice only), not the numbers.")),
   ("I","Etienne starts","4",[("Travis Etienne Jr.","","RB","NO","START",FB(1,"Travis Etienne Jr."),None)],
     ("Also","Off the injury report Friday. Also starts in DK II."))]
hc=y-18;rowhead(c,C2,hc);hdr(c,MV,hc,"MOVE");hdr(c,WX,hc,"THIS WEEK (BLEND)");hdr(c,WX+WS,hc,"YAHOO")
yy=hc-16
for j,(k,hd,num,men,nt) in enumerate(C):
    nrow=len(men);h=13+nrow*16+(10 if nt else 0)+4
    if j%2==0: c.setFillColor(SOFT);c.rect(M,yy-h+11,W-2*M,h,stroke=0,fill=1)
    x=BX;lgchip(c,x,yy,k);txt(c,x+CHW+7,yy,hd,"PopB",7.6)
    pill(c,W-M-8,yy-.5,"Set Fri",ST["green"],PAPER,6,"PopB",5,"r");txt(c,W-M-52,yy,"Game Sun","Pop",6.2,GR,"r")
    ry2=yy-15
    for i,(nm,stt,pos,tm,tag,bl,yh) in enumerate(men):
        prow(c,C2,ry2,nm,stt,pos,tm,None,{"Travis Etienne Jr.":("good","01")}.get(nm),("green",num),7.4,13)   # marks travel
        mv(c,ry2,tag,ST["green"] if tag=="START" else GR)
        dec(c,WX+17,ry2-1.5,bl,"Bebas",14,INKN,6)
        if yh: dec(c,WX+WS+11,ry2,yh,"PopM",7,GR2)
        ry2-=16
    if nt: note(c,BX+10,ry2+4,nt[0],nt[1]);ry2-=10
    yy=ry2-6
y=yy-10;section(c,y,"CLOSED","Processed since the last scan — shown once, then retired",GR2)
yy=y-18;x=BX+lgchip(c,BX,yy,"I")+7;txt(c,x,yy,"Kamara claimed, Addison dropped — landed Saturday.","PopM",7.4,GR)
c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(BX,yy-6,W-M,yy-6)
print("page2 lowest y",yy)
NEED=100
if yy-NEED-24<30:
    footer(c,2,"The Call Sheet");c.showPage()
    masthead(c,"THE CALL SHEET","Continued  ·  Byes ahead");y=Ht-124;PG=3
else:
    y=yy-26;PG=2
section(c,y,"BYES AHEAD","Byes that empty starting slots — nothing to do yet",None)
horizon(c,W-M,y+1.5,"WEEKS 5–8",align="r")
PA=[("5",[("I","Kelce — stream a free TE"),("II","Kelce — Andrews covers"),("IV","Kelce — Doubs or Shakir at flex"),("III","Chiefs D — Steelers cover")]),
   ("8",[("I","Shough, Etienne, McCaffrey, Kamara, Black"),("II","Montgomery, Etienne, Kamara, Winston, 49ers"),("III","Shough, Montgomery, Vele")]),
]
yy=y-20
for bi,(wk,rows) in enumerate(PA):
    bh_=13*((len(rows)+1)//2)+6
    if bi%2==1:
        c.setFillColor(SOFT);c.roundRect(M,yy-bh_+9,W-2*M,bh_+2,4,stroke=0,fill=1)
    else:
        c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,yy-bh_+9,W-M,yy-bh_+9)
    txt(c,M+12,yy-2,"WK "+wk,"Bebas",13,SUN[0])
    for i,(k,t) in enumerate(rows):
        xx=M+52+(i%2)*250;ly=yy-(i//2)*13;lgchip(c,xx,ly,k);txt(c,xx+CHW+5,ly,t,"Pop",7)
    yy-=bh_+4
print("byes lowest y",yy)
exec(open("/home/claude/cand/redesign/_fr_foursrc.py").read())
footer(c,PG,"The Call Sheet")
c.showPage()
exec(open("/home/claude/cand/redesign/pm_dk1.py").read())   # THE POST-MORTEM opens each league section — DK I first; II–IV join Tuesday
exec(open("/home/claude/cand/redesign/fr_v7.py").read())
exec(open("/home/claude/cand/redesign/_fr_legend.py").read())   # THE MARKS — legend, always the last page
c.save()
