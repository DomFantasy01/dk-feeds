"""WAIVER EXPERTS (Oct 27 2026, Dom: "We need experts that let us know before waiver wire picks").
The weekly-rankings panel (pull_experts.py) posts Wed/Thu - after claims run. This pulls named experts' FREE waiver columns,
which post Sun night - Tue, before claims process. Picked from FantasyPros 2026 in-season accuracy (season to date, read Oct 27):
  Nathan Jahnke (PFF)         #8  - already on the panel. Column posts Sunday night; only the top takeaways + QBs are free.
  Justin Boone (Yahoo)        #16 - full free column Tuesday morning, with a FAB bid on a $100 budget and drop candidates.
  Kevin English (Draft Sharks) #51 (Draft Sharks' Smola #9, Jody Smith #13) - full free column Tuesday, blind-bid % and drops.
Writes yahoo_drop/morning/waiver_experts.txt: expert|site|acc_rank|posted|order|player|pos|team|section|bid
A source that fails is logged and the others still write. Nothing is ever acted on from this file - it's the expert side of
the waiver-night check, beside the Scout."""
import json, os, re, sys, html, datetime as dt, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en-US,en;q=0.9"}

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read().decode("utf-8", "replace")

def text_of(h):
    h = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</?(p|div|h\d|li|tr|td|th|section|article|header|span|strong|figcaption)[^>]*>", "\n", h)
    h = html.unescape(re.sub(r"<[^>]+>", " ", h))
    return [re.sub(r"\s+", " ", l).strip() for l in h.split("\n") if l.strip()]

def week():
    s = json.loads(urllib.request.urlopen(urllib.request.Request("https://api.sleeper.app/v1/state/nfl", headers=UA), timeout=30).read())
    return int(s["week"])

def sq(n): return re.sub(r"[^a-z]", "", re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", "", n.lower()))

def player_index(repo):
    d = json.load(open(f"{repo}/feeds/sleeper_players_min.json"))["players"]
    idx = {}
    for p in d.values():
        if p.get("team") and p.get("pos") in ("QB", "RB", "WR", "TE", "K") and p.get("name"):
            idx.setdefault(sq(p["name"]), (p["name"], p["pos"], p["team"]))
    for nick, full in (("Bam Knight", "Zonovan Knight"), ("Chig Okonkwo", "Chigoziem Okonkwo"), ("Andy Borregales", "Andres Borregales")):
        if sq(full) in idx: idx.setdefault(sq(nick), idx[sq(full)])
    return idx

NAME_RE = re.compile(r"^([A-Z][A-Za-z.'\-]+(?: [A-Z][A-Za-z.'\-]+){1,3})(?=,| at | vs\.? | \(|/|$)")

def picks_from(lines, idx, start_pat, stop_pat, bid_pat=None, sections=None):
    out, sec, on, seen = [], "", False, set()
    for i, l in enumerate(lines):
        if not on:
            on = bool(re.search(start_pat, l))
            if on and sections:
                for pat, name in sections:
                    if re.fullmatch(pat, l, flags=re.I): sec = name
            continue
        if re.search(stop_pat, l): break
        if sections:
            for pat, name in sections:
                if re.fullmatch(pat, l, flags=re.I): sec = name
        if len(l) < 60 and re.search(r"(?i)(stash|stream|flex option|backup|dart-throw|options?$)", l) and not NAME_RE.match(l.split(" at ")[0]):
            sec = sec.split(":")[0] + ":" + l.lower()
        if re.match(r"(?i)^(quarterbacks|running backs|wide receivers|tight ends):", l):   # drop lists: "Running Backs: A, B"
            for nm in l.split(":", 1)[1].split(","):
                k = sq(nm)
                if k in idx and ("drop", k) not in seen:
                    seen.add(("drop", k)); out.append((idx[k], "drop", ""))
            continue
        for nm in [x.strip() for x in l.split("/")] if "/" in l and "%" not in l else [l]:
            m = NAME_RE.match(nm)
            if not m: continue
            k = sq(m.group(1))
            if k not in idx or (sec, k) in seen: continue
            bid = ""
            if bid_pat:
                for nxt in lines[i + 1:i + 9]:
                    if NAME_RE.match(nxt) and sq(NAME_RE.match(nxt).group(1)) in idx: break
                    b = re.search(bid_pat, nxt)
                    if b: bid = b.group(1); break
            seen.add((sec, k)); out.append((idx[k], sec, bid))
    return out

def boone(w, idx):
    a = get("https://sports.yahoo.com/author/justin-boone/")
    m = re.search(rf'href="(?:https://sports\.yahoo\.com)?(/fantasy/article/week-{w}-[^"]*waiver[^"]*\.html)"', a)
    if not m: return None, "no Week %d column on his author page yet" % w
    url = "https://sports.yahoo.com" + m.group(1)
    h = get(url); L = text_of(h)
    t = re.search(r'datetime="([^"]+)"', h)
    secs = [(r"top-10 overall pickups.*", "top10"), (r"quarterbacks", "QB"), (r"running backs", "RB"), (r"wide receivers", "WR"),
            (r"tight ends", "TE"), (r"week \d+ streamers", "streamers"), (r"drop candidates", "drop")]
    p = picks_from(L, idx, r"(?i)^top-10 overall pickups", r"(?i)^(read next|add yahoo sports)", r"^\$(\d+)$", secs)
    # Boone's FAB sits a few lines under each name; a "$5/$7" pair line covers a two-player heading
    return dict(expert="Justin Boone", site="Yahoo", acc="16", url=url, posted=t.group(1) if t else "", picks=p,
                note="FAB on a $100 budget"), ""

def english(w, idx):
    url = f"https://www.draftsharks.com/article/week-{w}-waiver-wire-pickups"
    h = get(url); L = text_of(h)
    if not any(re.search(rf"(?i)week {w} waiver", l) for l in L[:200]): return None, "page is not the Week %d column yet" % w
    by = next((l for l in L if l.startswith("By ")), "")
    t = next((l for l in L if re.match(r"^[A-Z][a-z]{2} \d{1,2}, 20\d\d at", l)), "")
    secs = [(r"priority targets", "priority"), (r"immediate help", "immediate"), (r"qb streamers", "QB stream"),
            (r"deep-league (options|plays)", "deep"), (r"upside stashes", "stash"), (r"injuries to (watch|note)", "injury-watch"),
            (r"top rb handcuffs", "handcuff"), (r"drops", "drop")]
    DIAG["english"] = f"{len(L)} lines, start found: {any(re.search('(?i)^priority targets$', l) for l in L)}, first: {' / '.join(L[:6])[:200]}"
    k0 = max([i for i, l in enumerate(L) if re.fullmatch(r"(?i)priority targets", l)] or [0])
    L = L[k0 - 1:] if k0 else L
    p = picks_from(L, idx, r"(?i)^priority targets$", r"(?i)^(top streaming defense|kevin english, senior)", r"(?i)blind bid recommendation:\s*([\d\-]+%)", secs)
    p = [x for x in p if x[1] not in ("injury-watch",)]
    return dict(expert=by[3:].strip() or "Kevin English", site="Draft Sharks", acc="51 (site: 9, 13)", url=url, posted=t, picks=p,
                note="blind bid as % of budget"), ""

def jahnke(w, idx):
    url = "https://www.pff.com/news/fantasy-football-waiver-wire-targets-2026"
    h = get(url); L = text_of(h)
    if not any(re.search(rf"(?i)week {w}\b", l) for l in L[:400]): return None, "PFF's column is not on Week %d yet" % w
    t = re.search(r'datetime="([^"]+)"', h)
    k0 = next((i for i, l in enumerate(L) if re.search('(?i)^jump to a position group', l)), 0)
    DIAG["jahnke"] = f"{len(L)} lines, after start: {' / '.join(L[k0:k0+40])[:1500]}"
    p = picks_from(L, idx, r"(?i)^jump to a position group", r"(?i)(exclusive content|want to keep reading)", None,
                   [(r"quarterback", "QB"), (r"running back", "RB"), (r"wide receiver", "WR"), (r"tight end", "TE")])
    return dict(expert="Nathan Jahnke", site="PFF", acc="8", url=url, posted=t.group(1) if t else "", picks=p,
                note="free part only (paywall after the QBs)"), ""

DIAG = {}

def main(repo="."):
    w = int(os.environ.get("DK_WEEK") or week())
    idx = player_index(repo)
    now = dt.datetime.now(dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=-7)))
    stamp = f"{now:%a %b} {now.day} {now.hour % 12 or 12}:{now:%M} {'AM' if now.hour < 12 else 'PM'} PT"
    rows, log, got = [], [], 0
    for fn in (boone, english, jahnke):
        try:
            r, why = fn(w, idx)
        except Exception as e:
            r, why = None, f"fetch failed: {e}"
        if not r or not r["picks"]:
            log.append(f"{fn.__name__}: NOT READ - {why or 'no players found on the page'} {DIAG.get(fn.__name__, '')}"); continue
        got += 1
        log.append(f"{r['expert']} ({r['site']}, accuracy #{r['acc']}): {len(r['picks'])} players, posted {r['posted'] or 'time not shown'} - {r['note']} - {r['url']}")
        for i, ((name, pos, team), sec, bid) in enumerate(r["picks"], 1):
            rows.append("|".join([r["expert"], r["site"], r["acc"], r["posted"], str(i), name, pos, team, sec, bid]))
    print(f"WAIVER EXPERTS week {w} {stamp}: {got} of 3 read"); print("\n".join(log))
    if not got:
        print("no source read - old file left in place"); sys.exit(1)
    od = f"{repo}/yahoo_drop/morning"; os.makedirs(od, exist_ok=True)
    head = f"# Waiver experts, week {w}. Read live {stamp} (GitHub read). expert|site|acc_rank|posted|order|player|pos|team|section|bid\n" + \
           "".join(f"# {l}\n" for l in log)
    open(f"{od}/waiver_experts.txt", "w").write(head + "\n".join(rows) + "\n")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
