# SFX do wstawek — paczka i arkusz czasów

Siedem dźwięków, generowanych `./make-sfx.sh` (ffmpeg). **Zero licencji, zero kredytów,
odtwarzalne jednym poleceniem** — dlatego nie leżą w `assets/`, tylko powstają na miejscu.

## Nie musisz układać ich ręcznie — `./build-tracks.sh`

Skrypt skleja z paczki **jedną gotową ścieżkę na scenę**: `tracks/<scena>_sfx.wav`, dokładnie
tak długą jak wstawka, z akcentami w miejscach z arkusza niżej.

```bash
./make-sfx.sh        # raz — generuje paczkę siedmiu dźwięków
./build-tracks.sh    # skleja tracks/*_sfx.wav dla wszystkich scen
./build-tracks.sh e08-05-granice   # albo jednej
```

W montażu kładziesz **jeden klip wyrównany do początku wstawki** — i masz komplet akcentów w punkt,
bez odmierzania dziesiątych części sekundy.

## Dlaczego to osobny plik, a nie audio wklejone w MP4

Wstawki idą do montażu jako **chromakey overlay** na gadaną głowę. Gdyby miały wklejoną ścieżkę
audio, nie dałoby się ich zmiksować pod narrację — a to montaż decyduje, czy w danym momencie
dźwięk ma być słyszalny, czy schowany pod zdaniem. Osobna ścieżka daje to samo ułożenie w czasie
i zostawia Ci suwak głośności.

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

### `e01-03-dostep` · 6,7 s — **pan poziomy + odjazd**
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,30 | `pop` | panel low-code |
| 0,62 / 0,90 | `pop` ×2 | kafle n8n · Zapier · Make (trzeci zostaje w ciszy) |
| 1,55 | `error` | **kłódka — nie zajrzysz** |
| 2,45 | `whoosh` + `line` | **przejazd kamery do repozytorium** |
| 2,90 | `pop` | panel repo |
| 3,17 / 3,43 / 3,70 | `tick` ×3 | wiersze drzewa plików |
| 3,87 | `pop` | Claude → czyta wszystko |
| 4,55 | `whoosh` | **odjazd — oba światy obok siebie** |
| 5,60 | `thud` | „Stuprocentowy dostęp do kodu." |

### `e01-04-skad-przenosisz` · 4,7 s
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,30 / 0,54 / 0,78 | `pop` ×3 | HubSpot · Salesforce · Excel |
| 1,45 / 1,79 | `line` ×2 | proces spływa w dół (trzecia linia bez dźwięku) |
| 2,40 | `pop` | karta Open Mercato |
| 3,55 | `thud` | „Szybko i tanio — czy nie?" |

### `e01-05-czym-to-nie-jest` · 4,9 s
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,30 / 0,52 / 0,74 | `pop` ×3 | Make · n8n · Zapier |
| 1,35 / 1,77 / 2,19 | `error` ×3 | **skreślenia, w rytmie zdania** |
| 2,85 | `thud` | „To nie ta klasa narzędzia." |
| 3,55 | `pop` | Open Mercato staje osobno |

### `e08-07-framework` · 6,1 s
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,30 / 0,50 | `pop` ×2 | Claude · Codex |
| 1,10 | `line` | kabel do struktury |
| 1,75 | `pop` | panel repozytorium |
| 2,10 / 2,25 / 2,40 | `tick` ×3 | AGENTS.md · .ai/specs · modules |
| 3,05 | `klik` | „Brakuje Ci tego…" |
| 3,57 | `error` | **„Tego nie możesz zrobić."** |
| 4,09 | `klik` | „Chcesz dobrze? Zrób tak." |
| 4,85 | `thud` | „Nie zaczyna od pustej kartki." |

### `e03-01-kartka` · 8,5 s — **pan poziomy, kartka stoi**
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,20 | `pop` | kartka wjeżdża |
| 0,75 | `pop` | stanowisko „handlowiec" |
| 1,15 | `klik` | podpis |
| 1,70 / 3,00 / 4,30 / 5,60 | `whoosh` ×4 | **kamera przesuwa firmę pod kartką** |
| 2,40 | `error` | pieczątka „WPROWADZONE" |
| 3,70 | `klik` | dopisek na marginesie |
| 5,00 | `pop` | ptaszek „spakowane" |
| 6,30 | `klik` | nr faktury |
| 7,42 | `thud` | „Sześć godzin. Jedna kartka." |

### `e03-02-warsztat` · 8,8 s — **pan poziomy + odjazd**
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,30 | `pop` | sekcja „właściciel" |
| 0,60 / 0,82 | `tick` ×2 | pytania (trzeciego nie dawaj) |
| 1,30 / 2,35 / 3,40 / 4,45 / 5,50 | `whoosh` ×5 | **przejazdy do kolejnych ról** |
| +0,26 po każdym | `pop` | sekcja wjeżdża |
| 6,65 | `whoosh` | **odjazd — sześć sekcji w kadrze** |
| 7,67 | `thud` | „Zapytaj konkretną osobę." |

### `e03-03-droga-zamowienia` · 8,1 s — **pan + licznik**
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,35 | `pop` | etap „handlowiec" |
| 0,62 | `tick` | ludzik + licznik rusza |
| 1,45 / 2,65 / 3,85 / 5,05 | `whoosh` ×4 | przejazdy |
| +0,30 `pop`, +0,58 `tick` | | etap i przyrost licznika |
| 6,30 | `error` | **licznik czerwienieje na 12** |
| 6,78 | `thud` | „Każda może zepsuć co innego." |

### `e03-04-trzy-warstwy` · 5,7 s
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,25 | `pop` | zlepek trzech warstw wjeżdża jako jedno |
| 1,05 | `whoosh` | **ROZJAZD — warstwy odsuwają się od siebie** |
| 1,75 / 1,90 | `line` ×2 | linie „nie mieszamy" wchodzą w szczeliny |
| 2,25 / 2,95 / 3,65 | `klik` ×3 | podświetlenie kolejnych warstw |
| 4,45 | `thud` | „Trzy warstwy. Nigdy razem." |

### `e03-05-slownik` · 5,9 s
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,20 | `pop` | słowo „zamówienie" |
| 0,95 / 1,85 / 2,75 | `whoosh` ×3 | **kamera trąca w bok** przy każdym odczytaniu |
| 1,11 / 2,01 / 2,91 | `pop` ×3 | dymki: handlowiec, administracja, produkcja |
| 3,70 | `whoosh` | kamera wraca na środek |
| 4,05 | `error` | **zderzenie — trzy znaczenia naraz** |
| 4,62 | `thud` | „Każdy zbuduje coś innego." |

### `e03-06-powtarzalnosc` · 6,2 s
| s | dźwięk | co się dzieje |
|---|---|---|
| 0,30 | `pop` | moduł 01 |
| 0,56 / 1,08 | `tick` ×2 | rekord, role (status i dokument w ciszy) |
| 2,05 / 3,25 | `whoosh` ×2 | dryf kamery przy kolejnych modułach |
| 2,32 / 3,45 | `pop` ×2 | moduł 02, moduł 03 |
| 3,13 / 3,89 | `klik` ×2 | moduł gotowy |
| 4,35 | `whoosh` | kamera wraca — trzy identyczne szkielety |
| 4,80 | `thud` | „Powtarzalność." |

---

## Gdyby paczka okazała się za surowa

To są dźwięki syntezowane, więc brzmią czysto i trochę „elektronicznie". Jeżeli po zmiksowaniu
uznasz, że potrzeba czegoś cieplejszego, są dwie drogi:

- **Higgsfield `generate_audio`** — kosztuje kredyty, ale daje bogatsze tekstury.
- **Biblioteka w edytorze** — większość ma wbudowane UI-clicki lepszej jakości; arkusz czasów
  wyżej działa niezależnie od źródła dźwięku.
