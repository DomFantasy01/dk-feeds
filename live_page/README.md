# Dark Knight Live - the page's own code

The Live page lives at **https://claude.ai/artifact/BpRiXXCsxMLsdfMoxfrztr** (see LIVE_URL.txt).
On Nov 4 2026 the old page (claude.ai/code/artifact/2342ca1f-...) disappeared and its code, which only lived
inside the page, went with it. From now on the page's code is kept here.

- `dark_knight_live.html` - the exact file that is published. To restore the page, publish this file as an artifact,
  declare capabilities `{"db": {}, "mcp": {"servers": [{"server": "Claude Code Remote", "tools": ["fire_trigger"]}]}}`,
  then run the Live sync once to fill it, and put the new address in LIVE_URL.txt and every scheduled task.
- `src/` - the same page in four pieces; `python3 live_page/build.py` rebuilds the html from them.
- Every change to the page is committed here in the same session that publishes it.

Data the page reads (artifact database, collection `live`): `state` (Yahoo read), `models` (experts, simulator,
charts), `alerts`, `health` (system check), `moves` (Dom's decided plan). The page writes `alert_marks`
(read / delete / separate / clear marks) and `trail` (one entry per Yahoo read, for the read-by-read charts).
