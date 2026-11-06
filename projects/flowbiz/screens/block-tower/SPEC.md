# Klocek 6: `block-tower` — wieża klocków rośnie (specyfikacja)

**Status:** ✅ zbudowane 07.11.2026 (pierwsza wersja, 3 formaty) — nazwy narzędzi w fazie „przed" wciąż do potwierdzenia
**Data:** 2026-11-06
**Do czego:** rolka „System składasz z klocków" — [`../../reels/blocks-2027/SCENARIUSZ.md`](../../reels/blocks-2027/SCENARIUSZ.md)
**Wzorzec techniczny:** `../stoper-40-do-5/scene.html` (jedna scena, układy z klas `fmt-land`/`fmt-port`/`alpha-mode`, jedna pauzowana timeline)

Grafika z HTML, nie treść AI — nie wymaga oznaczenia z art. 50 ust. 4 (w odróżnieniu od
grafik GPT w rolkach tekstowych, które są tylko szkicem kierunku).

## Co pokazuje

Dwie wieże na jednym obiekcie, jedna po drugiej:

1. **Przed (klocek = ból):** narzędzia spadają na stos bez podstawy — krzywo, każde innej
   szerokości, styki się nie łączą. Stos chwieje się i **wybucha**.
2. **2027 (klocek = odpowiedź):** z dołu wjeżdża fundament **Open Mercato**, na nim równo
   zatrzaskują się moduły — **te same pięć co w klocku 3** (`system-moduly-przelot`):
   01 Klienci · 02 Oferty · 03 Magazyn · 04 Portal klienta · 05 Asystent AI. Jeden impuls
   światła przechodzi z fundamentu przez wszystkie moduły. Nad szczytem kontur „+ Twój moduł" —
   wieża rośnie dalej.

## Fundament vs moduł — jak się różnią wizualnie

| Cecha | Fundament „Open Mercato" | Moduł (01–05) | Narzędzie „przed" |
|---|---|---|---|
| Wypełnienie | **pełny pomarańcz** `#FF6A1A → #FF8A3D` (gradient pionowy) — jedyny pomarańczowy blok w kadrze | karta `#1D1D22`, ramka 2 px `#3A3A43` | karta `#16161A`, ramka 2 px `#B8443C` (przytłumiona czerwień) |
| Szerokość (pion, alfa) | **800 px** — najszerszy, wystaje 30 px z każdej strony | 740 px, wszystkie równe | 380–560 px, każde inne |
| Wysokość | **140 px** — 1,8× moduł | 78 px | 72–96 px |
| Tekst | „Open Mercato" 54 px / 800, kolor `#160A03` (ciemny na pomarańczu — biały nie przechodzi kontrastu); pod spodem mono 20 px: „dane · uprawnienia · workflow · API" | numer mono `01` (`#8E8E98`) + nazwa 40 px / 700 `#F5F5F7` | nazwa narzędzia 34 px / 700 `#F5F5F7` + ogólny piktogram z `kit.js` (bez logotypów) |
| Akcent | poświata pod spodem `0 30px 80px rgba(255,106,26,.45)`, 4 zaczepy na górnej krawędzi (prostokątne, nie okrągłe — nie LEGO) | pasek 6 px `#FF6A1A` z lewej, zaczep wpada w zaczep poniżej | brak zaczepów, styki przesunięte |
| Ruch | wjeżdża z dołu, stoi nieruchomo, nie przechyla się | spada i **zatrzaskuje się** (sprężyna), zero przechyłu | spada, odbija się, przechyla, w końcu leci |
| Połączenie | źródło „kręgosłupa" — pionowej linii 3 px `#FF6A1A` po prawej wewnętrznej krawędzi wieży | kręgosłup rośnie przez każdy moduł | między narzędziami czerwone „×" na stykach |

Zasada czytelności: **pomarańcz = fundament i połączenie**, nic innego nie dostaje pełnego
pomarańczu. Widz ma w ułamku sekundy zobaczyć, na czym wszystko stoi.

## Oś czasu (14,0 s, 30 fps)

| Czas | Co się dzieje | Easing / szczegół |
|---|---|---|
| 0,0–0,4 | tło (w wersji pełnej), linia podłogi — przerywana, szara: „ziemia bez fundamentu" | `power2.out` |
| 0,4 / 1,0 / 1,6 / 2,2 / 2,8 / 3,4 | sześć narzędzi spada na stos (co 0,6 s). Przesunięcia x: 0, +34, −22, +48, −40, +62 px; obrót: 0°, 1,5°, −2°, 3°, −3,5°, 5° — stałe tablice, zero losowości | spadek `power2.in` 0,35 s, odbicie `back.out(2)` 0,25 s |
| od 1,6 | przy każdym lądowaniu czerwone „×" na styku z poprzednim (0,3 s błysku, zostaje przygaszone) | — |
| 3,8–4,6 | stos się chwieje: obrót całości ±2,5°, rosnąca amplituda | `sine.inOut`, `repeat: 3`, `yoyo` (skończone) |
| **4,6–5,4** | **wybuch:** narzędzia rozlatują się (x ±300–500, y w dół, obrót do ±40°), gasną do 0; czerwony błysk winiety 0,3; wstrząs kadru 3 px | `power3.out` |
| 5,4–5,6 | pusto, sama podłoga | oddech przed zmianą znaczenia |
| **5,6–6,4** | **fundament** wjeżdża z dołu (y +120 → 0), fala uderzeniowa na podłodze w 6,2, poświata narasta | `expo.out` 0,8 s |
| 6,4 / 7,3 / 8,2 / 9,1 / 10,0 | moduły 01–05 spadają z −160 px i zatrzaskują się; w chwili zatrzaśnięcia kręgosłup dorasta, a impuls 0,35 s biegnie po nim w dół do fundamentu | `back.out(1.6)` 0,45 s |
| **10,8–11,5** | **jeden mocny moment:** impuls światła z fundamentu w górę przez cały kręgosłup; ramka każdego modułu po kolei rozbłyska pomarańczem (stagger 0,1 s); fundament pulsuje | `power2.inOut` |
| 11,6–14,0 | nad szczytem kontur „+ Twój moduł" (przerywana ramka, `#A1A1AA`) oddycha (`repeat: 2`); kamera powoli dojeżdża (skala 1 → 1,03 na całym klipie) | montaż może uciąć ogon w dowolnym miejscu |

Punkty cięcia dla montażu: **0,4–3,8** stos rośnie · **3,8–4,6** chwianie · **4,6–5,4** wybuch ·
**5,6–6,9** fundament · **6,4–10,8** moduły · **10,8–12,1** impuls · **11,6–14,0** zapas.

## Formaty (z jednego `scene.html`, przez `make.mjs`)

| Wariant | Po co | Układ |
|---|---|---|
| `block-tower-9x16.mp4` | pełny ekran w rolce (np. przebitka `broll` + `full`) | wieża na środku, fundament dół na y 1560, szczyt ~y 860; większe klocki (moduł 96 px) |
| `block-tower-9x16-alpha.mov` | **główny dla rolki** — panel pod twarzą | wieża w polu x 140–940, y 980–1640 (fundament dół na 1640, szczyt modułów ~1090, kontur ~1010). Poza strefami zakazanymi. **Narzędzia NIE spadają z góry kadru** (przeleciałyby przez twarz): wchodzą z y ≈ 960 z przenikaniem, spadek tylko 120 px. Każdy klocek to nieprzezroczysta karta — czytelna na swetrze (pamięć `wstawki-czytelnosc-scrim-halo-karta`) |
| `block-tower-16x9.mp4` | odcinki YouTube, strona flowbiz.pl | wieża w lewej połowie (oś x 640), prawa połowa pusta pod tekst/twarz |

Dopisanie do `make.mjs`: `ALPHA["block-tower"] = ["9x16"]`. Pion z alfą — sprawdzić kompozytem
na prawdziwej klatce z nagrania Mateusza (h.264, yuv420p), nie na podglądzie sceny.

## Pułapki do obsłużenia (z dotychczasowych klocków)

- Pozycje startowe przez `tl.set(..., 0)`, nie CSS `transform` (`gsap_css_transform_conflict`).
- Wybuch i nachodzenie klocków = zasłanianie tekstu dla `hyperframes check` →
  `data-layout-allow-occlusion` na **węzłach tekstowych** etykiet (nie na kontenerze) — pamięć `hyperframes-check-zaslanianie`.
- Poświata i błysk winiety: krycie < 0,6 albo `data-layout-ignore`.
- Wszystko deterministyczne (stałe tablice przesunięć), skończone `repeat`.
- `ostrzeżenie nested_structure_needs_subcomposition` zostaje świadomie, jak w pozostałych klockach.

## Ile to potrwa

| Krok | Czas |
|---|---|
| `scene.html` (dwie fazy, trzy układy) + wpis w `make.mjs` | ~1,5 h |
| `check` + `snapshot` w kluczowych sekundach (1,6 / 4,8 / 6,2 / 10,9 / 13), poprawki | ~45 min |
| render 3 wariantów (alfa przez sekwencję PNG — najwolniejsza, ~10 min) | ~20 min |
| kompozyt alfy na klatce z nagrania + wpis do `final/INDEX.md` | ~20 min |
| **Razem** | **~3 h** pracy agenta, 0 kredytów |

Nie startuję przed akceptacją specyfikacji i nazw narzędzi.

## Otwarte

1. **Nazwy narzędzi w fazie „przed".** Domyślnie zestaw z klocka 4 (Excel, Gmail, wFirma,
   BaseLinker, Allegro, Make / n8n). „Brix" i „RP" z notatki Mateusza — do potwierdzenia, czym są
   i jak je zapisać; wchodzą jako podmiana tablicy.
2. **„Tylko Brix"** — jeśli wariant z jednym narzędziem, które rośnie i pęka, ma wejść do filmu,
   to osobna faza (~1 h dodatkowo).

## Ta sama wieża na flowbiz.pl

Wieża to zwykłe elementy DOM ze stałą geometrią i jedną pauzowaną timeline GSAP — na stronie
wystarczy podpiąć postęp przewijania pod `tl.progress()` (ScrollTrigger `scrub`) i pokazać fazę 2027
(fundament → moduły → impuls), a faza „przed" może zostać na górze sekcji jako punkt wyjścia.
Żeby film i strona były **tym samym obiektem**, wydzielamy z `scene.html` dane (lista modułów,
wymiary, kolejność) i znaczniki wieży do jednego modułu, z którego korzystają oba miejsca — kolory
idą ze zmiennych CSS, bo strona ma brandbook teal/amber (`flowbiz-automation-unlocked`), a reklamy
czerń + pomarańcz.
