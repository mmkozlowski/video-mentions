---
name: muzyka-ciagla-w-sklejce
description: Sklejka gotowych plików z osobno zmiksowaną muzyką urywa podkład na każdym łączeniu; skleja się surowe rendery (sam głos), muzykę kładzie się raz na całość
metadata:
  type: feedback
---

Short z dogrywkami (hak + treść + zakończenie + plansza) sklejany z GOTOWYCH plików ma na każdym łączeniu dziurę
w muzyce — każdy kawałek ma własny podkład z wejściem i wyciszeniem. MK 21.11: „w 0:54 ucinasz muzykę i później
znowu wraca — ona musi być cały czas jak podkład”, „nie musisz jej wycinać na to, jak mówię”.

**How to apply:** sklejaj `build/packaging/<klip>/<format>-F/render.mp4` (sam głos), wyrównaj mowę kawałków do
jednego poziomu (−18 LUFS, filtr głosu dogrywek osobno), a podkład i efekty (`sfx.json` przesunięte o miejsce kawałka)
kładzie raz `package.finalize` — `tools/assemble_short.py`. Odcinki YouTube sklejane z gotowych plików mają ten sam
efekt na wstawkach — tam jest akceptowany (wstawka = inna plansza, inna muzyka), ale przy zmianie muzyki trzeba pamiętać.
