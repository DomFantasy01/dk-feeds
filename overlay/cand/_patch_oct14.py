# THE OCT 14 SCOUT FIXES (Dom, Wed Oct 14 2026) - applied to the Scout on every build, after the Oct 10 batch.
# Safe to run twice (marker). Every anchor must match exactly once or the build stops - the Scout is never half-patched.
#  1  INJURED FREE AGENTS: the Scout read injury status only from Yahoo tags (rostered men) and nflverse's weekly files,
#     which lag - it ranked Tyquan Thornton first after he went on IR. Now ESPN's injury list and Sleeper's injury list
#     (both pulled every 30 min by the feed job) count too: IR/PUP/reserve = on IR, Out/Doubtful/Suspended = out this week.
#     The worse of the two sources wins. A Yahoo tag still wins for a man Yahoo has tagged.
#  2  ONE-GAME SPIKES: one bad game was already lifted to his next-worst; now one big game is also cut to his next-best
#     (4+ games). Calibrated Oct 14 against ESPN + Sleeper Week 6 projections: spike players read +1.3 pts a game too high
#     before, -0.1 after (183 players; everyone else's error also went down).
#  3  NAMES WITH INITIALS: "D.K. Metcalf" and "DK Metcalf" were two different men to the Scout (snap share read 0%).
#     Initials now join up ("d k metcalf" -> "dk metcalf") everywhere the Scout matches names.
import os
R=os.environ.get("DK_ROOT","/home/claude")
def patch(path,pairs,mark):
    s=open(path).read()
    if mark in s: print("   oct14:",path.split("/")[-1],"already in"); return
    for a,b,n in pairs:
        k=s.count(a); assert k==n,f"oct14 patch: {path.split('/')[-1]}: anchor found {k}x, expected {n}: {a[:80]}"
        s=s.replace(a,b)
    open(path,"w").write(s+f"\n# {mark}\n"); print("   oct14:",path.split("/")[-1],"patched (injured free agents, one-game spikes, initials)")

patch(f"{R}/dksys/scout/scout_engine.py",[
 # 3 initials join up
 ('return " ".join(n.split())',
  'return re.sub(r"\\b([a-z])\\s+(?=[a-z]\\b)",r"\\1"," ".join(n.split()))   # Oct 14: "d k metcalf" -> "dk metcalf"',1),
 ('sn=pd.read_csv(f"{D}/snap_counts_2026.csv"); sn=sn[sn.game_type=="REG"]',
  'sn=pd.read_csv(f"{D}/snap_counts_2026.csv"); sn=sn[sn.game_type=="REG"].copy(); sn["_nk"]=sn.player.map(norm)',1),
 ('_sp=sn[(sn.player==name)&(sn.team==team)]',
  '_sp=sn[(sn._nk==norm(name))&(sn.team==team)]',1),
 # 2 one big game cut to his next-best
 ('    if len(v)>=4: lo=sorted(v)[1]; i=v.index(min(v)); v=v[:i]+[lo]+v[i+1:]\n',
  '    if len(v)>=4: lo=sorted(v)[1]; i=v.index(min(v)); v=v[:i]+[lo]+v[i+1:]\n'
  '    if len(v)>=4: hi=sorted(v)[-2]; i=v.index(max(v)); v=v[:i]+[hi]+v[i+1:]   # Oct 14 (Dom): one big game is cut to his next-best\n',1),
 # 1 injured free agents
 ('def _newsback(p):\n',
  'EXTINJ={}\n'
  'try:   # Oct 14 (Dom): ESPN + Sleeper injury lists, so a hurt free agent is never ranked as available\n'
  '    _FDX=globals().get("_FD","/home/claude/domfantasy01/dk-feeds/feeds/"); _SEV={"O":1,"IR":2,"NA":3}\n'
  '    def _xadd(nm,pos,t):\n'
  '        if t and nm: k=(norm(nm),str(pos).upper()); EXTINJ[k]=t if _SEV[t]>_SEV.get(EXTINJ.get(k),0) else EXTINJ[k]\n'
  '    for _x in json.load(open(_FDX+"espn_injuries.json")).get("players",[]):\n'
  '        _s=str(_x.get("status","")).lower()\n'
  '        _xadd(_x.get("name"),_x.get("pos"),"NA" if "ret" in _s else "IR" if ("reserve" in _s or "pup" in _s or "physically" in _s) else "O" if _s in ("out","doubtful","suspension","suspended") else "")\n'
  '    _sl=json.load(open(_FDX+"sleeper_injuries.json")).get("players",{}); _sl=_sl.values() if isinstance(_sl,dict) else _sl\n'
  '    for _x in _sl:\n'
  '        _s=str(_x.get("inj") or "").upper()\n'
  '        _xadd(_x.get("name"),_x.get("pos"),"IR" if _s in ("IR","PUP","COV") else "O" if _s in ("OUT","SUS","DOUBTFUL") else "")\n'
  '    if not QUIET: print(f"Scout injury lists: {len(EXTINJ)} men out or on IR (ESPN + Sleeper)")\n'
  'except Exception as _e: print("Scout injury lists skipped:",_e)\n'
  'def _newsback(p):\n',1),
 ('def back(p,ytag=""):\n',
  'def back(p,ytag=""):\n'
  '    if not ytag: ytag=EXTINJ.get((norm(p["name"]),p.get("pos","")),"")   # Oct 14: no Yahoo tag -> ESPN/Sleeper status\n',1),
 ('if ytag in ("IR","IR-R","PUP-R") or p.get("nflstat")=="RES": return max(p["last"]+5,NOW+1)',
  'if ytag in ("IR","IR-R","PUP-R") or p.get("nflstat")=="RES": return max(p["last"]+5,NOW+1,_newsback(p))',1),
 ("({'IR minimum' if p['nflstat']=='RES' else 'listed Out'})",
  "({'IR minimum' if (p['nflstat']=='RES' or EXTINJ.get((norm(p['name']),p['pos']))=='IR') else 'listed Out'})",1),
],"OCT14 scout injured FAs + spikes + initials")
