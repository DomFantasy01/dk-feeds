# THE "AS OF" STAMP AND THE STOPLIGHT (Dom, Sat Oct 10 2026) - drawn on the subhead line of every masthead.
# As of = the moment this Dispatch was built (Pacific). The stoplight = how old the oldest of its three sources is at
# build time: green under 3 hours, amber 3 to 6, red past 6. Sources: Yahoo (matchups), Gotham, Sleeper - read from the
# same meter file every page uses, so every page shows the same light.
import datetime as _aod, json as _aoj, glob as _aog
from reportlab.lib.colors import HexColor as _AOH
_AO_PT=_aod.timezone(_aod.timedelta(hours=-7))
_AO_MON={1:"Jan.",2:"Feb.",3:"March",4:"April",5:"May",6:"June",7:"July",8:"Aug.",9:"Sept.",10:"Oct.",11:"Nov.",12:"Dec."}
def _ao_now(): return _aod.datetime.now(_AO_PT)
def _ao_fmt(t): return f"{t:%a} {_AO_MON[t.month]} {t.day}, {t.hour%12 or 12}:{t:%M} {'AM' if t.hour<12 else 'PM'} PT"
def _ao_parse(s,yr):
    try:
        p=s.replace(" PT","").split(); y=next((int(x) for x in p if len(x)==4 and x.isdigit()),yr)
        return _aod.datetime.strptime(f"{p[1]} {int(p[2])} {y} {p[-2]} {p[-1]}","%b %d %Y %I:%M %p").replace(tzinfo=_AO_PT)
    except Exception: return None
def asof_state():
    """(as-of text, light 'green'|'amber'|'red', oldest source label, its age in hours)"""
    now=_ao_now()
    try:
        f=sorted(_aog.glob("/home/claude/dksys/data/latest/meter/meter_wk*.json"),key=lambda p:int(p.split("_wk")[1].split(".")[0]))[-1]
        S=_aoj.load(open(f))["sources"]
        ages=[]
        for k,lab in (("yahoo_matchups","Yahoo"),("gotham","Gotham"),("sleeper_skill","Sleeper")):
            t=_ao_parse(S.get(k,{}).get("pulled_pt") or "",now.year)
            ages.append(((now-t).total_seconds()/3600 if t else 99.0,lab))
        h,lab=max(ages)
    except Exception: h,lab=99.0,"sources"
    light="green" if h<3 else ("amber" if h<6 else "red")
    return "As of "+_ao_fmt(now),light,lab,h
_AO_INK={"green":_AOH("#3FB36A"),"amber":_AOH("#F2B33D"),"red":_AOH("#E5484D")}
def stoplight(c,x,ymid,light,h=7.4):
    """a small horizontal three-lamp light; the live lamp lit with a soft halo, the other two dark. Returns its width."""
    r=h*.30; gap=h*.42; w=3*2*r+2*gap+h*.5
    c.saveState()
    c.setFillColor(_AOH("#0B1222")); c.setStrokeColor(_AOH("#3A4560")); c.setLineWidth(.6)
    c.roundRect(x,ymid-h/2,w,h,h/2,stroke=1,fill=1)
    for i,k in enumerate(("red","amber","green")):
        cx=x+h*.25+r+i*(2*r+gap)
        if k==light:
            col=_AO_INK[k]; c.setFillColor(col); c.setFillAlpha(.28); c.circle(cx,ymid,r*1.75,stroke=0,fill=1)
            c.setFillAlpha(1); c.circle(cx,ymid,r,stroke=0,fill=1)
        else:
            c.setFillColor(_AOH("#2A3347")); c.circle(cx,ymid,r,stroke=0,fill=1)
    c.restoreState(); return w
def asof_draw(c,x,y,font="PopM",sz=7.6,col=None):
    """draws '·  As of Sat Oct. 10, 7:52 PM PT  [light]' starting at x on baseline y; returns the end x"""
    t,light,lab,h=asof_state()
    s="  ·  "+t+"  "
    c.setFont(font,sz); c.setFillColor(col or _AOH("#E4E8F0")); c.drawString(x,y,s); x+=c.stringWidth(s,font,sz)
    return x+stoplight(c,x,y+sz*.34,light)
def asof_line(c,x,y,sub,xmax,font="PopM",sz=7.6,col=None):
    """the whole subhead tier: sub text, then '·  As of ...' and the light, fitted so it never runs into the puzzle"""
    t,light,lab,h=asof_state(); tail="  ·  "+t+"  "; lw=3*2*(7.4*.30)+2*(7.4*.42)+7.4*.5
    def width(s,f): return c.stringWidth(s+tail,font,f)+lw
    f=sz
    while width(sub,f)>xmax-x and f>6.6: f-=.1
    while width(sub,f)>xmax-x and len(sub)>8: sub=sub[:-2].rstrip(" ·,")+"…"
    c.setFont(font,f); c.setFillColor(col or _AOH("#E4E8F0")); c.drawString(x,y,sub+tail)
    return stoplight(c,x+c.stringWidth(sub+tail,font,f),y+f*.34,light)
