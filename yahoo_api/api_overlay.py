#!/usr/bin/env python3
# DARK KNIGHT - Yahoo API overlay (Oct 30 2026, Dom: "if the meters aren't right, fix them").
# Problem it fixes: the brief and the meters took Yahoo's win %, team totals and scores from the CHROME read only
# (7:50 AM / 12:50 PM / 4:50 PM), so overnight games (Thursday night) never reached the 5 AM brief, even though the
# Yahoo API read had them every build. Now every build lays the API's newer numbers over the last Chrome read:
#   league_windows_api.txt : every team's Yahoo win % (Yahoo's own number), projected total and record - from the API.
#                            The kickoff-window split for the mountain chart is still the Chrome read's (API has no split).
#   dom_matchups_api.txt   : Dom's four matchups, both sides - lineups, status and points from the API; Yahoo's
#                            per-player projections from the last Chrome read (the API refuses player projections).
# A file is written only when the API read is newer than the Chrome file it overlays; the header says exactly
# which numbers came from where and when. If anything is missing, nothing is written and the Chrome read stands.
#   python3 api_overlay.py <repo> <yahoo_dir> <games.csv>
import sys, os, re, json, glob, datetime as dt

PT = dt.timezone(dt.timedelta(hours=-7))
LG = {"DKI": "269381", "DKII": "1519795", "DKIII": "1507991", "DKIV": "864215"}
FIX = {"WSH": "WAS", "JAC": "JAX", "LAR": "LA"}
RX = re.compile(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (\w{3}) (\d{1,2}),?(?: (\d{4}))? (\d{1,2}):(\d{2}) ([AP]M) PT")

def file_time(path, year):
    m = RX.search(open(path, errors="ignore").read(400))
    if not m: return dt.datetime.fromtimestamp(os.path.getmtime(path), PT)
    t = dt.datetime.strptime(f"{m.group(2)} {m.group(3)} {m.group(4) or year} {m.group(5)}:{m.group(6)} {m.group(7)}", "%b %d %Y %I:%M %p")
    return t.replace(tzinfo=PT)
def newest_chrome(d, pat, year):
    fs = [f for f in glob.glob(os.path.join(d, pat)) if not f.endswith("_api.txt")]
    return max(fs, key=lambda f: file_time(f, year)) if fs else None
def ordinal(n):
    n = int(n); return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
def team(a): a = str(a).upper(); return FIX.get(a, a)

def kickoffs(games_csv, week):
    """team -> kickoff (aware PT datetime) from the nflverse schedule"""
    import pandas as pd
    G = pd.read_csv(games_csv, low_memory=False); G = G[(G.season == 2026) & (G.week == week) & (G.game_type == "REG")]
    K = {}
    for r in G.itertuples():
        et = dt.datetime.strptime(f"{r.gameday} {r.gametime}", "%Y-%m-%d %H:%M")
        # nflverse times are US Eastern; Eastern is UTC-4 until Nov 1, UTC-5 after (Pacific follows the same day)
        off = -4 if et < dt.datetime(2026, 11, 1, 2) else -5
        k = et.replace(tzinfo=dt.timezone(dt.timedelta(hours=off))).astimezone(dt.timezone(dt.timedelta(hours=off - 3)))
        K[team(r.home_team)] = K[team(r.away_team)] = k
    return K
def ko_text(k): return f"{k:%a} {k.hour % 12 or 12}:{k:%M} {'am' if k.hour < 12 else 'pm'}"

def main():
    repo, ydir, games = sys.argv[1:4]
    A = json.load(open(os.path.join(repo, "yahoo_api/latest.json")))
    at = dt.datetime.fromisoformat(A["read_utc"]).astimezone(PT); when = A["read_pt"]
    weeks = {L.get("week") for L in A["leagues"].values()}
    if len(weeks) != 1: print("overlay: leagues disagree on the week", weeks, "- nothing written"); return
    wk = weeks.pop(); wd = os.path.join(ydir, f"wk{wk}")
    if not os.path.isdir(wd): print(f"overlay: no Chrome read for week {wk} yet - nothing written"); return
    now = dt.datetime.now(PT); done = []

    # ---- 1. every team's Yahoo win %, total, record
    WF = newest_chrome(wd, "league_windows_*.txt", at.year)
    if WF and at > file_time(WF, at.year):
        win, rec = {}, {}
        for lab, L in A["leagues"].items():
            lid = LG[lab]
            for m in L.get("scoreboard", []):
                for x in m["teams"]:
                    try: win[(lid, x["name"])] = (round(float(x["win_probability"]) * 100), float(x["proj"]))
                    except (TypeError, ValueError): pass
            for s in L.get("standings", []):
                rec[(lid, s["name"])] = f"{s['w']}-{s['l']}-{s['tie']}/{ordinal(s['rank'])}"
        lines = open(WF).read().splitlines(); out, hit, n = [], 0, 0
        for ln in lines:
            if ln.startswith("#") or not ln.strip(): continue
            f = ln.split("~"); n += 1; k = (f[0], f[1])
            if k in win:
                f[3] = str(win[k][0]); f[-2] = f"{win[k][1]:.2f}"; hit += 1
            if k in rec: f[2] = rec[k]
            out.append("~".join(f))
        if n and hit == n:
            src = file_time(WF, at.year)
            head = (f"# Yahoo Week {wk} win %, projected totals and records from the Yahoo API read {when}; kickoff-window split "
                    f"and starters without a game from the Chrome read of {src:%a %b} {src.day} {src.hour % 12 or 12}:{src:%M} "
                    f"{'AM' if src.hour < 12 else 'PM'} PT. lg~team~record~yahoo win%~windows~counts~total~starters w/o game\n"
                    f"# {hit} of {n} teams from the API. (Yahoo API overlay)\n")
            open(os.path.join(wd, "league_windows_api.txt"), "w").write(head + "\n".join(out) + "\n")
            done.append(f"win % for {hit} of {n} teams")
        else: print(f"overlay: only {hit} of {n} teams matched the API - league windows left on the Chrome read")

    # ---- 2. Dom's four matchups: lineups + points from the API, Yahoo projections from Chrome
    MF = newest_chrome(wd, "dom_matchups_*.txt", at.year)
    if MF and at > file_time(MF, at.year) and all("matchup" in L for L in A["leagues"].values()):
        prev = {}
        for ln in open(MF):
            if ln.startswith("#") or "#" not in ln: continue
            lid, rest = ln.rstrip("\n").split("#", 1)
            for it in rest.replace("##", "|").split("|"):
                f = (it.split("^") + [""] * 7)[:7]; prev[(lid, f[1])] = f
        K = kickoffs(games, wk); rows, nproj, nplayers = [], 0, 0
        for lab, L in A["leagues"].items():
            lid = LG[lab]; sides = []
            for s in ("me", "op"):
                items = []
                for p in L["matchup"][s]["players"]:
                    if p["slot"] in ("BN", "IR", "IR+", ""): continue
                    nplayers += 1; old = prev.get((lid, p["name"]))
                    proj = old[5] if old else ""; nproj += bool(old and old[5])
                    k = K.get(team(p["team"])); ko = ko_text(k) if k else (old[4] if old else "")
                    if k and now >= k and p.get("points", "") != "": pts = p["points"]
                    elif old and old[6] not in ("", "–", "-"): pts = old[6]
                    else: pts = "–"
                    items.append("^".join([p["slot"], p["name"], p["team"], p["status"], ko, proj, pts]))
                sides.append("|".join(items))
            rows.append(f"{lid}#{sides[0]}##{sides[1]}")
        src = file_time(MF, at.year)
        head = (f"# Yahoo Week {wk} matchup pages for Dom's four teams, {when} (Yahoo API: lineups, status, points); Yahoo per-player "
                f"projections from the Chrome read of {src:%a %b} {src.day} {src.hour % 12 or 12}:{src:%M} {'AM' if src.hour < 12 else 'PM'} PT "
                f"({nproj} of {nplayers} starters matched). lg#ME starters ## OPP starters ; slot^player^team^status^kickoff(PT)^yahoo proj^points (Yahoo API overlay)\n")
        open(os.path.join(wd, "dom_matchups_api.txt"), "w").write(head + "\n".join(rows) + "\n")
        done.append(f"Dom's matchups ({nplayers} starters, {nproj} with Chrome projections)")
    print("overlay:", "; ".join(done) if done else "Chrome read is as new as the API - nothing to lay over", "| API read", when)

if __name__ == "__main__":
    try: main()
    except Exception as e: print("!! Yahoo API overlay FAILED - the Chrome read stands:", str(e)[:300])
