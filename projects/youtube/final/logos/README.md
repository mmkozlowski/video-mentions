# Logotypy do montażu — przezroczyste PNG

Wygenerowane: `assets/logos/export-png.mjs` (`node export-png.mjs`). Ręczne poprawki przepadną
przy następnym eksporcie — źródłem są SVG-e w `assets/logos/`.

Każdy znak w trzech wariantach, dłuższy bok **512 px**, kanał alfa:

| Plik | Kiedy |
|---|---|
| `<marka>.png` | kolor firmowy — gdy logo ma być rozpoznawalne samo z siebie |
| `<marka>-white.png` | na ciemnym kadrze albo na zdjęciu, gdy kolor marki gryzie się z tłem |
| `<marka>-amber.png` | `#F5A623` — gdy logo ma należeć do naszej planszy, nie stać obok niej |

**Kolory firmowe są celowo nieoficjalne tam, gdzie oryginał jest za ciemny.** GitHub to `#181717`,
Notion `#000000`, OpenAI `#412991` — na ciemnym kadrze wszystkie znikają, więc dostały jasne
zamienniki. Jeśli kładziesz logo na jasnym tle, weź wariant firmowy i sprawdź kontrast okiem.

**Znak jest jednobarwny.** Maska nie zna kolorów źródła, więc Slack i Google Drive tracą swoją
paletę. Dla nich, jeśli potrzeba oryginału, weź plik z `svg/` obok — wektory leżą w tym samym
folderze i skalują się bez utraty ostrości w programach, które je czytają (After Effects, Motion).

**Wnętrza są przezroczyste, nie białe.** Siatka w Excelu, litera N w Notion, kotek GitHuba —
to dziury w masce. Na ciemnym kadrze czytają się dobrze, na jasnym znak zrobi się pusty.

Podgląd całej paczki bez otwierania 54 plików: `_przeglad-kolor-marki.png`,
`_przeglad-white.png`, `_przeglad-amber.png`.

## Co jest

| Marka | Rozmiar | Kolor firmowy |
|---|---|---|
| `airtable` | 512×512 | `#18BFFF` |
| `claude` | 512×512 | `#D97757` |
| `excel` | 512×512 | `#21A366` |
| `github` | 512×512 | `#FAF8F0` |
| `googledrive` | 512×512 | `#4285F4` |
| `googlesheets` | 512×512 | `#34A853` |
| `hubspot` | 512×512 | `#FF7A59` |
| `make` | 512×512 | `#B36BFF` |
| `n8n` | 512×512 | `#EA4B71` |
| `notion` | 512×512 | `#FAF8F0` |
| `openai` | 512×512 | `#FAF8F0` |
| `openmercato` | 512×131 | `#F5A623` |
| `salesforce` | 512×512 | `#00A1E0` |
| `shopify` | 512×512 | `#7AB55C` |
| `slack` | 512×512 | `#FAF8F0` |
| `woocommerce` | 512×512 | `#C285D6` |
| `wordpress` | 512×512 | `#5A9FC4` |
| `zapier` | 512×512 | `#FF4F00` |
