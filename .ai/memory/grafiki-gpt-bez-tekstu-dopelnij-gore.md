---
name: grafiki-gpt-bez-tekstu-dopelnij-gore
description: Tło do rolki z GPT Image generuj bez tekstu z pustą górną tercją, a 2:3 → 9:16 dopełniaj górę zamiast przycinać boki; to treść AI, więc rolka dostaje oznaczenie
metadata:
  type: reference
---

Rolki tekstowe flowbiz (06.11.2026, `projects/flowbiz/reels/blocks-2027/`): Codex `image_gen`
z wzorem stylu `assets/higgsfield-grafiki/izometria-biurko-po-orange.png` trzyma paletę czerń +
pomarańcz za pierwszym razem (9/9 grafik użytecznych, ~3 min równolegle).

- **W prompcie: zero tekstu, liter, cyfr i logotypów; obiekt w dolnych 60 %, górna tercja pusta.**
  Tekst kładziemy w HTML — poprawka zdania kosztuje render, nie generację.
- **GPT zwraca 1024×1536 (2:3).** `crop` do 9:16 obcina ~16 % szerokości — ucina obiekt na brzegach.
  Zamiast tego: `scale=1080:-2,pad=1080:1920:0:(oh-ih):0x070709` (kolor tła obrazu).
- **To treść AI:** znak w kadrze przez ~4 s pod strefą zakazaną (y ≥ 250) + przełącznik na platformie.
- Generator lubi „klocki" z okrągłymi wypustkami (skojarzenie z LEGO) — przy reklamie płatnej
  dopisz „prostokątne zaczepy, nie okrągłe".

**Why:** przycięcie „cover" ucięło fundament w pierwszym renderze; okrągłe wypustki wyszły bez proszenia.
**How to apply:** prompty i skrypt: `reels/blocks-2027/gpt/generate.sh`. Powiązane: [[oznaczanie-tresci-ai]], [[nigdy-nie-rozciagaj-kadru]], [[pion-strefy-zakazane-reels]].
