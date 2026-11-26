#!/bin/bash
# Klatki kontrolne: ./snap.sh <projekt> <czasy po przecinku> <katalog wyjściowy>
set -e
cd "$(dirname "$0")"
export PATH="$HOME/.nvm/versions/node/v22.22.2/bin:$PATH"
mkdir -p "$1/assets"; cp -R shared/ "$1/assets/"; [ -f "$1/hyperframes.json" ] || cp shared/hyperframes.json "$1/"
npx --yes hyperframes@0.7.85 check "$1" 2>&1 | grep -E "✗|⚠|error\(s\)" || true
npx --yes hyperframes@0.7.85 snapshot "$1" --at "$2" --no-end --describe false -o "$3" 2>&1 | tail -1
