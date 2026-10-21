# THE POST-MORTEM — format sample, DK I, Week 3. One page per league:
#   (1) the team as a whole, (2) player by player with the VALUE marker and a verdict, (3) the week ahead + playoff picture.
# Borrows the scan's helpers (lines 1–265 of p12v7.py and the Call Sheet chip/section helpers) so it is the same design language.
import re,sys,json
_INDOC="PG" in globals()                       # exec'd inside p12v7.py: draw on the shared canvas, as the next page
if not _INDOC:
    SRC=open("/home/claude/cand/redesign/p12v7.py").read().split("\n")
    exec("\n".join(SRC[:265]))
    exec("\n".join(SRC[322:337]))
OUT="/mnt/user-data/outputs/DK_PostMortem_Format_v1.pdf"
if not _INDOC: c=canvas.Canvas(OUT,pagesize=letter)
def _pm_page():
    import pandas as pd
    sys.path.insert(0,"/home/claude/src/role_watch");from rw_core import norm
    OUT="/mnt/user-data/outputs/DK_PostMortem_Format_v1.pdf"
    ORG=H("#F7801E");ADK=H("#C25E0E");DKG=H("#A8740A")
    # ------------------------------------------------------------------ data
    LS=json.load(open("/mnt/user-data/outputs/dkl_db/live/state.json"));LS=LS.get("data",LS)
    LG1=[L for L in LS["leagues"] if L["key"]=="MOST"][0]
    st=pd.read_csv("/home/claude/src/role_watch/data/stats_player_week_2026.csv",low_memory=False).copy()
    st=st[st.season_type=="REG"].copy();st["key"]=st.player_display_name.fillna("").map(norm)
    st["pts"]=st.fantasy_points_ppr+0.25*st.carries.fillna(0)+2*st.passing_tds.fillna(0)   # DK I: full PPR, .25 a carry, 6-pt pass TD (checked vs Yahoo, Week 3)
    st=st[st.position.isin(["QB","RB","WR","TE"])]
    g=st.groupby("key").agg(nm=("player_display_name","first"),pos=("position","last"),tm=("team","last"),gp=("week","nunique"),tot=("pts","sum")).reset_index()
    g["ppg"]=g.tot/g.gp
    elig=g[g.gp>=2].copy();elig["rk"]=elig.groupby("pos").ppg.rank(ascending=False,method="min")
    RK=dict(zip(elig.key,elig.rk));PPG=dict(zip(g.key,g.ppg))
    WK={(k,w):p for k,w,p in zip(st.key,st.week,st.pts)}
    # KICKERS and DEFENSES, standard scoring (checked vs Yahoo Week 3: kickers 5 of 6 exact; defenses within a point or two, one miss)
    _a=pd.read_csv("/home/claude/src/role_watch/data/stats_player_week_2026.csv",low_memory=False);_a=_a[_a.season_type=="REG"].fillna(0)
    _k=_a[_a.position=="K"].copy();_k["key"]=_k.player_display_name.map(norm)
    _k["pts"]=3*(_k.fg_made_0_19+_k.fg_made_20_29+_k.fg_made_30_39)+4*_k.fg_made_40_49+5*(_k.fg_made_50_59+_k.fg_made_60_)+_k.pat_made
    _gm=pd.read_csv("/home/claude/src/role_watch/data/games_fresh_mon.csv");_gm=_gm[(_gm.season==2026)&(_gm.game_type=="REG")&_gm.home_score.notna()]
    _pa={}
    for _,r_ in _gm.iterrows(): _pa[(r_.home_team,r_.week)]=r_.away_score;_pa[(r_.away_team,r_.week)]=r_.home_score
    _d=_a.groupby(["team","week"]).agg(sk=("def_sacks","sum"),it=("def_interceptions","sum"),fr=("fumble_recovery_opp","sum"),td=("def_tds","sum"),stt_=("special_teams_tds","sum"),sf=("def_safeties","sum")).reset_index()
    _d["pa"]=[_pa.get((t,w)) for t,w in zip(_d.team,_d.week)];_d=_d[_d.pa.notna()].copy()
    _tier=lambda p:10 if p==0 else 7 if p<7 else 4 if p<14 else 1 if p<21 else 0 if p<28 else -1 if p<35 else -4
    _d["pts"]=_d.sk+2*_d.it+2*_d.fr+6*(_d.td+_d.stt_)+2*_d.sf+_d.pa.map(_tier)
    for _df,_pos,_kc in ((_k,"K","key"),(_d.assign(key=_d.team),"DEF","key")):
        _gg=_df.groupby(_kc).agg(gp=("week","nunique"),tot=("pts","sum")).reset_index();_gg["ppg"]=_gg.tot/_gg.gp
        _gg=_gg[_gg.gp>=2].copy();_gg["rk"]=_gg.ppg.rank(ascending=False,method="min")
        for kk,pp,rr in zip(_gg[_kc],_gg.ppg,_gg.rk): RK[(_pos,kk)]=rr;PPG[(_pos,kk)]=pp
    TOP={"QB":12,"TE":12,"RB":24,"WR":24,"K":12,"DEF":12}      # a 12-team league starts about 12 QB/TE/K/DEF and 24 RB/WR
    def value(key,pos):
        r=RK.get((pos,key)) if pos in ("K","DEF") else RK.get(key)
        if r is None or pos not in TOP: return None
        t=TOP[pos];return 3 if r<=t else 2 if r<=2*t else 1
    # who is on a DK I roster (A1–A12, IR included). Everyone else is available.
    ROS=set()
    for line in open("/home/claude/src/mkt/rosters_all_wk3_sun.txt"):
        m=re.match(r"A(\d+):(.*)",line.strip())
        if m and m.group(1)!="99":
            for n in m.group(2).split(";"): ROS.add(norm(re.sub(r"\(.*?\)","",n.replace("*","")).strip()))
    def best_free(pos,skip=()):
        f=elig[(elig.pos==pos)&(~elig.key.isin(ROS))&(~elig.key.isin(skip))].sort_values("ppg",ascending=False)
        return f.iloc[0] if len(f) else None
    # his roster: starters from Yahoo's live read (their finals), bench/IR from the Sunday roster line A2
    SL={p["name"]:p for p in LG1["players"]}
    MEN=[(p["slot"],p["name"],p["tm"].upper()) for p in LG1["players"]]+[("BN","Stefon Diggs","NE"),("BN","Kyle Monangai","CHI"),
         ("BN","Kaelon Black","SF"),("BN","Dontayvion Wicks","GB"),("BN","Alvin Kamara","NO"),("IR","Jayden Daniels","WAS")]
    POSOF={"QB":"QB","RB":"RB","WR":"WR","TE":"TE","K":"K","DEF":"DEF"}
    MNF={"CHI","PHI"}
    def wk3(nm,tm):
        if nm in SL and SL[nm]["actual"] is not None: return SL[nm]["actual"]
        return WK.get((norm(nm),3))
    # ------------------------------------------------------------------ marks
    def vmark(x,y,v):
        """VALUE: three rounded cells, left to right — 3 lit = valuable, 2 = average, 1 = weak. Navy on cream. None = grey dash."""
        if v is None: txt(c,x+7.5,y,"—","Pop",7,GR2,"c");return
        for i in range(3):
            c.setFillColor(INKN if i<v else H("#E4DDCD"));c.roundRect(x+i*5.4,y-.6,4.4,6.8,1.2,stroke=0,fill=1)
    def spark(x,y,vals,w=38,hh=10,mx=35):
        pts_=[(x+i*(w/2),y-2+min(v,mx)/mx*hh) for i,v in enumerate(vals) if v is not None]
        c.setStrokeColor(LINE);c.setLineWidth(.4);c.line(x,y-2,x+w,y-2)
        if len(pts_)>=2:
            c.setStrokeColor(INKN);c.setLineWidth(.9);p=c.beginPath();p.moveTo(*pts_[0])
            for q in pts_[1:]: p.lineTo(*q)
            c.drawPath(p,stroke=1,fill=0)
        for i,(px,py) in enumerate(pts_):
            last=(i==len(pts_)-1 and vals[2] is not None)
            c.setFillColor(ORG if last else INKN);c.circle(px,py,1.9 if last else 1.4,stroke=0,fill=1)
    VCOL={"KEEP":INKN,"WATCH":ST["gold"],"REPLACE":ST["red"],"HOLD":GR}
    def wrap(s,w,f,sz):
        out=[""]
        for wd in s.split():
            t=(out[-1]+" "+wd).strip()
            if c.stringWidth(t,f,sz)<=w: out[-1]=t
            else: out.append(wd)
        return out
    # ------------------------------------------------------------------ page
    masthead(c,"THE POST-MORTEM","DK I  ·  TheMostImportantThingInLife  ·  The week that was, and the one coming")
    y=Ht-126
    section(c,y,"THE TEAM","The week in one look",None)
    horizon(c,W-M,y+1.5,"FINALS READ SUN SEP 27 · 9:25 PM",align="r")
    # result card
    cy=y-16;ch=58;c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.6);c.roundRect(M,cy-ch,W-2*M,ch,6,stroke=1,fill=1)
    c.setFillColor(LG["I"]);c.roundRect(M,cy-ch,4,ch,2,stroke=0,fill=1)
    me,op=LG1["score"],LG1["oppScore"];won=me>op
    txt(c,M+14,cy-24,"WON" if won else "LOST","Bebas",26,ST["green"] if won else ST["red"])
    xw=M+14+c.stringWidth("WON" if won else "LOST","Bebas",26)+10
    txt(c,xw,cy-24,f"{me:.1f}","Bebas",26,INKN);xw+=c.stringWidth(f"{me:.1f}","Bebas",26)+6
    txt(c,xw,cy-24,"–","Bebas",26,GR2);xw+=c.stringWidth("–","Bebas",26)+6;txt(c,xw,cy-24,f"{op:.1f}","Bebas",26,GR)
    txt(c,M+14,cy-40,f"vs {LG1['opp']}  ·  manager {LG1['mgr']}  ·  won by {me-op:.1f}","PopM",7.2,GR)
    txt(c,M+14,cy-51,"Record now 1–2 (was 0–2).","PopB",7.2,INKN)
    # the four biggest and the weak spot, right side of the card
    sp=sorted(LG1["players"],key=lambda p:-(p["actual"] or 0))
    rx=M+300;txt(c,rx,cy-16,"CARRIED IT","PopB",5.4,GR)
    for i,p in enumerate(sp[:4]):
        txt(c,rx,cy-27-i*9.2,p["name"],"PopB",7.0,INKN);txt(c,rx+118,cy-27-i*9.2,f"{p['actual']:.1f}","PopB",7.0,ADK,"r")
    wk=min(LG1["players"],key=lambda p:(p["actual"] or 0)-(p["proj"] or 0))
    rx2=rx+140;txt(c,rx2,cy-16,"FELL SHORT","PopB",5.4,GR)
    txt(c,rx2,cy-27,wk["name"],"PopB",7.0,INKN);txt(c,rx2,cy-36.2,f"{wk['actual']:.1f}  vs  {wk['proj']:.1f} projected","Pop",6.6,GR)
    lo=min(LG1["players"],key=lambda p:p["actual"] or 0)
    # the opening paragraph — every clause is a number on this page
    py=cy-ch-13
    para=[f"A {me-op:.0f}-point win, the first of the season. Shough threw four touchdowns, and London, McCaffrey and Warren each cleared 24.",
          f"The one soft spot was the second flex: Henderson managed {wk['actual']:.1f} against a {wk['proj']:.1f} projection as New England lost 35–6.",
          "It climbs off 0–2 with eleven regular-season weeks left. Six of twelve make the playoffs."]
    for i,s in enumerate(para): txt(c,M+4,py-i*9.6,s,"Pop",7.2,INKN)
    # ------------------------------------------------------------------ player by player
    y=py-3*9.6-16
    section(c,y,"PLAYER BY PLAYER","Standing against the whole league at his position, how he's trending, and whether to replace him",None)
    X=dict(v=M+2,n=M+24,s=M+128,p=M+142,t=M+160,w3=M+206,av=M+240,rk=M+270,sp=M+282,vd=M+330,nt=M+376)
    hy=y-19
    for k_,t_ in (("n","PLAYER"),("s","STA"),("p","POS"),("t","TEAM"),("sp","WKS 1–3"),("vd","VERDICT"),("nt","WHY — AND WHO ELSE")): hdr(c,X[k_],hy,t_)
    hdr(c,X["v"],hy,"VALUE");hdr(c,X["w3"],hy+7,"WEEK 3","r");hdr(c,X["w3"],hy,"PTS","r");hdr(c,X["av"],hy+7,"SEASON","r");hdr(c,X["av"],hy,"A GAME","r")
    hdr(c,X["rk"],hy+7,"NFL","r");hdr(c,X["rk"],hy,"RANK","r")
    ry=hy-14;used=set();stats={"REPLACE":0,"WATCH":0}
    for gi,(slot,nm,tm) in enumerate(MEN):
        if slot=="BN" and MEN[gi-1][0]!="BN":
            ry-=3;hdr(c,X["n"],ry,"BENCH");ry-=11
        if slot=="IR":
            ry-=3;hdr(c,X["n"],ry,"INJURED RESERVE");ry-=11
        key=norm(nm);pos=({"W/R/T":None,"BN":None,"IR":None}.get(slot,slot)) or (g[g.key==key].pos.iloc[0] if (g.key==key).any() else "")
        if slot in ("K","DEF"): pos=slot
        kk_=tm if pos=="DEF" else key          # a defense is ranked by its team
        v=value(kk_,pos);a=wk3(nm,tm)
        avg=PPG.get((pos,kk_)) if pos in ("K","DEF") else PPG.get(key);rk=RK.get((pos,kk_)) if pos in ("K","DEF") else RK.get(key)
        stt=(SL.get(nm) or {}).get("status","") if nm in SL else ("O" if slot=="IR" else "")
        if nm in SL and SL[nm]["when"].startswith("Final"): stt=""       # a flag drops once the game is final
        if gi%2==0: c.setFillColor(SOFT);c.rect(M,ry-4,W-2*M,13.4,stroke=0,fill=1)
        vmark(X["v"],ry,v);txt(c,X["n"],ry,nm,"PopB",7.2,INKN)
        if stt: txt(c,X["s"],ry,SLET.get(stt,stt),"PopM",7,INKN)
        txt(c,X["p"],ry,pos,"Pop",6.8,GR);tier(c,X["t"],ry,tm,6.8)
        if a is not None: txt(c,X["w3"],ry,f"{a:.1f}","PopB",7.2,ADK,"r")
        else:
            lab_="MON" if tm in MNF else ("DNP" if slot!="IR" and pos in TOP else "—")
            txt(c,X["w3"],ry,lab_,"PopM" if lab_!="—" else "Pop",6.4,GR if lab_!="—" else GR2,"r")
        txt(c,X["av"],ry,"—" if avg is None else f"{avg:.1f}","PopM" if avg is not None else "Pop",7,INKN if avg is not None else GR2,"r")
        txt(c,X["rk"],ry,"—" if rk is None else f"{pos}{int(rk)}","Pop",6.6,GR if rk is not None else GR2,"r")
        if pos in TOP: spark(X["sp"],ry,[WK.get((key,w)) for w in (1,2,3)])
        # verdict — plain rules, printed in the legend
        bf=best_free(pos,used) if pos in TOP else None
        prior=[WK.get((key,w)) for w in (1,2)];prior=[q for q in prior if q is not None];pav=sum(prior)/len(prior) if prior else None
        if slot=="IR": vd="HOLD";why="On IR — costs no roster spot. Nothing to decide until he's back."
        elif v is None: vd="KEEP";why="Not enough games on record to rank him yet."
        elif a is None and tm not in MNF and pos in TOP: vd="WATCH";why="Didn't play in Week 3 — check his status before he starts again."
        elif pos in ("K","DEF") and v==1: vd="WATCH";why=f"{pos}{int(rk)} — bottom of the pool. Worth a look at the wire."
        elif pos in ("K","DEF") and v==2: vd="KEEP";why=f"{pos}{int(rk)} — middle of the pool."
        elif v==1 and bf is not None and avg is not None and bf.ppg>=avg+3:
            vd="REPLACE";used.add(bf.key);why=f"Bottom of the {pos} pool. Free: {bf.nm} ({bf.tm}), {bf.ppg:.1f} a game."
        elif v==1: vd="WATCH";why=f"Weak for a {pos}, but no free man clears him by 3 a game."+(f" Best: {bf.nm}, {bf.ppg:.1f}." if bf is not None else "")
        elif a is not None and pav and a<.6*pav and v<3: vd="WATCH";why=f"Week 3 was {a:.1f} against {pav:.1f} before. One bad week, or a slide."
        elif v==3: vd="KEEP";why=f"{pos}{int(rk)} in the NFL — an every-week starter."
        else:
            vd="KEEP"
            why=(f"Middle of the {pos} pool. Best free: {bf.nm}, {bf.ppg:.1f} a game." if bf is not None and bf.ppg>(avg or 0)
                 else f"Middle of the {pos} pool — nothing better is free.")
        if vd in stats: stats[vd]+=1
        pill(c,X["vd"],ry-.4,vd,VCOL[vd],PAPER,5.4,"PopB",4)
        txt(c,X["nt"],ry,why,"Pop",6.1,GR)
        ry-=13.4
    # ------------------------------------------------------------------ the week ahead
    y=ry-14
    section(c,y,"THE WEEK AHEAD","Each man against the man across from him — and who the opponent is",None)
    horizon(c,W-M,y+1.5,"OPPONENT LOADS TUESDAY",align="r")
    bx=M;bw=(W-2*M-10)/2;by=y-14;bh=86
    for i,(ttl,lines) in enumerate((("MAN AGAINST MAN",["Slot by slot: his starter, the opponent's, and the gap between them on the blend.",
          "Gap bars run from the middle — his side left in league blue, theirs right in grey — the longest bars are the week's swing spots.",
          "Byes and injuries on either side print in the row, not in a footnote."]),
         ("THE OPPONENT",["Record, place and points so far · how many of his starters are hurt or on bye.",
          "His best two men and his weakest slot — where the matchup is won.",
          "Win chance: the four-source blend beside Yahoo's, same as page one."]))):
        x0=bx+i*(bw+10);c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.6);c.roundRect(x0,by-bh,bw,bh,5,stroke=1,fill=1)
        txt(c,x0+10,by-14,ttl,"PopB",6.2,INKN)
        ly=by-28
        for s in lines:
            for ln in wrap(s,bw-20,"Pop",6.3): txt(c,x0+10,ly,ln,"Pop",6.3,GR);ly-=8.6
            ly-=2
    # playoff picture
    y=by-bh-18
    section(c,y,"THE PLAYOFF PICTURE","Six of twelve make it · division winners take the top seeds · Weeks 15–17",None)
    horizon(c,W-M,y+1.5,"TABLE THROUGH WEEK 2 · WEEK 3 LOADS TUESDAY",align="r")
    txt(c,M+4,y-18,"Through Week 2 DK I sat 11th of 12 at 0–2. The win makes it 1–2; where that lands depends on the other five games, which Tuesday's read fills in.","Pop",7.0,INKN)
    txt(c,M+4,y-28,"The full version draws the League Race chart here — same bands as the league page — with DK I's ball moved to its new place.","Pop",7.0,GR)
    # legend
    ky=48;x=M+2
    txt(c,x,ky,"Legend:","PopB",6.2,INKN);x+=c.stringWidth("Legend:  ","PopB",6.2)
    for v_,t_ in ((3,"Valuable"),(2,"Average"),(1,"Weak")):
        vmark(x,ky,v_);x+=19;txt(c,x,ky,t_,"Pop",6,GR);x+=c.stringWidth(t_,"Pop",6)+10
    txt(c,x,ky,"— against every NFL player at his position, by points a game: QB and TE top 12 valuable, 13–24 average; RB and WR top 24, 25–48.","Pop",6,GR)
    txt(c,M+36,ky-9,"Verdict: REPLACE = weak and a free man beats him by 3+ a game · WATCH = weak with nothing better free, a big drop, or didn't play · KEEP · HOLD = on IR.","Pop",6,GR)
    txt(c,M+36,ky-18,"Orange = what he scored in Week 3, the same meaning it has everywhere in the scan. The line runs Weeks 1, 2, 3.","Pop",6,GR)
    footer(c,(PG+1) if _INDOC else 1,"The Post-Mortem · DK I")
    print("post-mortem lowest row",ry,"stats",stats)

try: _pm_page()
except Exception as _e: print("PM page skipped (Week 3 page, no data):",_e)
if _INDOC: c.showPage();PG+=1
else: c.save()
