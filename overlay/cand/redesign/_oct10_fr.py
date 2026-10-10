# Oct 10 2026 (Dom) - exec'd by fieldpos24 after the column positions are set.
# 1. Team names print with capital letters ("Raider nation" -> "Raider Nation"); names their owners typed in capitals stay.
# 2. The Scout's spyglass joins the MARKER column: on the roster man a live Scout need is about, in the need's color
#    (red = act now, gold = watch). Fixed order: cluster, Signal, D, Trend, then the spyglass. Four marks tighten the pitch.
import json as _j10, os as _o10, re as _r10
_SMALL10={"a","an","and","the","of","or","to","in","on","for","by","at","vs"}
def _tct(s):
    out=[]
    for i,w in enumerate(str(s or "").split(" ")):
        if w.isalpha() and w.islower() and not (i and w in _SMALL10): w=w[:1].upper()+w[1:]
        out.append(w)
    return " ".join(out)
SCOUTMK={}
def _n10(s): return _r10.sub(r"[^a-z ]","",str(s).lower().replace(" defense","").replace(" def","")).strip()
def scout_rows(lab):
    """{normalized name: 'red'|'gold'} for every man a live Scout need names; red wins when two needs name him"""
    f=f"/home/claude/dksys/scout/scout_board_{lab.replace(' ','')}.json"
    if not _o10.path.exists(f): return {}
    out={}
    for it in _j10.load(open(f)).get("gate1",[]):
        for n in it.get("rows") or []:
            k=_n10(n)
            if out.get(k)!="red": out[k]=it.get("mark","gold")
    return out
def _scout_for(nm):
    if not nm or not SCOUTMK: return None
    k=_n10(nm)
    if k in SCOUTMK: return SCOUTMK[k]
    for sk,v in SCOUTMK.items():                      # defenses: "Vikings" on Yahoo, "Minnesota Vikings" in the Scout
        if sk and k and (sk.endswith(" "+k) or k.endswith(" "+sk)): return v
    return None
_CURNM=[None]
_prow10=prow
def prow(c,cols,y,nm,*a,**k):
    _CURNM[0]=nm
    try: return _prow10(c,cols,y,nm,*a,**k)
    finally: _CURNM[0]=None
def markers(c,x,mid,cl=None,sg=None,tr=None,dm=None):
    """ONE MARKER column. Order is fixed: cluster, Radar signal, D, Trend (D replaces Trend), then the Scout's spyglass."""
    if dm is not None and DREPLACE: tr=None
    sc=_scout_for(_CURNM[0])
    n=sum(1 for v in (cl,sg,dm,tr,sc) if v is not None and v is not False and v!="")
    P=MK_P if n<=3 else 13.5
    i=0
    if cl: tight(c,x+i*P,mid,MK_S,cl,True);i+=1
    if sg: sig7(c,x+i*P,mid-.26*11,11,sg[0],sg[1]);i+=1
    if dm is not None: dmark(c,x+i*P,mid,MK_S,dm);i+=1
    if tr: trend(c,x+i*P,mid,MK_S*.95,tr);i+=1
    if sc: scout_icon(c,x+i*P,mid,sc,9.5);i+=1
