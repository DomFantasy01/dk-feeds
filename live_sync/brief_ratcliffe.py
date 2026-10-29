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
    src = M.get("sources", {}).get("ratcliffe", {}); ksrc = M.get("sources", {}).get("koerner", {})
    L = [f"Ratcliffe vs engine - week {M['week']} (FTN read {src.get('pulled_pt', 'missing')}; Koerner read {ksrc.get('pulled_pt', 'missing')}; Ratcliffe leads, Koerner and the engine show beside him)"]
    if ksrc.get("status") != "OK": L.append(f"  Koerner's numbers are {ksrc.get('status', 'MISSING')} - his column is blank until the next FantasyLabs read.")
    if src.get("status") != "OK":
        L.append(f"  Ratcliffe's numbers are {src.get('status', 'MISSING')} - the meters show Yahoo in his place until the next FTN read.")
    for lab, bk in BOARDS:
        lg = M["leagues"].get(lab)
        if not lg: continue
        n = lg["needles"]
        L.append(f"  {lab}: chance to win this week - Yahoo {n.get('yahoo')}% (as set), Ratcliffe {n.get('ratcliffe')}%, Koerner {n.get('koerner') if n.get('koerner') is not None else 'no read'}"
                 + ("%" if n.get('koerner') is not None else "") + f", Gotham {n.get('gotham')}% (best lineups)")
        split = []
        for s in lg["starters"]["me"]:
            r, g = s.get("ratcliffe"), s.get("gotham")
            if s.get("ratcliffe_src") != "ftn":
                split.append(f"{s['player']} engine only (Ratcliffe doesn't project him)"); continue
            if r is not None and g is not None and abs(r - g) >= 3:
                split.append(f"{s['player']} Ratcliffe {r:.1f} vs engine {g:.1f}")
        if split: L.append("    Your starters where they split by 3+ points: " + "; ".join(split))
        # Oct 29 (Dom): Koerner beside Ratcliffe - always say when the two experts disagree on one of his starters
        ks = [f"{s['player']} Ratcliffe {s['ratcliffe']:.1f} vs Koerner {s['koerner']:.1f}" for s in lg["starters"]["me"]
              if s.get("ratcliffe_src") == "ftn" and s.get("koerner_src") == "flabs" and s.get("actual") is None
              and abs(s["ratcliffe"] - s["koerner"]) >= max(3.0, .25 * max(s["ratcliffe"], s["koerner"]))]
        if ks: L.append("    Experts split (Ratcliffe vs Koerner) on your starters: " + "; ".join(ks))
        bf = f"{repo}/dispatch_out/scout_state/scout_board_{bk}.json"
        if os.path.exists(bf):
            adds = json.load(open(bf)).get("adds", [])
            if adds:
                L.append("    Scout pickups: " + "; ".join(f"{a['name']} ({a['pos']} {a['team']}, {a['acq']}) +{a['gain']:.0f} - {a.get('rc', 'untagged')}"
                                                         + (f" ({a['rc_why']})" if a.get("rc_why") else "") + (f"; {a['ko']}" if a.get("ko") else "") for a in adds))
    L.append("  Flags only - nothing here is a move; any name still needs a live Yahoo check and the full workup.")
    sec = "\n".join(L) + "\n"
    b = open(brief).read() if os.path.exists(brief) else ""
    b = re.sub(r"(?s)\nRatcliffe vs engine - week .*?the full workup\.\n", "\n", b)
    open(brief, "w").write(b.rstrip("\n") + "\n\n" + sec)
    print(sec)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
