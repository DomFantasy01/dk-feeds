# THE READ STAMP (Dom, Sat Oct 10 2026): "Fri Oct. 9, 7:16 PM" - abbreviated day, month with its period, normal caps,
# Pacific. When every read in a line shares one date, the date leads once and the times follow; the moment one read is
# from another day, every read carries its own date, so a line never claims a date one of its reads doesn't have.
import datetime as _dsd
_DS_MON={1:"Jan.",2:"Feb.",3:"March",4:"April",5:"May",6:"June",7:"July",8:"Aug.",9:"Sept.",10:"Oct.",11:"Nov.",12:"Dec."}
def ds_parse(s,year=None):
    """'Fri Oct 09 07:16 PM PT' or 'Sat Oct 10 2026 09:50 AM PT' -> datetime (naive, Pacific). None if unreadable."""
    if not s or s=="?": return None
    p=s.replace(" PT","").split()
    try:
        yr=next((int(x) for x in p if len(x)==4 and x.isdigit()),year or _dsd.date.today().year)
        return _dsd.datetime.strptime(f"{p[1]} {int(p[2])} {yr} {p[-2]} {p[-1]}","%b %d %Y %I:%M %p")
    except Exception: return None
def ds_date(t): return f"{t:%a} {_DS_MON[t.month]} {t.day}"
def ds_time(t): return f"{t.hour%12 or 12}:{t:%M} {'AM' if t.hour<12 else 'PM'}"
def ds_full(t): return f"{ds_date(t)}, {ds_time(t)}"
def ds_line(pairs,tz=" PT"):
    """pairs = [(label, 'Fri Oct 09 07:16 PM PT'), ...] -> one honest line"""
    got=[(l,ds_parse(s)) for l,s in pairs]
    ok=[t for _,t in got if t]
    if ok and len({t.date() for t in ok})==1 and len(ok)==len(got):
        return ds_date(ok[0])+"  ·  "+"  ·  ".join(f"{l} {ds_time(t)}" for l,t in got)+tz
    return "  ·  ".join(f"{l} {ds_full(t) if t else 'not read'}" for l,t in got)+tz
