# ONE STATUS WORD (Dom, Tue Oct 13 2026) - FINAL, LIVE or UPCOMING, worked out once here in the meter and read by the
# front page, the Field Report scorecard and Dark Knight Live, so a league never reads settled in one place and live in another.
# Exec'd by meter_data.py just before it writes meter_wk<W>.json (uses its GW, LEAGUE_OUT and T).
#   a starter is DONE when his game is final (score posted, or 4 hours past kickoff), when he has no game (bye, empty slot),
#   or when he is ruled out (O, IR, NA, SUSP, PUP) before his kickoff;
#   FINAL    = every starter on both sides is done;
#   LIVE     = not final, and at least one starter's game on either side has kicked off;
#   UPCOMING = no starter's game has kicked off yet.
import datetime as _sd
try:
    from zoneinfo import ZoneInfo as _ZI; _ET = _ZI("America/New_York")
except Exception:
    _ET = _sd.timezone(_sd.timedelta(hours=-4))
_UTC = _sd.timezone.utc
_NOWU = _sd.datetime.now(_UTC)
_GAME = {}
for _r in GW.itertuples():
    try:
        _ko = _sd.datetime.strptime(f"{_r.gameday} {_r.gametime}", "%Y-%m-%d %H:%M").replace(tzinfo=_ET).astimezone(_UTC)
    except Exception:
        continue
    _fin = (_r.result == _r.result) or _NOWU > _ko + _sd.timedelta(hours=4)
    for _tm in (_r.home_team, _r.away_team): _GAME[T(_tm)] = (_ko, _fin)
_OUTT = ("O", "IR", "IR-R", "NA", "SUSP", "SUS", "PUP")
def _pgs(p):
    g = _GAME.get(T(p.get("team") or ""))
    if g is None: return "nogame"
    ko, fin = g
    if fin: return "final"
    if _NOWU >= ko: return "playing"
    if (p.get("status") or "").strip().upper() in _OUTT: return "out"
    return "pre"
for _lab, _L in LEAGUE_OUT.items():
    _all = []
    for _side in ("me", "op"):
        for _p in _L["starters"][_side]:
            _p["gs"] = _pgs(_p); _all.append(_p["gs"])
    _done = sum(1 for g in _all if g in ("final", "nogame", "out"))
    _kick = sum(1 for g in _all if g in ("final", "playing"))
    _L["state"] = "FINAL" if _all and _done == len(_all) else ("LIVE" if _kick else "UPCOMING")
    _L["state_note"] = f"{_done} of {len(_all)} starters done, {_kick} games kicked off"
print("STATE", {k: v["state"] for k, v in LEAGUE_OUT.items()})
