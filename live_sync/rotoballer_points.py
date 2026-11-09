"""ROTOBALLER - a free full-stat-line projection source (Nov 8 2026, Dom found it: "Look at rotoballer.com, I found rankings and
projections"). Tried out because it called Week 9's Jets backfield: Hall 12 carries / 3 catches ahead of Allen 10 / 1, Allen about
8.4 points in DK II scoring vs an actual of about 8.4 - while Ratcliffe had Allen 12.8 and Vegas 10.8.

Source: RotoBaller's rankings tool (rotoballer.com/nfl-fantasy-football-rankings-tiered-ppr/265860). The page fills its table from
RotoBaller's own public JSON feed, /wp-json/rb/v1/rankings?league=Overall&perPage=600&spreadsheet=ppr - about 370 players (QB, RB,
WR, TE, K, DST), each with a weekly stat line: carries, rush yds, rush TD, catches, rec yds, rec TD, pass yds, pass TD, INT. The
tab label in /wp-json/rb/v1/rankings-config?name=interface ("PPR (Wk 9)") says which week the list is for. RotoBaller Staff ranks.

Two jobs, same shape as vegas_points.py:
  read   - pulls the feed and the week label, saves yahoo_drop/rotoballer/rotoballer_weekly.json with our read time, the week label,
           the newest per-player update stamp and a fingerprint of the week's opponents. EVERY read also drops a small entry in
           yahoo_drop/rotoballer/reads.jsonl (time, week label, newest stamp, fingerprint, player count) - that log is the proof of
           WHEN each week's numbers first appear (Dom's rule: an expert must post before waivers and keep updating to kickoff).
  score  - every stat line scored in each league's OWN rules (same formula as Vegas, Ratcliffe, Koerner and Clay: 0.25 per carry
           in DK I-III, INT -2 / -1 in DK IV, full PPR). K uses RotoBaller's own points (no FG-distance split published); DEF has no
           stat line - left out. Writes dispatch_out/rotoballer_scored.csv and a weekly copy in dispatch_out/rotoballer_history/
           for the accuracy grade.
If the feed can't be reached, the last saved file is used only if it is for the current week - never a stale number passed as fresh.
Nov 8 10 PM (Dom: "Use it and evaluate later ... post it on DK Live, note testing"): also laid onto the meter like Vegas -
"rotoballer" on every starter and bench man, totals/needles["rotoballer"] and needles_set["rotoballer"] (best lineups both sides,
Ratcliffe's set moved by the per-man difference, same spread as the other needles). Shown on Live as a TESTING source; graded weekly.
usage: python3 rotoballer_points.py REPO WEEK [METER.json]  (read + score + meter)
       python3 rotoballer_points.py REPO WEEK --read-only   (read + log only - used by the every-few-hours watch)
       python3 rotoballer_points.py REPO WEEK --no-read     (score the saved file)"""
import sys, os, re, csv, json, time, hashlib, urllib.request
from statistics import NormalDist, median

R = sys.argv[1]; NOW = int(sys.argv[2]); O = os.path.join
MF = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else O(R, f"dispatch_out/meter_wk{NOW}.json")
SAVE = O(R, "yahoo_drop/rotoballer/rotoballer_weekly.json"); LOG = O(R, "yahoo_drop/rotoballer/reads.jsonl")
FEED = "https://www.rotoballer.com/wp-json/rb/v1/rankings?league=Overall&perPage=600&spreadsheet=ppr"
CONF = "https://www.rotoballer.com/wp-json/rb/v1/rankings-config?name=interface"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36", "Accept": "application/json"}
TEAMFIX = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX"}
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower().replace("’", "'")))
def _pdt():
    try:
        from zoneinfo import ZoneInfo; import datetime as dt
        return bool(dt.datetime.now(ZoneInfo("America/Los_Angeles")).dst())
    except Exception: return False
def pt_now(): return time.strftime("%a %b %-d %Y %-I:%M %p PT", time.gmtime(time.time() - (7 if _pdt() else 8) * 3600))
def f(x):
    try: return float(x)
    except Exception: return 0.0
def get(url): return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read().decode("utf-8", "replace"))

def week_label():
    """the tool's own tab label, e.g. 'PPR (Wk 9)' -> 9 (None if the label can't be found)"""
    try:
        m = re.search(r'"label"\s*:\s*"PPR \(Wk (\d+)\)"', json.dumps(get(CONF)))
        return int(m.group(1)) if m else None
    except Exception: return None

def read_feed():
    d = get(FEED); out = []
    for r in d.get("data") or []:
        p = r.get("player") or {}; pj = p.get("projections") or {}; pos = r.get("position") or ""
        if not p.get("name") or pos not in ("QB", "RB", "WR", "TE", "K"): continue
        st = dict(rush_att=f(pj.get("rus_att")), rush_yd=f(pj.get("rus_yds")), rush_td=f(pj.get("rus_td")), rec=f(pj.get("rec")),
                  rec_yd=f(pj.get("rec_yds")), rec_td=f(pj.get("rec_td")), pass_yd=f(pj.get("pas_yds")), pass_td=f(pj.get("pas_td")),
                  int=f(pj.get("pas_int")))
        out.append(dict(name=p["name"], pos=pos, team=TEAMFIX.get(r.get("team") or "", r.get("team") or ""), opp=r.get("opponent") or "",
                        rank=r.get("rank"), site_pts=f(pj.get("points")), st=st, updated_at=pj.get("updated_at") or r.get("updated_at")))
    if len(out) < 150: raise RuntimeError(f"feed came back with only {len(out)} players - layout may have changed")
    return out

def score(p, cfg):
    st, pos = p["st"], p["pos"]; g = lambda k: float(st.get(k) or 0)
    it = float(cfg.get("int", -2)); ra = float(cfg.get("rush_att", 0.25))
    run = g("rush_yd") / 10 + ra * g("rush_att") + 6 * g("rush_td")
    if pos == "QB": return g("pass_yd") / 25 + 6 * g("pass_td") + it * g("int") + run
    if pos in ("RB", "WR", "TE"): return run + g("rec") + g("rec_yd") / 10 + 6 * g("rec_td")
    if pos == "K": return None if cfg.get("no_kicker") else p["site_pts"]
    return None

if __name__ == "__main__":
    data = None
    if "--no-read" not in sys.argv:
        try:
            pl = read_feed(); wl = week_label()
            fp = hashlib.md5("|".join(sorted(f"{p['team']}{p['opp']}" for p in pl if p["pos"] in ("QB", "RB", "WR", "TE"))).encode()).hexdigest()[:10]
            newest = max((p["updated_at"] or "" for p in pl), default="")
            data = dict(read=pt_now(), read_utc=time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), week=wl, week_label=wl, newest_update_et=newest,
                        opp_fingerprint=fp, source="RotoBaller rankings tool, RotoBaller Staff projections (rotoballer.com)", players=pl)
            os.makedirs(os.path.dirname(SAVE), exist_ok=True); json.dump(data, open(SAVE, "w"), indent=0)
            prev = None
            try: prev = json.loads(open(LOG).read().strip().splitlines()[-1])
            except Exception: pass
            entry = dict(read_utc=data["read_utc"], read_pt=data["read"], week_label=wl, newest_update_et=newest, opp_fingerprint=fp, players=len(pl),
                         changed=(prev is None or prev.get("opp_fingerprint") != fp or prev.get("newest_update_et") != newest))
            open(LOG, "a").write(json.dumps(entry) + "\n")
            print(f"ROTOBALLER: read {len(pl)} players, week label {wl}, newest update {newest} ET, opponents {fp}{' (NEW)' if prev and prev.get('opp_fingerprint') != fp else ''}")
        except Exception as e:
            print(f"!! ROTOBALLER: feed read failed ({e}) - trying the last saved file")
    if "--read-only" in sys.argv: sys.exit(0 if data else 1)
    if data is None:
        try: data = json.load(open(SAVE))
        except Exception: print("ROTOBALLER: no saved file - RotoBaller is missing this build"); sys.exit(0)
    if int(data.get("week") or 0) != NOW: print(f"ROTOBALLER: list is Week {data.get('week')}, this is Week {NOW} - not used yet"); sys.exit(0)

    SCF = [p for p in (O(R, "system/dksys/data/latest/yahoo/scoring/scoring_audit_oct1.json"), "/home/claude/dksys/data/latest/yahoo/scoring/scoring_audit_oct1.json") if os.path.exists(p)]
    SC = json.load(open(SCF[0])); LGK = {1: "DK I 269381", 2: "DK II 1519795", 3: "DK III 1507991", 4: "DK IV 864215"}
    rows, val = [], {}
    for lg, key in LGK.items():
        for p in data["players"]:
            v = score(p, SC[key])
            if v is None: continue
            val[(lg, nk(p["name"]))] = round(v, 2)
            rows.append([lg, nk(p["name"]), p["name"], p["team"], p["pos"], p["opp"], round(v, 2), p["rank"], p["st"]["rush_att"], p["st"]["rec"], data["read"], p.get("updated_at") or ""])
    os.makedirs(O(R, "dispatch_out/rotoballer_history"), exist_ok=True)
    with open(O(R, "dispatch_out/rotoballer_scored.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["lg", "key", "name", "team", "pos", "opp", "wk", "rank", "rush_att", "rec", "read", "site_updated_et"]); w.writerows(rows)
    import shutil; shutil.copy(O(R, "dispatch_out/rotoballer_scored.csv"), O(R, f"dispatch_out/rotoballer_history/rotoballer_wk{NOW}.csv"))
    print(f"ROTOBALLER: {len(rows)} player-league rows scored in each league's own rules (Week {NOW})")

    try: M = json.load(open(MF))
    except Exception as e: print("ROTOBALLER: no meter file to fill -", e); sys.exit(0)
    LGN = {"DK I": 1, "DK II": 2, "DK III": 3, "DK IV": 4}; hit = miss = 0
    for lab, L in (M.get("leagues") or {}).items():
        lg = LGN.get(lab)
        for side in ("me", "op"):
            for s_ in (L.get("starters") or {}).get(side) or []:
                v = val.get((lg, nk(s_.get("player"))))
                if v is None: s_["rotoballer"] = s_.get("ratcliffe"); s_["rotoballer_src"] = "ratcliffe (not on RotoBaller's list)"; miss += 1
                else: s_["rotoballer"] = v; s_["rotoballer_src"] = "rotoballer"; hit += 1
        for b in L.get("bench") or []:
            v = val.get((lg, nk(b.get("player")))); b["rotoballer"] = v if v is not None else b.get("ratcliffe")
            b["rotoballer_src"] = "rotoballer" if v is not None else "ratcliffe (not on RotoBaller's list)"
    ND = NormalDist()
    for lab, L in (M.get("leagues") or {}).items():
        T, Nd = L.get("totals") or {}, L.get("needles") or {}
        sds = []
        for c in ("ratcliffe", "koerner", "gotham", "clay"):
            t = T.get(c); n = Nd.get(c)
            if t and n is not None and 2 <= n <= 98 and abs(t[0] - t[1]) > 1: sds.append((t[0] - t[1]) / ND.inv_cdf(n / 100))
        if not T.get("ratcliffe") or not any(x > 0 for x in sds): continue
        sd = median(x for x in sds if x > 0)
        dl = [sum((s_.get("rotoballer") or 0) - (s_.get("ratcliffe") or 0) for s_ in (L.get("starters") or {}).get(side) or [] if s_.get("actual") is None) for side in ("me", "op")]
        a, b = T["ratcliffe"][0] + dl[0], T["ratcliffe"][1] + dl[1]
        T["rotoballer"] = [round(a, 2), round(b, 2)]; Nd["rotoballer"] = round(100 * ND.cdf((a - b) / sd))
        rs = (L.get("needles_set") or {}).get("ratcliffe")
        if rs is not None and 1 <= rs <= 99:
            L.setdefault("needles_set", {})["rotoballer"] = round(100 * ND.cdf(ND.inv_cdf(rs / 100) + (dl[0] - dl[1]) / sd))
        print(f"   {lab}: RotoBaller {a:.1f} vs {b:.1f} -> {Nd['rotoballer']}% chance to win this week (best lineups {L.get('needles_set', {}).get('rotoballer')}%)")
    M.setdefault("sources", {})["rotoballer"] = dict(status="TESTING", read=data["read"], pulled_pt=data["read"], site_updated=data.get("newest_update_et", ""),
        note="RotoBaller Staff projections (free), stat lines scored in each league's own rules; on trial since Nov 8 - Ratcliffe leads")
    json.dump(M, open(MF, "w"), ensure_ascii=False)
    print(f"ROTOBALLER: starters on RotoBaller's list {hit}, not on it {miss} (Ratcliffe's number used)")
