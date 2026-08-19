# shorts IG — pionowe shorty z materiału nagranego telefonem

Reels/TikTok/Shorts **1080×1920, 30 fps**, składane z surowych nagrań z iPhone'a:
gadana głowa + przebitki + filmowany ekran. Bez generowania czegokolwiek, bez
kredytów — cały montaż liczy się lokalnie.

Czym to się różni od pozostałych projektów w repo:

| | `adresflow` / `granit` | **`shorts IG`** |
|---|---|---|
| źródło obrazu | generacje AI + plansze | **prawdziwe nagranie telefonem** |
| źródło głosu | lektor z TTS | **własny głos z nagrania** |
| oś czasu wyznacza | scenariusz i lektor | **to, co faktycznie padło** |
| główna robota | dobór ujęć pod tekst | **wycinanie pauz i dobór fragmentów** |

Dlatego nie używamy stąd `story.py` ani `voice.py` — kolejność jest odwrotna:
najpierw transkrypcja tego, co jest, potem decyzja, co zostaje.

## Pętla pracy

```bash
cd "projects/shorts IG"

# 0. materiał → assets/ (raz)
#    filmy do assets/raw/, zdjęcia do assets/photos/

# 1. transkrypcja każdego pliku ze znacznikami SŁÓW
for f in assets/raw/*.mov; do
  b=$(basename "$f" .mov)
  ffmpeg -y -v error -i "$f" -vn -ac 1 -ar 16000 "build/work/$b.wav"
  mlx_whisper "build/work/$b.wav" --model mlx-community/whisper-large-v3-turbo \
    --language pl --word-timestamps True --output-format json \
    --output-dir build/work --output-name "$b"
done

# 2. scenariusz: co zostaje → tools/edl.py
python3 tools/cut.py --plan          # sam plan cięć, bez renderu
python3 tools/cut.py                 # surowy skład → build/rough.mp4
python3 tools/cut.py a04 b05         # tylko wskazane wpisy, przy strojeniu

# 3. sprawdzenie składu — transkrypcja GOTOWEJ osi
ffmpeg -y -v error -i build/rough.mp4 -vn -ac 1 -ar 16000 build/work/rough.wav
mlx_whisper build/work/rough.wav --model mlx-community/whisper-large-v3-turbo \
  --language pl --word-timestamps True --output-format json \
  --output-dir build/work --output-name rough

# 4. warstwy i montaż
python3 tools/style.py               # napisy, plakietki, tytuł, plansza końcowa
python3 tools/assemble.py            # build/final-nomusic.mp4

# 5. muzyka — OSOBNO, na końcu
python3 tools/music.py --pick        # ranking: kolizja z pasmem mowy
python3 tools/music.py --try         # pełne wersje do odsłuchu → build/music-try/
python3 tools/music.py "March to Victory"   # wybrany → final/
```

Krok 3 nie jest opcjonalny. **Skład ocenia się transkrypcją, nie odsłuchem** —
przerwa większa niż 0,45 s między segmentami albo urwane słowo widać w wypisie
od razu, a w odsłuchu trzeba na nie trafić.

## Podział na etapy — i po co on jest

| Etap | Skrypt | Wynik | Co się tu decyduje |
|---|---|---|---|
| 1 | `cut.py` | `build/rough.mp4` | **co zostaje i w jakiej kolejności** |
| 2 | `style.py` + `assemble.py` | `build/final-nomusic.mp4` | napisy, przebitki, tytuł, domknięcie |
| 3 | `music.py` | `final/*.mp4` | podkład |

Etapy są rozdzielone dlatego, że **poprawka na etapie 1 unieważnia wszystko dalej**,
a poprawka na etapie 2 nie rusza etapu 1. Pokazywanie etapu 1 do akceptacji przed
włożeniem pracy w napisy oszczędza cały etap 2, gdy okaże się, że coś ma wylecieć.

`cut.py` cache'uje podklipy (`build/cuts/<key>.json` trzyma przepis), więc zmiana
jednego wpisu w EDL to ~5 s zamiast ~100 s.

## Zasada nadrzędna: oś dźwięku nie zmienia długości

Wszystkie efekty etapu 2 są **wyłącznie obrazowe** i wchodzą jako nakładki na
istniejącą oś. Żadnego `xfade`, żadnego przyspieszania ujęć, żadnego `atempo`.

Powód jest praktyczny: napisy są policzone z transkrypcji `rough.mp4`. Dopóki
dźwięk się nie rusza, pasują co do klatki i **żadna zmiana efektu nie wymaga
przeliczania napisów**. Domknięcie (zdjęcie z biurka + plansza końcowa)
doklejamy dopiero po skompletowaniu obrazu — przesuwa tylko ogon, więc też
niczego nie rozjeżdża.

## Progi cięcia pauz — łagodne z premedytacją

`PAUSE_MAX = 1.10`, `PAUSE_KEEP = 0.24` (`edl.py`). Doszliśmy tu w dwóch krokach
i oba warto znać:

| próg | wycięte | ujęć w jednym kawałku | jak wygląda |
|---|---|---|---|
| 0,30 s | 9,1 s | 7 z 19 | obraz skacze pod koniec materiału |
| 0,62 s | 2,9 s | 12 z 19 | dobrze, ale wciąż słychać przycinanie |
| **1,10 s** | **0,5 s** | **18 z 19** | **wersja przyjęta** |

Pierwsza wersja (0,30) była błędem: każde sekundowe przemilczenie i każde
zacięcie robiło osobne cięcie, więc pod koniec materiału szło kilka krótkich
ujęć jedno za drugim — czyta się to jak usterka, nie jak montaż.

Kontrola, że 1,10 nie zostawia dziur: w gotowej osi jedyna cisza dłuższa niż
1,2 s to **celowa** przebitka (2,9 s ujęcia z ręką sięgającą po jabłko).
Reszta przerw mieści się w 0,5–1,2 s, czyli w oddechu.

Materiał ma być **autentyczny, nie wygładzony** — oddech i potknięcie w kadrze
kosztują sekundę, nienaturalny przeskok kosztuje wiarygodność całego ujęcia.
Pojedyncze ujęcie może mieć własny próg — pole `pause_max` w EDL.

**Tnij zdania i całe myśli, nie oddechy w środku zdania.**

## Otwarcie i domknięcie: kadr, nie plansza

**Tytuł** jest nakładką na pierwszych 2,2 s materiału, a nie doklejoną planszą.
Pierwszy kadr to dzielony ekran (twarz z biegu u góry, kokpit agentów u dołu),
a napis siedzi w pasie na dole — tam, gdzie normalnie idą napisy, więc nic się
nie nakłada. Czarna płachta na starcie kosztuje dokładnie te sekundy, w których
widz decyduje, czy zostaje.

**Finał** też leży na ujęciu — na drodze, po której biegł, z jego cieniem
w kadrze. Domknięcie wraca tam, gdzie short się zaczął. Treść jest **pytaniem**,
nie deklaracją: czarna płachta z twierdzeniem czyta się jak koniec pliku, kadr
z ruchem i pytaniem czyta się jak koniec myśli (`question_plate()` w `style.py`,
`outro_over_video()` w `assemble.py`).

## Sześć rzeczy, które kosztowały czas przy pierwszym shorcie

**1. Kadr jest pionowy, ale plik NIE jest.** iPhone zapisuje 1920×1080 z
`rotation=-90` w metadanych. `ffprobe` bez `stream_side_data` pokaże materiał
poziomy i cała matematyka kadrowania wyjdzie obrócona. `cut.py` sprawdza rozmiar
**po** rotacji i mówi, gdy się nie zgadza.

**2. Jeden próg ciszy nie obsłuży całego materiału.** Na biegu wiatr i oddech
podbijają podłogę szumu do −28 dB w szczycie; w domu jest −38 dB. Przy domyślnych
−34 dB detektor nie znalazł w nagraniu z biegu **ani jednej** pauzy. Próg jest
per plik (`silence_db` w `edl.py`) i **zmierzony**, nie przepisany.

**3. Nie każdą pauzę widać w amplitudzie.** Między „przy komputerze" a „całą noc"
było 1,8 s samego wiatru — dla `silencedetect` to sygnał głośniejszy od niejednej
sylaby. Takie miejsca znajduje się po **braku SŁÓW w transkrypcji**, nie po braku
dźwięku. Reguła: cisza z pomiaru załatwia 90 % pauz, resztę trzeba zobaczyć
w wypisie słów.

**4. Ten ffmpeg nie umie napisów.** Homebrew buduje ffmpeg bez `libass`
i bez `freetype` — nie ma ani `subtitles`, ani `drawtext`
(`ffmpeg -filters | grep drawtext` → pusto). Napisy rysuje Pillow i wchodzą jako
**pas 1080×460 z alfą**, nie jako pełne klatki: montaż dostaje jedną nakładkę
zamiast dwustu.

**5. Nakładka dłuższa od materiału rozciąga obraz.** Pas napisów budowany
concat demuxerem wychodzi ~0,9 s dłuższy, bo lista musi kończyć się
powtórzeniem ostatniego pliku, a to powtórzenie dziedziczy czas poprzedniego
wpisu. `overlay` rozciąga wynik do dłuższego wejścia, a dźwięk (kopiowany) się
nie rozciąga — na końcu zostaje niema, zamrożona klatka. Dlatego `-t` jest
i na pasie napisów, i na wyjściu kompozycji. Wyłapała to dopiero kontrola
„dźwięk nie może być krótszy od obrazu" w `finalize_audio()`.

**6. Whisper myli nazwy własne.** „Opak Kreft" wyszło jako „opak krew". Napis idzie
na ekran, więc to błąd merytoryczny, nie literówka — słownik poprawek siedzi
w `FIXES` w `style.py` i **trzeba go przejrzeć dla każdego nowego shorta**, bo
każdy ma inne nazwy własne. Ostatnie sekundy transkrypcji potrafią się zapętlić
(„zrobione. zrobione. To To") — to artefakt dekodera, odsiewany automatycznie.

## Napisy

Okno napisu = jedna myśl: do 30 znaków, do 2,4 s, **nigdy przez kropkę**
(„minut. Ale jestem" czyta się jak błąd składu). Łamanie na dwie linie szuka
podziału wyrównującego długości — zachłanne zostawiało sieroty typu
„No dobra, bieg / już".

Aktywne słowo jest bursztynowe, reszta jasna, wszystko na kryjącej podkładce
`#0A0A08` przy 80 % — **podkładka nie jest ozdobą**: materiał skacze z jasnego
nieba na białą stronę www i bez niej połowa napisów znika.

Pas siedzi na `y=1190`, czyli w bezpiecznym polu między interfejsem Reels u góry
i u dołu.

## Muzyka

`MUS_VOL = 0.21` w `music.py` — dla porównania w reklamach z lektorem stoi 0,40.
Tutaj podkład ma podpierać rytm, nie prowadzić: mowa leci prawie bez przerwy,
a materiał ma brzmieć jak nagranie, nie jak spot.

Zmierzone na gotowym pliku: **−14,7 LUFS** integrated (cel IG ≈ −14), podkład
sam w przebitce bez mowy −18,6 dB, pod mową −16,6 dB.

Dobór: `python3 tools/music.py --pick` liczy, ile energii utwór ma w paśmie mowy
(300 Hz – 3 kHz) — im mniej, tym mniej walczy z głosem i tym mniej ducking musi
pompować. **Ale rankingu nie traktuj jak werdyktu**: surowy plik brzmi zupełnie
inaczej niż ten sam plik ściszony do 21 %, wystartowany od najgłośniejszego
fragmentu i duckowany. Do odsłuchu w kontekście służy
`python3 tools/music.py --try`, które renderuje pełne wersje z kilkoma
podkładami do `build/music-try/`.

## Kadrowanie i dynamika

Zbliżenie jest **statyczne, różne w sąsiednich ujęciach** (`zoom` w `edl.py`) —
cięcie czyta się jak zmiana kamery, a nie jak przeskok. Realizacja to
powiększenie + `crop` z powrotem do 1080×1920; `yshift` trzyma twarz w kadrze.

`scale=1080:1920` na materiale o innych proporcjach jest **zakazane** — deformuje
i widać to od razu (`.ai/memory/nigdy-nie-rozciagaj-kadru`).

Dzielony ekran (`patch_split`) kładzie gadaną głowę na górze, a kokpit z agentami
na dole, rozdzielone bursztynową kreską. Oba kadry to czysty `crop` bez skalowania.
Górna połowa idzie z `rough.mp4`, nie ze źródła — musi zostać zsynchronizowana
z dźwiękiem, który ma już powycinane pauzy.

## Co jest zrobione

**„Agenci pracowali całą noc"** (19.08.2026) — 152 s, 9:16, z podkładem
*March to Victory* (Silent Partner). ✅ skończony.

**152 s to świadomy wybór, nie przeoczenie.** Short pokazuje trzy dowody pracy
agentów; wycięcie któregokolwiek aktu robi z niego zapowiedź zamiast dowodu.
Nie skracaj go „bo reels" — a już na pewno nie progami cięcia pauz.

Trzy akty = trzy dowody: bieg i zapowiedź (`a*`), landing PPWR z 5 h transkrypcji
plus wpis i logo klienta (`b*`), fundamenty pod montaż YouTube (`c*`).

W `final/`: `v2` — wersja bieżąca; `v1` (113 s, bez aktu 3, cięcie pauz 0,62 s,
plansza końcowa na tuszu) zostaje do porównania.
Bieg rano → hook o sześciu agentach pracujących w nocy → dowód na ekranie:
kokpit z wyzwalaczami, landing page PPWR zbudowany z 5 h transkrypcji ze spotkań,
wpis na flowbiz.pl, logo klienta Opak Kreft.

Materiał: `IMG_1602` (gadana głowa, bieg), `IMG_1601` (ścieżka, przebitka —
także tło planszy końcowej),
`IMG_1603` (jabłonka — ujęcie idzie do 15,05 s, bo dopiero w 14,2 s ręka sięga
po jabłko), `IMG_1605` (ekran w domu, 199 s), **`IMG_1606`** (plan montażu
YouTube, 114 s), `IMG_1608` (biurko, domknięcie).

**Kompletność materiału sprawdzaj na starcie, nie po złożeniu.** `IMG_1606`
doszedł dopiero po zmontowaniu całości, bo nie został skopiowany razem z resztą —
a montaż wyglądał na kompletny, więc nic nie sygnalizowało braku. Numeracja
`IMG_` jest ciągła: **dziura w numerach = brakujący plik**, i to jedyny sygnał,
jaki masz (tu: 1604, 1605, **brak 1606**, 1607). **Kolejność zdjęć wynika z treści, nie z `creation_time`** — daty
w metadanych tych plików są niespójne (największy plik ma najwcześniejszą),
kolejność odtworzył numer `IMG_` i to, co widać w kadrze.
