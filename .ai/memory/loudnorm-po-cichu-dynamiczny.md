---
name: loudnorm-po-cichu-dynamiczny
description: loudnorm z linear=true przechodzi PO CICHU w tryb dynamiczny z ogranicznikiem, gdy szczyty nie pozwalają na potrzebne wzmocnienie — trzask na mocnych sylabach
metadata:
  type: feedback
---

`loudnorm=...:linear=true` jest liniowy tylko wtedy, gdy się da: jeśli do celu (np. −16 LUFS) trzeba więcej wzmocnienia,
niż pozwala sufit szczytów (TP −1,5), filtr bez ostrzeżenia przechodzi w tryb **dynamiczny** z ogranicznikiem.
Na mowie słychać to jako trzask / trzeszczenie mocnych sylab.

**Why:** dogrywki 20.11 (−32 LUFS, szczyty −10,9 dBTP → potrzebne +16 dB, możliwe +9,4 dB). MK: „Pełna historia
w odcinku na YouTube — mam wrażenie, że trzeszczy”. Flat factor był 0 — to nie klasyczny przester, tylko ogranicznik.

**How to apply:**
- Sprawdzaj `normalization_type` w wyjściu drugiego przebiegu (`print_format=json`) — „dynamic” = problem.
- Ciche nagranie z wysokimi szczytami: łagodna kompresja (`acompressor=threshold=-28dB:ratio=3`) i STAŁE
  wzmocnienie `min(cel − I, −1,5 − TP)` — bez ogranicznika; resztę głośności robi finalize.
- Kontrola trzasku: szczyt równy dokładnie progowi (−1,50 dB) na wielu kawałkach = ogranicznik pracował.

Powiązane: [[montaz-pulapki-synchronizacji]], [[prosby-o-glosnosc-tlumacz-na-decybele]]
