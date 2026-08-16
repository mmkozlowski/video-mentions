# YouTube — wstawki do odcinków Mateusza

Kanał YouTube, seria o OpenMercato. **Jedyny projekt w tym repo w 16:9** (reszta jest 9:16 pod TikToka).

Plan wstawek, przypisanie do miejsc w skryptach i lista ujęć do nagrania:
`Obsidian Vault → marketing/content/youtube/_plan-broll.md`.

## Czym to się różni od pozostałych projektów

**Nie ma tu montażu.** Nie składamy gotowego spotu — produkujemy **pojedyncze wstawki MP4**,
które Mateusz wrzuca do montażu odcinka po swojej stronie. Dlatego z pipeline'u AdresFlow
nie używamy `story.py`, `voice.py` ani `finalize.py`.

Wstawki są renderowane **na zielonym tle (`#00B140`)** i wycinane w montażu — nie zastępują
obrazu, tylko wchodzą na gadaną głowę.

## Struktura

```
Animation flowbiz youtube/     ← system animacji (istniał przed tym projektem)
├── CLAUDE.md                  ← REGUŁY: chromakey, chroma-plate, pan-path. Czytaj przed edycją.
├── compositions/
│   ├── scene-shell.css/js     wspólny chrome
│   ├── logos.css              WYGENEROWANE — znaki marek jako maski CSS
│   ├── sNN-*.html             16 scen z PIERWSZEGO odcinka
│   ├── eNN-MM-*.html          wstawki do kolejnych odcinków (e01, e08, …)
│   └── test-pan-path*.html    wzorce ścieżki panoramicznej
├── assets/logos/              SVG marek + build-logos-css.sh
├── render.js                  Playwright + ffmpeg, klatka po klatce
├── sfx/                       paczka dźwięków, arkusz czasów, build-tracks.sh
└── out/                       rendery, POZA gitem (odtwarzalne)
ai/                            decyzje tego projektu
assets/                        nagrania ekranu od Mateusza
final/                         wstawki zaakceptowane, do montażu
```

## Znaki marek w scenach

Kiedy Mateusz wymienia narzędzie z nazwy — Claude, Excel, HubSpot, n8n — na ekranie ma stać
**jego znak**, nie ikonka-zastępnik. Logotypy leżą w `assets/logos/` i wjeżdżają do scen przez
`logos.css`:

```html
<i class="logo logo-claude"></i>                        <!-- w kolorze marki -->
<i class="logo logo-github" style="color:#F5A623"></i>   <!-- w kolorze sceny -->
<span class="logo-lockup"><i class="logo logo-n8n"></i> n8n</span>
```

Rozmiar bierze się z `font-size` rodzica (logo ma 1em wysokości), szerokość liczy się sama
z proporcji oryginału — wordmark Open Mercato jest ~3,9× szerszy niż wysoki.

Nowe logo: wrzuć SVG do `assets/logos/`, dopisz kolor w `BRAND` w `build-logos-css.mjs`
(**wersja czytelna na ciemnym tle** — GitHub, Notion i OpenAI mają oficjalne kolory prawie czarne
i na scenie `#0A0A08` znikają), potem `./build-logos-css.sh`.

## Konwencja nazw

`eNN-MM-slug.html` — `NN` numer odcinka, `MM` kolejność wstawki w odcinku.
`render.js` grupuje wyjście po prefiksie: `e08-*` → `out/e08/`.

## Pętla pracy

```bash
cd "Animation flowbiz youtube"
NO_CHROMA=1 FPS=30 node render.js e08-01-cache     # wersja ciemna, do oceny
FPS=30 node render.js e08-01-cache                 # chromakey, do montażu
ffmpeg -ss 3 -i out/e08/e08-01-cache.mp4 -frames:v 1 /tmp/k.png   # klatka do obejrzenia
```

Jednorazowo: `npm install && npx playwright install chromium`.

## Trzy rzeczy, które łatwo zepsuć

1. **Każdy kontener musi mieć własne `background:#0D0D0B`.** Po wycięciu zielonego treść
   bez własnego tła wisi w powietrzu. Pełna reguła w `CLAUDE.md`.
2. **Ciemny tekst poza kartą idzie w `<span class="chroma-plate">`** — inaczej zniknie po keyu.
3. **Konflikt tweenów na tej samej właściwości.** `tl.from(el, {y:26})` nadpisze wcześniejszy
   ruch `y` tego elementu. Kosztowało to jedną nieudaną wersję sceny `e08-01`.

## Co jest zrobione

**Odcinek 08** (nagrany) — siedem wstawek: `cache`, `moduly`, `racja`, `warstwy` (pan pionowy),
`granice` (pan poziomy), `bariera`, `framework` (Claude + Codex wpadają w strukturę repo).
**Odcinek 01** (nagrany) — pięć: `kopie`, `cztery-branze` (pan + odjazd), `dostep` (pan + odjazd,
low-code vs repozytorium), `skad-przenosisz` (HubSpot · Salesforce · Excel → OM),
`czym-to-nie-jest` (Make · n8n · Zapier skreślone).
**Odcinek 03** — do zrobienia, sześć wstawek.

Każda ma wersję ciemną (do oceny) i `_chroma` (do montażu) w `out/eNN/`, oraz gotową ścieżkę
dźwiękową w `sfx/tracks/<scena>_sfx.wav`.
