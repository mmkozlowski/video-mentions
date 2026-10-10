---
name: wstawki-rozdzielczosc-pod-projekt
description: Wstawkę renderuj w 1920x1080 i pozwól edytorowi skalować w DÓŁ; render pod niższe płótno rozsypuje krawędzie małego tekstu
metadata:
  type: reference
---

**Renderuj wstawkę w 1920×1080 i pozwól edytorowi skalować ją w dół. Nigdy w górę.**

Skalowanie w dół uśrednia nadmiarowe piksele i zachowuje jakość. Skalowanie w górę jej nie
odtworzy — napis wyrenderowany jako 16 pikseli wysokości i powiększony 1,5× to poszarpana
krawędź, bo antyaliasing nie ma z czego zbudować gładkiego przejścia.

**Why:** 20.08 wstawka 1920×1080 weszła do CapCuta przycięta (edytor dopasowuje klip do
płótna). Uznałem, że rozwiązaniem jest render 1280×720 „pod projekt" — i to pogorszyło sprawę.
Eyebrow o rozmiarze 24 px w projekcie 1920 zszedł do **16 px realnych**, a CapCut i tak
skalował wstawkę w górę. Duże płaskie panele wyglądały dobrze, bo na nich skalowania nie widać;
rozsypał się **sam tekst na przezroczystości**. To myli, bo objaw wygląda na problem z alfą
albo z kodekiem, a jest zwykłym brakiem pikseli.

**How to apply:** przycięcie w edytorze to **nie** powód do zmniejszania renderu — to znak, że
edytor dopasowuje wstawkę do płótna. Ustaw skalę klipu ręcznie albo zrównaj płótno z 1920×1080.
`W`/`H` w rendererze zostają jako furtka na nietypowe płótna (9:16), nie jako lekarstwo na
przycięcie.

**Minimalne stopnie pisma liczone na 1920×1080:** eyebrow 34 px waga 700 (`letter-spacing`
maks. `0.18em`), etykiety w pigułkach 19 px, podpisy 21 px, tekst w kartach 24 px+, teza 50 px+.
Cienki i mocno rozstrzelony tekst jest najbardziej wrażliwy — powyżej `0.2em` podnieś wagę kroju.

**Pułapka CapCuta:** po podmianie pliku o tej samej nazwie edytor bierze kopię z cache'u
i nowej wersji nie widzi. Usuń klip z biblioteki mediów i wczytaj ponownie — inaczej oceniasz
poprawkę, której tam nie ma.

Powiązane: [[wstawki-alfa-nie-green-screen]], [[quicktime_wysoka_to_720p]]
