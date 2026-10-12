# flowbiz — klocki animacji (final)

Nieme klocki do montażu reklam i rolek. 30 fps, h.264 (MP4) albo qtrle z alfą (MOV).
Źródła i przebudowa: [`../README.md`](../README.md). Wyrenderowano 2026-10-10, HyperFrames 0.8.145.

| Plik | Format | Długość | Rozmiar |
|---|---|---|---|
| `oferta-chaos-do-systemu-16x9.mp4` | 1920×1080 | 10,0 s | 6,4 MB |
| `oferta-chaos-do-systemu-9x16.mp4` | 1080×1920 | 10,0 s | 6,5 MB |
| `agent-ai-duplikuje-oferte-16x9.mp4` | 1920×1080 | 10,0 s | 5,0 MB |
| `agent-ai-duplikuje-oferte-9x16.mp4` | 1080×1920 | 10,0 s | 3,7 MB |
| `agent-ai-duplikuje-oferte-16x9-alpha.mov` | 1920×1080, alfa | 10,0 s | 91 MB |
| `agent-ai-duplikuje-oferte-9x16-alpha.mov` | 1080×1920, alfa | 10,0 s | 89 MB |
| `system-moduly-przelot-16x9.mp4` | 1920×1080 | 12,0 s | 9,1 MB |
| `system-moduly-przelot-9x16.mp4` | 1080×1920 | 12,0 s | 7,0 MB |
| `integracje-w-jeden-system-16x9.mp4` | 1920×1080 | 10,0 s | 6,1 MB |
| `integracje-w-jeden-system-9x16.mp4` | 1080×1920 | 10,0 s | 5,8 MB |
| `stoper-40-do-5-16x9.mp4` | 1920×1080 | 8,0 s | 2,9 MB |
| `stoper-40-do-5-9x16.mp4` | 1080×1920 | 8,0 s | 2,9 MB |
| `stoper-40-do-5-16x9-alpha.mov` | 1920×1080, alfa | 8,0 s | 71 MB |
| `stoper-40-do-5-9x16-alpha.mov` | 1080×1920, alfa | 8,0 s | 138 MB |

**Pliki `.mov` są poza gitem** (`../.gitignore`) — po klonie odtwórz je
`./screens/render.sh agent-ai-duplikuje-oferte stoper-40-do-5`.

## Co pokazuje każdy klocek i do czego w montażu

### 1. `oferta-chaos-do-systemu` — 10 s
„Przed": arkusze xlsx (`cennik_tkaniny_v7_FINAL.xlsx` z błędem `#ADR!`), karteczki
(„dopłata za nadruk — zapytaj Basię?"), dzwoniący telefon „Nordtex dzwoni". Wszystko
wsiąka w okno **Konfigurator wyceny**, pola wypełniają się (torba 38×42, bawełna 220 g,
ucho długie, nadruk 1 kolor), cena nalicza się do 6 450,00 zł. W miejscu chaosu stoper
40:00 → **5–10 min**. Finał: toast **„Oferta OF/2026/10/042 gotowa"** (~7,0 s).
**Montaż:** środek spotu o ofertowaniu — ilustracja „było tak, jest tak". Najmocniejszy
z klocków jako samodzielna scena.

### 2. `agent-ai-duplikuje-oferte` — 10 s
Okno nowej oferty OF/2026/10/049 (pusta). ⌘K → paleta poleceń, wpisywane
„Duplikuj ofertę z poprzedniego zamówienia Nordtex", agent „myśli" (orb + shimmer),
odhacza kroki, dwie pozycje wpadają do tabeli, suma 11 730,00 zł, toast
**„Skopiowano 2 pozycje z ZAM/2026/0917"** (~7,1 s).
**Montaż:** moment o agencie AI. Wersja z alfą — okno pływa nad nagraniem
(poziom: prawa część kadru; pion: środek).

### 3. `system-moduly-przelot` — 12 s
Przelot przez moduły Open Mercato z etykietą nad oknem: **01 Klienci → 02 Oferty →
03 Magazyn → 04 Portal klienta → 05 Asystent AI**, co ~2,2 s. Aktywny moduł świeci
w sidebarze (w pionie: w pasku ikon), lekka perspektywa i dryf kamery. Finał: odpowiedź
asystenta ze szkicem oferty.
**Montaż:** „co dostajesz" — przegląd systemu; można ciąć po pojedynczym module
(okna: 0,5 / 2,7 / 4,9 / 7,1 / 9,3 s).

### 4. `integracje-w-jeden-system` — 10 s
Kafelki narzędzi tekstem + ogólne piktogramy (wFirma, BaseLinker, Allegro, Gmail, Excel,
Make / n8n — **bez logotypów**) łączą się świecącymi liniami z **„System firmy"**, dane
płyną impulsami. Od ~4,3 s system wypuszcza wyjścia: Zlecenia, Portal B2B, Raporty,
Powiadomienia (Telegram, dymek „Nowe zamówienie · Nordtex").
**Montaż:** odpowiedź na „mamy już swoje narzędzia" — integracja zamiast wymiany.

### 5. `stoper-40-do-5` — 8 s
Tarcza z podziałką, „40 min" zjeżdża do 5, łuk z czerwieni w pomarańcz, hit
**5–10 min** z falą (~3,3 s), napis „Oferta w 5–10 minut", „zamiast 40 minut —
przygotowanie jednej oferty", pigułka „Szwalnia · wdrożenie flowbiz", logo flowbiz (5,0 s).
**Montaż:** zamknięcie spotu / endcard. Wersja alfa 16×9 to układ **lewej tercji z kartą**
pod tekstem — na gadaną głowę, twarz zostaje odsłonięta (sprawdzone kompozytem po h.264).

## Weryfikacja

- `hyperframes check`: 0 błędów na wszystkich 14 projektach; jedno ostrzeżenie
  `nested_structure_needs_subcomposition` na każdym (uwaga o osi czasu w Studio, nie o renderze).
- Klatki obejrzane z gotowych MP4 (po kompresji h.264); nakładki alfa sprawdzone kompozytem
  na zdjęciu przez libx264 yuv420p (`.ai/memory/tekst-nasycony-kolor-na-materiale.md`).

## Treść

Jedyna prawdziwa liczba: **40 min → 5–10 min** (przygotowanie jednej oferty, szwalnia).
Reszta danych fikcyjna i spójna z makietami na flowbiz.pl (Pracownia Bałtyk, Nordtex).
Klocki to grafika z HTML, nie treść AI — nie wymagają oznaczenia z art. 50 ust. 4 AI Act.
