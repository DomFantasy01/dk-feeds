"""Nov 20 (Dom, voice): "if it's any of our experts that we're using, if it's two or more points off, we should mark it,
because we should at least be talking about it." Found on Braelon Allen: Ratcliffe's season-long line had him 16.4 for
Week 12 while Ratcliffe's own weekly, Clay, Koerner, RotoBaller and Vegas all had him about 10.

A MARK ONLY - it never changes a number, a lineup or a pick. Two checks, each in the league's own scoring:
  this week   - each expert (Ratcliffe, Koerner, Clay, RotoBaller, Vegas) against the middle of the others (needs 3+ experts)
  rest of season - Ratcliffe's per-game average against Clay's Weeks 12-17 average
A split counts when it is 2+ points AND 25%+ of the bigger number. Tested Nov 20 on Dom's four rosters: 2 points alone marked
39 players (nearly every starter - 2 points is normal noise on a 25-point QB); 2 points + 25% marked 10, all real splits
(Allen, Emmett Johnson, Price, Kiner, Fannin, White ...). Zeros are left out: a 0 is an injury/bye status, not an opinion.
"""
import csv, os, re, statistics, unicodedata as _ud

PTS, PCT = 2.0, 0.25
EXPERTS = (("Ratcliffe", "ftn_scored.csv"), ("Koerner", "koerner_scored.csv"), ("Clay", "clay_scored.csv"),
           ("RotoBaller", "rotoballer_scored.csv"), ("Vegas", "vegas_scored.csv"))


def _nk(s):
    s = "".join(c for c in _ud.normalize("NFKD", str(s)) if not _ud.combining(c))
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", s.lower()))


def _f(x):
    try: return float(x)
    except Exception: return None


def load(R):
    S = {}
    for ex, fn in EXPERTS:
        d = {}
        try:
            for r in csv.DictReader(open(os.path.join(R, "dispatch_out", fn))): d[(str(r["lg"]), _nk(r["name"]))] = r
        except Exception: pass
        S[ex] = d
    return S


def _big(a, b): return abs(a - b) >= PTS and abs(a - b) >= PCT * max(abs(a), abs(b))


def check(S, lg, name):
    """list of dicts {span, expert, his, others, note} for one player in one league ('1'..'4')."""
    lg, k, out = str(lg), _nk(name), []
    wk = {e: _f(S[e].get((lg, k), {}).get("wk")) for e in S}
    wk = {e: v for e, v in wk.items() if v is not None and v > 0.5}
    if len(wk) >= 3:
        for e, v in wk.items():
            oth = statistics.median([x for ee, x in wk.items() if ee != e])
            if _big(v, oth):
                out.append(dict(span="this week", expert=e, his=round(v, 1), others=round(oth, 1),
                                note=f"{e} {v:.1f} vs the others' middle {oth:.1f} this week"))
    r, c = S["Ratcliffe"].get((lg, k)), S["Clay"].get((lg, k))
    if r and c:
        rp = _f(r.get("ros_pg")); cv = [_f(c.get(f"w{w}")) for w in range(12, 18)]; cv = [x for x in cv if x and x > 0.5]
        if rp and rp > 0.5 and cv:
            ca = sum(cv) / len(cv)
            if _big(rp, ca):
                out.append(dict(span="rest of season", expert="Ratcliffe", his=round(rp, 1), others=round(ca, 1),
                                note=f"Ratcliffe {rp:.1f} a game vs Clay {ca:.1f} for the rest of the season"))
    return out
