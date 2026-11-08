"""Nov 8 2026 (Dom: "Fix" - the 2:06 AM build died when nflverse's GitHub downloads returned 504 Gateway Time-out).
One safe downloader for every nflverse file: tries up to 4 times (waits 15, 30, 60 s), and on success keeps a copy in
the build cache (NFL_CACHE, saved between runs by the workflow). If every try fails it falls back to the last good copy
and says so in the log; only when there is no copy at all does it report a failure.
Use:  python3 nfl_fetch.py URL DEST [--required]      exit 0 = fresh or cached copy in place, 1 = nothing (only if --required)"""
import os, sys, time, shutil, urllib.request, datetime

CACHE = os.environ.get("NFL_CACHE") or os.path.join(os.path.expanduser("~"), ".nflcache")
WAITS = (15, 30, 60)

def _stamp(p):
    t = datetime.datetime.fromtimestamp(os.path.getmtime(p), datetime.timezone.utc)
    return t.astimezone(__import__("zoneinfo").ZoneInfo("America/Los_Angeles")).strftime("%a %b %-d %-I:%M %p PT")

def fetch(url, dest, timeout=180):
    """Returns 'ok', 'cached' or 'failed'. Never leaves a half-written dest behind."""
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    cpath = os.path.join(CACHE, os.path.basename(url))
    tmp = dest + ".part"; err = ""
    for i in range(len(WAITS) + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb") as f:
                shutil.copyfileobj(r, f)
            if os.path.getsize(tmp) == 0: raise IOError("empty download")
            os.replace(tmp, dest)
            try:
                os.makedirs(CACHE, exist_ok=True); shutil.copy2(dest, cpath)
            except Exception as e:
                print(f"   (cache copy not saved: {e})")
            return "ok"
        except Exception as e:
            err = str(e)[:120]
            if os.path.exists(tmp): os.remove(tmp)
            if i < len(WAITS):
                print(f"   {os.path.basename(url)}: try {i+1} failed ({err}) - retrying in {WAITS[i]} s"); time.sleep(WAITS[i])
    if os.path.exists(cpath):
        shutil.copy2(cpath, dest)
        print(f"!! {os.path.basename(url)}: nflverse unreachable ({err}) - using the last good copy from {_stamp(cpath)}")
        return "cached"
    print(f"!! {os.path.basename(url)}: nflverse unreachable ({err}) and no saved copy yet")
    return "failed"

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    s = fetch(a[0], a[1])
    sys.exit(1 if (s == "failed" and "--required" in sys.argv) else 0)
