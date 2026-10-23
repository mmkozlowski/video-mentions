# PPWR Smart — styl wideo: grafiki, głos, animacja

**Data:** 2026-10-20 · **Wzorzec:** film TAGO „chaos → system” (spotkanie 21.10.2026), zaakceptowany przez
Mateusza („super to wyszło”). Każdy kolejny film PPWR Smart startuje od tego dokumentu.

## 1. Narracja — szkielet filmu

| Akt | Czas | Co widać | Rola |
|---|---|---|---|
| Chaos | ~40 s, 6 scen | ożywione ilustracje AI, etykieta „Dziś, bez systemu” (czerwona) | ból klienta jego językiem: skrzynka, składniki, poziomy opakowań, cicha zmiana u dostawcy, obchód miesięczny, wiedza w jednej głowie |
| Plansza | ~3 s | ciemna zieleń, złoty tekst | „A przepisów będzie przybywać.” — bez daty, bez obietnicy |
| Przejście | ~8 s | lejek → szuflady z ✓, etykieta „Z PPWR Smart” (złota) | lektor: „A teraz zobaczmy, jak to wygląda z PPWR Smart.” |
| System | ~40 s, 5 scen | **prawdziwe nagranie prototypu**, dwa okna (klient + dostawca), kursor | każda scena odpowiada na jedną scenę chaosu |
| Finał | ~5 s + ~7 s | ilustracja „system pilnuje” + plansza CTA z logo PPWRsmart | CTA = pilotaż z pomiarem, nie obietnica liczby |

**Twarde reguły treści**
- Liczby w filmie wyłącznie twarde, z rozmów z klientem (u TAGO: 40 dostawców, 626 komponentów, ok. 10
  elementów na wyrób, 3 poziomy, 2 ścieżki marki). Zero szacunków czasu i etatów, zero efektów z innych
  wdrożeń bez potwierdzenia ich właściciela.
- Część „system” nigdy nie jest generowana przez AI — tylko ekrany prawdziwego produktu/prototypu
  (por. `.ai/decisions/2026-07-30-ekran-produktu-z-html.md`). AI udaje wyłącznie świat klienta.
- W klatkach AI żadnych logo i opakowań klienta — opakowania generyczne.
- Do klienta zwracamy się „Państwo”. Funkcje spoza zakresu oferowanego etapu (np. raport dla zarządu
  = „Kierunek rozwoju”) nie mogą w lektorze brzmieć jak część etapu 1.
- Publikacja poza spotkaniem 1:1 (reklama, social) → oznaczenie treści AI, `.ai/memory/oznaczanie-tresci-ai.md`.

## 2. Grafiki (klatki AI)

- **Styl:** płaska ilustracja wektorowa, edytorska, bez gradientów fotograficznych; kremowe tło, sylwetki
  ludzi uproszczone, sporo „rekwizytów” biurowych i opakowaniowych (koperty, segregatory, rolki folii,
  kartony, palety, deklaracje z pieczątką).
- **Paleta:** ciemna zieleń `#0c3b2e` (i `#082a21`), złoto `#c8a55a`, krem `#f5f0e7`; czerwień tylko
  jako sygnał problemu (badge, pęknięcie pieczątki, pytajnik).
- **Napisy w kadrze:** krótkie, po polsku, wielkimi literami (DEKLARACJA ZGODNOŚCI, MARKA WŁASNA,
  ZBIORCZE (12 SZT.)). GPT Image trzyma je dobrze, ale zawsze sprawdź literówki i zdublowane numery.
- **Generator:** Higgsfield `gpt_image_2_5`, high, 2k, 16:9 (~4 kr. z poprawkami za klatkę).
- **Ludzie:** biali, polskie realia (`.ai/memory/higgsfield-generacja-przebitek.md`).
- Szablon promptu (zrekonstruowany z gotowych klatek — oryginalne prompty nie zostały zapisane):
  > Flat vector editorial illustration, 16:9. Cream background (#f5f0e7), deep green (#0c3b2e) and muted
  > gold (#c8a55a) palette, red only for warning accents. <scena>. Generic unbranded packaging.
  > Short Polish labels in uppercase: "<NAPIS>". Clean shapes, no photorealism, no gradients.
- Źródła: `assets/frames/01–08`.

## 3. Animacja

- **Ilustracje ożywiamy w Kling 3.0 Pro** (`kling3_0`, `mode: pro`, `sound: off`, 5 s, przejście 7 s,
  `start_image` = klatka), ~8,75 kr./klip. Szablon promptu ruchu:
  > Flat vector illustration comes to life. <co się rusza — konkretnie: koperty wysypują się z monitora,
  > telefony dzwonią, karteczki spadają, zegar przyspiesza, pieczątka pęka>. Slow camera push-in.
  > Keep the exact flat illustration style, colors and composition. No new text, no cuts.
  Wszystkie 8 klipów przeszło za pierwszym razem, bez artefaktów w tekście.
- Klip dopasowany do długości sceny przez `setpts` + `minterpolate=mi_mode=mci` (zwolnienie do ~0,6×
  wygląda płynnie na płaskiej ilustracji).
- **Ekran produktu = nagranie prawdziwej pracy**, nie zrzuty z najazdem (pierwsza wersja ze zrzutami
  została odrzucona: „to nie jest animacja, tylko slajdy”). Dwa okna obok siebie (klient | dostawca),
  ten sam stan aplikacji, rysowany kursor ze złotym „ripple” przy kliknięciu, pisanie z klawiatury
  litera po literze. Skrypt: `tools/record-prototype.js`.
- Przybliżenie na aktywne okno 1,0 → 1,18 (nie więcej — tekst UI musi zostać w kadrze).
- Przejścia: przenikanie 0,5 s; koniec filmu zejście do czerni 0,8 s.
- **Napisy:** Helvetica Neue Bold. Na ilustracjach dolna tercja 56 px na gradiencie zieleni, liczby
  złotem; etykieta-pigułka w lewym górnym rogu (czerwona „Dziś, bez systemu” / złota „Z PPWR Smart”).
  Na nagraniu pasek 150 px (zieleń 94 %) z krokiem „PPWR SMART · n” złotem i zdaniem kremowym 44 px.

## 4. Głos

- **ElevenLabs v4** przez Higgsfield (`elevenlabs_v4`, parametr `dialogue`), głos **Callum**
  `858499d9-fef5-40e1-bc29-b4dc661dc283` (preset). Spokojny, męski, rzeczowy.
- Nazwę marki zapisuj fonetycznie **„pe-pe-wu-er smart”**, w środku zdania, nigdy na jego początku. Bez tego TTS czyta PPWR po angielsku, a stary zapis „Pe Pe Wu Er” daje „PPUR”. Szczegóły i test Whisperem: `.ai/memory/wymowa-ppwr-lektor.md` (23.10.2026).
- Zdania krótkie, 1–2 na scenę; scena trwa = długość kwestii + 0,6 s; kwestia startuje 0,3 s po
  początku sceny. Głośność końcowa `loudnorm I=-16, TP=-1.5`.
- ⚠️ Film TAGO ma 15 kwestii generowanych **osobno** (żeby łatwo ciąć sceny pod spotkanie). To ryzyko
  dryfu barwy opisane w `.ai/memory/audio-lektor-muzyka.md` — tu w odsłuchu zaakceptowane, ale przy
  filmie publicznym generuj jeden plik i tnij po `silencedetect`.
- Bez muzyki (spotkanie na żywo, lektor + prowadzący). Do wersji reklamowej: ciche tło pod głosem.

## 5. Koszt wzorcowego filmu (100 s)

8 klatek GPT Image ~33 kr. + 8 klipów Kling ~75 kr. + 16 kwestii lektora ~18 kr. ≈ **126 kredytów**;
montaż i render lokalnie (~6 min na M-serii).
