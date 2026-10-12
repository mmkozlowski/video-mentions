---
name: iphone-hdr-psuje-render
description: Nagranie z iPhone'a (HLG/bt2020) w kompozycji przełącza HyperFrames na render HDR całego klipu — konwertuj do SDR przez avconvert (brak zscale w ffmpeg)
metadata:
  type: reference
---

Telefon Mateusza nagrywa w HDR: `color_transfer=arib-std-b67`, `bt2020`. Gdy taki plik
trafi do kompozycji jako przebitka, `hyperframes@latest` przełącza CAŁY render na HDR:
rgb48le, libx265 `-preset slow -crf 15`, wynik HLG. Render jest kilka razy wolniejszy,
kolory na zwykłym telefonie wyprane, a `ffprobe` zwraca „33.7,” (przecinek wywracał float).

- Konwersja: `avconvert -p Preset1920x1080 -s in.MOV -o out.mov` daje H.264 bt709 z
  tonemappingiem. Lokalny ffmpeg (homebrew) nie ma `zscale`, więc `tonemap` w nim nie zadziała.
- Bezpiecznik: `package.reject_hdr()` w `stage()`. Przepis przebitek: `tools/real_broll.py`.

**Why:** zmiana trybu jest cicha. Widać ją dopiero po czasie renderu i kodeku (hevc zamiast h264).

**How to apply:** każde nowe nagranie z telefonu najpierw przez `real_broll.py`
(albo `avconvert`). Gdy render nagle zwalnia, sprawdź `color_transfer` mediów.
Powiązane: [[montaz-pulapki-synchronizacji]], [[shorty-z-telefonu-pulapki]].
