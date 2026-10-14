# Dark Knight Live alerts (Dom, Oct 13 2026).
# One alert per player per event. Raw feed hits make the alert; Gotham only adds the numbers, it never gates.
# Colors: red = act now, gold = monitor, grey = noted. Green is never an input color: an alert the latest build
# no longer raises is marked resolved and the page shows it green in history.
# Usage: python3 alerts.py radar.json actions.json meter.json alarm.json prev_alerts.json(or -) out.json [--feeds DIR]
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

ITEMS = []
def add(**k):
    k.setdefault("src", SRC); k.setdefault("built", BUILT)
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
            by=it.get("by"), feed=(f"{n0.get('src')}, {n0.get('t')}: {n0.get('title')}" if n0 else ""))
    else:
        add(id=slug("w", W, lg, kind, who), color=color, lg=lg, who=who, kind=kind,
            title=it["what"].split(". ")[0] + ".", what=it["what"],
            tie=f"{lg} roster move.", fix=it["what"], ba=None, receipts=[], by=it.get("by"), feed="")

covered = {(x["lg"], x["who"]) for x in ITEMS}

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
            feed=f"{n0.get('src')}, {n0.get('t')}: {n0.get('title')}")
    hole_fill = {}
    for x in ITEMS:
        if x["lg"] == lg and x.get("ba") and x["kind"] in ("out", "bye"):
            hole_fill[x["who"]] = (x["ba"]["after"] or 0) - (x["ba"]["before"] or 0)
    for p in RL.get("in", []):
        fl = p.get("floor") or {}
        if not p.get("beats_floor") or g(p) is None: continue
        if fl.get("name") in hole_fill: continue   # that hole's alert already weighs the wire against the bench fill
        base = fl.get("gotham") or 0
        gain = g(p) - base
        if gain <= 0: continue
        n0 = p["news"][0] if p.get("news") else {}
        add(id=slug("w", W, lg, "in", p["name"]), color="gold" if gain >= FLOOR else "grey", lg=lg, who=p["name"],
            kind="wire", title=f"Free agent {p['name']} ({p['pos']}, {p.get('team','')}) beats your {fl.get('name')} by {gain:.1f}",
            what="; ".join(p.get("why") or []) or (n0.get("title") or "On the Scout's list."),
            tie=f"Your weakest {p['pos']} option in {lg} is {fl.get('name')} at Gotham {f1(base)}.",
            fix=f"Your call: claim {p['name']} and start him over {fl.get('name')}." + (" Gain is under 2 points, inside the noise." if gain < FLOOR else ""),
            ba={"label": f"that lineup spot, Gotham points", "before": round(base, 1), "after": round(g(p), 1)},
            receipts=[f"Workload last 5: {p.get('workload') or 'unknown'}", f"Yahoo ownership check: {p.get('acq') or 'unknown'}"],
            by="before waivers clear", feed=(f"{n0.get('src')}, {n0.get('t')}: {n0.get('title')}" if n0 else ""))
    for p in RL.get("opp", []):
        mk = p.get("marker", {})
        if mk.get("color") != "red" or not p.get("news"): continue
        n0 = p["news"][0]
        add(id=slug("w", W, lg, "opp", p["name"], n0.get("t")), color="grey", lg=lg, who=p["name"], kind="opp",
            title=f"Opponent's {p['pos']} " + (n0.get('title') if p['name'] in (n0.get('title') or '') else f"{p['name']}: {n0.get('title')}"), what=n0.get("text") or "",
            tie=f"Starts for {RL.get('opponent')}, your {lg} opponent.", fix="Nothing for you to do.",
            ba={"label": "his Gotham points", "before": g(p), "after": None}, receipts=[], by=None,
            feed=f"{n0.get('src')}, {n0.get('t')}: {n0.get('title')}")
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
                         "title": (it.get("title") or "").strip(), "text": re.sub(r"<[^>]+>", " ", it.get("text") or "").strip()})
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
    for x in ITEMS: seen_titles.setdefault((x["lg"], x["who"]), []).append((x.get("feed") or "") + " " + (x.get("title") or ""))
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
            if role != "starter" and not (bad or caut): continue     # bench and opponents: only injury or status news
            sev = 2 if bad else 1 if caut else 0
            k = (lg, name)
            if k in _best and (_best[k][0], _best[k][1]) >= (sev, d): continue
            _best[k] = (sev, d, len(ITEMS))
            if role == "starter": color = "red" if bad else ("gold" if caut else "grey")
            else: color = "grey"
            tie = {"starter": f"Your {slot} starter in {lg}.", "bench": f"On your {lg} {'IR' if slot == 'IR' else 'bench'}.",
                   "opp": f"Starts for your {lg} opponent."}[role]
            gone = bool(re.search(r"\b(released|releases|release|waived|waives|cut by|move on from|moves on from)\b", blob, re.I))
            fix = (f"His team has let him go, so he scores 0 unless someone signs him. Bench him and pick up another {slot}."
                   if role == "starter" and gone else
                   "Check his status before kickoff and line up a bench fill; the next Dispatch build re-scores the lineup."
                   if role == "starter" and (bad or caut) else "Nothing to do now." if role != "starter" else "Worth knowing; no action yet.")
            add(id=slug("w", W, lg, "feed", name, n["t"]), color=color, lg=lg, who=name, kind="feed",
                title=n["title"] if nn in _norm(n["title"]) else f"{name}: {n['title']}",
                what=(n["text"] or n["title"])[:400], tie=tie, fix=fix,
                ba={"label": "his Gotham points", "before": gp, "after": None} if role == "starter" and gp is not None else None,
                receipts=["Raw feed hit: the next Dispatch build confirms it against ESPN and Sleeper and re-scores your lineup"],
                by=None, feed=f"{n['src']}, {_pt(d)}: {n['title']}", news_t=d.isoformat(),
                src=f"{n['src']} (raw feed, pulled every 30 minutes)")
            seen_titles.setdefault((lg, name), []).append(n["title"])
    _keep = {v[2] for v in _best.values()}
    _cov = {(x["lg"], x["who"]) for x in ITEMS if x["kind"] != "feed"}
    ITEMS[:] = [x for i, x in enumerate(ITEMS) if x["kind"] != "feed" or
                (i in _keep and not ((x["lg"], x["who"]) in _cov and _when(x["news_t"]) <= _built))]

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
    if o.get("kind") == "feed" and not FEEDS and o.get("active"):
        pass                                          # a run without the feeds can't judge feed alerts; leave them as they are
    elif o.get("active"):
        o = dict(o, active=False, resolved_at=NOW)   # the latest build no longer raises it
    if (o.get("last_seen") or "") >= cut: out.append(o)
RANK = {"red": 0, "gold": 1, "grey": 2}
out.sort(key=lambda x: (not x.get("active"), RANK.get(x["color"], 3), x["lg"], x["who"]))
doc = {"week": W, "built": BUILT, "generated": NOW, "feeds_checked": NOW if FEEDS else PREV.get("feeds_checked"), "source": SRC, "items": out[:300]}
json.dump(doc, open(out_f, "w"), indent=1)
act = [x for x in out if x.get("active")]
print("ALERTS", len(act), "active:", {c: sum(1 for x in act if x["color"] == c) for c in RANK},
      "| resolved now:", sum(1 for x in out if x.get("resolved_at") == NOW))
