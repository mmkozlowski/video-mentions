---
workflow: motion-graphics
flow: autonomous
mode: autonomous
date: 2026-10-10
owner: Mateusz (flowbiz)
---

# BRIEF — klocki animacji flowbiz (czerń + pomarańcz)

Decyzje właściciela przekazane w zleceniu — bez wywiadu intencji.

## Cel

Pięć krótkich, niemych klocków animacji (6–12 s) do montażu reklam i rolek flowbiz:
software house budujący systemy dla firm na Open Mercato, automatyzacje i agentów AI.
Odbiorca reklam: właściciele firm 10–100 os., produkcja i handel B2B.

## Styl

- Klimat: **czerń + pomarańcz**, premium, nowocześnie, z nutą AI.
- Wzorce: `assets/higgsfield-grafiki/*.png` (kierunek stylu, nie do wklejania — teksty
  na nich bywają wymyślone) i makiety Open Mercato rysowane kodem na flowbiz.pl
  (`flowbiz-redesign-preview/src/components/home-v2/{quoteAutomationScene,openMercatoModules}.ts`),
  przemalowane na czerń + pomarańcz.
- Paleta: tło `#0B0B0D`, karty `#16161A` / `#1D1D22`, akcent `#FF6A1A`, jaśniejszy
  `#FF8A3D` + poświata, tekst `#F5F5F7` / `#A1A1AA`, błąd/„przed": przytłumiona czerwień.
- Font: Plus Jakarta Sans + JetBrains Mono do danych (lokalne pliki, OFL).
- Tło: delikatna siatka, ziarno, poświata. Jeden mocny moment na animację, easing premium.

## Klocki

| # | Nazwa | Co pokazuje |
|---|---|---|
| 1 | `oferta-chaos-do-systemu` | arkusze xlsx, karteczki, dzwoniący telefon wsiąkają w „Konfigurator wyceny"; stoper 40:00 → 5–10 min; finał „Oferta OF/2026/10/042 gotowa" |
| 2 | `agent-ai-duplikuje-oferte` | pole poleceń AI (⌘K), polecenie o Nordtex, agent „myśli", pozycje kopiują się, toast „Skopiowano 2 pozycje z ZAM/2026/0917" |
| 3 | `system-moduly-przelot` | przelot przez moduły Open Mercato: CRM → Oferty → Magazyn → Portal klienta → Asystent AI, aktywny moduł świeci w sidebarze |
| 4 | `integracje-w-jeden-system` | kafelki narzędzi (nazwy tekstem, bez logotypów) → świecące linie → „system firmy" → Zlecenia, Portal B2B, Raporty, Powiadomienia (Telegram) |
| 5 | `stoper-40-do-5` | hit liczby 40 min → 5–10 min, pierścień, „Szwalnia · wdrożenie flowbiz", logo flowbiz na końcu |

Każdy w dwóch formatach: **1920×1080** i **1080×1920**. Bez lektora, bez muzyki.

## Zasady treści

- Jedyna prawdziwa liczba z wdrożenia: **40 min → 5–10 min** (przygotowanie jednej oferty, szwalnia).
  Żadnych innych liczb, procentów ani wyników.
- Żadnych prawdziwych klientów ani kontrahentów — dane fikcyjne: Pracownia Bałtyk, Nordtex Sp. z o.o.
  (ten sam zestaw co makiety na flowbiz.pl).
- Teksty po polsku. Nazwy narzędzi w kl. 4 tylko tekstem, bez logotypów firm.
- To grafika z HTML, nie treść generowana AI — nie wymaga oznaczenia z art. 50 ust. 4 AI Act
  (patrz `.ai/memory/oznaczanie-tresci-ai.md`).

## Dostawa

- MP4 → `build/` (poza gitem), dobre wersje → `final/` + `final/INDEX.md`.
- Wersje z alfą (qtrle `.mov`) dla klocków, które mają sens jako nakładka (2 i 5).
- Render zatwierdzony z góry przez zlecenie (bez bramki „render now?").
