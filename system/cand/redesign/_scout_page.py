# THE SCOUT PAGE v2 (Dom, Fri Oct 9 2026) — ONE page per league, right after that league's Field Report.
# Rides the FIELD puzzle piece (PZ_SUB). Reads the board the Scout engine writes (dksys/scout/scout_board_<league>.json);
# nothing on this page is typed by hand. No drops are ever suggested here. No "you/your".
# Layout (Dom's batch): masthead = league + run time + the thin-data warning; Gate 1 right under it, no stamp strip.
# Each need: title + target with the Scout marker trailing (marker color = how urgent the PROBLEM is, Radar law);
# the why; then each recommendation with a triangle in the left gutter pointing at the PERSON (triangle color = how
# urgent that pickup is); then the life-cycle line. No ordinals: the order and the title carry the rank.
# Fit, don't cram: what doesn't fit goes to one "Also on the Board" line with its marker.
import json as _js, os as _os, datetime as _dts, re as _re
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
exec(open("/home/claude/cand/redesign/_scout_mark.py").read())
exec(open("/home/claude/cand/redesign/_oct10_scout.py").read())   # Oct 10: points added, open seats first
PZ_SUB["SCOUT"]=2                                   # the Scout lights the Field piece; four pieces only
_SCT=ParagraphStyle("sct",fontName="PopB",fontSize=8.4,leading=10.2,textColor=INKN)
_SCW=ParagraphStyle("scw",fontName="Pop",fontSize=6.8,leading=8.6,textColor=INKN)
_SCP=ParagraphStyle("scp",fontName="Pop",fontSize=6.8,leading=8.6,textColor=INKN)
_SCS=ParagraphStyle("scs",fontName="Pop",fontSize=5.8,leading=7.4,textColor=GR)
def _esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def _para(c,t,st,x,ytop,w):
    p=Paragraph(t,st);_,h=p.wrap(w,999);p.drawOn(c,x,ytop-h);return h
def _ph(t,st,w): return Paragraph(t,st).wrap(w,999)[1]
def _tc(s):
    """label capitalization, consistent with the rest of the Dispatch: Free Agent, Waivers, Clears Oct 14"""
    small={"a","an","the","of","or","and","in","on","to","for","by"}
    out=[]
    for i,w in enumerate(str(s).split(" ")):
        out.append(w if (i and w.lower() in small) or not w[:1].isalpha() else w[:1].upper()+w[1:])
    return " ".join(out)
def _sent(s):
    s=str(s).strip(); s=s[:1].upper()+s[1:]
    return s if s.endswith((".","!","?")) else s+"."
def _tri(c,x,ym,col,h=8.5):
    """the call-sheet triangle, gutter size, pointing right at the person"""
    c.setFillColor(TRI.get(col,TRI["gold"]));p=c.beginPath();p.moveTo(x,ym-h/2);p.lineTo(x+h*.95,ym);p.lineTo(x,ym+h/2);p.close()
    c.drawPath(p,stroke=0,fill=1)

_SUMMARY=('<font name="PopB">The Scout</font> is the engine built to find this team\'s needs: every hole and thin spot, week by week '
          'through the playoffs, ranked by what each one costs in wins, with what is needed, when, and who available could fill it. '
          'Everything here is a recommendation to talk through. A move becomes an action only once it is decided, and then it goes to the Call Sheet.')
_SCI=ParagraphStyle("sci",fontName="Pop",fontSize=8.4,leading=11.6,textColor=INKN)   # the Dispatch's intro/body style (Outlook, Post-Mortem)
def _footer(c,pg,lab):
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,20,W-M,20)
    txt(c,M,11,"DARK KNIGHT DISPATCH","PopB",6.4,INKN)
    txt(c,M+c.stringWidth("DARK KNIGHT DISPATCH","PopB",6.4)+8,11,f"Week {WEEKN}  ·  The Scout  ·  "+built_str(),"Pop",5.8,GR)
    txt(c,W-M,11,f"Scout · {lab}  ·  Page {pg}","Pop",5.8,GR,"r")

def scout_page(c,pg,lab,k):
    """one page; returns 1 (0 when this league has no Scout board yet)"""
    f=f"/home/claude/dksys/scout/scout_board_{lab.replace(' ','')}.json"
    if not _os.path.exists(f): return 0
    B=_js.load(open(f))
    try: _MPL=_js.load(open("/home/claude/cand/missing_pieces.json"))["leagues"].get(lab,[])   # Oct 23 (Dom): Missing Pieces
    except Exception: _MPL=[]
    _MPOS={x for m_ in _MPL for x in m_.get("pos",[])}
    def _fills(p): return ('  ·  <font name="PopB" color="#A8740B">Fills a missing piece</font>' if str(p.get("pos","")).upper() in _MPOS else "")
    _MPT=('<font name="PopB" color="#A8740B">Missing Pieces</font>  '+"  ·  ".join(f'<font name="PopB">{_esc(m_["piece"])}</font> - {_esc(m_["why"])}' for m_ in _MPL)) if _MPL else ""
    try:   # Oct 25 (Dom): EXPERT MOVES - which of his men the named experts moved up or down, right under the Missing Pieces
        _EM=_js.load(open("/home/claude/dksys/data/latest/expert_moves.json")); _EL=_EM["leagues"].get(lab,{})
        _cm=lambda x: _esc(x["line"].split(":")[0].split(" (")[0])+" "+_esc(x["line"].split(": ",1)[1].split(" since")[0].split(",")[0])
        _EB=[("Up: "+_cm(x)) for x in _EL.get("rising",[])[:3]]+[("Down: "+_cm(x)) for x in _EL.get("sliding",[])[:3]]
        _EMT=(f'<font name="PopB" color="#3E5FA8">Expert Moves</font>  <font size="7">(read {_esc(_EM.get("now_read","?"))})</font>  '+("  ·  ".join(_EB) if _EB else "no big moves on your roster"))
        _MPT=(_MPT+"<br/>"+_EMT) if _MPT else _EMT
    except Exception: pass
    today=_dts.datetime.now(_dts.timezone(_dts.timedelta(hours=-7))).date()
    def dage(first): return max(0,(today-_dts.date.fromisoformat(first)).days)
    def age(first):
        d=(today-_dts.date.fromisoformat(first)).days
        return "Added Today" if d<=0 else ("Added Yesterday" if d==1 else f"Added {d} Days Ago")
    dp=[s.strip() for s in B["depth"].split("·")]
    warn=_re.sub(r"^Built from real points and workload\s*[—-]\s*","",dp[0]); warn=warn[:1].upper()+warn[1:]
    srcs=" · ".join(s[:1].upper()+s[1:] for s in dp[1:])
    masthead(c,f"SCOUT  ·  {lab}",f"Week {WEEKN}  ·  {warn}")   # Oct 10: the run time lives in the footer, not the masthead
    TOP=Ht-MH-3-12; BOT=30; X0=M+16; IW=W-M-X0; GX=M+2      # GX = left gutter, triangles only
    # ---------- measure
    def g1_parts(it):
        rep=f' ({it["rep"]})' if it.get("rep") else ""
        title=(f'{_esc(it.get("head",""))}{rep}  <font name="Pop" color="#5A6273">—  {_esc(it["title"])}  ·  {_esc(it["target"])}</font>')
        why=_esc(_sent(it["why"]))
        picks=[]
        for j,p in enumerate(it["picks"]):
            picks.append((p.get("urg","gold") if j==0 else None,f'{_pt(p)}  ·  Scored {_esc(p["scores"])}  ·  '
                          f'{_esc(_tc(p["acq"]))}  ·  {_esc(_sent(p["why"]+"; helps "+p["when"]))}'+_gain(p)+('  ·  <font name="PopB" color="#B32020">'+_esc(p["now"])+'</font>' if "WORSE" in p.get("now","") else ('  ·  <font name="PopB">'+_esc(p["now"])+'</font>' if p.get("now") else ''))+_fills(p)))
        if not picks: picks=[(None,f'<font color="#5A6273">{_esc(it["none"])}</font>')]
        return title,why,picks,_esc(it["kill"])
    def g1_h(it):
        title,why,picks,kill=g1_parts(it)
        return _ph(title,_SCT,TW_)+1+_ph(why,_SCW,IW)+2+sum(_ph(t,_SCP,IW) for _,t in picks)+11
    def g2_line(it):
        p=it["pick"]
        t=(f'<font name="PopB">{_esc(it["title"])}</font>  ·  {_pt(p)}  ·  Scored {_esc(p["scores"])}  ·  '
           f'{_esc(_tc(p["acq"]))}  ·  {_esc(_sent(p["why"]+"; helps "+p["when"]))}'+_gain(p)+('  ·  <font name="PopB" color="#B32020">'+_esc(p["now"])+'</font>' if "WORSE" in p.get("now","") else ('  ·  <font name="PopB">'+_esc(p["now"])+'</font>' if p.get("now") else '')))+_fills(p)
        if not it.get("act",True): t+=' <font color="#5A6273">'+_esc(it.get("flag") or "One game only — flag, not act.")+'</font>'
        return p.get("urg","gold"),t
    HEAD=20; TW_=IW-118                                     # title width leaves the top-right for the drops-off line
    g2=[g2_line(it) for it in B["gate2"]]
    g2h=HEAD+(sum(_ph(t,_SCP,IW)+1 for _,t in g2) if g2 else 10)+6
    g3=B["gate3"]; g3h=HEAD+10+6
    chk=('<font name="PopB">Checked, Not Assumed</font>  '+"  ·  ".join(_esc(s) for s in B["checked"]+B.get("watch",[])+_chart_lines(lab,B))+
         f'<br/>{_esc(B["footer"])}  ·  {_esc(srcs)}')
    chh=_ph(chk,_SCS,W-2*M)+4
    room=TOP-BOT-HEAD-g2h-g3h-chh-6-(_ph(_SUMMARY,_SCI,W-2*M)+12)-_open_h(B)-((_ph(_MPT,_SCW,W-2*M)+8) if _MPT else 0)-(30 if len(B['gate1'])>3 else 0)   # Oct 10 night: room for the Also on the Board line
    full=[];used=0;rest=[]
    for it in B["gate1"]:
        h=g1_h(it)
        if not rest and used+h<=room-(16 if it is not B["gate1"][-1] else 0): full.append(it);used+=h
        else: rest.append(it)
    # ---------- draw
    y=TOP
    def gate_head(t,sub):
        nonlocal y
        txt(c,M,y,t,"PopB",8,INKN); txt(c,M+c.stringWidth(t,"PopB",8)+8,y+.3,sub,"Pop",6.2,GR); y-=5
        c.setStrokeColor(LG[k]);c.setLineWidth(1.1);c.line(M,y,W-M,y); y-=11
    y-=_para(c,_SUMMARY,_SCI,M,y,W-2*M)+20; y=_open_box(c,y,B)                   # even air: gold line to summary = summary to Gate 1
    if _MPT: y-=_para(c,_MPT,_SCW,M,y,W-2*M)+8                                  # Oct 23 (Dom): the team's Missing Pieces, right above Gate 1
    gate_head("Gate 1  ·  Needs, in Priority Order","Each slot named on this roster  ·  the target is what the slot will give  ·  measured against the opponent's man that week")
    for i,it in enumerate(full):
        title,why,picks,kill=g1_parts(it)
        p=Paragraph(title,_SCT);tw,th=p.wrap(TW_,999)
        p.drawOn(c,X0,y-th)
        lw=min(p.getActualLineWidths0()[-1] if hasattr(p,"getActualLineWidths0") else tw,tw)
        scout_mark_inline(c,X0+lw+6,y-th+3.0,it["mark"],it.get("age",dage(it["first"])),it.get("gap"),8)   # one line: glass + splat/count
        txt(c,W-M,y-7.2,kill,"Pop",5.8,GR,"r")                                  # the life-cycle line rides top right
        yy=y-th-1
        yy-=_para(c,why,_SCW,X0,yy,IW)+2
        for col,t in picks:
            h=_para(c,t,_SCP,X0,yy,IW)
            if col: _tri(c,GX,yy-4.3,col)                                       # triangle points at the person, never the need
            yy-=h
        y=yy-5
        if i<len(full)-1 or rest: c.setStrokeColor(LINE);c.setLineWidth(.4);c.line(X0,y+2.5,W-M,y+2.5); y-=5
    if rest:
        x=X0; txt(c,M,y-7,"","Pop",6,GR)
        lab0="Also on the Board"; txt(c,X0,y-7,lab0,"PopB",6.2,INKN); x=X0+c.stringWidth(lab0,"PopB",6.2)+8
        yl=y-7
        for it in rest:
            s=it["title"]; w=c.stringWidth(s,"Pop",6.2)+scout_icon_w(7)+14
            if x+w>W-M: x=X0; yl-=10
            txt(c,x,yl,s,"Pop",6.2,INKN); scout_icon(c,x+c.stringWidth(s,"Pop",6.2)+3+scout_icon_w(7)/2,yl+2.2,it["mark"],7); x+=w
        y=yl-12
    y-=10; gate_head("Gate 2  ·  Available, Could Incrementally Improve the Team","Found by workload, an opening, or a return  ·  priced as if a seat opens  ·  no drops suggested")
    if g2:
        for col,t in g2:
            h=_para(c,t,_SCP,X0,y,IW); _tri(c,GX,y-4.3,col); y-=h+1
    else: txt(c,X0,y-6,"None this run.","Pop",6.6,GR); y-=10
    y-=12; gate_head("Gate 3  ·  Hunches","Written down, aged and graded like any other name")
    if g3: txt(c,X0,y-6,"  ·  ".join(h.get("title",str(h)) if isinstance(h,dict) else str(h) for h in g3),"Pop",6.6,INKN)
    else: txt(c,X0,y-6,"None written yet.","Pop",6.6,GR)
    y-=16
    if y-chh<BOT: import sys as _sy; print('   SCOUT PAGE OVERFLOW',lab,round(BOT-(y-chh),1),'pt',file=_sy.stderr)   # never silently: the build log says so
    _para(c,chk,_SCS,M,max(y,BOT+chh),W-2*M)
    _footer(c,pg,lab); c.showPage()
    return 1

# OCT10 scout page

# OCT10c scout page

# OCT10d scout page fit

# OCT10e scout chart lines

# OCT14b the this-week guard on every Scout pick

# OCT21g Scout page flag + watch
