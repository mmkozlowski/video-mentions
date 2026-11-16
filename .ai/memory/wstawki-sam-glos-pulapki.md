---
name: wstawki-sam-glos-pulapki
description: Wstawki „sam głos” (dogrywki, voice_only) — tło pod b-rollem, panel w pionie, END nie przed ostatnim słowem, akcent na słowie kluczowym
metadata:
  type: project
---

Wstawki z samym głosem (`voice_only` w storyboardzie, dogrywki 16.11 w `raw/2026-11-16-dogrywki-audio/`)
miały w nocy 16→17.11 cztery błędy, których render i `--check` nie zgłaszają — widać je dopiero na klatkach:

- **B-roll czarny:** tło `voice-backdrop` leżało nad całym oknem wideo, więc zakrywało też b-roll. Teraz siedzi
  w oknie, nad twarzą, pod b-rollem (`package.py`, `<!--VOICE-BACKDROP-->`).
- **Linia w pionie:** w 9:16 / 4:5 okno twarzy ma tylko `face_h` px — między planszami prześwitywał dolny panel.
  Przy samym głosie panel jest ukryty.
- **Ucięte ostatnie słowo:** cięcie END w sklejce (`content_end − 0,35 s`) ucinało „…dobrze pó-”, gdy klip miał krótkie
  wybrzmienie. `assemble_episode` zatrzymuje się błędem; poprawka = dłuższy koniec klipu w EDL, nie mniejszy guard.
- **Akcent na „z” / „w”:** `*` przed krótkim słowem koloruje tylko je — gwiazdka idzie przed słowo kluczowe
  ([[storyboard-gwiazdka-wyroznia-slowo]]).

Karty panelu bocznego (`list`, `compare`) przy samym głosie wychodzą jako mała karta w rogu — na planszach głosowych
używaj pełnoekranowych: `mockup kinetic`, `beat` (burst/slam/strike), `broll` z tytułem.

**How to apply:** po każdej sklejce `tools/review_episode.py <odcinek>` (klatki wstawek + transkrypcja łączeń) i obejrzyj
arkusze, zanim wystawisz plik. Powiązane: [[ciecie-wstawek-po-renderze-nie-po-surowce]].
