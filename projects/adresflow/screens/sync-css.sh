#!/bin/bash
# Rozsyła wspólny arkusz do trzech projektów.
#
# Każdy projekt MUSI mieć własną kopię `assets/` — HyperFrames serwuje
# kompozycję z katalogiem projektu jako bazą URL, więc ścieżka `../assets/…`
# przechodzi render, ale 404-uje w podglądzie Studio (lint:
# invalid_parent_traversal_in_asset_path). Źródłem prawdy jest ./assets/app.css.
set -e
cd "$(dirname "$0")"

for p in kw wycena oferta; do
  cp assets/app.css "$p/assets/app.css"
  echo "→ $p/assets/app.css"
done

echo
echo "Teraz przepuść zmienione projekty przez bramkę:"
echo "  npx hyperframes check kw && npx hyperframes check wycena && npx hyperframes check oferta"
