"""THE PICKUP PANEL (Nov 9 2026, Dom: "compare all pickups to top 3 (avg), rather than just Ratcliffe" - and yes to Claude's two changes:
the three are picked on the last few weeks together, not reshuffled on one week's noise; the average decides pickups, alerts still fire
on any ONE source).

WHO IS ON IT: the sources that give a FORWARD number (rest of season / Weeks ahead) - a pickup is a rest-of-season decision:
  Ratcliffe  (FTN rest-of-season points a game, dispatch_out/ftn_scored.csv)
  Clay       (ESPN Week-by-week lines ahead, dispatch_out/clay_scored.csv - average of the weeks he plays)
  Yahoo      (Yahoo's weekly projections ahead, yahoo_drop/scout/yproj_dk<n>.txt - average of the weeks he plays)
  Gotham     (the engine's forward points a game, eng_fwd in <DK_ROOT>/dksys/engine/gotham_<league>.csv, written earlier in the build)
  Koerner, Vegas and RotoBaller post THIS WEEK only, so they stay in the expert check beside every pickup but not in the average.
HOW THE THREE ARE PICKED (Dom, Nov 9 8:07 AM: "list by accuracy, use top 3 available as the check from last week, rather than 3 or 4"):
the four are ranked by points missed per player in the LAST graded week (dispatch_out/scoreboard/graded.csv, every number frozen before
kickoff, each league's scoring), on the SAME players for all four. For each man the number is the average of the three most accurate
sources that HAVE a number for him (top 3 available) - when one of the top three has none, the fourth steps in. One source only = "thin".
Every comparison of two men uses the three most accurate sources that have numbers for BOTH, so nobody wins on a source the other lacks.
dispatch_out/pickup_panel.json keeps the order and the grades.
usage (module): P = Panel(REPO); P.rate(league_n, key, pos) -> (avg, {source: value}); P.compare(n, kA, posA, kB, posB)
usage (CLI):    python3 live_sync/panel.py REPO   -> prints and saves the panel
"""
# Nov 12 2026 6:47 AM (Dom, voice - replaces the Nov 9 top-3 average): NO MORE AVERAGING. Roles, not last week's order:
#   check 1 = Ratcliffe - his number DECIDES (rest of season for pickups/drops; this week for lineups)
#   check 2 = RotoBaller - the main check (this week; he caught the Week 9 Hall/Allen split nobody else did)
#   check 3 = Vegas - the this-week check (betting market workload)
# Everyone else (Koerner, Clay, Yahoo, Gotham) is reference only, listed under the three by accuracy over the last 4 graded weeks
# (not one week - Week 9 had all six within half a point). Nobody is ever excluded because one source dislikes him; a check that
# disagrees with Ratcliffe by 2+ points is a stop-and-talk flag, never a filter. If Ratcliffe has no number for a man, the most
# accurate forward source that does stands in, and the row says so.
import os, re, csv, json, glob, datetime
from zoneinfo import ZoneInfo

FORWARD = ("ratcliffe", "clay", "yahoo", "gotham")
NAME = {"ratcliffe": "Ratcliffe", "clay": "Clay", "yahoo": "Yahoo", "gotham": "Gotham", "koerner": "Koerner", "vegas": "Vegas", "rotoballer": "RotoBaller"}
# Nov 9 8:55 AM (Dom): "the top three that we have listed are the ones that we want to use this week in pickups" - all seven
# sources are ranked together (same players, last graded week); the top three are the check, whoever they are. Koerner, Vegas and
# RotoBaller post one week at a time: they count only once their numbers are for the week ahead (Dom: "every week it's going to change").
ALL = ("ratcliffe", "koerner", "clay", "vegas", "rotoballer", "yahoo", "gotham")
WEEKLY = {"koerner": ("koerner_scored.csv", "read_week", "read_pt"), "vegas": ("vegas_scored.csv", None, "read"), "rotoballer": ("rotoballer_scored.csv", None, "read")}
LAB = {1: "DKI", 2: "DKII", 3: "DKIII", 4: "DKIV"}
WEEKS_BACK, SIZE = 4, 3
ROLES = ("ratcliffe", "rotoballer", "vegas")      # Nov 12 (Dom): check 1, 2, 3 - fixed roles
FWD_FALLBACK = ("ratcliffe", "yahoo", "clay", "gotham")   # who stands in for a rest-of-season number when Ratcliffe has none
TEAMNAME = {"ARI": "Cardinals", "ATL": "Falcons", "BAL": "Ravens", "BUF": "Bills", "CAR": "Panthers", "CHI": "Bears", "CIN": "Bengals",
    "CLE": "Browns", "DAL": "Cowboys", "DEN": "Broncos", "DET": "Lions", "GB": "Packers", "HOU": "Texans", "IND": "Colts", "JAX": "Jaguars",
    "KC": "Chiefs", "LV": "Raiders", "LAC": "Chargers", "LA": "Rams", "MIA": "Dolphins", "MIN": "Vikings", "NE": "Patriots", "NO": "Saints",
    "NYG": "Giants", "NYJ": "Jets", "PHI": "Eagles", "PIT": "Steelers", "SF": "49ers", "SEA": "Seahawks", "TB": "Buccaneers", "TEN": "Titans", "WAS": "Commanders"}
NAME2TM = {v.lower(): k for k, v in TEAMNAME.items()}
FIX = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX"}

import unicodedata as _ud   # Nov 12: accents stripped - "Audric Estimé" showed as a free agent while rostered as "Audric Estime"
def norm(n):
    n = "".join(c for c in _ud.normalize("NFKD", str(n)) if not _ud.combining(c))
    n = str(n).replace("-", " ").lower().replace(".", "").replace("'", "").replace("’", "")
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return re.sub(r"[^a-z ]", "", re.sub(r"\s+", " ", n)).strip()
def tm_of(team, name=""):
    t = FIX.get(str(team).upper(), str(team).upper())
    if t in TEAMNAME: return t
    for w in norm(name).split():
        if w in NAME2TM: return NAME2TM[w]
    return t
def pkey(name, pos, team):     # the same key pickups.py uses: "jax def" for a defense, the normalized name otherwise
    return (tm_of(team, name) + " def").lower() if pos in ("DST", "DEF", "D/ST") else norm(name)
def fnum(x):
    try: return float(x)
    except Exception: return None

class Panel:
    def __init__(self, repo, root=None, save=True):
        self.R = repo; self.root = root or os.environ.get("DK_ROOT", "/home/claude")
        self.notes = []; self.W = self._week(); self.start = self._start()
        self.grades = self._grade(); self.members = self._pick(save)
        self.V = {s: {} for s in ALL}; self.read = {}; self.meta = {}; self.waiting = {}
        self._ratcliffe(); self._clay(); self._yahoo(); self._gotham(); self._weekly()

    # ---- which week we are in, and the first week still ahead
    def _week(self):
        fs = glob.glob(os.path.join(self.R, "dispatch_out", "meter_wk*.json"))
        return max([int(re.search(r"_wk(\d+)", f).group(1)) for f in fs] or [0])
    def _start(self):
        """Weeks ahead = this week if none of its games has kicked off, otherwise next week."""
        now = datetime.datetime.now(ZoneInfo("America/New_York")); first = None
        for gp in (os.path.join(self.root, "dksys", "gate", "fresh", "games.csv"), os.path.join(self.R, "system", "src", "role_watch", "data", "games.csv")):
            try:
                for g in csv.DictReader(open(gp)):
                    if g.get("season") != "2026" or g.get("game_type") != "REG" or str(g.get("week")) != str(self.W) or not g.get("gametime"): continue
                    t = datetime.datetime.strptime(g["gameday"] + " " + g["gametime"], "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("America/New_York"))
                    first = t if first is None or t < first else first
                if first: break
            except Exception: continue
        return self.W + 1 if (first is None or first <= now) else self.W

    # ---- the accuracy grade, same players for all four sources
    def _grade(self):
        """Every source with 20+ graded players in the last graded week, scored on the players they ALL have - nobody ranks
        higher for grading on easier players. If that shared set is under 20, each is scored on its own players (noted)."""
        try: G = list(csv.DictReader(open(os.path.join(self.R, "dispatch_out", "scoreboard", "graded.csv"))))
        except Exception: G = []
        weeks = sorted({int(r["week"]) for r in G}, reverse=True); out = {"weeks": [], "miss": {}, "players": 0, "basis": ""}
        # Nov 12 (Dom): graded over the last WEEKS_BACK graded weeks, not one. Each week is scored on the players every source that
        # week shares; a source's grade = its miss averaged over the weeks it was graded, weighted by players.
        acc = {}
        for w in weeks:
            R = [r for r in G if int(r["week"]) == w and fnum(r.get("actual")) is not None]
            srcs = [s for s in ALL if sum(fnum(r.get(s)) is not None for r in R) >= 20]
            if not srcs: continue
            com = [r for r in R if all(fnum(r.get(s)) is not None for s in srcs)]
            if len(com) < 20: continue
            tot = sum(fnum(r["actual"]) for r in com)
            for s in srcs:
                a = acc.setdefault(s, {"ab": 0.0, "e": 0.0, "n": 0, "t": 0.0, "w": []})
                a["ab"] += sum(abs(fnum(r[s]) - fnum(r["actual"])) for r in com); a["e"] += sum(fnum(r[s]) - fnum(r["actual"]) for r in com)
                a["n"] += len(com); a["t"] += tot; a["w"].append(w)
            out["weeks"].append(w); out["players"] += len(com)
            if len(out["weeks"]) >= WEEKS_BACK: break
        if acc:
            out["miss"] = {s: round(a["ab"] / a["n"], 2) for s, a in acc.items()}
            out["bias"] = {s: round(a["e"] / a["n"], 2) for s, a in acc.items()}
            out["pct"] = {s: (round(100 * a["e"] / a["t"], 1) if a["t"] > 0 else None) for s, a in acc.items()}
            out["src_weeks"] = {s: sorted(a["w"]) for s, a in acc.items()}
            out["basis"] = "last %d graded weeks, each week on the players every source shared" % len(out["weeks"])
            out["weeks"] = sorted(out["weeks"])
            return out
        for w in weeks:
            R = [r for r in G if int(r["week"]) == w and fnum(r.get("actual")) is not None]
            srcs = [s for s in ALL if sum(fnum(r.get(s)) is not None for r in R) >= 20]
            if len(srcs) < SIZE: continue
            com = [r for r in R if all(fnum(r.get(s)) is not None for s in srcs)]
            if len(com) >= 20:
                out["miss"] = {s: round(sum(abs(fnum(r[s]) - fnum(r["actual"])) for r in com) / len(com), 2) for s in srcs}
                out["bias"] = {s: round(sum(fnum(r[s]) - fnum(r["actual"]) for r in com) / len(com), 2) for s in srcs}   # Nov 9 9:10 AM (Dom): + guessed high, - low
                # Nov 10 (Dom): the same miss as a percent with its direction - +8 = projected players 8% too high, -5 = 5% too low (fair across the four scorings)
                tot = sum(fnum(r["actual"]) for r in com)
                out["pct"] = {s: (round(100 * sum(fnum(r[s]) - fnum(r["actual"]) for r in com) / tot, 1) if tot > 0 else None) for s in srcs}
                out["players"] = len(com); out["basis"] = "same players for every source"
            else:
                for s in srcs:
                    d = [abs(fnum(r[s]) - fnum(r["actual"])) for r in R if fnum(r.get(s)) is not None]; out["miss"][s] = round(sum(d) / len(d), 2)
                    e = [fnum(r[s]) - fnum(r["actual"]) for r in R if fnum(r.get(s)) is not None]; out.setdefault("bias", {})[s] = round(sum(e) / len(e), 2)
                    t = sum(fnum(r["actual"]) for r in R if fnum(r.get(s)) is not None); out.setdefault("pct", {})[s] = round(100 * sum(e) / t, 1) if t > 0 else None
                out["players"] = len(R); out["basis"] = "each source on its own players (too few shared)"
            out["weeks"] = [w]; break
        return out

    def _pick(self, save):
        fp = os.path.join(self.R, "dispatch_out", "pickup_panel.json"); m = self.grades["miss"]
        if not m: self.notes.append("no graded week yet - order Ratcliffe, Yahoo, Gotham, Clay"); order = ["ratcliffe", "yahoo", "gotham", "clay"]
        else: order = sorted(m, key=lambda s: m[s])
        self.ranked = order                                               # accuracy order (last 4 graded weeks) - for the "#rank" labels
        rest = [x for x in order if x not in ROLES] + [x for x in ALL if x not in order and x not in ROLES]
        self.order = list(ROLES) + rest                                   # Nov 12 (Dom): the three checks by role on top, the rest by accuracy
        if save:
            try:
                json.dump({"order": self.order, "accuracy_order": order, "members": list(ROLES), "graded_weeks": self.grades["weeks"], "players": self.grades["players"], "miss": m, "bias": self.grades.get("bias", {}), "pct": self.grades.get("pct", {}), "notes": self.notes,
                           "basis": self.grades.get("basis", ""),
                           "rule": "Nov 12 (Dom): no averaging - check 1 Ratcliffe decides, check 2 RotoBaller and check 3 Vegas are the checks (2+ points off Ratcliffe = stop and talk); the rest are reference, ordered by accuracy over the last 4 graded weeks",
                           "built": datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%a %b %-d %Y %-I:%M %p PT")}, open(fp, "w"), indent=1)
            except Exception: pass
        return list(ROLES)

    # ---- each source's number a game for the weeks ahead, in each league's own scoring
    def _put(self, s, n, key, v, meta=None):
        if v is not None and v > 0:
            self.V[s][(int(n), key)] = round(v, 2)
            if meta: self.meta.setdefault((int(n), key), meta)       # (name, team, pos) - lets a man only Yahoo or Gotham sees reach the list
    def _csv(self, fn):
        try: return list(csv.DictReader(open(os.path.join(self.R, "dispatch_out", fn))))
        except Exception: return []
    def _ratcliffe(self):
        for r in self._csv("ftn_scored.csv"):
            self._put("ratcliffe", r["lg"], pkey(r["name"], r["pos"], r["team"]), fnum(r.get("ros_pg"))); self.read["ratcliffe"] = r.get("read_pt", "")
    def _clay(self):
        for r in self._csv("clay_scored.csv"):
            v = [fnum(r.get(f"w{w}")) for w in range(self.start, 18)]; v = [x for x in v if x]
            self._put("clay", r["lg"], pkey(r["name"], r["pos"], r["team"]), sum(v) / len(v) if v else None); self.read["clay"] = r.get("read", "")
    def _yahoo(self):
        for n in LAB:
            fp = os.path.join(self.R, "yahoo_drop", "scout", f"yproj_dk{n}.txt"); acc = {}; ym = {}
            try: L = open(fp).read().splitlines()
            except Exception: continue
            m = re.search(r"read (?:live )?(.+?PT)", L[0] if L else ""); self.read["yahoo"] = m.group(1) if m else ""
            for ln in L[1:]:
                p = ln.split("|")
                if len(p) < 5 or not p[0].isdigit() or int(p[0]) < self.start: continue
                v = fnum(p[4])
                if v: k = pkey(p[1], p[3], p[2]); acc.setdefault(k, []).append(v); ym[k] = (p[1], tm_of(p[2], p[1]), "DST" if p[3] in ("DEF", "DST") else p[3])
            for k, v in acc.items(): self._put("yahoo", n, k, sum(v) / len(v), ym.get(k))
    def _gotham(self):
        for n, lab in LAB.items():
            fp = os.path.join(self.root, "dksys", "engine", f"gotham_{lab}.csv")
            try: rows = list(csv.DictReader(open(fp)))
            except Exception: self.notes.append(f"Gotham {lab} file not found - Gotham left out of the average there"); continue
            wk = max([int(fnum(r.get("week")) or 0) for r in rows] or [0])
            if wk < self.W:          # never average in a stale engine run (the repo's starting copy is Week 5)
                self.notes.append(f"Gotham {lab} is Week {wk} - stale, left out"); continue
            for r in rows: self._put("gotham", n, pkey(r["player"], r["pos"], r["team"]), fnum(r.get("eng_fwd")), (r["player"], tm_of(r["team"], r["player"]), r["pos"]))
            self.read["gotham"] = (rows[0].get("gotham_run") if rows else "") or ""

    def _weekly(self):
        """Koerner / Vegas / RotoBaller: one week's number. It counts only when that week is the week ahead (self.start);
        a number for a week already played sits out and the next most accurate source steps in."""
        for s, (fn, wkcol, rdcol) in WEEKLY.items():
            rows = self._csv(fn)
            if not rows: continue
            if wkcol: wk = int(fnum(rows[0].get(wkcol)) or 0)
            else:
                try: wk = int(json.load(open(os.path.join(self.R, "yahoo_drop", s, f"{s}_weekly.json"))).get("week") or 0)
                except Exception: wk = 0
            self.read[s] = rows[0].get(rdcol, "")
            if wk < self.start: self.waiting[s] = wk; continue
            for r in rows: self._put(s, r["lg"], pkey(r["name"], r["pos"], r["team"]), fnum(r.get("wk")))

    # ---- the panel's number
    def rate(self, n, key, pos=None):
        """(number, {source: value}) - Nov 12 (Dom): Ratcliffe's rest-of-season number decides; no average. When he has none,
        the most accurate forward source that does stands in (named, never hidden)."""
        for s in sorted(FWD_FALLBACK, key=lambda x: (x != "ratcliffe", self.ranked.index(x) if x in self.ranked else 99)):
            v = self.V[s].get((int(n), key))
            if v: return round(v, 2), {s: v}
        return None, {}
    def compare(self, n, ka, kb):
        """(a, b, sources) - both men on the SAME source: Ratcliffe when he has both, else the most accurate forward source that does."""
        for s in sorted(FWD_FALLBACK, key=lambda x: (x != "ratcliffe", self.ranked.index(x) if x in self.ranked else 99)):
            a, b = self.V[s].get((int(n), ka)), self.V[s].get((int(n), kb))
            if a and b: return round(a, 2), round(b, 2), [s]
        return None, None, []
    def checks(self, n, key):
        """{source: this-week value} for the two checks (RotoBaller, Vegas) - shown beside Ratcliffe, never deciding."""
        return {s: self.V[s][(int(n), key)] for s in ROLES[1:] if self.V[s].get((int(n), key))}
    def label(self, srcs=None):
        srcs = srcs or ["ratcliffe"]
        return " + ".join(NAME[s] for s in srcs) + ("" if srcs == ["ratcliffe"] else " (Ratcliffe has no number - stand-in)")
    def summary(self):
        m = self.grades["miss"]
        if self.waiting: self.notes.append("; ".join(f"{NAME[s]} has Week {w} numbers only - waits for Week {self.start}, next source steps in" for s, w in self.waiting.items() if s in self.members))
        return (f"Pickup panel: 1 {NAME[ROLES[0]]} decides, checks 2 {NAME[ROLES[1]]} and 3 {NAME[ROLES[2]]} (accuracy, points missed per player, {self.grades['players']} player-games, "
                f"Week {', '.join(map(str, sorted(self.grades['weeks'])))}: " + ", ".join(f"{NAME[s]} {m[s]:.2f}" for s in sorted(m, key=m.get)) + ")") if m else "Pickup panel: default (no grades)"

if __name__ == "__main__":
    import sys
    P = Panel(sys.argv[1]); print(P.summary()); print("weeks ahead from", P.start, "| numbers:", {s: len(v) for s, v in P.V.items()}); [print(" note:", x) for x in P.notes]
