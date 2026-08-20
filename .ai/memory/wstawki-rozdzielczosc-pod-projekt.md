---
name: wstawki-rozdzielczosc-pod-projekt
description: Wstawkę renderuj w rozdzielczości projektu montażowego — 1920x1080 wrzucone na płótno 720p pokazuje środkowe 66 % i wygląda jak zepsuty render
metadata:
  type: reference
---

**Renderuj wstawkę w rozdzielczości płótna projektu montażowego, nie „na maksa".**

Nagrania Mateusza z sierpnia są w **1280×720** (checklista kazała ustawić w QuickTimie jakość
„Wysoka", a to jest 720p). Projekt w CapCucie przejmuje rozdzielczość materiału, więc wstawka
1920×1080 wrzucona w skali 100 % jest **dokładnie 1,5× szersza od płótna** i widać z niej
środkowe 66 %: panele ucięte przy obu krawędziach, napisy bez pierwszej i ostatniej litery.

Objaw myli, bo wygląda na zepsuty render, a jest zwykłą arytmetyką skali.

```bash
W=1280 H=720 FPS=30 ALPHA=1 node render.js <scena>   # → *_alpha_720p.mov
```

Sceny są projektowane na 1920×1080; renderer skaluje całość przez `deviceScaleFactor`, więc
**układ zostaje ten sam**, zmienia się tylko liczba pikseli. Plik chudnie przy okazji o połowę.

**FPS też dopasuj do materiału** — nagrania są w 30 kl./s, więc wstawka w 60 nie doda płynności
na tej osi, a waży dwa razy tyle.

**Pułapka CapCuta:** po podmianie pliku o tej samej nazwie edytor korzysta z zaimportowanej
kopii z cache'u i nie widzi nowej wersji. Trzeba usunąć klip z biblioteki mediów i wczytać
ponownie — inaczej oceniasz poprawkę, której tam nie ma.

Powiązane: [[wstawki-alfa-nie-green-screen]], [[quicktime_wysoka_to_720p]]
