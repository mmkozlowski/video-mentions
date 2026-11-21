# s10-po-co-om — pionowe shorty z odcinka „Po co Open Mercato"

Reels/Shorts **1080×1920, 30 fps** wycinane ze zmontowanego odcinka YouTube
(`~/Youtube Projects/S-10 - czym jest OM/Postprodukcja/Odcinek-PO_CO_OPEN_MERCATO.mp4`,
3840×2160, 11:48). Odbiorca: osoby biznesowe zainteresowane Open Mercato.

Czym to się różni od `projects/shorts IG`: źródłem nie jest surówka z telefonu,
tylko **zmontowany odcinek** — pauzy są już wycięte, więc nie ma tu progów ciszy
ani `edl.py`. Zostaje dobór fragmentów po transkrypcji i kadrowanie 16:9 → 9:16.
Etapy i zasada akceptacji są te same co w `shorts IG`:
**etap 1 (surowy skład) → akceptacja → etap 2 (napisy, grafiki, plansze)**.

## Pętla pracy

```bash
cd projects/youtube/shorts/s10-po-co-om

# ── ETAP 1: surowy skład do akceptacji ────────────────────────────────────
# 1. transkrypcja odcinka ze znacznikami słów (raz)
ffmpeg -y -v error -i "$SRC" -vn -ac 1 -ar 16000 build/work/episode.wav
mlx_whisper build/work/episode.wav --model mlx-community/whisper-large-v3-turbo \
  --language pl --word-timestamps True --output-format json \
  --output-dir build/work --output-name episode

# 2. surowe składy (fragmenty w SHORTS w tools/rough.py)
python3 tools/rough.py          # wszystkie → build/rough/*.mp4

# 3. kontrola składu transkrypcją GOTOWEJ osi (nie odsłuchem)
#    — urwane słowo albo dziura > 0,45 s widać w wypisie od razu;
#    te transkrypcje (build/work/s?-*.json) są potem źródłem napisów

# ── ETAP 2: po akceptacji — obraz, warstwy, montaż ────────────────────────
python3 tools/edl.py                     # walidacja planu zoomów
python3 tools/picture.py                 # obraz z punch-inami + dźwięk → build/picture/
node tools/anim/render.cjs kopie-9x16 dostep-9x16   # pionowe plansze → build/anim/
python3.13 tools/style.py                # napisy/tytuły/plakietki/outra → build/overlays/
python3 tools/assemble.py                # kompozycja + loudnorm → build/final-nomusic/

# ── ETAP 3: muzyka, osobno i na końcu ─────────────────────────────────────
python3 tools/music.py --pick            # ranking ~/Repo/video-mentions/music
python3 tools/music.py "the_mountain"    # miks → final/*.mp4

# ── ETAP 4: QC hooków w Higgsfield virality_predictor (DARMOWY, 0 kredytów)
# utnij pierwsze 15,8 s finału, media_upload → curl PUT → media_confirm →
# virality_predictor create (max 2 równolegle). Czytaj hook/sustain/viral
# + krzywą visual_occipital. Szczegóły i benchmarki:
# .ai/memory/virality-predictor-w-procesie-shortow.md
```

Uwagi środowiskowe: `style.py` wymaga Pillow — jest w `python3.13` z Homebrew
(domyślny `python3` = 3.14 bez Pillow). `render.cjs` bierze Playwrighta
z `~/.claude/tools/flowbiz-docgen/node_modules` (chromium we wspólnym cache).

## Etap 2 — co się dzieje z obrazem

- **Zoomy**: statyczne, różne w sąsiednich ujęciach, przełączane na początkach
  zdań (`zooms` w `tools/edl.py`; WIDE 1.0 / CLOSE 1.18 / TIGHT 1.30 na finał).
  Na wypalonych planszach/przebitkach odcinka zoom stoi na 1.0.
- **Dźwięk**: cięty sample-exact z jednej ścieżki źródła z tych samych granic
  klatek co obraz (`picture.py`) — bez paddingu AAC, który w rough dawał
  do 90 ms rozjazdu na trzech szwach.
- **Pionowe animacje** (`tools/anim/`): plansze odcinka komponowane pod 16:9
  gubią boki w cropie, więc „Ten sam plik. Trzy wersje." (s2, 10,3–28,2 s)
  i „100% dostępu do kodu" (s4, 17,1–24,6 s) są przebudowane pod 1080×1920
  i wjeżdżają jako nakładki. Treść żyje NAD pasem napisów (y<1140). Render:
  własny `render.cjs` (wzór: `Animation flowbiz youtube/render.js`), reguły
  ciemnych teł kontenerów z tamtejszego CLAUDE.md obowiązują.
- **Napisy**: mechanika okien importowana wprost z
  `projects/shorts IG/tools/style.py` (bursztynowe aktywne słowo, kryjąca
  podkładka, okno nigdy przez kropkę). Poprawki zapisu per short w FIXES —
  m.in. „Cloud"→„Claude", „SASE"→„SaaS-y", „film"→„firm".
- **Typografia warstw: DM Sans** (`tools/fonts/`), nie Poppins — shorty
  studyjne mówią fontem grafik odcinka, nie stylem reelsów z telefonu
  (`.ai/memory/shorty-studyjne-vs-reelsy-ig`).
- **Hook**: cold-open ~1,35 s — pytanie na rozmytym, przyciemnionym kadrze
  ZANIM zacznie się mowa (`INTRO` w `edl.py`, `intro_clip()` w `assemble.py`).
  Tytuł równoległy do napisów się zlewał — odrzucone przy odbiorze.
- **Stemple kinetyczne**: duże hasła w różnych miejscach/rozmiarach z rotacją
  i wejściem slide+fade (`STAMPS` w `edl.py`).
- **Tempo**: całość ×1,01 (`SPEED` w `assemble.py`), przed loudnorm.
- **Screencast**: span `SCREEN` w planie zoomów = pełny kadr 16:9 na całą
  szerokość + blur-fill, nie pionowy crop.
- **Finał**: pytanie na żywym kadrze (ogon źródła 2,8 s po ostatnim
  fragmencie, wyciszony — podkład wychodzi tam na wierzch), logo flowbiz.

Pełna lista reguł odbioru: `.ai/memory/shorty-studyjne-vs-reelsy-ig.md`.

## EDL — cztery shorty (etap 1, do akceptacji)

Granice cięć potwierdzone na znacznikach SŁÓW z Whispera, nie na segmentach.
Czasy = sekundy odcinka źródłowego.

| # | Roboczy tytuł / hook | Fragmenty | Długość |
|---|---|---|---|
| s1 | **Po co Ci Open Mercato, skoro Excel działa?** — pattern interrupt: chwali konkurencję, potem pyta | 0,00–36,90 + 39,94–62,55 | ~60 s |
| s2 | **Wchodzę do firm i widzę Excela** — ból: ten sam plik w kilku wersjach, ukrywane marże | 175,16–203,35 + 237,30–257,50 | ~48 s |
| s3 | **Komu ODRADZAM Open Mercato** — transparentność, jeden ciągły fragment, zero szwów | 546,65–595,85 | ~49 s |
| s4 | **„Co tu jest wow?" — 100% dostępu do kodu** — anegdota z kolegą z branży + „to nie jest Make/N8N/Zapier" + puenta o własności kodu | 116,20–146,95 + 296,90–310,78 + 280,30–287,30 | ~52 s |

Dlaczego te, a nie inne (kryteria z `.ai/memory/copy-i-hook.md` — ból bije opis
produktu, pierwsze 3 s decydują):

- **s1** otwiera odcinek i był pisany jako hook — „Excel działa, no-code działa…
  więc po co wam Open Mercato?" broni się bez kontekstu.
- **s2** to czysty ból odbiorcy (chaos Exceli), bez słowa o produkcie do ~40 s.
- **s3** gra przeciwko oczekiwaniu (sprzedawca odradza własny produkt) —
  najmocniejszy sygnał wiarygodności w całym odcinku.
- **s4** odpowiada na pytanie, które zadaje każdy techniczny widz („czym to się
  różni od no-code"), i kończy się najlepszym one-linerem odcinka:
  „Kupują własność kodu i niezależność".

Rezerwa (nie weszły, do ewentualnej podmiany): „trzy zarzuty" 500,18–546,52
(AI umie budować software / boilerplate / kto weźmie odpowiedzialność) oraz
„cztery branże, jeden fundament" 633,66–667,48 + rada z demo do 693,98
(„…których sam nie napiszesz w tydzień").

## Kadrowanie

Mówca siedzi na osi kadru → **czysty centralny crop 1214×2160 → 1080×1920**,
bez skalowania proporcji (`.ai/memory/nigdy-nie-rozciagaj-kadru`). Uwaga na
etap 2: wstawki graficzne odcinka (plansza Make/n8n/Zapier ~297–303 s, plansza
„100% dostępu do kodu") są komponowane pod 16:9 — w centralnym cropie gubią
boczne loga. Te miejsca w etapie 2 dostają własne pionowe plansze z zasobów
repo (`projects/youtube/Animation flowbiz youtube/`), nie crop z odcinka.

## Struktura

```
tools/rough.py       cięcie surowego składu (etap 1)
tools/edl.py         fragmenty + plan zoomów (dane etapu 2)
tools/picture.py     obraz z punch-inami + dźwięk sample-exact
tools/anim/          pionowe kompozycje GSAP + render.cjs (Playwright)
tools/style.py       napisy/tytuły/plakietki/outra (Pillow, python3.13)
tools/assemble.py    kompozycja + ogon + loudnorm
tools/music.py       podkład z ~/Repo/video-mentions/music
build/               wszystko robocze (poza gitem): rough, picture, anim,
                     overlays, final-nomusic, work
final/               gotowe shorty (deliverable)
```
