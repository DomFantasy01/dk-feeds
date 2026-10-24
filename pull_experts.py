"""EXPERT PULL (Oct 24 2026, Dom). Each named expert's OWN weekly rankings (not a consensus), straight from FantasyPros'
public partner feed - the same feed the FantasyPros rankings widgets on expert sites use. No browser, no login.
Panel: Mick Ciallela (accuracy #1), Jeff Ratcliffe (#4), Patrick Thorman (#5), Sean Koerner (#7); Nathan Jahnke (#8) is the
backup who fills in if one of them has no list this week. Accuracy = FantasyPros 2026 in-season, season to date.
Writes yahoo_drop/morning/expert_rankings.txt (site|expert|list|rank|player|nflteam|pos) plus each expert's published time.
A failed expert is logged and the file says so; if no expert comes back the old file is left alone and the run fails loudly."""
import json, os, sys, time, datetime as dt, urllib.request, urllib.error
EXPERTS = [(1667, "Mick Ciallela"), (125, "Jeff Ratcliffe"), (534, "Patrick Thorman"), (120, "Sean Koerner"), (540, "Nathan Jahnke")]
POS = ["QB", "RB", "WR", "TE"]
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
    now = dt.datetime.now(dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=-7)))
    stamp = f"{now:%a %b} {now.day} {now:%Y} {now.hour % 12 or 12}:{now:%M} {'AM' if now.hour < 12 else 'PM'} PT"
    rows, log, got = [], [], 0
    for eid, name in EXPERTS:
        counts, pubs = [], set()
        for p in POS:
            j = get(eid, p, w)
            if not j: counts.append(f"{p}0"); continue
            pubs.add(str(j.get("published", "")))
            for pl in j["players"]:
                rk = str(pl.get("pos_rank", "")).lstrip("QBRWTE") or str(pl.get("rank", ""))
                rows.append("|".join(["FP", name, p, rk, pl.get("player_name", ""), pl.get("player_team_id", ""), p]))
            counts.append(f"{p}{len(j['players'])}")
        ok = all(c[2:] != "0" for c in counts)
        got += ok
        log.append(f"{name}: {'/'.join(counts)}, last updated {max(pubs) if pubs else 'none'} (FantasyPros time)" + ("" if ok else " - INCOMPLETE"))
    if not got:
        print("EXPERT PULL FAILED - no expert came back; old file left in place"); print("\n".join(log)); sys.exit(1)
    od = f"{repo}/yahoo_drop/morning"; os.makedirs(od, exist_ok=True)
    head = (f"# Named expert weekly rankings, week {w}. FantasyPros partner feed, read live {stamp} (GitHub read). "
            f"site|expert|list|rank|player|nflteam|pos\n" + "".join(f"# {l}\n" for l in log))
    open(f"{od}/expert_rankings.txt", "w").write(head + "\n".join(rows) + "\n")
    print(f"EXPERT PULL week {w} {stamp}: {got} of {len(EXPERTS)} experts complete"); print("\n".join(log))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
