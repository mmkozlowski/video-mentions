---
name: historia-zmian-per-film
description: Każda poprawka filmu (uwaga Mateusza, kontrola transkrypcją, zmiana stylu) trafia do historii tego filmu, zanim pójdzie render — data/video-history.json, widać ją w galerii
metadata:
  type: feedback
---

Mateusz 12.10.2026, po pierwszej rundzie poprawek z czasem („ep-vibecoding 2:00 — …”):
„prowadź też historię tych zmian dla danego video”.

W `projects/recording-library`: `python3 tools/history.py <id-filmu> "<czas> — co zmieniono" --by Mateusz|kontrola|Claude`
(jeden wpis = jedna runda, kilka zmian naraz jako osobne argumenty). Galeria pokazuje to pod filmem
jako „Historia zmian (N)”, najnowsze na górze.

**Why:** po kilku rundach nie wiadomo, co już poprawione, dlaczego film jest krótszy o 4 s ani czy
zmiana stylu (np. przekreślenie) objęła już ten plik; Mateusz ogląda galerię, nie git loga.

**How to apply:** przy KAŻDEJ zmianie filmu — także tej, której nikt nie zgłosił (kontrola znalazła
falstart, zmiana CSS wpływa na wiele plików) — dopisz wpis do każdego dotkniętego filmu, łącznie
z rolkami dzielącymi to samo cięcie. Czas w notce podawaj w osi filmu sprzed zmiany (tak, jak go
zgłoszono), a przesunięcie osi zaznacz słowami. Powiązane: [[whisper-gubi-falstarty]].
