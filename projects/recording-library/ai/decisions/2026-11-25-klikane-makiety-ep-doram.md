# Klikane makiety do ep-doram — Excel „przed”, Open Mercato „po”

**Data:** 2026-11-25
**Status:** ✅ wyrenderowane · ✅ wklejone do odcinka (v2, 26.11, akceptacja MK)

## Problem

MK po obejrzeniu ep-doram (11:48): w miejscach, gdzie mówi o ręcznej pracy w Excelu (kilka plików od kontrahentów,
dopisywanie kolumn, przeklejanie, ręczne drukowanie kodów kreskowych ok. 4:15), ekran jest nudny. Boczne listy
punktów i statyczne plansze nie pokazują, jak ta praca wygląda. Chciał makiet, które „same się klikają”: przed
(Excel) i po (system).

## Decyzja

- **HTML → HyperFrames, nie nagranie ani generacja.** Prawdziwego Excela klienta nie wolno pokazać (anonimowość),
  model wideo robi z UI papkę ([2026-07-30-ekran-produktu-z-html](../../../../.ai/decisions/2026-07-30-ekran-produktu-z-html.md)).
- **Wspólny kit** `animations/doram/shared/kit.js`: kursor z ripple, `moveClick`, `type` (litera po literze, seek-safe
  przez proxy), klawisze Ctrl+C/V/F/P w lewym dolnym rogu, `front()` do przełączania okien, arkusz z literami
  kolumn i numerami wierszy oraz `colsheet` z kolumnami jako blokami (wstawianie kolumny = przesunięcie transformem).
- **„Po” w wyglądzie Open Mercato**: powłoka z `tools/om_screens.py` przeniesiona do `om.css`/`om.js` i powiększona ×1,3
  pod pełny kadr ([ekrany-systemu-wyglad-open-mercato](../../../../.ai/memory/ekrany-systemu-wyglad-open-mercato.md)).
- **Długość = fragment wypowiedzi**, z czasami z transkrypcji gotowego pliku 11:48. Akcje na ekranie trafiają
  w słowa („przeklejała, drukowała” ×3 to trzy pętle, „80%, 100%” to ramki w tych kolorach).
- **Forma wklejenia: pełny ekran + PiP z twarzą**, jak istniejące plansze. Każda makieta zostawia prawy dolny róg pusty.
- Dane fikcyjne (Patiolux / Greenyard / Sonnwerk, zmyślone kody i ceny).

Lista momentów i plan wklejenia: `animations/doram/README.md`.

## Pułapki

- Kody kreskowe w wąskich etykietach znikały (flex shrink do zera). Pomaga `flex: none` + parametr `unit`.
- `hyperframes check` przy nachodzących oknach daje fałszywe `content_overlap`. Weryfikacja na klatkach.
- Rendery muszą iść po kolei z `--workers 2`, bo na Macu był prawie pełny swap (MK 25.11).
- Pamięć: [makiety-klikane-kit-hyperframes](../../../../.ai/memory/makiety-klikane-kit-hyperframes.md).

## Wklejenie (26.11)

MK 26.11 7:05: „Ok dodaj do video jest ok”. Zamiast przebudowywać odcinek od nowa (`package.py` → `assemble_episode.py`,
które zmieniłyby czasy względem zaakceptowanego 11:48), `tools/overlay_animations.py` kładzie animacje na **gotowy
plik** w czasach z jego transkrypcji.

- **Twarz w okienku z `master.mp4`, nie ze zmniejszonego finału.** Pod częścią animacji w finale leżą plansze z własnym
  okienkiem (np. ekran etykiet o 10:30), więc zmniejszony finał dałby miniaturę planszy. Kadr jak w `package.py`
  (przybliżenie ze środkiem w `FACE_CENTER_X`, 40% wysokości), położenie jak w `slate(pip=True)`.
- **Przesunięcie finał → master mierzone korelacją audio**, nie liczone z `assembly.json`. Długości wstawek są tam
  zaokrąglone do 0,1 s, a przesunięcie ze słów Whispera myliło się o ~0,2 s (6 klatek, widać to na ustach). Z korelacji
  wyszło 55,834 s przed ins-mid i 81,624 s po nim.
- **Bitrate stały ~12 Mb/s zamiast CRF 18.** CRF 18 na tym materiale (statyczne plansze, twarz) dawał ~3,5 Mb/s, a MK
  chce pełnej jakości pod YouTube.
- **Animacja 05: 94%, nie 95%.** Opis i rolka mówią 70% → 94% (MK 9:28: „po miesiącu osiągnęliśmy 94%”). Zdanie
  „AI dopasowuje to w 95%” (10:10) dotyczy jednego zamówienia, a licznik pokazuje łączną trafność, więc nie zawyżamy.

### Pułapki

- `split` jednego wejścia na kilka okienek rozłożonych po całym odcinku buforuje w RAM klatki do ostatniego użycia.
  Dlatego każdy kawałek mastera i każda maska to osobne wejście z `-ss/-t` / `-loop -t`.
- Wejście i wyjście to przenikanie 0,3 s, bez animowanego zjazdu twarzy jak w `slate(pip=True)`. Uproszczenie świadome:
  zjazd wymagałby skalowania klatka po klatce z maską zaokrągleń.
