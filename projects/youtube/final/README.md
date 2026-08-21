# final/ — wstawki zaakceptowane

Katalog **produktu**: to, co idzie do montażu. Rzeczy robocze i odtwarzalne siedzą
w `Animation flowbiz youtube/out/`.

| Katalog | Co tam jest |
|---|---|
| `e01/` | wstawki do odcinka 01 — **bierz `-v5-2026-08-21`** |
| `e01/referencje/` | te same wstawki złożone z materiałem poza edytorem, do porównania z własnym eksportem |
| `szablony/` | `txt-linia` — goła linia tekstu, treść podmieniana z linii poleceń |
| `testy/` | arkusze typograficzne: który wariant przeżywa kompresję |
| `_archiwum/` | starsze wersje (v2–v4), wyłącznie do porównania — **nie wrzucaj do montażu** |
| `logos/` | znaki marek |

## Odcinki 03 i 08

Ich wstawki **są wyrenderowane**, ale leżą w `out/e03/` i `out/e08/`, bo nie przeszły jeszcze
przeglądu. Do `final/` trafiają dopiero po akceptacji — taka jest umowa tego katalogu.

## Trzy reguły typografii (zmierzone, nie wymyślone)

| Element | Traktowanie |
|---|---|
| **biel** — nagłówek, akapit, cokolwiek | cień; domyślne wszędzie |
| **bursztyn mały** — nadtytuł, etykieta, podpis | **ramka**, nigdy obrys |
| **bursztyn duży** — teza, akapit od ~50 px | **cień**, bez ramki |

Obrys na bursztynie odpadł 21.08 — wygląda jak naklejka. Pełne uzasadnienie i pomiary:
`../ai/decisions/2026-08-20-wstawki-e01-czytelnosc-i-dostarczanie.md`.

## Pułapka

Edytor trzyma zaimportowane media w cache'u — podmiana pliku o tej samej nazwie nie zadziała.
Dlatego wersja i data są w nazwie. Przy aktualizacji **usuń stary klip z biblioteki mediów**.
