# B-roll z Veo 3.1 (Gemini API)

Ujęcia aktorskie do momentów, w których animacja nie ma czego pokazać — ludzie, biuro,
ekran. **Nie zastępują wstawek tekstowych**, tylko wypełniają fragmenty, gdzie mówisz
o odczuciach, a nie o mechanice.

| Plik | Co pokazuje | Gdzie w odcinku 01 |
|---|---|---|
| `02-chaos.mp4` | biuro, wszyscy mówią naraz, ktoś wnosi stos papierów | payoff, „chaos" |
| `03-szukanie.mp4` | dłonie przewijają arkusz, wzrok skacze po kolumnach | „szukanie po różnych miejscach" |
| `01-nerwowka.mp4` | człowiek odchyla się od biurka, przeciera twarz | „nerwówka" |
| `04-spokoj.mp4` | ten sam człowiek spokojnie klika raz i zamyka laptop | przejście do „a po?" |

**Czwarte ujęcie jest najważniejsze.** Bez kontrastu pozostałe trzy są tylko galerią
stresu, a nie argumentem.

## Jak generować kolejne

```bash
cd ~/Repo/video-mentions/projects/youtube
./tools-veo.sh "<slug>" "<opis po angielsku>" fast 8 1080p
```

Parametry: `pro` | `fast` | `lite`, długość w sekundach, rozdzielczość.

> 🔴 **1080p działa TYLKO przy 8 sekundach.** Przy 4 i 6 s API odrzuca żądanie komunikatem
> „1080p is not supported for a duration of N seconds". Domyślne 6 s daje ciche 720p —
> czyli dokładnie tę rozdzielczość, przez którą napisy się rozsypywały.

## Co działa w promptach

Wspólny sufiks stylistyczny trzyma paczkę spójną:

> Documentary style, handheld, shallow depth of field. Muted teal and amber tones, slightly
> desaturated, warm afternoon light through a window. No text, no captions, no on-screen
> graphics, no logos. Realistic, cinematic, natural office ambience.

`No text, no captions, no logos` jest istotne — bez tego model dokleja napisy i pseudologotypy,
które gryzą się z warstwą graficzną i wyglądają jak błąd.

## Oznaczanie treści AI

Materiał z Veo **nie ma C2PA**, więc platformy go nie oznaczą automatycznie. Przełącznik
„treści wygenerowane przez AI" trzeba włączyć ręcznie przy publikacji —
patrz `../../../.ai/memory/oznaczanie-tresci-ai.md`.
