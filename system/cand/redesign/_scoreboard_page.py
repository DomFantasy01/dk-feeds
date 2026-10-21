# THE SCOREBOARD PAGE (Dom, Sun Oct 11 2026) - the last page of the Dispatch, after The Marks.
# Who called it right: Yahoo, Gotham and Sleeper, each frozen at kickoff, graded against what the man actually scored
# in his league's scoring. This week on top, the running total from Week 2 under it, the trend by week, by position,
# what happens when the three disagree, and the week's biggest misses - the receipts.
# Data: cand/scoreboard.py (run here first so the page grades this build's finals; the later run in the build repeats it).
import subprocess as _sbp, itertools as _it, os as _os
_REPO=_os.environ.get("GITHUB_WORKSPACE","")
try: _sbp.run([sys.executable,"/home/claude/cand/scoreboard.py",_REPO],capture_output=True,text=True,timeout=300)
except Exception as _ex: print("SCOREBOARD page: grading run failed -",_ex)
_SBF=_os.path.join(_REPO,"dispatch_out","scoreboard","graded.csv")
_SRC=(("yahoo","Yahoo"),("gotham","Gotham"),("sleeper","Sleeper"))
_SCOL={"yahoo":H("#7B4FC9"),"gotham":INKN,"sleeper":H("#2EA3C4")}
def _sb_pairs(df,col):
    ok=n=0
    for _,g in df.dropna(subset=[col]).groupby(["week","pos"]):
        v=g[col].values;t=g.actual.values
        for i,j in _it.combinations(range(len(g)),2):
            if t[i]==t[j] or v[i]==v[j]: continue
            n+=1;ok+=(v[i]>v[j])==(t[i]>t[j])
    return (ok/n if n else None),n
def _sb_stats(df):
    o={}
    for k,_ in _SRC:
        x=df.dropna(subset=[k]); p,n=_sb_pairs(df,k)
        o[k]=dict(miss=(float((x[k]-x.actual).abs().mean()) if len(x) else None),pct=p,pairs=n,men=len(x))
    return o
def _sb_hd(y,title,sub):
    txt(c,M,y,title,"Bebas",14,INKN);txt(c,M+c.stringWidth(title,"Bebas",14)+8,y+.5,sub,"Pop",6.4,GR)
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,y-5,W-M,y-5)
def _sb_tiles(y,st,label):
    """three tiles: average miss (big), start/sit right; the best of the three on each count wears green"""
    bm=min((v["miss"] for v in st.values() if v["miss"] is not None),default=None)
    bp=max((v["pct"] for v in st.values() if v["pct"] is not None),default=None)
    tw=(W-2*M-2*10)/3;th=58
    for i,(k,nm) in enumerate(_SRC):
        x=M+i*(tw+10);v=st[k]
        c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.7);c.rect(x,y-th,tw,th,stroke=1,fill=1)
        c.setFillColor(_SCOL[k]);c.rect(x,y-th,3.2,th,stroke=0,fill=1)
        txt(c,x+11,y-14,nm.upper(),"Bebas",13,_SCOL[k]);txt(c,x+tw-8,y-13,label,"Pop",5.6,GR,"r")
        if v["miss"] is None: txt(c,x+11,y-40,"not graded yet","Pop",7,GR);continue
        good=bm is not None and abs(v["miss"]-bm)<.05
        txt(c,x+11,y-42,f"{v['miss']:.1f}","Bebas",26,ST["green"] if good else INKN)
        mx=x+11+c.stringWidth(f"{v['miss']:.1f}","Bebas",26)+4
        txt(c,mx,y-33,"points off","PopM",6,GR);txt(c,mx,y-41,"a man","PopM",6,GR)
        if v["pct"] is not None:
            gp=bp is not None and abs(v["pct"]-bp)<.005
            txt(c,x+tw-10,y-42,f"{v['pct']:.0%}","Bebas",20,ST["green"] if gp else INKN,"r")
            txt(c,x+tw-10,y-51,"start/sit calls right","Pop",5.4,GR,"r")
        txt(c,x+11,y-52,f"{v['men']} men graded","Pop",5.4,GR)
    return y-th
def _sb_verdict(st):
    ms=sorted(((v["miss"],k) for k,v in st.items() if v["miss"] is not None))
    if len(ms)<2: return "Not enough finals yet to call it."
    nm=dict(_SRC);(m0,k0),(m1,k1)=ms[0],ms[1];g=st["gotham"]["miss"]
    s=f"{nm[k0]} closest" if m1-m0>=.05 else f"{nm[k0]} and {nm[k1]} dead even"
    if k0!="gotham" and g is not None: s+=f". Gotham {g-m0:.1f} points a man behind."
    elif k0=="gotham": s+=f". Gotham ahead by {m1-m0:.1f} points a man."
    return s
SB_PAGE=c.getPageNumber()
masthead(c,"CALLS  ·  CALIBRATION","What needs you, then who called it right")
y=Ht-122
# ---- Oct 13 (Dom): ACTION ITEMS on page 2 - what needs you, most urgent first, each with its deadline (the CALLS button's page)
_ANS={"norm":norm}   # its own namespace, so none of its names can shadow the page code's
try: exec(open("/home/claude/cand/_actions.py").read(),_ANS); ACTIONS=_ANS["ACTIONS"]; ADVICE_SUM=_ANS["ADVICE_SUM"]
except Exception as _ex: ACTIONS=None; ADVICE_SUM=None; import traceback as _tb; _tb.print_exc(); print("ACTIONS FAILED -",repr(_ex)[:300])
_sb_hd(y,f"ACTION ITEMS  ·  WEEK {MTR.get('week','')}","What needs you, most urgent first  ·  the full case is on each league's page  ·  every move is your call")
y-=17
_ARC={1:ST["red"],2:ST["gold"],3:ST["gold"]}
if ACTIONS is None:
    txt(c,M,y,"Action items could not be built this run. The build log says why.","PopB",7.5,ST["red"]); y-=13
elif not ACTIONS:
    txt(c,M,y,"Nothing needs you right now: lineups set, no starter tagged, no claim the Scout rates urgent.","PopM",7.5,INKN); y-=13
else:
    for _a in ACTIONS[:6]:
        _tc=TEAMC8.get(_a["lg"],INKN); c.setFillColor(_tc); c.roundRect(M,y-2.6,30,10.4,3,stroke=0,fill=1)
        txt(c,M+15,y,_a["lg"],"Bebas",9,CARD,"c")
        c.setFillColor(_ARC.get(_a["rank"],GR)); c.circle(M+37,y+2.6,2.1,stroke=0,fill=1)
        _by=_a["by"]; _bw=c.stringWidth(_by,"PopB",6.8); _room=W-M-(M+44)-_bw-14; _wt=_a["what"]
        while c.stringWidth(_wt,"PopM",7.2)>_room and len(_wt)>8: _wt=_wt[:-2].rstrip()+"…" if not _wt.endswith("…") else _wt[:-3].rstrip()+"…"
        txt(c,M+44,y,_wt,"PopM",7.2,INKN); txt(c,W-M,y,_by,"PopB",6.8,_ARC.get(_a["rank"],GR),"r")
        c.setStrokeColor(LINE);c.setLineWidth(.3);c.line(M,y-4.6,W-M,y-4.6); y-=12.5
    if len(ACTIONS)>6: txt(c,M+44,y,f"+ {len(ACTIONS)-6} more, all in the morning brief","Pop",6,GR); y-=10
if ADVICE_SUM: txt(c,M,y-1,"THE ADVICE, GRADED:  "+ADVICE_SUM,"Pop",6,GR); y-=10
y-=12
try:
    R_=_pd.read_csv(_SBF)
except Exception as _ex:
    R_=None; print("SCOREBOARD page: no graded file -",_ex)
if R_ is None or not len(R_):
    txt(c,M,y,"Nothing graded yet. The Scoreboard fills in as games go final.","PopB",9,INKN)
else:
    R_=R_[R_.actual.notna()].copy(); wkn=int(R_.week.max()); cur=R_[R_.week==wkn]; wks=sorted(int(w) for w in R_.week.unique())
    try:
        _GG=_pd.read_csv("/home/claude/dksys/data/latest/games.csv",low_memory=False); _GG=_GG[(_GG.season==_GG.season.max())&(_GG.week==wkn)]
        fin_g=int(_GG.result.notna().sum()); tot_g=len(_GG)
    except Exception: fin_g=tot_g=None
    stc=_sb_stats(cur); sta=_sb_stats(R_)
    txt(c,M,y,_sb_verdict(sta),"PopB",11,INKN)
    txt(c,M,y-12,f"Running total, Weeks {wks[0]}–{wks[-1]}, {len(R_)} men. Every number is the one posted before kickoff, graded against the final stat line in that league's scoring.","Pop",6.2,GR)
    y-=32
    _sb_hd(y,f"THIS WEEK  ·  WEEK {wkn}",(f"{fin_g} of {tot_g} games final  ·  grows every build until Monday night" if fin_g is not None else "grows every build until Monday night")+"  ·  one week is noise")
    y=_sb_tiles(y-12,stc,f"Week {wkn}")-14
    _sb_hd(y,f"RUNNING TOTAL  ·  WEEKS {wks[0]}–{wks[-1]}","The real signal  ·  Weeks 2–4 graded by hand Oct 8, Week 5 on automatic")
    y=_sb_tiles(y-12,sta,f"Weeks {wks[0]}–{wks[-1]}")-14
    # ---- trend: average miss by week, one line per source (left) ... by position (right)
    _sb_hd(y,"THE TREND  ·  BY POSITION","Average points off a man, week by week  ·  and where each source misses most");y-=14
    cx0,cy0,cw,ch=M+22,y-112,250,104
    per={k:[] for k,_ in _SRC}
    for w in wks:
        s_=_sb_stats(R_[R_.week==w])
        for k,_ in _SRC: per[k].append(s_[k]["miss"])
    vals=[v for L in per.values() for v in L if v is not None]
    lo=max(0,int(min(vals))-1);hi=int(max(vals))+1
    c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.6);c.rect(cx0,cy0,cw,ch,stroke=1,fill=1)
    for t in range(lo,hi+1):
        yy=cy0+(t-lo)/(hi-lo)*ch;c.setStrokeColor(LINE);c.setLineWidth(.35);c.line(cx0,yy,cx0+cw,yy);txt(c,cx0-4,yy-2,str(t),"Pop",5.6,GR,"r")
    xs=[cx0+18+i*(cw-36)/max(1,len(wks)-1) for i in range(len(wks))]
    for i,w in enumerate(wks): txt(c,xs[i],cy0-9,f"Wk {w}","Pop",5.8,GR,"c")
    for k,nm in _SRC:
        pts=[(xs[i],cy0+(v-lo)/(hi-lo)*ch) for i,v in enumerate(per[k]) if v is not None]
        c.setStrokeColor(_SCOL[k]);c.setLineWidth(1.6 if k=="gotham" else 1.1)
        for a,b in zip(pts,pts[1:]): c.line(a[0],a[1],b[0],b[1])
        c.setFillColor(_SCOL[k])
        for p_ in pts: c.circle(p_[0],p_[1],1.8,stroke=0,fill=1)
    lx=cx0
    for k,nm in _SRC:
        c.setFillColor(_SCOL[k]);c.rect(lx,cy0+ch+4,8,2.2,stroke=0,fill=1);txt(c,lx+11,cy0+ch+3,nm,"PopM",6,_SCOL[k]);lx+=c.stringWidth(nm,"PopM",6)+24
    txt(c,cx0+cw,cy0+ch+3,"lower = closer","Pop",5.6,GR,"r")
    # by position table
    tx=cx0+cw+28;tcol=[tx,tx+40,tx+92,tx+144,tx+196]
    txt(c,tcol[0],y-4,"POS","PopB",6.2,GR)
    for i,(k,nm) in enumerate(_SRC): txt(c,tcol[i+1]+40,y-4,nm,"PopB",6.2,_SCOL[k],"r")
    ry=y-18
    for p_ in ("QB","RB","WR","TE"):
        g_=R_[R_.pos==p_]
        if not len(g_): continue
        s_=_sb_stats(g_);bm=min(v["miss"] for v in s_.values() if v["miss"] is not None)
        txt(c,tcol[0],ry,p_,"PopB",7.6,INKN);txt(c,tcol[0]+16,ry,f"{len(g_)}","Pop",5.6,GR)
        for i,(k,_) in enumerate(_SRC):
            v=s_[k]
            if v["miss"] is None: continue
            gd=abs(v["miss"]-bm)<.05
            txt(c,tcol[i+1]+22,ry,f"{v['miss']:.1f}","PopB" if gd else "Pop",7.6,ST["green"] if gd else INKN,"r")
            txt(c,tcol[i+1]+40,ry,f"{v['pct']:.0%}" if v["pct"] is not None else "–","Pop",6.2,GR,"r")
        c.setStrokeColor(LINE);c.setLineWidth(.35);c.line(tx,ry-5,W-M,ry-5);ry-=19
    txt(c,tx,ry+2,"Points off a man, then start/sit calls right. Green = closest at that position.","Pop",5.6,GR)
    y=cy0-26
    # ---- disagreement
    SRCK=[k for k,_ in _SRC]; R_["spread"]=R_[SRCK].max(axis=1)-R_[SRCK].min(axis=1)
    hi_=R_[R_.spread>=4]; lo_=R_[R_.spread<4]
    _sb_hd(y,"WHEN THEY DISAGREE","The three split by 4 points or more  ·  the red box on the Field Report  ·  the hard calls");y-=18
    if len(hi_):
        close={k:float(((hi_[k]-hi_.actual).abs()==hi_[SRCK].sub(hi_.actual,axis=0).abs().min(axis=1)).mean()) for k in SRCK}
        txt(c,M,y,f"{len(hi_)} men split 4+ points.  Misses run bigger on them: Yahoo {(hi_.yahoo-hi_.actual).abs().mean():.1f} points off, against {(lo_.yahoo-lo_.actual).abs().mean():.1f} when the three agree.","Pop",6.8,INKN);y-=15
        bx=M+120;bw=W-M-bx-40
        for k,nm in _SRC:
            txt(c,M,y,f"Closest of the three  ·  {nm}","PopM",6.6,_SCOL[k])
            c.setFillColor(SOFT);c.rect(bx,y-1,bw,7,stroke=0,fill=1);c.setFillColor(_SCOL[k]);c.rect(bx,y-1,bw*close[k],7,stroke=0,fill=1)
            c.setStrokeColor(LINE);c.setLineWidth(.4);c.rect(bx,y-1,bw,7,stroke=1,fill=0)
            txt(c,bx+bw+6,y,f"{close[k]:.0%}","PopB",7,INKN);y-=12
    else: txt(c,M,y,"No 4-point splits graded yet.","Pop",6.8,GR);y-=12
    y-=12
    # ---- biggest misses (the receipts) - this week, or the last week with named men
    nmw=R_[R_.league!="seed"]
    if len(nmw):
        bwk=int(nmw.week.max());B_=nmw[nmw.week==bwk].copy()
        B_["avgmiss"]=B_[SRCK].sub(B_.actual,axis=0).abs().mean(axis=1)
        B_=B_.sort_values("avgmiss",ascending=False).drop_duplicates("player").head(int(max(1,min(9,(y-88)//13+1))))
        _sb_hd(y,f"BIGGEST MISSES  ·  WEEK {bwk}","Where all three were furthest off  ·  green = the closest of the three on that man");y-=16
        cols=[M,M+150,M+200,M+258,M+316,M+374,M+440]
        for x_,h_,a_ in zip(cols,("PLAYER","LEAGUE","YAHOO","GOTHAM","SLEEPER","ACTUAL","WHAT HAPPENED"),("l","l","r","r","r","r","l")):
            txt(c,x_+(40 if a_=="r" else 0),y,h_,"PopB",5.8,GR,a_)
        y-=12
        for r in B_.itertuples():
            txt(c,cols[0],y,f"{r.player}, {r.pos}","PopM",7,INKN);txt(c,cols[1],y,r.league,"Pop",6.6,GR)
            ms={k:abs(getattr(r,k)-r.actual) for k in SRCK if _pd.notna(getattr(r,k))}
            best=min(ms,key=ms.get) if ms else None
            for i,k in enumerate(SRCK):
                v=getattr(r,k);txt(c,cols[2+i]+40,y,"–" if _pd.isna(v) else f"{v:.1f}","PopB" if k==best else "Pop",7,ST["green"] if k==best else INKN,"r")
            txt(c,cols[5]+40,y,f"{r.actual:.1f}","PopB",7,INKN,"r")
            nums=[getattr(r,k) for k in ms]
            wh=(f"Beat every number by {r.actual-max(nums):.1f}" if r.actual>max(nums) else f"Under every number by {min(nums)-r.actual:.1f}" if r.actual<min(nums) else "Landed between the numbers") if nums else ""
            txt(c,cols[6],y,wh,"Pop",6.2,GR)
            c.setStrokeColor(LINE);c.setLineWidth(.3);c.line(M,y-4,W-M,y-4);y-=13
    y-=6
    txt(c,M,max(y,48),"Gotham's rule since Oct 11: a game a man left hurt (under 35% of snaps when he usually plays 60% or more) no longer counts against his number.","Pop",5.8,GR)
    txt(c,M,max(y,48)-8,"Oct 13 test (Weeks 2-5, 505 player-weeks): three changes kept, Gotham 6.61 to 6.35 pts a man; practice trim off; middle-starter nudge did not help.","Pop",5.8,GR)
    print("SCOREBOARD page: week",wkn,"| men",len(R_),"| lowest y",round(y))
pass   # Oct 13: the footer pass draws this page's footer
c.showPage()

# OCT12 calibration

# OCT13 scoreboard footnote

# OCT13 calibration no double footer

# OCT13 calls and calibration
