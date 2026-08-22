# final/ — wstawki gotowe do montażu

Katalog **produktu**. Rzeczy robocze i odtwarzalne siedzą w `Animation flowbiz youtube/out/`.

| Katalog | Co tam jest |
|---|---|
| `e01/` | 9 wstawek do odcinka 01 |
| `e03/` | 6 wstawek do odcinka 03 |
| `e08/` | 7 wstawek do odcinka 08 |
| `eNN/warianty-long/` | dłuższe wersje tych samych scen — bierz, gdy potrzebujesz więcej czasu na antenie |
| `e01/referencje/` | wstawki złożone z materiałem **poza edytorem**, do porównania z własnym eksportem |
| `szablony/` | `txt-linia` — goła linia tekstu, treść podmieniana z linii poleceń |
| `testy/` | arkusze typograficzne: który wariant przeżywa kompresję |
| `logos/` | znaki marek |

Wszystkie pliki to `*_alpha.mov` (qtrle, 1920×1080, 30 kl./s) z oznaczeniem `v5-2026-08-22`.
Wersja w nazwie nie jest ozdobą: edytor trzyma media w cache'u i podmiana pliku o tej samej
nazwie nie zadziała. **Przy aktualizacji usuń stary klip z biblioteki mediów.**

## Cztery kroki, bez których to nie zadziała

1. **Płótno projektu 1920×1080.** Edytor dziedziczy rozdzielczość z pierwszego klipu,
   a nagrania mają 720p. Płótno 720p kosztuje **23 % ostrości krawędzi** (zmierzone).
2. Materiał 720p rozciągnij do pełnego kadru — będzie miękki, to wina źródła.
3. **Wstawkę wstaw w skali 100 %.** Jeśli edytor sam ją dopasuje, nadpisz ręcznie.
4. Eksport 1080p, bitrate zalecany lub wyżej.

Jeśli Twój eksport odbiega od `e01/referencje/`, przyczyna jest w ustawieniach projektu,
nie w plikach.

## Trzy reguły typografii (zmierzone, nie wymyślone)

| Element | Traktowanie |
|---|---|
| **biel** — nagłówek, akapit, cokolwiek | cień; domyślne wszędzie |
| **bursztyn mały** — nadtytuł, etykieta, podpis | **ramka**, nigdy obrys |
| **bursztyn duży** — teza, akapit od ~50 px | **cień**, bez ramki |

Pełne uzasadnienie, pomiary i pięć pułapek, które to kosztowało:
`../ai/decisions/2026-08-20-wstawki-e01-czytelnosc-i-dostarczanie.md`.
