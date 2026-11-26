#!/bin/bash
# Animacje do odcinka ep-doram — kopiuje shared/ do assets/ każdego projektu, sprawdza i renderuje.
#   ./render.sh                 wszystkie
#   ./render.sh 01-barcodes     wybrane
# Wynik: build/ (poza gitem). HyperFrames wymaga Node 22 (.ai/memory/hyperframes-wymaga-node-22).
set -e
cd "$(dirname "$0")"
export PATH="$HOME/.nvm/versions/node/v22.22.2/bin:$PATH"
HF="npx --yes hyperframes@0.7.85"
OUT=build; mkdir -p "$OUT"
PROJECTS=${@:-$(ls -d [0-9][0-9]-*/ | tr -d /)}
for p in $PROJECTS; do
  echo "── $p"
  mkdir -p "$p/assets"; cp -R shared/ "$p/assets/"
  [ -f "$p/hyperframes.json" ] || cp shared/hyperframes.json "$p/"
  $HF check "$p" || true
  # sekwencyjnie i z limitem (MK 25.11: swap prawie pełny) — 2 workery Chrome, nigdy kilka renderów naraz
  $HF render "$p" --fps 30 --quality high --workers 2 --output "$OUT/$p.mp4"
done
