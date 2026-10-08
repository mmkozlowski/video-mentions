# recording-library — baza materiałów wideo z sesji nagraniowych

Fundament pod rolki, reklamy i odcinki YouTube z **własnych nagrań gadanej głowy**
(MacBook, 1280×720, 30 fps, mikrofon na ramieniu). Jedna sesja → kilkadziesiąt
gotowych do obróbki klipów z rankingiem, transkrypcją słowo po słowie i dwoma
kadrami. Grafiki, napisy, mockupy systemu i HyperFrames to **kolejne etapy**,
budowane na tej bazie.

Sesja 1: **8.10.2026**, ~93 min materiału w trzech plikach.

## Co jest w materiale

| Plik źródłowy | Długość | Zawartość |
|---|---|---|
| `nagrywki reklamy i pozniej spokojne flow .mov` | 62:22 | 36 nagrań z promptera (0:40–40:15), freestyle o warsztatach (40:25–42:30), odcinek „8 wdrożeń Open Mercato” (42:37), case study **Rezon** — pamiątki (46:07), case study **Marpasz** — pasza (54:09) |
| `doram.mov` | 11:28 | case study **Doram** — meble ogrodowe, zamówienia z Niemiec |
| `vacuactiv.mov` | 18:46 | case study **Vacuactiv** — agent AI dla właściciela |

Garderoba: **koszula w kratę** do 29. minuty sesji (bloki 1–4, Flowbiz),
przerwa 29:20–30:30, potem **zielone polo** (warsztaty AI Słupsk, blok 6
i case studies). Na nagraniach case studies nazwy klientów nie padają.

Przypisanie klientów potwierdzone w ich repo: Rezon (`~/Repo/rezon-erp-openmercato`
— klienci z Kołobrzegu, wzory, trasy handlowców), Marpasz (`~/Repo/marpasz-system`
— Apilo, Subiekt).

## Struktura

```
recording-library/
├── data/                      ← W GICIE — baza i decyzje
│   ├── clips.json             BAZA: 63 klipy (generowana z tools/edl.py)
│   ├── catalog.md             ranking i karty klipów (generowany)
│   ├── prompter-catalog.json  36 pozycji scenariusza: kod, blok, marka, hook
│   ├── caption-fixes.json     słownik poprawek nazw własnych pod napisy
│   ├── transcripts/           Whisper large-v3-turbo, czasy słów — podstawa cięć
│   └── verify.json            wynik kontroli cięć (tools/verify.py)
├── tools/
│   ├── sources.py             ścieżki do surówki + geometria kadrów
│   ├── edl.py                 ← DECYZJE: co zostaje, oceny, uwagi
│   ├── build_clips.py         edl + transkrypcje → clips.json + catalog.md
│   ├── cut.py                 clips.json → build/library/<id>/
│   ├── verify.py              transkrypcja gotowych plików kontra oczekiwany tekst
│   └── words.py               wypis słów z czasami — do ustawiania cięć
└── build/                     POZA GITEM — odtwarzalne
    ├── library/<id>/          master.mp4 (16:9), vertical.mp4 (9:16), words.json, thumb.jpg
    └── work/                  wav-y, pliki kontrolne
```

Surówka (7 GB) zostaje w `~/Downloads/nagrywki pazdziernik 2026/` — ścieżki
tylko w `tools/sources.py`.

## Pętla pracy

```bash
cd projects/recording-library
python3 tools/words.py session 1110 1135   # gdzie są powtórki? przerwy > 0,45 s oznaczone ‖
# … decyzja → tools/edl.py
python3 tools/build_clips.py               # baza + ranking
python3 tools/cut.py                       # tnie tylko to, co się zmieniło (recipe.json)
python3 tools/verify.py                    # kontrola transkrypcją
```

Cała biblioteka tnie się w ~25 min na M5 Pro (libx264 CRF 17, dwa kadry).

## Rodzaje klipów

| kind | ile | co to jest | kadr |
|---|---|---|---|
| `ad` | 36 | nagranie z promptera, najlepszy dubel, powtórki wycięte | 16:9 + 9:16 |
| `chapter` | 21 | rozdział z case study — kandydat na rolkę | 16:9 + 9:16 |
| `episode` | 5 | pełny odcinek case study pod YouTube | 16:9 |
| `raw` | 1 | freestyle o warsztatach, do przebrania | 16:9 + 9:16 |

**Sklejki** (`ranges` z kilkoma przedziałami) wycinają nieudane początki zdań —
mówca zaczynał zdanie od nowa po pomyłce. Oddechów i potknięć w środku dobrego
dubla **nie wygładzamy** (`.ai/memory/autentycznosc-bije-gladkosc`). Na każdej
sklejce jest 12 ms fade dźwięku.

## Kadr pionowy — dlaczego twarz u góry, a nie pełny ekran

Z 720p pełnoekranowy pion to wycinek 405×720 powiększony ×2,67 — za miękki.
Układ bazowy: wycinek 640×720 → **1080×1215 u góry** (×1,69), a **dolne 705 px
to wolny panel** `#0A0A08` na napisy, wstawki i mockupy. Środek kadru jest
stały per plik (`FACE_CENTER_X`). Śledzenie twarzy to zadanie na kolejny etap.

## Ranking

`hook × 2 + delivery`, maks. 15 pkt. A ≥ 13, B ≥ 11, reszta C. Oceny są
**redakcyjne** — przed wydaniem budżetu na reklamę top 10 hooków trzeba puścić
przez predyktor (`.ai/memory/copy-i-hook`: ból bije opis, ruch w 1. s bije treść).

Pierwsza dziesiątka i kampania AI Słupsk: `data/catalog.md`.

## Stan kontroli (8.10.2026)

`verify.py`: **56 z 58 klipów `ok`** (pełne odcinki niesprawdzane — `--all`).
Dwa `check` są przyjęte świadomie: `ad-15-r5` (pokrycie 89,7 % — dubel z trzema
sklejkami, zapasowy, klasa C) i `ch-rezon-3` („i dzięki temu” w dwóch różnych
zdaniach — naturalna mowa). Dwie sklejki (`ad-14`, `ad-29`) trzeba było ustawić
po ciszy w sygnale, bo Whisper zgubił falstart / przesunął czasy słów
(`.ai/memory/whisper-gubi-falstarty`).

## Znane braki w materiale

- **Ustka (M2)** — zamiast niej powstała wersja regionalna „pomorskie
  i zachodniopomorskie, 40 minut od Ciebie”. Reklamy z nazwą Ustki nie ma.
- **RA3 „Asystent, który nie śpi”** — dwa przejęzyczenia zmieniające sens („i NIE
  siedzi w Twoim Telegramie”). Do ponownego nagrania.
- **01-1 „Kto zmienił cenę”** — „to NIE jest warunek” zamiast „to jest warunek”.
- **Bez numeru telefonu na nagraniu:** M3, M5, M6, R1, R8, RA1, L1, E4 —
  kontakt musi wejść grafiką na planszy końcowej.
- Adres **aislupsk.pl** jest wymawiany niewyraźnie — w napisach zawsze
  poprawiony (`caption-fixes.json`).

## Opakowanie: rolki, reklamy, YouTube (etap 2)

Szczegóły i decyzje: `ai/decisions/2026-10-09-opakowanie-klipow-trzy-formaty-dwie-palety.md`.

```bash
python3 tools/package.py ad-19-ra1 --check          # 3 formaty × 2 palety → build/packaging/
python3 tools/package.py ad-19-ra1 --format reels --palette A --snapshot 2 12 30
python3 tools/package.py ad-19-ra1 --render         # render + −14 LUFS → final/samples/
tools/package_all.sh                                # wszystkie storyboardy
python3 tools/broll_gen.py --list                   # b-rolle generowane: kadr → ożywienie
```

Storyboard (`packaging/storyboards/<clip>.json`) zna typy kart: `title`, `logos`, `stat`
(licznik), `compare` (przed/po), `list` (punkty zapalane na słowach), `chat` (Telegram
z przyciskiem „Zatwierdź”), `quote`, `broll`. Kotwice to słowa z `words.json`
(`"at": "lotnisku"`, `"until": "+2.0"`, `"zapam~"` = prefiks, `"nagle#2"` = drugie wystąpienie).

Logotypy narzędzi: `packaging/brand/logos/*.svg` (20 z systemu wstawek + Telegram, WhatsApp,
Obsidian, Gemini, Allegro, Acrobat, Kalendarz, Dropbox), kolory czytelne na ciemnym tle
w `LOGO_COLORS`.

## Kolejne etapy (kolejka nocna)

Każdy punkt jest niezależny i da się go puścić bez nadzoru:

1. `verify.py --all` — kontrola pełnych odcinków.
2. **Śledzenie twarzy** (OpenCV/MediaPipe w `.venv`) → `FACE_CENTER_X` per
   klatka zamiast stałej; kadr bliżej twarzy dla klipów z gestykulacją.
3. **Napisy** z `words.json` + `caption-fixes.json`, rysowane w Pillow jako
   pas z alfą w dolnym panelu (ten ffmpeg nie ma `drawtext`).
4. **Głośność** −14 LUFS dwuprzebiegowo, osobno od obrazu
   (`.ai/memory/montaz-pulapki-synchronizacji`).
5. **Plansze końcowe** w HyperFrames: Flowbiz (536 507 701, flowbiz.pl)
   i AI Słupsk (aislupsk.pl) — jedna plansza na markę, doklejana na końcu.
6. **Predyktor hooków** na klipach A — pierwsze 16 s.
7. **Odcinki case study**: lista miejsc na mockupy systemu i przejścia grafik,
   na podstawie transkrypcji (rozdziały już są w `CHAPTERS`).
