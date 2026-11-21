---
name: stoper-pion-alfa-zaslania-twarz
description: Układ lewej tercji stopera flowbiz istnieje tylko w 16x9-alpha; stoper-40-do-5-9x16-alpha ma tarczę na y 300–1000, czyli na twarzy w rolce
metadata:
  type: reference
---

`projects/flowbiz/final/stoper-40-do-5-16x9-alpha.mov` to nakładka w lewej tercji z kartą — twarz
odsłonięta. **Pionowa `9x16-alpha` NIE jest jej odpowiednikiem:** w `scene.html` klasa `alpha-mode`
zmienia układ tylko dla `fmt-land`; w pionie tarcza stoi na y 300–1000, tekst od y 1080 —
dokładnie tam, gdzie w rolce jest twarz (twarz u góry, panel na dole).

**Why:** łatwo założyć, że „stoper z alfą działa pod gadaną głowę" w każdym formacie — tak brzmiało
zlecenie z 06.11.2026. Wyszło dopiero przy czytaniu CSS sceny.

**How to apply:** w rolce 9:16 stoper wchodzi jako plansza na pełny ekran (`stoper-40-do-5-9x16.mp4`,
cięcie 1,2–4,9 s przed logo), a twarz wraca po nim. Jeśli ma być nakładką w pionie — potrzebny nowy
układ `alpha-mode .fmt-port` w dolnym panelu (y 980–1640), ~30 min pracy.
Powiązane: [[wstawki-uklad-lewy-domyslny]], [[pion-strefy-zakazane-reels]].
