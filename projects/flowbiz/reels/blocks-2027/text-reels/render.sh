#!/bin/bash
# Rolki tekstowe „System z klocków 2027": make → check → render MP4 do projects/flowbiz/build/.
#   ./render.sh                    # wszystkie warianty
#   ./render.sh A-contradiction    # jeden
set -euo pipefail
cd "$(dirname "$0")"
if ! node -e 'process.exit(+process.versions.node.split(".")[0] >= 22 ? 0 : 1)' 2>/dev/null; then
  NEWER=$(ls -d "$HOME"/.nvm/versions/node/v2[2-9]* 2>/dev/null | tail -1 || true)
  [ -n "$NEWER" ] || { echo "Potrzebny Node 22+ (HyperFrames)"; exit 1; }
  export PATH="$NEWER/bin:$PATH"
fi
HF="npx --yes hyperframes@0.8.145"
mkdir -p ../../../build
BUILD="$(cd ../../../build && pwd)"
for dir in $(node make.mjs "$@"); do
  name=$(basename "$dir")
  echo "── $name"
  $HF check "$dir"
  $HF render "$dir" --fps 30 --quality high -o "$BUILD/$name.mp4"
done
ls -la "$BUILD"/text-reel-*.mp4
