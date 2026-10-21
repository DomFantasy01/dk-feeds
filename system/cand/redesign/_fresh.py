# Freshness stamps (Dom's doctrine): one "as of" per block, date AND time, always printed.
# Times come from the source files themselves (or the ledger for browser reads). Gold = more than a day old at build.
import json,os,datetime as _dt
_PT=_dt.timezone(_dt.timedelta(hours=-7))
FRESH=json.load(open("/home/claude/dksys/data/state/fresh.json"))
BUILT=_dt.datetime.now(_PT)
def ftime(k):
    e=FRESH[k]
    return _dt.datetime.fromisoformat(e["at"]).astimezone(_PT) if "at" in e else _dt.datetime.fromtimestamp(os.path.getmtime(e["path"]),_PT)
def fmt(t,day=True):
    h=t.strftime("%I:%M %p").lstrip("0")
    _mo={9:"Sept.",3:"March",4:"April",5:"May",6:"June",7:"July"}.get(t.month,t.strftime("%b")+".")   # Oct 10: "Oct." with its period
    return (t.strftime("%a ")+_mo+" "+str(t.day)+", "+h).upper()
def built_str(): return "built "+fmt(BUILT).title().replace(" Am"," AM").replace(" Pm"," PM")+" PT"
def _clock(c,x,y,r,col):
    c.setStrokeColor(col);c.setLineWidth(.7);c.circle(x,y,r,stroke=1,fill=0)
    c.setLineCap(1);c.line(x,y,x,y+r*.62);c.line(x,y,x+r*.5,y);c.setLineCap(0)
def stamp(c,xr,y,keys,dark=False,sz=6.2):
    """right-aligned at xr. Fresh sources (a day old or less at build) share one time - the oldest of them, no label.
    Anything older is named on its own, in gold, so a block that couldn't refresh says so plainly."""
    ink=H("#C9CFDB") if dark else H("#4A4538");gold=H("#F2C14E") if dark else GOLDR
    ts=[(ftime(k),FRESH[k]["label"]) for k in keys]
    fresh=[t for t,_ in ts if (BUILT-t).total_seconds()<=86400]
    stale=sorted([(t,l) for t,l in ts if (BUILT-t).total_seconds()>86400],reverse=True)
    parts=[("AS OF  ","Pop",ink)]
    if fresh: parts.append((fmt(min(fresh)),"PopB",ink))
    for t,lab in stale:
        if len(parts)>1: parts.append(("  ·  ","Pop",ink))
        parts.append((lab+" ","Pop",gold));parts.append((fmt(t),"PopB",gold))
    w=sum(c.stringWidth(s,f,sz) for s,f,_ in parts);x=xr-w
    _clock(c,x-sz*.95,y+sz*.33,sz*.52,ink)
    for s,f,col in parts: txt(c,x,y,s,f,sz,col);x+=c.stringWidth(s,f,sz)
    return xr-w-sz*1.6
_WEEKK=["yahoo","stats","engine","market"];_SEASK=["schedule","stats"]
SECSTAMP={"week":{"STARTERS":_WEEKK,"BENCH":_WEEKK,"IR":_WEEKK},
          "season":{"THE SEASON AHEAD  ·  STARTERS":_SEASK,"BENCH":_SEASK,"IR":_SEASK}}
STMODE="week"
SECOFF={"THE SEASON AHEAD  ·  STARTERS":66}          # clear the WEEKS 4-17 chip
_section0=section
def section(c,y,title,sub,col):
    _section0(c,y,title,sub,col)
    k=SECSTAMP.get(STMODE,{}).get(title)
    if k: stamp(c,W-M-SECOFF.get(title,0),y+1,k)

# OCT10 fresh
