# v23: the Positions page runs on Gotham - engine core rows, with Gotham's this-week and next-three numbers laid over them
import pandas as _p23
_E10_run0=_E10.run
def _gotham_run(lab):
    R,O,p40=_E10_run0(lab)
    gf=f"/home/claude/dksys/engine/gotham_{lab.replace(' ','')}.csv"
    if _o23.path.exists(gf):
        Gd=_p23.read_csv(gf); mw=dict(zip(Gd.k.astype(str),Gd.eng_wk)); mf=dict(zip(Gd.k.astype(str),Gd.eng_fwd))
        R=R.copy(); R["eng_wk"]=[mw.get(k,v) for k,v in zip(R.k,R.eng_wk)]; R["eng_fwd"]=[mf.get(k,v) for k,v in zip(R.k,R.eng_fwd)]
    own=R.own.astype(str); ros=R[~own.isin(["FA","W","nan",""])]
    ROSTN[lab]={p:int((ros.pos==p).sum()) for p in ("QB","RB","WR","TE")}          # rostered league-wide, from the same read
    return R,O,p40
_E10.run=_gotham_run
_gs23=MTR["sources"].get("gotham",{}).get("pulled_pt","?"); _ss23=MTR["sources"].get("sleeper_skill",{}).get("pulled_pt","?")
PSTAMP=[("GOTHAM "+(" ".join(_gs23.split()[:3]+_gs23.split()[-3:-1])).upper(),"PopB",H("#8C8576"))]
CALLS={}
# v23b: the engine's "blend" column was the Oct 3 multi-source file - stale. Sleeper's current projection takes its place,
# priced in each league's scoring, so the Positions checks compare Gotham against a live outside read.
import sys as _sy23, json as _js23
_sy23.path.insert(0,'/home/claude/src/forecast'); import fc_model as _FM23
_SKF23=sorted(_g23.glob(f"/home/claude/domfantasy01/dk-feeds/feeds/proj/sleeper/wk{WEEKN}_*.csv"))[-1]
_SKD23=_p23.read_csv(_SKF23).fillna(0); _SKD23.columns=[c_.lower() for c_ in _SKD23.columns]; _SKD23["k"]=_SKD23.name.astype(str).map(norm)
def _slp23(lab):
    sc=_FM23.SC[{"DK I":1,"DK II":2,"DK III":3,"DK IV":4}[lab]]; d=_SKD23
    v=(.04*d.pass_yd+sc['ptd']*d.pass_td+sc['it']*d.pass_int+.1*d.rush_yd+6*d.rush_td+sc['ra']*d.rush_att+d.rec+.1*d.rec_yd+6*d.rec_td-2*d.fum_lost)
    return dict(zip(d.k,v.round(2)))
_gotham_run0=_E10.run
def _gotham_run2(lab):
    R,O,p40=_gotham_run0(lab); S_=_slp23(lab)
    R=R.copy(); R["blend"]=[S_.get(k) for k in R.k]; R["nsrc"]=[1 if S_.get(k) is not None else 0 for k in R.k]
    return R,O,p40
_E10.run=_gotham_run2
# v23c: door notes written inside the engine still quote the stale Oct 3 blend ("sources 6.78 vs engine 5.06") - strip those
import re as _re23
_SRCRX=_re23.compile(r";?\s*(CHECK: )?sources (far lower )?\(?[\d.]+\)?( vs engine [\d.]+)?")
def _clean23(x): return _SRCRX.sub("",x).strip("; ").replace("engine","Gotham") if isinstance(x,str) else x
_gotham_run1=_E10.run
def _gotham_run3(lab):
    R,O,p40=_gotham_run1(lab)
    for col in R.columns:
        if not _p23.api.types.is_numeric_dtype(R[col]) and not _p23.api.types.is_bool_dtype(R[col]): R[col]=R[col].map(_clean23)
    try:
        for col in O.columns:
            if not _p23.api.types.is_numeric_dtype(O[col]) and not _p23.api.types.is_bool_dtype(O[col]): O[col]=O[col].map(_clean23)
    except AttributeError: pass
    return R,O,p40
_E10.run=_gotham_run3
