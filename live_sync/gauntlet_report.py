# THE GAUNTLET REPORT (Dom, Wed Oct 14 2026)
# The gauntlet = system check -> Yahoo read -> Dispatch build -> Live sync -> system check again.
# This script turns the run into Dom's go / no-go checklist and folds it into live/health, so the Live page's
# Data panel and the push notification say the same thing:
#   what ran, what is current, what broke and fixed itself on the way, what is still broken, and GO or NO-GO.
# Usage: python3 gauntlet_report.py <pre health.json> <post health.json> <steps.json> <out.json>
#   steps.json (written by the gauntlet task):
#   {"started": ISO, "finished": ISO, "trigger": "scheduled" | "refresh" | "chat",
#    "read":  {"status": "ok" | "failed" | "missing", "detail": "...", "tries": 1 | 2},
#    "sync":  {"status": "ok" | "failed" | "skipped", "detail": "CHAIN ... line"},
#    "alerts":{"status": "ok" | "failed" | "skipped", "detail": "ALERTS ... line"}}
import json, sys, datetime as dt
pre, post, steps = (json.load(open(p)) for p in sys.argv[1:4]); out = sys.argv[4]
PT = dt.timezone(dt.timedelta(hours=-7))
def pt(iso):
    try: t = dt.datetime.fromisoformat(str(iso).replace("Z", "+00:00")).astimezone(PT)
    except Exception: return ""
    return f"{t:%a} {t.hour % 12 or 12}:{t:%M} {'AM' if t.hour < 12 else 'PM'}"
RANK = {"red": 3, "yellow": 2, "green": 1, "grey": 0}   # grey rows are information only - they never outrank a green
def worst(rows): return max((r["status"] for r in rows), key=lambda s: RANK.get(s, 0), default="grey")
live_rows = [r for r in post.get("rows", []) if r["group"] != "Known issues"]
def grp(*names): return [r for r in live_rows if r["group"] in names]
def named(group, word): return [r for r in live_rows if r["group"] == group and word.lower() in r["name"].lower()]
def why(rows):
    bad = [r for r in rows if r["status"] in ("red", "yellow")]
    return "; ".join(f'{r["name"]}: {r["detail"]}' for r in bad[:2]) if bad else (rows[0]["detail"] if rows else "")
R = steps.get("read", {}); S = steps.get("sync", {}); A = steps.get("alerts", {})
read_st = {"ok": "green", "failed": "red", "missing": "red"}.get(R.get("status"), "yellow")
items = [
    ("Yahoo read", read_st, R.get("detail") or ""),
    ("Dispatch build", worst(grp("Dispatch")), why(grp("Dispatch"))),
    ("Gotham", worst(grp("Gotham")), why(grp("Gotham"))),
    ("Scout", worst(grp("Scout")), why(grp("Scout"))),
    ("Radar", worst(grp("Radar")), why(grp("Radar"))),
    ("Meters (Live)", {"ok": "green", "failed": "red"}.get(S.get("status"), "yellow"), S.get("detail") or ""),
    ("Alerts", worst(grp("Alerts")) if A.get("status") == "ok" else "red", (A.get("detail") or "") + (" - " + why(grp("Alerts")) if worst(grp("Alerts")) != "green" else "")),
    ("Weather", worst(named("Feeds", "weather")) if named("Feeds", "weather") else "grey", why(named("Feeds", "weather")) or "rides with the build"),
    ("News + injury feeds", worst([r for r in grp("Feeds") if "weather" not in r["name"].lower()]), why([r for r in grp("Feeds") if "weather" not in r["name"].lower()])),
    ("Projections", worst(grp("Projections")), why(grp("Projections"))),
    ("Scoreboard", worst(grp("Checks")), why(grp("Checks"))),
    ("Live page", worst(grp("Live")), why(grp("Live"))),
]
# fixed on the way: red/yellow before the run, green after (and a read that needed a second try)
pre_bad = {(r["group"], r["name"]): r for r in pre.get("rows", []) if r["group"] != "Known issues" and r["status"] in ("red", "yellow")}
post_by = {(r["group"], r["name"]): r for r in live_rows}
healed = [f'{k[0]}: {k[1]} was {v["status"]} before the run ({v["detail"]}) - now green' for k, v in pre_bad.items()
          if post_by.get(k, {}).get("status") == "green"]
if R.get("status") == "ok" and int(R.get("tries") or 1) > 1: healed.insert(0, "Yahoo read failed on the first try and was started again - second try worked")
still = [f'{n}: {d}' for n, s, d in items if s == "red"]
watch = [f'{n}: {d}' for n, s, d in items if s == "yellow"]
known = [r for r in post.get("rows", []) if r["group"] == "Known issues" and r["status"] == "red"]
verdict = "NO-GO" if still else "GO"
lines = [f"GAUNTLET {verdict} - {pt(steps.get('finished') or post.get('checked'))} PT"]
lines += [f"  {'OK ' if s == 'green' else 'BAD' if s == 'red' else 'WATCH' if s == 'yellow' else '-- '} {n}" + (f" - {d}" if s != "green" and d else "") for n, s, d in items]
if healed: lines += ["Fixed on its own:"] + ["  " + h for h in healed]
if still: lines += ["Still broken - reach out to Claude:"] + ["  " + x for x in still]
if known: lines += ["Known open issues:"] + ["  " + r["name"] for r in known]
post["gauntlet"] = dict(verdict=verdict, started=steps.get("started"), finished=steps.get("finished"), trigger=steps.get("trigger", "scheduled"),
                        items=[dict(name=n, status=s, detail=d) for n, s, d in items], healed=healed, still=still, watch=watch,
                        summary=(f"GO - everything ran and is current" if not still and not watch else
                                 f"GO - {len(watch)} to watch" if not still else f"NO-GO - {len(still)} broken: " + "; ".join(x.split(':')[0] for x in still)))
json.dump(post, open(out, "w"), indent=1)
print("\n".join(lines))
