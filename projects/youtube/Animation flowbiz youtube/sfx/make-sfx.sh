#!/bin/bash
# Syntetyczna paczka SFX do wstawek — generowana ffmpegiem, zero licencji, zero kredytów.
# Wszystko mono 48 kHz, krótkie, celowo dyskretne: mają podbijać ruch, nie zagłuszać narracji.
#
#   ./make-sfx.sh          → sfx/*.wav
set -e
cd "$(dirname "$0")"

gen () { # nazwa, wyrazenie, dlugosc
  ffmpeg -y -v error -f lavfi -i "aevalsrc=${2}:d=${3}:s=48000" -ac 1 "$1.wav"
  echo "  ✓ $1.wav (${3}s)"
}

echo "── generuję paczkę SFX"

# POP — element wskakuje sprężyną (węzeł, karta, pigułka)
gen pop "0.45*sin(2*PI*(300+520*exp(-30*t))*t)*exp(-16*t)" 0.28

# KLIK — wciśnięcie przycisku, pojedyncze zdarzenie
gen klik "0.40*(random(0)*2-1)*exp(-260*t)" 0.06

# TICK — licznik, wpisywanie tekstu, drobne odhaczenie
gen tick "0.22*(random(1)*2-1)*exp(-420*t)" 0.035

# WHOOSH — przejazd kamery (pan), przesunięcie ekranu
gen whoosh "0.30*(random(2)*2-1)*sin(PI*t/0.55)*sin(PI*t/0.55)" 0.55

# LINE — dorysowywanie linii między stacjami
gen line "0.18*sin(2*PI*(180+300*t/0.9)*t)*sin(PI*t/0.9)" 0.90

# THUD — puenta, ciężkie lądowanie słowa
gen thud "0.55*sin(2*PI*(70+40*exp(-18*t))*t)*exp(-9*t)" 0.55

# ERROR — coś znika, coś się nie udało (czerwone akcenty)
gen error "0.40*sin(2*PI*(220-90*t/0.4)*t)*exp(-7*t)" 0.40

echo "── gotowe"
ls -la *.wav
