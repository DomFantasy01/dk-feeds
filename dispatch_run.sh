#!/bin/bash
# DARK KNIGHT DISPATCH - front page, scheduled build (Oct 8 2026). Runs on GitHub's computer from .github/workflows/dispatch.yml.
# Order (Dom's rule): refresh data -> verify -> build. Stops at the first failure, so a broken step never prints an old page as new.
# ROOT is /home/claude on Claude's workspace and on the runner (the bundle is unpacked there), so the code runs unchanged.
set -euo pipefail
ROOT=${DK_ROOT:-/home/claude}; REPO=${GITHUB_WORKSPACE:-$(pwd)}; GF=${DK_GFONTS:-/usr/share/fonts/truetype/google-fonts}
echo "== 0 unpack code + saved data into $ROOT"
if [ ! -d "$ROOT" ]; then sudo mkdir -p "$ROOT" && sudo chown "$(id -u)" "$ROOT"; fi
unzip -oq "$REPO/dispatch_bundle.zip" -d "$ROOT"
mkdir -p "$ROOT/dksys/data/latest/pbp" "$ROOT/dksys/data/latest/meter" "$ROOT/dksys/data/archive" "$ROOT/cand/global/out" "$ROOT/cand/fonts" "$ROOT/domfantasy01"
ln -sfn "$REPO" "$ROOT/domfantasy01/dk-feeds"                   # the feed job's own files (Sleeper, injuries) live in this repo
if [ -d "$REPO/yahoo_drop" ]; then cp -r "$REPO/yahoo_drop/." "$ROOT/dksys/data/latest/yahoo/"; echo "   newer Yahoo pulls from yahoo_drop/ applied"; fi
echo "== 1 fonts"
F=https://raw.githubusercontent.com/google/fonts/main/ofl
curl -sfL -o "$ROOT/cand/fonts/BebasNeue-Regular.ttf" $F/bebasneue/BebasNeue-Regular.ttf
if [ -w "$(dirname "$GF")" ] || [ -d "$GF" -a -w "$GF" ]; then S=""; else S=sudo; fi
$S mkdir -p "$GF"; for w in Regular Medium Bold; do $S curl -sfL -o "$GF/Poppins-$w.ttf" $F/poppins/Poppins-$w.ttf; done
echo "== 2 NFL data (nflverse)"
cd "$ROOT/dksys" && python3 gather/pull_nflverse.py && python3 gather/pull_pbp.py
curl -sfL -o data/latest/stats_week_2025.csv https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_2025.csv
echo "== 3 Gotham";      (cd engine && python3 gotham.py | head -2)
echo "== 4 meter data";  (cd meter && python3 meter_data.py | grep -E "^METER|^DK|^ALARMS|^  !")
echo "== 5 page";        (cd "$ROOT/cand/global" && python3 global33.py | grep "V33 DATA")
W=$(ls "$ROOT"/dksys/data/latest/meter/meter_wk*.json | sed 's/.*_wk\([0-9]*\)\.json/\1/' | sort -n | tail -1)
mkdir -p "$REPO/dispatch_out"
cp "$ROOT/cand/global/out/DK_Mountains_wk$W.pdf" "$REPO/dispatch_out/DK_Mountains_Wk${W}_latest.pdf"
cp "$ROOT/dksys/data/latest/meter/meter_wk$W.json" "$ROOT/dksys/data/latest/meter/alarm_wk$W.json" "$REPO/dispatch_out/"
echo "DONE week $W"
