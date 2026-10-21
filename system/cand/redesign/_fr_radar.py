# ================================================================== THE RADAR — v2, Dom Sun Sep 27 night
# The Radar is the NEWS page and the GATE. Every radar mark anywhere in the document points here for its writeup.
# Its inbound job: bring new men in. A free man enters the day his news breaks (splat), ages a day at a time, and
# falls off at 14 days unless fresh news resets him. Your own men with news get their writeup here too — not as
# drop candidates. Each row: points a game now vs forecast, workload a game now vs forecast, both against a tick =
# your weakest starter at that spot. News is the cause, workload the mechanism, points the answer.
_MINE={1:"A2",2:"B7",3:"C2",4:"D6"}
_NEED={1:{"QB":1,"RB":2,"WR":2,"TE":1},2:{"QB":2,"RB":2,"WR":3,"TE":1},   # from Dom's own live lineups:
       3:{"QB":1,"RB":2,"WR":2,"TE":1},4:{"QB":2,"RB":2,"WR":3,"TE":1}}   # II and IV superflex
_OUT=("(O)","(IR)","(IR-R)","(PUP-R)","(CEL)")
_RL={}
for ln in open(f"{_MK}/rosters_all_wk3_sun.txt"):
    if ":" not in ln or ln.startswith("#"): continue
    t,names=ln.split(":",1);_RL[t.strip()]=[n.strip() for n in names.split(";") if n.strip()]
_POS={k_:g_.sort_values("week").position.iloc[-1] for k_,g_ in _p.groupby("key")}
def _clean(n): return _re.sub(r"\(.*?\)","",n).lstrip("*").strip()
def _healthy(n): return not n.startswith("*") and not any(n.endswith(o) for o in _OUT)
_CTRI={(4,"brian robinson"):("gold","2")}          # claims written on the Call Sheet (item 2, DK IV)
FALLOFF=14
_TRADE=set()      # (league, name) — a trade man enters the Radar ONLY when Dom raises him by hand
def _games(k,key,pos,df=None):
    """per game, weeks on record: (workload, points in this league's scoring)"""
    qw,rw=WW[k];it,ra=_SC[k];out=[];df=_p if df is None else df
    for _,d in df[df.key==key].fillna(0).iterrows():
        w={"QB":d.attempts+qw*d.carries,"RB":d.carries+rw*d.targets}.get(pos,d.targets)
        pt=(.04*d.passing_yards+6*d.passing_tds+it*d.passing_interceptions+.1*d.rushing_yards+6*d.rushing_tds+ra*d.carries
            +.1*d.receiving_yards+6*d.receiving_tds+d.receptions)
        out.append((float(w),float(pt)))
    return out
def _fc(nw,g):
    """SAMPLE forecast rule until the Week 4 read: good news = back to his best week's workload; caution = holds;
    out = zero. Points follow workload at his own points-per-unit rate."""
    wn=sum(x[0] for x in g)/len(g);pn=sum(x[1] for x in g)/len(g)
    wf={"good":max(x[0] for x in g),"caution":wn,"bad":0.0}.get(nw["grade"],wn)
    pf=pn*(wf/wn) if wn>0 else 0.0
    return wn,wf,pn,pf
import sys as _sys2;_sys2.path.insert(0,"/home/claude/src/forecast");import fc_model as _FM
_FMF={}
def _fc_model(k,key,nw,g):
    """THE FORECAST MODEL (fc_model.py): recent games weighted most, his points-a-touch rate steadied toward the
    position's. News: out = zero. Good news gets a man ONTO the Radar but no longer lifts his forecast —
    in the Week 3 test that lift overshot all three good-news men (Etienne, Robinson, Ferguson).
    'Now' stays the plain Weeks 1-2 average, so the bar still reads now -> forecast."""
    if k not in _FMF: _FMF[k]=_FM.frame(k)
    wn=sum(x[0] for x in g)/len(g);pn=sum(x[1] for x in g)/len(g)
    m=_FM.forecast(_FMF[k],key,2,{"bad":"out"}.get(nw["grade"]))   # Week 3 test: the good-news lift overshot 3 of 3 — dropped
    if m is None: return _fc(nw,g)
    return wn,m["wl"],pn,m["pts"]
def _thin(k,pos,me_t):
    n=0;tot=0
    for t,names in _RL.items():
        if t[0]!="ABCD"[k-1] or t==me_t or t.endswith("99"): continue   # 99 = on waivers, no manager
        tot+=1;have=sum(1 for x in names if _healthy(x) and _POS.get(_norm(_clean(x)))==pos)
        if have<=_NEED[k][pos]: n+=1
    return n,tot
def _floor(k,D,pos):
    """the weakest starter at this spot: (name, workload a game, points a game)"""
    best=None
    for r in D["starts"]:
        if r[1] and r[3]==pos:
            g=_games(k,_norm(r[1]),pos)
            if not g: continue
            w=sum(x[0] for x in g)/len(g);pt=sum(x[1] for x in g)/len(g)
            if best is None or pt<best[2]: best=(r[1],w,pt)
    return best
def _last(n): return n.split()[-1] if not n.split()[-1].rstrip(".") in ("Jr","Sr","II","III") else n.split()[-2]
# ---- ACTUALS (Dom Mon Sep 28): what the man did in games played AFTER his news broke — the verdict on the forecast
_PA=_pd.read_csv("/home/claude/src/role_watch/data/stats_player_week_2026.csv",low_memory=False)
_PA=_PA[(_PA.season_type=="REG")&(_PA.week>=3)&_PA.player_display_name.notna()]
_GD=_pd.read_csv("/home/claude/src/role_watch/data/games.csv");_GD=dict(zip(_GD.game_id,_GD.gameday))
_PA=_PA.assign(key=_PA.player_display_name.map(_norm),gd=_PA.game_id.map(_GD))
def _act(k,key,pos,nw):
    m,d=(int(x) for x in nw["date"].split("/"))
    g=_games(k,key,pos,_PA[_PA.gd>f"2026-{m:02d}-{d:02d}"])
    if not g: return None
    return sum(x[0] for x in g)/len(g),sum(x[1] for x in g)/len(g),len(g)
ORG=H("#F7801E")                       # the ACTUAL bar — one orange everywhere, navy rim + the word inside
_TRK={"red":0,"gold":1,"green":2}
_NNAME={_norm(n):n for n in _json.load(open("/home/claude/src/wiremark/news_state.json"))["marks"]}
def radar(D,k,LC,top,groups=None,title="THE RADAR"):
    AC=ORG                                   # orange = ACTUAL on all four leagues (Dom Mon Sep 28: navy read as black — reversed)
    STL=H("#557391")                         # dull steel blue = the NOW / FORECAST body bar, every league
    BH=7.0;AH=4.2;CRM=H("#FBF7EF");ADK=H("#C25E0E")                            # body bar height; the orange actual straddles its top edge, half in, half out
    me_t=_MINE[k];own={_norm(_clean(x)) for t,v in _RL.items() if t[0]=="ABCD"[k-1] for x in v}
    rows_={_norm(r[1]):r for r in D["starts"]+D["bench"]+D["irs"] if r[1]}
    cin=[];yours=[]
    for nk,nw in _NEWS.items():
        if _nage(nw)>FALLOFF: continue
        key=next((kk for kk in _POS if kk==nk or kk.startswith(nk+" ")),nk);pos=_POS.get(key)
        if pos not in ("QB","RB","WR","TE"): continue
        g=_games(k,key,pos)
        if not g: continue
        wn,wf,pn,pf=_fc_model(k,key,nw,g);fl=_floor(k,D,pos)
        mine_r=rows_.get(key) or next((r for kk,r in rows_.items() if kk.startswith(nk)),None)
        rec=dict(key=key,nk=nk,nm=mine_r[1] if mine_r else _NNAME.get(nk,_DN.get(key,key)),tm=_TM.get(key,""),pos=pos,nw=nw,
                 wn=wn,wf=wf,pn=pn,pf=pf,fl=fl,row=mine_r,act=_act(k,key,pos,nw))
        rec["tri"]=(mine_r[7] if mine_r and len(mine_r)>7 else None) or _CTRI.get((k,nk))
        rec["how"]="Trade" if (k,nk) in _TRADE else ("Waiver wire" if any(_norm(_clean(x))==key or _norm(_clean(x)).startswith(nk) for x in _RL.get("ABCD"[k-1]+"99",[])) else "Free agent")
        if mine_r: yours.append(rec)                                   # his own men: every grade
        elif key not in own and nk not in own and nw["grade"]=="good": cin.append(rec)   # coming in: good news only
    na=max([int(t[1]) for t in [r_[7] for r_ in D["starts"]+D["bench"]+D["irs"] if len(r_)>7 and r_[7]]+[v for (kk,_),v in _CTRI.items() if kk==k] if str(t[1]).isdigit()]+[0])
    # AUTO-TRIANGLE: an available man whose actual beat the forecast
    for r in sorted(cin,key=lambda r:-(r["act"][1]-r["pf"]) if r["act"] else 0):
        if r["tri"] or not r["act"]: continue
        gap_=r["act"][1]-r["pf"]
        if gap_>=3: na+=1;r["tri"]=("red" if gap_>=6 else "gold",str(na));r["auto"]=True
    srt=lambda r:(_TRK.get(r["tri"][0],3) if r["tri"] else 3,-r["pf"])   # triangles first (red, gold, green), then forecast
    cin.sort(key=srt);yours.sort(key=srt)
    # ---------------- frame
    LN=D["name"]
    y=top;section(c,y,title,f"News that brings a player in, and news that moves a {LN} player",None)
    horizon(c,W-M,y+1.5,"NEWS READ FRI SEP 25  ·  ACTUALS THROUGH SUN SEP 27  ·  MODEL FORECASTS",align="r")
    CR=(M+2,M+20,M+104,M+120,M+140,M+172,0)          # the document's ONE player row: tri · name · STA · pos · team · marks
    P0,P1=M+276,M+376;WK0,WK1=M+396,M+496;RX=W-M-4
    allp=[v for r in cin+yours for v in (r["pn"],r["pf"],(r["fl"][2] if r["fl"] else 0),(r["act"][1] if r["act"] else 0))]
    st_=_tstep(max(allp+[10]));PMX=_math.ceil(max(allp+[10])/st_)*st_
    PX=lambda v:P0+min(v,PMX)/PMX*(P1-P0)
    NF=5.8;NW=P0-10-CR[1]                            # note lines stop short of the bars
    def heads(yy,inbound):
        rowhead(c,CR,yy)
        for v in range(0,int(PMX)+1,int(st_) if st_>=1 else 1): hdr(c,PX(v),yy,f"{v}","c")
        def khdr(x,lead):
            for t_,col in ((lead+" — ",GR),("ACTUAL",ADK),(" · ",GR),("NOW",STL),(" · ",GR),("FORECAST",INKN)):
                txt(c,x,yy+8,t_,"PopB",5.4,col);x+=c.stringWidth(t_,"PopB",5.4)
            return x
        khdr(P0,"POINTS");khdr(WK0,"WORKLOAD")
        for i_,t_ in enumerate(("0","25%","50%","75%","100%")): hdr(c,WK0+i_*(WK1-WK0)/4,yy,t_,"c")
        hdr(c,RX,yy+8,"GROWTH","r");hdr(c,RX,yy,"WORKLOAD","r")
    def grid(xs,y0,y1):
        c.saveState();c.setStrokeColor(LINE);c.setLineWidth(.4);c.setStrokeAlpha(.75)
        for xx in xs: c.line(xx,y0,xx,y1)
        c.restoreState()
    def abar(x0,va,s):
        """ACTUAL: thin orange band straddling the steel body's top edge. No word in it — the column header keys it.
        Its number rides at its end in dark orange, on a cream patch so no line ever runs through it."""
        yb=cur[0]+6.2-cur[1]+BH/2;wd=max(va-x0,.8)
        c.setFillColor(AC);c.setStrokeColor(INKN);c.setLineWidth(.35);c.rect(x0,yb-AH/2,wd,AH,stroke=1,fill=1)
        xe=va+2.2;sw=c.stringWidth(s,"PopB",6.2)
        c.setFillColor(CRM);c.rect(xe-1,yb-1.2,sw+2,6.0,stroke=0,fill=1)
        txt(c,xe,yb-.2,s,"PopB",6.2,ADK)
    def bar(x0,x1,vn,vf,tick,sn,sf):
        """Steel body: solid to NOW, faint tint on to the FORECAST, a crisp cap line where the forecast lands,
        the triangle tucked under it, a navy tick = weakest starter. No words inside any bar."""
        yb=cur[0]+6.2-cur[1];bh=BH;top=yb+bh/2+(AH/2 if cur[1] else 0);bot=yb-bh/2
        c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(x0,yb,x1,yb)
        for xx in (x0,x1): c.line(xx,yb-2,xx,yb+2)
        up=vf>=vn;lo,hi=(vn,vf) if up else (vf,vn)
        c.setFillColor(STL);c.rect(x0,bot,max(lo-x0,0),bh,stroke=0,fill=1)
        if hi-lo>.3:
            c.saveState();c.setFillColor(STL if up else ST["red"]);c.setFillAlpha(.30 if up else .22)
            c.rect(lo,bot,hi-lo,bh,stroke=0,fill=1);c.restoreState()
        c.setStrokeColor(INKN);c.setLineWidth(.9);c.setLineCap(0);c.line(vf,bot,vf,yb+bh/2)
        if tick is not None:
            c.setStrokeColor(INKN);c.setLineWidth(1.1);c.line(tick,bot-1.8,tick,top+1.2)
        th=4.2;tw=5.4;ty=bot-.8;c.setFillColor(INKN);p_=c.beginPath();p_.moveTo(vf,ty);p_.lineTo(vf+tw/2,ty-th);p_.lineTo(vf-tw/2,ty-th);p_.close()
        c.drawPath(p_,stroke=0,fill=1)
        ny_=ty-th-6.4;wf_=c.stringWidth(sf,"PopB",6.4);wn_=c.stringWidth(sn,"Pop",6.2)
        txt(c,vf,ny_,sf,"PopB",6.4,INKN,"c")
        if abs(vf-vn)<.5 and sn==sf: return
        gap_=(wf_+wn_)/2+3
        xn=vn if abs(vf-vn)>=gap_ else (vf-gap_ if up else vf+gap_)
        txt(c,xn,ny_,sn,"Pop",6.2,GR,"c")
    def amark(x,mid,how):
        """ACQUISITION MARKER — a marker in the marker column: F / W / T top to bottom, easiest to hardest.
        The open door gets the league tint, a bold letter and a check beside it; the eye reads down and stops there."""
        rh_=4.7;bw=9.8;top_=mid+rh_*1.5
        for i,lab in enumerate(("F","W","T")):
            ry=top_-(i+1)*rh_;on=(lab==how[0])
            if on:
                c.saveState();c.setFillColor(LC);c.setFillAlpha(.35);c.rect(x,ry,bw,rh_,stroke=0,fill=1);c.restoreState()
                c.setStrokeColor(INKN);c.setLineWidth(.8);c.setLineCap(1);c.setLineJoin(1)
                p_=c.beginPath();p_.moveTo(x+bw+1.4,ry+2.3);p_.lineTo(x+bw+2.6,ry+1.0);p_.lineTo(x+bw+4.8,ry+3.9);c.drawPath(p_,stroke=1,fill=0)
            txt(c,x+bw/2,ry+1.0,lab,"PopB" if on else "Pop",4.4,INKN if on else GR2,"c")
            if i: c.setStrokeColor(LINE);c.setLineWidth(.3);c.line(x,ry+rh_,x+bw,ry+rh_)
        c.setStrokeColor(GR);c.setLineWidth(.5);c.rect(x,top_-3*rh_,bw,3*rh_,stroke=1,fill=0)
    def wrap(s,font,wd=None):
        wd=wd or NW;out=[];cur_=""
        for w in s.split(" "):
            t=(cur_+" "+w).strip()
            if c.stringWidth(t,font,NF)<=wd or not cur_: cur_=t
            else: out.append(cur_);cur_=w
        return out+[cur_]
    def notes(r):
        nw=r["nw"];fl=r["fl"];pos=r["pos"]
        nt=nw["note"];s1=f"{nw['date']} — {nt[:1].upper()+nt[1:]}."
        wk=f"Workload {_fmt(r['wn'])} to {_fmt(r['wf'])}, points {r['pn']:.1f} to {r['pf']:.1f} — "
        if fl and _norm(fl[0])!=r["key"]:
            s2=wk+(f"clears {fl[0]}, the weakest {LN} {pos} starter ({fl[2]:.1f})." if r["pf"]>fl[2]
                   else f"short of {fl[0]}, the weakest {LN} {pos} starter ({fl[2]:.1f}).")
        elif fl: s2=wk+f"he is the weakest {LN} {pos} starter."
        else: s2=wk+f"no {LN} {pos} starter to measure against."
        return [("News:",wrap(s1,"Pop")),("Forecast:",wrap(s2,"Pop",RX-CR[1]-c.stringWidth("Forecast:  ","PopB",NF)))]   # the forecast line sits below the bar numbers — it may run full width
    def off(r): return 3 if r["act"] else 0
    def rh_of(r): return 35+off(r)+7.6*sum(len(l)-1 for _,l in notes(r))
    cur=[0,0]
    def row(yy,r,inbound):
        cur[0]=yy;cur[1]=off(r);nm,tm,pos,nw=r["nm"],r["tm"],r["pos"],r["nw"]
        rw=r["row"];stt=(rw[2] if rw else "") or ""
        cl=rw[5] if rw else None;sg=_sgof(nm,rw[6] if rw else None)
        tri=r["tri"]
        prow(c,CR,yy,_sn(nm,20),stt,pos,tm,cl,sg,tri,7.2,12,13)
        nmk=sum(1 for m in (cl,sg,TREND.get(nm)) if m);cp=_capof(tm);ax=CR[5]+nmk*MK_P-MK_P/2+1
        if cp: _cap(ax,yy+7.2*.36,cp[0],cp[1]);ax+=_capw()+4
        if inbound: amark(ax,yy+7.2*.36,r["how"])
        fl=r["fl"];yb=yy+6.2-off(r)
        grid([PX(v) for v in range(int(st_) if st_>=1 else 1,int(PMX)+1,int(st_) if st_>=1 else 1)],yy+13,yb-10.6)
        grid([WK0+i_*(WK1-WK0)/4 for i_ in (1,2,3)],yy+13,yb-10.6)
        bar(P0,P1,PX(r["pn"]),PX(r["pf"]),PX(fl[2]) if fl else None,f"{r['pn']:.1f}",f"{r['pf']:.1f}")
        if r["act"]: abar(P0,PX(r["act"][1]),f"{r['act'][1]:.1f}")
        wm=max(max(WPG[(k,pos)].values()),r["wn"],r["wf"],fl[1] if fl else 0,r["act"][0] if r["act"] else 0)
        WX_=lambda v:WK0+v/wm*(WK1-WK0)
        bar(WK0,WK1,WX_(r["wn"]),WX_(r["wf"]),WX_(fl[1]) if fl else None,_fmt(r["wn"]),_fmt(r["wf"]))
        if r["act"]: abar(WK0,WX_(r["act"][0]),_fmt(r["act"][0]))
        gp=(r["wf"]/r["wn"]-1)*100 if r["wn"]>0 else 0
        gs=f"+{gp:.0f}%" if gp>=.5 else (f"−{-gp:.0f}%" if gp<=-.5 else "0%")
        txt(c,RX,yy,gs,"PopB",7.6,ST["green"] if gp>=.5 else (ST["red"] if gp<=-.5 else GR),"r")
        ny=yy-10.5-off(r);lx=CR[1]
        for lab,lines in notes(r):
            txt(c,lx,ny,lab,"PopB",NF,INKN)
            for j,l in enumerate(lines):
                txt(c,lx+c.stringWidth("Forecast:  ","PopB",NF),ny,l,"Pop",NF,GR);ny-=7.6
        c.setStrokeColor(LINE);c.setLineWidth(.35);c.line(M+2,yy-rh_of(r)+13.6,W-M-2,yy-rh_of(r)+13.6)
    yy=y-22;FLOOR=int(__import__("os").environ.get("RFLOOR","72"));spill=[]
    def group(title,sub,items,inbound):
        nonlocal yy
        if yy-40<FLOOR: spill.append((title,sub,items,inbound));return
        txt(c,M+2,yy,title,"PopB",7.2,INKN)
        txt(c,M+2+c.stringWidth(title,"PopB",7.2)+8,yy,sub,"Pop",6.0,GR)
        if not items: yy-=14;txt(c,CR[1],yy,f"Nobody available in {LN} has good news in the last 14 days." if inbound else f"No {LN} player is in the news in the last 14 days.","Pop",6.6,GR);yy-=18;return
        yy-=19;heads(yy,inbound);yy-=17
        for i,r in enumerate(items):
            if yy-rh_of(r)<FLOOR: spill.append((title+" — CONTINUED",sub,items[i:],inbound));return
            row(yy,r,inbound);yy-=rh_of(r)
        yy-=6
    for g_ in (groups or [("COMING IN — AVAILABLE IN THIS LEAGUE",f"Gate: available in {LN}, GOOD news in the last 14 days, QB/RB/WR/TE. Highest forecast first; a triangle jumps the queue",cin,True),
               (f"{LN} — IN THE NEWS",f"Gate: on the {LN} roster, ANY news in the last 14 days. Highest forecast first; a triangle jumps the queue",yours,False)]): group(*g_)
    def legend(ky):
        x0=M+2;f6=6.0;x=x0
        txt(c,x,ky,"Legend:","PopB",6.2,INKN);x+=c.stringWidth("Legend:  ","PopB",6.2);xs=x
        c.setFillColor(AC);c.setStrokeColor(INKN);c.setLineWidth(.45);c.rect(x,ky+1.2,12,4.2,stroke=1,fill=1)
        t_="Actual — what he did in games since the news";txt(c,x+15,ky,t_,"Pop",f6,GR);x+=24+c.stringWidth(t_,"Pop",f6)
        c.setFillColor(STL);c.rect(x,ky-1.4,10,7.4,stroke=0,fill=1);txt(c,x+13,ky,"Now","Pop",f6,GR);x+=17+c.stringWidth("Now","Pop",f6)
        c.saveState();c.setFillColor(STL);c.setFillAlpha(.30);c.rect(x,ky-1.4,10,7.4,stroke=0,fill=1);c.restoreState()
        txt(c,x+13,ky,"Room to forecast","Pop",f6,GR);x+=20+c.stringWidth("Room to forecast","Pop",f6)
        c.setFillColor(INKN);p_=c.beginPath();p_.moveTo(x+3,ky+5);p_.lineTo(x+5.8,ky);p_.lineTo(x+.2,ky);p_.close();c.drawPath(p_,stroke=0,fill=1)
        txt(c,x+10,ky,"Forecast","Pop",f6,GR);x+=17+c.stringWidth("Forecast","Pop",f6)
        c.setStrokeColor(INKN);c.setLineWidth(1.1);c.line(x+2,ky-2,x+2,ky+6);t_=f"Weakest {LN} starter"
        txt(c,x+7,ky,t_,"Pop",f6,GR)
        txt(c,xs,ky-9,"Acquisition marker: F free agent · W waiver wire · T trade, easiest to hardest — the check marks the way in.  Growth = change in workload, now to forecast.  Every bar is per game.","Pop",f6,GR)
        txt(c,xs,ky-18,"Triangle on an available man with no claim behind it = his actual beat the forecast since the news: red by 6 points or more, gold by 3 or more.","Pop",f6,GR)
        txt(c,xs,ky-27,"Forecasts: the scan's own model — latest games count most. Good news puts a man here but doesn't lift his number; out = zero. Workload bars run to the top load.","Pop",f6,GR)
    if spill and all(not it for _,_,it,_ in spill):     # an empty group never earns a page of its own — its one sentence rides here
        for t_,_,_,inb in spill:
            txt(c,M+2,yy+1,t_.replace(" — CONTINUED",""),"PopB",7.2,INKN)
            txt(c,M+2+c.stringWidth(t_.replace(" — CONTINUED",""),"PopB",7.2)+8,yy+1,f"Nobody available in {LN} has good news in the last 14 days." if inb else f"No {LN} player is in the news in the last 14 days.","Pop",6.6,GR);yy-=12
        spill=[]
    legend(max(yy+2,FLOOR-6) if not spill else FLOOR-6)
    return spill
def radar_cont(D,k,LC,spill,FP):
    """the Radar runs long: it continues on its own page behind The League — same rows, same header, same legend"""
    masthead(c,"THE LEAGUE  ·  "+D["name"],"The Radar, continued from the page before")
    more=radar(D,k,LC,Ht-122,groups=spill,title="THE RADAR — CONTINUED")
    footer(c,FP,"The League · "+D["name"]+" · Radar continued");c.showPage()
    if more: radar_cont(D,k,LC,more,FP)
