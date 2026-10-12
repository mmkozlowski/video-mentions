# Starsze odcinki kanału w bibliotece: rolki, zajawki i pełne odcinki z pięciu plików

**Data:** 2026-10-11
**Status:** ✅ wdrożone (render nocny 11→12.10)

Rozszerza: [Baza klipów](2026-10-08-baza-klipow-z-sesji-nagraniowej.md),
[Opakowanie klipów](2026-10-09-opakowanie-klipow-trzy-formaty-dwie-palety.md).

## Problem

Mateusz dorzucił siedem starszych nagrań z `~/Youtube Projects` (S11 Claude vs Open Mercato,
S12 Jak składam moduł, S-10 Po co Open Mercato + dogrywki) z prośbą: „co z nich idzie
wyciągnąć — rolki, shorty, zapowiedzi, pełnometrażowe filmy”. Pliki są w tym samym
układzie co sesja 8.10 (720p, zielone polo), ale:

- **dwa mają minuty rozmytego obrazu** (S11 7:19–13:39, `budowanie - modulu.mov` od 8:00),
- **S12 istnieje w dwóch plikach** (część 1 w „budowanie”, część 2 w „dogrywce”),
- S-10 jest już opublikowany jako odcinek z wtopionymi grafikami.

## Decyzja

1. **Pięć nowych źródeł w `sources.py`** (ścieżki w `YT_DIR`), środek twarzy zmierzony per plik.
   Stary S11 i stary S12 zostają poza biblioteką — mają czystsze odpowiedniki.
2. **S12 jako składanka** `ep-module` = `ep-module-1` (budowanie, tylko ostra część)
   + `ep-module-2` (dogrywka) w `compile_episode.py`. Łączenie zakrywa plansza „Rozmowa → specyfikacja”.
3. **S-10 tnę z surówki** (`Surowy/01 - czym jest OM.mov`), nie z gotowego odcinka —
   nasze grafiki nie mogą lądować na wtopionych.
4. **Wynik:** 27 rolek 9:16 (7 vibe, 10 moduł, 11 S-10 — w tym hook „Excel działa”
   z dogrywki), 2 odcinki 16:9 (7:52 i 8:03) z rozdziałami, 3 zajawki 4:5 (składanki dwóch–trzech
   rolek, ~75–90 s). Rolki tylko w formacie `reels` — te same pliki idą na Shorts i IG.
5. **12 nowych makiet** w `mockups.py` pod treść tych odcinków: dane w przeglądarce
   (`storage`), moduły, które się sypią (`deps`), warstwy uprawnień (`layers`), droga kartki
   (`route`), specyfikacja (`spec`), słownik pojęć (`glossary`), checklista (`checklist`),
   kopie Excela (`copies`), historia zmian (`history`), pytania z warsztatu (`questions`),
   moduły Open Mercato (`modules`), repozytorium (`repo`). W pionie powiększane `zoom` ×1,3.
6. Galeria: osobna strona `final/samples/starsze-odcinki.html` (seria = zajawka → odcinek → rolki).

## Pułapki

- **Rozmycie nie wychodzi w transkrypcji** — pomiar `edgedetect` przed EDL
  (`.ai/memory/sprawdz-ostrosc-zrodla`).
- **Whisper przykrył drugi dubel jednym słowem** (`ch-module-3`, „…w głowie właściciela” ×2):
  granica z sygnału `(220.6, 250.0, None, 249.95)`; wykrył to `verify.py`.
- **Prefiks id w `package.py`**: `ep-module` łapał `ep-module-1` — dokładne id ma teraz pierwszeństwo.
- Napisy: Whisper pisze „kodeks”, „cloud”, „cash”, „Europy” (urlopy) — dopisane do `caption-fixes.json`.
  Zostały znane potknięcia słowne w samych nagraniach (np. „a i też pisze aplikację” = „AI też”,
  „w 90-90%” = 99%) — w napisach tak, jak powiedziane.
- `ch-om-5` wymienia z nazwy ERP Symfonia („koszmar”) — przed płatną promocją rozważ wersję bez nazwy.

## Dopisek 12.10 — poprawki z czasem i historia zmian

Pierwsza runda uwag Mateusza (13 punktów, ep-vibecoding + ep-doram) zrobiona przez `locate.py`
i granice z sygnału; kontrola transkrypcją znalazła przy tym jeszcze jeden falstart (3:24).
Od teraz każda zmiana filmu ląduje w `data/video-history.json` (`tools/history.py`), a galeria
pokazuje historię pod filmem. Styl: przekreślenie `strike` leży na napisie (nie na planszy),
`slam` w 16:9 o 30% mniejszy i bez łamania linii.

## Dopisek 12.10 — plansza filmów i ocena przewidywanej skuteczności

Plansza (artefakt Cd35tVFfQoR53XmTEkYDgW, baza `videos` / `notes` / `meta/plan`) zbiera wszystkie 66 filmów:
sekcje decyzji (Do oceny → Publikujemy / Test w reklamie / Do poprawki / Odrzucone), podgląd pierwszych
15 s (assets), uwagi z czasem od zespołu i agencji, wspólny plan pracy. Ocena z `tools/scorecard.py`:
hook 30 + otwarcie 15 + CTA 15 + przekaz 10 + konkret 10 + długość 10 + dynamika 10, klasy A/B/C tercylami.
**To przewidywanie, nie konwersja** — po publikacji dopisujemy prawdziwe wyniki i kalibrujemy wagi.

Higgsfield Virality Predictor (`tools/predictor_fetch.py`): darmowy, max 16 s, 2 zadania naraz na planie
Plus; każdy plik trzeba wgrać przez podpisany link (ręczne przepisywanie — dlatego liczony tylko dla
wariantów A/B). Pułapka: dwa warianty ad-11 różniące się tylko hasłem na start dostały identyczny wynik
(50/34/100) — model reaguje na obraz i dźwięk, nie na treść napisu, więc do oceny hasła się nie nadaje.

Tempo mowy (12.10): 4,2–4,9 sylaby/s czystej mowy we wszystkich nagraniach (swobodna polszczyzna ~5,5–6).
Próbki 1,05× i 1,08× z korektą koloru i dźwięku w `final/samples/postprodukcja/` — decyzja Mateusza.

Plansza lokalna (12.10, Mateusz: „wolę to mieć na localhost”): `python3 tools/board_server.py` →
http://localhost:8765, pełne filmy z `final/samples` (Range — da się przewijać odcinki), decyzje i uwagi
w `data/board-state.json` (w repo, Claude czyta uwagi wprost z pliku), historia zmian filmu na karcie,
przycisk „Wstaw czas” bierze moment z odtwarzacza. `--lan` udostępnia planszę w sieci lokalnej.
Artefakt Cd35tVFfQoR53XmTEkYDgW zostaje jako wersja do wysłania poza biuro (tylko 15-sekundowe podglądy).

Panel (12.10, wieczór): plansza przeniesiona do FlowBiz Studio, zakładka „Filmy” — `tools/export_studio.py` pisze
`studio-index.json` + `exports/studio-manifest.json`, studio czyta je i strumieniuje wideo; decyzje w
`flowbiz-ads-studio/data/videos/`. `board_server.py` wyłączony (zapas). ADR: `flowbiz-ads-studio/ai/decisions/2026-10-12-zakladka-filmy-zrodla-z-innych-repo.md`.

Kolor (12.10): Mateusz wybrał poziom „średnio” z czterech próbek (`final/samples/postprodukcja/kolor-*.mp4`) —
`cut.py` `COLOR_GRADE`, na samym nagraniu (nie na grafikach). Wchodzi przy przecięciu całej biblioteki razem z tempem
(decyzja o tempie: otwarta), żeby nie renderować 66 filmów dwa razy.
