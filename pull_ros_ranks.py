"""Nov 20 (Dom, voice): rest-of-season RANKINGS as another check on playoff decisions - "they're not going to give you points,
but they would share where they are, whether they're 20th or 30th." Found on Pitts vs Kincaid: Ratcliffe had Pitts 11.5 a game,
but ESPN (TE10 Kincaid / TE19 Pitts), FantasyPros (Kincaid TE11, Pitts outside the top 12) and RotoWire all had Kincaid ahead.

Source: FantasyPros' public partner feed (the same one pull_experts.py uses) - the expert-consensus rest-of-season list, half-PPR,
QB/RB/WR/TE. Writes yahoo_drop/morning/ros_ranks.json: {"read_utc", "source", "pos": {"TE": [{"name","team","rank"}...]}}.
A RANK ONLY - it never changes a number. A failed read keeps the last good file.
"""
import json, os, sys, datetime as dt, urllib.request

R = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = os.path.join(R, "yahoo_drop", "morning", "ros_ranks.json")
UA = {"User-Agent": "Mozilla/5.0 (dk-feeds ros ranks)"}
API = "https://partners.fantasypros.com/api/v1/consensus-rankings.php?sport=NFL&year={y}&week=0&id=1054&position={p}&type=ROS&scoring=HALF&filters=1:2:3:4:5:7:8:9:285:699"

def main():
    y = dt.date.today().year
    out = {"read_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "source": "FantasyPros expert consensus, rest of season (half-PPR)", "pos": {}}
    for p in ("QB", "RB", "WR", "TE"):
        try:
            j = json.loads(urllib.request.urlopen(urllib.request.Request(API.format(y=y, p=p), headers=UA), timeout=40).read())
            rows = j.get("players") or []
            out["pos"][p] = [dict(name=r.get("player_name"), team=r.get("player_team_id"), rank=int(r.get("rank_ecr") or r.get("pos_rank", "0").lstrip("QBRWTE") or 0))
                             for r in rows if r.get("player_name")]
            out.setdefault("updated", j.get("last_updated"))
            print(f"ROS {p}: {len(out['pos'][p])} players")
        except Exception as e:
            print(f"!! ROS {p} read failed: {type(e).__name__}: {e}")
    if sum(len(v) for v in out["pos"].values()) < 100:
        print("!! ROS ranks too short - keeping the last good file"); return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=0)
    print("ROS ranks saved", OUT)

if __name__ == "__main__":
    main()
