---
name: ciecie-wstawek-po-renderze-nie-po-surowce
description: Punkt wklejenia wstawki liczysz z transkrypcji gotowego renderu i po końcu zdania — czasy słów z surówki są przesunięte o 0,5–1,5 s
metadata:
  type: project
---

Wklejając przerywnik do gotowego odcinka (`projects/recording-library/tools/assemble_episode.py`),
tniesz w przerwie po **końcu zdania** według transkrypcji **gotowego renderu**
(`build/work/final-words/<odcinek>.json`, mlx large-v3-turbo z czasami słów).

Noc 04→05.11: dwa pierwsze podejścia dały 9 łączeń w środku zdania, mimo że cisza w sygnale była
„najdłuższa w oknie”:
- kotwica rozdziału z storyboardu trafia w środek zdania, a najbliższa cisza to oddech
  („firma handlowa, która… | wstawka | handluje paszą”),
- czasy słów z transkrypcji surówki są przesunięte o 0,5–1,5 s względem renderu
  („katalog… | wstawka | AI.”),
- kropka w skrócie „np.” to nie koniec zdania.

**How to apply:** test łączenia = transkrypcja ±6 s wokół każdego połączenia gotowego pliku,
nie podgląd. Zamknięcie odcinka wchodzi przed własnym pożegnaniem z nagrania („Dzięki i do
usłyszenia”), nie po nim. Pułapka pokrewna: [[whisper-gubi-falstarty]].
