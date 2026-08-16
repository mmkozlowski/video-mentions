#!/bin/bash
# Skleja gotową ścieżkę dźwiękową dla każdej wstawki — jeden WAV o długości sceny,
# z akcentami położonymi dokładnie tam, gdzie mówi arkusz czasów w README.md.
#
#   ./build-tracks.sh              → tracks/<scena>_sfx.wav
#   ./build-tracks.sh e08-05-granice
#
# Po co osobny WAV, a nie audio wklejone w MP4:
# wstawka jest nakładką chromakey, więc montaż musi móc ściszyć dźwięk pod zdaniem.
# Kładziesz ten plik jako JEDEN klip wyrównany do początku wstawki i masz komplet
# akcentów w punkt, zachowując pełną kontrolę nad poziomem.
set -e
cd "$(dirname "$0")"
mkdir -p tracks

# scena|długość|czas:dźwięk,czas:dźwięk,...
SCENES=(
"e08-01-cache|4.1|0.20:pop,1.10:pop,1.75:klik,1.95:tick,2.13:tick,2.31:tick,2.75:error,3.20:thud"
"e08-02-moduly|3.9|0.25:pop,0.51:pop,0.77:pop,1.16:pop,1.95:tick,2.60:error,3.00:thud"
"e08-03-racja|4.3|0.30:pop,1.00:pop,1.35:tick,1.60:tick,1.85:tick,2.10:tick,2.35:tick,2.60:tick,2.85:tick,3.10:tick,3.40:thud"
"e08-04-warstwy|7.3|0.30:pop,1.15:whoosh,1.15:line,1.55:pop,2.50:whoosh,2.50:line,2.90:pop,3.85:whoosh,3.85:line,4.25:pop,5.20:whoosh,6.25:thud"
"e08-05-granice|6.0|0.30:pop,1.30:whoosh,1.30:line,1.80:pop,2.85:whoosh,2.85:line,3.35:pop,4.40:thud"
"e08-06-bariera|3.6|0.35:pop,1.15:error,1.70:pop,2.15:line,2.70:thud"
"e01-01-kopie|4.0|0.25:pop,1.00:whoosh,1.45:whoosh,1.75:tick,2.15:tick,2.70:pop,3.20:thud"
"e01-02-cztery-branze|8.2|0.30:pop,1.25:whoosh,1.25:line,1.70:pop,2.70:whoosh,2.70:line,3.15:pop,4.15:whoosh,4.15:line,4.60:pop,5.60:whoosh,6.35:pop,7.15:thud"
"e01-03-dostep|6.7|0.30:pop,0.62:pop,0.90:pop,1.55:error,2.45:whoosh,2.45:line,2.90:pop,3.17:tick,3.43:tick,3.70:tick,3.87:pop,4.55:whoosh,5.60:thud"
"e01-04-skad-przenosisz|4.7|0.30:pop,0.54:pop,0.78:pop,1.45:line,1.79:line,2.40:pop,3.55:thud"
"e01-05-czym-to-nie-jest|4.9|0.30:pop,0.52:pop,0.74:pop,1.35:error,1.77:error,2.19:error,2.85:thud,3.55:pop"
"e08-07-framework|6.1|0.30:pop,0.50:pop,1.10:line,1.75:pop,2.10:tick,2.25:tick,2.40:tick,3.05:klik,3.57:error,4.09:klik,4.85:thud"
)

build () {
  local name="$1" dur="$2" events="$3"
  local inputs=() filters=() labels=() i=0

  IFS=',' read -ra EV <<< "$events"
  for e in "${EV[@]}"; do
    local t="${e%%:*}" snd="${e##*:}"
    local ms=$(printf "%.0f" "$(echo "$t * 1000" | bc -l)")
    inputs+=(-i "$snd.wav")
    filters+=("[$i]adelay=${ms}|${ms}[a$i]")
    labels+=("[a$i]")
    i=$((i+1))
  done

  local fc
  fc="$(IFS=';'; echo "${filters[*]}");$(IFS=''; echo "${labels[*]}")amix=inputs=$i:normalize=0:dropout_transition=0[m];[m]apad[out]"

  ffmpeg -y -v error "${inputs[@]}" \
    -filter_complex "$fc" -map "[out]" -t "$dur" -ac 1 -ar 48000 \
    "tracks/${name}_sfx.wav"
  echo "  ✓ tracks/${name}_sfx.wav  (${dur}s, $i akcentów)"
}

echo "── składam ścieżki SFX"
for row in "${SCENES[@]}"; do
  IFS='|' read -r name dur events <<< "$row"
  if [ -n "$1" ] && [ "$1" != "$name" ]; then continue; fi
  build "$name" "$dur" "$events"
done
echo "── gotowe"
