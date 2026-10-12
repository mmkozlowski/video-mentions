---
name: studio-czyta-spis-po-eksporcie
description: FlowBiz Studio widzi nowy/zmieniony film dopiero po tools/export_studio.py; uwagi agencji są w flowbiz-ads-studio/data/videos, nie w tym repo
metadata:
  type: project
---

Od 12.10.2026 plansza filmów to zakładka „Filmy” w `~/Repo/flowbiz-ads-studio`. Studio czyta
`studio-index.json` → `projects/recording-library/exports/studio-manifest.json`; oba pisze
`tools/export_studio.py` (też miniatury w `final/thumbs/`).

- **Po każdym renderze albo `scorecard.py` / `history.py` uruchom `export_studio.py`** — inaczej
  panel pokazuje starą historię, starą ocenę albo nie widzi nowego filmu (spis jest poza gitem).
- **Uwagi i sekcje agencji czytaj z `~/Repo/flowbiz-ads-studio/data/videos/<źródło>--<projekt>--<film>.json`**,
  nie z `data/board-state.json` (stara plansza `board_server.py` jest tylko zapasem).
- Studio na tej maszynie wskazuje worktree `cerith` przez `STUDIO_SOURCE_VIDEO_MENTIONS` w `.env`
  studia, bo rendery (`final/`) są tylko tam. Po przeniesieniu pracy do innego checkoutu zmień tę ścieżkę.

**Why:** spis jest kontraktem między repo — zmiana w danych bez eksportu jest dla panelu niewidoczna.

**How to apply:** render → `history.py` → `scorecard.py` → `export_studio.py`. Przy uwagach od agencji
zacznij od `data/videos/` w studiu. Powiązane: [[historia-zmian-per-film]].
