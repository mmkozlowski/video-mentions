#!/usr/bin/env bash
# Buduje film TAGO „chaos → system”: klipy Kling (MP4 poza gitem — CLIPS_DIR, domyślnie kopia w vaulcie)
# + nagranie prototypu (assets/recordings) → sekwencje klatek w katalogu tymczasowym
# → animation.html (napisy, przejścia) → final/2026-10-21-tago-chaos-system.mp4 + lektor (assets/voice).
# Długość klipu w scenie = długość sceny z `scenes` w animation.html (klip zwalniany przez minterpolate).
# Nowe nagranie prototypu: python3 -m http.server 8099 w revision-003, potem node record-prototype.js
set -euo pipefail
cd "$(dirname "$0")"
CLIPS="${CLIPS_DIR:-$HOME/Documents/Obsidian Vault/sales/tago/prezentacje/2026-10-21-animacja-chaos-system/media/clips}"
mkdir -p ../final
F="${FRAMES_DIR:-$(mktemp -d)/f}"
mkdir -p "$F"
# klip:długość sceny (s) — trzymać w zgodzie z animation.html
for pair in 1:6.4 3:8.4 4:6.9 5:6.4 6:7.1 2:6.5 7:8.35 8:5.0; do
  i=${pair%%:*}; d=${pair##*:}
  src=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CLIPS/$i.mp4")
  mkdir -p "$F/ai$i"
  ffmpeg -loglevel error -y -i "$CLIPS/$i.mp4" \
    -vf "setpts=$(python3 -c "print($d/$src)")*PTS,minterpolate=fps=30:mi_mode=mci,scale=1920:1080:flags=lanczos" \
    -q:v 3 "$F/ai$i/%04d.jpg" &
done
mkdir -p "$F/rec"
ffmpeg -loglevel error -y -i ../assets/recordings/tago-revision-003-dwa-okna.webm -vf fps=30 -q:v 2 "$F/rec/%04d.jpg" &
wait
node render-animation.mjs "$F" "$(cd ../final && pwd)/2026-10-21-tago-chaos-system.mp4"
