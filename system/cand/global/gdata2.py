import pandas as pd, math, json
ROOT="/home/claude/dksys/data/latest/"
LG={"DK I":dict(id=269381,me=2,opp=3,slots="QB WR WR RB RB TE WRT WRT K DEF"),
    "DK II":dict(id=1519795,me=7,opp=8,slots="QB WR WR WR RB RB TE WRT QWRT K DEF"),
    "DK III":dict(id=1507991,me=2,opp=1,slots="QB WR WR RB RB TE WRT WRT DEF"),
    "DK IV":dict(id=864215,me=6,opp=5,slots="QB WR WR WR RB RB TE WRT QWRT K DEF")}
ELIG={"QB":{"QB"},"WR":{"WR"},"RB":{"RB"},"TE":{"TE"},"K":{"K"},"DEF":{"DEF"},"WRT":{"WR","RB","TE"},"QWRT":{"QB","WR","RB","TE"}}
SIG={"QB":8.0,"RB":8.0,"WR":8.5,"TE":6.5,"K":4.5,"DEF":6.5}; RHO=.14
B=pd.read_csv(ROOT+"blend.csv"); ST=pd.read_csv(ROOT+"yahoo/standings.csv")
G=pd.read_csv(ROOT+"games.csv",low_memory=False); G=G[(G.season==2026)&(G.week==4)]
# ---- game windows built from this week's real kickoffs (nflverse gametime is Eastern) ----
DORD={"Thursday":0,"Friday":1,"Saturday":2,"Sunday":3,"Monday":4}
DAB={"Thursday":"THU","Friday":"FRI","Saturday":"SAT","Monday":"MON"}   # Sunday prints the time alone
MERGE=45     # kickoffs on the same day within 45 minutes are one window (Sunday 4:05 and 4:25 ET)
def _mins(t): return int(t[:2])*60+int(t[3:5])
_slots=sorted({(r.weekday,r.gametime) for r in G.itertuples()},key=lambda k:(DORD[k[0]],_mins(k[1])))
WINS=[]          # each: dict(day, et, slots)
for d,t in _slots:
    if WINS and WINS[-1]["day"]==d and _mins(t)-_mins(WINS[-1]["slots"][-1])<=MERGE: WINS[-1]["slots"].append(t)
    else: WINS.append(dict(day=d,et=t,slots=[t]))
def _pt(et):
    m=_mins(et)-180; h=(m//60)%24; mm=m%60; h12=h%12 or 12; return f"{h12}:{mm:02d}"
for w in WINS: w["pt"]=_pt(w["et"]); w["lab"]=(DAB[w["day"]]+" " if w["day"] in DAB else "")+w["pt"]
WIN=[w["lab"] for w in WINS]; NW=len(WINS)
_SLOT={(w["day"],t):i for i,w in enumerate(WINS) for t in w["slots"]}
def window(t):
    r=G[(G.away_team==t)|(G.home_team==t)]
    if r.empty: return None
    r=r.iloc[0]; return _SLOT[(r.weekday,r.gametime)]
def best(df,slots):
    pool=df.sort_values("yahoo_wk",ascending=False).to_dict("records"); used=set(); out=[]
    order=sorted(slots.split(),key=lambda s:len(ELIG[s]))
    for s in order:
        for p in pool:
            if p["player"] in used: continue
            if p["pos"] in ELIG[s] and p["status"] not in ("IR",):
                used.add(p["player"]); out.append(dict(p,slot=s)); break
    return out
def sidevar(L):
    s=[SIG.get(p["pos"],8.0) for p in L]; ss=sum(x*x for x in s); st=sum(s); return ss+RHO*(st*st-ss)
def phi(z): return .5*(1+math.erf(z/math.sqrt(2)))
B.loc[B.team=="LAR","team"]="LA"; B.loc[B.team=="WSH","team"]="WAS"
def league(lab):
    cfg=LG[lab]; d=B[B.league==lab]; st=ST[ST.league==cfg["id"]].copy()
    teams={}
    for o,g in d[~d.owner.astype(str).str.startswith(("FA","W"))].groupby("owner"):
        L=best(g,cfg["slots"]); tot=sum(p["yahoo_wk"] for p in L)
        win=[0.0]*NW; cnt=[0]*NW
        for p in L:
            w=window(p["team"]); 
            if w is None: continue
            win[w]+=p["yahoo_wk"]; cnt[w]+=1
        teams[int(o)]=dict(name=g.owner_name.iloc[0],lineup=L,tot=tot,win=win,cnt=cnt)
    return cfg,teams,st
if __name__=="__main__":
    for lab in LG:
        cfg,T,st=league(lab); me,op=T[cfg["me"]],T[cfg["opp"]]
        sd=math.sqrt(sidevar(me["lineup"])+sidevar(op["lineup"]))
        print(lab,me["name"],round(me["tot"],1),op["name"],round(op["tot"],1),"chance",round(100*phi((me["tot"]-op["tot"])/sd)),"sd",round(sd,1),me["cnt"],op["cnt"],len(T))
        print("  names not in standings:",[t["name"] for t in T.values() if t["name"] not in set(st.team)])
