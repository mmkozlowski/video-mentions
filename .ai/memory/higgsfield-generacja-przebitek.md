---
name: higgsfield-generacja-przebitek
description: Przebitki w Higgsfield — GPT Image 2.5 (0,25 kr.) + Kling 3.0 Pro 5 s bez dźwięku (8,75 kr.); limit 429 przy partiach, rekomendacja presetu zamiast zadania, normalizacja 1924×1076
metadata:
  type: reference
---

Sprawdzone 10.10.2026 przy 18 przebitkach (162 kredyty):

- **Kadr:** `generate_image`, model `gpt_image_2_5`, 16:9, 0,25 kr. Partie po 4, bo przy 12
  część dostaje 429 (rate limit). Odrzucone nie kosztują i można je ponowić.
- **Ruch:** `kling3_0`, `mode: pro`, `sound: off`, `duration: 5`, media
  `{role: start_image, value: <job_id kadru>}`, 8,75 kr. Seedance 2.5 1080p kosztuje 60 kr.
  za 5 s, więc się nie opłaca.
- **Pułapka:** zamiast zadania przychodzi `preset_recommendation` („IN THE DARK”). Ponów
  z `declined_preset_id`.
- Wynik to 1924×1076 px i 24 kl./s, bez HDR. Kompresuj do 1920×1080 bt709 CRF 21
  (179 MB → 49 MB).
- W promptach zawsze „white Central European (Polish) people”, polskie realia. Mateusz
  odrzuca azjatyckie i ciemnoskóre postacie w swoich materiałach.

**Why:** kadry z GPT Image są realistyczne i dobrze trzymają polskie napisy (KOŁOBRZEG,
USTKA). Kling Pro ożywia je bez artefaktów taniej niż Veo przez Gemini API.

**How to apply:** manifest w `projects/recording-library/data/hf-broll.json`. Przed
większą partią sprawdź `balance` i koszt (`get_cost: true`). Limit ustalony przez
Mateusza: 400 kredytów na ten etap.
Powiązane: [[higgsfield-mcp-limity]], [[veo-gemini-api]], [[oznaczanie-tresci-ai]].
