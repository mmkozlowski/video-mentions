# Plan reklam: księga wieczysta, wycena, oferta — „jednym kliknięciem"

**Data:** 2026-07-30
**Status:** ✅ wdrożone (2026-07-30) — spoty `10-ksiega-wieczysta`, `11-wycena-rciwn`,
`12-kreator-oferty` w `projects/adresflow/final/`

> **Jak rozwiązaliśmy główne ryzyko.** Sekcja „Czego brakuje" zakładała, że bez
> nagrań ekranu spoty będą słabsze. Znalazła się trzecia droga: **ekrany produktu
> odtworzone jako HTML i wyrenderowane przez HyperFrames** (`projects/adresflow/screens/`) —
> czytelne UI i poprawne polskie napisy, koszt 0 kredytów, zmiana danych to edycja
> pliku. Nagrania ekranu nie są już potrzebne. Szczegóły i kompromisy:
> [`.ai/decisions/2026-07-30-ekran-produktu-z-html.md`](../decisions/2026-07-30-reklamy-ekran-produktu-z-html.md).
>
> **Zmierzony wynik** (`virality_predictor`, pierwsze 16 s):
> KW hook 37 / sustain 95 · wycena 34 / 92 · oferta 34 / 92. Dla porównania
> wcześniejszy spot narracyjny miał hook 26 — otwarcie bólem proceduralnym
> podniosło hook o ok. 10 punktów bez utraty sustainu.
>
> **Koszt:** 67,5 kr na trzy ujęcia (`seedance_2_0`, 5 s) + ok. 1 kr na lektora.
> Mieści się w szacunku 60–70 kr.

## Czym te trzy funkcje różnią się od dotychczasowych

Dotychczasowe spoty (rzut 3D, home staging, działka) opierały się na **transformacji obrazu** — jest przed, jest po, różnica jest widowiskowa i sama się sprzedaje.

Te trzy funkcje są **ekranowe**: efektem nie jest ładny obraz, tylko dane i dokument. Nie ma czego „morfować". To zmienia konstrukcję spotu:

| | dotychczasowe | te trzy |
|---|---|---|
| Bohater kadru | efekt (render) | **agent i jego czas** |
| Dowód | widać różnicę | **liczba kliknięć / minut** |
| Ryzyko | brak | pokazanie UI, którego nie ma |

**Wniosek: bohaterem musi być ból proceduralny**, nie ładny wynik. Kontrast: dziesięć kroków i pół godziny kontra jedno kliknięcie.

## Co te funkcje robią naprawdę (z repo)

| Funkcja | Fakty | Koszt |
|---|---|---|
| **Księga wieczysta** | portal EKW MS jest za anty-botem Imperva; dane pobieramy przez dostawcę za portem `KsiegaWieczystaProvider`, czas ~30–40 s (`apps/api/src/modules/ksiega-wieczysta`) | — |
| **Wycena** | „Wpisz adres — pobieram realne ceny transakcyjne z rejestru państwowego (RCiWN). Mediana zł/m², rozkład cen i lista transakcji." | **0 kredytów** |
| **Oferta** | kreator 4 kroki: adres + wycena → dane → zdjęcia AI → opis AI + eksport (`OfferWizardPage`) | zależnie od zdjęć |

Dwie z trzech są **darmowe** — to mocny argument, wpisuje się w obecną retorykę „nie mówimy o własnej cenie, prowadzimy do darmowego progu".

## Szkice trzech spotów

Konstrukcja jak w sprawdzonych: **ból → koszt starej metody → jedno kliknięcie → CTA**. Otwarcie zawsze bólem, nie opisem funkcji (zmierzone: ból bije opis o kilkanaście punktów `hook_score`).

### Spot A — Księga wieczysta

> „Znowu przepisujesz numer księgi wieczystej?
> Portal, captcha, cztery działy, przewijanie.
> Tu wklejasz numer. **Masz wszystko na jednym ekranie.**
> Wejdź na AdresFlow i odbierz 30 darmowych kredytów."

Ból jest bardzo konkretny — każdy agent zna przeklikiwanie działów I–IV i wygasające sesje. Wariant hooka do testu A/B: *„Ile razy dziś otwierałeś EKW?"*

### Spot B — Wycena

> „Klient pyta, ile warte jest jego mieszkanie.
> Zgadujesz? Dzwonisz po kolegach?
> Wpisujesz adres. **Realne ceny z aktów notarialnych.**
> Mediana, rozkład, transakcje z okolicy. Za darmo."

Najmocniejsza z trzech — ból jest emocjonalny (agent nie chce wyjść na niekompetentnego), a dowód twardy: **dane z rejestru państwowego, nie z ogłoszeń**. To rozróżnienie warto wyeksponować, bo portale pokazują ceny ofertowe, a my transakcyjne.

### Spot C — Oferta / eksport

> „Oferta w Wordzie. Zdjęcia osobno. Opis pisany od zera.
> Godzina roboty na jedno mieszkanie.
> Cztery kroki — adres, dane, zdjęcia, opis.
> **Gotowa oferta do wysłania.**"

Tu warto pokazać kontrast **objętości pracy**: bałagan plików kontra jeden dokument.

## Czego brakuje — i to jest główne ryzyko

**Nie mamy ani jednego nagrania ekranu produktu.** Wszystkie trzy spoty żyją z pokazania, że coś dzieje się na ekranie w jednym kroku.

**Nie da się tego wygenerować przez AI.** Modele wideo renderują UI jako nieczytelną papkę, a polskie napisy jako bełkot — mamy to zmierzone przy innych ujęciach. Wygenerowany „ekran AdresFlow" byłby fałszywy i widać by to było.

**Potrzebne od Ciebie: trzy nagrania ekranu (screen recording), po 10–15 s każde:**

1. wklejenie numeru KW → wynik na ekranie,
2. wpisanie adresu → mediana i wykres,
3. przejście kreatora oferty → gotowy dokument.

Mogą być z telefonu albo z QuickTime, byle 9:16 lub przycinalne do pionu. Resztę — oprawę, napisy, lektora, muzykę — dorobi istniejący pipeline.

## Czy potrzebny MCP

**Do przebitek „starej metody" — tak, ale niewiele.** Trzy ujęcia po ~20 kr:

| Ujęcie | Do czego |
|---|---|
| agent przy laptopie z portalem, przeciera oczy, stos papierów | Spot A |
| agent z klientem, rozkłada ręce („nie wiem, ile to warte") | Spot B |
| biurko zawalone wydrukami, agent składa ofertę ręcznie | Spot C |

**Reszta bez MCP:** ujęcia agenta, grafika, mieszkania i tabletu już mamy w `projects/adresflow/assets/shots/raw-*.mp4`; lektor to ~0,3 kr za spot; montaż, napisy i muzyka są darmowe.

**Szacunek: ~60–70 kredytów na trzy spoty** (przy stanie 291). Gdyby budżet miał być mniejszy, Spot B i C mogą wykorzystać istniejące ujęcia `raw-agent` i `raw-grafik` — wtedy koszt spada do ~20 kr.

## Kolejność, którą proponuję

1. **Wycena** — najmocniejszy ból i darmowa funkcja, najłatwiej obronić przekaz.
2. **Księga wieczysta** — ból najbardziej konkretny, ale wymaga dobrego nagrania ekranu.
3. **Oferta** — najtrudniejsza wizualnie, bo „dokument" słabo się pokazuje w pionie.

## Do decyzji — rozstrzygnięte 2026-07-30

- ~~Czy dostarczysz nagrania ekranu?~~ → **nie są potrzebne**, ekrany renderujemy z HTML.
- ~~Czy możemy powiedzieć „ceny z aktów notarialnych, nie z ogłoszeń"?~~ → **tak**, zatwierdzone; jest w spocie 11 jako dwie osobne frazy i jako pigułka na ekranie.
- ~~Czy „jednym kliknięciem" jest uczciwe przy KW?~~ → **nie**; używamy **„jedno wklejenie zamiast dziesięciu kliknięć"**, a spot pokazuje pasek pobierania z podpisem „Pobieram z portalu EKW…".

## Zostało otwarte

- **Nie ma eksportu do PDF.** Zadanie mówiło „oferta PDF jednym kliknięciem", ale
  krok 4 kreatora (`adresflow-v2/apps/web/src/pages/OfferWizardPage.tsx:731-763`) daje *Kopiuj*,
  *Pobierz .txt*, *Podgląd strony*, *Pobierz stronę HTML*. Spot 12 mówi więc
  **„gotowe ogłoszenie do wysłania"**. Do decyzji: dorobić eksport PDF w produkcie
  (wtedy copy i kompozycja `projects/adresflow/screens/oferta/` do aktualizacji) czy zostawić.
- **„899 zł u grafika"** nadal wymaga źródła przed płatną kampanią (dotyczy spotów 02, 08).
- **`adresflow-v2/apps/web/src/lib/data.ts:322`** wciąż mówi „5 kredytów" zamiast 30 — bug w produkcie,
  niezależny od reklam, ale spoty obiecują 30.
- **Spoty 01–09 zbudowano przed fixem klatkażu** w `story.py` (miały ok. 0,6 s
  naddatku obrazu nad lektorem). Warto je przebudować przy najbliższej zmianie.

## Powiązane

- Pipeline i narzędzia: `projects/adresflow/tools/README.md`
- Historia decyzji: `projects/adresflow/ai/decisions/2026-07-30-reklamy-higgsfield-rzut-3d.md`
- Pamięć: `.ai/memory/copy-i-hook.md`, `.ai/memory/realia-agenta-nieruchomosci.md`
