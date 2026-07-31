#!/bin/bash
# Renderuje wszystkie ekrany produktu do ../build/screens/ — stamtąd bierze je
# story.py jako ujęcia `ekran-*`. Wynik jest odtwarzalny i kosztuje 0 kredytów,
# dlatego leży w build/ (poza gitem), a nie w assets/.
set -e
cd "$(dirname "$0")"

OUT=../build/screens
mkdir -p "$OUT"

for p in "$@"; do :; done
PROJECTS=${@:-"kw wycena oferta"}

for p in $PROJECTS; do
  echo "── $p"
  npx --yes hyperframes@latest check "$p"
  npx --yes hyperframes@latest render "$p" --fps 30 --quality high --output "$OUT/screen-$p.mp4"
done

ls -la "$OUT"
