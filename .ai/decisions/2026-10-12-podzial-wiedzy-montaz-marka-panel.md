# Podział wiedzy: montaż tutaj, marka w FlowBiz, panel w studiu

**Data:** 2026-10-12
**Status:** ✅ wdrożone (dokumenty, połączenia, zakładka „Filmy” w studiu) · plan (`brand.json`)

## Problem

Wiedza o produkcji wideo była rozproszona w ~35 wpisach pamięci i 3 ADR-ach — czytelna dla
Claude, nie dla agencji. Marka FlowBiz (kolory, font, ton) żyje w repo strony, panel marketingu
w `flowbiz-ads-studio`, a pipeline wideo tutaj. Mateusz: „muszę te dwa repo jakoś połączyć”.

## Decyzja

- **Trzy repo zostają osobne** — 26 GB nagrań nie ma iść do repo strony wdrażanej na Vercel,
  a panel z tokenami Meta/Google nie miesza się z montażem.
- **Wytyczne montażu i marka rozdzielone** (decyzja Mateusza): `WYTYCZNE-MONTAZU.md`
  (jak tniemy, co wycinamy, formaty, kontrola) i `KATALOG-UKLADOW.md` (układy przejść, tekstów,
  przebitek z prawdziwymi klatkami, `tools/layout_catalog.py`) tutaj; kolory/font/logo/ton
  tylko w `flowbiz-automation-unlocked` (`.ai/memory/project-rebrand-palette-font.md`,
  `src/app/globals.css`).
- **Każdy projekt ma w README sekcję „Połączenia z repo”**, a README główne — tabelę.
- Zakładka „Filmy” w studiu czyta `studio-index.json` tego repo (źródło w `flowbiz-ads-studio/data/sources.json`,
  ścieżka na maszynie w `.env`), plansza `board_server.py` wyłączona. Plan: marka eksportowana do `brand.json` czytanego przez `package.py`.

## Pułapki

- Paleta B w `recording-library/tools/package.py` to ręczna kopia tokenów strony — do czasu
  `brand.json` zmiana na stronie nie przechodzi do wideo sama.
- `projects/recording-library/final/` jest poza gitem; wyjątek tylko dla `final/catalog/`.
- Ogólna poprawka Mateusza do filmu trafia do pamięci **i** do `WYTYCZNE-MONTAZU.md`.

Powiązane: [Starsze odcinki kanału](../../projects/recording-library/ai/decisions/2026-10-11-starsze-odcinki-kanalu.md).
