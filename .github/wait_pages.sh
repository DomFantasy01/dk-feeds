#!/usr/bin/env bash
# Nov 5: wait until no "pages build and deployment" run is queued or running before we push.
# Two pushes a minute apart made GitHub reject the second Pages deploy ("in progress deployment"),
# which emailed a "run failed" and could leave the site one push behind. Never blocks a save:
# gives up after ~4 minutes and pushes anyway.
R="${GITHUB_REPOSITORY:-DomFantasy01/dk-feeds}"
for i in $(seq 1 48); do
  n=0
  for s in queued in_progress waiting; do
    c=$(gh api "repos/$R/actions/runs?status=$s&per_page=50" \
          --jq '[.workflow_runs[] | select(.name=="pages build and deployment")] | length' 2>/dev/null || echo 0)
    n=$((n + c))
  done
  [ "$n" -eq 0 ] && exit 0
  [ "$i" -eq 1 ] && echo "waiting for the Pages deploy in progress to finish..."
  sleep 5
done
echo "Pages deploy still busy after ~4 min - pushing anyway"
exit 0
