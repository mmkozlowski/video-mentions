# CLAUDE.md — flowbiz.pl Open Mercato animation

Project-wide rules for editing/extending the scene set.

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
   - `render.js` — `SCENES` array
   - `index.html` — `SCENES` array + clip manifest
   - `scenes.html` — `SCENES` array
5. Test obu trybów:
   - normalny: otwórz scenę osobno, zobacz czy gra
   - chromakey: dopisz `?bg=green` do URL, zobacz czy ciemne teksty mają podkładki

## Edycja treści scen

- **Pojedyncza literówka:** otwórz `compositions/sNN-*.html` — direct-edit działa, klikasz w tekst i przepisujesz.
- **Sprawdzenie wszystkich scen:** otwórz `scenes.html` — siatka 16 miniatur, "Edytuj" na każdej karcie.
- **Po edycji treści ciemnego tekstu poza kartą:** upewnij się że tekst jest opakowany w `<span class="chroma-plate">`.
