# Katalog układów — przejścia, teksty, przebitki

Uzupełnienie [`WYTYCZNE-MONTAZU.md`](WYTYCZNE-MONTAZU.md): wytyczne mówią **jak** montujemy,
katalog pokazuje **czym** — każdy układ, którego używamy, z prawdziwą klatką z gotowego filmu.

Klatki odświeża jedno polecenie (po zmianie wyglądu albo nowym układzie):

```bash
cd projects/recording-library && python3 tools/layout_catalog.py   # → final/catalog/*.jpg
```

Kolory, fonty i logo — brandbook w repo FlowBiz (patrz „Połączenia z repo” w README).
Nazwa w `kodzie` to typ zdarzenia w storyboardzie (`packaging/storyboards/<film>.json`) —
tak się do układu odwołujesz w uwagach („tu daj `slam`”).

Formaty: **rolka** 9:16 (twarz u góry, panel na dole) · **reklama** 9:16 z planszą CTA ·
**zajawka** 4:5 · **odcinek** 16:9 (twarz pełnym kadrem, panel z boku albo pasek na dole).

---

## 1. Otwarcie

| Układ | Kiedy | Wygląd |
|---|---|---|
| **Okładka** `cover` — jedno zdanie kontekstu na pierwszym ekranie | każda rolka wycięta z dłuższego odcinka; bez niej „nie wiadomo, o czym mowa” | <img src="projects/recording-library/final/catalog/cover-reels.jpg" width="160"> <img src="projects/recording-library/final/catalog/cover-feed.jpg" width="190"> |
| **Hook** `hook` — nagłówek na twarzy przez pierwsze 3–6 s, panel wjeżdża po nim | każda rolka, reklama i zajawka; odcinek 16:9 go nie ma | <img src="projects/recording-library/final/catalog/hook-reels.jpg" width="160"> <img src="projects/recording-library/final/catalog/hook-feed.jpg" width="190"> |

## 2. Przejścia i uderzenia

Plansza na pełny ekran, głos leci pod spodem. Wchodzi przez **błysk bieli** — to jest też
nasze przejście na dużym przeskoku w nagraniu. Rytm: co 15–30 s inna forma.

| Układ | Kiedy | Wygląd |
|---|---|---|
| **Liczba** `beat` / `burst` — duża liczba z poświatą i cząstkami | pada mocna liczba: „8 wdrożeń”, „40 minut” | <img src="projects/recording-library/final/catalog/beat-burst.jpg" width="300"> |
| **Przekreślenie** `beat` / `strike` — stara wartość przekreślona na tekście | „było — jest”: kilkanaście godzin → minuty, stary sposób | <img src="projects/recording-library/final/catalog/beat-strike.jpg" width="300"> |
| **Trzy linie** `beat` / `slam` — teza w trzech liniach z belką i wstrząsem | puenta, zwrot akcji: „jeden moment i wszystko się wywraca” | <img src="projects/recording-library/final/catalog/beat-slam.jpg" width="300"> |
| **Plansza rozdziału** `slate` — tytuł części na pełnym ekranie, twarz w okienku | początek nowej części odcinka; zmiana tematu | <img src="projects/recording-library/final/catalog/slate-youtube.jpg" width="300"> |
| **Zmiana planu** (automatyczna) — przybliżenie/oddalenie twarzy | na każdej sklejce i co kilka zdań; nic nie trzeba zamawiać | — |

## 3. Teksty na twarzy i w panelu

W rolce lądują w dolnym panelu, w odcinku w panelu bocznym (700 px) albo na **pasku dolnym**
(`zone: "lower"`, tylko 16:9). W odcinku tytuł i cytat losują układ, żeby nie jechał w kółko
ten sam.

| Układ | Kiedy | Rolka | Odcinek |
|---|---|---|---|
| **Tytuł** `title` — hasło + nadtytuł | nazwa tematu, główna myśl fragmentu | <img src="projects/recording-library/final/catalog/title-reels.jpg" width="130"> | <img src="projects/recording-library/final/catalog/title-youtube.jpg" width="230"> <img src="projects/recording-library/final/catalog/title-youtube-lower.jpg" width="230"> |
| **Lista** `list` — 3–4 hasła po kolei | wyliczenie; hasła podobnej długości, nie zdania z mowy | <img src="projects/recording-library/final/catalog/list-reels.jpg" width="130"> | <img src="projects/recording-library/final/catalog/list-youtube.jpg" width="230"> |
| **Porównanie** `compare` — dwie kolumny albo dwa słupki | przed/po, ręcznie/w systemie, my/oni | <img src="projects/recording-library/final/catalog/compare-reels.jpg" width="130"> | <img src="projects/recording-library/final/catalog/compare-youtube.jpg" width="230"> |
| **Liczba w panelu** `stat` — liczba z podpisem, bez przerywania twarzy | liczba, która nie zasługuje na pełny ekran | <img src="projects/recording-library/final/catalog/stat-reels.jpg" width="130"> | <img src="projects/recording-library/final/catalog/stat-youtube.jpg" width="230"> |
| **Cytat** `quote` | zdanie klienta albo mocne zdanie autora | <img src="projects/recording-library/final/catalog/quote-reels.jpg" width="130"> | <img src="projects/recording-library/final/catalog/quote-youtube.jpg" width="230"> <img src="projects/recording-library/final/catalog/quote-youtube-lower.jpg" width="230"> |
| **Czat** `chat` — dymki rozmowy | rozmowa z AI, pytanie klienta, „AI zawsze przyzna Ci rację” | <img src="projects/recording-library/final/catalog/chat-reels.jpg" width="130"> | <img src="projects/recording-library/final/catalog/chat-youtube.jpg" width="230"> |
| **Logo narzędzi** `logos` — oryginalne logotypy | padają nazwy narzędzi: Claude, Codex, Excel, n8n | <img src="projects/recording-library/final/catalog/logos-reels.jpg" width="130"> | <img src="projects/recording-library/final/catalog/logos-youtube.jpg" width="230"> |

Napisy (tylko pion) idą same z transkrypcji i znikają, gdy karta powtarza wypowiedź.

## 4. Przebitki

| Układ | Kiedy | Wygląd |
|---|---|---|
| **Przebitka w pionie** `broll` — zastępuje twarz, panel zostaje | ilustracja tego, co pada; najpierw własne nagrania Mateusza | <img src="projects/recording-library/final/catalog/broll-reels.jpg" width="130"> |
| **Przebitka na cały pion** `broll` + `full` — animacja na pełny ekran 9:16 | klocek animacji flowbiz, który w ramce twarzy byłby obcięty | <img src="projects/recording-library/final/catalog/broll-full.jpg" width="130"> |
| **Przebitka w odcinku** `broll` — pełny kadr 16:9, powolny najazd | jak wyżej; materiał z generatora dostaje znak „AI” u góry | <img src="projects/recording-library/final/catalog/broll-youtube.jpg" width="230"> |

## 5. Makiety — pokazanie mechanizmu

`mockup` z nazwą: makieta systemu na pełnym ekranie, twarz w okienku w rogu, głos pod spodem.
Używamy, gdy w nagraniu pada **mechanizm** — jak coś działa w firmie albo w systemie. Nowa
makieta to funkcja w `projects/recording-library/tools/mockups.py`.

| Makieta | Pokazuje | | Makieta | Pokazuje |
|---|---|---|---|---|
| `excels` <br><img src="projects/recording-library/final/catalog/mockup-excels.jpg" width="200"> | kilka Exceli z tym samym zamówieniem | | `copies` <br><img src="projects/recording-library/final/catalog/mockup-copies.jpg" width="120"> | ten sam plik w kilku wersjach |
| `match` <br><img src="projects/recording-library/final/catalog/mockup-match.jpg" width="200"> | dopasowanie nazw produktów z pewnością | | `labels` <br><img src="projects/recording-library/final/catalog/mockup-labels.jpg" width="200"> | generowanie etykiet z zamówienia |
| `funnel` <br><img src="projects/recording-library/final/catalog/mockup-funnel.jpg" width="200"> | wystawione oferty → wygrane | | `pdfs` <br><img src="projects/recording-library/final/catalog/mockup-pdfs.jpg" width="200"> | każdy ma swoją wersję oferty |
| `telegram` <br><img src="projects/recording-library/final/catalog/mockup-telegram.jpg" width="200"> | asystent firmy na komunikatorze | | `context` <br><img src="projects/recording-library/final/catalog/mockup-context.jpg" width="120"> | czat AI gubi kontekst rozmowy |
| `sources` <br><img src="projects/recording-library/final/catalog/mockup-sources.jpg" width="200"> | wiedza w głowach, kartkach, mailach | | `board` <br><img src="projects/recording-library/final/catalog/mockup-board.jpg" width="200"> | tablica zadań / proces |
| `b2b` <br><img src="projects/recording-library/final/catalog/mockup-b2b.jpg" width="200"> | panel klienta B2B, zamówienia | | `catalog` <br><img src="projects/recording-library/final/catalog/mockup-catalog.jpg" width="200"> | katalog produktów |
| `parcels` <br><img src="projects/recording-library/final/catalog/mockup-parcels.jpg" width="200"> | ręczne pakowanie / wysyłka | | `coast` <br><img src="projects/recording-library/final/catalog/mockup-coast.jpg" width="200"> | sezonowość, trasa handlowca |
| `sync` <br><img src="projects/recording-library/final/catalog/mockup-sync.jpg" width="200"> | synchronizacja z zewnętrznym systemem | | `storage` <br><img src="projects/recording-library/final/catalog/mockup-storage.jpg" width="200"> | gdzie trzymane są dane (aplikacja z AI) |
| `deps` <br><img src="projects/recording-library/final/catalog/mockup-deps.jpg" width="200"> | zależności — jedna zmiana psuje resztę | | `layers` <br><img src="projects/recording-library/final/catalog/mockup-layers.jpg" width="200"> | warstwy systemu (fundament gotowy) |
| `repo` <br><img src="projects/recording-library/final/catalog/mockup-repo.jpg" width="200"> | kod i specyfikacja w repozytorium | | `modules` <br><img src="projects/recording-library/final/catalog/mockup-modules.jpg" width="120"> | gotowe moduły Open Mercato |
| `route` <br><img src="projects/recording-library/final/catalog/mockup-route.jpg" width="200"> | droga zamówienia przez firmę | | `questions` <br><img src="projects/recording-library/final/catalog/mockup-questions.jpg" width="200"> | warsztat: pytania po rolach |
| `spec` <br><img src="projects/recording-library/final/catalog/mockup-spec.jpg" width="200"> | specyfikacja: problem w liczbach | | `glossary` <br><img src="projects/recording-library/final/catalog/mockup-glossary.jpg" width="200"> | słownik — to samo słowo, dwa znaczenia |
| `checklist` <br><img src="projects/recording-library/final/catalog/mockup-checklist.jpg" width="200"> | lista wymagań odhaczana po kolei | | `history` <br><img src="projects/recording-library/final/catalog/mockup-history.jpg" width="120"> | historia zmian rekordu |

## 6. Zakończenie

| Układ | Kiedy | Rolka | Odcinek |
|---|---|---|---|
| **Plansza końcowa** `endcard` — duże logo, wezwanie | koniec każdego filmu; w reklamie z przyciskiem | <img src="projects/recording-library/final/catalog/endcard-reels.jpg" width="130"> | <img src="projects/recording-library/final/catalog/endcard-youtube.jpg" width="230"> |

## Jak dobierać — skrót

- **Pada liczba** → `burst` (mocna) albo `stat` (poboczna).
- **Było/jest** → `strike`; dwie strony → `compare`.
- **Puenta** → `slam`. **Nowa część odcinka** → `slate`.
- **Wyliczenie** → `list`. **Nazwy narzędzi** → `logos`. **Rozmowa** → `chat`.
- **Jak to działa** → `mockup`. **O czym mowa, a nie ma czego pokazać** → `broll`.
- Dwa pełnoekranowe układy pod rząd tylko wtedy, gdy między nimi wraca twarz.
