#!/bin/bash
# DARK KNIGHT DISPATCH - scheduled build v2 (Oct 9 2026). Runs on GitHub's computer from .github/workflows/dispatch.yml.
# v2 adds THE SCOUT and the league pages (Field Report, Field - Scout, Positions) to the v1 front page.
# Order (Dom's rule): refresh data -> verify -> build. Stops at the first failure, so a broken step never prints an old page as new.
# ROOT is /home/claude on Claude's workspace and on the runner (the bundle is unpacked there), so the code runs unchanged.
set -euo pipefail
ROOT=${DK_ROOT:-/home/claude}; REPO=${GITHUB_WORKSPACE:-$(pwd)}; GF=${DK_GFONTS:-/usr/share/fonts/truetype/google-fonts}
OUTX=/mnt/user-data/outputs
echo "== 0 unpack code + saved data into $ROOT"
for d in "$ROOT" "$OUTX"; do if [ ! -d "$d" ]; then sudo mkdir -p "$d"; fi; sudo chown -R "$(id -u)" "$d"; done
unzip -oq "$REPO/dispatch_bundle.zip" -d "$ROOT"
mkdir -p "$ROOT/dksys/data/latest/pbp" "$ROOT/dksys/data/latest/meter" "$ROOT/dksys/data/archive" "$ROOT/dksys/gate/fresh" \
         "$ROOT/cand/global/out" "$ROOT/cand/fonts" "$ROOT/domfantasy01" "$OUTX/dkl_db/live"
cp "$ROOT/_ext/dkl_db/live/state.json" "$OUTX/dkl_db/live/state.json"
ln -sfn "$REPO" "$ROOT/domfantasy01/dk-feeds"                   # the feed jobs' own files (Sleeper, injuries) live in this repo
if [ -d "$REPO/scout_state" ]; then cp -r "$REPO/scout_state/." "$ROOT/dksys/scout/"; echo "   Scout memory restored (life cycle + archive)"; fi
if [ -d "$REPO/yahoo_drop" ]; then
  cp -r "$REPO/yahoo_drop/." "$ROOT/dksys/data/latest/yahoo/"; echo "   newer Yahoo pulls from yahoo_drop/ applied"
  if [ -d "$REPO/yahoo_drop/scout" ]; then cp -r "$REPO/yahoo_drop/scout/." "$ROOT/dksys/scout/"; echo "   newer Yahoo rosters/waivers for the Scout applied"; fi
fi
echo "== 1 fonts"
F=https://raw.githubusercontent.com/google/fonts/main/ofl
curl -sfL -o "$ROOT/cand/fonts/BebasNeue-Regular.ttf" $F/bebasneue/BebasNeue-Regular.ttf
sudo mkdir -p "$GF"; for w in Regular Medium Bold Light; do sudo curl -sfL -o "$GF/Poppins-$w.ttf" $F/poppins/Poppins-$w.ttf; done
echo "== 2 NFL data (nflverse)"
cd "$ROOT/dksys" && python3 gather/pull_nflverse.py && python3 gather/pull_pbp.py
N=https://github.com/nflverse/nflverse-data/releases/download
curl -sfL -o data/latest/stats_week_2025.csv $N/stats_player/stats_player_week_2025.csv
curl -sfL -o gate/fresh/play_by_play_2026.csv.gz $N/pbp/play_by_play_2026.csv.gz
curl -sfL -o gate/fresh/stats_player_week_2026.csv $N/stats_player/stats_player_week_2026.csv
curl -sfL -o gate/fresh/injuries_2026.csv $N/injuries/injuries_2026.csv
curl -sfL -o gate/fresh/roster_2026.csv $N/rosters/roster_2026.csv
curl -sfL -o gate/fresh/snap_counts_2026.csv $N/snap_counts/snap_counts_2026.csv
echo "== 3 Gotham";      (cd engine && python3 gotham.py | head -2)
echo "== 4 meter data";  (cd meter && python3 meter_data.py | grep -E "^METER|^DK|^ALARMS|^  !" || true)
echo "== 5 front page";  (cd "$ROOT/cand/global" && python3 global33.py > /tmp/front.log 2>&1 || { tail -20 /tmp/front.log; exit 1; })
echo "== 6 THE SCOUT, all four leagues"
for L in DKI DKII DKIII DKIV; do (cd "$ROOT/dksys/scout" && python3 scout_engine.py $L --quiet) && echo "   Scout $L ok"; done
echo "== 7 league pages (Field Report, Field - Scout, Positions)"
W=$(ls "$ROOT"/dksys/data/latest/meter/meter_wk*.json | sed 's/.*_wk\([0-9]*\)\.json/\1/' | sort -n | tail -1)
(cd "$ROOT/cand/redesign" && python3 fieldpos24.py "$ROOT/cand/global/out/DK_League_Pages_wk$W.pdf" > /tmp/league.log 2>&1 || { tail -20 /tmp/league.log; exit 1; })
echo "== 8 save"
mkdir -p "$REPO/dispatch_out" "$REPO/scout_state"
cp "$ROOT/cand/global/out/DK_Mountains_wk$W.pdf" "$REPO/dispatch_out/DK_Mountains_Wk${W}_latest.pdf"
cp "$ROOT/cand/global/out/DK_League_Pages_wk$W.pdf" "$REPO/dispatch_out/DK_League_Pages_Wk${W}_latest.pdf"
cp "$ROOT/dksys/data/latest/meter/meter_wk$W.json" "$ROOT/dksys/data/latest/meter/alarm_wk$W.json" "$REPO/dispatch_out/"
cp "$ROOT"/dksys/scout/scout_state_DK*.json "$ROOT"/dksys/scout/scout_archive_DK*.jsonl "$ROOT"/dksys/scout/scout_board_DK*.json "$REPO/scout_state/"
echo "DONE week $W"
