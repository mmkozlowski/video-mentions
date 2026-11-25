---
name: makiety-klikane-kit-hyperframes
description: Animowane makiety „same się klikają” (Excel przed / Open Mercato po) robimy na wspólnym kicie animations/doram/shared — trzy pułapki: flex zgniata kody kreskowe, pozycje z offsetLeft nie widzą transformu, check sypie fałszywymi overlapami
metadata:
  type: project
---

Klikane makiety do odcinka (kursor, klik, pisanie, Ctrl+C/V/P, przełączanie okien) są w
`projects/recording-library/animations/doram/`: sześć projektów HyperFrames i `shared/` (kit.js, kit.css, om.css/om.js
z powłoką Open Mercato wygenerowaną z `tools/om_screens.py`). Nowa makieta = nowy katalog `NN-slug/index.html`
na kicie, a render przez `render.sh` (kopiuje shared → assets, `--workers 2`, po kolei).

Pułapki, które kosztowały iterację (25.11):
1. **Kod kreskowy w wąskim pojemniku znika.** `<u>` w `.bars` (flex) bez `flex: none` kurczy się do zera, bo
   marginesy się nie kurczą. Szerokość kresek steruje 4. parametr `Kit.barcode(el, tekst, wys, unit)`.
2. **`Kit.box()` liczy z offsetLeft, więc nie widzi transformu.** Element przesunięty `x` (wstawiona kolumna) wymaga
   ręcznego doliczenia przesunięcia. Za to pozycje nie zależą od chwili osi, w której się je liczy.
3. **`Kit.sheet()` nie może nadpisywać `innerHTML` celu.** Gubiło `.selbox` i padał runtime `offsetParent of null`.
   Teraz dokleja tabelę.
4. **`hyperframes check` daje dziesiątki `content_overlap`/`text_occluded`** przy nachodzących oknach i stosie
   etykiet. To nie są błędy: weryfikacja idzie na klatkach (`snap.sh`), nie na tej bramce.
5. **Okienko z twarzą (PiP 0,27×) zajmuje x 1354–1872, y 740–1032** w 1920×1080. Makieta pod wklejenie
   z `slate(pip=True)` zostawia ten prostokąt pusty.
6. **Chip/podświetlenie nad oknem wyciągniętym `front()`** potrzebuje z-index wyższego niż okna (chip 40, ramki 30).

**Why:** MK chce w odcinkach „mockupów, które same się klikają” w miejscach o ręcznej pracy. Bez kitu każda
makieta zaczynała od tych samych błędów.

**How to apply:** czasy wejścia bierz z transkrypcji GOTOWEGO pliku (Whisper na finale), nie z surówki
([[ciecie-wstawek-po-renderze-nie-po-surowce]]). Wygląd systemu: [[ekrany-systemu-wyglad-open-mercato]].
Ekrany z HTML: [[ekran-produktu-hyperframes]]. Node 22: [[hyperframes-wymaga-node-22]].
ADR: `projects/recording-library/ai/decisions/2026-11-25-klikane-makiety-ep-doram.md`.
