---
name: audio-lektor-muzyka
description: Pułapki ścieżki dźwiękowej reklam — dryf głosu, płaska ekspresja, ciche intro podkładu, wybór Harrisona
metadata:
  type: reference
---

Ustalenia z produkcji spotów AdresFlow (2026-07-30). Wszystkie zweryfikowane pomiarem, nie na słuch.

**Lektor: NIGDY nie generuj fraz osobnymi wywołaniami.** Każde wywołanie `generate_audio` to niezależny sampling — barwa i akcent dryfują, w odsłuchu **słychać dwie różne osoby**, a nazwa marki bywa czytana raz po polsku, raz po angielsku. Generuj **jeden plik na cały tekst**, a granice fraz wykryj przez `silencedetect` (`detect_phrases` w `story.py` dobiera próg automatycznie pod oczekiwaną liczbę fraz).

**Wybrany głos: Harrison** `573e5163-59b3-4926-aab1-951ef2985f81` (ElevenLabs przez `text2speech_v2`). Wybrany po pomiarze ekspresji — `projects/adresflow/tools/voice_test.py` liczy zmienność wysokości tonu, rozrzut głośności i LRA:

| Głos | Zmienność tonu | Ekspresja |
|---|---|---|
| Wilder | 99,8 Hz | 8,6 (ale mówi ~17 % wolniej) |
| **Harrison ✅** | 46,3 Hz | 7,3 |
| Marcus (poprzedni) | 40,4 Hz | 6,4 — brzmiał płasko |

**Wykrzykniki w tekście nie naprawiają płaskiego głosu** — emfaza podniosła Marcusa z 6,4 na 6,9, czyli w granicach szumu. Płaskość siedzi w barwie, nie w interpunkcji.

**Zmiana głosu wymusza korektę scenariuszy** — każdy głos pauzuje inaczej, więc zmienia się liczba wykrytych fraz (przy przejściu Marcus → Harrison: `story` 6→7, `hs` i `dz` 5→6). `story.py` zatrzymuje się i wypisuje granice, gdy scenariusz się nie zgadza.

**Muzyka — trzy przyczyny „nie słychać podkładu", wszystkie naprawione:**
1. **Ciche intro** — biblioteczne podkłady zaczynają się cicho (zmierzone: 5,4 dB ciszej niż w środku). `music_offset()` startuje od najgłośniejszego fragmentu.
2. **Za agresywny ducking** — `threshold=0.05, ratio=8` to wyciszenie pod każdą sylabą. Teraz `0.12 / 4`.
3. **Za niski poziom** — `MUS_VOL` 0,22 → 0,40.

Efekt: podkład w planszy końcowej z −23,1 dB na ok. −16 dB. Podkład **musi przyjść z zewnątrz** — Higgsfield przez MCP nie generuje muzyki. Dobór: `pick_music.py` (mniej energii w paśmie mowy 300 Hz–3 kHz = lepiej; unikaj LRA > 5). Sprawdzone: `Frequency` (89 BPM) i `Magic Marker` (92 BPM) z YouTube Audio Library.

**Why:** każda z tych rzeczy brzmi jak „coś jest nie tak z dźwiękiem", a ma zupełnie inną przyczynę techniczną — bez pomiaru łatwo naprawiać nie to.

**How to apply:** po każdej zmianie lektora puść `voice_test.py`, a mowę w klipach AI weryfikuj Whisperem. Limity API: [[higgsfield-mcp-limity]], pipeline: [[pipeline-montazu]].
