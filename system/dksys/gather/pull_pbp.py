import urllib.request, os, time, json, datetime
URL='https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2026.csv.gz'
DST='/home/claude/dksys/data/latest/pbp/pbp_2026.csv.gz'
def main():
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    t=time.time()
    req=urllib.request.Request(URL, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=180) as r, open(DST,'wb') as f:
        status=r.status; f.write(r.read())
    now=datetime.datetime.now(datetime.timezone.utc)
    print('HTTP', status, os.path.getsize(DST), 'bytes', '%.1fs'%(time.time()-t))
    print('pulled', now.strftime('%Y-%m-%d %H:%M UTC'), '/',
          (now-datetime.timedelta(hours=7)).strftime('%H:%M PT'))
if __name__=='__main__': main()
