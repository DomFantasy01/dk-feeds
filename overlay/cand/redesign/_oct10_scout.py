# Oct 10 2026 (Dom) - exec'd by _scout_page.py.
# 1. Every pick says what it is worth: points added to the best lineup, Week 5 through Week 17, playoffs included.
# 2. An open seat leads the page: how many seats are free (no drop needed) and the best uses of them, ranked by points added.
def _gain(p):
    g=p.get("gain")
    if g is None: return ""
    return f'  ·  <font name="PopB">Adds ~{g:.0f} pts through Wk 17</font>'+(f' ({p["pgain"]:.0f} in the playoffs)' if p.get("pgain") else "")
_OPS=ParagraphStyle("ops",fontName="Pop",fontSize=7.4,leading=9.8,textColor=INKN)
def _open_txt(B):
    o=B.get("open") or {}; parts=[]
    if o.get("start"): parts.append(f'{o["start"]} starting slot{"s" if o["start"]>1 else ""} empty')
    if o.get("bench"): parts.append(f'{o["bench"]} bench seat{"s" if o["bench"]>1 else ""} open')
    if o.get("ir"): parts.append(f'{o["ir"]} IR slot{"s" if o["ir"]>1 else ""} open (only for a player Yahoo lists as IR or Out)')
    if not parts: return None
    head='<font name="PopB" color="#B32020">Open Seats</font>  —  '+_esc(", ".join(parts)).replace("—","&#8212;")
    adds=B.get("adds") or []
    _d=[a for a in adds if a["pos"] in ("DEF","K")][:1]                     # one defense at most: a second D's number is not a weekly stream
    adds=sorted([a for a in adds if a["pos"] not in ("DEF","K")],key=lambda a:-a["gain"])[:3]+_d   # the defense goes last: its total is overstated
    def _one(a):
        nm=f'<font name="PopB">{_esc(a["name"])}</font>'+("" if a["pos"] in ("DEF","K") else f', {_esc(a["team"])} {_esc(a["pos"])}')
        pg=f'; {a["pgain"]:.0f} in the playoffs' if a.get("pgain") else ""
        sd=" as a second defense (overstated: counted against no add, not a weekly stream)" if a["pos"]=="DEF" else ""
        return f'{nm}{sd} +{a["gain"]:.0f} pts{pg} ({_esc(_tc(a["acq"]).lower() if a["acq"].lower().startswith("free agent") else _tc(a["acq"]))})'
    if (o.get("start") or o.get("bench")) and adds:
        head+=('. An add here costs no drop. <font name="PopB">Best uses, by points added through Week 17:</font> '+"  ·  ".join(_one(a) for a in adds[:4])+".")
    return head
def _open_h(B):
    t=_open_txt(B); return 0 if not t else _ph(t,_OPS,W-2*M-16)+14
def _open_box(c,y,B):
    t=_open_txt(B)
    if not t: return y
    p=Paragraph(t,_OPS); _,h=p.wrap(W-2*M-16,999)
    c.saveState(); c.setFillColor(H("#FBEDEA")); c.setStrokeColor(H("#B32020")); c.setLineWidth(.8)
    c.roundRect(M,y-h-8,W-2*M,h+8,4,stroke=1,fill=1); c.restoreState()
    p.drawOn(c,M+8,y-h-4); return y-h-8-12
