# Noc 04→05.11: dopracowanie 7 odcinków YouTube

**Data:** 2026-11-04
**Status:** w toku (pętla nocna)

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
- [ ] 7. Makiety „jak Apilo”: lista zamówień, zamówienie 4×25 kg, „Wyślij przesyłkę” z 4 komentarzami — dane zmyślone
- [ ] 8. Storyboard ep-marpasz: logotypy + makiety w miejscach z planu; uzupełnienie braków z pkt 2 we wszystkich odcinkach
- [ ] 9. Sklejki odcinków ze wstawkami (`compile_episode.py`), przeliczone rozdziały
- [ ] 10. Render youtube wszystkich 7 → klatki kontrolne co ~30 s + transkrypcja gotowego pliku (urwania na łączeniach)
- [ ] 11. Podglądy Studia (serwer buduje sam w tle) + rozdziały w `data/episodes/*.json` panelu
- [ ] 12. Commit tylko własnych ścieżek, ADR, raport dla Mateusza

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
