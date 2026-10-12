---
name: pion-jedno-na-raz
description: Mateusz odrzucił pion z hookiem, napisami i kartą naraz — jedno zdanie na jednym tle, napisy znikają, gdy karta mówi to samo, ikony na osobnej planszy
metadata:
  type: feedback
---

Przegląd próbek 9.10.2026: w pionie **nie może być wszystkiego naraz**. Trzy razy ten sam
tekst na ekranie (hook, napis, karta) to „chaos i natłok”, a hook w kafelkach słowo po
słowie wygląda na pocięty.

- Jedno zdanie = jedno tło (blok, nie kafelek pod każdym słowem).
- Pod hookiem tylko twarz i hook. Dolny panel wjeżdża po chwili.
- Gdy karta powtarza wypowiedź, zostaje sam pasek, bez napisów.
- Ikony narzędzi na osobnej planszy z głosem pod spodem, nie w panelu pod twarzą.
- Lepiej osobna plansza z tekstem niż kilka wierszy na głowie.
- Logo nie jako mały znak w rogu, tylko duże na ostatnim ekranie (nowe „flowbiz AI”).
- Hook na dole, na twarzy, a nie pełnoekranowy tekst na start („traci wiarygodność”, do testu).
- Zawsze wycinać „yyy” i dłuższe milczenie. Zoom in/out na twarzy jest obowiązkowy.
- Wersja YouTube z panelem bocznym jest dobra, nie przebudowywać jej bez powodu.
- (9.10 po południu) Kilka zdań pokazuj po kolei, nie na jednym slajdzie. Hook ma grafikę
  (ikona albo schemat z oryginalnymi logo), a nie sam tekst. Hook pisz jak nagłówek, nie
  przepisuj 1:1 tego, co mówię. Numer i liczba z jednostką się nie łamią, a font jest
  stały, bez przeskoków. Nic nie zasłania głowy (chip zjechał na pierś). Tylko paleta A.

- (9.10 wieczór) Punkty listy to **hasła**, nie zdania: podobna długość (12–20 znaków),
  jedna składnia, jeden rozmiar fontu dla całej listy, nie słowo w słowo z mowy.
  `package.py` ostrzega przy > 22 znakach. Logo flowbiz AI ma bursztynowe „w”.

- Klip wycięty z odcinka (ch-*) dostaje **okładkę**: jedno zdanie kontekstu na pierwszym
  ekranie (pole `cover`). Bez niej „dobrze się słucha, ale nie wiadomo, o czym mowa”.
- **Przebitki mają wyglądać na polskie.** Żadnych azjatyckich postaci ani hal, bo Mateusz to
  odrzucił. Najpierw jego własne b-rolle (`~/Youtube Projects/b-rolle`, `real_broll.py`).
  W promptach generatora: polskie małe firmy, europejscy ludzie.

- (10.10) **Wzorzec odcinka, który Mateusz pochwalił („świetne animacje!”): ep-open-mercato-offers.**
  Na każde 15–30 s inna forma: uderzenie (burst/strike/slam z błyskiem), makieta pokazująca
  mechanizm z nagrania, klocek flowbiz, pasek dolny, twarz w okienku przy planszach.
  Kolejne odcinki składaj według niego.

**Why:** odbiorca w pionie ma jedną rzecz do przeczytania naraz. Duplikat tekstu i ścisk
zabijają czytelność, a w podglądzie na komputerze tego nie widać.

**How to apply:** każdy nowy element w pionie → zapytaj, co jeszcze jest wtedy na ekranie.
Mechanika w `projects/recording-library/tools/package.py` (`caption_blocks`, `intro`,
`zooms`, `slate`). Przed renderem uruchom `tools/layout_audit.py`, bo mamy dużo układów
i tekst wychodził poza kartę. Powiązane: [[pion-strefy-zakazane-reels]], [[copy-i-hook]].
