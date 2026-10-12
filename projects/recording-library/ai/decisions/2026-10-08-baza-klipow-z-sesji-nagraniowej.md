# Baza klipów z sesji nagraniowej zamiast montażu pojedynczych rolek

**Data:** 2026-10-08
**Status:** ✅ wdrożone (etap 1: cięcie, baza, ranking) · plan (etapy 2+: napisy, grafiki, HyperFrames)

## Problem

Jedna 93-minutowa sesja zawiera 36 reklam z promptera (część w kilku dublach),
4 case studies, odcinek o Open Mercato i freestyle. Dotychczasowy pipeline
(`shorts IG`) montuje JEDEN short od początku do końca. Tu potrzeba bazy, z której
przez kolejne tygodnie (także w nocnych przebiegach bez nadzoru) powstają rolki,
reklamy Meta, kampania AI Słupsk na listopad i odcinki YouTube.

## Diagnoza

- **Nagranie nie trzyma się promptera.** Mateusz improwizuje: dokłada zdania
  („Pokażę Ci, gdzie można zaoszczędzić kilkadziesiąt godzin tygodniowo”), zmienia
  liczby (3 h → 6 h, poprawka na nagraniu), zamienia miasto (Ustka → całe
  Pomorze). Automatyczne dopasowanie do tekstu scenariusza daje fałszywe granice.
  Decyzja o dublu zapada po **czytaniu transkrypcji**, scenariusz służy tylko
  do identyfikacji nagrania.
- **Powtórki siedzą w środku ujęć**, nie tylko między dublami (np. „a później
  najpierw porządkujemy dane…” w jednym zdaniu). Cięcie musi iść po czasach słów,
  a nie po segmentach Whispera.
- **Whisper zapętlił się na długim pliku** („55. 55. 55.” od 35. minuty) przy
  domyślnym `condition_on_previous_text`. Druga próba z
  `--condition-on-previous-text False --hallucination-silence-threshold 2` czysta.

## Decyzja

1. **Decyzje w kodzie, baza generowana.** `tools/edl.py` trzyma przedziały
   `[od, do)`, oceny i uwagi; `build_clips.py` dociąga granice do słów i generuje
   `data/clips.json` + `data/catalog.md`. Ręcznie edytuje się tylko EDL.
2. **Transkrypcje w gicie** (`data/transcripts/`, 1,3 MB). Ponowny przebieg
   Whispera daje inne czasy słów — bez zamrożonej transkrypcji EDL przestaje
   pasować.
3. **Dwa kadry na klip:** master 16:9 (pod HyperFrames i YouTube) i pion
   9:16 z twarzą w górnych 1215 px i wolnym panelem 705 px na grafikę.
   Pełnoekranowy pion z 720p (×2,67) odrzucony jako za miękki.
4. **Ranking `hook × 2 + delivery`** — hook waży podwójnie, bo o zatrzymaniu
   decydują 3 pierwsze sekundy. Oceny redakcyjne, przed budżetem do predyktora.
5. **Kontrola transkrypcją gotowego pliku** (`verify.py`): pokrycie słów ≥ 90%,
   brak nowych powtórzonych trigramów, a/v ±0,1 s.

## Pułapki

- `-c copy` przy cięciu zakazane (klatki kluczowe) — każdy klip jest
  przekodowany, sklejki jednym przebiegiem `trim`/`concat` z jednego wejścia.
- Granica przedziału nie może wejść na sąsiednie słowo (`GUARD` 40 ms), inaczej
  do klipu wraca początek wyciętego dubla.
- Whisper potrafi pominąć falstart albo przesunąć czasy słów przy kilku krótkich
  próbach (ad-14, ad-29). Tam granica idzie z ciszy w sygnale — EDL przyjmuje
  `(od, do, dokładny_start, dokładny_koniec)`. Wykrywa to tylko `verify.py`.
- Nazwy klientów tylko w polu `client` bazy. W reklamach z promptera nazwy nie
  padają („producent mebli ogrodowych”) — tak ma zostać.

Powiązane: `projects/shorts IG/ai/decisions/2026-08-19-pipeline-shortow-z-telefonu.md`
(pipeline jednego shorta — napisy i muzyka stamtąd są do przeniesienia w etapie 2).
