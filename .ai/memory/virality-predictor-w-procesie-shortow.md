---
name: virality-predictor-w-procesie-shortow
description: Higgsfield virality_predictor jest DARMOWY na planie plus — stały krok QC hooków shortów; co realnie rusza wynik, a czego model nie widzi
metadata:
  type: project
---

Zmierzone na shortach S-10 „Po co Open Mercato" (2026-08-26), plan `plus`,
stan kredytów przed i po serii 6 analiz: **14,81 → 14,81** — predyktor nie
zjada kredytów, można nim iterować bez limitu budżetu.

**Jak włączyć w proces** (krok po `music.py`, przed publikacją):
1. Utnij pierwsze ~15,8 s gotowego shorta (model przyjmuje max 16 s).
2. `media_upload` → curl PUT → `media_confirm` → `virality_predictor` create
   (max 2 zadania równolegle, job ~30–60 s).
3. Czytaj: `hook_score` (okno 0–3 s), `sustain`, `viral_potential` oraz
   krzywą `visual_occipital` po sekundach — ona mówi, GDZIE uwaga siada.

**Benchmarki** (do porównywania kolejnych shortów):
- AdresFlow (reklamy z lektorem): hook 26–42.
- S-10 (studyjna gadana głowa, cold-open z pytaniem): hook 30–36,
  sustain 93–100, viral 52–58. Narracja kupuje sustain kosztem hooka —
  zgodnie z [[copy-i-hook]].

**Co widać w krzywych:**
- Kora wzrokowa **skacze na pełnoekranowych planszach/animacjach i
  przebitkach** (s2: 0,25 → 0,64 dokładnie na wjeździe pionowej planszy;
  s3: wzrost przez cały baked b-roll) i **siada na czystej gadanej głowie**
  po ~3 s (dołki 0,25–0,35).
- **Czego model nie widzi:** subtelny ruch w 1,35-sekundowym intro (push-in
  + tekst slide/fade) nie zmienił hooka ani o punkt (s1: 35→35, s2: 30→30) —
  model próbkuje ~1 klatkę/s. Żeby ruszyć hook_score, zmiana w oknie 0–3 s
  musi być WIDOCZNA na pojedynczej klatce (inna kompozycja/plansza/kolor),
  nie mikro-ruchem. Mikro-ruch i tak zostaje — służy ludziom, nie modelowi.

**How to apply:** traktuj wynik jak regresję, nie wyrok: porównuj wersje
tego samego shorta i shorty między sobą; pojedyncza liczba bez porównania
nic nie mówi. Duże zmiany w 0–3 s konsultuj z autorem — pełnoekranowa
plansza w hooku bije gadaną głowę w modelu, ale kłóci się z „kadr, nie
plansza" ([[autentycznosc-bije-gladkosc]] — reżim telefoniczny) i z
estetyką studyjną ([[shorty-studyjne-vs-reelsy-ig]]). Powiązane:
[[higgsfield-mcp-limity]].
