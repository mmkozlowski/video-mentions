---
name: whisper-gubi-falstarty
description: Przy powtórkach dubla Whisper pomija falstart albo przesuwa czasy słów o ~1,5 s — sklejkę w takim miejscu ustawia się po ciszy w sygnale, a wykrywa transkrypcją gotowego klipu
metadata:
  type: reference
---

Sesja 8.10.2026, 58 klipów sprawdzonych ponowną transkrypcją: w dwóch sklejka
ustawiona po czasach słów zostawiła powtórzenie.

- **Falstart pominięty w transkrypcji.** „Zapraszamy szefów firm, osoby
  decyzyjne.” (2000,6–2004,4 s) nie ma w czasach słów — Whisper skleił go
  z drugim startem. Klip zaczynał się od dwóch „Zapraszamy szefów firm”.
- **Czasy słów przesunięte.** W okolicy kilku krótkich prób („A na hali…
  Zrobiono… A na hali”) słowa miały czasy przesunięte o ~1,5 s, więc cięcie
  „po słowach” wpuściło nieudaną próbę.

- **Słowo rozciągnięte na cały dubel** (11.10, „Jak składam moduł”, 248,5–253,2 s):
  „…a nie jak wygląda w głowie właściciela” padło dwa razy, a w transkrypcji
  raz — ostatnie „właściciela” trwało 4 s i przykryło drugi dubel. Cięcie
  „na końcu słowa” wpuściło oba. Wykryło to dopiero `verify.py`.

Lek: granica z **ciszy w sygnale** (`silencedetect` na wycinku ±5 s,
`-32…-38 dB`, `d=0.1–0.25`) i ewentualnie transkrypcja samego 2-sekundowego
wycinka. W EDL `projects/recording-library` takie miejsce zapisuje się jako
`(od, do, dokładny_start, dokładny_koniec)`.

**Why:** w obu przypadkach wypis słów wyglądał poprawnie — błąd był w samych
danych, z których liczyliśmy cięcie.

**How to apply:** po cięciu ZAWSZE transkrypcja gotowego pliku
(`tools/verify.py`) i szukanie powtórzonych trigramów, których nie ma
w oczekiwanym tekście. Naturalne powtórzenia („i dzięki temu” w dwóch zdaniach)
odsiewa się, czytając kontekst. Powiązane: [[whisper-dlugi-plik-petla]],
[[shorty-z-telefonu-pulapki]].
