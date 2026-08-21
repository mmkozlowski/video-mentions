# Wstawki e01 — gotowe do montażu

**Bierz pliki `-v5-2026-08-21`.** Starsze wersje leżą w `../_archiwum/` wyłącznie na wypadek
porównania — nie wrzucaj ich do montażu.

| Plik | Czas | Gdzie w skrypcie |
|---|---|---|
| `e01-06-kod-agenta-v4` | 6,2 s | hook, „Claude i tak wchodzi w ten kod" |
| `e01-07-serwer-i-dostep-v4` | 6,4 s | segment 3, „ani do kodu, ani do infrastruktury" |
| `e01-08b-tytul-lewy-v4` | 4,4 s | obietnica, ~0:55 — **wariant zalecany** |
| `e01-08-tytul-v4` | 4,4 s | ta sama karta wyśrodkowana — zapasowa |

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

## Szablon gołego tekstu — `txt-linia`

Jedna linia na materiale, **bez karty i bez scrimu**. Czytelność niesie sama typografia:
waga 900 + twardy cień + delikatna poświata. Bursztyn tylko w belce i podpisie, gdzie ma
obrys — nigdy w samym zdaniu.

Treść podmieniasz **z linii poleceń, bez dotykania HTML-a**:

```bash
cd ~/Repo/video-mentions/projects/youtube/"Animation flowbiz youtube"
TXT="Twoje zdanie" SUB="podpis" FPS=30 ALPHA=1 node render.js txt-linia-lewy
# → out/txt-linia-lewy_alpha.mov
```

`SUB` jest opcjonalny — pusty znika razem z bursztynową belką.
Warianty: `txt-linia` (wyśrodkowany, 76 px) i `txt-linia-lewy` (blok po lewej, 64 px,
zalecany, bo nie zasłania mówiącego).

Przykłady w tym katalogu: `txt-linia-PRZYKLAD-v1` i `txt-linia-lewy-PRZYKLAD-v1`
(treść: „Nie kupujesz systemu. Kupujesz własność kodu.").

## Co zmieniło się w v5

**Obrys na bursztynie wycofany** — wyglądał jak naklejka. Mały bursztyn (nadtytuły, podpisy)
wrócił na **ramkę**; duży bursztyn („szybko i tanio?") dostał **cień** zamiast konturu.
Biel bez zmian: waga 900 + twardy cień.

**Ciemne karty zostaly nietkniete** i to jest swiadome: okno IDE, panele platform, karta
werdyktu i znacznik odcinka **sa elementem ukladu**, a nie latka na czytelnosc. Ramka pod
napisem to obejscie; karta z trescia to projekt. Nie kasuj drugiego przy sprzataniu pierwszego.

Zasada, ktora z tego wynika:

| Element | Czego potrzebuje |
|---|---|
| naglowek / akapit **bialy** | nic — waga 700–900 + twardy cien |
| **bursztyn** | **albo** pigulka, **albo** obrys — jedno z dwoch, nigdy oba |
| cokolwiek w ciemnej karcie | nic, karta juz to zalatwia |
