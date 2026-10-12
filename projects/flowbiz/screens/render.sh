#!/bin/bash
# Przebudowa klocków animacji flowbiz: źródło → projekty HyperFrames → check → render.
#
#   screens/render.sh                       # wszystkie klocki, oba formaty (+ alfa tam, gdzie jest)
#   screens/render.sh stoper-40-do-5        # jeden klocek
#
# Wynik w build/ (poza gitem, odtwarzalny):
#   build/<klocek>-16x9.mp4, build/<klocek>-9x16.mp4
#   build/<klocek>-<format>-alpha.mov       (qtrle + alfa — nakładka na inny materiał)
# Do final/ kopiujemy ręcznie dopiero obejrzane wersje (patrz README).
set -euo pipefail
cd "$(dirname "$0")/.."

# HyperFrames wymaga Node 22+. Domyślny node bywa starszy (nvm), więc sięgamy po nowszy.
if ! node -e 'process.exit(+process.versions.node.split(".")[0] >= 22 ? 0 : 1)' 2>/dev/null; then
  NEWER=$(ls -d "$HOME"/.nvm/versions/node/v2[2-9]* 2>/dev/null | tail -1 || true)
  [ -n "$NEWER" ] || { echo "Potrzebny Node 22+ (HyperFrames)"; exit 1; }
  export PATH="$NEWER/bin:$PATH"
fi

HF="npx --yes hyperframes@0.8.145"
FPS=30

for dir in $(node screens/make.mjs "$@"); do
  name=$(basename "$dir")
  echo "── $name"
  $HF check "$dir"
  if [[ "$name" == *-alpha ]]; then
    frames="build/frames/$name"
    rm -rf "$frames"
    $HF render "$dir" --format png-sequence --fps $FPS -o "$frames"
    # qtrle (QuickTime Animation): bezstratny, z alfą, ~9× mniejszy od ProRes 4444 na płaskiej
    # grafice; czytany natywnie przez QuickTime, Final Cut i CapCut (.ai/memory/wstawki-alfa-nie-green-screen.md)
    ffmpeg -y -loglevel error -framerate $FPS -i "$frames/frame_%06d.png" -c:v qtrle -pix_fmt argb "build/$name.mov"
    rm -rf "$frames"
  else
    $HF render "$dir" --fps $FPS --quality high -o "build/$name.mp4"
  fi
done

ls -la build/*.mp4 build/*.mov 2>/dev/null
