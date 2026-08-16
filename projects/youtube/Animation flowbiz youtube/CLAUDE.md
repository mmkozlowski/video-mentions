# CLAUDE.md — flowbiz.pl Open Mercato animation

Project-wide rules for editing/extending the scene set.

## ⚠️ KRYTYCZNA REGUŁA: kształty MUSZĄ mieć własne ciemne tła

**Każdy kontener wizualny (koło, karta, pill, badge, bąbelek, węzeł, …) musi mieć eksplicit `background:#0D0D0B` (lub inny solid, ciemny kolor) — NIE może opierać się na tym że pod spodem widać ciemne tło sceny.**

Powód: w chromakey mode `.stage` staje się zielony. Jeśli kształt ma `background:rgba(245,166,35,0.06)` albo `background:transparent`, po wycięciu green-screen w editorze ze środka kształtu znika tło, ikona/tekst "wisi w powietrzu" na transparent i znika kiedy montaż jest na ciemnym tle.

### ❌ ŹLE
```css
.s09-sat {
  border:1.5px solid rgba(245,166,35,0.2);
  background:rgba(245,166,35,0.02);   /* ← prawie przezroczyste — znika po keyu */
}
.s07-card {
  background:rgba(192,85,58,0.06);    /* ← tekst karty zostaje na transparent */
}
.s12-root {
  background:rgba(245,166,35,0.06);   /* ← napis "OPEN MERCATO" znika */
}
```

### ✅ DOBRZE
```css
.s09-sat {
  border:1.5px solid rgba(245,166,35,0.2);
  background:#0D0D0B;                 /* solid — ikona zawsze ma ciemne tło pod sobą */
}
.s07-card {
  background:#0D0D0B;                 /* tekst zawsze czytelny */
}
.s12-root {
  background:#0D0D0B;
}
```

### Decision tree

1. **Element ma `background:transparent` lub brak `background`?** → musisz dodać `#0D0D0B`, chyba że to layout-wrapper bez wizualnej obecności.
2. **Element ma `background:rgba(..., 0.0X)` (alpha < 0.5)?** → ZAWSZE zamień na `#0D0D0B`. Subtle amber tint przy 0.06 alpha i tak jest praktycznie niewidoczny — koszt zerowy, zysk pełna kompatybilność z chromakey.
3. **Element ma `background:rgba(..., 0.5+)` lub pełny kolor?** → OK, ten alpha jest wystarczający żeby zasłonić green.
4. **Element to dekoracja typu kropka, linia, glow?** → OK, tu można amber/transparent — te elementy same w sobie są kolorem, nie tłem dla treści.

### Dotyczy też wnętrzy ramek

Jeśli masz `<div>` z `border` ale bez `background`, w chromakey wnętrze ramki będzie zielone. Dodaj `background:#0D0D0B`.

### Konwencja kolorystyczna

- Główne tło sceny (`--bg`): `#0A0A08` (tylko `.stage`)
- Tło kart / węzłów / kontenerów: `#0D0D0B` (1 ton jaśniejsze od stage — daje delikatny edge)
- Tło "podniesionych" kart (np. modal-like, hover): `#13110D` (jeszcze 1 ton jaśniejsze)
- NIE używaj amber-tinted backgrounds dla kontenerów. Akcent rób przez border + glow + ikonę.

---

## Project structure

- `compositions/sNN-*.html` — 16 scen GSAP, każda samowystarczalna (1920×1080).
- `compositions/scene-shell.css` + `scene-shell.js` — wspólny chrome (fit, native 1:1, pasek odtwarzacza, watermark, chromakey).
- `compositions/recorder.js` — legacy in-browser recorder (getDisplayMedia).
- `index.html` — automatyczne odtwarzanie 16 scen w sekwencji z flash-through-white.
- `scenes.html` — siatka 16 miniatur do podglądu i edycji.
- `render.js` — Playwright + ffmpeg, klatka-po-klatce do MP4.
- `design_handoff_flowbiz_animation/` — gotowa paczka do Claude Code z README PL.

## Scene contract (każda scena MUSI to spełniać)

```js
window.__sceneTimeline = gsapTimelineInstance;  // GSAP Timeline, paused
flowbizScene.init({
  id: "scene-NN",
  duration: <seconds>,
  label: "Scene NN · Tytuł · Xs",
  timeline: tl
});
```

CSS hooks (z scene-shell.css):
- `body.native` → bez transformów scale (renderer 1:1)
- `body.export` → ukryte chrome (.controls, .corner-brand) — tylko do renderu
- `body.chromakey` → tło stage zielone, siatki/rays/watermark schowane

## Paleta

```
--bg        #0A0A08    background sceny (też kolor podkładek chromakey)
--amber     #F5A623    akcent główny
--light     #FAF8F0    jasny tekst
--sec1      #5A5450    średnio-ciemny szary
--sec2      #3A3630    ciemny szary
--sec3      #2E2C28    bardzo ciemny szary
--red       #C0553A    alarm / strike / error
--green     #6BAA6B    sukces / zero opłat
--watermark #1E1C18    watermark text
```

Typografia: **DM Sans** (Google Fonts), wagi 400–900, opsz 9–40.
Ikony: **@tabler/icons-webfont 3.5.0** (`<i class="ti ti-...">`).
Spring ease: `back.out(1.6)` lub `back.out(1.7)` (≈ cubic-bezier(0.34, 1.56, 0.64, 1)).

## ⚠️ KRYTYCZNA REGUŁA: chromakey (green screen)

Renderer domyślnie pakuje sceny na **broadcast green #00B140** żeby user mógł wyciąć tło w editorze. To wymaga **dyscypliny przy dodawaniu treści do scen**.

### Co zostaje ciemne (jest OK):
- **Karty, węzły, bąbelki czatu** — wszystko co ma własne `background:#0D0D0B` / `rgba(245,166,35,0.06)` etc. Te elementy są na ciemnym i tak, więc po wycięciu zielonego dalej widać tekst na ciemnej karcie.
- **Jasny tekst** (#FAF8F0) — bright na transparent jest wyraźny po wycięciu.
- **Amber tekst** (#F5A623) — kolor akcentu, dobrze widoczny po keyowaniu.
- **Czerwony/zielony tekst** (#C0553A, #6BAA6B) — kolory akcentów.

### Co zniknie po wycięciu green (BIG PROBLEM):
- **Ciemne napisy bez własnej karty/podkładki:**
  - kolor `#1A1916`, `#2E2C28`, `#3A3630`, `#5A5450` — szare i ciemnoszare
  - umieszczone bezpośrednio w `.scene` (nie w `.s07-card`, `.s09-sat`, `.s14-chat` itp.)
  - po `chroma key out` zostają ciemne piksele na transparent — bardzo mało widoczne, jak user ma ciemny montaż = NIEWIDOCZNE

### ROZWIĄZANIE: klasa `.chroma-plate` (+ opcjonalny `.amber`)

Dla każdego "samotnego ciemnego napisu" w scenie zawijasz tekst w span z klasą `chroma-plate`. W chromakey mode dostanie **ciemną podkładkę + override koloru tekstu na biały** (domyślnie) lub na amber (z modyfikatorem `.amber`).

```html
<!-- ŹLE — tekst zniknie na transparent po keyu -->
<div class="s01-label">BUDOWANIE NARZĘDZIA</div>

<!-- DOBRZE (biały tekst, dla body/podpisów) -->
<div class="s01-label">
  <span class="chroma-plate">BUDOWANIE NARZĘDZIA</span>
</div>

<!-- DOBRZE (amber tekst, dla label-i / akcentów) -->
<div class="s01-label">
  <span class="chroma-plate amber">BUDOWANIE NARZĘDZIA</span>
</div>
```

`.chroma-plate` zachowuje się w dwóch trybach:
- **Normalny ciemny render:** override koloru tekstu (biały lub amber) jest **zawsze aktywny** — żeby finalne kolory były spójne między trybami. Brak podkładki (niepotrzebna, tło jest ciemne).
- **Chromakey mode** (`body.chromakey`): dodatkowo doklejona ciemna podkładka z 16px halo, żeby tekst nie zniknął po wycięciu zielonego.

To znaczy: scena wygląda identycznie w obu trybach (biały/amber tekst), tylko w chromakey dochodzi ciemny prostokąt za tekstem. Edytując tekst, widzisz od razu finalny kolor — bez zgadywania.

Implementacja (`scene-shell.css`):
```css
/* Color override applies ALWAYS (both normal dark mode and chromakey). */
.chroma-plate { color:#FAF8F0; }
.chroma-plate.amber { color:#F5A623; }

/* Plate background + halo activates ONLY in chromakey mode. */
body.chromakey .chroma-plate {
  display:inline-block;
  background:#0A0A08;
  box-shadow:0 0 0 16px #0A0A08;   /* 16px halo */
}
```

### Decision tree — KIEDY chroma-plate i jaki wariant:

1. Czy tekst jest **wewnątrz karty/węzła/bąbelka** (ma własne `background` na elemencie-rodzicu)? → **NIE TRZEBA** chroma-plate.
2. Czy tekst jest **jasny** (#FAF8F0, biały) na nagim tle? → NIE TRZEBA — biały bright tekst dobrze widoczny po keyu.
3. Czy tekst jest **amber/red/green** (akcent) na nagim tle? → NIE TRZEBA — kolory akcentów dobrze widoczne.
4. Czy tekst jest **szary/ciemnoszary** (#1A → #6A) i NIE jest w karcie? → **TAK, wrap w `<span class="chroma-plate">`**.
   - Dla **label-i / eyebrow / brand / akcentów** → `<span class="chroma-plate amber">`
   - Dla **body / podpisów / długich zdań** → `<span class="chroma-plate">` (domyślnie biały)

### Reguła rytmu wizualnego:
Naprzemiennie używaj amber i białego między scenami i w obrębie sceny — żeby keyowane wideo nie wyglądało monotonnie. Generalna zasada: krótkie label-y `.amber`, dłuższe podpisy `.chroma-plate` (białe).

### Edge cases:

- **Wieloliniowy tekst:** wrap całą zawartość w jeden span — `box-shadow` halo otoczy bounding box.
- **Tekst z `text-shadow` glow:** chroma-plate przytnie glow do bounding boxu + 16px halo. Jeśli to widać brzydko, zwiększ halo dla tego elementu inline:
  ```html
  <span class="chroma-plate" style="box-shadow:0 0 0 32px #0A0A08">...</span>
  ```
- **Tekst z animacją `translateX`/`translateY` z dużymi offsetami:** plate animuje się razem z tekstem — OK.
- **SVG paths (linie łączące węzły):** zostają widoczne na green. Po keyu są floating amber liniami. Akceptowalne wizualnie.

## Renderowanie

```bash
node render.js                          # chromakey domyślnie → out/open-mercato-chromakey.mp4
NO_CHROMA=1 node render.js              # ciemny render z flash → out/open-mercato.mp4
node render.js sNN-name                 # pojedyncza scena
FPS=30 node render.js                   # 30 zamiast 60
CHROMA=blue|magenta|%23RRGGBB node ...  # inny kolor klucza
```

## Dodawanie nowej sceny

1. Skopiuj plik bliskiej sceny (np. `s01-pol-roku.html`) i nazwij `sNN-<slug>.html`.
2. Zmień:
   - `<title>`
   - klasy CSS z `s01-` → `sNN-`
   - treść w `.scene`
   - timeline GSAP
   - `flowbizScene.init({ id:"scene-NN", duration:X, label:"…", timeline:tl })`
3. **Dla każdego nowego ciemnego/szarego tekstu poza kartami: dodaj `<span class="chroma-plate">`** (patrz decision tree wyżej).
4. Dopisz do:
   - ~~`render.js` — `SCENES` array~~ ← już NIE trzeba, render.js auto-discoveruje z `compositions/*.html`
   - `index.html` — `SCENES` array + clip manifest (jeśli ma być w sekwencji)
   - `scenes.html` — `SCENES` array (jeśli ma być w siatce miniatur)
5. Test obu trybów:
   - normalny: otwórz scenę osobno, zobacz czy gra
   - chromakey: dopisz `?bg=green` do URL, zobacz czy ciemne teksty mają podkładki

## Edycja treści scen

- **Pojedyncza literówka:** otwórz `compositions/sNN-*.html` — direct-edit działa, klikasz w tekst i przepisujesz.
- **Sprawdzenie wszystkich scen:** otwórz `scenes.html` — siatka 16 miniatur, "Edytuj" na każdej karcie.
- **Po edycji treści ciemnego tekstu poza kartą:** upewnij się że tekst jest opakowany w `<span class="chroma-plate">`.

## Pattern: ścieżka panoramiczna (pan-path scene)

Wzorzec sceny gdzie **kamera przesuwa canvas w bok / po krzywej**, a ikony pojawiają się jak stacje połączone linią. Daje efekt "podróży" przez proces. Dwa działające warianty referencyjne:

- `compositions/test-pan-path.html` — **prosta linia pozioma**, równe odstępy, ostre stacje (4 węzły).
- `compositions/test-pan-path-v2.html` — **krzywa bezier + abstrakcyjne rozmieszczenie** (XY scatter), pan w dwóch osiach, dekoracyjne kropki, pulse jadący po ścieżce.

### Architektura

```
.scene
  ├── .tpp-eyebrow         ← fixed chrome (NIE w trekcie!) eyebrow u góry
  ├── .tpp-track           ← width >> 1920px, animowany translate(x,y)
  │     ├── svg.tpp-svg    ← curved path (bg dashed + fg solid amber)
  │     ├── .tpp-node × N  ← absolute left/top w koordynatach treku
  │     ├── .tpp-label × N ← absolute, alternuje above/below per labelBelow
  │     ├── .tpp-deco × M  ← opcjonalne dekoracje wzdłuż ścieżki
  │     └── .tpp-pulse     ← jeździ po ścieżce (getPointAtLength)
  ├── .tpp-fade.left/right ← gradient masks do zakrycia hard-cutów (display:none w chromakey)
  └── .tpp-counter         ← fixed chrome, NIE w trekcie
```

### Kluczowe wzory

**Mapping stacji kamery:** `STATIONS[i] = { x: 960 - node.x, y: 540 - node.y }` — minus, bo przesuwamy track w przeciwną stronę.

**Budowanie krzywej (Catmull-Rom → cubic bezier):**
```js
function buildCurvePath(pts, k=0.35){
  let d = `M ${pts[0].x} ${pts[0].y}`;
  for (let i=0; i<pts.length-1; i++){
    const p0=pts[i-1]||pts[i], p1=pts[i], p2=pts[i+1], p3=pts[i+2]||p2;
    const c1x=p1.x+(p2.x-p0.x)*k, c1y=p1.y+(p2.y-p0.y)*k;
    const c2x=p2.x-(p3.x-p1.x)*k, c2y=p2.y-(p3.y-p1.y)*k;
    d += ` C ${c1x} ${c1y}, ${c2x} ${c2y}, ${p2.x} ${p2.y}`;
  }
  return d;
}
```
`k` ≈ 0.35 daje płynną krzywą; >0.5 robi pętle, <0.2 prawie prosto.

**Sampling NODE_T (gdzie jest każdy węzeł na ścieżce, 0..1):** użyj `path.getPointAtLength()` z 600 próbkami i pick najbliższy do każdej pozycji węzła. Potrzebne żeby `stroke-dashoffset` i pulse zatrzymywały się dokładnie na węźle.

**Animacja linii:** `pathFg` ma `pathLength="1"` + `stroke-dasharray="1"`. `stroke-dashoffset` animowany od `1` (nic) do `0` (cała). Per krok: `1 - NODE_T[i]`.

**Pulse po ścieżce:** osobne dummy obiekt `{t: NODE_T[i-1]}` tween-ujemy do `NODE_T[i]`, w `onUpdate` ustawiamy `gsap.set('#pulse', { x: p.x, y: p.y })` używając `getPointAtLength(t * totalLen)`.

**Rytm timeline'a:**
- intro 0.0–1.2s (eyebrow, counter, node 0 spring, pulse init)
- `STEP = 1.55s` na każdą kolejną stację:
  - `t+0.00` — pan startuje (0.95s, `power2.inOut`)
  - `t+0.00` — line draw (0.95s, sync z pan-em)
  - `t+0.00` — pulse jedzie (0.95s, sync)
  - `t+0.50` — nowy node spring-in (`back.out(1.7)`)
  - `t+0.85` — `activate(i)` (przerzucenie klasy `.active`)
  - `t+0.95` — label fade
- outro: pulse + active node breath (0.9s yoyo)

### ⚠️ Chromakey discipline dla pan-path scen

Wszystko co user kazał pamiętać, plus własne uwagi:

1. **Środek węzła (`.tpp-node`) MUSI mieć `background:#0D0D0B`** — eksplicit, nie polegaj na dziedziczeniu. Inaczej po wycięciu greenu ikona "wisi" w powietrzu bez koła pod sobą. Border amber + dark fill = ikona zawsze ma kontrast.

2. **Gradient-fade na bokach (`.tpp-fade`) → `display:none` w `body.chromakey`** — w trybie chromakey nie ma sensu maskować bo i tak całe tło jest green key. Hard-cuty schowają się po keyu.

3. **Label-e (number/title/desc) poza kartą:**
   - numer (amber, krótki) → `<span class="chroma-plate amber">01</span>`
   - title (`#FAF8F0` jasny) → BEZ plate, biały na transparent po keyu jest OK
   - desc (jasny z opacity) → też zazwyczaj OK, ale jak masz `color:#5A5450` to MUSI być plate

4. **Eyebrow + counter** (poza trekiem) → wrap w `chroma-plate` (amber dla eyebrow, default biały dla counter).

5. **SVG path (`pathFg`, `pathBg`)** → amber, widoczne po keyu. OK.

6. **Dekoracyjne kropki (`.tpp-deco`)** → amber, OK.

7. **Grid background (`svg.grid`)** → już schowany przez globalny chromakey CSS w `scene-shell.js`.

### Defensywny CSS dla każdej nowej pan-path sceny

Wklej do `<style>` żeby node ZAWSZE miał ciemne wnętrze, nawet jak ktoś będzie tweakował:

```css
.tpp-node{
  background:#0D0D0B;   /* explicit, nie transparent */
  /* w chromakey i tak zostaje ciemne — bo .stage staje się green
     ale node ma własny bg, więc ikona dostaje ciemne tło */
}
body.chromakey .tpp-node{
  /* defensive override jakby ktoś przypadkiem dał transparent gdzie indziej */
  background:#0D0D0B !important;
}
```

### Tweaks do iteracji

- `NODES[]` — pozycje x/y, ikony, copy
- `k` w `buildCurvePath` — agresywność krzywej (0.2 prawie prosto / 0.35 płynnie / 0.6 pętle)
- `STEP` — czas na stację (1.2 szybko / 1.55 default / 2.0 spokojnie)
- ease pan-u: `power2.inOut` (default), `power3.inOut` (mocniejszy settle), `expo.inOut` (długi glide, ostry stop)
- `GAP` (v1) — odległość między węzłami w linii prostej
- `.tpp-fade` width 220–280px — szerokość gradient-mask na bokach
- gęstość `NUM_DECOS` — 18 default, 0 wyłącza dekoracje

---

## Znaki marek — `logos.css`

Gdy w skrypcie pada nazwa narzędzia (Claude, Codex, Excel, HubSpot, Salesforce, n8n, Zapier,
Make, GitHub, Open Mercato), scena pokazuje **prawdziwy znak marki**, nie ikonkę Tablera.
Rozpoznawalny logotyp robi w ułamku sekundy to, na co napis potrzebuje całego zdania.

```html
<i class="logo logo-claude"></i>                         <!-- kolor marki -->
<i class="logo logo-github" style="color:#F5A623"></i>    <!-- kolor sceny -->
<span class="logo-lockup"><i class="logo logo-n8n"></i> n8n</span>
```

Trzy rzeczy, o których trzeba pamiętać:

1. **`logos.css` jest generowane** — `assets/logos/build-logos-css.sh`. Ręczna edycja przepada
   przy następnym buildzie. Nowe logo: SVG do `assets/logos/`, kolor do tablicy `BRAND`, build.
2. **Kolor marki musi być czytelny na `#0A0A08`.** Oficjalny GitHub to `#181717`, Notion `#000000`,
   OpenAI `#412991` — wszystkie znikają na naszym tle. W `BRAND` siedzą więc warianty jasne, i to
   jest celowe, nie pomyłka.
3. **Logo to maska pokolorowana `background-color`**, więc zachowuje się jak tekst: ciemny wariant
   poza kartą wymaga `.chroma-plate`, tak samo jak reszta ciemnych elementów. Wszystkie kolory
   w `BRAND` są jasne albo nasycone, więc dziś to nie gryzie — ale po dodaniu ciemnego logo
   sprawdź render `_chroma`, nie tylko ciemny.

Znak z jednym plikiem SVG jest **spłaszczany do jednej barwy** — maska nie zna kolorów źródła.
Loga wielobarwne (Slack, Google Drive) tracą przez to swoją paletę; jeśli w scenie ma być
oryginał, wstaw `<img>` zamiast maski i pamiętaj o własnym tle pod chromakey.
