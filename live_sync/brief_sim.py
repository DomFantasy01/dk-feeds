"""SIMULATOR in the brief (Oct 28 2026, Dom: "run sims as another test of my teams"). Appends the simulator's
report (dispatch_out/sim/sim_latest.txt) to the brief, replacing its own section. Flags only - nothing here is a move."""
import os, re, sys
def main(sim_txt, brief):
    if not os.path.exists(sim_txt): print("no simulator report - section skipped"); return
    body = open(sim_txt).read().strip()
    sec = "Simulator - " + body.split("THE SIMULATOR - ", 1)[-1] + "\n  Flags only - the simulator tests; you decide.\n"
    b = open(brief).read() if os.path.exists(brief) else ""
    b = re.sub(r"(?s)\nSimulator - .*?Flags only - the simulator tests; you decide\.\n", "\n", b)
    open(brief, "w").write(b.rstrip("\n") + "\n\n" + sec)
    print(sec)
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
