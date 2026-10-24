# THE SCOUT ENGINE v2 (Dom, Fri Oct 9 2026) — rebuilt from board.py v1 (kept as board_v1_backup.py).
# Gate 1: my team's holes, week by week, each slot measured against the opponent's man at the same slot that week
#         (his whole roster rolled forward to that week, not today's lineup).
# Gate 2: available players found by workload (or a door opening / a return), converted to points,
#         then the only question: can he incrementally improve my team — where, and when (week fill / season / playoffs).
# Gate 3: hunches — carried from hunches_DKI.csv, aged like everything else.
# Rules: no Yahoo projections; no drop suggestions; nothing assumed — every outside player the math leans on is checked
#        against the live Yahoo rosters; every bar says why it is what it is; run stamp + per-item age + kill condition.
# v2 valuation: proven players are judged mostly on real points (70/30 with workload) with last season as a prior;
#        unproven players lean on workload (40/60). One bad game can't sink a player (his worst game is lifted to his
#        next-worst). Recent games still count more.
import pandas as pd, numpy as np, re, json, os, math, collections, datetime as dt, sys
H="/home/claude/dksys/scout"; D="/home/claude/dksys/gate/fresh"; L="/home/claude/dksys/data/latest"
try:   # Oct 12 (Dom): the week comes from the schedule, never typed in
    _gm=pd.read_csv(L+'/games.csv',low_memory=False); _gm=_gm[(_gm.season==2026)&(_gm.game_type=='REG')]; NOW=int(_gm[_gm.result.isna()].week.min())
except Exception: NOW=5
LAST=17; PLAYOFF={15,16,17}
LGK=[a for a in sys.argv[1:] if a.startswith("DK")]; LGK=LGK[0] if LGK else "DKI"
CFGS={
 "DKI":dict(lab="DK I",n=1,me=2,slots=["QB","WR","WR","RB","RB","TE","FLEX","FLEX","K","DEF"],intp=-2,ratt=.25,kick="flat",dfn="dk",median=False,
   teams={1:"JD",2:"Dark Knight I",3:"DIKFORE",4:"Rolling With Romo",5:"World Of Pain",6:"Punching Bag",7:"Raider nation",8:"Coin Toss Mike",9:"Mr. Rodgers' Neighborhood",10:"RoadDogg",11:"Kraft Beer TDs",12:"Remember the Tutens"},
   opp={5:7,6:5,7:10,8:6,9:9,10:4,11:12,12:8,13:1,14:11},urg={5:1.0,6:1.0,7:.9,8:.9,9:.75,10:.75,11:.75,12:.75,13:.75,14:.75,15:.4,16:.4,17:.4},
   record="1-3, 9th of 12",rost_at="Yahoo 9:50 AM PT",protect=["Travis Kelce","Kaelon Black"],pending=""),
 "DKII":dict(lab="DK II",n=2,me=7,slots=["QB","WR","WR","WR","RB","RB","TE","FLEX","SUPERFLEX","K","DEF"],intp=-2,ratt=.25,kick="dist",dfn="std",median=False,
   teams={1:"Daejon Love Special",2:"Diddys Booty Butter",3:"RFFR",4:"FUCKING COWBOYS",5:"How 'Bout Them Points",6:"Trophy Hunter",7:"Dark Knight II",8:"RAIDER FAN",9:"Rams house",10:"Rated PG-18",11:"Hector Football",12:"Ground Game evan"},
   opp={5:4,6:3,7:12,8:6,9:11,10:2,11:9,12:1,13:5,14:10},urg={5:1.0,6:.95,7:.9,8:.9,9:.8,10:.8,11:.8,12:.8,13:.8,14:.8,15:.55,16:.55,17:.55},
   record="2-2, 8th of 12",rost_at="Yahoo 11:45 AM PT",protect=["Travis Kelce"],pending=""),
 "DKIII":dict(lab="DK III",n=3,me=2,slots=["QB","WR","WR","RB","RB","TE","FLEX","FLEX","DEF"],intp=-2,ratt=.25,kick=None,dfn="dk",median=False,
   teams={1:"Benchdad's Beach",2:"Dark Knight III",3:"Maly's Better Half",4:"Bad and Bougie 2.0",5:"Dawg Pound Eric",6:"The Deer Hunter Part Deux",7:"Press Coverage steph",8:"Rushin Roulette",9:"Dominique by 6",10:"Derek's Better Half",11:"Beachmom's Bench",12:"And A Goedert To You Sir",13:"Mr. Bobo",14:"Mrs. Bobo"},
   opp={5:12,6:3,7:6,8:1,9:3,10:13,11:8,12:6,13:12,14:5},urg={5:1.0,6:1.0,7:.9,8:.9,9:.75,10:.75,11:.75,12:.75,13:.75,14:.75,15:.4,16:.4,17:.4},
   record="1-3, 11th of 14",rost_at="Yahoo 11:45 AM PT",protect=[],pending=""),
 "DKIV":dict(lab="DK IV",n=4,me=6,slots=["QB","WR","WR","WR","RB","RB","TE","FLEX","SUPERFLEX","K","DEF"],intp=-1,ratt=0,kick="dist",dfn="std",median=True,
   teams={1:"Brad's Ballers",2:"Alan's Team",3:"Fly Eagles Fly",4:"Lin's Team",5:"Team Other",6:"Dark Knight IV",8:"Mr. Irrelevant",9:"Bad and Boujee",10:"Dream Killers",11:"Killer Ko-Gees"},
   opp={5:8,6:3,7:1,8:11,9:2,10:4,11:10,12:9,13:5,14:8},urg={5:.9,6:.9,7:.85,8:.85,9:.8,10:.8,11:.8,12:.8,13:.8,14:.8,15:.8,16:.8,17:.8},
   record="5-3, 5th of 10 (median game too)",rost_at="Yahoo 11:45 AM PT",protect=["Travis Kelce"],pending=""),
}
CF=CFGS[LGK]; ME=CF["me"]; TEAMNAMES=CF["teams"]; OPP=CF["opp"]; URG=CF["urg"]
SD=25.0
SLOTS=CF["slots"]; FLEXMAP={"FLEX":("RB","WR","TE"),"SUPERFLEX":("QB","RB","WR","TE")}; FLEXOK=("RB","WR","TE")
def okfor(s): return FLEXMAP.get(s,(s,))
TEAMFIX={"LAR":"LA"}
def tm(t): t=t.upper(); return TEAMFIX.get(t,t)
def norm(n):
    n=re.sub(r"[.'’\-]"," ",str(n).lower()); n=re.sub(r"\b(jr|sr|ii|iii|iv|v)\b","",n); return re.sub(r"\b([a-z])\s+(?=[a-z]\b)",r"\1"," ".join(n.split()))   # Oct 14: "d k metcalf" -> "dk metcalf"
NOWPT=dt.datetime.now(dt.timezone(dt.timedelta(hours=-7)))
QUIET="--quiet" in sys.argv

# ================= inputs =================
R=[l.rstrip("\n").split("|") for l in open(f"{H}/dk{CF['n']}_rosters_live.txt") if l.strip() and not l.startswith("#")]
# Oct 9: the roster read's own time goes on the page (the API reader writes it in the file's first line)
_rh=[l for l in open(f"{H}/dk{CF['n']}_rosters_live.txt") if l.startswith("#")]
_rm=re.search(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (\w{3}) (\d{1,2})\D*?(?:\d{4} )?~?(\d{1,2}:\d{2} [AP]M) PT",_rh[0]) if _rh else None
if _rm: CF["rost_at"]=f"Yahoo {_rm.group(1)} {_rm.group(2)} {_rm.group(3)}, {_rm.group(4)} PT"+(" (API)" if "API" in _rh[0] else "")
ROS=pd.DataFrame(R,columns=["tid","slot","name","team","pos","tag"]); ROS["tid"]=ROS.tid.astype(int); ROS["team"]=ROS.team.map(tm)
WAIV={}
for l in open(f"{H}/dk{CF['n']}_waivers.txt"):
    if l.startswith("#"): continue
    for it in l.strip().split("|"):
        if "/" in it: n,c=it.rsplit("/",1); WAIV[norm(n)]=c
for _nn,_aa in {"cardinals":"ARI","falcons":"ATL","ravens":"BAL","bills":"BUF","panthers":"CAR","bears":"CHI","bengals":"CIN","browns":"CLE","cowboys":"DAL","broncos":"DEN","lions":"DET","packers":"GB","texans":"HOU","colts":"IND","jaguars":"JAX","chiefs":"KC","raiders":"LV","chargers":"LAC","rams":"LA","dolphins":"MIA","vikings":"MIN","patriots":"NE","saints":"NO","giants":"NYG","jets":"NYJ","eagles":"PHI","steelers":"PIT","49ers":"SF","seahawks":"SEA","buccaneers":"TB","titans":"TEN","commanders":"WAS"}.items():   # Oct 17 (Dom): a defense on waivers is found by its nickname
    if _nn in WAIV: WAIV["def "+_aa.lower()]=WAIV[_nn]
pbp=pd.read_csv(f"{D}/play_by_play_2026.csv.gz",low_memory=False); pbp=pbp[pbp.season_type=="REG"]
st=pd.read_csv(f"{D}/stats_player_week_2026.csv",low_memory=False); st=st[st.season_type=="REG"].copy()
s25=pd.read_csv(f"{L}/stats_week_2025.csv",low_memory=False); s25=s25[s25.season_type=="REG"].copy()
inj=pd.read_csv(f"{D}/injuries_2026.csv"); ro=pd.read_csv(f"{D}/roster_2026.csv",low_memory=False)
sn=pd.read_csv(f"{D}/snap_counts_2026.csv"); sn=sn[sn.game_type=="REG"].copy(); sn["_nk"]=sn.player.map(norm)
games=pd.read_csv(f"{L}/games.csv"); games=games[(games.season==2026)&(games.game_type=="REG")]
def most(df):
    g=lambda c: df[c].fillna(0) if c in df else 0
    return (g("receptions")+g("receiving_yards")/10+6*g("receiving_tds")+g("passing_yards")/25+6*g("passing_tds")+CF["intp"]*g("passing_interceptions")
            +g("rushing_yards")/10+6*g("rushing_tds")+CF["ratt"]*g("carries")-2*(g("rushing_fumbles_lost")+g("receiving_fumbles_lost")+g("sack_fumbles_lost"))
            +2*(g("passing_2pt_conversions")+g("rushing_2pt_conversions")+g("receiving_2pt_conversions")))
st["fp"]=most(st); s25["fp"]=most(s25)
P25=s25.groupby("player_display_name").agg(g=("week","nunique"),fp=("fp","sum")); P25["ppg"]=P25.fp/P25.g
P25=P25[P25.g>=6].ppg.to_dict(); P25={norm(k):v for k,v in P25.items()}

# work (expected points from targets / carries / throws)
b=lambda y: pd.cut(y,[0,2,5,10,20,40,100],labels=False,include_lowest=True)
pas=pbp[(pbp.play_type=="pass")&(pbp.two_point_attempt!=1)].copy(); pas["yb"]=b(pas.yardline_100); cpf=pas.cp.fillna(pas.complete_pass.mean())
tg=pas[pas.receiver_player_id.notna()].copy(); tdr=tg.groupby("yb").pass_touchdown.mean()
tg["xfp"]=cpf.reindex(tg.index)*(1+(tg.air_yards.fillna(0)+tg.xyac_mean_yardage.fillna(0))/10)+6*tg.yb.map(tdr).astype(float)
ru=pbp[(pbp.play_type=="run")&(pbp.two_point_attempt!=1)&pbp.rusher_player_id.notna()].copy(); ru["yb"]=b(ru.yardline_100)
rz=ru.groupby("yb").agg(y=("yards_gained","mean"),td=("rush_touchdown","mean")); ru["xfp"]=CF["ratt"]+ru.yb.map(rz.y).astype(float)/10+6*ru.yb.map(rz.td).astype(float)
pa=pas[pas.passer_player_id.notna()].copy(); ptd=pa.groupby("yb").pass_touchdown.mean(); pint=pa.interception.mean()
pa["xfp"]=cpf.reindex(pa.index)*(pa.air_yards.fillna(0)+pa.xyac_mean_yardage.fillna(0))/25+6*pa.yb.map(ptd).astype(float)+CF["intp"]*pint
X=pd.concat([tg[["receiver_player_id","week","xfp"]].rename(columns={"receiver_player_id":"id"}),ru[["rusher_player_id","week","xfp"]].rename(columns={"rusher_player_id":"id"}),
             pa[["passer_player_id","week","xfp"]].rename(columns={"passer_player_id":"id"})]).groupby(["id","week"]).xfp.sum()
# kickers & defenses in league scoring
kk=pbp[(pbp.field_goal_attempt==1)|(pbp.extra_point_attempt==1)].copy()
kk["kp"]=np.where(kk.field_goal_result=="made",(np.where(kk.kick_distance>=50,4,3) if CF["kick"]=="flat" else np.where(kk.kick_distance>=50,5,np.where(kk.kick_distance>=40,4,3))),0)+np.where(kk.extra_point_result=="good",1,0)-np.where(kk.extra_point_attempt.eq(1)&kk.extra_point_result.ne("good"),1,0)
KP=kk.groupby(["kicker_player_id","posteam","defteam","week"]).kp.sum().reset_index()
kname=st[st.position=="K"].drop_duplicates("player_id").set_index("player_id").player_display_name.to_dict()
fin=pbp.groupby(["game_id","week","home_team","away_team"]).agg(hs=("total_home_score","max"),as_=("total_away_score","max")).reset_index()
dd=pbp.copy(); dd["ret_td"]=((dd.touchdown==1)&(dd.td_team==dd.defteam)).astype(int); dd["fds"]=((dd.down==4)&(dd.fourth_down_failed==1)).astype(int)
dd["blk"]=dd.field_goal_result.eq("blocked").astype(int)+dd.punt_blocked.fillna(0)
DG=dd.groupby(["defteam","posteam","week"]).agg(sk=("sack","sum"),it=("interception","sum"),fr=("fumble_lost","sum"),td=("ret_td","sum"),sf=("safety","sum"),blk=("blk","sum"),fds=("fds","sum")).reset_index()
def pa_pts(p):
    if CF["dfn"]=="dk": return 17 if p==0 else 13 if p<=6 else 10 if p<=13 else 4 if p<=20 else 1 if p<=27 else -3 if p<=34 else -6
    return 10 if p==0 else 7 if p<=6 else 4 if p<=13 else 1 if p<=20 else 0 if p<=27 else -1 if p<=34 else -4
pts={}
for r in fin.itertuples(): pts[(r.home_team,r.week)]=r.as_; pts[(r.away_team,r.week)]=r.hs
DG["dp"]=DG.sk+2*(DG.it+DG.fr+DG.sf+DG.blk)+6*DG.td+(DG.fds if CF["dfn"]=="dk" else 0)+[pa_pts(pts.get((t,w),20)) for t,w in zip(DG.defteam,DG.week)]

# schedule & matchup difficulty (real points each defense allows to each position)
sched={};byes={}
for t in pd.unique(games[["home_team","away_team"]].values.ravel()):
    g=games[(games.home_team==t)|(games.away_team==t)]; sched[t]={int(r.week):r.away_team if r.home_team==t else r.home_team for r in g.itertuples()}
    byes[t]=[x for x in range(1,19) if x not in sched[t]]
allow={}
a=st[st.position.isin(["QB","RB","WR","TE"])].groupby(["opponent_team","position","week"]).fp.sum().reset_index().groupby(["opponent_team","position"]).fp.mean()
for (t,p),v in a.items(): allow[(t,p)]=v
for t,v in KP.groupby(["defteam","week"]).kp.sum().groupby("defteam").mean().items(): allow[(t,"K")]=v
for t,v in DG.groupby(["posteam","week"]).dp.sum().groupby("posteam").mean().items(): allow[(t,"DEF")]=v
RATIO={};TAG={}
for pos in ["QB","RB","WR","TE","K","DEF"]:
    s=pd.Series({k[0]:v for k,v in allow.items() if k[1]==pos}); q1,q2=s.quantile(1/3),s.quantile(2/3)
    for t,v in s.items(): RATIO[(t,pos)]=1+.5*(v/s.mean()-1); TAG[(t,pos)]="easy" if v>=q2 else "hard" if v<=q1 else "avg"

# ================= valuation v2 =================
def steady(v):
    """recent-weighted average where the single worst game is lifted to the next-worst (one bad night can't sink a player)"""
    v=[x for x in v if pd.notna(x)]
    if not v: return 0.0
    if len(v)>=4: lo=sorted(v)[1]; i=v.index(min(v)); v=v[:i]+[lo]+v[i+1:]
    if len(v)>=4: hi=sorted(v)[-2]; i=v.index(max(v)); v=v[:i]+[hi]+v[i+1:]   # Oct 14 (Dom): one big game is cut to his next-best
    return (.5*np.mean(v[-2:])+.5*np.mean(v)) if len(v)>=3 else float(np.mean(v))
inj5=inj[inj.week==inj.week.max()]; rep=inj5.set_index("gsis_id").report_status.dropna().to_dict()
prac=inj5.set_index("gsis_id").practice_status.dropna().to_dict()
injname=inj.dropna(subset=["report_primary_injury"]).drop_duplicates("gsis_id",keep="last").set_index("gsis_id").report_primary_injury.to_dict()
rs=ro[ro.week==ro.week.max()].set_index("gsis_id").status.to_dict()
SEASON_OUT={"de von achane"}
PL={}
for pid,g in st[st.position.isin(["QB","RB","WR","TE"])].groupby("player_id"):
    g=g.sort_values("week"); name=g.player_display_name.iloc[-1]; team=g.team.iloc[-1]; pos=g.position.iloc[-1]
    _sp=sn[(sn._nk==norm(name))&(sn.team==team)].set_index("week").offense_pct   # Oct 10 late: drop a game he left hurt
    if len(_sp)>=2 and _sp.median()>=.6:
        _ex=[w for w in g.week if _sp.get(w,1)<.35]
        if _ex and len(g)>len(_ex): g=g[~g.week.isin(_ex)]
    fp=list(g.fp); xv=[X.get((pid,w),0) for w in g.week]
    prior=P25.get(norm(name)); proven=prior is not None and prior>=8
    wr=.7 if proven else .4
    v26=wr*steady(fp)+(1-wr)*steady(xv)
    val=(len(fp)*v26+3*prior)/(len(fp)+3) if proven else v26          # last season counts like three games
    PL[(norm(name),team)]=dict(name=name,team=team,pos=pos,pid=pid,fwd=val,v26=v26,prior=prior,proven=proven,fp=fp,xv=xv,
        wks=list(g.week),last=int(g.week.max()),nflstat=rs.get(pid,""),rep=rep.get(pid,""),prac=prac.get(pid,""),inj=injname.get(pid,""))
for (pid,team),g in KP.groupby(["kicker_player_id","posteam"]):
    g=g.groupby("week").kp.sum(); n=kname.get(pid,pid)
    PL[(norm(n),team)]=dict(name=n,team=team,pos="K",fwd=steady(list(g.values)),fp=list(g.values),xv=[],wks=list(g.index),last=int(g.index.max()),nflstat="",rep="",prac="",inj="",proven=True,prior=None)
for t,g in DG.groupby("defteam"):
    g=g.groupby("week").dp.sum(); PL[("def "+t.lower(),t)]=dict(name=t+" defense",team=t,pos="DEF",fwd=steady(list(g.values)),fp=list(g.values),xv=[],wks=list(g.index),last=int(g.index.max()),nflstat="",rep="",prac="",inj="",proven=True,prior=None)

# ---- Oct 17 (Dom): THE TRADE CHECK - Sleeper's current team vs the team each man played for ----
MOVED={}
try:
    _FDT=globals().get("_FD","/home/claude/domfantasy01/dk-feeds/feeds/")
    _spl=json.load(open(_FDT+"sleeper_players_min.json")).get("players",{})
    _cur=collections.defaultdict(list)
    for _x in (_spl.values() if isinstance(_spl,dict) else _spl):
        if _x.get("pos") in ("QB","RB","WR","TE") and _x.get("name"):
            _cur[(norm(_x["name"]),_x["pos"])].append(tm(_x["team"]) if _x.get("team") else None)
    for _k,_p in list(PL.items()):
        if _p["pos"] not in ("QB","RB","WR","TE"): continue
        _c=_cur.get((norm(_p["name"]),_p["pos"]))
        if not _c or len(set(_c))!=1: continue                     # unknown or ambiguous name - leave him alone
        _t2=_c[0]
        if _t2 is None:
            SEASON_OUT.add(norm(_p["name"])); _p["gone"]="on no NFL roster now (Sleeper)"; continue
        if _t2!=_p["team"]:
            _t1=_p["team"]; _p["team"]=_t2; _p["oldteam"]=_t1
            _p["moved"]=f"moved {_t1} to {_t2} - his numbers so far are from {_t1}"
            del PL[_k]; PL[(_k[0],_t2)]=_p; MOVED[(_k[0],_t2)]=(_t1,_t2)
    for _k,(_t1,_t2) in MOVED.items():
        _m=PL[_k]
        _inc=sorted([q for kk,q in PL.items() if kk!=_k and q.get("team")==_t2 and q["pos"]==_m["pos"] and not q.get("oldteam")],
                    key=lambda q:-q["fwd"])[:(3 if _m["pos"]=="WR" else 2)]
        _tot=_m["fwd"]+sum(q["fwd"] for q in _inc)
        if not _inc or _tot<=0: continue
        _sh=_m["fwd"]/_tot
        for q in _inc:
            _was=q["fwd"]; q["fwd"]=_was*(1-_sh); q["v26"]=q.get("v26",_was)*(1-_sh)
            q.setdefault("tradecut",[]).append(f"{_m['name']} joined {_t2} from {_t1}: his pre-trade ~{_was:.1f} a game cut to ~{q['fwd']:.1f} ({_sh*100:.0f}% of the {_m['pos']} production goes to the newcomer)")
    if not QUIET: print(f"Scout trade check: {len(MOVED)} men changed teams (Sleeper)" + (": " + ", ".join(f"{PL[k]['name']} {a}->{b}" for k,(a,b) in MOVED.items()) if MOVED else ""))
except Exception as _e: print("Scout trade check skipped:",_e)

# ---- Oct 17 (Dom): THE NEWS CHECK - the last 14 days of news on every man the Scout recommends ----
_NEWSIT=[]
try:
    _FDN=globals().get("_FD","/home/claude/domfantasy01/dk-feeds/feeds/")
    _now_u=dt.datetime.now(dt.timezone.utc); _seen=set()
    for _fn,_src in (("rotowire_history.jsonl","RotoWire"),("espn_news_history.jsonl","ESPN"),("news_extra_history.jsonl","PFT/RotoBaller")):
        try:
            for _l in open(_FDN+_fn):
                try: _j=json.loads(_l)
                except Exception: continue
                _t=str(_j.get("title") or ""); _pu=str(_j.get("published_utc") or "")
                if not _t or _t in _seen: continue
                try: _when=dt.datetime.fromisoformat(_pu.replace("Z","+00:00"))
                except Exception: continue
                if (_now_u-_when).days>14: continue
                _seen.add(_t)
                _src2=_src if _src!="PFT/RotoBaller" else ("PFT" if _j.get("source")=="pft" else "RotoBaller" if _j.get("source")=="rotoballer" else _src)
                _NEWSIT.append((_when," "+norm(_t+" "+str(_j.get("text") or ""))+" ",_t,_src2," "+norm(_t)+" "))
        except Exception: pass
    _NEWSIT.sort(key=lambda x:x[0])
    if not QUIET: print(f"Scout news check: {len(_NEWSIT)} items from the last 14 days")
except Exception as _e: print("Scout news check skipped:",_e)
_BADNEWS=re.compile(r"\b(injured reserve|placed on ir|to ir|on ir|surgery|procedure|out indefinitely|ruled out|will miss|miss(es)? (multiple|several|the next)|setback|released|waived|traded|trade (for|to|with)|acquire\w*|demoted|benched|suspend\w*|carted|fracture|torn|tear)\b")
def newscheck(p):
    """newest item mentioning him, and whether recent news (7 days) is bad; DEF and K are skipped"""
    if p["pos"] in ("DEF",) or not _NEWSIT: return None,False
    nk=" "+norm(p["name"])+" "
    hits=[x for x in _NEWSIT if nk in x[1]]
    if not hits: return "news: nothing on him in 14 days (RotoWire, ESPN, PFT, RotoBaller)",False
    # a flag needs the item to be ABOUT him: his name (or his last name, with his full name in the story) in the headline -
    # a list story that mentions forty players ("hot seat", "trade deadline") is not news about him
    ln=" "+norm(p["name"]).split()[-1]+" "
    about=[x for x in hits if nk in x[4] or ln in x[4]]
    bad=[x for x in about if (dt.datetime.now(dt.timezone.utc)-x[0]).days<=7 and (_BADNEWS.search(x[1]) or re.search(r"\bout\b",x[4]))]
    hits=about or hits
    x=bad[-1] if bad else hits[-1]
    d_=x[0].astimezone(dt.timezone(dt.timedelta(hours=-7)))
    line=f"{'NEWS FLAG - check before acting: ' if bad else 'news '}({x[3]}, {d_:%b} {d_.day}): {x[2]}"
    return line,bool(bad)
def find(name,team,pos):
    if pos=="DEF": return ("def "+team.lower(),team)
    k=norm(name)
    if (k,team) in PL: return (k,team)
    c=[key for key in PL if key[0]==k]
    if not c:   # Oct 20 (Dom): "J. Croskey-Merritt" -> the one J... Croskey-Merritt (same team first)
        _m=re.match(r"^([a-z]) (.+)$",k)
        if _m:
            c=[key for key in PL if key[1]==team and key[0].startswith(_m.group(1)) and key[0].endswith(" "+_m.group(2))] or \
              [key for key in PL if key[0].startswith(_m.group(1)) and key[0].endswith(" "+_m.group(2))]
    return c[0] if c else None

# ================= Yahoo ownership (for verification) =================
OWN={}
for r in ROS.itertuples():
    k=find(r.name,r.team,r.pos)
    OWN[(norm(r.name),r.team)]=(r.tid,r.slot,r.tag)
    if k: OWN[k]=(r.tid,r.slot,r.tag)
def owner(k): return OWN.get(k)

_NEWSRE=re.compile(r"week-to-week|week to week|(?:could|may|will|expected to) miss (?:some |significant |extended )?time|miss some time|multiple weeks|several weeks|(?:miss|sidelined|out)(?: for)?(?: about| roughly| at least| the next)? (?:\w+|\d+)(?:-to-| to |-)?(?:\w+|\d+)? weeks",re.I)
_NUMW={"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"a":1,"couple":2}
def _nweeks(t):
    m=re.search(r"(?:miss|sidelined|out)(?: for)?(?: about| roughly| at least| the next)? (\w+|\d+)(?:-to-| to |-)?(?:\w+|\d+)? weeks",t,re.I)
    if m and "multiple" not in m.group(1).lower() and "several" not in m.group(1).lower():
        w=m.group(1).lower(); return int(w) if w.isdigit() else _NUMW.get(w,2)
    return 2
NEWSOUT={}
try:   # Oct 12 (Dom): news that he will miss time keeps him out - only news written after his last game counts
    _FD='/home/claude/domfantasy01/dk-feeds/feeds/'; _IT=[]
    try:
        for _x in json.load(open(_FD+'espn_injuries.json')).get('players',[]): _IT.append((_x.get('name',''),_x.get('detail',''),_x.get('date',''),'ESPN'))
    except Exception: pass
    for _fn,_src in (('rotowire_history.jsonl','RotoWire'),('news_extra_history.jsonl','news')):
        try:
            for _l in open(_FD+_fn):
                try: _j=json.loads(_l)
                except Exception: continue
                _t=str(_j.get('title') or ''); _ts=_j.get('published_utc') or _j.get('first_seen_utc') or ''
                if _t.count(',')>=2: continue                                 # a list article names many men - not news about one
                _IT.append((_t.split(':')[0] if _src=='RotoWire' else _t,_t+' '+re.sub(r'<[^>]+>',' ',str(_j.get('text') or '')),_ts,_j.get('source',_src)))
        except Exception: pass
    _GD={}
    for _r in _gm.itertuples(): _GD[(tm(_r.home_team),int(_r.week))]=str(_r.gameday); _GD[(tm(_r.away_team),int(_r.week))]=str(_r.gameday)
    _NAMES={norm(p['name']):p for p in PL.values() if p.get('pos') in ('QB','RB','WR','TE')}
    # Oct 21 (Dom): a newer official tag beats an older "week-to-week". Montgomery: RotoWire "week-to-week" Oct 12, then ESPN
    # Questionable Oct 21 - the old note had him out through Week 8 and the alerts told Dom to bench him. When ESPN's injury
    # entry is newer than the news and does not say Out / IR, that news no longer decides how long he is out.
    _ESPD={}
    try:
        for _x in json.load(open(_FD+'espn_injuries.json')).get('players',[]): _ESPD[norm(_x.get('name',''))]=(str(_x.get('status','')).lower(),str(_x.get('date',''))[:10])
    except Exception: pass
    for _nm,_tx,_ts,_src in _IT:
        if not _ts or not _NEWSRE.search(_tx): continue
        _when=dt.datetime.fromisoformat(str(_ts).replace('Z','+00:00')) if 'T' in str(_ts) else None
        if _when is None or _when.tzinfo is None or (NOWPT-_when).days>10: continue
        for _k,_p in _NAMES.items():
            if not _p['name'] or _p['name'] not in _nm: continue
            _es=_ESPD.get(_k)
            if _es and _es[1]>_when.strftime('%Y-%m-%d') and not any(w in _es[0] for w in ('out','reserve','pup','suspen','doubtful')): continue
            _gday=_GD.get((_p['team'],int(_p['last'])),'')
            if _gday and _when.strftime('%Y-%m-%d')<_gday: continue           # written before his last game - he has played since
            _n=_nweeks(_tx); _ph=_NEWSRE.search(_tx).group(0)
            if _k not in NEWSOUT or _n>NEWSOUT[_k][0]: NEWSOUT[_k]=(_n,f'{_src}: "{_ph}" ({_when.astimezone(NOWPT.tzinfo).strftime("%b %d")})')
except Exception as _e: print('Scout news check skipped:',_e)
EXTINJ={}
try:   # Oct 14 (Dom): ESPN + Sleeper injury lists, so a hurt free agent is never ranked as available
    _FDX=globals().get("_FD","/home/claude/domfantasy01/dk-feeds/feeds/"); _SEV={"O":1,"IR":2,"NA":3}
    def _xadd(nm,pos,t):
        if t and nm: k=(norm(nm),str(pos).upper()); EXTINJ[k]=t if _SEV[t]>_SEV.get(EXTINJ.get(k),0) else EXTINJ[k]
    for _x in json.load(open(_FDX+"espn_injuries.json")).get("players",[]):
        _s=str(_x.get("status","")).lower()
        _xadd(_x.get("name"),_x.get("pos"),"NA" if "ret" in _s else "IR" if ("reserve" in _s or "pup" in _s or "physically" in _s) else "O" if _s in ("out","doubtful","suspension","suspended") else "")
    _sl=json.load(open(_FDX+"sleeper_injuries.json")).get("players",{}); _sl=_sl.values() if isinstance(_sl,dict) else _sl
    for _x in _sl:
        _s=str(_x.get("inj") or "").upper()
        _xadd(_x.get("name"),_x.get("pos"),"IR" if _s in ("IR","PUP","COV") else "O" if _s in ("OUT","SUS","DOUBTFUL") else "")
    if not QUIET: print(f"Scout injury lists: {len(EXTINJ)} men out or on IR (ESPN + Sleeper)")
except Exception as _e: print("Scout injury lists skipped:",_e)
SEASONOUT_WHY={}
try:   # Oct 21 (Dom): SEASON-ENDING NEWS - ESPN's injury report + the news feeds; a man found here is out for the year
    _SOR=re.compile(r"(season[- ]ending|out for the (?:20\d\d )?(?:season|year)|done for the (?:season|year)|lost for the (?:season|year)|(?:end|ends|ending|ended) (?:his|their) (?:20\d\d )?season|(?:miss|missing|out for|sidelined for|over for)\b[^.]{0,30}?\b(?:rest|remainder) of the (?:20\d\d )?season)",re.I)
    _FDS=globals().get("_FD","/home/claude/domfantasy01/dk-feeds/feeds/"); _SOI=[]
    try:
        for _x in json.load(open(_FDS+"espn_injuries.json")).get("players",[]):
            _SOI.append((_x.get("name",""),str(_x.get("detail","")),str(_x.get("date","")),"ESPN injury report",True))
    except Exception: pass
    for _fn,_sr in (("rotowire_history.jsonl","RotoWire"),("espn_news_history.jsonl","ESPN"),("news_extra_history.jsonl","news")):
        try:
            for _l in open(_FDS+_fn):
                try: _j=json.loads(_l)
                except Exception: continue
                _t=str(_j.get("title") or "")
                if not _t or _t.count(",")>=2: continue                       # a list article names many men
                _SOI.append((_t,_t+" "+re.sub(r"<[^>]+>"," ",str(_j.get("text") or "")),str(_j.get("published_utc") or ""),_sr,False))
        except Exception: pass
    _GDS={}
    for _r in games.itertuples(): _GDS[(tm(_r.home_team),int(_r.week))]=str(_r.gameday); _GDS[(tm(_r.away_team),int(_r.week))]=str(_r.gameday)
    _nu=dt.datetime.now(dt.timezone.utc)
    for _k,_p in PL.items():
        if _p.get("pos") not in ("QB","RB","WR","TE"): continue
        _nk=norm(_p["name"])
        for _nm,_tx,_ts,_sr,_ex in _SOI:
            if (norm(_nm)!=_nk) if _ex else (_p["name"] not in _nm or "?" in _nm): continue   # a question headline ("Is he out for the season?") is not news
            _ln=_p["name"].split()[-1]
            _parts=[_tx] if _ex else [_nm]+[x for x in re.split(r"(?<=[.!?])\s+",_tx[len(_nm):]) if _ln in x]   # the headline, or a sentence that names him
            _m=None
            for _x in _parts:
                for _mm in _SOR.finditer(_x):
                    if not re.search(r"(\bnot\b|n't\b|\bavoid\w*|\bno\b|\bnon\b)[^.]{0,20}$",_x[max(0,_mm.start()-25):_mm.start()],re.I): _m=_mm; break
                if _m: break
            if not _m: continue
            try: _w=dt.datetime.fromisoformat(_ts.replace("Z","+00:00"))
            except Exception: continue
            if _w.tzinfo is None or (_nu-_w).days>45: continue
            _gday=_GDS.get((_p["team"],int(_p["last"])),"")
            if _gday and _w.strftime("%Y-%m-%d")<_gday: continue             # written before his last game - he has played since
            SEASON_OUT.add(_nk); SEASONOUT_WHY[_nk]=f'{_sr}: "{_m.group(0)}" ({_w:%b} {_w.day})'; break
    if not QUIET: print(f"Scout season-ending check: {len(SEASONOUT_WHY)} men out for the year"+(" - "+", ".join(sorted(SEASONOUT_WHY)) if SEASONOUT_WHY else ""))
except Exception as _e: print("Scout season-ending check skipped:",_e)
# Oct 21 (Dom): return dates count the TEAM'S GAMES, not calendar weeks - a bye inside the stretch pushes the return a week
# (Pittman: IR Oct 10, PIT bye Wk 9 -> back Wk 10, not 9), and IR runs four games from the day he was PLACED on it, which can
# be later than his last game (Roman Wilson: hurt Wk 5, placed Oct 17 -> back Wk 11, not 10).
_TGW={}
try:
    for (_t_,_w_),_d_ in _GD.items(): _TGW.setdefault(_t_,[]).append(_w_)
    for _t_ in _TGW: _TGW[_t_]=sorted(set(_TGW[_t_]))
except Exception: pass
def _gafter(t,w,n):
    ws=[x for x in _TGW.get(t,[]) if x>w]
    return ws[n-1] if len(ws)>=n else 99
IRPL={}
try:
    _IRRE=re.compile(r"(plac\w*|lands?|landed|put|puts|headed|bound|moved|moves|going)\b[^.]{0,40}?\b(injured reserve|IR)\b",re.I)
    for _nm,_tx,_ts,_src in _IT:
        if not _ts or _src=='ESPN' or not _IRRE.search(str(_tx)[:300]): continue   # placement stories only; only matters for a man already tagged IR
        _when=str(_ts)[:10]
        for _k,_p in _NAMES.items():
            if not _p['name'] or _p['name'] not in _nm: continue
            _fw=next((w for w in _TGW.get(_p['team'],[]) if _GD.get((_p['team'],w),'')>=_when),None)
            if _fw and (_k not in IRPL or _fw>IRPL[_k][0]): IRPL[_k]=(_fw,_when)
except Exception as _e: print('Scout IR placement read skipped:',_e)
def _newsback(p):
    n=NEWSOUT.get(norm(p['name']))
    return _gafter(p['team'],int(p['last']),n[0]+1) if n else 0
def back(p,ytag=""):
    if not ytag: ytag=EXTINJ.get((norm(p["name"]),p.get("pos","")),"")   # Oct 14: no Yahoo tag -> ESPN/Sleeper status
    if ytag in ("NA","CEL") or norm(p["name"]) in SEASON_OUT: return 99
    if ytag in ("IR","IR-R","PUP-R") or p.get("nflstat")=="RES":
        _pl=IRPL.get(norm(p["name"]))
        return max(_gafter(p["team"],int(p["last"]),5),_gafter(p["team"],_pl[0]-1,5) if _pl else 0,NOW+1,_newsback(p))
    if ytag=="O" or p.get("rep") in ("Out","Doubtful"): return max(NOW+1,_newsback(p))
    return max(NOW,_newsback(p))   # Oct 12: news that he will miss time

# ================= ripples: a backup's boost ends when the man he replaced is due back =================
SNAP={(norm(r.player),r.team,int(r.week)):r.offense_pct for r in sn.itertuples()}
TEAMLAST=st.groupby("team").week.max().to_dict()
INJWK=int(inj.week.max()) if len(inj) else 0      # Oct 21: the injury report's week - a full practice counts only on this week's report
CLOSE={}
skill={k:p for k,p in PL.items() if p["pos"] in ("QB","RB","WR","TE")}
for k,p in skill.items():
    o=owner(k); yt=o[2] if o else ""; bw=back(p,yt); why=""
    if bw==99: continue
    if bw>NOW: why=("on IR" if (yt in ("IR","IR-R","PUP-R") or p["nflstat"]=="RES") else "listed Out")+(f" ({p['inj']})" if p["inj"] else "")
    elif p["last"]<TEAMLAST.get(p["team"],0) and p["nflstat"]!="RES" and p["inj"]: bw=NOW; why=f"missed his last game{' ('+p['inj']+')' if p['inj'] else ''}, practicing this week ({(p['prac'] or 'no report').replace(' Participation in Practice','').lower()})"
    else: continue
    full=[w for w in p["wks"] if SNAP.get((k[0],p["team"],w),1)>=.35]
    if not full: continue
    # the returning man must be a real role player, not a backup who saw garbage time (Lock, Cropper, Oliver, Moore)
    starter_wks=[w for w in p["wks"] if SNAP.get((k[0],p["team"],w),0)>=(.7 if p["pos"]=="QB" else .5)]
    if not starter_wks or p["fwd"]<6 or (p["pos"]=="QB" and p["last"] not in starter_wks): continue
    for k2,m in skill.items():
        if k2==k or m["team"]!=p["team"] or m["pos"]!=p["pos"]: continue
        if p["fwd"]<.5*m["fwd"]: continue
        def blend(f,x): return (.7*f+.3*x) if m["proven"] else (.4*f+.6*x)
        withv=[blend(f,x) for f,x,w in zip(m["fp"],m["xv"],m["wks"]) if w in full]
        wo=[blend(f,x) for f,x,w in zip(m["fp"],m["xv"],m["wks"]) if w not in full]
        if not wo: continue
        wv=np.mean(withv) if withv else (0.0 if p["pos"]=="QB" else .5*np.mean(wo))
        if m["proven"] and m["prior"]: wv=(len(withv)*wv+3*m["prior"])/(len(withv)+3) if withv else wv
        if np.mean(wo)-wv>=2 and (k2 not in CLOSE or CLOSE[k2]["week"]>bw):
            CLOSE[k2]=dict(week=bw,who=p["name"],whokey=k,after=wv,before=np.mean(wo),why=why)

RETURNERS={}
try:   # Oct 21 (Dom): proven men coming back with no 2026 games (Josh Jacobs off the exempt list)
    _FDR=globals().get("_FD","/home/claude/domfantasy01/dk-feeds/feeds/")
    _spr=json.load(open(_FDR+"sleeper_players_min.json")).get("players",{}); _spr=_spr.values() if isinstance(_spr,dict) else _spr
    _have={norm(p["name"]) for p in PL.values()}
    _RX=re.compile(r"(practic\w*|return\w*|debut|activated|reinstated|off (?:the )?(?:commissioner'?s )?exempt|cleared|back on the field|could play|will play|expected to play|set to play)",re.I)
    _NOWX=re.compile(r"(debut|could play|will play|expected to play|set to play|chance to play|might play|may play)",re.I)
    _hl=[]
    for _fn in ("rotowire_history.jsonl","espn_news_history.jsonl","news_extra_history.jsonl"):
        try:
            for _l in open(_FDR+_fn):
                try: _j=json.loads(_l)
                except Exception: continue
                _t=str(_j.get("title") or ""); _ts=str(_j.get("published_utc") or "")
                if not _t or "?" in _t or _t.count(",")>=2: continue
                try: _w=dt.datetime.fromisoformat(_ts.replace("Z","+00:00"))
                except Exception: continue
                if _w.tzinfo is None or (dt.datetime.now(dt.timezone.utc)-_w).days>7: continue
                _hl.append((_w,_t,_t+" "+re.sub(r"<[^>]+>"," ",str(_j.get("text") or ""))))
        except Exception: pass
    for _x in _spr:
        _nm=_x.get("name") or ""; _ps=_x.get("pos"); _tm=_x.get("team")
        if _ps not in ("QB","RB","TE") or not _tm or _x.get("inj"): continue
        _nk=norm(_nm); _pr=P25.get(_nk)
        if _nk in _have or _nk in SEASON_OUT or _pr is None or _pr<(15 if _ps=="QB" else 10): continue
        _hit=[h for h in _hl if _nm in h[1] and _RX.search(h[2])]
        if not _hit: continue
        _h=max(_hit); _wk=NOW if _NOWX.search(_h[2]) else NOW+1
        RETURNERS[_nk]=dict(name=_nm,team=tm(_tm),pos=_ps,prior=_pr,week=_wk,news=f"{_h[1]} ({_h[0]:%b} {_h[0].day})")
        for _k2,_m in skill.items():
            if _m["team"]!=tm(_tm) or _m["pos"]!=_ps or _m["fwd"]>_pr*1.25: continue           # a teammate clearly better than him keeps his job
            if _k2 not in CLOSE or CLOSE[_k2]["week"]>_wk:
                CLOSE[_k2]=dict(week=_wk,who=_nm,whokey=(_nk,tm(_tm)),after=.5*_m["fwd"],before=_m["fwd"],why=f"back with no games yet this season - {_h[1]}")
    if not QUIET: print(f"Scout returners: {len(RETURNERS)} - "+", ".join(f"{v['name']} ({v['team']} {v['pos']}, Wk {v['week']})" for v in RETURNERS.values()))
except Exception as _e: print("Scout returners check skipped:",_e)

# Oct 14 afternoon (Dom): this week's Sleeper numbers + the this-week guard
import glob as _glb
_FDG = globals().get("_FD", "/home/claude/domfantasy01/dk-feeds/feeds/")
def _lastcsv(sub):
    fs = sorted(_glb.glob(os.path.join(_FDG, "proj", sub, f"wk{NOW}_*.csv")))
    return pd.read_csv(fs[-1]) if fs else None
_SLKD, _SLPPR = {}, {}
try:
    _kd = _lastcsv("sleeper_kdef")
    if _kd is not None:
        for _r in _kd.itertuples():
            _s = json.loads(_r.stats) if isinstance(_r.stats, str) else {}
            if _r.pos == "DEF":
                _v = (_s.get("sack", 0) + 2 * (_s.get("int", 0) + _s.get("fum_rec", 0) + _s.get("safe", 0) + _s.get("blk_kick", 0))
                      + 6 * _s.get("def_td", 0) + pa_pts(_s.get("pts_allow", 20)))
                _SLKD[("DEF", tm(str(_r.team)))] = round(_v, 2)
            elif _r.pos == "K" and CF["kick"]:
                f40, f50 = (3, 4) if CF["kick"] == "flat" else (4, 5)
                _v = (3 * (_s.get("fgm_0_19", 0) + _s.get("fgm_20_29", 0) + _s.get("fgm_30_39", 0)) + f40 * _s.get("fgm_40_49", 0)
                      + f50 * _s.get("fgm_50p", 0) + _s.get("xpm", 0) - _s.get("xpmiss", 0))
                _SLKD[("K", norm(_r.name))] = round(_v, 2)
    _pp = _lastcsv("sleeper")
    if _pp is not None:
        for _r in _pp.itertuples():
            if pd.notna(_r.pts_ppr): _SLPPR[norm(_r.name)] = float(_r.pts_ppr)
except Exception as _e: print("Scout: Sleeper this-week numbers skipped:", _e)
def _kdkey(p): return ("DEF", p["team"]) if p["pos"] == "DEF" else ("K", norm(p["name"]))

# Oct 14 2 PM (Dom): Yahoo's weekly projections (Chrome read) - blended half and half into the Scout's weekly values
_YP = {}
def _ypk(p): return ("DEF", tm(p["team"])) if p["pos"] == "DEF" else (p["pos"], norm(p["name"]))
try:
    _yf = f"{H}/yproj_dk{CF['n']}.txt"
    if os.path.exists(_yf):
        _yl = open(_yf).read().splitlines()
        _ym = re.search(r"read live (\w{3} \w{3} \d{1,2} \d{4} \d{1,2}:\d{2} [AP]M) PT", _yl[0] if _yl else "")
        _yt = dt.datetime.strptime(_ym.group(1), "%a %b %d %Y %I:%M %p").replace(tzinfo=NOWPT.tzinfo) if _ym else None
        if _yt and (NOWPT - _yt).total_seconds() <= 36 * 3600:
            for _l in _yl[1:]:
                _x = _l.split("|")
                if len(_x) < 5: continue
                try: _YP[((("DEF", tm(_x[2])) if _x[3] == "DEF" else (_x[3], norm(_x[1]))), int(_x[0]))] = float(_x[4])
                except Exception: pass
            print(f"Scout: Yahoo weekly projections in ({len(_YP)} player-weeks, read {_ym.group(1)} PT)")
        else: print("Scout: Yahoo projections file is older than 36 hours - not used")
    else: print("Scout: no Yahoo projections file - the Scout runs on its own model")
except Exception as _e: print("Scout: Yahoo projections skipped:", _e)
YMAX={}
for (_yk,_yw),_yv in _YP.items():
    if _yw>=NOW: YMAX[_yk]=max(YMAX.get(_yk,0.0),_yv)
def weekly(p,x,ytag=""):
    if x in byes.get(p["team"],[]) or x<back(p,ytag): return 0.0
    _y=_YP.get((_ypk(p),x))
    if x==NOW and p["pos"] in ("DEF","K") and _SLKD.get(_kdkey(p)) is not None: return _SLKD[_kdkey(p)] if _y is None else (_SLKD[_kdkey(p)]+_y)/2   # Oct 14: this week = Sleeper (+ Yahoo), league scoring
    v=p["fwd"]; ck=(norm(p["name"]),p["team"])
    if ck in CLOSE and x>=CLOSE[ck]["week"]: v=min(v,CLOSE[ck]["after"])
    _mv=v*RATIO.get((sched[p["team"]].get(x),p["pos"]),1.0)
    return _mv if _y is None else (_mv+_y)/2   # Oct 14 2 PM (Dom): half the Scout's model, half Yahoo's projection for that week

TEAMS=collections.defaultdict(list); MISS=[]
for r in ROS.itertuples():
    k=find(r.name,r.team,r.pos)
    if k is None: MISS.append(f"{r.name} ({r.team}, {r.tag or 'no tag'})"); continue
    TEAMS[r.tid].append(dict(key=k,name=r.name,pos=r.pos,ytag=r.tag,slot=r.slot))
taken=set(OWN)
def vals(m,x): return weekly(PL[m["key"]],x,m["ytag"])
def lineup(members,x):
    pool=sorted(((vals(m,x),m["pos"],i) for i,m in enumerate(members)),reverse=True); used=set(); out=[]
    for s in SLOTS:
        ok=okfor(s)
        pick=next(((v,i) for v,p,i in pool if i not in used and p in ok),(0.0,None))
        if pick[1] is not None: used.add(pick[1])
        out.append((s,pick[1],pick[0]))
    srt=sorted(out,key=lambda o:(SLOTS.index(o[0]),-o[2])); cnt=collections.Counter(); lab=[]
    for s,i,v in srt: cnt[s]+=1; lab.append((s+(str(cnt[s]) if SLOTS.count(s)>1 else ""),i,v))
    return lab
def total(members,x): return sum(v for _,_,v in lineup(members,x))
WEEKS=list(range(NOW,LAST+1)); MINE=TEAMS[ME]
LU={x:lineup(MINE,x) for x in WEEKS}; my={x:sum(v for _,_,v in LU[x]) for x in WEEKS}
OLU={x:lineup(TEAMS[OPP[x]],x) for x in WEEKS if x in OPP}
opp={x:(sum(v for _,_,v in OLU[x]) if x in OLU else float(np.median([total(TEAMS[t],x) for t in TEAMS if t!=ME]))) for x in WEEKS}
def winp(m): return .5*(1+math.erf(m/(SD*math.sqrt(2))))
def _lv(m): return math.exp(-.5*(m/SD)**2)/(SD*math.sqrt(2*math.pi))
MED={x:float(np.median([total(TEAMS[t],x) for t in TEAMS if t!=ME])) for x in WEEKS} if CF["median"] else {}
LEV={x:URG[x]*(_lv(my[x]-opp[x])+(_lv(my[x]-MED[x]) if CF["median"] else 0)) for x in WEEKS}

# ================= GATE 1: my holes, slot vs slot =================
def fullstrength():
    pool=sorted(((PL[m["key"]]["fwd"],m["pos"],i) for i,m in enumerate(MINE) if m["slot"]!="IR" and m["ytag"] not in ("NA","CEL")),reverse=True)
    used=set(); out=[]
    for s_ in SLOTS:
        ok=okfor(s_); _c=next(((v,p,i) for v,p,i in pool if i not in used and p in ok),None)
        if _c is None:   # Oct 13: nobody healthy for this seat (DK II kicker released, tagged NA) - the seat counts as worth 0
            _c=next(((0.0,m["pos"],i) for i,m in enumerate(MINE) if i not in used and m["pos"] in ok and m["slot"]!="IR"),None)
            if _c is None: raise SystemExit(f"Scout: nobody at all on the roster for {s_}")
        v,p,i=_c; used.add(i); out.append((s_,i,v))
    cnt=collections.Counter(); d={}
    for s_,i,v in sorted(out,key=lambda o:(SLOTS.index(o[0]),-o[2])): cnt[s_]+=1; d[s_+(str(cnt[s_]) if SLOTS.count(s_)>1 else "")]=(MINE[i]["name"],v,i)
    return d
FULL=fullstrength()
def where(name,x):
    for lab,i,v in LU[x]:
        if i is not None and MINE[i]["name"]==name: return lab
    return None
HOLES=collections.defaultdict(list)
for x in WEEKS:
    theirs={lab:(TEAMS[OPP[x]][i]["name"] if i is not None else None,v) for lab,i,v in OLU[x]} if x in OLU else {}
    for lab,i,v in LU[x]:
        fn,fv,fi=FULL[lab]; who=MINE[i]["name"] if i is not None else None
        tn,tv=theirs.get(lab,(None,None)); reasons=[]; kind="short"
        if who is None or v==0: kind="empty"; reasons.append(f"{fn} on bye" if x in byes.get(PL[MINE[fi]["key"]]["team"],[]) else "slot empty")
        else:
            p=PL[MINE[i]["key"]]; ck=MINE[i]["key"]
            if who!=fn:
                w_=where(fn,x)
                pf=PL[MINE[fi]["key"]]
                st_=("moves up to "+w_) if w_ else "on bye" if x in byes.get(pf["team"],[]) else "out" if x<back(pf,MINE[fi]["ytag"]) else f"sits for a better matchup ({who})"
                reasons.append(f"{fn} {st_}" + ("" if st_.startswith("sits") else f", {who} slides in"))
            if ck in CLOSE and x>=CLOSE[ck]["week"]: reasons.append(f"{who} fades to ~{CLOSE[ck]['after']:.0f} once {CLOSE[ck]['who']} is back")
            o=sched[p["team"]].get(x)
            if TAG.get((o,p["pos"]))=="hard": reasons.append(f"hard matchup vs {o}")
        short_full=fv-v; short_opp=(tv-v) if tv is not None else 0
        if kind=="empty" or (short_full>=2 and v<.85*fv) or (short_opp>=4 and reasons):
            HOLES[lab].append(dict(week=x,who=who,val=v,full=fv,fullname=fn,them=tn,themv=tv,reasons=reasons,kind=kind))
# ================= GATE 2: available players — workload / door / return → points → where do they improve my team =================
def gate2_reason(k,p):
    o=owner(k); r=[]
    if back(p)>NOW: r.append(f"due back Wk {back(p)} ({'IR minimum' if (p['nflstat']=='RES' or EXTINJ.get((norm(p['name']),p['pos']))=='IR') else 'listed Out'})")
    mates=[m for kk_,m in skill.items() if m["team"]==p["team"] and m["pos"]==p["pos"] and kk_!=k and back(m,(owner(kk_) or (0,0,''))[2])>NOW]
    if mates and len(p["xv"])>=2 and np.mean(p["xv"][-2:])>np.mean(p["xv"][:-2] or [0])+2: r.append(f"door open: {mates[0]['name']} out")
    if len(p["xv"])>=3:
        e,l=np.mean(p["xv"][:-2]),np.mean(p["xv"][-2:])
        if l-e>=3 and l>=1.25*e: r.append(f"workload up from {e:.1f} to {l:.1f} expected a game")
    if len(p["fp"])>=2 and np.mean(p["xv"] or [0])-np.mean(p["fp"])>=3: r.append(f"getting {np.mean(p['xv']):.1f} expected but scoring {np.mean(p['fp']):.1f}")
    if p.get("moved"): r.append(p["moved"])                       # Oct 17 (Dom): the trade check
    for _tc in p.get("tradecut",[]): r.append("door closing: "+_tc)
    return r
cands=[k for k in PL if k not in taken and PL[k]["fwd"]>=(5 if PL[k]["pos"] in ("K","DEF") else 6) and norm(PL[k]["name"]) not in SEASON_OUT]
# Oct 10 night (Dom): the Positions chart's free agents (its doors list) are priced here too, floor or not
DOORS={}
try:
    import io as _io, contextlib as _cl
    sys.path.insert(0,"/home/claude/dksys/engine"); _av=sys.argv[:]; sys.argv=["engine3v.py",str(NOW)]; _cwd=os.getcwd(); os.chdir("/home/claude/dksys/engine")
    with _cl.redirect_stdout(_io.StringIO()):
        import engine3v as _E3
        os.environ["DK_DOORCAP"]="99"; _R3,_O3,_=_E3.run(CF["lab"]); os.environ.pop("DK_DOORCAP",None)
    os.chdir(_cwd); sys.argv=_av
    for _o in _O3.itertuples():
        _k=find(_o.player,_o.team,_o.pos)
        if _k and _k not in taken: DOORS[_k]=dict(why=_o.why.split(" (")[0],doors=_o.doors)
    cands=list(dict.fromkeys(cands+[k for k in DOORS if norm(PL[k]["name"]) not in SEASON_OUT]))
except Exception as _ex: print("   scout: Positions doors not read -",_ex)
G2=[]
for k in cands:
    p=PL[k]; newm=dict(key=k,name=p["name"],pos=p["pos"],ytag="",slot="BN")
    team2=MINE+[newm]                                   # no drop: an add is priced as "if a seat opens"
    g={x:total(team2,x)-my[x] for x in WEEKS}
    good=[x for x in WEEKS if g[x]>=1.5]
    if not good: continue
    wins=sum(LEV[x]*g[x] for x in WEEKS)
    slots=collections.Counter(lab for x in good for lab,i,v in lineup(team2,x) if i is not None and team2[i]["key"]==k)
    lvl=slots.most_common(1)[0][0] if slots else "?"
    pk=[x for x in good if x in PLAYOFF]
    kind="season-long" if len(good)>=.6*len(WEEKS) else ("playoffs" if pk and len(good)==len(pk) else "fill")
    _flag=None if len(p["fp"])>=2 else "One game only — flag, not act."
    if p["pos"] not in ("K","DEF"):
        _missed=p["last"]<TEAMLAST.get(p["team"],0) and not p.get("moved") and bool(p.get("inj") or EXTINJ.get((norm(p["name"]),p["pos"])))
        _full=INJWK==NOW and "full" in str(p.get("prac","")).lower()
        if back(p)>NOW: _flag=f"Watch, not a pickup yet: listed out, due back Wk {back(p)} - waits for his return to be confirmed (a full practice)."
        elif _missed and not _full: _flag="Watch, not a pickup yet: missed his last game hurt"+(f" ({p['inj']})" if p.get("inj") else "")+" - waits for a full practice this week."
        elif (_YP or _SLPPR) and _flag is None:
            _ob=[v for v in (YMAX.get(_ypk(p)),_SLPPR.get(norm(p["name"]))) if v is not None]
            if not _ob: _flag="Watch: only the Scout's model has a number on him - no Yahoo or Sleeper projection backs it."
            elif max(_ob)<5: _flag=f"Watch: Yahoo/Sleeper have him at {max(_ob):.1f} at best - the Scout's ~{p['fwd']:.1f} isn't backed up."
    # Oct 24 (Dom, Ladd McConkey in DK II): a returning player on WAIVERS can't wait for a full practice - his claim window
    # closes first and a rival takes him. If his waivers clear within 2 days and he helps in any week ahead,
    # he goes up as a claim decision now, with the injury written on the card.
    if _flag and _flag.startswith("Watch, not a pickup yet") and k[0] in WAIV:   # any kind - a fill he'd cover is still lost if a rival claims him first
        try:
            _cd = dt.datetime.strptime(WAIV[k[0]] + f" {dt.date.today().year}", "%b %d %Y").date()
            if (_cd - dt.date.today()).days <= 2:
                _flag = None; p = dict(p); p["claim_note"] = f"Injured now ({p.get('inj') or 'listed out'}), due back Wk {back(p)} - but his waivers clear {WAIV[k[0]]}, before a return can be confirmed. Claim decision now or he goes to whoever claims him."
        except Exception: pass
    G2.append(dict(act=_flag is None,flag=_flag,k=k,p=p,g=g,good=good,wins=wins,lvl=lvl,kind=kind,why=([p["claim_note"]] if p.get("claim_note") else [])+list(gate2_reason(k,p)),acq=("waivers, clears "+WAIV[k[0]]) if k[0] in WAIV else "free agent"))
G2.sort(key=lambda e:-e["wins"])
# Oct 21 (Dom): PRICE THE DROP - every pickup is priced against the best man to let go for him (or an open bench seat)
try:
    _BCAP={"DKI":5,"DKII":5,"DKIII":5,"DKIV":5}.get(LGK,5); _openb=_BCAP-sum(1 for m in MINE if m["slot"]=="BN")
    # a handcuff is never the drop (Dom: check what a bench man is FOR): the #2 back behind a lead back (12+ a game, half the touches)
    _HC=set(); _tl0=st.groupby("team").week.max().to_dict()
    for _t,_g in st[st.position=="RB"].groupby("team"):
        _g=_g[_g.week>=_tl0.get(_t,0)-2]; _tch=(_g.carries.fillna(0)+_g.targets.fillna(0)).groupby(_g.player_display_name).sum().sort_values(ascending=False)
        if len(_tch)>=2 and _tch.sum()>0 and _tch.iloc[0]/_tch.sum()>=.5 and _tch.iloc[1]/_tch.sum()>=.15:
            _sk0=find(_tch.index[0],_t,"RB")
            if _sk0 and PL[_sk0]["fwd"]>=12: _HC.add(norm(_tch.index[1]))
    _cut=[(i,m) for i,m in enumerate(MINE) if m["slot"]!="IR" and m["name"] not in CF["protect"] and norm(m["name"]) not in _HC]
    for e in G2:
        if _openb>0: e["drop"]=None; continue
        _nm=dict(key=e["k"],name=e["p"]["name"],pos=e["p"]["pos"],ytag="",slot="BN"); _best=None
        for i,m in _cut:
            _t3=[x for j,x in enumerate(MINE) if j!=i]+[_nm]
            _g={x:total(_t3,x)-my[x] for x in WEEKS}; _s=sum(_g.values())
            if _best is None or _s>_best[0]: _best=(_s,m,_g)
        if _best is None: continue
        e["drop"]=_best[1]["name"]; e["g_nodrop"]=e["g"]; e["g"]=_best[2]
        e["good"]=[x for x in WEEKS if e["g"][x]>=1.5]; e["wins"]=sum(LEV[x]*e["g"][x] for x in WEEKS)
    G2=[e for e in G2 if e["good"] and (not e.get("drop") or sum(e["g"].values())>0)]   # a pickup that loses points net of the drop is no pickup
    G2.sort(key=lambda e:-e["wins"])
    if not QUIET: print(f"Scout drop pricing: {'open bench seat - no drop needed' if _openb>0 else str(len(G2))+' pickups priced against the best drop'}")
except Exception as _e: print("Scout drop pricing skipped:",_e)
def _gn(e): return round(sum(e["g"].values()) if e.get("drop") else sum(max(0.0,v) for v in e["g"].values()),1)    # net of the drop
def _pgn(e): return round(sum(e["g"].get(x,0.0) for x in PLAYOFF) if e.get("drop") else sum(max(0.0,e["g"].get(x,0.0)) for x in PLAYOFF),1)

# ================= life cycle =================
SF=f"{H}/scout_state_{LGK}.json"
state=json.load(open(SF)) if os.path.exists(SF) else {"items":{},"kills":{}}
state.setdefault("kills",{})
state["kills"].setdefault("Tyler Higbee",{"type":"soft","on":"2026-10-09","until_week":NOW+2,"why":"Dom: Ferguson back Wk 8, three Rams TEs by the playoffs"})
def kills_str():
    ks=[(n,k) for n,k in state["kills"].items() if killed(n)]
    return " · Killed: "+", ".join(f"{n.split()[-1]} ({'soft, two games' if k['type']=='soft' else 'season'})" for n,k in ks) if ks else ""
def killed(n): k=state["kills"].get(n); return bool(k) and (k["type"]=="hard" or NOW<=k.get("until_week",0))
def age(first):
    d=(NOWPT.date()-dt.date.fromisoformat(first)).days
    return "added today" if d==0 else "added yesterday" if d==1 else f"added {d} days ago"
def wk(lst):
    if not lst: return ""
    runs=[];s=p_=lst[0]
    for x in lst[1:]+[None]:
        if x is None or x!=p_+1: runs.append(f"Week {s}" if s==p_ else f"Weeks {s}-{p_}"); s=x
        p_=x if x is not None else p_
    return ", ".join(runs)
def recline(e):
    p=e["p"]; sc=", ".join(f"{v:.0f}" if p['pos'] in ('K','DEF') else f"{v:.1f}" for v in p["fp"])
    when=wk(e["fill_weeks"]) if e.get("fill_weeks") else wk(e["good"])
    why="; ".join(e["why"]) if e["why"] else f"his current level, ~{p['fwd']:.0f} a game, improves the team"
    _nl,_nb=newscheck(p)                                            # Oct 17 (Dom): the news check
    if _nl: why=why+"; "+_nl
    return f"{p['name']}, {p['team']} — scored {sc} — {e['acq']} — {why}; helps {when}"

# ================= build the board =================
def fills_for(okpos,w):
    f=[]
    for e in G2:
        if e["p"]["pos"] not in okpos or killed(e["p"]["name"]) or not e["act"]: continue
        fw=[x for x in w if e["g"][x]>=1.5]
        if not fw: continue
        f.append((sum(LEV[x]*e["g"][x] for x in w),dict(e,fill_weeks=fw)))
    return sorted(f,key=lambda t:-t[0])
needs=[]
def add_need(lab,kind,w,bar,why,lst,okpos,ideal=None):
    fl=fills_for(okpos,w); stake=sum(LEV[h["week"]]*max(h["full"]-h["val"],(h["themv"] or 0)-h["val"],0) for h in lst) if lst else 0
    if kind=="season-long": stake=sum(LEV[x]*(FULL[lab][1]-bar) for x in WEEKS)
    scarcity=1/(1+min(len(fl),6)*.35)
    needs.append(dict(lab=lab,kind=kind,weeks=w,bar=bar,ideal=ideal,why=why,holes=lst,fills=fl[:2],n=len(fl),stake=stake,prio=stake*scarcity))
for lab,lst in HOLES.items():
    pos=lab.rstrip("12"); okpos=okfor(pos)
    fn,fv,fi=FULL[lab]; single=SLOTS.count(pos)==1
    emp=[h for h in lst if h["kind"]=="empty"]; sh=[h for h in lst if h["kind"]!="empty"]
    if emp:                                                 # one need per slot, all its empty weeks together
        rs=" · ".join((f"Wk {h['week']} " if len(emp)>1 else "")+h['reasons'][0] for h in emp)
        add_need((pos+"2") if single else lab,"fill",[h["week"] for h in emp],0,f"{rs}; ideally ~{fv:.0f} ({fn}{"'" if fn.endswith('s') else "'s"} level)",emp,okpos,ideal=fv)
    if sh:
        add_need(lab,"fill",[h["week"] for h in sh],float(np.mean([h["val"] for h in sh])),None,sh,okpos)
# season-long: the slot's regular holder is about to fade (the man he replaced is coming back)
for lab,(fn,fv,fi) in FULL.items():
    k=MINE[fi]["key"]
    if k in CLOSE and CLOSE[k]["week"]<=NOW+1:
        c=CLOSE[k]; pos=lab.rstrip("12"); okpos=okfor(pos)
        add_need(lab,"season-long",WEEKS,c["after"],f"replacing a ~{c['before']:.0f}: {fn} becomes ~{c['after']:.0f} once {c['who']} is back ({c['why']}) — anything over {c['after']:.0f} is an improvement",[],okpos)
needs.sort(key=lambda n:-n["prio"])
# ================= print =================
out=[]
P=out.append
# Oct 23 (Dom): the header said "Yahoo 9:50 AM", "Weeks 1-4" and an old record no matter when it ran - every
# stamp here now comes from the files actually read
_wt=st.groupby("week").team.nunique() if len(st) else None   # Oct 23: a week counts once most teams have played it (Thursday's lone game is not a week)
_GW=int(max([w for w,n in _wt.items() if n>=24] or [0])) if _wt is not None else 0
_GX=int(st.week.max()) if len(st) else 0
_GWS=f"Weeks 1-{_GW}"+(f" + Week {_GX} games so far" if _GX>_GW else "")
_st0=dt.datetime.fromtimestamp(os.path.getmtime(f"{D}/stats_player_week_2026.csv"),dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=-7)))
_ststamp0=f"{_st0:%a} {_st0.hour%12 or 12}:{_st0:%M} {'AM' if _st0.hour<12 else 'PM'} PT"
_REC=CF["record"]
try:
    import glob as _g0
    _sf0=sorted(_g0.glob(f"{L}/yahoo/wk{NOW}/standings_*.txt"),key=os.path.getmtime)
    _lid0={"DKI":"269381","DKII":"1519795","DKIII":"1507991","DKIV":"864215"}[LGK]
    for _ln0 in (open(_sf0[-1]) if _sf0 else []):
        if _ln0.startswith(_lid0+"#"):
            _rows0=[r.split("^") for r in _ln0.split("#",1)[1].strip().split("|")]
            _rows0=[r for r in _rows0 if len(r)>=5]
            _w=lambda r: tuple(int(x) for x in r[2].split("-")[:2])
            _rows0.sort(key=lambda r:(-_w(r)[0],_w(r)[1],-float(r[4] or 0)))
            for _i0,r in enumerate(_rows0,1):
                if re.sub(r"[^a-z0-9]","",r[1].lower())==re.sub(r"[^a-z0-9]","",str(TEAMNAMES.get(ME,"")).lower()): _REC=f"{r[2].rsplit('-0',1)[0] if r[2].endswith('-0') else r[2]}, {_i0}{'th' if 10<=_i0%100<=20 else {1:'st',2:'nd',3:'rd'}.get(_i0%10,'th')} of {len(_rows0)} (Yahoo standings {os.path.basename(_sf0[-1])[10:-4]})"
except Exception as _e0: pass
P(f"THE SCOUT — {CF['lab']} — run {NOWPT.strftime('%a %b %d, %I:%M %p PT')} — record {_REC}")
P(f"Inputs: all {len(TEAMNAMES)} rosters + waivers ({CF['rost_at']}) · stats & play-by-play (nflverse {_ststamp0}; {_GWS}) · 2025 season as a prior · Yahoo projections only as a cross-check")
P(f"Read depth: {_GWS} of 2026 data — directional, not settled.\n")
P("GATE 1 — YOUR NEEDS, IN PRIORITY ORDER")
for n,nd in enumerate(needs,1):
    w=nd["weeks"]; when="season-long" if nd["kind"]=="season-long" else wk(w)+" fill"
    first=state["items"].setdefault(f"need:{nd['lab']}:{when}",NOWPT.date().isoformat())
    mark="RED" if (min(w)<=NOW+1 and nd["n"]>0) or (nd["kind"]=="season-long") else "GOLD"
    bar=f"ideally beat {nd['bar']:.0f}" if nd["bar"]>0 else f"anything beats 0, ideally ~{nd['ideal']:.0f}"
    P(f"{n}. [{mark}] {nd['lab']}, {when}, {bar}  ({age(first)})")
    if nd["why"]: P(f"   Why: {nd['why']}.")
    else:
        rs_=[]
        for h in nd["holes"]: rs_.append(f"Wk {h['week']}: {h['who']} ~{h['val']:.0f}"+(f" ({'; '.join(h['reasons'])})" if h['reasons'] else ""))
        P(f"   Why: at full strength this slot gives ~{nd['holes'][0]['full']:.0f} ({nd['holes'][0]['fullname']}). "+" · ".join(rs_)+".")
    opps=[h for h in nd["holes"] if h["them"]]
    if opps: P("   Man across from you: "+" · ".join(f"Wk {h['week']} {h['them']} ~{h['themv']:.0f} vs your {h['who'] or 'nobody'} ~{h['val']:.0f}" for h in opps[:4]))
    if not nd["fills"]: P("   No recommendation — nobody available fits.")
    else:
        for j,(val,e) in enumerate(nd["fills"],1): P(f"   {j}) {recline(e)}")
    P(f"   Kill when: {'its week passes' if nd['kind']!='season-long' else 'the man he replaced is back and the fade is confirmed in real games, or a pickup fills it'}.")
P("\nGATE 2 — AVAILABLE PLAYERS WHO COULD INCREMENTALLY IMPROVE THE TEAM (found by workload / door / return; ranked by wins added)")
shown=0
for e in G2:
    if killed(e["p"]["name"]) or not e["why"]: continue
    if not e["act"]: e=dict(e,why=e["why"]+[e.get("flag") or "one game only — flag, not act"])
    first=state["items"].setdefault("g2:"+e["p"]["name"],NOWPT.date().isoformat()); shown+=1
    kind="season-long" if e["kind"]=="season-long" else ("playoffs" if e["kind"]=="playoffs" else wk(e["good"]))
    P(f"{shown}. [{'RED' if min(e['good'])<=NOW+1 and e['wins']>=.1 else 'GOLD'}] {e['lvl']}, {kind} — {recline(e)}  ({age(first)})")
    if shown>=8: break
if shown==0: P("   none this run")
hf=f"{H}/hunches_{LGK}.csv"
P("\nGATE 3 — HUNCHES"); P(open(hf).read().strip() if os.path.exists(hf) and len(open(hf).read().strip().splitlines())>1 else "   none written yet")
P(f"\nCHECKED, NOT ASSUMED — players the math leans on, verified against the live Yahoo rosters ({CF['rost_at']}) and the injury report:")
for k,c in CLOSE.items():
    o=owner(k)
    if not o or o[0]!=ME: continue
    r=owner(c["whokey"])
    status=f"rostered by {TEAMNAMES[r[0]]} ({r[1]}{', Yahoo tag '+r[2] if r[2] else ''})" if r else "NOT ROSTERED — available in "+CF["lab"]
    pr=PL.get(c["whokey"],{"prac":""})   # Oct 21: a returner with no 2026 games is not in PL
    P(f" • {PL[k]['name']}: ~{c['before']:.0f} → ~{c['after']:.0f} from Week {c['week']}, because {c['who']} ({c['why']}) is due back. {c['who']}: {status}; practice: {pr['prac'] or 'no report'}.")
P("\nPROTECTED (Dom's call): "+", ".join(CF["protect"])+kills_str()+(" · PENDING: "+CF["pending"] if CF["pending"] else ""))
if MISS: P("No 2026 games, not scored: "+", ".join(MISS))
# ---- structured board for the Dispatch page (Dispatch voice: no "you/your", one decimal, capitalized labels)
_stt=dt.datetime.fromtimestamp(os.path.getmtime(f"{D}/stats_player_week_2026.csv"),dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=-7)))
_ststamp=f"{_stt:%a} {_stt.hour%12 or 12}:{_stt:%M} {'AM' if _stt.hour<12 else 'PM'} PT"
BOARD=dict(league=CF["lab"],run=NOWPT.isoformat(),run_str=NOWPT.strftime('%a %b %d, %I:%M %p PT').replace(' 0',' '),
           depth=f"Built from real points and workload — {_GWS} of 2026 data, so read it as a direction · rosters {CF['rost_at']} · stats nflverse "+_ststamp,
           gate1=[],gate2=[],gate3=[],checked=[],
           footer=(("Protected (Dom's call): "+", ".join(CF["protect"])) if CF["protect"] else "Protected: none")+kills_str()+(" · Pending: "+CF["pending"] if CF["pending"] else ""))
def sn_(n):
    if not n: return "nobody"
    if n.split()[0] in ("New","Los","San","Green","Kansas","Tampa","Las"): return n
    parts=[x for x in n.split() if x.rstrip(".") not in ("Jr","Sr","II","III","IV","V")]; return parts[-1] if parts else n
def short_r(r):
    r=r.replace(" Jr.","").replace(" Sr.","").replace(" II","").replace(" III","")
    r=re.sub(r"([A-Z][a-z'A-Z.\-]+ )+([A-Z][a-zA-Z'\-]+)",lambda m:m.group(2),r)
    return re.sub(r"(\S+) sits for a better matchup \(([^)]+)\)",r"\1 has a worse matchup",r)
def wkc(lst):
    runs=[];s_=p_=lst[0]
    for x in lst[1:]+[None]:
        if x is None or x!=p_+1: runs.append(f"{s_}" if s_==p_ else f"{s_}-{p_}"); s_=x
        p_=x if x is not None else p_
    return ("Week " if len(lst)==1 else "Weeks ")+", ".join(runs)
_NOUN={"RB":"the Backfield","WR":"the Receiving Corps","TE":"the Tight End Spot","QB":"the Quarterback Spot","K":"the Kicker Spot",
       "DEF":"the Defense","FLEX":"the Flex","SUPERFLEX":"the Superflex"}
def _cause(r):
    if "on bye" in r: return "bye"
    if "hard matchup" in r: return "matchup"
    if "fades to" in r: return "fade"
    if r=="slot empty": return "empty"
    return "shuffle"
def headline(nd):
    """the plain-language headline that leads each need: names the problem; the slot code rides behind it"""
    pos=nd["lab"].rstrip("12"); n=_NOUN.get(pos,pos); N=n[0].upper()+n[1:]; one=len(nd["weeks"])==1
    if nd["kind"]=="season-long": return f"{N} Won't Hold"
    if nd["bar"]==0: return "The Defense Goes Dark" if pos=="DEF" else ("The Kicker Goes Dark" if pos=="K" else f"The {nd['lab']} Slot Goes Empty")
    cs=[_cause(h["reasons"][0]) if h["reasons"] else "shuffle" for h in nd["holes"]]
    top=max(set(cs),key=lambda x:(cs.count(x),x=="bye"))
    if top=="bye": return f"A Bye Hits {n}" if one else f"Byes Hit {n}"
    if top=="matchup": return f"A Tough Draw for {n}" if one else f"Tough Draws for {n}"
    if top=="fade": return f"{N} Fades"
    return f"{N} Runs Thin"
def cap_when(w): return "Season-Long" if w=="season-long" else w.replace("fill","Fill")
# Oct 14 afternoon (Dom): THE THIS-WEEK GUARD - this week's numbers for a pickup next to the starter he'd replace
_MET = {}
try:
    for _m in json.load(open(f"{L}/meter/meter_wk{NOW}.json"))["leagues"][CF["lab"]]["starters"]["me"]:
        _MET[("DEF", tm(_m.get("team") or "")) if _m.get("pos") == "DEF" else (_m.get("pos"), norm(_m["player"]))] = _m
except Exception as _e: print("Scout: meter numbers for the this-week guard skipped:", _e)
_GOT = {}
try:
    _gc = pd.read_csv(os.path.join(os.path.dirname(H), "engine", f"gotham_{LGK}.csv"))
    if "week" in _gc and int(_gc.week.iloc[0]) == NOW:          # only a Gotham run for THIS week counts
        for _r in _gc.itertuples():
            if pd.notna(_r.eng_wk): _GOT[norm(_r.player)] = float(_r.eng_wk)
    else: print("Scout: Gotham file is not for Week", NOW, "- the guard shows Gotham as not read")
except Exception as _e: print("Scout: Gotham numbers for the this-week guard skipped:", _e)
def _f(v): return "not read" if v is None else f"{v:.1f}"
def thisweek(p):
    try:
        if NOW not in LU: return ""
        el = [(lab, i, v) for lab, i, v in LU[NOW] if i is not None and p["pos"] in okfor(re.sub(r"\d+$", "", lab))]
        if not el: return ""
        lab, i, v = min(el, key=lambda t: t[2]); st = MINE[i]; sp = PL[st["key"]]
        kd = p["pos"] in ("DEF", "K")
        if v <= 0:                                            # nobody playing in that seat this week (bye / out)
            return f"This week: your {lab} seat has nobody playing ({st['name']} {'on bye' if NOW in byes.get(sp['team'], []) else 'out'}), so any healthy {p['pos']} who plays helps this week"
        mk = ("DEF", sp["team"]) if sp["pos"] == "DEF" else (sp["pos"], norm(st["name"]))
        sm = _MET.get(mk, {})
        if x_bye := (NOW in byes.get(p["team"], [])): return f"This week: {p['name'].replace(' defense',' DEF')} has a bye - no help this week"
        if NOW < back(p): return f"This week: {p['name']} is out (due back Wk {back(p)}) - no help this week"
        a = dict(Gotham=(None if kd else _GOT.get(norm(p["name"]))),
                 Sleeper=(_SLKD.get(_kdkey(p)) if kd else _SLPPR.get(norm(p["name"]))), Yahoo=_YP.get((_ypk(p), NOW)))
        b = dict(Gotham=(sm.get("gotham") if not kd else None) if sm else (None if kd else _GOT.get(norm(st["name"]))),
                 Sleeper=(_SLKD.get(_kdkey(sp)) if kd else _SLPPR.get(norm(st["name"]))), Yahoo=sm.get("yahoo") if sm.get("yahoo") is not None else _YP.get((_ypk(sp), NOW)))
        pairs = [(k, a[k], b[k]) for k in ("Gotham", "Sleeper", "Yahoo") if not (kd and k == "Gotham")]
        both = [(x, y) for _, x, y in pairs if x is not None and y is not None]
        verdict = ("WORSE this week" if both and all(x < y for x, y in both) else "better this week" if both and all(x > y for x, y in both)
                   else "mixed this week" if both else "this week unknown")
        nm = st["name"] if sp["pos"] != "DEF" else st["name"] + " DEF"
        return (f"This week vs your {lab} {nm}: " + " · ".join(f"{k} {_f(x)} vs {_f(y)}" for k, x, y in pairs)
                + (" (Sleeper PPR)" if not kd else "") + f" - {verdict}")
    except Exception as _e:
        return ""
def _gd_ko(team):
    try:
        g_=games[(games.week==NOW)&((games.home_team==team)|(games.away_team==team))]
        if not len(g_): return None
        r_=g_.iloc[0]; t_=dt.datetime.strptime(f"{r_.gameday} {r_.gametime}","%Y-%m-%d %H:%M")-dt.timedelta(hours=3)   # Eastern -> Pacific
        return t_
    except Exception: return None
def guard(e):
    """Oct 21 (Dom): late kickoff (the Sunday bench locks first) and a starter who could come back and take the work"""
    p=e["p"]; k=e["k"]; out=[]
    t_=_gd_ko(p["team"])
    if t_ is not None and t_.weekday() in (0,3):
        out.append(f"plays {t_:%A} night ({t_.hour%12 or 12}:{t_:%M} PM PT) - if you start him and he sits, your Sunday players have already locked")
    if k in CLOSE:
        c_=CLOSE[k]; out.append(f"his role shrinks to ~{c_['after']:.1f} from Wk {c_['week']} when {c_['who']} is back ({c_['why']})")
    for r_ in e.get("why") or []:
        m_=re.match(r"door open: (.+) out",r_)
        if m_ and k not in CLOSE: out.append(f"his work depends on {m_.group(1)} staying out - check {m_.group(1).split()[-1]}'s status first")
    return out
_STAND={}
try:
    _sf=sorted(_glb.glob(f"{L}/yahoo/wk{NOW}/standings_*.txt"))
    if _sf:
        _lid={"DKI":"269381","DKII":"1519795","DKIII":"1507991","DKIV":"864215"}[LGK]
        for _ln in open(_sf[-1]):
            if not _ln.startswith(_lid+"#"): continue
            for _row in _ln.split("#",1)[1].strip().split("|"):
                _c=_row.split("^")
                if len(_c)>=9 and _c[7].startswith("$"): _STAND[re.sub(r"[^a-z0-9]","",_c[1].lower())]=(_c[7],_c[8])
except Exception as _e: print("Scout rival check: standings not read -",_e)
def _faab(tid):
    n_=re.sub(r"[^a-z0-9]","",str(TEAMNAMES.get(tid,"")).lower())
    for k_,v_ in _STAND.items():
        if n_ and (n_.startswith(k_) or k_.startswith(n_)): return v_
    return None
_NST={"QB":1,"RB":2,"WR":3,"TE":1}
def rivals(e):
    """Oct 21 (Dom): which other teams would start him over one of their own, and what each has to spend"""
    p=e["p"]
    if p["pos"] not in _NST or "aiver" not in e.get("acq",""): return None
    need=[]
    for tid,mem in TEAMS.items():
        if tid==ME: continue
        vs=sorted([PL[m["key"]]["fwd"] for m in mem if m["pos"]==p["pos"] and m["slot"]!="IR" and m["ytag"] not in ("NA","IR","O")],reverse=True)
        top=vs[:_NST[p["pos"]]]
        if len(top)<_NST[p["pos"]] or (top and p["fwd"]>top[-1]):
            fb=_faab(tid); need.append((TEAMNAMES.get(tid,str(tid)),fb))
    if not need: return "rival check: no other team would start him - the minimum bid should do"
    return f"rival check: {len(need)} team{'s' if len(need)>1 else ''} would start him over one of their own - "+", ".join(f"{n_} ({fb[0]} left, waiver #{fb[1]})" if fb else n_ for n_,fb in need[:6])
def _pick(e,need_red,w):
    p=e["p"]; sc=", ".join(f"{v:.0f}" if p['pos'] in ('K','DEF') else f"{v:.1f}" for v in p["fp"])
    why="; ".join(e["why"]) if e["why"] else f"current level ~{p['fwd']:.1f} a game"
    fw=e.get("fill_weeks") or e["good"]
    urg="red" if (need_red and min(fw)<=NOW+1) else "gold"
    _nl,_nb=newscheck(p)                                            # Oct 17 (Dom): the news check on every pickup
    if _nl: why=why+"; "+_nl
    if _nb or p.get("moved") or p.get("tradecut"): urg="gold"       # Oct 17 (Dom): check before acting
    _gl=guard(e); _rv=rivals(e)                                     # Oct 21 (Dom): the pickup guard + the rival check
    if _gl: why=why+"; CHECK FIRST: "+"; ".join(_gl); urg="gold"
    if _rv: why=why+"; "+_rv
    return dict(guard=_gl,rivals=_rv,drop=e.get("drop"),name=p["name"].replace(" defense"," DEF"),team=p["team"],pos=p["pos"],scores=sc,acq=e["acq"].replace("free agent","Free agent").replace("waivers,","Waivers,"),
                why=why[0].upper()+why[1:],when=wk(fw).replace("Week","Wk").replace("Weeks","Wks"),urg=urg,now=thisweek(p),
                gain=_gn(e),pgain=_pgn(e))   # Oct 10: points added through Wk 17
# ---- LIFE CYCLE + ARCHIVE (Dom, Oct 9): the Signal's rule on the spyglass. A need keeps one stable key per slot and
# kind; every day it shows is recorded. First day = splat; then a zero-padded day count. A need that left and came back
# prints its fresh count over the gap it was gone (01/12), never the splat. Nothing is deleted: every run appends to
# scout_archive_<league>.jsonl, so any item can be recalled after it leaves the page.
TODAY=NOWPT.date()
state.setdefault("life",{})
def life(key):
    L=state["life"].setdefault(key,{"eps":[]}); t=TODAY.isoformat()
    if L["eps"] and L["eps"][-1][1]>=(TODAY-dt.timedelta(days=1)).isoformat():
        L["eps"][-1][1]=max(L["eps"][-1][1],t)
    elif not L["eps"] or L["eps"][-1][1]!=t: L["eps"].append([t,t])
    st=dt.date.fromisoformat(L["eps"][-1][0]); age=(TODAY-st).days
    gap=None
    if len(L["eps"])>1: gap=(st-dt.date.fromisoformat(L["eps"][-2][1])).days
    return dict(age=age,gap=gap,first=L["eps"][0][0])
season_labs={nd["lab"] for nd in needs if nd["kind"]=="season-long"}
picked=set()
for nd in needs:
    if nd["kind"]!="season-long" and nd["lab"] in season_labs and nd["bar"]>0:
        continue                                            # folded into that slot's season-long line
    w=nd["weeks"]
    if nd["kind"]=="fill" and len(w)>=.6*len(WEEKS): nd["kind"]="season-long"
    when="season-long" if nd["kind"]=="season-long" else wkc(w)+" fill"
    key=f"need:{nd['lab']}:{nd['kind']}:{'empty' if nd['bar']==0 else 'short'}"; LF=life(key); first=LF["first"]
    red=(min(w)<=NOW+1 and nd["n"]>0) or (nd["kind"]=="season-long")
    tgt=nd["bar"] if nd["bar"]>0 else nd["ideal"]
    if nd["why"]: why=nd["why"].replace(f" — anything over {nd['bar']:.0f} is an improvement","")
    else:
        hs=nd["holes"]
        why=" · ".join(f"Wk {h['week']} {sn_(h['who'])} ~{h['val']:.1f}"+(f" ({short_r(h['reasons'][0])})" if h['reasons'] else "") for h in hs)
        why=f"Full strength ~{hs[0]['full']:.1f} ({sn_(hs[0]['fullname'])}). "+why
    if nd["kind"]=="season-long":
        extra=[n2 for n2 in needs if n2["lab"]==nd["lab"] and n2["kind"]!="season-long" and n2["bar"]>0]
        if extra:
            worst=sorted(extra[0]["holes"],key=lambda h:h["val"])[:2]
            why+=". Worst weeks: "+", ".join(f"Wk {h['week']} {sn_(h['who'])} ~{h['val']:.1f}" for h in worst)
    if nd["bar"]==0: why+=" — anything beats zero"
    across=" · ".join(f"Wk {h['week']} {sn_(h['them'])} ~{h['themv']:.1f} vs {sn_(h['who'])} ~{h['val']:.1f}" for h in nd["holes"] if h["them"])[:160]
    picks=[_pick(e,red,w) for _,e in nd["fills"]]; picked|={p["name"] for p in picks}
    BOARD["gate1"].append(dict(mark="red" if red else "gold",first=first,key=key,age=LF["age"],gap=LF["gap"],head=headline(nd),title=f"{nd['lab']}, {cap_when(when)}",target=f"Target {tgt:.1f} pts",
        why=(why[0].upper()+why[1:]).rstrip(".")+".",across=across,picks=picks,none=None if picks else "No recommendation — nobody available fits.",
        kill=("Drops Off After Wk "+str(max(w))) if nd["kind"]!="season-long" else "Drops Off When Filled",
        rows=sorted({n_ for n_ in ([FULL[nd["lab"]][0]] if nd["kind"]=="season-long" and nd["lab"] in FULL else [])+
                     [(h["fullname"] if h["kind"]=="empty" else h["who"]) for h in nd["holes"] if h["week"]<=NOW+1] if n_})))   # Oct 10: the men a live need is about
for e in G2:
    if killed(e["p"]["name"]) or not e["why"] or e["p"]["name"].replace(" defense"," DEF") in picked: continue
    LF=life("g2:"+e["p"]["name"]); first=LF["first"]
    kind="Season-Long" if e["kind"]=="season-long" else ("Playoffs" if e["kind"]=="playoffs" else wkc(e["good"]))
    BOARD["gate2"].append(dict(mark="red" if min(e['good'])<=NOW+1 and e['wins']>=.1 else "gold",first=first,age=LF["age"],gap=LF["gap"],title=f"{e['lvl']}, {kind}",pick=_pick(e,False,e["good"]),act=e["act"],flag=e.get("flag")))
    if len(BOARD["gate2"])>=4: break
for k,c in CLOSE.items():
    o=owner(k)
    if not o or o[0]!=ME: continue
    r=owner(c["whokey"])
    BOARD["checked"].append(f"{sn_(PL[k]['name'])} ~{c['before']:.1f} to ~{c['after']:.1f} from Wk {c['week']} — {c['who']} checked: "+
        (f"rostered by {TEAMNAMES[r[0]]}{' (IR)' if r[1]=='IR' else ''}" if r else "NOT rostered — available"))
from collections import Counter as _Ctr
# Oct 9 (Dom): a count only when the SAME slot repeats (DEF + DEF2, K + K2) - never RB1 vs RB2 or WR1 vs WR2
_fam=lambda it: re.sub(r"2$","",it["title"].split(",")[0]) if it["title"].split(",")[0].rstrip("2") in ("QB","TE","K","DEF","SUPERFLEX") else it["title"].split(",")[0]
BOARD["gate1"].sort(key=lambda it: 0 if it["mark"]=="red" else 1)   # Oct 9 (Dom): every red spyglass first, then gold; priority holds inside each
_cnt=_Ctr(_fam(it) for it in BOARD["gate1"])
for it in BOARD["gate1"]: it["rep"]=_cnt[_fam(it)] if _cnt[_fam(it)]>1 else 0
with open(f"{H}/scout_archive_{LGK}.jsonl","a") as _af:
    _af.write(json.dumps(dict(run=NOWPT.isoformat(),league=CF["lab"],
        gate1=[{k:it.get(k) for k in ("key","mark","head","title","target","why","kill","age","gap")}|{"picks":[p["name"] for p in it["picks"]]} for it in BOARD["gate1"]],
        gate2=[dict(title=it["title"],mark=it["mark"],name=it["pick"]["name"],why=it["pick"]["why"]) for it in BOARD["gate2"]]))+"\n")
# Oct 10 (Dom): open seats lead the page - empty starting slots, open bench seats, open IR slots - and the best uses of them,
# ranked by points the player adds to the best lineup through Week 17 (playoffs included). Caps from each league's Yahoo settings.
_CAP={"DKI":(5,1),"DKII":(5,2),"DKIII":(5,1),"DKIV":(5,3)}[LGK]; _me=ROS[ROS.tid==ME]
_nst=int((~_me.slot.isin(["BN","IR"])).sum())
BOARD["open"]=dict(start=max(0,len(SLOTS)-_nst),bench=max(0,_CAP[0]-int((_me.slot=="BN").sum())),ir=max(0,_CAP[1]-int((_me.slot=="IR").sum())))
BOARD["adds"]=[dict(guard=guard(e),rivals=rivals(e),drop=e.get("drop"),name=e["p"]["name"].replace(" defense"," DEF"),team=e["p"]["team"],pos=e["p"]["pos"],acq=e["acq"].replace("free agent","Free agent").replace("waivers,","Waivers,"),
                    gain=_gn(e),pgain=_pgn(e),now=thisweek(e["p"]))
               for e in sorted([e for e in G2 if e["act"] and not killed(e["p"]["name"])],key=lambda e:-_gn(e))[:6]]
_named={p["name"] for it in BOARD["gate1"] for p in it["picks"]}|{it["pick"]["name"] for it in BOARD["gate2"]}
_chk=[]
for _k,_d in DOORS.items():
    _p=PL[_k]
    if _p["name"] in _named or killed(_p["name"]): continue
    _e=next((e for e in G2 if e["k"]==_k),None); _gn=round(sum(max(0.0,v) for v in _e["g"].values()),1) if _e else 0.0
    _chk.append((-_gn,f"{_p['name']} ({_p['team']} {_p['pos']}) is on the Positions chart ({_d['why'].rstrip('; ')}) — "+
        (f"adds ~{_gn:.0f} pts through Wk 17" if _gn>=1 else "adds nothing to the best lineup through Wk 17")+f", real level ~{_p['fwd']:.1f} a game; ranks below the picks above"))
BOARD["priced"]={re.sub(r"[^a-z]","",re.sub(r"\b(jr|sr|ii|iii|iv|v)\b","",PL[_k]["name"].lower())):dict(fwd=round(PL[_k]["fwd"],1),gain=next((round(sum(max(0.0,v) for v in e["g"].values()),1) for e in G2 if e["k"]==_k),0.0)) for _k in DOORS}   # the page names the chart men
# Oct 10 night (Dom): a Questionable starter gets his contingency named - if he sits, what it costs and who fills it
BOARD["qcont"]=[]
for _i,_m in enumerate(MINE):                       # every man Yahoo has STARTING (the lineup as set) with a Q or D tag
    if _m["slot"] in ("BN","IR") or _m["ytag"] not in ("Q","D"): continue
    if int(PL[_m["key"]]["last"])>=NOW: continue      # Oct 12: his game this week is already over
    _v=vals(_m,NOW); _lab=next((l for l,j,v in LU[NOW] if j==_i),_m["pos"])
    _rest=[m for j,m in enumerate(MINE) if j!=_i]; _base=total(_rest,NOW); _loss=my[NOW]-_base; _fl=[]
    _okp=okfor(re.sub(r"\d+$","",_lab))
    for _k in [k for k in cands if PL[k]["pos"] in _okp and not killed(PL[k]["name"])]:
        _nm=dict(key=_k,name=PL[_k]["name"],pos=PL[_k]["pos"],ytag="",slot="BN")
        _g0=total(_rest+[_nm],NOW)-_base; _g1=(total(MINE+[_nm],NOW+1)-my[NOW+1]) if NOW+1 in my else 0.0
        if _g0>=1: _fl.append(dict(name=PL[_k]["name"],team=PL[_k]["team"],pos=PL[_k]["pos"],now=round(_g0,1),nxt=round(_g1,1),fwd=round(PL[_k]["fwd"],1),
                                   acq=("Waivers, clears "+WAIV[_k[0]]) if _k[0] in WAIV else "Free agent"))
    _fl.sort(key=lambda d:-(d["now"]+d["nxt"]))
    BOARD["qcont"].append(dict(name=MINE[_i]["name"],slot=_lab,tag=MINE[_i]["ytag"],val=round(_v,1),loss=round(_loss,1),fills=_fl[:3],
                               ir=BOARD["open"]["ir"]>0,bench=BOARD["open"]["bench"]>0))
BOARD["moves"]=[]
try:   # Oct 12 (Dom): roster moves - IR first, then drop candidates - stated plainly, Dom decides
    _irs=BOARD["open"]["ir"]; _hurt=[]
    for _m in MINE:
        if _m["slot"]=="IR" or _m["pos"] in ("K","DEF"): continue
        _p=PL[_m["key"]]; _b=back(_p,_m["ytag"]); _s=max(NOW,int(_p["last"])+1)
        if _b==99 or _b-_s>=2:
            _nw=NEWSOUT.get(norm(_p["name"]))
            _why=(_nw[1] if _nw else {"O":"Yahoo lists him Out","IR":"Yahoo lists him on IR","IR-R":"Yahoo lists him on IR","PUP-R":"Yahoo lists him on PUP","NA":"Yahoo lists him not active"}.get(_m["ytag"],"listed out"))
            _hurt.append((_p["fwd"],_m,_p,_b,_why,_s))
    _hurt.sort(key=lambda t:-t[0])
    for _f,_m,_p,_b,_why,_s in _hurt:
        _ret="out for the season" if _b==99 else (f"out Weeks {_s}-{_b-1}, back about Week {_b}" if _b-1>_s else f"out Week {_s}, back about Week {_b}")
        _bw=[w for w in range(_s,(_b if _b!=99 else _s))] ; _by=[w for w in byes.get(_p["team"],[]) if _b!=99 and _s<=w<=_b]
        while _b!=99 and _b in byes.get(_p["team"],[]): _b+=1
        _ret="out for the season" if _b==99 else (f"out Weeks {_s}-{_b-1}, back about Week {_b}" if _b-1>_s else f"out Week {_s}, back about Week {_b}")
        if _by: _ret+=f" (Week {_by[0]} is his bye)"
        _elig=_m["ytag"] in ("O","IR","IR-R","PUP-R","NA")
        _lvl=f"~{_f:.1f} a game when healthy"
        if _irs>0:
            _irs-=1
            _t=(f"Move {_m['name']} ({_p['team']} {_m['pos']}) to IR - {_why}; {_ret}; {_lvl}. "+("Yahoo already allows it." if _elig else f"Yahoo tags him {_m['ytag'] or 'healthy'} today, and IR takes only a player Yahoo lists as Out or IR - move him the day Yahoo flips him; until then he sits on the bench."))
            BOARD["moves"].append(dict(kind="ir",name=_m["name"],text=_t))
        else:
            _hk={id(h[1]) for h in _hurt}; _cost=[]
            for _j,_o in enumerate(MINE):
                if _o["slot"]!="BN" or id(_o) in _hk or _o["pos"] in ("K","DEF"): continue
                _rest=[x for i,x in enumerate(MINE) if i!=_j]; _cost.append((sum(my[x]-total(_rest,x) for x in WEEKS if x>=_s and x in my),_o))
            _cost.sort(key=lambda t:t[0]); _alt=(f" The cheapest other bench seat to free instead: {_cost[0][1]['name']} ({PL[_cost[0][1]['key']]['team']} {_cost[0][1]['pos']}), worth ~{_cost[0][0]:.0f} pts to the best lineup through Week {LAST}." if _cost else "")
            _hi=next(i for i,x in enumerate(MINE) if x is _m); _rh=[x for i,x in enumerate(MINE) if i!=_hi]   # Oct 12: what he is worth once back
            _hv=sum(my[x]-total(_rh,x) for x in WEEKS if _b!=99 and x>=_b and x in my)
            if _cost and _hv>_cost[0][0]+3:
                _t=(f"Hold {_m['name']} ({_p['team']} {_m['pos']}) - {_why}; {_ret}; {_lvl}. Once back he is worth ~{_hv:.0f} pts to the best lineup through Week {LAST}, more than the cheapest other bench seat, {_cost[0][1]['name']} ({PL[_cost[0][1]['key']]['team']} {_cost[0][1]['pos']}, ~{_cost[0][0]:.0f} pts). If a roster seat is needed while he is out, free that one instead. Dom's call - never an order.")
                BOARD["moves"].append(dict(kind="hold",name=_m["name"],free=_cost[0][1]["name"],text=_t))
            else:
                _t=(f"Drop candidate: {_m['name']} ({_p['team']} {_m['pos']}) - {_why}; {_ret}; {_lvl}. No IR slot is left"+(" after the move above" if any(x['kind']=='ir' for x in BOARD['moves']) else "")+", so holding him costs a roster seat while he is out."+_alt+" Dom's call - never an order.")
                BOARD["moves"].append(dict(kind="drop",name=_m["name"],text=_t))
except Exception as _e: BOARD["moves"]=[dict(kind="note",name="",text=f"Roster-move check failed: {_e}")]

# ---- Oct 17 (Dom): THE PRE-KICKOFF CHECK ----
PREKICK=[]
try:
    from zoneinfo import ZoneInfo as _ZI
    _NOWU=dt.datetime.now(dt.timezone.utc); _ET=_ZI("America/New_York"); _PT=_ZI("America/Los_Angeles")
    _KO={}
    for _r in games[games.week==NOW].itertuples():
        try:
            _k=dt.datetime.strptime(f"{_r.gameday} {_r.gametime}","%Y-%m-%d %H:%M").replace(tzinfo=_ET).astimezone(dt.timezone.utc)
            _KO[tm(_r.home_team)]=_k; _KO[tm(_r.away_team)]=_k
        except Exception: pass
    _LID={"DKI":"269381","DKII":"1519795","DKIII":"1507991","DKIV":"864215"}[LGK]
    _M=json.load(open(f"{L}/meter/meter_wk{NOW}.json")); _ML=_M["leagues"]; _ML=_ML if isinstance(_ML,list) else list(_ML.values())
    _LG=[x for x in _ML if str(x.get("league_id"))==_LID][0]
    _EL={"QB":("QB",),"RB":("RB",),"WR":("WR",),"TE":("TE",),"W/R/T":("RB","WR","TE"),"Q/W/R/T":("QB","RB","WR","TE"),"K":("K",),"DEF":("DEF",)}
    _pool=[]
    for _k,_p in PL.items():
        if _k in taken or _k[0] in WAIV or norm(_p["name"]) in SEASON_OUT or killed(_p["name"]): continue
        if NOW in byes.get(_p["team"],[]) or NOW<back(_p): continue
        _ko=_KO.get(_p["team"])
        if not _ko or _ko<=_NOWU: continue                       # no game, or his game already started
        _kd=_p["pos"] in ("K","DEF")
        _s=_SLKD.get(_kdkey(_p)) if _kd else _SLPPR.get(norm(_p["name"]))
        if _s is None: continue
        _pool.append(dict(k=_k,p=_p,sl=_s,ya=_YP.get((_ypk(_p),NOW)),go=None if _kd else _GOT.get(norm(_p["name"])),ko=_ko))
    _used=set()
    for _st in _LG["starters"]["me"]:
        _slot=_st.get("slot"); _ok=_EL.get(_slot)
        if not _ok or _st.get("gs") not in (None,"pre"): continue        # his game started: locked
        _empty=(not _st.get("player")) or (_st.get("status") or "").upper() in ("O","IR","IR-R","NA","SUSP","PUP") or ((_st.get("sleeper") or 0)<=0 and (_st.get("yahoo") or 0)<=0)
        _best=None
        for _c in _pool:
            if _c["p"]["pos"] not in _ok or _c["k"] in _used: continue
            if _empty:
                _m=_c["sl"]; _why="empty seat"
                if _m<3: continue
            else:
                _ms=_c["sl"]-(_st.get("sleeper") or 0)
                _my=None if (_c["ya"] is None or _st.get("yahoo") is None) else _c["ya"]-_st["yahoo"]
                _mg=None if (_c["go"] is None or _st.get("gotham") is None) else _c["go"]-_st["gotham"]
                if _ms<2: continue
                if _my is not None:
                    if _my<2: continue
                    _why="Sleeper and Yahoo agree"
                elif _mg is not None:
                    if _mg<2: continue
                    _why="Sleeper and Gotham agree (no Yahoo number)"
                else:
                    _why="Sleeper only (no Yahoo or Gotham number)"
                _m=_ms
            if not _best or _m>_best[0]: _best=(_m,_c,_why)
        if not _best: continue
        _m,_c,_why=_best; _used.add(_c["k"]); _p=_c["p"]
        _sko=_KO.get(tm(_st.get("team") or ""))
        _dl=min([x for x in (_c["ko"],_sko) if x] or [_c["ko"]])
        _g2=next((e for e in G2 if e["k"]==_c["k"]),None)
        _nl,_nb=newscheck(_p)
        PREKICK.append(dict(slot=_slot,starter=_st.get("player") or "(empty)",starter_team=_st.get("team"),
            starter_nums=dict(sleeper=_st.get("sleeper"),yahoo=_st.get("yahoo"),gotham=_st.get("gotham")),
            name=_p["name"].replace(" defense"," DEF"),team=_p["team"],pos=_p["pos"],
            nums=dict(sleeper=round(_c["sl"],1),yahoo=None if _c["ya"] is None else round(_c["ya"],1),gotham=None if _c["go"] is None else round(_c["go"],1)),
            gain=round(_m,1),basis=_why,empty=bool(_empty),
            color=("gold" if (_nb or _why.startswith("Sleeper only")) else "red"),
            deadline_utc=_dl.isoformat(),deadline_pt=f"{_dl.astimezone(_PT):%a} {_dl.astimezone(_PT).hour%12 or 12}:{_dl.astimezone(_PT):%M} {'AM' if _dl.astimezone(_PT).hour<12 else 'PM'} PT",
            ros_gain=round(sum(max(0.0,v) for v in _g2["g"].values()),1) if _g2 else None,
            news=_nl or "",checked=NOWPT.strftime('%a %b %d, %I:%M %p PT').replace(' 0',' ')))
    if not QUIET: print(f"Pre-kickoff check: {len(PREKICK)} upgrade(s) - " + "; ".join(f"{x['name']} over {x['starter']} (+{x['gain']}, {x['basis']}, by {x['deadline_pt']})" for x in PREKICK))
except Exception as _e: print("Pre-kickoff check skipped:",type(_e).__name__,_e)
BOARD["prekick"]=PREKICK
# Oct 21 (Dom): THE WATCH LIST - injured men waiting on a confirmed return, backups one injury from a lead job (stashes),
# and men whose workload jumped while their season level is still under the Scout's floor. Facts only - Dom's call.
BOARD["watch"]=[]
try:
    for e in G2:
        if e.get("flag","") and str(e.get("flag")).startswith("Watch") and not killed(e["p"]["name"]):
            BOARD["watch"].append(f"Watch: {e['p']['name']} ({e['p']['team']} {e['p']['pos']}) - {e['flag'].split(': ',1)[1]}")
    BOARD["watch"]=BOARD["watch"][:3]
    _tl=st.groupby("team").week.max().to_dict(); _stash=[]
    for _t,_g in st[st.position=="RB"].groupby("team"):
        _g=_g[_g.week>=_tl.get(_t,0)-2]
        _tch=(_g.carries.fillna(0)+_g.targets.fillna(0)).groupby(_g.player_display_name).sum().sort_values(ascending=False)
        if len(_tch)<2 or _tch.sum()<=0: continue
        _sn,_bn=_tch.index[0],_tch.index[1]; _ss,_bs=_tch.iloc[0]/_tch.sum(),_tch.iloc[1]/_tch.sum()
        _sk=find(_sn,_t,"RB"); _bk=find(_bn,_t,"RB")
        if not _sk or not _bk or _bk in taken or norm(_bn) in SEASON_OUT or killed(_bn): continue
        if _ss<.5 or _bs<.15 or PL[_sk]["fwd"]<12: continue
        _acq=("waivers, clears "+WAIV[_bk[0]]) if _bk[0] in WAIV else "free agent"
        _stash.append((PL[_sk]["fwd"]*_bs,f"Stash: {_bn} ({_t} RB, {_acq}) - {_bs:.0%} of the {_t} backfield's touches the last three games behind {_sn} (~{PL[_sk]['fwd']:.1f} a game, {_ss:.0%}); the lead job is his if {_sn.split()[-1]} goes down; his own level now ~{PL[_bk]['fwd']:.1f}"))
    _stash=sorted(_stash,reverse=True)[:2]; BOARD["watch"]+=[s for _,s in _stash]; _named={s.split(' (')[0].split(': ',1)[1] for s in BOARD['watch']}
    _g2k={e["k"] for e in G2}; _rise=[]
    for _k,_p in PL.items():
        if _p["pos"] not in ("RB","WR","TE") or _p["name"] in _named or _k in taken or _k in _g2k or norm(_p["name"]) in SEASON_OUT or killed(_p["name"]): continue
        _xv=_p.get("xv") or []
        if len(_xv)<3 or _p["last"]<_tl.get(_p["team"],0): continue
        _e,_l=float(np.mean(_xv[:-1])),float(_xv[-1])
        if _l>=8 and _l>=2*max(_e,1):
            _acq=("waivers, clears "+WAIV[_k[0]]) if _k[0] in WAIV else "free agent"
            _rise.append((_l-_e,f"Rising: {_p['name']} ({_p['team']} {_p['pos']}, {_acq}) - workload jumped to {_l:.1f} expected points last game from {_e:.1f} before; season level ~{_p['fwd']:.1f}, not on the Scout's pickup list yet - one more game like it and he is"))
    BOARD["watch"]+=[s for _,s in sorted(_rise,reverse=True)[:2]]
    try:   # Oct 21 (Dom): fading starters and who is taking their work
        _tw=st.groupby("team").week.apply(lambda s:sorted(set(int(x) for x in s))).to_dict()
        _ttg=st.groupby(["team","week"]).targets.sum().to_dict()
        _mine={m["key"] for m in MINE}; _fade=[]
        for _t,_wks in _tw.items():
            if len(_wks)<5: continue
            _last,_prev=_wks[-3:],_wks[:-3][-3:]
            for _pos in ("RB","WR","TE"):
                _s=st[(st.team==_t)&(st.position==_pos)]
                _snp=sn[(sn.team==_t)&(sn.position==_pos)]
                def _sh(name,wks):
                    _x=_s[(_s.player_display_name==name)&(_s.week.isin(wks))]
                    if _pos=="RB":
                        _all=_s[_s.week.isin(wks)]; _d=float((_all.carries.fillna(0)+_all.targets.fillna(0)).sum())
                        return float((_x.carries.fillna(0)+_x.targets.fillna(0)).sum())/_d if _d else 0.0
                    _d=float(sum(_ttg.get((_t,w),0) for w in wks)); return float(_x.targets.fillna(0).sum())/_d if _d else 0.0
                def _sp(name,wks):
                    _x=_snp[(_snp._nk==norm(name))&(_snp.week.isin(wks))]
                    return float(_x.offense_pct.sum())/len(wks)                       # a game he sat counts as 0 snaps (for the man taking work)
                def _played(name,wks):
                    _x=_snp[(_snp._nk==norm(name))&(_snp.week.isin(wks))&(_snp.offense_pct>0)]
                    return sorted(_x.offense_pct.tolist())
                for _nm in _s.player_display_name.unique():
                    _k=find(_nm,_t,_pos)
                    if not _k: continue
                    _p=PL[_k]
                    if _p["last"]<_wks[-1] or norm(_nm) in SEASON_OUT: continue       # he missed the last game - an injury, not a fade
                    _pl1,_pl0=_played(_nm,_last),_played(_nm,_prev)
                    if len(_pl1)<3 or len(_pl0)<2: continue                          # a fade is lost work while playing - a missed game is an injury
                    _sp0,_sp1=float(np.median(_pl0)),float(np.median(_pl1)); _sh0,_sh1=_sh(_nm,_prev),_sh(_nm,_last)
                    if _sp0<(.5 if _pos=="RB" else .6) or _sp0-_sp1<.10 or max(_pl1)>_sp0-.03 or _sh0-_sh1<.05: continue   # every one of the last three games below his old level
                    _best=None
                    for _nm2 in _s.player_display_name.unique():
                        if _nm2==_nm: continue
                        _a0,_a1=_sp(_nm2,_prev),_sp(_nm2,_last); _b0,_b1=_sh(_nm2,_prev),_sh(_nm2,_last)
                        if _a1-_a0>=.08 and _b1>_b0 and (_best is None or _b1-_b0>_best[0]): _best=(_b1-_b0,_nm2,_a0,_a1,_b0,_b1)
                    if not _best: continue
                    _d,_nm2,_a0,_a1,_b0,_b1=_best; _k2=find(_nm2,_t,_pos)
                    # a third teammate who carried real work before and missed games in the window (Monangai) - the shift is an
                    # injury fill that ends when he returns, not a starter losing his job
                    if any(_sh(_o,_prev)>=.2 and len(_played(_o,_last))<3 for _o in _s.player_display_name.unique() if _o not in (_nm,_nm2)): continue
                    _avail=bool(_k2) and _k2 not in taken and not killed(_nm2)
                    _yours=_k in _mine
                    if not (_avail or _yours): continue
                    _acq=(("waivers, clears "+WAIV[_k2[0]]) if _k2[0] in WAIV else "free agent") if _avail else ("on your roster" if _k2 in _mine else "rostered")
                    _wl="touch" if _pos=="RB" else "target"
                    _fade.append(((2 if _yours else 1)*(_sh0-_sh1+_d),
                        f"{'Your starter fading' if _yours else 'Early warning'}: {_nm} ({_t} {_pos}) snaps {_sp0:.0%} to {_sp1:.0%} (typical game), {_wl} share {_sh0:.0%} to {_sh1:.0%} the last three games; "
                        f"{_nm2} ({_acq}) is taking the work - snaps {_a0:.0%} to {_a1:.0%}, {_wl} share {_b0:.0%} to {_b1:.0%}"+(f", level now ~{PL[_k2]['fwd']:.1f}" if _k2 else "")))
        BOARD["fade"]=[s for _,s in sorted(_fade,reverse=True)[:4]]
        BOARD["watch"]+=BOARD["fade"][:3]
    except Exception as _e: print("Scout fade check skipped:",_e)
    if not QUIET: print(f"Scout watch list: {len(BOARD['watch'])} lines")
except Exception as _e: print("Scout watch list skipped:",_e)
json.dump(BOARD,open(f"{H}/scout_board_{LGK}.json","w"),indent=1)
json.dump(state,open(SF,"w"),indent=1)
REPORT="\n".join(out)
if not QUIET: print(REPORT)
pd.to_pickle(dict(PL=PL,TEAMS=TEAMS,LU=LU,OLU=OLU,my=my,opp=opp,needs=needs,G2=G2,CLOSE=CLOSE,FULL=FULL),f"{H}/scout_v2_{LGK}.pkl")

# OCT10 scout rows

# OCT10c scout open

# OCT10d scout doors qcont

# OCT10e scout prices doors

# OCT10f scout exit games

# OCT12 scout now

# OCT12 scout hold rule

# OCT13 scout empty seat

# OCT14 scout injured FAs + spikes + initials

# OCT14b this-week guard + defense this week

# OCT14c Yahoo weekly projections in the Scout

# OCT20c abbreviated roster names match

# OCT17 trade check + news check

# OCT17 defenses on waivers

# OCT17 pre-kickoff check

# OCT21a season-ending news

# OCT21b wait on injured + outside check + price the drop

# OCT21c Yahoo best weekly number

# OCT21e flag + drop on the board

# OCT21f watch list

# OCT21i fading starters

# OCT21l returners with no games this season

# OCT21n stale Oct 14 waiver rule off

# OCT21o pickup guard + rival check
