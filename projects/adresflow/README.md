# AdresFlow — reklamy wideo 9:16

Spoty pod Reels / TikTok / Shorts dla [AdresFlow](https://adresflow.com) — Studio AI
dla agentów nieruchomości. Kod aplikacji: `~/Repo/adresflow-v2`.

**Gotowe spoty: [`final/`](final/) — 12 sztuk z opisem, gdzie którego użyć.**

## Katalogi

| | Co tam jest | W gicie |
|---|---|---|
| `final/` | 12 gotowych spotów 1080×1920 + `README.md` z indeksem | tak |
| `assets/shots/` | ujęcia z Higgsfielda (`raw-*.mp4`) — kupione za kredyty | tak |
| `assets/voice/` | lektorzy (`vo-*.mp3`) + testy głosów | tak |
| `assets/music/` | `music.mp3` (wybrany podkład) + `library/` (YouTube Audio Library) | tak |
| `assets/photos/` | zdjęcia produktowe: home staging przed/po, działki, rzuty | tak |
| `assets/reference/` | inspiracje i materiały poglądowe | tak |
| `screens/` | ekrany produktu jako kompozycje HTML → wideo | tak |
| `tools/` | pipeline montażu (Python + ffmpeg + Pillow) | tak |
| `build/` | wszystko odtwarzalne: złożone spoty, warstwy, cache, ekrany | **nie** |

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
python3 tools/finalize.py              # weryfikacja + kopia do final/
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

Pełna lista: [`../../.ai/MEMORY.md`](../../.ai/MEMORY.md) ·
realia branży: [`ai/realia-agenta-nieruchomosci.md`](ai/realia-agenta-nieruchomosci.md)

## Otwarte

- **Brak eksportu PDF w produkcie** — spot 12 mówi „gotowe ogłoszenie do wysłania",
  bo krok 4 kreatora daje tylko *Kopiuj / .txt / podgląd / stronę HTML*.
- **„899 zł u grafika"** (spoty 02, 08) wymaga źródła przed płatną kampanią.
- **Spoty 01–09 zbudowane przed fixem klatkażu** w `story.py` — mają ok. 0,6 s
  naddatku obrazu nad lektorem. Warte przebudowy przy najbliższej zmianie.
