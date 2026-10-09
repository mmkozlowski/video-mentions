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
