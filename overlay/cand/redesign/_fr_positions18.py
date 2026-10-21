# ================================================================== POSITIONS v12 (from v11) — Dom's eleven-item batch, Fri Oct 2:
#   name leads every plate; team smaller behind it; never an underline under his own team; this week's opponent
#   ('vs DAL') smaller still, underlined by how that defense has done against HIS position (red hard, green easy,
#   nothing = middle; underline only, never over); gold ring = best at the position, gold AND violet when he's yours;
#   trend smoothed (engine2: last game .6 + the one before .4, against his earlier average); Thursday's game counted;
#   an as-of stamp names what the page knows.
# v16 (Dom Fri Oct 2, voice): swagger pass. Corners renamed STUDS / WORKHORSES / SLEEPERS / DEAD WEIGHT (Dom chose swagger),
#   set as Bebas stamps with an underline, Studs lit green; axis titles heavier; major + minor ticks inward on all four sides.
# v15 (Dom Fri Oct 2, voice): spacing pass + marks on the plates.
#   SPACING STANDARD (Claude's own numbers, set once for all four leagues): axis titles 13pt off the frame on BOTH axes,
#   tick labels 4pt off the frame on both; notes under each chart 5.6pt grey on 7.4 lead; as-of pill centered in its band
#   with 8pt above and below; legend lifted; 'How to read it' gets its own line with room.
#   MARKS on the plates, so the page points to the rest of the document instead of growing a note block:
#     call TRIANGLE (left of the name) only when the man is on the Call Sheet -- CALLS dict, empty until a call is made;
#     SIGNAL (radar arcs + day count) from his own injury-report line this week: red = out/DNP, gold = limited/questionable,
#       count = days since the first report this week, Wednesday = 01 (Claude's own count rule);
#     CLUSTER on Dom's bench men whose engine rank at the position is below the number rostered in the league
#       (the settled cluster rule, engine rank standing in for Yahoo's rank - Claude's substitution), red first / gold / grey.
#   Badge words in plain English: why he's here · what he's for · how long.
# v14 (Dom Fri Oct 2): every nameplate edge the same light outline -- rings carry yours/best; gold edge kept on the best man; 'MIDDLE OF N ROSTERED' label removed.
# v13 (Dom Fri Oct 2): matchup reads '@ ATL' away, 'vs ATL' home (neutral site = vs); quadrant lines dotted and light.
# ---- v11 header follows
# ================================================================== POSITIONS v11 (from v10) — ruled in voice Fri Oct 2:
#   lines at the MEDIAN of rostered men; the ball carries the trend: green rising, red falling, gold new (no history), empty flat;
#   tint = how hard he moved, last week vs his own earlier average (15% = flat edge, 75%+ = deepest: Claude's own cut points);
#   Dom's men keep a thick violet ring.  Trend arrows on plates, act/monitor rings and the dark-gold standard ball retired.
# ---- v10 header follows
# POSITIONS v10 — the real DK III page off the engine (Fri Oct 2)
# Rebuilt from _fr_positions9.py. Exec'd AFTER the v8 chain so _plate/_blot/swarm/inote/masthead/horizon are shared.
# Spec: /mnt/user-data/outputs/DK_Positions_v10_Spec.pdf.  Data: /home/claude/dksys/engine/engine.py (engine number + doors).
#   ACROSS = engine number, forward case (points a game over his next three games, league scoring).
#   UP     = workload a game, recent-weighted (fc_model units: QB throws + runs, RB carries + weighted targets, WR/TE targets).
#   Quadrant lines = the STARTABLE line (Claude's call on open call 1): the Nth man at the position, N = teams x slots,
#     flex slots split RB .3 / WR .6 / TE .1 (Claude's own split).  Only top-right colored.  No decision line.
#   Balls: violet = Dom (Global palette - Claude's call on open call 4), grey = candidate, gold outline = monitor,
#     red outline = act, filled dark gold = best at the position league-wide, hollow = no usage to measure.
#   Candidates get on through a door, never a points line; Dom's men always plot; floor = 85% of his weakest starter.
import sys as _s10, importlib as _il10, os as _os18
_s10.path.insert(0,"/home/claude/dksys/engine")
_av=_s10.argv[:];_s10.argv=["engine3.py",_os18.environ.get("DK_WEEK","5")];import engine3 as _E10   # v18: drift-aware engine (Oct 6);_s10.argv=_av
DOMV=H("#A98BFF");ACT=H("#D64545");MONI=H("#C9961A");QL=H("#B8B0A0");FRAME=H("#6B6458");GRN10=H("#12A150")
QN={"tr":"STUDS","tl":"WORKHORSES","br":"SLEEPERS","bl":"DEAD WEIGHT"}
QSZ=10.0   # corner stamps: Bebas, underlined; Studs lit green (v16b: toned down from 11.5, Dom)
UPL10={"QB":"THROWS + RUNS A GAME","RB":"CARRIES + WEIGHTED TARGETS A GAME","WR":"TARGETS A GAME","TE":"TARGETS A GAME"}
def _startN(teams,slots):
    fl=slots.get("FLEX",0)*teams
    return {"QB":teams*slots.get("QB",1)+(teams*slots.get("SF",0)),"RB":teams*slots["RB"]+round(.3*fl),
            "WR":teams*slots["WR"]+round(.6*fl),"TE":teams*slots["TE"]+round(.1*fl)}
TGRN=H("#12A150");TRED=H("#D64545");TGLD=H("#E0A526")
def _tint(col,a): return Color(1-(1-col.red)*a,1-(1-col.green)*a,1-(1-col.blue)*a)
GOLDR=H("#C9961A")
def _opp(r):
    pl=bool(r.get("played_wk")) if hasattr(r,"get") else False
    o,w=_E10.nextopp(r.team,_E10.WEEK,pl)
    if o is None: return None
    return (o,w,_E10.DTIER.get((o,r.pos)),_E10.HOME.get((r.team,w)))
def _Rk(R,o,col):
    m=R[R.k==_norm(o.player)]
    return float(m[col].iloc[0]) if len(m) else None
def _trend11(p):
    if p["hol"]: return TGLD,"new"
    ch=p.get("trs")
    if ch is None or ch!=ch: return None,"flat"
    if abs(ch)<.15: return None,"flat"
    a=.28+.72*min(1,(abs(ch)-.15)/.60)
    return _tint(TGRN if ch>0 else TRED,a),("up" if ch>0 else "down")
import pandas as _pd15
_DOORW={"USAGE":"USAGE UP","EVENT":"ROLE OPENED","EVENT?":"ROLE MAY OPEN","COVER":"FILLS A HOLE","MARKET":"MARKET RISING"}
_TAGW={"SEASON":"SEASON PIECE","BYE COVER":"BYE COVER","INJURY COVER":"INJURY COVER"}
def _durw(d):
    if d=="ROS": return "REST OF SEASON"
    if d=="?": return "HOW LONG UNCLEAR"
    if d.endswith("WK"): n=d[:-2];return n+(" WEEK" if n=="1" else " WEEKS")
    return d
_TAGS={"BYE COVER":"BYE","INJURY COVER":"INJ"}      # v16b: SEASON drops - ROS already says it
def _durs(d):
    if d=="ROS": return "ROS"
    if d=="?": return "? WK"
    if d.endswith("WK"): return d[:-2]+" WK"
    return d
def _badge(o):
    """v16b: the WHY becomes glyphs (one per door), the WHAT-FOR and HOW-LONG a short word. Picture over paragraph."""
    g=[d for d in str(o.doors).split("+") if d in ("USAGE","EVENT","EVENT?","COVER","MARKET")]
    w=" ".join(x for x in (_TAGS.get(o.tag,""),_durs(o.dur)) if x)
    return (g,w)
GS=5.6   # door-glyph size
def dglyph(cx,cy,code,s=GS):
    """Door glyphs - each means one thing everywhere: arrow = usage up, star = role opened (hollow = may open),
    plus-box = fills a hole, rising bars = market rising."""
    h=s/2;c.saveState();c.setLineJoin(1);c.setLineCap(1)
    if code=="USAGE":
        c.setFillColor(TGRN);p=c.beginPath();p.moveTo(cx,cy+h);p.lineTo(cx+h*.95,cy-h*.05);p.lineTo(cx+h*.38,cy-h*.05)
        p.lineTo(cx+h*.38,cy-h);p.lineTo(cx-h*.38,cy-h);p.lineTo(cx-h*.38,cy-h*.05);p.lineTo(cx-h*.95,cy-h*.05);p.close();c.drawPath(p,stroke=0,fill=1)
    elif code in ("EVENT","EVENT?"):
        import math as _m;p=c.beginPath()
        for i in range(10):
            a=_m.pi/2+i*_m.pi/5;rr=h*1.05 if i%2==0 else h*.45
            (p.moveTo if i==0 else p.lineTo)(cx+rr*_m.cos(a),cy+rr*_m.sin(a))
        p.close()
        if code=="EVENT": c.setFillColor(INKN);c.drawPath(p,stroke=0,fill=1)
        else: c.setStrokeColor(MONI);c.setLineWidth(.75);c.drawPath(p,stroke=1,fill=0)
    elif code=="COVER":
        c.setStrokeColor(INKN);c.setLineWidth(.7);c.roundRect(cx-h*.9,cy-h*.9,h*1.8,h*1.8,.8,stroke=1,fill=0)
        c.setLineWidth(.85);c.line(cx-h*.5,cy,cx+h*.5,cy);c.line(cx,cy-h*.5,cx,cy+h*.5)
    elif code=="MARKET":
        c.setFillColor(TGRN)
        for i,hh in enumerate((.7,1.25,1.9)): c.rect(cx-h+i*h*.72,cy-h,h*.52,h*hh,stroke=0,fill=1)
    c.restoreState()
import datetime as _dt
_INJ=_pd15.read_csv("/home/claude/dksys/data/latest/injuries.csv");_INJ=_INJ[_INJ.season==2026].copy();_INJ["k"]=_INJ.full_name.map(_norm)
_G15=_pd15.read_csv("/home/claude/dksys/data/latest/games.csv",low_memory=False);_G15=_G15[(_G15.season==2026)&(_G15.week==_E10.WEEK)]
_SUN=max(_dt.date.fromisoformat(d) for d in _G15.gameday if _dt.date.fromisoformat(d).weekday()==6)
_TODAY=(_dt.datetime.utcnow()-_dt.timedelta(hours=7)).date()            # Pacific
_DAYS=max(1,(_TODAY-(_SUN-_dt.timedelta(days=4))).days+1)               # Wednesday of the week = 01
CALLS={}   # (league, player) -> (color, call-sheet number). Filled only when a call is on the Call Sheet. Empty Fri Oct 2.
ROSTN={"DK I":{"QB":22,"RB":53,"WR":64,"TE":22},"DK II":{"QB":30,"RB":54,"WR":67,"TE":20},"DK III":{"QB":26,"RB":59,"WR":74,"TE":25},"DK IV":{"QB":27,"RB":52,"WR":56,"TE":17}}   # rostered league-wide, Yahoo Fri Oct 2
def _signal(nm):
    if _norm(nm) in _E10.CLEARED: return None
    I=_INJ[_INJ.k==_norm(nm)]
    if not len(I): return None
    wk=I[I.week==_E10.WEEK]
    if not len(wk): return None
    r=wk.iloc[-1];ps=str(r.practice_status);rs=str(r.report_status)
    if rs in ("Out","Doubtful") or ps.startswith("Did Not"): col="bad"
    elif rs=="Questionable" or ps.startswith("Limited"): col="caution"
    else: return None
    return (col,"%02d"%_DAYS)
def _plate12(x,y,r,lab,tm,opp,tag,tagc,edge,cl=None,sg=None,tri=None,dm=None):
    """v12 plate: NAME first (the key), then his team smaller, then this week's opponent smaller still with the matchup
    underline under the OPPONENT only, then the badge (door · reason · how long). Underline only - never an overline."""
    sz=PS;s2=sz*.80;s3=sz*.74;px=2.2;sp=c.stringWidth(" ","PopM",sz)
    nw=c.stringWidth(lab,"PopM",sz);tw=c.stringWidth(tm,"PopM",s2) if tm else 0
    if opp:
        at="@ " if opp[3]=="away" else "vs "
        ot=("WK%d "%opp[1] if opp[1]!=_E10.WEEK else "")+at;ow1=c.stringWidth(ot,"Pop",s3);ow2=c.stringWidth(opp[0],"PopM",s3)
    else: ot="";ow1=ow2=0
    if tag and isinstance(tag,tuple): tg,tw2=tag;gw=len(tg)*(GS+1.6)+(c.stringWidth(tw2,"PopB",sz*.80) if tw2 else 0)
    else: tg=None;gw=c.stringWidth(tag,"PopB",sz*.80) if tag else 0
    w=nw+(sp+tw if tm else 0)+(sp+ow1+ow2 if opp else 0)+(sp*1.6+gw if tag else 0)+2*px;h=sz+3.6
    nmk=(1 if cl else 0)+(1 if sg else 0)+(1 if dm is not None else 0);mkw=(2.5+MK_S*.35+(nmk-1)*MK_P+MK_S*.55) if nmk else 0
    trw=(TRI_H*.95+3) if tri else 0;wt=w;w=trw+wt+mkw
    cands=[]
    for d in (0,5,10,15,20,26,33,40,48,56,64,74,86,100):
        for s_ in ((1,) if d==0 else (1,-1)):
            cands+=[(x+r+3,y-h/2+s_*d),(x-r-3-w,y-h/2+s_*d)]
        for sh in (0,-.35,.35,-.7,.7):
            cands+=[(x-w/2+sh*w,y+r+3+d),(x-w/2+sh*w,y-r-3-h-d)]
    cands.sort(key=lambda q:((q[0]+w/2-x)**2*.5+(q[1]+h/2-y)**2))
    def hit(bx,by):
        cxl,cyl=bx+w/2,by+h/2;dm=(cxl-x)**2+(cyl-y)**2
        if any(((cxl-ox)**2+(cyl-oy)**2)<dm*.8 for ox,oy in DOTS if (ox,oy)!=(x,y)): return True
        if any(((min(max(ox,bx),bx+w)-ox)**2+(min(max(oy,by),by+h)-oy)**2)<(r+4)**2 for ox,oy in DOTS if (ox,oy)!=(x,y)): return True   # v16b: no plate touching another man's ball
        if bx<BOUND[0] or bx+w>BOUND[1] or by<BOUND[2] or by+h>BOUND[3]: return True
        for (ox,oy,ow,oh) in OBST:
            if bx<ox+ow+1 and bx+w>ox-1 and by<oy+oh+1 and by+h>oy-1: return True
        return False
    def cost(bx,by):
        if bx<BOUND[0] or bx+w>BOUND[1] or by<BOUND[2] or by+h>BOUND[3]: return 1e9
        return sum(max(0,min(bx+w,ox+ow)-max(bx,ox))*max(0,min(by+h,oy+oh)-max(by,oy)) for ox,oy,ow,oh in OBST)
    for bx,by in cands:
        if not hit(bx,by): break
    else: bx,by=min(cands,key=lambda q:cost(*q))
    cx_,cy_=min(max(x,bx),bx+w),min(max(y,by),by+h);dd=((cx_-x)**2+(cy_-y)**2)**.5
    if dd>r+6:
        ux,uy=(cx_-x)/dd,(cy_-y)/dd
        c.saveState();c.setStrokeColor(GR);c.setLineWidth(.6);c.setLineCap(1);c.setDash(.1,1.6)
        c.line(x+ux*(r+1.2),y+uy*(r+1.2),cx_,cy_);c.restoreState()
    OBST.append((bx,by,w,h));bx0=bx;bx=bx+trw
    if tri: ntri(c,bx0,by+h/2,*tri)
    if nmk: markers(c,bx+wt+2.5+MK_S*.35,by+h/2,cl,sg,None,dm)
    ec=edge or alpha(GR,.6)
    c.saveState();c.setStrokeColor(ec);c.setLineWidth(.9 if edge else .5);c.roundRect(bx,by,wt,h,1.8,stroke=1,fill=0);c.restoreState()
    ty=by+1.8+sz*.14;tx=bx+px
    txt(c,tx,ty,lab,"PopM",sz,INKN);tx+=nw
    if tm: tx+=sp;txt(c,tx,ty,tm,"PopM",s2,GR);tx+=tw
    if opp:
        tx+=sp;txt(c,tx,ty,ot,"Pop",s3,GR2);tx+=ow1;txt(c,tx,ty,opp[0],"PopM",s3,GR)
        uc=ST["red"] if opp[2]=="hard" else ST["green"] if opp[2]=="easy" else None
        if uc: c.setStrokeColor(uc);c.setLineWidth(.9);c.line(tx,ty-1.3,tx+ow2,ty-1.3)
        tx+=ow2
    if tag and tg is not None:
        tx+=sp*1.6
        for g_ in tg: dglyph(tx+GS/2,ty+sz*.30,g_);tx+=GS+1.6
        if tw2: txt(c,tx,ty+.2,tw2,"PopB",sz*.80,tagc)
    elif tag: tx+=sp*1.6;txt(c,tx,ty+.2,tag,"PopB",sz*.80,tagc)
def inote15(x,y,w,lab,s,sz=5.6,lead=7.4):
    txt(c,x,y,lab+":","PopB",sz,GR);ix=x+c.stringWidth(lab+":  ","PopB",sz);line=""
    for wd in s.split():
        t_=(line+" "+wd).strip()
        if c.stringWidth(t_,"Pop",sz)>w-(ix-x): txt(c,ix,y,line,"Pop",sz,GR);y-=lead;line=wd
        else: line=t_
    if line: txt(c,ix,y,line,"Pop",sz,GR);y-=lead
    return y-1.2
_GALL=_pd15.read_csv("/home/claude/dksys/data/latest/games.csv",low_memory=False);_GALL=_GALL[_GALL.season==2026]
def _bye(tm):
    ws=set(_GALL[(_GALL.home_team==tm)|(_GALL.away_team==tm)].week)
    for w in range(5,15):
        if w not in ws: return w
    return None
# Oct 9 (Dom): the cluster called Kelce first-out off a workload-only number. Two guards, same as the Scout engine:
# Dom's protected names never qualify, and a PROVEN scorer never qualifies - real points a game (this season, or last
# season over 6+ games) inside the number rostered at his position league-wide.
CLU_PROTECT={"Travis Kelce","Kaelon Black"}
def _ppg_table():
    import pandas as _pd
    out={}
    for f,mn in (("/home/claude/dksys/data/latest/stats_week.csv",2),("/home/claude/dksys/data/latest/stats_week_2025.csv",6)):
        try:
            d=_pd.read_csv(f,low_memory=False); d=d[d.season_type=="REG"]
            g=d.groupby(["player_display_name","position"]).agg(n=("week","nunique"),p=("fantasy_points_ppr","sum")).reset_index()
            g=g[g.n>=mn]; g["ppg"]=g.p/g.n; out[f]=g
        except Exception as e: print("CLU proven table missing",f,e)
    return out
_PPG=_ppg_table()
def _proven(name,pos,n_):
    if not n_: return False
    for g in _PPG.values():
        gp=g[g.position==pos].sort_values("ppg",ascending=False).reset_index(drop=True)
        row=gp[gp.player_display_name==name]
        if len(row) and row.index[0]<n_: return True
    return False
def clu17(lab,R):
    """v17 drop cluster - the cut order itself (the Cuttable page is retired, Oct 3).
    Qualify: healthy bench QB/RB/WR/TE ranked below the number rostered at his position league-wide (forward number).
    PROTECTED (Dom's rule): a handcuff (same-team RB to one of his RBs) or the only bench man at a position whose
    starter is on bye Weeks 5-7. Protected men sort behind every unprotected man and never print red."""
    RN_=ROSTN.get(lab,{});qual=[]
    mine=R[R.own=="MINE"];st=mine[mine.slot!="B"];bn=mine[mine.slot=="B"]
    myrb=set(mine[(mine.pos=="RB")].team)
    for _,m in bn[bn.pos.isin(["QB","RB","WR","TE"])&bn.eng_fwd.notna()].iterrows():
        if m.eng_wk==0 or _signal(m.player): continue
        if m.player in CLU_PROTECT or _proven(m.player,m.pos,RN_.get(m.pos)): continue   # Oct 9: never mark a proven scorer (the Kelce fix)
        P_=R[(R.pos==m.pos)&R.eng_fwd.notna()].sort_values("eng_fwd",ascending=False).reset_index(drop=True)
        rk=int((P_.eng_fwd>m.eng_fwd).sum())+1;n_=RN_.get(m.pos)
        if not(n_ and rk>n_): continue
        cuff=m.pos=="RB" and ((mine.pos=="RB")&(mine.team==m.team)&(mine.player!=m.player)).any()
        need=any(_bye(t) in (5,6,7) for t in st[st.pos==m.pos].team)
        sole=need and int((bn.pos==m.pos).sum())==1
        qual.append((1 if (cuff or sole) else 0,m.eng_fwd/float(P_.eng_fwd.iloc[n_-1]),m.player))
    out={};cols=["red","gold","grey"];k=0
    for prot,_,nm in sorted(qual)[:3]:
        if prot and k==0: k=1
        if k>2: break
        out[nm]=cols[k];k+=1
    PROT17[lab]=[nm for prot,_,nm in qual if prot]
    print("CLU17",lab,out,"protected",PROT17[lab],"qual",[(q[2],round(q[1],2)) for q in qual])
    return out
PROT17={}
exec(open('/home/claude/cand/redesign/_oct11_pos.py').read())   # Oct 10 night: full names, Scout picks, plates in words
PSTAMP=[("DATA AS OF FRI OCT 2","PopB",H("#8C8576")),("  ·  ","Pop",H("#8C8576")),("MARKET THU OCT 1","PopB",GOLDR)]   # gold = older than a day at build
def position_page10(lab,teams,slots,out_label,pagen=None):
    R,O,p40=_E10.run(lab);SN=_startN(teams,slots)
    DMP={r_d.player:(r_d.drift_swing>0) for r_d in R.itertuples() if r_d.drift=="D"}   # v18 D marks off engine3
    masthead(c,"POSITIONS  ·  "+lab,"Roles, and the free agents worth a look")
    # v17d (Dom): the floating AS OF pill had no home - freshness now lives on each panel it vouches for.
    PM=22;top=Ht-124;gap=16;gw_=(W-2*PM-gap)/2;ph=(top-98)/2
    reads={}
    CLU=clu17(lab,R)
    for i,pos in enumerate(("QB","RB","WR","TE")):
        x0=PM+(i%2)*(gw_+gap);yT=top-(i//2)*ph
        A=R[(R.pos==pos)&R.eng_fwd.notna()&R.wl_pg.notna()&(R.games>=2)]
        RO=A[~A.own.isin(["FA","W"])];n=len(RO)
        xline=float(RO.eng_fwd.median());yline=float(RO.wl_pg.median())
        me=R[(R.own=="MINE")&(R.pos==pos)&(R.slot!="I")]
        Op=_with_scout(O[O.pos==pos] if len(O) else O,R,pos,lab)
        best=A.sort_values("eng_fwd",ascending=False).iloc[0]
        pts=[]
        for _,m in me.iterrows():
            hol=m.wl_pg!=m.wl_pg or m.eng_fwd!=m.eng_fwd
            pts.append(dict(nm=m.player,tm=m.team,kind="mine",x=m.eng_fwd if not hol else None,y=m.wl_pg if not hol else None,trs=m.trend,opp=_opp(m),
                            hol=hol,dir=m.dir,tag=("OUT WK4" if m.eng_wk==0 else None),out=None,best=m.k==best.k))
        for _,o in Op.iterrows():
            mon="GOLD-MONITOR" in o.ball
            pts.append(dict(nm=o.player,tm=o.team,kind="cand",x=o.eng_fwd,y=o.wl_pg,hol=o.ball.startswith("HOLLOW"),dir=o.dir,trs=_Rk(R,o,'trend'),opp=_opp(R[R.k==_norm(o.player)].iloc[0]),
                            tag=_badge(o),out=(MONI if mon else (ACT if o.n>=2 else None)),best=_norm(o.player)==best.k,row=o))
        if not any(p["best"] for p in pts):
            pts.append(dict(nm=best.player,tm=best.team,kind="std",x=best.eng_fwd,y=best.wl_pg,hol=False,dir=best.dir,tag=None,out=None,best=True,trs=best.trend,opp=_opp(best)))
        # ---- per-panel axis fit
        xv=[p["x"] for p in pts if p["x"] is not None]+[xline];yv=[p["y"] for p in pts if p["y"] is not None]+[yline]
        # equal quadrants: each axis centred on its median line, wide enough for the farthest man (+10%)
        dx=1.15*max(abs(v-xline) for v in xv) or 1;dy=1.40*max(abs(v-yline) for v in yv) or 1   # v16: headroom so no ball sits on a corner stamp
        xlo,xhi=xline-dx,xline+dx;ylo,yhi=yline-dy,yline+dy
        for p in pts:
            if p["hol"]: p["x"],p["y"]=xlo+(xhi-xlo)*.04,ylo+(yhi-ylo)*.06
        mx0,mx1=x0+19,x0+gw_-1;my1=yT-12;my0=my1-ph+96
        XM=lambda v:mx0+(v-xlo)/(xhi-xlo)*(mx1-mx0);YM=lambda v:my0+(v-ylo)/(yhi-ylo)*(my1-my0)
        txt(c,x0,yT,POSN[pos],"Bebas",16,INKN)
        stamp(c,mx1,yT+1.2,["engine","market"],sz=5.8)                       # this panel's "as of", on its title line
        L,R_,B,T=mx0,mx1,my0,my1;qx,qy=XM(xline),YM(yline)
        c.setFillColor(CARD);c.rect(L,B,R_-L,T-B,stroke=0,fill=1)
        c.setFillColor(alpha(GRN10,.16));c.rect(qx,qy,R_-qx,T-qy,stroke=0,fill=1)
        c.saveState();c.setStrokeColor(QL);c.setLineWidth(.6);c.setLineCap(1);c.setDash(.1,2.4);c.line(qx,B,qx,T);c.line(L,qy,R_,qy);c.restoreState()
        c.setStrokeColor(FRAME);c.setLineWidth(1.0);c.rect(L,B,R_-L,T-B,stroke=1,fill=0)
        _QB=[]
        for key,(ax,ay,al) in {"tr":(R_-6,T-13,"r"),"tl":(L+6,T-13,"l"),"br":(R_-6,B+8,"r"),"bl":(L+6,B+8,"l")}.items():
            qw=c.stringWidth(QN[key],"Bebas",QSZ);qx0=ax-qw if al=="r" else ax;lit=key=="tr"
            txt(c,qx0,ay,QN[key],"Bebas",QSZ,GRN10 if lit else alpha(GR2,.75))
            c.saveState();c.setStrokeColor(GRN10 if lit else alpha(GR2,.45));c.setLineWidth(1.6 if lit else .9);c.setLineCap(0)
            c.line(qx0,ay-2.6,qx0+qw,ay-2.6);c.restoreState()
            _QB.append((qx0-2,ay-4,qw+4,QSZ*.75+6))
        # ticks
        def _ticks(lo,hi):
            sp=hi-lo;st=.5 if sp<=4 else 1 if sp<=8 else 2 if sp<=16 else 5 if sp<=40 else 10
            v=_math.ceil(lo/st)*st;o=[]
            while v<=hi+1e-9: o.append(round(v,2));v+=st
            return o,st
        tx_,stx=_ticks(xlo,xhi)
        c.saveState();c.setStrokeColor(FRAME);c.setLineCap(0)
        for v in tx_:                                    # major ticks inward 3.2pt, minor (half step) 1.6pt
            if v<0: continue
            txt(c,XM(v),B-4-5.2*.72,(f"{v:g}"),"PopM",5.2,GR,"c")
            c.setLineWidth(.7);c.line(XM(v),B,XM(v),B+3.2);c.line(XM(v),T,XM(v),T-3.2)
            m_=v+stx/2
            if m_<=xhi: c.setLineWidth(.5);c.line(XM(m_),B,XM(m_),B+1.6);c.line(XM(m_),T,XM(m_),T-1.6)
        c.restoreState()
        txt(c,(mx0+mx1)/2,B-13-5.8*.72,"ENGINE — POINTS A GAME, NEXT THREE GAMES","PopB",5.8,FRAME,"c")
        ty_,sty=_ticks(ylo,yhi)
        for v in [u for u in ty_ if u>=0]:
            txt(c,L-4,YM(v)-1.9,f"{v:g}","PopM",5.2,GR,"r");c.setStrokeColor(FRAME);c.setLineCap(0)
            c.setLineWidth(.7);c.line(L,YM(v),L+3.2,YM(v));c.line(R_,YM(v),R_-3.2,YM(v))
            m_=v+sty/2
            if m_<=yhi: c.setLineWidth(.5);c.line(L,YM(m_),L+1.6,YM(m_));c.line(R_,YM(m_),R_-1.6,YM(m_))
        c.saveState();c.translate(L-13,(B+T)/2);c.rotate(90);txt(c,0,0,UPL10[pos],"PopB",5.8,FRAME,"c");c.restoreState()
        _SL=(qx,T,n)
        # balls
        OBST.clear();BOUND[:]=[L+1,R_-1,B+1,T-1]
        MD=swarm([(XM(p["x"]),YM(p["y"]),3.6,p) for p in pts],4.8);DOTS[:]=[(x,y) for x,y,_,_ in MD]
        for x,y,r_,p in MD: OBST.append((x-r_-2,y-r_-2,2*r_+4,2*r_+4))
        OBST.extend(_QB)
        for x,y,r_,p in MD:
            fc,p["mv"]=_trend11(p)
            _blot(x,y,r_,fc if fc is not None else CARD,alpha(INKN,.55),.6)
            if p["kind"]=="mine":
                c.saveState();c.setStrokeColor(DOMV);c.setLineWidth(1.8);c.circle(x,y,r_+1.5,stroke=1,fill=0);c.restoreState()
            if p["best"]:
                rr=r_+(3.4 if p["kind"]=="mine" else 1.5)
                c.saveState();c.setStrokeColor(GOLDR);c.setLineWidth(1.8);c.circle(x,y,rr,stroke=1,fill=0);c.restoreState()
        lastc={}
        for p in pts: lastc[last(p["nm"])]=lastc.get(last(p["nm"]),0)+1
        for x,y,r_,p in MD:
            lb=_fullnm(p["nm"])
            _plate12(x,y,r_,lb,p["tm"],p.get("opp"),p["tag"],(ACT if p["kind"]=="mine" else GR),GOLDR if p["best"] else None,
                     cl=CLU.get(p["nm"]),sg=_signal(p["nm"]),tri=CALLS.get((lab,p["nm"])),dm=DMP.get(p["nm"]))
        # ---- the read under the panel
        ny=B-29;nx_=mx0;nw_=mx1-mx0
        st_=me[me.slot.isin(["S","F"])&me.eng_fwd.notna()]
        if len(st_):
            ws=st_.sort_values("eng_fwd").iloc[0];fl=.85*ws.eng_fwd
            ny=inote15(nx_,ny,nw_,"Floor",f"{fl:.1f} a game — 85% of {ws.player}, your weakest starter here ({ws.eng_fwd:.1f}).")
        else: fl=None
        if len(Op):
            ny=inote15(nx_,ny,nw_,"Doors","; ".join(f"{o.player} — {o.why.split(' (')[0]}" for _,o in Op.iterrows()))
            ck=[f"{o.player} {o.eng_fwd:.1f} vs {o.blend:.1f}" for _,o in Op.iterrows() if o.check]
            if ck: ny=inote15(nx_,ny,nw_,"Check","sources far lower than the engine — "+", ".join(ck)+". Look before acting.")
        else:
            F=R[(R.pos==pos)&R.own.isin(["FA","W"])&R.eng_fwd.notna()&(R.games>=2)&~R.k.isin(_E10.OUTSEASON)].sort_values("eng_fwd",ascending=False).head(2)
            near=", ".join(f"{f.player} {f.team} {f.eng_fwd:.1f}" for _,f in F.iterrows())
            ny=inote15(nx_,ny,nw_,"Doors",f"no free agent clears the floor through any door. Closest: {near}.")
        reads[pos]=dict(floor=fl,cands=list(Op.player) if len(Op) else [])
    # ---- key
    LX=PM+19;ky=88;x=LX;f6=6.0
    txt(c,x,ky,"Legend:","PopB",6.2,INKN);x+=c.stringWidth("Legend:  ","PopB",6.2)
    for fc,lb in ((_tint(TGRN,.35),None),(TGRN,"rising (pale = a little, deep = a lot)"),(_tint(TRED,.35),None),(TRED,"falling (pink = a little, red = a lot)"),(TGLD,"new — no games yet"),(CARD,"flat")):
        _blot(x+4,ky+2,3.4,fc,alpha(INKN,.55),.6)
        if lb: txt(c,x+11,ky,lb,"Pop",f6,GR);x+=18+c.stringWidth(lb,"Pop",f6)
        else: x+=10
    ky-=10;x=LX+c.stringWidth("Legend:  ","PopB",6.2)   # Oct 10 night: the rings get their own line
    _blot(x+5,ky+2,3.4,CARD,alpha(INKN,.55),.6);c.saveState();c.setStrokeColor(DOMV);c.setLineWidth(1.8);c.circle(x+5,ky+2,4.9,stroke=1,fill=0);c.restoreState()
    txt(c,x+13,ky,"violet ring = on this roster","Pop",f6,GR);x+=21+c.stringWidth("violet ring = on this roster","Pop",f6)
    _blot(x+5,ky+2,3.4,CARD,alpha(INKN,.55),.6);c.saveState();c.setStrokeColor(GOLDR);c.setLineWidth(1.8);c.circle(x+5,ky+2,4.9,stroke=1,fill=0);c.restoreState()
    txt(c,x+13,ky,"gold ring = best at the position        BYE FILL / INJURY FILL = covers a bye or an injury on this roster","Pop",f6,GR)
    ky-=10;x=LX+c.stringWidth("Legend:  ","PopB",6.2)
    txt(c,x,ky,"Movement = his last two games, the latest counting most, against his own earlier average.        SCOUT PICK = recommended on the Scout page","Pop",f6,GR)
    ky-=10;txt(c,x,ky,"vs = home, @ = away (this week's opponent).  Line under him:","Pop",f6,GR);x2=x+c.stringWidth("vs = home, @ = away (this week's opponent).  Line under him:  ","Pop",f6)
    for col,lb in ((ST["red"],"hard"),(ST["green"],"easy")):
        c.setStrokeColor(col);c.setLineWidth(.9);c.line(x2,ky-1.3,x2+12,ky-1.3);txt(c,x2+15,ky,lb,"Pop",f6,GR);x2+=21+c.stringWidth(lb,"Pop",f6)
    txt(c,x2,ky,"against this man's position;  none = middle.  Thursday's teams show next week's game.","Pop",f6,GR)
    ky-=10;x4=x
    txt(c,x4,ky,"Plate words:  USAGE UP = workload jumped  ·  ROLE OPENED = a teammate ahead of him is out (MAY OPEN = unconfirmed)  ·  MARKET UP = sources well above Gotham","Pop",f6,GR)
    ky-=10;x3=x
    _ms=((lambda xx,yy: tight(c,xx,yy,MK_S*.8,"red",True)),"drop order — red first, then gold, then grey",14),\
        ((lambda xx,yy: sig7(c,xx,yy-.26*9,9,"caution","03")),"news this week — Radar page",14),\
        ((lambda xx,yy: dmark(c,xx,yy,MK_S*.8,True)),"drift moved his workload",12),\
        ((lambda xx,yy: ntri(c,xx-3,yy,"gold","1")),"on the Call Sheet",19)
    txt(c,x3,ky,"Marks beside a plate:","Pop",f6,GR);x3+=c.stringWidth("Marks beside a plate:  ","Pop",f6)
    for fn,lb,o_ in _ms:
        fn(x3+5,ky+2);txt(c,x3+o_,ky,lb,"Pop",f6,GR);x3+=o_+10+c.stringWidth(lb,"Pop",f6)
    note(c,LX,27,"How to read it","Across = points going forward. Up = how much his team uses him. Lines = the middle of the rostered field. Studs = ahead on both.",6.0)
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,20,W-M,20)
    txt(c,M,11,"DARK KNIGHT FANTASY FOOTBALL","PopB",6.4,INKN)
    txt(c,M+c.stringWidth("DARK KNIGHT FANTASY FOOTBALL","PopB",6.4)+8,11,"Week 4  ·  Positions  ·  "+built_str(),"Pop",5.8,GR)
    txt(c,W-M,11,out_label,"Pop",5.8,GR,"r")
    c.showPage()
    return reads

# OCT10 positions

# OCT10c positions sub

# OCT10d positions words
