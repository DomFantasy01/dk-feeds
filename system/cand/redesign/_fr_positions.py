# ================================================================== YOUR POSITIONS — one page per league, SIX panels (v7b)
# Dom's design, Sat Sep 26 night: "the truth on these guys isn't just the points."
# Across = what he's worth: ESPN rest-of-season points a game.  Up = what his team thinks of him: workload change,
# Week 1 to Week 2 (snap share + touches; quarterbacks: snap share + throws and runs). Kickers and defenses have no
# workload, so their up axis is what Vegas expects: team points (kickers) or points against (defenses), Weeks 3–4.
# Rank tiers, Dom Sat night: green = top six at the position on BOTH axes (playoff quality), gold = seven to twelve
# (holds a slot). Workload a game: QB throws + 3x runs; RB runs + 2x targets; WR/TE targets. K/DEF: Vegas, same ranks.
# Radar arcs over a dot = news this week (green good, gold caution, red bad). Red underline under a team = bad offense.
import sys as _sys2
_sys2.path.insert(0,"/home/claude/cand")
with contextlib.redirect_stdout(io.StringIO()):
    from batch7 import arcs7 as _arcs7, sig7 as _sig7, tight as _tight
    from marklib import INK as _INK
import json as _json, math as _math
_MK="/home/claude/src/mkt"
_GONE=eval(open(f"{_MK}/yahoo_gone_wk3_fri.txt").read().split("\n")[0])
_ROST={}
for ln in open(f"{_MK}/rosters_all_wk3_sun.txt"):
    if ":" not in ln or ln.startswith("#"): continue
    t,names=ln.split(":",1);lg={"A":1,"B":2,"C":3,"D":4}.get(t[0])
    if lg: _ROST.setdefault(lg,set()).update(_re.sub(r"\(.*?\)","",n).lstrip("*").strip() for n in names.split(";"))
_DROP=eval(open(f"{_MK}/dropped_wk3_sun.txt").read())
_NEWS={_norm(n):v for n,v in _json.load(open("/home/claude/src/wiremark/news_state.json"))["marks"].items()}
import datetime as _dt
_NREF=_dt.date(2026,9,26)                      # the scan's read day: Saturday. Age counts from here (Etienne 9/25 = 01)
def _nage(nw):
    m,d=(int(x) for x in nw["date"].split("/"));return (_NREF-_dt.date(2026,m,d)).days
def _sgof(nm,row_sg=None):
    """the WHOLE radar mark, every page: grade color + age under the arcs, splat only the day it breaks.
    A mark already set on the man's line item wins, so it reads identically wherever he appears."""
    if row_sg: return row_sg
    nw=_NEWS.get(_norm(nm))
    if not nw: return None
    a=_nage(nw);return (nw["grade"],None if a<=0 else f"{a:02d}")
# ---- workload a game, every man in the league at the position (weeks on record)
# Dom Mon Sep 28: Positions runs on every week on record (1–3). The Radar keeps its own Weeks 1–2 "now" (_p) on purpose.
_p12=_p
_pP=_pd.read_csv("/home/claude/src/role_watch/data/stats_player_week_2026.csv",low_memory=False)
_pP=_pP[(_pP.season_type=="REG")&_pP.week.isin([1,2,3])&_pP.player_display_name.notna()]
_pP=_pP.assign(key=_pP.player_display_name.map(_norm),opps=_pP.carries.fillna(0)+_pP.targets.fillna(0))
_p=_pP
_sP=_pd.read_csv("/home/claude/src/role_watch/data/snap_counts_2026.csv");_sP=_sP[(_sP.game_type=="REG")&_sP.week.isin([1,2,3])&_sP.player.notna()]
_sP=_sP.assign(key=_sP.player.map(_norm))
# Weights come from the data, not a round guess: actual fantasy points per run vs per throw (QB) and per target vs
# per carry (RB), Weeks 1-2, every man at the position, priced in that league's scoring. DK I-III: full PPR, pass TD 6,
# INT -2, +0.25 a rush attempt. DK IV: INT -1, no rush-attempt bonus.
_SC={1:(-2,.25),2:(-2,.25),3:(-2,.25),4:(-1,0.0)}
def _wts(k):
    it,ra=_SC[k];q=_p[_p.position=="QB"].fillna(0);r=_p[_p.position=="RB"].fillna(0)
    pp=(.04*q.passing_yards+6*q.passing_tds+it*q.passing_interceptions).sum()/q.attempts.sum()
    rp=(.1*q.rushing_yards+6*q.rushing_tds+ra*q.carries).sum()/q.carries.sum()
    rc=(.1*r.rushing_yards+6*r.rushing_tds+ra*r.carries).sum()/r.carries.sum()
    rt=(.1*r.receiving_yards+6*r.receiving_tds+r.receptions).sum()/r.targets.sum()
    return round(rp/pp,1),round(rt/rc,1)
WW={k:_wts(k) for k in _SC};WPG={}
for _k,(_qw,_rw) in WW.items():
    _WF={"QB":lambda d,w=_qw:d.attempts.fillna(0)+w*d.carries.fillna(0),"RB":lambda d,w=_rw:d.carries.fillna(0)+w*d.targets.fillna(0),
         "WR":lambda d:d.targets.fillna(0),"TE":lambda d:d.targets.fillna(0)}
    for _ps,_fn in _WF.items():
        _d=_p[_p.position==_ps];_d=_d.assign(w=_fn(_d))
        WPG[(_k,_ps)]={k_:float(g_.w.mean()) for k_,g_ in _d.groupby("key")}
_DN={k_:g_.player_display_name.iloc[-1] for k_,g_ in _p.groupby("key")}
_TM={k_:g_.sort_values("week").team.iloc[-1] for k_,g_ in _p.groupby("key")}
_RMED=sorted(remaining(t,18) for t in SCH)[len(SCH)//2]
_PC={"1":"QB","2":"RB","3":"WR","4":"TE","5":"K","16":"DEF"};PPG={}
for _e in open("/home/claude/src/mkt/espn_season_wk3_fri.txt").read().strip().split(";"):
    _f=_e.split("|");_ps=_PC.get(_f[1])
    if not _ps: continue
    _t=_TM.get(_norm(_f[0]));_r=remaining(_t,18) if _t in SCH else _RMED
    if _r: PPG.setdefault(_ps,{})[_f[0]]=(float(_f[2])-float(_f[3]))/_r
_k=_p[_p.position=="K"].fillna(0)
KW=round((3*_k.fg_made.sum()/max(1,_k.fg_att.sum()))/(_k.pat_made.sum()/max(1,_k.pat_att.sum())),1)   # a field-goal try is worth this many PATs
_kg=_k.assign(w=_k.pat_att+KW*_k.fg_att).groupby("team").w.mean()
KPG={t:float(v) for t,v in _kg.items()}
_dg=_p.fillna({"def_sacks":0,"def_interceptions":0,"fumble_recovery_opp":0})
_dg=_dg.assign(w=_dg.def_sacks+_dg.def_interceptions+_dg.fumble_recovery_opp).groupby(["team","week"]).w.sum().groupby("team").mean()
DPG={t:float(v) for t,v in _dg.items()}
_p=_p12                                       # the Radar reads Weeks 1–2 again from here on
_AK={"LA":"LAR","LAR":"LA","WSH":"WAS","WAS":"WSH"}
def _nth(vals,n):
    v=sorted(vals,reverse=True);return v[min(n,len(v))-1] if v else 0.0
# ---- Vegas, Weeks 3–4: points each team is expected to score / allow
_g=_pd.read_csv("/home/claude/src/role_watch/data/games.csv");_g=_g[(_g.season==2026)&_g.week.isin([3,4])].dropna(subset=["total_line"])
_FOR={};_AG={}
for _,r in _g.iterrows():
    hi=(r.total_line+r.spread_line)/2;ai=(r.total_line-r.spread_line)/2
    _FOR.setdefault(r.home_team,[]).append(hi);_AG.setdefault(r.home_team,[]).append(ai)
    _FOR.setdefault(r.away_team,[]).append(ai);_AG.setdefault(r.away_team,[]).append(hi)
_FOR={t:sum(v)/len(v) for t,v in _FOR.items()};_AG={t:sum(v)/len(v) for t,v in _AG.items()}
_VMEAN=sum(_FOR.values())/len(_FOR)
def _up(k,pos,nm,tm):
    """the up axis, per position. None = no Week 2 snaps on record"""
    if pos=="K": return KPG.get(tm,KPG.get(_AK.get(tm,""),None))
    if pos=="DEF": return DPG.get(tm,DPG.get(_AK.get(tm,""),None))
    return WPG[(k,pos)].get(_norm(nm))
def _free(k,pos):
    out=[]
    for ln in open(f"{_MK}/yahoo_dk{k}.txt"):
        p0,rest=ln.split("|",1)
        if p0!=pos: continue
        for it in rest.strip().split(";"):
            f=it.split("|")
            if len(f)<5: continue
            nm,tm=f[0],f[1];nm={_norm(k_):k_ for k_ in ESPN}.get(_norm(nm),nm)   # Yahoo drops suffixes ESPN keeps
            if _norm(nm) in {_norm(x) for x in _GONE.get(k,[])} or _norm(nm) in {_norm(x) for x in _ROST.get(k,set())}: continue
            out.append((nm,tm if tm in SCH else {"LA":"LAR","LAR":"LA","WSH":"WAS"}.get(tm,tm)))
    seen={_norm(n) for n,_ in out}
    for nm in _DROP.get("ABCD"[k-1],[]):                       # dropped since Friday: back on the wire today
        nm={_norm(k_):k_ for k_ in ESPN}.get(_norm(nm),nm)
        if _norm(nm) in seen or nm not in PPG.get(pos,{}) or _norm(nm) in {_norm(x) for x in _ROST.get(k,set())}: continue
        tm=_TM.get(_norm(nm))
        if tm: out.append((nm,tm))
    return out
def _trend(nm):
    """usage direction: the scan's TREND mark where set, else first-to-latest snap share (5-point threshold)"""
    if nm in TREND: return TREND[nm]
    g=_sP[_sP.key==_norm(nm)].sort_values("week")        # Weeks 1–3 of snaps
    if len(g)<2: return None
    d=float(g.offense_pct.iloc[-1])-float(g.offense_pct.iloc[0])
    return 1 if d>=.05 else -1 if d<=-.05 else None
def _arrow(x,y,d):
    """trend arrow straight through the dot: green up, red down, white halo so it reads on any fill"""
    k=ST["green"] if d>0 else ST["red"];f=1 if d>0 else -1;L_=4.0;h=1.8
    for col,w in ((CARD,1.7),(k,1.0)):
        c.saveState();c.setStrokeColor(col);c.setLineWidth(w);c.setLineCap(1);c.setLineJoin(1)
        p=c.beginPath();p.moveTo(x,y-L_*f);p.lineTo(x,y+L_*f);c.drawPath(p,stroke=1,fill=0)
        p=c.beginPath();p.moveTo(x-h,y+(L_-h)*f);p.lineTo(x,y+L_*f);p.lineTo(x+h,y+(L_-h)*f);c.drawPath(p,stroke=1,fill=0)
        c.restoreState()
POSN={"QB":"QUARTERBACKS","RB":"RUNNING BACKS","WR":"RECEIVERS","TE":"TIGHT ENDS","K":"KICKERS","DEF":"DEFENSES"}
def UPLAB(k,pos):
    qw,rw=WW[k]
    return {"QB":f"THROWS + {qw:g}x RUNS A GAME","RB":f"RUNS + {rw:g}x TARGETS A GAME","WR":"TARGETS A GAME","TE":"TARGETS A GAME",
            "K":f"PATS + {KW:g}x FG TRIES A GAME","DEF":"SACKS + TAKEAWAYS A GAME"}[pos]
def _tstep(span):
    raw=span/4.0
    for s_ in (1,2,2.5,5,10,20,25,50,100):
        if s_>=raw: return s_
    return 100
def _fmt(v):
    v=abs(v);return str(int(round(v))) if abs(v-round(v))<1e-6 else f"{v:.1f}"
PS=5.4;MG=8.6;MP=11.0      # name size; mark size and pitch on the plate (line items: 7.2 / 12 / 17, same ratio)
def _marks_w(cl,sg,tr): return MP*sum(1 for m in (cl,sg,tr) if m)
def _plate(x,y,r,lab,tm,cl,sg,tr,std=False,tag=None,tagc=None,edge=None,cap=None):
    """Dom Sun, batch 2: see-through plate, one plain name size for everyone, team on every plate (green underline =
    strong team, red = weak, nothing = middle), then the line items' three marks — cluster, radar, trend — riding right
    of the name and sliding left when one is missing. A dotted leader runs back to the dot when the plate moves."""
    fnt="PopM";sz=PS;tw=c.stringWidth(lab,fnt,sz);gap=c.stringWidth("  ",fnt,sz)
    aw=c.stringWidth(tm,fnt,sz) if tm else 0;mw=_marks_w(cl,sg,tr)+((_capw()+1.5) if cap else 0);px=2.2
    TG=tag or STD_T;TC=tagc or DKG;tg=std or bool(tag)
    sw=c.stringWidth(TG,"PopB",sz*.82)+c.stringWidth(" ",fnt,sz) if tg else 0
    w=sw+tw+(gap+aw if tm else 0)+(1.5+mw if mw else 0)+2*px;h=sz+(5.6 if sg else 3.6)
    cands=[]
    for d in (0,5,10,15,20,26,33,40,48,56,64,74,86,100):
        for s_ in ((1,) if d==0 else (1,-1)):
            cands+=[(x+r+3,y-h/2+s_*d),(x-r-3-w,y-h/2+s_*d)]
        for sh in (0,-.35,.35,-.7,.7):
            cands+=[(x-w/2+sh*w,y+r+3+d),(x-w/2+sh*w,y-r-3-h-d)]
    cands.sort(key=lambda q:((q[0]+w/2-x)**2*.5+(q[1]+h/2-y)**2))       # nearest first
    def hit(bx,by):
        cxl,cyl=bx+w/2,by+h/2;dm=(cxl-x)**2+(cyl-y)**2
        if any(((cxl-ox)**2+(cyl-oy)**2)<dm*.8 for ox,oy in DOTS if (ox,oy)!=(x,y)): return True
        if bx<BOUND[0] or bx+w>BOUND[1] or by<BOUND[2] or by+h>BOUND[3]: return True
        for (ox,oy,ow,oh) in OBST:
            if bx<ox+ow+1 and bx+w>ox-1 and by<oy+oh+1 and by+h>oy-1: return True
        return False
    def cost(bx,by):                                                  # no clean room: least overlap wins
        if bx<BOUND[0] or bx+w>BOUND[1] or by<BOUND[2] or by+h>BOUND[3]: return 1e9
        return sum(max(0,min(bx+w,ox+ow)-max(bx,ox))*max(0,min(by+h,oy+oh)-max(by,oy)) for ox,oy,ow,oh in OBST)
    for bx,by in cands:
        if not hit(bx,by): break
    else: bx,by=min(cands,key=lambda q:cost(*q))
    cx_,cy_=min(max(x,bx),bx+w),min(max(y,by),by+h)
    dd=((cx_-x)**2+(cy_-y)**2)**.5
    if dd>r+6:
        ux,uy=(cx_-x)/dd,(cy_-y)/dd
        c.saveState();c.setStrokeColor(GR);c.setLineWidth(.6);c.setLineCap(1);c.setDash(.1,1.6)
        c.line(x+ux*(r+1.2),y+uy*(r+1.2),cx_,cy_);c.restoreState()
    c.saveState();c.setStrokeColor(TC if tg else (edge or alpha(GR,.6)));c.setLineWidth(.9 if (tg or edge) else .5)
    c.roundRect(bx,by,w,h,1.8,stroke=1,fill=0);c.restoreState()       # outline only: the bands show through
    ty=by+(3.6 if not sg else 3.2)/2+sz*.14;tx=bx+px
    if tg: txt(c,tx,ty+.3,TG,"PopB",sz*.82,TC);tx+=sw
    txt(c,tx,ty,lab,fnt,sz,INKN);tx+=tw
    if tm:
        tx+=gap;txt(c,tx,ty,tm,fnt,sz,GR)
        k_=ST["green"] if tm in TOP else ST["red"] if tm in BOT else None
        if k_: c.setStrokeColor(k_);c.setLineWidth(.8);c.line(tx,ty-1.2,tx+aw,ty-1.2)
        tx+=aw
    mid=ty+sz*.36;mx=tx+1.5+MP/2
    if cl: _tight(c,mx-1.5,mid,MG,cl,True);mx+=MP
    if sg: _sig7(c,mx,mid-.26*MG,MG,sg[0],sg[1]);mx+=MP
    if tr: _TRG(c,mx,mid,MG*.95,tr);mx+=MP
    if cap: _cap(mx-MP/2+.5,mid,cap[0],cap[1])
    OBST.append((bx,by,w,h))
CORN={"work":("ROLE AHEAD OF POINTS","WHERE YOU WANT THEM","NEITHER","POINTS AHEAD OF ROLE"),
      "vegas":("GOOD GAMES, LOW SCORER","WHERE YOU WANT THEM","NEITHER","GOOD SCORER, HARD GAMES")}
GOLD=ST["gold"];GREEN=ST["green"];FAG=H("#5C677D");_TRG=trend;DKG=H("#A8740A")
def _blot(x,y,r,fill,stroke=None,lw=1.1):
    """Dom Sun: the glossy ball — a plain dot with a small highlight up-left. Centre is the data point.
    Dom Sun: the standard is a filled dark-gold ball too (DKG) — dark enough to hold inside the gold band."""
    c.saveState()
    if fill is not None: c.setFillColor(fill)
    if stroke is not None: c.setStrokeColor(stroke);c.setLineWidth(lw)
    c.circle(x,y,r,stroke=1 if stroke is not None else 0,fill=1 if fill is not None else 0)
    if fill is not None:
        c.setFillColor(alpha(CARD,.55));c.circle(x-r*.33,y+r*.33,r*.32,stroke=0,fill=1)
    c.restoreState()
# ---- the schedule capsule: long left = rest of season (Weeks 4-14), short right = playoffs (15-17), paper gap
CAPH=6.4;CAPF=4.3
CAPT={"green":H("#136B31"),"gold":H("#7A5406"),"red":H("#9E2219")}   # Dom Sun: soft wash, dark letters
def _capw(): return c.stringWidth("ROS","PopB",CAPF)+3.6+.9+c.stringWidth("PO","PopB",CAPF)+3.0
def _cap(x,y,g1,g2):
    """x = left edge, y = centre line. g1/g2 = 'green'|'gold'|'red'."""
    w1=c.stringWidth("ROS","PopB",CAPF)+3.6;w2=c.stringWidth("PO","PopB",CAPF)+3.0;gp=.9;W_=w1+gp+w2;h=CAPH;b=y-h/2
    for (cx0,cw,g,t) in ((x,w1,g1,"ROS"),(x+w1+gp,w2,g2,"PO")):
        c.saveState();p=c.beginPath();p.rect(cx0,b-1,cw,h+2);c.clipPath(p,stroke=0,fill=0)
        c.setFillColor(alpha(ST[g],.28));c.setStrokeColor(alpha(ST[g],.85));c.setLineWidth(.5)
        c.roundRect(x+.25,b+.25,W_-.5,h-.5,h/2,stroke=1,fill=1);c.restoreState()
        txt(c,cx0+cw/2,b+h/2-CAPF*.36,t,"PopB",CAPF,CAPT[g],"c")
def _sgrade(tm,ws):
    tm={"LAR":"LA","WSH":"WAS"}.get(tm,tm)
    if tm not in SCH: return None
    n=sum((SCH[tm].get(w) in SOFTD)-(SCH[tm].get(w) in TOUGH) for w in ws if SCH[tm].get(w))
    return "green" if n>=2 else "red" if n<=-2 else "gold"
def _capof(tm):
    a,b=_sgrade(tm,range(4,15)),_sgrade(tm,(15,16,17))
    return (a,b) if a and b else None
_NICK={"Cardinals":"ARI","Falcons":"ATL","Ravens":"BAL","Bills":"BUF","Panthers":"CAR","Bears":"CHI","Bengals":"CIN","Browns":"CLE",
 "Cowboys":"DAL","Broncos":"DEN","Lions":"DET","Packers":"GB","Texans":"HOU","Colts":"IND","Jaguars":"JAX","Chiefs":"KC","Raiders":"LV",
 "Chargers":"LAC","Rams":"LA","Dolphins":"MIA","Vikings":"MIN","Patriots":"NE","Saints":"NO","Giants":"NYG","Jets":"NYJ","Eagles":"PHI",
 "Steelers":"PIT","49ers":"SF","Seahawks":"SEA","Buccaneers":"TB","Titans":"TEN","Commanders":"WAS"}
STD_T="STANDARD"
def inote(x,y,w,lab,s,sz=6.2,lead=8.2):
    """bold label and text on one line, wrapping under the text"""
    txt(c,x,y,lab+":","PopB",sz,INKN);ix=x+c.stringWidth(lab+":  ","PopB",sz);line=""
    for wd in s.split():
        t=(line+" "+wd).strip()
        if c.stringWidth(t,"Pop",sz)>w-(ix-x): txt(c,ix,y,line,"Pop",sz,INKN);y-=lead;line=wd
        else: line=t
    if line: txt(c,ix,y,line,"Pop",sz,INKN);y-=lead
    return y-1
def position_page(D):
    k=D["k"];LC=LG[RN[k]];FP=D["page"]+3;LG_=D["name"]
    masthead(c,"POSITIONS  ·  "+LG_,LG_+" players and the five best free agents — What he's worth, against what his team thinks of him")
    PM=22;top=Ht-110;gap=12;gw_=(W-2*PM-gap)/2;ph=212   # Dom Sun: bigger panels, still six
    for i,pos in enumerate(("QB","RB","WR","TE","K","DEF")):
        x0=PM+(i%2)*(gw_+gap);yT=top-(i//2)*ph;veg=pos in ("K","DEF")
        if pos=="K" and not any(r[3]=="K" for r in D["starts"]):
            txt(c,x0,yT,POSN[pos],"Bebas",16,INKN)
            c.setFillColor(SOFT);c.roundRect(x0+30,yT-80,gw_-34,40,4,stroke=0,fill=1)
            txt(c,x0+30+(gw_-34)/2,yT-63,"No kicker slot in this league.","PopM",7.2,GR,"c");continue
        pts=[];nodata=[]
        mine=D["starts"]+D["bench"]
        for r in mine:
            nm,stt,ps,tm=r[1],r[2],r[3],r[4]
            if not nm or ps!=pos or stt=="O" or nm not in ESPN: continue
            fin=r in D["starts"] and len(r)>11 and r[11]
            u=_up(k,pos,nm,tm)
            nd=u is None
            if nd: nodata.append(nm);u=0.0
            sg=_sgof(nm,r[6] if len(r)>6 else None)
            pts.append([nm,tm,"start" if r in D["starts"] else "bench",float(rosg(nm,tm)),u,fin,nd,r[5] if len(r)>5 else None,sg])
        fa=[];mine_={r[1] for r in D["starts"]+D["bench"]+D["irs"] if r[1]}
        for nm,tm in _free(k,pos):
            if nm in mine_ or nm not in ESPN or tm not in SCH: continue
            u=_up(k,pos,nm,tm)
            nw=_NEWS.get(_norm(nm))
            fa.append([nm,tm,"free",float(rosg(nm,tm)),0.0 if u is None else u,False,u is None,None,_sgof(nm)])
        fa=sorted(fa,key=lambda p:-p[3]);keep=fa[:5]
        keep+=[p for p in fa[5:] if (_NEWS.get(_norm(p[0])) or {}).get("grade")=="good"]   # good news earns a dot outside the five
        fa=keep
        nodata+=[p[0] for p in fa if p[6]];pts+=fa
        for p in pts: p.append(False)
        ld=max(PPG.get(pos,{}).items(),key=lambda t:t[1],default=None)
        if ld:
            ln_=ld[0];hit_=[p for p in pts if _norm(p[0])==_norm(ln_)]
            if hit_: hit_[0][9]=True
            else:
                ltm=_NICK.get(ln_) if pos=="DEF" else _TM.get(_norm(ln_))
                u=_up(k,pos,ln_,ltm) if ltm else None
                pts.append([ln_,ltm,"std",ld[1],0.0 if u is None else u,False,u is None,None,None,True])
        # ---- scales: the whole position; tier marks from the league's 6th and 12th best
        mx0,mx1=x0+25,x0+gw_-1;my1=yT-9;my0=my1-137
        allx=list(PPG.get(pos,{}).values())
        ally=list((KPG if pos=="K" else DPG if pos=="DEF" else WPG[(k,pos)]).values())
        x6,x12=_nth(allx,6),_nth(allx,12);y6,y12=_nth(ally,6),_nth(ally,12)
        xs=[p[3] for p in pts] or [0,10]
        xlo=max(0,int(min(xs+[x12]))-1);xhi=int(max(xs+[max(allx or [10])]))+2
        yv=[p[4] for p in pts if not p[6]]
        ylo=min(yv+[y12]);yhi=max(yv+[max(ally or [1])]);pad=.08*(yhi-ylo or 1);ylo-=pad;yhi+=pad
        if not veg: ylo=min(0.0,ylo)
        for p in pts:
            if p[6]: p[4]=ylo
        XM=lambda v:mx0+(v-xlo)/(xhi-xlo)*(mx1-mx0);YM=lambda v:my0+6+(v-ylo)/(yhi-ylo)*(my1-my0-12)
        starts=[p for p in pts if p[2]=="start"]
        bar=min(starts,key=lambda p:p[3]) if starts else None
        xs_=bar[3] if bar else None
        txt(c,x0,yT,POSN[pos],"Bebas",16,INKN)
        c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.6);c.rect(mx0-4,my0-2,mx1-mx0+8,my1-my0+4,stroke=1,fill=1)
        L,R_,B,T=mx0-4,mx1+4,my0-2,my1+2
        cl=lambda v,a,b:max(a,min(b,v))
        gx,gy=cl(XM(x6),L,R_),cl(YM(y6),B,T);yx,yy=cl(XM(x12),L,R_),cl(YM(y12),B,T)
        c.setFillColor(alpha(GOLD,.24));c.rect(yx,yy,R_-yx,T-yy,stroke=0,fill=1)      # seven to twelve
        c.setFillColor(CARD);c.rect(gx,gy,R_-gx,T-gy,stroke=0,fill=1)
        c.setFillColor(alpha(GREEN,.22));c.rect(gx,gy,R_-gx,T-gy,stroke=0,fill=1)     # top six
        c.setLineWidth(.9)                                                            # Dom Sun: thin dark band edges
        for ex,ey,col in ((yx,yy,DKG),(gx,gy,GREEN)):
            c.setStrokeColor(col)
            if ex>L+.5: c.line(ex,max(ey,B),ex,T)
            if ey>B+.5: c.line(max(ex,L),ey,R_,ey)
        bx=XM(xs_) if bar else None
        for v in range(xlo,xhi+1,2 if xhi-xlo<=14 else 4):
            txt(c,XM(v),my0-8.5,str(v),"PopM",5.2,GR,"c")
        hdr(c,(mx0+mx1)/2,my0-16,"POINTS A GAME, REST OF SEASON","c")
        c.saveState();c.translate(x0+5,(my0+my1)/2);c.rotate(90);hdr(c,0,0,UPLAB(k,pos),"c");c.restoreState()
        st_=_tstep(yhi-ylo);v=_math.ceil(ylo/st_)*st_
        while v<=yhi+1e-9:
            yy_=YM(v)
            if B<=yy_<=T:
                txt(c,mx0-6,yy_-1.9,_fmt(v),"PopM",5.2,GR,"r")
                c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(L-2,yy_,L,yy_)
            v+=st_
        OBST.clear();BOUND[:]=[L+1,R_-1,B+1,T-1]
        # weakest-starter line cut (Dom Sun: read as a judgment on him)
        # ---- dots
        MD=swarm([(XM(p[3]),YM(p[4]),3.4,p) for p in pts],4.6)
        DOTS[:]=[(x,y) for x,y,_,_ in MD]
        for x,y,r_,p in MD:
            OBST.append((x-r_-2,y-r_-2,2*r_+4,2*r_+4))
        def zone_(xx,yy_):
            if xx>=gx and yy_>=gy: return "g"
            if xx>=yx and yy_>=yy: return "y"
            return "w"
        def blab(lab,col,z,cands,sz=5.4):
            wl=c.stringWidth(lab,"PopB",sz);h=sz
            for bx_,by_ in cands:
                if bx_<L+2 or bx_+wl>R_-2 or by_<B+2 or by_+h>T-2: continue
                if not all(zone_(a,b)==z for a in (bx_-1,bx_+wl+1) for b in (by_-1,by_+h+1)): continue
                if any(bx_-1<ox+ow and bx_+wl+1>ox and by_-1<oy+oh and by_+h+1>oy for ox,oy,ow,oh in OBST): continue
                txt(c,bx_,by_+.6,lab,"PopB",sz,col);OBST.append((bx_-1,by_-1,wl+2,h+2));return True
        _w=lambda t:c.stringWidth(t,"PopB",5.4)
        t1,t2,t3="TOP SIX","7TH TO 12TH","OUTSIDE TOP 12"
        blab(t1,GREEN,"g",[(R_-4-_w(t1)-dx,T-9-dy) for dy in range(0,60,4) for dx in range(0,90,6)])
        ok2=blab(t2,DKG,"y",[(gx-4-_w(t2)-dx,T-9-dy) for dy in range(0,40,4) for dx in range(0,120,6)]+
                        [(R_-4-_w(t2)-dx,gy-9-dy) for dy in range(0,40,3) for dx in range(0,90,6)])
        if not ok2:                                           # thin strip: center it on the gold, shrinking to fit
            for sz_ in (5.4,4.8,4.3):
                wl_=c.stringWidth(t2,"PopB",sz_);cx_=(gx+R_)/2-wl_/2;cy_=(yy+gy)/2-sz_/2
                vx_=(yx+gx)/2-wl_/2;vy_=(gy+T)/2-sz_/2
                cand=[(cx_+d,cy_) for d in (0,-8,8,-16,16,-24,24,-32,32)]+[(vx_,vy_+d) for d in (0,-8,8,-16,16)]
                if blab(t2,DKG,"y",cand,sz_): break
            else:                                             # still no room flat: stand it up in the gold strip, centered
                if gx-yx>=7 and T-gy>=_w(t2)+6:
                    c.saveState();c.translate((yx+gx)/2+1.9,(gy+T)/2);c.rotate(90)
                    txt(c,0,0,t2,"PopB",5.0,DKG,"c");c.restoreState()
        blab(t3,GR,"w",[(L+4+dx,T-9-dy) for dy in range(0,140,4) for dx in range(0,100,6)]+
                        [(L+4+dx,B+4+dy) for dy in range(0,60,4) for dx in range(0,100,6)])
        for x,y,r_,p in MD:
            if p[2]=="std": _blot(x,y,r_+.4,DKG)
            else: _blot(x,y,r_,LC if p[2]!="free" else FAG,DKG if p[9] else None,1.1)
            if p[6]: c.setDash(1.5,1.5);_dot(x,y,r_+2.4,None,GR,.7);c.setDash()
        lastc={}
        for p in pts: lastc[last(p[0])]=lastc.get(last(p[0]),0)+1
        for x,y,r_,p in MD:
            lb=last(p[0]) if lastc[last(p[0])]==1 else p[0].split()[0][0]+". "+last(p[0])
            _plate(x,y,r_,lb,None if pos=="DEF" else p[1],None if p[2]=="std" else p[7],None if p[2]=="std" else p[8],
                   None if veg or p[2]=="std" else _trend(p[0]),std=p[9],
                   cap=None if p[2]=="std" or pos=="DEF" else _capof(p[1]))
        # ---- the read, one or two lines under the panel
        ny=my0-28;nx_=mx0;nw_=mx1-mx0
        xl=max(PPG.get(pos,{}).items(),key=lambda t:t[1],default=None)
        if pos=="K": yl=max(KPG.items(),key=lambda t:t[1]);ys=f"kicks — {yl[0]} {yl[1]:.1f}"
        elif pos=="DEF": yl=max(DPG.items(),key=lambda t:t[1]);ys=f"sacks + takeaways — {yl[0]} {yl[1]:.1f}"
        else:
            yl=max(WPG[(k,pos)].items(),key=lambda t:t[1]);ys=f"workload — {last(_DN.get(yl[0],yl[0]))} {yl[1]:.0f}"
        t6=sorted(allx,reverse=True)[:6];av=sum(t6)/len(t6) if t6 else 0;gp=x6-x12
        if allx:
            thin=gp<.12*x6
            ny=inote(nx_,ny,nw_,"Tiers",f"top six average {av:.1f}. 6th to 12th "+
                (f"only {gp:.1f} apart — thin, don't pay to climb." if thin else f"drops {gp:.1f} — a real gap, worth climbing."))
        inG=lambda p:not p[6] and p[3]>=x6 and p[4]>=y6
        inY=lambda p:not p[6] and not inG(p) and p[3]>=x12 and p[4]>=y12
        fg=[p for p in pts if p[2]=="free" and inG(p)];fy=[p for p in pts if p[2]=="free" and inY(p)]
        if fg: b=max(fg,key=lambda p:p[3]);s_=f"{b[0]} is top six on both, {b[3]:.1f} a game. Research before a claim."
        elif fy: b=max(fy,key=lambda p:p[3]);s_=f"{b[0]} is in the gold — top twelve, not top six ({b[3]:.1f} a game)."
        else: s_="nobody on the wire reaches the green or the gold."
        ny=inote(nx_,ny,nw_,"Wire",s_)
        if not bar: continue
        out=[p for p in starts if not p[6] and not inG(p) and not inY(p)]
        if out:
            s_=", ".join(last(p[0]) for p in out)+" — outside the top twelve."
            inote(nx_,ny,nw_,"Watch",s_)
        elif nodata: inote(nx_,ny,nw_,"No usage",", ".join(last(n) for n in nodata[:3])+" — no Week 2 snaps on record; not judged.")
    # ---- key
    LX=PM+25;ky=46;x=LX;f6=6.0
    txt(c,x,ky,"Legend:","PopB",6.2,INKN);x+=c.stringWidth("Legend:  ","PopB",6.2)
    _blot(x+4,ky+2,3.4,LG[RN[k]]);txt(c,x+11,ky,LG_,"Pop",f6,GR);x+=18+c.stringWidth(LG_,"Pop",f6)
    _blot(x+4,ky+2,3.6,DKG);txt(c,x+11,ky,"Standard — best at the position","Pop",f6,GR);x+=18+c.stringWidth("Standard — best at the position","Pop",f6)
    _blot(x+4,ky+2,3.4,FAG);txt(c,x+11,ky,"Free agent — five best, plus any with good news","Pop",f6,GR);x+=18+c.stringWidth("Free agent — five best, plus any with good news","Pop",f6)
    for t_,k_ in (("KC",ST["green"]),("PIT",ST["red"])):
        w1=c.stringWidth(t_,"PopM",PS);txt(c,x,ky,t_,"PopM",PS,GR);c.setStrokeColor(k_);c.setLineWidth(.8);c.line(x,ky-1.2,x+w1,ky-1.2);x+=w1+4
    txt(c,x,ky,"= strong / weak team, no line = middle","Pop",f6,GR);ky-=11;x=LX+c.stringWidth("Legend:  ","PopB",6.2)
    txt(c,x,ky,"Marks right of the name, same as the line items:","Pop",f6,GR);x+=c.stringWidth("Marks right of the name, same as the line items:","Pop",f6)+8
    _tight(c,x+2,ky+2,MG,"gold",True);_sig7(c,x+2+MP,ky+2-.26*MG,MG,"good","01");_TRG(c,x+2+2*MP,ky+2,MG*.95,1)
    txt(c,x+3*MP,ky,"cluster · radar · trend","Pop",f6,GR)
    x+=3*MP+c.stringWidth("cluster · radar · trend","Pop",f6)+12;_cap(x,ky+2,"green","red");x+=_capw()+5
    t_="= schedule, left season, right playoffs. Green easy, gold mixed, red rough."
    txt(c,x,ky,t_,"Pop",f6,GR)
    note(c,LX,24,"How to read it","Green = top six at his position on points AND workload — playoff quality. Gold = seven to twelve — holds a slot. Outside = a problem.",6.0)
    footer(c,FP,"Positions · "+LG_)
    c.showPage()
