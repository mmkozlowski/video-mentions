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
"e01-03-dostep|6.7|0.30:pop,0.62:pop,0.90:pop,1.18:pop,1.55:error,2.45:whoosh,2.90:pop,3.17:tick,3.43:tick,3.70:tick,3.87:pop,4.55:whoosh,5.60:thud"
"e01-04-skad-przenosisz|6.0|0.30:pop,0.56:pop,0.82:pop,1.35:pop,1.61:pop,1.87:pop,2.45:line,2.84:line,3.65:pop,4.85:thud"
"e01-05-czym-to-nie-jest|4.9|0.30:pop,0.52:pop,0.74:pop,1.35:error,1.77:error,2.19:error,2.85:thud,3.55:pop"
"e08-07-framework|6.1|0.30:pop,0.50:pop,1.10:line,1.75:pop,2.10:tick,2.25:tick,2.40:tick,3.05:klik,3.57:error,4.09:klik,4.85:thud"
"e03-01-kartka|8.5|0.20:pop,0.75:pop,1.15:klik,1.70:whoosh,2.40:error,3.00:whoosh,3.70:klik,4.30:whoosh,5.00:pop,5.60:whoosh,6.30:klik,7.42:thud"
"e03-02-warsztat|8.8|0.30:pop,0.60:tick,0.82:tick,1.30:whoosh,1.56:pop,2.35:whoosh,2.61:pop,3.40:whoosh,3.66:pop,4.45:whoosh,4.71:pop,5.50:whoosh,5.76:pop,6.65:whoosh,7.67:thud"
"e03-03-droga-zamowienia|9.03|0.35:pop,0.62:tick,1.55:whoosh,2.17:pop,2.97:whoosh,3.59:pop,4.39:whoosh,5.01:pop,5.81:whoosh,6.43:pop,7.28:error,7.76:thud"
"e03-04-trzy-warstwy|5.7|0.25:pop,1.05:whoosh,1.75:line,1.90:line,2.25:klik,2.95:klik,3.65:klik,4.45:thud"
"e03-05-slownik|5.9|0.20:pop,0.95:whoosh,1.11:pop,1.85:whoosh,2.01:pop,2.75:whoosh,2.91:pop,3.70:whoosh,4.05:error,4.62:thud"
"e03-06-powtarzalnosc|6.2|0.30:pop,0.56:tick,1.08:tick,2.05:whoosh,2.32:pop,3.13:klik,3.45:pop,3.89:klik,4.35:whoosh,4.80:thud"
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

# ── wersje długie ───────────────────────────────────────────────────────────
# Nie przepisujemy czasów ręcznie. Długa wersja to te same beaty spowolnione
# o `slow` i przesunięte o `lead` (karta tytułowa), więc każdy akcent wypada
# w  lead + t/slow.  Dzięki temu poprawka w scenie krótkiej propaguje się tu
# sama, a arkusz nie może się rozjechać z obrazem.
#
# scena-bazowa|slow|lead|długość-wersji-długiej
LONG=(
"e01-02-cztery-branze|0.62|3.90|19.3"
"e01-03-dostep|0.58|3.90|17.7"
"e01-04-skad-przenosisz|0.58|3.90|16.7"
"e01-05-czym-to-nie-jest|0.50|3.90|16.1"
"e03-01-kartka|0.70|3.90|18.2"
"e03-02-warsztat|0.70|3.90|18.5"
"e03-03-droga-zamowienia|0.72|3.90|18.6"
"e03-04-trzy-warstwy|0.60|3.90|16.0"
"e03-05-slownik|0.60|3.90|16.3"
"e03-06-powtarzalnosc|0.62|3.90|16.5"
"e08-01-cache|0.60|3.90|13.7"
"e08-02-moduly|0.60|3.90|13.4"
"e08-03-racja|0.60|3.90|14.1"
"e08-04-warstwy|0.65|3.90|17.5"
"e08-05-granice|0.62|3.90|16.2"
"e08-06-bariera|0.60|3.90|13.0"
"e08-07-framework|0.62|3.90|16.3"
)

# akcenty samej karty tytułowej — te same w każdej długiej wersji
TITLE_CUES="0.20:pop,2.60:whoosh"

for row in "${LONG[@]}"; do
  IFS='|' read -r base slow lead dur <<< "$row"
  if [ -n "$1" ] && [ "$1" != "${base}-long" ]; then continue; fi

  src=""
  for r in "${SCENES[@]}"; do
    IFS='|' read -r n d e <<< "$r"
    [ "$n" = "$base" ] && src="$e"
  done
  [ -z "$src" ] && { echo "  ! brak bazy dla $base"; continue; }

  shifted=$(python3 -c "
import sys
src, slow, lead = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
out = []
for ev in src.split(','):
    t, snd = ev.split(':')
    out.append('%.2f:%s' % (lead + float(t)/slow, snd))
print(','.join(out))
" "$src" "$slow" "$lead")

  build "${base}-long" "$dur" "${TITLE_CUES},${shifted}"
done

# e01-01 ma wersję długą pisaną od zera, nie przeskalowaną — własne czasy
if [ -z "$1" ] || [ "$1" = "e01-01-kopie-long" ]; then
  build "e01-01-kopie-long" "19.8" \
    "0.20:pop,2.60:whoosh,3.70:pop,4.10:tick,4.42:tick,6.55:whoosh,7.25:whoosh,8.00:pop,8.36:tick,8.68:tick,9.60:error,10.85:whoosh,11.55:whoosh,12.30:pop,12.66:tick,12.98:tick,13.90:error,14.30:error,15.35:whoosh,16.40:whoosh,17.25:klik,18.15:thud"
fi


# ── eksperymenty ────────────────────────────────────────────────────────────
# Nie da się ich wyprowadzić ze scen krótkich, bo nie mają odpowiedników —
# to nowe układy. Czasy liczone ręcznie z lead + t/slow każdej sceny.
EXP=(
"x01-split-co-kupujesz|13.0|0.20:pop,2.60:whoosh,4.18:pop,5.12:tick,6.54:whoosh,7.65:pop,8.59:tick,10.50:thud"
"x02-kinetyka-cache|14.0|0.10:pop,1.65:pop,3.05:pop,4.60:pop,6.05:pop,7.50:error,9.40:pop,10.70:thud"
"x03-zegar-szesc-godzin|15.0|0.20:pop,2.60:whoosh,4.13:klik,5.47:klik,6.81:klik,8.15:klik,9.49:klik,10.83:klik,12.60:thud"
"x04-venn-dostep|14.5|0.20:pop,2.60:whoosh,4.04:pop,5.04:pop,5.90:tick,7.19:pop,8.30:pop,9.40:pop,10.90:thud"
"x05-izo-warstwy|11.0|0.20:pop,2.60:whoosh,4.08:pop,5.03:pop,5.98:pop,6.93:pop,8.00:whoosh,9.60:thud"
"x06-kalkulator-40min|12.0|0.20:pop,2.60:whoosh,4.03:pop,5.12:klik,5.63:pop,6.72:line,8.80:pop,9.90:thud"
"x07-terminal-granice|14.0|0.20:pop,2.60:whoosh,4.45:tick,6.34:klik,7.28:klik,8.22:error,9.17:pop,10.11:klik,11.60:thud"
"x08-graf-fundament|12.0|0.20:pop,2.60:whoosh,4.08:pop,4.84:pop,5.59:pop,6.35:pop,7.20:line,8.50:pop,10.00:thud"
"x09-miernik-trafnosci|12.0|0.20:pop,2.60:whoosh,4.03:tick,5.15:line,6.53:pop,8.24:error,9.60:thud"
"x10-rozlewanie-modulu|14.0|0.20:pop,2.60:whoosh,5.00:whoosh,6.23:whoosh,7.45:whoosh,8.55:error,9.83:thud,11.50:pop"
)

for row in "${EXP[@]}"; do
  IFS='|' read -r name dur events <<< "$row"
  if [ -n "$1" ] && [ "$1" != "$name" ]; then continue; fi
  build "$name" "$dur" "$events"
done

echo "── gotowe"
