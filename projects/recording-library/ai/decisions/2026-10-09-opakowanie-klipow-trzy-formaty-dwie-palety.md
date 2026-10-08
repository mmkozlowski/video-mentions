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
