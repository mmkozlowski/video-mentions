---
name: nigdy-nie-rozciagaj-kadru
description: Nigdy nie skaluj obrazu bez zachowania proporcji — lepiej rozmyte pasy niż spłaszczona twarz
metadata:
  type: feedback
---

**Proporcji obrazu nie wolno naruszać w żadnym wypadku.** Gdy materiał nie pasuje do kadru docelowego, dopełniamy go **rozmytą kopią** albo przycinamy — nigdy nie ściskamy ani nie rozciągamy.

**Why:** w dzielonym ekranie kadrowałem górę jako `crop=iw:ih*0.62`, a potem `scale=1080:960` — czyli obszar 1080×1190 wciskany w 1080×960. Twarz Bartka wychodziła **spłaszczona o 20%** i od razu to widać. Właściciel wyłapał to natychmiast: „rozciągnąłeś tak, że wygląda niekorzystnie". Rozmyty pas na boku nikomu nie przeszkadza, zdeformowana twarz dyskwalifikuje materiał.

**How to apply:**

- `scale=W:H` na materiale o innych proporcjach = **błąd**. Zawsze albo `scale=W:-2` / `scale=-2:H` (jeden wymiar wolny), albo `force_original_aspect_ratio` plus `crop`, albo czysty `crop` bez skalowania.
- Gdy treść nie wypełnia kadru — **blur-fill**: `split`, tło `scale ... increase, crop, gblur=sigma=40, eq=brightness=-0.26`, treść `scale=W:-2`, na wierzch `overlay=(W-w)/2:(H-h)/2`. Przy jasnym, gładkim tle rozmycie czyta się jak głębia, nie jak pasy.
- **Najbezpieczniejszy wariant to czysty `crop` bez `scale`** — zero ryzyka deformacji. Tak jest teraz zrobiona górna połowa zakończenia: `crop=1080:960:0:(ih-960)/2` na klipie 1080×1920.
- Weryfikacja przed pokazaniem: wytnij klatkę i porównaj proporcje twarzy ze źródłem. Deformacji rzędu 10–20% nie widać w liczbach z `ffprobe`, tylko na oko.

Powiązane pułapki montażowe: [[montaz-pulapki-synchronizacji]].
