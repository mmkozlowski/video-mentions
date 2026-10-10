# Opakowanie klipów: jeden storyboard → trzy formaty × dwie palety

**Data:** 2026-10-09 (noc z 8 na 9.10)
**Status:** ✅ wdrożone (próbki 5 klipów) · plan (reszta biblioteki, Higgsfield)

## Problem

Z bazy 63 klipów (ADR [2026-10-08](2026-10-08-baza-klipow-z-sesji-nagraniowej.md)) mają
powstać rolki, reklamy i materiał na YouTube — każdy format inaczej skrojony pod kanał,
zawsze z **oryginalnymi znakami narzędzi**, a paleta jest nierozstrzygnięta: kanał YouTube
(czerń + bursztyn) kontra strona flowbiz.pl (ciemna zieleń + `#1C9E7A`).

## Decyzja

1. **Grafika z HTML (HyperFrames), nie z generatora** — jak przy ekranach produktu
   (`.ai/decisions/2026-07-30-ekran-produktu-z-html.md`). Karty, czat Telegrama, liczniki,
   listy i logotypy są deterministyczne i tanie w poprawkach. Generator robi wyłącznie
   ujęcia z życia (b-roll).
2. **Jeden storyboard na klip** (`packaging/storyboards/<clip>.json`), zdarzenia kotwiczone
   na **wypowiadanych słowach**, nie sekundach. Generator `tools/package.py` składa z niego
   wszystkie warianty:

   | format | kadr | co ma |
   |---|---|---|
   | `reels` | 9:16 | twarz u góry (1215 px), karty w panelu, napisy słowo po słowie, hook, CTA organiczne (komentarz → lead magnet) |
   | `ad` | 9:16 | jak reels + chip CTA, plansza końcowa z konsultacją / zapisem i telefonem |
   | `youtube` | 16:9 | twarz pełnym kadrem, karty w panelu bocznym (twarz odjeżdża w lewo), belka z imieniem, bez napisów |

3. **Dwie palety A/B** z tych samych storyboardów — decyzja o palecie zapada na żywym
   materiale, nie na opisie. A = `scene-shell.css` z systemu wstawek, B = tokeny strony
   (`--brand #1C9E7A`, tryb ciemny `hsl(165 40% 8%)`, Plus Jakarta Sans).
4. **B-roll dwuetapowo: kadr → ożywienie.** Najpierw 18 istniejących ujęć Veo z
   `projects/youtube` (darmowe), potem nowe: kadr Nano Banana Pro (ocena w sekundę, ~0,13 USD),
   ożywienie Veo 3.1 tylko dla kadrów, które przeszły ocenę. Higgsfield był niezalogowany
   tej nocy — ścieżka zapasowa przez Gemini API z tym samym podziałem etapów.
5. **Wykończenie** (`finalize()`): dwuprzebiegowy loudnorm do **−14 LUFS** (render wychodził
   −26), x264 CRF 20 (60 MB → ~20 MB), kontrola a/v ≤ 0,1 s.

## Pułapki

- **Kotwica słowna musi być dokładna i szukana od bieżącego zdarzenia w przód.** „Siedzi”
  trafiło w „siedzi” z hooka (ujemny czas karty), „Po” trafiło w „początku”. Prefiks tylko
  z tyldą (`zapam~`).
- **Pion ma trzy strefy zakazane:** górne ~230 px (UI Reels), prawa kolumna przycisków
  (~130 px), dolne ~260 px. Panel kart ma `right:132px`, chip CTA i znak AI siedzą pod
  górnym UI.
- **Wszystko, co stoi u góry kadru, wchodzi po hooku** — znak marki, chip CTA i podpis
  przebitki nachodziły na tytuł z pierwszych sekund (wyłapał `hyperframes check`).
- **Znak „Ujęcie wygenerowane przez AI”** przy pierwszej przebitce generowanej, u góry,
  na czas przebitki (art. 50 ust. 4 AI Act, `.ai/memory/oznaczanie-tresci-ai`).
  Przełącznik na platformie nadal ręcznie.
- **Nano Banana Pro zwraca JPEG** mimo kadru zamawianego jak PNG — rozszerzenie z `mimeType`.
  Na hasło „tylko jeden kadr” potrafi oddać tryptyk z ramkami — kadry ocenia się arkuszem
  przed ożywieniem.
- **Węzeł 22+**: `hyperframes` nie wstaje na domyślnym Node 20 z nvm.

## Korekta po pierwszym przeglądzie (9.10, rano)

Mateusz obejrzał 90 próbek. Wersja YouTube (panel boczny) się obroniła, w pionie było
**za dużo naraz**: hook w kafelkach słowo po słowie, pod nim napisy powtarzające to samo,
karta w panelu z tym samym tekstem, znak AI, chip i logo w rogu, wszystko w pierwszych
sekundach. Do tego wiszące „yyy” i pauzy z nagrania z promptera.

Decyzje (wszystkie w silniku, więc dotyczą każdego klipu):

1. **Jedno zdanie = jedno tło.** Hook to jeden blok na dole kadru, na piersi, nie na twarzy.
   Pełnoekranowa plansza z hookiem odpada, bo zdaniem Mateusza zabiera wiarygodność.
   Można ją potem przetestować jako wariant A/B.
2. **Kolejność wejść.** Pod hookiem twarz na całym ekranie i sam hook. Po hooku kadr
   odjeżdża i wjeżdża dolny panel. Karty w panelu startują dopiero po nim.
3. **Napisy znikają**, gdy na ekranie jest hook, plansza albo karta powtarzająca wypowiedź
   (wspólne słowo ≥ 4 litery). Wtedy zostaje sam pasek.
4. **Ikony narzędzi w pionie na osobnej planszy** (pełny ekran, głos pod spodem).
   W 16:9 zostają w panelu bocznym. Nowy typ zdarzenia `slate` to plansza z jednym zdaniem.
5. **Logo tylko na ostatnim ekranie**, duże, w nowej wersji „flowbiz AI”
   (`brand/logos/flowbiz-ai.png`). Znak w rogu usunięty. YouTube dostał planszę 2,5 s.
6. **Chip CTA w dwóch oknach** (po hooku i na finiszu) zamiast przez cały klip. Końcówka
   przewija miejscowości: Słupsk → Pomorze → Gdańsk → Koszalin → strona.
7. **Wycięte pauzy.** `build_clips.py` tnie każdą lukę między słowami > 0,55 s (Whisper nie
   zapisuje „yyy”, więc w transkrypcji to dziura). Zostaje 0,20 s po słowie i 0,12 s przed
   następnym. Z 63 klipów zeszło 272 s.
8. **Zoom na twarzy** zmienia plan skokiem na każdej sklejce (`splices.json` z `cut.py`)
   i co kilka zdań, z wolnym dryfem pomiędzy. Maskuje cięcia po pauzach.
9. **Tekst dopasowany do strefy** (`fit()`): rozmiar liczony z szerokości strefy i najdłuższego
   słowa. Porównanie w 16:9 układa się w pionie. Strefy przycinają zawartość, a
   `tools/layout_audit.py` przepuszcza wszystkie warianty przez `hyperframes check`
   i zbiera każde wyjście tekstu poza ramkę.

Pułapka: **hook dłuższy niż ~6 s** (W11 miał 10 s) robił z pierwszego ekranu ścianę tekstu.
`package.py` ostrzega. Kotwica `until` ma kończyć pierwszą frazę, nie drugą.
Liczbowe `until` w hooku psują się po wycięciu pauz, dlatego tylko kotwice słowne.

### Do testu (pomysły Mateusza, jeszcze niezrobione)

- **Pierwszy ekran z segmentem odbiorcy:** „AI w firmie produkcyjnej” / „AI w firmie
  handlowej” jako jeden z wariantów reklamy (plansza 1–1,5 s albo pasek nad hookiem)
  i jako miniaturka/okładka rolki. Mierzymy CTR i koszt kliknięcia per segment.
- **Pełnoekranowy hook-plansza** jako wariant B wobec hooka na twarzy (hipoteza Mateusza:
  plansza traci wiarygodność).
- **Czytelność wg referencji (rolka BRAVE / AI Tech Leaders, pokazana przez Mateusza):**
  twarz na pełnym ekranie przez cały czas; jedna zaokrąglona, prawie czarna karta pływa
  nisko i pojawia się tylko, gdy ma treść (liczba + krótki podpis, jedna makieta); napisy
  to 1–2 słowa wersalikami ze świeceniem, na wysokości piersi nad kartą. Mateusz: „nie
  musisz tego teraz stosować, chodzi o czytelność”. Kandydat na wariant `float` obok
  obecnego panelu, do porównania w galerii.

## Druga korekta (9.10, popołudnie)

Uwagi Mateusza do drugiej serii i co z nimi zrobiliśmy:

1. **Tylko paleta A (bursztyn).** „Zieleń kiepsko wygląda.” `ACTIVE_PALETTES = ["A"]`
   w `package.py`. Render, galeria i audyt robią tylko A, a B zostaje w słowniku pod
   ręczne `--palette B`. Liczba wariantów spada z 90 do 45.
2. **Hook to nie sam tekst.** Nad zdaniem stoi grafika: ikona 3D albo schemat (A vs B,
   przepływ, logo narzędzi, licznik 70 → 94 %). Ikony robi `tools/hook_art.py` (Gemini,
   Nano Banana Pro, 17 sztuk, ok. 2,3 USD), a logo narzędzi są zawsze oryginalne
   z `logos.css` i nigdy nie są generowane. Schemat opisuje `hook.visual` w storyboardzie.
   Ikona ma tło karty i `mix-blend-mode:lighten` z maską radialną, więc nie widać
   kwadratu. Docelowo GPT w Higgsfield. Logowanie czeka na Mateusza.
3. **Zdania po kolei, nie wszystko na jednym slajdzie.** Hook i karta tytułowa dzielą
   tekst na zdania. Kolejne pojawia się, gdy pada jego pierwsze słowo, a gdy tekst jest
   przepisany inaczej niż mowa, czas dzieli się proporcjonalnie do długości. W hooku
   zdania leżą w jednej komórce siatki: karta ma wysokość najdłuższego, font jest jeden
   dla wszystkich, więc nic nie skacze.
4. **Hook to nagłówek, nie transkrypcja.** „Co, jak jedyna osoba, która wie, pójdzie
   na emeryturę?” → „Cała wiedza w jednym zeszycie. Co, gdy przyjdzie emerytura?”.
   Etykieta schematu, która powtarza słowo z hooka, wypada (razem z pozostałymi, dla
   symetrii).
5. **Numer telefonu i liczba z jednostką się nie łamią.** `tokens()` skleja grupy cyfr
   („536 507 701”) i liczbę z następnym słowem („3 miesiące”) twardą spacją. `fit()`
   liczy na tych tokenach i szacuje znak na 0,68 em (DM Sans 800 jest szerszy, niż
   zakładaliśmy). Tytuł planszy końcowej też przechodzi przez `fit()`.
6. **Chip nie wchodzi na głowę.** Zjechał z `top:236` na `face_h − 250` (pierś, nad
   napisami).
7. **„Yyyy” nadal było słychać** (ch-offers-1). Whisper dokleja przeciągnięte „yyy”
   i ciszę do sąsiedniego słowa („wycen.” trwało 4,8 s), więc cięcie po lukach między
   słowami tego nie widzi. `tools/fillers.py` czyta audio co 20 ms i wycina ciszę
   (< −42 dB, ≥ 0,55 s, zostaje 0,15 s oddechu) oraz głos bez granicy sylaby przez
   ≥ 0,5 s (przeciągnięta samogłoska). Cięcie, które zostawiłoby kawałek mowy < 0,3 s,
   jest pomijane. Z biblioteki zeszło kolejne 455 s.

Pułapka przy 7: **czasy słów Whispera bywają przesunięte w ciszę** („Jestem” 0,6 s
przed głosem). Gdy tę ciszę wycinamy, słowo liczone po samym początku wypadało
z `words.json`, a za nim napisy i kotwice storyboardu („nie ma słowa „Jestem””, albo
kotwica łapała późniejsze „na”). `cut.words_in` przypisuje teraz słowo do przedziału
o największej części wspólnej, a słowo w całości w krótkiej wyciętej luce stawia na
początku następnego. `cut.py --words-only` przelicza słowa bez kodowania wideo.

Drobne pułapki z tej rundy:
- Po wycięciu „yyy” mówię szybciej, więc kotwica hooka potrafi wypaść za wcześnie
  (ch-offers-1: hook 1,5 s). `package.py` ostrzega, gdy hook trwa < 2,5 s albo dłużej niż
  ~4 s na zdanie.
- Znak „Ujęcie wygenerowane przez AI” trwał co najmniej 2 s, a przebitka bywa krótsza
  (1,2–1,8 s), więc znak zostawał na twarzy. Teraz kończy się razem z przebitką.
- Licznik w grafice hooka i ta sama liczba w zdaniu to dubel. Gdy jest licznik 70 → 94 %,
  zdanie mówi co innego („AI nauczyło się zamówień. Bez programowania od nowa.”).

## Trzecia korekta (9.10, wieczór): cięcia, AI Słupsk, grafiki, odcinki

**Cięcia urywały słowa** (ad-14, 15. s: „…wdrożeniem na [rok]”). Były dwie przyczyny.
Detektor „yyy” wziął przeciągnięte „roook, Ja” (0,5 s głosu bez granicy sylaby) za
„yyy”, a stare cięcie po lukach między słowami wierzyło czasom Whispera, które bywają
przesunięte o pół sekundy. Decyzja: **wycinamy wyłącznie po sygnale** (cisza albo „yyy”
w `fillers.py`), a słowa z transkrypcji tylko chronią. „Yyy” nie może zjeść więcej niż
30% słowa krótszego niż 0,8 s (`cuts_into_word`). Funkcja `build_clips.tighten`
została usunięta.

**Za mocno wycięte pauzy** (Mateusz po odsłuchu). Cisza jest wycinana dopiero powyżej
0,7 s, a zostaje po 0,2 s oddechu z każdej strony (ok. 0,4 s pauzy). Próg ciszy to
−40 dB, z oddechem włącznie. Klipy są ok. 2 s dłuższe niż w poprzedniej serii.

**AI Słupsk w kierunku strony aislupsk.pl.** Paleta `S`: granat-fiolet `#160A2E`, róż
`#FF3388`, gradient tła, nagłówki w kursywie Plus Jakarta Sans (dociągnięta 700/800
italic, OFL) i `word-spacing` 0,1 em, bo kursywa z ujemnym trackingiem zlepiała słowa.
Paletę wybiera marka (`BRANDS[...]["palette"]`, `palettes_for`), a flowbiz zostaje na A.
Ekran końcowy AI Słupsk ma sylwetkę z ratuszem ze strony (`mateusz-cutout.png`,
prawdziwe zdjęcie).

**Prawdziwe przebitki Słupska** (telefon Mateusza, `~/Youtube Projects/b-rolle`,
IMG_8634–8641): ratusz, ulice, deptak, park. Przepis jest w `tools/real_broll.py`,
nagrania bez dźwięku (słychać dzieci), wynik w `build/broll-real/`. W storyboardzie mają
`"ai": false`, więc bez znaku AI, i podpis „Słupsk”. Wchodzą tam, gdzie pada „Słupsk”,
„stąd”, „ze Słupska”.

**Grafiki statyczne pod sprzedaż** (`tools/static_ads.py`): 7 komunikatów × feed 4:5
i story 9:16. Każda liczba pochodzi z nagranego wdrożenia (źródło w
`final/static/sources.json`). Story zostawia górne 260 i dolne 360 px pod interfejs IG.

**Odcinki: makiety i pilot ep-doram.**
- `tools/mockups.py`, zdarzenie `mockup`: ekran dopasowania (doram), Telegram w trybach
  `brief` i `order` (vacuactiv) oraz panel klienta B2B (rezon). Każda makieta pokazuje
  mechanizm z nagrania, bez nazw klientów, w 16:9 i w pionie.
- Przebitka może być nieożywionym kadrem (`.jpg`), wtedy ruch daje tylko Ken Burns.
- `tools/chapters.py` liczy rozdziały YouTube z kotwic w storyboardzie, więc same się
  przesuwają przy zmianie cięcia.
- Pilot `ep-doram.json` (16:9) ma 16 kart (każda ≤ ~14 s), 2 plansze i 6 przebitek.
  Odcinek renderuje się jako jedna kompozycja (11 min).

Pułapka: w odcinkach zakresy EDL nie zawsze idą chronologicznie, więc „następny zakres”
dla słowa-sieroty liczymy po czasie źródła, nie po kolejności listy (inaczej słowa
lądowały kilkadziesiąt sekund dalej).

Pułapka: **nagrania z iPhone'a są w HDR (HLG, bt2020)**. Jedna taka przebitka sprawiła, że
`hyperframes@latest` przełączył cały klip na render HDR (rgb48, x265 slow, wynik HLG): kilka
razy wolniej, a na zwykłym telefonie wyprane kolory. Dodatkowo `ffprobe` na takim pliku
dopisywał przecinek („33.7,”) i wywracał `finalize`. Naprawa:
- `real_broll.py` przepuszcza źródło przez systemowy `avconvert` (H.264 1920×1080 → bt709),
  bo ten ffmpeg nie ma `zscale`;
- `stage()` odrzuca media HDR (`reject_hdr`);
- `probe_duration` bierze pierwszą liczbę z wyjścia `ffprobe`.

**Listy to hasła** (Mateusz: „skracać nawet do haseł, żeby wyglądały tak samo i były
czytelne — ten sam font i długość, nie słowo w słowo”). Lista ma jeden rozmiar fontu, czyli
minimum z punktów, a punkt dłuższy niż 22 znaki daje ostrzeżenie. 21 punktów przepisanych
na hasła 12–20 znaków.

**Logo z bursztynowym „w”** (`flowbiz-ai.png`; biały oryginał to `flowbiz-ai-white.png`).
Litera ma kolumny 447–744 px w PNG i jest przemalowana na `#F5A623`.

**Przebitki muszą wyglądać na polskie** (Mateusz: „b-rolle nie mogą być azjatyckie, muszą
być polskie, podobne do naszych klimatów”). Z ujęć Veo z `projects/youtube` wypadły:
07-warsztat-stol, 18-hala-timelapse, 10-kod-okulary, 01-biuro-excele i 16-tablica-rysunek.
Zamiast nich weszły ujęcia Mateusza z `~/Youtube Projects/b-rolle`, opisane w
`real_broll.py`:
- stock (prawdziwe, bez znaku AI): chaos w biurze, zmęczona szefowa, przy biurku, kod na
  laptopie, zespół;
- Veo („AI”, znak wodny w rogu obcięty): stres przy Excelu, stos dokumentów, szwalnia;
- kadr s11 (warsztat spawalniczy) zamiast azjatyckiej linii produkcyjnej.

**Okładka dla klipów wyrwanych z odcinka** (Mateusz: „dobrze się słucha, ale musi być nadany
kontekst na pierwszym ekranie”). Pole `cover` w storyboardzie daje pełnoekranową planszę od
pierwszej klatki, ok. 2,2 s, z głosem pod spodem: jedno zdanie, kto i jaki problem. Hook
wchodzi po okładce i trwa co najmniej 2,5 s. Mają ją cztery klipy `ch-*`, a jej klatka nadaje
się na okładkę rolki.

## Czwarta korekta (10.10): odcinek dynamiczny i różnorodny

Mateusz o pilocie ep-doram: „czemu wybierasz tylko jeden wariant tekstu po prawej stronie,
masz tyle różnych opcji”, a potem: „dodawać tak, żeby pasowały do kontekstu, nie raz losowo,
żeby było dynamicznie i różnorodnie”. Odcinek 16:9 ma teraz sześć układów:

1. **Panel boczny** (dotychczasowy): listy, porównania, logo.
2. **Pasek dolny na twarzy** (`zone: "lower"`): twarz zostaje na pełnym ekranie.
3. **Nagłówek na przebitce** (`broll.title`, `kicker`, `center`): gradient u dołu albo
   duże hasło na środku.
4. **Uderzenie** (`type: "beat"`), efekty przeniesione z systemu wstawek YouTube
   (`design_handoff_flowbiz_animation`):
   - `strike` (s02): liczba z przekreśleniem po skosie, na stan „przed”;
   - `burst` (s08): liczba z poświatą i cząstkami, na wynik;
   - `slam` (s10): trzy linie z belką i wstrząsem, na puentę.
   Wejście przez błysk bieli (0,2 s).
5. **Twarz w okienku** (`pip`): przy makietach i planszach twarz nie znika, tylko zjeżdża
   do zaokrąglonego okienka w prawym dolnym rogu.
6. **Plansza i makieta na pełnym ekranie.**

Zasada doboru: efekt wynika z treści (liczba, puenta, makieta). Tytuły i cytaty bez
wskazanej strefy losują panel albo pasek, powtarzalnie (ziarno = id klipu) i nigdy trzy razy
z rzędu tak samo.

Nowe prototypy systemu, które pokazują to, o czym mowa: `excels` (trzy Excele kontrahentów
z innymi kolumnami, ep-doram 2:30) i `labels` (klik → PDF 40 stron etykiet, 9:40).

Do zrobienia: grafiki z Higgsfield (GPT Image), ożywiane potem w Higgsfield/Veo, dobrane
do kontekstu odcinków. Czeka na logowanie Mateusza; zastępczo Gemini + Veo jak s01–s12.

## Higgsfield (10.10): przebitki biznesowe pod polski rynek

Mateusz się zalogował: „bądź kreatywny, stawiaj na biznes, żeby robiło wrażenie i
konwertowało w kontekście sprzedaży AI i automatyzacji, dostosowane do rynku polskiego”.

- **18 kadrów w GPT Image 2.5** (0,25 kr./szt.), wszystkie ożywione w **Kling 3.0 Pro**
  (5 s, bez dźwięku, 8,75 kr./szt.). Razem **162 kredyty** z limitu 400 (saldo 1142 → 980).
- **Tematy:**
  - przed/po: biuro zasypane zamówieniami → czysty dashboard;
  - szef w kontroli: raport o 7:00, lotnisko w Gdańsku, zamówienie z auta;
  - branże z odcinków: szwalnia, etykiety, magnesy „Kołobrzeg”, bus nad Bałtykiem,
    kubki „USTKA”, sklep z tabletem, worki paszy, kierownik produkcji, karteczki;
  - sprzedaż usługi: konsultacja na hali, warsztaty w Słupsku, umowa w czacie, mózg firmy.
- W każdym prompcie wprost „white Central European (Polish) people”, polskie realia,
  paleta bursztyn/zieleń.
- **Pliki:** kadry w `assets/broll/hf/stills/`, wideo w `assets/broll/hf/video/` (po
  kompresji do 1080p 49 MB z 179 MB). Manifest z id zadań i kosztem w `data/hf-broll.json`.
- Przebitki weszły do 11 storyboardów i do ep-rezon.
- Nowe prototypy do ep-rezon: `sync` (PC Business ⇄ Open Mercato), `coast` (trasa
  handlowca po wybrzeżu) i `b2b` w trybie `rep` (panel handlowca).

Pułapki Higgsfield:
- `gpt_image_2_5` odrzuca część partii (429, rate limit), więc wysyłaj po 4. Odrzucone
  zadanie nie kosztuje, wystarczy ponowić.
- Kling czasem zwraca rekomendację presetu („IN THE DARK”) zamiast zadania. Trzeba
  ponowić z `declined_preset_id`.
- Wynik ma 1924×1076 px i 24 kl./s, więc normalizujemy do 1920×1080 bt709.
