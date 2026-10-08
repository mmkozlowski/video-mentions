---
name: veo-gemini-api
description: Jak generować wstawki filmowe przez Veo 3.1 w Gemini API — parametry, które przechodzą, i te które nie
metadata:
  type: reference
---

Wstawki filmowe do YouTube generujemy przez **Veo 3.1 w Gemini API**, nie przez Higgsfielda
(ten miał 15 kredytów, a jedna generacja kosztuje 8–25). Narzędzie:
`projects/youtube/Animation flowbiz youtube/tools-veo-generate.mjs`.

Trzy rzeczy wyszły dopiero na żywym API:

1. **`personGeneration: "allow_adult"` zwraca 400** — „currently not supported". Parametr
   trzeba pominąć zupełnie; ujęcia z ludźmi i tak wychodzą.
2. **Domyślna rozdzielczość to 720p.** `resolution: "1080p"` trzeba podać jawnie, inaczej
   dostajesz materiał, który na osi 1080p trzeba skalować w górę.
3. **Nazwy modeli zmieniają się między wydaniami.** Skrypt woła `GET /v1beta/models` i wybiera
   wariant `fast` z widocznych `veo-*`, zamiast wpisywać nazwę na sztywno — inaczej płacisz
   za joba, który zwróci 404.

Endpoint jest długodziałający: `:predictLongRunning`, potem polling `GET /v1beta/{operation}`
co ~12 s. Ujęcie 8 s schodzi w 1–3 minuty.

Klucz leży w `~/Repo/GEMINI_API` (poza jakimkolwiek repozytorium — `~/Repo` nie jest gitem,
więc nie ma ryzyka commita).

Wynikowe MP4 **commitujemy** mimo rozmiaru: są płatne i generatywne, więc drugi raz nie wyjdą
identycznie. To zgodne z tym, co repo już robi (38 plików wideo w historii).

**Etap „najpierw kadr” (2026-10-09, `projects/recording-library/tools/broll_gen.py`):**
ten sam klucz widzi `gemini-3-pro-image` (Nano Banana Pro) — kadr 2752×1536 za ~0,13 USD,
a Veo 3.1 przyjmuje go jako `instances[].image` (image-to-video). Cztery rzeczy:

4. **Plik klucza to `GEMINI_API=AIza…`, nie `GEMINI_API_KEY`.** `source` go nie wystawi pod
   nazwą, której szuka skrypt — parsuj wartość po `=`, nigdy jej nie wypisując.
5. **Model obrazów zwraca JPEG**, nawet gdy prosisz o PNG — rozszerzenie bierz z `mimeType`,
   inaczej ffmpeg wywraca się na „Invalid PNG signature”, a Veo dostaje zły `mimeType`.
6. **„Jeden kadr” bywa tryptykiem.** Na hasła typu „full-bleed 16:9” model oddał dwa razy
   kolaż z ramkami. Pomaga wprost: „a single photograph, one frame, no panels, no collage”.
   Kadry ocenia się arkuszem (`ffmpeg … tile=4x3`) PRZED ożywieniem.
7. **Image-to-video trwa 4–5 min na ujęcie** (tekst-do-wideo 1–3 min) — puszczaj partią w tle.

Powiązane: [[oznaczanie-tresci-ai]] (te ujęcia wymagają znaku AI), [[higgsfield-mcp-limity]].
