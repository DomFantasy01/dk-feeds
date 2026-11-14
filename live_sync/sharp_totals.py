"""SHARP FOOTBALL BETTING TOTALS - the playoff-offense tag (Nov 14 2026, Dom: "check what you just told me on whether we
could deploy that in a way that would make sense"; "bring it to the table so we can see it").

Reads Sharp Football Analysis's free implied-team-totals page (betting-market numbers: consensus total and spread across
DraftKings, FanDuel, BetMGM, Fanatics, Caesars) and keeps, for every NFL team:
  ros   - implied points a game for the rest of the season
  games - games left
  po    - implied points in the fantasy playoffs, Weeks 15-17 combined (look-ahead numbers until those lines post)
  po_rank - 1 = best playoff offense of 32
It rates whole OFFENSES, never players: a matchup/environment tag next to Ratcliffe and Clay, never a decider.
Writes dispatch_out/sharp_totals.json. Never fails the build: on any error it keeps the last good file.
usage: python3 sharp_totals.py REPO"""
import sys, os, re, json, html, urllib.request, datetime as dt
from zoneinfo import ZoneInfo

R = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = os.path.join(R, "dispatch_out", "sharp_totals.json")
URL = "https://www.sharpfootballanalysis.com/fantasy/nfl-implied-team-totals-tool/"
TEAMS = {"Arizona Cardinals": "ARI", "Atlanta Falcons": "ATL", "Baltimore Ravens": "BAL", "Buffalo Bills": "BUF", "Carolina Panthers": "CAR",
         "Chicago Bears": "CHI", "Cincinnati Bengals": "CIN", "Cleveland Browns": "CLE", "Dallas Cowboys": "DAL", "Denver Broncos": "DEN",
         "Detroit Lions": "DET", "Green Bay Packers": "GB", "Houston Texans": "HOU", "Indianapolis Colts": "IND", "Jacksonville Jaguars": "JAX",
         "Kansas City Chiefs": "KC", "Las Vegas Raiders": "LV", "Los Angeles Chargers": "LAC", "Los Angeles Rams": "LAR", "Miami Dolphins": "MIA",
         "Minnesota Vikings": "MIN", "New England Patriots": "NE", "New Orleans Saints": "NO", "New York Giants": "NYG", "New York Jets": "NYJ",
         "Philadelphia Eagles": "PHI", "Pittsburgh Steelers": "PIT", "San Francisco 49ers": "SF", "Seattle Seahawks": "SEA",
         "Tampa Bay Buccaneers": "TB", "Tennessee Titans": "TEN", "Washington Commanders": "WAS"}

def parse(page):
    """The rest-of-season table: <th scope="row">Team</th><td>ros</td><td>games</td><td>weeks 15-17</td>."""
    i = page.find("Fantasy Playoffs (Weeks 15-17)")
    if i < 0: raise ValueError("playoff table not found on the page")
    body = page[i: page.find("</table>", i)]
    teams = {}
    for name, ros, g, po in re.findall(r'<th[^>]*>\s*([^<]+?)\s*</th>\s*<td[^>]*>\s*([\d.]+)\s*</td>\s*<td[^>]*>\s*(\d+)\s*</td>\s*<td[^>]*>\s*([\d.]+)\s*</td>', body):
        ab = TEAMS.get(html.unescape(name).strip())
        if ab: teams[ab] = dict(ros=float(ros), games=int(g), po=float(po))
    if len(teams) < 28: raise ValueError(f"only {len(teams)} teams parsed")
    for k, (ab, _) in enumerate(sorted(teams.items(), key=lambda x: -x[1]["po"]), 1): teams[ab]["po_rank"] = k
    m = re.search(r"[Oo]dds last updated\s+([^<]{6,60}?)\.?\s*<", page)
    return teams, (html.unescape(m.group(1)).strip() if m else "")

def main():
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (dk-feeds)"})
        page = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
        teams, upd = parse(page)
        now = dt.datetime.now(ZoneInfo("America/Los_Angeles"))
        json.dump(dict(read=now.strftime("%a %b %-d %Y %-I:%M %p PT"), odds_updated=upd, source="Sharp Football Analysis implied team totals (betting lines)",
                       note="Whole offenses, not players. Weeks 15-17 = look-ahead estimates until those lines post. A tag, never a decider.",
                       teams=teams), open(OUT, "w"), indent=1)
        top = sorted(teams.items(), key=lambda x: x[1]["po_rank"])
        print(f"SHARP: {len(teams)} teams, odds updated {upd or '?'}; playoff best {top[0][0]} {top[0][1]['po']}, worst {top[-1][0]} {top[-1][1]['po']}")
    except Exception as e:
        print("!! SHARP totals skipped - keeping the last good file:", str(e)[:160])

if __name__ == "__main__":
    main()
