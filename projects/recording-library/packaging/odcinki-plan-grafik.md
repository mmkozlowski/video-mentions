---
typ: plan
etap: 3 — odcinki case study (YouTube 16:9)
status: w toku — makiety wspólne gotowe (tools/mockups.py), pilot ep-doram wyrenderowany do oceny
źródło czasów: data/transcripts/*.txt (czasy ≈, liczone od początku klipu ep-*)
---

# Odcinki case study — rozdziały, makiety systemu, przejścia

Pięć pełnych odcinków leży w bazie jako `ep-*` (master 16:9 w `build/library/`).
Każdy dostaje: **rozdziały** (znaczniki YouTube), **makiety systemu** w HTML
(HyperFrames — ekran produktu z HTML zamiast nagrań, `.ai/decisions/2026-07-30-…`),
**b-rolle** (Veo z `projects/youtube` + generowane `s01–s12`) i **karty** z generatora
`tools/package.py` (format `youtube`).

Zasada: makieta pokazuje **mechanizm, o którym właśnie mowa**, nie dekorację. Nazwy klientów
nie padają na ekranie — na nagraniach też nie padają.

---

## ep-doram — Meble ogrodowe: zamówienia z Niemiec (11:18)

| ≈ czas | rozdział | grafika / makieta | b-roll |
|---|---|---|---|
| 0:00 | Kolejny przypadek z firmy | belka z imieniem, tytuł odcinka | s08 szwalnia |
| 0:27 | Zamówienia w Excelu od kontrahentów z Niemiec | **makieta: Excel kontrahenta** — jedna pozycja w 5 nazwach (DE/EN) podświetlana po kolei | s04 wydruki |
| 1:13 | Kilka dni klepania, frustracja ludzi | licznik „kilka dni / zamówienie ze 100 pozycjami” | 01 biuro-excele |
| 2:02 | „Dawno nie widziałem takiej radości” — 10 minut | karta przed/po: dni → 10 min | — |
| 2:20 | Dlaczego tak długo: nazwy, ceny, kolumny, 3 kontrahentów | trzy Excele obok siebie, każdy inny układ kolumn | — |
| 3:29 | Kody kreskowe: przeklejała, drukowała | **pętla przeklej → drukuj ×3** (kinetyczny rytm na słowach) | 02 drukarka, s12 etykiety |
| 4:46 | Najpierw jedna baza — boli, ale trzeba | Excele wpadają do jednej bazy (logo Open Mercato) | — |
| 6:01 | Pamięć dla AI | **makieta: ekran dopasowania** — pozycje z kolorem pewności (brak / 80% / 100%), tak jak opisuje to nagranie | — |
| 7:28 | Dygresja: jak uczy się czat | okno czatu, które „zapamiętuje” poprawki | 03 palce-klawiatura |
| 8:36 | 70% → 94% → 95% | **licznik trafności** (gotowa karta `stat`, rozdział `ch-doram-5`) | 09 operator |
| 9:56 | Kody bez AI — 15 minut | **makieta: PDF 40 stron etykiet** generowany po kliknięciu | s12 etykiety |
| 10:33 | Co dalej, zaproszenie do komentarzy | plansza końcowa + pytanie do widzów | — |

## ep-vacuactiv — Agent AI dla właściciela firmy (18:37)

Najdłuższy — kandydat do skrócenia o dygresje (12:15–14:40 o pamięci ChatGPT da się
zastąpić jedną animacją). Decyzja po obejrzeniu przez Mateusza.

| ≈ czas | rozdział | grafika / makieta | b-roll |
|---|---|---|---|
| 0:00 | Asystent AI do zarządzania firmą | tytuł, belka | s11 hala sprzętu |
| 0:30 | ChatGPT zapomina i halucynuje | **animacja: okno kontekstu, które się przepełnia** i wypycha stare wytyczne | 11 noc-monitor |
| 2:06 | Dane w głowach, na kartkach, w mailach | trzy źródła → pusty agent („nie wiem”) | 06 kartka-schemat |
| 3:23 | Mózg firmy: 100–150 GB danych | dysk → manuale, procedury, filmy, oferty → graf wiedzy | 15 serwerownia |
| 4:21 | „Chcę codzienny brief” | **makieta: raport poranny w Telegramie** (karta `chat`) | s10 poranna kawa |
| 5:18 | Open Mercato jako fundament | logo + moduły z pudełka | — |
| 5:38 | Dlaczego gotowce się nie wdrażają | karta: system dopasowany do ludzi, nie odwrotnie | — |
| 7:12 | Excel kierownika produkcji → widoki w systemie | **makieta: Excel i widok tablicy produkcji obok siebie** — prawie ten sam układ | 09 operator |
| 8:56 | Wydruk PDF 1:1 jak dawny Excel | PDF wyjeżdża z widoku | 02 drukarka |
| 9:17 | Codzienny briefing staje się przyjemnością | lista powiadomień: etapy, opóźnienia, kluczowi klienci | s02 telefon |
| 10:24 | Zamówienie z Telegrama w trzy kliknięcia | **makieta: menu bota** — „utwórz / zduplikuj ostatnie” | s01 lotnisko |
| 11:11 | Obsidian + Hermes + Codex | graf: logo Obsidian, OpenAI (Codex), Hermes jako węzeł opisany | 12 terminal-logi |
| 12:15 | Pamięć zapisywana na bieżąco | pliki markdown przybywające w grafie | — |
| 14:48 | Fundamenty i systemy zamknięte | system otwarty (API) vs zamknięty (kłódka) | — |
| 16:58 | Najpierw konsultacje, ludzie, nawyk | plansza końcowa: konsultacja flowbiz.pl | 07 warsztat-stol |

## ep-open-mercato-offers — 8 wdrożeń Open Mercato: oferty (3:31)

| ≈ czas | rozdział | grafika / makieta | b-roll |
|---|---|---|---|
| 0:00 | 8 wdrożeń, firmy handlowe i produkcyjne | licznik 8, logo Open Mercato | — |
| 0:23 | Każdy ma swoją wersję oferty | **pięć PDF-ów z różnymi logo i układem** rozsypanych na stole | s04 wydruki |
| 1:38 | 20 ofert → 3 zamówienia | **lejek 20 → 3** i pytanie „dlaczego?” | — |
| 2:26 | Asystent czyta maile → szkic oferty w 5 min | rozdział `ch-offers-1` już zapakowany | s02 telefon |

## ep-rezon — Pamiątki znad morza: system B2B (7:38)

| ≈ czas | rozdział | grafika / makieta | b-roll |
|---|---|---|---|
| 0:00 | Firma z Kołobrzegu, proces na kartkach | tytuł | s07 pamiątki-tablet |
| 0:36 | Kontrola z księgowości = po fakcie | oś czasu: miesiąc / kwartał / rok vs „na zawołanie” | 17 podpis |
| 1:19 | Centralizacja jako fundament pod AI | rozproszone Excele → jedna baza | — |
| 2:20 | Integracja z PC Business, synchronizacja codzienna | **diagram: PC Business ⇄ Open Mercato raz na dobę** (ceny, zamówienia, stany) | 15 serwerownia |
| 3:04 | Handlowiec objeżdżał całe wybrzeże | **animowana mapa wybrzeża** (Kołobrzeg → Ustka → Łeba) i zima: południe Polski | 04 magazyn-tablet |
| 4:45 | Każda miejscowość ma swój napis | magnes „Ustka” nie pójdzie do Rowów — półprodukt zużyty | s07 pamiątki |
| 5:49 | Panel klienta: sam zamawia, widzi statusy | **makieta: panel klienta B2B** (zamówienie, statusy) | — |
| 6:53 | Handlowiec może zamówić za klienta | dwa panele: klient widzi swoje, handlowiec swoich klientów | — |

## ep-marpasz — Pasza dla zwierząt: etykiety i katalog AI (8:08)

| ≈ czas | rozdział | grafika / makieta | b-roll |
|---|---|---|---|
| 0:00 | Brakuje realnych przypadków AI | tytuł, „kilkanaście przykładów” | — |
| 0:31 | Paczki do 25 kg: cztery worki = cztery etykiety | **makieta: jedno zamówienie rozbite na 4 paczki** | s06 worki-paszy |
| 1:37 | Komentarz → Excel → etykieta, po kolei | pętla kroków z licznikiem zamówień | 03 palce-klawiatura |
| 2:37 | 10–15 min na zamówienie, 100–200 paczek dziennie | mnożenie czasu na tablicy | — |
| 3:15 | Teraz: AI łączy w koszyk, jedno kliknięcie | rozdział `ch-marpasz-2` już zapakowany | s06 worki-paszy |
| 3:53 | ~100 godzin miesięcznie | licznik 100 h | — |
| 5:06 | Katalog AI: faktura → produkty → opisy | **makieta: faktura → lista produktów → opisy pod Allegro / sklep / Erli** (logo Allegro, WordPress) | s04 wydruki |
| 7:27 | AI to dokręcanie śrubek przez kilka miesięcy | karta `quote` | — |

---

## Kolejność budowy (propozycja)

1. Makiety wspólne dla kilku odcinków: **raport/menu bota w Telegramie** (vacuactiv, offers,
   rolki RA*), **ekran dopasowania z kolorami pewności** (doram), **panel klienta B2B** (rezon).
2. Storyboardy `ep-*.json` dla formatu `youtube` — karty i przebitki jak w próbkach.
3. Mapa wybrzeża i diagram synchronizacji — `/motion-graphics`.
4. Render odcinka w częściach (sub-kompozycje po rozdziałach — 11–18 min to za dużo
   na jedną oś czasu GSAP).
