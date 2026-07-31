# Reklamy wideo „Rzut 3D z kartki" przez Higgsfield MCP

**Data:** 2026-07-30
**Status:** ✅ wdrożone (pierwszy spot 8 s gotowy w `projects/adresflow/build/`)

## Problem

Chcieliśmy przetestować generowanie krótkich reklam produktu (kilkusekundowych, format 9:16 pod Reels/TikTok) na materiale, który już mamy w `ads/`: odręczny szkic rzutu na kartce → rzut 2D → render 3D. Narzędzie: Higgsfield przez MCP.

## Diagnoza — trzy pułapki, które kosztowały czas

### 1. Trial „unlimited" nie działa przez MCP/API

Panel Higgsfield pokazywał **1-day unlimited free trial — Active, 22 modele unlimited**. Mimo to każde żądanie z `use_unlim: true` było odrzucane:

```
Error: Unlimited generations aren't supported for seedance_2_0.
Error: Unlimited generations aren't supported for nano_banana_pro.
```

...choć oba modele deklarują `supports_unlim: true` w `models_explore`. `balance` konsekwentnie zwracał `unlim: { available: false, remaining: null }`, a panel pokazywał „0 Free generations in total / +$0 Saved".

**Wniosek: unlimited z planu obowiązuje w webowej aplikacji Higgsfield, ale nie jest wystawiony przez MCP.** Przez MCP liczą się wyłącznie kredyty (u nas: 10).

Odrzucone żądania są darmowe — MCP gwarantuje, że request niemożliwy do obsłużenia za darmo jest **odrzucany, nigdy po cichu obciążany**. Można więc bezpiecznie próbować `use_unlim: true`, zamiast zgadywać z góry.

### 2. `veo3_1_lite` wymusza `duration: 8` przy dwóch kadrach

```
Value error, duration must be 8 when both start_image and end_image are set
```

Planowaliśmy dwa ujęcia po 4 s (kartka→2D, 2D→3D) za 2×4 kr. Nie da się: przy `start_image` + `end_image` dozwolone jest tylko 8 s = 8 kr. Wyszło to na korzyść — jedno ciągłe ujęcie 8 s (kartka → 3D) czyta się lepiej niż dwa cięcia, a lektor 8,93 s trafia w nie co do sekundy.

### 3. `seed_audio` — `speech_rate` musi być liczbą całkowitą

```
speech_rate: Input should be a valid integer, got a number with a fractional part (0.95)
```

Przekazanie `0.95` wywala 422. Pomijamy parametr albo dajemy int.

### 4. `seed_audio` NIE mówi po polsku

Domyślny model TTS (`seed_audio`, ByteDance) czyta polski tekst **fonetycznie po angielsku** — nie nadaje się do lektora PL. Trzeba przełączyć się na `text2speech_v2` z `variant: "elevenlabs"` (model multilingual). Koszt rośnie z 0,2 na 0,3 kr za próbkę.

Dodatkowo: skróty czytaj fonetycznie w prompcie (`3D` → `trzy de`), inaczej silnik przeczyta je po angielsku. Część głosów presetowych zwraca `403 free_trial_model_requires_plan` — wymagają planu wyższego niż Plus (u nas odpadł „Roman").

Głosy anglojęzyczne (Marcus, Vlad) przez ElevenLabs przeczytają polski poprawnie, ale mogą nieść obcy akcent. Dla natywnej wymowy właściwą drogą jest `create_voice` — sklonowanie prawdziwego polskiego głosu z próbki audio.

## Decyzja

**Model wideo: `veo3_1_lite`** — jedyny w tej półce cenowej, który przyjmuje `start_image` + `end_image` (8 kr / 8 s). Kadry z `end_image` są kluczowe: przejście trafia dokładnie w naszą grafikę, zamiast halucynować własny render.

**Model lektora: `seed_audio`, głos preset „Marcus"** (męski, `6f98d3dd-324f-4845-8c28-c1d1647a06cd`) — 0,2 kr, poprawnie czyta polski.

**Zmierzone koszty wideo (preflight `get_cost`, 5 s / 720p / 9:16):**

| Model | Koszt | start+end frame |
|---|---|---|
| `veo3_1_lite` (8 s) | 8 kr | ✅ |
| `kling3_0_turbo` | 7,5 kr | ❌ tylko start |
| `seedance_2_0_mini` | 12,5 kr | ✅ |
| `seedance_2_0` | 17,5 kr | ✅ + 4K, natywne audio |
| `grok_video_v15` | 22,5 kr | ❌ tylko start |
| `seed_audio` (lektor) | 0,2 kr | — |

## Wynik

`projects/adresflow/build/rzut3d-reklama.mp4` — 8,93 s, 768×1344 (9:16), lektor PL. Przejście jest **płynnym morfem**, nie cięciem: kartka lekko się obraca, szkic prześwituje przez wyrastające ściany, podłoga dostaje drewno, meble wjeżdżają na miejsce.

Skrypt lektora:

> „Odręczny szkic. Jedno kliknięcie. I masz gotowy render 3D mieszkania. AdresFlow — rzut 3D z kartki, w minutę."

Nazwa narzędzia i copy wzięte z produktu (`adresflow-v2/apps/web/src/lib/data.ts:73-81`), obietnica z `ai/GOAL.md`.

Sklejka lektora z wideo (wideo 8,00 s, audio 8,93 s — dopychamy ostatnią klatką):

```bash
ffmpeg -i rzut3d-8s-raw.mp4 -i lektor-marcus.wav \
  -filter_complex "[0:v]tpad=stop_mode=clone:stop_duration=1[v]" \
  -map "[v]" -map 1:a -c:v libx264 -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest rzut3d-reklama.mp4
```

## Pułapki na przyszłość

- **Weryfikuj wynik gęstym próbkowaniem klatek.** Podgląd co 48 klatek sugerował twarde cięcie kartka→3D; dopiero `select='between(n,48,90)*not(mod(n,6))'` pokazał, że morf jest płynny. Przy 8 s / 24 fps (192 klatki) próbkuj co ~6 klatek w okolicy przejścia.
- **`generate_video` podpowiada presety** („IN THE DARK", „ELEVATE") i **nie generuje**, dopóki nie odrzucisz przez `declined_preset_id`. To nie błąd — to jedno dodatkowe okrążenie w każdym nowym prompcie.
- Prompty do modeli wideo pisz po angielsku; polski idzie tylko do lektora.
- Etap pośredni (płaski kolorowy rzut 2D z `ads/fajny rzut z karkti`) został w tym ujęciu pominięty — model idzie kartka → 3D. Żeby go pokazać, trzeba dwóch osobnych ujęć i sklejki.

## Etap 2 — branding i trzy wersje (2026-07-30, po wykupieniu planu Plus)

Po doładowaniu konta (1200 kr) powstały trzy obrandowane wersje 9:16 — `projects/adresflow/build/adresflow-v{1,2,3}.mp4`. Pipeline i szczegóły: `projects/adresflow/tools/README.md`.

**Decyzja: kredyty wyłącznie na wideo, cały branding lokalnie.** Logo, typografia, plansze i montaż robi `projects/adresflow/tools/` (Pillow + ImageMagick + ffmpeg) — 0 kredytów, w pełni powtarzalne, poprawka tekstu nie wymaga regeneracji ujęcia. Teksty siedzą w słowniku `VERSIONS` w `brand.py`.

| Wersja | Materiał | Model | Koszt |
|---|---|---|---|
| v1 „Narysowałeś rzut na kartce?" | szkic → 3D | `veo3_1_lite` 8 s | 8 kr (etap 1) |
| v2 „Karta lokalu od dewelopera?" | karta M10 → 3D z ogródkiem | `veo3_1_lite` 8 s | 8 kr |
| v3 „Twój szkic. Nasz render." | szkic → 3D, dynamiczny | `seedance_2_0` 6 s | 27 kr |

**Seedance jest wart różnicy ceny** (27 vs 8 kr): prompt o „violet glow racing along the pen strokes" dał efekt zapalających się fioletowych linii — przypadkiem dokładnie w kolorze marki `#8b5cf6`. `veo3_1_lite` przy tym samym promptcie robi spokojniejsze przenikanie. Do materiałów, które mają wyglądać premium, warto brać Seedance.

Zmierzone koszty (preflight, 9:16): `veo3_1_lite` 8 s = 8 kr · `seedance_2_0` 6 s/720p = 27 kr · `seedance_2_0` 8 s/1080p = 72 kr.

### Pułapki etapu 2

- **Wypalone czarne pasy w treści klatki** — gdy obraz wejściowy ma inny aspekt niż 9:16, model może wpalić pasy w piksele. `cropdetect` ich **nie wykryje**. Naprawa i sposób pomiaru: `projects/adresflow/tools/README.md`.
- **ffmpeg bez `drawtext`** (brak libfreetype) — napisy renderuje Pillow do PNG, ffmpeg tylko nakłada.
- **ImageMagick ignoruje gradienty w SVG** — logo powstaje przez alfę + gradient jako maskę.
- **Poppins:** `fonts.google.com/download` zwraca HTML zamiast ZIP; brać z `github.com/google/fonts`.
- Ciemne pigułki pod napisami są konieczne — materiał 3D jest niemal biały, sam biały tekst znika.

Spoty są na razie **bez lektora** (świadomie — najpierw obraz i dynamika). Ścieżka PL z etapu 1 czeka w `projects/adresflow/build/lektor-marcus-eleven.mp3`.

## Etap 3 — copy sprzedażowe i dynamika napisów (2026-07-30)

**Decyzja: perswazja stoi na kontraście z ceną branżową, nie na naszym cenniku.** To, że rzut 3D kosztuje u nas 2 kredyty, jest dla agenta nieistotne — punktem odniesienia jest kilkaset złotych, które płaci się za rzut w branży. Stąd hasła typu „Kilka złotych. Nie kilkaset."

Trzy wersje = trzy kierunki do testu A/B (kontrast cenowy / brak pośrednika / efekt + cena), a nie warianty jednego przekazu. Zestawienie i źródła wszystkich liczb: `projects/adresflow/tools/README.md`.

**Napisy animowane linia po linii.** Każda linia to osobna warstwa PNG (`brand.py` zapisuje `{ver}-hook0.png` + manifest `{ver}.json` z pozycją), a `render.py` animuje ją efektem „pop" (skala 0,86 → 1,06 → 1,00 przez `scale=eval=frame`) z kaskadą 0,13 s. `build.sh` został zastąpiony przez `render.py`.

Stopień pisma dobiera się automatycznie (`fit_size`), więc zmiana copy nie wymaga strojenia layoutu.

## Etap 4 — 2K, lektor i pomiar klikalności (2026-07-30)

**Podział ról MCP vs lokalnie** (opisany w `projects/adresflow/tools/README.md`): MCP robi ujęcia, podbicie jakości, głos i ocenę; typografia, logo i montaż zostają lokalnie, bo modele kaleczą polskie znaki, nie trafiają w `#8b5cf6`, a każda poprawka copy kosztowałaby kolejną generację.

- **`upscale_video`** (`bytedance`, preset `aigc`) podbił v3 z 720p do 2K (1440×2560). Montaż wychodzi w 1080×1920, ale zejście z 2K daje ostrość nieosiągalną dla `ffmpeg`. Narzędzie **nie ma preflightu kosztu** i wymaga podania wymiarów źródła.
- **Lektor PL** dograny do wszystkich wersji (`text2speech_v2` + `elevenlabs`, głos Marcus). `render.py` wykrywa `vo-{ver}.mp3` automatycznie i wydłuża endcard, żeby głos dokończył zdanie.
- **Copy przeszło na konkretne kwoty** — „Zamiast 899 zł zapłać 9,90 zł" zamiast nieostrego „kilka / kilkaset".

### Wynik `virality_predictor` — hook jest za słaby

Analiza spotu v3 (wersja sprzed zmiany copy):

| Metryka | Wynik |
|---|---|
| `hook_score` (0–3 s) | **27 / 100** |
| `sustain` | 97 / 100 |
| `overall_score` | 42 |
| `viral_potential` | 39 |
| `peak_second` | 6 (na końcu) |

Czyta się to jednoznacznie: **kto zostanie, ten dooglądа (sustain 97), ale początek nie zatrzymuje.** Spot startuje statyczną kartką, a najmocniejsze bodźce — fioletowa transformacja i kontrast cenowy — przychodzą dopiero w drugiej połowie; szczyt uwagi wypada na 6. sekundzie, czyli przy planszy końcowej.

Wniosek do przetestowania: **przenieść kwotę i efekt na pierwsze sekundy** — otworzyć ceną („899 zł za rzut 3D?") zamiast opisem, ewentualnie zacząć od przebłysku gotowego renderu. To hipoteza do zmierzenia kolejnym przebiegiem `virality_predictor`, nie pewnik.

## Etap 5 — test hooków na liczbach (2026-07-30)

Trzy warianty hooka, ten sam materiał, zmierzone `virality_predictor`:

| Wariant | Otwarcie | hook | sustain | overall | viral |
|---|---|---|---|---|---|
| v3 (baseline) | „Twój szkic. Nasz render 3D rzutu." | 27 | 97 | 42 | 39 |
| **v3d ✅** | **„Znowu czekasz na rzut 3D?"** | **42** | 91 | **54** | **53** |
| v3e | „Rzut na kartce. Nikt tego nie kupi." | 40 | 92 | 53 | 52 |
| v3b | plansza `899 zł → 9,90 zł` | 31 | 93 | 45 | 44 |

**Wygrywa ból agenta, nie cena.** v3d podniósł `hook_score` o **56 %** (27 → 42) i `viral_potential` o 36 % (39 → 53). `peak_second` przesunął się z 6. sekundy na **0** — najmocniejszy moment jest teraz na starcie, o co chodziło.

Dwie rzeczy, które zadziałały razem:

1. **Ból zamiast opisu produktu** — „Znowu czekasz…" / „Nikt tego nie kupi" biją „Twój szkic. Nasz render." o kilkanaście punktów.
2. **Speed ramp** (`ramp: (2.6, 2.6)` w `JOBS`) — pierwsze 2,6 s materiału leci 2,6× szybciej, więc fioletowa transformacja zaczyna się w 1. sekundzie zamiast w trzeciej. Statyczny start był połową problemu.

**Statyczna plansza cenowa (v3b) wypadła najsłabiej** z trzech nowych — samo pokazanie kwoty bez ruchu daje hook 31. Wniosek: w rolkach ruch w pierwszej sekundzie waży więcej niż treść komunikatu.

`sustain` spadł z 97 na 91–93, ale to efekt dłuższego spotu (11 s vs 7,6 s) — przy rosnącym `overall` to korzystna wymiana.

Limit planu Plus: **2 równoległe zadania** `virality_predictor` — trzecią analizę trzeba puścić po zakończeniu poprzednich.

## Etap 6 — spot narracyjny 20 s z synchronizacją lektora (2026-07-30)

### Problem: napisy nie trafiały w słowa

Przy jednym pliku lektora napisy miały timing **procentowy** (hook do 46 % długości) — nie miały jak trafić we frazy. Rozwiązanie odwraca kolejność produkcji: **najpierw głos, potem obraz pod głos.**

Lektor jest cięty na frazy (`projects/adresflow/build/vo/s1..s6.mp3`), każda mierzona osobno, a `projects/adresflow/tools/story.py` buduje z tego timeline — napisy i cięcia montażowe wynikają z FAKTYCZNEJ długości fraz. Ujęcia są rozciągane/skracane do sumy przypisanych im fraz.

Efekt (`projects/adresflow/build/adresflow-story.mp4`, 21 s):

| czas | ujęcie | fraza / napis |
|---|---|---|
| 0,0–2,4 | agent | „Znowu rzut na kartce?" |
| 2,6–8,3 | agent (cięcie na zbliżenie) | „899 zł i tydzień." |
| 8,5–10,6 | transformacja | „Wrzuć zdjęcie." |
| 10,8–12,9 | transformacja | „Masz render 3D." |
| 13,1–16,4 | tablet | „W minutę. Za 9,90 zł." |
| 16,6–20,4 | endcard | — |

Dwa nowe ujęcia z `seedance_2_0` (po 5 s): agent odbierający odręczny szkic i łapiący się za głowę oraz dłonie obracające tablet z renderem 3D. Domykają narrację problem → rozwiązanie → efekt.

### Wynik pomiaru: narracja kupuje sustain kosztem hooka

| Wariant | hook | sustain | overall | viral |
|---|---|---|---|---|
| v3d (6 s, speed ramp) | **42** | 91 | 54 | 53 |
| story (20 s, narracja) | 26 | **98** | 46 | 50 |

**Hipoteza, która się NIE potwierdziła:** podejrzewałem, że hook zabiło slow motion (scena 5 s rozciągana do 8,3 s). Przebudowa na cięcie na zbliżenie (`MAX_SLOW = 1.15`, `ZOOM = 1.30`) dała wynik **identyczny** — hook 26.

Prawdziwa przyczyna jest w rozbiciu na regiony: aktywność kory wzrokowej w pierwszych sekundach **spada** (0,41 → 0,35) i skacze dopiero przy fioletowej transformacji (0,67). Scena biurowa — stonowane kolory, spokojny ruch, człowiek w koszuli — jest wizualnie za słaba na otwarcie rolki. Abstrakcyjny fiolet przyciąga wzrok natychmiast, realistyczna scena nie.

**Wniosek: to nie wada, tylko dwa różne narzędzia.** Krótki v3d (hook 42) do zimnego ruchu — łapie uwagę nieznających marki. Długi `story` (sustain 98, prawie maksimum) do remarketingu — dla tych, którzy już kliknęli i chcą zrozumieć produkt.

Do przetestowania: hybryda — 1,5 s fioletowej transformacji jako teaser przed sceną agenta.

### Muzyka — Higgsfield jej nie zrobi

`sonilo_music` (muzyka) i `mirelo_text_to_audio` (SFX) są w katalogu oznaczone **„Game pipeline only"** i instrukcja serwera nakazuje odmawiać standalone requestów o muzykę. Podkład trzeba dostarczyć z zewnątrz.

`story.py` jest już na to przygotowany: wykrywa `projects/adresflow/build/music.mp3` i miksuje go z **duckingiem** (`sidechaincompress` — podkład ścisza się pod lektorem), głośność 0,22, fade in/out, całość normalizowana do `-14 LUFS`. Bez pliku renderuje się sam lektor.

Ciekawostka: `inworld_text_to_speech` ma **natywne polskie głosy** („Szymon (pl)", „Wojciech (pl)"), które rozwiązałyby kwestię akcentu — ale jest zastrzeżony dla pipeline'u gier.

### Limity, na które trafiliśmy

- `virality_predictor` przyjmuje **maksymalnie 16 s** — dłuższy spot trzeba przyciąć do analizy (`hook_score` liczy się z okna 0–3 s, więc wynik pozostaje miarodajny).

## Etap 7 — spójny lektor i retoryka bez własnych cen (2026-07-30)

### Pułapka: frazy generowane osobno = dwa różne głosy

Pierwsza wersja `story.py` generowała każdą frazę osobnym wywołaniem `generate_audio`. W odsłuchu **słychać dwie różne osoby** — każda generacja to niezależny sampling, więc barwa i akcent dryfują, a „AdresFlow" bywa czytane raz po polsku, raz po angielsku.

**Rozwiązanie: jeden plik na cały tekst** (`projects/adresflow/build/vo-full.mp3`) + cięcie na frazy przez `silencedetect` (`noise=-32dB:d=0.22`). Daje spójny głos i ten sam timing co osobne pliki. `story.py` weryfikuje, czy liczba wykrytych fraz zgadza się z `SCRIPT`, i przy niezgodności wypisuje granice do dostrojenia progów.

Pisząc tekst lektora, rozdzielaj frazy kropkami — ElevenLabs robi na nich pauzy, a to one wyznaczają cięcia montażowe.

### Zmiana retoryki: nie licytujemy się własną ceną

Podawanie kwoty 9,90 zł było kłopotliwe — trudno ją obronić przy modelu kredytowym, gdzie koszt zależy od pakietu i liczby etapów (patrz rozbieżność wyliczeń w etapie 3). **Decyzja: o naszej cenie nie mówimy wcale.**

Aktualna linia:

> „Znowu rzut na kartce? **899 zł u grafika. Tydzień.** Wrzuć zdjęcie. Render 3D w 60 sekund. **Za darmo — 30 kredytów.**"

Kontrast z ceną u grafika zostaje, ale zamiast licytacji cenowej prowadzimy do **darmowych kredytów startowych**. CTA: „Odbierz 30 kredytów", endcard: „Pierwsze rzuty 3D za darmo". Zaleta: nie trzeba bronić żadnej własnej kwoty, a bariera wejścia spada do zera.

Retoryka obowiązuje we **wszystkich** wersjach — `VERSIONS` w `brand.py`, `SCRIPT` w `story.py` i plansza `price_shock` (`899 zł` → `ZA DARMO`). Endcard wszędzie: „Pierwsze rzuty 3D za darmo" → „Odbierz 30 kredytów" → `adresflow.com`.

### Pełna narracja w siedmiu aktach

Dwa dodatkowe ujęcia z `seedance_2_0` domknęły opowieść — **grafik** ślęczący nocą nad CAD-em (koszt starej metody) i **para oglądająca mieszkanie** (korzyść dla klienta):

| czas | ujęcie | fraza |
|---|---|---|
| 0,0–2,2 | agent z kartką | „Znowu rzut na kartce?" |
| 2,6–7,7 | grafik nocą w CAD | „899 zł u grafika. Tydzień." |
| 8,1–10,1 | transformacja | „Wrzuć zdjęcie." |
| 10,5–13,6 | render 3D | „Render 3D w 60 sekund." |
| 14,0–16,9 | para w mieszkaniu | „Pokaż, jak naprawdę wygląda." |
| 17,2–21,0 | tablet | „Za darmo. 30 kredytów." |
| 21,0–24,2 | endcard | — |

Łuk: problem → koszt alternatywy → rozwiązanie → efekt → korzyść dla klienta → CTA.

Wynik: `projects/adresflow/build/adresflow-story.mp4`, 24,7 s. Krótkie warianty (v1, v2, v3, v3b, v3d, v3e) przebudowane z tą samą retoryką i nowymi lektorami.

## Etap 8 — kampania na całe Studio AI (2026-07-30)

Rozszerzenie z jednego narzędzia (rzut 3D) na **cztery spoty pokrywające ofertę**:

| Spot | Narzędzie | Długość | Oś narracyjna |
|---|---|---|---|
| `adresflow-story.mp4` | Rzut 3D z kartki | 24,7 s | kartka → grafik → transformacja → mieszkanie |
| `adresflow-hs.mp4` | Home staging | 21,3 s | stare wnętrze → ekipa remontowa → jedno zdjęcie |
| `adresflow-dz.mp4` | Zabudowa działek | 18,2 s | pusta działka → koparka → dom w minutę |
| `adresflow-full.mp4` | całe Studio AI | 28,1 s | dzień agenta → wszystkie narzędzia |

**Materiał źródłowy w większości był już w repo.** `projects/adresflow/assets/photos/` zawiera realne pary przed/po z produktu (home staging ×4, działka z zabudową, pusty pokój, remont). Wystarczyło wgrać je jako `start_image` + `end_image`. Dogenerowano tylko ujęcia „starej metody", których nie było: ekipa remontowa i koparka na działce.

Ujęcia są **wielokrotnego użytku** — `full` składa się wyłącznie z materiału nakręconego na potrzeby pozostałych spotów. Inwentarz bazy: `projects/adresflow/tools/README.md`.

### Zmiany w narzędziach

- `story.py` obsługuje **wiele scenariuszy** (`STORIES`), każdy z własnym lektorem, eyebrow i planszą końcową. Bez tego wszystkie spoty dziedziczyły branding rzutu 3D — spot o home stagingu wyświetlał „RZUT 3D Z KARTKI".
- **Automatyczny dobór progu ciszy** (`detect_phrases(want=N)`): nagrania różnią się dynamiką, `vo-hs.mp3` przy `-32dB/0.22` dawał 2 frazy zamiast 6. Skrypt przechodzi po siatce progów i wybiera trafiający w oczekiwaną liczbę fraz. Nowy lektor nie wymaga już ręcznego strojenia.

### Pułapka: kadr 16:9 → 9:16 zjada transformację

Pary przed/po z produktu są w 16:9. Przy przycięciu do pionu ginie sporo kadru i transformacja wnętrza (`raw-hs-morph`) wyszła **subtelnie** — pokój się tylko rozjaśnia. Transformacja działki, gdzie zmiana jest w centrum kadru, wyszła znakomicie. Do nowych par wybieraj takie, gdzie różnica przed/po jest wyraźna w środkowej, pionowej części zdjęcia.

## Etap 9 — miks muzyki, ujęcie zewnętrzne, rozpoznanie gadającej głowy (2026-07-30)

### Muzyka: „nie słychać, dopiero potem się rozkręca"

Trzy niezależne przyczyny, wszystkie naprawione w `story.py`:

1. **Ciche intro podkładu** — zmierzone: `Magic Marker` i `Monks` są na starcie **5,4 dB cichsze** niż w środku, a montaż brał utwór od 0 s. `music_offset()` skanuje utwór i startuje od najgłośniejszego fragmentu (dla Magic Markera: 72 s).
2. **Za agresywny ducking** — `threshold=0.05, ratio=8` to praktycznie wyciszenie pod każdą sylabą. Teraz `0.12 / 4`.
3. **Za niski poziom** — `MUS_VOL` 0,22 → 0,40, fade in 0,8 s → 0,35 s.

Efekt: poziom podkładu w planszy końcowej wzrósł z **−23,1 dB na ok. −16 dB** we wszystkich czterech spotach.

Do doboru podkładu powstał `projects/adresflow/tools/pick_music.py` — ranking po energii w paśmie mowy (300 Hz–3 kHz) i LRA. Z 16 utworów z biblioteki YouTube najlepiej wypadły `Frequency` (89 BPM) i `fajne Magic Marker` (92 BPM); `On Hold` odpada (LRA 6,1 — sam skacze głośnością).

### Ujęcie zewnętrzne

Dogenerowano `raw-dzialka-spacer.mp4` (para z agentem idzie wzdłuż domów po trawie) — spot o działce kończy się teraz **na zewnątrz**, a nie we wnętrzu mieszkania.

### Gadająca głowa: Seedance nie mówi po polsku

Rozpoznanie formatu UGC talking head (`get_workflow_instructions("ugc-flow")`). Krytyczne ustalenie, zweryfikowane lokalnie **Whisperem**:

| Ścieżka | Transkrypcja |
|---|---|
| Seedance mówi PL wprost | „wijałam z jukne znajdanie z ofersa" ❌ bełkot |
| Seedance EN | „Check this out. I took plane photos from a listing…" ✅ |
| Seedance EN → `dubbing` `pol` | **„Spójrz na to, wziąłem zwykłe zdjęcia z ogłoszenia…"** ✅ |

Model **udaje polską fonetykę** — Whisper wykrywa język jako polski, ale słowa są przekręcone. Właściwa droga: nagrać po angielsku, potem `dubbing` z `target_language: "pol"`, który tłumaczy, syntezuje i ponownie synchronizuje usta.

**Pułapka: rodzaj gramatyczny.** Angielskie „I took" jest bezrodzajowe, więc dubbing wybrał formę męską przy postaci kobiecej. Kwestie EN trzeba pisać tak, by po polsku wyszły bezrodzajowo, albo weryfikować wynik.

**Zasada: mowę weryfikuj Whisperem, nie na oko.** W systemie jest `whisper` (homebrew) — klatki nie powiedzą, czy model mówi to, co miał.

### Pułapka: przerwany render daje uszkodzony plik

Przebudowa puszczona przez `nohup … &` została ubita w połowie i zostawiła `adresflow-story.mp4` oraz `adresflow-full.mp4` z **210 i 115 błędami dekodera** — przy czym `ffprobe` pokazywał poprawny czas trwania, a klatki dawały się wyciągnąć. Walidacja, która to wykrywa:

```bash
ffmpeg -v error -i plik.mp4 -f null - 2>&1 | grep -c "Invalid NAL\|Error splitting"
```

Zero = plik zdrowy. Warto puszczać po każdym renderze wsadowym.

## Etap 10 — spot UGC z gadającą głową i paczka finalna (2026-07-30)

**Powstał `projects/adresflow/final/`** — dziewięć gotowych spotów z `README.md` opisującym, gdzie którego użyć. Buduje go `projects/adresflow/tools/finalize.py`, który kopiuje **tylko pliki bez błędów dekodera** i weryfikuje obecność ścieżki audio.

### Gadająca głowa — pipeline, który zadziałał

1. Postać: `soul_2`, 3:4, 2k (`raw`: jedno zdjęcie agentki, reużywane jako `start_image` we wszystkich klipach — trzyma tożsamość).
2. Dwa klipy `seedance_2_0` (14 s + 13 s), kwestie **po angielsku**, `generate_audio: true`.
3. `dubbing` → `pol` na każdym klipie osobno.
4. Sklejka klipów → `raw-ugc-agentka.mp4` (obraz) + `vo-ugc.mp3` (dźwięk).
5. `story.py ugc` — wykrywa frazy w dubbingowanym audio i wstawia **przebitki narzędzi** dokładnie tam, gdzie agentka je opisuje.

**Kluczowa poprawka w montażu: `SYNC_SHOTS`.** Ujęcia, w których postać mówi, nie mogą być rozciągane ani przyspieszane — rozjechałby się lip-sync. Dla nich skrypt wycina fragment 1:1 z oryginału (`-ss start -t want`, bez `setpts`), zamiast skalować tempo jak przy zwykłych przebitkach.

### Pułapki dubbingu (poza rodzajem gramatycznym)

- **Nazwa marki bywa rozbijana.** „Go to AdresFlow" wyszło raz poprawnie („adres flow"), a raz jako **„A to z flow"**. Pisanie `Adres Flow` jako dwóch słów w oryginale EN daje stabilniejszy wynik.
- **Terminy branżowe tłumaczą się dosłownie.** „home staging" → „kształtowanie domu", „3D floor plan" → „trójwymiarowy plan piętra". Zamiast terminu lepiej opisać efekt („It looks brand new" → „wygląda jak nowy").
- Każdy klip weryfikuj Whisperem przed montażem — dwie z trzech generacji wymagały poprawki.

### Korekta merytoryczna: agent nie remontuje

Ujęcie „ekipa remontowa" (malarz na drabinie, skręcanie mebli) było **nietrafione** — agenci nieruchomości rzadko robią remont, raczej sprzątają i odświeżają przed sesją zdjęciową. Zastąpione przez `raw-sprzatanie.mp4` (wynoszenie pudła, poprawianie poduszek, odsłanianie okien), a narracja spotu `hs` przepisana: „Sprzątanie. Wynoszenie rzeczy. Cały dzień, a zdjęcia i tak słabe."

## Etap 11 — muzyka w krótkich spotach i wybór głosu (2026-07-30)

### `render.py` w ogóle nie obsługiwał podkładu

Poprawki miksu trafiły wcześniej tylko do `story.py`, więc **cztery krótkie spoty nie miały muzyki wcale**. Dodano obsługę z importem wspólnych stałych i `music_offset()` ze `story.py` (jedno źródło prawdy). Poziom podkładu w planszy końcowej wzrósł z −19,1 dB (sam pogłos) na −14,7 dB realnej muzyki.

### Głos: „mało emocji" jest mierzalne

Ekspresja = **zmienność wysokości tonu** + rozrzut głośności między sylabami + LRA. Powstało `projects/adresflow/tools/voice_test.py`, które to liczy.

| Głos | Zmienność tonu | Ekspresja |
|---|---|---|
| Wilder | 99,8 Hz | 8,6 |
| **Harrison ✅** | 46,3 Hz | 7,3 |
| Zane | 53,5 Hz | 6,9 |
| Marcus (poprzedni) | 40,4 Hz | 6,4 |

**Dodanie wykrzykników nie pomaga** — Marcus z emfazą podskoczył z 6,4 na 6,9, czyli w granicach szumu. Płaskość siedzi w barwie głosu, nie w interpunkcji.

Wybrany **Harrison** (`573e5163-59b3-4926-aab1-951ef2985f81`) — Wilder ma żywszą intonację, ale mówi o ~17 % wolniej, co rozdmuchuje długość spotów.

### Zmiana głosu wymusza korektę scenariuszy

Każdy głos pauzuje inaczej, więc **zmienia się liczba wykrytych fraz**: `story` 6 → 7, `hs` i `dz` 5 → 6, `full` bez zmian. `story.py` zatrzymuje się z wypisaniem granic, gdy scenariusz się nie zgadza — wtedy trzeba dodać lub scalić wpisy. Wychodzi to na plus: drobniejszy podział = więcej plansz i lepsza dynamika.

Uwaga: **spot UGC (01) ma głos agentki z dubbingu**, nie lektora — zmiana presetu go nie dotyczy.

### HyperFrames

Plugin `hyperframes@claude-plugins-official` (0.7.82) został zainstalowany 2026-07-30 o 13:05, ale **nie był dostępny w sesji**, która wystartowała wcześniej — lista skilli ładuje się przy starcie. Po restarcie warto sprawdzić, czy `embedded-captions`, `motion-graphics`, `hyperframes-animation` i `hyperframes-keyframes` zastąpią część ręcznej roboty z `projects/adresflow/tools/`.

### Do zweryfikowania przed płatną kampanią

- **899 zł za rzut 3D w branży** to wiedza domenowa właściciela, nie dane z repo — roszczenie porównawcze w reklamie musi być prawdziwe i weryfikowalne, więc trzeba mieć na to źródło (cennik pracowni, oferta, zrzut).
- **9,90 zł za rzut** jest wyższe niż wynik z cennika w repo (6 kr ≈ 5,88 zł), czyli reklama obiecuje drożej niż jest — od strony roszczeń bezpieczne, ale warto świadomie potwierdzić tę kwotę.
- **Rozbieżność w produkcie:** `adresflow-v2/apps/web/src/lib/data.ts:322` mówi „5 kredytów na start", a faktyczny grant to **30** (`signup_credits_30`, migracja z 2026-05-20; potwierdzone w `adresflow-v2 → internal-metrics.repository.ts`). Reklamy używają prawdziwej liczby 30 — wpis w `data.ts` do poprawy.

## Powiązane

- Pipeline produkcyjny: `projects/adresflow/tools/README.md`
- Pamięć: `.ai/memory/higgsfield-mcp-limity.md`
- Materiał źródłowy: `ads/fajny rzut z karkti/` (szkic + 3 rzuty), `ads/rzut 3d 1/` (karta lokalu M10 → 3D z ogródkiem)
