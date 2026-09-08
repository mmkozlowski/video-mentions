---
name: shorty-studyjne-vs-reelsy-ig
description: Dwa reżimy pionowych shortów — surówka z telefonu (autentyczność) i materiał studyjny z odcinka (polish + brand odcinka); nie przenosić reguł jednego na drugi
metadata:
  type: feedback
---

Uwaga Mateusza przy shortach z odcinka YouTube (2026-08-25): „shorty te studyjne
to są zupełnie co innego niż te reelsy z Instagrama". W repo żyją DWA reżimy
pionowych shortów i mają OSOBNE reguły:

| | `projects/shorts IG` (telefon) | shorty z odcinka (studio) |
|---|---|---|
| kryterium | autentyczność — potknięcia i oddechy zostają | polish — materiał już zmontowany, doszlifowany |
| typografia warstw | Poppins | **DM Sans** — font grafik odcinka (system animacji FlowBiz) |
| cięcie pauz | progi ciszy per plik, łagodne | brak — pauzy wyciął montaż odcinka |
| grafika | plakietki/plansze proste, „domowe" | plansze spójne z wypalonymi grafikami odcinka (paleta ink/amber, karty #0D0D0B) |
| dynamika | przebitki z surówki | statyczne punch-iny (WIDE/CLOSE/TIGHT) przełączane na początkach zdań |

## Uwagi Mateusza z odbioru pierwszej wersji (2026-08-25) — reguły stałe

1. **Hook = cold-open, nie pas równoległy do napisów.** Pytanie-hook idzie na
   rozmytym/przyciemnionym kadrze ZANIM zacznie się mowa (~1,3 s), potem obraz
   „wyostrza się" w ujęcie. Tytuł wyświetlany równolegle z napisami w tej samej
   strefie „się zlewa" — tak nie może być. Wzór: otwarcie s4 (blur + pytanie
   przed mową).
2. **Napisy: jedna podkładka na całe okno, interlinia ≥ 102 przy foncie 66.**
   Osobne plate'y per linia przy interlinii 88 nachodzą na siebie — okno
   wygląda na „sklejone i nierówne".
3. **„ai" pisz „AI".** Whisper potrafi rozbić „AI też…" na „a i też…" —
   sklejka tokenów, nie tylko FIXES.
4. **Dynamika > spokój.** Stemple kinetyczne (duże hasła w różnych miejscach,
   rozmiarach, z rotacją i wejściem slide+fade), pionowe animacje, tempo
   całości +1% (setpts/atempo, przed loudnorm). „Jest nudno" = za mało
   zdarzeń na ekranie, nie za wolna mowa.
5. **Ekran/screencast NIGDY w pionowym cropie** — widać pasek strony i „mało
   widać". Pełny kadr 16:9 na całą szerokość + blur-fill z tego samego ujęcia
   (czysty crop 83% zdejmuje ramki). Dotyczy każdego spanu, gdzie odcinek
   pokazuje ekran.

**Why:** reguły z `.ai/memory/autentycznosc-bije-gladkosc` brzmią jak uniwersalne,
a są reżimowe — przeniesione na materiał studyjny dają efekt „taniości" zamiast
wiarygodności; w drugą stronę polish zabija autentyczność surówki.

**How to apply:** przed montażem pionowego shorta ustal źródło: telefon →
reguły `projects/shorts IG/README.md`; odcinek studyjny →
`projects/youtube/shorts/*/README.md` (zoomy, DM Sans, pionowe przebudowy
wypalonych plansz). Mechanika okien napisów (czasy słów, aktywne słowo,
kryjąca podkładka) jest wspólna dla obu. Powiązane:
[[autentycznosc-bije-gladkosc]], [[copy-i-hook]].
