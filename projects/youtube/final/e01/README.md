# Wstawki e01 — gotowe do montażu

**Bierz pliki `-v3-2026-08-21`.** Wersje `v2` leżą w `_stare-v2/` wyłącznie na wypadek
porównania — nie wrzucaj ich do montażu.

| Plik | Czas | Gdzie w skrypcie |
|---|---|---|
| `e01-06-kod-agenta-v3` | 6,2 s | hook, „Claude i tak wchodzi w ten kod" |
| `e01-07-serwer-i-dostep-v3` | 6,4 s | segment 3, „ani do kodu, ani do infrastruktury" |
| `e01-08b-tytul-lewy-v3` | 4,4 s | obietnica, ~0:55 — **wariant zalecany** |
| `e01-08-tytul-v3` | 4,4 s | ta sama karta wyśrodkowana — zapasowa |

## Jak je wstawić

1. **Płótno projektu 1920×1080.** CapCut dziedziczy rozdzielczość z pierwszego klipu,
   a nagrania mają 720p — trzeba to nadpisać w ustawieniach projektu.
2. Materiał 720p rozciągnij do pełnego kadru (będzie miękki — to wina źródła).
3. **Wstawkę wstaw w skali 100 %.** Jeśli edytor sam ją dopasuje, nadpisz ręcznie.
4. Eksport 1080p, bitrate zalecany lub wyżej.

Płótno 720p kosztuje **23 % ostrości krawędzi** (zmierzone). Renderowanie wstawek w 4K
tego nie odrabia — daje 4 %. Jedyna realna dźwignia to punkt 1.

## Referencje

`referencje/REF-*.mp4` to te same wstawki **złożone z materiałem poza edytorem**, w 1080p.
Służą do porównania z własnym eksportem: jeśli Twój odbiega od referencji, przyczyna jest
w ustawieniach projektu, nie w plikach.

## Pułapka

Edytor trzyma zaimportowane media w cache'u — podmiana pliku o tej samej nazwie nie zadziała.
Dlatego wersja i data są w nazwie. Przy aktualizacji **usuń stary klip z biblioteki mediów**.
