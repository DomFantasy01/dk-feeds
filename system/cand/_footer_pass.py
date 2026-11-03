# ONE FOOTER ON EVERY PAGE (Dom, Sat Oct 10 2026). Runs on the assembled Dispatch after every build.
# Each page generator drew its own footer (some none, some without a page number, all worded differently). This pass
# covers the bottom band of every page and draws one identical footer: the report name, the week, the section the page
# belongs to, a centered Dark Knight Live button, and "Page N of M" - numbered across the whole assembled document.
import sys, re, io, glob, json, datetime as dt
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor as H
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
GF="/usr/share/fonts/truetype/google-fonts/"
for n,f in (("Pop","Poppins-Regular"),("PopB","Poppins-Bold")): pdfmetrics.registerFont(TTFont(n,GF+f+".ttf"))
import os
_BB=[f for f in ("/home/claude/cand/fonts/BebasNeue-Regular.ttf",os.path.join(os.path.dirname(os.path.abspath(__file__)),"fonts/BebasNeue-Regular.ttf")) if os.path.exists(f)]
try: pdfmetrics.registerFont(TTFont("BebasN",_BB[0]))
except Exception: pdfmetrics.registerFont(TTFont("BebasN",GF+"Poppins-Bold.ttf"))   # Bebas is what Live's buttons use
PT=__import__("zoneinfo").ZoneInfo("America/Los_Angeles"); now=dt.datetime.now(PT)
MON={1:"Jan.",2:"Feb.",3:"March",4:"April",5:"May",6:"June",7:"July",8:"Aug.",9:"Sept.",10:"Oct.",11:"Nov.",12:"Dec."}
built=f"Built {now:%a} {MON[now.month]} {now.day}, {now.hour%12 or 12}:{now:%M} {'AM' if now.hour<12 else 'PM'} PT"
try:
    mf=sorted(glob.glob("/home/claude/dksys/data/latest/meter/meter_wk*.json"),key=lambda p:int(p.split("_wk")[1].split(".")[0]))[-1]
    week=json.load(open(mf))["week"]
except Exception: week="?"
LIVE_URL="https://claude.ai/artifact/5MYR1N6N64JTdERe7zRZJh"
YAHOO_URL="https://football.fantasysports.yahoo.com/"          # lineups & waivers (same as Live, Nov 3)
BLITZ_URL="https://leagueblitz.app/"                            # live play-by-play (same as Live, Nov 3)
FULL_URL="https://domfantasy01.github.io/dk-feeds/dispatch_out/Dark_Knight_Dispatch_full_latest.pdf"
ONE_URL="https://domfantasy01.github.io/dk-feeds/dispatch_out/Dark_Knight_Dispatch_latest.pdf"
ONEPAGE="onepage" in (sys.argv[1] if len(sys.argv)>1 else "").lower()
PAPER,INKN,GR,LINE=H("#FBF7EF"),H("#14213D"),H("#7A7F8C"),H("#DDD5C4")
SEC=re.compile(r"(OVERVIEW|FIELD REPORT|SCOUT|POSITIONS|THE MARKS|POST-MORTEM|OUTLOOK|CALIBRATION)(?:[\s·]*(DK ?[1-4]|DK I{1,3}V?|DK IV|FANTASY FOOTBALL))?",re.I)
def section(page):
    try: t=page.extract_text() or ""
    except Exception: t=""
    m=SEC.search(t)
    if not m: return ""
    a=m.group(1).title().replace("Post-Mortem","Post-Mortem"); b=m.group(2)
    if b: b=re.sub(r"DK ?(IV|III|II|I|[1-4])\b",lambda q:"DK "+{"1":"I","2":"II","3":"III","4":"IV"}.get(q.group(1),q.group(1)),b)   # Oct 12: DK1-DK4
    if b and b.startswith("DK"): return f"{a} · {b}"
    return a
# THE CONTROLS STRIP (Dom, Nov 3: "a line of controls like in DK Live"). Same look as Live's CONTROLS bar - a dark framed
# strip, the label notched into its top edge in brushed gold type, four identical brushed-gold buttons with a caption under
# each name. Drawn on the Overview page (the one-page Dispatch and page 1 of the full edition), in the empty band
# between the footnote and the footer. Other pages keep the small link row in the footer.
def controls(c,W_):
    M=30; y0,y1=27.5,58.5; bx0,bx1=M,W_-M
    c.setFillColor(H("#0A1020")); c.setStrokeColor(H("#2A3A5E")); c.setLineWidth(.8); c.roundRect(bx0,y0,bx1-bx0,y1-y0,6,stroke=1,fill=1)
    lab="CONTROLS"; c.setFont("PopB",5.6); lw=c.stringWidth(lab,"PopB",5.6)+c._charSpace*0
    sp=1.1; tw=lw+sp*(len(lab)-1)+8
    c.setFillColor(PAPER); c.rect(bx0+10,y1-3,tw,6,stroke=0,fill=1)
    c.saveState(); t=c.beginText(bx0+14,y1-1.9); t.setFont("PopB",5.6); t.setCharSpace(sp); t.setFillColor(H("#B89A5A")); t.textOut(lab); t.setCharSpace(0); c.drawText(t); c.restoreState()
    B=[("YAHOO","lineups & waivers",YAHOO_URL),("BLITZ","live play-by-play",BLITZ_URL),("LIVE","Dark Knight Live",LIVE_URL)]
    B.append(("FULL DISPATCH","all pages, latest build",FULL_URL) if ONEPAGE else ("ONE-PAGE","the overview link",ONE_URL))
    gap=6; pad=7; bw=(bx1-bx0-2*pad-gap*(len(B)-1))/len(B); bh=20; by=y0+4.5
    for k,(name,cap,u) in enumerate(B):
        x=bx0+pad+k*(bw+gap)
        c.saveState(); pth=c.beginPath(); pth.roundRect(x,by,bw,bh,4); c.clipPath(pth,stroke=0,fill=0)
        c.linearGradient(x,by+bh,x,by,(H("#E3BE6A"),H("#C99A3E"),H("#A97A26")),(0,.5,1),extend=True)
        for yy in range(int(by),int(by+bh)+1):                               # the brushed grain
            c.setStrokeColor(H("#FFF4D2"),alpha=.22 if yy%2 else .0); c.setLineWidth(.35); c.line(x,yy+.25,x+bw,yy+.25)
            if yy%3==0: c.setStrokeColor(H("#462C06"),alpha=.18); c.line(x,yy+.75,x+bw,yy+.75)
        c.setFillColor(H("#FFF6D7"),alpha=.18); c.rect(x+bw*.30,by,bw*.18,bh,stroke=0,fill=1)   # soft sheen
        c.restoreState()
        c.setStrokeColor(H("#7A5A1C")); c.setLineWidth(.7); c.roundRect(x,by,bw,bh,4,stroke=1,fill=0)
        c.setFillColor(H("#1A1206")); c.setFont("BebasN",11.5); c.drawCentredString(x+bw/2,by+9.6,name)
        c.setFont("Pop",5.4); c.drawCentredString(x+bw/2,by+3.4,cap)
        c.linkURL(u,(x,by,x+bw,by+bh),relative=0,thickness=0)
src=sys.argv[1]; R=PdfReader(src); N=len(R.pages); w=PdfWriter()
for i,pg in enumerate(R.pages):
    W_=float(pg.mediabox.width); buf=io.BytesIO(); c=canvas.Canvas(buf,pagesize=(W_,float(pg.mediabox.height))); M=30
    c.setFillColor(PAPER); c.rect(0,0,W_,25.5,stroke=0,fill=1)                     # the old footer, whatever it was, goes under
    c.setStrokeColor(LINE); c.setLineWidth(.6); c.line(M,20,W_-M,20)
    c.setFont("PopB",6.4); c.setFillColor(INKN); c.drawString(M,10.4,"DARK KNIGHT DISPATCH")
    x=M+c.stringWidth("DARK KNIGHT DISPATCH","PopB",6.4)+8
    sec=section(pg); mid=f"Week {week}"+("  ·  "+sec if sec else "")      # Oct 11 (Dom): no date stamp down here - each page carries its own where it belongs
    c.setFont("Pop",5.8); c.setFillColor(GR); c.drawString(x,10.4,mid)
    # the link row, centered: the same links as Dark Knight Live's CONTROLS bar - Yahoo, Blitz, Live - plus the full
    # edition on the one-page Dispatch (Dom, Nov 3). Dark Knight Live keeps its navy-and-gold button (Oct 11).
    ov=sec.lower().startswith("overview")
    if ov: controls(c,W_)                                                   # the CONTROLS strip sits above the footer
    btns=[("DARK KNIGHT LIVE",LIVE_URL,True)] if ov else [("YAHOO",YAHOO_URL,False),("BLITZ",BLITZ_URL,False),("DARK KNIGHT LIVE",LIVE_URL,True)]
    ws=[c.stringWidth(t+"  \u203a","PopB",6.4)+14 for t,_,_ in btns]; gap=5; bx=W_/2-(sum(ws)+gap*(len(ws)-1))/2
    for (t,u,main),bw in zip(btns,ws):
        if main: c.setFillColor(INKN); c.roundRect(bx,6.8,bw,11.2,3,stroke=0,fill=1); c.setFillColor(H("#EFD23E"))
        else: c.setStrokeColor(INKN); c.setLineWidth(.6); c.setFillColor(H("#FFFFFF")); c.roundRect(bx,6.8,bw,11.2,3,stroke=1,fill=1); c.setFillColor(INKN)
        c.setFont("PopB",6.4); c.drawCentredString(bx+bw/2,10.4,t+"  \u203a")
        c.linkURL(u,(bx,6.8,bx+bw,18.0),relative=0,thickness=0); bx+=bw+gap
    c.setFont("Pop",5.8); c.setFillColor(GR); c.drawRightString(W_-M,10.4,f"Page {i+1} of {N}")
    c.save(); buf.seek(0); pg.merge_page(PdfReader(buf).pages[0]); w.add_page(pg)
w.write(src); print("   footers: one footer on all",N,"pages, numbered 1 to",N)

# OCT12 footer dk names

# OCT12 footer roman names
