---
name: pion-strefy-zakazane-reels
description: Kadr 9:16 ma trzy strefy zasłaniane przez UI Reels/TikToka — górne ~230 px, prawa kolumna ~130 px, dolne ~260 px; wszystko u góry wchodzi dopiero po hooku
metadata:
  type: reference
---

Przy opakowaniu gadanej głowy w pionie 1080×1920 (`projects/recording-library/tools/package.py`)
treść wolno kłaść tylko w polu ok. **x 44–948, y 230–1660**:

- **górne ~230 px** — nazwa konta, przycisk „obserwuj”, pasek postępu,
- **prawa kolumna ~130 px** od ok. y 1100 — serce, komentarz, udostępnij (panel kart ma `right:132px`),
- **dolne ~260 px** — opis, dźwięk, CTA reklamy Meta.

Druga reguła wyszła z `hyperframes check` (content_overlap): **wszystko, co stoi u góry
kadru — znak marki, chip CTA, podpis przebitki, znak AI — wchodzi dopiero PO hooku**. Hook
siedzi w y≈250 przez pierwsze 3–5 s i każda z tych warstw na niego nachodziła.

**Why:** zasłonięty znak AI to nieważne oznaczenie ([[oznaczanie-tresci-ai]]), zasłonięte
CTA to zmarnowany lead — a w podglądzie na komputerze nic tego nie zdradza.

**How to apply:** nowy element w pionie → sprawdź y względem trzech stref i czas względem
`hook_end`. Kontrola: `hyperframes check` (layout) + klatka kontrolna po hooku.
Powiązane: [[copy-i-hook]], [[nigdy-nie-rozciagaj-kadru]].
