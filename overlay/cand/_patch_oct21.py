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
