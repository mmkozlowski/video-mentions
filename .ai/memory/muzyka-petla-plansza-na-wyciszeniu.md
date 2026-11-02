---
name: muzyka-petla-plansza-na-wyciszeniu
description: Film dłuższy niż utwór zapętla muzykę od początku — zmiana długości potrafi położyć planszę końcową na naturalnym wyciszeniu utworu; mierz planszę po każdej zmianie długości odcinka
metadata:
  type: feedback
---

`mix_music()` zapętla utwór (`-stream_loop -1`) z okresem równym **całej długości pliku**.
Kolejne przebiegi zaczynają się od 0, a nie od `offset`. Utwór domyślny ma 135,2 s, a ostatnie
~10 s to wyciszenie do zera. Plansza końcowa wypada na pozycji `(długość_klipu + offset) mod 135,2`.

02.11.2026: ep-8-wdrozen urósł o 23 s (dołożony kontekst w dwóch miejscach). Plansza trafiła na 129–133 s
utworu i spadła z −23 do **−45 LUFS**, czyli praktycznie cisza. Prośba brzmiała „muzyka 3–4% ciszej”.
Pierwsza poprawka `musicOffset` (10 s) trafiła w cichszy fragment utworu (−15,5 zamiast −10 LUFS)
i dała −8 dB zamiast −3. Dopiero offset 30,5 s położył planszę w części o tej samej głośności co wcześniej.

**Why:** zmiana długości odcinka zmienia miejsce w utworze, na które trafia plansza. Głośność całości
(−14 LUFS) tego nie pokaże, bo dominuje ją głos.

**How to apply:** po każdej zmianie długości filmu dłuższego niż utwór zmierz LUFS ostatnich ~2 s
(sama muzyka) w starej i nowej wersji. Przy rozjeździe dobierz `musicOffset` w storyboardzie tak,
żeby `(clip_len + offset) mod L` wypadało w części utworu o tej samej głośności (pomiar `ebur128`
w oknach 3 s). Zmianę raportuj w dB — [[prosby-o-glosnosc-tlumacz-na-decybele]].
