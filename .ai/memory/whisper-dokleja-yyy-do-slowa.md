---
name: whisper-dokleja-yyy-do-slowa
description: „Yyy” i cisza siedzą w środku słowa z Whispera (słowo trwa kilka sekund) — cięcie po lukach ich nie widzi, trzeba czytać audio; czasy słów bywają przesunięte w ciszę
metadata:
  type: reference
---

Whisper nie zapisuje „yyy” jako słowa. Dokleja je razem z ciszą do sąsiedniego słowa:
w ch-offers-1 „wycen.” trwało 4,84 s, w tym 1,3 s ciszy i 0,8 s „yyy”. Cięcie po lukach
między słowami (`build_clips.tighten`) tego nie widzi i Mateusz dalej słyszał „yyyy”.

- Wykrywanie w audio (`projects/recording-library/tools/fillers.py`): RMS co 20 ms.
  Cisza: < −42 dB przez ≥ 0,55 s. „Yyy”: głos bez spadku o 5 dB (granicy sylaby) przez
  ≥ 0,5 s, bo normalna mowa ma taki spadek co 0,15–0,25 s.
- Ramki 5 ms (astats przed resamplingiem) są za krótkie, bo drgania głosu dają fałszywe
  „sylaby”. Najpierw `aresample=16000`, potem `asetnsamples=320`.
- **Druga strona medalu:** czasy słów bywają przesunięte w ciszę („Jestem” zaczyna się
  0,6 s przed głosem). Po wycięciu tej ciszy słowo liczone po początku znika z napisów
  i kotwic. Przypisuj słowa po największej części wspólnej z przedziałem (`cut.words_in`).

**Why:** bez tego „wycięte yyy” jest tylko w teorii, a naprawa ciszy gubi słowa i psuje
kotwice storyboardów.

**How to apply:** po każdej zmianie cięcia sprawdź, czy kotwice storyboardów dalej się
znajdują (`package.py` rzuca „nie ma słowa…”). Powiązane: [[whisper-gubi-falstarty]],
[[pion-jedno-na-raz]], [[montaz-pulapki-synchronizacji]].
