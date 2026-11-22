---
name: ffmpeg-wspolne-wejscie-zjada-ram
description: Wiele trim z jednego wejścia ffmpeg + concat w innej kolejności niż w pliku = bufor surowych klatek w RAM (35 GB, restart Maca); każdy kawałek jako osobne wejście -ss/-to, składanki po jednej
metadata:
  type: feedback
---

22.11.2026 przy składaniu odcinków (`tools/assemble_episode.py`) Mac Mateusza dwa razy stanął i sam się zrestartował.
W logach systemu była panika jądra („watchdog timeout: no checkins from watchdogd in 93 seconds”) i JetsamEvent,
w którym jeden ffmpeg zajmował **35 GB z 48 GB RAM**.

**Why:** w grafie było kilkanaście `[0:v]trim=a:b` z jednego wejścia (renderu), sklejanych przez `concat`. Fragmenty
„W tym odcinku” pochodzą z końca odcinka, a idą na początek filmu. ffmpeg musiał więc zdekodować prawie cały odcinek
i trzymać w pamięci surowe klatki dla gałęzi, które przyjdą później. Jedna składanka mieściła się w RAM, sześć naraz już nie.
Sam CPU spowalnia komputer, ale go nie zawiesza. Zawiesza go pamięć.

**How to apply:**
- Każdy kawałek pliku to osobne wejście `-ss a -to b -i plik` (w `assemble_episode.py` jest to `source_slice`). Nigdy wiele `trim` z jednego wejścia, gdy kolejność w filmie ≠ kolejności w pliku. Po zmianie: 2,2 GB zamiast ~35 GB, wynik identyczny.
- Długie rendery (składanki, `package.py --render`) puszczaj **po jednym**, w tle: `nice -n 15 taskpolicy -c utility`. Mateusz pracuje na tym samym komputerze.
- Przy nowym grafie zmierz pamięć: `/usr/bin/time -l` → „maximum resident set size”.
- Zawieszenie albo restart → `/Library/Logs/DiagnosticReports/` (JetsamEvent-*.ips, .contents.panic) mówi, kto zjadł pamięć.
