"""RATCLIFFE vs THE ENGINE in the brief (Oct 28 2026, Dom: Ratcliffe leads; never exclude anybody - tag both agree /
Ratcliffe only / engine only, and always tell him when they disagree, on his players or the wire).
Reads dispatch_out/meter_wk<W>.json (this week's numbers per starter) and the four Scout boards (pickups with their tags)
and appends a "Ratcliffe vs engine" section. Idempotent: replaces its own section. Flags only - nothing here is a move."""
import json, os, re, sys

BOARDS = [("DK I", "DKI"), ("DK II", "DKII"), ("DK III", "DKIII"), ("DK IV", "DKIV")]

def main(repo, brief):
    mf = sorted([f for f in os.listdir(f"{repo}/dispatch_out") if re.match(r"meter_wk\d+\.json$", f)], key=lambda f: int(re.findall(r"\d+", f)[0]))
    if not mf: print("no meter - section skipped"); return
    M = json.load(open(f"{repo}/dispatch_out/{mf[-1]}"))
    src = M.get("sources", {}).get("ratcliffe", {})
    L = [f"Ratcliffe vs engine - week {M['week']} (FTN read {src.get('pulled_pt', 'missing')}; Ratcliffe leads, the engine shows beside him)"]
    if src.get("status") != "OK":
        L.append(f"  Ratcliffe's numbers are {src.get('status', 'MISSING')} - the meters show Yahoo in his place until the next FTN read.")
    for lab, bk in BOARDS:
        lg = M["leagues"].get(lab)
        if not lg: continue
        n = lg["needles"]
        L.append(f"  {lab}: win chance - Ratcliffe {n.get('ratcliffe')}%, Yahoo {n.get('yahoo')}%, Gotham {n.get('gotham')}% (best lineups; Yahoo as set)")
        split = []
        for s in lg["starters"]["me"]:
            r, g = s.get("ratcliffe"), s.get("gotham")
            if s.get("ratcliffe_src") != "ftn":
                split.append(f"{s['player']} engine only (Ratcliffe doesn't project him)"); continue
            if r is not None and g is not None and abs(r - g) >= 3:
                split.append(f"{s['player']} Ratcliffe {r:.1f} vs engine {g:.1f}")
        if split: L.append("    Your starters where they split by 3+ points: " + "; ".join(split))
        bf = f"{repo}/dispatch_out/scout_state/scout_board_{bk}.json"
        if os.path.exists(bf):
            adds = json.load(open(bf)).get("adds", [])
            if adds:
                L.append("    Scout pickups: " + "; ".join(f"{a['name']} ({a['pos']} {a['team']}, {a['acq']}) +{a['gain']:.0f} - {a.get('rc', 'untagged')}"
                                                         + (f" ({a['rc_why']})" if a.get("rc_why") else "") for a in adds))
    L.append("  Flags only - nothing here is a move; any name still needs a live Yahoo check and the full workup.")
    sec = "\n".join(L) + "\n"
    b = open(brief).read() if os.path.exists(brief) else ""
    b = re.sub(r"(?s)\nRatcliffe vs engine - week .*?the full workup\.\n", "\n", b)
    open(brief, "w").write(b.rstrip("\n") + "\n\n" + sec)
    print(sec)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
