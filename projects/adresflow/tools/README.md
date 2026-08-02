# Produkcja reklam wideo AdresFlow (9:16)

> **Gotowe reklamy leżą w `projects/adresflow/final/`** — dziewięć spotów z opisem, gdzie którego użyć.
> Ten dokument opisuje, jak powstają i jak je zmieniać.
> Aktualizacja folderu: `python3 finalize.py` (kopiuje tylko pliki bez błędów dekodera).

Pipeline do składania spotów reklamowych: materiał z Higgsfield + warstwa brandingowa robiona lokalnie.

> **Ekrany produktu nie pochodzą z Higgsfield.** Spoty 10–12 (księga wieczysta,
> wycena, kreator oferty) pokazują UI AdresFlow renderowane z HTML przez
> HyperFrames — projekty w `../hyperframes/{kw,wycena,oferta}/`, wyjście
> `../out/screen-*.mp4`. Modele wideo renderują interfejs jako nieczytelną papkę,
> a polskie napisy jako bełkot. Zmiana danych na ekranie = edycja HTML +
> `npx hyperframes check <projekt> && npx hyperframes render <projekt> --fps 30 --quality high --output ../out/screen-<projekt>.mp4`.
> Kosztuje 0 kredytów. **Jak zrobić kolejny taki ekran — `../hyperframes/README.md`**
> (pętla pracy, skala typografii, wzorce choreografii, pułapki bramki `check`).

**Zasada: kredyty idą wyłącznie na wideo.** Logo, typografia, plansze i montaż powstają lokalnie — kosztują 0 kredytów i są w pełni powtarzalne, więc poprawka tekstu nie wymaga regeneracji ujęcia.

## Pliki

| Plik | Rola |
|---|---|
| `brand.py` | generuje warstwy (chrome / linie napisów / endcard) do `overlays/` + `*.json` z pozycjami |
| `render.py` | montaż: wideo bazowe + animowane napisy + endcard |
| `logo.svg`, `logo-brand.png` | logo z `new-design/logo-paths.json` w gradiencie brandu |
| `fonts/Poppins-*.ttf` | font marki (nagłówki wg `adresflow-v2/apps/web/src/styles/legacy.css`) |
| `overlays/` | wygenerowane warstwy PNG z alfą + manifesty pozycji |

## Użycie

```bash
python3 brand.py          # przegeneruj warstwy po zmianie tekstów
python3 render.py         # zmontuj wszystkie wersje do ../out/
python3 render.py v3      # tylko jedna wersja
```

Teksty reklam siedzą w słowniku `VERSIONS` w `brand.py` — jedno miejsce do edycji. Stopień pisma dobiera się **automatycznie** (`fit_size`), więc dłuższe hasło nie rozwali layoutu.

## Paleta (źródło: `adresflow-v2/apps/web/src/styles/legacy.css`)

| Rola | Hex |
|---|---|
| tło / pigułki | `#0a0b10` |
| akcent | `#8b5cf6` |
| akcent jasny | `#a78bfa` |
| magenta (koniec gradientu) | `#d946ef` |
| tekst | `#f1f5f9` |
| tekst drugorzędny | `#94a3b8` |

Gradient marki: `#8b5cf6 → #d946ef` (jak `.logo-flow`). Używany na logo, akcentowanej linii napisu i przycisku CTA.

## Layout planszy

- **Góra:** para pigułek — eyebrow `RZUT 3D Z KARTKI` po lewej, znak + `AdresFlow` po prawej (równa wysokość 126 px).
- **Dół:** nagłówek w dwóch liniach, Poppins Bold 86 px, białe na ciemnych pigułkach; jedna linia wypełniona gradientem marki.
- **Endcard:** ciemne tło z poświatą, logo 300 px, nazwa w gradiencie, podtytuł, CTA `adresflow.com`.

Ciemne pigułki pod tekstem są konieczne — materiał 3D jest niemal biały, więc sam biały tekst byłby nieczytelny.

## Animacja napisów (`render.py`)

Każda linia jest **osobną warstwą PNG** — inaczej nie dałoby się animować ich niezależnie. `brand.py` zapisuje je jako `{ver}-hook0.png`, `{ver}-hook1.png` itd. plus `{ver}.json` z docelową pozycją środka (`cx`, `cy`) i rozmiarem bazowym.

Efekt „pop": skala **0,86 → 1,06 → 1,00** (przeskoczenie i powrót) w 0,34 s, do tego fade 0,16 s i mikro-slide 90 px. Linie wchodzą kaskadowo z opóźnieniem **0,13 s** — to daje rytm typowy dla rolek.

Skalowanie robi `scale=eval=frame` z wyrażeniem zależnym od `t`, a overlay wyśrodkowuje przez `x='cx-w/2':y='cy-h/2'`, więc warstwa rośnie od środka, nie od lewego górnego rogu.

Timing skaluje się do długości klipu: hook wchodzi w 0,40 s i gaśnie w 46 % długości, payoff wchodzi zaraz potem i gaśnie 0,55 s przed końcem (żeby nie prześwitywał przez endcard). Chrome (eyebrow + znak) trzyma się przez cały klip. Endcard ma powolny zoom 1,0 → 1,06, doklejany przenikaniem 0,45 s.

Żeby zweryfikować animację na jednolitym tle (bez szumu z wideo), wyrenderuj samą warstwę na `color=c=0x203040` i zrób `tile` z klatek wejścia — pomiar szerokości pigułki wprost na gotowym spocie jest niewiarygodny, bo ciemne piksele materiału zaburzają próg.

### Pułapka: wypalone czarne pasy w materiale

Gdy obraz wejściowy ma inny aspekt niż 9:16, model potrafi **wypalić czarne pasy w treści** klatki (nie jako letterbox kontenera — `cropdetect` ich nie znajdzie, bo pikselowo są częścią obrazu).

Zdarzyło się to na `veo3_1_lite` przy portretowym skanie kartki: treść zajmowała tylko `y=220..1059` z 1280. Naprawa to czwarty argument `build`:

```bash
build v1 "$OUT/rzut3d-8s-raw.mp4" 8.0 "720:839:0:220"
```

Wycina treść i wypełnia kadr jej rozmytą, przyciemnioną kopią (`gblur=sigma=45`) — standardowy zabieg z rolek. Zakres pasów mierzy się tak:

```bash
ffmpeg -ss 4 -i klip.mp4 -frames:v 1 f.png
python3 -c "
from PIL import Image; import numpy as np
a=np.array(Image.open('f.png').convert('L')); r=a.mean(axis=1)
d=[i for i,v in enumerate(r) if v<28]
print('góra do', max([i for i in d if i<len(r)//2], default=-1),
      '| dół od', min([i for i in d if i>len(r)//2], default=len(r)))"
```

`seedance_2_0` i drugi przebieg `veo3_1_lite` dały pełny kadr bez pasów — problem jest zależny od materiału wejściowego, więc **mierz każdy nowy klip**.

## Środowisko

- `ffmpeg` **nie ma** `drawtext` (brak libfreetype) — dlatego napisy renderuje Pillow do PNG, a ffmpeg tylko je nakłada przez `overlay`.
- ImageMagick renderuje SVG, ale **ignoruje gradienty** (`fill="url(#g)"`) — logo powstaje przez wyciągnięcie alfy i podłożenie gradientu jako maski.
- Poppins nie ma w systemie; pobrany z `github.com/google/fonts` (pobranie z `fonts.google.com/download` zwraca HTML, nie ZIP).

## Co robi MCP, a co lokalnie

Podział jest celowy:

| MCP (kredyty) | Lokalnie (0 kredytów) |
|---|---|
| generowanie ujęć (`generate_video`) | typografia i napisy |
| **podbicie jakości** (`upscale_video`) | logo i kolory marki |
| lektor (`generate_audio`) | montaż, timing, animacja |
| **ocena klikalności** (`virality_predictor`) | — |

Napisy i logo celowo **nie** idą przez AI: modele kaleczą polskie znaki, nie trafiają w firmowy `#8b5cf6`, a każda poprawka copy kosztowałaby kolejną generację.

### Podbicie jakości materiału

Ujęcia wychodzą w 720p. `upscale_video` z providerem `bytedance` i presetem **`aigc`** (materiał wygenerowany przez AI) podbija je do 2K:

```
upscale_video(provider="bytedance", video_id=<job_id ujęcia>,
              width=720, height=1280, resolution="2k", preset="aigc", fps=30)
```

Wymaga podania wymiarów źródła i **nie ma preflightu kosztu**. Montaż i tak wychodzi w 1080×1920 (standard Reels/TikTok), ale zejście z 2K daje ostrość, której `ffmpeg` nie wyciągnie z 720p.

### Ocena przed publikacją

`virality_predictor` zwraca `hook_score` (0–3 s), `sustain`, `viral_potential` i `peak_second`. Warto puszczać spot przed kampanią — `hook_score` mówi wprost, czy pierwsze trzy sekundy zatrzymują. **Limit planu Plus: 2 równoległe zadania.**

Zmierzone warianty hooka (ten sam materiał, różne otwarcia):

| Wariant | Otwarcie | hook | overall | viral |
|---|---|---|---|---|
| v3 | „Twój szkic. Nasz render 3D rzutu." | 27 | 42 | 39 |
| **v3d ✅** | **„Znowu czekasz na rzut 3D?"** | **42** | **54** | **53** |
| v3e | „Rzut na kartce. Nikt tego nie kupi." | 40 | 53 | 52 |
| v3b | plansza `899 zł → 9,90 zł` | 31 | 45 | 44 |

Dwa wnioski, które warto przenosić na kolejne spoty:

1. **Ból odbiorcy bije opis produktu.** „Znowu czekasz…" wygrywa z „Twój szkic. Nasz render." o 15 punktów hooka.
2. **Ruch w 1. sekundzie waży więcej niż treść.** Statyczna plansza z kwotą (v3b) dała tylko 31 — mniej niż warianty z `ramp`, mimo mocnego komunikatu.

### Speed ramp

Opcja `ramp: (head, factor)` w `JOBS` przyspiesza początek materiału — `(2.6, 2.6)` znaczy „pierwsze 2,6 s leci 2,6× szybciej". Dzięki temu transformacja zaczyna się od razu, zamiast po statycznym wstępie. To była połowa poprawy `hook_score`.

Opcja `shock: <sekundy>` dokleja przed materiałem planszę `{ver}-shock.png` z kwotą — działa, ale wypadła słabiej niż sam `ramp`.

## Spot narracyjny (`story.py`) — lektor steruje montażem

`render.py` robi krótkie spoty (6–11 s) z jednym plikiem lektora. `story.py` robi **spot narracyjny ~20 s**, w którym obraz i napisy są podporządkowane głosowi.

**Dlaczego osobny skrypt:** przy zwykłym montażu napisy mają timing procentowy i nie trafiają w słowa. Tutaj kolejność jest odwrócona — **najpierw głos, potem obraz pod głos**.

1. Lektor to **JEDEN plik** `../out/vo-full.mp3` z całym tekstem.
2. `detect_phrases()` znajduje granice fraz przez `silencedetect` — to jedyne źródło prawdy o timingu.
3. Ujęcia z `SHOTS` są rozciągane/skracane do sumy przypisanych im fraz.
4. Napisy wchodzą dokładnie w oknie swojej frazy.

Scenariusze siedzą w `STORIES` — słownik `klucz → {eyebrow, end, script}`, gdzie `script` to jeden wpis `{lines, accent, shot}` na frazę, **w kolejności wystąpienia**. Każdy scenariusz ma własny plik lektora `../out/vo-<klucz>.mp3` oraz **własny eyebrow i planszę końcową** (generowane automatycznie przez `make_brand`) — bez tego wszystkie spoty dziedziczyłyby branding rzutu 3D.

```bash
python3 story.py           # wszystkie scenariusze
python3 story.py hs dz     # wybrane
```

Aktualne scenariusze:

| Klucz | Narzędzie | Długość | Oś narracyjna |
|---|---|---|---|
| `story` | Rzut 3D z kartki | 24,7 s | kartka → grafik → transformacja → mieszkanie |
| `hs` | Home staging | 21,3 s | stare wnętrze → ekipa remontowa → jedno zdjęcie |
| `dz` | Zabudowa działek | 18,2 s | pusta działka → koparka → dom w minutę |
| `full` | całe Studio AI | 28,1 s | dzień agenta → wszystkie narzędzia |

### Automatyczny dobór progu ciszy

Nagrania różnią się dynamiką, więc jeden sztywny próg nie działa dla wszystkich — `vo-hs.mp3` przy `-32dB/0.22` dawał tylko 2 frazy zamiast 6. `detect_phrases(path, want=N)` przechodzi po siatce progów i wybiera ten, który daje dokładnie `N` fraz (a jak żaden nie trafi — najbliższy). Dzięki temu nowy lektor nie wymaga ręcznego strojenia.

Dodatkowo mikroprzerwy krótsze niż 0,25 s są pomijane, żeby oddech w środku zdania nie rozbijał frazy.

### Pułapka: nigdy nie generuj lektora frazami osobno

Pierwsza wersja generowała każdą frazę osobnym wywołaniem `generate_audio`. Efekt: **słychać dwie różne osoby** — każda generacja to niezależny sampling, więc barwa i akcent dryfują, a „AdresFlow" bywa czytane raz po polsku, raz po angielsku.

Jeden plik na cały tekst rozwiązuje to definitywnie, a `silencedetect` daje ten sam timing co osobne pliki. Progi: `SIL_DB = -32dB`, `SIL_MIN = 0.22` — przy innym tempie mowy mogą wymagać dostrojenia (skrypt pokaże, ile fraz wykrył).

Pisząc tekst lektora, **rozdzielaj frazy kropkami** — ElevenLabs robi na nich pauzy, a to one wyznaczają cięcia. Liczby i skróty nadal słownie (`899` → „osiemset dziewięćdziesiąt dziewięć", `3D` → „trzy de", `AdresFlow` → „Adres Flow").

### Za mało materiału na frazę

Gdy ujęcie jest krótsze niż przypisane mu frazy, **nie spowalniamy go dowolnie** — powyżej `MAX_SLOW = 1.15` widać slow motion. Zamiast tego skrypt tnie na zbliżenie: druga część to ten sam materiał w zoomie `ZOOM = 1.30`. Wygląda jak cięcie montażowe, nie jak zwolnione tempo.

Uwaga z pomiarów: **ta poprawka nie podniosła `hook_score`** (26 przed i po). Slow motion nie był przyczyną — realistyczna scena biurowa jest po prostu wizualnie słabszym otwarciem niż abstrakcyjna transformacja. Warto o tym pamiętać, dobierając ujęcie na pierwsze 3 sekundy.

## Muzyka w tle

**Higgsfield przez MCP nie generuje muzyki.** `sonilo_music` i `mirelo_text_to_audio` są oznaczone „Game pipeline only" i instrukcja serwera nakazuje odmawiać standalone requestów. Podkład musi pochodzić z zewnątrz.

`story.py` wykrywa `../out/music.mp3` automatycznie i miksuje go z **duckingiem** — `sidechaincompress` ścisza podkład pod lektorem, całość do `-14 LUFS`. Bez pliku renderuje się sam lektor, nic nie trzeba przełączać.

### Pułapka: „muzyki nie słychać, dopiero potem się rozkręca"

Trzy przyczyny, wszystkie naprawione:

1. **Ciche intro.** Podkłady z bibliotek zaczynają się cicho — zmierzone: `Magic Marker` i `Monks` są na starcie **5,4 dB cichsze** niż w środku. Start od 0 s trafiał w najcichszy fragment. `music_offset()` skanuje utwór i zaczyna od **najgłośniejszego** miejsca.
2. **Za agresywny ducking.** `threshold=0.05, ratio=8` to praktycznie wyciszenie pod każdą sylabą. Teraz `MUS_THRESH=0.12, MUS_RATIO=4`.
3. **Za niski poziom.** `MUS_VOL` podniesione z 0,22 na 0,40, fade in skrócony z 0,8 s na 0,35 s.

Efekt mierzalny: poziom podkładu w planszy końcowej (gdzie lektor milczy) wzrósł z **−23,1 dB na −16,2 dB**.

### Dobór podkładu — `pick_music.py`

```bash
python3 pick_music.py     # ranking plików z ../muzyka darmowa youtube/
```

Mierzy, ile energii utwór ma w **paśmie mowy (300 Hz – 3 kHz)** i jaki ma zakres dynamiki (LRA), na próbce ze środka utworu. Im mniej w paśmie mowy, tym delikatniejszy ducking wystarczy. Wysokie LRA (np. `On Hold` z 6,1) znaczy, że utwór sam skacze głośnością i będzie wyskakiwał między frazami.

Do tego warto zmierzyć tempo — 85–95 BPM siada pod lektora, 130+ rozjeżdża się z rytmem napisów.

Jedyna licencjonowana muzyka dostępna przez MCP to `tiktok_music_trending` / `tiktok_music_tune`, ale **nie zwraca pliku audio** — utwór dokleja TikTok po swojej stronie przy `tiktok_publish` w trybie DIRECT_POST, i wymaga podłączonego konta. Do montażu lokalnego bezużyteczne (ustalenie z projektu Granit).

## Lektor

Ścieżki leżą jako `../out/vo-{ver}.mp3`; `render.py` **wykrywa je automatycznie** i wtedy:

- wydłuża endcard tak, żeby głos zdążył dokończyć zdanie (`end_d = vo + 0.4 − dur + 0.45`),
- dodaje `adelay` 200 ms, fade'y i `loudnorm=I=-16:TP=-1.5` (norma dla social).

Bez pliku `vo-*.mp3` spot renderuje się niemy — nic nie trzeba przełączać.

Teksty lektora siedzą w polu `vo` w `VERSIONS`. **Liczby i skróty pisz słownie** (`899` → „osiemset dziewięćdziesiąt dziewięć", `3D` → „trzy de") — inaczej silnik czyta je po angielsku.

### Dobór głosu po ekspresji — `voice_test.py`

```bash
python3 voice_test.py "Marcus=/tmp/a.mp3" "Wilder=/tmp/b.mp3"
```

„Mało emocji w głosie" da się zmierzyć: ekspresja to **zmienność wysokości tonu** (intonacja), rozrzut głośności między sylabami i LRA. Płaski lektor ma niskie wszystkie trzy.

Zmierzone na tym samym tekście:

| Głos | Zmienność tonu | Ekspresja |
|---|---|---|
| **Wilder** (`39c02668-cd27-4313-9164-2ba0eb5098cf`) | **99,8 Hz** | **8,6** |
| Harrison (`573e5163-…`) | 46,3 Hz | 7,3 |
| Zane (`9ddbff06-…`) | 53,5 Hz | 6,9 |
| Marcus (`6f98d3dd-…`) | 40,4 Hz | 6,4 |

**Wykrzykniki w tekście nie wystarczą** — dodanie emfazy podniosło Marcusa tylko z 6,4 na 6,9. Płaskość siedzi w samym głosie, nie w interpunkcji. Zmiana głosu daje dwukrotnie większą zmienność intonacji.

**Wybrany głos: Harrison** (`573e5163-59b3-4926-aab1-951ef2985f81`) — najlepszy balans między ekspresją a powagą. Wilder ma jeszcze żywszą intonację, ale mówi wyraźnie wolniej (15,2 s wobec 13,0 s na tym samym tekście).

### Zmiana głosu wymusza korektę scenariuszy

Każdy głos robi pauzy w innych miejscach, więc **liczba wykrytych fraz się zmienia**. Po przejściu z Marcusa na Harrisona: `story` 6 → 7 fraz, `hs` i `dz` 5 → 6, `full` bez zmian. Skrypt to wykrywa i zatrzymuje się z wypisaniem granic — wtedy trzeba dodać/scalić wpisy w `script`.

W praktyce wychodzi to na plus: drobniejszy podział to więcej plansz i większa dynamika napisów.

## Gadająca głowa (UGC talking head) — stan rozpoznania

Format: agentka mówi do kamery, przebitki narzędzi, napisy karaoke. Higgsfield ma na to gotowy przepis — `get_workflow_instructions("ugc-flow")`: postać przez `soul_2`, boardy 16:9 z ośmioma slotami przez `gpt_image_2`, de-slop przez `seedream_v5_pro`, klipy przez `seedance_2_0` (mowa renderowana natywnie, bez `generate_audio`).

**Krytyczne ograniczenie: Seedance nie mówi poprawnie po polsku.** Test (postać + kwestia PL w prompcie) zweryfikowany lokalnie Whisperem:

```
Detected language: Polish
miało być:  „Wzięłam zwykłe zdjęcia z oferty i wrzuciłam je do AdresFlow."
usłyszane:  „wijałam z jukne znajdanie z ofersa i wruszyłam ją do adres flow."
```

Język rozpoznany jako polski, ale słowa przekręcone — model **udaje polską fonetykę**. Do publikacji się nie nadaje.

**Droga obejścia — POTWIERDZONA:** nagrać kwestię po angielsku, a potem `dubbing` z `target_language: "pol"` (tłumaczy, syntezuje i **ponownie synchronizuje usta**).

Zmierzone Whisperem na tym samym ujęciu:

| Ścieżka | Transkrypcja |
|---|---|
| Seedance mówi PL wprost | „wijałam z jukne znajdanie z ofersa i wruszyłam ją do adres flow" ❌ |
| Seedance EN | „Check this out. I took plane photos from a listing and dropped them into address flow" ✅ |
| Seedance EN → `dubbing` pol | **„Spójrz na to, wziąłem zwykłe zdjęcia z ogłoszenia i wrzuciłem je do adres flow"** ✅ |

Pliki testowe: `../out/TEST-talkinghead-{pl,en,dubbing-pl}.mp4`.

### KRYTYCZNE: rodzaj gramatyczny w dubbingu

Angielski czas przeszły jest bezrodzajowy („I took"), polski **nie jest** — tłumacz musi wybrać rodzaj i wybiera **męski**. Przy kobiecie na ekranie („wziąłem" zamiast „wzięłam") to dyskwalifikuje materiał.

**Zasada: kwestie EN pisz w czasie teraźniejszym albo trybie rozkazującym.** Zweryfikowane na tym samym ujęciu:

| Kwestia EN | Polski wynik |
|---|---|
| „I **took** photos and **dropped** them in" | „**wziąłem** … **wrzuciłem**" ❌ forma męska |
| „You **upload** one photo, and AdresFlow **gives** you…" | „**Wgrywasz** jedno zdjęcie, a AdresFlow **daje ci**…" ✅ bezrodzajowe |

Bezpieczne formy polskie: `biorę / przeciągam / mam / wrzucasz / masz / zobacz / skończ / wejdź`. Niebezpieczne: wszystko w czasie przeszłym i tryb przypuszczający.

**Drugi drobiazg:** dubbing tłumaczy dosłownie — „3D floor plan" wyszło jako „trójwymiarowy plan piętra" zamiast branżowego „rzut 3D". Terminy warto sprawdzić Whisperem i w razie potrzeby przeredagować oryginał EN.

### Weryfikacja mowy Whisperem

W systemie jest `whisper` (homebrew). Do sprawdzenia, czy klip faktycznie mówi to, co miał:

```bash
ffmpeg -i klip.mp4 -vn -ar 16000 -ac 1 /tmp/a.wav
whisper /tmp/a.wav --model base --output_format txt --fp16 False
```

Wypisuje wykryty język i transkrypcję. Bez tego nie da się stwierdzić, czy generacja mówi poprawnie — samo „brzmi po polsku" na klatkach nic nie znaczy.

## Copy — na czym stoi perswazja

Trzy wersje to **trzy kierunki do testu A/B**, nie trzy warianty tego samego:

| Wersja | Kierunek | Hook → Payoff |
|---|---|---|
| v1 | kontrast cenowy | „Rzut 3D u grafika? 899 zł." → „U nas: 9,90 zł. I jedna minuta." |
| v2 | brak pośrednika | „Masz kartę lokalu. Nie masz wizualizacji." → „9,90 zł. Zamiast 899 zł." |
| v3 | efekt + cena | „Twój szkic. Nasz render 3D rzutu." → „Zamiast 899 zł zapłać 9,90 zł." |

Konkretne kwoty biją nieostre „kilka / kilkaset" — liczba jest zapamiętywalna i daje natychmiastowy kontrast.

### Retoryka: kontrast z ceną u grafika, ale bez NASZEJ ceny

Podawanie własnej kwoty (9,90 zł) okazało się kłopotliwe — trudno ją obronić przy modelu kredytowym, gdzie koszt zależy od pakietu i liczby etapów. Aktualna linia w `story.py` omija ten problem:

> „Znowu rzut na kartce? **899 zł u grafika. Tydzień.** Wrzuć zdjęcie. Render 3D w 60 sekund. **Za darmo — 15 kredytów.**"

Kontrast zostaje (899 zł i tydzień u grafika), ale zamiast licytować się ceną prowadzimy do **darmowych kredytów startowych**. CTA: „Odbierz 15 kredytów". Zaleta: nie trzeba bronić żadnej własnej kwoty, a bariera wejścia spada do zera.

Ta linia obowiązuje we **wszystkich** wersjach — `VERSIONS` w `brand.py`, `SCRIPT` w `story.py` oraz plansza `price_shock` (`899 zł` → `ZA DARMO`). Endcard wszędzie: „Pierwsze rzuty 3D za darmo" → „Odbierz 15 kredytów" → `adresflow.com`.

Liczby użyte w copy i ich źródła:

- **15 kredytów gratis na start** — wartość obowiązująca od 2026-08-02 (wcześniej 30). **Do zsynchronizowania po stronie produktu:** nazwa migracji nadal brzmi `signup_credits_30`, a `data.ts:322` mówi „5 kredytów na start" — dopóki to nie zgra się z reklamą, spot obiecuje co innego niż daje rejestracja.
- **9,90 zł za rzut** — decyzja właściciela. Z cennika w repo wychodzi mniej (2 kr/etap × 3 etapy = 6 kr ≈ 5,88 zł przy `BASE_RATE 0,98 zł/kr`), więc reklama obiecuje **drożej niż jest** — od strony roszczeń bezpieczne.
- **899 zł za rzut 3D w branży** — wiedza domenowa właściciela, **nie dane z repo**. Roszczenie porównawcze w płatnej kampanii musi być prawdziwe i weryfikowalne, więc przed publikacją warto mieć na to źródło (cennik pracowni, oferta, zrzut).

## Baza ujęć (`../out/raw-*.mp4`)

Materiał jest **wielokrotnego użytku** — te same ujęcia obsługują kilka scenariuszy, więc nowy spot zwykle nie wymaga generowania niczego nowego.

| Plik | Co pokazuje | Rola narracyjna |
|---|---|---|
| `raw-agent.mp4` | klient podaje odręczny szkic, agent łapie się za głowę | problem |
| `raw-grafik.mp4` | grafik nocą w CAD-zie, przeciera oczy | koszt starej metody |
| `raw-ekipa.mp4` | malarz na drabinie, składanie mebli | koszt starej metody |
| `raw-budowa.mp4` | koparka kopie fundamenty | koszt starej metody |
| `raw-v3-2k.mp4` | kartka → render 3D (fioletowa transformacja, 2K) | rozwiązanie |
| `raw-hs-morph.mp4` | wnętrze przed → po | rozwiązanie |
| `raw-dz-morph.mp4` | pusta działka → dom | rozwiązanie |
| `raw-tablet.mp4` | dłonie z tabletem pokazującym render | efekt |
| `raw-mieszkanie.mp4` | para ogląda mieszkanie z agentką | korzyść dla klienta |

**Źródła przed/po są w repo, nie generowane:** `projects/adresflow/assets/photos/` zawiera realne pary z produktu (`przed1..3`/`po1..3`, `dzialka`/`dzialka_po`, `puste`/`pusty_pokoj_po`, `remont_przed`/`remont_po`). Do transformacji wystarczy wgrać parę jako `start_image` + `end_image`.

Uwaga: pary są w kadrze 16:9, a spoty w 9:16 — przy przycięciu ginie sporo kadru i transformacja wnętrza potrafi wyjść **subtelnie** (tak stało się z `raw-hs-morph`). Do nowych par wybieraj takie, gdzie różnica przed/po jest wyraźna także w środkowej, pionowej części kadru.

## Powiązane

- ADR: `projects/adresflow/ai/decisions/2026-07-30-reklamy-higgsfield-rzut-3d.md`
- Pamięć: `.ai/memory/higgsfield-mcp-limity.md`
- Materiał źródłowy: `ads/fajny rzut z karkti/`, `ads/rzut 3d 1/`
