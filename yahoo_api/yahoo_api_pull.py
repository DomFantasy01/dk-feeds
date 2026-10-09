#!/usr/bin/env python3
# DARK KNIGHT - Yahoo read through Yahoo's official Fantasy Sports API (Oct 9 2026).
# Runs on GitHub's computer: no Chrome, no Dom's computer. Read-only (the app is registered "Fantasy Sports: Read").
#   python3 yahoo_api_pull.py auth <code> [repo]   one time: trade the approval code Yahoo shows for a lasting key
#   python3 yahoo_api_pull.py read [repo]          every run: read all four leagues, write the files the Dispatch uses
# Secrets come from the environment (GitHub repository secrets YAHOO_CLIENT_ID / YAHOO_CLIENT_SECRET) and are never
# printed. The lasting key (refresh token) is stored ENCRYPTED in yahoo_auth/token.enc with a key made from the client
# secret, so the public repo never holds anything usable. Standard library only.
import os, sys, json, time, base64, hashlib, hmac, secrets as _sec, urllib.request, urllib.parse, datetime as dt
import xml.etree.ElementTree as ET

LEAGUES = [("DKI", 1, "269381", 2), ("DKII", 2, "1519795", 7), ("DKIII", 3, "1507991", 2), ("DKIV", 4, "864215", 6)]
REDIRECT = "https://localhost"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
API = "https://fantasysports.yahooapis.com/fantasy/v2/"
NS = {"y": "http://fantasysports.yahooapis.com/fantasy/v2/base.rng"}
PT = dt.timezone(dt.timedelta(hours=-7))          # PDT; the stamp text says PT (shifts an hour after Nov 1, like the rest)

def now_pt(): return dt.datetime.now(dt.timezone.utc).astimezone(PT)
def stamp(t): return f"{t:%a} {t:%b} {t.day} {t.hour % 12 or 12}:{t:%M} {'AM' if t.hour < 12 else 'PM'} PT"
def creds():
    i, s = os.environ.get("YAHOO_CLIENT_ID", ""), os.environ.get("YAHOO_CLIENT_SECRET", "")
    if not i or not s: raise SystemExit("YAHOO_CLIENT_ID / YAHOO_CLIENT_SECRET are not set (GitHub repository secrets)")
    return i.strip(), s.strip()

# ---------------- encrypted token file (stdlib: SHA-256 keystream + HMAC) ----------------
def _keys(secret):
    k = hashlib.sha256(("dk-yahoo-v1|" + secret).encode()).digest()
    return hashlib.sha256(k + b"enc").digest(), hashlib.sha256(k + b"mac").digest()
def _stream(k, nonce, n):
    out, c = b"", 0
    while len(out) < n: out += hashlib.sha256(k + nonce + c.to_bytes(8, "big")).digest(); c += 1
    return out[:n]
def seal(obj, secret):
    ek, mk = _keys(secret); nonce = _sec.token_bytes(16); pt_ = json.dumps(obj).encode()
    ct = bytes(a ^ b for a, b in zip(pt_, _stream(ek, nonce, len(pt_))))
    tag = hmac.new(mk, nonce + ct, hashlib.sha256).digest()
    return json.dumps({"v": 1, "n": base64.b64encode(nonce).decode(), "c": base64.b64encode(ct).decode(), "t": base64.b64encode(tag).decode()})
def unseal(txt, secret):
    d = json.loads(txt); ek, mk = _keys(secret); nonce, ct = base64.b64decode(d["n"]), base64.b64decode(d["c"])
    if not hmac.compare_digest(hmac.new(mk, nonce + ct, hashlib.sha256).digest(), base64.b64decode(d["t"])):
        raise SystemExit("token file does not match this client secret (re-run the one-time approval)")
    return json.loads(bytes(a ^ b for a, b in zip(ct, _stream(ek, nonce, len(ct)))))

# ---------------- OAuth ----------------
def token_call(fields):
    cid, sec = creds()
    req = urllib.request.Request(TOKEN_URL, data=urllib.parse.urlencode(fields).encode(), method="POST", headers={
        "Authorization": "Basic " + base64.b64encode(f"{cid}:{sec}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")[:300]
        raise SystemExit(f"Yahoo sign-in refused ({e.code}): {body}")
def save_token(repo, tok):
    os.makedirs(f"{repo}/yahoo_auth", exist_ok=True)
    keep = {"refresh_token": tok["refresh_token"], "saved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    open(f"{repo}/yahoo_auth/token.enc", "w").write(seal(keep, creds()[1]) + "\n")
def access_token(repo):
    p = f"{repo}/yahoo_auth/token.enc"
    if not os.path.exists(p): raise SystemExit("no yahoo_auth/token.enc yet - run the one-time approval first")
    old = unseal(open(p).read().strip(), creds()[1])
    tok = token_call({"grant_type": "refresh_token", "refresh_token": old["refresh_token"], "redirect_uri": REDIRECT})
    if tok.get("refresh_token") and tok["refresh_token"] != old["refresh_token"]: save_token(repo, tok)
    return tok["access_token"]

# ---------------- API ----------------
class Y:
    def __init__(s, at): s.at, s.calls = at, 0
    def get(s, path):
        for attempt in range(3):
            req = urllib.request.Request(API + path, headers={"Authorization": "Bearer " + s.at})
            try:
                with urllib.request.urlopen(req, timeout=40) as r: s.calls += 1; return ET.fromstring(r.read())
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503) and attempt < 2: time.sleep(4 * (attempt + 1)); continue
                raise RuntimeError(f"{path}: HTTP {e.code} {e.read().decode(errors='ignore')[:200]}")
            except Exception as e:
                if attempt < 2: time.sleep(4); continue
                raise RuntimeError(f"{path}: {e}")
def t(el, path, default=""):
    x = el.find(path, NS); return (x.text or "").strip() if x is not None and x.text is not None else default
def player_row(p):
    pos = t(p, "y:display_position"); name = t(p, "y:name/y:full")
    if pos == "DEF":
        full = t(p, "y:editorial_team_full_name"); name = full.split()[-1] if full else name   # Yahoo pages show the nickname
    abbr = t(p, "y:editorial_team_abbr"); abbr = abbr[:1] + abbr[1:].lower() if abbr else ""
    return dict(slot=t(p, "y:selected_position/y:position"), name=name, team=abbr, pos=pos, status=t(p, "y:status"),
                key=t(p, "y:player_key"))
def read_league(y, gk, lab, lid, me, log):
    lk = f"{gk}.l.{lid}"; L = {"league_key": lk, "me": me}
    meta = y.get(f"league/{lk}").find("y:league", NS); L["name"] = t(meta, "y:name"); L["week"] = int(t(meta, "y:current_week", "0") or 0)
    teams = []
    for tm in y.get(f"league/{lk}/teams/roster").iterfind(".//y:team", NS):
        tid = int(t(tm, "y:team_id")); pl = [player_row(p) for p in tm.iterfind("y:roster/y:players/y:player", NS)]
        teams.append(dict(id=tid, name=t(tm, "y:name"), players=pl))
    L["teams"] = sorted(teams, key=lambda d: d["id"])
    sb = []
    for m in y.get(f"league/{lk}/scoreboard").iterfind(".//y:matchup", NS):
        side = [dict(id=int(t(x, "y:team_id")), name=t(x, "y:name"), points=t(x, "y:team_points/y:total"),
                     proj=t(x, "y:team_projected_points/y:total"), win_probability=t(x, "y:win_probability"))
                for x in m.iterfind("y:teams/y:team", NS)]
        sb.append(dict(week=t(m, "y:week"), status=t(m, "y:status"), teams=side))
    L["scoreboard"] = sb
    st = []
    for x in y.get(f"league/{lk}/standings").iterfind(".//y:team", NS):
        st.append(dict(id=int(t(x, "y:team_id")), name=t(x, "y:name"), rank=t(x, "y:team_standings/y:rank"),
                       w=t(x, "y:team_standings/y:outcome_totals/y:wins"), l=t(x, "y:team_standings/y:outcome_totals/y:losses"),
                       tie=t(x, "y:team_standings/y:outcome_totals/y:ties"), pf=t(x, "y:team_points/y:total")))
    L["standings"] = st
    wv, start = [], 0
    while start < 400:
        got = list(y.get(f"league/{lk}/players;status=W;start={start};count=25/ownership").iterfind(".//y:player", NS))
        for p in got:
            wd = t(p, "y:ownership/y:waiver_date")
            wv.append(dict(name=player_row(p)["name"], pos=t(p, "y:display_position"), clears=wd))
        if len(got) < 25: break
        start += 25
    L["waivers"] = wv
    n = sum(len(x["players"]) for x in teams)
    log.append(f"{lab} {L['name']}: week {L['week']}, {len(teams)} teams, {n} rostered, {len(sb)} matchups, {len(wv)} on waivers")
    return L

def clears(d):
    try: x = dt.date.fromisoformat(d); return f"{x:%b} {x.day}"
    except Exception: return "waivers"
def write_scout(repo, lab, n, L, when):
    od = f"{repo}/yahoo_drop/scout"; os.makedirs(od, exist_ok=True)
    head = f"# {lab} ({L['league_key']}) all {len(L['teams'])} rosters, Yahoo API read {when}. team|slot|name|team|pos|status"
    rows = [f"{tm['id']}|{p['slot']}|{p['name']}|{p['team']}|{p['pos']}|{p['status']}" for tm in L["teams"] for p in tm["players"]]
    open(f"{od}/dk{n}_rosters_live.txt", "w").write(head + "\n" + "\n".join(rows) + "\n")
    open(f"{od}/dk{n}_waivers.txt", "w").write(f"# {lab} players on waivers (not free agents), Yahoo API read {when}: name/clears\n"
                                              + "|".join(f"{w['name']}/{clears(w['clears'])}" for w in L["waivers"]) + "\n")
def write_all_rosters(repo, out, when, tag):
    wk = max((L.get("week") or 0) for L in out.values()) or 0
    od = f"{repo}/yahoo_drop/wk{wk}"; os.makedirs(od, exist_ok=True)
    lines = [f"{n}~{tm['id']}~" + "|".join(p["name"] for p in tm["players"]) for lab, n, _, _ in LEAGUES if lab in out for tm in out[lab]["teams"]]
    open(f"{od}/all_rosters_{tag}.txt", "w").write(f"# Yahoo team pages, every team in all four leagues, {when}. league(1=DK I 269381, 2=DK II 1519795, 3=DK III 1507991, 4=DK IV 864215)~team id~players (DEF listed by nickname). (Yahoo API read)\n" + "\n".join(lines) + "\n")

def main():
    a = sys.argv[1:]
    if not a: raise SystemExit(__doc__ or "usage: auth <code> [repo] | read [repo]")
    if a[0] == "auth":
        repo = a[2] if len(a) > 2 else os.getcwd()
        tok = token_call({"grant_type": "authorization_code", "code": a[1].strip(), "redirect_uri": REDIRECT})
        save_token(repo, tok); print("approved: lasting key saved (encrypted) to yahoo_auth/token.enc"); a = ["read", repo]
    if a[0] == "read":
        repo = a[1] if len(a) > 1 else os.getcwd(); T = now_pt(); when = stamp(T); tag = f"{T:%a}".lower() + f"{T:%H%M}"
        log, out = [], {}
        y = Y(access_token(repo))
        gk = t(y.get("game/nfl").find("y:game", NS), "y:game_key")
        for lab, n, lid, me in LEAGUES:
            try: out[lab] = read_league(y, gk, lab, lid, me, log); write_scout(repo, lab, n, out[lab], when)
            except Exception as e: log.append(f"FAILED {lab}: {str(e)[:200]}")
        if out: write_all_rosters(repo, out, when, tag)
        os.makedirs(f"{repo}/yahoo_api", exist_ok=True)
        status = dict(read_pt=when, read_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), game_key=gk,
                      leagues_read=sorted(out), calls=y.calls, log=log)
        json.dump(dict(status, leagues=out), open(f"{repo}/yahoo_api/latest.json", "w"), indent=1)
        json.dump(status, open(f"{repo}/yahoo_api/status.json", "w"), indent=1)
        print("YAHOO API read", when, "|", "; ".join(log))
        if not out: raise SystemExit("no league could be read")
main()
