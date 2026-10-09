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

**Why:** odbiorca w pionie ma jedną rzecz do przeczytania naraz. Duplikat tekstu i ścisk
zabijają czytelność, a w podglądzie na komputerze tego nie widać.

**How to apply:** każdy nowy element w pionie → zapytaj, co jeszcze jest wtedy na ekranie.
Mechanika w `projects/recording-library/tools/package.py` (`caption_blocks`, `intro`,
`zooms`, `slate`). Przed renderem uruchom `tools/layout_audit.py`, bo mamy dużo układów
i tekst wychodził poza kartę. Powiązane: [[pion-strefy-zakazane-reels]], [[copy-i-hook]].
