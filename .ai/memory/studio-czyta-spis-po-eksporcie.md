---
name: studio-czyta-spis-po-eksporcie
description: Studio czyta filmy z JEDNEGO wspólnego folderu ~/Media/flowbiz-wideo (poza gitem, niezależnie od gałęzi); eksport idzie sam po każdym renderze/sklejce; „odrzucone” w Studiu = do usunięcia (studio_cleanup.py)
metadata:
  type: project
---

Od 21.11.2026 (MK: „Studio czyta z jednego miejsca, my tworzymy nowe wersje, w Studiu zaznaczam, co do usunięcia”):

- **Jedno miejsce:** `~/Media/flowbiz-wideo/` (zmienna `STUDIO_SHARED`) — `studio-index.json` + `projects/<projekt>/`
  (`final/samples`, `final/thumbs`, `exports/studio-manifest.json`, `versions/<film>/<data>.mp4`). Podział na projekty;
  w projekcie serie i formaty (rolka/reklama/zajawka/odcinek). Studio (`flowbiz-ads-studio-cmo/.env`:
  `STUDIO_SOURCE_VIDEO_MENTIONS=/Users/mac/Media/flowbiz-wideo/studio-index.json`) czyta tylko stąd.
- **Automatycznie:** `package.py --render/--finalize-only`, `assemble_episode.py`, `assemble_short.py` wołają na końcu
  `export_studio.main()` (wyłączenie: `STUDIO_AUTO_EXPORT=0`). Plik kopiowany klonem APFS (`cp -c`) — 0 dodatkowego miejsca.
- **Wersje:** nowa wersja zastępuje plik pod tym samym id (decyzje i uwagi w Studiu zostają — klucz to id filmu),
  poprzednia idzie do `versions/`; w spisie `versions[]` z gałęzią, commitem, datą.
- **Usuwanie:** sekcja „odrzucone” w Studiu → `python3 tools/studio_cleanup.py` (podgląd) / `--tak` (usuwa pliki,
  archiwum ponad KEEP=2, wpisuje do `exports/removed.json`, żeby eksport ich nie przywracał). Tylko na polecenie MK.
- Strony podglądu w tailnecie (gotowe-*, probki-*) — już nie; przegląd tylko w Studiu.

**Why:** Studio było przypięte do worktree `cerith` i do ręcznego eksportu → „nieświeże pliki” i ryzyko utraty
wszystkiego przy usunięciu worktree.

**How to apply:** nie kieruj Studia na worktree; nowy projekt wideo = własny eksport do `projects/<nazwa>/` we
wspólnym folderze (index scala projekty po id). Restart Studia: zabij tylko jego PID-y (pamięć vaulta
`nie-pkill-szerokim-wzorcem`), start `PORT=4318 nohup npm exec tsx src/server.ts` w `~/Repo/flowbiz-ads-studio-cmo`.
