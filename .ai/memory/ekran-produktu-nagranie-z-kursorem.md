---
name: ekran-produktu-nagranie-z-kursorem
description: Gdy produkt ma działający prototyp — nagraj prawdziwą pracę (Playwright, dwa okna, rysowany kursor), nie zrzuty z najazdem; zrzuty z ramkami odbierane są jako „slajdy”
metadata:
  type: feedback
---

Zrzuty ekranu z najazdem kamery i złotą ramką zostały odrzucone (film PPWR Smart dla TAGO, 20.10.2026):
„to nie jest animacja, tylko slajdy”. Zadziałało nagranie **prawdziwej pracy** w prototypie.

Przepis (`projects/ppwrsmart/tools/record-prototype.js`):
- strona-rama 1920×1080 z dwoma `<iframe>` z tego samego originu (stan współdzielony przez
  localStorage/BroadcastChannel) — klient po lewej, dostawca po prawej;
- `recordVideo` Playwrighta na ramie; ramka dostępna przez `(await page.$('#fa')).contentFrame()`
  (`page.frame({name:''})` rzuca błąd);
- kursor to SVG na ramie, ruch easingiem do `locator.boundingBox()` (współrzędne już względem ramy),
  złoty „ripple” przy kliknięciu, pisanie litera po literze co ~55 ms;
- przygotowanie stanu pod zasłoną `#cover` z `pointer-events:none` (bez tego zasłona przechwytuje kliki);
- znaczniki czasu scen do `markers.json` — montaż tnie nagranie po nich.

**Why:** widz ma zobaczyć, że rzecz działa, a nie że ktoś zrobił ładne zrzuty. Kursor i zmiana statusu
w drugim oknie sprzedają przepływ lepiej niż jakikolwiek napis.

**How to apply:** jeśli produkt ma prototyp albo demo — nagrywaj; HyperFrames ([[ekran-produktu-hyperframes]])
zostaje dla ekranów, których jeszcze nie ma. Powiązane: [[ilustracja-ai-ozywiona-kling]].
