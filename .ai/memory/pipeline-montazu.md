---
name: pipeline-montazu
description: Reklamy wideo 9:16 powstają w projects/adresflow/tools/ — kredyty tylko na ujęcia i głos, cały montaż lokalnie
metadata:
  type: project
---

Kampanie wideo AdresFlow (Reels/TikTok, 1080×1920) produkuje **`projects/adresflow/tools/`**. Gotowe spoty leżą w **`projects/adresflow/final/`** z własnym `README.md` opisującym, gdzie którego użyć.

**Zasada, na której stoi cały pipeline: kredyty Higgsfield idą WYŁĄCZNIE na generowanie** (ujęcia, głos, dubbing, upscale, analiza). Typografia, logo, plansze, napisy, montaż, muzyka i ducking robią się lokalnie w Pillow/ImageMagick/ffmpeg — za darmo i dowolną liczbę razy. Dlatego zmiana copy nie kosztuje ani kredyta.

| Skrypt | Rola |
|---|---|
| `brand.py` | plansze i warstwy napisów; teksty krótkich spotów w `VERSIONS` |
| `story.py` | spoty narracyjne; scenariusze w `STORIES`, montaż sterowany lektorem |
| `render.py` | krótkie warianty (10–13 s) |
| `finalize.py` | kopiuje gotowe do `../FINAL/` + generuje indeks; **pomija pliki z błędami dekodera** |
| `pick_music.py` | ranking podkładów po energii w paśmie mowy i LRA |
| `voice_test.py` | ranking głosów po ekspresji (zmienność tonu, rozrzut głośności) |

Ujęcia (`projects/adresflow/assets/shots/raw-*.mp4`) są **wielokrotnego użytku** — nowy spot zwykle nie wymaga nowych generacji. Materiał przed/po do transformacji jest już w repo w `projects/adresflow/assets/photos/` (home staging ×4, działka z zabudową, pusty pokój, remont).

**Pion → poziom: przycięcie NIE działa.** Kadr 16:9 wycięty z 9:16 zostawia
31 % wysokości i ucina głowy. Poziom składamy z rozmytego tła (to samo ujęcie,
`gblur`) + ostrego pionu na środku. Kwadrat 1:1 można przyciąć, ale tylko dla
materiału fotograficznego — ekrany produktu i kompozycje z przyklejonymi
planszami trzeba padować, bo przycięcie wywala górę albo dół (w tym wymagany
prawnie znak AI).

**Kadry inne niż 9:16 WYPROWADZAMY z gotowego pionu** (`tools/reframe.py`),
nie budujemy natywnie. Budowanie natywne działa i wygląda lepiej, ale oznacza
utrzymywanie trzech układów graficznych zamiast jednego — przy pionie jako
głównym kanale to się nie zwraca. Cena kompromisu: napisy i znak AI są wypalone
w pionie, więc w kwadracie i poziomie są mniejsze.

**Why:** bez tego podziału każda poprawka tekstu czy muzyki oznaczałaby ponowną generację za kredyty, a przy 10 spotach to setki kredytów na kosmetykę.

**How to apply:** zanim wygenerujesz cokolwiek nowego, sprawdź `projects/adresflow/assets/shots/raw-*.mp4` i `projects/adresflow/assets/photos/` — najczęściej materiał już jest. Pełna dokumentacja: `projects/adresflow/tools/README.md`, historia decyzji: `projects/adresflow/ai/decisions/2026-07-30-reklamy-higgsfield-rzut-3d.md`. Limity API: [[higgsfield-mcp-limity]].
