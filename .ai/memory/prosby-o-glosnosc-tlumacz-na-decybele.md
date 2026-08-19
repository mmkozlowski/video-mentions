---
name: prosby-o-glosnosc-tlumacz-na-decybele
description: „Podgłośnij o kilka procent" to kierunek, nie mnożnik — dosłowne 2 % jest poniżej progu słyszalności; przeliczaj na dB i raportuj w dB
metadata:
  type: feedback
---

Przy strojeniu podkładu padły dwie prośby w procentach i **żadnej nie wolno wziąć
dosłownie**:

- „możesz o kilka procent podgłośnić" → zrobione +2,4 dB (0,16 → 0,21, czyli
  +31 % liniowo). Zaakceptowane.
- „jednak trzeba ściszyć o 2 %" → dosłowne 2 % to **−0,18 dB**. Zrobione −1,0 dB
  (0,21 → 0,187, czyli −11 % liniowo). Zaakceptowane.

**Próg słyszalności różnicy głośności dla szerokiego pasma to ok. 1 dB.**
Wykonanie dosłownych 2 % byłoby zmianą, której autor fizycznie nie usłyszy —
czyli renderem do kosza i pytaniem „dalej za głośno?" w następnej turze.

**Why:** procent i decybel to nie ta sama skala, a rozmowa o dźwięku toczy się
w procentach, bo tak wygląda suwak w każdym edytorze. Wykonanie prośby
literalnie jest tu formą nieposłuszeństwa — daje wynik, którego nikt nie chciał.

**How to apply:** traktuj procenty jako **kierunek i wielkość kroku**, nie jako
mnożnik. Najmniejszy sensowny krok to 1 dB; „kilka procent" ≈ 2–3 dB; „wyraźnie"
≈ 4–6 dB. **Zawsze raportuj zmianę w dB obok liczby z konfiguracji** i podaj
następny krok, gdyby był potrzebny — wtedy kolejna prośba przychodzi już
w kalibrowanych jednostkach. Aktualne poziomy i historia dojścia do nich:
komentarz przy `MUS_VOL` w `projects/shorts IG/tools/music.py`. Powiązane:
[[audio-lektor-muzyka]].
