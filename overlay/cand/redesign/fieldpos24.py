# v24 (Oct 9): adds THE SCOUT page per league after the Field Report. Driver: the v8 chain for shared helpers, then per league: FIELD REPORT (2 pp, v17) + POSITIONS (v17).
import sys, os, shutil, glob, re
_OUT10=sys.argv[1]
src=open("/home/claude/cand/redesign/p12v10.py").read().replace("/mnt/user-data/outputs/DK_Redesign_Sample_v9.pdf","/tmp/_chain_v9.pdf")
exec(src)
#for f in glob.glob("/mnt/user-data/outputs/Mark_Batch_Mockup_v*.pdf"): shutil.move(f,"/home/claude/scratch_sidefx/"+os.path.basename(f))
exec(open("/home/claude/cand/redesign/fp23_live.py").read())          # v23: week, Gotham, live data - before any page code
exec(open("/home/claude/cand/redesign/_fr_positions18.py").read().replace("ENGINE — POINTS A GAME, NEXT THREE GAMES","GOTHAM — POINTS A GAME, NEXT THREE GAMES").replace("DARK KNIGHT FANTASY FOOTBALL","DARK KNIGHT DISPATCH")
     .replace('_s10.argv=["engine3.py",_os18.environ.get("DK_WEEK","5")];import engine3 as _E10','_s10.argv=["engine3v.py",str(WEEKN)];import engine3v as _E10')
     .replace('"Week 4  ·  Positions  ·  "','f"Week {WEEKN}  ·  Positions  ·  "').replace('"sources far lower than the engine — "','"Sleeper far lower than Gotham — "').replace('for _,o in Op.iterrows()))','for _,o in Op.head(4).iterrows()))'))
exec(open("/home/claude/cand/redesign/fp23_shim.py").read())          # v23: Gotham numbers into the engine rows, rostered counts, stamps
exec(open("/home/claude/cand/redesign/_masthead_puzzle.py").read())   # v17c: puzzle masthead
exec(open("/home/claude/cand/redesign/_masthead_field.py").read())   # v8 masthead: four-piece field puzzle
PZ_TITLE="DARK KNIGHT DISPATCH"   # v49: the report is the Dispatch (Dom, Mon Oct 5)
exec(open("/home/claude/cand/redesign/_fresh.py").read())   # freshness stamps: one per block, date and time
SECSTAMP["week"]["STARTERS"]=["live"]   # v48: the starters table reads the same sweep as the meter
_fr=open("/home/claude/cand/redesign/fr17c.py").read().replace("DARK KNIGHT FANTASY FOOTBALL","DARK KNIGHT DISPATCH")
_fr=_fr.replace("    _CL=clu17(LG_,_E10.run(LG_)[0])","    _RD=_E10.run(LG_)[0];DMK.clear();DMK.update({r_d.player:(r_d.drift_swing>0) for r_d in _RD.itertuples() if r_d.drift=='D'})   # v22: D marks\n    _CL=clu17(LG_,_RD)",1)
for _a,_b in (('c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.6);c.roundRect(x,y,w,h,7,stroke=1,fill=1)','gcard(c,x,y,w,h,LG[d["k"]])'),('c.setFillColor(CARD);c.setStrokeColor(LINE);c.setLineWidth(.6);c.roundRect(px,top-gh,pw,gh,7,stroke=1,fill=1)','gcard(c,px,top-gh,pw,gh,INKN)'),('stamp(c,M+gw-4,top+5,["yahoo"])','stamp(c,M+gw-4,top+5,["live"])'),('"Win chance — Yahoo, read Sat morning"','"Win probability — Yahoo center, Gotham left, Sleeper right"'),('gauge(c,x+54,T-84,30,d["win"],d["last"],col,False,d["me"]>d["opp"])','gauge_m3(c,x+54,T-84,30,d["win"],d["last"],d["eff"],col,d["comp"])'),
              ('"PROJECTED — BEST LINEUPS"','"YAHOO NOW — PROJECTED FINAL"'),
              ('(BR,"ENGINE","NEXT 3")','(BR,"MODELED","NEXT 3")'),
              ('(BR,"MODELED","NEXT 3")','(GW,"GOTHAM",f"WEEK {WEEKN}"),(BR,"GOTHAM","NEXT 3")'),
              ('    fdec(c,BR,ry,fwd17(','    _gwcell(c,GW,ry,nm,stt)\n    fdec(c,BR,ry,fwd17('),
              ('"Blend = Yahoo, Rotowire, CBS and ESPN, all read Sat Oct 3 night — Yahoo beside it, bold when they part by 3. Next 3 = points a game, his next three."','NUMBERS_NOTE')):
    assert _fr.count(_a)==1,_a; _fr=_fr.replace(_a,_b)
_fr=_fr.replace('"Their best lineup off the Saturday-night roster read (Sat Oct 3)."','"Whoever Yahoo shows across from you, same sweep as the meter (Sun 2:20 p.m. PT)."')
# v48 (Dom, Sun Oct 4): one timestamp for the whole page - the tables and THE GAME read the same sweep as the meter
for _a,_b in (('(YH,"YAHOO","WEEK 4")','(YH,"YAHOO","NOW")'),('(B3,"BLEND","WEEK 4")','(B3,"SLEEPER",f"WEEK {WEEKN}")'),('(OPP,"OPPONENT","PTS")','(OPP,"THEIR MAN","NOW")'),
              ('''    yv=yah17(nm,LAB17) if stt not in ("O","IR") else None
    if yv is not None and not fin:
        far=bl not in (None,"") and abs(float(bl)-yv)>=3
        fdec(c,YH,ry,f"{yv:.1f}",False,"PopB" if far else "PopM",7.2,INKN)
    else: fdec(c,YH,ry,None,False,"PopM",7.2)''','''    _n=_NOWME(nm)
    if _n: _nowcell(c,YH,ry,_n,(_mrow(nm,LAB17) or {}).get("team"),"PopB")
    else: fdec(c,YH,ry,None,False,"PopM",7.2)'''),
              ('ry=h-15;mine=theirs=0;t0=ry+RP_-4.4','ry=h-15;mine=theirs=0;blsum=0;t0=ry+RP_-4.4'),
              ('''        txt(c,OPN,ry,om,"Pop",7,INKN);fdec(c,OPP,ry,ov,of,"PopM",7.2)
        if bl and ov:
            d=float(bl)-float(ov);mine+=float(bl);theirs+=float(ov)''','''        _a=_NOWME(nm);_b=_NOWOP(om)
        txt(c,OPN,ry,om,"Pop",7,INKN);(_nowcell(c,OPP,ry,_b,(OPMAP.get(om) or {}).get("team"),"PopM") if _b else fdec(c,OPP,ry,None,False,"PopM",7.2))
        if bl: blsum+=float(bl)
        if _a and _b:
            d=_a[0]-_b[0];mine+=_a[0];theirs+=_b[0]'''),
              ('txt(c,NX,ry+1,"BEST POSSIBLE LINEUP","PopB",6.6,INKN);dec(c,B3,ry+1,f"{mine:.1f}","PopB",8,INKN,5.4,"")',
               'txt(c,NX,ry+1,"LINEUP AS SET","PopB",6.6,INKN);dec(c,B3,ry+1,f"{blsum:.1f}","PopM",8,GR,5.4,"");dec(c,YH,ry+1,f"{mine:.1f}","PopB",8,INKN,5.4,"")'),
              ('ds=[(float(r[8])-float(r[10]),r[1],r[9]) for r in STARTS if r[1] and r[8] and r[10]]',
               'ds=[(_NOWME(r[1])[0]-_NOWOP(r[9])[0],r[1],r[9]) for r in STARTS if r[1] and _NOWME(r[1]) and _NOWOP(r[9])]'),
              ('"Blend, both sides at best lineup"','"Yahoo now, both lineups as set"'),
              ('stamp(c,px+pw-4,top+5,["market","news"])','stamp(c,px+pw-4,top+5,["live","news"])')):
    assert _fr.count(_a)==1,_a; _fr=_fr.replace(_a,_b)

for _a,_b in (('"Week 4  ·  Field Report  ·  "','f"Week {WEEKN}  ·  Field Report  ·  "'),
              ('horizon(c,px+12,yy,"WEEK 4",','horizon(c,px+12,yy,f"WEEK {WEEKN}",'),
              ("if r['home_score']!='' and int(r['week'])<=4:","if r['home_score']!='' and int(r['week'])<WEEKN:"),
              ('WK17=4','WK17=WEEKN'),
              ('"The season ahead, Weeks 4–17"','f"The season ahead, Weeks {WEEKN}–17"'),
              ('"Every man, Weeks 4–17 — the playoff weeks framed"','f"Every man, Weeks {WEEKN}–17 — the playoff weeks framed"'),
              ('WK=list(range(4,18))','WK=list(range(WEEKN,18))'),
              ('"Colors run off every game played so far — Weeks 1–3, plus Thursday\'s Pittsburgh–Cleveland — and recalculate every week."','f"Colors run off every game played so far — Weeks 1–{WEEKN-1} — and recalculate every build."'),
              ('"Whoever Yahoo shows across from you, same sweep as the meter (Sun 2:20 p.m. PT)."','"Whoever Yahoo shows across the matchup — the same read as the meter."')):
    assert _fr.count(_a)==1,_a; _fr=_fr.replace(_a,_b)
def gauge_m(c,cx,cy,r,v,mv,col):
    """v19: the same meter as the Overview - solid needle and big number = Yahoo, dotted needle and small number = modeled."""
    c.setLineCap(0)
    c.setStrokeColor(SOFT);c.setLineWidth(r*.26);c.arc(cx-r,cy-r,cx+r,cy+r,0,180)
    c.setStrokeColor(col);c.arc(cx-r,cy-r,cx+r,cy+r,180-180*v/100,180*v/100)
    for t in range(0,101,25):
        a=math.radians(180-1.8*t);c.setStrokeColor(PAPER if t not in (0,100) else SOFT);c.setLineWidth(1.2)
        c.line(cx+(r-r*.13)*math.cos(a),cy+(r-r*.13)*math.sin(a),cx+(r+r*.13)*math.cos(a),cy+(r+r*.13)*math.sin(a))
    am=math.radians(180-1.8*mv);c.saveState();c.setDash(2,1.6);c.setStrokeColor(GR);c.setLineWidth(1.3)
    c.line(cx,cy,cx+r*.98*math.cos(am),cy+r*.98*math.sin(am));c.restoreState()
    a=math.radians(180-1.8*v);c.setStrokeColor(INKN);c.setLineWidth(2.2);c.setLineCap(1);c.line(cx,cy,cx+r*1.02*math.cos(a),cy+r*1.02*math.sin(a));c.setLineCap(0)
    c.setFillColor(INKN);c.circle(cx,cy,3,stroke=0,fill=1)
    txt(c,cx-6,cy-20,f"{v}%","Bebas",23,INKN,"c")
    mx=cx+27;txt(c,mx,cy-6.5,"MODELED","PopB",4.6,GR,"c")
    c.saveState();c.setDash(2,1.4);c.setStrokeColor(GR);c.setLineWidth(.9);c.line(mx-9,cy-9.5,mx+9,cy-9.5);c.restoreState()
    txt(c,mx,cy-21,f"{mv}%","Bebas",12,GR,"c")
    txt(c,cx,cy-28.5,"PROJECTED WIN PROBABILITY","PopB",5.2,INKN,"c")

def gauge_m3(c,cx,cy,r,v,mw,me,col,cp):
    """v20: the Overview meter on paper - Yahoo center (boldest needle), WORKLOAD left (toned, thinner), EFFICIENCY right
    (new: thinnest, dotted). Gold outer ticks = share of the matchup already played."""
    c.setLineCap(0)
    bo=r*1.13;bw=r*.36;bi=bo-bw;rc=(bo+bi)/2   # v23 (Dom): band thickened inward, ruled lines following the arc
    c.setStrokeColor(SOFT);c.setLineWidth(bw);c.arc(cx-rc,cy-rc,cx+rc,cy+rc,0,180)
    c.setStrokeColor(col);c.arc(cx-rc,cy-rc,cx+rc,cy+rc,180-180*v/100,180*v/100)
    c.saveState()
    for f_,lw_,al_ in ((.13,.9,.55),(.33,.7,.38),(.53,.52,.24),(.73,.36,.13)):
        rr_=bi+bw*f_;c.setStrokeColor(INKN);c.setStrokeAlpha(al_);c.setLineWidth(lw_);c.arc(cx-rr_,cy-rr_,cx+rr_,cy+rr_,180-180*v/100,180*v/100)
    c.restoreState()
    for t in range(0,101,25):
        a=math.radians(180-1.8*t);c.setStrokeColor(PAPER if t not in (0,100) else SOFT);c.setLineWidth(1.2)
        c.line(cx+bi*math.cos(a),cy+bi*math.sin(a),cx+bo*math.cos(a),cy+bo*math.sin(a))
    ro=r+r*.13+1.2;comp=cp["all_pct"]
    for t in range(0,101,5):
        a=math.radians(180-1.8*t);on=t<=comp and comp>0;lg=t%25==0
        c.setStrokeColor(H("#E0A526") if on else LINE);c.setLineWidth((.9 if lg else .7) if on else .45)
        c.line(cx+ro*math.cos(a),cy+ro*math.sin(a),cx+(ro+(3.6 if lg else 2.4))*math.cos(a),cy+(ro+(3.6 if lg else 2.4))*math.sin(a))
    # v22: Yahoo down first, full length; the models print over it on a white halo, shorter, each with its own tip
    NS=((v,1.0,INKN,None,1.02,None),(mw,.68,GR,None,.86,"dot"),(me,.45,GR,(1.6,1.3),.70,"ring"))
    for val,wf,cl,ds,lf,tip in NS:
        a=math.radians(180-1.8*val);L=r*lf;tx,ty=cx+L*math.cos(a),cy+L*math.sin(a);c.saveState();c.setLineCap(1)
        if tip: c.setStrokeColor(CARD);c.setLineWidth(2.2*wf+1.6);c.line(cx,cy,tx,ty)
        c.setStrokeColor(cl);c.setLineWidth(2.2*wf)
        if ds: c.setDash(*ds)
        c.line(cx,cy,tx,ty);c.setDash()
        if tip=="dot": c.setFillColor(CARD);c.circle(tx,ty,3.0,fill=1,stroke=0);c.setFillColor(cl);c.circle(tx,ty,2.1,fill=1,stroke=0)
        if tip=="ring": c.setFillColor(CARD);c.circle(tx,ty,2.6,fill=1,stroke=0);c.setStrokeColor(cl);c.setLineWidth(.8);c.circle(tx,ty,1.7,fill=0,stroke=1)
        c.restoreState()
    c.setFillColor(INKN);c.circle(cx,cy,3,stroke=0,fill=1)
    def key(x,y,wf,cl,ds,ln):
        c.saveState();c.setStrokeColor(cl);c.setLineWidth(max(.6,1.8*wf));c.setLineCap(1)
        if ds: c.setDash(*ds)
        c.line(x-ln/2,y,x+ln/2-(2 if ds or cl==GR else 0),y);c.setDash()
        if cl==GR and not ds: c.setFillColor(cl);c.circle(x+ln/2,y,1.5,fill=1,stroke=0)
        if ds: c.setLineWidth(.7);c.circle(x+ln/2,y,1.5,fill=0,stroke=1)
        c.restoreState()
    txt(c,cx,cy-19,f"{v}%","Bebas",21,INKN,"c");key(cx,cy-22,1.0,INKN,None,18);txt(c,cx,cy-27,"YAHOO","PopB",4.4,INKN,"c")
    for x,val,wf,cl,ds,lab in ((cx-31,mw,.68,GR,None,"GOTHAM"),(cx+31,me,.45,GR2,(1.6,1.3),"SLEEPER")):
        txt(c,x,cy-16,f"{val}%","Bebas",10.5,GR,"c");key(x,cy-19,wf,GR,ds,13);txt(c,x,cy-23.5,lab,"PopB",3.9,GR,"c")   # v21: equal models, equal type
    txt(c,cx,cy-33,"PROJECTED WIN PROBABILITY","PopB",5.0,INKN,"c")

def gcard(c,x,y,w,h,col):
    """v20: the card graduates like the Overview blocks - clean white at the bottom, deepening toward the top."""
    c.saveState();p=c.beginPath();p.roundRect(x,y,w,h,7);c.clipPath(p,stroke=0)
    top=mix(CARD,col,.30) if "mix" in globals() else CARD
    c.linearGradient(x,y,x,y+h,(CARD,CARD,top),(0,.35,1),extend=False);c.restoreState()
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.roundRect(x,y,w,h,7,stroke=1,fill=0)
exec(_fr)   # v18: every number says whose it is - Yahoo, blend or modeled
import pandas as _pd

# ===================== v23 (Thu Oct 8 2026): every page off the data - nothing typed per week =====================
import pandas as _pd
NX_=NX;B3=NX_+272;YH=NX_+303;GW=NX_+334;BR=NX_+365;AA=NX_+396;OPN=NX_+414;OPP=NX_+478;PAIR=(OPN-8,OPP+15)
DL=W-M-13   # Oct 10: DELTA clear of its divider
exec(open("/home/claude/cand/redesign/_oct10_fr.py").read())   # Oct 10: team-name capitals, the Scout mark in the MARKER column
NUMBERS_NOTE=f"Gotham = ours: this week (pregame once played), next 3. Yahoo = now. Sleeper = league scoring. Actual = avg Wks 1–{WEEKN-1}. Red box: Gotham, Yahoo 4+ apart. Green glow: game on now."
# ---- freshness stamps: every block reads one data build, so one time, no pile-up
_PT23=_d23.timezone(_d23.timedelta(hours=-7))
def _iso23(k):
    p=MTR["sources"].get(k,{}).get("pulled_pt")
    if not p: return None
    try:
        parts=p.replace(" PT","").split(); s=" ".join(parts[1:3])+" "+str(_d23.datetime.now(_PT23).year)+" "+" ".join(parts[-2:])
        return _d23.datetime.strptime(s,"%b %d %Y %I:%M %p").replace(tzinfo=_PT23).isoformat()
    except Exception: return None
_SRCK={"yahoo":"yahoo_matchups","live":"yahoo_matchups","stats":"nfl_schedule","schedule":"nfl_schedule","engine":"gotham","market":"sleeper_skill","news":"sleeper_kdef"}
FRESH={k:dict(at=_iso23(v) or _d23.datetime.now(_PT23).isoformat(),label=v.split("_")[0].upper()) for k,v in _SRCK.items()}
_WEEKK=["live","stats","engine"];_SEASK=["schedule","stats"]
SECSTAMP={"week":{"STARTERS":_WEEKK,"BENCH":_WEEKK,"IR":_WEEKK},"season":{"THE SEASON AHEAD  ·  STARTERS":_SEASK,"BENCH":_SEASK,"IR":_SEASK}}
_horizon0=horizon
def horizon(c,*a,**k):                                    # v23: the season chip reads the current week
    a=tuple((f"WEEKS {WEEKN}–17" if x=="WEEKS 4–17" else x) for x in a); return _horizon0(c,*a,**k)
_note0=note
def note(c,x,y,a,b,sz=6.2,*r,**k):                        # v23: a note never runs past its card or the page edge
    lim=(W-M-14 if x>W/2 else W-M)-x-c.stringWidth(a+":  ","PopB",sz)
    while c.stringWidth(b,"Pop",sz)>lim and sz>5.0: sz-=.1
    while c.stringWidth(b,"Pop",sz)>lim and len(b)>12: b=b[:-2].rstrip(" ,;·")+"…"
    return _note0(c,x,y,a,b,sz,*r,**k)
# ---- the numbers on every row
EN={}
for _lab in ("DK I","DK II","DK III","DK IV"):
    _e=_pd.read_csv(f"/home/claude/dksys/engine/gotham_{_lab.replace(' ','')}.csv"); _e["k"]=_e.k.astype(str); EN[_lab]=_e
SW=_pd.read_csv("/home/claude/dksys/data/latest/stats_week.csv",low_memory=False); SW=SW[(SW.season==2026)&(SW.week<WEEKN)&(SW.season_type=="REG")]
SW["k"]=SW.player_display_name.fillna("").astype(str).map(norm)
def _mrows(lab):
    L=MTR["leagues"][lab]; return L["starters"]["me"]+L.get("bench",[])
def _mrow(nm,lab):
    k=norm(nm)
    for p in _mrows(lab):
        if norm(p["player"])==k: return p
    return None
def _pos17(nm,lab):
    p=_mrow(nm,lab); return None if p is None else p["pos"]
def team_of(nm,lab):
    p=_mrow(nm,lab); return None if p is None else _gt(p["team"])
def wk17(nm,lab):
    p=_mrow(nm,lab)
    if p is None: return None,False
    if p.get("actual") is not None: return f"{p['actual']:.1f}",True
    return (None if p.get("sleeper") is None else f"{p['sleeper']:.1f}"),False
def wkm17(nm,lab):
    p=_mrow(nm,lab)
    if p is not None and p["pos"] in ("K","DEF"): return None            # Gotham borrows Sleeper there - not shown twice
    e=EN[lab];m=e[e.k==norm(nm)]
    if not m.empty and bool(m.played_wk.iloc[0]):          # Oct 11: game played - show Gotham's pregame number, not the actual
        pv=_pregame_g(nm,lab); return None if pv is None else f"{pv:.1f}"
    return None if m.empty or _pd.isna(m.eng_wk.iloc[0]) else f"{float(m.eng_wk.iloc[0]):.1f}"
_PREG={}
def _pregame_g(nm,lab):
    import os as _po, json as _pj
    if "d" not in _PREG:
        f=_po.path.join(_po.environ.get("GITHUB_WORKSPACE","/nonexistent"),"dispatch_out","scoreboard",f"pregame_wk{WEEKN}.json")
        try: _PREG["d"]=_pj.load(open(f))
        except Exception: _PREG["d"]={}
    for v in _PREG["d"].values():
        if v.get("league")==lab and norm(v.get("player",""))==norm(nm) and v.get("gotham") is not None: return float(v["gotham"])
    return None
def _gw_started(nm):
    import datetime as _gd; from zoneinfo import ZoneInfo as _gz
    p=_mrow(nm,LAB17); t=(p or {}).get("team")
    if not t: return True
    g=_pd.read_csv("/home/claude/dksys/data/latest/games.csv",low_memory=False); t={"LAR":"LA","JAC":"JAX","WSH":"WAS"}.get(t,t)
    g=g[(g.season==g.season.max())&(g.week==WEEKN)&((g.home_team==t)|(g.away_team==t))]
    if g.empty: return True
    ko=_gd.datetime.strptime(f"{g.gameday.iloc[0]} {g.gametime.iloc[0]}","%Y-%m-%d %H:%M").replace(tzinfo=_gz("America/New_York"))
    return _gd.datetime.now(_gd.timezone.utc)>=ko
def _gwcell(c,x,y,nm,stt):
    from reportlab.lib.colors import HexColor as _HX
    v=wkm17(nm,LAB17) if stt not in ("O","IR") else None
    n=_NOWME(nm) if v is not None else None
    flag=bool(n) and not n[1] and abs(float(v)-float(n[0]))>=4 and not _gw_started(nm)   # pregame only: after kickoff the numbers mean other things
    if flag: c.setStrokeColor(_HX("#C62828")); c.setLineWidth(.8); c.roundRect(x-17,y-3,34,10.5,2.5,stroke=1,fill=0)
    fdec(c,x,y,v,False,"PopB" if flag else "PopM",7.2,_HX("#C62828") if flag else INKN)
def _team_live(t):
    import datetime as _ld; from zoneinfo import ZoneInfo as _lz
    if not t: return False
    if "g" not in _PREG: _PREG["g"]=_pd.read_csv("/home/claude/dksys/data/latest/games.csv",low_memory=False)
    g=_PREG["g"]; t={"LAR":"LA","JAC":"JAX","WSH":"WAS"}.get(t,t)
    g=g[(g.season==g.season.max())&(g.week==WEEKN)&((g.home_team==t)|(g.away_team==t))]
    if g.empty or g.result.notna().iloc[0]: return False
    ko=_ld.datetime.strptime(f"{g.gameday.iloc[0]} {g.gametime.iloc[0]}","%Y-%m-%d %H:%M").replace(tzinfo=_lz("America/New_York"))
    now=_ld.datetime.now(_ld.timezone.utc); return ko<=now<=ko+_ld.timedelta(hours=4)
def _nowcell(c,x,y,n,team,font):
    from reportlab.lib.colors import HexColor as _HX
    if n and not n[1] and _team_live(team):
        G=_HX("#3FB36A"); c.saveState()
        for k,a in ((2.4,.10),(1.5,.16),(.7,.24)): c.setFillColor(G); c.setFillAlpha(a); c.roundRect(x-17-k,y-3-k,34+2*k,10.5+2*k,2.5+k,stroke=0,fill=1)
        c.restoreState()
        fdec(c,x,y,f"{n[0]:.1f}",False,font,7.2,INKN)
        b=f"{n[0]:.1f}".split(".")[1]; txt(c,x+c.stringWidth("."+b,font,7.2)+1.6,y,"LIVE","PopB",4.6,_HX("#1E7A45"))
    else: fdec(c,x,y,(f"{n[0]:.1f}" if n else None),bool(n and n[1]),font,7.2,INKN)
_SLOTN={"W/R/T":"FLEX","Q/W/R/T":"S-FLEX"}
def _st(s): return {"IR-R":"IR","PUP-R":"IR","NA":"O"}.get(s,s or "")
def rows17(lab):
    L=MTR["leagues"][lab];S=[];Bn=[];Ir=[]
    for p,o in zip(L["starters"]["me"],L["starters"]["op"]):
        v,f=wk17(p["player"],lab)
        S.append((_SLOTN.get(p["slot"],p["slot"]),p["player"],_st(p["status"]),p["pos"],_gt(p["team"]),None,None,None,v,"—",None,f,False))
    for p in L.get("bench",[]):
        r=(p["slot"],p["player"],_st(p["status"]),p["pos"],_gt(p["team"]),None,None,None)
        if p["slot"]=="IR": Ir.append(r+(None,))
        else:
            v,f=wk17(p["player"],lab); Bn.append(r+((v if _st(p["status"]) not in ("O","IR") else None),f))
    return S,Bn,Ir
def _live(side,lab):
    return [dict(name=p["player"],yahoo=(p["actual"] if p["actual"] is not None else (p["yahoo"] or 0.0)),state=("F" if p["actual"] is not None else "P"),
                 team=_gt(p["team"]),slot=p["slot"],pts=p["actual"] or 0.0) for p in MTR["leagues"][lab]["starters"][side]]
LIVE_ME=[];LIVE_OP=[]
def _pick(rows,key,team=None,slot=None):
    k=norm(key); hit=[d for d in rows if norm(d["name"])==k]
    if not hit:
        ln=norm(key.split(". ",1)[-1].split()[-1]) if key else ""
        hit=[d for d in rows if ln and (norm(d["name"]).endswith(" "+ln) or norm(d["name"])==ln)] if ln else []
        _fi=norm(key)[:1]; hit=[d for d in hit if norm(d["name"])[:1]==_fi]   # Oct 11: same first initial, or no match
        if len(hit)>1 and team: hit=[d for d in hit if d["team"]==team] or hit
    return hit[0] if hit else None
def _val(d): return (d["yahoo"],d["state"]=="F") if d else None
def _NOWME(nm):
    if not nm: return None
    d=_pick(LIVE_ME,nm)
    if d is None:
        dd=[x for x in LIVE_ME if x["slot"]=="DEF" and (norm(x["name"]) in norm(nm) or norm(nm) in norm(x["name"]))]; d=dd[0] if dd else None
    return _val(d)
_DEFT={"LA":"LAR"}
OPMAP={}
def _NOWOP(om):
    if not om or om=="—": return None
    if om in OPMAP: return _val(OPMAP[om])
    if om.endswith(" D"):
        t=om[:-2].strip().upper(); dd=[x for x in LIVE_OP if x["slot"]=="DEF" and (x["team"]==t or _DEFT.get(x["team"])==t)]
        return _val(dd[0]) if dd else None
    return _val(_pick(LIVE_OP,om))

# ---- standings and the card, from the same read
def _sfx(n): return {1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th") if not 10<=n%100<=20 else "th"
def _stand(lab):
    lid=MTR["leagues"][lab]["league_id"]; f=sorted(_g23.glob(f"/home/claude/dksys/data/latest/yahoo/wk{WEEKN}/standings_*.txt"),key=_o23.path.getmtime)[-1]
    for line in open(f):
        if line.startswith(lid+"#"):
            rows=[];div=None
            for it in line.rstrip("\n").split("#",1)[1].split("|"):
                fz=it.split("^")
                if len(fz)==1: div=fz[0]; continue
                nd=lid=="864215"; rows.append(dict(rank=int(fz[0]),team=fz[1],rec=fz[2],pf=float(fz[3] if nd else fz[4]),div=div))
            return rows
    return []
_TEAMS={"DK I":"Most Important","DK II":"Winners Sinners","DK III":"Hers His Ver 2.0","DK IV":"Murrieta NXTDR"}   # Oct 11 (Dom): short one-line names, same as Dark Knight Live
_KK={"DK I":"I","DK II":"II","DK III":"III","DK IV":"IV"}
def _panel(lab,S):
    L=MTR["leagues"][lab]; n=L["needles"]; out=[]
    hurt=[f"{last(r[1])} ({r[2]})" for r in S if r[1] and r[2] in ("Q","D","O","IR")]
    nog=[last(p["player"]) for p in L["starters"]["me"] if p["window"] is None]
    out.append(("Watch",_open_note(lab)+("No game this week: "+", ".join(nog)+". " if nog else "")+("Tagged: "+", ".join(hurt)+"." if hurt else "No starter carries an injury tag.")))
    by={}
    for p in L["starters"]["me"]+L.get("bench",[]):
        t=_gt(p["team"])
        if t in SCH:
            b=bye(t)
            if WEEKN<=b<=WEEKN+3: by.setdefault(b,[]).append(last(p["player"]))
    out.append(("Byes","  ·  ".join(f"Wk {b} "+", ".join(v) for b,v in sorted(by.items()) if b<=WEEKN+2) or "None in the next three weeks."))
    vals=[v for v in (n["gotham"],n["yahoo"],n["sleeper"]) if v is not None]       # Oct 9: a missing read is named, never crashes
    sp=(max(vals)-min(vals)) if len(vals)>1 else 0
    gap=[x.split(": ",1)[1].split(" - ")[0] for x in MTR.get("notes",[]) if x.startswith(lab+":") and "Gotham" in x]
    _f=lambda v: "missing this run" if v is None else f"{v}%"
    out.append(("Reads",f"Gotham {_f(n['gotham'])}, Yahoo {_f(n['yahoo'])}"+(" (posted % missing; from Yahoo's projected totals)" if lab in YMISS else "")+f", Sleeper {_f(n['sleeper'])}"+(" — they split." if sp>=10 else " — they agree.")+(" "+gap[0]+"." if gap and sp>=10 else "")))
    out.append(("Opponent",f"{_tct(L['opp'])} is {L['opp_record']}"+(f", {L['opp_rank']}{_sfx(L['opp_rank'])}." if L.get('opp_rank') else ".")))
    return out
_CMP={}
for _lab,_L in MTR["leagues"].items():
    _bm=sum(p["actual"] or 0 for p in _L["starters"]["me"]);_bo=sum(p["actual"] or 0 for p in _L["starters"]["op"]);_pm,_po=_L["totals"]["yahoo"]
    _CMP[_lab]=dict(me_board=_bm,op_board=_bo,all_pct=round(100*(_bm+_bo)/(_pm+_po)) if _pm+_po else 0)
LEAGUES=(("DK I",12,dict(QB=1,RB=2,WR=2,TE=1,FLEX=2)),("DK II",12,dict(QB=1,RB=2,WR=3,TE=1,FLEX=1,SF=1)),
         ("DK III",14,dict(QB=1,RB=2,WR=2,TE=1,FLEX=2)),("DK IV",10,dict(QB=1,RB=2,WR=3,TE=1,FLEX=1,SF=1)))
from reportlab.pdfgen import canvas as _cv
c=_cv.Canvas(_OUT10,pagesize=letter)
for _f_ in list(globals().values()):
    if callable(_f_) and getattr(_f_,"__globals__",None) is globals(): pass
pg=2        # page 1 is the mountains page, built by global33 and set in front at assembly
exec(open("/home/claude/cand/redesign/_fr_v8.py").read())   # Oct 12 (Dom): the v8 Field Report, the new masthead on every page, DK1-DK4
exec(open("/home/claude/cand/redesign/_scoreboard_page.py").read()); pg+=1   # Oct 12 (Dom): CALIBRATION, up front
# THE CALENDAR (Dom, Thu Oct 8): Monday Post-Mortem provisional, Tuesday final, Wednesday-Thursday Outlook - right behind the front page.
exec(open("/home/claude/cand/redesign/_calendar.py").read())
if False:   # Oct 12 (Dom): the Post-Mortem lives on each Field Report now
    exec(open("/home/claude/cand/redesign/_pm_auto.py").read()); postmortem_page(c,pg); c.showPage(); pg+=1
elif False:   # Oct 12 (Dom): the Outlook lives on each Field Report's card now
    exec(open("/home/claude/cand/redesign/_outlook.py").read()); outlook_page(c,pg); c.showPage(); pg+=1
exec(open("/home/claude/cand/redesign/_scout_page.py").read())   # v24: THE SCOUT page
for L_,T_,S_ in LEAGUES:
    L=MTR["leagues"][L_]; ST_=_stand(L_)
    S,Bn,Ir=rows17(L_)
    Bn,Ir,_OPN=open_rows(L_,Bn,Ir)   # Oct 10: empty slots print as OPEN
    LIVE_ME[:]=_live("me",L_);LIVE_OP[:]=_live("op",L_)
    OPMAP.clear()
    def _short(d):
        if d["slot"]=="DEF": return d["team"]+" D"
        n=d["name"]; return n if (len(n)>2 and n[1]==".") else n.split()[0][0]+". "+" ".join(n.split()[1:])
    _S2=[]
    for i,r in enumerate(S):
        o=LIVE_OP[i]; om_=_short(o); OPMAP[om_]=o; _S2.append(r[:9]+(om_,None)+r[11:])
    S=_S2
    me=[t for t in ST_ if t["team"]==L["me"]][0]; sixth=sorted(ST_,key=lambda t:t["rank"])[5]
    _w=lambda rec:(lambda a:a[0]+.5*a[2])([int(x) for x in rec.split("-")])
    gb=_w(sixth["rec"])-_w(me["rec"]); pfr=sorted([t["pf"] for t in ST_],reverse=True).index(me["pf"])+1
    line=("In — inside the top six" if me["rank"]<=6 else (f"Out — {gb:g} game{'s' if gb!=1 else ''} back of 6th" if gb>0 else "Out — level with 6th on record"))
    nog=[p["player"] for p in L["starters"]["me"] if p["window"] is None]; out_=[r[1] for r in S if r[1] and r[2] in ("O","IR") and not any(p["player"]==r[1] and p.get("actual") is not None for p in L["starters"]["me"])]
    q_=[last(r[1]) for r in S if r[1] and r[2] in ("Q","D") and not any(p["player"]==r[1] and p.get("actual") is not None for p in L["starters"]["me"])]   # Oct 12: played men need no kickoff check
    if nog or out_: st_,verdict=("red","Fix the lineup: "+", ".join(nog+out_)+(" has" if len(nog+out_)==1 else " have")+" no game or is out.")
    elif q_: st_,verdict=("gold",", ".join(q_)+(" is" if len(q_)==1 else " are")+" questionable — check before kickoff.")
    else: st_,verdict=("green","Lineup set — nothing to do before kickoff.")
    played=L["played"]; when=(f"First kickoff {MTR['windows'][0].title().replace(' Am',' AM').replace(' Pm',' PM')} PT" if played["me"]+played["op"]==0
          else f"{played['me']} of {played['of'][0]} starters played")
    n=L["needles"]
    cardd=dict(k=_KK[L_],team=_TEAMS[L_],win=n["yahoo"],last=n["gotham"],eff=n["sleeper"],comp=_CMP[L_],me=L["totals"]["yahoo"][0],opp=L["totals"]["yahoo"][1],
               oppn=_tct(L["opp"]),oppr=f"{L['opp_record']}"+(f" · {L['opp_rank']}{_sfx(L['opp_rank'])}" if L.get("opp_rank") else ""),
               rec=me["rec"][:-2].replace("-","–") if me["rec"].endswith("-0") else me["rec"].replace("-","–"),place=me["rank"],of=len(ST_),
               pts=f"{me['pf']:.0f} points  ·  {pfr}{_sfx(pfr)} in scoring",line=line,
               shead=f"After Week {WEEKN-1}  ·  Top six make playoffs"+("  ·  Median game too" if L_=="DK IV" else ""),st=st_,verdict=verdict,when=when)
    fn="a gold number marked FINAL is a game already played. NOW = Yahoo's projection for the lineup as set. Sleeper and Gotham are pre-game reads of the same men."
    nIR=len(Ir)
    D=dict(k=_KK[L_],name=L_,page=pg,starts=S,bench=Bn,irs=Ir,cardd=cardd,panel=_panel(L_,S),fnote=fn,
           irsub=_irsub(L_,Ir),
           sub=f"{_TEAMS[L_]}  ·  vs {_tct(L['opp'])}")
    print("=====",L_,"card",{k:v for k,v in cardd.items() if k in ("rec","place","line","pts","oppr","st","verdict")})
    SCOUTMK.clear(); SCOUTMK.update(scout_rows(L_))
    pg+=field_report8(c,pg,L_)   # Oct 12: v8 - one page, two when the roster runs long
    c.bookmarkPage("dk_scout_"+L_.replace(" ",""))   # Oct 14: where the Radar and Scout marks land
    pg+=scout_page(c,pg,L_,_KK[L_])          # v24: THE SCOUT rides right behind the Field Report (where the Radar lives)
    SCOUTMK.clear(); SCOUTMK.update(scout_rows(L_))
    c.bookmarkPage("dk_pos_"+L_.replace(" ",""))   # Oct 14: where the drift and trend marks land
    r_=position_page10(L_,T_,S_,"Positions · "+L_);pg+=1
exec(open("/home/claude/cand/redesign/_fr_legend4.py").read().replace("Weeks 4-7",f"Weeks {WEEKN}-{WEEKN+3}").replace("The workload engine changed his number  ·  his role moved over his last two games  ·  look in the workload engine","Gotham changed his number  ·  his role moved over his last two games  ·  look in Gotham"))   # THE MARKS travels as the last page
c.save()

# OCT10 field report

# OCT10c field open

# OCT10d field final

# OCT10f slot words

# OCT11 short names pages

# OCT11 alarm played pages

# OCT11 lastname initial

# OCT11 disagreement flag

# OCT11 gotham pregame

# OCT11 live glow

# OCT11 scoreboard page

# OCT12 field q played

# OCT12 field v8

# OCT12 outlook page retires

# OCT14 mark link targets
