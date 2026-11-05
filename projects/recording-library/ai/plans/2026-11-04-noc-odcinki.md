# Noc 04→05.11: dopracowanie 7 odcinków YouTube

**Data:** 2026-11-04
**Status:** ✅ zrobione (05.11 ~02:00) — ADR: [[../decisions/2026-11-05-odcinki-z-wstawkami-o-uslugach]]

Zlecenie Mateusza (04.11, wieczór): „pracuj całą noc, dopracowuj w loopie, testuj, weryfikuj,
sklej z poprawkami”. Wykryć urwane zdania i braki w planszach (ekranach), wstawić nagrane
przerywniki o usługach, logotypy i makiety „jak Apilo” do Marpasza.

**Poza zakresem:** `ep-vibecoding` („Szef programuje z AI”) — opublikowany. Niezacommitowane zmiany
w tym worktree (storyboardy `ch-vibe-*`, `zaj-vibecoding`, hunk vibecoding w `edl.py`, `package.py`,
`clips.json`) są cudze — nie commitować ich, nie nadpisywać.

**Odcinki:** ep-open-mercato-offers, ep-8-wdrozen, ep-doram, ep-rezon, ep-marpasz, ep-vacuactiv, ep-module.

Plan wstawek (miejsca, podejścia): vault `marketing/content/youtube/_wstawki-uslugi-plan.md`.
Źródło wstawek: `~/Youtube Projects/openmerxat-wstawki.mov` (transkrypt: scratchpad sesji, do
ponownego zrobienia `whisper … --model turbo` jeśli zniknie).

## Pętla — jedna runda = jeden punkt

Każdy punkt: zrób → zweryfikuj (verify.py / transkrypcja gotowego pliku / klatki kontrolne Read)
→ odhacz z wynikiem w jednym zdaniu → następny. Nie przechodź dalej z czerwonym testem.

- [x] 1. Audyt cięć: każda sklejka i granica EDL w 7 odcinkach — słowo przed/po, czy zdanie urwane, falstart, dubel (words.json + splices.json)
- [x] 2. Audyt plansz: przedziały > 25 s bez zdarzenia w storyboardzie, nazwane narzędzia bez logotypu, liczby bez planszy
- [x] 3. Poprawki cięć w `edl.py` (tylko hunki 7 odcinków) → `cut.py` → `verify.py` dla poprawionych
- [x] 4. Wstawki jako klipy biblioteki: źródło `wstawki` w `sources.py`, klipy `ins-intro`, `ins-mid`, `ins-mid-long`, `ins-outro` w `edl.py` → `cut.py` → `verify.py`
- [x] 5. Odsłuch „w filmie / w firmie” (1:39, 2:39 w pliku wstawek) — transkrypcja wycinka large-v3
- [x] 6. Logotypy: apilo, baselinker, inpost, nexo, allegro (jest?), erli → `assets/logos` + kolory
- [x] 7. Makiety „jak Apilo”: lista zamówień, zamówienie 4×25 kg, „Wyślij przesyłkę” z 4 komentarzami — dane zmyślone
- [x] 8. Plansze w lukach: wszystkie 7 odcinków bez luk > 25 s (patrz runda 4)
- [x] 9. Sklejki odcinków ze wstawkami (`compile_episode.py`), przeliczone rozdziały
- [x] 10. Render youtube wszystkich 7 → klatki kontrolne co ~30 s + transkrypcja gotowego pliku (urwania na łączeniach)
- [x] 11. Podglądy Studia (serwer buduje sam w tle) + rozdziały w `data/episodes/*.json` panelu
- [x] 12. Commit tylko własnych ścieżek, ADR, raport dla Mateusza

## Dziennik

(dopisywany po każdej rundzie)

### Runda 1 (04.11 ~23:30) — cięcia

Metoda: transkrypcja GOTOWYCH plików (mlx large-v3-turbo, słowa z czasami) → sąsiednie powtórzenia
fraz, wycieki na brzegach, porównanie z oczekiwanym tekstem. Czasy Whispera w surówce bywają
przesunięte o ~1,5 s — granice ustawiane z ciszy w sygnale (`fillers.levels`) i sprawdzane sklejką
dźwięku + transkrypcją, zanim weszły do EDL.

Naprawione (zweryfikowane transkrypcją nowego mastera):
- ep-rezon: początek „Pójdzie. Ok” → „OK, kolejny temat” (start 2770,20); falstart „Włożyliśmy,” wycięty;
  duble „na pace / na naszym dostawcach. Dostawczaku.” → „na tak zwanej, na pace, na naszym dostawczaku”.
- ep-module (cz. 1): „właściciela. Właściciela.” → jedno (start 253,48).
- ep-8-wdrozen: rozdziały kończące się na „więc” (kody, Doram) i „firmę handlową i” (katalog AI, Marpasz)
  → nowe klipy `ch-doram-6-kody-15-minut-full`, `ch-marpasz-3-katalog-ai-full` tylko dla składanki;
  rolki i reklamy miejskie zostają na starych klipach.

Świadomie zostawione: retoryczne powtórzenia („Mózg firmy. Mózg firmy polega…”, „Niewłaściwe.
Niewłaściwe dlatego…”, „przeklejała, drukowała ×3”), potknięcie Marpasz 1:30 („ma się teraz. Teraz,
jak wcześniej…” — wycięcie psuło sens), Vacu Activ rozdz. 5 kończy się opadającym „sprawnie.” (wycinek).

### Runda 1 — audyt plansz (luki > 25 s bez grafiki)

- ep-vacuactiv: grafika ~20% czasu, 15 luk (najdłuższe 7:35–8:33 58 s, 11:24–12:20 56 s); marki bez logo:
  WhatsApp/Slack 9:33, Telegram 10:22, Obsidian 13:19, Subiekt 14:34.
- ep-doram: ~29%, 9 luk (7:39–8:33 55 s, 2:41–3:23 43 s, 5:03–5:45 43 s).
- ep-marpasz: ~29%, 4 luki; bez logo: Apilo/BaseLinker 0:40, Apilo 1:35, Nexo 5:03.
- ep-8-wdrozen: ~38%, 7 luk ~26–39 s (dziedziczone z rozdziałów).
- ep-module: ~55%, 1 luka 4:18–5:07 (49 s); 2 kotwice „Nie handlowiec” nie trafiają (do sprawdzenia przy renderze).
- ep-rezon, ep-open-mercato-offers: bez luk > 25 s.

### Runda 2 (05.11 ~00:30) — wstawki i logotypy

- Źródło `inserts` (`openmerxat-wstawki.mov`), transkrypcja `data/transcripts/inserts.json`.
  Klipy: `ins-intro` 32,1 s, `ins-mid` 30,1 s, `ins-mid-long` 51,3 s (OM), `ins-outro` 15,9 s —
  `verify.py`: ok, pokrycie 95–100%. Każda sklejka najpierw sprawdzona sklejką dźwięku + transkrypcją.
- „w filmie”: dwa modele (turbo, large-v3-turbo) słyszą „w filmie” — zdanie pominięte, zaproszenie
  od „Poczekaj, zatrzymam Cię tu na chwilę.” prosto do „Robię konsultacje…”.
- Logotypy (packaging/brand/logos): apilo, baselinker, erli (CDN integracji BaseLinkera / apilo.com),
  inpost (inpost.pl), nexo (ikona „nexo PRO” z insert.com.pl) — obrysowane potrace, sprawdzone renderem.

### Runda 3 (05.11 ~01:30) — makiety Apilo + Marpasz, checkpoint

- Makieta `apilo` (mockups.py): `mode: orders` — lista zamówień, pierwsza pozycja „4 paczki” podświetlona;
  `mode: shipment` — „Wyślij przesyłkę”, 4 paczki × „Komentarz” wpisywany po kolei, „Wyślij”.
  Klatki kontrolne obejrzane (76 s, 101,5 s): układ jak panel Apilo, dane zmyślone (ZAM-10418…).
- ep-marpasz: logotypy Apilo+BaseLinker (0:40), lista zamówień (1:08), „Wyślij przesyłkę” (1:34),
  stara plansza „wcześniej ręcznie” przesunięta na 1:48, Nexo (5:02), Erli dopisane do platform,
  tytuł „Drugi przykład z tej firmy” (4:46), lista „Wprowadzanie produktów” (5:28).
- Gałąź **mmkozlowski/noc-odcinki-0411** (od gałęzi Agaty, jej niezacommitowane zmiany NIE weszły:
  hunki vibecoding w edl.py, zmiany package.py poza LOGO_COLORS, klipy vibe w clips.json z HEAD).
  Commit d30a8b3, wypchnięty.

**Następna runda:** pkt 8 dla vacuactiv (15 luk), doram (9), 8-wdrozen (7), module (1 + kotwice
„Nie handlowiec”), potem pkt 9: montaż wstawek = cięcie gotowych renderów youtube-F w punktach
z planu wstawek + render wstawek przez storyboard (CTA flowbiz.pl / 536 507 701) i sklejenie ffmpeg.

### Runda 4 (05.11 ~02:15) — plansze w lukach

Udział grafiki w czasie (przed → po): Vacu Activ 20% → 40% (15 luk → 0), Doram 29% → 49% (9 → 0),
Marpasz 29% → 42%, 8 wdrożeń 38% → 44% (7 → 0), moduł 55% → 57%. Rezon i oferty bez zmian (bez luk).
Tylko istniejące typy zdarzeń (title/list/beat/logos), treść wyłącznie z tego, co Mateusz mówi
w danym miejscu; kotwice sprawdzone — czasy rosną monotonicznie, żadna nie cofa się do wcześniejszego
wystąpienia słowa. „8 wdrożeń”: dołożona karta „Case study · producent sprzętu sportowego” na wejściu
rozdziału Vacu Activ (wcześniej zaczynał się bez kontekstu od „My wychodzimy z innego założenia”).
Fałszywe alarmy audytu: kotwice „Nie handlowiec” (moduł) działają przez caption-fixes („handlowie”).
Składanki przebudowane (`compile_episode.py`) z klipami *-full.

### Runda 5 (05.11 ~02:45) — wstawki w odcinkach (w toku)

- Storyboardy wstawek `ins-*.json` (bez planszy końcowej, CTA flowbiz.pl · 536 507 701), klatki
  ins-mid obejrzane.
- `tools/assemble_episode.py`: render youtube-F + wstawki → `…__youtube-F--with-inserts.mp4`,
  cięcie w najdłuższej ciszy ±1,5 s od kotwicy rozdziału, zamknięcie przed planszą końcową,
  rozdziały po przesunięciu → `data/assembly.json`.
- Render w tle: 4 wstawki + 7 odcinków (nowe cięcia i plansze). Potem: assemble → transkrypcja
  gotowych plików na łączeniach → klatki kontrolne.

### Runda 6 (05.11 ~00:45) — sklejanie i kontrola łączeń

- Rendery: 4 wstawki + 7 odcinków (youtube-F) bez błędów. ep-8-wdrozen: storyboard miał czasy
  liczbowe (plansze rozdziałów i rozdziały) ze starej składanki — po wydłużeniu dwóch rozdziałów
  wypadały w środku zdań; przeliczone na nowe początki części, render ponowiony.
- Pierwsze sklejenie 5 odcinków → transkrypcja każdego łączenia ±6 s. Czysto: oferty, moduł,
  zaproszenie w Rezonie i Marpaszu, wszystkie zamknięcia. **Złe:** wstęp Marpasz („firma handlowa,
  która… | wstawka | handluje paszą”), wstęp Rezon („kontrolę nad… | … | nad firmą”), wstęp i
  zaproszenie Doram w środku zdania, zamknięcie Doram po „Dzięki i do usłyszenia”.
- Przyczyna: kotwica rozdziału w środku zdania, najbliższa cisza = oddech. Poprawka w
  `assemble_episode.py`: cięcie w ciszy po NAJBLIŻSZYM końcu zdania (. ? !), rozdział startuje tuż
  po wstawce; Doram: zamknięcie `before:Dzięki i do usłyszenia`. Ponowne sklejenie + kontrola w toku.

### Runda 7 (05.11 ~01:30) — łączenia czyste, klatki kontrolne

- Trzecie podejście do cięć: granice słów z transkrypcji GOTOWEGO renderu (`build/work/final-words/`),
  cięcie w przerwie po najbliższym końcu zdania; skróty („np.”) wykluczone; zamknięcie przed własnym
  pożegnaniem (`before:` — Doram „Dzięki i do usłyszenia”, Vacu Activ „No dobra. Dziękuję Wam…”).
- Kontrola transkrypcją wszystkich 40 łączeń (7 odcinków × 4–6): każde od końca zdania do wstawki
  i z powrotem. Dwa świadome kompromisy: Marpasz „…to też jest katalog AI. | zaproszenie | Katalog AI,
  jak to wygląda?”, 8 wdrożeń „…tworzenie ofert. | przedstawienie | To jest jeden z…”.
- Klatki kontrolne nowych plansz (Doram 7, Vacu Activ 8): błąd znacznika — `*` wyróżnia od słowa
  do końca, para `*…*` zostawiała dosłowną gwiazdkę („drugi Excel*”). Poprawione 5 tytułów
  (Doram 2, Vacu Activ 2, 8 wdrożeń 1), ponowny render tych trzech + sklejenie.

### Runda 8 (05.11 ~02:00) — Studio i zamknięcie

- `export_studio.py`: odcinek z `--with-inserts.mp4` ma pierwszeństwo przed gołym renderem; spis
  wyeksportowany (66 filmów). Rozdziały 7 odcinków wpisane przez API panelu (PATCH 200). Panel nie
  przyjmuje `length` — długości w raporcie. Podglądy nowych plików buduje serwer w tle.
- Klatka kontrolna po poprawce napisu: „Excel → Excel → drukarka” ✅.

### Runda 9 (05.11 rano) — uwagi Mateusza po obejrzeniu Marpasza

- **Wstawki bez twarzy** („sztucznie wygląda, dźwięk się rozjeżdża, inne ujęcie kamery — zostawmy
  dźwięk, resztę na planszach”): storyboard `"voice_only": true` → stałe tło pod planszami, kamera nie
  prześwituje; cztery wstawki przepisane na ciągłe plansze z jego zdaniami.
- **Przedstawienie do „…miałem okazję już dotknąć”** — „to nie jest odcinek sponsorowany” wycięte
  („po co mam się tłumaczyć”), cięcie w ciszy 74,38–74,76 s źródła; transkrypcja końcówki ✅.
- **Dźwięk wstawek:** głośność zintegrowana była równa (−14 LUFS); różnica to barwa — wstawce brakowało
  4–6 dB w 1–4 kHz (pomiar widma obu nagrań). `"voice_filter"`: EQ + łagodna bramka na ogon pogłosu.
  `"music_intro": false` — wstawka nie odpala od nowa wejścia muzyki (było słychać doklejenie).
- **Apilo w Marpaszu:** nowy tryb makiety `comment` — JEDNO pole „Komentarz” z czterema pozycjami po
  przecinku; zaznacz i usuń → Excel → drukuj 1/4 → wklej z powrotem → druga pozycja → … 4/4; kroki
  przypięte do słów (`beats`). Ekran wchodzi przy „wracając do sedna” (~10 s później niż przedtem), na
  „fajny system do marketplace'ów” samo logo Apilo. Stary tryb `shipment` (4 pola) zostaje w kodzie.
- **Rezon ~3:30:** mapa zamiast krzywej — prawdziwy zarys wybrzeża (lon/lat, Świnoujście → Hel →
  Mierzeja Wiślana), trasa Kołobrzeg → Ustka → Rowy → Łeba.
- **Jingiel otwarcia** (`Miniaturki Youtube.mp4`): 1,2 s plansza + wejście muzyki → odcinek pod maską
  L (pasek z logo i dolny z CTA) → paski zjeżdżają z kadru po 6,5 s. Pierwsza wersja (pomniejszone okno
  + przenikanie) dawała podwójny obraz — odrzucona po klatkach.
- Sklejone wszystkie 7 odcinków; transkrypcja wszystkich łączeń — każde na końcu zdania (te same dwa
  kompromisy co w rundzie 7). Rozdziały w Studiu przez PATCH (nagłówek `x-studio-request: 1` — nowy
  wymóg panelu). Długości: oferty 3:36, 8 wdrożeń 15:05, Doram 11:50, Rezon 8:02, Marpasz 8:49,
  Vacu Activ 18:53, moduł 9:32.

### Runda 10 (05.11) — paski z miniaturek przy końcu, nie na otwarciu

- Mateusz po obejrzeniu: „ta wstawka z maską nie może być od pierwszej sekundy — ewentualnie przy końcu”.
  Jingiel otwarcia usunięty; paski (maska L) idą na planszach zamknięcia `ins-outro` — wjazd po 0,3 s,
  zjazd 1 s przed końcem. Próba na ostatnich 8 s ujęcia odcinka odrzucona po klatkach: pasek boczny
  ucinał dolny napis „Pokażę, jak to zrobić u Ciebie”.
- Sklejanie przy pełnym obciążeniu Maca zagłodziło panel Studia (load 37) — kolejne sklejki puszczać
  z `nice -n 20`. Długości: oferty 3:35, 8 wdrożeń 15:04, Doram 11:49, Rezon 8:01, Marpasz 8:48,
  Vacu Activ 18:51, moduł 9:31. Rozdziały w Studiu (PATCH 200).

### Runda 11 (05.11) — przedstawienie się: klocki modułów zamiast samego tekstu

- Mateusz: „zamiast samego dużego tekstu animacja klikania się mockupu — składania klocków z modułów
  w jeden system”. Źródło: nowa sekcja strony flowbiz.pl „Z tych klocków składamy Twój system”
  (worktree `porcupinefish`, 9 modułów z prototypów, dane zmyślone). Markup i CSS skopiowane do
  `packaging/brand/site-modules/` (README: skąd i jak odświeżyć), ruch napisany od nowa w
  `mockups.py` → `modules()` na osi GSAP, bo silnik strony liczy czas zegarem przeglądarki.
- `ins-intro`: plansza „Mateusz Kozłowski” zostaje (0–3,7 s); od „pomagam” Excel w oknie systemu →
  od „systemy” 9 klocków wlatuje i wpina się łącznikiem w okno (menu i licznik „n / 9 modułów”
  rosną) → przy „produkcja opakowań / wyroby medyczne / handel B2B / sprzedaż” zapala się moduł
  i kursor klika dwa kroki jego ekranu → na „obszarów” świeci cały system.
- Pułapki: `"until": "+8"` liczy się od startu zdarzenia (przy jednym zdarzeniu od 3,7 s plansza gasła
  w 11,7 s) — koniec podany liczbą (19,3). Wycinek CSS ze strony urwany w połowie reguły unieważnił
  cały arkusz (ikony SVG na pół ekranu) — sprawdzać bilans klamer.

### Runda 12 (05.11) — falstarty w zaproszeniu, muzyka −6 dB

- Mateusz (Marpasz 5:13 i 5:25): „zzzz”, „zatrzymam cię” dwa razy, „wychodzisz i wychodzisz”. Transkrypcja
  słów tego nie pokazywała — whisper scalał falstart z właściwym ujęciem, a jedynym śladem była 3-sekundowa
  dziura między „odpowiedzią” a „czy”. Wykryte dopiero po rozbiciu źródła na wyspy mowy (`silencedetect`)
  i transkrypcji każdej osobno: 95,83–96,71 „Zzzzzz”, 171,77–172,04 szum (whisper: „dziękuję”),
  175,9–179,4 „i wychodzisz z… odpowiem…”. Wycięte z `ins-mid` (i „zzzz” z `ins-mid-long`); Marpasz po
  sklejeniu przepisany słowo po słowie — ciągłe „i wychodzisz z odpowiedzią, czy to w ogóle się opłaca”.
  **Wniosek:** przy wstawkach z wielu podejść dziury >1,5 s między słowami transkrypcji traktuj jak
  podejrzenie falstartu i odsłuchuj wyspami.
- Muzyka „dalej za głośno na całym filmie”: storyboard `"music_db": -6.0` (dokłada do wejścia, tła i końcówki)
  w 7 odcinkach i 4 wstawkach; reklamy bez zmian. Przemiks przez `--finalize-only`, bez renderu obrazu.
- Długości: oferty 3:35, 8 wdrożeń 15:03, Doram 11:44, Rezon 7:56, Marpasz 8:43, Vacu Activ 18:47,
  moduł 9:30. Rozdziały w Studiu (PATCH 200 ×7).
