#!/bin/bash
# DARK KNIGHT DISPATCH - scheduled build v3 (Oct 9 2026): everything the Oct 8 script did (front page, all Dispatch pages,
# calendar, Radar, scheduled Yahoo reads) PLUS THE SCOUT for all four leagues inside the Dispatch. Runs on GitHub's computer from .github/workflows/dispatch.yml.
# Order (Dom's rule): refresh data -> verify -> build. Stops at the first failure, so a broken step never prints an old page as new.
# ROOT is /home/claude on Claude's workspace and on the runner (the bundle is unpacked there), so the code runs unchanged.
set -euo pipefail
ROOT=${DK_ROOT:-/home/claude}; REPO=${GITHUB_WORKSPACE:-$(pwd)}; GF=${DK_GFONTS:-/usr/share/fonts/truetype/google-fonts}
echo "== 0 unpack code + saved data into $ROOT"
if [ ! -d "$ROOT" ]; then sudo mkdir -p "$ROOT" && sudo chown "$(id -u)" "$ROOT"; fi
# Oct 21 (Dom): ONE SYSTEM. All the code and its starting data live as plain files in system/ - no zip bundle, no overlay,
# no patch scripts run at build time. What is in system/ is exactly what runs. (The old patch scripts sit in retired/, never run.)
cp -r "$REPO/system/." "$ROOT/"; echo "   code from system/ (the one copy of the code)"
OUTD=${DK_OUTD:-/mnt/user-data/outputs}
[ -d "$OUTD" ] || { sudo mkdir -p "$OUTD" && sudo chown "$(id -u)" "$OUTD"; }   # old page code writes practice files here
[ -f "$OUTD/dkl_db/live/state.json" ] || { mkdir -p "$OUTD/dkl_db/live" && echo '{"leagues":[],"week":0}' > "$OUTD/dkl_db/live/state.json"; }   # and reads this (practice page only)
mkdir -p "$ROOT/dksys/data/latest/pbp" "$ROOT/dksys/data/latest/meter" "$ROOT/dksys/data/archive" "$ROOT/cand/global/out" "$ROOT/cand/fonts" "$ROOT/domfantasy01"
ln -sfn "$REPO" "$ROOT/domfantasy01/dk-feeds"                   # the feed job's own files (Sleeper, injuries) live in this repo
echo "== 0b Yahoo through the Yahoo API (no Chrome) - a failed read keeps the last good one and says so"
if [ -n "${YAHOO_CLIENT_ID:-}" ] && [ -f "$REPO/yahoo_auth/token.enc" ] && [ -f "$REPO/yahoo_api/yahoo_api_pull.py" ]; then
  python3 "$REPO/yahoo_api/yahoo_api_pull.py" read "$REPO" || echo "!! Yahoo API read FAILED - using the last good Yahoo read"
else echo "   Yahoo API not approved yet - using the last Yahoo read in the repo"; fi
if [ -d "$REPO/yahoo_drop" ]; then cp -r "$REPO/yahoo_drop/." "$ROOT/dksys/data/latest/yahoo/"; echo "   newer Yahoo pulls from yahoo_drop/ applied"; fi
if [ -d "$REPO/yahoo_drop/scout" ]; then cp -r "$REPO/yahoo_drop/scout/." "$ROOT/dksys/scout/"; echo "   newer Yahoo rosters/waivers for the Scout applied"; fi
if [ -d "$REPO/dispatch_out/scout_state" ]; then cp -r "$REPO/dispatch_out/scout_state/." "$ROOT/dksys/scout/"; echo "   Scout memory restored (life cycle + archive)"; fi
python3 - "$REPO" "$ROOT" <<'PYIN'
# the scheduled Yahoo read (Oct 8) commits one bundle per read to yahoo_drop/_inbox/ - unpack them oldest first so the newest wins
import sys, json, glob, os
R, ROOT = sys.argv[1], sys.argv[2]; fs = sorted(glob.glob(R + "/yahoo_drop/_inbox/pull_*.json"))
for f in fs:
    d = json.load(open(f))
    for p, c in d["files"].items():
        if ".." in p or p.startswith("/"): continue
        o = os.path.join(ROOT, "dksys/data/latest/yahoo", p); os.makedirs(os.path.dirname(o), exist_ok=True); open(o, "w").write(c)
if fs: print("   scheduled Yahoo reads unpacked:", len(fs), "| newest", os.path.basename(fs[-1]), "read", json.load(open(fs[-1])).get("read_pt"))
PYIN
echo "== 0c the named experts' rankings (Oct 25, Dom): pulled fresh every build - on game days they update after the inactives"
python3 "$REPO/pull_experts.py" "$REPO" | head -2 || echo "!! expert pull failed - the panel uses the last saved lists"
echo "== 1 fonts"
F=https://raw.githubusercontent.com/google/fonts/main/ofl
curl -sfL -o "$ROOT/cand/fonts/BebasNeue-Regular.ttf" $F/bebasneue/BebasNeue-Regular.ttf
if [ -w "$(dirname "$GF")" ] || [ -d "$GF" -a -w "$GF" ]; then S=""; else S=sudo; fi
$S mkdir -p "$GF"; for w in Regular Medium Bold Light SemiBold; do $S curl -sfL -o "$GF/Poppins-$w.ttf" $F/poppins/Poppins-$w.ttf; done
echo "== 2 NFL data (nflverse)"
cd "$ROOT/dksys" && python3 gather/pull_nflverse.py && python3 gather/pull_pbp.py
N=https://github.com/nflverse/nflverse-data/releases/download; mkdir -p gate/fresh
curl -sfL -o data/latest/stats_week_2025.csv $N/stats_player/stats_player_week_2025.csv
curl -sfL -o gate/fresh/play_by_play_2026.csv.gz $N/pbp/play_by_play_2026.csv.gz          # the Scout's inputs (Oct 9)
curl -sfL -o gate/fresh/stats_player_week_2026.csv $N/stats_player/stats_player_week_2026.csv
curl -sfL -o gate/fresh/injuries_2026.csv $N/injuries/injuries_2026.csv
curl -sfL -o gate/fresh/roster_2026.csv $N/rosters/roster_2026.csv
curl -sfL -o gate/fresh/snap_counts_2026.csv $N/snap_counts/snap_counts_2026.csv
echo "== 3 Gotham";      (cd engine && python3 gotham.py | head -2)
echo "== 4 meter data";  (cd meter && python3 meter_data.py | grep -E "^METER|^DK|^ALARMS|^  !")
echo "== 4b expert moves (Oct 25, Dom): who the named experts moved up or down since the last pull and since last week"
WM=$(ls "$ROOT"/dksys/data/latest/meter/meter_wk*.json | sed 's/.*_wk\([0-9]*\)\.json/\1/' | sort -n | tail -1)
DK_ROOT="$ROOT" python3 "$ROOT/dksys/scout/expert_moves.py" "$REPO" --meter "$ROOT/dksys/data/latest/meter/meter_wk$WM.json" > "$ROOT/expert_moves.log" 2>&1 && head -3 "$ROOT/expert_moves.log" || { echo "!! EXPERT MOVES FAILED - the Dispatch prints without them"; tail -5 "$ROOT/expert_moves.log"; }
DK_ROOT="$ROOT" python3 "$ROOT/dksys/scout/pieces_check.py" "$REPO" --pieces "$ROOT/cand/missing_pieces.json" --meter "$ROOT/dksys/data/latest/meter/meter_wk$WM.json" > "$ROOT/pieces_check.log" 2>&1 && head -1 "$ROOT/pieces_check.log" || { echo "!! MISSING PIECES CHECK FAILED"; tail -5 "$ROOT/pieces_check.log"; }
echo "== 5 front page";  (cd "$ROOT/cand/global" && python3 global33.py | grep "V33 DATA")
echo "== 5b THE SCOUT, all four leagues"
# Oct 24: a Scout crash used to pass silently (the old board was copied back as if new). Now it is logged loudly and
# written to dispatch_out/SCOUT_FAILED.txt, which a good run clears.
rm -f "$REPO/dispatch_out/SCOUT_FAILED.txt"
for L in DKI DKII DKIII DKIV; do
  if (cd "$ROOT/dksys/scout" && python3 scout_engine.py $L --quiet) > "$ROOT/scout_$L.log" 2>&1; then echo "   Scout $L ok"
  else echo "!! SCOUT $L FAILED - its board is the last good one"; tail -4 "$ROOT/scout_$L.log"; { echo "Scout $L failed at $(date -u +%FT%TZ):"; tail -4 "$ROOT/scout_$L.log"; } >> "$REPO/dispatch_out/SCOUT_FAILED.txt"; fi
done
echo "== 5c alerts for the Field Report's alert mark (Oct 14, Dom): same code and feeds as Live's alerts, kept build to build"
WA=$(ls "$ROOT"/dksys/data/latest/meter/meter_wk*.json | sed 's/.*_wk\([0-9]*\)\.json/\1/' | sort -n | tail -1)
python3 "$REPO/live_sync/alerts.py" "$REPO/dispatch_out/radar_wk$WA.json" "$REPO/dispatch_out/actions_latest.json" "$ROOT/dksys/data/latest/meter/meter_wk$WA.json" "$ROOT/dksys/data/latest/meter/alarm_wk$WA.json" "$REPO/dispatch_out/alerts_build.json" "$REPO/dispatch_out/alerts_build.json" --feeds "$REPO/feeds" || echo "!! alert marks skipped this build - the Field Report prints without them"
echo "== 6 the other pages"; W0=$(ls "$ROOT"/dksys/data/latest/meter/meter_wk*.json | sed 's/.*_wk\([0-9]*\)\.json/\1/' | sort -n | tail -1)
(cd "$ROOT/cand/redesign" && python3 fieldpos24.py "$ROOT/cand/global/out/DK_Dispatch_wk${W0}_pages.pdf" | grep -E "^=====|V23 LIVE|^CALENDAR|^POST-MORTEM|^OUTLOOK" | cut -c1-120)
python3 -m pip install -q pypdf 2>/dev/null || pip install -q pypdf
python3 - "$ROOT" "$W0" <<'PYEOF'
import sys; from pypdf import PdfReader, PdfWriter
R,W=sys.argv[1],sys.argv[2]; w=PdfWriter()
w.add_page(PdfReader(f"{R}/cand/global/out/DK_Mountains_wk{W}.pdf").pages[0])
for p in PdfReader(f"{R}/cand/global/out/DK_Dispatch_wk{W}_pages.pdf").pages: w.add_page(p)
w.write(f"{R}/cand/global/out/Dark_Knight_Dispatch_Wk{W}.pdf"); print("assembled",len(w.pages),"pages")
PYEOF
if [ -f "$ROOT/cand/_footer_pass.py" ]; then python3 "$ROOT/cand/_footer_pass.py" "$ROOT/cand/global/out/Dark_Knight_Dispatch_Wk${W0}.pdf"; fi   # one footer on every page, Page N of M (Dom, Oct 10)
W=$(ls "$ROOT"/dksys/data/latest/meter/meter_wk*.json | sed 's/.*_wk\([0-9]*\)\.json/\1/' | sort -n | tail -1)
mkdir -p "$REPO/dispatch_out"
cp "$ROOT/cand/global/out/DK_Mountains_wk$W.pdf" "$REPO/dispatch_out/DK_Mountains_Wk${W}_latest.pdf"
cp "$ROOT/cand/global/out/Dark_Knight_Dispatch_Wk$W.pdf" "$REPO/dispatch_out/Dark_Knight_Dispatch_Wk${W}_latest.pdf"
cp "$ROOT/cand/global/out/Dark_Knight_Dispatch_Wk$W.pdf" "$REPO/dispatch_out/Dark_Knight_Dispatch_latest.pdf"   # one fixed link that never changes week to week (Oct 9)
cp "$ROOT/dksys/data/latest/meter/meter_wk$W.json" "$ROOT/dksys/data/latest/meter/alarm_wk$W.json" "$REPO/dispatch_out/"
cp "$ROOT/dksys/data/latest/weather_wk$W.json" "$REPO/dispatch_out/" 2>/dev/null || echo "no weather file this build"   # game weather for Dark Knight Live (Oct 11)
rm -f "$REPO"/dispatch_out/DK_League_Pages_Wk*_latest.pdf                     # the Oct 9 v2 test file: the Scout now lives inside the Dispatch
mkdir -p "$REPO/dispatch_out/scout_state"                                       # the Scout's memory rides back to the repo with the pages
cp "$ROOT"/dksys/scout/scout_state_DK*.json "$ROOT"/dksys/scout/scout_archive_DK*.jsonl "$ROOT"/dksys/scout/scout_board_DK*.json "$REPO/dispatch_out/scout_state/"
if [ -f "$ROOT/cand/scoreboard.py" ]; then python3 "$ROOT/cand/scoreboard.py" "$REPO" || echo "!! SCOREBOARD FAILED - the Dispatch above still saved"; fi   # the checks-and-balances engine (Dom, Oct 11)
echo "== 7 the Radar (live news, per league)"
if (cd "$ROOT/dksys/radar" && python3 radar_data.py && python3 radar_pages.py "$REPO/dispatch_out/DK_Radar_Wk${W}_latest.pdf"); then
  cp "$ROOT/dksys/data/latest/radar/radar_wk$W.json" "$REPO/dispatch_out/"; rm -f "$REPO/dispatch_out/RADAR_FAILED.txt"
else
  echo "Radar build FAILED at $(date -u +%FT%TZ) - the Dispatch above still saved; see the run log" > "$REPO/dispatch_out/RADAR_FAILED.txt"; echo "!! RADAR FAILED"
fi
echo "== 8 the state file (Oct 19, Dom): one file Claude reads instead of scraping Yahoo"
python3 "$REPO/state/build_state.py" "$REPO" "$ROOT" || echo "!! STATE FILE FAILED - the Dispatch above still saved"
echo "== 9 MORNING CHECK (Oct 24, Dom): expert lane (Justin Boone), new-arrival gate (traded/signed/dropped), transaction review"
# Its own lane beside the Scout - the Scout's workload filters never touch it. Reads yahoo_drop/morning/ (the 5 AM Chrome read).
# First the EXPERT PANEL: six named voices (Boone, ESPN, CBS, FFToday, Sleeper, Yahoo) + the full workup; only names it passes reach the brief.
curl -sfL -o "$ROOT/dksys/gate/fresh/games.csv" https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv || echo "!! schedule download failed - the panel prints without byes and playoff matchups"
python3 "$ROOT/dksys/scout/expert_panel.py" "$REPO" --stats "$ROOT/dksys/gate/fresh/stats_player_week_2026.csv" --snaps "$ROOT/dksys/gate/fresh/snap_counts_2026.csv" --games "$ROOT/dksys/gate/fresh/games.csv" > "$ROOT/expert_panel.log" 2>&1 && head -2 "$ROOT/expert_panel.log" || { echo "!! EXPERT PANEL FAILED"; tail -5 "$ROOT/expert_panel.log"; rm -f "$REPO/dispatch_out/expert_panel.json"; }
if python3 "$ROOT/dksys/scout/morning_review.py" "$REPO" > "$ROOT/morning_review.log" 2>&1; then head -2 "$ROOT/morning_review.log"; else echo "!! MORNING CHECK FAILED - the Dispatch above still saved"; tail -5 "$ROOT/morning_review.log"; fi
DK_ROOT="$ROOT" python3 "$ROOT/dksys/scout/expert_moves.py" "$REPO" --meter "$REPO/dispatch_out/meter_wk$W.json" --brief > "$ROOT/expert_moves2.log" 2>&1 && echo "   expert moves added to the brief" || { echo "!! EXPERT MOVES (brief) FAILED"; tail -5 "$ROOT/expert_moves2.log"; }
DK_ROOT="$ROOT" python3 "$ROOT/dksys/scout/pieces_check.py" "$REPO" --pieces "$ROOT/cand/missing_pieces.json" --meter "$REPO/dispatch_out/meter_wk$W.json" --brief > "$ROOT/pieces_check2.log" 2>&1 && echo "   missing pieces check added to the brief" || { echo "!! MISSING PIECES CHECK (brief) FAILED"; tail -5 "$ROOT/pieces_check2.log"; }
python3 "$REPO/live_sync/brief_scoreboard.py" "$REPO/dispatch_out/scoreboard/scoreboard.txt" "$REPO/dispatch_out/brief_latest.txt" || echo "!! SCOREBOARD section skipped"   # Oct 27 (Dom): the weekly projection check, heard in the brief
python3 "$REPO/live_sync/brief_waiver_experts.py" "$REPO" "$REPO/dispatch_out/brief_latest.txt" || echo "!! WAIVER EXPERTS section skipped"   # Oct 27 (Dom): experts before claims
python3 "$REPO/live_sync/brief_prekick.py" "$REPO/dispatch_out/alerts_build.json" "$REPO/dispatch_out/brief_latest.txt" || echo "!! BEFORE LOCK section skipped"
echo "DONE week $W"
