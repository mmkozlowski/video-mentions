---
name: wymowa-ppwr-lektor
description: Callum (ElevenLabs v4, głos angielski) połyka „wu” w PPWR; Whisper NIE wykrywa tego błędu (dopowiada znany skrót) — wymowę rozstrzyga ucho Mateusza na stronie z próbkami
metadata:
  type: feedback
---

Mateusz 23.10.2026: „PPWR musisz wymawiać po polsku, dziwnie czyta”. Zapis z `styl-wideo.md` („Pe Pe Wu Er”)
dawał w Whisperze `small` „PPUR”, czyli „wu” znikało.

Zmierzone na tym samym głosie (Callum, `elevenlabs_v4`):
- „…obowiązuje pe-pe-wu-er.” → PPWR ✓ (w środku zdania, z łącznikami)
- „Automatyzacja deklaracji pepewuer.” → PPWR ✓ (jednym słowem; tu „pe-pe-wu-er” dało „P-P-WR”)
- „Pe-pe-wu-er obowiązuje…” → „Te pebuer”, „PWR”, „P-Pewwer” ✗. **Akronim na początku zdania zawsze się psuje.**
  Przebuduj zdanie: „Od dwunastego sierpnia obowiązuje pe-pe-wu-er.”
- „pe-pe-wu-er smart kropka kom” → „ppwrsmart.com” ✓

**Korekta tego samego dnia:** Mateusz nadal słyszał „pepeuer” w kwestiach, które Whisper `small` zapisał
jako „PPWR”. **Whisper nie nadaje się do weryfikacji wymowy skrótów**, bo dopasowuje do znanego słowa.
Sprawdzone próbki: Callum w 5 zapisach i dwa polskie głosy natywne Inworld (Wojciech, Szymon). Mateusz wybrał
obecną wersję Callum „pe-pe-wu-er” („lepiej chyba nie będzie”).

**Why:** lektor z angielskim akcentem na nazwie produktu psuje całą reklamę, a w tekście ani
w transkrypcji tego nie widać.

**How to apply:** pisz „pe-pe-wu-er” w środku zdania. Whisper wyłapie tylko grube błędy (np. „Te pebuer”
na początku zdania). Przy nowym filmie albo nowym głosie wystaw stronę z 4–6 próbkami
(`ads/2026-10-23-youtube/voice-tests/index.html`) i daj Mateuszowi wybrać uchem **przed** renderem. Jeśli
problem wróci, następny krok to polski głos natywny (Inworld: Wojciech / Szymon).
Powiązane: [[audio-lektor-muzyka]].
