# THE OCT 17 SCOUT FIXES (Dom, Sat Oct 17 2026) - applied to the Scout on every build, after the Oct 14 batch.
# Safe to run twice (marker). Every anchor must match exactly once or the build stops - the Scout is never half-patched.
#  1  THE TRADE CHECK. The Scout valued every player off the games he has already played, so a trade was invisible
#     until the new games showed up. It recommended Xavier Hutchinson (HOU WR) the week Houston traded for Marvin
#     Harrison Jr. - Dom caught it, the engine didn't. Now Sleeper's current team (pulled every 30 min by the feed job)
#     is checked against the team each man played his games for:
#       - a man who changed teams is moved to his new team (his byes and matchups follow him) and every line on him says
#         his numbers come from the old team;
#       - the incumbents at his position on the new team (top 3 WRs, top 2 at the other spots) lose the newcomer's share
#         of that position's production - e.g. a newcomer worth 15 joining receivers worth 9, 8 and 6 takes 39% - and
#         every line on them shows the cut with its arithmetic (was 9.0, now 5.5);
#       - a man Sleeper shows on no NFL team (released, unsigned) is never recommended.
#     Name matches must be unique (name + position) or the man is left alone - no guessing.
#  2  THE NEWS CHECK ON EVERY PICKUP. Before any available player is recommended, the Scout reads the last 14 days of
#     news it already keeps (RotoWire, ESPN, PFT/RotoBaller history) for his name. Every pick carries its newest item
#     (source, date, headline) or says plainly that no news was found. News of injury, surgery, IR, a trade, a release,
#     a benching or a suspension in the last 7 days raises a NEWS FLAG on the line, and a flagged pick is never red
#     (act now) - it drops to gold so Dom checks it before acting.
#  3  DEFENSES ON WAIVERS: a defense on Yahoo's waiver list now prints its waiver date instead of "Free agent".
import os
R=os.environ.get("DK_ROOT","/home/claude")
def patch(path,pairs,mark):
    s=open(path).read()
    if mark in s: print("   oct17:",path.split("/")[-1],"already in"); return
    for a,b,n in pairs:
        k=s.count(a); assert k==n,f"oct17 patch: {path.split('/')[-1]}: anchor found {k}x, expected {n}: {a[:80]}"
        s=s.replace(a,b)
    open(path,"w").write(s+f"\n# {mark}\n"); print("   oct17:",path.split("/")[-1],"patched -",mark)

_TRADE = r'''
# ---- Oct 17 (Dom): THE TRADE CHECK - Sleeper's current team vs the team each man played for ----
MOVED={}
try:
    _FDT=globals().get("_FD","/home/claude/domfantasy01/dk-feeds/feeds/")
    _spl=json.load(open(_FDT+"sleeper_players_min.json")).get("players",{})
    _cur=collections.defaultdict(list)
    for _x in (_spl.values() if isinstance(_spl,dict) else _spl):
        if _x.get("pos") in ("QB","RB","WR","TE") and _x.get("name"):
            _cur[(norm(_x["name"]),_x["pos"])].append(tm(_x["team"]) if _x.get("team") else None)
    for _k,_p in list(PL.items()):
        if _p["pos"] not in ("QB","RB","WR","TE"): continue
        _c=_cur.get((norm(_p["name"]),_p["pos"]))
        if not _c or len(set(_c))!=1: continue                     # unknown or ambiguous name - leave him alone
        _t2=_c[0]
        if _t2 is None:
            SEASON_OUT.add(norm(_p["name"])); _p["gone"]="on no NFL roster now (Sleeper)"; continue
        if _t2!=_p["team"]:
            _t1=_p["team"]; _p["team"]=_t2; _p["oldteam"]=_t1
            _p["moved"]=f"moved {_t1} to {_t2} - his numbers so far are from {_t1}"
            del PL[_k]; PL[(_k[0],_t2)]=_p; MOVED[(_k[0],_t2)]=(_t1,_t2)
    for _k,(_t1,_t2) in MOVED.items():
        _m=PL[_k]
        _inc=sorted([q for kk,q in PL.items() if kk!=_k and q.get("team")==_t2 and q["pos"]==_m["pos"] and not q.get("oldteam")],
                    key=lambda q:-q["fwd"])[:(3 if _m["pos"]=="WR" else 2)]
        _tot=_m["fwd"]+sum(q["fwd"] for q in _inc)
        if not _inc or _tot<=0: continue
        _sh=_m["fwd"]/_tot
        for q in _inc:
            _was=q["fwd"]; q["fwd"]=_was*(1-_sh); q["v26"]=q.get("v26",_was)*(1-_sh)
            q.setdefault("tradecut",[]).append(f"{_m['name']} joined {_t2} from {_t1}: his pre-trade ~{_was:.1f} a game cut to ~{q['fwd']:.1f} ({_sh*100:.0f}% of the {_m['pos']} production goes to the newcomer)")
    if not QUIET: print(f"Scout trade check: {len(MOVED)} men changed teams (Sleeper)" + (": " + ", ".join(f"{PL[k]['name']} {a}->{b}" for k,(a,b) in MOVED.items()) if MOVED else ""))
except Exception as _e: print("Scout trade check skipped:",_e)
'''

_NEWS = r'''
# ---- Oct 17 (Dom): THE NEWS CHECK - the last 14 days of news on every man the Scout recommends ----
_NEWSIT=[]
try:
    _FDN=globals().get("_FD","/home/claude/domfantasy01/dk-feeds/feeds/")
    _now_u=dt.datetime.now(dt.timezone.utc); _seen=set()
    for _fn,_src in (("rotowire_history.jsonl","RotoWire"),("espn_news_history.jsonl","ESPN"),("news_extra_history.jsonl","PFT/RotoBaller")):
        try:
            for _l in open(_FDN+_fn):
                try: _j=json.loads(_l)
                except Exception: continue
                _t=str(_j.get("title") or ""); _pu=str(_j.get("published_utc") or "")
                if not _t or _t in _seen: continue
                try: _when=dt.datetime.fromisoformat(_pu.replace("Z","+00:00"))
                except Exception: continue
                if (_now_u-_when).days>14: continue
                _seen.add(_t)
                _src2=_src if _src!="PFT/RotoBaller" else ("PFT" if _j.get("source")=="pft" else "RotoBaller" if _j.get("source")=="rotoballer" else _src)
                _NEWSIT.append((_when," "+norm(_t+" "+str(_j.get("text") or ""))+" ",_t,_src2," "+norm(_t)+" "))
        except Exception: pass
    _NEWSIT.sort(key=lambda x:x[0])
    if not QUIET: print(f"Scout news check: {len(_NEWSIT)} items from the last 14 days")
except Exception as _e: print("Scout news check skipped:",_e)
_BADNEWS=re.compile(r"\b(injured reserve|placed on ir|to ir|on ir|surgery|procedure|out indefinitely|ruled out|will miss|miss(es)? (multiple|several|the next)|setback|released|waived|traded|trade (for|to|with)|acquire\w*|demoted|benched|suspend\w*|carted|fracture|torn|tear)\b")
def newscheck(p):
    """newest item mentioning him, and whether recent news (7 days) is bad; DEF and K are skipped"""
    if p["pos"] in ("DEF",) or not _NEWSIT: return None,False
    nk=" "+norm(p["name"])+" "
    hits=[x for x in _NEWSIT if nk in x[1]]
    if not hits: return "news: nothing on him in 14 days (RotoWire, ESPN, PFT, RotoBaller)",False
    # a flag needs the item to be ABOUT him: his name (or his last name, with his full name in the story) in the headline -
    # a list story that mentions forty players ("hot seat", "trade deadline") is not news about him
    ln=" "+norm(p["name"]).split()[-1]+" "
    about=[x for x in hits if nk in x[4] or ln in x[4]]
    bad=[x for x in about if (dt.datetime.now(dt.timezone.utc)-x[0]).days<=7 and (_BADNEWS.search(x[1]) or re.search(r"\bout\b",x[4]))]
    hits=about or hits
    x=bad[-1] if bad else hits[-1]
    d_=x[0].astimezone(dt.timezone(dt.timedelta(hours=-7)))
    line=f"{'NEWS FLAG - check before acting: ' if bad else 'news '}({x[3]}, {d_:%b} {d_.day}): {x[2]}"
    return line,bool(bad)
'''

patch(f"{R}/dksys/scout/scout_engine.py",[
 # 1 the trade check runs once every player is valued, before ownership is matched (so a moved man is found on his new team)
 ('def find(name,team,pos):\n', _TRADE + _NEWS + 'def find(name,team,pos):\n', 1),
 # every recommendation reason carries the trade note and the news check
 ('    if len(p["fp"])>=2 and np.mean(p["xv"] or [0])-np.mean(p["fp"])>=3: r.append(f"getting {np.mean(p[\'xv\']):.1f} expected but scoring {np.mean(p[\'fp\']):.1f}")\n    return r\n',
  '    if len(p["fp"])>=2 and np.mean(p["xv"] or [0])-np.mean(p["fp"])>=3: r.append(f"getting {np.mean(p[\'xv\']):.1f} expected but scoring {np.mean(p[\'fp\']):.1f}")\n'
  '    if p.get("moved"): r.append(p["moved"])                       # Oct 17 (Dom): the trade check\n'
  '    for _tc in p.get("tradecut",[]): r.append("door closing: "+_tc)\n'
  '    return r\n',1),
 # every recommendation carries the news check, and a flagged pick is never red
 ('    urg="red" if (need_red and min(fw)<=NOW+1) else "gold"\n    return dict(name=p["name"].replace(" defense"," DEF"),team=p["team"],pos=p["pos"],',
  '    urg="red" if (need_red and min(fw)<=NOW+1) else "gold"\n'
  '    _nl,_nb=newscheck(p)                                            # Oct 17 (Dom): the news check on every pickup\n'
  '    if _nl: why=why+"; "+_nl\n'
  '    if _nb or p.get("moved") or p.get("tradecut"): urg="gold"       # Oct 17 (Dom): check before acting\n'
  '    return dict(name=p["name"].replace(" defense"," DEF"),team=p["team"],pos=p["pos"],',1),
 # the text report's Gate 1 / Gate 2 lines carry it too
 ('    return f"{p[\'name\']}, {p[\'team\']} — scored {sc} — {e[\'acq\']} — {why}; helps {when}"\n',
  '    _nl,_nb=newscheck(p)                                            # Oct 17 (Dom): the news check\n'
  '    if _nl: why=why+"; "+_nl\n'
  '    return f"{p[\'name\']}, {p[\'team\']} — scored {sc} — {e[\'acq\']} — {why}; helps {when}"\n',1),
],"OCT17 trade check + news check")

# ---------- 3  DEFENSES ON WAIVERS (Dom, Oct 17) ----------
# Yahoo lists a defense on waivers by nickname ("Broncos/Oct 21") but the Scout keys defenses as "def den", so a defense
# on waivers printed as a free agent - the Broncos showed "Free agent" in DK IV while Yahoo had them on waivers until
# Tuesday (their game had kicked off). Nicknames now map to the Scout's key, so a defense's waiver date prints.
_NICK = ('{"cardinals":"ARI","falcons":"ATL","ravens":"BAL","bills":"BUF","panthers":"CAR","bears":"CHI","bengals":"CIN",'
         '"browns":"CLE","cowboys":"DAL","broncos":"DEN","lions":"DET","packers":"GB","texans":"HOU","colts":"IND",'
         '"jaguars":"JAX","chiefs":"KC","raiders":"LV","chargers":"LAC","rams":"LA","dolphins":"MIA","vikings":"MIN",'
         '"patriots":"NE","saints":"NO","giants":"NYG","jets":"NYJ","eagles":"PHI","steelers":"PIT","49ers":"SF",'
         '"seahawks":"SEA","buccaneers":"TB","titans":"TEN","commanders":"WAS"}')
patch(f"{R}/dksys/scout/scout_engine.py",[
 ('pbp=pd.read_csv(f"{D}/play_by_play_2026.csv.gz"',
  'for _nn,_aa in ' + _NICK + '.items():   # Oct 17 (Dom): a defense on waivers is found by its nickname\n'
  '    if _nn in WAIV: WAIV["def "+_aa.lower()]=WAIV[_nn]\n'
  'pbp=pd.read_csv(f"{D}/play_by_play_2026.csv.gz"',1),
],"OCT17 defenses on waivers")

# ---------- 4  THE PRE-KICKOFF CHECK (Dom, Oct 17) ----------
# Before every kickoff the Scout puts each of Dom's starters whose game hasn't started against the best healthy free
# agent at a spot he's eligible for, using THIS WEEK's numbers (Sleeper and Yahoo, plus Gotham for skill players).
# It flags a clear upgrade - better by 2+ points (Dom's noise line) on both Sleeper and Yahoo, or on Sleeper and Gotham
# when Yahoo has no number - and an empty seat (bye / out / nobody playing) that any healthy player would beat.
# Waiver players can't be added in time to start this week, so only free agents count; a free agent whose own game has
# already kicked off can't be started either. Defenses and kickers are in (the wire alert never saw them - that's how
# the Broncos over Seattle went unflagged on Thursday Oct 15). The flags ride the Scout board (prekick) to the alerts.
_PREKICK = r'''
# ---- Oct 17 (Dom): THE PRE-KICKOFF CHECK ----
PREKICK=[]
try:
    from zoneinfo import ZoneInfo as _ZI
    _NOWU=dt.datetime.now(dt.timezone.utc); _ET=_ZI("America/New_York"); _PT=_ZI("America/Los_Angeles")
    _KO={}
    for _r in games[games.week==NOW].itertuples():
        try:
            _k=dt.datetime.strptime(f"{_r.gameday} {_r.gametime}","%Y-%m-%d %H:%M").replace(tzinfo=_ET).astimezone(dt.timezone.utc)
            _KO[tm(_r.home_team)]=_k; _KO[tm(_r.away_team)]=_k
        except Exception: pass
    _LID={"DKI":"269381","DKII":"1519795","DKIII":"1507991","DKIV":"864215"}[LGK]
    _M=json.load(open(f"{L}/meter/meter_wk{NOW}.json")); _ML=_M["leagues"]; _ML=_ML if isinstance(_ML,list) else list(_ML.values())
    _LG=[x for x in _ML if str(x.get("league_id"))==_LID][0]
    _EL={"QB":("QB",),"RB":("RB",),"WR":("WR",),"TE":("TE",),"W/R/T":("RB","WR","TE"),"Q/W/R/T":("QB","RB","WR","TE"),"K":("K",),"DEF":("DEF",)}
    _pool=[]
    for _k,_p in PL.items():
        if _k in taken or _k[0] in WAIV or norm(_p["name"]) in SEASON_OUT or killed(_p["name"]): continue
        if NOW in byes.get(_p["team"],[]) or NOW<back(_p): continue
        _ko=_KO.get(_p["team"])
        if not _ko or _ko<=_NOWU: continue                       # no game, or his game already started
        _kd=_p["pos"] in ("K","DEF")
        _s=_SLKD.get(_kdkey(_p)) if _kd else _SLPPR.get(norm(_p["name"]))
        if _s is None: continue
        _pool.append(dict(k=_k,p=_p,sl=_s,ya=_YP.get((_ypk(_p),NOW)),go=None if _kd else _GOT.get(norm(_p["name"])),ko=_ko))
    _used=set()
    for _st in _LG["starters"]["me"]:
        _slot=_st.get("slot"); _ok=_EL.get(_slot)
        if not _ok or _st.get("gs") not in (None,"pre"): continue        # his game started: locked
        _empty=(not _st.get("player")) or (_st.get("status") or "").upper() in ("O","IR","IR-R","NA","SUSP","PUP") or ((_st.get("sleeper") or 0)<=0 and (_st.get("yahoo") or 0)<=0)
        _best=None
        for _c in _pool:
            if _c["p"]["pos"] not in _ok or _c["k"] in _used: continue
            if _empty:
                _m=_c["sl"]; _why="empty seat"
                if _m<3: continue
            else:
                _ms=_c["sl"]-(_st.get("sleeper") or 0)
                _my=None if (_c["ya"] is None or _st.get("yahoo") is None) else _c["ya"]-_st["yahoo"]
                _mg=None if (_c["go"] is None or _st.get("gotham") is None) else _c["go"]-_st["gotham"]
                if _ms<2: continue
                if _my is not None:
                    if _my<2: continue
                    _why="Sleeper and Yahoo agree"
                elif _mg is not None:
                    if _mg<2: continue
                    _why="Sleeper and Gotham agree (no Yahoo number)"
                else:
                    _why="Sleeper only (no Yahoo or Gotham number)"
                _m=_ms
            if not _best or _m>_best[0]: _best=(_m,_c,_why)
        if not _best: continue
        _m,_c,_why=_best; _used.add(_c["k"]); _p=_c["p"]
        _sko=_KO.get(tm(_st.get("team") or ""))
        _dl=min([x for x in (_c["ko"],_sko) if x] or [_c["ko"]])
        _g2=next((e for e in G2 if e["k"]==_c["k"]),None)
        _nl,_nb=newscheck(_p)
        PREKICK.append(dict(slot=_slot,starter=_st.get("player") or "(empty)",starter_team=_st.get("team"),
            starter_nums=dict(sleeper=_st.get("sleeper"),yahoo=_st.get("yahoo"),gotham=_st.get("gotham")),
            name=_p["name"].replace(" defense"," DEF"),team=_p["team"],pos=_p["pos"],
            nums=dict(sleeper=round(_c["sl"],1),yahoo=None if _c["ya"] is None else round(_c["ya"],1),gotham=None if _c["go"] is None else round(_c["go"],1)),
            gain=round(_m,1),basis=_why,empty=bool(_empty),
            color=("gold" if (_nb or _why.startswith("Sleeper only")) else "red"),
            deadline_utc=_dl.isoformat(),deadline_pt=f"{_dl.astimezone(_PT):%a} {_dl.astimezone(_PT).hour%12 or 12}:{_dl.astimezone(_PT):%M} {'AM' if _dl.astimezone(_PT).hour<12 else 'PM'} PT",
            ros_gain=round(sum(max(0.0,v) for v in _g2["g"].values()),1) if _g2 else None,
            news=_nl or "",checked=NOWPT.strftime('%a %b %d, %I:%M %p PT').replace(' 0',' ')))
    if not QUIET: print(f"Pre-kickoff check: {len(PREKICK)} upgrade(s) - " + "; ".join(f"{x['name']} over {x['starter']} (+{x['gain']}, {x['basis']}, by {x['deadline_pt']})" for x in PREKICK))
except Exception as _e: print("Pre-kickoff check skipped:",type(_e).__name__,_e)
BOARD["prekick"]=PREKICK
'''
patch(f"{R}/dksys/scout/scout_engine.py",[
 ('json.dump(BOARD,open(f"{H}/scout_board_{LGK}.json","w"),indent=1)',
  _PREKICK + 'json.dump(BOARD,open(f"{H}/scout_board_{LGK}.json","w"),indent=1)',1),
],"OCT17 pre-kickoff check")
