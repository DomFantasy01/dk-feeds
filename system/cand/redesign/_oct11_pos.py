# Oct 10 night (Dom) - exec'd by _fr_positions18 (the Positions page), after its helpers are defined.
# 1. Every ball carries the man's full name - first and last, the same for everyone. No bare "Sutton", no lone "Harrison".
# 2. The Scout's picks for this position are plotted too (their plate says SCOUT PICK), so the men the Scout recommends
#    and the men the chart's doors find sit on the same axes. The Scout, in turn, prices every man the doors find.
# 3. Plates say in words why a man is here and for how long - no glyph to decode, no "BYE ROS" that reads like "buy".
import json as _j11, os as _o11
def _fullnm(n):
    return str(n).replace(" defense"," DEF")
_DW11={"USAGE":"USAGE UP","EVENT":"ROLE OPENED","EVENT?":"ROLE MAY OPEN","MARKET":"MARKET UP"}
_TW11={"BYE COVER":"BYE FILL","INJURY COVER":"INJURY FILL"}
def _dur11(d):
    d=str(d)
    if d=="ROS": return "ALL SEASON"
    if d=="?": return "HOW LONG UNCLEAR"
    if d.endswith("WK"): n=d[:-2]; return n+(" WEEK" if n=="1" else " WEEKS")
    return d
def _badge(o):
    """the plate's last words: why he is here (the strongest door), what he is for, how long - all in words"""
    if str(o.doors)=="SCOUT": return "SCOUT PICK"
    ds=[d for d in str(o.doors).split("+") if d in _DW11]
    parts=([_DW11[ds[0]]] if ds else [])+[x for x in (_TW11.get(o.tag,""),_dur11(o.dur)) if x]
    return " · ".join(parts)
def _scout_names(lab):
    f=f"/home/claude/dksys/scout/scout_board_{lab.replace(' ','')}.json"
    if not _o11.path.exists(f): return {}
    B=_j11.load(open(f)); out={}
    for it in B.get("gate1",[]):
        for p in it.get("picks",[]): out.setdefault(p["name"],p)
    for it in B.get("gate2",[]): out.setdefault(it["pick"]["name"],it["pick"])
    for q in B.get("qcont",[]):                         # a contingency fill only when the starter's absence really costs
        if q.get("loss",0)<3: continue
        for p in q.get("fills",[]):
            if p.get("now",0)>=3: out.setdefault(p["name"],p)
    return out
import re as _r11
def _nk11(n): return _r11.sub(r"[^a-z]","",_r11.sub(r"\b(jr|sr|ii|iii|iv|v)\b","",str(n).lower()))
def _priced(lab):
    f=f"/home/claude/dksys/scout/scout_board_{lab.replace(' ','')}.json"
    return (_j11.load(open(f)).get("priced") or {}) if _o11.path.exists(f) else {}
def _with_scout(Op,R,pos,lab):
    """the doors' candidates plus the Scout's picks at this position (at most three more, by points added)"""
    have={_norm(x) for x in (Op.player if len(Op) else [])}; add=[]
    for nm,p in _scout_names(lab).items():
        k=_norm(nm)
        if k in have: continue
        m=R[(R.k==k)&(R.pos==pos)&R.own.isin(["FA","W"])&R.eng_fwd.notna()&R.wl_pg.notna()]
        if not len(m): continue
        r=m.iloc[0]
        add.append(dict(player=r.player,team=r.team,pos=pos,own=r.own,doors="SCOUT",n=0,eng_fwd=r.eng_fwd,wl_pg=r.wl_pg,dir=r.dir,
                        games=r.games,why=f"Scout pick — adds ~{p.get('gain',0):.0f} pts through Wk 17" if p.get("gain") is not None else "Scout pick",
                        check=False,tag="",dur="",ball="GREY",blend=r.blend if "blend" in m.columns else None,_g=p.get("gain") or 0))
    add=sorted(add,key=lambda d:-d["_g"])[:3]
    if len(Op):                                                    # seven free agents a panel at most: the Scout's picks first,
        pr=_priced(lab)                                            # then the doors men by the points the Scout says they add
        Op=Op.assign(_pg=[pr.get(_nk11(x),{}).get("gain",-1) for x in Op.player]).sort_values("_pg",ascending=False,kind="stable").drop(columns=["_pg"])
        Op=Op.head(max(0,_PANEL_MAX-len(add)))
    if not add: return Op
    A=_pd15.DataFrame(add).drop(columns=["_g"])
    return _pd15.concat([Op,A],ignore_index=True) if len(Op) else A
_PANEL_MAX=7
def _chart_rows(lab):
    """the free agents the Positions chart actually draws for this league (doors men only, not the Scout's own picks)"""
    R_,O_,_=_E10.run(lab); out=[]
    for pos in ("QB","RB","WR","TE"):
        Op=_with_scout(O_[O_.pos==pos] if len(O_) else O_,R_,pos,lab)
        if len(Op): out+=[o for o in Op.itertuples() if str(o.doors)!="SCOUT"]
    return out
