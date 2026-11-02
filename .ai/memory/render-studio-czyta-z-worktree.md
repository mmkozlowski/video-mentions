---
name: render-studio-czyta-z-worktree
description: Studio (localhost:4318) czyta filmy z worktree wskazanego zmienną STUDIO_SOURCE_VIDEO_MENTIONS, nie z ~/Repo/video-mentions — render poza nim jest niewidoczny; w świeżym worktree brakuje ignorowanych assetów
metadata:
  type: reference
---

**Skąd Studio bierze filmy.** Proces Studia (`flowbiz-ads-studio`, port 4318) ma w środowisku
`STUDIO_SOURCE_VIDEO_MENTIONS=<ścieżka>/studio-index.json`. To nadpisuje `~/Repo/video-mentions` z konfiguracji.
02.11.2026 wskazywało na worktree `~/orca/workspaces/video-mentions/cerith`. Tylko tam leżą `build/`
i `final/samples/` (oba poza gitem). W `~/Repo/video-mentions` nie było żadnego z nich.
Sprawdzenie zajmuje sekundę: `curl -s localhost:4318/api/sources` → pole `resolvedIndex`.

**Jak renderować z innego worktree.** Narzędzia liczą ścieżki od `Path(__file__)`, więc wystarczą
symlinki w swoim worktree: `build`, `final/samples`, `final/thumbs` → do worktree Studia. Trzeba też dołożyć
**ignorowane assety**: `assets/broll/hf/video/` (mp4 są w `.gitignore`). Bez nich HyperFrames nie renderuje
(`VIDEO_SOURCE_UNRENDERABLE`). Tniesz tylko swoje klipy (`cut.py <id>`, `compile_episode.build(<id>)`), bo
build jest wspólny z cudzą sesją. Manifest Studia podmieniasz tylko we wpisach swoich filmów, bo pełny
`export_studio.py` nadpisałby stan tamtej sesji.

**Pułapka, która to ukrywała:** nieudany render HyperFrames zostawiał stary `render.mp4`, a `finalize()`
kładł na nim nową muzykę. W `final/` lądował stary obraz z nowym czasem, bez żadnego błędu. Od 02.11
`package.py` kasuje `render.mp4` przed renderem. Zawsze sprawdzaj datę `render.mp4` i transkrybuj wycinek
gotowego pliku w miejscu poprawki, zanim uznasz render za udany.

Powiązane: [[montaz-pulapki-synchronizacji]], ADR `projects/recording-library/ai/decisions/2026-11-02-poprawki-studia-02-11.md`.
