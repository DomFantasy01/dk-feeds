import os, sys, time, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nfl_fetch import fetch
URL='https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2026.csv.gz'
DST='/home/claude/dksys/data/latest/pbp/pbp_2026.csv.gz'
def main():
    # Nov 8: retries + last-good-copy fallback (nfl_fetch) - a GitHub 504 no longer kills the build
    t=time.time(); s=fetch(URL, DST)
    if s=='failed': print('!! pbp: no play-by-play this build'); sys.exit(1)
    now=datetime.datetime.now(datetime.timezone.utc)
    print('pbp', s, os.path.getsize(DST), 'bytes', '%.1fs'%(time.time()-t))
    print('pulled', now.strftime('%Y-%m-%d %H:%M UTC'), '/',
          now.astimezone(__import__("zoneinfo").ZoneInfo("America/Los_Angeles")).strftime('%H:%M PT'))
if __name__=='__main__': main()
