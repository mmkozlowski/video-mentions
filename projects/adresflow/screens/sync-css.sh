#!/bin/bash
# Rozsyła wspólne arkusze i assety do projektów kompozycji.
#
# Każdy projekt MUSI mieć własną kopię `assets/` — HyperFrames serwuje
# kompozycję z katalogiem projektu jako bazą URL, więc ścieżka `../assets/…`
# przechodzi render, ale 404-uje w podglądzie Studio (lint:
# invalid_parent_traversal_in_asset_path). Źródłem prawdy jest ./assets/.
#
# Skrypt sam wykrywa projekty i to, których arkuszy używa dany `index.html`.
# Pierwsza wersja miała listę projektów wpisaną na sztywno (kw/wycena/oferta)
# i kopiowała wyłącznie `app.css` — więc dopisany do `pov.css` znak AI nigdy nie
# dojechał do projektów POV i wyrenderował się bez stylów. Błąd wyszedł dopiero
# na gotowym pliku, po dwóch renderach.
set -e
cd "$(dirname "$0")"

shopt -s nullglob
changed=0

for dir in */; do
  p="${dir%/}"
  [ -f "$p/index.html" ] || continue
  # css i wspólne assety (np. ai-icon.png) — pierwsza wersja brała tylko *.css
  for css in assets/*.css assets/*.png assets/*.svg; do
    [ -f "$css" ] || continue
    name=$(basename "$css")
    # kopiujemy tylko arkusze, do których projekt faktycznie się odwołuje
    grep -q "assets/$name" "$p/index.html" || continue
    mkdir -p "$p/assets"
    if ! cmp -s "$css" "$p/assets/$name"; then
      cp "$css" "$p/assets/$name"
      echo "→ $p/assets/$name"
      changed=1
    fi
  done
done

[ "$changed" = 0 ] && echo "wszystko aktualne"

cat <<'EOF'

Zmienione projekty przepuść przez bramkę (POV pomijamy — patrz README):
  npx hyperframes check kw && npx hyperframes check wycena && npx hyperframes check oferta
EOF
