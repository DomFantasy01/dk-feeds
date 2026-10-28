"""WAIVER EXPERTS in the brief (Oct 27 2026, Dom: experts that weigh in BEFORE waiver claims).
Reads yahoo_drop/morning/waiver_experts.txt (pull_waiver_experts.py), every league's live Yahoo rosters and the Scout boards,
and appends a "Waiver experts" section to the brief: each expert's top adds with who holds them in each of Dom's leagues,
whether the Scout agrees, their bids, and any expert drop candidate sitting on Dom's rosters. Also writes
dispatch_out/waiver_experts.json. Idempotent: replaces its own section. Flags only - nothing here is a move."""
import json, os, re, sys

LEAGUES = [("DK I", "dk1", "DKI", "2", "FAAB"), ("DK II", "dk2", "DKII", "7", "FAAB"),
           ("DK III", "dk3", "DKIII", "2", "FAAB"), ("DK IV", "dk4", "DKIV", "6", "priority")]
TOP = {"top10": 99, "priority": 99, "immediate": 99}   # sections that count as an expert's headline adds

def sq(n): return re.sub(r"[^a-z]", "", re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", "", n.lower()))

def main(repo, brief):
    f = f"{repo}/yahoo_drop/morning/waiver_experts.txt"
    if not os.path.exists(f): print("no waiver_experts.txt - section skipped"); return
    raw = open(f).read().splitlines()
    head = [l[2:] for l in raw if l.startswith("# ")]
    rows = [l.split("|") for l in raw if l and not l.startswith("#")]
    wk = re.search(r"week (\d+)", head[0]).group(1) if head else "?"
    held, mine, adds, roster_age = {}, {}, {}, {}
    for dk, short, board, me, _ in LEAGUES:
        held[dk], mine[dk] = {}, set()
        rf = f"{repo}/yahoo_drop/scout/{short}_rosters_live.txt"
        if os.path.exists(rf):
            for l in open(rf):
                if l.startswith("#"):
                    m = re.search(r"read live (.*?PT)", l); roster_age[dk] = m.group(1) if m else ""
                    continue
                p = l.rstrip("\n").split("|")
                if len(p) > 2:
                    held[dk][sq(p[2])] = p[0]
                    if p[0] == me: mine[dk].add(sq(p[2]))
        bf = f"{repo}/dispatch_out/scout_state/scout_board_{board}.json"
        adds[dk] = {}
        if os.path.exists(bf):
            for a in json.load(open(bf)).get("adds", []):
                adds[dk][sq(a["name"])] = (a.get("gain"), a["name"])
    experts = []
    for r in rows:
        if r[0] not in [e["expert"] for e in experts]:
            experts.append(dict(expert=r[0], site=r[1], acc=r[2], posted=r[3], picks=[]))
        next(e for e in experts if e["expert"] == r[0])["picks"].append(dict(order=int(r[4]), name=r[5], pos=r[6], team=r[7], sec=r[8], bid=r[9]))

    def where(name):
        k, out = sq(name), []
        for dk, *_ in LEAGUES:
            if k in mine[dk]: out.append(f"{dk} yours")
            elif k in held[dk]: out.append(f"{dk} taken")
            else:
                g = adds[dk].get(k, (None,))[0]
                out.append(f"{dk} OPEN" + (f" - Scout agrees (+{g:.0f})" if isinstance(g, (int, float)) and g > 0 else " - not in the Scout's adds"))
        return "; ".join(out)

    L = [f"Waiver experts - week {wk} (named experts' waiver columns, posted before claims run)"]
    L += [f"  Read: {re.sub(r' - https?://\S+', '', h)[:160]}" for h in head[1:]]
    J = {"week": wk, "read": head, "experts": []}
    for e in experts:
        top = [p for p in e["picks"] if p["sec"] in TOP][:10] or e["picks"][:8]
        L.append(f"  {e['expert']} ({e['site']}, accuracy #{e['acc']}) - top adds:")
        je = dict(e, top=[])
        for p in top:
            # his bid for this player can sit in a later position section - take the first one he gave
            bid = p["bid"] or next((q["bid"] for q in e["picks"] if q["name"] == p["name"] and q["bid"]), "")
            b = (f" bid ${bid} of 100" if bid and "%" not in bid else f" bid {bid}" if bid else "")
            w = where(p["name"])
            L.append(f"    {p['name']} ({p['pos']} {p['team']}){b} - {w}")
            je["top"].append(dict(p, bid=bid, where=w))
        drops = [p for p in e["picks"] if p["sec"] == "drop"]
        hit = [f"{p['name']} ({dk})" for p in drops for dk, *_ in LEAGUES if sq(p["name"]) in mine[dk]]
        if hit:
            L.append(f"    Drop candidates he names that are on your rosters: {', '.join(hit)}")
        je["your_drops"] = hit
        J["experts"].append(je)
    # the engine's adds no expert mentions - always say when they disagree
    named = {sq(p["name"]) for e in experts for p in e["picks"]}
    for dk, *_ in LEAGUES:
        lone = [f"{n} (+{g:.0f})" for k, (g, n) in adds[dk].items() if isinstance(g, (int, float)) and g >= 5 and k not in named and not n.endswith("DEF")]
        if lone: L.append(f"  {dk}: Scout adds no expert names - {', '.join(lone)}")
    L.append(f"  Rosters: Yahoo read {', '.join(f'{k} {v}' for k, v in roster_age.items())}. Flags only - nothing here is a move.")
    sec = "\n".join(L) + "\n"
    json.dump(J, open(f"{repo}/dispatch_out/waiver_experts.json", "w"), indent=1)
    b = open(brief).read() if os.path.exists(brief) else ""
    b = re.sub(r"(?s)\nWaiver experts - week .*?Flags only - nothing here is a move\.\n", "\n", b)
    open(brief, "w").write(b.rstrip("\n") + "\n\n" + sec)
    print(sec)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
