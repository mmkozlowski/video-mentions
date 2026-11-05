# Odcinki YouTube z przerywnikami o usługach, poprawki cięć i plansz (noc 04→05.11)

**Data:** 2026-11-05
**Status:** ✅ wdrożone (gałąź `mmkozlowski/noc-odcinki-0411`), pliki w `final/samples/*--with-inserts.mp4`

Rozszerza: [Starsze odcinki kanału](2026-10-11-starsze-odcinki-kanalu.md). Plan i dziennik nocy:
[`ai/plans/2026-11-04-noc-odcinki.md`](../plans/2026-11-04-noc-odcinki.md).

## Problem

Mateusz 04.11: odcinki mają być pełnoprawnymi filmami na YouTube (nie reklamami) z wstawkami, które
już nagrał — przedstawienie się, zaproszenie na konsultację, zamknięcie. Do tego: wyłapać urwane
zdania i braki w planszach, a w odcinku o Marpaszu dać logotypy Apilo/BaseLinkera i ekrany
„przypominające Apilo” na danych przykładowych.

## Decyzja

1. **Przerywniki jako klipy biblioteki** z `openmerxat-wstawki.mov` (źródło `inserts`):
   `ins-intro`, `ins-mid`, `ins-mid-long` (z „Open Mercato przetworzy to na specyfikację” — tylko
   odcinki o OM), `ins-outro`. Zdanie „u Ciebie w filmie jest dokładnie tak samo” pominięte.
2. **Sklejanie po renderze**, nie w storyboardzie: `assemble_episode.py` tnie gotowy youtube-F
   w przerwie po końcu zdania (czasy słów z transkrypcji renderu), wkleja opakowane wstawki,
   przelicza rozdziały (`data/assembly.json` → Studio). Odcinki zostają jednym storyboardem.
3. **Kontrola transkrypcją gotowych plików** zamiast porównania z tekstem oczekiwanym — tekst
   z surówki ma dziury i przesunięcia.
4. **Plansze w lukach > 25 s** tylko z istniejących typów i wyłącznie z treści, którą Mateusz mówi
   w tym miejscu. Makieta `apilo` (lista zamówień, „Wyślij przesyłkę” z 4 komentarzami) — kolory
   i układ z panelu, dane zmyślone; prawdziwe zrzuty poza repo.

## Pułapki

- Czasy słów surówki przesunięte o 0,5–1,5 s → [[ciecie-wstawek-po-renderze-nie-po-surowce]].
- `*` w tekstach storyboardu wyróżnia od słowa → [[storyboard-gwiazdka-wyroznia-slowo]].
- Składanka z liczbowymi kotwicami (ep-8-wdrozen: plansze rozdziałów) rozjeżdża się przy zmianie
  długości części — po wydłużeniu klipu przelicz liczby w storyboardzie.
- Rozdziały kończące się w pół zdania w składance: nowe klipy `*-full` tylko dla składanki, żeby nie
  ruszać rolek i reklam miejskich zbudowanych na starych.

## Aktualizacja 05.11 rano — wstawki jako głos na planszach, jingiel

Wstawki nagrane innym ujęciem i w innym pomieszczeniu odstawały obrazem i barwą głosu. Decyzja
Mateusza: **w odcinku zostaje tylko jego głos, obraz to plansze** (`voice_only`), przedstawienie bez
„to nie jest odcinek sponsorowany”. Barwa wyrównana korekcją (`voice_filter`), bez ponownego wejścia
muzyki (`music_intro: false`). Paski z `Miniaturki Youtube.mp4` jako maska L (pasek boczny + dolny CTA) idą
na planszach zamknięcia — `assemble_episode.py`, `BARS_*`. Pierwsza wersja (jingiel od pierwszej sekundy)
odrzucona przez Mateusza: „nie może być od pierwszej sekundy — ewentualnie przy końcu”.

**Pułapka:** przenikanie (`xfade`) pomniejszonego okna w pełną klatkę daje podwójny obraz, bo te same
klatki leżą w dwóch geometriach. Paski mają zjeżdżać nad niezmienionym obrazem, nie obraz się rozszerzać.
