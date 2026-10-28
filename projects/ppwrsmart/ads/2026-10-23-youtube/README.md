# PPWR Smart — reklamy YouTube „Automatyzacja deklaracji PPWR szyta na miarę Twojego przedsiębiorstwa”

**Data:** 2026-10-23 · **Status:** etap 1 — klatki i zrzuty (bez animacji, bez lektora) · **Landing:** ppwrsmart.com
**Styl:** [`../../ai/styl-wideo.md`](../../ai/styl-wideo.md) — ta sama paleta i ilustracje co film TAGO „chaos → system”.

## 1. Decyzja: długości i formaty

| Format | Długość | Gdzie | Po co |
|---|---|---|---|
| **A. Spot główny** (in-stream, pomijalny) | **30 s**, 16:9 | YouTube, zimny ruch B2B (segmenty: PPWR, deklaracja zgodności, opakowania) | ból → system → hasło → CTA. Płacimy dopiero za 30 s oglądania albo klik, więc 30 s to pełna długość, za którą i tak płacimy |
| **B. Cięcie** (in-feed / niepomijalny) | **15 s**, 16:9 | YouTube, kampania na zasięg w grupie docelowej | hook + 2 ekrany systemu + hasło |
| **C. Bumper** ×2 | **6 s**, 16:9 | remarketing (odwiedzający ppwrsmart.com) | przypomnienie: liczba albo hasło + adres |
| Później | 30 s, 9:16 | Shorts | te same klatki, przeskalowane do pionu (generacja 9:16, nie rozciąganie) |

**Dlaczego nie dłużej:** 100-sekundowy film TAGO zostaje do sprzedaży 1:1 i na landing. W reklamie o pominięciu decyduje pierwsze 5 s, dlatego hook jest wymienną kostką 0–5 s, a reszta spotu jest wspólna. Google Ads testuje warianty A/B bez montowania od nowa całego filmu.

## 2. Hooki (0–5 s) i ocena klikalności

Kryteria (1–5): **Z**atrzymanie (ruch, przerwanie wzorca w 1. s) · **T**rafność (czy producent z opakowaniami rozpozna się w 2 s) · **B**ól / stawka · **C**iekawość (pytanie, które zatrzymuje przed „Pomiń”) · **W**iarygodność · **S**pójność z hasłem i landingiem. Wagi: Z 20, T 20, B 20, C 15, W 15, S 10 → wynik /100.

| # | Hook (lektor / napis) | Klatka | Z | T | B | C | W | S | **Wynik** |
|---|---|---|---|---|---|---|---|---|---|
| H4 | „Dostawca zmienił folię. **Twoja deklaracja PPWR właśnie przestała być aktualna.**” | `h4-cicha-zmiana-folii` | 4 | 5 | 5 | 5 | 4 | 4 | **91** |
| H5 | „Kontrola prosi o deklarację zgodności. **Gdzie ona jest? W mailu? W segregatorze?**” | `h5-kontrola` | 5 | 4 | 5 | 4 | 4 | 3 | **86** |
| H3 | „Deklaracja PPWR w **3 minuty zamiast 20**. Zmierzone u producenta opakowań.” | `h3-20-min-3-min` | 4 | 4 | 3 | 4 | 5 | 4 | **79** |
| H1 | „Każde opakowanie w Twoim wyrobie potrzebuje deklaracji zgodności. **Każde.**” | `h1-sciana-opakowan` | 3 | 5 | 4 | 3 | 4 | 4 | **77** |
| H2 | „PPWR obowiązuje od 12 sierpnia. **Masz deklaracje do wszystkich opakowań?**” | `h2-termin-12-08` | 3 | 4 | 4 | 3 | 5 | 3 | **74** |
| H6 | „Automatyzacja deklaracji PPWR szyta na miarę Twojego przedsiębiorstwa.” | `h6-szyte-na-miare` | 3 | 3 | 1 | 2 | 3 | 5 | **53** |

**Rekomendacja:** do testu A/B **H4, H5, H3**, a H1 jako zapas. **Hasło (H6) nie otwiera spotu, tylko go zamyka.** Opis produktu w roli hooka przegrywa z bólem odbiorcy o kilkanaście punktów (`.ai/memory/copy-i-hook.md`, zmierzone na spotach AdresFlow). Hasło trafia na scenę 22–26 s i na bumper B.

- **H4** wygrywa, bo opisuje ryzyko, którego odbiorca nie widzi: zmiana jest „cicha”, więc pytanie „czy u mnie też?” zatrzymuje przed „Pomiń”. To prawdziwy przypadek z rozmów z producentami (zmiana folii v3→v4), podany bez nazwy klienta.
- **H5** ma najmocniejszy ruch: lawina maili i PDF-ów od pierwszej klatki. Strach przed kontrolą działa szeroko, ale trochę mniej celnie.
- **H3** to jedyna twarda liczba. 20 → 3 minuty zmierzył klient (OPAK KREFT) i liczba jest już publicznie na ppwrsmart.com. Ten hook działa najlepiej na ludzi, którzy już szukają rozwiązania. ⚠️ Liczba wymaga źródła, więc nazwa klienta albo case na landingu musi zostać.
- **H2:** sama data to standard, którym otwierają wszyscy sprzedawcy szkoleń PPWR, więc odbiorca na nią nie reaguje. Data po 12.08 brzmi już jak „spóźniłeś się”, a nie jak termin.

Wyniki to ocena ekspercka, nie pomiar. Po animacji puszczamy `virality_predictor` (hook_score, do 16 s na plik), a ostatecznie rozstrzyga A/B w Google Ads (wskaźnik obejrzeń i CTR).

## 3. Scenariusze

### A. Spot główny 30 s (wspólny korpus, hook wymienny)

| Czas | Obraz | Lektor (Callum, ElevenLabs v4) | Napis |
|---|---|---|---|
| 0–5 s | **hook H4 / H5 / H3** (ożywiona klatka) | wg tabeli wyżej | pigułka czerwona „Dziś, bez systemu” |
| 5–9 s | `b1-twoj-erp` (ożywiona: dane płyną z ERP do szuflad) | „Pe Pe Wu Er Smart łączy się z Twoim ERP i zbiera dokumenty od dostawców w jednym miejscu.” | pigułka złota „Z PPWR Smart” |
| 9–13 s | zrzut `03-do-weryfikacji` (najazd 1,0→1,18, kursor) | „Dostawca sam wgrywa specyfikację. Ty tylko akceptujesz.” | PPWR SMART · 1 |
| 13–17 s | zrzut `02-wyrob-blokada` | „System wie, czego brakuje, i nie wypuści niekompletnego wyrobu.” | PPWR SMART · 2 |
| 17–22 s | zrzut `10-deklaracja-dokument` → `b2-deklaracje-pl-en` | „Deklarację zgodności UE wystawiasz jednym kliknięciem.” | PPWR SMART · 3 |
| 22–26 s | `h6-szyte-na-miare` | „Automatyzacja deklaracji PPWR, szyta na miarę Twojego przedsiębiorstwa.” | hasło złotem |
| 26–30 s | plansza końcowa (HTML, logo PPWRsmart) | „Umów bezpłatny przegląd dokumentacji na ppwrsmart.com.” | **Bezpłatny przegląd dokumentacji · 30 min · ppwrsmart.com** |

### B. Cięcie 15 s

| Czas | Obraz | Lektor |
|---|---|---|
| 0–4 s | hook H4 (albo H3) | wersja skrócona: „Dostawca zmienił folię. Twoja deklaracja jest nieaktualna.” |
| 4–7 s | `02-wyrob-blokada` | „Pe Pe Wu Er Smart to wychwyci.” |
| 7–10 s | `10-deklaracja-dokument` | „I wystawi nową deklarację.” |
| 10–12,5 s | `h6-szyte-na-miare` | „Szyte na miarę Twojego przedsiębiorstwa.” |
| 12,5–15 s | plansza końcowa | „ppwrsmart.com” |

### C. Bumpery 6 s

- **C1 (liczba):** `h3-20-min-3-min` z animacją stopera → plansza „Deklaracje PPWR · ppwrsmart.com”. Bez lektora albo jedno zdanie: „Deklaracja PPWR: 3 minuty, nie 20.”
- **C2 (hasło):** `h6-szyte-na-miare` → logo. „Deklaracje PPWR szyte na miarę. ppwrsmart.com.”

## 4. Materiał w tym folderze

| Plik | Co | Źródło |
|---|---|---|
| `frames/h1…h6-*.jpg` | 6 klatek hooków (w tym hasło) | Higgsfield `gpt_image_2_5`, high, 2k, 16:9 — szablon promptu ze `styl-wideo.md` §2 |
| `frames/b1-twoj-erp.jpg`, `frames/b2-deklaracje-pl-en.jpg` | 2 klatki korpusu | jw. |
| `screens/*.png` | 9 ekranów systemu, 1920×1080 | prototyp revision-004 **zanonimizowany** przez `../../tools/capture-neutral-screens.cjs` |
| `storyboard.html` / `storyboard.jpg` | storyboard wszystkich spotów | render lokalny |

**Anonimizacja ekranów:** skrypt podmienia w locie (bez zmian w prototypie):
- logo klienta na znak „Twoja Firma”;
- zdjęcia produktów na neutralne pudełko;
- nazwę klienta i nazwę ERP na „Twoja Firma” i „ERP”;
- indeksy i nazwy z kartoteki klienta na generyczne;
- adres strony produktu (usunięty) i domeny e-mail.

Na koniec skrypt sprawdza tekst każdego ekranu pod kątem pozostałości: wynik `leaks: []` przy wszystkich 9. Zostały nazwy fikcyjnych dostawców z prototypu (Tekturix, Folmar Flex, Termoform Wola). ⚠️ Przed publikacją sprawdź, czy takich firm nie ma na rynku, albo zmień je na „Dostawca A/B/C”.

## 5. Do decyzji / do potwierdzenia przed montażem

1. **PL/EN w deklaracji** (`b2` ma zakładki PL i EN): w prototypie revision-004 wersji angielskiej jeszcze nie ma. Jeśli produkt jej nie ma, zakładki trzeba wygenerować od nowa bez nich. Lektor ich nie obiecuje.
2. **„Jednym kliknięciem”:** w prototypie jest „Zatwierdź i wystaw wszystkie”. Trzeba zdecydować, czy to obietnica produktu.
3. **Hasło na Ty** („Twojego przedsiębiorstwa”) przy landingu, który pisze na Pan/Pani: wariant celowy w reklamie, do potwierdzenia.
4. Testujemy **H4, H5, H3**?

## 6. Następny krok i koszt (Higgsfield, kredyty)

| Krok | Ilość | Szacunek |
|---|---|---|
| Ożywienie klatek w Kling 3.0 Pro (5 s, `start_image`) | 8 klipów | ~70 kr. |
| Lektor ElevenLabs v4, **jeden plik na spot** (cięcie po `silencedetect`, bez dryfu barwy) | 3 spoty + 6 wariantów hooków | ~5 kr. |
| Nagranie ekranów z kursorem (`record-prototype.js` + anonimizacja z `capture-neutral-screens.cjs`) | 3 sceny | 0 kr. (lokalnie) |
| `virality_predictor` na hookach (≤16 s) | 3–4 | wg cennika |

Stan konta po tym etapie: ~380 kr. (przed: 414,7).

**Oznaczenie AI** (`.ai/memory/oznaczanie-tresci-ai.md`): ilustracje i lektor to treść AI, więc potrzebny znak u góry kadru przez pierwsze ~4 s i przełącznik „zmienione lub syntetyczne treści” w YouTube przy każdej publikacji. Ekrany systemu, plansze i napisy nie są treścią AI.

---

## 7. Filmy z lektorem: wersja „chaos → system” bez klienta (23.10, wieczór)

**Uwagi Mateusza:**
- film TAGO „chaos → system” się podoba, ale nie może być w nim mowy o TAGO;
- **żadnych nazw własnych** (firm, osób, miast);
- logo PPWRsmart;
- wersje pionowe na Reels, Shorts i TikToka;
- różne hooki odwołujące się do **PPWR i daty 12 sierpnia**;
- dwie grupy odbiorców: **producent żywności** i **producent kartonów (opakowań)**.

### Wersje (`final/`)

| Plik | Format | Odbiorca | Napis hooka (0–8 s) |
|---|---|---|---|
| `food-16x9-full.mp4` | 16:9, 120 s | żywność | „PPWR obowiązuje od 12 sierpnia 2026. Masz deklaracje do wszystkich opakowań?” |
| `food-9x16-reel-1-data.mp4` | 9:16, 69 s | żywność | jw. (kalendarz 12.08.2026 + pieczątka PPWR) |
| `food-9x16-reel-2-folia.mp4` | 9:16, 68 s | żywność | „PPWR obowiązuje od 12.08.2026. A Twój dostawca właśnie zmienił folię.” |
| `food-9x16-reel-3-kontrola.mp4` | 9:16, 69 s | żywność | „PPWR już obowiązuje. Kontrola zapyta o deklaracje, nie o plany.” |
| `food-9x16-reel-4-kazde-opakowanie.mp4` | 9:16, 71 s | żywność | „Od 12 sierpnia każde opakowanie w Twoim wyrobie potrzebuje dokumentacji zgodności. Każde.” |
| `carton-16x9-full.mp4` | 16:9, 108 s | kartony | „PPWR obowiązuje od 12 sierpnia 2026. Klient pyta o deklarację do każdego zamówienia.” |
| `carton-9x16-reel-1-klient-pyta.mp4` | 9:16, 65 s | kartony | jw. |
| `carton-9x16-reel-2-word.mp4` | 9:16, 63 s | kartony | „PPWR obowiązuje od 12.08.2026. A Ty wciąż składasz deklaracje ręcznie, w Wordzie?” |
| `carton-9x16-reel-3-tektura.mp4` | 9:16, 66 s | kartony | „PPWR obowiązuje od 12.08.2026. Dostawca tektury zmienił jej skład — Twoja deklaracja o tym nie wie.” |

Napisy są skrócone, a lektor w każdej wersji zaczyna od „Od dwunastego sierpnia obowiązuje pe-pe-wu-er…” (patrz poprawki niżej). Źródłem prawdy dla tekstów jest `specs/build-specs.py`.

Każdy hook w nagłówku i w pierwszym zdaniu lektora przywołuje PPWR i datę 12 sierpnia. Kąt jest inny w każdej wersji: termin, cicha zmiana u dostawcy, kontrola, skala, klient, ręczna praca.

### Jak to jest złożone

- **Opis scen** generuje `specs/build-specs.py`, a wynik ląduje w `specs/*.json`. Hooki są wymienne, a korpus jest wspólny dla danej grupy odbiorców.
  - Nowy hook dodajesz jako nowy wpis w `FOOD_HOOKS` / `CARTON_HOOKS`, potem `python3 build-specs.py && ./render-all.sh <spec>.json`.
- **Montaż:** `../../tools/render-ad.mjs` + `../../tools/ad-composer.html`.
  - Długość sceny wynika z długości kwestii lektora.
  - 9:16 = nagłówek u góry, obraz kwadratowy (ilustracje) albo jedno okno prototypu (nagranie).
  - Dolne ~15% kadru jest puste, bo zasłania je interfejs Reels/TikToka.
  - Oznaczenie „Treści wygenerowane z użyciem AI” jest u góry przez pierwsze 4 s.
  - Logo `assets/brand/lockup-inverse.svg` jest w rogu i na planszy końcowej.
- **System bez klienta:**
  - Nagranie: `tools/record-prototype-neutral.cjs`. To prawdziwa praca w prototypie, dwa okna i kursor.
  - Zrzuty: `tools/capture-neutral-screens.cjs`.
  - Oba korzystają z `tools/neutralize-prototype.cjs`, który podmienia w locie logo, nazwę klienta, ERP, indeksy, dostawców, osoby, miasta, domeny i zdjęcia produktów. Na końcu sprawdza tekst każdego ekranu pod kątem pozostałości.
  - Karta techniczna dla kartonów: `tools/capture-carton-card.cjs` (podgląd karty z `ppwrsmart-demo`, dane producenta i osób zamazane).
- **Lektor:**
  - Głos Callum (ElevenLabs v4) jak w filmie TAGO.
  - Nowe kwestie leżą w `voice/`. Kwestie z filmu TAGO bez nazw i liczb klienta są użyte ponownie jako `voice/tago-film-*.mp3`.
- **Klipy Kling** (`assets/clips*/`, poza gitem):
  - 8 z filmu TAGO;
  - 4 hooki dla żywności (h1, h2, h3, h5);
  - 7 klatek kartonowych (k1–k7);
  - hasło (h6).

### Pułapki, które wyszły po drodze

- Klatka `01-skrzynka` z filmu TAGO ma na monitorze **wymyślone przez AI nazwy firm**, a do tego „40 dostawców”. Wypadła ze wszystkich wersji. Przy nowych klatkach w promptach dopisuj „no readable company names”.
- Klatka `b2-deklaracje-pl-en` obiecuje wersję EN, więc nie ma jej w filmach.
- „3 minuty zamiast 20” to pomiar OPAK KREFT, opublikowany na ppwrsmart.com. W filmie nie pada nazwa producenta, a pomiar musi zostać opisany na landingu jako źródło.

### Koszt (kredyty Higgsfield)

| Pozycja | Kr. |
|---|---|
| 8 klatek reklamowych + 7 klatek kartonowych (GPT Image 2.5) | ~60 |
| 12 klipów Kling 3.0 Pro (4 hooki, 7 kartonowych, hasło) | ~105 |
| 21 kwestii lektora | ~10 |

### Poprawki po uwagach z 23.10, późny wieczór

- **Wymowa PPWR:** lektor czyta „pe-pe-wu-er”, a hasło „pepewuer”. Wszystkie hooki zaczynają się od „Od dwunastego sierpnia obowiązuje pe-pe-wu-er…”, bo akronim na początku zdania zawsze psuł się w TTS. Próby są w `voice-tests/`, a pamięć w `.ai/memory/wymowa-ppwr-lektor.md`.
- **„Tektura” zamiast „papierni”:** zmiana objęła lektora, napisy, klatkę `k3-surowce` (ciężarówka TEKTURA) i kartę techniczną („Dostawca tektury”).
- **Czas pracy:**
  - wersja dla żywności: „Ręcznie jedna deklaracja potrafi zająć nawet godzinę. Z PPWR Smart to kilka minut”;
  - wersja dla kartonów: „nawet godzina” na klatce `k5` (stoper 60 MIN) oraz zmierzone „3 minuty” na końcu.
  - „Nawet godzina” to ogólna obserwacja, bez przypisania komukolwiek (decyzja Mateusza 23.10). Wymiana na liczbę wymaga źródła.
- **„Nie musisz zatrudniać do tego nowych ludzi”:** dopisane w obu wersjach, napis „Bez nowych etatów”.
- **Plansza modułów** (zakres etapu 1 z planu dla TAGO, bez nazwy klienta): import z ERP, portal dostawcy, receptury opakowań, reguły PPWR i blokady, deklaracje zgodności UE, karty techniczne, wersje i archiwum. Stoi przed hasłem we wszystkich wersjach.
- **Reelsy spożywcze:** wypadła scena „obchód miesięczny”. Reelsy mają ~65–70 s (scena modułów i czas pracy doszły).

### Stan na 28.10 i co dalej

- **Gdzie są filmy:** `final/` w tym folderze (poza gitem) oraz kopia na Google Drive: `Mój dysk/Firmowe/Marketing/PPWR Smart/2026-10-23 reklamy wideo/` (podfoldery „Producent żywności”, „Producent kartonów”). 28.10 synchronizacja Drive z chmurą nie szła — przed usunięciem worktree sprawdź, czy pliki są w chmurze.
- **Wymowa:** Mateusz odsłuchał próbki w `voice-tests/` i zostawił wariant 0 (obecny). Hasło czyta „pepewuer”; porównanie z próbkami 7 i 8 czeka na decyzję.
- **Otwarte, do decyzji Mateusza:**
  - krótsze reelsy 30–45 s (obecne ~65–70 s);
  - wariant hooka z realistycznymi zdjęciami z polskich firm (pani 55+), źródło i przepis w `recording-library/assets/broll/hf/stills/` i `tools/broll_gen.py`;
  - przy publikacji włączyć oznaczenie treści AI w ustawieniach platformy.

