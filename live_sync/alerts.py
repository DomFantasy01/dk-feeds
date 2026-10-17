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
BUILT = A.get("built_pt") or M.get("built_pt") or ""
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
def _nm(s): return re.sub(r"[^a-z ]", "", re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", "", (s or "").lower())).strip()
OWN = {}
for lg_, n_ in LGN.items():
    ro, wv = _rd(n_, "rosters_live"), _rd(n_, "waivers")
    if not ro: continue
    stamp = (re.search(r"read live (.+? PT)", ro) or [None, "time unknown"])[1]
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
        if not p.get("beats_floor") or g(p) is None: continue
        if fl.get("name") in hole_fill: continue   # that hole's alert already weighs the wire against the bench fill
        own_st = ownership(lg, p["name"])
        if own_st and own_st[0] == "taken": continue           # Yahoo's live read: someone already rosters him
        better = max((x for x in bench if x.get("pos") == p.get("pos") and g(x) >= g(p)), key=g, default=None)
        if better:                                             # your bench already beats him: no pickup alert
            BENCH_BEATS.setdefault(lg, []).append((p["name"], better["player"])); continue
        base = fl.get("gotham") or 0
        gain = g(p) - base
        if gain <= 0: continue
        n0 = p["news"][0] if p.get("news") else {}
        fp = mine.get(fl.get("name"), {})
        # Oct 16 (Dom): never weigh a pickup against a starter whose game has already started - his score is locked
        # (Sutton's final 3.9 on Thursday read as "Antonio Williams beats him by 3.5").
        if fp.get("gs") not in (None, "pre"): continue
        votes, cmp_ = agree(p.get("sleeper"), fp.get("sleeper"), p.get("yahoo"), fp.get("yahoo"))
        tag = {2: "all three agree", 1: "Gotham + one", 0: "Gotham only"}.get(votes, "Gotham only")
        if own_st and own_st[0] == "waivers":
            kind_l, how = "On waivers", f"Waiver claim: he clears {own_st[1]}, so you have to win the claim, and adding him means dropping someone."
        elif own_st:
            kind_l, how = "Free agent", "Not on Yahoo's waiver list, so an instant add, but adding him means dropping someone."
        else:
            kind_l, how = "Free agent?", "Yahoo's roster read wasn't available, so it isn't confirmed he's still out there."
        why = [re.sub(r"^opening: (.+?) \u2014 (.+)$", r"Opening: \1 is \2, which frees up work", w) for w in (p.get("why") or [])]
        add(id=slug("w", W, lg, "in", p["name"]), color="gold" if gain >= FLOOR else "grey", lg=lg, who=p["name"],
            kind="wire", title=f"{kind_l}: {p['name']} ({p['pos']}, {p.get('team','')}) beats your {fl.get('name')} by {gain:.1f} ({tag})",
            what="; ".join(why) or "On the Scout's list.",
            tie=f"Your weakest {p['pos']} option in {lg} is {fl.get('name')}.",
            fix=f"Your call: {'claim' if kind_l == 'On waivers' else 'add'} {p['name']} and start him over {fl.get('name')}. {how}" + (" Gain is under 2 points, inside the noise." if gain < FLOOR else ""),
            ba={"label": "that lineup spot, Gotham points", "before": round(base, 1), "after": round(g(p), 1)},
            receipts=[f"This week: Gotham {f1(g(p))} vs {f1(base)} \u00b7 {cmp_}",
                      f"Workload last 5 (the work Gotham's number is built on): {p.get('workload') or 'unknown'}",
                      f"Yahoo roster read: {own_st[2] if own_st else 'not available'}"],
            by=("before waivers clear " + own_st[1]) if own_st and own_st[0] == "waivers" else None,
            feed=feedline(n0), feed_title=n0.get("title"), src="Gotham, with Yahoo and Sleeper shown")
    # your own bench vs your own starters, Gotham-driven like the wire (Oct 14: the bench check's other half)
    used_b = set()
    for st in L.get("starters", {}).get("me", []):
        if st.get("gs") != "pre" or g(st) is None or st.get("slot") in ("QB", "K", "DEF", "Q/W/R/T"): continue
        c = max((x for x in bench if x["player"] not in used_b and ok(x.get("pos"), st["slot"])), key=g, default=None)
        if not c or g(c) - g(st) < FLOOR: continue
        used_b.add(c["player"])
        votes, cmp_ = agree(c.get("sleeper"), st.get("sleeper"), c.get("yahoo"), st.get("yahoo"))
        tag = {2: "all three agree", 1: "Gotham + one", 0: "Gotham only"}.get(votes, "Gotham only")
        gain = g(c) - g(st)
        add(id=slug("w", W, lg, "bench", c["player"], st["player"]), color="gold", lg=lg, who=c["player"], kind="bench",
            title=f"Your bench's {c['player']} beats your {st['slot']} {st['player']} by {gain:.1f} ({tag})",
            what=f"Gotham has {c['player']} at {f1(g(c))} and {st['player']} at {f1(g(st))} this week.",
            tie=f"Both are already on your {lg} roster: no pickup, no drop.",
            fix=f"Your call: start {c['player']} over {st['player']}." + ("" if votes == 2 else " Yahoo and Sleeper don't both see it yet, so this is Gotham's early read."),
            ba={"label": "that lineup spot, Gotham points", "before": round(g(st), 1), "after": round(g(c), 1)},
            receipts=[f"This week: Gotham {f1(g(c))} vs {f1(g(st))} \u00b7 {cmp_}",
                      "Workload last 5: " + ", ".join(f"{q['player']} {q.get('workload') or wl(lg, q['player'])}" for q in (c, st)).replace(" unknown", " not in this build")],
            by="before kickoff", feed="", src="Gotham, with Yahoo and Sleeper shown")
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
            beats = weak[0] is not None and p > weak[1]
            if not beats and p < 5: continue
            kind_l = "On waivers" if own_st[0] == "waivers" else "Free agent"
            add(id=slug("w", W, lg, "online", name), color="gold" if beats else "grey", lg=lg, who=name, kind="online",
                title=f"Coming online: {name} ({pos}, {team}), {why}. {kind_l}" + (f", clears {own_st[1]}" if own_st[0] == "waivers" else ""),
                what=(news[2] if news else f"Sleeper now projects him {p:.1f} this week; Gotham has no recent games to rate him."),
                tie=(f"Would beat your weakest {pos} starter in {lg}, {weak[0]['player']} ({weak[1]:.1f})." if beats else
                     f"Not ahead of your {pos} starters yet" + (f" (weakest: {weak[0]['player']}, {weak[1]:.1f})" if weak[0] else "") + "; worth watching."),
                fix=(f"Your call: {'claim' if own_st[0] == 'waivers' else 'add'} {name} - Sleeper projects {p:.1f} (PPR). Confirm his role in the news first; Gotham can't rate him until he plays. Adding him means dropping someone."
                     if beats else "Nothing to do yet - watch his first game back."),
                ba=None, receipts=[gl, st_line, f"Sleeper projection pulled {_stamp_pt}", f"Yahoo roster read: {own_st[2]}"],
                by=(("before waivers clear " + own_st[1]) if own_st[0] == "waivers" else "before kickoff") if beats else None,
                feed=(f"{srcname(news[1])}, {_pt(_when(news[0]))}" if news and _when(news[0]) else ""), feed_title=(news[2] if news else None),
                src="Sleeper projection + nflverse game log (Gotham can't rate him yet)")
            nonline += 1
    ONLINE_NOTE = f"coming online: {len(CAND)} players checked, {nonline} alerts (Sleeper {_stamp_pt}, games through Week {GMAX})"
except Exception as e:
    ONLINE_NOTE = f"coming online check skipped: {type(e).__name__}: {e}"

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
for i, o in old.items():
    if i in seen: continue
    if o.get("kind") == "feed" and (o.get("fix") or "").startswith("Worth knowing"): continue   # Oct 14 (Dom): retired card type
    if o.get("kind") == "feed" and not FEEDS and o.get("active"):
        pass                                          # a run without the feeds can't judge feed alerts; leave them as they are
    elif o.get("active"):
        o = dict(o, active=False, resolved_at=NOW)   # the latest build no longer raises it
    if (o.get("last_seen") or "") >= cut: out.append(o)
RANK = {"red": 0, "gold": 1, "grey": 2}
out.sort(key=lambda x: (not x.get("active"), RANK.get(x["color"], 3), x["lg"], x["who"]))
doc = {"week": W, "built": BUILT, "generated": NOW, "feeds_checked": NOW if FEEDS else PREV.get("feeds_checked"), "source": SRC, "items": out[:300], "online_check": ONLINE_NOTE}
json.dump(doc, open(out_f, "w"), indent=1)
act = [x for x in out if x.get("active")]
print("ALERTS", len(act), "active:", {c: sum(1 for x in act if x["color"] == c) for c in RANK},
      "| resolved now:", sum(1 for x in out if x.get("resolved_at") == NOW), "|", ONLINE_NOTE)
