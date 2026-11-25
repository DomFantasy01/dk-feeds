"""NEWS SWEEP helpers (Nov 16 2026, Dom: "make sure we get any of the news they put out that's of value ... all the players
out there available to us and anything that can help us or hurt us that my opponents are using ... future games and playoff
games"; "we don't lose anything that we've flagged"; trades, players off IR, new signings, players with no numbers yet).

Four full reads a day (4 AM, 10 AM, 2 PM, 7 PM PT) by a scheduled Claude run in Dom's Chrome: RotoBaller (free account),
FTN articles (Ratcliffe's site, paid), ESPN fantasy articles (Clay's site, free), Dr. Roto (free articles), FantasyPros (paid),
FantasyLabs (Koerner's site, paid), Yahoo Plus, RotoWire / Rotoworld free articles, team beat writers. Every source is a
FLAGGER: a name it raises goes on the league's talk list (a "sweep" card - NEWS tag - in that league's alerts on the Live page) and stays
there until Dom deletes or separates it. Ratcliffe still decides; nothing here is a move.

  python3 news_sweep.py owners REPO_OR_RAW_BASE names.json out.json
      who owns each name in DK1-DK4: yours / this week's opponent / an upcoming opponent (week) / rival team N /
      on waivers until <date> / not on a roster (free agent - confirm on Yahoo live). names.json = ["Name", ...]
  python3 news_sweep.py merge alerts.json alert_marks.json flags.json out.json [sources.json]
      folds the run's flags into the Live alerts document. flags.json = [{lg: "DK I".."DK IV", who, color: red|gold|grey,
      title, tie, fix, own, receipts: [..], src, feed}]. Same player + league + still open -> the card updates (first_seen
      kept, receipts merged). A card Dom deleted or separated comes back only when the headline is new.
alerts.py carries "sweep" cards forward untouched, so the Dispatch's own rebuilds never resolve them."""
import sys, json, re, datetime as dt, urllib.request, os

LG = [("DK I", "dk1", "269381", 2), ("DK II", "dk2", "1519795", 7), ("DK III", "dk3", "1507991", 2), ("DK IV", "dk4", "864215", 6)]
NOW = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower()))
def slug(*p): return re.sub(r"[^a-z0-9]+", "-", "-".join(str(x) for x in p).lower()).strip("-")[:90]

def rd(base, rel):
    if base.startswith("http"):
        return urllib.request.urlopen(f"{base.rstrip('/')}/{rel}?t={int(dt.datetime.now().timestamp())}", timeout=30).read().decode()
    return open(os.path.join(base, rel)).read()

def owners(base, names_f, out_f):
    names = json.load(open(names_f))
    st = json.loads(rd(base, "dispatch_out/live_state_latest.json")); W = int(st.get("week") or 0)
    sch = json.loads(rd(base, "yahoo_drop/sim/league_schedule.json"))["schedule"]
    out, read_at = {}, {}
    for lab, short, lid, me in LG:
        ros, wav = {}, {}
        txt = rd(base, f"yahoo_drop/scout/{short}_rosters_live.txt")
        m_ = re.search(r"read ([^.:]*?\d{1,2}:\d\d [AP]M PT)", txt.splitlines()[0] if txt else ""); read_at[lab] = m_.group(1) if m_ else "unknown"
        for ln in txt.splitlines():
            if ln.startswith("#") or "|" not in ln: continue
            t, slot, nm, tm, pos, stt = (ln.split("|") + [""] * 6)[:6]
            ros[nk(nm)] = (int(t), slot, tm, pos, stt)
        for ln in rd(base, f"yahoo_drop/scout/{short}_waivers.txt").splitlines():
            if ln.startswith("#"): continue
            for e in ln.split("|"):
                if "/" in e: n, c = e.rsplit("/", 1); wav[nk(n)] = c
        opp = {}   # team id -> weeks Dom plays them from this week through 14
        for wk in range(W, 15):
            for pr in (sch.get(lid, {}).get(str(wk)) or "").split():
                a, b = map(int, pr.split("-"))
                if me in (a, b): opp.setdefault(b if a == me else a, []).append(wk)
        for n in names:
            k = nk(n); r = ros.get(k)
            if r:
                t, slot, tm, pos, stt = r
                if t == me: s = f"yours ({'bench' if slot in ('BN', 'IR') else 'starting ' + slot}{', ' + stt if stt else ''})"
                elif t in opp:
                    wks = opp[t]; s = (f"this week's opponent's (team {t}, {slot})" if wks[0] == W else f"team {t}'s ({slot}) - you play them Week {wks[0]}") + \
                        (f"; also Week {', '.join(map(str, wks[1:]))}" if len(wks) > 1 else "")
                else: s = f"rival team {t}'s ({slot})"
            elif k in wav: s = f"on waivers until {wav[k]}"
            else: s = "not on a roster in the last Yahoo read - free agent or on waivers (the waiver file is partial): check Yahoo live"
            out.setdefault(n, {})[lab] = s
    json.dump({"week": W, "read": read_at, "owners": out}, open(out_f, "w"), indent=1)
    print("OWNERS", len(names), "names | week", W, "|", "; ".join(f"{k} rosters read {v}" for k, v in read_at.items()))

RANK = {"red": 0, "gold": 1, "grey": 2}
def merge(al_f, mk_f, fl_f, out_f, src_f=None):
    A = json.load(open(al_f)); A = A.get("data", A)
    try: MK = json.load(open(mk_f)); MK = MK.get("data", MK)
    except Exception: MK = {}
    flags = json.load(open(fl_f))
    items = A.get("items", [])
    by = {x["id"]: x for x in items}
    new = upd = back = skip = 0
    for f in flags:
        lg = f["lg"]; who = f["who"]; base = "sweep-" + slug(lg, who)
        vers = sorted([x for x in items if x["id"] == base or x["id"].startswith(base + "-v")], key=lambda x: x["first_seen"])
        cur = vers[-1] if vers else None
        gone = cur and (MK.get(cur["id"], {}).get("deleted") or MK.get(cur["id"], {}).get("cleared"))
        if cur and not gone:
            cur["receipts"] = list(dict.fromkeys((f.get("receipts") or []) + (cur.get("receipts") or [])))[:12]
            for k in ("title", "tie", "fix", "own", "src", "feed", "by"):
                if f.get(k): cur[k] = f[k]
            if RANK.get(f.get("color"), 2) < RANK.get(cur.get("color"), 2): cur["color"] = f["color"]
            if not cur.get("active"): cur["first_seen"] = NOW   # Nov 25 (Dom): news on an archived card brings it back as today's news
            cur["updated_at"] = NOW   # the morning reset and the page's soft pulse go by the latest news, not the first
            cur["what"] = cur["title"]; cur["last_seen"] = NOW; cur["built"] = f.get("built") or cur.get("built"); cur["active"] = True
            upd += 1; continue
        if cur and gone and (cur.get("title") or "").strip().lower() == (f.get("title") or "").strip().lower():
            skip += 1; continue      # Dom already dealt with this exact news
        nid = base if not vers else f"{base}-v{len(vers) + 1}"
        x = {"id": nid, "kind": "sweep", "lg": lg, "who": who, "color": f.get("color") if f.get("color") in RANK else "gold",
             "title": f.get("title", ""), "what": f.get("title", ""), "tie": f.get("tie", ""), "fix": f.get("fix") or "Talk it through - Ratcliffe decides; no move made.",
             "own": f.get("own", ""), "by": f.get("by", ""), "receipts": (f.get("receipts") or [])[:12], "src": f.get("src", "News sweep"),
             "feed": f.get("feed", ""), "built": f.get("built", ""), "ba": None, "first_seen": NOW, "last_seen": NOW, "active": True}
        items.append(x); by[nid] = x
        if vers: back += 1
        else: new += 1
    items.sort(key=lambda x: (not x.get("active"), RANK.get(x.get("color"), 3), x.get("lg", ""), x.get("who", "")))
    A["items"] = items; A["news_checked"] = NOW
    # Nov 17 (Dom): every sweep saves its site checklist, so the morning system check can say which sites were really read.
    # sources.json = {"RotoBaller": {"status": "read" | "nothing new" | "not signed in" | "blocked" | "failed", "items": n, "note": ""}, ...}
    if src_f:
        try: A["news_sources"] = json.load(open(src_f))
        except Exception as e: A["news_sources"] = {"checklist": {"status": "failed", "note": f"sources file unreadable: {e}"}}
    else: A.pop("news_sources", None)
    LIMIT = 240000
    sz = lambda d: len(json.dumps({"id": "alerts", "data": d}, separators=(",", ":")).encode())
    while sz(A) > LIMIT:
        old = [i for i, x in enumerate(A["items"]) if not x.get("active")]
        if not old: break
        A["items"].pop(min(old, key=lambda i: A["items"][i].get("resolved_at") or A["items"][i].get("last_seen") or ""))
    json.dump(A, open(out_f, "w"), separators=(",", ":"))
    print(f"NEWS MERGE new {new} | updated {upd} | back after a clear {back} | already dealt with {skip} | open news cards "
          f"{sum(1 for x in items if x.get('kind') == 'sweep' and x.get('active'))} | size {sz(A):,} bytes")

if __name__ == "__main__":
    if sys.argv[1] == "owners": owners(*sys.argv[2:5])
    elif sys.argv[1] == "merge": merge(*sys.argv[2:7])
    else: print(__doc__)
