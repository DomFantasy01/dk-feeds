"""Dark Knight Role Watch -- the numbers.

Week-over-week role change for every RB, WR and TE, from free nflverse data.
A player is a RISER when, from the prior week to the latest completed week,
  * his offensive snap share rose 10 points or more and now sits at 40%+, or
  * his opportunities (carries + targets) rose by a third or more, by at
    least 4, to 8 or more;
and in either case he saw at least 5 opportunities in the latest week.
A player is a FALLER on the same tests in reverse (share down 10+ points, or
opportunities down a third and by 4+).  Fallers are only shown for Dom's own
players -- a rival losing a role is not Dom's business.

Team quality is Dom's standing bad-team filter.  Two weeks of 2026 is too thin
to judge a team alone, so it blends last season's full record with this
season's, game for game:  under .400 = POOR (fails the rule).
"""
import os, re, json
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SEASON = 2026
POS = ("RB", "WR", "TE")
SNAP_JUMP, SNAP_FLOOR = 0.10, 0.40
OPP_RATIO, OPP_JUMP, OPP_FLOOR = 1.33, 4, 8
USE_FLOOR = 5          # a riser must also see 5+ opportunities -- snaps with no ball are decoy work
POOR_BELOW = 0.400

def norm(n):
    n = n.replace("-", " ")   # Oct 20 (Dom): hyphen = space, same as names.norm
    n = n.lower().replace(".", "").replace("'", "").replace("\u2019", "")
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return re.sub(r"[^a-z ]", "", re.sub(r"\s+", " ", n)).strip()

def load():
    s = pd.read_csv(os.path.join(DATA, f"snap_counts_{SEASON}.csv"))
    p = pd.read_csv(os.path.join(DATA, f"stats_player_week_{SEASON}.csv"), low_memory=False)
    g = pd.read_csv(os.path.join(DATA, "games.csv"))
    s = s[(s.season == SEASON) & (s.game_type == "REG") & s.position.isin(POS)]
    p = p[(p.season_type == "REG") & p.position.isin(POS)].copy()
    s = s.assign(key=s.player.map(norm))[["key", "player", "position", "team", "week", "offense_pct"]]
    p = p.assign(key=p.player_display_name.map(norm))
    p = p[["key", "team", "week", "carries", "targets", "target_share", "fantasy_points_ppr"]]
    df = s.merge(p, on=["key", "team", "week"], how="left").fillna(
        {"carries": 0, "targets": 0, "target_share": 0, "fantasy_points_ppr": 0})
    df["opps"] = df.carries + df.targets
    # Compare only COMPLETE weeks: a week counts once every game in it has a score.
    # (Fri Sep 26: nflverse already carries Thursday's Week 3 for ATL and GB alone.)
    gs = g[(g.season == SEASON) & (g.game_type == "REG")]
    done = [w for w, x in gs.groupby("week") if x.result.notna().all()]
    df = df[df.week <= max(done)]
    return df, g

def team_quality(g):
    q = {}
    reg = g[(g.game_type == "REG") & g.home_score.notna()]
    for season, wt in ((SEASON, 1.0),):          # THIS SEASON ONLY (Dom, Sat Sep 26) -- last year is a different team
        for _, r in reg[reg.season == season].iterrows():
            for tm, us, them in ((r.home_team, r.home_score, r.away_score),
                                 (r.away_team, r.away_score, r.home_score)):
                w = 1.0 if us > them else 0.5 if us == them else 0.0
                d = q.setdefault(tm, {"w": 0.0, "n": 0.0, "rec": [0, 0], "pd": 0})
                d["w"] += w * wt; d["n"] += wt
                if season == SEASON:
                    d["rec"][0 if us > them else 1] += 1 if us != them else 0
                    d["pd"] += int(us - them)
    out = {}
    for tm, d in q.items():
        pct = d["w"] / d["n"] if d["n"] else 0.5
        out[tm] = {"pct": round(pct, 3), "rec": "%d-%d" % tuple(d["rec"]), "pd": d["pd"],
                   "label": "POOR" if pct < POOR_BELOW else "GOOD" if pct >= 0.600 else "OK"}
    out["LAR"] = out.get("LAR", out.get("LA"))
    return out

def changes(df):
    L = int(df.week.max()); P = L - 1
    a = df[df.week == P].set_index("key"); b = df[df.week == L].set_index("key")
    rows = []
    for k, r in b.iterrows():
        pr = a.loc[k] if k in a.index else None
        if isinstance(pr, pd.DataFrame): pr = pr.iloc[0]
        s0 = float(pr.offense_pct) if pr is not None else 0.0
        o0 = float(pr.opps) if pr is not None else 0.0
        s1, o1 = float(r.offense_pct), float(r.opps)
        up = (s1 - s0 >= SNAP_JUMP and s1 >= SNAP_FLOOR) or \
             (o1 >= OPP_FLOOR and o1 - o0 >= OPP_JUMP and o1 >= OPP_RATIO * max(o0, 1))
        up = up and o1 >= USE_FLOOR
        dn = (s0 - s1 >= SNAP_JUMP) or (o0 - o1 >= OPP_JUMP and o1 <= o0 / OPP_RATIO)
        if up or dn:
            rows.append({"key": k, "name": r.player, "pos": r.position, "team": r.team,
                         "s0": round(s0 * 100), "s1": round(s1 * 100), "o0": int(o0), "o1": int(o1),
                         "c1": int(r.carries), "t1": int(r.targets), "ppr1": round(float(r.fantasy_points_ppr), 1),
                         "dir": "UP" if up else "DOWN",
                         "score": round((s1 - s0) * 100 + 2 * (o1 - o0), 1)})
    return P, L, rows

def compute():
    df, g = load()
    tq = team_quality(g)
    P, L, rows = changes(df)
    for r in rows: r["tq"] = tq.get(r["team"], {"label": "OK", "rec": "?", "pd": 0, "pct": .5})
    return P, L, rows, tq

if __name__ == "__main__":
    P, L, rows, tq = compute()
    up = sorted([r for r in rows if r["dir"] == "UP"], key=lambda r: -r["score"])
    dn = [r for r in rows if r["dir"] == "DOWN"]
    print("weeks", P, "->", L, "| risers", len(up), "| fallers", len(dn))
    for r in up[:45]:
        print(f'{r["name"]:24s}{r["pos"]} {r["team"]:3s} snap {r["s0"]:>3}->{r["s1"]:>3} opp {r["o0"]:>2}->{r["o1"]:>2} {r["tq"]["label"]} {r["tq"]["rec"]}')
    json.dump({"P": P, "L": L, "rows": rows}, open(os.path.join(HERE, "changes.json"), "w"), indent=1)
    print({t: (v["label"], v["pct"]) for t, v in sorted(tq.items()) if v and v["label"] == "POOR"})

# OCT20b role_watch names read hyphens as spaces
