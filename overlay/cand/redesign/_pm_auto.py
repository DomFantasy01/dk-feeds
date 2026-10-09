# THE POST-MORTEM, automatic (Thu Oct 8 2026). Replaces the hand-typed Week 4 page (_postmortem2.py), same look.
# Facts only, looking back - built from Yahoo's own matchup pages for the week just played (yahoo/wk<PW>/dom_matchups_*.txt).
# Monday = provisional, stamped NOT COMPLETE. Tuesday = final, but only when the read came in after the last game ended
# and every starter on both sides has a score; otherwise it still says provisional and why. Nothing is typed per week.
import glob as _gp, re as _rp, datetime as _dp, pandas as _pdp
from zoneinfo import ZoneInfo as _ZP
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
_ET=_ZP("America/New_York"); _PTZ=_ZP("America/Los_Angeles")
_YD="/home/claude/dksys/data/latest/yahoo/"
_PMLG=(("I","DK I","269381","TheMostImportantThingInLife"),("II","DK II","1519795","Winners and Sinners"),
       ("III","DK III","1507991","Hers and His Version 2.0"),("IV","DK IV","864215","Murrieta NextDoor"))
_MYTEAM={"269381":"Dark Knight I","1519795":"Dark Knight II","1507991":"Dark Knight III","864215":"Dark Knight IV"}

# ---- the NFL weeks, kickoffs in Pacific time
_G=_pdp.read_csv("/home/claude/dksys/data/latest/games.csv",low_memory=False); _G=_G[(_G.season==CAL_NOW.year if CAL_NOW.month>2 else _G.season==CAL_NOW.year-1)&(_G.game_type=="REG")]
def _ko(r): return _dp.datetime.strptime(f"{r.gameday} {r.gametime}","%Y-%m-%d %H:%M").replace(tzinfo=_ET).astimezone(_PTZ)
_KO={}
for _rg in _G.itertuples(): _KO.setdefault(int(_rg.week),[]).append(_ko(_rg))
_started=[w for w,v in _KO.items() if min(v)<=CAL_NOW]
PM_WEEK=max(_started) if _started else None            # the week most recently under way = the week being looked back on

def _hdr_time(path):
    """the pull time written in the file's own header ('Thu Oct 8 3:20 PM PT') - disk times lie on GitHub's computer"""
    h=open(path).readline()
    m=_rp.search(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (\w{3}) (\d{1,2}),? (\d{1,2}):(\d{2}) ([AP]M) PT",h)
    if not m: return None
    t=_dp.datetime.strptime(f"{m.group(2)} {m.group(3)} {CAL_NOW.year} {m.group(4)}:{m.group(5)} {m.group(6)}","%b %d %Y %I:%M %p")
    return t.replace(tzinfo=_PTZ)
def _newest(pattern,before=None):
    fs=[(f,_hdr_time(f)) for f in _gp.glob(pattern)]; fs=[x for x in fs if x[1] and (before is None or x[1]<before)]
    return max(fs,key=lambda x:x[1]) if fs else (None,None)
def _side(s):
    out=[]
    for it in s.split("|"):
        if not it.strip(): continue
        slot,name,team,st,ko,proj,pts=(it.split("^")+[""]*7)[:7]
        name=_rp.sub(r"(No new player Notes|New Player Note|Player Notes?)$","",name).strip()
        m=_rp.match(r"^(.*?)(Q|D|O|IR|SUS|PUP)$",name)
        if m and slot!="DEF" and not name.endswith(("Jr","Sr","II","III","IV")): name,st=m.group(1),m.group(2)
        f=lambda v:float(v) if v not in ("","–","-") else None
        out.append(dict(slot=slot,name=name,team=team,status=st,ko=ko,proj=f(proj),pts=f(pts)))
    return out
def _fmt_t(t): return t.strftime("%a %b %-d %-I:%M %p").replace("AM","a.m.").replace("PM","p.m.")+" PT"
def _rec(r): return r.replace("-0","",1) if r.endswith("-0") and r.count("-")==2 else r
def _sfx2(n): return "th" if 10<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10,"th")
def _list(xs): return xs[0] if len(xs)==1 else ", ".join(xs[:-1])+" and "+xs[-1]

def pm_build():
    """everything the page says, as data - also printed to the build log so a wrong line can be traced"""
    if PM_WEEK is None: return dict(state="none")
    W_=PM_WEEK; first,last=min(_KO[W_]),max(_KO[W_])
    MF,MT=_newest(_YD+f"wk{W_}/dom_matchups_*.txt")
    SF,STt=_newest(_YD+f"wk{W_}/standings_*.txt",before=first)
    D=dict(week=W_,read=MT,file=MF,last_game=last,stand_read=STt,leagues=[])
    if not MF: D["state"]="waiting"; return D
    M_={}
    for line in open(MF):
        if line.startswith("#") or "#" not in line: continue
        lg,rest=line.rstrip("\n").split("#",1); me,op=rest.split("##"); M_[lg]=(_side(me),_side(op))
    ST={}
    if SF:
        for line in open(SF):
            if line.startswith("#") or "#" not in line: continue
            lg,rest=line.rstrip("\n").split("#",1); rows=[it.split("^") for it in rest.split("|") if it.count("^")>=2]
            ST[lg]=dict(n=len(rows),me=next((r for r in rows if r[1]==_MYTEAM.get(lg)),None))
    scored=sum(1 for v in M_.values() for s in v for p in s if p["pts"] is not None)
    if scored==0: D["state"]="waiting"; return D          # the newest read is from before the games - nothing to look back on yet
    pend_all=0; started={}
    for k,lab,lg,full in _PMLG:
        if lg not in M_: D["leagues"].append(dict(k=k,lab=lab,missing=True)); continue
        me,op=M_[lg]
        ms=sum(p["pts"] or 0 for p in me); os_=sum(p["pts"] or 0 for p in op)
        mp=[p for p in me if p["pts"] is None]; opn=[p for p in op if p["pts"] is None]; pend_all+=len(mp)+len(opn)
        done=[p for p in me if p["pts"] is not None and p["proj"] is not None]
        up=sorted([p for p in done if p["pts"]-p["proj"]>=3],key=lambda p:p["proj"]-p["pts"])[:3]
        dn=sorted([p for p in done if p["pts"]-p["proj"]<=-4],key=lambda p:p["pts"]-p["proj"])[:3]
        ob=max([p for p in op if p["pts"] is not None],key=lambda p:p["pts"],default=None)
        hurt=[p for p in me if p["status"] in ("O","IR","D","SUS")]
        for p in me:
            if p["pts"] is not None and p["slot"]!="DEF": started.setdefault(p["name"],[]).append((lab,p))
        s=ST.get(lg,{})
        D["leagues"].append(dict(k=k,lab=lab,lg=lg,full=full,me=ms,op=os_,mp=mp,opn=opn,up=up,dn=dn,ob=ob,hurt=hurt,stand=s))
    OPPN={}
    WFt=_newest(_YD+f"wk{W_}/league_windows_*.txt")[0]
    if WFt:
        rows=[l.rstrip("\n").split("~") for l in open(WFt) if not l.startswith("#") and l.strip()]
        for i in range(0,len(rows)-1,2):
            a,b=rows[i],rows[i+1]
            for x,y_ in ((a,b),(b,a)):
                if _MYTEAM.get(x[0])==x[1]: OPPN[x[0]]=y_[1]
    for L in D["leagues"]: L["oppn"]=OPPN.get(L.get("lg"))
    D["across"]=[(n,v) for n,v in started.items() if len(v)>=2]
    D["pending"]=pend_all
    fin=(PM_MODE=="final" and pend_all==0 and MT>=last+_dp.timedelta(hours=3,minutes=30))
    D["state"]="final" if fin else "provisional"
    return D

PMD=pm_build()
print("POST-MORTEM",PMD.get("state"),"week",PMD.get("week"),"read",PMD.get("read"),"pending",PMD.get("pending"))

_PMB=ParagraphStyle("pmb",fontName="Pop",fontSize=8.3,leading=11.3,textColor=INKN)
_PMN=ParagraphStyle("pmn",fontName="Pop",fontSize=6.2,leading=8.3,textColor=GR)
_PMA=ParagraphStyle("pma",fontName="Pop",fontSize=8.5,leading=11.8,textColor=INKN)
_PMR=ParagraphStyle("pmr",fontName="PopB",fontSize=8.0,leading=11.0,textColor=TRED)
def _pmpara(c,t,st,x,ytop,w):
    p=Paragraph(t.replace("&","&amp;"),st);_,h=p.wrap(w,999);p.drawOn(c,x,ytop-h);return h
def _pmh(t,st,w):
    _,h=Paragraph(t.replace("&","&amp;"),st).wrap(w,999);return h
def _pl(p): return f"{p['name']} {p['pts']:.1f} on {p['proj']:.1f}"

def _body(L,oppn):
    out=[]
    d=L["me"]-L["op"]
    if not L["mp"] and not L["opn"]:
        out.append(("Won" if d>0 else "Lost" if d<0 else "Tied")+f" {L['me']:.1f}–{L['op']:.1f}.")
    else:
        out.append(("Ahead" if d>0 else "Behind" if d<0 else "Level")+(f" by {abs(d):.1f}." if d else "."))
        if L["mp"]: out.append(f"Still to play: {_list([p['name'] for p in L['mp']])} (Yahoo {sum(p['proj'] or 0 for p in L['mp']):.1f} combined).")
        out.append(f"{oppn} still has {_list([p['name'] for p in L['opn']])} (Yahoo {sum(p['proj'] or 0 for p in L['opn']):.1f})." if L["opn"] else f"{oppn} is done.")
    if L["up"]: out.append("Above Yahoo: "+", ".join(_pl(p) for p in L["up"])+".")
    if L["dn"]: out.append("Short of Yahoo: "+", ".join(_pl(p) for p in L["dn"])+".")
    if L["ob"] and L["ob"]["pts"]>=20: out.append(f"{oppn}'s best: {L['ob']['name']} {L['ob']['pts']:.1f}"+(f" (Yahoo {L['ob']['proj']:.1f})." if L['ob']['proj'] is not None else "."))
    if L["hurt"]: out.append("In the lineup while listed "+"; ".join(f"{p['status']}: {p['name']} {(p['pts'] or 0):.1f}" for p in L["hurt"])+".")
    return " ".join(out)

def postmortem_page(c,pg):
    from reportlab.lib.colors import Color
    D=PMD; W_=D.get("week") or WEEKN
    fin=D.get("state")=="final"
    if fin: tag="FINAL  ·  Yahoo read "+_fmt_t(D["read"])
    elif D.get("state")=="provisional": tag="PROVISIONAL — NOT COMPLETE  ·  Yahoo read "+_fmt_t(D["read"])
    else: tag="WAITING ON THE YAHOO READ"
    masthead(c,"POST-MORTEM",f"Week {W_}  ·  "+tag)
    y=Ht-MH-3-20
    section(c,y,"WHAT HAPPENED","Facts only, looking back. The week ahead belongs to the Outlook (Wednesday).",None)
    y-=19
    if D.get("state") in ("waiting","none"):
        last=D.get("read")
        y-=_pmpara(c,f"No Yahoo read of Week {W_} since the games were played"+(f" — the newest is {_fmt_t(last)}, from before kickoff." if last else ".")+
                   " The Post-Mortem fills in from the first read after the games. Nothing on this page is guessed.",_PMR,M,y,W-2*M)+9
    else:
        if not fin:
            why=("Monday night is still to play and Yahoo's stat corrections have not settled." if PM_MODE=="provisional" else
                 "Tuesday's final read has not come in — this is still the read below, with "+(f"{D['pending']} starter{'s' if D['pending']!=1 else ''} unscored." if D["pending"] else "Monday night not yet settled."))
            y-=_pmpara(c,"NOT COMPLETE. "+why+" The final edition follows Tuesday.",_PMR,M,y,W-2*M)+9
        IW=W-2*M-24
        def _mx(p,q,t): return Color(p.red*(1-t)+q.red*t,p.green*(1-t)+q.green*t,p.blue*(1-t)+q.blue*t)
        BH=54
        for L in D["leagues"]:
            k=L["k"]
            if L.get("missing"):
                hb=12;H_=BH
                gcard(c,M,y-H_,W-2*M,H_,LG[k]); txt(c,M+12,y-20,f"{L['lab']}: not in this Yahoo read.","PopB",8,TRED); y-=H_+7; continue
            oppn=L.get("oppn") or "The opponent"
            body=_body(L,oppn)
            hb=_pmh(body,_PMB,IW);H_=BH+8+hb+8
            gcard(c,M,y-H_,W-2*M,H_,LG[k])
            c.saveState();p=c.beginPath();p.roundRect(M,y-H_,W-2*M,H_,7);c.clipPath(p,stroke=0)
            c.linearGradient(M,y-BH,M,y,(INKN,_mx(INKN,LG[k],.42)),(0,1),extend=False)
            c.restoreState()
            hy=y-16;x=M+12;x+=lgchip(c,x,hy,k)+7
            txt(c,x,hy,L["full"],"PopB",8.8,PAPER);x+=c.stringWidth(L["full"],"PopB",8.8)+6
            if oppn!="The opponent": txt(c,x,hy,"vs "+oppn,"Pop",7.4,H("#C9CFDB"))
            s=L["stand"]
            st=(f"Entered the week {_rec(s['me'][2]).replace('-','–')}, {s['me'][0]}{_sfx2(int(s['me'][0]))} of {s['n']}." if s.get("me") else "Record entering the week: no standings read from before kickoff.")
            if k=="IV": st+="  Median game: not in this read."
            txt(c,M+12,y-38,st,"PopM",7.6,H("#E6E9EF"))
            dd=L["me"]-L["op"]
            if L["mp"] or L["opn"]: tag_,tc=f"IN PROGRESS  ·  {len(L['mp'])+len(L['opn'])} TO PLAY",TGLD
            else: tag_,tc=("WON",TGRN) if dd>0 else (("LOST",TRED) if dd<0 else ("TIED",TGLD))
            tw=c.stringWidth(tag_,"PopB",6.6)+12
            c.setFillColor(tc);c.rect(W-M-10-tw,hy-3.5,tw,12,stroke=0,fill=1)
            txt(c,W-M-10-tw/2,hy,tag_,"PopB",6.6,PAPER,"c")
            xr=W-M-10
            for v,lab,col in ((f"{L['op']:.1f}","OPP",H("#C9CFDB")),(f"{L['me']:.1f}",L["lab"],PAPER)):
                txt(c,xr,y-41,v,"Bebas",20,col,"r");wv=c.stringWidth(v,"Bebas",20)
                txt(c,xr-wv/2,y-50,lab,"PopB",5.2,H("#C9CFDB"),"c");xr-=wv+16
            txt(c,xr+8,y-41,"YAHOO","PopB",5.4,H("#8A93A6"),"r")
            _pmpara(c,body,_PMB,M+12,y-BH-8,IW)
            y-=H_+7
        if D.get("across"):
            bits=[]
            for n,v in sorted(D["across"],key=lambda x:-len(x[1]))[:2]:
                p=v[0][1]; same=all(abs((q["pts"] or 0)-(p["pts"] or 0))<.05 for _,q in v)
                bits.append(f"{n} started in {len(v)} leagues"+(f" and scored {p['pts']:.1f} in each" if same else ": "+", ".join(f"{q['pts']:.1f} in {l}" for l,q in v))
                            +(f" (Yahoo {p['proj']:.1f})." if p["proj"] is not None else "."))
            AC='<font name="PopB">ACROSS ALL FOUR</font>   '+" ".join(bits)
            ha=_pmh(AC,_PMA,IW-8)+12
            c.setFillColor(SOFT);c.rect(M,y-ha,W-2*M,ha,stroke=0,fill=1);c.setFillColor(SUN[1]);c.rect(M,y-ha,4,ha,stroke=0,fill=1)
            _pmpara(c,AC,_PMA,M+14,y-6,IW-8);y-=ha+9
        src=("Every number on this page is Yahoo's. Scores and starters: Dom's four Yahoo matchup pages, read "+_fmt_t(D["read"])+
             ". Records entering the week: Yahoo standings"+(", read "+_fmt_t(D["stand_read"]) if D.get("stand_read") else " — none read before kickoff")+
             ". Yahoo = Yahoo's projection before the game.")
        _pmpara(c,src,_PMN,M,y,W-2*M)
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,20,W-M,20)
    txt(c,M,11,"DARK KNIGHT DISPATCH","PopB",6.4,INKN)
    txt(c,M+c.stringWidth("DARK KNIGHT DISPATCH","PopB",6.4)+8,11,f"Week {W_}  ·  Post-Mortem, "+("final" if fin else "provisional")+"  ·  "+built_str(),"Pop",5.8,GR)
    txt(c,W-M,11,"Post-Mortem  ·  page "+str(pg),"Pop",5.8,GR,"r")
