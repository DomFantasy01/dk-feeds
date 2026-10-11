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
PT=dt.timezone(dt.timedelta(hours=-7)); now=dt.datetime.now(PT)
MON={1:"Jan.",2:"Feb.",3:"March",4:"April",5:"May",6:"June",7:"July",8:"Aug.",9:"Sept.",10:"Oct.",11:"Nov.",12:"Dec."}
built=f"Built {now:%a} {MON[now.month]} {now.day}, {now.hour%12 or 12}:{now:%M} {'AM' if now.hour<12 else 'PM'} PT"
try:
    mf=sorted(glob.glob("/home/claude/dksys/data/latest/meter/meter_wk*.json"),key=lambda p:int(p.split("_wk")[1].split(".")[0]))[-1]
    week=json.load(open(mf))["week"]
except Exception: week="?"
LIVE_URL="https://claude.ai/artifact/5MYR1N6N64JTdERe7zRZJh"
PAPER,INKN,GR,LINE=H("#FBF7EF"),H("#14213D"),H("#7A7F8C"),H("#DDD5C4")
SEC=re.compile(r"(OVERVIEW|FIELD REPORT|SCOUT|POSITIONS|THE MARKS|POST-MORTEM|OUTLOOK)(?:\s*·\s*(DK I{1,3}V?|DK IV|FANTASY FOOTBALL))?")
def section(page):
    try: t=page.extract_text() or ""
    except Exception: t=""
    m=SEC.search(t)
    if not m: return ""
    a=m.group(1).title().replace("Post-Mortem","Post-Mortem"); b=m.group(2)
    if b and b.startswith("DK"): return f"{a} · {b}"
    return a
src=sys.argv[1]; R=PdfReader(src); N=len(R.pages); w=PdfWriter()
for i,pg in enumerate(R.pages):
    W_=float(pg.mediabox.width); buf=io.BytesIO(); c=canvas.Canvas(buf,pagesize=(W_,float(pg.mediabox.height))); M=30
    c.setFillColor(PAPER); c.rect(0,0,W_,25.5,stroke=0,fill=1)                     # the old footer, whatever it was, goes under
    c.setStrokeColor(LINE); c.setLineWidth(.6); c.line(M,20,W_-M,20)
    c.setFont("PopB",6.4); c.setFillColor(INKN); c.drawString(M,10.4,"DARK KNIGHT DISPATCH")
    x=M+c.stringWidth("DARK KNIGHT DISPATCH","PopB",6.4)+8
    sec=section(pg); mid=f"Week {week}"+("  ·  "+sec if sec else "")      # Oct 11 (Dom): no date stamp down here - each page carries its own where it belongs
    c.setFont("Pop",5.8); c.setFillColor(GR); c.drawString(x,10.4,mid)
    # the button to Dark Knight Live, centered, in the footer's own type size (Dom, Oct 11)
    lt="DARK KNIGHT LIVE  \u203a"; lw=c.stringWidth(lt,"PopB",6.4)+14; lx=W_/2-lw/2
    c.setFillColor(INKN); c.roundRect(lx,6.8,lw,11.2,3,stroke=0,fill=1)
    c.setFillColor(H("#EFD23E")); c.setFont("PopB",6.4); c.drawCentredString(W_/2,10.4,lt)
    c.linkURL(LIVE_URL,(lx,6.8,lx+lw,18.0),relative=0,thickness=0)
    c.setFont("Pop",5.8); c.setFillColor(GR); c.drawRightString(W_-M,10.4,f"Page {i+1} of {N}")
    c.save(); buf.seek(0); pg.merge_page(PdfReader(buf).pages[0]); w.add_page(pg)
w.write(src); print("   footers: one footer on all",N,"pages, numbered 1 to",N)
