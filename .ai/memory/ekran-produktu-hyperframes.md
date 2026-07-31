---
name: ekran-produktu-hyperframes
description: Ekrany produktu w reklamach renderujemy z HTML przez HyperFrames (projects/adresflow/screens/) — modele wideo robią z UI papkę, a z polskich napisów bełkot
metadata:
  type: project
---

Ekran AdresFlow w spotach (KW, wycena, kreator oferty — `projects/adresflow/final/10..12`) to
**kompozycja HTML renderowana do wideo przez HyperFrames**, projekty w
`projects/adresflow/screens/{kw,wycena,oferta}/`. Wyjście: `projects/adresflow/build/screen-*.mp4`, wpięte do
`SHOTS` w `story.py` jako `ekran-kw` / `ekran-wyc` / `ekran-of`.

**Nie generuj ekranu produktu modelem wideo** — UI wychodzi nieczytelną papką,
a polskie napisy bełkotem. Nie czekaj też na nagranie ekranu: HTML jest wierniejszy
i zmiana danych na ekranie kosztuje 0 kredytów zamiast ponownej generacji.

Tokeny w `projects/adresflow/screens/assets/app.css` są przeniesione z
`adresflow-v2/apps/web/src/styles/legacy.css`, layouty odwzorowują `KsiegaWieczystaCard`,
`StatCard` + `Histogram` (`WycenaScreen`) i stepper z `OfferWizardPage`.

**Cztery rzeczy, które odrzuca `npx hyperframes check`** (i nie są oczywiste):

1. **`--text-3` z aplikacji (`#6b7a92`) nie przechodzi kontrastu** — 3,77:1 przy
   wymaganych 4,5:1 na `--elevated`. W kompozycjach jest `#8593ab`.
2. **Przewijanie treści pod paskiem aplikacji = `text_occluded`** — bramka liczy
   nachodzenie na prostokątach i ignoruje `overflow: hidden`. Albo pasek jedzie
   razem z treścią, albo chrome stoi, a rusza się sam element.
3. **Pozycję wyjściową ustawiaj `tl.set(sel, {y}, 0)`, nie CSS-owym `transform`** —
   inaczej `gsap_css_transform_conflict` i element skacze na starcie.
4. **Ścieżki do assetów muszą być root-relative** (`assets/…`), `../assets/…`
   działa w renderze, ale 404-uje w podglądzie Studio. Stąd trzy osobne projekty
   z własną kopią `assets/`, a nie jeden wspólny katalog.

**Osobno: `compose()` w `story.py` produkował VFR** — obraz wychodził dłuższy od
lektora (26,5 s przy 20,3 s głosu), napisy rozjeżdżały się ze słowami, endcard
puchł z 3,2 s do 7 s. Naprawione przez `-r 30 -fps_mode cfr -t {total}`.
**Spoty 01–09 zbudowano jeszcze przed fixem** (miały ok. 0,6 s naddatku) — przy
najbliższej zmianie któregoś warto je przebudować.

**Why:** bloker planu brzmiał „nie mamy nagrań ekranu i nie da się ich
wygenerować" — a trzecia droga (HTML → wideo) była dostępna i lepsza od obu.
Bramki HyperFrames odrzucają rzeczy, które w aplikacji są poprawne, więc bez tej
listy każdy nowy ekran zaczyna się od tych samych czterech błędów.

**How to apply:** **zanim zbudujesz nowy ekran, przeczytaj `projects/adresflow/screens/README.md`** —
jest tam pętla `check → snapshot → render`, skala typografii pod kadr 9:16,
cztery wzorce choreografii (wklejenie zamiast pisania, widoczne czekanie, licznik
na proxy, kroki kreatora na `translateX`) i zasady dopasowania długości klipu do
fraz lektora. Nowy ekran zaczynaj od `cp -R kw nazwa-ekranu`.
Decyzja i kompromisy: `.ai/decisions/2026-07-30-ekran-produktu-z-html.md`.
Pipeline: [[pipeline-montazu]], copy: [[copy-i-hook]],
limity API: [[higgsfield-mcp-limity]].
