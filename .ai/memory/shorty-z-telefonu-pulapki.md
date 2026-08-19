---
name: shorty-z-telefonu-pulapki
description: Pięć pułapek montażu shortów z nagrań iPhone'em — rotacja w metadanych, próg ciszy per plik, pauzy niewidoczne w amplitudzie, ffmpeg bez libass, nakładka dłuższa od materiału
metadata:
  type: reference
---

Dotyczy każdego shorta składanego z **prawdziwego nagrania telefonem** (odwrotny
kierunek niż spoty z lektorem: głos już istnieje i wyznacza oś czasu). Pipeline:
`projects/shorts IG/`, instrukcja w jego `README.md`.

**1. Pion siedzi w metadanych, nie w pliku.** iPhone zapisuje 1920×1080
z `rotation=-90`. `ffprobe -show_entries stream=width,height` pokaże materiał
POZIOMY i cała matematyka kadrowania wyjdzie obrócona. Pytaj o
`stream_side_data=rotation` i licz rozmiar po obrocie.

**2. Próg ciszy jest per plik i musi być ZMIERZONY.** Zmierzone szczyty szumu
w pauzach jednego dnia zdjęciowego: bieg −28,3 dB, sad −29,0 dB, wnętrze
−37,7 dB. Domyślne −34 dB nie wykryło w nagraniu z biegu **ani jednej** pauzy —
pierwszy przebieg wyciął 0,00 s i wyglądało to na poprawny wynik. Mierz próg na
filtrze identycznym z tym, który idzie do renderu (wzmocnienie + highpass),
bo próg policzony na innym sygnale wskaże ciszę gdzie indziej.

**3. Nie każdą pauzę widać w amplitudzie.** 1,8 s samego wiatru między dwoma
zdaniami miało szczyty −14 dB — głośniej niż niejedna sylaba. Pomiar ciszy
załatwia ok. 90 % pauz; **resztę znajduje się po braku SŁÓW w transkrypcji**,
nie po braku sygnału.

**4. ffmpeg z Homebrew nie umie napisów.** Budowany bez `libass` i bez
`freetype` → nie ma ani `subtitles`, ani `drawtext` (sprawdź:
`ffmpeg -filters | grep drawtext`). Napisy rysuj w Pillow i wkładaj jako
**pas 1080×460 z alfą**, nie jako ~230 pełnoklatkowych nakładek z `enable=`.

**5. Nakładka dłuższa od materiału ROZCIĄGA obraz.** Pas napisów budowany
concat demuxerem wychodzi ~0,9 s dłuższy, bo lista musi kończyć się
powtórzeniem ostatniego pliku, a to powtórzenie dziedziczy czas trwania
poprzedniego wpisu. `overlay` rozciąga wynik do dłuższego wejścia, dźwięk
(kopiowany) się nie rozciąga i na końcu zostaje **niema, zamrożona klatka**.
Lek: `-t <długość materiału>` i na pasie napisów, i na wyjściu kompozycji.
Wyłapała to dopiero kontrola „dźwięk nie może być krótszy od obrazu".

**Bonus, który zmylił montaż:** `creation_time` w tych plikach kłamał
o kolejności — największy miał najwcześniejszy znacznik, a znaczniki mniejszych
na siebie nachodziły. Kolejność ustalasz numeracją `IMG_` i treścią kadru.

**Why:** każda z tych rzeczy daje wynik, który wygląda na poprawny —
skrypt kończy się kodem 0, plik powstaje, nic nie krzyczy. Widać dopiero na
gotowym materiale: obrócony kadr, zero wyciętych pauz, brak napisów.

**How to apply:** kolejność pracy to transkrypcja → wybór fragmentów → cięcie →
**transkrypcja gotowej osi jako kontrola** → napisy z tej samej transkrypcji.
Skład ocenia się wypisem słów, nie odsłuchem: przerwa > 0,45 s albo urwane słowo
widać od razu, a w odsłuchu trzeba na nie trafić. Powiązane:
[[montaz-pulapki-synchronizacji]], [[nigdy-nie-rozciagaj-kadru]],
[[audio-lektor-muzyka]].
