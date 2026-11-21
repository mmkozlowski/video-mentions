# „System z klocków" 2027 — trzy warianty

**Data:** 2026-11-06 · **Status:** szkice do wyboru (rolki tekstowe), animacja i nagranie później
**Pełny scenariusz z gadaną głową (wariant A):** [`SCENARIUSZ.md`](SCENARIUSZ.md)
**Nowa scenka do filmu:** [`../../screens/block-tower/SPEC.md`](../../screens/block-tower/SPEC.md)

Na razie każdy wariant istnieje jako **rolka tekstowa 9:16** (~22 s): grafika z GPT na pełny kadr,
jedno zdanie naraz, plansza końcowa z dużym logo i jednym pytaniem. Służy do wyboru kierunku.
Docelowo: Mateusz na kamerze + animowana wieża z HTML (`block-tower`).

| Wariant | Oś | Grafiki (GPT) | Rolka tekstowa | CTA |
|---|---|---|---|---|
| **A — Sprzeczność** | kiedyś klocek = problem (nie gada z poprzednim) → 2027: składaj z klocków, ale na fundamencie. Jedyna liczba: szwalnia 40 → 5–10 min | `a1-tower-collapsing`, `a2-foundation`, `a3-tower-on-foundation` | [text-reel-A-contradiction.mp4](https://macbook-pro-mateusz.taild4f545.ts.net/pliki/flowbiz-klocki-2027/text-reel-A-contradiction.mp4) | „Ile systemów masz dziś w firmie?" |
| **B — Topowe narzędzia i tak wybuchają** | wątek z notatki Mateusza: bierzesz najlepsze narzędzia, każde świetne, razem wybucha. Winny nie jest klocek, tylko brak fundamentu | `b1-premium-stack`, `b2-explosion`, `b3-reassembled` | [text-reel-B-top-tools-explode.mp4](https://macbook-pro-mateusz.taild4f545.ts.net/pliki/flowbiz-klocki-2027/text-reel-B-top-tools-explode.mp4) | „Ile narzędzi spinasz dziś ręcznie?" |
| **C — Szczera granica** | karta „workflow-klocki": regułę wyklikasz z klocków i działa od ręki — aż naklikasz za dużo. Proste wyklikujesz, złożone schodzi do kodu, ten sam fundament | `c1-simple-flow`, `c2-tangled-mess`, `c3-code-floor` | [text-reel-C-honest-limit.mp4](https://macbook-pro-mateusz.taild4f545.ts.net/pliki/flowbiz-klocki-2027/text-reel-C-honest-limit.mp4) | „Gdzie u Ciebie kończą się klocki?" |

Linki działają tylko w tailnecie. Pliki MP4 leżą poza gitem (`projects/flowbiz/build/`), odtwarzalne jednym poleceniem.

**Rekomendacja:** A jako główna rolka (zawiera całą sprzeczność i jedyną liczbę), B jako krótka
reklama na zimny ruch (najmocniejszy ruch w 1. s, ból zamiast opisu), C jako post do lejka
„consideration" dla tych, którzy już znają no-code — jest najbardziej w głosie anty-fanboy.

## Oznaczenie AI — wraca

Grafiki z GPT Image to **treść generowana AI** (art. 50 ust. 4 AI Act). Każda rolka tekstowa ma
znak „Grafiki wygenerowane z pomocą AI" u góry przez pierwsze ~4 s (y 250, pod strefą zakazaną),
a przy publikacji trzeba **ręcznie** włączyć przełącznik AI na platformie (materiał nie ma C2PA —
pamięć `oznaczanie-tresci-ai`). Docelowa wersja z wieżą z HTML i nagraniem Mateusza oznaczenia nie potrzebuje.

## Twarde zasady treści — sprawdzone

- Jedyna liczba: 40 min → 5–10 min (tylko wariant A, z „przygotowanie jednej oferty" i „Szwalnia").
  „2027" to rok, nie wynik. Pozostałe warianty bez liczb.
- Żadnych klientów: anegdota ze spotkania z karty vaulta nie weszła (prawdziwa klientka).
- Żadnych nazw ani logotypów narzędzi w grafikach — prompt zabrania tekstu i znaków, obejrzane.
- Po polsku: cały tekst nakładany w HTML (GPT psuje polskie znaki, więc obrazy są bez tekstu).

## Do decyzji

1. **Który wariant** idzie dalej do nagrania i animacji (albo dwa: główna rolka + reklama).
2. **Fundament w `a2` ma okrągłe wypustki, kojarzy się z LEGO.** W szkicu to nie problem; do
   publikacji płatnej lepiej przegenerować z prostokątnymi zaczepami (spec `block-tower` już je ma prostokątne).
3. **Nazwy narzędzi w wariancie B / fazie „przed"** — „Brix" i „RP" z notatki Mateusza wciąż
   nierozszyfrowane. Grafiki B celowo pokazują drogie materiały zamiast nazw, więc nie czekają na odpowiedź.

## Przebudowa

```bash
cd projects/flowbiz/reels/blocks-2027
./gpt/generate.sh b2-explosion          # przegeneruj grafikę (usuń najpierw stary .png); Codex image_gen
./text-reels/render.sh                  # wszystkie rolki → projects/flowbiz/build/text-reel-*.mp4
./text-reels/render.sh A-contradiction  # jedna
```

Teksty i czasy zdań: `text-reels/variants.json` (zmiana tekstu = 0 generacji, ~15 s renderu).
Szablon: `text-reels/template.html`. Prompty grafik: `gpt/generate.sh`.
