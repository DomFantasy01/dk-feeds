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
WEEKS_BACK, SIZE = 1, 3
TEAMNAME = {"ARI": "Cardinals", "ATL": "Falcons", "BAL": "Ravens", "BUF": "Bills", "CAR": "Panthers", "CHI": "Bears", "CIN": "Bengals",
    "CLE": "Browns", "DAL": "Cowboys", "DEN": "Broncos", "DET": "Lions", "GB": "Packers", "HOU": "Texans", "IND": "Colts", "JAX": "Jaguars",
    "KC": "Chiefs", "LV": "Raiders", "LAC": "Chargers", "LA": "Rams", "MIA": "Dolphins", "MIN": "Vikings", "NE": "Patriots", "NO": "Saints",
    "NYG": "Giants", "NYJ": "Jets", "PHI": "Eagles", "PIT": "Steelers", "SF": "49ers", "SEA": "Seahawks", "TB": "Buccaneers", "TEN": "Titans", "WAS": "Commanders"}
NAME2TM = {v.lower(): k for k, v in TEAMNAME.items()}
FIX = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX"}

def norm(n):
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
        self.order = order + [s for s in ALL if s not in order]          # ungraded sources last, never in the check
        self.ranked = order
        if save:
            try:
                json.dump({"order": order, "members": order[:SIZE], "graded_weeks": self.grades["weeks"], "players": self.grades["players"], "miss": m, "bias": self.grades.get("bias", {}), "pct": self.grades.get("pct", {}), "notes": self.notes,
                           "basis": self.grades.get("basis", ""),
                           "rule": "all sources ranked by points missed per player, last graded week; the top 3 are the check; each man = average of the 3 most accurate that have a number for him",
                           "built": datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%a %b %-d %Y %-I:%M %p PT")}, open(fp, "w"), indent=1)
            except Exception: pass
        return order[:SIZE]

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
        """(average, {source: value}) over the three most accurate sources that have a number for him."""
        got = {}
        for s in self.order:
            v = self.V[s].get((int(n), key))
            if v: got[s] = v
            if len(got) >= SIZE: break
        return (round(sum(got.values()) / len(got), 2) if got else None), got
    def compare(self, n, ka, kb):
        """(a, b, sources) - both men averaged over the three most accurate sources that have numbers for BOTH."""
        both = [s for s in self.order if self.V[s].get((int(n), ka)) and self.V[s].get((int(n), kb))][:SIZE]
        if not both: return None, None, []
        return round(sum(self.V[s][(int(n), ka)] for s in both) / len(both), 2), round(sum(self.V[s][(int(n), kb)] for s in both) / len(both), 2), both
    def label(self, srcs=None):
        return ("avg of " if len(srcs or self.members) > 1 else "") + " + ".join(NAME[s] for s in (srcs or self.members))
    def summary(self):
        m = self.grades["miss"]
        if self.waiting: self.notes.append("; ".join(f"{NAME[s]} has Week {w} numbers only - waits for Week {self.start}, next source steps in" for s, w in self.waiting.items() if s in self.members))
        return (f"Pickup panel: {', '.join(NAME[s] for s in self.members)} (points missed per player, same {self.grades['players']} players, "
                f"Week {', '.join(map(str, sorted(self.grades['weeks'])))}: " + ", ".join(f"{NAME[s]} {m[s]:.2f}" for s in sorted(m, key=m.get)) + ")") if m else "Pickup panel: default (no grades)"

if __name__ == "__main__":
    import sys
    P = Panel(sys.argv[1]); print(P.summary()); print("weeks ahead from", P.start, "| numbers:", {s: len(v) for s, v in P.V.items()}); [print(" note:", x) for x in P.notes]
