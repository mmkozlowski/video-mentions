---
name: montaz-pulapki-synchronizacji
description: Cztery błędy, przez które obraz rozjeżdżał się z dźwiękiem w spotach Granitu — każdy odkryty dopiero po reklamacji właściciela
metadata:
  type: reference
---

Cztery niezależne przyczyny rozjazdu obraz/dźwięk, wszystkie wyłapane dopiero wtedy, gdy właściciel obejrzał gotowy materiał. **Żadnej nie widać w logach — każdą trzeba zmierzyć.** Pełne opisy i procedury weryfikacji: `ads/tools/README.md`.

**1. `-c copy` przy przesuwaniu ujęcia.** Kopia strumienia tnie **wyłącznie na klatkach kluczowych**, więc żądane wejście w 7,34 s lądowało nawet sekundę wcześniej. Zawsze przekodowywać przy `-ss`, nigdy `-c copy`.

**2. Ujęcie z mówiącymi ustami restartuje się po przebitce.** Każda grupa jest domyślnie przycinana od zera. Po powrocie do twarzy obraz startował od początku, a lektor leciał dalej — rozjazd rósł do siedmiu sekund. Rejestr `LIPSYNC_SHOTS` liczy punkt wejścia jako `start_bloku − start_ścieżki`.

**3. Dźwięk dłuższy niż obraz.** `loudnorm` buforuje i wypuszcza dłuższy strumień niż wejście; `amix` jeszcze to wydłuża, a `-t` na wyjściu **tego nie ucina**. Ścieżka wychodziła 20,9 s przy 14,4 s wideo. Obraz i dźwięk renderujemy **osobnymi przebiegami** i porównujemy długości przed muxem.

**4. Napisy wyprowadzane z ciszy, nie z treści.** `silencedetect` widzi tylko pauzy, więc przerwa w środku zdania robiła z niego dwa okna i cały timeline przesuwał się o jedno. Teraz każdy wpis ma pole `say` (co pada) obok `lines` (co widać), a timeline powstaje z **czasów pojedynczych słów** z Whispera.

**Rozwiązanie, które zamyka całą klasę tych błędów — pomysł właściciela:** zamiast przecinać ujęcie z twarzą, **dzielimy ekran**. Bartek leci u góry bez jednego cięcia, na dole zmieniają się przebitki. Nie ma czego rozjechać, bo nie ma czego ciąć. Buduje to `build_split_outro()`.

**Zasada na przyszłość:** dźwięk i obraz mówiącej osoby tnij **z tego samego punktu tego samego nagrania**, jednym przebiegiem. Jeśli nowy klip zaczyna się w 3. sekundzie, jego audio też musi zaczynać się w 3. sekundzie.

**Jak weryfikować, zanim pokażesz komuś plik:**
- głośność w oknach co 2 s (cisza w środku nie ruszy średniej; `-91 dB` to zawsze błąd),
- długość ścieżki audio kontra długość wideo,
- klatka z gotowego spotu w chwili `T` kontra klatka ze źródła w `T − start_ścieżki`.

Kadrowanie: przebitki w dzielonym ekranie tnij **od górnej krawędzi** — wycinek ze środka ucinał zawodnikom głowy.
