# FIELD REPORT v17 data — Week 4, built Sat Oct 3 UTC (Fri Oct 2 PT).
# Rosters: Dom's live Yahoo rosters pulled Fri Oct 2.  Opponents: blend owner snapshot Thu Oct 1 (not re-pulled).
# Week number per man = mean of the Yahoo / Rotowire / ESPN week-4 projections in blend.csv (Thu Oct 1) —
#   or his actual Thursday score from the engine when his team played (PIT, CLE).  NEXT 3 = engine forward number.
# ACTUAL AVERAGE = his own games, Weeks 1–4, scored in the league's settings off nflverse stats (no 40+ bonuses).
import sys, pandas as pd, math
sys.path.insert(0,"/home/claude/dksys/gather"); from names import norm
DL_="/home/claude/dksys/data/latest/"
BL=pd.read_csv(DL_+"blend.csv"); BL.loc[BL.team=="LAR","team"]="LA"; BL.loc[BL.team=="WSH","team"]="WAS"
BL["k"]=BL.player.map(norm)
EN={lab:pd.read_csv(f"/home/claude/dksys/engine/engine2_{lab.replace(' ','')}.csv") for lab in ("DK I","DK II","DK III","DK IV")}
for e in EN.values(): e["k"]=e.player.map(norm)
SW=pd.read_csv(DL_+"stats_week.csv",low_memory=False); SW=SW[(SW.season==2026)&(SW.week<=4)&(SW.season_type=="REG")]
SW["k"]=SW.player_display_name.fillna("").astype(str).map(norm)
DEFN={"Vikings":"MIN DEF","Bills":"BUF DEF","Steelers":"PIT DEF","Chiefs":"KC DEF","Seahawks":"SEA DEF"}
def _sc(r,lab):
    intp=-1 if lab=="DK IV" else -2; car=0 if lab=="DK IV" else .25
    f=lambda x: 0 if pd.isna(x) else x
    return (f(r.passing_yards)/25+6*f(r.passing_tds)+intp*f(r.passing_interceptions)+f(r.rushing_yards)/10+6*f(r.rushing_tds)
            +car*f(r.carries)+f(r.receptions)+f(r.receiving_yards)/10+6*f(r.receiving_tds)
            -2*(f(r.rushing_fumbles_lost)+f(r.receiving_fumbles_lost)+f(r.sack_fumbles_lost))
            +2*(f(r.passing_2pt_conversions)+f(r.rushing_2pt_conversions)+f(r.receiving_2pt_conversions)))
def actavg17(nm,lab):
    if nm in DEFN or _pos17(nm,lab) in ("K","DEF"): return None
    g=SW[SW.k==norm(nm)]
    if g.empty: return None
    return f"{sum(_sc(r,lab) for r in g.itertuples())/len(g):.1f}"
def _pos17(nm,lab):
    b=_brow(nm,lab);return None if b is None else b.pos
def _brow(nm,lab):
    b=BL[(BL.league==lab)&(BL.k==norm(DEFN.get(nm,nm)))]
    return None if b.empty else b.iloc[0]
def wk17(nm,lab):
    """(week number as string, banked?)"""
    e=EN[lab];m=e[e.k==norm(nm)]
    if len(m) and bool(m.played_wk.iloc[0]): return f"{float(m.eng_wk.iloc[0]):.1f}",True
    b=_brow(nm,lab)
    if b is None: return None,False
    v=[x for x in (b.yahoo_wk,b.roto_wk,b.espn_wk) if not pd.isna(x)]
    return (f"{sum(v)/len(v):.1f}" if v else None),False
def yah17(nm,lab):
    b=_brow(nm,lab); 
    if b is None or pd.isna(b.yahoo_wk) or b.yahoo_wk==0: return None
    return float(b.yahoo_wk)
def fwd17(nm,lab):
    e=EN[lab];m=e[e.k==norm(nm)]
    return None if m.empty or pd.isna(m.eng_fwd.iloc[0]) else f"{float(m.eng_fwd.iloc[0]):.1f}"
def dir17(nm,lab):
    e=EN[lab];m=e[e.k==norm(nm)]
    if m.empty: return None
    return {"RISING":1,"FALLING":-1}.get(str(m.dir.iloc[0]))
TEAM17={}
def team_of(nm,lab):
    b=_brow(nm,lab)
    if b is not None: return b.team
    return {"Vikings":"MIN","Bills":"BUF","Steelers":"PIT","Chiefs":"KC","Seahawks":"SEA"}.get(nm)
# ---- Dom's rosters, Yahoo read Sat Oct 3 ~17:45 UTC: (slot, name, pos, status). Bateman added (DK II), Shakir gone (DK IV, swapped Fri for Washington).
ROS17={
 "DK I":dict(S=[("QB","Tyler Shough","QB",""),("WR","George Pickens","WR",""),("WR","Stefon Diggs","WR",""),
                ("RB","Jaylen Warren","RB",""),("RB","Christian McCaffrey","RB",""),("TE","Travis Kelce","TE",""),
                ("FLX","Drake London","WR",""),("FLX","Alvin Kamara","RB",""),("K","Chris Boswell","K",""),("DEF","Vikings","DEF","")],
             B=[("BN","TreVeyon Henderson","RB",""),("BN","Kaelon Black","RB",""),("BN","Dontayvion Wicks","WR",""),
                ("BN","Jayden Daniels","QB","O"),("BN","Kenyon Sadiq","TE","")],
             I=[("IR","Travis Etienne Jr.","RB","IR")],slots="QB WR WR RB RB TE WRT WRT K DEF",me=2,opp=3),
 "DK II":dict(S=[("QB","Sam Darnold","QB",""),("WR","Ja'Marr Chase","WR",""),("WR","Drake London","WR",""),("WR","Courtland Sutton","WR",""),
                 ("RB","David Montgomery","RB",""),("RB","Alvin Kamara","RB",""),("TE","Travis Kelce","TE",""),
                 ("FLX","Braelon Allen","RB",""),("SFLX","Jacoby Brissett","QB",""),("K","Harrison Mevis","K",""),("DEF","Bills","DEF","")],
              B=[("BN","MarShawn Lloyd","RB",""),("BN","Mark Andrews","TE",""),("BN","Aaron Rodgers","QB",""),("BN","Tre' Harris","WR",""),("BN","Rashod Bateman","WR","")],
              I=[("IR","Jayden Daniels","QB","O"),("IR","Travis Etienne Jr.","RB","IR")],slots="QB WR WR WR RB RB TE WRT QWRT K DEF",me=7,opp=8),
 "DK III":dict(S=[("QB","Tyler Shough","QB",""),("WR","George Pickens","WR",""),("WR","Jaylen Waddle","WR",""),
                  ("RB","David Montgomery","RB",""),("RB","George Holani","RB",""),("TE","Harold Fannin Jr.","TE",""),
                  ("FLX","Josh Downs","WR",""),("FLX","Devaughn Vele","WR",""),("DEF","Steelers","DEF","")],
               B=[("BN","Rachaad White","RB","O"),("BN","Michael Pittman Jr.","WR",""),("BN","Aaron Rodgers","QB",""),
                  ("BN","T.J. Hockenson","TE",""),("BN","Chiefs","DEF","")],
               I=[("IR","Jayden Daniels","QB","O")],slots="QB WR WR RB RB TE WRT WRT DEF",me=2,opp=1),
 "DK IV":dict(S=[("QB","Jared Goff","QB",""),("WR","Josh Downs","WR",""),("WR","Wan'Dale Robinson","WR",""),("WR","Malik Washington","WR",""),
                 ("RB","Bijan Robinson","RB",""),("RB","D'Andre Swift","RB",""),("TE","Travis Kelce","TE",""),
                 ("FLX","Zay Flowers","WR","Q"),("SFLX","C.J. Stroud","QB",""),("K","Tyler Loop","K",""),("DEF","Seahawks","DEF","")],
              B=[("BN","Terry McLaurin","WR","D"),("BN","Justin Jefferson","WR","O"),("BN","Dak Prescott","QB",""),
                 ("BN","Tucker Kraft","TE",""),("BN","RJ Harvey","RB","")],
              I=[("IR","James Conner","RB","IR"),("IR","Isiah Pacheco","RB","IR"),("IR","Tank Dell","WR","IR")],
              slots="QB WR WR WR RB RB TE WRT QWRT K DEF",me=6,opp=5)}
ELIG17={"QB":{"QB"},"WR":{"WR"},"RB":{"RB"},"TE":{"TE"},"K":{"K"},"DEF":{"DEF"},"WRT":{"WR","RB","TE"},"QWRT":{"QB","WR","RB","TE"}}
SMAP={"WRT":"FLX","QWRT":"SFLX"}
def opp_lineup(lab):
    """opponent's best lineup on the same week number, from the Thu Oct 1 owner snapshot; outs and IR skipped"""
    R=ROS17[lab];d=BL[(BL.league==lab)&(BL.owner.astype(str)==str(R["opp"]))]
    pool=[]
    for r in d.itertuples():
        if str(r.status) in ("O","D","IR","IR-R","PUP-R","NA"): continue
        v,f=wk17(r.player,lab)
        if v is None or float(v)==0: continue
        pool.append((float(v),r.player,r.pos,f))
    pool.sort(reverse=True);used=set();out={}
    for s in sorted(R["slots"].split(),key=lambda s:len(ELIG17[s])):
        for v,nm,pos,f in pool:
            if nm in used or pos not in ELIG17[s]: continue
            used.add(nm);out.setdefault(SMAP.get(s,s),[]).append((nm,v,f));break
    return out
def rows17(lab):
    R=ROS17[lab];O=opp_lineup(lab);S=[];tot=[0,0]
    for sl,nm,pos,st in R["S"]:
        v,f=wk17(nm,lab);on,ov,of=O[sl].pop(0) if O.get(sl) else (None,None,False)
        S.append((sl,nm,st,pos,team_of(nm,lab),None,None,None,v,(on.replace(" DEF"," D") if on.endswith(" DEF") else short(on)) if on else "—",f"{ov:.1f}" if ov is not None else None,f,of))
    Bn=[(sl,nm,st,pos,team_of(nm,lab),None,None,None,wk17(nm,lab)[0] if st not in ("O","IR") else None,wk17(nm,lab)[1] and st not in ("O","IR")) for sl,nm,pos,st in R["B"]]
    Ir=[(sl,nm,st,pos,team_of(nm,lab),None,None,None,None) for sl,nm,pos,st in R["I"]]
    return S,Bn,Ir
