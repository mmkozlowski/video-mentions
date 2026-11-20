# Noc 20→21.11: dogrywki 06–43 nagrane ponownie (pogłos)

**Data:** 2026-11-20
**Status:** ✅ wdrożone (wstawki, 4 odcinki, 8 shortów, muzyka i efekty ElevenLabs)
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

## Druga część nocy (21.11, po odsłuchu MK)

1. **Trzask w dogrywkach** („Pełna historia… trzeszczy”): loudnorm `linear=true` po cichu przechodził w dynamiczny
   z ogranicznikiem (potrzebne +16 dB, szczyty pozwalały na +9,4). `dubs_ingest`: kompresja ratio 3 + stałe
   wzmocnienie do −16 LUFS albo −1,5 dBTP → −18,7 LUFS, bez ogranicznika. Pamięć: `.ai/memory/loudnorm-po-cichu-dynamiczny.md`.
2. **Muzyka MK** (`assets/music/`): jingle-2 → ins-hello-offers / ins-lead-*; jingle-przedstawienie → ins-intro;
   tlo2 → pozostałe wstawki odcinków. Treść odcinków zostaje na Way Back Home (podkłady 29 s — pętla dawałaby dziury);
   ins-mid-long (50 s) ma tlo2 tylko przez pierwsze ~29 s.
3. **Shorty z ciągłym podkładem** („w 0:54 ucinasz muzykę”): `assemble_short` skleja surowe rendery i kładzie jeden
   podkład na całość. Pamięć: `.ai/memory/muzyka-ciagla-w-sklejce.md`.
4. **Efekty dźwiękowe** (`assets/sfx/`, ElevenLabs): `package.sfx_plan` — efekt na wejście planszy wg typu
   (burst → uderzenie, slam → puenta, strike → glitch, stat → licznik, chat → powiadomienie, list/title/quote/logos → pop,
   kinetic/broll/slate/compare → whoosh, inne makiety → przycisk), maks. 1 na 0,8 s, szczyt −14…−22 dBFS w surowym
   miksie. Działa też przy `--finalize-only` (momenty z `Composition.build()` bez renderu obrazu); `sfx.json` obok render.mp4.
5. **„5 MIN” we wstępie oferty** wskakiwało na pierwsze „w” („działają w normalnych…”) i ucinało napis — kotwica `w#2`.

Pułapka skryptu: `ffmpeg` w pętli `while read` zjada stdin (resztę listy) — zawsze `-nostdin`.
