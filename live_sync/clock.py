"""THE CLOCK (Nov 4 2026, Dom: "fix the engines").
GitHub's scheduler drops scheduled runs when it is busy. On Nov 4 the news feed job (set for every 30 minutes) ran only
about once an hour, 15-25 minutes late; the projection job (hourly) missed its 4 PM and 6 PM runs; the 7:40 PM Dispatch
build never started. Every light on Live that turned red that day traced back to a run GitHub never started.

This job is a missed-run catcher. It stays awake for just under 6 hours, and every 4 minutes it looks at each watched
job's own cron lines: if a scheduled time passed more than GRACE minutes ago and that job has not started since
(any trigger - schedule, a Claude task's 'Run workflow', a manual run), it starts the job itself through
workflow_dispatch, once per missed time. It never writes to the repo and never runs a build itself.

Guard: the writer jobs share one GitHub queue (concurrency group dk-feeds), and GitHub keeps only ONE waiting run per
queue - a new one cancels the one already waiting. So the clock never starts a job while another run in that queue is
waiting; it tries again on its next pass.

usage: python live_sync/clock.py [--dry-run --now ISO --runs runs.json]   (GH_TOKEN, GITHUB_REPOSITORY from Actions)
"""
import json, os, re, sys, time, subprocess, datetime as dt
from croniter import croniter

UTC = dt.timezone.utc
REPO = os.environ.get("GITHUB_REPOSITORY", "DomFantasy01/dk-feeds")
WATCH = ["pull.yml", "proj.yml", "dispatch.yml"]   # the jobs whose schedules GitHub drops
GRACE = 26          # minutes: on Nov 4 GitHub started the scheduled runs it did keep 10-25 minutes late - wait that out first
LOOKBACK = 55       # minutes: only catch a slot this recent (an older miss is covered by the next slot)
EARLY = {"dispatch.yml": 8}    # minutes: a build started up to 8 min before the slot covers it (others: 3)
# Nov 8 (Dom: "the page should update every 20 minutes in games"): with the 20-minute game-window builds, a 26-minute grace
# meant the newest slot was ALWAYS younger than the grace, so the clock never caught a missed 20-minute build - Sunday night
# the page went about an hour between builds. The Dispatch build now gets its own short grace.
GRACE_WF = {"dispatch.yml": 7}
PASS = 4            # minutes between passes
LIFE = 345          # minutes this run stays awake (GitHub's limit is 360)
WAITING = {"queued", "waiting", "pending", "requested"}
A = sys.argv[1:]
DRY = "--dry-run" in A

def crons(wf):
    txt = open(f".github/workflows/{wf}").read()
    return re.findall(r"^\s*-\s*cron:\s*'([^']+)'", txt, re.M)

def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)

def runs():
    if "--runs" in A: return json.load(open(A[A.index("--runs") + 1]))
    r = gh("api", f"repos/{REPO}/actions/runs?per_page=100")
    if r.returncode: raise RuntimeError(r.stderr.strip()[:200])
    return json.loads(r.stdout)["workflow_runs"]

def ts(s): return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))

def last_slot(wf, now):
    s = [croniter(c, now).get_prev(dt.datetime) for c in crons(wf)]
    return max(s) if s else None

def one_pass(now, R, fired, log):
    qwait = [r for r in R if r.get("path", "").split("/")[-1] in WATCH + ["experts.yml", "waiver_experts.yml", "yahoo_auth.yml", "yahoo_probe.yml"]
             and r.get("status") in WAITING]
    for wf in WATCH:
        S = last_slot(wf, now)
        if not S: continue
        age = (now - S).total_seconds() / 60
        if age < GRACE_WF.get(wf, GRACE) or age > LOOKBACK or (wf, S) in fired: continue
        mine = [r for r in R if r.get("path", "").endswith("/" + wf)]
        if any(ts(r["created_at"]) >= S - dt.timedelta(minutes=EARLY.get(wf, 3)) for r in mine): continue
        if qwait:
            log(f"{now:%H:%MZ} {wf}: slot {S:%H:%MZ} missed, but a run is waiting in the queue - trying next pass")
            continue
        fired.add((wf, S))
        if DRY:
            log(f"{now:%H:%MZ} {wf}: slot {S:%H:%MZ} missed ({age:.0f} min) - WOULD START")
            continue
        r = gh("workflow", "run", wf, "-R", REPO, "--ref", "main")
        log(f"{now:%H:%MZ} {wf}: slot {S:%H:%MZ} missed ({age:.0f} min) - started: " + ("ok" if r.returncode == 0 else r.stderr.strip()[:200]))
        qwait = [1]   # what we just started now waits in the queue; the next job waits for the next pass

def main():
    log = lambda m: print(m, flush=True)
    fired = set()
    if DRY:
        now = ts(A[A.index("--now") + 1]) if "--now" in A else dt.datetime.now(UTC)
        one_pass(now, runs(), fired, log); return
    t0 = time.time()
    log(f"clock awake {dt.datetime.now(UTC):%Y-%m-%d %H:%MZ}; watching {', '.join(WATCH)}")
    while (time.time() - t0) / 60 < LIFE:
        try: one_pass(dt.datetime.now(UTC), runs(), fired, log)
        except Exception as e: log(f"pass failed: {e}")
        time.sleep(PASS * 60)
    r = gh("workflow", "run", "clock.yml", "-R", REPO, "--ref", "main")   # hand off to the next clock
    log("handoff to next clock: " + ("ok" if r.returncode == 0 else r.stderr.strip()[:200]))

if __name__ == "__main__":
    main()
