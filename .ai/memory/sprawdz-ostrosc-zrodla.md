---
name: sprawdz-ostrosc-zrodla
description: Surowe nagrania z kanału potrafią mieć rozmyty obraz przez kilka minut (twarde cięcie, nie utrata ostrości) — przed wyborem dubli zmierz ostrość całego pliku
metadata:
  type: feedback
---

11.10.2026, starsze odcinki: dwa z siedmiu plików miały długie rozmyte odcinki —
S11 `openmercato-08-gdycloud…` 7:18,8–13:38,9, `budowanie - modulu.mov` od 8:00 do
końca. Przejście jest twarde (z klatki na klatkę), więc to rozmycie z eksportu,
nie kamera. Dźwięk w tych miejscach jest dobry, dlatego transkrypcja niczego nie zdradza.

Pomiar w 10 s: `ffmpeg -i plik -vf "fps=1/5,scale=160:-1,edgedetect,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-" -f null -`
— ostry kadr ma YAVG ≈ 15–23, rozmyty ≈ 0,7–6.

**Why:** wybór dubli idzie po transkrypcji; bez pomiaru rolka z rozmytą twarzą wyszłaby
dopiero na renderze, po godzinie pracy.

**How to apply:** przy każdym nowym źródle pomiar ostrości obok `ffprobe`, zanim
powstanie EDL. Rozmyty fragment: szukaj innej wersji nagrania (często jest dogrywka
albo czysta wersja obok w `~/Youtube Projects/`), a w ostateczności dźwięk pod
pełnoekranową grafiką. Powiązane: [[whisper-gubi-falstarty]], [[iphone-hdr-psuje-render]].
