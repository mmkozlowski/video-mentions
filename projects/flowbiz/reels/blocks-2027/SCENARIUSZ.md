# Rolka 2027 — „System składasz z klocków"

**Format:** rolka/reklama 9:16, 1080×1920, ≤ 45 s (liczone po tempie 1,05×, WYTYCZNE §9)
**Twarz:** Mateusz na kamerze, gadana głowa — twarz u góry, panel na dole (układ rolki z `projects/recording-library`)
**Odbiorca:** właściciel firmy 10–100 osób, produkcja i handel B2B
**Status:** koncepcja do akceptacji · 2026-11-06
**Specyfikacja nowej scenki:** [`../../screens/block-tower/SPEC.md`](../../screens/block-tower/SPEC.md)
**Warianty (A/B/C, rolki tekstowe):** [`WARIANTY.md`](WARIANTY.md) — ten dokument to pełna wersja wariantu A z Mateuszem na kamerze
**ADR:** [`../../ai/decisions/2026-11-06-rolka-klocki-2027.md`](../../ai/decisions/2026-11-06-rolka-klocki-2027.md)

## Oś kreatywna

To samo słowo, dwa przeciwne znaczenia — i to jest hak:

- **Kiedyś klocek = ból.** Każde nowe wymaganie to kolejne narzędzie dorzucone na stos.
  Każde z osobna jest topowe, a razem i tak się wali, bo żadne nie gada z poprzednim
  (karta vaulta `2026-05-06-kazdy-system-to-kolejny-klocek`, własne słowa Mateusza ze spotkania:
  „dokładamy kolejne klocki").
- **W 2027 klocek = odpowiedź.** Mateusz mówi coś pozornie odwrotnego: składaj system z klocków.
  Różnica jest jedna: klocek stoi na fundamencie (Open Mercato), więc gada z resztą.
- **Szczera granica (anty-fanboy):** klocków da się nakłaść za dużo. Wtedy schodzimy do kodu
  (karta `2026-06-17-workflow-klocki-dziala-od-reki`).

Głos: empathic contrarian. Najpierw uznanie („każde z osobna świetne"), potem twardo („i tak się wali").

## Scenariusz sekunda po sekundzie

Legenda kolumny „Źródło":
**NOWE** — scenka do zbudowania (`block-tower`, spec obok) · **ISTN.** — plik z `projects/flowbiz/final/`
z sekundą cięcia · **UKŁAD** — gotowy układ z [`KATALOG-UKLADOW.md`](../../../../KATALOG-UKLADOW.md)
(nowa treść, istniejący wygląd).
Czasy rolki są orientacyjne (tempo Mateusza 4,2–4,9 sylaby/s × 1,05). Ostateczne granice wyznacza
transkrypcja dubla, nie ta tabela (pamięć `nagranie-z-promptera-nie-trzyma-sie-tekstu`).

| Czas rolki | Mateusz mówi do kamery | Na ekranie | Źródło (plik · sekunda cięcia) | Do dorobienia |
|---|---|---|---|---|
| **0,0–3,0** | „Każdy nowy system w firmie to kolejny klocek." | Twarz, ruch od 1. klatki (zoom). Hook na twarzy, jako nagłówek: **„Kolejny system = kolejny klocek"** + mała ikona klocka. Pod hookiem nic więcej. | UKŁAD `hook` | treść hooka + ikona klocka (z `kit.js`) |
| **3,0–7,8** | „Bierzesz najlepsze narzędzia na rynku. Jedno. Drugie. Kolejne…" | Twarz u góry. W dolnym panelu narzędzia spadają na stos — krzywo, każde innej szerokości, bez fundamentu. Nazwy tylko tekstem. | **NOWE** `block-tower-9x16-alpha.mov` · **0,4–3,8** | scenka; nazwy narzędzi — patrz „Otwarte" |
| **7,8–10,4** | „Tylko że żadne nie gada z poprzednim." | Panel: stos się chwieje, na stykach czerwone „×" (brak połączenia). Napisy znikają — obraz mówi to samo. | **NOWE** `block-tower-9x16-alpha.mov` · **3,8–4,6** | — |
| **10,4–12,0** | „I w końcu to się wali." | Panel: wieża wybucha, klocki rozlatują się i gasną. Twarz zostaje — reakcja Mateusza jest częścią ujęcia. | **NOWE** `block-tower-9x16-alpha.mov` · **4,6–5,4** | — |
| **12,0–17,4** | „Dlatego w dwa tysiące dwudziestym siódmym powiem ci coś odwrotnego: składaj system z klocków." | **Rama 2027.** Błysk → plansza na pełny ekran, głos pod spodem: nadtytuł **„2027"**, przekreślone **„klocek = problem"** → **„klocek = odpowiedź"**. | UKŁAD `beat` / `strike` | treść planszy (3 krótkie elementy) |
| **17,4–21,9** | „Tylko klocek musi na czymś stać. U nas tym fundamentem jest Open Mercato." | Twarz wraca. Panel: z dołu wjeżdża pomarańczowy fundament **„Open Mercato"**, szerszy od wszystkiego nad nim, z poświatą. | **NOWE** `block-tower-9x16-alpha.mov` · **5,6–6,9** (zostaw ogon do 7,0 na oddech) | — |
| **21,9–25,5** | „Na nim dokładamy to, czego potrzebuje twoja firma…" | Panel: pierwsze moduły wskakują równo na fundament (Klienci, Oferty). | **NOWE** `block-tower-9x16-alpha.mov` · **6,4–8,2** | — |
| **25,5–29,0** | „…oferty, magazyn, portal dla klienta, asystenta AI." | Pełny ekran, prawdziwe ekrany systemu — każde wymienione słowo to jego okno (etykieta nad oknem = to, co pada). | **ISTN.** `system-moduly-przelot-9x16.mp4` · **3,0–3,9** (Oferty) + **5,2–6,1** (Magazyn) + **7,4–8,3** (Portal klienta) + **9,6–10,5** (Asystent AI) | — |
| **29,0–32,9** | „I każdy nowy klocek gada z resztą. Bo stoi na tym samym." | Twarz wraca. Panel: wieża w stanie po przelocie (stoją już 3 moduły), wskakują ostatnie, światło biegnie z fundamentu w górę przez wszystkie — **jeden mocny moment**. Nad szczytem kontur „+ Twój moduł". | **NOWE** `block-tower-9x16-alpha.mov` · **8,2–12,1** | — |
| **32,9–34,3** | „W szwalni przygotowanie oferty…" | Twarz, sam napis. | nagranie | — |
| **34,3–37,6** | „…zeszło z czterdziestu minut do pięciu–dziesięciu." | Pełny ekran: tarcza 40 → 5–10, hit z falą, „Oferta w 5–10 minut", „Szwalnia · wdrożenie flowbiz". Cięcie **przed** logo — logo dostaje plansza końcowa. Napisy znikają (karta mówi to samo). | **ISTN.** `stoper-40-do-5-9x16.mp4` (MP4, nie alfa) · **1,2–4,9** | — |
| **37,6–41,5** | „Czy da się nakłaść za dużo klocków? Da się. Wtedy schodzimy do kodu." | Sama twarz, napisy. Bez grafiki — to zdanie ma brzmieć jak przyznanie się, nie jak slajd. | nagranie | — (**pierwsze do wycięcia**, jeśli dubel wyjdzie za długi) |
| **41,5–45,0** | „Napisz w komentarzu, ile systemów masz dziś w firmie." | Od ~42,5 plansza końcowa: duże logo flowbiz, pod nim pytanie z CTA. W wersji reklamowej przycisk „Umów rozmowę" + flowbiz.pl. | UKŁAD `endcard` | tekst CTA (organic / reklama) |

**Rytm form:** hook → panel (wieża) → pełny ekran (2027) → panel → pełny ekran (przelot) → panel →
pełny ekran (stoper) → twarz → endcard. Między dwoma pełnymi ekranami zawsze wraca twarz (KATALOG, „Jak dobierać").
Uderzenie co 5–8 s — w rolce szybciej niż 15–30 s z odcinka, bo cały film ma 45 s.

**Strefy pionu:** cała nowa grafika w polu x 140–940, y 980–1640 (panel) — poza górnymi 230 px,
prawą kolumną 130 px od y 1100 i dolnymi 260 px (pamięć `pion-strefy-zakazane-reels`). Nic nie
wchodzi na twarz, w tym spadające klocki (spec: w alfie klocki nie lecą z góry kadru).

**Muzyka i dźwięk:** jak w WYTYCZNYCH §9 (biblioteka z licencją, ~25 dB pod głosem). Jeden
akcent dźwiękowy warto dać na wybuch wieży (10,4–12,0) i na impuls światła (~31 s).

## Tekst do promptera

Pisany do mówienia, nie do czytania. Pauzy = nowa linia. To jest **intencja** — Mateusz może
improwizować, dubel wybieramy z transkrypcji. Jedynej liczby (40 → 5–10) nie zmieniać.

```
Każdy nowy system w firmie to kolejny klocek.

Bierzesz najlepsze narzędzia na rynku.
Jedno. Drugie. Kolejne…

Tylko że żadne nie gada z poprzednim.

I w końcu to się wali.

Dlatego w dwa tysiące dwudziestym siódmym
powiem ci coś odwrotnego:
składaj system z klocków.

Tylko klocek musi na czymś stać.
U nas tym fundamentem jest Open Mercato.

Na nim dokładamy to, czego potrzebuje twoja firma:
oferty, magazyn, portal dla klienta, asystenta AI.

I każdy nowy klocek gada z resztą.
Bo stoi na tym samym.

W szwalni przygotowanie oferty
zeszło z czterdziestu minut do pięciu–dziesięciu.

Czy da się nakłaść za dużo klocków? Da się.
Wtedy schodzimy do kodu.

Napisz w komentarzu, ile systemów masz dziś w firmie.
```

Wariant CTA do reklamy (zamiast ostatniej linii): „Zobacz, jak to wygląda u nas — flowbiz.pl."

**Na planie:** jedno ujęcie ciągłe, ten sam strój od początku do końca (w razie dograń).
Twarz w górnej połowie kadru z zapasem nad głową — dolne ~45 % kadru przykryje panel z wieżą.
Lepiej 3 pełne duble niż sklejanie z kawałków (WYTYCZNE §2).

## Zgodność z twardymi zasadami treści

| Zasada | Jak spełniona |
|---|---|
| Jedyna liczba 40 min → 5–10 min | pada raz, ze słowami „przygotowanie oferty" i „szwalnia"; żadnych innych liczb, procentów, wyników. „2027" to rok w ramie, nie wynik. Licznik „ile systemów masz" pytamy u widza, sami żadnego nie podajemy |
| Żadnych prawdziwych klientów | anegdota ze spotkania **nie weszła** do tekstu (klientka jest prawdziwa, a „pięć systemów dla jednej paczki" to i liczba, i rozpoznawalny szczegół). Zostały tylko własne słowa Mateusza („dokładamy kolejne klocki"). Na ekranach Pracownia Bałtyk / Nordtex, jak w makietach |
| Narzędzia tylko tekstem, bez logotypów | nazwy na klockach to tekst + ogólne piktogramy z `kit.js`, jak w klocku `integracje-w-jeden-system` |
| Po polsku | tak |
| AI Act art. 50 ust. 4 | **cały materiał bez AI**: prawdziwe nagranie Mateusza + grafika z HTML + muzyka z biblioteki. Oznaczenie nie jest potrzebne. **Jeśli** ktoś zechce dorzucić przebitkę z generatora (np. wybuch wieży z Higgsfielda), avatar albo syntetyczny głos — **oznaczenie wraca** (przełącznik na platformie + znak u góry przez ~4 s). Nie proponuję tego: lip-sync po polsku nie działa (pamięć `lipsync-ai-nie-dziala-pl`), a wybuch w HTML wygląda spójnie z resztą |
| Reklama | wersja płatna dostaje osobne oznaczenie „materiał sponsorowany" — to inny obowiązek niż AI |

## Otwarte — do decyzji Mateusza

1. **Nazwy narzędzi na walącej się wieży.** Z notatki: „wziąć topowe narzędzia… Brix nie wystarcza
   i tak wybucha… albo inaczej, że tylko Brix". Potwierdzone: to treść (wieża narzędzi, która się wali).
   **Niepotwierdzone: czym są „Brix" i „RP"** — nie zgaduję. Do czasu odpowiedzi wieża dostaje zestaw
   już zaakceptowany w klocku 4: Excel, Gmail, wFirma, BaseLinker, Allegro, Make / n8n. Brix i RP
   wchodzą jako dwa klocki po potwierdzeniu pisowni (podmiana tablicy w `scene.html`, zero przebudowy).
2. **Wariant „tylko Brix"** z tej samej notatki — jeśli to znaczy „jedno narzędzie robi za wszystko
   i też pęka", to inna scena (jeden klocek, który rośnie i się rozsadza). Nie projektuję, dopóki nie wiem.
3. **Hook na ekranie:** rekomenduję „Kolejny system = kolejny klocek". Alternatywa bólowa:
   „Twoje systemy nie gadają ze sobą?" — mocniejsza, ale to zdanie pada dopiero w 8. s
   (WYTYCZNE §4: hook mówi tylko to, co pada w nagraniu — tu pada, tylko później).
4. **Rama 2027** — rozumiem jako planszę `strike` z rokiem w nadtytule (12–17 s). Jeśli „rama"
   miała znaczyć stały element przez cały film (np. znaczek „2027" w rogu) — powiedz, dołożę;
   uwaga, że góra kadru to strefa zakazana, a znaczek musi wejść po hooku.
5. **Granica „da się nakłaść za dużo"** (37,6–41,5) — zostawiam, bo to głos Mateusza.
   Jeśli dubel wyjdzie powyżej 45 s, wylatuje pierwsza.
