---
name: oznaczanie-tresci-ai
description: Od 2026-08-02 spoty z materiałem AI muszą być oznaczone (art. 50 ust. 4 AI Act) — materiał z Higgsfielda nie ma C2PA, więc platformy nie zrobią tego za nas
metadata:
  type: reference
---

Od **2 sierpnia 2026** obowiązuje art. 50 ust. 4 AI Act: kto stosuje system AI
generujący obraz/dźwięk/wideo wyglądające na autentyczne, **musi ujawnić, że
treść jest sztuczna**. Digital Omnibus tego nie przesunął — odroczono tylko
high-risk i maszynowy watermarking z ust. 2 (do 2 grudnia 2026). Kara: do
15 mln EUR albo 3 % obrotu.

**Podział obowiązków:** art. 50 ust. 2 (znakowanie maszynowe) leży po stronie
**dostawcy modelu** — Higgsfield, ElevenLabs. Art. 50 ust. 4 (ujawnienie
odbiorcy) leży po **naszej**. Nie mieszaj tych dwóch.

**Materiał z Higgsfielda przychodzi BEZ metadanych C2PA** — sprawdzone
`ffprobe` na surowym pliku, są tylko `major_brand` i `encoder`. Skutek:
**platformy nie oznaczą spotu automatycznie**, bo nie mają czego wykryć.
Przełącznik „AI-generated content" na TikToku / „AI info" na Meta / „zmienione
lub syntetyczne treści" na YouTube trzeba włączyć **ręcznie przy każdej
publikacji**. Przekodowanie w ffmpeg i tak zdejmuje metadane, więc nawet gdyby
dostawca je wstawił, nie przetrwałyby montażu.

**Trzy warstwy, które stosujemy:** przełącznik na platformie (ręcznie) + znak
w kadrze przez pierwsze ~4 s + metadane pliku i rejestr `final/OZNACZENIA-AI.md`
(generowany z `AI_MAP` w `finalize.py`).

**Znak idzie u GÓRY kadru, nie na dole** — dolne ~15 % zasłania w Reels
i TikToku interfejs aplikacji. Oznaczenie, którego nie widać, nie jest
oznaczeniem. I **tylko na starcie**, bo przepis mówi „najpóźniej przy pierwszej
ekspozycji", a znak przez 30 s zaśmieca kadr. Plansza *przed* spotem odpada —
zmierzone okno 0–3 s decyduje o `hook_score` ([[copy-i-hook]]).

**Oznaczenie AI nie zastępuje oznaczenia „reklama" / „materiał sponsorowany".**
To dwa różne obowiązki.

**Nie oznaczaj wszystkiego jak leci** — ekrany produktu pisane w HTML,
typografia, napisy, montaż i muzyka nie są treścią AI. Rozmycie granicy osłabia
przekaz i utrudnia obronę rejestru.

**Why:** łatwo założyć, że „platforma sama wykryje AI" albo że skoro model ma
obowiązek znakowania, to sprawa jest załatwiona. Oba założenia są fałszywe przy
naszym pipelinie i oba kosztowałyby karę, a nie ostrzeżenie.

**How to apply:** nowy spot → dopisz go do `AI_MAP` w `tools/finalize.py`
(bez wpisu rejestr oznaczy go jako brakujący) i **pamiętaj o przełączniku przy
publikacji**. Decyzja i szczegóły: `.ai/decisions/2026-08-02-oznaczanie-tresci-ai.md`.
Format POV ma znak w kompozycji HTML, nie w warstwie brandingowej:
[[format-pov-nagrane-telefonem]].
