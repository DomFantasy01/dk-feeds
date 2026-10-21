"""Stage 1 GATHER — pull log. Every file in data/latest gets one entry:
source, url, pulled (UTC and Pacific), size, rows, freshest week, status.
Nothing downstream may read a file that has no manifest entry."""
import json, os, datetime
from zoneinfo import ZoneInfo
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LATEST = os.path.join(ROOT, "data", "latest")
MAN = os.path.join(LATEST, "manifest.json")
PT = ZoneInfo("America/Los_Angeles")

def now_stamps():
    u = datetime.datetime.now(datetime.timezone.utc)
    p = u.astimezone(PT)
    return u.strftime("%Y-%m-%d %H:%M UTC"), p.strftime("%a %b %d %Y %I:%M %p %Z")

def load():
    if os.path.exists(MAN):
        return json.load(open(MAN))
    return {}

def record(key, **fields):
    m = load()
    utc, pt = now_stamps()
    fields.setdefault("pulled_utc", utc)
    fields.setdefault("pulled_pt", pt)
    m[key] = fields
    json.dump(m, open(MAN, "w"), indent=2)
    return m[key]

def report():
    m = load()
    lines = []
    for k in sorted(m):
        e = m[k]
        lines.append(f"{k:28s} {e.get('status','?'):7s} {e.get('pulled_pt','?'):32s} rows={e.get('rows','-')} {e.get('freshness','')}")
    return "\n".join(lines)

if __name__ == "__main__":
    print(report())
