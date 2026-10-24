"""GOTHAM (engine4) — rebuilt Thu Oct 8 2026 after the original was lost with the old workspace.
Run: python3 gotham.py            (week read from the schedule: first week with unplayed games)
     python3 gotham.py 5          (force a week)
WHAT IT IS = engine3 (usage x rate x status, drift D-marker, vacated-role transfer)
  + 2025 PRIOR: last season's per-game points in each league's scoring, worth K=2 games, blended with this season's number
    (n games this season: (n*engine + 2*prior)/(n+2)). Rookies / no 2025 games: engine number alone, flagged prior=none.
  + MATCHUP FACTOR OFF (DK_NOMATCH) and RECENCY WEIGHTING OFF (DK_DECAY=1, every game counts the same).
  + QB RATE SHRINK 250 (Oct 8): a hot QB streak counts for less. Back-test Wks 2-4: QB miss 7.85 -> 7.73, all 6.10 -> 6.08.
  + NEWS WIRING (Oct 8): live ESPN+Sleeper injury status (work moves only when both agree), QB depth chart, same-absence role.
PROOF (Oct 8, Weeks 2-4, 500 player-weeks, MOST scoring, miss = avg points off per player, lower is better):
  Yahoo 5.92 | original Gotham (saved numbers) 6.02 | this rebuild 6.03 | engine3 alone 6.57 | Sleeper 5.90
  rebuild vs original Gotham numbers: correlation .981, avg distance 0.76 pts. File: backtest_oct8.csv
OUTPUT: gotham_<league>.csv (engine3 columns + eng_wk/eng_fwd re-stated with the prior, prior, n_games, week, run stamp)
"""
import os, sys, subprocess, json, datetime as dt, pandas as pd, numpy as np
sys.path.insert(0,'/home/claude/dksys/gather'); from names import norm
sys.path.insert(0,'/home/claude/src/forecast'); import fc_model as FM
HERE=os.path.dirname(os.path.abspath(__file__)); D='/home/claude/dksys/data/latest/'
K_PRIOR=2.0
def current_week():
    g=pd.read_csv(D+'games.csv'); g=g[(g.season==2026)&(g.game_type=='REG')]
    w=int(g[g.result.isna()].week.min())
    import glob as _gw   # Oct 12: hold the week until Yahoo's first read of the new one is in
    return w if (w<=1 or _gw.glob(D+f'yahoo/wk{w}/dom_matchups_*.txt')) else w-1
WEEK=int(sys.argv[1]) if len(sys.argv)>1 else current_week()
env=dict(os.environ,DK_NOMATCH='1',DK_DECAY='1',DK_KSHR_QB=os.environ.get('DK_KSHR_QB','250'))   # Oct 8: QB rate pulled harder to the position average (tested: QB miss 7.85->7.73, overall 6.10->6.08; Dom approved)
r=subprocess.run([sys.executable,os.path.join(HERE,'engine3v.py'),str(WEEK)],cwd=HERE,env=env,capture_output=True,text=True)
if r.returncode: print(r.stderr[-3000:]); raise SystemExit('GOTHAM FAILED: engine core did not run')
P=pd.read_csv(D+'stats_week_2025.csv',low_memory=False); P=P[P.season_type=='REG'].fillna(0).copy(); P['k']=P.player_display_name.fillna('').astype(str).map(norm)
S=pd.read_csv(D+'stats_week.csv',low_memory=False); S=S[(S.season_type=='REG')&(S.week<WEEK)].copy(); S['k']=S.player_display_name.fillna('').astype(str).map(norm)
NG=S.groupby('k').size()
stamp=dt.datetime.now(dt.timezone(dt.timedelta(hours=-7))).strftime('%a %b %d %Y %I:%M %p PT')
LGK={'DKI':1,'DKII':2,'DKIII':3,'DKIV':4}; summary={}
try:   # Oct 21 (Dom): jobs inherited from a man out for the season - last season's number is left out for whoever took the job
    OUTS=set(json.load(open(os.path.join(HERE,'outseason.json'))))
    _l=S.sort_values('week').groupby('k').last()
    INH={(str(_l.loc[k_].team),str(_l.loc[k_].position)) for k_ in OUTS if k_ in _l.index}
except Exception as _e: OUTS,INH=set(),set(); print('GOTHAM inherited-job check skipped:',_e)
for lab,k in LGK.items():
    E=pd.read_csv(os.path.join(HERE,f'engine3_{lab}.csv'))
    pr=P.assign(pts=FM.price(P,k)).groupby('k').pts.mean()
    E['prior']=E.k.map(pr).round(2); E['n_games']=E.k.map(NG).fillna(0).astype(int)
    def bl(v,row):
        if pd.isna(v) or pd.isna(row.prior) or bool(row.played_wk): return v
        if (row.role_add or 0)>0: return v           # his role changed this week - last season says nothing about the new one
        if (getattr(row,'era',0) or 0)>0: return v    # Oct 23: he became the starter this season - last season was a different job
        if (str(row.team),str(row.pos)) in INH and row.k not in OUTS and row.n_games>=2 and v>=1.5*row.prior: return v   # Oct 21: he inherited the job of a man out for the season
        if str(row.status).upper() in ('O','IR','PUP','OUT','NFI','SUS') or v==0: return v   # out = zero, the prior never revives him
        if str(row.status).upper()=='D':            # doubtful: blend the uncut number, then keep the engine's quarter cut
            u=v/.25; return round(.25*(row.n_games*u+K_PRIOR*row.prior)/(row.n_games+K_PRIOR),2)
        return round((row.n_games*v+K_PRIOR*row.prior)/(row.n_games+K_PRIOR),2)
    E['eng_wk_core']=E.eng_wk; E['eng_fwd_core']=E.eng_fwd
    E['eng_wk']=[bl(v,r_) for v,r_ in zip(E.eng_wk,E.itertuples())]
    E['eng_fwd']=[bl(v,r_) for v,r_ in zip(E.eng_fwd,E.itertuples())]
    E['oct12']=''
    try:   # Oct 12 (Dom): elite low-Vegas cut + practice trim, this week's number only, each on its own switch
        _g=pd.read_csv(D+'games.csv'); _g=_g[(_g.season==2026)&(_g.week==WEEK)&_g.total_line.notna()&_g.spread_line.notna()]
        _TF={'LAR':'LA','WSH':'WAS','JAC':'JAX'}; _t=lambda x:_TF.get(str(x).upper(),str(x).upper())
        _IMP={**{_t(a):(t_+s_)/2 for a,t_,s_ in zip(_g.home_team,_g.total_line,_g.spread_line)},**{_t(a):(t_-s_)/2 for a,t_,s_ in zip(_g.away_team,_g.total_line,_g.spread_line)}}
        _M=float(np.mean(list(_IMP.values()))) if _IMP else None
        _pp=S[S.position.isin(['QB','RB','WR','TE'])].groupby(['k','position']).fantasy_points_ppr.agg(['mean','size']).reset_index(); _pp=_pp[_pp['size']>=2]
        _pp['pr']=_pp.groupby('position')['mean'].rank(ascending=False,pct=True); _EL={(a,b) for a,b,c in zip(_pp.k,_pp.position,_pp.pr) if c<=.20}
        _I=pd.read_csv(D+'injuries.csv'); _I=_I[_I.week==WEEK]
        _PR={norm(str(a)) for a,b,c in zip(_I.full_name,_I.practice_status,_I.report_status) if ('Did Not' in str(b) or 'Limited' in str(b)) and str(c)=='nan'}
        _ne=_np=0
        for i_,r_ in E.iterrows():
            v=r_.eng_wk
            if pd.isna(v) or v<=0 or bool(r_.played_wk): continue
            tm=_t(r_.team); tag=[]
            if os.environ.get('DK_ELITEVEG','on')!='off' and _M and (r_.k,r_.pos) in _EL and tm in _IMP and _IMP[tm]<_M:
                v=max(0.0,v+.5*(_IMP[tm]-_M)); tag.append(f'elite low-Vegas {.5*(_IMP[tm]-_M):+.1f}'); _ne+=1
            if os.environ.get('DK_PRACTRIM','off')!='off' and r_.k in _PR:
                v=v*.95; tag.append('practice x.95'); _np+=1
            if tag: E.at[i_,'eng_wk']=round(v,2); E.at[i_,'oct12']='; '.join(tag)
        _msg=f'OCT12 {lab}: elite low-Vegas cuts {_ne} | practice trims {_np} | handoff {os.environ.get("DK_HANDOFF","0.5")} | vegas half {os.environ.get("DK_VEGHALF","on")}'
    except Exception as _e: _msg=f'OCT12 {lab}: adjustments skipped: {_e}'
    open(os.path.join(HERE,'gotham_oct12.txt'),'a' if lab!='DKI' else 'w').write(_msg+'\n')   # no print: the build reads only gotham's first two lines
    E['week']=WEEK; E['gotham_run']=stamp
    E.to_csv(os.path.join(HERE,f'gotham_{lab}.csv'),index=False)
    summary[lab]=dict(players=len(E),with_prior=int(E.prior.notna().sum()),no_prior=int(E.prior.isna().sum()),dom=int(E.own.astype(str).eq('DOM').sum()) if 'own' in E else None)
json.dump(dict(week=WEEK,run=stamp,k_prior=K_PRIOR,leagues=summary),open(os.path.join(HERE,'gotham_status.json'),'w'),indent=1)
print('GOTHAM week',WEEK,'run',stamp); print(json.dumps(summary))

# OCT12 elite vegas and practice

# OCT12 week holds gotham

# OCT13 practice trim off

# OCT21k Gotham inherited jobs
