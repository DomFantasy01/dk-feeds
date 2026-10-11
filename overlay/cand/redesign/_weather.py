# GAME WEATHER (Dom, Sun Oct 11 2026) - exec'd by _oct10_fr.py. Every build pulls the kickoff forecast for each game of the
# week from Open-Meteo (free, no key; the forecast reaches about 7 days out, so it tracks all week and sharpens toward
# Sunday). Each player's row on the Field Report gets a small picture beside his opponent: a dome for an indoor game, a
# roof with an opening for a retractable roof (open or closed is decided on game day), and for an outdoor game the sky
# at kickoff - sun, cloud, rain, snow - with wind streaks when it blows. A picture turns red only when the weather can
# move the game: sustained wind 15 mph+, gusts 25 mph+, rain 60%+ or a tenth of an inch, any snow, 25F or colder.
import json as _wj, os as _wo, datetime as _wdt, urllib.request as _wu
from zoneinfo import ZoneInfo as _WZ
import pandas as _wpd
_WX_HOME={"ARI":(33.5276,-112.2626),"ATL":(33.7554,-84.4008),"BAL":(39.2780,-76.6227),"BUF":(42.7738,-78.7870),"CAR":(35.2258,-80.8528),
 "CHI":(41.8623,-87.6167),"CIN":(39.0955,-84.5161),"CLE":(41.5061,-81.6995),"DAL":(32.7473,-97.0945),"DEN":(39.7439,-105.0201),
 "DET":(42.3400,-83.0456),"GB":(44.5013,-88.0622),"HOU":(29.6847,-95.4107),"IND":(39.7601,-86.1639),"JAX":(30.3239,-81.6373),
 "KC":(39.0489,-94.4839),"LV":(36.0909,-115.1833),"LAC":(33.9535,-118.3392),"LA":(33.9535,-118.3392),"MIA":(25.9580,-80.2389),
 "MIN":(44.9737,-93.2581),"NE":(42.0909,-71.2643),"NO":(29.9511,-90.0812),"NYG":(40.8135,-74.0745),"NYJ":(40.8135,-74.0745),
 "PHI":(39.9008,-75.1675),"PIT":(40.4468,-80.0158),"SF":(37.4030,-121.9700),"SEA":(47.5952,-122.3316),"TB":(27.9759,-82.5033),
 "TEN":(36.1665,-86.7713),"WAS":(38.9078,-76.8645)}
_WX_PLACE={"Tottenham Hotspur Stadium":(51.6043,-0.0664),"Wembley Stadium":(51.5560,-0.2796),"Stade de France":(48.9245,2.3602),
 "Bernabeu":(40.4531,-3.6883),"FC Bayern Munich Stadium":(48.2188,11.6247),"Estadio Banorte":(19.3029,-99.1505),
 "Maracana Stadium":(-22.9122,-43.2302),"Melbourne Cricket Ground":(-37.8200,144.9834)}
_WX_RETRACT={"ARI","ATL","DAL","HOU","IND"}          # roofs that open; nflverse leaves them blank until game day
_WX_DOME={"DET","LV","LA","LAC","MIN","NO"}           # fixed roofs
WX={}; WX_PULLED=None; WX_NOTE="no forecast reached this build"
def _wx_roof(r):
    rf=str(r.roof) if r.roof==r.roof else ""
    if rf in ("dome","closed") or (not rf and r.home_team in _WX_DOME): return "dome"
    if rf=="open" or (not rf and r.home_team in _WX_RETRACT): return "retract"
    return "out"
def _wx_load(week):
    global WX,WX_PULLED,WX_NOTE
    try:
        g=_wpd.read_csv("/home/claude/dksys/data/latest/games.csv",low_memory=False); g=g[(g.season==g.season.max())&(g.week==week)]
    except Exception as ex: WX_NOTE="schedule not read ("+str(ex)[:40]+")"; return
    now=_wdt.datetime.now(_wdt.timezone.utc); games=[]
    for r in g.itertuples():
        try: ko=_wdt.datetime.strptime(f"{r.gameday} {r.gametime}","%Y-%m-%d %H:%M").replace(tzinfo=_WZ("America/New_York")).astimezone(_wdt.timezone.utc)
        except Exception: continue
        if ko<now-_wdt.timedelta(hours=4): continue                     # already played
        roof=_wx_roof(r); ll=_WX_PLACE.get(str(r.stadium)) or _WX_HOME.get(r.home_team)
        games.append(dict(home=r.home_team,away=r.away_team,ko=ko,roof=roof,ll=ll))
    out=[x for x in games if x["roof"]!="dome" and x["ll"] and x["ko"]<now+_wdt.timedelta(days=7)]
    fc={}
    src=_wo.environ.get("DK_WX_FILE")
    try:
        if src: fc=_wj.load(open(src))
        elif out:
            u=("https://api.open-meteo.com/v1/forecast?latitude="+",".join(f"{x['ll'][0]:.4f}" for x in out)+"&longitude="+",".join(f"{x['ll'][1]:.4f}" for x in out)+
               "&hourly=temperature_2m,precipitation_probability,precipitation,snowfall,wind_speed_10m,wind_gusts_10m,cloud_cover"
               "&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=GMT&forecast_days=8")
            js=_wj.loads(_wu.urlopen(u,timeout=20).read()); js=js if isinstance(js,list) else [js]
            fc={x["home"]:j["hourly"] for x,j in zip(out,js)}
            _wj.dump(fc,open("/home/claude/dksys/data/latest/weather_hourly.json","w"))
        WX_PULLED=now
    except Exception as ex: WX_NOTE="forecast not reached this build ("+str(ex)[:50]+")"; fc={}
    for x in games:
        w=dict(roof=x["roof"],ko=x["ko"].isoformat(),game=f"{x['away']} @ {x['home']}",sky=None,flag=False,why=[])
        H=fc.get(x["home"])
        if x["roof"]!="dome" and H:
            k=x["ko"].strftime("%Y-%m-%dT%H:00"); i=H["time"].index(k) if k in H["time"] else None
            if i is not None:
                sl=lambda key:[v for v in H[key][i:i+4] if v is not None]
                t=min(sl("temperature_2m") or [60]); pp=max(sl("precipitation_probability") or [0]); pr=sum(sl("precipitation")); sn=sum(sl("snowfall") or [0])
                ws=max(sl("wind_speed_10m") or [0]); wg=max(sl("wind_gusts_10m") or [0]); cc=max(sl("cloud_cover") or [0])
                w.update(temp=round(t),pop=pp,rain=round(pr,2),snow=round(sn,2),wind=round(ws),gust=round(wg))
                w["sky"]="snow" if sn>0 else ("rain" if (pp>=40 or pr>=.02) else ("cloud" if cc>=60 else "sun"))
                if ws>=15: w["why"].append(f"wind {round(ws)} mph")
                if wg>=25: w["why"].append(f"gusts {round(wg)}")
                if pp>=60 or pr>=.1: w["why"].append(f"rain {pp}%")
                if sn>0: w["why"].append("snow")
                if t<=25: w["why"].append(f"{round(t)}F")
                w["flag"]=bool(w["why"]); w["windy"]=ws>=15 or wg>=25
        WX[x["home"]]=w; WX[x["away"]]=w
    if WX_PULLED:
        pt=WX_PULLED.astimezone(_WZ("America/Los_Angeles"))
        bad=sorted({f"{x['away']} at {x['home']}" for x in games if WX[x['home']].get("flag")})
        WX_NOTE=(f"the picture beside each opponent is the sky at kickoff, Open-Meteo {pt:%a} {pt.hour%12 or 12}:{pt:%M} {'AM' if pt.hour<12 else 'PM'} PT. "
                 "Red = it can move the game"+(" ("+", ".join(bad)+")" if bad else " (none this week)")+". Dome = indoors.")
    try:                                                                  # the same read for Dark Knight Live (Oct 11): dispatch_run.sh copies it to dispatch_out
        _wj.dump({"week":int(week),"pulled":WX_PULLED.isoformat() if WX_PULLED else None,"teams":WX},
                 open(f"/home/claude/dksys/data/latest/weather_wk{int(week)}.json","w"))
    except Exception: pass
# ---- the pictures (about the size of a lowercase letter; centered at cx, cy)
def wx_icon(c,cx,cy,w,s=7.0):
    from reportlab.lib.colors import HexColor as _H
    if not w: return 0
    red=_H("#C62828"); ink=red if w.get("flag") else _H("#5A6478"); c.saveState(); c.setLineCap(1); c.setLineJoin(1)
    if w["roof"]=="dome" or (w["roof"]=="retract" and not w.get("sky")):
        c.setFillColor(_H("#8C96A8") if w["roof"]=="dome" else _H("#FFFFFF")); c.setStrokeColor(_H("#5A6478")); c.setLineWidth(.7)
        p=c.beginPath(); p.moveTo(cx+s*.55,cy-s*.32); p.arcTo(cx-s*.55,cy-s*.32-s*.55,cx+s*.55,cy-s*.32+s*.55,0,180); p.close()
        c.drawPath(p,stroke=1,fill=1)
        if w["roof"]=="retract": c.setStrokeColor(_H("#FFFFFF")); c.setLineWidth(1.4); c.line(cx-s*.08,cy+s*.2,cx+s*.12,cy+s*.33)
        c.setStrokeColor(_H("#5A6478")); c.setLineWidth(.7); c.line(cx-s*.62,cy-s*.32,cx+s*.62,cy-s*.32)
        c.restoreState(); return s*1.3
    sky=w.get("sky") or "sun"
    if w["roof"]=="retract":                                              # a roof that may open: a small arch over the sky
        c.setStrokeColor(_H("#8C96A8")); c.setLineWidth(.6); c.arc(cx-s*.7,cy-s*.2,cx+s*.7,cy+s*.95,20,140)
    if sky=="sun":
        c.setFillColor(_H("#E8A317") if not w.get("flag") else red); c.circle(cx,cy,s*.24,stroke=0,fill=1)
        c.setStrokeColor(_H("#E8A317") if not w.get("flag") else red); c.setLineWidth(.6)
        import math as _m
        for k in range(8):
            a=k*_m.pi/4; c.line(cx+s*.33*_m.cos(a),cy+s*.33*_m.sin(a),cx+s*.46*_m.cos(a),cy+s*.46*_m.sin(a))
    else:
        c.setFillColor(_H("#B9C1CF") if sky=="cloud" else ink)
        for dx,dy,r in ((-.2,.02,.2),(.08,.12,.26),(.3,0,.18)): c.circle(cx+s*dx,cy+s*dy,s*r,stroke=0,fill=1)
        c.rect(cx-s*.2,cy-s*.18,s*.5,s*.2,stroke=0,fill=1)
        if sky=="rain":
            c.setStrokeColor(_H("#2F6FD6") if not w.get("flag") else red); c.setLineWidth(.75)
            for dx in (-.15,.08,.31): c.line(cx+s*dx,cy-s*.3,cx+s*(dx-.07),cy-s*.52)
        if sky=="snow":
            c.setStrokeColor(red); c.setLineWidth(.6)
            for dx in (-.12,.22): c.line(cx+s*dx-s*.08,cy-s*.42,cx+s*dx+s*.08,cy-s*.42); c.line(cx+s*dx,cy-s*.5,cx+s*dx,cy-s*.34)
    wid=s*1.0
    if w.get("windy"):                                                    # wind streaks beside the sky
        x0=cx+s*.62; c.setStrokeColor(red if w.get("flag") else ink); c.setLineWidth(.75)
        for dy,ln in ((.2,.62),(0,.8),(-.2,.5)): c.line(x0,cy+s*dy,x0+s*ln,cy+s*dy)
        wid+=s*.9
    c.restoreState(); return wid
