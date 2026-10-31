"""WHO IS OUT THIS WEEK (Oct 31 2026, Dom: Henderson was ruled out but Ratcliffe's file still had him at 8.2 - "a stale number could
sneak into a decision"). One list every step uses: a man tagged O (out), IR or SUSP on any Yahoo roster read, or on the official
inactives list for this week. His THIS-WEEK number is zero for every expert until their own files catch up; later weeks untouched."""
import os, re, json, glob
def nk(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(s).lower().replace("’", "'")))
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
            for p in json.load(open(f)).get("players") or []: out[nk(p.get("name"))] = "inactive / out (ESPN injury feed)"
        except Exception: pass
    return out
