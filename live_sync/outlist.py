"""WHO IS OUT THIS WEEK (Oct 31 2026, Dom: Henderson was ruled out but Ratcliffe's file still had him at 8.2 - "a stale number could
sneak into a decision"). One list every step uses: a man tagged O (out), IR or SUSP on any Yahoo roster read, or on the official
inactives list for this week. His THIS-WEEK number is zero for every expert until their own files catch up; later weeks untouched."""
import os, re, json, glob
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower().replace("’", "'")))
# Nov 1 (Dom's DK4: Browns LB Justin Jefferson's inactive zeroed the Vikings WR Justin Jefferson for every expert): an inactive
# counts only for a fantasy position, and only when his NFL team matches the man's team - name alone is never enough.
FANTASY_POS = {"QB", "RB", "WR", "TE", "K", "FB", "PK"}
TEAM_ABBR = {"arizona cardinals": "ARI", "atlanta falcons": "ATL", "baltimore ravens": "BAL", "buffalo bills": "BUF", "carolina panthers": "CAR",
             "chicago bears": "CHI", "cincinnati bengals": "CIN", "cleveland browns": "CLE", "dallas cowboys": "DAL", "denver broncos": "DEN",
             "detroit lions": "DET", "green bay packers": "GB", "houston texans": "HOU", "indianapolis colts": "IND", "jacksonville jaguars": "JAX",
             "kansas city chiefs": "KC", "las vegas raiders": "LV", "los angeles chargers": "LAC", "los angeles rams": "LA", "miami dolphins": "MIA",
             "minnesota vikings": "MIN", "new england patriots": "NE", "new orleans saints": "NO", "new york giants": "NYG", "new york jets": "NYJ",
             "philadelphia eagles": "PHI", "pittsburgh steelers": "PIT", "san francisco 49ers": "SF", "seattle seahawks": "SEA",
             "tampa bay buccaneers": "TB", "tennessee titans": "TEN", "washington commanders": "WAS"}
def team_abbr(t):
    t = str(t or "").strip(); u = t.upper().replace("WSH", "WAS").replace("JAC", "JAX").replace("LAR", "LA")
    return TEAM_ABBR.get(t.lower()) or (u if len(u) <= 3 else "")
def inactive_counts(entry, team=None):
    """True when this inactive-list entry can be the fantasy player on `team` (abbr or full name; None = unknown)."""
    pos = str(entry.get("pos") or "").upper()
    if pos and pos not in FANTASY_POS: return False
    a, b = team_abbr(entry.get("team")), team_abbr(team)
    return not (a and b and a != b)
def known_teams(R):
    """nk(name) -> set of NFL team abbrs, from every Yahoo roster row and the Sleeper player list"""
    kt = {}
    for f in glob.glob(os.path.join(R, "yahoo_drop/scout/dk*_rosters_live.txt")):
        try:
            for ln in open(f):
                x = ln.rstrip("\n").split("|")
                if not ln.startswith("#") and len(x) >= 5 and team_abbr(x[3]): kt.setdefault(nk(x[2]), set()).add(team_abbr(x[3]))
        except Exception: pass
    try:
        for p in (json.load(open(os.path.join(R, "feeds/sleeper_players_min.json"))).get("players") or {}).values():
            if p.get("name") and team_abbr(p.get("team")) and str(p.get("pos") or "").upper() in FANTASY_POS: kt.setdefault(nk(p["name"]), set()).add(team_abbr(p["team"]))
    except Exception: pass
    return kt
OUT_TAGS = {"O", "IR", "SUSP", "PUP-R", "NFI-R"}
def out_now(R, week=None):
    out = {}
    for f in glob.glob(os.path.join(R, "yahoo_drop/scout/dk*_rosters_live.txt")):
        try:
            for ln in open(f):
                if ln.startswith("#") or "|" not in ln: continue
                x = ln.rstrip("\n").split("|")
                if len(x) >= 6 and x[5].strip().upper() in OUT_TAGS: out[nk(x[2])] = "Yahoo tag " + x[5].strip().upper()
        except Exception: pass
    fs = sorted(glob.glob(os.path.join(R, "feeds/inactives/wk*.json")), key=lambda p: int(re.search(r"wk(\d+)", p).group(1)))
    if week is not None: fs = [p for p in fs if p.endswith(f"wk{week}.json")]
    for f in fs[-1:]:
        try:
            kt = known_teams(R)
            for p in json.load(open(f)).get("players") or []:
                k = nk(p.get("name")); teams = kt.get(k)
                if not inactive_counts(p): continue
                if teams and team_abbr(p.get("team")) and team_abbr(p.get("team")) not in teams: continue   # same name, different team
                out[k] = "inactive / out (ESPN injury feed)"
        except Exception: pass
    return out
