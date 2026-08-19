# Pipeline shortów pionowych z materiału nagranego telefonem

**Data:** 2026-08-19
**Status:** ✅ wdrożone (pierwszy short złożony: „Agenci pracowali całą noc", 107 s)

## Problem

Do repo trafił nowy typ materiału: cztery pionowe nagrania z iPhone'a (4,5 min
łącznie) — gadana głowa nagrana w trakcie biegu, przebitki i 199 s filmowanego
ekranu z efektami nocnej pracy agentów. Cel: jeden short na Reels, złożony bez
ręcznego montażu, z założeniem, że kolejne będą powstawać regularnie.

Istniejący pipeline (`adresflow`, `granit`) zakłada odwrotny kierunek: jest
scenariusz, do niego generuje się lektora, a montaż układa ujęcia pod głos.
Tutaj głos już istnieje i jest nieedytowalny — to, co padło na biegu, wyznacza
oś czasu. Dodatkowo z 4,5 min surówki musiało zostać ok. 1,5 min.

## Decyzja

**Trzy rozdzielone etapy, każdy z osobnym wynikiem do obejrzenia.**

| Etap | Skrypt | Wynik | Co się decyduje |
|---|---|---|---|
| 1 | `cut.py` (+ `edl.py`) | `build/rough.mp4` | co zostaje i w jakiej kolejności |
| 2 | `style.py` + `assemble.py` | `build/final-nomusic.mp4` | napisy, przebitki, plansze, dynamika |
| 3 | `music.py` | `final/*.mp4` | podkład |

Podział nie jest kosmetyczny: **poprawka na etapie 1 unieważnia wszystko dalej**,
a poprawka na etapie 2 nie rusza etapu 1. Pokazanie etapu 1 do akceptacji, zanim
włoży się pracę w napisy, oszczędza cały etap 2, gdy okaże się, że fragment ma
wylecieć.

**Zasada nadrzędna: oś dźwięku nie zmienia długości.** Wszystkie efekty etapu 2
są wyłącznie obrazowe i wchodzą jako nakładki na istniejącą oś — żadnego `xfade`,
`atempo` ani przyspieszania ujęć. Napisy są policzone z transkrypcji
`rough.mp4`, więc dopóki dźwięk stoi, pasują co do klatki i zmiana efektu nie
wymaga ich przeliczania. Domknięcie (zdjęcie + plansza końcowa) doklejane jest
dopiero po skompletowaniu obrazu, więc przesuwa tylko ogon. Tytuł otwierający
NIE jest planszą — leży jako nakładka na pierwszych sekundach materiału.

**Wycinanie pauz jest mierzone, nie zgadywane.** `silencedetect` z progiem
ustawianym **per plik**, na filtrze identycznym z tym, który idzie do renderu.
Pauza dłuższa niż `PAUSE_MAX` zostaje skrócona do `PAUSE_KEEP`.

**Progi są łagodne (1,10 / 0,24), nie agresywne — po dwóch korektach z 19.08.**
Pierwsza wersja miała 0,30 / 0,12 i pod koniec materiału obraz skakał: każde
zacięcie robiło osobne cięcie, więc szło kilka krótkich ujęć jedno za drugim.
Autor: „nie są to może idealnie powiedziane kwestie, ale dają poczucie, że to
jest bardzo autentyczne, i na tym głównie zależy". Przy reklamie z lektorem
każde cięcie bliżej ideału jest ulepszeniem; tutaj jest odwrotnie — im bardziej
materiał wygląda na zmontowany, tym mniej wygląda na prawdziwy.

**Skład ocenia się transkrypcją gotowej osi, nie odsłuchem.** Po `cut.py`
transkrybujemy `rough.mp4` i patrzymy na przerwy między segmentami. Ta sama
transkrypcja jest potem źródłem napisów — jedno źródło prawdy zamiast
przeliczania czasów ze źródeł na oś wynikową.

## Pułapki, które to kosztowało

**1. Pion w metadanych, nie w pliku.** iPhone zapisuje 1920×1080 z `rotation=-90`.
`ffprobe` bez `stream_side_data` pokazuje materiał poziomy. `cut.py` sprawdza
rozmiar po rotacji i ostrzega, gdy założenie nie zachodzi.

**2. Jeden próg ciszy nie obsługuje całego materiału.** Zmierzone szczyty szumu
w pauzach: bieg −28,3 dB, jabłonka −29,0 dB, dom −37,7 dB. Przy domyślnych
−34 dB detektor nie znalazł w nagraniu z biegu **ani jednej** pauzy — pierwszy
przebieg wyciął 0,00 s. Próg jest teraz polem `silence_db` w `edl.py`.

**3. Nie każdą pauzę widać w amplitudzie.** Między „przy komputerze" a „całą noc"
leżało 1,8 s samego wiatru, ze szczytami −14 dB — głośniej niż niejedna sylaba.
Takie miejsca znajduje się po **braku słów w transkrypcji**, nie po braku
sygnału. Pomiar ciszy załatwia ok. 90 % pauz; reszta wymaga spojrzenia w wypis
słów.

**4. Ten ffmpeg nie ma napisów.** Homebrew buduje ffmpeg 8.1 bez `libass`
i bez `freetype` — brak `subtitles` i `drawtext`. Napisy rysuje Pillow i wchodzą
jako pas 1080×460 z alfą (jedna nakładka zamiast ~230 z `enable=`).

**5. Whisper myli nazwy własne.** „Opak Kreft" → „opak krew", „ogarnięty" →
„obernięty". Na ekranie to błąd merytoryczny, nie literówka. Słownik `FIXES`
w `style.py` trzeba przejrzeć dla każdego nowego shorta. Ogon transkrypcji
potrafi się zapętlić — odsiewany automatycznie.

**6. Nakładka dłuższa od materiału rozciąga obraz.** Pas napisów z concat
demuxera wychodził ~0,9 s dłuższy niż materiał (lista musi kończyć się
powtórzeniem ostatniego pliku, a ono dziedziczy czas poprzedniego wpisu).
`overlay` rozciągnął do tego cały obraz, dźwięk kopiowany z `rough` się nie
rozciągnął i na końcu została niema, zamrożona klatka. `-t` jest teraz i na
pasie napisów, i na wyjściu kompozycji. **Wyłapała to wyłącznie kontrola
„dźwięk nie może być krótszy od obrazu"** — w logach nic nie było widać.

**7. `creation_time` skłamał o kolejności.** Największy plik miał najwcześniejszy
znacznik, a znaczniki mniejszych na siebie nachodziły. Kolejność odtworzono
z numeracji `IMG_` i z treści kadrów. **Do ustalania montażu nie używamy dat
z metadanych bez sprawdzenia w obrazie.**

## Korekty po pierwszym przeglądzie (19.08)

- Progi cięcia pauz podniesione 0,30 → 0,62 → **1,10 s**. Przy 0,30 wycinało
  9,1 s i obraz skakał; przy 1,10 wycina 0,5 s, a 18 z 19 ujęć jest w jednym
  kawałku. Sprawdzone, że to nie zostawia dziur: jedyna cisza dłuższa niż 1,2 s
  w gotowej osi jest **celowa** (przebitka z ręką sięgającą po jabłko).
- `IMG_1603` przedłużone do 15,05 s: samo zdanie kończy się w 12,74 s, ale gest
  sięgnięcia po jabłko pada dopiero w 14,2 s. **Cięcie na ostatnim słowie
  ucinało puentę ujęcia.**
- `IMG_1605` przywrócone od 0,55 s zamiast od 9 s: żart „dwóch kierowników
  pilnuje całego zamieszania" został wcześniej odrzucony jako niepasujący do
  obrazu, a chodziło o plecaki dzieciaków, które w tym kadrze są. **Zanim
  wytniesz ujęcie „bo obraz nie pasuje", sprawdź, czy zdanie nie mówi właśnie
  o tym, co widać.**
- Plansza otwierająca zastąpiona **nakładką na pierwszych 2,2 s materiału**:
  dzielony ekran (twarz + kokpit) z tytułem w dolnym pasie. Czarna płachta
  na starcie kosztuje sekundy, w których widz decyduje, czy zostaje.
- Plansza końcowa też zeszła z czarnego tła **na ujęcie z biegu** (droga, cień
  biegacza), a treść zmieniła się z deklaracji na **pytanie**. Twierdzenie na
  czarnym czyta się jak koniec pliku; pytanie na ruchomym kadrze czyta się jak
  koniec myśli i zostawia miejsce na odpowiedź w komentarzu.

## Dodany akt 3 (19.08, po domknięciu pierwszej wersji)

`IMG_1606` (114 s — plan montażu odcinków YouTube, trzy odcinki, grafiki
wygenerowane na green screenie) **nie został skopiowany razem z resztą materiału**
i wyszło to dopiero wtedy, gdy short był już zmontowany, z muzyką i zaakceptowany.

Nic tego nie sygnalizowało: cztery pliki układały się w spójną historię,
transkrypcje nie zawierały żadnego urwanego wątku, a kontaktówka z `IMG_1605`
nie pokazywała kadru, którego by brakowało. **Jedyny sygnał, jaki istniał, to
dziura w numeracji `IMG_`** — 1604, 1605, _brak 1606_, 1607.

**Wniosek do procedury: kompletność materiału sprawdzaj przed transkrypcją,
po numerach plików, a nie po tym, czy historia się klei.** Historia klei się
zawsze, bo składasz ją z tego, co masz.

Blok wszedł jako trzeci dowód, PRZED domknięciem — kończy się na „efekty nie
takie złe, ale wszystko trzeba przejrzeć i zweryfikować", co prowadzi wprost
do pytania na planszy końcowej. Nieużyty fragment `[81,80–95,26]` (naturalne CTA
własnymi słowami) jest opisany w `edl.py` jako alternatywa dla planszy.

## Długość: 152 s to decyzja, nie przeoczenie

Zaproponowałem skrót do ~127 s (wyrzucenie `b03`, `b07`, `b02` — najsłabszego
wizualnie ujęcia i dwóch fragmentów, które powtarzają to, co już padło).
**Autor odrzucił: „nie przejmuj się tą długością".**

Zapisuję to jako regułę, żeby nikt — ani człowiek, ani agent — nie „naprawiał"
tego przy kolejnym shorcie:

- **Kompletność dowodu bije długość.** Short pokazuje trzy rzeczy, które agenty
  zrobiły przez noc. Wycięcie któregokolwiek aktu robi z tego zapowiedź zamiast
  dowodu, a dowód jest tu produktem.
- Odbiorca jest niszowy i B2B — ogląda, bo chce zobaczyć, co się dało zrobić,
  a nie dlatego, że wciągnął go hook.
- **Progów cięcia pauz nie ruszamy nigdy w imię długości.** Skracanie oddechów
  cofnęłoby wszystko, co ustaliliśmy wyżej o autentyczności, a zysk jest
  rzędu kilku sekund. Jeśli już skracać — to całymi myślami.

## Czego świadomie nie zrobiono

- **Muzyki od razu** — weszła dopiero po akceptacji obrazu, i to była dobra
  kolejność: obraz zmieniał się cztery razy, a każda zmiana wymagałaby
  przeliczenia miksu. Wybrany podkład: *March to Victory* (Silent Partner),
  `MUS_VOL = 0.21`. Ranking `--pick` (kolizja z pasmem mowy) zawęził wybór do
  trzech, ale decyzję podjął odsłuch pełnych wersji z `--try` — **surowy plik
  z biblioteki brzmi zupełnie inaczej niż ten sam plik ściszony, przesunięty
  do najgłośniejszego fragmentu i duckowany pod mowę**.
- **Stabilizacji** ujęć z ręki. `libvidstab` nie ma w tej instalacji, a `deshake`
  przycina i faluje kadr. Drżenie telefonu jest tu częścią wiarygodności formatu.
- **Odmłodzenia b03** (ciemne ekrany terminala). Podbicie jasności i kontrastu
  pomaga, ale materiał nie stanie się czytelny — pełni rolę faktury „dowód pracy",
  nie treści do czytania.

Powiązane: [[../../../.ai/memory/montaz-pulapki-synchronizacji]],
[[../../../.ai/memory/nigdy-nie-rozciagaj-kadru]],
[[../../../.ai/memory/audio-lektor-muzyka]],
[[../../../.ai/memory/shorty-z-telefonu-pulapki]],
[[../../../.ai/memory/autentycznosc-bije-gladkosc]], instrukcja: `../../README.md`.
