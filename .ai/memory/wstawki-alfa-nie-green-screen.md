---
name: wstawki-alfa-nie-green-screen
description: Wstawki na gadaną głowę renderuj z kanałem alfa, nie na zielonym — key zawsze zostawia zielony rant na antyaliasowanych krawędziach liter; kodek qtrle zamiast ProRes 4444
metadata:
  type: reference
---

**Wstawki wchodzące na materiał renderuj z prawdziwym kanałem alfa.** Green screen zostaw
wyłącznie dla narzędzi, które alfy nie przyjmują.

Powód jest fizyczny, nie narzędziowy: krawędź litery jest antyaliasowana, więc piksel brzegowy
to **mieszanka koloru tekstu i tła**. Na zielonym biała litera ma obwódkę pikseli biało-zielonych.
Key usuwa czystą zieleń, a mieszane piksele zostają — **zielony rant wokół każdej litery**.
Podniesienie progu keya nie pomaga: zaczyna zjadać sam tekst. Przy alfie nie ma czego wycinać.

**Kodek: `qtrle` (QuickTime Animation), nie ProRes 4444.** Bezstratny, z alfą, natywny na macOS
(QuickTime, Final Cut, CapCut). Na płaskiej grafice pakuje ~9× lepiej przy identycznym obrazie —
karta tytułowa 4,4 s: 106 MB w ProRes wobec 8,1 MB w qtrle. Sceny, w których prawie każdy piksel
zmienia się co klatkę (wpisywany kod), zyskują mniej — RLE nie ma na czym oszczędzić.

```bash
ALPHA=1 node render.js <scena>                     # qtrle + alfa → *_alpha.mov
ALPHA_CODEC=prores ALPHA=1 node render.js <scena>  # gdy narzędzie nie czyta qtrle
```

**Pułapka pochodna: podkładki chromakeya trzeba w trybie alfa wyłączyć.** Istnieją po to, żeby
ciemny tekst przetrwał wycinanie zieleni. Przy alfie robią z siebie **czarne prostokąty na twarzy**.
Renderer zdejmuje je sam (`background:transparent; box-shadow:none`), ale nie nadawaj ich tekstowi
jasnemu ani bursztynowemu w ogóle — ten i tak jest widoczny po keyu.

**Why:** karta tytułowa e01 poszła do CapCuta na zielonym i miała zielony rant na wszystkich
literach plus dwa czarne prostokąty pod napisami. Wyglądało to jak błąd montażu, a było
konsekwencją samego formatu dostarczenia.

**How to apply:** sprawdzaj wstawkę **kompozytem na prawdziwej klatce z nagrania**, nie na
podglądzie sceny — rant widać dopiero na materiale:

```bash
ffmpeg -i tlo.png -i wstawka_alpha.mov \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto" -frames:v 1 test.jpg
```

Powiązane: [[ekran-produktu-hyperframes]], [[montaz-pulapki-synchronizacji]]
