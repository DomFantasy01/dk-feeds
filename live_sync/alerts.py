# Dark Knight Live alerts (Dom, Oct 13 2026).
# One alert per player per event. Raw feed hits make the alert; Gotham only adds the numbers, it never gates.
# Colors: red = act now, gold = monitor, grey = noted. Green is never an input color: an alert the latest build
# no longer raises is marked resolved and the page shows it green in history.
# Usage: python3 alerts.py radar.json actions.json meter.json alarm.json prev_alerts.json(or -) out.json [--feeds DIR] [--scout DIR]
# Oct 14 11:40 (Dom): GOTHAM DRIVES the wire alerts (it's the only forward-looking source); Yahoo and Sleeper are shown
# beside it, never vote, and the alert is labeled 'all three agree' / 'Gotham + one' / 'Gotham only'. Your own bench is
# checked first (no alert for a free agent your bench already beats). Waiver players are flagged too, labeled as a claim.
# Cards: no raw feed markup, no before/after row without a real after-value, source = where the tip came from,
# and no 'worth knowing, no action' feed cards (a name in a start/sit list is not news).
import json, re, sys, datetime as dt

radar_f, act_f, meter_f, alarm_f, prev_f, out_f = sys.argv[1:7]
J = lambda f: json.load(open(f))
R, A, M = J(radar_f), J(act_f), J(meter_f)
try: AL = J(alarm_f)
except Exception: AL = {}
try: PREV = J(prev_f) if prev_f != "-" else {}
except Exception: PREV = {}
W = M.get("week") or A.get("week")
NOW = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
SRC = "Dark Knight Dispatch"
BUILT = M.get("built_pt") or A.get("built_pt") or ""   # Oct 24: the meter is rebuilt earlier in the same build; the actions file is the previous build's, so it gave a stale second time stamp
FLOOR = 2.0   # Dom's noise floor: a gain under 2 Gotham points is noted, not flagged

def slug(*p): return re.sub(r"[^a-z0-9]+", "-", "-".join(str(x) for x in p).lower()).strip("-")[:90]
def f1(x): return "unknown" if x is None else f"{x:.1f}"
ELIG = {"QB": {"QB"}, "RB": {"RB"}, "WR": {"WR"}, "TE": {"TE"}, "K": {"K"}, "DEF": {"DEF"},
        "W/R/T": {"WR", "RB", "TE"}, "W/R": {"WR", "RB"}, "W/T": {"WR", "TE"},
        "Q/W/R/T": {"QB", "WR", "RB", "TE"}}
def ok(pos, slot): return pos in ELIG.get(slot, {slot})
def g(p): v = p.get("gotham"); return v if isinstance(v, (int, float)) else None
def healthy(p): return (p.get("status") or "").upper() not in ("O", "IR", "IR-R", "NA", "SUSP", "PUP", "D")
import html as _html
def clean(t):   # Oct 14 (Dom): raw feed markup ("<img width=135 ...") never reaches a card, even when the feed cut the tag off
    t = re.sub(r"<[^>]*(?:>|$)", " ", t or "")
    return re.sub(r"\s+", " ", _html.unescape(t)).strip()
SRCN = {"rotoballer": "RotoBaller", "pft": "PFT", "rotowire": "RotoWire", "espn": "ESPN", "espn news": "ESPN news"}
def srcname(x): return SRCN.get((x or "").strip().lower(), x or "")
def feedline(n0): return f"{srcname(n0.get('src'))}, {n0.get('t')}" if n0 else ""

ITEMS = []
def add(**k):
    k.setdefault("src", SRC); k.setdefault("built", BUILT)
    if k.get("ba") and k["ba"].get("after") is None: k["ba"] = None     # Oct 14 (Dom): "before -> unknown" tells him nothing
    k["what"] = clean(k.get("what"))
    ITEMS.append(k)

# ---------- lineup holes and other ranked actions (from the Dispatch's Action Items) ----------
used = {}   # league -> bench players already proposed as a fill
for it in sorted(A.get("items", []), key=lambda x: x["rank"]):
    lg, who, kind = it["lg"], it["who"], it["kind"]
    L = M["leagues"].get(lg, {}); RL = R["leagues"].get(lg, {})
    color = "red" if it["rank"] == 1 else ("gold" if it["rank"] in (2, 3) else "grey")
    tie, fix, ba, receipts = "", "", None, []
    if it["rank"] == 1:
        st = next((p for p in L.get("starters", {}).get("me", []) if p["player"] == who), None)
        if st:
            slot, hole_g = st["slot"], (g(st) or 0.0)
            pro = "It" if slot == "DEF" else "He"
            tie = f"Your {slot} starter in {lg}. " + (f"{pro} has no game this week, so {pro.lower()} scores 0." if kind == "bye"
                  else f"{pro} scores 0 if left in the lineup.")
            if kind != "bye" and hole_g:
                receipts.append(f"Gotham still has him at {f1(hole_g)} because ESPN and Sleeper don't both list him out yet")
            # bench first: a bench player who fits the slot directly, or by sliding a flex starter into the hole
            cands = []
            for b in L.get("bench", []):
                if b.get("slot") == "IR" or not healthy(b) or g(b) is None or b["player"] in used.get(lg, set()): continue
                if ok(b.get("pos"), slot): cands.append((g(b), b, None))
                for f in L["starters"]["me"]:
                    if f is st or f["slot"] == slot or g(f) is None: continue
                    if ok(f.get("pos"), slot) and ok(b.get("pos"), f["slot"]) and f.get("gs") == "pre":
                        cands.append((g(b), b, f))
            cands.sort(key=lambda c: -c[0])
            wire = [p for p in RL.get("in", []) if ok(p.get("pos"), slot) and g(p) is not None]
            wire.sort(key=lambda p: -g(p))
            tot = ((L.get("totals_set") or L.get("totals") or {}).get("gotham") or [None])[0]   # as set: the meter's totals now assume the best lineup
            if cands:
                gb, b, f = cands[0]
                used.setdefault(lg, set()).add(b["player"])
                fix = (f"Bench: start {b['player']} ({b['pos']}, Gotham {f1(gb)})" +
                       (f" in the {f['slot']} and slide {f['player']} into the {slot}" if f else f" at {slot}") + ".")
                if wire and g(wire[0]) - gb >= FLOOR:
                    fix += f" The wire has better: {wire[0]['name']} (Gotham {f1(g(wire[0]))}), but that costs a pickup."
                elif wire:
                    fix += f" Best on the wire is {wire[0]['name']} (Gotham {f1(g(wire[0]))}), no better."
                after_g = gb
            else:
                fix = f"Nobody on your bench can play {slot}."
                claim = next((x for x in A["items"] if x["lg"] == lg and x["kind"] == "claim"
                              and slot.rstrip("0123456789") in x["what"]), None)
                if wire:
                    fix += f" Wire: {wire[0]['name']} ({wire[0]['pos']}, {wire[0].get('team','')}, Gotham {f1(g(wire[0]))})."
                    after_g = g(wire[0])
                else:
                    fix += " The Scout has no ranked free agent at that spot (unknown) - pick the best one Yahoo shows."
                    after_g = None
                if claim: fix += f" The Scout's waiver pick: {claim['who']}."
            if tot is not None:
                before = tot - hole_g
                ba = {"label": f"{lg} lineup, Gotham points",
                      "before": round(before, 1),
                      "after": None if after_g is None else round(before + after_g, 1)}
            ba_win = "Win chance after the move: unknown until the next build."
        else:
            tie = f"Your starter in {lg}."
            ba_win = ""
        news = next((p for p in RL.get("own", []) if p["name"] == who), None)
        n0 = next((n for n in (news or {}).get("news", []) if n.get("grade") == "bad"), {}) if kind != "bye" else {}
        add(id=slug("w", W, lg, kind, who), color=color, lg=lg, who=who, kind=kind,
            title=it["what"].split(". ")[0] + ".",
            what=it["what"], tie=tie, fix=fix, ba=ba, receipts=receipts + ([ba_win] if ba_win else []),
            by=it.get("by"), feed=feedline(n0), feed_title=(n0 or {}).get("title"))
    else:
        add(id=slug("w", W, lg, kind, who), color=color, lg=lg, who=who, kind=kind,
            title=it["what"].split(". ")[0] + ".", what=it["what"],
            tie=f"{lg} roster move.", fix=it["what"], ba=None, receipts=[], by=it.get("by"), feed="")

covered = {(x["lg"], x["who"]) for x in ITEMS}

def _when(s):
    try: return dt.datetime.fromisoformat((s or "").replace("Z", "+00:00"))
    except Exception: return None
def _pt(d):
    return d.astimezone(dt.timezone(dt.timedelta(hours=-7))).strftime("%a %b %-d %-I:%M %p PT")
# ---------- Yahoo's live roster read (the Scout's files): who's taken, who's on waivers ----------
SCOUT = sys.argv[sys.argv.index("--scout") + 1] if "--scout" in sys.argv else None
LGN = {"DK I": 1, "DK II": 2, "DK III": 3, "DK IV": 4}
def _rd(n, kind):
    import os, urllib.request, time
    for d in [SCOUT, os.path.join(os.path.dirname(os.path.abspath(radar_f)), "..", "yahoo_drop", "scout")]:
        if d and os.path.exists(os.path.join(d, f"dk{n}_{kind}.txt")): return open(os.path.join(d, f"dk{n}_{kind}.txt")).read()
    try:
        u = f"https://raw.githubusercontent.com/DomFantasy01/dk-feeds/main/yahoo_drop/scout/dk{n}_{kind}.txt?t={int(time.time())}"
        return urllib.request.urlopen(u, timeout=20).read().decode()
    except Exception: return ""
# Oct 25: Sleeper "Zonovan Knight" = Yahoo/nflverse "Bam Knight" - one man; without this the alerts called Dom's own starter a free agent
_NICK = {"zonovan knight": "bam knight"}
def _nm(s):
    k = re.sub(r"[^a-z ]", "", re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", "", (s or "").lower())).strip()
    return _NICK.get(k, k)
OWN = {}
for lg_, n_ in LGN.items():
    ro, wv = _rd(n_, "rosters_live"), _rd(n_, "waivers")
    if not ro: continue
    stamp = (re.search(r"read(?: live)? (\w{3} \w{3} \d+.*? PT)", ro) or [None, "time unknown"])[1]   # Oct 29: the API read says "Yahoo API read Thu ..."
    taken = {_nm(l.split("|")[2]) for l in ro.splitlines() if l and not l.startswith("#") and l.count("|") >= 4}
    wl_ = {}
    for l in wv.splitlines():
        if l.startswith("#"): continue
        for e in l.split("|"):
            if "/" in e: nm_, dte = e.rsplit("/", 1); wl_[_nm(nm_)] = dte.strip()
    OWN[lg_] = (taken, wl_, stamp)
def ownership(lg, name):
    if lg not in OWN: return None
    taken, wl_, stamp = OWN[lg]; k = _nm(name)
    if k in taken: return ("taken", "", f"rostered by another team, read {stamp}")
    if k in wl_: return ("waivers", wl_[k], f"on waivers until {wl_[k]}, read {stamp}")
    return ("free", "", f"not rostered and not on the waiver list (it shows the top 15), read {stamp}")
def agree(ws, fs, wy, fy):   # wire/bench man vs your starter on the two sources that only show, never vote
    parts, votes = [], 0
    for lab, a, b in (("Sleeper", ws, fs), ("Yahoo", wy, fy)):
        if a is None or b is None:
            parts.append(f"{lab} {'not read' if a is None else f'{a:.1f}'} vs {'not read' if b is None else f'{b:.1f}'}"); continue
        parts.append(f"{lab} {a:.1f} vs {b:.1f}"); votes += a > b
    return votes, " \u00b7 ".join(parts)
def wl(lg, name):
    for p in R.get("leagues", {}).get(lg, {}).get("own", []):
        if p.get("name") == name and isinstance(p.get("workload"), str): return p["workload"]
    return "unknown"
# ---------- Oct 29 (Dom): THE ALERT BAR, WHOSE PLAYER, ALL FOUR NUMBERS ----------
# "If just one alerts to that, it's probably adequate." A pickup/start alert fires when ANY ONE source - Ratcliffe (FTN),
# Koerner (FantasyLabs), Yahoo or Gotham - has the man at least 15% AND at least 2 points a week better than the starter
# he'd replace (2 points is Dom's noise line, measured per week he'd start, never a rest-of-season total), or when he
# fills a real hole (bye, out). All four numbers are shown, Ratcliffe first. Under the bar it does not reach Dom -
# a riser with a real reason (a starter ahead of him out, a bigger role, work climbing) gets a separate RISING card.
import os as _o2, csv as _c2
BAR_PCT, BAR_PTS = 0.15, 2.0
_ROOT = _o2.environ.get("DK_ROOT", "/home/claude")
_LGN = {"DK I": "1", "DK II": "2", "DK III": "3", "DK IV": "4"}
_RAW = "https://raw.githubusercontent.com/DomFantasy01/dk-feeds/main/"
def _rawtxt(rel):   # Oct 29: the hourly Live pass runs outside the repo - fall back to GitHub's copy
    import urllib.request, time
    try: return urllib.request.urlopen(f"{_RAW}{rel}?t={int(time.time())}", timeout=40).read().decode()
    except Exception: return ""
_HERE = _o2.path.join(_o2.path.dirname(_o2.path.abspath(radar_f)), "..")
def _ldcsv(f):
    for d in (_ROOT + "/dksys/data/latest/", _o2.path.join(_HERE, "dispatch_out") + "/"):
        if _o2.path.exists(d + f): return list(_c2.DictReader(open(d + f)))
    t = _rawtxt("dispatch_out/" + f)
    return list(_c2.DictReader(t.splitlines())) if t else []
def _fl(v):
    try: return float(v) if v not in ("", None, "nan") else None
    except Exception: return None
RAT, KOR, YPJ, RAT_AT, KOR_AT = {}, {}, {}, "", ""
for r in _ldcsv("ftn_scored.csv"):
    RAT[(str(r.get("lg")), _nm(r.get("name")))] = (_fl(r.get("wk")), _fl(r.get("ros_pg"))); RAT_AT = r.get("read_pt") or RAT_AT
for r in _ldcsv("koerner_scored.csv"):
    KOR[(str(r.get("lg")), _nm(r.get("name")))] = _fl(r.get("wk")); KOR_AT = r.get("read_pt") or KOR_AT
YP_AT = ""
for _n2 in "1234":
    _t2 = ""
    for _d2 in [SCOUT, _o2.path.join(_o2.path.dirname(_o2.path.abspath(radar_f)), "..", "yahoo_drop", "scout")]:
        _p2 = _o2.path.join(_d2 or "", f"yproj_dk{_n2}.txt")
        if _d2 and _o2.path.exists(_p2): _t2 = open(_p2).read(); break
    if not _t2: _t2 = _rawtxt(f"yahoo_drop/scout/yproj_dk{_n2}.txt")
    for l in _t2.splitlines():
        if l.startswith("#"): YP_AT = (re.search(r"read live (.+? PT)", l) or [None, YP_AT])[1]; continue
        x = l.split("|")
        if len(x) >= 5 and str(x[0]) == str(W): YPJ[(_n2, _nm(x[1]))] = _fl(x[4])
GOT = {}
for _lg2, _RL2 in R.get("leagues", {}).items():
    for p in (_RL2.get("in") or []) + (_RL2.get("own") or []):
        if isinstance(p.get("gotham"), (int, float)): GOT[(_LGN.get(_lg2), _nm(p.get("name")))] = p["gotham"]
for _lg2, _L2 in M.get("leagues", {}).items():
    for p in (_L2.get("starters") or {}).get("me", []) + (_L2.get("bench") or []) + (_L2.get("starters") or {}).get("op", []):
        if isinstance(p.get("gotham"), (int, float)): GOT[(_LGN.get(_lg2), _nm(p.get("player")))] = p["gotham"]
def nums(lg, name, p=None):
    """This week's four numbers for a man in one league: Ratcliffe, Koerner, Yahoo, Gotham (None = that source has no number)."""
    n, k, p = _LGN.get(lg), _nm(name), p or {}
    pick = lambda a, b: a if isinstance(a, (int, float)) else b
    return {"ratcliffe": pick(p.get("ratcliffe"), (RAT.get((n, k)) or (None, None))[0]),
            "koerner": pick(p.get("koerner"), KOR.get((n, k))),
            "yahoo": pick(p.get("yahoo"), YPJ.get((n, k))),
            "gotham": pick(p.get("gotham"), GOT.get((n, k)))}
NAMES = {"ratcliffe": "Ratcliffe", "koerner": "Koerner", "yahoo": "Yahoo", "gotham": "Gotham"}
def bar(cn, sn):
    """Sources where the candidate clears 15% AND 2 points a week over the starter. [] = he doesn't reach Dom."""
    out = []
    for s in NAMES:
        a, b = cn.get(s), sn.get(s)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) and a - b >= BAR_PTS and a >= b * (1 + BAR_PCT): out.append(s)
    return out
def numline(cn, sn, sname="your starter"):
    return "This week, him vs " + sname + ": " + " · ".join(
        f"{NAMES[s]} {f1(cn.get(s)) if cn.get(s) is not None else 'no number'} vs {f1(sn.get(s)) if sn.get(s) is not None else 'no number'}" for s in NAMES)
def barline(ok_):
    return ("Clears the bar (15% and 2+ points this week) on " + ", ".join(NAMES[s] for s in ok_) + ("" if len(ok_) > 1 else " only - one source is enough to talk it through") + ".") if ok_ else ""
def srcages():
    return f"Numbers: Ratcliffe read {RAT_AT or 'unknown'} · Koerner read {KOR_AT or 'unknown'} · Yahoo read {YP_AT or 'unknown'} · Gotham built {BUILT or 'unknown'}"
# whose player: Yahoo's API read (yahoo_api/latest.json) names every team in every league
YA = {}
for _d2 in [_o2.path.join(_o2.path.dirname(_o2.path.abspath(radar_f)), "..", "yahoo_api", "latest.json")]:
    try: YA = json.load(open(_d2))
    except Exception:
        try: YA = json.loads(_rawtxt("yahoo_api/latest.json") or "{}")
        except Exception: YA = {}
YA_AT = YA.get("read_pt") or ""
_TEAMOF = {}
for _lk2, _YL in (YA.get("leagues") or {}).items():
    _lab2 = {"DKI": "DK I", "DKII": "DK II", "DKIII": "DK III", "DKIV": "DK IV"}.get(_lk2)
    for _tm in _YL.get("teams") or []:
        for _pl in _tm.get("players") or []:
            _TEAMOF[(_lab2, _nm(_pl.get("name")))] = (_tm.get("id"), _tm.get("name"), _pl.get("slot"), _YL.get("me"))
    for _wv in _YL.get("waivers") or []:
        _TEAMOF.setdefault((_lab2, _nm(_wv.get("name"))), ("W", _wv.get("clears"), None, _YL.get("me")))
def own_tag(lg, name, hint=None):
    """Whose man he is, said first on every card: YOUR PLAYER / OPPONENT / ANOTHER TEAM / FREE AGENT / ON WAIVERS (+ back from IR, new signing)."""
    t = _TEAMOF.get((lg, _nm(name)))
    opp = (M.get("leagues", {}).get(lg) or {}).get("opp") or ""
    if t and t[0] == "W": base = f"On waivers until {t[1]}"
    elif t and t[0] == t[3]: base = "Your player" + (" (IR)" if t[2] == "IR" else " (bench)" if t[2] == "BN" else "")
    elif t and opp and t[1] == opp: base = f"Opponent this week: {opp}"
    elif t: base = f"Another team's player: {t[1]}"
    elif YA: base = "Free agent"
    else: base = "Owner unknown (no Yahoo read)"
    return base + (f" · {hint}" if hint else "")
RISERS = []    # (lg, radar item, his numbers, starter's numbers, starter) - under the bar this week; the RISING check weighs them
BENCH_BEATS = {}

# ---------- the Radar: your roster, the wire, your opponent ----------
for lg, RL in R.get("leagues", {}).items():
    L = M["leagues"].get(lg, {})
    for p in RL.get("own", []):
        if (lg, p["name"]) in covered or not p.get("news"): continue
        mk, n0 = p.get("marker", {}), p["news"][0]
        grades = mk.get("grades", [])
        starter = p.get("slot") not in ("BN", "IR")
        if "bad" in grades and mk.get("color") == "red":
            color = "red" if starter else "grey"
        elif "caution" in grades and mk.get("color") in ("red", "gold"):
            color = "gold" if starter else "grey"
        else:
            continue
        add(id=slug("w", W, lg, "news", p["name"], n0.get("t")), color=color, lg=lg, who=p["name"], kind="news",
            title=(n0.get('title') if p['name'] in (n0.get('title') or '') else f"{p['name']}: {n0.get('title')}"),
            what=n0.get("text") or n0.get("title"),
            tie=(f"Your {p['slot']} starter in {lg}." if starter else f"On your {lg} {'IR' if p.get('slot')=='IR' else 'bench'}; costs you nothing this week."),
            fix=("Check his status before kickoff and have a bench fill ready if he sits." if starter
                 else ("Nothing to do now. Consider IR or a drop if the seat is needed." if "bad" in grades else "Nothing to do now.")),
            ba={"label": f"his Gotham points", "before": g(p), "after": None} if starter else None,
            receipts=[f"Workload last 5: {p.get('workload') or 'unknown'}"], by=None,
            feed=feedline(n0), feed_title=n0.get("title"))
    hole_fill = {}
    for x in ITEMS:
        if x["lg"] == lg and x.get("ba") and x["kind"] in ("out", "bye"):
            hole_fill[x["who"]] = (x["ba"]["after"] or 0) - (x["ba"]["before"] or 0)
    # Oct 14 (Dom): Gotham drives; Yahoo and Sleeper are shown, not counted as votes. Bench first. Waivers flagged as a claim.
    mine = {x["player"]: x for x in L.get("starters", {}).get("me", []) + L.get("bench", [])}
    bench = [x for x in L.get("bench", []) if x.get("slot") != "IR" and healthy(x) and g(x) is not None]
    for p in RL.get("in", []):
        fl = p.get("floor") or {}
        if not fl.get("name"): continue                        # Oct 29: no Gotham gate any more - the bar below asks all four sources
        if fl.get("name") in hole_fill: continue   # that hole's alert already weighs the wire against the bench fill
        own_st = ownership(lg, p["name"])
        if own_st and own_st[0] == "taken": continue           # Yahoo's live read: someone already rosters him
        better = max((x for x in bench if x.get("pos") == p.get("pos") and g(p) is not None and g(x) >= g(p)), key=g, default=None)
        if better:                                             # your bench already beats him: no pickup alert
            BENCH_BEATS.setdefault(lg, []).append((p["name"], better["player"])); continue
        base = fl.get("gotham") or 0
        gain = (g(p) or 0) - base
        n0 = p["news"][0] if p.get("news") else {}
        fp = mine.get(fl.get("name"), {})
        # Oct 16 (Dom): never weigh a pickup against a starter whose game has already started - his score is locked
        # (Sutton's final 3.9 on Thursday read as "Antonio Williams beats him by 3.5").
        if fp.get("gs") not in (None, "pre"): continue
        cn_, sn_ = nums(lg, p["name"], p), nums(lg, fl.get("name"), fp)
        ok_ = bar(cn_, sn_)
        if not ok_: continue                                   # Oct 29 (Dom): under 15% / 2 points on every source - don't tell him
        tag = "clears the bar on " + ", ".join(NAMES[s_] for s_ in ok_)
        cmp_ = numline(cn_, sn_, fl.get("name"))
        if own_st and own_st[0] == "waivers":
            kind_l, how = "On waivers", f"Waiver claim: he clears {own_st[1]}, so you have to win the claim, and adding him means dropping someone."
        elif own_st:
            kind_l, how = "Free agent", "Not on Yahoo's waiver list, so an instant add, but adding him means dropping someone."
        else:
            kind_l, how = "Free agent?", "Yahoo's roster read wasn't available, so it isn't confirmed he's still out there."
        why = [re.sub(r"^opening: (.+?) \u2014 (.+)$", r"Opening: \1 is \2, which frees up work", w) for w in (p.get("why") or [])]
        add(id=slug("w", W, lg, "in", p["name"]), color="gold", lg=lg, who=p["name"],
            kind="wire", title=f"{kind_l}: {p['name']} ({p['pos']}, {p.get('team','')}) over your {fl.get('name')} this week ({tag})",
            what="; ".join(why) or "On the Scout's list.",
            tie=f"Your weakest {p['pos']} option in {lg} is {fl.get('name')}.",
            fix=f"Talk it through: {'claim' if kind_l == 'On waivers' else 'add'} {p['name']} and start him over {fl.get('name')}? {how} Full workup and a live Yahoo check first.",
            ba=None,
            receipts=[cmp_, barline(ok_),
                      f"Workload last 5 (the work Gotham's number is built on): {p.get('workload') or 'unknown'}",
                      f"Yahoo roster read: {own_st[2] if own_st else 'not available'}"],
            by=("before waivers clear " + own_st[1]) if own_st and own_st[0] == "waivers" else None,
            feed=feedline(n0), feed_title=n0.get("title"), src="the Radar's wire list, with Ratcliffe, Koerner, Yahoo and Gotham")
    # your own bench vs your own starters, Gotham-driven like the wire (Oct 14: the bench check's other half)
    used_b = set()
    for st in L.get("starters", {}).get("me", []):
        if st.get("gs") != "pre" or g(st) is None or st.get("slot") in ("QB", "K", "DEF", "Q/W/R/T"): continue
        c, ok_ = None, []
        for x_ in sorted((x for x in bench if x["player"] not in used_b and ok(x.get("pos"), st["slot"])), key=lambda x: -(x.get("ratcliffe") or g(x) or 0)):
            ok_ = bar(nums(lg, x_["player"], x_), nums(lg, st["player"], st))
            if ok_: c = x_; break
        if not c: continue
        used_b.add(c["player"])
        cmp_ = numline(nums(lg, c["player"], c), nums(lg, st["player"], st), st["player"])
        tag = "clears the bar on " + ", ".join(NAMES[s_] for s_ in ok_)
        gain = (c.get("ratcliffe") or g(c) or 0) - (st.get("ratcliffe") or g(st) or 0)
        add(id=slug("w", W, lg, "bench", c["player"], st["player"]), color="gold", lg=lg, who=c["player"], kind="bench",
            title=f"Your bench's {c['player']} over your {st['slot']} {st['player']} this week ({tag})",
            what=f"Ratcliffe has {c['player']} at {f1(c.get('ratcliffe'))} and {st['player']} at {f1(st.get('ratcliffe'))} this week.",
            tie=f"Both are already on your {lg} roster: no pickup, no drop.",
            fix=f"Your call: start {c['player']} over {st['player']}?" + ("" if "ratcliffe" in ok_ else " Ratcliffe doesn't see it - find out why first."),
            ba=None,
            receipts=[cmp_, barline(ok_),
                      "Workload last 5: " + ", ".join(f"{q['player']} {q.get('workload') or wl(lg, q['player'])}" for q in (c, st)).replace(" unknown", " not in this build")],
            by="before kickoff", feed="", src="your bench vs your starters, Ratcliffe, Koerner, Yahoo and Gotham")
    for p in RL.get("opp", []):
        mk = p.get("marker", {})
        if mk.get("color") != "red" or not p.get("news"): continue
        n0 = p["news"][0]
        add(id=slug("w", W, lg, "opp", p["name"], n0.get("t")), color="grey", lg=lg, who=p["name"], kind="opp",
            title=f"Opponent's {p['pos']} " + (n0.get('title') if p['name'] in (n0.get('title') or '') else f"{p['name']}: {n0.get('title')}"), what=n0.get("text") or "",
            tie=f"Starts for {RL.get('opponent')}, your {lg} opponent.", fix="Nothing for you to do.",
            ba=None, receipts=[], by=None, feed=feedline(n0), feed_title=n0.get("title"))
for n in AL.get("notes", []):
    m = re.match(r"(DK [IV]+): opponent starter (.+?) \((\w+)\) has no game", n)
    if m:
        lg, who = m.group(1), m.group(2) + (" defense" if " " not in m.group(2) else "")
        add(id=slug("w", W, lg, "oppbye", who), color="grey", lg=lg, who=who, kind="opp",
            title=f"Opponent's {who} has no game this week", what=n, tie=f"Your {lg} opponent must replace him.",
            fix="Nothing for you to do.", ba=None, receipts=[], by=None, feed="")

# ---------- raw feed hits (Dom, Oct 13 afternoon): the 30-minute fast lane ----------
# With --feeds DIR, every news item from the last 48 hours in the raw feeds (RotoWire, ESPN news, PFT, RotoBaller,
# ESPN injury list) that names one of YOUR players (starters and bench, all four leagues) or an opponent's starter
# becomes an alert by itself - the feed hit triggers it; Gotham only adds numbers. Starter + bad news = red,
# starter + caution = gold, everything else = noted. Items the Dispatch already raised are not repeated.
FEEDS = sys.argv[sys.argv.index("--feeds") + 1] if "--feeds" in sys.argv else None
BAD = re.compile(r"\b(released|releases|release|waived|waives|cut by|move on from|moves on from|ruled out|out for|will not play|won't play|placed on (?:injured reserve|ir)|injured reserve|\bIR\b|season-ending|torn|tear|fracture|broken|surgery|concussion protocol|carted|suspended|expected to miss|will miss|out (?:multiple|several|indefinitely)|doubtful|high[- ]ankle)", re.I)
CAUTION = re.compile(r"\b(questionable|limited|did not practice|DNP|game-time|day-to-day|week-to-week|uncertain|injur|hamstring|ankle|knee|groin|calf|shoulder|illness|back|quad|foot)\b", re.I)
GOOD = re.compile(r"\b(bigger|heavier|larger|expanded|increased|more) (?:workload|role|work|snaps|touches|usage|opportunit\w*)|\b(lead role|lead back|starting role|in line for|line for more|step into|steps into|takes over|take over|promoted|elevated|activated|returns? to practice|cleared|full practice|no injury designation|expected to play|will start|set to start|draws start|starting job|workhorse|operating as|remains (?:the |his team's |\w+'s )?(?:RB1|WR1|TE1|QB1|starter|lead|top|featured|No\. 1))\b", re.I)
def _norm(s): return re.sub(r"[^a-z ]", "", re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", "", (s or "").lower())).strip()
if FEEDS:
    import os
    cut = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=48)
    news = []
    def _ld(f):
        try: return json.load(open(os.path.join(FEEDS, f)))
        except Exception: return {}
    for f, label in (("rotowire_latest.json", "RotoWire"), ("espn_news.json", "ESPN news"), ("news_extra.json", None)):
        for it in _ld(f).get("items", []):
            news.append({"t": it.get("published_utc"), "src": label or it.get("source") or it.get("src") or "PFT/RotoBaller",
                         "title": clean(it.get("title")), "text": clean(it.get("text"))})
    for p in _ld("espn_injuries.json").get("players", []):
        if (p.get("status") or "").strip().lower() in ("active", ""): continue   # "Active" is not news
        news.append({"t": (p.get("date") or "").replace("Z", ":00Z") if len(p.get("date") or "") == 17 else p.get("date"),
                     "src": "ESPN injury list", "title": f"{p.get('name')}: {p.get('status')} ({p.get('type') or 'injury'})",
                     "text": p.get("detail") or "", "who": p.get("name")})
    def _when(s):
        try: return dt.datetime.fromisoformat((s or "").replace("Z", "+00:00"))
        except Exception: return None
    def _pt(d):
        return d.astimezone(dt.timezone(dt.timedelta(hours=-7))).strftime("%a %b %-d %-I:%M %p PT")
    people = []   # (league, name, role, slot, gotham)
    for lg, L in M["leagues"].items():
        for p in L.get("starters", {}).get("me", []): people.append((lg, p["player"], "starter", p["slot"], g(p)))
        for p in L.get("bench", []): people.append((lg, p["player"], "bench", p.get("slot"), g(p)))
        for p in L.get("starters", {}).get("op", []): people.append((lg, p["player"], "opp", p["slot"], g(p)))
    seen_titles, _best = {}, {}
    _built = _when(R.get("built_utc")) or cut
    for x in ITEMS: seen_titles.setdefault((x["lg"], x["who"]), []).append((x.get("feed_title") or "") + " " + (x.get("title") or ""))
    for n in news:
        d = _when(n["t"])
        if not d or d < cut or not n["title"]: continue
        blob = n["title"] + " " + n["text"]
        nb = " " + _norm(blob) + " "
        for lg, name, role, slot, gp in people:
            nn = _norm(name)
            if len(nn.split()) < 2: continue                        # team defenses: a team name matches every story about the team
            if not nn or (" " + nn + " ") not in " " + _norm(n["title"]) + " ": continue   # the player must be in the headline
            if n.get("who") and _norm(n["who"]) != nn: continue
            if any(n["title"][:60] in s for s in seen_titles.get((lg, name), [])): continue
            bad, caut = bool(BAD.search(blob)), bool(CAUTION.search(blob))
            # Oct 16 (Dom): "Swift: Bigger workload sans Monangai" came out red because the story says MONANGAI was
            # ruled out. The headline is written about its subject: when it carries opportunity language and no bad or
            # caution words of its own, the bad words belong to someone else and this is good news for our man.
            good = bool(GOOD.search(n["title"])) and not BAD.search(n["title"]) and not CAUTION.search(n["title"])
            if good: bad = caut = False
            if not (bad or caut or (good and role != "opp")): continue     # Oct 14 (Dom): a name in a start/sit list is not news - no 'worth knowing' cards
            sev = 2 if bad else 1 if caut else 0
            k = (lg, name)
            if k in _best and (_best[k][0], _best[k][1]) >= (sev, d): continue
            _best[k] = (sev, d, len(ITEMS))
            if good: color = "grey"   # noted, nothing to do - green stays reserved for a resolved alert
            elif role == "starter": color = "red" if bad else ("gold" if caut else "grey")
            else: color = "grey"
            tie = {"starter": f"Your {slot} starter in {lg}.", "bench": f"On your {lg} {'IR' if slot == 'IR' else 'bench'}.",
                   "opp": f"Starts for your {lg} opponent."}[role]
            gone = bool(re.search(r"\b(released|releases|release|waived|waives|cut by|move on from|moves on from)\b", blob, re.I))
            fix = ("Good news, nothing to do: more work for him." if good else
                   f"His team has let him go, so he scores 0 unless someone signs him. Bench him and pick up another {slot}."
                   if role == "starter" and gone else
                   "Check his status before kickoff and line up a bench fill; the next Dispatch build re-scores the lineup."
                   if role == "starter" else "Nothing to do now.")
            add(id=slug("w", W, lg, "feed", name, n["t"]), color=color, lg=lg, who=name, kind="feed",
                title=n["title"] if nn in _norm(n["title"]) else f"{name}: {n['title']}",
                what=(n["text"] or n["title"])[:400], tie=tie, fix=fix,
                ba=None,
                receipts=["Raw feed hit: the next Dispatch build confirms it against ESPN and Sleeper and re-scores your lineup"],
                by=None, feed=f"{srcname(n['src'])}, {_pt(d)}", feed_title=n["title"], news_t=d.isoformat(),
                src=f"{srcname(n['src'])} (raw feed, pulled every 30 minutes)")
            seen_titles.setdefault((lg, name), []).append(n["title"])
    _keep = {v[2] for v in _best.values()}
    _cov = {(x["lg"], x["who"]) for x in ITEMS if x["kind"] != "feed"}
    ITEMS[:] = [x for i, x in enumerate(ITEMS) if x["kind"] != "feed" or
                (i in _keep and not ((x["lg"], x["who"]) in _cov and _when(x["news_t"]) <= _built))]

# ---------- COMING ONLINE (Dom, Oct 14 noon): players Gotham can't rate yet ----------
# A man who hasn't played this season, hasn't played in 3+ weeks, or just changed teams has no recent games, so Gotham
# has no number for him and the wire alerts above never see him. This section catches him from the forward side:
# Sleeper's projection for this week (it moves the moment a team activates or signs someone) + nflverse's game log
# (who has actually played) + Yahoo's live roster read (is he available). Runs on every alert pass, fetching what it needs.
ONLINE_NOTE = ""
def _raw(rel, binary=False):
    import os, urllib.request, time
    for d in ([FEEDS] if FEEDS else []) + [os.path.join(os.path.dirname(os.path.abspath(radar_f)), "..", "feeds")]:
        p = os.path.join(d, rel)
        if os.path.exists(p): return open(p, "rb").read() if binary else open(p).read()
    u = f"https://raw.githubusercontent.com/DomFantasy01/dk-feeds/main/feeds/{rel}?t={int(time.time())}"
    b = urllib.request.urlopen(u, timeout=40).read()
    return b if binary else b.decode()
def _sleeper_proj(week):
    import csv, io, glob, os
    for d in ([FEEDS] if FEEDS else []) + [os.path.join(os.path.dirname(os.path.abspath(radar_f)), "..", "feeds")]:
        fs = sorted(glob.glob(os.path.join(d, "proj", "sleeper", f"wk{week}_*.csv")))
        if fs: return fs[-1].rsplit("_", 1)[1][:-4], list(csv.DictReader(open(fs[-1])))
    runs = [json.loads(l) for l in _raw("proj/status_log.jsonl").splitlines() if l.strip()]
    for r in reversed(runs):
        if str((r.get("sources", {}).get("sleeper", {}) or {}).get(f"wk{week}", "")).startswith("saved"):
            try: return r["run_utc"], list(csv.DictReader(io.StringIO(_raw(f"proj/sleeper/wk{week}_{r['run_utc']}.csv"))))
            except Exception: continue
    return None, []
try:
    import csv, io, urllib.request
    W_ = int(W)
    _stamp, _rows = _sleeper_proj(W_)
    if not _rows: raise RuntimeError(f"no Sleeper projection file for Week {W_}")
    _raw_g = urllib.request.urlopen(urllib.request.Request(
        "https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_2026.csv",
        headers={"User-Agent": "dk"}), timeout=90).read().decode()
    GP, LASTTM = {}, {}
    for r in csv.DictReader(io.StringIO(_raw_g)):
        if r.get("season_type") != "REG": continue
        k = _nm(r.get("player_display_name")); wk = int(r["week"])
        GP.setdefault(k, set()).add(wk)
        if wk >= max(GP[k]): LASTTM[k] = r.get("team")
    GMAX = max((max(v) for v in GP.values()), default=0)
    SP = {}
    try:
        for v in json.loads(_raw("sleeper_players_min.json")).get("players", {}).values():
            if v.get("name"): SP[_nm(v["name"])] = v
    except Exception: pass
    NEWS = []
    for f in ("rotowire_latest.json", "espn_news.json", "news_extra.json"):
        try:
            for it in json.loads(_raw(f)).get("items", []):
                NEWS.append((it.get("published_utc") or "", it.get("source") or it.get("src") or {"rotowire_latest.json": "RotoWire", "espn_news.json": "ESPN news"}.get(f, "PFT/RotoBaller"), clean(it.get("title"))))
        except Exception: pass
    NEWS.sort(reverse=True)
    PROJ = {_nm(r["name"]): r for r in _rows}
    def _pp(name):
        r = PROJ.get(_nm(name))
        try: return float(r["pts_ppr"]) if r and r.get("pts_ppr") not in ("", None) else None
        except Exception: return None
    _t = dt.datetime.strptime(_stamp, "%Y-%m-%dT%H%MZ").replace(tzinfo=dt.timezone.utc)
    _stamp_pt = _t.astimezone(dt.timezone(dt.timedelta(hours=-7))).strftime("%a %-I:%M %p PT")
    CAND = []
    for r in _rows:
        if r.get("pos") not in ("QB", "RB", "WR", "TE"): continue
        p = _pp(r["name"])
        if p is None or p < 3: continue
        k = _nm(r["name"]); g = GP.get(k, set())
        _tm = lambda t: {"LA": "LAR", "JAC": "JAX", "WSH": "WAS", "OAK": "LV", "SD": "LAC", "STL": "LAR"}.get(t or "", t or "")
        why = ("hasn't played a game this season" if not g else
               f"no game since Week {max(g)}" if max(g) <= GMAX - 2 else
               f"only one game this season (Week {max(g)}), just back" if len(g) == 1 else
               f"new team: played for {_tm(LASTTM.get(k))}, now {r.get('team')}" if LASTTM.get(k) and r.get("team") and _tm(LASTTM[k]) != _tm(r.get("team")) else None)
        if why: CAND.append((r, p, k, g, why))
    nonline = 0
    for lg, L in M["leagues"].items():
        mine_ = {_nm(x["player"]): x for x in L.get("starters", {}).get("me", []) + L.get("bench", [])}
        for r, p, k, g, why in CAND:
            name, pos, team = r["name"], r["pos"], r.get("team") or ""
            sp = SP.get(k, {}); inj = sp.get("inj") or ""
            news = next(((t, src, ttl) for t, src, ttl in NEWS if (" " + k + " ") in (" " + _nm(ttl) + " ")), None)
            starters = [x for x in L.get("starters", {}).get("me", []) if x.get("pos") == pos and x.get("slot") == pos and x.get("gs") in ("pre", None)]
            weak = min(((x, _pp(x["player"])) for x in starters if _pp(x["player"]) is not None), key=lambda t: t[1], default=(None, None))
            gl = ("Games this season: none" if not g else "Games this season: Week " + ", ".join(str(w) for w in sorted(g))) + f" (nflverse game log, through Week {GMAX})"
            st_line = f"Sleeper injury status: {inj}" if inj else "Sleeper injury status: none listed"
            if k in mine_:
                me = mine_[k]
                if me.get("slot") not in ("BN", "IR") and me in L.get("starters", {}).get("me", []): continue
                where = "IR" if me.get("slot") == "IR" or (me.get("status") or "").startswith("IR") else "bench"
                add(id=slug("w", W, lg, "online", name), color="gold", lg=lg, who=name, kind="online",
                    title=f"Coming back: your {where} player {name} ({pos}, {team}), {why}",
                    what=(news[2] if news else f"Sleeper now projects him {p:.1f} this week."),
                    tie=f"On your {lg} {where}.",
                    fix=(f"Sleeper projects {p:.1f} (PPR) this week" + (f", vs your weakest {pos} starter {weak[0]['player']} at {weak[1]:.1f}" if weak[0] else "") +
                         ". Gotham can't rate him yet (no recent games). " + ("If he's been activated, move him off IR and into a starting spot if he's the better play." if where == "IR" else "Consider starting him if his role is confirmed.")),
                    ba=None, receipts=[gl, st_line, f"Sleeper projection pulled {_stamp_pt}"], by="before kickoff",
                    feed=(f"{srcname(news[1])}, {_pt(_when(news[0]))}" if news and _when(news[0]) else ""), feed_title=(news[2] if news else None),
                    src="Sleeper projection + nflverse game log (Gotham can't rate him yet)")
                nonline += 1; continue
            own_st = ownership(lg, name)
            if not own_st or own_st[0] == "taken": continue
            _st = [x for x in L.get("starters", {}).get("me", []) if ok(pos, x.get("slot")) and x.get("gs") in ("pre", None) and x.get("slot") != "Q/W/R/T"]
            _st = min(_st, key=lambda x: nums(lg, x["player"], x).get("ratcliffe") or 99, default=None)
            cn_ = nums(lg, name); sn_ = nums(lg, _st["player"], _st) if _st else {}
            ok_ = bar(cn_, sn_)
            if not ok_ and not any(v is not None for v in cn_.values()) and weak[0] is not None:   # nobody but Sleeper rates him yet
                ok_ = ["sleeper"] if (p - weak[1] >= BAR_PTS and p >= weak[1] * (1 + BAR_PCT)) else []
            beats = bool(ok_)
            if not beats:
                RISERS.append((lg, {"name": name, "pos": pos, "team": team, "why": [why], "online": True}, cn_, sn_, _st)); continue
            kind_l = "On waivers" if own_st[0] == "waivers" else "Free agent"
            add(id=slug("w", W, lg, "online", name), color="gold" if beats else "grey", lg=lg, who=name, kind="online",
                title=f"Coming online: {name} ({pos}, {team}), {why}. {kind_l}" + (f", clears {own_st[1]}" if own_st[0] == "waivers" else ""),
                what=(news[2] if news else f"Sleeper now projects him {p:.1f} this week; Gotham has no recent games to rate him."),
                tie=(f"Would beat your weakest {pos} starter in {lg}, {weak[0]['player']} ({weak[1]:.1f})." if beats else
                     f"Not ahead of your {pos} starters yet" + (f" (weakest: {weak[0]['player']}, {weak[1]:.1f})" if weak[0] else "") + "; worth watching."),
                fix=(f"Your call: {'claim' if own_st[0] == 'waivers' else 'add'} {name} - Sleeper projects {p:.1f} (PPR). Confirm his role in the news first; Gotham can't rate him until he plays. Adding him means dropping someone."
                     if beats else "Nothing to do yet - watch his first game back."),
                ba=None, receipts=[numline(cn_, sn_, _st["player"]) if _st else "", ("Only Sleeper rates him so far" if ok_ == ["sleeper"] else barline(ok_)), gl, st_line, f"Sleeper projection pulled {_stamp_pt}", f"Yahoo roster read: {own_st[2]}"],
                by=(("before waivers clear " + own_st[1]) if own_st[0] == "waivers" else "before kickoff") if beats else None,
                feed=(f"{srcname(news[1])}, {_pt(_when(news[0]))}" if news and _when(news[0]) else ""), feed_title=(news[2] if news else None),
                src="Sleeper projection + nflverse game log (Gotham can't rate him yet)")
            nonline += 1
    ONLINE_NOTE = f"coming online: {len(CAND)} players checked, {nonline} alerts (Sleeper {_stamp_pt}, games through Week {GMAX})"
except Exception as e:
    ONLINE_NOTE = f"coming online check skipped: {type(e).__name__}: {e}"

# ---------- THE PRE-KICKOFF CHECK (Dom, Oct 17) ----------
# The Scout puts each starter whose game hasn't started against the best healthy free agent, on this week's numbers,
# defenses and kickers included (the wire alert above never saw them - the Broncos over Seattle went unflagged Oct 15).
# Each flag becomes an alert that stands until its deadline (the earlier of the two kickoffs), then drops off.
PREKICK_NOTE = ""
try:
    import os, urllib.request, time
    _now = dt.datetime.now(dt.timezone.utc)
    _dirs = [os.path.join(os.environ.get("DK_ROOT", "/home/claude"), "dksys", "scout"),
             os.path.join(os.path.dirname(os.path.abspath(act_f)), "scout_state")]
    _n = 0
    for _lk, _lab in (("DKI", "DK I"), ("DKII", "DK II"), ("DKIII", "DK III"), ("DKIV", "DK IV")):
        _b = None
        for _d in _dirs:
            _f = os.path.join(_d, f"scout_board_{_lk}.json")
            if os.path.exists(_f): _b = json.load(open(_f)); break
        if _b is None:
            _b = json.loads(urllib.request.urlopen(f"https://raw.githubusercontent.com/DomFantasy01/dk-feeds/main/dispatch_out/scout_state/scout_board_{_lk}.json?t={int(time.time())}", timeout=40).read())
        for _x in _b.get("prekick", []) or []:
            try: _dl = dt.datetime.fromisoformat(_x["deadline_utc"])
            except Exception: continue
            if _dl <= _now: continue                      # kickoff passed: nothing left to do
            _sn, _cn = _x.get("starter_nums") or {}, _x.get("nums") or {}
            _sn = dict(nums(_lab, _x.get("starter") or "", _sn) if _x.get("starter") else {}, **{k_: v_ for k_, v_ in _sn.items() if v_ is not None})
            _cn = dict(nums(_lab, _x["name"]), **{k_: v_ for k_, v_ in _cn.items() if v_ is not None})
            if not _x.get("empty") and not bar(_cn, _sn): continue   # Oct 29 (Dom): 15% and 2 points on at least one source
            _vs = " \u00b7 ".join(f"{NAMES[k]} {f1(_cn.get(k))} vs {f1(_sn.get(k))}" for k in NAMES if _cn.get(k) is not None or _sn.get(k) is not None)
            add(id=slug("pk", W, _lab, _x["slot"], _x["name"], _x["starter"]), color=_x.get("color", "gold"), lg=_lab, who=_x["name"], kind="prekick",
                title=(f"Before kickoff: {_x['name']} ({_x['pos']}, {_x['team']}) fills your empty {_x['slot']} seat" if _x.get("empty")
                       else f"Before kickoff: {_x['name']} ({_x['pos']}, {_x['team']}) beats your {_x['slot']} {_x['starter']} by {_x['gain']:.1f} this week"),
                what=f"Free agent, on this week's numbers ({_x['basis']})." + (f" Rest of season he adds ~{_x['ros_gain']:.0f} points." if _x.get("ros_gain") else ""),
                tie=f"Your {_x['slot']} starter in {_lab} is {_x['starter']}.",
                fix=f"Your call, before {_x['deadline_pt']}: add {_x['name']} and start him over {_x['starter']}. Adding him means dropping someone - pick the drop with the full workup.",
                ba=({"label": "that lineup spot this week, Ratcliffe points", "before": _sn.get("ratcliffe"), "after": _cn.get("ratcliffe")} if _cn.get("ratcliffe") is not None
                    else {"label": "that lineup spot this week, Sleeper points", "before": _sn.get("sleeper"), "after": _cn.get("sleeper")}),
                receipts=[f"This week: {_vs}", f"Scout check: {_x.get('checked','')}", _x.get("news") or "news: not checked"],
                by="before " + _x["deadline_pt"], src="the Scout's pre-kickoff check (Ratcliffe first, then Yahoo, Gotham, Sleeper)")
            _n += 1
    PREKICK_NOTE = f"pre-kickoff check: {_n} upgrade(s)"
except Exception as e:
    PREKICK_NOTE = f"pre-kickoff check skipped: {type(e).__name__}: {e}"

# ---------- BEFORE LOCK: THE RADAR'S PICKUP FLAGS (Dom, Oct 25) ----------
# "That's why we did this today." The Radar flagged Seth McGowan at 9:47 AM; he was a free agent until the Colts kicked
# off at 10, and nobody put him in front of Dom. Every Radar "in" flag (trending adds, openings from an injury or a trade
# rumor, good news) is checked against the latest Yahoo roster + waiver read: if he is a FREE AGENT and his game has not
# started, he becomes an alert that stands until his kickoff - the window when he can be added free, with no bid.
RADAR_NOTE = ""
try:
    import csv as _csv, io as _io, urllib.request as _ur, os as _os
    _gf = _os.path.join(_os.environ.get("DK_ROOT", "/home/claude"), "dksys", "data", "latest", "games.csv")
    _gtxt = open(_gf).read() if _os.path.exists(_gf) else _ur.urlopen("https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv", timeout=60).read().decode()
    _TM = {"LA": "LAR", "JAC": "JAX", "WSH": "WAS", "OAK": "LV", "SD": "LAC", "STL": "LAR"}
    _KO = {}
    for _g in _csv.DictReader(_io.StringIO(_gtxt)):
        if _g.get("season") != "2026" or str(_g.get("week")) != str(W) or not _g.get("gameday"): continue
        try: _t = dt.datetime.strptime(f"{_g['gameday']} {_g.get('gametime') or '13:00'}", "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone(dt.timedelta(hours=-4)))  # nflverse times are US Eastern (EDT until Nov 1)
        except Exception: continue
        if dt.date(2026, 11, 1) <= _t.date() < dt.date(2027, 3, 14): _t = _t.replace(tzinfo=dt.timezone(dt.timedelta(hours=-5)))
        for _k in ("home_team", "away_team"): _KO[_TM.get(_g[_k], _g[_k])] = _t
    _nowu = dt.datetime.now(dt.timezone.utc); _PT = dt.timezone(dt.timedelta(hours=-7 if _nowu.date() < dt.date(2026, 11, 1) else -8))
    _pp_ = (lambda n: (lambda r: float(r["pts_ppr"]) if r and r.get("pts_ppr") not in ("", None) else None)(PROJ.get(_nm(n)))) if "PROJ" in globals() else (lambda n: None)
    _nr = 0
    for lg, RL in R.get("leagues", {}).items():
        L = M["leagues"].get(lg, {}); _shown = 0
        for it in RL.get("in", []) or []:
            name, pos, team = it.get("name"), it.get("pos"), _TM.get(it.get("team") or "", it.get("team") or "")
            if pos not in ("QB", "RB", "WR", "TE") or not name: continue
            own_st = ownership(lg, name)
            if not own_st or own_st[0] != "free": continue          # rostered or on waivers: no free window to catch
            ko = _KO.get(team)
            if not ko or ko <= _nowu: continue                       # bye, or his game has started (he is on waivers now)
            why = "; ".join(it.get("why") or [])
            m_ = re.search(r"Sleeper adds #(\d+)", why); rank = int(m_.group(1)) if m_ else 99
            # Oct 29 (Dom): Ratcliffe, Koerner, Yahoo and Gotham - never Sleeper - against the starter he'd replace
            # (the weakest starter who could hold his seat, flex included, whose game hasn't started)
            starters = [x for x in L.get("starters", {}).get("me", []) if ok(pos, x.get("slot")) and x.get("gs") in ("pre", None) and x.get("slot") not in ("Q/W/R/T",)]
            def _rk(x): v = nums(lg, x["player"], x); return next((v[s_] for s_ in NAMES if v.get(s_) is not None), 99)
            st_ = min(starters, key=_rk, default=None)
            if st_ is None: continue
            cn_, sn_ = nums(lg, name, it), nums(lg, st_["player"], st_)
            ok_ = bar(cn_, sn_)
            if not ok_:
                RISERS.append((lg, it, cn_, sn_, st_)); continue      # under the bar this week: the rising check decides
            ko_pt = ko.astimezone(_PT); kot = f"{ko_pt:%a} {ko_pt.hour % 12 or 12}:{ko_pt:%M} {'AM' if ko_pt.hour < 12 else 'PM'} PT"
            n0 = (it.get("news") or [{}])[0]
            add(id=slug("rk", W, lg, name), color="gold", lg=lg, who=name, kind="radar_prekick",
                title=f"Before lock ({kot}): {name} ({pos}, {team}) over your {st_['slot']} {st_['player']} this week - clears the bar on " + ", ".join(NAMES[s_] for s_ in ok_),
                what=(n0.get("title") or "") + (f" - {n0.get('text')}" if n0.get("text") else "") + (f" Radar: {why}." if why else ""),
                tie=f"Would start over your {st_['slot']} {st_['player']} in {lg} this week, and he's free to add with no bid until {kot}.",
                fix=f"Free to add, no bid, until his game kicks off {kot}; after that he goes to waivers. Bring him to Dom with the full workup before then - never add without Dom's go.",
                ba=None, receipts=[numline(cn_, sn_, st_["player"]), barline(ok_), own_st[2], f"kickoff {kot} (nflverse schedule)", f"Radar flag: {why}"] + ([f"{srcname(n0.get('src'))}, {n0.get('t')}"] if n0.get("t") else []),
                by="before " + kot, deadline_utc=ko.isoformat(), feed=feedline(n0) if n0 else "", feed_title=n0.get("title"),
                src="the Radar, checked on Ratcliffe, Koerner, Yahoo and Gotham")
            _nr += 1; _shown += 1
            if _shown >= 4: break
    RADAR_NOTE = f"radar before-lock: {_nr} free agent(s)"
except Exception as e:
    RADAR_NOTE = f"radar before-lock check skipped: {type(e).__name__}: {e}"

# ---------- Oct 28 (Dom): THE RATCLIFFE ALERTS - "how else do we find out if we don't do that?" ----------
# 1. every Scout pickup that clears the 15% bar (or fills a hole) becomes an alert, so nobody has to go read the boards
# 2. your starters: FTN (Ratcliffe) well under Yahoo this week, or a sharp drop since the last FTN read
# 3. the FTN read itself: stale or missing numbers are an alert, never a silent fallback
FTN_NOTE = ""; FTN_SEEN = {}
try:
    import os, urllib.request, time
    _src = (M.get("sources") or {}).get("ratcliffe") or {}
    if _src.get("status") != "OK":
        add(id=slug("ftn", W, "stale", _src.get("pulled_pt") or "none"), color="red", lg="DK I", who="FTN read", kind="ftn_stale",
            title=f"Ratcliffe's numbers are {_src.get('status','MISSING').lower()}" + (f" - last FTN read {_src.get('pulled_pt')}" if _src.get("pulled_pt") else ""),
            what="The meters, the Scout and the lineup calls are running on old FTN numbers (or Yahoo in their place).",
            tie="Every league (shown under DK I).", fix="Check that your PC is on with Chrome signed in to FTN; the next scheduled read will refresh it.",
            ba=None, receipts=[f"FTN read age: {_src.get('age_h')} h (limit 36 h)"], by="now", src="the FTN read check")
    _dirs = [os.path.join(os.environ.get("DK_ROOT", "/home/claude"), "dksys", "scout"), os.path.join(os.path.dirname(os.path.abspath(act_f)), "scout_state")]
    _np = _ns = 0
    for _lk, _lab in (("DKI", "DK I"), ("DKII", "DK II"), ("DKIII", "DK III"), ("DKIV", "DK IV")):
        _b = None
        for _d in _dirs:
            _f = os.path.join(_d, f"scout_board_{_lk}.json")
            if os.path.exists(_f): _b = json.load(open(_f)); break
        if _b is None:
            _b = json.loads(urllib.request.urlopen(f"https://raw.githubusercontent.com/DomFantasy01/dk-feeds/main/dispatch_out/scout_state/scout_board_{_lk}.json?t={int(time.time())}", timeout=40).read())
        _wl = max(1, 17 - int(W) + 1)
        for _x in (_b.get("adds") or [])[:4]:
            _bp = _x.get("bar_pct")
            if (_x.get("gain") or 0) / _wl < BAR_PTS or (_bp is not None and _bp < 15): continue   # Oct 29 (Dom): Tampa's '2 points through Week 17' is 0.2 a week - noise
            add(id=slug("sc", W, _lab, _x["name"]), color="gold", lg=_lab, who=_x["name"], kind="scout_pickup",
                title=f"Scout pickup: {_x['name']} ({_x['pos']}, {_x['team']}) adds ~{_x['gain'] / _wl:.1f} pts a week (~{_x['gain']:.0f} through Week 17)" + (f", {_bp:.0f}% over the man he'd replace" if _bp is not None else ""),
                what=f"{_x['acq']}. " + (f"Drop to make room: {_x['drop']}. " if _x.get("drop") else "Open bench seat - no drop needed. ")
                     + f"Ratcliffe vs engine: {_x.get('rc','?')}" + (f" ({_x['rc_why']})" if _x.get("rc_why") else "") + ".",
                tie=f"{_lab} roster.", fix="Flag for the full workup and a live Yahoo check before any claim - nothing is a move until we've talked it through.",
                ba=None, receipts=[_x.get("now") or "", "rival check: " + str(_x.get("rivals") or "none")] + [f"check first: {g_}" for g_ in (_x.get("guard") or [])],
                by="before the claim deadline", src="the Scout (Ratcliffe-led, 15% bar)")
            _np += 1
    _prev_seen = PREV.get("ftn_seen") or {}
    for _lab, _L in (M.get("leagues") or {}).items():
        for _s in (_L.get("starters") or {}).get("me", []):
            if _s.get("ratcliffe_src") != "ftn" or _s.get("actual") is not None: continue
            _r, _y = _s.get("ratcliffe"), _s.get("yahoo"); _key = f"{_lab}|{_s['player']}"; FTN_SEEN[_key] = _r
            _old = _prev_seen.get(_key)
            if isinstance(_old, (int, float)) and _r is not None and _old - _r >= 3 and _r <= .75 * _old:
                add(id=slug("fd", W, _lab, _s["player"], round(_r)), color="red", lg=_lab, who=_s["player"], kind="ftn_drop",
                    title=f"Ratcliffe cut your {_s['slot']} {_s['player']} from {_old:.1f} to {_r:.1f}",
                    what="A sharp drop since the last FTN read usually means news - an injury, a role change or a benching.",
                    tie=f"Your {_s['slot']} starter in {_lab}.", fix="Check the news and your bench before his kickoff.",
                    ba={"label": "Ratcliffe this week", "before": _old, "after": _r}, receipts=[f"Yahoo has him at {f1(_y)}"],
                    by="before his kickoff", src="the FTN read")
                _ns += 1
            elif _r is not None and isinstance(_y, (int, float)) and _y >= 6 and _r <= .7 * _y:
                add(id=slug("fy", W, _lab, _s["player"]), color="gold", lg=_lab, who=_s["player"], kind="ftn_low",
                    title=f"Ratcliffe is well under Yahoo on your {_s['slot']} {_s['player']}: {_r:.1f} vs {_y:.1f}",
                    what="When the expert and Yahoo split this much on a starter, find out why before lock.",
                    tie=f"Your {_s['slot']} starter in {_lab}.", fix="Look at the news and your bench options; nothing to do if the reason doesn't hold up.",
                    ba=None, receipts=[f"Gotham has him at {f1(_s.get('gotham'))}"], by="before his kickoff", src="the FTN read vs Yahoo")
                _ns += 1
    FTN_NOTE = f"ratcliffe: {_np} scout pickup(s), {_ns} starter flag(s), read {_src.get('status','MISSING')}"
except Exception as e:
    FTN_NOTE = f"ratcliffe alerts skipped: {type(e).__name__}: {e}"

# ---------- Oct 29 (Dom): RISING PLAYERS - "I don't want to miss people that are up and coming" ----------
# Men under this week's bar still reach Dom when something real is pushing their work up: a starter ahead of him OUT
# (not merely questionable/limited), news of a bigger role, his snaps/targets climbing, Ratcliffe's rest-of-season number
# clearing the bar over the starter he'd replace, or he's just come back / changed teams and an expert already rates him.
# One card per man per league, at most 3 per league, free agents and waiver men only. It's a heads-up to talk through.
RISE_NOTE = ""
try:
    # a ROLE change, not a practice report ("full practice" / "returns to practice" are health news, not more work)
    ROLE = re.compile(r"\b((bigger|heavier|larger|expanded|increased|more|elevated) (workload|role|work|snaps?|snap count|touches|usage|playing time|opportunit\w*)|uptick|lead role|lead back|starting role|takes? over|step(s)? into|in line for|promoted|starting job|will start|set to start|draws start|workhorse|inherits)\b", re.I)
    _OUTRX = re.compile(r"opening: (.+?) — (out|doubtful|ir\b|injured reserve|placed on|traded|released|waived|suspended|season)", re.I)
    def _wlup(w):
        try: v = [float(x) for x in str(w or "").split("/") if x.strip() not in ("", "-")]
        except Exception: return None
        if len(v) < 4: return None
        a, b = sum(v[-2:]) / 2, sum(v[:-2]) / len(v[:-2])
        return (a, b) if a >= 6 and a >= 1.5 * max(b, 1) else None
    _rk2, _seen2 = {}, {(x["lg"], _nm(x["who"])) for x in ITEMS}
    for lg, it, cn_, sn_, st_ in RISERS:
        name = it.get("name"); k = (lg, _nm(name))
        if k in _seen2: continue
        o_ = ownership(lg, name)
        if o_ and o_[0] == "taken": continue
        why_ = "; ".join(it.get("why") or []); rs = []
        m_ = _OUTRX.search(why_)
        if m_: rs.append(f"{m_.group(1)} is {m_.group(2).lower()}, so his work goes up")
        if re.search(r"good news", why_) and ROLE.search((it.get("news") or [{}])[0].get("title") or ""):
            rs.append("news of a bigger role: " + it["news"][0]["title"])
        w_ = _wlup(it.get("workload"))
        if w_: rs.append(f"his work is climbing: {w_[0]:.0f} a game the last two vs {w_[1]:.0f} before (snaps/targets/touches, last games {it.get('workload')})")
        rp = (RAT.get((_LGN.get(lg), _nm(name))) or (None, None))[1]
        sp = (RAT.get((_LGN.get(lg), _nm(st_["player"]))) or (None, None))[1] if st_ else None
        if isinstance(rp, (int, float)) and isinstance(sp, (int, float)) and rp - sp >= BAR_PTS and rp >= sp * (1 + BAR_PCT):
            rs.append(f"Ratcliffe's rest of season has him at {rp:.1f} a game vs {sp:.1f} for {st_['player']}")
        if it.get("online") and any(isinstance(v, (int, float)) and v >= 6 for v in cn_.values()):
            rs.append(why_ + " - and an expert already projects him for real work")
        if not rs: continue
        best = max([v for v in cn_.values() if isinstance(v, (int, float))] or [0])
        _rk2.setdefault(lg, []).append((len(rs), best, lg, it, cn_, sn_, st_, rs, o_))
    _nr2 = 0
    for lg, L_ in _rk2.items():
        for n_, best, lg, it, cn_, sn_, st_, rs, o_ in sorted(L_, key=lambda t: (-t[0], -t[1]))[:3]:
            name, pos, team = it.get("name"), it.get("pos"), it.get("team") or ""
            add(id=slug("rise", W, lg, name), color="gold", lg=lg, who=name, kind="rising",
                title=f"Rising: {name} ({pos}, {team}) - " + rs[0],
                what="; ".join(rs[1:]) or rs[0],
                tie=(f"Not ahead of your {st_['slot']} {st_['player']} this week, but if this holds he could be in a few weeks - and he's cheapest now." if st_
                     else "Not a starter for you this week; worth catching while he's cheap."),
                fix="Nothing to do yet: talk it through, and give him the full workup if the reason holds.",
                ba=None, receipts=[numline(cn_, sn_, st_["player"]) if st_ else "", "Why he's flagged: " + "; ".join(rs),
                                   ("Yahoo: " + o_[2]) if o_ else ""],
                by=None, src="the rising-player check (Radar, workload, Ratcliffe rest of season)")
            _nr2 += 1
    RISE_NOTE = f"rising: {_nr2} of {len(RISERS)} under-the-bar men"
except Exception as e:
    RISE_NOTE = f"rising check skipped: {type(e).__name__}: {e}"

_rpk = {(x["lg"], x["who"]) for x in ITEMS if x.get("kind") == "radar_prekick"}
ITEMS[:] = [x for x in ITEMS if not (x.get("kind") == "wire" and (x["lg"], x["who"]) in _rpk)]
# ---------- Oct 29 (Dom): every card says whose man he is, what it means for him, and where the numbers came from ----------
for x in ITEMS:
    hint = None
    if x.get("kind") == "online":
        t_ = (x.get("title") or "").lower()
        hint = "new team" if "new team" in t_ else "back from injury" if ("no game since" in t_ or "just back" in t_ or "coming back" in t_) else "hasn't played yet" if "hasn't played" in t_ else None
    if x.get("kind") in ("ftn_stale",): x["own"] = "System"; continue
    x["own"] = own_tag(x["lg"], x["who"].replace(" defense", ""), hint)
    if x.get("kind") == "feed":
        role = "starter" if (x.get("tie") or "").startswith("Your ") else "opp" if "opponent" in (x.get("tie") or "") else "bench"
        good = (x.get("fix") or "").startswith("Good news")
        bad = x.get("color") == "red"
        opp = (M.get("leagues", {}).get(x["lg"]) or {}).get("opp") or "your opponent"
        x["tie"] = {("starter", True): x.get("tie", "") + " Good sign: he looks set to play, so no fill needed.",
                    ("starter", False): x.get("tie", "") + (" If he sits, you need a fill in that seat before his kickoff." if not bad else " He likely scores little or nothing: line up a fill now."),
                    ("bench", True): x.get("tie", "") + " Good for him; it changes nothing this week unless you start him.",
                    ("bench", False): x.get("tie", "") + " He isn't in your lineup, so this week's score doesn't change.",
                    ("opp", True): f"Starts for {opp}, your {x['lg']} opponent this week: he looks set to play.",
                    ("opp", False): f"Starts for {opp}, your {x['lg']} opponent this week: if he sits, their score drops."}[(role, good)]
    if x.get("kind") in ("wire", "bench", "radar_prekick", "prekick", "online", "rising") and srcages() not in (x.get("receipts") or []):
        x["receipts"] = [r for r in (x.get("receipts") or []) if r] + [srcages()]

# ---------- merge with what Live already holds ----------
old = {x["id"]: x for x in PREV.get("items", [])}
seen, out = set(), []
for x in ITEMS:
    if x["id"] in seen: continue
    seen.add(x["id"])
    o = old.get(x["id"], {})
    x["first_seen"] = o.get("first_seen") or NOW
    x["last_seen"] = NOW
    x["active"] = True
    out.append(x)
cut = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)).isoformat()
cut7 = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)).isoformat()   # Oct 20 (Dom): archived cards clear 7 days after archiving, as the page says
cut7 = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat()   # Oct 29 (Dom): resolved cards are kept one day, then dropped
for i, o in old.items():
    if i in seen: continue
    if o.get("kind") == "feed" and (o.get("fix") or "").startswith("Worth knowing"): continue   # Oct 14 (Dom): retired card type
    if o.get("kind") == "feed" and not FEEDS and o.get("active"):
        pass                                          # a run without the feeds can't judge feed alerts; leave them as they are
    elif o.get("active"):
        o = dict(o, active=False, resolved_at=NOW,   # the latest build no longer raises it - say why (Oct 29, Dom)
                 resolved_why={"feed": "the news is over 48 hours old, or newer news on him replaced it",
                               "radar_prekick": "his game kicked off, someone added him, or he fell under the bar",
                               "prekick": "the kickoff passed or he fell under the bar",
                               "wire": "he fell under the bar or someone added him", "rising": "the reason went away or he was added",
                               "scout_pickup": "the Scout no longer ranks him", "out": "the lineup hole is filled", "bye": "the lineup hole is filled"
                               }.get(o.get("kind"), "the latest build no longer raises it"))
    if o.get("active") or not o.get("resolved_at") or o["resolved_at"] >= cut7:
        if (o.get("last_seen") or "") >= cut: out.append(o)
RANK = {"red": 0, "gold": 1, "grey": 2}
out.sort(key=lambda x: (not x.get("active"), RANK.get(x["color"], 3), x["lg"], x["who"]))
doc = {"week": W, "built": BUILT, "generated": NOW, "feeds_checked": NOW if FEEDS else PREV.get("feeds_checked"), "source": SRC, "items": out[:300], "online_check": ONLINE_NOTE, "ftn_seen": FTN_SEEN or PREV.get("ftn_seen") or {}}
# Oct 20 (Dom): SIZE GUARD - the Live database refuses a document over 262,144 bytes, and every hourly run with the
# news feeds came out ~274 KB, so its write was refused and the page sat on the 7:13 AM feeds. Drop the oldest archived
# cards (never an active one) until the document fits with room to spare, and write it compact.
LIMIT = 240000
def _sz(d): return len(json.dumps({"id": "alerts", "data": d}, separators=(",", ":")).encode())
_dropped = 0
while _sz(doc) > LIMIT:
    _old = [i for i, x in enumerate(doc["items"]) if not x.get("active")]
    if not _old: break
    _i = min(_old, key=lambda i: doc["items"][i].get("resolved_at") or doc["items"][i].get("last_seen") or "")
    doc["items"].pop(_i); _dropped += 1
json.dump(doc, open(out_f, "w"), separators=(",", ":"))
SIZE_NOTE = f"size {_sz(doc):,} bytes" + (f", {_dropped} oldest archived cards dropped to fit" if _dropped else "") + (" - STILL OVER THE LIMIT" if _sz(doc) > 262144 else "")
act = [x for x in out if x.get("active")]
print("ALERTS", len(act), "active:", {c: sum(1 for x in act if x["color"] == c) for c in RANK},
      "| resolved now:", sum(1 for x in out if x.get("resolved_at") == NOW), "|", ONLINE_NOTE, "|", PREKICK_NOTE, "|", RADAR_NOTE, "|", FTN_NOTE, "|", RISE_NOTE, "|", SIZE_NOTE)
