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
