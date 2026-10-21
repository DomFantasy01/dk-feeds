import sys
sys.path.insert(0,'/home/claude/src/role_watch');from rw_core import norm
exec(open('/home/claude/src/mkt/yweek_mine_wk3.py').read())
_MK='/home/claude/src/mkt'
def src(f):
    out={}
    for e in open(f).read().replace("\n",";").split(";"):
        a=e.split("|")
        if len(a)>=2:
            try: out[norm(a[0])]=float(a[1])
            except: pass
    return out
def ysrc(f):
    out={}
    for line in open(f):
        for e in line.strip().split(";"):
            a=e.split("|")
            if a and a[0] in("QB","RB","WR","TE","K","DEF"): a=a[1:]
            if len(a)>=4:
                try: out[norm(a[0])]=float(a[3])
                except: pass
    return out
import pandas as pd
_st=pd.read_csv('/home/claude/src/role_watch/data/stats_player_week_2026.csv',low_memory=False)
_st=_st[_st.week==3].copy();_st["key"]=_st.player_display_name.fillna("").map(norm)
def four(k,n):
    key=norm(n);fp,cb,es=[src(f"{_MK}/{s}_dk{k}.txt") for s in("fp","cbs","espn")];yf=ysrc(f"{_MK}/yahoo_dk{k}.txt")
    yw={norm(a):b for a,b in YWK[k].items()}
    v=[fp.get(key),cb.get(key),es.get(key),yw.get(key,yf.get(key))]
    r=_st[_st.key==key];act=None
    if len(r):
        r=r.iloc[0];act=float(r.fantasy_points_ppr)+(0.25*float(r.carries or 0) if k!=4 else float(r.get('passing_interceptions',0) or 0))
    return v,act
# Yahoo's own final where the live feed has it (it knows each league's exact scoring);
# a computed final only where that league's formula was checked against Yahoo (DK I and DK IV).
import json as _json
_LS=_json.load(open('/mnt/user-data/outputs/dkl_db/live/state.json'));_LS=_LS.get("data",_LS)
_LK={"MOST":1,"WINNERS":2,"HERS&HIS":3,"NEXTDOOR":4}
_YACT={(_LK[L["key"]],norm(p["name"])):p["actual"] for L in _LS["leagues"] for p in L["players"] if p.get("actual") is not None}
_MNF={"CHI","PHI"}
def fsrow(k,n,tm):
    v,a=four(k,n)
    ya=_YACT.get((k,norm(n)))
    if ya is not None: a=ya
    elif k not in (1,4): a=None
    g=[x for x in v if x is not None]
    return dict(k=k,n=n,v=v,bl=(sum(g)/len(g) if g else None),act=a,mnf=(a is None and tm in _MNF))
def FB(k,n,tm=""):
    r=fsrow(k,n,tm);return "—" if r["bl"] is None else f"{r['bl']:.1f}"
def FY(k,n):
    y=four(k,n)[0][3];return None if y is None else f"{y:.1f}"
