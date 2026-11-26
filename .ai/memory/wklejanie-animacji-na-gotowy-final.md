---
name: wklejanie-animacji-na-gotowy-final
description: Animacje/wstawki pełnoekranowe na GOTOWY odcinek — twarz w okienku z master.mp4, przesunięcie finał→master z korelacji audio, bitrate stały pod YouTube
metadata:
  type: project
---

Wklejanie animacji do gotowego odcinka (ep-doram v2, 26.11) robi `projects/recording-library/tools/overlay_animations.py`
z planem `animations/<odcinek>/inserts.json`.

- Okienko twarzy bierz z `build/library/<odcinek>/master.mp4`, nie ze zmniejszonego finału, bo pod spodem bywają
  plansze z własnym okienkiem.
- Przesunięcie finał → master mierz korelacją audio (numpy jest tylko w `/opt/homebrew/bin/python3.13`). Słowa
  Whispera i `assembly.json` mylą się o 0,1–0,2 s, a na ustach w okienku to widać.
- CRF 18 na odcinkach z planszami daje ~3,5 Mb/s, a MK chce pełnej jakości pod YouTube: `-b:v 12M -maxrate 16M`,
  AAC 320k.
- `build/` i `final/` są tylko w worktree `cerith` (i w `~/Media/flowbiz-wideo/.../final/samples`). Czytać wolno,
  zapisywać tam nie.

**Why:** MK 26.11: „podłej wersję już w pełnej rozdzielczości”. Animacje nie mogą przesuwać zaakceptowanych czasów.
**How to apply:** przy kolejnym odcinku z animacjami skopiuj `inserts.json` i zmierz przesunięcia. Patrz [[makiety-klikane-kit-hyperframes]].
