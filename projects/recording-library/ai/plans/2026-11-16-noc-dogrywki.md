# Noc 16→17.11: odcinki bez wstępu „8 wdrożeń”, dogrywki audio na planszach

**Data:** 2026-11-16
**Status:** w toku
**Zlecenie:** Mateusz przez sesję „Plan publikacji contentu”: „to nie jest o 8 wdrożeniach”. Odcinek
na czwartek 19.11 nie może zaczynać się od wstępu składanki. Materiał: dogrywki audio
(43 kwestie z vault `marketing/content/youtube/2026-11-15-do-dogrania.md`).

## Który odcinek idzie w czwartek

**Doprecyzowanie Mateusza (16.11, 22:55):** karty w pipeline mają przesunięte daty, tabela
w `_pipeline-plan.md` jest nieaktualna. Kolejność publikacji i pracy:

| Czwartek | Odcinek |
|---|---|
| 19.11 | **Oferta w 5 minut** (ep-open-mercato-offers) — dogrywki D/F/I, część C jeśli jest w nagraniu |
| 26.11 | meble / Excel (ep-doram) |
| 03.12 | pamiątki (ep-rezon) |
| 10.12 | 8 wdrożeń (ep-8-wdrozen) — łączniki case'ów 6–12 |

## Które odcinki zaczynały się od wstępu składanki

| Odcinek | Pierwsze zdanie przed zmianą | Po zmianie startuje od |
|---|---|---|
| ep-open-mercato-offers | „Cześć! Zrobiłem już 8 wdrożeń z Open Mercato… Pierwsza rzecz to jest” | „Tworzenie ofert. To jest jeden z najczęściej…” |
| ep-doram | „No dobra, lecimy z kolejnymi praktycznymi użyciami AI w firmach.” | „Teraz na warsztat możemy wziąć firmę…” |
| ep-rezon | „Ok, kolejny temat.” | „Firma produkująca pamiątki…” |
| ep-marpasz, ep-vacuactiv, ep-module | — czyste | bez zmian |
| ep-8-wdrozen | wstęp „8 wdrożeń” jest na miejscu (to jest ta składanka) | bez zmian; część „oferty” to teraz osobny klip `ch-offers-0-z-wstepem-8-wdrozen` |

Granice cięć z ciszy w sygnale (`fillers.levels`), każdy start sprawdzony Whisperem wycinka
i gotowego mastera. Czasy Whispera źródła są tu przesunięte o 0,6–1,5 s.

## Postęp

- [x] Kolejność publikacji i odcinki ze wstępem składanki
- [x] EDL: nowe starty ofert, mebli, pamiątek; storyboardy (rozdział „Cześć” i licznik „8” wycięte z ofert)
- [x] Kolizja: plansze z dawnego początku wjeżdżały pod pasek z imieniem (0,6–4,8 s) — przesunięte
- [x] Kołobrzeg: plansza, rozdział, b-roll (napis na magnesach), podpis na mapie — usunięte; audio = decyzja MK
- [x] Dogrywki: `tools/dubs_ingest.py` (sklejenie, −16 LUFS, transkrypcja), `tools/dubs_split.py` → `raw/…/kwestie/01–43.wav` + `mapa.csv`
- [x] Plansze dynamiczne: `mockups.kinetic` (słowa z rozmycia w rytm mowy, akcent + podkreślenie, push-in) + mieszanka typów
- [x] Wstawki z dogrywek: wstęp (13+14 / 14+15), łączniki A1–A4, case'y 6–12, kontakt (23), subskrypcja + ekran końcowy (37+39), pożegnanie (24)
- [x] Sklejki 4 odcinków + przegląd `tools/review_episode.py` (klatki + transkrypcja łączeń), 3 iteracje poprawek
- [ ] Mastery 1440p w tailnecie (oferty gotowe; meble, pamiątki, 8 wdrożeń w toku)
- [ ] Shorty i rolki (hak G + zakończenie H z dogrywek)

## Decyzje (16→17.11)

- **Kotwica tła „sam głos”:** `voice-backdrop` leżał nad całym oknem wideo (z-index 6) i zakrywał b-roll — teraz w oknie,
  nad twarzą, pod b-rollem (`package.py`).
- **Cięcie END nie może ucinać ostatniego słowa:** `assemble_episode` zatrzymuje się z błędem; oferty miały „…dobrze pó-” —
  koniec klipu w EDL przedłużony do 2768,65.
- **Składanka 8 wdrożeń** dostała własne warianty części (`*--8w`, `ch-offers-0-z-wstepem-8-wdrozen`) — rolki zostają na starych
  klipach. W wariantach poprawki studia z 02.11 (commit 941f34f na niescalonej gałęzi `mmkozlowski/poprawki-studia-02-11`):
  kontekst mebli i 4 worków paszy. Kotwice storyboardu przeliczone po słowach w obrębie części.
- **Zakończenia bez dubli:** meble i 8 wdrożeń mają własne CTA w nagraniu — meble dostają tylko kontakt (23) przed
  „więc dziękuję Wam”, 8 wdrożeń tylko subskrypcję + ekran końcowy. Oferty i pamiątki: A4 → zamknięcie → 37+39 → 24.
- **Prawda w tytule/początku:** oferty — kicker „Case study · oferty” (Open Mercato nie pada w odcinku), „5 MIN = szkic
  oferty zamiast kilkunastu godzin”; 8 wdrożeń — pod „8” podpis „w tym odcinku: 7 historii z 4 firm”.

## Pytania na rano (MK)

1. **Kwestie do odsłuchu:** 22 („w filmie / w firmie”), 36 („w polskiej filmie”), 41 („nazwy film nie podaję”) — modele się
   nie zgadzają albo słyszą „film”. Nie są użyte w odcinkach.
2. **Kołobrzeg w nagraniu pamiątek** (0:03 odcinka, „Firma produkująca pamiątki w Kołobrzegu przyszła do mnie…”): wariant
   wycięty / wyciszony / bez zmian — podglądy w tailnecie `pamiatki-kolobrzeg-warianty/`.
3. **Tytuł „8 wdrożeń”** — odcinek pokazuje 7 historii z 4 firm. Propozycja: „7 wdrożeń w 4 firmach: co realnie dało AI”
   albo zostawić (wstęp mówi prawdę: „zrobiłem już 8 wdrożeń… powiem pokrótce”).
4. **Łącznik 10 mówi „hurtownia pamiątek”**, klient to producent (plansza mówi „producent”). Zostawić?
5. **Ekran końcowy:** okno ~15 s (39 + 24 + plansza końcowa), nie 20 — po „do zobaczenia” w nagraniu nie ma ciszy.
6. **Studio:** `zaj-8-wdrozen` ma `publishAt` 19.11, a odcinek przeszedł na 10.12 — przestawić?
7. **Gałąź `mmkozlowski/poprawki-studia-02-11`** (9 commitów z 02.11) nie jest w main ani w tej gałęzi — scalić?

## Dziennik

- 22:35 Drive: pliki w „Mój dysk” od 22:34 (API je widzi), lokalny mount ich nie ma. Log DriveFS:
  `change_ids_up_to_date: false`, kolejka 12 124 operacji. Próba zamknięcia aplikacji utknęła
  („Quit initiated”), nie zabijam procesu siłą (ryzyko utraty wysyłanych plików). Ekran zablokowany.
