# Wstawki do odcinka e01 — czytelność na materiale i sposób dostarczania

**Data:** 2026-08-20
**Status:** ✅ wdrożone (cztery wstawki e01 zaakceptowane, reguły zapisane w `CLAUDE.md` systemu animacji)

## Problem

Do trzech nagranych odcinków OpenMercato brakowało wstawek pod pierwsze minuty odcinka 01.
Powstały trzy nowe sceny (`e01-06`, `e01-07`, `e01-08` + wariant `e01-08b`), ale **żadna nie
wyglądała dobrze po wrzuceniu do montażu**, mimo że w podglądzie sceny wszystko było poprawne.

Diagnoza zajęła kilka rund, bo objawy nakładały się na siebie i każdy z osobna wyglądał
na inną przyczynę: zielona obwódka, rozmyte krawędzie, poszarpane litery, przycięty kadr.

## Diagnoza — pięć osobnych przyczyn, jedna po drugiej

**1. Zielona obwódka wokół liter.** Nie do naprawienia progiem keya. Krawędź litery jest
antyaliasowana, więc piksel brzegowy to mieszanka koloru tekstu i tła. Key usuwa czystą zieleń,
mieszane piksele zostają. → **render z kanałem alfa**, nie green screen.

**2. Czarne prostokąty pod napisami.** To `chroma-plate`, nałożone nadmiarowo na tekst jasny
i bursztynowy (reguła mówi wprost, że taki tekst podkładki nie potrzebuje). Przy alfie plate
nie ma racji bytu. → renderer **wyłącza plate'y w trybie alfa**.

**3. Nieczytelny tekst na jasnym swetrze i dłoniach.** Werdykt leżał gołym tekstem w dolnej
tercji. Ani jaśniejsza czerwień, ani poświata, ani pas-gradient tego nie uratowały.
→ **karta z własnym solidnym tłem**; przy okazji plik schudł ze 140 MB do 20 MB.

**4. Przycięta wstawka.** Edytor dopasowuje klip do płótna. Wyrenderowałem wtedy wersję 720p
„pod projekt" i **to pogorszyło sprawę** — eyebrow 24 px zszedł do 16 px realnych, a edytor
i tak skalował w górę. → **zawsze 1920×1080**, skalowanie w dół jest bezpieczne, w górę nie.

**5. Poszarpany bursztynowy napis — przyczyna właściwa.** Wskazał ją Mateusz, zestawiając dwa
napisy w tym samym materiale: biały ostry, bursztynowy poszarpany. **H.264 w 4:2:0 trzyma
luminancję w pełnej rozdzielczości, a chrominancję w ćwiartkowej.** Biały tekst niesie krawędź
w luminancji i przeżywa kompresję; nasycony bursztyn na jasnej ścianie niesie ją w chrominancji,
którą podpróbkowanie wyrzuca. → **mały bursztyn wyłącznie na ciemnej pigułce**.

## Decyzja

**Dostarczamy `_alpha.mov` (qtrle), nie green screen.** Kodek qtrle zamiast ProRes 4444 —
bezstratny, z alfą, natywny na macOS, ~9× mniejszy na płaskiej grafice. `_chroma.mp4` zostaje
wersją awaryjną dla narzędzi bez alfy i jest **z założenia gorszy** (bez scrimu i bez poświaty).

**Renderujemy 1920×1080 przy 30 kl./s.** Rozdzielczość nigdy poniżej płótna montażu; 30 kl./s,
bo nagrania źródłowe są w 30.

**Scena z tekstem powstaje w dwóch wariantach — lewym i wyśrodkowanym. Lewy jest domyślny.**
Wyśrodkowany ląduje na twarzy mówiącego; lewy zostawia prawą połowę kadru odsłoniętą, więc tekst
i mówiący działają równocześnie. Zatwierdzone przez Mateusza słowami „wygląda bardzo pro".

**Hierarchia narzędzi czytelności:** karta (tekst w dolnej tercji) → scrim gradientowy (wstawka
przejmuje kadr) → poświata (krótki podpis na spokojnym tle). **Nigdy dwa naraz.**

**Bez dryfu po ustawieniu się karty.** Ruch należy do wejścia; powolny ruch w bezruchu czyta się
na materiale jak usterka.

## Pułapki

**Weryfikuj po kompresji, nie na klatce PNG.** To kosztowało najwięcej rund — sprawdzałem
kompozyty jako PNG/JPEG, gdzie chrominancja jest pełna, więc uszkodzenie bursztynu **w ogóle
nie występowało**. Materiał trzeba przepuścić przez `libx264 -pix_fmt yuv420p`.

**Weryfikuj kompozytem na prawdziwej klatce z nagrania**, nie na podglądzie sceny. Na ciemnym
tle podglądu każdy problem czytelności znika.

**Edytor trzyma zaimportowane media w cache'u.** Podmiana pliku o tej samej nazwie nie działa —
oceniasz wtedy poprawkę, której tam nie ma. Zdarzyło się dwa razy. Dlatego gotowe wstawki idą
do `final/e01/` z **wersją i datą w nazwie**.

**Przycięcie w edytorze nie jest powodem do zmniejszania renderu** — to znak, że edytor dopasowuje
klip do płótna.

**Scrim nie działa z chromakeyem** — półprzezroczysta ciemna warstwa na zieleni daje ciemnozielony,
którego key nie usunie. `scene-shell.css` chowa go w trybie chromakey.

## Otwarte

- Kropkowana pionowa linia zgłoszona przy jednej ze wstawek. Skan kanału alfy pokazał zero
  niezerowych pikseli w pustych pasach kadru, więc **nie pochodzi ze wstawki**. Kandydatki:
  perforowana tablica w kadrze, podgląd proxy edytora. Nierozstrzygnięte — Mateusz odpuścił temat.
- `final/e01/` waży 375 MB. Konwencja repo mówi, że `final/` wchodzi do gita, ale przy tej wadze
  warto to przemyśleć — rendery są odtwarzalne jednym poleceniem.

## Powiązane

- `projects/youtube/Animation flowbiz youtube/CLAUDE.md` — reguły operacyjne
- `.ai/memory/wstawki-alfa-nie-green-screen.md`
- `.ai/memory/wstawki-czytelnosc-scrim-halo-karta.md`
- `.ai/memory/wstawki-uklad-lewy-domyslny.md`
- `.ai/memory/wstawki-rozdzielczosc-pod-projekt.md`
- `.ai/memory/tekst-nasycony-kolor-na-materiale.md`
