# Puts THE CALENDAR into the bundle's fieldpos23.py on GitHub's computer (Thu Oct 8 2026). Safe to run twice.
p="/home/claude/cand/redesign/fieldpos23.py"; s=open(p).read()
a='''# Post-Mortem rule (Dom, Oct 8): partial Tuesday, full Wednesday, gone Thursday through Monday.
_DOW=_d23.datetime.now(_PT23).weekday()      # Mon 0 .. Sun 6
PM_SHOW=_DOW in (1,2)
if PM_SHOW: print("POST-MORTEM day - page held until its own rebuild is done (it still carries Week 4 text)")
'''
b='''# THE CALENDAR (Dom, Thu Oct 8): Monday Post-Mortem provisional, Tuesday final, Wednesday-Thursday Outlook - right behind the front page.
exec(open("/home/claude/cand/redesign/_calendar.py").read())
if PM_MODE:
    exec(open("/home/claude/cand/redesign/_pm_auto.py").read()); postmortem_page(c,pg); c.showPage(); pg+=1
elif OUTLOOK_ON:
    exec(open("/home/claude/cand/redesign/_outlook.py").read()); outlook_page(c,pg); c.showPage(); pg+=1
'''
if b in s: print("   calendar: already in")
else:
    assert s.count(a)==1, "calendar patch: the old Post-Mortem rule was not found"
    open(p,"w").write(s.replace(a,b)); print("   calendar: Post-Mortem Mon/Tue, Outlook Wed/Thu")

# ---- Yahoo read times (Thu Oct 8): on GitHub's computer every file's disk time is the moment it was copied in, so the meter
# printed the build time as the Yahoo read time and could not tell an old read from a new one. The pull time written inside
# each file now wins; the disk time is only a fallback.
p="/home/claude/dksys/meter/meter_data.py"; s=open(p).read()
A='''def file_time(path):
    """pull time written in a file's own name (…_thu1050 / …T1830Z) beats the disk time when present"""
    return None'''
B='''def file_time(path):
    """the pull time written inside the file (header line, or "pulled_pt" in a JSON) beats the disk time when present"""
    try:
        head = open(path, errors="ignore").read(400)
        m = re.search(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (\\w{3}) (\\d{1,2}),?(?: (\\d{4}))? (\\d{1,2}):(\\d{2}) ([AP]M) PT", head)
        if not m: return None
        t = dt.datetime.strptime(f"{m.group(2)} {m.group(3)} {m.group(4) or NOW.year} {m.group(5)}:{m.group(6)} {m.group(7)}", "%b %d %Y %I:%M %p")
        return t.replace(tzinfo=PT)
    except Exception: return None'''
if "the pull time written inside the file" in s: print("   meter read times: already in")
else:
    for a,b in ((A,B),("    m = dt.datetime.fromtimestamp(os.path.getmtime(path), PT)","    m = file_time(path) or dt.datetime.fromtimestamp(os.path.getmtime(path), PT)"),
                ("    f = sorted(glob.glob(pattern), key=os.path.getmtime); return f[-1] if f else None",
                 "    f = sorted(glob.glob(pattern), key=lambda q: (file_time(q) or dt.datetime.fromtimestamp(os.path.getmtime(q), PT))); return f[-1] if f else None")):
        assert s.count(a)==1, "meter read-time patch: anchor not found"; s=s.replace(a,b)
    open(p,"w").write(s); print("   meter read times: taken from inside each Yahoo file")
