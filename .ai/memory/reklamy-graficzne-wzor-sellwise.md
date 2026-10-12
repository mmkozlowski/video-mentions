---
name: reklamy-graficzne-wzor-sellwise
description: Grafiki reklamowe wg SellWise/WiseGroup — jedna myśl, nagłówek w 2 grubościach z frazą w ramce, prawdziwy człowiek z imieniem i rolą, jeden przycisk; pierwsza seria z ikonami i liczbami była „tragiczna, chaotyczna”
metadata:
  type: feedback
---

Mateusz 10.10.2026 o pierwszej serii grafik statycznych (liczby, przekreślenia, ikony 3D,
stopka): „tragiczne, mocno chaotyczne”. Kazał zobaczyć reklamy SellWise i Let's Automate
(WiseGroup) w bibliotece reklam Meta.

Wzór, który działa (tools/static_ads.py):
- **jedna myśl** — nagłówek 6–10 słów w dwóch grubościach (400 + 800), kluczowa fraza
  w ramce w kolorze akcentu (`white-space:nowrap`, bo łamana ramka wygląda na błąd);
- najwyżej jedna linia pod spodem + jedna linia dowodu z liczbą z nagranego wdrożenia;
- **prawdziwy człowiek** (Mateusz) z podpisem imię + rola, duży, z prawej;
- **jeden przycisk** z czasownikiem; logo u góry; dużo powietrza.

Zdjęcia: prawdziwe, nie z Gemini (`Youtube Projects/Mój ryj` to w większości generacje ✦ —
wymagałyby oznaczenia AI). Marynarka: `packaging/brand/mateusz-marynarka.png` (ppwrsmart,
tło wycięte w Higgsfield, 614×768 — przy większym formacie lekko miękkie; lepsze zdjęcie
w wysokiej rozdzielczości podniesie jakość).

Biblioteka reklam Meta otwiera się Playwrightem z przeglądarką HyperFrames
(`~/.cache/hyperframes/chrome/...`), bez logowania; wyszukiwanie słowem łapie szum
(WALLTATTOO), więc filtruj po tekście reklamy.

**Why:** grafika w feedzie ma sekundę — zatrzymuje twarz i jedno zdanie, a nie układ
pięciu elementów. **How to apply:** nowa grafika = nowy wpis w `ADS`, nigdy nowy element
w układzie. Powiązane: [[grafiki-reklamowe-z-twarza-mateusza]], [[pion-jedno-na-raz]].
