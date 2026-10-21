# v23 LIVE DATA (Thu Oct 8 2026) - exec'd by fieldpos23 right after the shared drawing chain, before any page code.
# Everything weekly comes from ONE file: /home/claude/dksys/data/latest/meter/meter_wk<W>.json (built by meter_data.py),
# plus the Gotham tables and the NFL schedule. Nothing here is typed per week.
import json as _j23, glob as _g23, os as _o23, csv as _c23, datetime as _d23
_o23.environ.setdefault("DK_NOMATCH","1"); _o23.environ.setdefault("DK_DECAY","1"); _o23.environ.setdefault("DK_KSHR_QB","250")   # Gotham settings for the engine import
_MF23=sorted(_g23.glob("/home/claude/dksys/data/latest/meter/meter_wk*.json"),key=lambda p:int(p.split("_wk")[1].split(".")[0]))[-1]
MTR=_j23.load(open(_MF23)); WEEKN=MTR["week"]; _o23.environ["DK_WEEK"]=str(WEEKN)
YMISS={}   # Oct 9: Yahoo's posted win % missing -> the dial uses the win % implied by Yahoo's own projected totals, and says so
for _lb23,_L23 in MTR["leagues"].items():
    _n23=_L23["needles"]
    if _n23.get("yahoo") is None and _n23.get("yahoo_from_spread") is not None: _n23["yahoo"]=_n23["yahoo_from_spread"]; YMISS[_lb23]=True
def _hm23(k):
    p=MTR["sources"].get(k,{}).get("pulled_pt") or "?"
    return p if p=="?" else " ".join(p.split()[:3])+", "+" ".join(p.split()[-3:-1])
YREAD="Yahoo read "+_hm23("yahoo_matchups")
# the schedule, fresh (the chain's copy was the Oct 2 role-watch file)
G=[r for r in _c23.DictReader(open('/home/claude/dksys/data/latest/games.csv')) if r['season']=='2026' and r['game_type']=='REG']
SCH={}
for r in G:
    SCH.setdefault(r['away_team'],{})[int(r['week'])]=r['home_team'];SCH.setdefault(r['home_team'],{})[int(r['week'])]=r['away_team']
_TOG={"LAR":"LA","JAC":"JAX","WSH":"WAS"}                    # meter team codes -> schedule codes
def _gt(t): return _TOG.get(str(t or ""),str(t or ""))
print("V23 LIVE week",WEEKN,"|",YREAD,"| meter",_MF23)
