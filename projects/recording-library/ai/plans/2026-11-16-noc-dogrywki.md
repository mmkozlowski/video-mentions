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
- [x] Mastery 1440p w tailnecie: `pliki/odcinki-2026-11-17/` (oferty 19.11, meble 26.11, pamiątki 03.12, 8 wdrożeń 10.12 + rozdziały)
- [x] Shorty i rolki (8): hak G + zakończenie H z dogrywek, `tools/assemble_short.py` → `…--with-dubs.mp4`, `pliki/rolki-2026-11-17/`
  - zajawki mebli i paszy przepięte na warianty `--8w` (kontekst na starcie, domknięte „na to.”) — uwagi ze Studia 29.10 i 15.11
  - kwestia 26 nieużyta (liczba nie ma pokrycia w treści); w pionie przy samym głosie ukryty dolny panel (prześwitywała linia)

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

## Poprawki po odsłuchu masterów (17.11)

Lista MK: `POPRAWKI-2026-11-17.md` (tailnet `odcinki-2026-11-17/`), czasy w gotowym masterze → źródło przez
`plan_segments` + `locate`. Każda granica z ciszy w sygnale i sprawdzona Whisperem sklejki (nie samego wycinka).

- **Anonimowość (decyzja MK 17.11, „Do decyzji MK” wchodzi):** meble bez „z Podsłupska” (81,98 / 83,04), pamiątki bez
  „w Kołobrzegu” (2778,52 / 2780,95 → „Firma produkująca pamiątki przyszła do mnie”), b-roll z latarnią (h08) zamieniony
  na h01 we wstępie i na h16 przy „samochód”. Zostaje: „z Podsłupska” w reklamach ad-15/ad-16 (sesja 1049/1103) i
  w nieużywanym `ch-doram-2-kilka-dni-10-minut`.
- **„Dlaczego?” w meblach (pkt 14):** sygnał pokazuje oba podejścia później niż Whisper (pierwsze ~92,96–93,38, drugie od
  97,42) — koniec 92,42 (po „wykonywały.”), start 97,30.
- **Składanka 8 wdrożeń:** bez falstartu kierownika, bez „kilkunastu kliknięć” (też zajawka mebli), case 10 od „Klient
  przestaje zamawiać”.
- **Shorty:** hak 28 („Dlatego/Do tego”) → 30; zajawka 8 wdrożeń = same kody do „15 minut pracy” (bez śrubek i CTA
  sprzedażowego); rolka o kodach i zajawka od „generowanie samych kodów kreskowych”; zajawka pamiątek z hakiem z odcinka
  („I nagle produkujemy tego dziesiątki tysięcy sztuk…”), bez „Ta branża też”; rolka „komu odradzam” bez „Nie masz
  ograniczeń na użytkowników”. Rolki IG o kodach i „komu odradzam”: plansza końcowa „Zapisz, przyda się / Podeślij
  komuś” zamiast konsultacji.
- **Pierwsza klatka shorta (miniatura IG):** plansze haka wjeżdżają z pustego tła — `assemble_short` kładzie przez
  0,3 s klatkę z pełnym tekstem (0,9 s haka), potem animacja.
- **Oferty:** kwestia 30 na planszy przed A4 (domknięcie), „KILKANAŚCIE GODZIN”, bez „oferty często,”.

## Uwagi Agaty ze Studia (17.11, 11:48–12:08)

Każda granica z ciszy w sygnale i sprawdzona Whisperem sklejki (large-v3 i turbo).

- **Kody (zaj-8, rolka 22.11):** „no to [tutaj to] nie było tutaj” → wycięte 610,49–610,82.
- **ad-28-w1 (+ --ai-slupsk):** falstart „War-” (1982,55–1983,17) przed „Warsztaty są w Słupsku”; koniec w ciszy po
  „ai.slupsk.pl” (1990,45) — wcześniej wchodziło „i-” z kolejnego zdania. Muzyka pod planszą końcową schodzi przez 1 s.
- **Zajawka mebli:** osobny klip `ch-doram-5-70-94--zajawka` (wariant `--8w` zostaje w składance). Po „zamówienia
  w Excelu” zdanie z odcinka o kilkunastu nazwach tego samego produktu (po niemiecku / po angielsku); wątek „miernik /
  wyliczaliśmy” wycięty → „…nazwany w różnych momentach. Z początku … 70%”. Plansza „pięć nazw” → „kilkanaście nazw”
  (tak mówi nagranie).
- **Kartka:** start od drugiego „Zanim” (66,90). **ERP lat 90.:** start od „A drugą stroną były systemy” (469,06).
- **ad-12-r2 (+ --ai-w-produkcji):** zająknięcie to falstart „jest w zzz…” (802,58–803,78) przed powtórzonym „jest
  w zeszytach” — między „Wiedza” a „o” w źródle jest tylko 0,6 s pauzy, nie zająknięcie.
- **Napisy na cięciach:** EDL `caption_words` (cut.py) — w przedziale źródła słowa z czasami zmierzonymi na sygnale.
  Reguła luki w `words_in` wciągała wycięte „tutaj to” z powrotem do napisów, a „Zanim”/„A” wypadały.
- **Studio pokazuje shorty z dogrywkami:** `export_studio.py` bierze `…--with-dubs.mp4`, gdy istnieje (pytanie 7).

## Pytania na rano (MK)

1. **Kwestie do odsłuchu:** 22 („w filmie / w firmie”), 36 („w polskiej filmie”), 41 („nazwy film nie podaję”) — modele się
   nie zgadzają albo słyszą „film”. Nie są użyte w odcinkach.
2. ~~**Kołobrzeg w nagraniu pamiątek**~~ — rozstrzygnięte 17.11: wycięte (sekcja wyżej). (0:03 odcinka, „Firma produkująca pamiątki w Kołobrzegu przyszła do mnie…”): wariant
   wycięty / wyciszony / bez zmian — podglądy w tailnecie `pamiatki-kolobrzeg-warianty/`.
3. ~~**Tytuł „8 wdrożeń”**~~ — zamknięte 17.11, decyzja MK: tytuł zostaje „8 wdrożeń” z Open Mercato („bo to się klika”), Open Mercato zostaje w tytule, na planszach i w opisie; podpis pod „8” („w tym odcinku: 7 historii z 4 firm”) zostaje. Było: — odcinek pokazuje 7 historii z 4 firm. Propozycja: „7 wdrożeń w 4 firmach: co realnie dało AI”
   albo zostawić (wstęp mówi prawdę: „zrobiłem już 8 wdrożeń… powiem pokrótce”).
4. **Łącznik 10 mówi „hurtownia pamiątek”**, klient to producent (plansza mówi „producent”). Zostawić?
5. **Ekran końcowy:** okno ~15 s (39 + 24 + plansza końcowa), nie 20 — po „do zobaczenia” w nagraniu nie ma ciszy.
6. **Studio:** `zaj-8-wdrozen` ma `publishAt` 19.11, a odcinek przeszedł na 10.12 — przestawić?
7. ~~**Shorty w Studiu**~~ — zamknięte 17.11: Studio pokazuje `--with-dubs` (`export_studio.py`). Było: nowe wersje to `…--with-dubs.mp4` — `export_studio.py` ich nie podmienia (dla odcinków podmienia
   `--with-inserts`). Podmienić w Studiu?
8. **Gałąź `mmkozlowski/poprawki-studia-02-11`** (9 commitów z 02.11) nie jest w main ani w tej gałęzi — scalić?

## Dziennik

- 22:35 Drive: pliki w „Mój dysk” od 22:34 (API je widzi), lokalny mount ich nie ma. Log DriveFS:
  `change_ids_up_to_date: false`, kolejka 12 124 operacji. Próba zamknięcia aplikacji utknęła
  („Quit initiated”), nie zabijam procesu siłą (ryzyko utraty wysyłanych plików). Ekran zablokowany.
