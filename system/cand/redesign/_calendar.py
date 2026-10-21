# THE DISPATCH CALENDAR (Dom, Thu Oct 8 2026) - which extra page rides behind the front page, by Pacific weekday.
#   Monday     POST-MORTEM, provisional - marked NOT COMPLETE (Monday night still to play, stat fixes not settled)
#   Tuesday    POST-MORTEM, final edition
#   Wed - Thu  OUTLOOK - the week ahead, one lean page
#   Fri - Sun  neither
# DK_DAY=mon|tue|wed|thu|fri|sat|sun forces a day (testing only). Pacific time with daylight saving handled (Nov 1 included).
import os as _oc, datetime as _dc
from zoneinfo import ZoneInfo as _ZC
CAL_TZ=_ZC("America/Los_Angeles")
CAL_NOW=_dc.datetime.now(CAL_TZ)
_CDAYS=["mon","tue","wed","thu","fri","sat","sun"]
CAL_DOW=_CDAYS.index(_oc.environ["DK_DAY"]) if _oc.environ.get("DK_DAY") in _CDAYS else CAL_NOW.weekday()
PM_MODE={0:"provisional",1:"final"}.get(CAL_DOW)        # None = no Post-Mortem today
OUTLOOK_ON=CAL_DOW in (2,3)
print("CALENDAR",_CDAYS[CAL_DOW].upper(),"| post-mortem:",PM_MODE or "off","| outlook:","on" if OUTLOOK_ON else "off")
