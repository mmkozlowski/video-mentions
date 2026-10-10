---
name: hyperframes-check-zaslanianie
description: Bramka `hyperframes check` — zwolnienie z zasłaniania działa tylko na zasłanianym tekście; scrim od 0,6 krycia liczy się jako zasłonięcie
metadata:
  type: feedback
---

`hyperframes check` (0.8.x) zgłasza tekst zasłonięty innym elementem. Zwolnienie
`data-layout-allow-occlusion` działa **wyłącznie na samym zasłanianym tekście** — nie na
elemencie, który zasłania, i nie dziedziczy się w dół drzewa. Warstwa przyciemniająca
(scrim) o widocznym kryciu ≥ 0,6 też liczy się jako zasłonięcie.

**Why:** przy animacjach flowbiz (10.10.2026) atrybut postawiony na kontenerze nakładki
nic nie dawał, a bramka blokowała render, choć kadr wyglądał poprawnie.

**How to apply:** zwolnienie stawiaj na konkretnym węźle tekstowym, który ma być
przykryty (np. tekst pod przelatującą kartą); scrim pod tekstem trzymaj poniżej 0,6 albo
zwolnij tekst, który świadomie leży pod nim. Przykład: `projects/flowbiz/screens/`.
