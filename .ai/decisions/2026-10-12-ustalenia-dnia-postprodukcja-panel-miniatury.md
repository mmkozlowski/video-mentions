# Ustalenia z 12.10.2026 — postprodukcja, panel filmów, miniatury

**Data:** 2026-10-12
**Status:** ✅ zapisane · częściowo do wykonania (render całości, szablon miniatur)

Zbiorcza lista decyzji Mateusza z jednego dnia pracy — każda ma szczegóły w miejscu wskazanym obok.

## Decyzje

| Temat | Decyzja | Gdzie szczegóły |
|---|---|---|
| Podział wiedzy | Trzy repo osobno: montaż tu, marka w `flowbiz-automation-unlocked`, panel w `flowbiz-ads-studio` | [ADR podziału](2026-10-12-podzial-wiedzy-montaz-marka-panel.md) |
| Wytyczne montażu | Jeden dokument dla agencji i dla Claude, oddzielnie od brandbooka | `WYTYCZNE-MONTAZU.md` |
| Układy | Katalog przejść, tekstów i przebitek z prawdziwymi klatkami | `KATALOG-UKLADOW.md` |
| Połączenia | Każdy projekt ma w README sekcję „Połączenia z repo” | `projects/*/README.md` |
| Panel filmów | Zakładka „Filmy” w studiu; studio czyta `studio-index.json` → spisy projektów, nic nie kopiuje; decyzje i uwagi w `flowbiz-ads-studio/data/videos/` | `flowbiz-ads-studio/ai/decisions/2026-10-12-zakladka-filmy-zrodla-z-innych-repo.md` |
| YouTube w studiu | Osobna zakładka połączona z Filmami — publikacja odcinka w jego karcie, bogatsze pola, lista „gotowe do publikacji?” | jw. |
| Dostęp | Studio przez Tailscale (tailnet only), agencja po zaproszeniu do tailnetu | `flowbiz-ads-studio/README.md` |
| Kolor | Poziom **„średnio”** (kontrast +10%, nasycenie +18%, lekkie wyostrzenie), tylko na nagraniu, nie na grafikach | `cut.py` `COLOR_GRADE`, wytyczne §9 |
| Tempo mowy | ✅ **1,05×** w rolkach, reklamach i zajawkach; odcinki 16:9 1,00× (rozdziały w opisach YouTube). Nałożone w `package.py` per format, nie w cięciu — `ep-8-wdrozen` jest sklejony z klipów rozdziałów | próbki `final/samples/postprodukcja/` |
| Miniatury — źródła wiedzy | Bez zewnętrznych skilli „noname”; opieramy się na danych z sieci, własnych wytycznych i wzorze z Claude Design | wytyczne §13 |
| Miniatury — konstrukcja | Z przeglądu 4 kanałów bierzemy tylko konstrukcję: 3 elementy (twarz + 2–4 linie z podświetloną liczbą + jeden rekwizyt), stały szablon kanału | wytyczne §13, `~/Youtube Projects/inspiracje/miniatury-kanaly-2026-10-12/` |
| Miniatury — styl | Klimat reklam i wzoru „Miniatura VS - AI-first” (zieleń + mięta, białe/zielone pole hasła) | wytyczne §13 |
| Zdjęcia twarzy | `~/Youtube Projects/Mój ryj` zatwierdzone | wytyczne §13 |
| Oznaczanie AI na miniaturach | Bez znaczka na miniaturze; dopisek w stopce opisu „Miniatura i część ujęć wygenerowane z pomocą AI” | wytyczne §13 |

## Do zrobienia

- ✅ Noc 12→13.10: przecięcie z kolorem i render 66 filmów (kolor + tempo + muzyka), `verify.py`, historia, `export_studio.py`.
- Szablon miniatury + przycisk „Generuj miniatury” w karcie odcinka; miniatury 8 odcinków.
  Plik HTML z Claude Design („Miniatura VS - AI-first.html”) pozwoli odwzorować 1:1.
- `brand.json` w repo strony zamiast palet wpisanych w `package.py`.
- Tagi, przypięte komentarze i daty publikacji 8 odcinków (lista kontrolna w studiu).
- Storyboard `ad-33-g1`: kotwica „Programista” nie istnieje po przecięciu.
