# Klikane makiety do ep-doram — Excel „przed”, Open Mercato „po”

**Data:** 2026-11-25
**Status:** ✅ wyrenderowane i pokazane MK · ⏳ wklejenie do odcinka czeka na akceptację MK

## Problem

MK po obejrzeniu ep-doram (11:48): w miejscach, gdzie mówi o ręcznej pracy w Excelu (kilka plików od kontrahentów,
dopisywanie kolumn, przeklejanie, ręczne drukowanie kodów kreskowych ok. 4:15), ekran jest nudny. Boczne listy
punktów i statyczne plansze nie pokazują, jak ta praca wygląda. Chciał makiet, które „same się klikają”: przed
(Excel) i po (system).

## Decyzja

- **HTML → HyperFrames, nie nagranie ani generacja.** Prawdziwego Excela klienta nie wolno pokazać (anonimowość),
  model wideo robi z UI papkę ([2026-07-30-ekran-produktu-z-html](../../../../.ai/decisions/2026-07-30-ekran-produktu-z-html.md)).
- **Wspólny kit** `animations/doram/shared/kit.js`: kursor z ripple, `moveClick`, `type` (litera po literze, seek-safe
  przez proxy), klawisze Ctrl+C/V/F/P w lewym dolnym rogu, `front()` do przełączania okien, arkusz z literami
  kolumn i numerami wierszy oraz `colsheet` z kolumnami jako blokami (wstawianie kolumny = przesunięcie transformem).
- **„Po” w wyglądzie Open Mercato**: powłoka z `tools/om_screens.py` przeniesiona do `om.css`/`om.js` i powiększona ×1,3
  pod pełny kadr ([ekrany-systemu-wyglad-open-mercato](../../../../.ai/memory/ekrany-systemu-wyglad-open-mercato.md)).
- **Długość = fragment wypowiedzi**, z czasami z transkrypcji gotowego pliku 11:48. Akcje na ekranie trafiają
  w słowa („przeklejała, drukowała” ×3 to trzy pętle, „80%, 100%” to ramki w tych kolorach).
- **Forma wklejenia: pełny ekran + PiP z twarzą**, jak istniejące plansze. Każda makieta zostawia prawy dolny róg pusty.
- Dane fikcyjne (Patiolux / Greenyard / Sonnwerk, zmyślone kody i ceny).

Lista momentów i plan wklejenia: `animations/doram/README.md`.

## Pułapki

- Kody kreskowe w wąskich etykietach znikały (flex shrink do zera). Pomaga `flex: none` + parametr `unit`.
- `hyperframes check` przy nachodzących oknach daje fałszywe `content_overlap`. Weryfikacja na klatkach.
- Rendery muszą iść po kolei z `--workers 2`, bo na Macu był prawie pełny swap (MK 25.11).
- Pamięć: [makiety-klikane-kit-hyperframes](../../../../.ai/memory/makiety-klikane-kit-hyperframes.md).
