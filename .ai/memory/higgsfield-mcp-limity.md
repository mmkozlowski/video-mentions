---
name: higgsfield-mcp-limity
description: Higgsfield przez MCP ignoruje trial unlimited (liczą się tylko kredyty); veo3_1_lite wymusza 8s przy start+end frame
metadata:
  type: reference
---

Przy generowaniu reklam wideo przez Higgsfield MCP obowiązują trzy twarde ograniczenia, których nie widać w panelu webowym:

1. **Trial „unlimited" nie działa przez MCP.** Panel może pokazywać „22 modele unlimited, Active", a `models_explore` może zwracać `supports_unlim: true` — mimo to `use_unlim: true` zwraca `Unlimited generations aren't supported for <model>`. `balance` konsekwentnie daje `unlim: { available: false }`. Przez MCP liczą się **wyłącznie kredyty**. Odrzucone żądanie unlim jest darmowe (MCP nigdy nie obciąża po cichu), więc można próbować bez ryzyka.

2. **`veo3_1_lite` wymusza `duration: 8`, gdy podasz `start_image` i `end_image`** (`Value error, duration must be 8`). Nie da się zrobić dwóch tanich ujęć po 4 s z morfem — jedno ujęcie 8 s kosztuje 8 kr.

3. **`seed_audio` przyjmuje `speech_rate` tylko jako int** — `0.95` wywala 422.

4. **`seed_audio` (domyślny TTS) nie mówi po polsku** — czyta polski tekst fonetycznie po angielsku. Do lektora PL używaj `text2speech_v2` + `variant: "elevenlabs"` (multilingual, 0,3 kr zamiast 0,2). Skróty pisz fonetycznie (`3D` → `trzy de`). Część głosów presetowych zwraca `403 free_trial_model_requires_plan` — wymagają planu wyższego niż Plus.

5. **`seedance_2_0` też nie mówi poprawnie po polsku.** Mowa renderowana natywnie w klipie (talking head) brzmi jak polski, ale słowa są przekręcone — Whisper wykrywa `Polish`, a transkrypcja pokazuje bełkot („wzięłam zwykłe zdjęcia" → „wijałam z jukne znajdanie"). Do publikacji: nagraj kwestię **po angielsku**, potem `dubbing` z `target_language: "pol"` (tłumaczy, syntezuje i ponownie synchronizuje usta).

5a. **Kwestie do dubbingu pisz w czasie TERAŹNIEJSZYM lub trybie rozkazującym.** Angielski czas przeszły jest bezrodzajowy („I took"), polski nie — tłumacz musi wybrać rodzaj i wybiera **męski**. Przy kobiecie na ekranie („wziąłem" zamiast „wzięłam") to dyskwalifikuje materiał. Bezpieczne formy: „biorę / przeciągam / mam / wrzucasz / zobacz / skończ" — nie mają rodzaju.

6. **Weryfikuj mowę Whisperem, nie na oko.** W systemie jest `whisper` (homebrew): `ffmpeg -i klip.mp4 -vn -ar 16000 -ac 1 /tmp/a.wav && whisper /tmp/a.wav --model base --output_format txt --fp16 False`. Klatki nie powiedzą, czy model mówi to, co miał.

Dodatkowo `generate_video` przy pierwszym wywołaniu podpowiada preset zamiast generować; trzeba powtórzyć z `declined_preset_id`.

**Why:** te trzy rzeczy wychodzą dopiero po nieudanym wywołaniu, a przy 10 kredytach na koncie każda pomyłka w planowaniu budżetu kosztuje cały test.

**How to apply:** zawsze rób preflight `get_cost: true` przed generacją wideo i planuj budżet na kredytach, nie na trialu. Do przejść „obraz A → obraz B" wybieraj model z rolą `end_image` (`veo3_1_lite` 8 kr/8 s, `seedance_2_0` 17,5 kr/5 s + 4K) — bez `end_image` model halucynuje własny kadr końcowy zamiast trafić w naszą grafikę. Szczegóły i zmierzony cennik: `projects/adresflow/ai/decisions/2026-07-30-reklamy-higgsfield-rzut-3d.md`.

**Bliźniacze notatki w projekcie Granit** (`~/Repo/granit/.ai/memory/`), gdzie też powstają reklamy przez Higgsfield: `higgsfield-audio-mozliwosci` (m.in. `tiktok_music_trending` jako jedyna licencjonowana muzyka — bez pliku do montażu), `higgsfield-wideo-koszty-limity`, `reklamy-hook-lektor-lekcje`. Przy zmianie ustaleń warto zaktualizować oba miejsca.
