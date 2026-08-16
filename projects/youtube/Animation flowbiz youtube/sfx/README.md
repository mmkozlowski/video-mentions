# SFX do wstawek — paczka i arkusz czasów

Siedem dźwięków, generowanych `./make-sfx.sh` (ffmpeg). **Zero licencji, zero kredytów,
odtwarzalne jednym poleceniem** — dlatego nie leżą w `assets/`, tylko powstają na miejscu.

## Dlaczego nie wbudowuję ich w MP4

Wstawki idą do montażu jako **chromakey overlay** na gadaną głowę. Gdyby miały wklejoną ścieżkę
audio, nie dałoby się ich zmiksować pod narrację — a to montaż decyduje, czy w danym momencie
dźwięk ma być słyszalny, czy schowany pod zdaniem. Dostajesz więc **osobne WAV-y i arkusz czasów**.

## Paczka

| Plik | Czas | Do czego |
|---|---|---|
| `pop.wav` | 0,28 s | element wskakuje sprężyną — karta, węzeł, dymek |
| `klik.wav` | 0,06 s | wciśnięcie przycisku, pojedyncze zdarzenie |
| `tick.wav` | 0,035 s | licznik, wpisywanie tekstu, znikający wiersz |
| `whoosh.wav` | 0,55 s | przejazd kamery, przesunięcie ekranu |
| `line.wav` | 0,90 s | dorysowywanie linii między stacjami |
| `thud.wav` | 0,55 s | puenta, ciężkie lądowanie słowa |
| `error.wav` | 0,40 s | coś znika, coś się nie udało — akcenty czerwone |

Wszystko mono 48 kHz, celowo dyskretne. Mają **podbijać ruch, nie zagłuszać narracji**.

## Trzy zasady miksu

1. **−18 do −24 dBFS pod narracją.** Dźwięk ma być wyczuwalny, nie słyszalny jako osobna warstwa.
2. **Maksymalnie jeden akcent na ~0,8 sekundy.** Osiem modułów wskakujących po kolei nie oznacza
   ośmiu popów — daj trzy pierwsze i ostatni, resztę zostaw ciszy. Inaczej robi się karabin.
3. **Pod zdaniem kluczowym nie ma nic.** Jeśli w tym miejscu mówisz puentę, `thud` idzie
   **po** ostatnim słowie, nie pod nim.

---

## Arkusz czasów — gdzie co położyć

Sekundy liczone od początku wstawki.

### `e08-01-cache` · 4,1 s
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,20 | `pop` | karta z pracownikami |
| 1,10 | `pop` | pojawia się przycisk |
| 1,75 | `klik` | **wciśnięcie** |
| 1,95 / 2,13 / 2,31 | `tick` ×3 | wiersze znikają (nie dawaj wszystkich sześciu) |
| 2,75 | `error` | „brak danych" |
| 3,20 | `thud` | „Cała jego praca. Zniknęła." |

### `e08-02-moduly` · 3,9 s
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,25 / 0,51 / 0,77 | `pop` ×3 | pierwsze trzy moduły |
| 1,16 | `pop` | ostatni moduł |
| 1,95 | `tick` | drgnięcie |
| 2,60 | `error` | obramowania gasną |
| 3,00 | `thud` | „Żaden nie wie o drugim." |

### `e08-03-racja` · 4,3 s
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,30 | `pop` | dymek „TY" |
| 1,00 | `pop` | dymek agenta |
| 1,35–3,20 | `tick` co ~0,25 s | pisanie (albo jedna pętla typing pod spodem) |
| 3,40 | `thud` | „Zawsze ma rację." |

### `e08-04-warstwy` · 7,3 s — **pan pionowy**
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,30 | `pop` | warstwa 01 |
| 1,15 | `whoosh` + `line` | **kamera zjeżdża 01 → 02** |
| 1,55 | `pop` | warstwa 02 |
| 2,50 | `whoosh` + `line` | zjazd 02 → 03 |
| 2,90 | `pop` | warstwa 03 |
| 3,85 | `whoosh` + `line` | zjazd 03 → 04 |
| 4,25 | `pop` | warstwa 04 |
| 5,20 | `whoosh` | **odjazd kamery** — cały stos w kadrze |
| 6,25 | `thud` | „Nie po roku." |

### `e08-05-granice` · 6,0 s — **scena z panem**
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,30 | `pop` | węzeł 01 |
| 1,30 | `whoosh` + `line` | **przejazd kamery 01 → 02** |
| 1,80 | `pop` | węzeł 02 |
| 2,85 | `whoosh` + `line` | przejazd 02 → 03 |
| 3,35 | `pop` | węzeł 03 |
| 4,40 | `thud` | outro, puls na aktywnym węźle |

### `e08-06-bariera` · 3,6 s
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,35 | `pop` | „BUDOWANIA" wjeżdża |
| 1,15 | `error` | **skreślenie** |
| 1,70 | `pop` | „PROJEKTOWANIA" |
| 2,15 | `line` | bursztynowa kreska |
| 2,70 | `thud` | puls |

### `e01-01-kopie` · 4,0 s
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,25 | `pop` | oryginał `zamowienia.xlsx` |
| 1,00 | `whoosh` | **kopia się wysuwa** |
| 1,45 | `whoosh` | druga kopia |
| 1,75 / 2,15 | `tick` ×2 | gasną kolumny |
| 2,70 | `pop` | pytanie |
| 3,20 | `thud` | „WSZYSCY TRZEJ" |

### `e01-02-cztery-branze` · 8,2 s — **pan poziomy + odjazd**
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,30 | `pop` | stacja 01 · opakowania |
| 1,25 | `whoosh` + `line` | **przejazd 01 → 02** |
| 1,70 | `pop` | stacja 02 · medycyna |
| 2,70 | `whoosh` + `line` | przejazd 02 → 03 |
| 3,15 | `pop` | stacja 03 · produkcja MTO |
| 4,15 | `whoosh` + `line` | przejazd 03 → 04 |
| 4,60 | `pop` | stacja 04 · mała produkcja |
| 5,60 | `whoosh` | **odjazd kamery** — cztery branże w kadrze |
| 6,35 | `pop` | wspólny szkielet wyłania się pod nimi |
| 7,15 | `thud` | „Jeden fundament." |

---

## Gdyby paczka okazała się za surowa

To są dźwięki syntezowane, więc brzmią czysto i trochę „elektronicznie". Jeżeli po zmiksowaniu
uznasz, że potrzeba czegoś cieplejszego, są dwie drogi:

- **Higgsfield `generate_audio`** — kosztuje kredyty, ale daje bogatsze tekstury.
- **Biblioteka w edytorze** — większość ma wbudowane UI-clicki lepszej jakości; arkusz czasów
  wyżej działa niezależnie od źródła dźwięku.
