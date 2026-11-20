# Noc 20→21.11: dogrywki 06–43 nagrane ponownie (pogłos)

**Data:** 2026-11-20
**Status:** ✅ wdrożone (wstawki, 4 odcinki, 8 shortów); muzyka z ElevenLabs — czeka na wybór MK
**Poprzedni etap:** [2026-11-16-noc-dogrywki.md](2026-11-16-noc-dogrywki.md)

## Problem
MK po odsłuchu próbek: „dziwny pogłos” na wszystkich wstawkach poza A1. Pomiar — czas spadku o 20 dB po końcu
frazy (okna 10 ms, mediana z pełnego pliku): sesja z kamerą 8.10 i pierwszy plik dogrywek (01–05) **60 ms**,
drugi plik (06–43) **130–140 ms** równo od pierwszej sekundy. Ten sam QuickTime, 9 minut różnicy → zmienione
ustawienie mikrofonu (MK: „widocznie ustawienia na mikrofonie mogły mi się zmienić”). Obróbka nie tworzyła pogłosu,
ale jednoprzebiegowy `loudnorm` go uwypuklał (dynamiczne wzmocnienie ogonów, tło −81 → −60 dB).

Odrzucone: czyszczenie ffmpeg (ekspander + EQ skraca ogony do 60 ms, pogłos w słowach zostaje) i DeepFilterNet
(wymaga Rusta). MK wybrał dogranie.

## Decyzja
- Nagranie 20.11 (`raw/2026-11-16-dogrywki-audio/dogrywki-2026-11-20-nowe-glosowe-nagranie.aifc`, 60 ms) zastępuje
  drugi plik 16.11 (przeniesiony do Kosza). Oś sklejki: 01–05 bez zmian (0–63,68 s), 06–43 od 65,68 s.
- `dubs_ingest`: loudnorm dwuprzebiegowy, liniowy.
- `dubs_split`: okna z ciszy w sygnale (czasy Whispera przesunięte, kwestie bez przerw); lista vault
  `2026-11-20-do-dogrania-ponownie.md` (10: „producent” zamiast „hurtownia”).
- 15: dubel „będzie o tym” — sklejka 126,58 | 128,30 (ostatnie pełne podejście), sprawdzona Whisperem sklejki.
- ins-g27: podpis „zupełnie niepotrzebne” jak w nagraniu.

## Wynik
- verify: 25 wstawek `ok`, 2 `check` fałszywe (pełne zdania, inne słowa niż lista: „wygląda/wyglądało”).
- Odcinki oferty, meble, pamiątki, 8 wdrożeń + 8 shortów przebudowane; rozdziały bez zmian.
- Mastery 1440p: tailnet `pliki/odcinki-2026-11-21/`, rolki `pliki/rolki-2026-11-21/`.

## Pułapki
- `ep-marpasz` zatrzymuje `assemble_episode` („cięcie END ucina ostatnie słowo”) — niezależne od dogrywek;
  marpasz, vacuactiv i moduł nie mają wstawek z dogrywek, ich mastery z 10.11 zostają.
- Muzyka (ElevenLabs, `music/2026-11-20-elevenlabs/`): jingiel 20 s ×4, intro pod głos 29 s (B ciepłe ×2, C deep
  focus ×4). Licencja komercyjna tylko z płatnego planu ElevenLabs. Podmiana = `package.py --finalize-only` + sklejki.
