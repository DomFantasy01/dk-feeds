"""MIKE CLAY (ESPN) - THE NUMBERS CHECK BESIDE RATCLIFFE (Oct 31 2026, Dom: "Mike Clay is very, very good ... get rid of that guy
we're converting on our own"; "Ratcliffe and Koerner give the numbers, Clay is the numbers check, Brenton is the ranking check").

Two jobs, one file:
  read   - pulls Clay's projections from ESPN's public fantasy feed (no login): the full stat line for every player for THIS week
           and EVERY week ahead through Week 17 (the playoff weeks included - no other expert we use publishes those).
           Saved to yahoo_drop/clay/clay_weekly.json. If ESPN can't be reached, the last saved file is used only if it is for
           the current week; otherwise Clay is simply missing this build (said so) - never a stale number passed as fresh.
  score  - every stat line scored in each league's OWN rules (the same formulas as Ratcliffe and Koerner, gather/ftn.py score()),
           never ESPN's own points. Writes dispatch_out/clay_scored.csv (lg, key, name, team, pos, wk = this week, w9..w17 =
           the weeks ahead) and puts "clay" on every starter and bench man in the meter, plus totals["clay"] and needles["clay"]
           (chance to win this week on Clay's numbers, same spread the meter uses for every other source).
Clay is a CHECK: Ratcliffe still leads every number that drives a decision. ESPN is not in FantasyPros' accuracy contest, so
the scoreboard grades Clay ourselves from Week 8 on (frozen pregame like the others).
usage: python3 clay_points.py REPO WEEK [METER.json]       (reads ESPN, scores, writes)
       python3 clay_points.py REPO WEEK METER.json --no-read  (scores the saved file into another meter copy)"""
import sys, os, re, csv, json, math, time, urllib.request
from statistics import NormalDist, median

R = sys.argv[1]; NOW = int(sys.argv[2]); O = os.path.join
MF = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else O(R, f"dispatch_out/meter_wk{NOW}.json")
SAVE = O(R, "yahoo_drop/clay/clay_weekly.json")
LASTWK = 17
TEAM = {1: "ATL", 2: "BUF", 3: "CHI", 4: "CIN", 5: "CLE", 6: "DAL", 7: "DEN", 8: "DET", 9: "GB", 10: "TEN", 11: "IND", 12: "KC", 13: "LV",
        14: "LA", 15: "MIA", 16: "MIN", 17: "NE", 18: "NO", 19: "NYG", 20: "NYJ", 21: "PHI", 22: "ARI", 23: "PIT", 24: "LAC", 25: "SF",
        26: "SEA", 27: "TB", 28: "WAS", 29: "CAR", 30: "JAX", 33: "BAL", 34: "HOU"}
POS = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "DST"}
KEEP = {3, 4, 20, 23, 24, 25, 42, 43, 53, 72, 74, 77, 80, 86, 95, 96, 97, 98, 99, 105, 120}
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower().replace("’", "'")))
def pt_now():
    return time.strftime("%a %b %-d %Y %-I:%M %p PT", time.gmtime(time.time() - 7 * 3600 if _pdt() else time.time() - 8 * 3600))
def _pdt():
    try:
        from zoneinfo import ZoneInfo; import datetime as dt
        return bool(dt.datetime.now(ZoneInfo("America/Los_Angeles")).dst())
    except Exception: return True

def read_espn():
    weeks = list(range(NOW, LASTWK + 1))
    filt = {"players": {"limit": 1500, "sortPercOwned": {"sortPriority": 1, "sortAsc": False},
                        "filterStatsForTopScoringPeriodIds": {"value": len(weeks), "additionalValue": [f"11{2026}{w}" for w in weeks]}}}
    url = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/segments/0/leaguedefaults/3?view=kona_player_info"
    req = urllib.request.Request(url, headers={"X-Fantasy-Filter": json.dumps(filt), "X-Fantasy-Platform": "kona-PROD", "Accept": "application/json",
                                               "User-Agent": "Mozilla/5.0 (dk-feeds build)"})
    j = json.load(urllib.request.urlopen(req, timeout=60))
    out = []
    for x in j.get("players") or []:
        p = x.get("player") or {}; pos = POS.get(p.get("defaultPositionId"))
        if not pos: continue
        wk = {}
        for s in p.get("stats") or []:
            if s.get("statSourceId") == 1 and s.get("statSplitTypeId") == 1 and NOW <= int(s.get("scoringPeriodId") or 0) <= LASTWK:
                wk[str(s["scoringPeriodId"])] = {str(k): round(v, 3) for k, v in (s.get("stats") or {}).items() if int(k) in KEEP and v}
        if wk: out.append(dict(name=p.get("fullName"), pos=pos, team=TEAM.get(p.get("proTeamId"), ""), wk=wk))
    if len(out) < 200: raise RuntimeError(f"only {len(out)} players came back")
    return out

def score(st, pos, lg, cfg):
    g = lambda i: float(st.get(str(i), 0) or 0); it = -1 if lg == 4 else -2; ra = 0 if lg == 4 else .25
    if pos in ("QB", "RB", "WR", "TE"):
        return g(3) / 25 + 6 * g(4) + it * g(20) + g(24) / 10 + 6 * g(25) + ra * g(23) + g(53) + g(42) / 10 + 6 * g(43) - 2 * g(72)
    if pos == "K":
        if cfg.get("no_kicker"): return None
        kc = cfg.get("K", {}); return 3 * g(80) + kc.get("fg40_49", 4) * g(77) + kc.get("fg50", 5) * g(74) + g(86)
    if pos == "DST":
        pa = cfg.get("DEF_pa", [10, 7, 4, 1, 0, -1, -4]); ppg = g(120) or 21.0
        E = [(0, .5), (.5, 6.5), (6.5, 13.5), (13.5, 20.5), (20.5, 27.5), (27.5, 34.5), (34.5, 99)]
        cdf = lambda x: .5 * (1 + math.erf((x - ppg) / (9.0 * math.sqrt(2))))
        tier = sum(v * (cdf(b) - cdf(a if a > 0 else -99)) for v, (a, b) in zip(pa, E))
        return tier + g(99) + 2 * g(95) + 2 * g(96) + 6 * g(105) + 2 * g(98) + 2 * g(97)
    return None

# ---------------------------------------------------------------- read
data = None
if "--no-read" not in sys.argv:
    try:
        pl = read_espn(); data = dict(read=pt_now(), week=NOW, source="ESPN fantasy projections (Mike Clay), public feed", players=pl)
        os.makedirs(os.path.dirname(SAVE), exist_ok=True); json.dump(data, open(SAVE, "w"))
        print(f"CLAY: read {len(pl)} players, Weeks {NOW}-{LASTWK}, {data['read']}")
    except Exception as e:
        print(f"!! CLAY: ESPN read failed ({e}) - trying the last saved file")
if data is None:
    try: data = json.load(open(SAVE))
    except Exception: print("CLAY: no saved file - Clay is missing this build"); sys.exit(0)
    if int(data.get("week") or 0) != NOW: print(f"CLAY: saved file is Week {data.get('week')}, this is Week {NOW} - not used"); sys.exit(0)

# ---------------------------------------------------------------- score, every league
SCF = [p for p in (O(R, "system/dksys/data/latest/yahoo/scoring/scoring_audit_oct1.json"), "/home/claude/dksys/data/latest/yahoo/scoring/scoring_audit_oct1.json") if os.path.exists(p)]
SC = json.load(open(SCF[0])); LGK = {1: "DK I 269381", 2: "DK II 1519795", 3: "DK III 1507991", 4: "DK IV 864215"}
rows, val, valwk = [], {}, {}
for lg, key in LGK.items():
    cfg = SC[key]
    for p in data["players"]:
        ws = {}
        for w, st in p["wk"].items():
            v = score(st, p["pos"], lg, cfg)
            if v is not None: ws[int(w)] = round(v, 2)
        if not ws: continue
        k_ = (p["team"] + "DEF") if p["pos"] == "DST" else nk(p["name"])
        val[(lg, k_)] = ws.get(NOW); valwk[(lg, k_)] = ws
        rows.append([lg, k_, p["name"], p["team"], p["pos"], ws.get(NOW, "")] + [ws.get(w, "") for w in range(NOW + 1, LASTWK + 1)])
os.makedirs(O(R, "dispatch_out"), exist_ok=True)
with open(O(R, "dispatch_out/clay_scored.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["lg", "key", "name", "team", "pos", "wk"] + [f"w{x}" for x in range(NOW + 1, LASTWK + 1)] + ["read"])
    for r in rows: w.writerow(r + [data["read"]])
os.makedirs(O(R, "dispatch_out/clay_history"), exist_ok=True)   # one copy per week, kept for the accuracy check
try:
    import shutil; shutil.copy(O(R, "dispatch_out/clay_scored.csv"), O(R, f"dispatch_out/clay_history/clay_wk{NOW}.csv"))
except Exception: pass

# ---------------------------------------------------------------- into the meter: every man, totals, needle
try: M = json.load(open(MF))
except Exception as e: print("CLAY: no meter file to fill -", e); sys.exit(0)
LGN = {"DK I": 1, "DK II": 2, "DK III": 3, "DK IV": 4}; hit = miss = 0
def kof(s): return (str(s.get("team") or "").upper().replace("WSH", "WAS").replace("LAR", "LA") + "DEF") if s.get("pos") in ("DEF", "DST") else nk(s.get("player"))
for lab, L in (M.get("leagues") or {}).items():
    lg = LGN.get(lab)
    for side in ("me", "op"):
        for s in (L.get("starters") or {}).get(side) or []:
            v = val.get((lg, kof(s)))
            if v is None: s["clay"] = s.get("ratcliffe"); s["clay_src"] = "ratcliffe (Clay has no number for him)"; miss += 1
            else: s["clay"] = v; s["clay_src"] = "espn"; hit += 1
    for b in L.get("bench") or []:
        v = val.get((lg, kof(b))); b["clay"] = v if v is not None else b.get("ratcliffe")
ND = NormalDist()
for lab, L in (M.get("leagues") or {}).items():
    T, Nd = L.get("totals") or {}, L.get("needles") or {}
    sds = []
    for c in ("ratcliffe", "koerner", "gotham", "sleeper", "yahoo_from_spread"):
        t = T.get(c if c != "yahoo_from_spread" else "yahoo"); n = Nd.get(c)
        if t and n is not None and 2 <= n <= 98 and abs(t[0] - t[1]) > 1: sds.append((t[0] - t[1]) / ND.inv_cdf(n / 100))
    if not T.get("ratcliffe") or not any(x > 0 for x in sds): continue
    sd = median(x for x in sds if x > 0)
    dl = [sum((s.get("clay") or 0) - (s.get("ratcliffe") or 0) for s in (L.get("starters") or {}).get(side) or [] if s.get("actual") is None) for side in ("me", "op")]
    a, b = T["ratcliffe"][0] + dl[0], T["ratcliffe"][1] + dl[1]
    T["clay"] = [round(a, 2), round(b, 2)]; Nd["clay"] = round(100 * ND.cdf((a - b) / sd))
    print(f"   {lab}: Clay {a:.1f} vs {b:.1f} -> {Nd['clay']}% chance to win this week")
M.setdefault("sources", {})["clay"] = dict(status="OK", read=data["read"], pulled_pt=data["read"], note="Mike Clay (ESPN) projections, full stat lines scored in each league's own rules; weeks ahead through Week 17")
json.dump(M, open(MF, "w"), ensure_ascii=False)
print(f"CLAY: starters with his number {hit}, without {miss} (Ratcliffe's number used); {len(rows)} player-league rows")
