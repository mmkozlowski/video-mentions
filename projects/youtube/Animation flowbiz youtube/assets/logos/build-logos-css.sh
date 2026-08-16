#!/bin/bash
# Zamienia SVG-e marek w assets/logos/ na jeden plik compositions/logos.css.
#
# Dlaczego data: URI, a nie `url(../assets/logos/x.svg)`:
# render.js otwiera scenę przez file://, a maski CSS wczytywane z osobnego pliku
# lokalnego bywają blokowane przez CORS Chromium — wtedy logo znika bez błędu.
# Wklejone base64 nie ma tego problemu i scena jest samowystarczalna.
#
#   ./build-logos-css.sh
set -e
cd "$(dirname "$0")"
node build-logos-css.mjs
