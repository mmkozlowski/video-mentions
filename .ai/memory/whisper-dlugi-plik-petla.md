---
name: whisper-dlugi-plik-petla
description: mlx_whisper na nagraniu > 30 min zapętla się („55. 55. 55.”) przy domyślnym condition_on_previous_text — wyłączać od razu
metadata:
  type: reference
---

Na 62-minutowej sesji (8.10.2026) `mlx_whisper` z large-v3-turbo zapętlił się
od 35. minuty: setki segmentów „55.” co 20 ms. Pliki 11 i 19 min z tego samego
dnia wyszły czysto. Przyczyna: domyślne `condition_on_previous_text=True` — model
karmi się własnym błędem i nie wychodzi z pętli aż do końca pliku.

Druga próba: `--condition-on-previous-text False --hallucination-silence-threshold 2`
— czysta transkrypcja, czasy słów poprawne, ~8× szybciej niż realtime na M5 Pro.

**Why:** pętla nie przerywa procesu ani nie zmienia kodu wyjścia — plik JSON
powstaje i wygląda na kompletny. Widać ją tylko w podglądzie logu albo
w liczbie powtórzeń tego samego tekstu.

**How to apply:** dla plików dłuższych niż ~20 min od razu dawaj oba flagi;
po każdej transkrypcji policz `Counter` tekstów segmentów — tekst powtórzony
> 5 razy to pętla. Powiązane: [[shorty-z-telefonu-pulapki]].
