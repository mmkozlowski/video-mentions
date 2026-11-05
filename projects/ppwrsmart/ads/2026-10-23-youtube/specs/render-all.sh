#!/usr/bin/env bash
# Renders every spec in this folder into ../final/<spec>.mp4 (one after another; ~2–4 min per reel).
set -euo pipefail
cd "$(dirname "$0")"
for s in ${@:-*.json}; do
  n=${s%.json}
  node ../../../tools/render-ad.mjs "$s" "../final/$n.mp4"
done
