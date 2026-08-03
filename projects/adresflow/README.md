# AdresFlow — reklamy wideo 9:16

Spoty pod Reels / TikTok / Shorts dla [AdresFlow](https://adresflow.com) — Studio AI
dla agentów nieruchomości. Kod aplikacji: `~/Repo/adresflow-v2`.

**Gotowe spoty: [`final/`](final/) — 14 sztuk z opisem, gdzie którego użyć.**

## Katalogi

| | Co tam jest | W gicie |
|---|---|---|
| `final/` | 14 gotowych spotów 1080×1920 + `README.md` z indeksem | tak |
| `final/1x1/`, `final/16x9/` | te same spoty w kwadracie i poziomie | **nie** — `reframe.py` |
| `assets/shots/` | ujęcia z Higgsfielda (`raw-*.mp4`) — kupione za kredyty | tak |
| `assets/voice/` | lektorzy (`vo-*.mp3`) + testy głosów | tak |
| `assets/music/` | `music.mp3` (wybrany podkład) + `library/` (YouTube Audio Library) | tak |
| `assets/photos/` | zdjęcia produktowe: home staging przed/po, działki, rzuty | tak |
| `assets/reference/` | inspiracje i materiały poglądowe | tak |
| `screens/` | ekrany produktu jako kompozycje HTML → wideo | tak |
| `tools/` | pipeline montażu (Python + ffmpeg + Pillow) | tak |
| `build/` | wszystko odtwarzalne: złożone spoty, warstwy, cache, ekrany | **nie** |

## Kadry

Każdy spot wychodzi w trzech kadrach, do `final/9x16/`, `final/1x1/`, `final/16x9/`.

**Cały materiał źródłowy jest pionowy** (720×1280 albo 1440×2560) — nie mamy ani
jednego ujęcia poziomego. To determinuje sposób przekładania:

| Kadr | Materiał fotograficzny | Ekrany produktu i POV |
|---|---|---|
| 9:16 | natywny | natywny |
| 1:1 | przycięty (bohater zostaje) | rozmyte tło |
| 16:9 | rozmyte tło | rozmyte tło |

Przycięcie pionu do 16:9 zostawia **31 % wysokości** i ucina głowy, dlatego
poziom powstaje metodą „rozmyte tło z tego samego ujęcia + ostry pion na
środku". To standard przy przekładaniu pionu na poziom, ale **nie zastąpi
materiału nakręconego natywnie w poziomie** — jeśli 16:9 ma być głównym
kanałem, warto wygenerować ujęcia od nowa.

Ekrany produktu i spoty POV nigdy nie są przycinane: w POV plansza-hook siedzi
u góry, a wymagany prawnie znak AI u dołu — każde przycięcie wywala jedno albo
drugie.

Napisy siedzą niżej w 9:16 (0,693 wysokości) niż w niższych kadrach (0,56) —
przy tym samym ułamku druga linia lądowała dokładnie na znaku AI.

```bash
python3 tools/story.py 1x1 16x9       # wybrane kadry
python3 tools/story.py wycena 1x1     # jeden spot, jeden kadr
```

## Kadry

Master jest **pionowy**. Kwadrat i poziom wyprowadza `tools/reframe.py`:
ostry pion na środku, rozmyte tło zrobione z tego samego ujęcia.

Dlaczego nie przycinamy: cały materiał źródłowy jest pionowy (720×1280 albo
1440×2560), a kadr 16:9 wycięty z 9:16 zostawia **31 % wysokości** i ucina
głowy. Nie mamy ani jednego ujęcia poziomego.

Świadomy kompromis: napisy, plansze i znak AI są wypalone w pionie, więc
w kwadracie i poziomie wychodzą mniejsze. Wersja bez tego kompromisu wymagałaby
przebudowy każdego spotu natywnie pod kadr, czyli utrzymywania trzech układów
graficznych zamiast jednego — nie warto, dopóki 9:16 jest głównym kanałem.

## Jak to działa

```
assets/shots/     ┐
assets/voice/     ├─→  tools/story.py  ─→  build/  ─→  tools/finalize.py  ─→  final/
assets/music/     │
build/screens/    ┘         ↑
    ↑                  build/overlays/
screens/render.sh      tools/brand.py
```

**Lektor prowadzi montaż, nie odwrotnie.** `story.py` tnie jeden plik głosu na
frazy przez `silencedetect`, a długość ujęć i timing napisów wynikają z długości
fraz. Dlatego lektora generuje się **jednym wywołaniem na cały spot** — osobne
wywołania dają dryf barwy i słychać dwie różne osoby.

Szczegóły: [`tools/README.md`](tools/README.md) · ekrany produktu:
[`screens/README.md`](screens/README.md)

## Odtworzenie od zera

```bash
./screens/render.sh                    # ekrany HTML → build/screens/  (0 kredytów)
python3 tools/brand.py                 # plansze i napisy → build/overlays/
python3 tools/story.py                 # spoty narracyjne → build/
python3 tools/render.py                # krótkie warianty → build/
python3 tools/pov.py                   # spoty POV: grade + muzyka → build/
python3 tools/finalize.py              # weryfikacja + kopia do final/
python3 tools/reframe.py               # kadry 1:1 i 16:9 z gotowych pionów
```

Nowy spot zwykle **nie wymaga nowych generacji** — sprawdź najpierw
`assets/shots/` i `assets/photos/`.

## Zasady, które kosztowały kredyty

- Kredyty idą **wyłącznie** na generacje (ujęcia, głos). Typografia, plansze,
  napisy, montaż i muzyka są lokalne — zmiana copy nie kosztuje ani kredyta.
- Ekranów produktu **nie generuj modelem wideo** — UI wychodzi papką, a polskie
  napisy bełkotem. Są pisane jako HTML w `screens/`.
- Otwieraj spot **bólem odbiorcy i ruchem**, nie opisem funkcji (zmierzone).
- O własnej cenie nie mówimy — prowadzimy do 30 darmowych kredytów.
- Spoty POV (13–14) **łamią bramkę `check` celowo** — weryfikuj je `snapshot`-em.
- **Każdy spot musi mieć wpis w `AI_MAP`** (`tools/finalize.py`) i włączony
  przełącznik AI przy publikacji — patrz [`final/OZNACZENIA-AI.md`](final/OZNACZENIA-AI.md).

Pełna lista: [`../../.ai/MEMORY.md`](../../.ai/MEMORY.md) ·
realia branży: [`ai/realia-agenta-nieruchomosci.md`](ai/realia-agenta-nieruchomosci.md)

## Pułapki układu katalogów

- **`build/` jest poza gitem, więc plik źródłowy, który tam trafi, znika z repo.**
  Przy wydzielaniu repo `rzut3d-8s-raw.mp4` (źródło wariantu `v1`) został
  zaklasyfikowany jako eksperyment i wylądował w `build/` — `render.py` przestał
  budować spot 08, a błąd wyszedł dopiero przy następnym pełnym przebiegu.
  Po zmianach w układzie warto przepuścić kontrolę: każdy plik z `SHOTS`,
  `JOBS`, `music.mp3` i `vo-*.mp3` musi istnieć w `assets/`.
- **`screens/sync-css.sh` rozsyła arkusze do projektów kompozycji** — projekty
  nie współdzielą `assets/`, bo ścieżka `../assets/` 404-uje w Studio. Uruchom go
  po każdej zmianie w `screens/assets/*.css`.

## Otwarte

- **Spot 01 został na 30 kredytach.** Agentka MÓWI „trzydzieści darmowych
  kredytów" w samym ujęciu, więc napis 15 kłóciłby się z tym, co słychać.
  Do decyzji: ponowny dubbing `raw-ugc-agentka.mp4` z nową kwotą albo wycofanie
  spotu z kampanii. Pozostałe 13 spotów mówi 15.

- **Brak eksportu PDF w produkcie** — spot 12 mówi „gotowe ogłoszenie do wysłania",
  bo krok 4 kreatora daje tylko *Kopiuj / .txt / podgląd / stronę HTML*.
- **„899 zł u grafika"** (spoty 02, 08) wymaga źródła przed płatną kampanią.
- **Spoty 01–09 zbudowane przed fixem klatkażu** w `story.py` — mają ok. 0,6 s
  naddatku obrazu nad lektorem. Warte przebudowy przy najbliższej zmianie.
