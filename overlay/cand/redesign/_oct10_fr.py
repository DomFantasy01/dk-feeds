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
# ---- Oct 10, second pass (Dom): marks a size smaller so up to four fit the MARKER column without touching SLOT
MK_S=9.6; MK_P=13.0
def markers(c,x,mid,cl=None,sg=None,tr=None,dm=None):
    """ONE MARKER column, fixed order: cluster, Radar signal, D, Trend (D replaces Trend), the Scout's spyglass."""
    if dm is not None and DREPLACE: tr=None
    sc=_scout_for(_CURNM[0])
    n=sum(1 for v in (cl,sg,dm,tr,sc) if v is not None and v is not False and v!="")
    P=MK_P if n<=3 else 11.0
    x=x-2; i=0
    if cl: tight(c,x+i*P,mid,MK_S,cl,True);i+=1
    if sg: sig7(c,x+i*P,mid-.26*9,9,sg[0],sg[1]);i+=1
    if dm is not None: dmark(c,x+i*P,mid,MK_S,dm);i+=1
    if tr: trend(c,x+i*P,mid,MK_S*.95,tr);i+=1
    if sc: scout_icon(c,x+i*P,mid,sc,7.6);i+=1
# ---- every roster slot prints; an empty one says OPEN in red (bench, IR or a starting slot)
_CAPS={"DK I":(5,1),"DK II":(5,2),"DK III":(5,1),"DK IV":(5,3)}           # bench, IR - from each league's Yahoo settings, Oct 10
def open_counts(lab):
    L=MTR["leagues"][lab]; b=L.get("bench",[])
    bn=sum(1 for p in b if p.get("slot")=="BN"); ir=sum(1 for p in b if p.get("slot")=="IR")
    st=sum(1 for p in L["starters"]["me"] if not p.get("player"))
    cb,ci=_CAPS.get(lab,(bn,ir)); return dict(start=st,bench=max(0,cb-bn),ir=max(0,ci-ir))
def open_rows(lab,Bn,Ir):
    o=open_counts(lab)
    Bn=list(Bn)+[("BN",None,"","","",None,None,None,None,False)]*o["bench"]
    Ir=list(Ir)+[("IR",None,"","","",None,None,None,None)]*o["ir"]
    return Bn,Ir,o
def _open_note(lab):
    o=open_counts(lab); p=[]
    if o["start"]: p.append(f'{o["start"]} starting slot{"s" if o["start"]>1 else ""} empty')
    if o["bench"]: p.append(f'{o["bench"]} bench seat{"s" if o["bench"]>1 else ""} open')
    if o["ir"]: p.append(f'{o["ir"]} IR slot{"s" if o["ir"]>1 else ""} open')
    return ("OPEN: "+", ".join(p)+" — see the Scout. ") if p else ""
def _irsub(lab,Ir):
    cap=_CAPS.get(lab,(0,len(Ir)))[1]; o=open_counts(lab)["ir"]
    w={1:"One slot",2:"Two slots",3:"Three slots"}.get(cap,f"{cap} slots")
    return f"{w} in this league"+(f"  ·  {o} open" if o else "  ·  all full")
def prow(c,cols,y,nm,*a,**k):
    _CURNM[0]=nm
    try:
        if nm is None:                                    # an empty slot: say so, in red, where the name would be
            tx,cn=cols[0],cols[1]; sz=a[6] if len(a)>6 else k.get("sz",7.4)
            txt(c,cn,y,"OPEN","PopB",sz,H("#B32020")); txt(c,cn+c.stringWidth("OPEN  ","PopB",sz),y,"nobody in this slot","Pop",sz*.9,GR)
            return
        return _prow10(c,cols,y,nm,*a,**k)
    finally: _CURNM[0]=None
# ---- Positions page notes: never spill into the chart below (four lines at most per panel, a size smaller)
_INOTE_N=[0]
def inote15(x,y,w,lab,s,sz=5.3,lead=6.8):
    if lab=="Floor": _INOTE_N[0]=0
    s=s.replace("your weakest starter","the weakest starter").replace(";;",";")
    txt(c,x,y,lab+":","PopB",sz,GR);ix=x+c.stringWidth(lab+":  ","PopB",sz);line="";lines=[]
    for wd in s.split():
        t_=(line+" "+wd).strip()
        if c.stringWidth(t_,"Pop",sz)>w-(ix-x): lines.append(line);line=wd
        else: line=t_
    if line: lines.append(line)
    room=max(1,4-_INOTE_N[0]); keep=lines[:room]
    if len(lines)>room: keep[-1]=keep[-1].rstrip(" ,;")+"…"
    for l_ in keep: txt(c,ix,y,l_,"Pop",sz,GR);y-=lead
    _INOTE_N[0]+=len(keep); return y-1.0
class _OpenSched(dict):                                   # an OPEN row has no NFL team: its season cells print a quiet dash
    def get(self,k,d=None): return "—"
SCH[""]=_OpenSched()
_byes_note0=byes_note
def byes_note(men): return _byes_note0([m for m in men if m[1]])   # an OPEN row has no bye to report
def band_groups(men,key):                                 # every table bands the same way: plain alternating rows
    return [i%2==0 for i in range(len(men))]
LG["III"]=H("#7B5CE0")                                    # DK III wears the same purple as on the Overview, on every page
# ---- Oct 10 night (Dom): the spyglass keeps the Radar's convention everywhere it appears - the glass, and under it the
# splat on its first day or the zero-padded day count after (the same count the Scout page prints for that need).
def scout_rows(lab):
    """{normalized name: (color, age, gap)} for every man a live Scout need names; red wins, then the longest-running"""
    f=f"/home/claude/dksys/scout/scout_board_{lab.replace(' ','')}.json"
    if not _o10.path.exists(f): return {}
    out={}
    for it in _j10.load(open(f)).get("gate1",[]):
        v=(it.get("mark","gold"),int(it.get("age") or 0),it.get("gap"))
        for n in it.get("rows") or []:
            k=_n10(n); o=out.get(k)
            if o is None or (v[0]=="red" and o[0]!="red") or (v[0]==o[0] and v[1]>o[1]): out[k]=v
    return out
def markers(c,x,mid,cl=None,sg=None,tr=None,dm=None):
    """ONE MARKER column, fixed order: cluster, Radar signal, D, Trend (D replaces Trend), the Scout's spyglass."""
    if dm is not None and DREPLACE: tr=None
    sc=_scout_for(_CURNM[0])
    n=sum(1 for v in (cl,sg,dm,tr,sc) if v is not None and v is not False and v!="")
    P=MK_P if n<=3 else 11.0
    x=x-2; i=0
    if cl: tight(c,x+i*P,mid,MK_S,cl,True);i+=1
    if sg: sig7(c,x+i*P,mid-.26*9,9,sg[0],sg[1]);i+=1
    if dm is not None: dmark(c,x+i*P,mid,MK_S,dm);i+=1
    if tr: trend(c,x+i*P,mid,MK_S*.95,tr);i+=1
    if sc:
        col,age,gap=sc if isinstance(sc,tuple) else (sc,0,None)
        scout_mark(c,x+i*P,mid+2.3,col,age,6.6);i+=1        # glass above, splat or day count under it - the Radar's way
# ---- Oct 10 night (Dom): a banked score says FINAL in words, like every other label on the page - never a lone "F"
def fdec(c,xd,y,v,fin=False,font="PopB",sz=7.4,col=INKN):
    """bare number on its decimal; a banked score gets the soft wash and the word FINAL, small, right behind it"""
    if fin and v not in (None,""):
        c.setFillColor(alpha(SUN[1],.22));c.roundRect(xd-17,y-3,36,10.5,2.5,stroke=0,fill=1)
    dec(c,xd,y,v,font,sz,col,5.4,"")
    if fin and v not in (None,""):
        b=str(v).split(".")[1] if "." in str(v) else ""
        txt(c,xd+c.stringWidth("."+b,font,sz)+1.2,y+.6,"FINAL","PopB",3.6,INKN)
# ---- Oct 10 late (Dom): no lone abbreviations in the column furniture - STA reads TAG (Yahoo's injury tag), the
# opponent's number column reads THEIR MAN, and the slot chip says FLEX / S-FLEX (the chip's type shrinks to fit).
_hdr10=hdr
_HDRW={"STA":"TAG"}
def hdr(c,x,y,s,align="l"): return _hdr10(c,x,y,_HDRW.get(s,s),align)
def slotchip(c,x,y,s):
    w=c.stringWidth("SFLX","PopB",5.8)+8; sz=min(5.8,5.8*(w-3)/max(1,c.stringWidth(s,"PopB",5.8)))
    c.setFillColor(alpha(LG["I"],.16));c.roundRect(x,y-2.6,w,9.4,2.5,stroke=0,fill=1)
    txt(c,x+w/2,y+(5.8-sz)*.35,s,"PopB",sz,H("#1B4F9C"),"c")
