"""VEGAS - THE MONEY'S NUMBER (Nov 7 2026, Dom: "I want this to be a needle, and I want it to say Vegas"; "give it some weight ...
it's gonna let us know if there's a disagreement, and then that way we can look at it and compare it and talk about it").

Source: First Down Studio (firstdown.studio/rankings), free, "powered by Vegas player props". Every player with a posted prop gets a
stat line built from the sportsbook lines: QB pass yds / pass TD / INT / rush yds / rush TD; RB rush yds / rush att / rec / rec yds /
TD; WR and TE rec / rec yds / TD; K points only. Plus a rank and its gap to the experts' consensus (ECR), e.g. Singletary 19 (+14).

Two jobs, one file (same shape as clay_points.py):
  read   - pulls the QB, RB, WR, TE and K pages (server-rendered HTML tables), saves yahoo_drop/vegas/vegas_weekly.json with the
           site's "Updated" stamp and our read time. If the site can't be reached, the last saved file is used only if it is for the
           current week; otherwise Vegas is simply missing this build (said so) - never a stale number passed as fresh.
  score  - every stat line scored in each league's OWN rules (same formulas as Ratcliffe, Koerner and Clay: 0.25 per carry in
           DK1-3, INT -2 / -1 in DK4, full PPR), never the site's own half-PPR points. K uses the site's points (no FG-distance
           split is published). DEF: no props exist for defenses - Ratcliffe's number stands in, flagged.
           Writes dispatch_out/vegas_scored.csv (lg, key, name, team, pos, wk, rank, ecr_gap, read, site_updated) and a weekly copy
           in dispatch_out/vegas_history/ for the accuracy grade; puts "vegas" on every starter and bench man in the meter, plus
           totals["vegas"], needles["vegas"] (chance to win this week on Vegas's numbers, best lineup both sides via Ratcliffe's
           set + the per-man difference, same spread as the other needles) and needles_set["vegas"].
Vegas is a CHECK beside the named experts: Ratcliffe still leads every number that drives a decision. Its job is the disagreement.
Props run conservative on touchdowns, so its points run low across the board - the ORDER and the gap matter more than the raw total.
Players with no prop (deep backups, injured men whose props are pulled) have no Vegas number; Ratcliffe's stands in, flagged.
usage: python3 vegas_points.py REPO WEEK [METER.json]            (reads the site, scores, writes)
       python3 vegas_points.py REPO WEEK METER.json --no-read     (scores the saved file into another meter copy)
       python3 vegas_points.py REPO WEEK --read-only [--keep-raw] (read + save only; --keep-raw also saves the raw pages)"""
import sys, os, re, csv, json, html, time, urllib.request
from statistics import NormalDist, median

R = sys.argv[1]; NOW = int(sys.argv[2]); O = os.path.join
MF = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else O(R, f"dispatch_out/meter_wk{NOW}.json")
SAVE = O(R, "yahoo_drop/vegas/vegas_weekly.json")
PAGES = {"QB": "https://www.firstdown.studio/rankings", "RB": "https://www.firstdown.studio/rankings/rb",
         "WR": "https://www.firstdown.studio/rankings/wr", "TE": "https://www.firstdown.studio/rankings/te",
         "K": "https://www.firstdown.studio/rankings/k"}
# data cells after rank, player, site points - in page order (verified Nov 7 against the rendered tables)
COLS = {"QB": ["pass_yd", "pass_td", "int", "rush_yd", "rush_td"], "RB": ["rush_yd", "rush_att", "rec", "rec_yd", "td"],
        "WR": ["rec", "rec_yd", "td"], "TE": ["rec", "rec_yd", "td"], "K": ["team_pts"]}
STATUS = {"questionable": "Q", "doubtful": "D", "out": "O", "q": "Q", "d": "D", "o": "O", "ir": "IR", "probable": "P"}
TEAMFIX = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX"}
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower().replace("’", "'")))
def _pdt():
    try:
        from zoneinfo import ZoneInfo; import datetime as dt
        return bool(dt.datetime.now(ZoneInfo("America/Los_Angeles")).dst())
    except Exception: return False
def pt_now(): return time.strftime("%a %b %-d %Y %-I:%M %p PT", time.gmtime(time.time() - (7 if _pdt() else 8) * 3600))
def num(t):
    m = re.search(r"-?\d+(?:\.\d+)?", t or ""); return float(m.group()) if m else None

# ---------------------------------------------------------------- the page parser
def _chunks(cell):
    """text pieces of one <td>, split wherever a tag sits (each name / team / status lives in its own element)."""
    cell = re.sub(r"(?is)<(script|style|svg)[^>]*>.*?</\1>", " ", cell)
    out = [html.unescape(x).strip() for x in re.split(r"<[^>]+>", cell)]
    return [x for x in out if x]

TEAM_RE = re.compile(r"([A-Z]{2,3})\s*(@|vs\.?)\s*([A-Z]{2,3})\s*$")
def _player(chunks, known):
    txt = " ".join(chunks); m = TEAM_RE.search(txt.replace(" ", " "))
    team, opp, home = (TEAMFIX.get(m.group(1), m.group(1)), TEAMFIX.get(m.group(3), m.group(3)), m.group(2).startswith("vs")) if m else ("", "", None)
    status = ""
    for c in chunks:
        if c.lower() in STATUS and c.lower() not in ("q", "d", "o"): status = STATUS[c.lower()]
    names = [c for c in chunks if re.search(r"[a-z]", c) and (" " in c or "-" in c or "'" in c) and not TEAM_RE.search(c)
             and c.lower() not in STATUS and not re.match(r"^(@|vs)\b", c)]
    name = max(names, key=len) if names else ""
    if not name or " " not in name.strip(". "):
        # everything arrived in one text run: strip team/status, then find the longest known player key that ends the run
        rest = nk(TEAM_RE.sub("", txt)); rest = re.sub(r"(questionable|doubtful|out)[qdo]?$", "", rest)
        hit = max((k for k in known if rest.endswith(k)), key=len, default="")
        name = known.get(hit, "") if hit else ""
    return name.strip(), team, opp, home, status

def parse(pos, page, known):
    rows = []
    for tr in re.findall(r"(?is)<tr\b[^>]*>(.*?)</tr>", page):
        cells = re.findall(r"(?is)<td\b[^>]*>(.*?)</td>", tr)
        if len(cells) < 3: continue
        ch = [_chunks(c) for c in cells]
        pts = num(" ".join(ch[2]))
        if pts is None: continue
        rk = re.search(r"(\d+)\s*(?:\(\s*([+-]\s*\d+)\s*\))?\s*$", " ".join(ch[0]))
        if not rk: continue
        name, team, opp, home, status = _player(ch[1], known)
        if not name: continue
        vals = [num(" ".join(c)) for c in ch[3:3 + len(COLS[pos])]]
        st = {k: (v or 0.0) for k, v in zip(COLS[pos], vals)}
        rows.append(dict(name=name, pos=pos, team=team, opp=opp, home=home, status=status, rank=int(rk.group(1)),
                         ecr_gap=int(rk.group(2).replace(" ", "")) if rk.group(2) else 0, site_pts=pts, st=st))
    return rows

def known_names():
    k = {}
    for f in ("dispatch_out/clay_scored.csv", "dispatch_out/ftn_scored.csv"):
        try:
            for r in csv.DictReader(open(O(R, f))): k.setdefault(nk(r["name"]), r["name"])
        except Exception: pass
    return k

# Nov 7 11:30 AM: every page also carries the site's own data rows (all 190 players, every position) as JSON inside the page:
# full-precision stat lines, which stats came from a Vegas prop vs the site's own model fill-in ("projection"), the injury tag,
# kickoff time, the experts' consensus rank (ppr_erc) and the time the site last updated. Those rows are read first; the
# rendered table is the fallback if they ever disappear.
JMAP = {"passing_yards": "pass_yd", "passing_touchdowns": "pass_td", "interceptions": "int", "rushing_yards": "rush_yd",
        "rushing_attempts": "rush_att", "receptions": "rec", "receiving_yards": "rec_yd"}
def json_rows(page):
    t = page.replace('\\"', '"'); out = {}; i = 0
    while True:
        i = t.find('"rows":[', i)
        if i < 0: break
        j = i + 7; d = 0; k = j
        for k in range(j, len(t)):
            c = t[k]
            if c == "[": d += 1
            elif c == "]":
                d -= 1
                if d == 0: break
        try:
            for r in json.loads(t[j:k + 1]):
                if isinstance(r, dict) and r.get("position") and r.get("name"): out[r.get("player_id") or r["name"]] = r
        except Exception: pass
        i = k
    return out
def from_json(rows):
    by = {}
    for r in rows.values(): by.setdefault(r["position"], []).append(r)
    out = []
    for pos, lst in by.items():
        if pos not in COLS: continue
        lst.sort(key=lambda r: -(r.get("ppr") or 0))
        for n, r in enumerate(lst, 1):
            st = {v: float(r.get(k) or 0) for k, v in JMAP.items()}
            st["rush_td" if pos == "QB" else "td"] = float(r.get("expected_touchdowns") or 0)
            src = r.get("stat_sources") or {}; vs = sum(1 for v in src.values() if v == "vegas")
            erc = r.get("ppr_erc")
            out.append(dict(name=r["name"], pos=pos, team=TEAMFIX.get(r.get("team") or "", r.get("team") or ""), opp=r.get("opponent") or "",
                            home=" vs " in (r.get("game_details") or ""), status=STATUS.get(str(r.get("injury_status") or "").lower(), str(r.get("injury_status") or "")),
                            rank=n, ecr_gap=(int(erc) - n) if isinstance(erc, (int, float)) else 0, ecr=erc,
                            site_pts=round(float(r.get("ppr") or 0), 2), st=st, kickoff=r.get("kickoff_at"),
                            vegas_share=round(vs / len(src), 2) if src else None,
                            model_fill=[JMAP.get(k, k) for k, v in src.items() if v != "vegas"], updated_at=r.get("updated_at")))
    return out
def _pt(iso):
    try:
        import datetime as dt; from zoneinfo import ZoneInfo
        return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(ZoneInfo("America/Los_Angeles")).strftime("%a %b %-d %-I:%M %p PT")
    except Exception: return iso or ""

class NotPosted(RuntimeError): pass   # Nov 10: site is on the new week but its rankings aren't up yet ("Want to know first when Week N rankings drop?")
def not_posted_ok():
    # waiting is normal Tue, Wed and Thu morning PT; still waiting after Thu noon (Thursday-night kickoff) = a real problem, fail loudly
    import datetime as dt; from zoneinfo import ZoneInfo
    n = dt.datetime.now(ZoneInfo("America/Los_Angeles")); return n.weekday() in (1, 2) or (n.weekday() == 3 and n.hour < 12)

def read_site(keep_raw=False):
    known = known_names(); out, meta, allj = [], {}, {}
    for pos, url in PAGES.items():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
                                                   "Accept": "text/html"})
        page = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")
        jr = json_rows(page); allj.update(jr)
        rows = parse(pos, page, known)
        up = re.search(r"Updated:?\s*(?:<[^>]+>\s*)*([0-9]{1,2}/[0-9]{1,2}[^<]{0,14})", page)
        wk = re.search(r"Week\s*(?:<[^>]+>\s*)*(\d{1,2})\b", page)
        meta[pos] = dict(n=len(rows), json=len(jr), updated=(up.group(1).strip() if up else ""), week=int(wk.group(1)) if wk else None,
                         waiting=bool(re.search(r"rankings\s+drop\?", page)))
        if keep_raw or (len(rows) < 15 and len(jr) < 100):
            os.makedirs(O(R, "yahoo_drop/vegas/raw"), exist_ok=True); open(O(R, f"yahoo_drop/vegas/raw/{pos.lower()}.html"), "w").write(page)
        print(f"   VEGAS {pos}: {len(rows)} table rows, {len(jr)} data rows, site updated '{meta[pos]['updated']}', page week {meta[pos]['week']}")
        out += rows
    if len(allj) >= 100:
        js = from_json(allj); ups = sorted(r["updated_at"] for r in js if r.get("updated_at"))
        meta["data_rows"] = len(js); meta["updated_at"] = _pt(ups[-1]) if ups else ""
        wks = [r.get("week") for r in allj.values() if r.get("week")]
        if wks and max(set(wks), key=wks.count) != NOW: raise RuntimeError(f"site data is Week {max(set(wks), key=wks.count)}, this is Week {NOW}")
        print(f"   VEGAS: using the page data rows ({len(js)} players, site data updated {meta['updated_at']})")
        return js, meta
    if all(meta[p]["n"] < 15 for p in ("QB", "RB", "WR", "TE")) and all(meta[p].get("waiting") for p in ("QB", "RB", "WR", "TE")):
        raise NotPosted(f"site is on Week {meta['RB'].get('week')} but its rankings are not posted yet")
    short = [p for p in ("QB", "RB", "WR", "TE") if meta[p]["n"] < 15]
    if short: raise RuntimeError(f"page(s) {short} came back with too few rows - layout may have changed (raw pages saved in yahoo_drop/vegas/raw/)")
    pw = [m["week"] for m in meta.values() if isinstance(m, dict) and m.get("week")]
    if pw and max(set(pw), key=pw.count) != NOW: raise RuntimeError(f"site shows Week {max(set(pw), key=pw.count)}, this is Week {NOW}")
    return out, meta

# ---------------------------------------------------------------- scoring, each league's own rules
def score(p, lg, cfg):
    st, pos = p["st"], p["pos"]; g = lambda k: float(st.get(k) or 0)
    it = float(cfg.get("int", -2)); ra = float(cfg.get("rush_att", 0.25))
    run = g("rush_yd") / 10 + ra * g("rush_att")   # carries count for every position (same as Ratcliffe/Clay scoring)
    if pos == "QB": return g("pass_yd") / 25 + 6 * g("pass_td") + it * g("int") + run + 6 * g("rush_td")
    if pos in ("RB", "WR", "TE"): return run + g("rec") + g("rec_yd") / 10 + 6 * g("td")
    if pos == "K": return None if cfg.get("no_kicker") else p["site_pts"]
    return None

if __name__ == "__main__":
    data = None
    if "--no-read" not in sys.argv:
        try:
            pl, meta = read_site("--keep-raw" in sys.argv)
            data = dict(read=pt_now(), week=NOW, source="First Down Studio Vegas prop rankings (firstdown.studio)", pages=meta,
                        site_updated=meta.get("updated_at") or meta.get("RB", {}).get("updated", ""), players=pl)
            os.makedirs(os.path.dirname(SAVE), exist_ok=True); json.dump(data, open(SAVE, "w"), indent=0)
            print(f"VEGAS: read {len(pl)} players, {data['read']} (site updated {data['site_updated']})")
        except NotPosted as e:
            ok = not_posted_ok()
            print(f"{'VEGAS' if ok else '!! VEGAS'}: {e} - Week {NOW} Vegas waits ({'normal before Thursday noon PT' if ok else 'past Thursday noon PT - FAILING'})")
            try:
                os.makedirs(os.path.dirname(SAVE), exist_ok=True)
                json.dump(dict(checked=pt_now(), week=NOW, state="waiting" if ok else "late", note=str(e)), open(O(R, "yahoo_drop/vegas/status.json"), "w"))
            except Exception: pass
            if "--read-only" in sys.argv: sys.exit(0 if ok else 1)
        except Exception as e:
            print(f"!! VEGAS: site read failed ({e}) - trying the last saved file")
    if "--read-only" in sys.argv: sys.exit(0 if data else 1)
    if data is None:
        try: data = json.load(open(SAVE))
        except Exception: print("VEGAS: no saved file - Vegas is missing this build"); sys.exit(0)
        if int(data.get("week") or 0) != NOW: print(f"VEGAS: saved file is Week {data.get('week')}, this is Week {NOW} - not used"); sys.exit(0)

    SCF = [p for p in (O(R, "system/dksys/data/latest/yahoo/scoring/scoring_audit_oct1.json"), "/home/claude/dksys/data/latest/yahoo/scoring/scoring_audit_oct1.json") if os.path.exists(p)]
    SC = json.load(open(SCF[0])); LGK = {1: "DK I 269381", 2: "DK II 1519795", 3: "DK III 1507991", 4: "DK IV 864215"}
    rows, val, info = [], {}, {}
    for lg, key in LGK.items():
        cfg = SC[key]
        for p in data["players"]:
            v = score(p, lg, cfg)
            if v is None: continue
            k_ = nk(p["name"]); val[(lg, k_)] = round(v, 2); info[k_] = p
            rows.append([lg, k_, p["name"], p["team"], p["pos"], round(v, 2), p["rank"], p["ecr_gap"], p.get("status", ""),
                         p["st"].get("rush_att", ""), p["st"].get("rec", ""), data["read"], data.get("site_updated", ""),
                         "" if p.get("vegas_share") is None else p["vegas_share"], " ".join(p.get("model_fill") or [])])
    os.makedirs(O(R, "dispatch_out/vegas_history"), exist_ok=True)
    with open(O(R, "dispatch_out/vegas_scored.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["lg", "key", "name", "team", "pos", "wk", "rank", "ecr_gap", "status", "rush_att", "rec", "read", "site_updated", "vegas_share", "model_fill"])
        w.writerows(rows)
    try:
        import shutil; shutil.copy(O(R, "dispatch_out/vegas_scored.csv"), O(R, f"dispatch_out/vegas_history/vegas_wk{NOW}.csv"))
    except Exception: pass

    try: M = json.load(open(MF))
    except Exception as e: print("VEGAS: no meter file to fill -", e); sys.exit(0)
    LGN = {"DK I": 1, "DK II": 2, "DK III": 3, "DK IV": 4}; hit = miss = 0
    for lab, L in (M.get("leagues") or {}).items():
        lg = LGN.get(lab)
        for side in ("me", "op"):
            for s in (L.get("starters") or {}).get(side) or []:
                v = val.get((lg, nk(s.get("player"))))
                if v is None: s["vegas"] = s.get("ratcliffe"); s["vegas_src"] = "ratcliffe (no Vegas prop)"; miss += 1
                else:
                    s["vegas"] = v; s["vegas_src"] = "props"; hit += 1
                    i = info.get(nk(s.get("player"))) or {}; s["vegas_rank"] = i.get("rank"); s["vegas_gap"] = i.get("ecr_gap"); s["vegas_share"] = i.get("vegas_share")
        for b in L.get("bench") or []:
            v = val.get((lg, nk(b.get("player")))); b["vegas"] = v if v is not None else b.get("ratcliffe")
            b["vegas_src"] = "props" if v is not None else "ratcliffe (no Vegas prop)"
    ND = NormalDist()
    for lab, L in (M.get("leagues") or {}).items():
        T, Nd = L.get("totals") or {}, L.get("needles") or {}
        sds = []
        for c in ("ratcliffe", "koerner", "gotham", "clay"):
            t = T.get(c); n = Nd.get(c)
            if t and n is not None and 2 <= n <= 98 and abs(t[0] - t[1]) > 1: sds.append((t[0] - t[1]) / ND.inv_cdf(n / 100))
        if not T.get("ratcliffe") or not any(x > 0 for x in sds): continue
        sd = median(x for x in sds if x > 0)
        dl = [sum((s.get("vegas") or 0) - (s.get("ratcliffe") or 0) for s in (L.get("starters") or {}).get(side) or [] if s.get("actual") is None) for side in ("me", "op")]
        a, b = T["ratcliffe"][0] + dl[0], T["ratcliffe"][1] + dl[1]
        T["vegas"] = [round(a, 2), round(b, 2)]; Nd["vegas"] = round(100 * ND.cdf((a - b) / sd))
        # best-lineup version for Live's pregame needle: Ratcliffe's best-lineup chance moved by the same Vegas difference
        rs = (L.get("needles_set") or {}).get("ratcliffe")
        if rs is not None and 1 <= rs <= 99:
            z = ND.inv_cdf(rs / 100) + (dl[0] - dl[1]) / sd
            L.setdefault("needles_set", {})["vegas"] = round(100 * ND.cdf(z))
        print(f"   {lab}: Vegas {a:.1f} vs {b:.1f} -> {Nd['vegas']}% chance to win this week (best lineups {L.get('needles_set', {}).get('vegas')}%)")
    M.setdefault("sources", {})["vegas"] = dict(status="OK", read=data["read"], pulled_pt=data["read"], site_updated=data.get("site_updated", ""),
        note="Vegas player props (First Down Studio), stat lines scored in each league's own rules; a check beside the experts - Ratcliffe leads")
    json.dump(M, open(MF, "w"), ensure_ascii=False)
    print(f"VEGAS: starters with a prop {hit}, without {miss} (Ratcliffe's number used); {len(rows)} player-league rows")
