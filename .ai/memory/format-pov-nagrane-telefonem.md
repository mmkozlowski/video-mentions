---
name: format-pov-nagrane-telefonem
description: Format POV „jak to robię" — ekran laptopa filmowany telefonem symulujemy w HTML; sprzedaje go geometria kadru i utrata jakości, nie sam UI
metadata:
  type: reference
---

Drugi format spotów obok narracyjnego (patrz [[copy-i-hook]]): **POV „jak to
robię"** — ktoś filmuje telefonem swój laptop i przechodzi realny workflow.
Bez lektora, muzyka niesie rytm, cała treść siedzi w przyklejonej planszy.
Wzorzec: `projects/adresflow/assets/reference/inspieracja-*.mp4` (Archsynth).

**Anatomia formatu** (zmierzona na oryginale, 36,8 s, 360p):

1. przyklejona plansza-hook w kolorowym pudełku, zostaje przez cały spot;
2. workflow **łącznie z czekaniem** — widać licznik sekund i statusy etapów;
3. brak lektora, muzyka od pierwszej sekundy;
4. minimalna plansza końcowa: jedna linia + domena;
5. **niska jakość obrazu jest częścią stylu** — czysty render 1080p czyta się
   jak zapis ekranu, nie jak film z telefonu.

**Ekran symulujemy w HTML** (`projects/adresflow/screens/pov-*`), a nie
nagrywamy. Sprzedają go dwie rzeczy, w tej kolejności:

**Geometria.** Laptop MUSI być mniejszy od kadru — pierwsza wersja miała ekran
na całą szerokość i obudowa wychodziła poza krawędź, przez co nie było widać
ani ramki, ani perspektywy. Klawiatura musi stykać się z dolną krawędzią
obudowy; przy `rotateX(58deg)` ścisnęła się do 53 % wysokości i wyszedł z niej
pasek — 52° i wyższy blok wypełniają kadr. Klawisze są poza głębią ostrości,
więc `filter: blur()` załatwia brak detalu.

**Utrata jakości.** W ffmpeg: zejście do 540p → szum → powrót do 1080p → lekki
chłodny cast → delikatny unsharp, żeby tekst nie zniknął. Szum sypiemy w
NISKIEJ rozdzielczości, bo po powiększeniu zlewa się w ziarno zamiast leżeć na
wierzchu jako piksele. Skrypt: `projects/adresflow/tools/pov.py`.

Dryf ręki to kilka **niesynchronicznych** oscylacji o różnych okresach
(3,1 s / 4,7 s / 7,5 s) na jednym wrapperze. Jeden równy tween czyta się jak
animacja, nie jak trzymany telefon.

**`hyperframes check` odrzuca ten format i to jest w porządku.** Refleks na
szkle i winieta celowo kładą się na tekście (`text_occluded`), a perspektywa
powiększa prostokąty (`content_overlap`) — bramka liczy na prostokątach i nie
wie o `overflow: hidden` ani o zamierzonej stylizacji. Przy POV weryfikuj
`snapshot`-em, nie bramką; przy zwykłych ekranach bramka nadal obowiązuje
(patrz [[ekran-produktu-hyperframes]]).

**Uczciwość:** to świadoma stylizacja — spot wygląda na nagranie użytkownika,
choć nim nie jest. Nie zmyśla nic o produkcie (UI i liczby są prawdziwe), ale
przy kampanii wartej powołania się na „prawdziwego użytkownika" trzeba mieć to
z tyłu głowy. Najautentyczniejszy wariant to nadal 40 s nagrane telefonem przez
właściciela — reszta pipeline'u przyjmuje takie ujęcie bez zmian.

**Why:** format wygląda na najprostszy ze wszystkich (przecież to „tylko
nagranie ekranu"), a w praktyce cała robota siedzi w dwóch miejscach, których
nie widać na pierwszy rzut oka: w geometrii kadru i w celowym psuciu jakości.

**How to apply:** nowy spot POV zaczynaj od `cp -R screens/pov-rzut screens/pov-<nazwa>`,
podmień treść ekranu i planszę, potem `tools/pov.py`. Instrukcja:
`projects/adresflow/screens/README.md`.
