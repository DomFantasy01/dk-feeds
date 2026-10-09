# THE OUTLOOK (Dom, Thu Oct 8 2026) - Wednesday and Thursday, one lean page that sets the stage for the week.
# Per league: the matchup and Yahoo's projected margin, byes in his lineup, questionable starters, close start/sit calls.
# One waiver nudge at the bottom, from the Radar. The depth stays in the league pages and the Radar - this is the glance.
# Everything comes from the same meter file as the rest of the Dispatch; nothing is typed per week.
import json as _jo, os as _oo, glob as _go
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
_OB=ParagraphStyle("ob",fontName="Pop",fontSize=8.4,leading=11.6,textColor=INKN)
_ON=ParagraphStyle("on",fontName="Pop",fontSize=6.2,leading=8.3,textColor=GR)
_OLG=(("I","DK I"),("II","DK II"),("III","DK III"),("IV","DK IV"))
_FLEXOK={"W/R/T":("RB","WR","TE"),"Q/W/R/T":("QB","RB","WR","TE")}
def _avg(p):
    v=[x for x in (p.get("gotham"),p.get("sleeper")) if x is not None]
    return sum(v)/len(v) if v else None
def _nm(p): return p.get("player") or p.get("name")

def outlook_data():
    out=[]
    for k,lab in _OLG:
        L=MTR["leagues"].get(lab)
        if not L: out.append(dict(k=k,lab=lab,missing=True)); continue
        me=L["starters"]["me"]; ym,yo=L["totals"]["yahoo"]
        bye=[p for p in me if p.get("window") is None and p.get("team")]
        q=[p for p in me if p.get("status") in ("Q","D","O","IR")]
        close=[]
        for b in L.get("bench",[]):
            if b["slot"]!="BN" or b.get("window") is None or b.get("status") in ("O","IR"): continue
            bv=_avg(b)
            if bv is None: continue
            rivals=[p for p in me if p.get("pos")==b.get("pos") or b.get("pos") in _FLEXOK.get(p["slot"],())]
            rivals=[(p,_avg(p)) for p in rivals if _avg(p) is not None]
            if not rivals: continue
            p,pv=min(rivals,key=lambda x:x[1])
            if bv>=pv-1.0: close.append((b,bv,p,pv))
        close=sorted(close,key=lambda x:x[3]-x[1])[:2]
        out.append(dict(k=k,lab=lab,full=L["league"],opp=L["opp"],orec=L.get("opp_record"),orank=L.get("opp_rank"),rec=L.get("record"),
                        rank=L.get("rank"),teams=L.get("teams"),ym=ym,yo=yo,ywin=L["needles"].get("yahoo"),bye=bye,q=q,close=close))
    return out

def _radar_nudge():
    """the one waiver line: the Radar's best free-agent or waiver add that clears his weakest starter, across all four"""
    fs=[f"/home/claude/domfantasy01/dk-feeds/dispatch_out/radar_wk{WEEKN}.json",f"/home/claude/dksys/data/latest/radar/radar_wk{WEEKN}.json"]
    best=None; built=None
    for f in fs:
        if not _oo.path.exists(f): continue
        R=_jo.load(open(f))
        if built and R.get("built_utc","")<=built: continue
        built=R.get("built_utc",""); bt=R.get("built"); best=None
        for lab,L in R.get("leagues",{}).items():
            for r in L.get("in",[]):
                if not r.get("beats_floor") or r.get("gotham") is None or not r.get("floor"): continue
                gap=r["gotham"]-(r["floor"].get("gotham") or 0)
                if best is None or gap>best[0]: best=(gap,lab,r,bt)
    return best

OLD=outlook_data(); OLN=_radar_nudge()
print("OUTLOOK week",WEEKN,"|",", ".join(f"{d['lab']} {d['ym']-d['yo']:+.1f}" for d in OLD if not d.get("missing")),"| nudge:",OLN[2]["name"] if OLN else None)

def _ol_para(c,t,st,x,ytop,w):
    p=Paragraph(t.replace("&","&amp;"),st);_,h=p.wrap(w,999);p.drawOn(c,x,ytop-h);return h
def _ol_h(t,st,w): return Paragraph(t.replace("&","&amp;"),st).wrap(w,999)[1]

def outlook_page(c,pg):
    from reportlab.lib.colors import Color
    masthead(c,"OUTLOOK",f"Week {WEEKN}  ·  the week ahead  ·  {YREAD}")
    y=Ht-MH-3-20
    section(c,y,"THE WEEK AHEAD","Where each matchup stands on Yahoo, and the few things to settle before kickoff.",None)
    y-=24
    IW=W-2*M-24; BH=50
    def _mx(p,q,t): return Color(p.red*(1-t)+q.red*t,p.green*(1-t)+q.green*t,p.blue*(1-t)+q.blue*t)
    for d in OLD:
        k=d["k"]
        if d.get("missing"):
            gcard(c,M,y-30,W-2*M,30,LG[k]); txt(c,M+12,y-18,f"{d['lab']}: no Yahoo matchup read for Week {WEEKN} yet.","PopB",8,TRED); y-=37; continue
        lines=[]
        if d["bye"]: lines.append('<font name="PopB" color="#D64545">Bye in the lineup:</font> '+", ".join(f"{_nm(p)} ({p['team']})" for p in d["bye"])+".")
        if d["q"]: lines.append('<font name="PopB" color="#B07A00">Injuries to watch:</font> '+", ".join(f"{_nm(p)} ({p['status']})" for p in d["q"])+".")
        for b,bv,p,pv in d["close"]:
            lines.append('<font name="PopB">Close call:</font> '+f"{_nm(b)} (bench) {bv:.1f} vs {_nm(p)} (starting) {pv:.1f}.")
        if not lines: lines.append('<font name="PopB" color="#12A150">Lineup set</font> — no byes, no injury tags, no close calls.')
        body="<br/>".join(lines)
        hb=_ol_h(body,_OB,IW); H_=BH+8+hb+9
        gcard(c,M,y-H_,W-2*M,H_,LG[k])
        c.saveState();p_=c.beginPath();p_.roundRect(M,y-H_,W-2*M,H_,7);c.clipPath(p_,stroke=0)
        c.linearGradient(M,y-BH,M,y,(INKN,_mx(INKN,LG[k],.42)),(0,1),extend=False);c.restoreState()
        hy=y-16;x=M+12;x+=lgchip(c,x,hy,k)+7
        txt(c,x,hy,d["full"],"PopB",8.8,PAPER);x+=c.stringWidth(d["full"],"PopB",8.8)+6
        txt(c,x,hy,"vs "+(d["opp"] or "?"),"Pop",7.4,H("#C9CFDB"))
        sub=(f"{(d['rec'] or '').replace('-0','',1) if (d['rec'] or '').endswith('-0') else d['rec']}, {d['rank']}{_sfx(d['rank'])} of {d['teams']}" if d.get("rank") else "")
        osub=(f"{d['opp']} {d['orec'][:-2] if (d['orec'] or '').endswith('-0') else d['orec']}"+(f", {d['orank']}{_sfx(d['orank'])}" if d.get("orank") else "")) if d.get("orec") else ""
        txt(c,M+12,y-36,"  ·  ".join(t for t in (sub,osub) if t).replace("-","–"),"PopM",7.4,H("#E6E9EF"))
        mg=d["ym"]-d["yo"]
        tag_=(f"AHEAD {mg:.1f} ON YAHOO" if mg>=0.05 else (f"BEHIND {-mg:.1f} ON YAHOO" if mg<=-0.05 else "EVEN ON YAHOO"))+(f"  ·  {d['ywin']}%" if d.get("ywin") is not None else "")
        tc=TGRN if mg>=0.05 else TGLD
        tw=c.stringWidth(tag_,"PopB",6.6)+12
        c.setFillColor(tc);c.rect(W-M-10-tw,hy-3.5,tw,12,stroke=0,fill=1);txt(c,W-M-10-tw/2,hy,tag_,"PopB",6.6,PAPER,"c")
        xr=W-M-10
        for v,lab,col in ((f"{d['yo']:.1f}","OPP",H("#C9CFDB")),(f"{d['ym']:.1f}",d["lab"],PAPER)):
            txt(c,xr,y-39,v,"Bebas",18,col,"r");wv=c.stringWidth(v,"Bebas",18)
            txt(c,xr-wv/2,y-47,lab,"PopB",5.2,H("#C9CFDB"),"c");xr-=wv+14
        txt(c,xr+6,y-39,"YAHOO PROJ","PopB",5.4,H("#8A93A6"),"r")
        _ol_para(c,body,_OB,M+12,y-BH-8,IW)
        y-=H_+8
    # the one waiver line
    if OLN:
        gap,lab,r,bt=OLN
        t=(f'<font name="PopB">WAIVER NUDGE</font>   {lab}: {r["name"]} ({r["pos"]}, {r["team"]}) — {r.get("acq","available")}. '
           f'Gotham {r["gotham"]:.1f} against the weakest starter, {r["floor"]["name"]} {r["floor"]["gotham"]:.1f}. The Radar has the news behind it.')
    else:
        t='<font name="PopB">WAIVER NUDGE</font>   Nothing on the Radar clears a starter right now.'
    ha=_ol_h(t,_OB,W-2*M-22)+12
    c.setFillColor(SOFT);c.rect(M,y-ha,W-2*M,ha,stroke=0,fill=1);c.setFillColor(SUN[1]);c.rect(M,y-ha,4,ha,stroke=0,fill=1)
    _ol_para(c,t,_OB,M+14,y-6,W-2*M-22); y-=ha+9
    src=(f"Matchups, records, Yahoo projections, win % and injury tags: Yahoo, {YREAD[len('Yahoo read '):]}. Byes: the NFL schedule. "
         f"Close calls: Gotham and Sleeper averaged, bench against the weakest starter he could replace, within a point. "
         +(f"Waiver nudge: the Radar, built {OLN[3]}." if OLN and OLN[3] else "Waiver nudge: the Radar."))
    _ol_para(c,src,_ON,M,y,W-2*M)
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,20,W-M,20)
    txt(c,M,11,"DARK KNIGHT DISPATCH","PopB",6.4,INKN)
    txt(c,M+c.stringWidth("DARK KNIGHT DISPATCH","PopB",6.4)+8,11,f"Week {WEEKN}  ·  Outlook  ·  "+built_str(),"Pop",5.8,GR)
    txt(c,W-M,11,"Outlook  ·  page "+str(pg),"Pop",5.8,GR,"r")
