---
name: tekst-nasycony-kolor-na-materiale
description: Mały nasycony (bursztynowy) tekst na materiale wideo zawsze wyjdzie poszarpany — h.264 4:2:0 trzyma chrominancję w ćwiartkowej rozdzielczości; ratunek to ciemna pigułka albo biel
metadata:
  type: reference
---

**Mały nasycony tekst — u nas bursztyn `#F5A623` — nie może leżeć bezpośrednio na materiale
wideo.** Zawsze wyjdzie poszarpany i nie naprawi tego ani większy stopień pisma, ani wyższa
rozdzielczość renderu, ani antyaliasing.

Powód jest kodekowy: **h.264 w 4:2:0 trzyma luminancję w pełnej rozdzielczości, a chrominancję
w ćwiartkowej**. Biały tekst niesie informację o krawędzi w luminancji i przeżywa kompresję.
Bursztyn na jasnej ścianie ma niski kontrast luminancji — krawędź siedzi głównie w chrominancji,
którą podpróbkowanie wyrzuca.

**Test rozstrzygający:** jeśli w tym samym ujęciu biały napis jest ostry, a kolorowy poszarpany —
to jest ten problem, a nie render.

**Zasady:** mały bursztyn → na ciemną pigułkę (`.pill`); tekst wprost na materiale → biały
`#FAF8F0` wagi 700+; bursztyn bez podkładki tylko duży (50 px+); wewnątrz ciemnych kart bursztyn
jest bezpieczny.

**Why + pułapka metodyczna:** 20.08 diagnozowałem to przez kilka rund jako problem z alfą,
z kodekiem alfy i z rozdzielczością, bo **sprawdzałem kompozyty jako PNG/JPEG** — tam chrominancja
jest pełna i uszkodzenie nie występuje. Mateusz zobaczył je od razu, bo oglądał w edytorze.

**How to apply:** wstawkę oceniaj **po przepuszczeniu przez ten sam kodek co eksport**:

```bash
ffmpeg -loop 1 -t 1 -i klatka.png -ss 3.0 -i wstawka_alpha.mov \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto" \
  -frames:v 30 -c:v libx264 -pix_fmt yuv420p -crf 20 test.mp4
```

Powiązane: [[wstawki-czytelnosc-scrim-halo-karta]], [[wstawki-rozdzielczosc-pod-projekt]]
