# Film TAGO „chaos → system”: ilustracje AI ożywione w Kling + prawdziwe nagranie prototypu + lektor

**Data:** 2026-10-20
**Status:** ✅ wdrożone (film na spotkanie 21.10.2026)

## Problem

Na spotkanie z zarządem TAGO brakowało twardych liczb efektu (TAGO nie mierzy czasu). Zamiast slajdu
z mierzalnością — krótki film „jak to wygląda bez systemu / z systemem” (pomysł MK + MZ, 20.10).

## Przebieg i diagnoza

1. **v1 — slajdy:** klatki AI z najazdem kamery + zrzuty prototypu z ramkami. Odrzucone przez Mateusza:
   „to nie jest animacja, tylko slajdy” i „brakuje lektora”. Ruch kamery po stopklatce nie jest
   animacją — widz czeka na coś, co się wydarzy.
2. **v2 — animacja:** klatki ożywione w Kling 3.0 Pro (elementy się ruszają), część „system” nagrana
   jako prawdziwa praca w prototypie w dwóch oknach z kursorem, lektor ElevenLabs. Zaakceptowane.
3. Poprawka: przejście „A teraz to samo, z systemem” → „A teraz zobaczmy, jak to wygląda z PPWR Smart”;
   etykiety „Z systemem” → „Z PPWR Smart”. Marka pada w punkcie zwrotnym, nie na końcu.

## Decyzja

- Wzorzec filmu PPWR Smart = `ai/styl-wideo.md`.
- Świat klienta → ilustracja AI (ożywiona). Produkt → wyłącznie nagranie prawdziwego UI.
- Kompozycja w HTML odtwarzanym klatka po klatce (`await seek(t)` + Playwright), bo Chromium z Playwrighta
  nie dekoduje H.264 — warstwy ruchome idą jako sekwencje JPG wycięte ffmpegiem.

## Pułapki

- `record-prototype.js` przygotowuje stan pod zasłoną (reset, akceptacja wypraski, taśma Bugaj), żeby na
  nagraniu brakowało tylko folii Folmar — inaczej wyrób nie odblokuje się w jednym przebiegu. Komponenty:
  K-102 = wypraska, K-103 = folia, K-111 = taśma.
- Lektor generowany per kwestia (dryf barwy — patrz `.ai/memory/audio-lektor-muzyka.md`).
- Klatki AI kolidowały z zasadą „zero grafik AI” z notatki do prezentacji TAGO — decyzja MK/MZ.

Powiązane: vault `sales/tago/prezentacje/2026-10-21-animacja-chaos-system/storyboard.md`.
