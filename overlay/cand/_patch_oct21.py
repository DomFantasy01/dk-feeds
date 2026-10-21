# THE OCT 21 SCOUT FIXES (Dom, Wed Oct 21 2026) - run on every build after the Oct 17 batch. Safe to run twice (marker).
# Every anchor must match exactly once or that fix is skipped with a "!!" line - the Scout is never half-patched.
# Why: the new Scout report card graded every past pickup call - the calls that cleared the 20-point bar beat the man
# they'd replace only 7 of 16 times, and 6 of the 9 misses were men who scored zero because they were hurt.
#  1  SEASON-ENDING NEWS: McLaurin (torn patellar tendon) and Hurts (blood clots) stayed on the boards. ESPN's injury report
#     and the news feeds are now read for season-ending language; a man found there is out for the year everywhere.
#  2  WAIT ON THE INJURED: a man who is listed Out/IR, or who missed his team's last game hurt, is "watch", not a pickup,
#     until his return is confirmed - a full practice on this week's report.
#  3  OUTSIDE CHECK: a pickup needs Yahoo or Sleeper behind it - at least 5 a game from one of them. A man only the Scout's
#     own model likes (Pierre Strong) is "watch".
#  4  PRICE THE DROP: every pickup is now priced against the best man to drop for him (or an open bench seat), so the
#     gain is what the roster really gains. The drop is named on the pick.
#  5  STASHES: the backs one injury away from a lead job (the backup behind a lead back, on waivers or free) are listed
#     before the starter gets hurt.
#  6  RISING WORKLOAD BELOW THE FLOOR: men whose workload jumped but whose season level is under the Scout's floor
#     (Bam Knight) are named as "watch" instead of never being mentioned.
import os
R=os.environ.get("DK_ROOT","/home/claude")
def patch(path,pairs,mark):
    s=open(path).read()
    if mark in s: print("   oct21:",path.split("/")[-1],"already in -",mark); return
    for a,b,n in pairs:
        k=s.count(a); assert k==n,f"oct21 patch: {path.split('/')[-1]}: anchor found {k}x, expected {n}: {a[:80]}"
    for a,b,n in pairs: s=s.replace(a,b)
    open(path,"w").write(s+f"\n# {mark}\n"); print("   oct21:",path.split("/")[-1],"patched -",mark)
SE=f"{R}/dksys/scout/scout_engine.py"

# ---- 1 season-ending news
_SEASON = r'''
SEASONOUT_WHY={}
try:   # Oct 21 (Dom): SEASON-ENDING NEWS - ESPN's injury report + the news feeds; a man found here is out for the year
    _SOR=re.compile(r"(season[- ]ending|out for the (?:20\d\d )?(?:season|year)|done for the (?:season|year)|lost for the (?:season|year)|(?:end|ends|ending|ended) (?:his|their) (?:20\d\d )?season|(?:miss|missing|out for|sidelined for|over for)\b[^.]{0,30}?\b(?:rest|remainder) of the (?:20\d\d )?season)",re.I)
    _FDS=globals().get("_FD","/home/claude/domfantasy01/dk-feeds/feeds/"); _SOI=[]
    try:
        for _x in json.load(open(_FDS+"espn_injuries.json")).get("players",[]):
            _SOI.append((_x.get("name",""),str(_x.get("detail","")),str(_x.get("date","")),"ESPN injury report",True))
    except Exception: pass
    for _fn,_sr in (("rotowire_history.jsonl","RotoWire"),("espn_news_history.jsonl","ESPN"),("news_extra_history.jsonl","news")):
        try:
            for _l in open(_FDS+_fn):
                try: _j=json.loads(_l)
                except Exception: continue
                _t=str(_j.get("title") or "")
                if not _t or _t.count(",")>=2: continue                       # a list article names many men
                _SOI.append((_t,_t+" "+re.sub(r"<[^>]+>"," ",str(_j.get("text") or "")),str(_j.get("published_utc") or ""),_sr,False))
        except Exception: pass
    _GDS={}
    for _r in games.itertuples(): _GDS[(tm(_r.home_team),int(_r.week))]=str(_r.gameday); _GDS[(tm(_r.away_team),int(_r.week))]=str(_r.gameday)
    _nu=dt.datetime.now(dt.timezone.utc)
    for _k,_p in PL.items():
        if _p.get("pos") not in ("QB","RB","WR","TE"): continue
        _nk=norm(_p["name"])
        for _nm,_tx,_ts,_sr,_ex in _SOI:
            if (norm(_nm)!=_nk) if _ex else (_p["name"] not in _nm or "?" in _nm): continue   # a question headline ("Is he out for the season?") is not news
            _ln=_p["name"].split()[-1]
            _parts=[_tx] if _ex else [_nm]+[x for x in re.split(r"(?<=[.!?])\s+",_tx[len(_nm):]) if _ln in x]   # the headline, or a sentence that names him
            _m=None
            for _x in _parts:
                for _mm in _SOR.finditer(_x):
                    if not re.search(r"(\bnot\b|n't\b|\bavoid\w*|\bno\b|\bnon\b)[^.]{0,20}$",_x[max(0,_mm.start()-25):_mm.start()],re.I): _m=_mm; break
                if _m: break
            if not _m: continue
            try: _w=dt.datetime.fromisoformat(_ts.replace("Z","+00:00"))
            except Exception: continue
            if _w.tzinfo is None or (_nu-_w).days>45: continue
            _gday=_GDS.get((_p["team"],int(_p["last"])),"")
            if _gday and _w.strftime("%Y-%m-%d")<_gday: continue             # written before his last game - he has played since
            SEASON_OUT.add(_nk); SEASONOUT_WHY[_nk]=f'{_sr}: "{_m.group(0)}" ({_w:%b} {_w.day})'; break
    if not QUIET: print(f"Scout season-ending check: {len(SEASONOUT_WHY)} men out for the year"+(" - "+", ".join(sorted(SEASONOUT_WHY)) if SEASONOUT_WHY else ""))
except Exception as _e: print("Scout season-ending check skipped:",_e)
def _newsback(p):
'''
try: patch(SE,[("def _newsback(p):\n",_SEASON.lstrip("\n"),1)],"OCT21a season-ending news")
except AssertionError as _e: print("!! OCT21a season-ending news NOT applied:",_e)

# ---- 2+3 wait on the injured, outside check   ---- 4 price the drop
_FLAGS = r'''    _flag=None if len(p["fp"])>=2 else "One game only — flag, not act."
    if p["pos"] not in ("K","DEF"):
        _missed=p["last"]<TEAMLAST.get(p["team"],0) and not p.get("moved") and bool(p.get("inj") or EXTINJ.get((norm(p["name"]),p["pos"])))
        _full=INJWK==NOW and "full" in str(p.get("prac","")).lower()
        if back(p)>NOW: _flag=f"Watch, not a pickup yet: listed out, due back Wk {back(p)} - waits for his return to be confirmed (a full practice)."
        elif _missed and not _full: _flag="Watch, not a pickup yet: missed his last game hurt"+(f" ({p['inj']})" if p.get("inj") else "")+" - waits for a full practice this week."
        elif (_YP or _SLPPR) and _flag is None:
            _ob=[v for v in (YMAX.get(_ypk(p)),_SLPPR.get(norm(p["name"]))) if v is not None]
            if not _ob: _flag="Watch: only the Scout's model has a number on him - no Yahoo or Sleeper projection backs it."
            elif max(_ob)<5: _flag=f"Watch: Yahoo/Sleeper have him at {max(_ob):.1f} at best - the Scout's ~{p['fwd']:.1f} isn't backed up."
    G2.append(dict(act=_flag is None,flag=_flag,k=k,'''
_PRE = r'''TEAMLAST=st.groupby("team").week.max().to_dict()
'''
_INJWK = r'''TEAMLAST=st.groupby("team").week.max().to_dict()
INJWK=int(inj.week.max()) if len(inj) else 0      # Oct 21: the injury report's week - a full practice counts only on this week's report
'''
_DROP = r'''G2.sort(key=lambda e:-e["wins"])
# Oct 21 (Dom): PRICE THE DROP - every pickup is priced against the best man to let go for him (or an open bench seat)
try:
    _BCAP={"DKI":5,"DKII":5,"DKIII":5,"DKIV":5}.get(LGK,5); _openb=_BCAP-sum(1 for m in MINE if m["slot"]=="BN")
    # a handcuff is never the drop (Dom: check what a bench man is FOR): the #2 back behind a lead back (12+ a game, half the touches)
    _HC=set(); _tl0=st.groupby("team").week.max().to_dict()
    for _t,_g in st[st.position=="RB"].groupby("team"):
        _g=_g[_g.week>=_tl0.get(_t,0)-2]; _tch=(_g.carries.fillna(0)+_g.targets.fillna(0)).groupby(_g.player_display_name).sum().sort_values(ascending=False)
        if len(_tch)>=2 and _tch.sum()>0 and _tch.iloc[0]/_tch.sum()>=.5 and _tch.iloc[1]/_tch.sum()>=.15:
            _sk0=find(_tch.index[0],_t,"RB")
            if _sk0 and PL[_sk0]["fwd"]>=12: _HC.add(norm(_tch.index[1]))
    _cut=[(i,m) for i,m in enumerate(MINE) if m["slot"]!="IR" and m["name"] not in CF["protect"] and norm(m["name"]) not in _HC]
    for e in G2:
        if _openb>0: e["drop"]=None; continue
        _nm=dict(key=e["k"],name=e["p"]["name"],pos=e["p"]["pos"],ytag="",slot="BN"); _best=None
        for i,m in _cut:
            _t3=[x for j,x in enumerate(MINE) if j!=i]+[_nm]
            _g={x:total(_t3,x)-my[x] for x in WEEKS}; _s=sum(_g.values())
            if _best is None or _s>_best[0]: _best=(_s,m,_g)
        if _best is None: continue
        e["drop"]=_best[1]["name"]; e["g_nodrop"]=e["g"]; e["g"]=_best[2]
        e["good"]=[x for x in WEEKS if e["g"][x]>=1.5]; e["wins"]=sum(LEV[x]*e["g"][x] for x in WEEKS)
    G2=[e for e in G2 if e["good"] and (not e.get("drop") or sum(e["g"].values())>0)]   # a pickup that loses points net of the drop is no pickup
    G2.sort(key=lambda e:-e["wins"])
    if not QUIET: print(f"Scout drop pricing: {'open bench seat - no drop needed' if _openb>0 else str(len(G2))+' pickups priced against the best drop'}")
except Exception as _e: print("Scout drop pricing skipped:",_e)
def _gn(e): return round(sum(e["g"].values()) if e.get("drop") else sum(max(0.0,v) for v in e["g"].values()),1)    # net of the drop
def _pgn(e): return round(sum(e["g"].get(x,0.0) for x in PLAYOFF) if e.get("drop") else sum(max(0.0,e["g"].get(x,0.0)) for x in PLAYOFF),1)
'''
try: patch(SE,[(_PRE,_INJWK,1),('    G2.append(dict(act=len(p["fp"])>=2,k=k,',_FLAGS,1),('G2.sort(key=lambda e:-e["wins"])\n',_DROP,1)],"OCT21b wait on injured + outside check + price the drop")
except AssertionError as _e: print("!! OCT21b NOT applied:",_e)
# YMAX (Yahoo's best weekly number from this week on) is needed by the flags above, which run before the drop step - define it
# right after Yahoo's weekly projections are read.
try: patch(SE,[('def weekly(p,x,ytag=""):\n',
  'YMAX={}\nfor (_yk,_yw),_yv in _YP.items():\n    if _yw>=NOW: YMAX[_yk]=max(YMAX.get(_yk,0.0),_yv)\ndef weekly(p,x,ytag=""):\n',1)],"OCT21c Yahoo best weekly number")
except AssertionError as _e: print("!! OCT21c NOT applied:",_e)

# ---- the flag and the drop ride on the board
try: patch(SE,[
 ('    if not e["act"]: e=dict(e,why=e["why"]+["one game only — flag, not act"])',
  '    if not e["act"]: e=dict(e,why=e["why"]+[e.get("flag") or "one game only — flag, not act"])',1),
 ('pick=_pick(e,False,e["good"]),act=e["act"]))','pick=_pick(e,False,e["good"]),act=e["act"],flag=e.get("flag")))',1),
 ('    return dict(name=p["name"].replace(" defense"," DEF"),team=p["team"],pos=p["pos"],scores=sc,',
  '    return dict(drop=e.get("drop"),name=p["name"].replace(" defense"," DEF"),team=p["team"],pos=p["pos"],scores=sc,',1),
 ('BOARD["adds"]=[dict(name=e["p"]["name"].replace(" defense"," DEF"),','BOARD["adds"]=[dict(drop=e.get("drop"),name=e["p"]["name"].replace(" defense"," DEF"),',1),
 ('gain=round(sum(max(0.0,v) for v in e["g"].values()),1),pgain=round(sum(max(0.0,e["g"].get(x,0.0)) for x in PLAYOFF),1)','gain=_gn(e),pgain=_pgn(e)',2),
 ('key=lambda e:-sum(max(0.0,v) for v in e["g"].values()))[:6]]','key=lambda e:-_gn(e))[:6]]',1),
],"OCT21e flag + drop on the board")
except AssertionError as _e: print("!! OCT21e NOT applied:",_e)

# ---- 5 stashes + 6 rising workload below the floor + watch list
_WATCH = r'''# Oct 21 (Dom): THE WATCH LIST - injured men waiting on a confirmed return, backups one injury from a lead job (stashes),
# and men whose workload jumped while their season level is still under the Scout's floor. Facts only - Dom's call.
BOARD["watch"]=[]
try:
    for e in G2:
        if e.get("flag","") and str(e.get("flag")).startswith("Watch") and not killed(e["p"]["name"]):
            BOARD["watch"].append(f"Watch: {e['p']['name']} ({e['p']['team']} {e['p']['pos']}) - {e['flag'].split(': ',1)[1]}")
    BOARD["watch"]=BOARD["watch"][:3]
    _tl=st.groupby("team").week.max().to_dict(); _stash=[]
    for _t,_g in st[st.position=="RB"].groupby("team"):
        _g=_g[_g.week>=_tl.get(_t,0)-2]
        _tch=(_g.carries.fillna(0)+_g.targets.fillna(0)).groupby(_g.player_display_name).sum().sort_values(ascending=False)
        if len(_tch)<2 or _tch.sum()<=0: continue
        _sn,_bn=_tch.index[0],_tch.index[1]; _ss,_bs=_tch.iloc[0]/_tch.sum(),_tch.iloc[1]/_tch.sum()
        _sk=find(_sn,_t,"RB"); _bk=find(_bn,_t,"RB")
        if not _sk or not _bk or _bk in taken or norm(_bn) in SEASON_OUT or killed(_bn): continue
        if _ss<.5 or _bs<.15 or PL[_sk]["fwd"]<12: continue
        _acq=("waivers, clears "+WAIV[_bk[0]]) if _bk[0] in WAIV else "free agent"
        _stash.append((PL[_sk]["fwd"]*_bs,f"Stash: {_bn} ({_t} RB, {_acq}) - {_bs:.0%} of the {_t} backfield's touches the last three games behind {_sn} (~{PL[_sk]['fwd']:.1f} a game, {_ss:.0%}); the lead job is his if {_sn.split()[-1]} goes down; his own level now ~{PL[_bk]['fwd']:.1f}"))
    _stash=sorted(_stash,reverse=True)[:2]; BOARD["watch"]+=[s for _,s in _stash]; _named={s.split(' (')[0].split(': ',1)[1] for s in BOARD['watch']}
    _g2k={e["k"] for e in G2}; _rise=[]
    for _k,_p in PL.items():
        if _p["pos"] not in ("RB","WR","TE") or _p["name"] in _named or _k in taken or _k in _g2k or norm(_p["name"]) in SEASON_OUT or killed(_p["name"]): continue
        _xv=_p.get("xv") or []
        if len(_xv)<3 or _p["last"]<_tl.get(_p["team"],0): continue
        _e,_l=float(np.mean(_xv[:-1])),float(_xv[-1])
        if _l>=8 and _l>=2*max(_e,1):
            _acq=("waivers, clears "+WAIV[_k[0]]) if _k[0] in WAIV else "free agent"
            _rise.append((_l-_e,f"Rising: {_p['name']} ({_p['team']} {_p['pos']}, {_acq}) - workload jumped to {_l:.1f} expected points last game from {_e:.1f} before; season level ~{_p['fwd']:.1f}, not on the Scout's pickup list yet - one more game like it and he is"))
    BOARD["watch"]+=[s for _,s in sorted(_rise,reverse=True)[:2]]
    if not QUIET: print(f"Scout watch list: {len(BOARD['watch'])} lines")
except Exception as _e: print("Scout watch list skipped:",_e)
json.dump(BOARD,open(f"{H}/scout_board_{LGK}.json","w"),indent=1)
'''
try: patch(SE,[('json.dump(BOARD,open(f"{H}/scout_board_{LGK}.json","w"),indent=1)\n',_WATCH,1)],"OCT21f watch list")
except AssertionError as _e: print("!! OCT21f NOT applied:",_e)

# ---- the Dispatch's Scout page shows the flag and the watch list
try: patch(f"{R}/cand/redesign/_scout_page.py",[
 ("""        if not it.get("act",True): t+=' <font color="#5A6273">One game only — flag, not act.</font>'""",
  """        if not it.get("act",True): t+=' <font color="#5A6273">'+_esc(it.get("flag") or "One game only — flag, not act.")+'</font>'""",1),
 ('"  ·  ".join(_esc(s) for s in B["checked"]+_chart_lines(lab,B))','"  ·  ".join(_esc(s) for s in B["checked"]+B.get("watch",[])+_chart_lines(lab,B))',1),
 ],"OCT21g Scout page flag + watch")
except AssertionError as _e: print("!! OCT21g NOT applied:",_e)

# ---- 1b the Positions chart (engine3v doors) reads the same season-ending news - McLaurin was still a "bye fill" there
_E3SO = r'''OUTSEASON={norm(n) for n in ['De\'Von Achane']}   # season-ending, never a candidate
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
'''
try: patch(f"{R}/dksys/engine/engine3v.py",[("OUTSEASON={norm(n) for n in ['De\\'Von Achane']}   # season-ending, never a candidate\n",_E3SO,1)],"OCT21h Positions doors season-ending")
except AssertionError as _e: print("!! OCT21h NOT applied:",_e)

# ---- 7 FADING STARTER -> RISING TEAMMATE (Dom, Oct 21 9:40 AM): a starter losing snaps and touches over the last three
#      games, paired with the teammate at his position picking up that work - an early warning before the backup breaks
#      out, and a warning when the fading man is on Dom's own roster.
_FADE = r'''    try:   # Oct 21 (Dom): fading starters and who is taking their work
        _tw=st.groupby("team").week.apply(lambda s:sorted(set(int(x) for x in s))).to_dict()
        _ttg=st.groupby(["team","week"]).targets.sum().to_dict()
        _mine={m["key"] for m in MINE}; _fade=[]
        for _t,_wks in _tw.items():
            if len(_wks)<5: continue
            _last,_prev=_wks[-3:],_wks[:-3][-3:]
            for _pos in ("RB","WR","TE"):
                _s=st[(st.team==_t)&(st.position==_pos)]
                _snp=sn[(sn.team==_t)&(sn.position==_pos)]
                def _sh(name,wks):
                    _x=_s[(_s.player_display_name==name)&(_s.week.isin(wks))]
                    if _pos=="RB":
                        _all=_s[_s.week.isin(wks)]; _d=float((_all.carries.fillna(0)+_all.targets.fillna(0)).sum())
                        return float((_x.carries.fillna(0)+_x.targets.fillna(0)).sum())/_d if _d else 0.0
                    _d=float(sum(_ttg.get((_t,w),0) for w in wks)); return float(_x.targets.fillna(0).sum())/_d if _d else 0.0
                def _sp(name,wks):
                    _x=_snp[(_snp._nk==norm(name))&(_snp.week.isin(wks))]
                    return float(_x.offense_pct.sum())/len(wks)                       # a game he sat counts as 0 snaps (for the man taking work)
                def _played(name,wks):
                    _x=_snp[(_snp._nk==norm(name))&(_snp.week.isin(wks))&(_snp.offense_pct>0)]
                    return sorted(_x.offense_pct.tolist())
                for _nm in _s.player_display_name.unique():
                    _k=find(_nm,_t,_pos)
                    if not _k: continue
                    _p=PL[_k]
                    if _p["last"]<_wks[-1] or norm(_nm) in SEASON_OUT: continue       # he missed the last game - an injury, not a fade
                    _pl1,_pl0=_played(_nm,_last),_played(_nm,_prev)
                    if len(_pl1)<3 or len(_pl0)<2: continue                          # a fade is lost work while playing - a missed game is an injury
                    _sp0,_sp1=float(np.median(_pl0)),float(np.median(_pl1)); _sh0,_sh1=_sh(_nm,_prev),_sh(_nm,_last)
                    if _sp0<(.5 if _pos=="RB" else .6) or _sp0-_sp1<.10 or max(_pl1)>_sp0-.03 or _sh0-_sh1<.05: continue   # every one of the last three games below his old level
                    _best=None
                    for _nm2 in _s.player_display_name.unique():
                        if _nm2==_nm: continue
                        _a0,_a1=_sp(_nm2,_prev),_sp(_nm2,_last); _b0,_b1=_sh(_nm2,_prev),_sh(_nm2,_last)
                        if _a1-_a0>=.08 and _b1>_b0 and (_best is None or _b1-_b0>_best[0]): _best=(_b1-_b0,_nm2,_a0,_a1,_b0,_b1)
                    if not _best: continue
                    _d,_nm2,_a0,_a1,_b0,_b1=_best; _k2=find(_nm2,_t,_pos)
                    # a third teammate who carried real work before and missed games in the window (Monangai) - the shift is an
                    # injury fill that ends when he returns, not a starter losing his job
                    if any(_sh(_o,_prev)>=.2 and len(_played(_o,_last))<3 for _o in _s.player_display_name.unique() if _o not in (_nm,_nm2)): continue
                    _avail=bool(_k2) and _k2 not in taken and not killed(_nm2)
                    _yours=_k in _mine
                    if not (_avail or _yours): continue
                    _acq=(("waivers, clears "+WAIV[_k2[0]]) if _k2[0] in WAIV else "free agent") if _avail else ("on your roster" if _k2 in _mine else "rostered")
                    _wl="touch" if _pos=="RB" else "target"
                    _fade.append(((2 if _yours else 1)*(_sh0-_sh1+_d),
                        f"{'Your starter fading' if _yours else 'Early warning'}: {_nm} ({_t} {_pos}) snaps {_sp0:.0%} to {_sp1:.0%} (typical game), {_wl} share {_sh0:.0%} to {_sh1:.0%} the last three games; "
                        f"{_nm2} ({_acq}) is taking the work - snaps {_a0:.0%} to {_a1:.0%}, {_wl} share {_b0:.0%} to {_b1:.0%}"+(f", level now ~{PL[_k2]['fwd']:.1f}" if _k2 else "")))
        BOARD["fade"]=[s for _,s in sorted(_fade,reverse=True)[:4]]
        BOARD["watch"]+=BOARD["fade"][:3]
    except Exception as _e: print("Scout fade check skipped:",_e)
    if not QUIET: print(f"Scout watch list: {len(BOARD['watch'])} lines")
'''
try: patch(SE,[("    if not QUIET: print(f\"Scout watch list: {len(BOARD['watch'])} lines\")\n",_FADE,1)],"OCT21i fading starters")
except AssertionError as _e: print("!! OCT21i NOT applied:",_e)

# ---- 8 GOTHAM: AN INHERITED JOB (Dom, Oct 21). Gotham blends in last season's per-game number (worth two games). When a man
#      took over for a starter who is out for the season (Ollie Gordon for Achane), last season was a backup's year and says
#      nothing about the job he has now - so for him the 2025 number is left out, the same way Gotham already leaves it out
#      for a role change this week. Tested this week: only men behind a season-ending injury are touched.
try: patch(f"{R}/dksys/engine/engine3v.py",[("except Exception as _e3: print('ENGINE3 season-ending check skipped:', _e3)\n",
  "except Exception as _e3: print('ENGINE3 season-ending check skipped:', _e3)\n"
  "try: json.dump(sorted(OUTSEASON),open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'outseason.json'),'w'))   # Oct 21: Gotham reads it (inherited jobs)\n"
  "except Exception: pass\n",1)],"OCT21j engine3 writes the season-ending list")
except AssertionError as _e: print("!! OCT21j NOT applied:",_e)
try: patch(f"{R}/dksys/engine/gotham.py",[
 ("LGK={'DKI':1,'DKII':2,'DKIII':3,'DKIV':4}; summary={}\n",
  "LGK={'DKI':1,'DKII':2,'DKIII':3,'DKIV':4}; summary={}\n"
  "try:   # Oct 21 (Dom): jobs inherited from a man out for the season - last season's number is left out for whoever took the job\n"
  "    OUTS=set(json.load(open(os.path.join(HERE,'outseason.json'))))\n"
  "    _l=S.sort_values('week').groupby('k').last()\n"
  "    INH={(str(_l.loc[k_].team),str(_l.loc[k_].position)) for k_ in OUTS if k_ in _l.index}\n"
  "except Exception as _e: OUTS,INH=set(),set(); print('GOTHAM inherited-job check skipped:',_e)\n"
  "",1),
 ("        if (row.role_add or 0)>0: return v           # his role changed this week - last season says nothing about the new one\n",
  "        if (row.role_add or 0)>0: return v           # his role changed this week - last season says nothing about the new one\n"
  "        if (str(row.team),str(row.pos)) in INH and row.k not in OUTS and row.n_games>=2 and v>=1.5*row.prior: return v   # Oct 21: he inherited the job of a man out for the season\n",1),
],"OCT21k Gotham inherited jobs")
except AssertionError as _e: print("!! OCT21k NOT applied:",_e)

# ---- 9 RETURNING MEN WITH NO GAMES THIS SEASON (Dom, Oct 21): Josh Jacobs missed six games on the exempt list and is back
#      at practice - the Scout had no 2026 games for him, so it never cut MarShawn Lloyd's role. A proven back/TE/QB from last
#      season (Sleeper has him on a team, no injury tag) with fresh news that he is practicing or returning now counts as
#      coming back: his position-mates on that team fall to half their level from his return week (the Scout's own rule
#      for a returning man it has no shared games with).
_RET = r'''
RETURNERS={}
try:   # Oct 21 (Dom): proven men coming back with no 2026 games (Josh Jacobs off the exempt list)
    _FDR=globals().get("_FD","/home/claude/domfantasy01/dk-feeds/feeds/")
    _spr=json.load(open(_FDR+"sleeper_players_min.json")).get("players",{}); _spr=_spr.values() if isinstance(_spr,dict) else _spr
    _have={norm(p["name"]) for p in PL.values()}
    _RX=re.compile(r"(practic\w*|return\w*|debut|activated|reinstated|off (?:the )?(?:commissioner'?s )?exempt|cleared|back on the field|could play|will play|expected to play|set to play)",re.I)
    _NOWX=re.compile(r"(debut|could play|will play|expected to play|set to play|chance to play|might play|may play)",re.I)
    _hl=[]
    for _fn in ("rotowire_history.jsonl","espn_news_history.jsonl","news_extra_history.jsonl"):
        try:
            for _l in open(_FDR+_fn):
                try: _j=json.loads(_l)
                except Exception: continue
                _t=str(_j.get("title") or ""); _ts=str(_j.get("published_utc") or "")
                if not _t or "?" in _t or _t.count(",")>=2: continue
                try: _w=dt.datetime.fromisoformat(_ts.replace("Z","+00:00"))
                except Exception: continue
                if _w.tzinfo is None or (dt.datetime.now(dt.timezone.utc)-_w).days>7: continue
                _hl.append((_w,_t,_t+" "+re.sub(r"<[^>]+>"," ",str(_j.get("text") or ""))))
        except Exception: pass
    for _x in _spr:
        _nm=_x.get("name") or ""; _ps=_x.get("pos"); _tm=_x.get("team")
        if _ps not in ("QB","RB","TE") or not _tm or _x.get("inj"): continue
        _nk=norm(_nm); _pr=P25.get(_nk)
        if _nk in _have or _nk in SEASON_OUT or _pr is None or _pr<(15 if _ps=="QB" else 10): continue
        _hit=[h for h in _hl if _nm in h[1] and _RX.search(h[2])]
        if not _hit: continue
        _h=max(_hit); _wk=NOW if _NOWX.search(_h[2]) else NOW+1
        RETURNERS[_nk]=dict(name=_nm,team=tm(_tm),pos=_ps,prior=_pr,week=_wk,news=f"{_h[1]} ({_h[0]:%b} {_h[0].day})")
        for _k2,_m in skill.items():
            if _m["team"]!=tm(_tm) or _m["pos"]!=_ps or _m["fwd"]>_pr*1.25: continue           # a teammate clearly better than him keeps his job
            if _k2 not in CLOSE or CLOSE[_k2]["week"]>_wk:
                CLOSE[_k2]=dict(week=_wk,who=_nm,whokey=(_nk,tm(_tm)),after=.5*_m["fwd"],before=_m["fwd"],why=f"back with no games yet this season - {_h[1]}")
    if not QUIET: print(f"Scout returners: {len(RETURNERS)} - "+", ".join(f"{v['name']} ({v['team']} {v['pos']}, Wk {v['week']})" for v in RETURNERS.values()))
except Exception as _e: print("Scout returners check skipped:",_e)

# Oct 14 afternoon (Dom): this week's Sleeper numbers + the this-week guard
'''
try: patch(SE,[
 ("\n\n# Oct 14 afternoon (Dom): this week's Sleeper numbers + the this-week guard\n",_RET,1),
 ('    pr=PL[c["whokey"]]\n','    pr=PL.get(c["whokey"],{"prac":""})   # Oct 21: a returner with no 2026 games is not in PL\n',1),
],"OCT21l returners with no games this season")
except AssertionError as _e: print("!! OCT21l NOT applied:",_e)

# ---- 10 THE MORNING BRIEF (Dom, Oct 21): (a) a Scout "watch" (injured, or no outside backing) is never a to-do - the brief told
#      Dom to add Pierre Strong after the Scout had moved him to watch; (b) a questionable or doubtful starter now carries the
#      latest injury note (ESPN's injury report, dated) so the brief says what is known, not just "check his status".
try: patch(f"{R}/cand/_actions.py",[
 ('        if _g.get("mark") != "red" or not _pk.get("name"): continue\n',
  '        if _g.get("mark") != "red" or not _pk.get("name") or _g.get("act") is False: continue   # Oct 21: a Scout watch is not a to-do\n',1),
 ('            ACTIONS.append(dict(lg=_lab, rank=4, kind="check", who=_nm, what=f"{_who} is {_AWORD[_st]}. Check his status", by=f"before his {_a_ko(_p.get(\'kickoff\'))} kickoff"))\n',
  '            ACTIONS.append(dict(lg=_lab, rank=4, kind="check", who=_nm, what=f"{_who} is {_AWORD[_st]}"+_a_inj(_nm)+". Check his status", by=f"before his {_a_ko(_p.get(\'kickoff\'))} kickoff"))\n',1),
 ('# ---------------------------------------------------------------- ACTIONS\n',
  '# Oct 21 (Dom): the latest injury note for a tagged starter, from ESPN\'s injury report (dated, first sentence)\n'
  '_AINJ = {}\n'
  'try:\n'
  '    for _x in _aj.load(open("/home/claude/domfantasy01/dk-feeds/feeds/espn_injuries.json")).get("players", []):\n'
  '        _AINJ[_x.get("name", "")] = _x\n'
  'except Exception: pass\n'
  'def _a_inj(nm):\n'
  '    x = _AINJ.get(nm) or next((v for k, v in _AINJ.items() if k.replace(" Jr.", "").replace(" II", "") == nm.replace(" Jr.", "").replace(" II", "")), None)\n'
  '    if not x or not x.get("detail"): return ""\n'
  '    try: d = _ad.datetime.fromisoformat(str(x.get("date", "")).replace("Z", "+00:00")); ds = f"{d:%b} {d.day}"\n'
  '    except Exception: return ""\n'
  '    if (_ad.datetime.now(_ad.timezone.utc) - d).days > 5: return ""   # an old note says nothing about this week\n'
  '    s = _ar.split(r"(?<=[.!?])\\s+", str(x["detail"]).strip())[0]\n'
  '    if len(s.split()) < 4:   # ESPN sometimes posts only the tag - use the newest RotoWire note on him instead\n'
  '        try:\n'
  '            best = None\n'
  '            for _l in open("/home/claude/domfantasy01/dk-feeds/feeds/rotowire_history.jsonl"):\n'
  '                _j = _aj.loads(_l); _t = str(_j.get("title") or "")\n'
  '                if not _t.startswith(nm + ":"): continue\n'
  '                _w = _ad.datetime.fromisoformat(str(_j.get("published_utc")).replace("Z", "+00:00"))\n'
  '                if (_ad.datetime.now(_ad.timezone.utc) - _w).days <= 5 and (best is None or _w > best[0]): best = (_w, _t.split(":", 1)[1].strip(), str(_j.get("text") or ""))\n'
  '            if not best: return ""\n'
  '            d, s = best[0], best[1] + " - " + _ar.split(r"(?<=[.!?])\\s+", best[2].strip())[0]\n'
  '            return f" - latest (RotoWire, {d:%b} {d.day}): {s.rstrip(\'.\')}"\n'
  '        except Exception: return ""\n'
  '    return f" - latest ({\'ESPN\'}{\', \' + ds if ds else \'\'}): {s.rstrip(\'.\')}"\n'
  '# ---------------------------------------------------------------- ACTIONS\n',1),
],"OCT21m brief: no watch to-dos, injury notes")
except AssertionError as _e: print("!! OCT21m NOT applied:",_e)

# ---- 11 STALE WAIVER DATE (Oct 21): Tampa Bay and Dallas men were all marked "waivers, clears Oct 14" (a one-week rule from
#      Week 6) - long past, so they are free agents unless Yahoo's waiver list says otherwise.
try: patch(SE,[('("waivers, clears Oct 14" if PL[k]["team"] in ("TB","DAL") else "free agent")','"free agent"',1)],"OCT21n stale Oct 14 waiver rule off")
except AssertionError as _e: print("!! OCT21n NOT applied:",_e)

# ---- 12 THE PICKUP GUARD + THE RIVAL CHECK (Dom, Oct 21). Two misses today: Dameon Pierce was recommended without saying his
#      game is Monday night (the Sunday bench locks first) or that Barkley could return; Kimani Vidal's $1 bid was suggested
#      without checking which rivals need a running back. Every pick on the board now carries both checks.
_GUARD = r'''
def _gd_ko(team):
    try:
        g_=games[(games.week==NOW)&((games.home_team==team)|(games.away_team==team))]
        if not len(g_): return None
        r_=g_.iloc[0]; t_=dt.datetime.strptime(f"{r_.gameday} {r_.gametime}","%Y-%m-%d %H:%M")-dt.timedelta(hours=3)   # Eastern -> Pacific
        return t_
    except Exception: return None
def guard(e):
    """Oct 21 (Dom): late kickoff (the Sunday bench locks first) and a starter who could come back and take the work"""
    p=e["p"]; k=e["k"]; out=[]
    t_=_gd_ko(p["team"])
    if t_ is not None and t_.weekday() in (0,3):
        out.append(f"plays {t_:%A} night ({t_.hour%12 or 12}:{t_:%M} PM PT) - if you start him and he sits, your Sunday players have already locked")
    if k in CLOSE:
        c_=CLOSE[k]; out.append(f"his role shrinks to ~{c_['after']:.1f} from Wk {c_['week']} when {c_['who']} is back ({c_['why']})")
    for r_ in e.get("why") or []:
        m_=re.match(r"door open: (.+) out",r_)
        if m_ and k not in CLOSE: out.append(f"his work depends on {m_.group(1)} staying out - check {m_.group(1).split()[-1]}'s status first")
    return out
_STAND={}
try:
    _sf=sorted(_glb.glob(f"{L}/yahoo/wk{NOW}/standings_*.txt"))
    if _sf:
        _lid={"DKI":"269381","DKII":"1519795","DKIII":"1507991","DKIV":"864215"}[LGK]
        for _ln in open(_sf[-1]):
            if not _ln.startswith(_lid+"#"): continue
            for _row in _ln.split("#",1)[1].strip().split("|"):
                _c=_row.split("^")
                if len(_c)>=9 and _c[7].startswith("$"): _STAND[re.sub(r"[^a-z0-9]","",_c[1].lower())]=(_c[7],_c[8])
except Exception as _e: print("Scout rival check: standings not read -",_e)
def _faab(tid):
    n_=re.sub(r"[^a-z0-9]","",str(TEAMNAMES.get(tid,"")).lower())
    for k_,v_ in _STAND.items():
        if n_ and (n_.startswith(k_) or k_.startswith(n_)): return v_
    return None
_NST={"QB":1,"RB":2,"WR":3,"TE":1}
def rivals(e):
    """Oct 21 (Dom): which other teams would start him over one of their own, and what each has to spend"""
    p=e["p"]
    if p["pos"] not in _NST or "aiver" not in e.get("acq",""): return None
    need=[]
    for tid,mem in TEAMS.items():
        if tid==ME: continue
        vs=sorted([PL[m["key"]]["fwd"] for m in mem if m["pos"]==p["pos"] and m["slot"]!="IR" and m["ytag"] not in ("NA","IR","O")],reverse=True)
        top=vs[:_NST[p["pos"]]]
        if len(top)<_NST[p["pos"]] or (top and p["fwd"]>top[-1]):
            fb=_faab(tid); need.append((TEAMNAMES.get(tid,str(tid)),fb))
    if not need: return "rival check: no other team would start him - the minimum bid should do"
    return f"rival check: {len(need)} team{'s' if len(need)>1 else ''} would start him over one of their own - "+", ".join(f"{n_} ({fb[0]} left, waiver #{fb[1]})" if fb else n_ for n_,fb in need[:6])
'''
try: patch(SE,[
 ('def _pick(e,need_red,w):\n',_GUARD.lstrip("\n")+'def _pick(e,need_red,w):\n',1),
 ('    if _nb or p.get("moved") or p.get("tradecut"): urg="gold"       # Oct 17 (Dom): check before acting\n',
  '    if _nb or p.get("moved") or p.get("tradecut"): urg="gold"       # Oct 17 (Dom): check before acting\n'
  '    _gl=guard(e); _rv=rivals(e)                                     # Oct 21 (Dom): the pickup guard + the rival check\n'
  '    if _gl: why=why+"; CHECK FIRST: "+"; ".join(_gl); urg="gold"\n'
  '    if _rv: why=why+"; "+_rv\n',1),
 ('    return dict(drop=e.get("drop"),name=p["name"].replace(" defense"," DEF"),team=p["team"],pos=p["pos"],scores=sc,',
  '    return dict(guard=_gl,rivals=_rv,drop=e.get("drop"),name=p["name"].replace(" defense"," DEF"),team=p["team"],pos=p["pos"],scores=sc,',1),
 ('BOARD["adds"]=[dict(drop=e.get("drop"),','BOARD["adds"]=[dict(guard=guard(e),rivals=rivals(e),drop=e.get("drop"),',1),
],"OCT21o pickup guard + rival check")
except AssertionError as _e: print("!! OCT21o NOT applied:",_e)
