#!/bin/bash
# DARK KNIGHT DISPATCH - scheduled build v3 (Oct 9 2026): everything the Oct 8 script did (front page, all Dispatch pages,
# calendar, Radar, scheduled Yahoo reads) PLUS THE SCOUT for all four leagues inside the Dispatch. Runs on GitHub's computer from .github/workflows/dispatch.yml.
# Order (Dom's rule): refresh data -> verify -> build. Stops at the first failure, so a broken step never prints an old page as new.
# ROOT is /home/claude on Claude's workspace and on the runner (the bundle is unpacked there), so the code runs unchanged.
set -euo pipefail
ROOT=${DK_ROOT:-/home/claude}; REPO=${GITHUB_WORKSPACE:-$(pwd)}; GF=${DK_GFONTS:-/usr/share/fonts/truetype/google-fonts}
echo "== 0 unpack code + saved data into $ROOT"
if [ ! -d "$ROOT" ]; then sudo mkdir -p "$ROOT" && sudo chown "$(id -u)" "$ROOT"; fi
unzip -oq "$REPO/dispatch_bundle.zip" -d "$ROOT"
python3 - "$ROOT/dksys/meter/meter_data.py" <<'PYFIX'
import sys; p=sys.argv[1]; s=open(p).read(); a="YWIN[(x[0], x[1])] = int(x[3])"
if a in s: open(p,"w").write(s.replace(a,"YWIN[(x[0], x[1])] = (int(x[3]) if x[3].strip() else None)")); print("   meter: blank Yahoo win % allowed")
PYFIX
if [ -d "$REPO/overlay" ]; then cp -r "$REPO/overlay/." "$ROOT/"; echo "   code updates from overlay/ applied"; fi   # newer scripts committed as text, no zip needed
[ -f "$ROOT/cand/redesign/_cal_patch.py" ] && python3 "$ROOT/cand/redesign/_cal_patch.py"   # the Dispatch calendar (Oct 8)
OUTD=${DK_OUTD:-/mnt/user-data/outputs}
[ -d "$OUTD" ] || { sudo mkdir -p "$OUTD" && sudo chown "$(id -u)" "$OUTD"; }   # old page code writes practice files here
[ -f "$OUTD/dkl_db/live/state.json" ] || { mkdir -p "$OUTD/dkl_db/live" && echo '{"leagues":[],"week":0}' > "$OUTD/dkl_db/live/state.json"; }   # and reads this (practice page only)
mkdir -p "$ROOT/dksys/data/latest/pbp" "$ROOT/dksys/data/latest/meter" "$ROOT/dksys/data/archive" "$ROOT/cand/global/out" "$ROOT/cand/fonts" "$ROOT/domfantasy01"
ln -sfn "$REPO" "$ROOT/domfantasy01/dk-feeds"                   # the feed job's own files (Sleeper, injuries) live in this repo
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
echo "== 5 front page";  (cd "$ROOT/cand/global" && python3 global33.py | grep "V33 DATA")
echo "== 5b THE SCOUT, all four leagues"
for L in DKI DKII DKIII DKIV; do (cd "$ROOT/dksys/scout" && python3 scout_engine.py $L --quiet) && echo "   Scout $L ok"; done
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
W=$(ls "$ROOT"/dksys/data/latest/meter/meter_wk*.json | sed 's/.*_wk\([0-9]*\)\.json/\1/' | sort -n | tail -1)
mkdir -p "$REPO/dispatch_out"
cp "$ROOT/cand/global/out/DK_Mountains_wk$W.pdf" "$REPO/dispatch_out/DK_Mountains_Wk${W}_latest.pdf"
cp "$ROOT/cand/global/out/Dark_Knight_Dispatch_Wk$W.pdf" "$REPO/dispatch_out/Dark_Knight_Dispatch_Wk${W}_latest.pdf"
cp "$ROOT/dksys/data/latest/meter/meter_wk$W.json" "$ROOT/dksys/data/latest/meter/alarm_wk$W.json" "$REPO/dispatch_out/"
rm -f "$REPO"/dispatch_out/DK_League_Pages_Wk*_latest.pdf                     # the Oct 9 v2 test file: the Scout now lives inside the Dispatch
mkdir -p "$REPO/dispatch_out/scout_state"                                       # the Scout's memory rides back to the repo with the pages
cp "$ROOT"/dksys/scout/scout_state_DK*.json "$ROOT"/dksys/scout/scout_archive_DK*.jsonl "$ROOT"/dksys/scout/scout_board_DK*.json "$REPO/dispatch_out/scout_state/"
echo "== 7 the Radar (live news, per league)"
if (cd "$ROOT/dksys/radar" && python3 radar_data.py && python3 radar_pages.py "$REPO/dispatch_out/DK_Radar_Wk${W}_latest.pdf"); then
  cp "$ROOT/dksys/data/latest/radar/radar_wk$W.json" "$REPO/dispatch_out/"; rm -f "$REPO/dispatch_out/RADAR_FAILED.txt"
else
  echo "Radar build FAILED at $(date -u +%FT%TZ) - the Dispatch above still saved; see the run log" > "$REPO/dispatch_out/RADAR_FAILED.txt"; echo "!! RADAR FAILED"
fi
echo "DONE week $W"
