---
name: ilustracja-ai-ozywiona-kling
description: Płaskie ilustracje wektorowe ożywia Kling 3.0 Pro bez psucia stylu i napisów, jeśli prompt nazywa konkretny ruch i zakazuje nowego tekstu; stopklatka z najazdem to nie animacja
metadata:
  type: reference
---

Sprawdzone 20.10.2026 na 8 klatkach GPT Image (płaska ilustracja, polskie napisy w kadrze), film PPWR Smart:
`kling3_0`, `mode: pro`, `sound: off`, 5 s (7 s dla przejścia), `start_image` = wgrana klatka,
8,75 kr./5 s. **8/8 za pierwszym razem**, styl i napisy w kadrze nienaruszone.

Prompt: „Flat vector illustration comes to life. <konkretny ruch>. Slow camera push-in. Keep the exact
flat illustration style, colors and composition. No new text, no cuts.” Konkret ruchu decyduje
o efekcie: „koperty wysypują się z monitora”, „pieczątka pęka”, „zegar przyspiesza”, „dokumenty
przelatują przez lejek do szuflad”.

Dopasowanie do sceny dłuższej niż klip: `setpts=<k>*PTS,minterpolate=fps=30:mi_mode=mci` — do ~0,6×
płynnie na płaskiej grafice.

**Why:** pierwsza wersja (stopklatki z najazdem kamery) została odrzucona jako „slajdy”. Ruch wewnątrz
kadru jest tym, co odbiorca nazywa animacją.

**How to apply:** upload klatek przez `media_upload` (PUT z nagłówkiem `If-None-Match: *`) →
`media_confirm` → `generate_video_batch` dla wszystkich klipów naraz. Powiązane:
[[higgsfield-generacja-przebitek]], [[ekran-produktu-nagranie-z-kursorem]].
