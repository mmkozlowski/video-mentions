# Ujęcia aplikacji do reklam — jak je robimy

Ekrany AdresFlow w spotach **nie są nagrywane ani generowane modelem wideo**.
Są pisane jako HTML i renderowane do MP4 przez [HyperFrames](https://hyperframes.heygen.com).

Dlaczego tak — i jakie są tego koszty — mówi ADR
`../../../.ai/decisions/2026-07-30-ekran-produktu-z-html.md`. Ten plik jest
instrukcją: **jak zrobić kolejne ujęcie, żeby wyszło tak dobrze jak trzy pierwsze.**

```
projects/adresflow/screens/
├── assets/app.css        ← ŹRÓDŁO arkusza (tokeny + komponenty)
├── sync-css.sh           ← rozsyła app.css do projektów
├── kw/       index.html + assets/   → ../build/screens/screen-kw.mp4      (13 s)
├── wycena/   index.html + assets/   → ../build/screens/screen-wycena.mp4  (14 s)
└── oferta/   index.html + assets/   → ../build/screens/screen-oferta.mp4  (15 s)
```

Każdy ekran to **osobny projekt** — `check` i `render` przyjmują katalog, nie plik,
a assety muszą być root-relative (patrz „Bramka" niżej). Stąd trzy kopie `assets/`
i `sync-css.sh` zamiast jednego wspólnego katalogu.

---

## Pętla pracy

```bash
cd projects/adresflow/screens

./render.sh kw                                  # check + render jednego ekranu
npx hyperframes check kw                       # bramka: lint + runtime + layout + motion + kontrast
npx hyperframes snapshot kw --at 1,3,5,8,12    # klatki do obejrzenia + contact-sheet.jpg
npx hyperframes render kw --fps 30 --quality high --output ../build/screens/screen-kw.mp4
```

**Zawsze w tej kolejności.** `check` łapie rzeczy, których nie widać w podglądzie
(nachodzenie tekstu, kontrast, konflikty transformów), a `snapshot` — rzeczy,
których nie złapie żaden automat (martwy dół kadru, kursor na placeholderze,
dziura po dropdownie). Obie te kategorie wystąpiły przy trzech pierwszych ekranach.

Po zmianie `assets/app.css`: `./sync-css.sh`, potem `check` na wszystkich trzech.

---

## Zasada nadrzędna: to ma być czytelne na telefonie

Kadr 1080×1920 ogląda się w Reels na ekranie 6". **Skala aplikacji ×2** — to nie
jest kaprys, to minimum czytelności. Wartości w `assets/app.css` (nie zmniejszaj
ich „bo się nie mieści" — zamiast tego wywal treść):

| Rola | Rozmiar | Uwaga |
|---|---|---|
| Nagłówek ekranu (`.h1`) | 62 px | jedna linia, maks. dwie |
| Podtytuł (`.sub`) | 30 px | |
| Wartość w polu (`.input`) | 40 px | pole ma 104 px wysokości |
| Liczba-bohater (`.stat-value`) | 54 px | `tabular-nums` obowiązkowo |
| Wartość faktu (`.fact-value`) | 32 px | |
| Etykieta (`.fact-label`) | 20 px | wersaliki + `letter-spacing` |
| Margines kadru (`.frame`) | 96 px / 60 px | góra-dół / boki |

Kolumna treści to ~960 px. **Więcej niż 6 pól w siatce 2×3 przestaje być
czytelne** — wtedy podziel ekran na dwa beaty zamiast upychać.

Dane na ekranach są przykładowe, ale **spójne między spotami**: Katowice
Śródmieście, KW `SL1S/00099246/5`, 58,40 m², mediana 12 480 zł/m², 38 transakcji,
cena 729 000 zł. Trzymaj się tego zestawu — widz ogląda spoty jeden po drugim.

---

## Szkielet kompozycji

```html
<div id="root" data-composition-id="kw" data-start="0"
     data-duration="13" data-width="1080" data-height="1920" data-fps="30">

  <div class="stage"></div>              <!-- tło NA DZIECKU, nie na #root -->

  <section class="clip" data-start="0" data-duration="13" data-track-index="1">
    <div class="frame">
      <div class="viewport">             <!-- obszar przycięty -->
        <div id="kw-stack" class="viewport-stack">
          …treść ekranu…
        </div>
      </div>
    </div>
  </section>
</div>

<script>
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true });
  tl.set("#kw-stack", { y: 430 }, 0);   // pozycja wyjściowa PRZEZ TIMELINE
  …
  window.__timelines["kw"] = tl;
</script>
```

Cztery rzeczy są nieoczywiste i każda kosztowała jedno przejście bramki:

1. **Wypełnienie kadru siedzi na `.stage`, nie na `#root`.** Tło na samym korzeniu
   bywa gubione przy składaniu klatek — render wychodzi czarny, mimo że podgląd
   i `snapshot` pokazują poprawnie.
2. **Pozycja wyjściowa przez `tl.set(sel, {y}, 0)`**, nigdy przez inline
   `transform: translateY()`. Inaczej `gsap_css_transform_conflict` — GSAP
   nadpisuje cały transform i element skacze w pierwszej klatce.
3. **Ścieżki root-relative** (`assets/app.css`), nie `../assets/…`.
4. **Jedna timeline na kompozycję**, `paused`, budowana synchronicznie,
   zarejestrowana pod kluczem równym `data-composition-id`.

Zakazane, bo łamie determinizm renderu: `repeat: -1` (używaj skończonej liczby),
animowanie `display`/`visibility`, `Math.random()`, zegar, sieć.

---

## Choreografia, która się sprawdziła

Ekran ma **opowiadać krok po kroku**, nie tylko istnieć. Cztery wzorce z trzech
zbudowanych klipów — każdy do skopiowania:

### 1. Wklejenie zamiast pisania

Nie animuj wpisywania litera po literze. Wymaga mierzenia szerokości znaków, żeby
kursor nie stał w miejscu — kruche i brzydkie. **Wklejenie jest prostsze i mocniej
gra z przekazem** („jedno wklejenie zamiast dziesięciu kliknięć"):

```js
tl.to("#kw-caret", { opacity: 0, duration: 0.45, repeat: 3, yoyo: true,
                     ease: "steps(1)" }, 0.9);        // kursor mruga w pustym polu
tl.to(["#kw-ph-1","#kw-ph-2","#kw-ph-3","#kw-caret"], { opacity: 0, duration: 0.12 }, 2.7);
tl.to(["#kw-val-1","#kw-val-2","#kw-val-3"], { opacity: 1, duration: 0.18 }, 2.72);
tl.fromTo(".ring", { opacity: 0, scale: 1.06 },
                   { opacity: 1, scale: 1, duration: 0.22 }, 2.72);  // błysk ramki
```

Placeholder w polu z kursorem odsuń (`left: 46px`), żeby kursor nie stał na literze.

### 2. Czekanie, które widać

Funkcja trwa (KW ~30–40 s) — pokaż to, zamiast udawać natychmiastowość. Spinner
o **skończonej** liczbie obrotów + pasek postępu na `scaleX`:

```js
tl.to("#kw-spinner",     { rotation: 1440, duration: 1.6, ease: "none" }, 3.8);
tl.to("#kw-loadbar-fill",{ scaleX: 1,      duration: 1.5, ease: "power1.inOut" }, 3.8);
```

### 3. Liczby, które się naliczają

Tween po obiekcie proxy — wartość wynika z czasu, więc jest seek-safe:

```js
function countTo(sel, end, at, dur) {
  const el = document.querySelector(sel), proxy = { v: 0 };
  tl.to(proxy, { v: end, duration: dur, ease: "power2.out",
    onUpdate: () => { el.textContent = Math.round(proxy.v).toLocaleString("pl-PL"); } }, at);
}
countTo("#wy-n-median", 12480, 5.4, 1.1);
```

Element z licznikiem musi mieć `font-variant-numeric: tabular-nums`, inaczej
szerokość skacze przy każdej cyfrze.

### 4. Kroki kreatora jako poziomy pasek

Przełączanie paneli przez `display` jest zabronione. Filmstrip na `translateX`
jest deterministyczny i wygląda jak prawdziwy kreator:

```css
.wiz-track { display: flex; gap: 60px; width: max-content; height: 100%; }
.wiz-panel { width: 960px; display: flex; flex-direction: column; justify-content: center; }
```
```js
const PANEL = 960 + 60;
tl.to("#of-track", { x: -PANEL,     duration: 0.7, ease: "power3.inOut" }, 2.6);
tl.to("#of-track", { x: -PANEL * 2, duration: 0.7, ease: "power3.inOut" }, 5.0);
```

`justify-content: center` na panelu jest ważne — panele mają różną wysokość,
a bez tego krótki krok 1 wisi u góry, a długi krok 4 wypełnia kadr.

---

## Bramka `check` — pułapki, które odrzuca

Wszystkie cztery to rzeczy **poprawne w aplikacji**, których bramka nie przepuszcza
w wideo. Nie walcz z nimi, tylko od razu pisz po jej stronie:

| Zgłoszenie | Przyczyna | Co robić |
|---|---|---|
| kontrast 3,77:1 przy wymaganych 4,5:1 | `--text-3` z aplikacji (`#6b7a92`) na `--elevated` | w kompozycjach `#8593ab` (4,8:1) — i tak było za ciemne na telefonie |
| kontrast 1,45:1 przy wymaganych 3:1 | obramowanie `--border` (`#3a4268`) jako element UI | `--border-strong` `#6d78a8` |
| `text_occluded` / `content_overlap` | treść przewija się **pod** paskiem aplikacji | bramka liczy prostokąty i **ignoruje `overflow: hidden`** — albo pasek jedzie razem z treścią (kw, wycena), albo chrome stoi i rusza się sam element (oferta) |
| `invalid_parent_traversal_in_asset_path` | `../assets/app.css` | root-relative + `sync-css.sh` |

**Ostrzeżenia `container_overflow` i `panel_out_of_canvas` są w porządku** — tak
wygląda przewijana treść w przyciętym viewporcie. Zero **błędów** to warunek renderu.

---

## Wpięcie do spotu

Klip sam w sobie nie jest reklamą — jest ujęciem. Wpina się do `../tools/story.py`:

```python
SHOTS = {
    "ekran-kw":  "screen-kw.mp4",
    "ekran-wyc": "screen-wycena.mp4",
    "ekran-of":  "screen-oferta.mp4",
}
```

**Klip jest dopasowywany czasowo do fraz lektora**, nie odwrotnie — `build_video()`
rozciąga albo ściska ujęcie do sumy przypisanych mu fraz. Praktyczne wnioski:

- Rób klip **dłuższy** niż slot w spocie. Przyspieszenie wygląda snappy,
  spowolnienie powyżej 1,15× wygląda jak slow motion i gasi hook.
- Przy ściśnięciu mocniejszym niż ~2× (oferta: 15 s → 6,3 s) treść zaczyna migać.
  Wtedy albo przypisz ekranowi więcej fraz w `STORIES`, albo skróć choreografię.
- Ostatnie sekundy klipu niech będą **powolnym dojazdem** na wynik — jeśli montaż
  utnie klip wcześniej, nic się nie traci.

---

## Nowy ekran — od czego zacząć

```bash
cd projects/adresflow/screens
cp -R kw nazwa-ekranu && rm -rf nazwa-ekranu/snapshots
```

Potem w `nazwa-ekranu/index.html` podmień `data-composition-id`, klucz
`window.__timelines[…]` i prefiksy `id` (muszą być unikalne w obrębie projektu),
i przepisz treść. Layout bierz z realnego komponentu w `~/Repo/adresflow-v2/apps/web/src` — chodzi o to,
żeby widz zobaczył ten sam ekran, który dostanie po rejestracji.

---

## Format POV — „nagrane telefonem"

Spoty 13–14 to inny format: **ktoś filmuje telefonem swój laptop** i przechodzi
workflow. Bez lektora, jedna przyklejona plansza, muzyka niesie rytm. Wzorzec:
`../assets/reference/inspieracja-*.mp4`. Projekty: `pov-rzut/`, `pov-staging/`,
wspólny arkusz `assets/pov.css`.

Zmierzone: **hook 40 / sustain 97** (staging) i **hook 37 / sustain 100** (rzut) —
najwyższy sustain w całej bibliotece. Format buduje napięcie licznikiem i płaci
transformacją na końcu, więc uwaga rośnie zamiast opadać.

### Co sprzedaje iluzję — w tej kolejności

**1. Geometria kadru.** Laptop MUSI być mniejszy od kadru. Pierwsza wersja miała
ekran na całą szerokość — obudowa wyszła poza krawędź, nie było widać ani ramki,
ani perspektywy, i wyglądało to jak zwykły zapis ekranu. Klawiatura musi stykać
się z dolną krawędzią obudowy, nie wisieć osobno.

Uwaga na kąt klawiatury: przy `rotateX(58deg)` wysokość ścisnęła się do 53 % i
wyszedł z niej pasek zamiast klawiszy. Działa `52deg` przy bloku 1020 px —
wtedy wypełnia kadr do dolnej krawędzi.

**2. Utrata jakości** (w ffmpeg, `../tools/pov.py`):

```
scale=540:960 → noise=alls=7 → scale=1080:1920 → cast → unsharp
```

Szum sypiemy w **niskiej** rozdzielczości — po powiększeniu zlewa się w ziarno
zamiast leżeć na wierzchu jako piksele. Czysty render 1080p czyta się jak zapis
ekranu i zabija format.

**3. Dryf ręki** — kilka **niesynchronicznych** oscylacji o różnych okresach
(3,1 s / 4,7 s / 7,5 s) na jednym wrapperze. Jeden równy tween czyta się jak
animacja, nie jak trzymany telefon.

**4. Pokaż czekanie.** Oryginał trzyma widza licznikiem („1 s" → „49 s") i listą
etapów, które się odhaczają. To jest napięcie spotu — nie skracaj tego.

### `check` tutaj nie obowiązuje

Bramka zgłasza kilkadziesiąt błędów i **to jest poprawne zachowanie**: refleks i
winieta celowo kładą się na tekście (`text_occluded`), a perspektywa powiększa
prostokąty (`content_overlap`). Bramka liczy na prostokątach i nie wie ani o
`overflow: hidden`, ani o zamierzonej stylizacji. **Przy POV weryfikuj
`snapshot`-em.** Przy zwykłych ekranach (`kw`, `wycena`, `oferta`) bramka
obowiązuje normalnie.

### Nowy spot POV

```bash
cp -R pov-rzut pov-<nazwa> && rm -rf pov-<nazwa>/snapshots
# podmień: data-composition-id, klucz window.__timelines, prefiksy id,
# treść ekranu, planszę-hook, obrazki w assets/img/
npx hyperframes snapshot pov-<nazwa> --at 1,4,11,17,21,28   # OGLĄDAJ, nie checkuj
npx hyperframes render pov-<nazwa> --fps 30 --quality high \
  --output ../build/screens/pov-<nazwa>-raw.mp4
python3 ../tools/pov.py pov-<nazwa>                          # grade + muzyka
```

Dopisz spot do `SPOTS` w `../tools/pov.py` i w `../tools/finalize.py`.

**Pilnuj spójności materiału.** Pierwsza wersja stagingu pokazywała „przed" i
„po" z trzech różnych mieszkań — technicznie działało, merytorycznie było
bezwartościowe. Pary w `../assets/photos/` to `przed1`/`po1`, `przed2`/`po2`,
`przed3`/`po3`, `przed-CZxYyuvD`/`po-CF8Pn4Vn`.
