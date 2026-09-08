---
name: ffmpeg-atempo-w-jednym-grafie
description: ffmpeg 8.1 — atempo w jednym filter_complex z setpts na wideo po cichu nie działa (audio wraca do osi wideo); zmiany tempa rób dwoma przebiegami i muksuj
metadata:
  type: reference
---

Przy przyspieszaniu gotowego montażu o 1% (shorty studyjne, 2026-08-25):

```
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=PTS/1.01[v];[0:a]atempo=1.01[a]" \
  -map "[v]" -map "[a]" …
```

**wideo wychodzi przyspieszone, audio NIE** — bez żadnego błędu ani ostrzeżenia.
Zmierzone na ffmpeg 8.1 (Homebrew) przy ×1.5 dla czytelności: wideo 35 s,
audio 51,8 s (≈ wejściowe). Ten sam `atempo` uruchomiony osobno (`-vn -af`)
albo obok `-c:v copy` działa poprawnie — psuje się tylko kombinacja obu gałęzi
w jednym `filter_complex`, wygląda jakby muxer rozciągał audio z powrotem do
osi wideo.

**How to apply:** zmianę tempa całości rób DWOMA przebiegami — wideo
(`-vf setpts=PTS/x -an`), audio (`-vn -af atempo=x`), porównaj długości,
zmuksuj `-c:v copy`. Wzorzec: `speed_up()` w
`projects/youtube/shorts/s10-po-co-om/tools/assemble.py`. To ta sama rodzina
pułapek co [[montaz-pulapki-synchronizacji]] — niewidoczna w logach, trzeba
mierzyć długości strumieni.
