# Klocki animacji flowbiz: HTML + HyperFrames, czerń + pomarańcz, jedna prawdziwa liczba

**Data:** 2026-10-10
**Status:** ✅ wdrożone — 5 klocków × 2 formaty (+ 4 nakładki z alfą) w `final/`

## Problem

Mateusz montuje na drugim komputerze reklamy i rolki flowbiz i potrzebuje „klocków" —
krótkich animacji systemu i ofert, które wstawia między ujęcia. Kierunek wizualny wskazał
sam: czerń + pomarańcz, premium, z nutą AI (grafiki z Higgsfielda w
`assets/higgsfield-grafiki/` oraz moduły rysowane kodem na flowbiz.pl).

Dwa ryzyka: (1) grafiki z generatora mają wymyślone teksty i liczby — nie da się ich
animować ani poprawić; (2) reklama software house'u, która pokazuje zmyślone wyniki albo
nazwy prawdziwych klientów, podważa wiarygodność, którą ma budować.

## Decyzja

### 1. HTML → wideo przez HyperFrames, nie model wideo

Ta sama zasada co w ADR repo
[`2026-07-30-ekran-produktu-z-html.md`](../../../../.ai/decisions/2026-07-30-ekran-produktu-z-html.md):
UI z modelu wideo to papka z bełkotem zamiast polskich napisów, a w HTML każda zmiana
danych kosztuje 0 kredytów. Makiety Open Mercato przeniesione strukturą z
`flowbiz-redesign-preview/src/components/home-v2/{quoteAutomationScene,openMercatoModules}.ts`
(AppShell z sidebarem, konfigurator wyceny, tabele), przemalowane na nową paletę.

**Jedno źródło na klocek, dwa formaty z generatora** (`screens/make.mjs`): scena ma układ
poziomy i pionowy w jednym pliku (klasy `fmt-land`/`fmt-port`), a `make.mjs` składa z niej
osobne projekty 1920×1080 i 1080×1920 w `build/hf/`. Powód: `check`/`snapshot` widzą tylko
`index.html` projektu, a rozmiar korzenia jest stały — dwie ręczne kopie rozjechałyby się.

### 2. Paleta i typografia

| Rola | Wartość |
|---|---|
| tło | `#0B0B0D` + siatka 72 px, ziarno, poświata |
| karty | `#16161A` / `#1D1D22` |
| akcent | `#FF6A1A`, jaśniejszy `#FF8A3D`, poświata `rgba(255,106,26,.45)` |
| tekst | `#F5F5F7` / `#A1A1AA` (trzeciorzędny `#8E8E98` — przechodzi kontrast 4,5:1 na kartach) |
| „przed" / błąd | przytłumiona czerwień `#B8443C`, tekst `#F19A91` |
| font | Plus Jakarta Sans + JetBrains Mono do danych (lokalne pliki OFL w `screens/shared/fonts/`) |

Na pomarańczowych przyciskach tekst ciemny (`#160A03`) — biały na `#FF6A1A` nie przechodzi
kontrastu. Mały kolorowy tekst tylko na ciemnej pigułce lub w ciemnej karcie
([[tekst-nasycony-kolor-na-materiale]]).

### 3. Zasady treści

- **Jedyna prawdziwa liczba: 40 min → 5–10 min** (przygotowanie jednej oferty, szwalnia —
  case study na flowbiz.pl). Żadnych innych wyników, procentów ani „x razy szybciej".
- **Dane fikcyjne, te same co w makietach na stronie** — Pracownia Bałtyk, Nordtex Sp. z o.o.,
  OF/2026/10/042, ZAM/2026/0917, kwoty 6 450,00 / 11 730,00 zł. Widz, który ogląda
  reklamę i stronę, widzi jeden spójny świat.
- **Narzędzia w klocku integracji tylko z nazwy**, z ogólnymi piktogramami — bez logotypów
  wFirmy, BaseLinkera, Allegro, Gmaila, Excela, Make/n8n.
- **Klocki nie są treścią AI** w rozumieniu art. 50 ust. 4 AI Act (HTML, typografia, makiety)
  — nie oznaczamy ich ([[oznaczanie-tresci-ai]]). Jeśli wejdą do spotu razem z ujęciami
  z Higgsfielda, oznaczenie dotyczy spotu.

### 4. Ruch

Jeden mocny moment na klocek (toast „gotowa", wypuszczenie wyjść z systemu, przejście
40 → 5–10), easing `expo.out`/`back.out`, powolny dojazd kamery do końca klipu — montaż
może uciąć ogon bez straty. Wszystko seek-safe: jedna pauzowana timeline, liczniki na
proxy, skończone powtórzenia, zero zegara i losowości.

### 5. Nakładki z alfą

Klocki 2 (agent AI) i 5 (stoper) mają warianty `-alpha.mov` (qtrle) — bez tła, siatki
i ziarna ([[wstawki-alfa-nie-green-screen]]). Stoper w poziomie z alfą przechodzi w układ
**lewej tercji** z kartą pod tekstem, żeby nie zasłaniać twarzy mówiącego
([[wstawki-uklad-lewy-domyslny]], [[wstawki-czytelnosc-scrim-halo-karta]]).

## Pułapki

1. **`data-layout-allow-occlusion` musi być na zakrywanym tekście** (bramka sprawdza
   `hasAttribute` na samym elemencie tekstu, bez dziedziczenia). Postawienie go na modalu
   albo na rodzicu nic nie daje.
2. **Scrim liczy się jako zakrycie, gdy element ma `opacity ≥ 0.6`.** Ściemnienie pod
   modalem: ciemny kolor tła + `opacity` elementu ~0,55.
3. **`check` zgłasza `nested_structure_needs_subcomposition`** dla każdej sceny — to uwaga
   o osi czasu w Studio. Zostawiona świadomie: klocek ma jeden klip, rozbijanie na
   sub-kompozycje nic nie daje w renderze.
4. **HyperFrames wymaga Node 22+**, a domyślny node na tej maszynie to 20 — `render.sh`
   sam sięga po nowszy z nvm.

## Do decyzji właściciela

- Logo na końcu klocka 5 to `logo-ai-mono-white.svg` ze strony (biały, z dopiskiem
  „AUTOMATION & CONSULTING"). Jeśli ma być wersja bez dopisku albo z pomarańczowym znakiem —
  podmiana pliku w `screens/shared/`.
- Nakładki `.mov` (40–150 MB sztuka, ~440 MB razem z MP4) są w `final/`, ale poza gitem
  (`projects/flowbiz/.gitignore`, precedens `projects/youtube`). Jeśli mają trafić na drugi
  komputer inaczej niż przez `./screens/render.sh` — git-lfs albo Drive.
- Wersje alfa poziome mają sens na gadaną głowę; pionowe alfa (9×16) — na rolki z nagraniem
  telefonem. Pozostałe klocki są pełnoekranowe i alfy nie dostały.

## Powiązane

- ADR repo: [ekran produktu z HTML](../../../../.ai/decisions/2026-07-30-ekran-produktu-z-html.md)
- Pamięć repo: `ekran-produktu-hyperframes`, `wstawki-alfa-nie-green-screen`,
  `wstawki-uklad-lewy-domyslny`, `wstawki-rozdzielczosc-pod-projekt`,
  `tekst-nasycony-kolor-na-materiale`, `oznaczanie-tresci-ai`
- Instrukcja przebudowy: [`../../README.md`](../../README.md)
