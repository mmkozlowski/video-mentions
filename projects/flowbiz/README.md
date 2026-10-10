# flowbiz — klocki animacji systemu (czerń + pomarańcz)

Krótkie, nieme animacje do montażu reklam i rolek flowbiz: system na Open Mercato,
oferta, agent AI, integracje i jedyna liczba z wdrożenia (szwalnia: 40 min → 5–10 min).
Wszystko rysowane w HTML i renderowane przez HyperFrames — zero kredytów, zero materiału AI.

Decyzje: [`BRIEF.md`](BRIEF.md), ADR
[`ai/decisions/2026-10-10-animacje-systemu-czern-pomarancz.md`](ai/decisions/2026-10-10-animacje-systemu-czern-pomarancz.md).
Gotowe pliki i do czego służą: [`final/INDEX.md`](final/INDEX.md).

```
projects/flowbiz/
├── BRIEF.md                      decyzje właściciela (styl, treść, formaty)
├── assets/higgsfield-grafiki/    wzorce stylu (nie do wklejania)
├── screens/
│   ├── shared/                   ŹRÓDŁO: flowbiz.css, kit.js (ikony, liczniki), fonty OFL, logo
│   ├── <klocek>/scene.html       ŹRÓDŁO: jedna scena, układ poziom/pion z jednego pliku
│   ├── make.mjs                  generuje projekty HyperFrames do build/hf/
│   └── render.sh                 make → check → render (MP4 + .mov z alfą)
├── build/                        ROBOCZE, poza gitem (projekty hf, rendery)
└── final/                        GOTOWE — MP4 i .mov + INDEX.md
```

## Przebudowa

```bash
cd projects/flowbiz
./screens/render.sh                     # wszystkie klocki, wszystkie formaty
./screens/render.sh stoper-40-do-5      # jeden klocek
```

Wymaga Node 22+ (skrypt sam sięga po nowszy node z nvm) i ffmpeg. HyperFrames przypięty
na `0.8.145`. Po obejrzeniu skopiuj dobre wersje z `build/` do `final/` i zaktualizuj
`final/INDEX.md`.

## Edycja sceny

1. Edytuj `screens/<klocek>/scene.html` (albo `screens/shared/*`, jeśli zmiana dotyczy wszystkich).
2. `node screens/make.mjs <klocek>` — generuje `build/hf/<klocek>-16x9/` i `-9x16/` (+ `-alpha`).
3. `npx hyperframes check build/hf/<klocek>-16x9` i `snapshot --at …` — obejrzyj klatki.
4. `./screens/render.sh <klocek>`.

Nie edytuj plików w `build/hf/` — nadpisuje je każde `make.mjs`.

Dlaczego generator: `check` i `snapshot` widzą tylko `index.html` projektu, a korzeń kompozycji
ma stałe `data-width/height`. Dwa formaty to dwa projekty — trzymanie dwóch ręcznych kopii
każdej sceny rozjechałoby je przy pierwszej poprawce. W pliku źródłowym `__W__`, `__H__`,
`__FMT__` (`land`/`port`), `__ID__` i `__HTMLCLASS__` (`alpha-mode` dla nakładek) podstawia `make.mjs`.

## Zasady treści (skrót z BRIEF)

- Jedyna prawdziwa liczba: **40 min → 5–10 min** (przygotowanie jednej oferty, szwalnia).
- Dane fikcyjne, spójne z makietami na flowbiz.pl: Pracownia Bałtyk, Nordtex Sp. z o.o.,
  OF/2026/10/042, ZAM/2026/0917.
- Narzędzia w klocku integracji: nazwy tekstem + ogólne piktogramy, bez logotypów firm.

## Pułapki, które wyszły przy budowie

- **`data-layout-allow-occlusion` działa na zakrywanym tekście, nie na zakrywającym
  elemencie i się nie dziedziczy.** Modal (paleta ⌘K) i rozrzucony chaos dostają waiver
  na potomkach w JS — patrz komentarze w scenach 1 i 2.
- **Scrim o pełnej kryjącości to „zakrycie" dla bramki.** Ściemnienie pod modalem robimy
  elementem z `opacity < 0.6` (bramka go wtedy pomija), a ciemność bierzemy z koloru tła.
- **Wpisywanie tekstu bez mierzenia DOM:** pole poleceń ma font mono (JetBrains Mono,
  znak = 0,6 em), więc szerokość i kursor to `n × znak` z `ease: steps(n)`.
- **Ostrzeżenie `nested_structure_needs_subcomposition`** zostaje świadomie — to uwaga
  o czytelności osi czasu w Studio, nie o renderze.
