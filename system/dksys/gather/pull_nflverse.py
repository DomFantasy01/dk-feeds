"""Stage 1 GATHER — free nflverse data (schedule + Vegas, snaps, weekly stats,
official practice/injury reports, rosters). Downloads fresh copies every run;
previous copies move to data/archive/<stamp>/. Reports failures, never hides them."""
import os, sys, shutil, urllib.request, datetime
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import manifest as M

SEASON = 2026
SRC = {
 "games":      "https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv",
 "snap_counts":f"https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_{SEASON}.csv",
 "stats_week": f"https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_{SEASON}.csv",
 "injuries":   f"https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_{SEASON}.csv",
 "depth_charts":f"https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_{SEASON}.csv",
 "rosters_nfl":f"https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_{SEASON}.csv",
}

def freshness(key, path):
    df = pd.read_csv(path, low_memory=False)
    if "season" in df.columns:
        df = df[df.season == SEASON]
    note = ""
    if key == "games":
        wk = {}
        for w in sorted(df.week.unique()):
            d = df[df.week == w]
            wk[int(w)] = (int(d.spread_line.notna().sum()), len(d))
        played = df[df.result.notna()].week.max()
        nxt = [w for w,(a,b) in wk.items() if w > (played or 0)][:2]
        note = f"last played wk {int(played) if played==played else 0}; lines " + ", ".join(f"wk{w} {wk[w][0]}/{wk[w][1]}" for w in nxt)
    elif "week" in df.columns:
        note = f"weeks {int(df.week.min())}-{int(df.week.max())}"
    return len(df), note

def pull(key):
    url = SRC[key]
    dest = os.path.join(M.LATEST, f"{key}.csv")
    tmp = dest + ".part"
    try:
        urllib.request.urlretrieve(url, tmp)
        rows, note = freshness(key, tmp)
        if os.path.exists(dest):
            stamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M")
            arc = os.path.join(M.ROOT, "data", "archive", stamp); os.makedirs(arc, exist_ok=True)
            shutil.move(dest, os.path.join(arc, f"{key}.csv"))
        os.replace(tmp, dest)
        return M.record(key, source="nflverse", url=url, status="ok", rows=rows,
                        bytes=os.path.getsize(dest), freshness=note)
    except Exception as e:
        if os.path.exists(tmp): os.remove(tmp)
        return M.record(key, source="nflverse", url=url, status="FAILED", error=str(e)[:200])

if __name__ == "__main__":
    for k in (sys.argv[1:] or SRC):
        e = pull(k); print(k, e["status"], e.get("freshness", e.get("error","")))
