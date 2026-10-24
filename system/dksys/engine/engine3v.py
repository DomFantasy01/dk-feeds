"""DK ENGINE v3 = engine2 + DRIFT (Tue Oct 6 late). Run: python3 engine3.py 5  -> engine3_<league>.csv + doors_report3.txt
DRIFT (Dom ruled Oct 6): when a man's share of team work moved >= DRIFT_SWING pts over his last 2 games vs the games before,
  and he played both, his workload is recalculated from those 2 games alone (the role he has NOW), instead of the decayed
  average that still remembers the old role. Marked D (column drift=D). Self-retiring: once the new role is old enough that
  the earlier-weeks average catches up, the swing drops under the line and D comes off. Thresholds = Claude's seeds.
Everything else unchanged from engine2 except inputs refreshed for Week 5 (see INPUTS below).
PREVIOUS HEADER:
DK ENGINE v1 (Fri Oct 2) - the engine number and the four doors, per league, per position.
Run: python3 engine.py [week]   -> engine_<league>.csv + doors_report2.txt
ENGINE NUMBER (points a game, league scoring):
  recent-weighted workload (Wks 1-3 weights .42/.65/1.0, missed weeks skipped)
  x points per workload unit, shrunk to the position mean by 40 units
  x matchup factor (points the opponent allowed to the position vs league mean, square-rooted, held .88-1.12)
  x status (O/IR/PUP = 0 this week; D x.25; Q no cut).  Vegas implied totals: NOT WIRED YET.
  WEEK = this week's opponent.  FWD = average over the next 3 played games (the forward case).
DOORS (candidates = free agents / waivers in that league):
  USAGE  last week's workload >= 1.25x his earlier average AND at least the 40th pct of rostered men at the position
  EVENT  on the transaction log with a role-moving event, or a same-team same-position man went to IR / is Out
  COVER  Dom has a starter at the position on bye or out in the next 4 weeks; candidate plays that week and beats Dom's bench cover
  MARKET outside sources' blend >= 1.3x our FWD number, 2+ sources
  ONE FACT ONE DOOR: a USAGE rise that happened in the same week as the teammate event that caused it counts once (EVENT).
FLOOR: FWD below 85% of Dom's weakest starter at the position -> no dot, unless COVER or a no-history EVENT (hollow ball).
CAP: 6 candidates per panel; Dom's men never capped. Sort: doors, then FWD margin over the floor - never raw points.
Claude's own (not measured): the thresholds 1.25x / 40th pct / 1.3x / 85% / 6, the matchup band, the red-zone weights in fc_model.
"""
import sys, csv, json, statistics as st
import numpy as np
import pandas as pd
sys.path.insert(0,'/home/claude/dksys/gather'); from names import norm
sys.path.insert(0,'/home/claude/src/forecast'); import fc_model as FM
import os
STATSF=os.environ.get('DK_STATS','/home/claude/dksys/data/latest/stats_week.csv')   # override for back-tests
FM.STATS=STATSF   # v3 INPUTS: fresh nflverse weekly stats (Wks 1-4 complete), not role_watch's Oct 2 copy
DRIFT_SWING=float(os.environ.get('DK_DRIFT','10.0')); DRIFT_HOLD=2   # v3 DRIFT seeds (Claude's): share points, games
D='/home/claude/dksys/data/latest/'
WEEK=int(sys.argv[1]) if len(sys.argv)>1 else 4
POS=('QB','RB','WR','TE'); WTS=(.42,.65,1.0); KSHR=40; DECAY=float(os.environ.get('DK_DECAY','.65'))
LG={'DK I':1,'DK II':2,'DK III':3,'DK IV':4}
TFIX={'LAR':'LA','WSH':'WAS','JAC':'JAX'}
T=lambda t: TFIX.get(str(t).upper(),str(t).upper())
# Dom's rosters as pulled Fri Oct 2 (slot S = starter, F = flex/superflex starter, B = bench, I = IR)
# v3 INPUTS: Dom's rosters as of Oct 4-6 (slot S starter, F flex/superflex, B bench, I IR)
# v4 (Oct 8): Dom's rosters and who is OUT are READ FROM the latest Yahoo roster pull - never typed in by hand.
import glob as _g
_RF=sorted(_g.glob('/home/claude/dksys/data/latest/yahoo/wk*/dom_rosters.json'),key=lambda p:int(p.split('/wk')[1].split('/')[0]))[-1]
_RJ=json.load(open(_RF)); print('ROSTERS FROM',_RF,'pulled',_RJ['pulled_pt'])
_SM=lambda sl:'I' if sl=='IR' else 'B' if sl=='BN' else 'F' if sl in ('W/R/T','Q/W/R/T') else 'S'
ROST={lab:[(p['player'],_SM(p['slot'])) for p in v['players'] if p['slot'] not in ('K','DEF')] for lab,v in _RJ['leagues'].items()}
_OUTST={'IR','IR-R','O','PUP','PUP-R','SUS','NFI','NFI-R'}
_YST={norm(p['player']):p['status'] for v in _RJ['leagues'].values() for p in v['players']}   # Yahoo's tag for Dom's men
OUTSEASON={norm(n) for n in ['De\'Von Achane']}   # season-ending, never a candidate
try:   # Oct 21 (Dom): season-ending news (ESPN injury report + single-man headlines, no question headlines) - same rule as the Scout
    import re as _re3, datetime as _dt3
    _SOR3=_re3.compile(r"(season[- ]ending|out for the (?:20\d\d )?(?:season|year)|done for the (?:season|year)|lost for the (?:season|year)|(?:end|ends|ending|ended) (?:his|their) (?:20\d\d )?season|(?:miss|missing|out for|sidelined for|over for)\b[^.]{0,30}?\b(?:rest|remainder) of the (?:20\d\d )?season)",_re3.I)
    _NEG3=_re3.compile(r"(\bnot\b|n't\b|\bavoid\w*|\bno\b|\bnon\b)[^.]{0,20}$",_re3.I)
    _nu3=_dt3.datetime.now(_dt3.timezone.utc); _F3='/home/claude/domfantasy01/dk-feeds/feeds/'
    def _so3(tx):
        for _mm in _SOR3.finditer(tx):
            if not _NEG3.search(tx[max(0,_mm.start()-25):_mm.start()]): return True
        return False
    def _fresh3(ts):
        try: w=_dt3.datetime.fromisoformat(str(ts).replace("Z","+00:00")); return w.tzinfo is not None and (_nu3-w).days<=45
        except Exception: return False
    for _x in json.load(open(_F3+'espn_injuries.json')).get('players',[]):
        if _fresh3(_x.get('date')) and _so3(str(_x.get('detail',''))): OUTSEASON.add(norm(_x.get('name','')))
    for _fn in ('rotowire_history.jsonl','espn_news_history.jsonl'):
        for _l in open(_F3+_fn):
            try: _j=json.loads(_l)
            except Exception: continue
            _t=str(_j.get('title') or '')
            if not _t or '?' in _t or _t.count(',')>=2 or not _fresh3(_j.get('published_utc')) or not _so3(_t): continue
            if _fn.startswith('rotowire') and ':' in _t: OUTSEASON.add(norm(_t.split(':')[0]))      # RotoWire headlines start "Name: ..."
    print('ENGINE3 season-ending:', len(OUTSEASON), 'men')
except Exception as _e3: print('ENGINE3 season-ending check skipped:', _e3)
try: json.dump(sorted(OUTSEASON),open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'outseason.json'),'w'))   # Oct 21: Gotham reads it (inherited jobs)
except Exception: pass
OUTNOW={norm(p['player']) for v in _RJ['leagues'].values() for p in v['players'] if p['status'] in _OUTST}   # v4: from Yahoo's own status tags
BL=pd.read_csv(D+'blend.csv'); BL['k']=BL.player.map(norm); BL['team']=BL.team.map(T)
G=pd.read_csv(D+'games.csv',low_memory=False); G=G[(G.season==2026)&(G.game_type=='REG')]
SCH={}; HOME={}   # v2: home/away per team-week; neutral sites (London) marked neutral
for _,g in G.iterrows():
    a,h=T(g.away_team),T(g.home_team); SCH.setdefault(a,{})[int(g.week)]=h; SCH.setdefault(h,{})[int(g.week)]=a
    nt=str(g.location)=='Neutral'; HOME[(a,int(g.week))]='neutral' if nt else 'away'; HOME[(h,int(g.week))]='neutral' if nt else 'home'
SW=pd.read_csv(STATSF,low_memory=False); SW=SW[(SW.season_type=='REG')&(SW.week<=WEEK)]   # v2: games already played this week (Thursday) count
ALLOW={}
for p in POS:
    d=SW[SW.position==p].groupby(['opponent_team','week']).fantasy_points_ppr.sum().groupby('opponent_team').mean()
    for t,v in d.items(): ALLOW[(T(t),p)]=v/d.mean()
DTIER={}
for p in POS:
    rk=sorted([t for (t,pp) in ALLOW if pp==p],key=lambda t:-ALLOW[(t,p)])
    for i,t in enumerate(rk): DTIER[(t,p)]='easy' if i<11 else ('hard' if i>=len(rk)-11 else None)
DGAMES={T(t):int(n) for t,n in SW.groupby('opponent_team').week.nunique().items()}
# v4 RED ZONE (measured, not guessed): every carry / target inside the 20 earns extra workload units equal to how much
# more it scores than an ordinary one, from this season's play-by-play (Weeks 1-4 Thu, ~450 red-zone carries, ~430 targets).
PBP=pd.read_csv(D+'pbp/pbp_2026.csv.gz',low_memory=False)
PBP=PBP[(PBP.season_type=='REG')&(PBP.two_point_attempt!=1)&(PBP.week<=WEEK)&(PBP.week<=int(os.environ.get('DK_MAXWK','99')))]
_ru=PBP[(PBP.play_type=='run')&PBP.rusher_player_id.notna()].copy(); _ru['rz']=_ru.yardline_100<=20
_ru['v']=.1*_ru.rushing_yards.fillna(0)+6*_ru.rush_touchdown.fillna(0)
_pa=PBP[(PBP.play_type=='pass')&PBP.receiver_player_id.notna()].copy(); _pa['rz']=_pa.yardline_100<=20
_pa['v']=_pa.complete_pass.fillna(0)+.1*_pa.receiving_yards.fillna(0)+6*_pa.pass_touchdown.fillna(0)
_cv=_ru.groupby('rz').v.mean(); _tv=_pa.groupby('rz').v.mean()
RZT=float(_tv[True]/_tv[False]-1)                                        # extra target-units per red-zone target
RZC={k:float((_cv[True]+FM.SC[k]['ra'])/(_cv[False]+FM.SC[k]['ra'])-1) for k in (1,2,3,4)}   # carry bonus leagues value an ordinary carry more
RZ=pd.concat([_ru[_ru.rz].groupby(['rusher_player_id','week']).size().rename('rzc'),
              _pa[_pa.rz].groupby(['receiver_player_id','week']).size().rename('rzt')],axis=1).fillna(0)
RZ.index.names=['player_id','week']; RZ=RZ.reset_index()
# v4 VEGAS: each team's implied points this week (spread + total). Factor = (implied / league mean implied) ^ .5, held .88-1.12,
# then blended with the matchup factor as a geometric mean - Vegas already prices the defense, so it is not stacked on top.
# CLAUDE'S OWN: the square root, the band, the 50/50 blend. Lines: data/latest/vegas/wk4_lines.json
VEG={}
# v3 INPUTS: this week's lines from nflverse games.csv (spread_line > 0 = home favored)
for _,g_ in G[(G.week==WEEK)&G.total_line.notna()&G.spread_line.notna()].iterrows():
    VEG[T(g_.home_team)]=(g_.total_line+g_.spread_line)/2; VEG[T(g_.away_team)]=(g_.total_line-g_.spread_line)/2
if not VEG: print('VEGAS NOT LOADED for week',WEEK)
VEGM=st.mean(VEG.values()) if VEG else None
def vfac(team): return None if team not in VEG else max(.88,min(1.12,(VEG[team]/VEGM)**.5))
def nextopp(team,wk,played):
    w=wk+1 if played else wk
    while w<=18 and SCH.get(team,{}).get(w) is None: w+=1
    return SCH.get(team,{}).get(w),w
def mfac(team,pos,wk):
    o=SCH.get(team,{}).get(wk)
    if o is None: return None                      # bye
    if os.environ.get('DK_NOMATCH'): return 1.0
    return max(.88,min(1.12,ALLOW.get((o,pos),1.0)**.5))
TX=list(csv.DictReader(open('/home/claude/dksys/tx/log.csv')))
OF=json.load(open('/home/claude/dksys/engine/own_fresh_oct2.json')); OFCHK={norm(n) for n in OF['_checked']}
# Oct 10 night (Dom): who owns whom = the newest Yahoo read of every team in the league, not the Oct 1 blend
_LIVE={};_WV={}
for _n,_lb in ((1,'DK I'),(2,'DK II'),(3,'DK III'),(4,'DK IV')):
    _f=f'/home/claude/dksys/scout/dk{_n}_rosters_live.txt'
    if os.path.exists(_f): _LIVE[_lb]={norm(l.split('|')[2]):l.split('|')[0] for l in open(_f) if l.strip() and not l.startswith('#') and l.count('|')>=4}
    _w=f'/home/claude/dksys/scout/dk{_n}_waivers.txt'
    if os.path.exists(_w): _WV[_lb]={norm(x.split('/')[0]) for l in open(_w) if not l.startswith('#') for x in l.strip().split('|') if x}
# this week's injury report: a man is DOWN if Out/Doubtful, or DNP for an injury (not rest)
INJ=pd.read_csv(D+'injuries.csv'); INJ=INJ[INJ.week==WEEK]
_IRS={norm(str(a)):str(b) for a,b in zip(INJ.full_name,INJ.report_status) if str(b)!='nan'}   # v4: this week's official report status
# Friday statuses cross-confirmed in session where nflverse still carries a stale midweek DNP (Fri Oct 2).
# nflverse keeps one row a week, so a Wednesday DNP can outlive a Friday full practice. Each entry needs 2+ sources.
CLEARED={}   # v3: Oct 2 clearance expired
INJ=INJ[~INJ.full_name.map(norm).isin(CLEARED)]
DOWN={}
for _,r in INJ.iterrows():
    rs=str(r.report_status); ps=str(r.practice_status); why=str(r.practice_primary_injury)
    if rs in ('Out','Doubtful') or ('Did Not Participate' in ps and 'Not injury related' not in why):
        DOWN[norm(r.full_name)]=(T(r.team),r.position,rs if rs!='nan' else 'DNP')
# v5 NEWS WIRING (Thu Oct 8, rebuilt after the original was lost): live injury status from Dom's GitHub feed job
# (ESPN injuries + Sleeper injuries, refreshed every 30 min). The official NFL report wins when it carries a designation;
# until it does (Wed/Thu), the feeds decide. Both feeds agree -> that status. They disagree -> the milder one, flagged.
# Only one feed has him -> that status, marked single-source. IR / PUP / suspended count as Out.
_FD='/home/claude/domfantasy01/dk-feeds/feeds/'
_SEV={'Out':3,'IR':3,'PUP':3,'Suspension':3,'Doubtful':2,'Questionable':1}
def _canon(x):
    x=str(x or '')
    return 'Out' if x in ('Out','IR','PUP','Suspension','Injured Reserve','O') else x if x in ('Doubtful','Questionable') else ''
_E={}; _S={}
try:
    if os.environ.get('DK_NOFEEDS'): raise RuntimeError('feeds off (back-test)')
    _EJ=json.load(open(_FD+'espn_injuries.json')); _EJ=_EJ.get('players',_EJ) if isinstance(_EJ,dict) else _EJ
    for it in (_EJ.values() if isinstance(_EJ,dict) else _EJ):
        if isinstance(it,dict) and it.get('name'): _E[norm(it['name'])]=_canon(it.get('status'))
except Exception as _e: print('ESPN injury feed not read:',_e)
try:
    if os.environ.get('DK_NOFEEDS'): raise RuntimeError('feeds off (back-test)')
    _SJ=json.load(open(_FD+'sleeper_injuries.json')); _SJ=_SJ.get('players',_SJ)
    for it in (_SJ.values() if isinstance(_SJ,dict) else _SJ):
        if isinstance(it,dict) and it.get('name'): _S[norm(it['name'])]=(_canon(it.get('inj')),T(it.get('team') or ''),it.get('pos'))
except Exception as _e: print('Sleeper injury feed not read:',_e)
FEEDST={}
for k in set(_E)|set(_S):
    e=_E.get(k,''); s_,tm_,ps_=_S.get(k,('','',''))
    if e and s_: st_=e if e==s_ else min((e,s_),key=lambda z:_SEV.get(z,0)); src='ESPN+Sleeper'+('' if e==s_ else ' DISAGREE')
    else: st_=e or s_; src='ESPN only' if e else 'Sleeper only'
    if st_: FEEDST[k]=(st_,src,tm_,ps_)
STATUS={}   # this week's status per player: official report first, then the feeds
for k,(st_,src,tm_,ps_) in FEEDST.items(): STATUS[k]=(st_,src)
for k,v in _IRS.items():
    if v in ('Out','Doubtful','Questionable'): STATUS[k]=(v,'NFL report')
try:   # Oct 11 (Dom): week-to-week = Doubtful, read from ESPN's news line
    import re as _wre, datetime as dt
    _WTW=_wre.compile(r'week-to-week|week to week|(expected to|will|could|set to|slated to) miss (about |roughly |at least |the next )?(\w+|\d+)(-to-| to |-)?(\w+|\d+)? weeks|sidelined (for )?(about |roughly |at least )?(\w+|\d+)(-to-| to |-)?(\w+|\d+)? weeks',_wre.I)
    _now=dt.datetime.now(dt.timezone.utc); _wtw=[]
    for it in (_EJ.values() if isinstance(_EJ,dict) else _EJ):
        if not isinstance(it,dict) or not it.get('name') or not _WTW.search(str(it.get('detail',''))): continue
        try: _age=(_now-dt.datetime.strptime(str(it.get('date',''))[:16],'%Y-%m-%dT%H:%M').replace(tzinfo=dt.timezone.utc)).days
        except Exception: continue
        k=norm(it['name'])
        if _age<=10 and _IRS.get(k) not in ('Out','Doubtful','Questionable') and STATUS.get(k,('',''))[0] not in ('Out','Doubtful'):
            STATUS[k]=('Doubtful','week-to-week (ESPN news)'); _wtw.append(it['name'])
    print('WEEK-TO-WEEK -> Doubtful:',len(_wtw),'|',', '.join(_wtw[:20]))
except Exception as _e: print('week-to-week rule skipped:',_e)
for k,(st_,src,tm_,ps_) in FEEDST.items():
    if st_ in ('Out','Doubtful') and STATUS[k][1]=='ESPN+Sleeper' and (k not in DOWN or DOWN[k][2]=='DNP'):   # Dom's rule: injury news moves work only when cross-confirmed
        t0,p0=(DOWN[k][0],DOWN[k][1]) if k in DOWN else (tm_,ps_)
        if t0: DOWN[k]=(t0,p0,st_)                 # a feed-confirmed absence moves his work to teammates, same as the report
print('NEWS WIRING: feed statuses',len(FEEDST),'| DOWN now',len(DOWN))
# v5 DEPTH CHART (QB): a quarterback who is not first on his team's latest depth chart, while the first is healthy, is a backup -> 0.
_DC=pd.read_csv(D+'depth_charts.csv',low_memory=False)
_DCK=os.environ.get('DK_DEPTH_BEFORE')   # back-test: the last depth snapshot taken before that week's games
_DC=_DC[_DC.dt==(_DC[_DC.dt<_DCK].dt.max() if _DCK else _DC.dt.max())]
_QB1={}
for _,r_ in _DC[_DC.pos_abb=='QB'].sort_values('pos_rank').iterrows(): _QB1.setdefault(T(r_.team),norm(r_.player_name))
_QBRANK={norm(a):(T(t),int(rk)) for a,t,rk in zip(_DC[_DC.pos_abb=='QB'].player_name,_DC[_DC.pos_abb=='QB'].team,_DC[_DC.pos_abb=='QB'].pos_rank)}
print('DEPTH CHART snapshot',_DC.dt.max(),'| QB1s',len(_QB1))
# v3 ROLE CHANGE (Sat Oct 3 late): the engine projects FORWARD. When a man who was taking work is Out (or Doubtful)
# this week, the work he leaves behind moves to the active teammates at his position, split by each man's own recent workload.
# Only work he was actually taking in his team's last game counts (an absence already baked into recent weeks is not counted twice).
# Claude's own, not measured: the transfer rates below (the rest of the vacated work goes to other positions / scheme); Doubtful vacates 75%.
# QB not handled: a backup QB has no workload history to scale.
# v4 (Sun Oct 4 ~1 a.m.): rates MEASURED on 23 real cases, Weeks 2-4 (a man taking work missed the next game; what his
# position-mates gained vs their own recent workload), then pulled toward the old guesses (.75/.60/.60) by 40 units of
# vacated work, the same shrink the engine uses on points-per-unit. Raw: RB .95 (6 cases), WR 1.15 (6), TE .13 (11, tiny volumes).
# Small sample - recalibrate weekly from role_cases. File: engine/role_cases_wk2_4.csv
VACATE={'RB':.88,'WR':.88,'TE':.37}
TSHR=1.0   # v5 thin-sample workload shrink, MEDIUM (Dom's call). Light would be .5, heavy 2.0.
FIRMOUT={n:(1.0 if v[2]=='Out' else .75) for n,v in DOWN.items() if v[2] in ('Out','Doubtful')}
for n in OUTNOW: FIRMOUT[n]=1.0
# DNP alone is a practice day, not an absence (rule table: no move without a designation) -> MONITOR, not a door
MOVE={'RETURN_WINDOW','ACTIVATED','PROMOTED','SIGNED_ACTIVE','TRADE'}
def _drop_exits(F):
    """Oct 11 (Dom): remove past games a man left hurt - under 35% of snaps when his usual (median) is 60%+; keeps at least one game"""
    if os.environ.get("DK_INJEXIT","on")=="off": return F   # Oct 13: a switch for future before/after tests (on by default)
    try: sn=pd.read_csv("/home/claude/dksys/gate/fresh/snap_counts_2026.csv",low_memory=False)
    except Exception as ex: print("INJURY-EXIT: no snap counts, nothing dropped -",ex); return F
    sn=sn[(sn.game_type=="REG")&(sn.week<WEEK)&sn.position.isin(POS)].copy(); sn["k"]=sn.player.astype(str).map(FM.norm)
    drop=set(); seen=[]
    for (k_,p_),g_ in sn.groupby(["k","position"]):
        if len(g_)<2 or g_.offense_pct.median()<.6: continue
        ex=[int(w) for w,v in zip(g_.week,g_.offense_pct) if v<.35]
        if ex and len(ex)<len(g_):
            drop.update((k_,w) for w in ex); seen.append(f"{g_.player.iloc[0]} Wk "+",".join(map(str,ex)))
    if not drop: return F
    m=[(k_,int(w)) in drop and w<WEEK for k_,w in zip(F.key,F.week)]
    if "_EXITSHOWN" not in globals(): print("INJURY-EXIT games dropped:",len(drop),"|","; ".join(sorted(seen))); globals()["_EXITSHOWN"]=1
    return F[~pd.Series(m,index=F.index)]
def run(lab):
    k=LG[lab]; F=FM.frame(k); F=F[F.week<=WEEK] if not os.environ.get('DK_BT') else F[F.week<WEEK]   # Oct 23: DK_BT (back-test) - the week being tested is never seen
    F=F.merge(RZ,on=['player_id','week'],how='left'); F[['rzc','rzt']]=F[['rzc','rzt']].fillna(0)
    rw_=FM.WT[k][1]
    F['wl']=F.wl+np.where(F.position=='RB',RZC[k]*F.rzc+rw_*RZT*F.rzt,np.where(F.position.isin(['WR','TE']),RZT*F.rzt,0))   # v4 red zone
    F['team']=F.team.map(T)
    F=_drop_exits(F)   # Oct 11 (Dom): a game he left hurt is not his level
    ser={}
    for _,r in F.iterrows(): ser.setdefault(r.key,{})[int(r.week)]=(float(r.wl),float(r.pts),r.team,r.position)
    effp={p:float(F[F.position==p].pts.sum()/max(F[F.position==p].wl.sum(),1)) for p in POS}
    # v3: recent-weighted workload for every man, then the vacated-role transfer for this week
    WL={}; LASTW={}
    for key,sk in ser.items():
        gw_=[w for w in sorted(sk) if sk[w][0]>0 and w<WEEK]
        if not gw_: continue
        wts=[DECAY**(len(gw_)-1-i) for i in range(len(gw_))]
        WL[key]=(sum(wt*sk[w][0] for wt,w in zip(wts,gw_))/sum(wts),sk[gw_[-1]][2],sk[gw_[-1]][3],gw_[-1])
    tlast={}
    for key,(_,tm,_,lw) in WL.items(): tlast[tm]=max(tlast.get(tm,0),lw)
    ROLE={}; ROLEWHY={}
    for key,frac in FIRMOUT.items():
        if key not in WL: continue
        wl_,tm,p,lw=WL[key]
        if p not in VACATE or lw<tlast.get(tm,0): continue      # not taking work in the team's last game -> already baked in
        if WEEK in SCH.get(tm,{}) and any(WEEK in ser.get(k2,{}) for k2,v2 in WL.items() if v2[1]==tm): continue   # already played this week
        mates=[k2 for k2,v2 in WL.items() if v2[1]==tm and v2[2]==p and k2!=key and k2 not in FIRMOUT]
        tot=sum(WL[k2][0] for k2 in mates)
        if not tot: continue
        for k2 in mates:
            g_=(VACATE[p] if os.environ.get('DK_HANDOFF','0.5')=='off' else min(VACATE[p],float(os.environ.get('DK_HANDOFF','0.5'))))*frac*wl_*WL[k2][0]/tot   # Oct 12 (Dom): half handoff
            ROLE[k2]=ROLE.get(k2,0)+g_; ROLEWHY.setdefault(k2,[]).append(key)
    # v6 (Oct 8) SAME-ABSENCE ROLE: when a teammate at his position is Out/Doubtful again this week and has already missed
    # games this season, the best evidence for this week is what THIS man did in the games that teammate missed
    # (Braelon Allen with Breece Hall out: 17.8 in Week 4 vs ~9 as the backup). Lifts him to that level, scaled by how sure
    # the absence is (Out 1.0, Doubtful .75). Never lowers anyone. Needs the teammate to have been a real worker (>=8 a game).
    for key,frac in (FIRMOUT.items() if not os.environ.get('DK_NOSAMEABS') else []):
        if key not in WL: continue
        wl_,tm,p,lw=WL[key]
        if p not in VACATE or wl_<8: continue
        played={w for w,v in ser.get(key,{}).items() if v[0]>0 and w<WEEK}
        tw={w for k_,sk_ in ser.items() for w,v in sk_.items() if v[2]==tm and w<WEEK}
        missed=sorted(tw-played)
        if not missed or not played or max(played)<max(tw)-1: continue   # only a FRESH absence: he played in one of his team's last two games
        for k2,(w2,t2,p2,l2) in WL.items():
            if t2!=tm or p2!=p or k2==key or k2 in FIRMOUT: continue
            sk2=ser.get(k2,{}); wm=[sk2[w][0] for w in missed if w in sk2]
            if not wm: continue
            lift=(sum(wm)/len(wm)-(w2+ROLE.get(k2,0)))*frac
            if lift>0:
                ROLE[k2]=ROLE.get(k2,0)+lift; ROLEWHY.setdefault(k2,[]).append(key+' (same absence, wks '+','.join(map(str,missed))+')')
    # v5: role norms - average workload by position and by depth rank on his team in that game (1 = team's top man at the position).
    # A man with fewer than 3 games has his workload pulled toward the norm for the depth rank he held in his latest game.
    # MEDIUM = TSHR 1.0: the norm counts as one extra game (one game on record -> halfway; two games -> about 38%).
    _G=F[F.position.isin(POS)&(F.wl>0)].copy(); _G['rk']=_G.groupby(['team','week','position']).wl.rank(ascending=False,method='first')
    _N=_G.groupby(['position','rk']).wl.mean().to_dict()
    _K=_G.sort_values('week').groupby('key').agg(pos=('position','first'),rk=('rk','last'))   # the depth rank he held in his LATEST game = his current role
    RANKN={(k_,v_.pos):_N.get((v_.pos,round(v_.rk)),None) for k_,v_ in _K.iterrows()}
    RANKN={k_:v_ for k_,v_ in RANKN.items() if v_ is not None}
    # v3 DRIFT: share of team work, last DRIFT_HOLD games vs earlier games (RB carries+targets, WR/TE targets)
    _S=F[F.position.isin(['RB','WR','TE'])&(F.week<WEEK)].copy()
    _t=_S.groupby(['team','week']).agg(tc=('carries','sum'),tt=('targets','sum')).reset_index()
    _S=_S.merge(_t,on=['team','week'])
    _S['sh']=np.where(_S.position=='RB',(_S.carries+_S.targets)/(_S.tc+_S.tt).clip(lower=1),_S.targets/_S.tt.clip(lower=1))
    DRIFT={}
    for key_,g_ in _S.groupby('key'):
        lw_=[w for w in (WEEK-2,WEEK-1)]
        late_=g_[g_.week.isin(lw_)]; early_=g_[g_.week<WEEK-DRIFT_HOLD]
        if len(late_)<DRIFT_HOLD or not len(early_): continue
        if late_.wl.min()<=0: continue
        d_=(late_.sh.mean()-early_.sh.mean())*100
        if abs(d_)>=DRIFT_SWING: DRIFT[key_]=(round(d_,1),float(late_.wl.mean()))
    # v7 NEW STARTER (Oct 23, Dom). Back-test, Weeks 4-6, all four leagues, games before each week only: fired once (Gordon Wk 5:
    # 12.3 -> 14.2, scored 14.8), changed nobody else; overall miss 5.911 -> 5.907 (DK IV). A looser first try, without the snap
    # checks, made 18-31 player-weeks worse and was thrown out. Off switch: DK_ERA=off. A backup counts as the
    # new starter - and only his games since then set his workload - when ALL of these hold:
    #  1. a teammate at his position who was a real worker (8+ a game) has missed his team's last 2+ games and is on IR/PUP
    #     (Sleeper), not just Questionable;  2. the backup has 2+ games since that teammate's last game;
    #  3b. the injured man was the lead: 50%+ of snaps in the games he played;
    #  3. his snap share jumped and stayed up: every one of those games at 45%+ of snaps, and their average at least
    #     20 points above his average before the injury.  (Ollie Gordon: 19% before Achane's ACL, then 84 / 56 / 65.)
    ERA={}
    if os.environ.get('DK_ERA','on')!='off':   # Oct 23: passed the Weeks 4-6 back-test (see the note above) - on by default
        try:
            _SJ2=json.load(open(_FD+'sleeper_injuries.json')); _SJ2=_SJ2.get('players',_SJ2)
            _SIRALL={norm(i['name']) for i in (_SJ2.values() if isinstance(_SJ2,dict) else _SJ2) if isinstance(i,dict) and i.get('name') and str(i.get('inj') or '') in ('IR','PUP')}
            _sn=pd.read_csv("/home/claude/dksys/gate/fresh/snap_counts_2026.csv",low_memory=False)
            _sn=_sn[(_sn.game_type=="REG")&(_sn.week<WEEK)]; _SNP={(FM.norm(str(a)),int(w)):float(v) for a,w,v in zip(_sn.player,_sn.week,_sn.offense_pct)}
        except Exception as _e: _SIRALL=set(); _SNP={}; print('NEW STARTER rule skipped:',_e)
        _tw={}
        for k_,sk_ in ser.items():
            for w_,v_ in sk_.items():
                if w_<WEEK: _tw.setdefault(v_[2],set()).add(w_)
        for k_,sk_ in ser.items():
            if k_ not in _SIRALL or STATUS.get(k_,('',''))[0]=='Questionable': continue
            pl_=sorted(w for w,v in sk_.items() if v[0]>0 and w<WEEK)
            if not pl_: continue
            tm_,p_=sk_[pl_[-1]][2],sk_[pl_[-1]][3]
            if p_ not in VACATE or sum(sk_[w][0] for w in pl_)/len(pl_)<8: continue
            if len([w for w in _tw.get(tm_,()) if w>pl_[-1]])<2: continue
            for k2,sk2 in ser.items():
                if k2==k_: continue
                g2=[w for w,v in sk2.items() if v[0]>0 and w<WEEK and v[2]==tm_ and v[3]==p_]
                aft=[w for w in g2 if w>pl_[-1]]; bef=[w for w in g2 if w<=pl_[-1]]
                if len(aft)<2 or not bef: continue
                if os.environ.get('DK_ERA_TOP','on')!='off':   # 4. the injured man was his team's top worker at the position (the lead back, not a backup)
                    _si=[_SNP.get((k_,w)) for w in pl_]; _si=[x for x in _si if x is not None]
                    if not _si or sum(_si)/len(_si)<.50: continue      # snaps decide the lead back, the same in every league's scoring
                sa=[_SNP.get((k2,w)) for w in aft]; sb=[_SNP.get((k2,w)) for w in bef]
                if None in sa or not [x for x in sb if x is not None]: continue
                sb=[x for x in sb if x is not None]
                if min(sa)>=.45 and sum(sa)/len(sa)>=sum(sb)/len(sb)+.20: ERA[k2]=max(ERA.get(k2,0),pl_[-1]+1)
        if ERA: print('NEW STARTER (role era):',', '.join(f'{k_} from Wk {w_}' for k_,w_ in ERA.items()))
    b=BL[(BL.league==lab)&(BL.pos.isin(POS))].copy()
    mine={norm(n):s for n,s in ROST[lab]}
    rows=[]
    for _,r in b.iterrows():
        s=ser.get(r.k,{}); wk=sorted(s)
        gw=[w for w in wk if s[w][0]>0 and w<=WEEK]
        if r.k in ERA: gw=[w for w in gw if w>=ERA[r.k]]   # v7 NEW STARTER: only the games in his current job
        pl=[(DECAY**(len(gw)-1-i),s[w][0],s[w][1]) for i,w in enumerate(gw)]   # v2: latest game 1.0, each older .65 of the next (= .42/.65/1.0 at three games)
        team=r.team
        if pl:
            opp=sum(w*x for w,x,_ in pl)/sum(w for w,_,_ in pl)
            if len(pl)<3 and (r.k,r.pos) in RANKN:          # v5 THIN-SAMPLE WORKLOAD SHRINK (Dom ruled Sun Oct 4: build it, MEDIUM)
                opp=(sum(w*x for w,x,_ in pl)+TSHR*RANKN[(r.k,r.pos)])/(sum(w for w,_,_ in pl)+TSHR)
            _K=float(os.environ.get('DK_KSHR_QB',KSHR)) if r.pos=='QB' else KSHR; eff=(sum(p for _,_,p in pl)+_K*effp[r.pos])/(sum(x for _,x,_ in pl)+_K)   # v6: QB rate shrink, tested Oct 8
        else: opp=eff=None
        opp_pre=opp; dmark=''
        if opp is not None and r.k in DRIFT and (DRIFT[r.k][1]-opp)*DRIFT[r.k][0]>0:   # v3 DRIFT: workload = last 2 games; only moves the way the role moved
            opp=DRIFT[r.k][1]; dmark='D'
        def num(wk_):
            m=mfac(team,r.pos,wk_)
            if opp is None or m is None: return None
            if wk_==WEEK and vfac(team) is not None: m=vfac(team) if (os.environ.get('DK_NOMATCH') and os.environ.get('DK_VEGHALF','on')!='off') else (m*vfac(team))**.5      # v4 Vegas; Oct 12 (Dom): matchup off -> Vegas at half strength, not a quarter
            return (opp+(ROLE.get(r.k,0) if wk_==WEEK else 0))*eff*m      # v3: vacated role counts this week only
        ewk=num(WEEK)
        if WEEK in s: ewk=s[WEEK][1]                 # v2: this week already played (Thursday) -> his actual points
        elif ewk is not None:
            if r.k in OUTNOW: ewk=0.0                  # Yahoo tags him IR/Out
            st5,src5=STATUS.get(r.k,('',''))
            if src5=='ESPN+Sleeper DISAGREE' and st5=='Out': st5='Doubtful'   # Oct 11 (Dom): one source alone saying Out now zeroes him; a real disagreement still softens
            if st5=='Out': ewk=0.0                     # v5: report or feeds say Out
            elif st5=='Doubtful' and not os.environ.get('DK_NODCUT'): ewk*=.25             # v5: the engine's standing Doubtful cut, now applied
            if r.pos=='QB' and r.k in _QBRANK and _QBRANK[r.k][1]>1 and not os.environ.get('DK_NODEPTH'):
                q1=_QB1.get(_QBRANK[r.k][0])
                if q1 and STATUS.get(q1,('',''))[0] not in ('Out','Doubtful'): ewk=0.0   # v5: backup QB behind a healthy starter
        fw=[num(w) for w in range(WEEK+1,WEEK+8) if mfac(team,r.pos,w) is not None][:3]
        fwd=st.mean(fw) if fw and None not in fw else None
        last=s[max(wk)][0] if wk else 0; early=[s[w][0] for w in wk[:-1]]
        # v2 page trend, smoothed: the last game counts .6 and the one before it .4, measured against the average of every game before the last. One bad Sunday dents the reading; a two-week slide colors it.
        gl=[s[w][0] for w in wk]
        if len(gl)>=2 and st.mean(gl[:-1])>0: tr_s=((.6*gl[-1]+.4*gl[-2])-st.mean(gl[:-1]))/st.mean(gl[:-1])
        else: tr_s=None
        dirn='?' if len(wk)<2 else ('RISING' if last>=1.15*st.mean(early) else 'FALLING' if last<=.85*st.mean(early) else 'FLAT')
        o=str(r.owner); own='MINE' if r.k in mine else ('FA' if o=='FA' else 'W' if o.startswith('W') else 'T'+o)
        fr={norm(n):v for n,v in OF[lab].items()}
        if r.k not in mine and r.k in OFCHK:          # fresher Yahoo read wins over blend's Oct 1 owner
            own=('T'+fr[r.k]) if r.k in fr else (own if own in ('FA','W') else 'FA')
        if _LIVE.get(lab) and r.k not in mine: own=('T'+_LIVE[lab][r.k]) if r.k in _LIVE[lab] else ('W' if r.k in _WV.get(lab,()) else 'FA')   # Oct 10 night: live Yahoo read wins
        rows.append(dict(player=r.player,k=r.k,pos=r.pos,team=team,own=own,slot=mine.get(r.k,''),status=(_YST.get(r.k) if r.k in _YST else {'Out':'O','Doubtful':'D','Questionable':'Q'}.get(STATUS.get(r.k,('',''))[0],'')),status_src=STATUS.get(r.k,('',''))[1],
            games=len(pl),trend=None if tr_s is None else round(tr_s,3),wseq='/'.join(f'{x:.0f}' for x in gl),played_wk=WEEK in s,wl_last=round(last,1),wl_early=round(st.mean(early),1) if early else None,dir=dirn,
            wl_pg=round(opp,1) if opp else None,ppu=round(eff,3) if eff else None,eng_wk=None if ewk is None else round(ewk,2),
            eng_fwd=None if fwd is None else round(fwd,2),blend=r.blend_ppg,nsrc=r.n_sources,pct=r.pct_rostered,
            role_add=round(ROLE.get(r.k,0),1),role_from='|'.join(ROLEWHY.get(r.k,[])),veg=VEG.get(team),
            drift=dmark,drift_swing=DRIFT[r.k][0] if dmark else None,wl_pre_drift=round(opp_pre,1) if opp_pre else None,era=ERA.get(r.k,0)))
    R=pd.DataFrame(rows)
    # thresholds from rostered men in this league
    rost=R[~R.own.isin(['FA','W'])]
    p40={p:rost[(rost.pos==p)&(rost.wl_last>0)].wl_last.quantile(.4) for p in POS}
    out=[]
    for p in POS:
        me=R[(R.own=='MINE')&(R.pos==p)]
        starters=me[me.slot.isin(['S','F'])&me.eng_fwd.notna()]
        floor=.85*starters.eng_fwd.min() if len(starters) else None
        # holes: a Dom starter at p on bye or out in WEEK..WEEK+3
        holes=[]
        for _,m in me[me.slot.isin(['S','F'])].iterrows():
            for w in range(WEEK,WEEK+4):
                if mfac(m.team,p,w) is None or (w==WEEK and m.k in OUTNOW): holes.append((w,m.player))
        benchbest={w:max([x for x in [mfac(m.team,p,w) and (m.eng_fwd or 0) for _,m in me[me.slot=='B'].iterrows()] if x] or [0]) for w,_ in holes}
        cands=R[(R.pos==p)&R.own.isin(['FA','W'])]
        for _,c in cands.iterrows():
            if c.k in OUTSEASON: continue
            doors=[]; why=[]
            ev=[t for t in TX if norm(t['player'])==c.k and t['event'] in MOVE]
            teammate=[t for t in TX if t['pos']==p and T(t['team'])==c.team and t['event']=='IR_PLACED' and norm(t['player'])!=c.k
                      and ((R.k==norm(t['player']))&(R.games>0)).any()]
            # a teammate's absence only opens work if he was TAKING work this season (Charbonnet has 0 games - his absence is the baseline)
            tmout=[n for n in OUTNOW if n!=c.k and ((R.k==n)&(R.team==c.team)&(R.pos==p)&(R.games>0)).any()]
            # teammates at his position who were taking work and are DOWN on this week's report
            tmdown=[n for n,(tt,pp,s_) in DOWN.items() if tt==c.team and pp==p and n!=c.k and ((R.k==n)&(R.games>0)).any()]
            injev=False
            if ev: doors.append('EVENT'); why.append(ev[0]['event'].lower()+' '+ev[0]['date'][5:])
            elif (teammate or tmout) and c.wl_pg and c.wl_pg>0:
                doors.append('EVENT'); why.append('teammate out: '+(teammate[0]['player'] if teammate else R[R.k==tmout[0]].player.iloc[0])); injev=True
            elif tmdown and c.wl_pg and c.wl_pg>0:
                firm=[n for n in tmdown if DOWN[n][2] in ('Out','Doubtful')]
                doors.append('EVENT' if firm else 'EVENT?'); injev=True
                why.append('teammate down this week: '+', '.join(R[R.k==n].player.iloc[0]+' '+DOWN[n][2] for n in tmdown))
            if c.dir=='RISING' and c.wl_early and c.wl_last>=1.25*c.wl_early and c.wl_last>=p40[p]:
                if injev: why.append(f'(workload {c.wl_early}->{c.wl_last} is the same injury - one fact, one door)')
                else: doors.append('USAGE'); why.append(f'workload {c.wl_early}->{c.wl_last}')
            cov=[(w,n) for w,n in holes if mfac(c.team,p,w) is not None and (c.eng_fwd or 0)>benchbest.get(w,0) and (c.eng_fwd or 0)>0]
            if cov: doors.append('COVER'); why.append('covers '+', '.join(f'Wk{w} {n}' for w,n in cov))
            if c.eng_fwd and c.blend and c.nsrc>=2 and c.blend>=1.3*c.eng_fwd: doors.append('MARKET'); why.append(f'sources {c.blend} vs engine {c.eng_fwd}')
            if not doors: continue
            real=[d for d in doors if d!='EVENT?']
            hollow=c.games==0
            above= floor is None or (c.eng_fwd is not None and c.eng_fwd>=floor)
            if not real and (not above or c.games<2): continue   # a monitor-only man needs 2+ games behind his number
            if not (above or 'COVER' in doors or (hollow and 'EVENT' in doors)): continue
            byeh=[w for w,n in cov if mfac(R[R.player==n].team.iloc[0],p,w) is None]
            tag=('BYE COVER' if byeh else 'INJURY COVER') if 'COVER' in doors else 'SEASON'
            chk=''
            if c.eng_fwd and c.blend and c.blend>0:
                q=c.eng_fwd/c.blend
                if q>=1.6: chk=f'CHECK: sources far lower ({c.blend})'
                elif q<=.6: chk=f'CHECK: sources far higher ({c.blend})'
            dur=('?' if (hollow or (injev and 'USAGE' not in doors and 'COVER' not in doors)) else f'{len({w for w,_ in cov})}WK' if doors==['COVER'] else 'ROS')
            out.append(dict(lab=lab,pos=p,player=c.player,team=c.team,own=c.own,doors='+'.join(doors),n=len(real),why='; '.join(why),
                eng_wk=c.eng_wk,eng_fwd=c.eng_fwd,floor=None if floor is None else round(floor,2),margin=None if (floor is None or c.eng_fwd is None) else round(c.eng_fwd-floor,2),
                dir=c.dir,games=c.games,wl_pg=c.wl_pg,blend=c.blend,tag=tag,dur=dur,check=chk,ball=('HOLLOW' if hollow else 'GREY')+('/GOLD-MONITOR' if 'EVENT?' in doors else '')+('/THIN' if c.games==1 else '')))
    O=pd.DataFrame(out)
    if len(O): O=O.sort_values(['pos','n','margin'],ascending=[True,False,False]).groupby('pos').head(int(os.environ.get('DK_DOORCAP','8')))
    R.to_csv(f'engine3_{lab.replace(" ","")}.csv',index=False)
    return R,O,p40
if __name__=='__main__':
    rep=open('doors_report3.txt','w')
    for lab in LG:
        R,O,p40=run(lab)
        print(f'\n===== {lab}  ({len(R)} players scored)',file=rep)
        for p in POS:
            me=R[(R.own=='MINE')&(R.pos==p)].sort_values('eng_fwd',ascending=False)
            print(f'  {p}  DOM: '+' | '.join(f"{m.player}{(' [D+' if m.drift_swing>0 else ' [D-')+str(round(m.drift_swing))+']' if m.drift else ''} {m.slot} wk{m.eng_wk} fwd{m.eng_fwd} {m.dir}" for _,m in me.iterrows()),file=rep)
            for _,o in (O[O.pos==p].iterrows() if len(O) else []):
                print(f"     + {o.player} {o.team} [{o.doors}] wk{o.eng_wk} fwd{o.eng_fwd} floor{o.floor} {o.dir} g{o.games} blend{o.blend} | {o.tag} {o.dur} {o.ball} | {o.why} {o.check}",file=rep)
    rep.close(); print(open('doors_report3.txt').read())

# OCT10d live ownership

# OCT10e doorcap

# OCT11 gotham injury exits

# OCT11 selfout and week-to-week

# OCT12 handoff and vegas

# OCT13 injury exit switch

# OCT21h Positions doors season-ending

# OCT21j engine3 writes the season-ending list
