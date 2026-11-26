# Animacje „same się klikają” do odcinka ep-doram

Polecenie MK 25.11: *„w momentach gdzie mówię o excelach, przeklejaniu, generowaniu… więcej mockupów, które same się
będą klikać… 4:15 kody kreskowe… kolumny Excela… otwórz Excel, otwórz inny Excel — dorób te animacje, bo są kluczowe;
przygotuj, pokaż, później wkleimy”*.

Sześć kompozycji HyperFrames 1920×1080, 30 fps, bez dźwięku. Każda trwa dokładnie tyle, ile fragment wypowiedzi.
Wszystkie dane są fikcyjne: kontrahenci *Patiolux Handel GmbH*, *Greenyard Outdoor Ltd* i *Sonnwerk Möbel GmbH*,
produkty mebli ogrodowych i ceny są zmyślone. Nie ma nazwy klienta, dostawców, osób ani prawdziwych cen.

## Lista momentów (czasy w gotowym pliku 11:48, `ep-doram__youtube-F--with-inserts.mp4`)

Czasy pochodzą z transkrypcji Whisper samego finału, nie z surówki.

| # | Wejście → wyjście | Co mówi MK | Animacja | Długość |
|---|---|---|---|---|
| 03 | **1:17.7 → 1:38.7** | „tą samą rzecz nazwać na kilkanaście sposobów… raz po niemiecku, raz po angielsku… rozszyfrowanie bardzo czasochłonne” | PRZED: arkusz zamówień z dwóch lat, Ctrl+F „teak”. 8 nazw jednego krzesła zapala się po kolei, dostaje znaczki DE/EN i nitki do jednego produktu w katalogu, na końcu „?” | 21.0 s |
| 02 | **2:39.3 → 3:09.0** | „dopasować różne nazwy… sprawdzić ceny z katalogiem rozproszonym na różne Excele… dopisać swoje kolumny… trzech kontrahentów, każdy inaczej” | PRZED: zamówienie DE → Ctrl+C → `katalog_2024.xlsx` → Ctrl+F „nie znaleziono” → „teak” → 89 € → drugi plik `cennik_eksport_2025.xlsx` → 94 € (w zamówieniu 92 €, notatka „która cena?”) → PPM „Wstaw kolumnę” ×2 („Nr kat.”, „Cena kat.”), ramki na rozjazdach → trzy okna kontrahentów z różnym układem kolumn | 29.7 s |
| 01 | **3:56.2 → 4:35.4** | „kod całego zamówienia, kod produktu, części… brała numery, wklejała do innego Excela… drukowała, przeklejała, drukowała ×3” | PRZED: trzy kolumny kodów, „104 pozycje × 3 kody = 312 etykiet” → Ctrl+C → `generator_kodow.xlsx` → Ctrl+V → kod się rysuje → Ctrl+P → Drukuj → etykieta wyjeżdża z drukarki. Pętla przyspiesza zgodnie z „przeklejała, drukowała”, zegar biegnie 08:00 → 10:27, licznik 4/312 | 39.2 s |
| 04 | **6:50.3 → 7:12.0** | „przy wgraniu dokumentu… prawdopodobieństwo, że to jest to… w kilku kolorach: nie dopasowałem, 80%, 100%” | PO (Open Mercato): plik przeciągnięty na import → „AI czyta 104 pozycje” → tabela, procenty dobijają od zera → dymek „to prawdopodobnie to” → legenda kolorów, potem ramki: czerwona (brak) → pomarańczowe (78/82%) → zielona (100%) | 21.7 s |
| 05 | **9:41.0 → 10:15.2** | „powiedzieć mu: ten produkt to tak naprawdę ten, z taką tkaniną… zapisaliśmy. AI zapamiętało… kolejne zamówienie… 95%” | PO: klik „wybierz produkt” → panel, wpisanie „fotel bali” → wybór produktu i tkaniny → „Dopasuj i zapisz” → wiersz zielony, komunikat „zapisano w słowniku”, karta „Pamięć AI”, słownik 214 → 215 → nowe zamówienie KW49, pozycje „z pamięci” → trafność 70% → 94% (łączna po miesiącu, MK 9:28; „95%” w zdaniu dotyczy jednego zamówienia) | 34.2 s |
| 06 | **10:29.8 → 10:52.3** | „bez AI, program bierze cztery numery, generuje PDF… po minucie 40 stron etykiet… z kilku dni 15 minut” | PO: karta zamówienia, cztery numery w ramkach → „Generuj etykiety” → PDF składa się 0 → 40 stron, przewijanie wszystkich stron → „PDF gotowy · 40 stron · 54 s” → Drukuj → „kilka dni → 15 min” | 22.5 s |

Pliki do obejrzenia (tailnet):
`https://macbook-pro-mateusz.taild4f545.ts.net/pliki/doram-anim-NN-<temat>.mp4` (01-kody-kreskowe, 02-kolumny-kilka-exceli,
03-nazwy-de-en, 04-dopasowanie-ai, 05-korekta-pamiec-ai, 06-etykiety-system) oraz `doram-anim-podglad.mp4`
(wszystkie po kolei w kolejności odcinka, 2:48).

## Wklejenie (MK 26.11 7:05: „Ok dodaj do video jest ok”)

Wklejone w wersji v2 odcinka: `tools/overlay_animations.py animations/doram/inserts.json`. Skrypt kładzie animacje
na gotowy plik 11:48 i dokłada okienko twarzy z czystego `master.mp4` (bez plansz pod spodem). Przesunięcie
finał → master zmierzone korelacją audio: 55,834 s przed ins-mid, 81,624 s po nim. Wejście i wyjście to przenikanie
0,3 s animacji razem z okienkiem, bez animowanego zjazdu twarzy. Kodowanie pod YouTube: 1920×1080, H.264 ~12 Mb/s, AAC 320k.

**Forma: pełny ekran z okienkiem twarzy MK w prawym dolnym rogu (PiP).** To ten sam wzorzec co obecne plansze
„Przeklej. Drukuj.” i ekrany systemu. `slate(pip=True)` w `tools/package.py` zjeżdża twarzą do okienka 0,27×
(x 1354–1872, y 740–1032). Każda animacja zostawia ten prostokąt pusty. Głos MK leci pod spodem bez zmian.

| # | Wejście | Wyjście | Co zastępuje w obecnym montażu |
|---|---|---|---|
| 03 | 1:17.7 | 1:38.7 | boczny panel „Jeden produkt, trzy nazwy” (lista 3 punktów) |
| 02 | 2:39.3 | 3:09.0 | boczny panel „Dlaczego to tyle trwało” i planszę z trzema Excelami kontrahentów (~3:01–3:09) |
| 01 | 3:56.2 | 4:35.4 | belkę „Kody kreskowe ręcznie: Excel → Excel → drukarka” (~4:18) i początek planszy „Przeklej. Drukuj.”. Plansza „Przeklej. Drukuj.” może zostać **po** animacji (od 4:35.4) jako puenta |
| 04 | 6:50.3 | 7:12.0 | boczny panel „Ten sam produkt u kontrahenta” i statyczny ekran importu (~7:05) |
| 05 | 9:41.0 | 10:15.2 | dziś twarz bez grafiki, nic nie wypada |
| 06 | 10:29.8 | 10:52.3 | statyczny ekran etykiet ZAM-2026-0418 (~10:30–10:52) |

Uwagi do wklejenia:
- **Ciąć po renderze, nie po surówce** (`.ai/memory/ciecie-wstawek-po-renderze-nie-po-surowce`). Czasy wyżej są
  czasami w pliku 11:48. Jeśli montaż przed wklejeniem się zmieni, trzeba je przeliczyć z nowej transkrypcji.
- Wejście i wyjście PiP trwa 0,5 s (zjazd twarzy). Animacje mają w pierwszych 0,5 s tylko wejście tła i okien, więc
  nic ważnego nie ginie.
- Rozdziały w opisie YouTube zostają bez zmian, bo animacje nie przesuwają czasu.
- 01 i 02 to „PRZED” (pomarańczowy kicker), 04–06 to „PO” (zielony). Przy zmianie kolejności fragmentów pilnuj, żeby
  „PO” nie wypadło przed „PRZED”.

## Jak budować

```bash
cd projects/recording-library/animations/doram
./snap.sh 01-barcodes 4,12,30 /ścieżka/na/klatki   # check + klatki kontrolne
./render.sh 01-barcodes                            # → build/01-barcodes.mp4 (poza gitem)
```

`render.sh` kopiuje `shared/` do `assets/` każdego projektu. HyperFrames wymaga ścieżek root-relative, więc
`assets/` jest w `.gitignore`. Rendery idą **po kolei, z `--workers 2`**, nigdy kilka naraz (MK 25.11: swap prawie
pełny). Jeden render trwa 15–25 s.

`shared/`: `kit.js` (kursor, klik, pisanie, klawisze, arkusz z kolumnami, kod kreskowy), `kit.css` (paleta F, okno
arkusza), `om.css` + `om-icons.js` + `om.js` (powłoka Open Mercato wygenerowana z `tools/om_screens.py`, rozmiary ×1,3).

`check` zgłasza dziesiątki `content_overlap` i `text_occluded`. To okna celowo nachodzą na siebie i etykiety leżą
w stosie. Weryfikacja jest na klatkach, nie na tej bramce.
