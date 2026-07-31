# Ekran produktu w reklamach renderujemy z HTML (HyperFrames), nie generujemy modelem

**Data:** 2026-07-30
**Status:** ✅ wdrożone — spoty 10–12 w `projects/adresflow/final/`

## Problem

Trzy nowe spoty (księga wieczysta, wycena, kreator oferty) opisuje plan
[`projects/adresflow/ai/plans/2026-07-30-reklamy-kw-wycena-oferta.md`](../plans/2026-07-30-reklamy-kw-wycena-oferta.md).
Plan zatrzymał się na jednym blokerze: **te funkcje są ekranowe**. Nie ma w nich
transformacji obrazu (przed → po), która sprzedaje dotychczasowe spoty; dowodem
jest to, co dzieje się na ekranie produktu. A ekranu produktu nie mieliśmy:

- **nie ma ani jednego nagrania ekranu** — nikt ich nie zrobił;
- **nie da się ich wygenerować modelem wideo** — modele renderują UI jako
  nieczytelną papkę, a polskie napisy jako bełkot (zmierzone przy innych ujęciach,
  patrz [`2026-07-30-reklamy-higgsfield-rzut-3d.md`](2026-07-30-reklamy-higgsfield-rzut-3d.md)).

## Decyzja

**Ekrany produktu odtwarzamy jako kompozycje HTML i renderujemy do wideo
przez HyperFrames** (`projects/adresflow/screens/`), zamiast czekać na nagrania ekranu albo
generować ekran modelem.

Trzy osobne projekty — `kw/`, `wycena/`, `oferta/` — każdy ze wspólnym arkuszem
`assets/app.css`, w którym tokeny są przeniesione 1:1 z
`adresflow-v2/apps/web/src/styles/legacy.css` (tło `#0a0b10`, akcent `#8b5cf6`, magenta
`#d946ef`, font Poppins). Layouty odwzorowują realne komponenty:
`KsiegaWieczystaCard`, `StatCard` + `Histogram` z `WycenaScreen`, stepper i krok 4
z `OfferWizardPage`.

Wyjście: `projects/adresflow/build/screen-{kw,wycena,oferta}.mp4` (1080×1920, 30 fps), wpięte do
`SHOTS` w `story.py` jako ujęcia `ekran-kw`, `ekran-wyc`, `ekran-of`.

### Dlaczego tak

| | nagranie ekranu | generacja modelem | **HTML → wideo** |
|---|---|---|---|
| Czytelność UI | pełna | papka | **pełna** |
| Polskie napisy | poprawne | bełkot | **poprawne** |
| Koszt zmiany danych | ponowne nagranie | ponowna generacja | **edycja HTML, 0 kredytów** |
| Dostępność dziś | brak | — | **jest** |

To ta sama zasada, na której stoi cały pipeline reklam: **kredyty idą wyłącznie
na to, czego nie da się zrobić lokalnie**. Ekran produktu okazał się rzeczą,
którą da się zrobić lokalnie — i to lepiej niż generatorem.

**Świadomy kompromis:** to rekonstrukcja UI, nie zapis z produkcji. Dane na
ekranach są przykładowe (Katowice Śródmieście, KW `SL1S/00099246/5`, mediana
12 480 zł/m²). Layout jest wierny komponentom, ale gdy UI się zmieni,
kompozycje trzeba zaktualizować ręcznie — nic tego nie pilnuje.

## Pułapki, które kosztowały czas

1. **`check` odrzuca kolor `--text-3` z aplikacji.** `#6b7a92` na `--elevated`
   daje 3,77:1, a bramka wymaga 4,5:1. W kompozycjach jest rozjaśniony do
   `#8593ab` (4,8:1). To nie jest rozjazd z designem produktu — w kadrze wideo
   oglądanym na telefonie ten kolor i tak był za ciemny.
2. **Przewijanie treści pod paskiem aplikacji zgłasza `text_occluded`.** Bramka
   liczy nachodzenie na prostokątach, ignorując `overflow: hidden`. Rozwiązanie:
   albo pasek jedzie razem z treścią (kw, wycena), albo ruch siedzi w samym
   elemencie, a chrome stoi (oferta).
3. **Pozycja wyjściowa przez `tl.set(…, 0)`, nie przez CSS `transform`.**
   Inline `transform: translateY()` + tween na `y` to `gsap_css_transform_conflict`
   — GSAP nadpisuje cały transform i element skacze.
4. **Kroki kreatora przełączane przez `translateX` na pasku, nie przez `display`.**
   Animowanie `display` łamie determinizm renderu.

## Efekt uboczny: naprawiony klatkaż w `story.py`

Przy montażu wyszło, że `compose()` produkował **VFR** — obraz wychodził dłuższy
od lektora (26,5 s przy 20,3 s głosu). Napisy są wypalane na sztywnych czasach,
więc rozjeżdżały się ze słowami, a endcard puchł z 3,2 s do ponad 7 s.

Przyczyna: kilkanaście wejść `-loop 1` (chrome + linia napisów na frazę) i brak
jawnego klatkażu na wyjściu. Fix: `-r 30 -fps_mode cfr -t {total}` w `compose()`.

**To dotyczyło też dziewięciu wcześniejszych spotów** — każdy miał ok. 0,6 s
naddatku. Spoty 01–09 w `projects/adresflow/final/` nie zostały przebudowane; przy najbliższej
zmianie któregoś warto puścić `story.py` ponownie.

## Czego NIE zrobiliśmy — brak eksportu PDF

Zadanie brzmiało „oferta PDF jednym kliknięciem". **Produkt nie ma eksportu do
PDF.** Krok 4 kreatora (`adresflow-v2/apps/web/src/pages/OfferWizardPage.tsx:731-763`)
eksportuje: *Kopiuj*, *Pobierz .txt*, *Podgląd strony*, *Pobierz stronę HTML*.

Spot 12 mówi więc **„gotowe ogłoszenie do wysłania"**, a nie „PDF", i pokazuje
realny rząd przycisków eksportu. Reklama obiecująca PDF byłaby nieprawdziwa.
Do decyzji właściciela: dopisać eksport PDF do produktu i wtedy przenumerować
copy, albo zostać przy obecnym sformułowaniu.

## Powiązane

- **Instrukcja budowania kolejnych ekranów: `projects/adresflow/screens/README.md`** —
  pętla pracy, skala typografii pod 9:16, wzorce choreografii, wpięcie do `story.py`
- Plan: [`projects/adresflow/ai/plans/2026-07-30-reklamy-kw-wycena-oferta.md`](../plans/2026-07-30-reklamy-kw-wycena-oferta.md)
- Poprzedni ADR o produkcji reklam: [`2026-07-30-reklamy-higgsfield-rzut-3d.md`](2026-07-30-reklamy-higgsfield-rzut-3d.md)
- Pipeline: `projects/adresflow/tools/README.md`, indeks spotów: `projects/adresflow/final/README.md`
- Pamięć: `.ai/memory/ekran-produktu-hyperframes.md`,
  [[pipeline-montazu]], [[copy-i-hook]], [[higgsfield-mcp-limity]]
