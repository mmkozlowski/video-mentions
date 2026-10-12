---
name: nagranie-z-promptera-nie-trzyma-sie-tekstu
description: Mateusz przy prompterze improwizuje (liczby, miasta, dodatkowe zdania) — dubel wybiera się z transkrypcji, scenariusz tylko identyfikuje nagranie
metadata:
  type: feedback
---

Sesja 8.10.2026, 36 nagrań z promptera: prawie żadne nie jest wierne tekstowi.
Mateusz dokłada zdania i CTA, poprawia liczby na nagraniu (3 h → 6 h
przepisywania — **poprawka jest celowa, zostaje wersja z 6 h**), zamienia
miasto (Ustka → „pomorskie i zachodniopomorskie, 40 minut”), czasem pomija
telefon, który był w scenariuszu.

**Why:** automatyczne dopasowanie do scenariusza dałoby złe granice i odrzuciło
dobre, improwizowane dodatki. Tekst scenariusza to **intencja**, nagranie to
**prawda** — tak jak w [[autentycznosc-bije-gladkosc]].

**How to apply:** scenariusz służy do rozpoznania, które to nagranie i czy
padło CTA. Wybór dubla i granic — z wypisu słów (`tools/words.py`
w `projects/recording-library`). Brakujące CTA uzupełnia się grafiką, nie
cięciem z innego dubla. Odchylenia, które zmieniają sens („to NIE jest
warunek”), wpisuj do `notes` klipu — nie poprawiaj ich po cichu.
