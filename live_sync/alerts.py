# Dark Knight Live alerts (Dom, Oct 13 2026).
# One alert per player per event. Raw feed hits make the alert; Gotham only adds the numbers, it never gates.
# Colors: red = act now, gold = monitor, grey = noted. Green is never an input color: an alert the latest build
# no longer raises is marked resolved and the page shows it green in history.
# Usage: python3 alerts.py radar.json actions.json meter.json alarm.json prev_alerts.json(or -) out.json
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
            tot = (L.get("totals", {}).get("gotham") or [None])[0]
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
    if o.get("active"):
        o = dict(o, active=False, resolved_at=NOW)   # the latest build no longer raises it
    if (o.get("last_seen") or "") >= cut: out.append(o)
RANK = {"red": 0, "gold": 1, "grey": 2}
out.sort(key=lambda x: (not x.get("active"), RANK.get(x["color"], 3), x["lg"], x["who"]))
doc = {"week": W, "built": BUILT, "generated": NOW, "source": SRC, "items": out[:300]}
json.dump(doc, open(out_f, "w"), indent=1)
act = [x for x in out if x.get("active")]
print("ALERTS", len(act), "active:", {c: sum(1 for x in act if x["color"] == c) for c in RANK},
      "| resolved now:", sum(1 for x in out if x.get("resolved_at") == NOW))
