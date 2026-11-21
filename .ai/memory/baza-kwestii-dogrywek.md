---
name: baza-kwestii-dogrywek
description: Dogrywki Mateusza tniemy do bazy kwestii (kwestie/<nr>.wav → lines.json + /kwestie w Studiu); nowe nagranie zawsze NA KOŃCU ORDER, a mowa bez pauzy dzielona w dołku energii
metadata:
  type: project
---

21.11.2026 (MK: „dobrze to wycinać i zbudować z tych moich tekstów bazę — może być w Studio”). Baza: `recording-library/tools/export_lines.py`
→ `~/Media/flowbiz-wideo/projects/recording-library/exports/lines.json` + `lines/<nr>.m4a`; Studio `/kwestie`.

**Why:** Mateusz nie mówi numerów, w nagraniu 21.11 część kwestii powiedział swoimi słowami i dołożył wolne wypowiedzi
(przedstawienia 44l–o, moduły M1–M3, ból abonamentu F1–F4). Bez bazy te nagrania giną w 7-minutowym pliku.

**How to apply:**
- Nowy plik dogrywek dokładaj na KONIEC `ORDER` w `dubs_ingest.py` — inaczej przesuną się zakresy wszystkich istniejących
  wstawek z `source="dubs"` (edl.py liczy w osi sklejonego pliku).
- Ingest liczy wzmocnienie z całości — po dołożeniu pliku poziom starych kwestii się zmienia (finalize i tak normalizuje).
- Gdzie mowa idzie bez pauzy (np. 47a–e, 73b→M1, 79), granica = dołek RMS (ramki 20 ms) w ±0,2 s od czasu Whispera;
  wpis jako lista zakresów (dokładne granice), kilka zakresów = sklejka zająknięcia (86: wycięte „na jeden”).
- Każde cięcie sprawdzone transkrypcją wyciętego pliku (large-v3) — kolumna `transkrypt` w mapie.
