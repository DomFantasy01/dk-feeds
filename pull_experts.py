"""EXPERT PULL (Oct 24 2026, Dom). Each named expert's OWN weekly rankings (not a consensus), straight from FantasyPros'
public partner feed - the same feed the FantasyPros rankings widgets on expert sites use. No browser, no login.
Panel: Mick Ciallela (accuracy #1), Jeff Ratcliffe (#4), Patrick Thorman (#5), Sean Koerner (#7); Nathan Jahnke (#8) is the
backup who fills in if one of them has no list this week. Accuracy = FantasyPros 2026 in-season, season to date.
Writes yahoo_drop/morning/expert_rankings.txt (site|expert|list|rank|player|nflteam|pos) plus each expert's published time.
A failed expert is logged and the file says so; if no expert comes back the old file is left alone and the run fails loudly."""
import json, os, re, sys, time, datetime as dt, urllib.request, urllib.error
EXPERTS = [(125, "Jeff Ratcliffe"), (120, "Sean Koerner")]   # Nov 3 (Dom): the five ranking experts (Brenton, Ciallela, Orginski, Jahnke, Thorman) are "all useless" - removed Nov 4   # was:    # Oct 31 (Dom: "I want another expert ... I don't want to pay"): Brenton (Points Over Hype) - FantasyPros 2026 in-season accuracy #1, free feed   # Oct 29 (Dom): Orginski (FTN) added - 2026 accuracy #3
POS = ["QB", "RB", "WR", "TE", "DST", "K"]   # Nov 1 (Dom: "we should be looking at everything"): defenses and kickers too
API = "https://partners.fantasypros.com/api/v1/expert-rankings.php"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "Accept": "application/json"}

def week():
    s = json.loads(urllib.request.urlopen(urllib.request.Request("https://api.sleeper.app/v1/state/nfl", headers=UA), timeout=30).read())
    return int(s["week"])

def get(eid, pos, w):
    for scoring in (("PPR", "STD") if pos == "QB" else ("PPR",)):
        url = f"{API}?id={eid}&scoring={scoring}&type=WEEKLY&position={pos}&sport=NFL&year=2026&week={w}"
        for a in range(3):
            try:
                j = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read())
                if j.get("players"): return j
                break
            except Exception as e:
                err = e; time.sleep(3 * (a + 1))
    return None

def main(repo="."):
    w = int(os.environ.get("DK_WEEK") or week())
    now = dt.datetime.now(dt.timezone.utc).astimezone(__import__("zoneinfo").ZoneInfo("America/Los_Angeles"))
    stamp = f"{now:%a %b} {now.day} {now:%Y} {now.hour % 12 or 12}:{now:%M} {'AM' if now.hour < 12 else 'PM'} PT"
    rows, log, got = [], [], 0
    # Nov 5 (Dom, "Fix"): an expert can come back empty for a few minutes while he republishes (Ratcliffe, 3:41 PM Nov 5).
    # Keep his last good rows for that position from the previous file instead of wiping them, and say so in the header.
    prev, prev_stamp = {}, ""
    try:
        for ln in open(f"{repo}/yahoo_drop/morning/expert_rankings.txt"):
            if ln.startswith("# Named expert"):
                m = re.search(rf"week {w}\. .*?read live (.+?) \(", ln); prev_stamp = m.group(1) if m else ""
            elif not ln.startswith("#") and ln.count("|") == 6 and prev_stamp:
                f = ln.rstrip("\n").split("|"); prev.setdefault((f[1], f[2]), []).append(ln.rstrip("\n"))
    except FileNotFoundError:
        pass
    for eid, name in EXPERTS:
        counts, pubs, kept = [], set(), []
        for p in POS:
            j = get(eid, p, w)
            if not j:
                old = prev.get((name, p), [])
                if old: rows.extend(old); kept.append(p); counts.append(f"{p}{len(old)}")
                else: counts.append(f"{p}0")
                continue
            pubs.add(str(j.get("published", "")))
            for pl in j["players"]:
                rk = re.sub(r"^[A-Z]+", "", str(pl.get("pos_rank", ""))) or str(pl.get("rank", ""))
                rows.append("|".join(["FP", name, p, rk, pl.get("player_name", ""), pl.get("player_team_id", ""), p]))
            counts.append(f"{p}{len(j['players'])}")
        ok = all(int(re.sub(r"^[A-Z]+", "", c)) > 0 for c in counts)   # Nov 5 fix: was c[2:], which read "K30" as 0 and failed complete lists
        got += ok
        note = f" - {'/'.join(kept)} kept from the {prev_stamp} pull (feed empty right now)" if kept else ""
        log.append(f"{name}: {'/'.join(counts)}, last updated {max(pubs) if pubs else 'none'} (FantasyPros time)" + ("" if ok else " - INCOMPLETE") + note)
    if not got:
        print("EXPERT PULL FAILED - no expert came back; old file left in place"); print("\n".join(log)); sys.exit(1)
    od = f"{repo}/yahoo_drop/morning"; os.makedirs(od, exist_ok=True)
    head = (f"# Named expert weekly rankings, week {w}. FantasyPros partner feed, read live {stamp} (GitHub read). "
            f"site|expert|list|rank|player|nflteam|pos\n" + "".join(f"# {l}\n" for l in log))
    open(f"{od}/expert_rankings.txt", "w").write(head + "\n".join(rows) + "\n")
    print(f"EXPERT PULL week {w} {stamp}: {got} of {len(EXPERTS)} experts complete"); print("\n".join(log))
    snapshot(od, w, head, rows)
    # Oct 25 (Dom): week-to-week moves need last week's list - pull it once if it was never saved
    hd = f"{od}/expert_history"
    if not os.environ.get("DK_WEEK") and w > 1 and not any(f.startswith(f"wk{w-1}_") for f in os.listdir(hd)):
        prow, plog = [], []
        for eid, name in EXPERTS:
            n_ = 0
            for p in POS:
                j = get(eid, p, w - 1)
                for pl in (j or {}).get("players", []):
                    rk = re.sub(r"^[A-Z]+", "", str(pl.get("pos_rank", ""))) or str(pl.get("rank", ""))
                    prow.append("|".join(["FP", name, p, rk, pl.get("player_name", ""), pl.get("player_team_id", ""), p])); n_ += 1
            plog.append(f"{name}: {n_} rows (week {w-1} final list, backfilled)")
        if prow:
            snapshot(od, w - 1, f"# Named expert weekly rankings, week {w-1}. FantasyPros partner feed, read live {stamp} (GitHub read, backfill of last week's final list). site|expert|list|rank|player|nflteam|pos\n"
                     + "".join(f"# {l}\n" for l in plog), prow, tag="final")
            print(f"backfilled week {w-1}: {len(prow)} rows")

def snapshot(od, w, head, rows, tag=None):
    """Oct 25 (Dom): keep every pull so expert_moves.py can say who moved up and down. Skips a pull identical to the last one."""
    hd = f"{od}/expert_history"; os.makedirs(hd, exist_ok=True)
    body = "\n".join(rows) + "\n"
    prev = sorted(f for f in os.listdir(hd) if f.startswith(f"wk{w}_"))
    if prev and not tag and [l for l in open(f"{hd}/{prev[-1]}").read().splitlines() if not l.startswith("#")] == rows: return
    t = tag or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%MZ")
    open(f"{hd}/wk{w}_{t}.txt", "w").write(head + body)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
