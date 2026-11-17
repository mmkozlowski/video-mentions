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

- **Koniec słowa za wcześnie** (16.10, ad-11-r1, uwaga Agaty „ucięte Excel”):
  Whisper kończył „Excelu” na 733,98, a głos trwał do 734,21 (potem zwarcie „t”
  z „trzy”). Sklejka na 734,06 urywała „-lu”. Przy mowie bez pauzy granica
  z obwiedni RMS co 10 ms — szukaj zwarcia spółgłoski następnego słowa.
- **Trzy duble w jednym słowie** (16.10, ad-35-w9, 2342–2356 s): „plus konkretne
  zastosowania…” padło 3 razy, transkrypcja miała je raz, z „w” trwającym 6,4 s.
  Napisy brały się z tych złych czasów, więc po cięciu poprawiono też czasy słów
  w `data/transcripts/session.json` (transkrypcja 3–4-sekundowych wycinków).

- **Napisy po cięciu w środku frazy** (17.11, uwagi Agaty): „no to [tutaj to] nie było” — po cięciu
  reguła luki w `cut.words_in` (≤ 2 słowa w luce ≤ 2 s → przeklejone za lukę) wciągała wycięte
  „tutaj to” z powrotem do napisów, a przy starcie od drugiego „Zanim” jedyne „Zanim” z transkrypcji
  wypadało. W EDL pole `caption_words=[(od, do, [(słowo, start, koniec), …])]` zastępuje słowa
  w przedziale źródła czasami zmierzonymi na sygnale. Sprawdzaj `build/library/<klip>/words.json` po cięciu.
- **Zgłoszone miejsce ≠ miejsce zająknięcia** (17.11, ad-12-r2): uwaga „między »Wiedza« a »o« 2 s”,
  a w źródle była tam pauza 0,6 s — falstart „jest w zzz…” siedział 2 s dalej. Szukaj transkrypcją
  wycinków 1–2 s wokół zgłoszenia, nie tnij w zgłoszonej sekundzie na ślepo.

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
