---
name: kotwice-sklejki-odcinkow
description: assemble_episode — before: bierze OSTATNIE wystąpienie, first: pierwsze, word: tnie po końcu zdania (łapie przecinki); transkrypcja renderu w cache musi być nowsza niż render
metadata:
  type: feedback
---

Wstawki w odcinkach (`tools/assemble_episode.py`, PLAN) kotwiczy się na słowach z transkrypcji GOTOWEGO renderu
(`build/work/final-words/<odcinek>.json`). Trzy pułapki z 21.11 (otwarcia odcinków: treść 15–25 s, potem przedstawienie):

- **`before:X` = przerwa przed OSTATNIM wystąpieniem X** — pisane pod zakończenia („przed własnym pożegnaniem”).
  Do otwarć użyte trafiło 2 minuty za daleko. Do otwarć jest **`first:X`** (pierwsze wystąpienie).
- **`word:X` tnie po „końcu zdania” wokół X** — Whisper stawia przecinki i kropki w środku myśli, więc wstawka
  potrafi wejść po „jakiś szablon,”. Przy otwarciach lepsze `first:<pierwsze słowo następnego zdania>`.
- **Transkrypcja renderu leżała w cache** po zmianie cięcia (meble bez wstępu): kotwice liczone ze starej osi, 16 s obok,
  bez żadnego błędu. Od 21.11 `render_words` odświeża transkrypcję, gdy render jest nowszy.

**How to apply:** po zmianie EDL odcinka zawsze `assemble_episode --dry` + `review_episode` i czytaj tekst łączeń —
wstawka ma wejść między zdaniami, które się domykają. Render, który się nie wykonał (np. kotwica planszy przed
kursorem: „nie ma słowa X w klipie”), zostawia stary `render.mp4` — sprawdzaj datę pliku, nie tylko kod wyjścia skryptu.

Powiązane: [[montaz-pulapki-synchronizacji]], [[whisper-gubi-falstarty]]
