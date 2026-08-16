# Handoff: flowbiz.pl — Open Mercato (Build with Matt)

Pakiet zawiera **16 scen animowanych w GSAP** (HTML/CSS/JS, 1920×1080) + skrypt renderujący do **MP4 60fps** przez **Playwright + ffmpeg**. Bez nagrywania ekranu — klatka po klatce, deterministycznie, pixel-perfect.

> **Zadanie dla Claude Code:** odpalić te HTML-e w headless Chromium, wyciąć każdą scenę do MP4, skleić w jeden `open-mercato.mp4` z białymi flash-cutami między scenami. Nie trzeba przepisywać scen do żadnego frameworka — są samowystarczalne.

---

## TL;DR — szybki start

```bash
# 1. Zależności systemowe (jednorazowo)
#    macOS:   brew install ffmpeg node
#    Ubuntu:  sudo apt install ffmpeg nodejs npm
#    Windows: winget install Gyan.FFmpeg OpenJS.NodeJS

# 2. W tym folderze:
npm install
npx playwright install chromium    # ściąga przeglądarkę dla Playwright (~150 MB)

# 3. Render wszystkich scen + sklejony master:
node render.js

# 4. Wynik w ./out/:
#    s01-pol-roku_chroma.mp4 … s16-cta_chroma.mp4   (pojedyncze sceny na zielonym)
#    open-mercato-chromakey.mp4                       ← finalny film, gotowy do keyowania
```

> **Domyślnie renderuje na green screen** (broadcast green #00B140) — od razu nadaje się do wycięcia tła w CapCut / Premiere / Resolve / DaVinci.
> Żeby zrenderować z ciemnym tłem (jak w przeglądarce): `NO_CHROMA=1 node render.js`

**Pojedyncza scena:** `node render.js s09-node-zmienne`
**Inny framerate:** `FPS=30 node render.js` (domyślnie 60)
**Inny kolor klucza:** `CHROMA=blue node render.js` lub `CHROMA=magenta` lub `CHROMA=%23FF1493` (hex z URL-encoded #)
**Ciemne tło (bez chromakey) + białe flashe:** `NO_CHROMA=1 node render.js`
**Zachowaj klatki PNG:** `KEEP_FRAMES=1 node render.js`

---

## Chromakey / Greenscreen mode

Jeśli chcesz wyciąć tło i podłożyć własne (np. w CapCut / Premiere / Resolve / DaVinci):

```bash
# Domyślnie (broadcast green #00B140)
node render.js   # → out/open-mercato-chromakey.mp4

# Inny kolor:
CHROMA=greenpure  node render.js    # #00FF00 (pure digital green)
CHROMA=blue       node render.js    # #0000FF (blue screen)
CHROMA=magenta    node render.js    # #FF00FF (magenta key)
CHROMA=%23FF1493  node render.js    # dowolny hex (URL-encoded #)

# Wyłącz chromakey (ciemne tło + białe flashe):
NO_CHROMA=1 node render.js          # → out/open-mercato.mp4
```

### ⚠️ KRYTYCZNA REGUŁA przy dodawaniu/edycji treści

**Tylko tło sceny (`.stage`) idzie na zielony — wszystkie elementy UI (karty, węzły, bąbelki czatu) ZOSTAJĄ ciemne.**

Ciemne napisy (kolor `#1A`..`#6A`, czyli wszystkie szare i ciemnoszare) na NAGIM tle muszą dostać **ciemną podkładkę**, inaczej po wycięciu zielonego tła w editorze TEKST ZNIKA na transparent.

Robisz to przez owijanie tekstu w `<span class="chroma-plate">`:

```html
<!-- ZŁE — tekst zniknie po keyu na ciemny montaż -->
<div class="s01-label">BUDOWANIE NARZĘDZIA</div>

<!-- DOBRZE — w chromakey dostanie ciemną podkładkę z 16px halo -->
<div class="s01-label">
  <span class="chroma-plate">BUDOWANIE NARZĘDZIA</span>
</div>
```

Klasa `.chroma-plate` jest **no-op w normalnym ciemnym trybie**, aktywuje się tylko gdy `body.chromakey`. Można ją dodawać śmiało wszędzie gdzie pasuje.

**Pełne reguły + decision tree:** patrz `CLAUDE.md` w tym pakiecie.

W chromakey mode **automatycznie**:
- tło stage = kolor klucza (np. zielony)
- siatka, koła i radialne linie tła znikają (bo amber-rgba na zielonym wyglądałoby brzydko)
- watermark `flowbiz.pl` znika
- sceny składają się **twardymi cięciami** (bez białego flash, bo flash by się wykluczył na keyowaniu)

**Test w przeglądarce bez renderowania:** dopisz `?bg=green` do URL dowolnej sceny:
`compositions/s09-node-zmienne.html?bg=green`

---

## Zawartość paczki

```
design_handoff_flowbiz_animation/
├── README.md                          ← ten plik
├── package.json
├── render.js                          ← główny renderer (Playwright + ffmpeg)
│
├── index.html                         ← podgląd: pełen 50s cut z flash transitions
├── scenes.html                        ← przegląd 16 scen w siatce (do edycji tekstu)
│
└── compositions/
    ├── scene-shell.css                ← wspólny szkielet stylów (1920×1080, native 1:1, watermark)
    ├── scene-shell.js                 ← wspólny kontroler (fit + autoplay + recorder)
    ├── recorder.js                    ← (legacy) browser screen-recorder; render.js go nie używa
    │
    ├── s01-pol-roku.html              · 2.5s · "PÓŁ ROKU"
    ├── s02-8-miesiecy.html            · 2.5s · "8 MIESIĘCY" + diagonal strike
    ├── s03-oplacalo-sie.html          · 2.5s · "Opłacało się." (payoff)
    ├── s04-40-minut.html              · 2.5s · "40 MINUT" (before / pain)
    ├── s05-2-minuty.html              · 2.5s · "→ 2 MINUTY" (after / win)
    ├── s06-wiedza-korytarzowa.html    · 2.5s · "WIEDZA KORYTARZOWA"
    ├── s07-node-ryzyko.html           · 4.0s · node graph: osoba → 3 ryzyka
    ├── s08-20-30.html                 · 2.5s · "20–30 zmiennych" + particle burst
    ├── s09-node-zmienne.html          · 4.5s · node graph: centralny + 8 satelitów
    ├── s10-retool-sufit.html          · 2.5s · "RETOOL TRAFIŁ W SUFIT" + impact
    ├── s11-modify-nothing.html        · 2.5s · "MODIFY NOTHING, EXTEND EVERYTHING"
    ├── s12-node-moduly.html           · 4.5s · top-down tree: 5 modułów Open Mercato
    ├── s13-z-systemem.html            · 2.5s · "Z SYSTEMEM ROZMAWIASZ"
    ├── s14-chat-erp.html              · 4.0s · chat AI z efektem pisania
    ├── s15-gigantyczny-przeskok.html  · 2.5s · "GIGANTYCZNY PRZESKOK"
    └── s16-cta.html                   · 2.5s · CTA — "Napisz MERCATO w komentarzu"
```

**Łączny czas finalnego MP4:** ~47.5s animacji + 15× 0.2s flash transitions = **~50.5s**.

---

## Jak to działa pod spodem

Każda scena HTML w `compositions/` wystawia globalny obiekt `window.__sceneTimeline` (GSAP `Timeline` z `paused: true`). Renderer:

1. **Ładuje scenę w headless Chromium** w trybie 1:1 (`viewport 1920×1080`, `deviceScaleFactor: 1`, klasa `body.native` bez transformów skalujących, klasa `body.export` ukrywa UI gracza).
2. **Pauzuje timeline na 0** (`tl.pause(0)`).
3. **Iteruje klatka po klatce** — dla każdego `f ∈ [0, totalFrames)` ustawia `tl.time(f / FPS)`, oddaje przeglądarce klatkę na render i robi `page.screenshot()` jako PNG (`00000.png`, `00001.png`, …).
4. **Koduje PNG → MP4** przez ffmpeg: `libx264`, `yuv420p`, `crf 16`, `preset slow`, `+faststart`. Bliska bezstratności, nadaje się jako master na YouTube.
5. **Skleja sceny** z efektem `xfade=fadewhite:duration=0.2` (białe przejście) w `open-mercato.mp4`. Z `NO_FLASH=1` robi twardy concat bez re-enkodowania.

Renderer dodatkowo injectuje CSS żeby na pewno ukryć:
- pasek odtwarzacza w każdej scenie (`.controls`)
- napis u góry „Build with Matt · Scene XX · …" (`.corner-brand`)

Watermark `flowbiz.pl` (prawy-dolny) **zostaje**. Żeby go wyciąć, odkomentuj linię `/* .watermark { display: none !important; } */` w `render.js`.

---

## Wymagania

| Narzędzie | Wersja | Po co |
|---|---|---|
| Node.js  | ≥ 18    | Uruchamia Playwright + skrypt renderujący |
| Playwright | ^1.48 | Headless Chromium do precyzyjnych zrzutów |
| ffmpeg   | ≥ 4.4   | Kodowanie PNG → H.264 MP4 + xfade transitions |

Po `npm install` MUSISZ jeszcze raz odpalić `npx playwright install chromium` żeby Playwright pobrał swój binarny Chromium. To jednorazowe.

---

## Parametry, które warto znać

### Lista scen w `render.js`

```js
const SCENES = [
  ['s01-pol-roku',            2.5, 0.4],   // [file, duration, tail]
  ['s02-8-miesiecy',          2.5, 0.4],
  // ...
  ['s16-cta',                 2.5, 0.4],
];
```

- **duration** = długość animacji w sekundach (czas, który renderer faktycznie renderuje).
- **tail** = nie używane przez render.js (zostawione dla zgodności z `recorder.js`).
- Kolejność określa kolejność scen w `open-mercato.mp4`. Usunięcie wpisu wycina scenę z finalu.

### ffmpeg — jakość / format

W funkcji `encode()`:

- **Mniejszy plik, niższa jakość:** podnieś `-crf` z 16 na np. 20 (acceptable) lub 23 (web).
- **ProRes do montażu (Premiere / Resolve):** podmień blok kodeka na:
  ```js
  '-c:v', 'prores_ks', '-profile:v', '3',
  '-pix_fmt', 'yuv422p10le',
  // usuń -preset, -crf, -movflags
  ```
  i zmień rozszerzenie wyjścia na `.mov`.
- **DNxHR:** `'-c:v','dnxhd','-profile:v','dnxhr_hq','-pix_fmt','yuv422p'`.

### FPS

Domyślnie 60. Dla YouTube 30 jest wystarczająco gładko i o połowę szybsze do wyrenderowania:
```bash
FPS=30 node render.js
```

---

## Troubleshooting

**„page.waitForFunction: timeout"** — fonty Google Fonts (DM Sans), tabler-icons CDN albo GSAP CDN nie załadowały się w czasie nawigacji. Sprawdź połączenie sieciowe maszyny renderującej. Można też zembedować zasoby lokalnie — wszystkie scene-HTML-e linkują tylko 3 CDN-y i można je ściągnąć do `compositions/vendor/`.

**Czarne ramki / cięte sceny** — coś zostało w `body` po renderze. Sprawdź czy w devtools (`chromium.launch({ headless: false })`) `document.body.classList` zawiera `native` i `export`.

**Klatki się powtarzają / animacja nie skacze** — GSAP cachuje stan. `render.js` używa `tl.time(t, false)` i `tl.pause(0)` na starcie — jeśli to nie wystarcza, dodaj `tl.invalidate()` przed pierwszą klatką.

**ffmpeg: command not found** — zainstaluj systemowo (patrz TL;DR). Renderer wywołuje `ffmpeg` z `PATH`.

**Render trwa długo** — 1080p60, jedna scena 2.5s = 150 klatek × ~150-200ms na zrzut = ~30s. Razem 16 scen + concat = ~10-15 min na typowym MacBooku. Headful tryb (`{headless: false}`) bywa szybszy na niektórych Linuxach z GPU.

**Animacje wyglądają zbyt szybko / wolno** — duration w `SCENES` musi odpowiadać `tl.duration()` w scenie. Jeśli edytujesz timeline, zaktualizuj też wpis w `SCENES`.

---

## Tryb podglądu (przeglądarka)

Otwórz w przeglądarce:

- **`index.html`** — pełny 50s cut, automatyczne odtwarzanie wszystkich 16 scen z flash transitions. Spacja = restart.
- **`scenes.html`** — siatka 16 miniatur (wszystkie sceny grają równocześnie). Hover → przyciski „Replay" i „Edytuj". Klawisz `R` = replay wszystkiego.
- **Pojedyncza scena**, np. `compositions/s09-node-zmienne.html` — z paskiem odtwarzacza, restart, fullscreen, przyciskiem „Nagraj" (in-browser WebM przez getDisplayMedia) i trybem 1:1.

---

## Pliki źródłowe — kontrakt z renderem

Każda scena MUSI:

```js
window.__sceneTimeline = gsapTimelineInstance;  // GSAP Timeline, paused
// CSS: body.native → bez transformów scale
//      body.export → ukryte chrome (.controls, .corner-brand)
```

Wspólny szkielet to `scene-shell.css` + `scene-shell.js`. Nowa scena to ~60 linii inline (treść + timeline) + 1 wywołanie:

```js
flowbizScene.init({
  id: "scene-NN",
  duration: 2.5,
  label: "Scene NN · Tytuł · 2.5s",
  timeline: tl
});
```

Jeśli dodasz scenę — dopisz wpis do `SCENES` w `render.js` i `scenes.html` (do podglądu). I do `index.html` (do pełnego cutu z transitions).

---

## Kontakt / kontekst

- **Brand:** flowbiz.pl
- **Autor materiału:** Build with Matt (YouTube)
- **Tematyka:** case study Open Mercato — pół roku → 8 miesięcy w low-code → "Opłacało się." → 40min vs 2min → wiedza korytarzowa → 20-30 zmiennych → Retool sufit → "Modify nothing, extend everything" → moduły Open Mercato → "Z systemem rozmawiasz" → chat ERP → gigantyczny przeskok → CTA „Napisz MERCATO".
- **Paleta:**
  - `--bg #0A0A08` (background)
  - `--amber #F5A623` (akcent główny)
  - `--light #FAF8F0` (jasny tekst)
  - `--sec1 #5A5450`, `--sec2 #3A3630`, `--sec3 #2E2C28` (drugorzędne szare)
  - `--red #C0553A` (alarm / strike)
  - `--green #6BAA6B` (sukces / zero opłat)
  - `--watermark #1E1C18`
- **Typografia:** DM Sans (Google Fonts), opsz 9–40, wagi 400–900
- **Ikony:** @tabler/icons-webfont 3.5.0
- **Animacja:** GSAP 3.12.5 z CDN (`back.out(1.6/1.7)` dla springów ≈ `cubic-bezier(0.34, 1.56, 0.64, 1)`)

Nic nie wymaga buildowania — HTML/CSS/JS, all CDN.
