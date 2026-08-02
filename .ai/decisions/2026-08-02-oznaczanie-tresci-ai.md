# Oznaczanie treści AI w spotach — trzy warstwy, znak tylko na starcie

**Data:** 2026-08-02
**Status:** ✅ wdrożone — wszystkie spoty w `projects/adresflow/final/`

## Podstawa

**Art. 50 ust. 4 AI Act** (rozporządzenie 2024/1689) stosowany od **2 sierpnia
2026 r.**: podmiot stosujący system AI, który generuje lub modyfikuje obraz,
dźwięk albo wideo wyglądające na autentyczne, **ujawnia, że treść została
sztucznie wygenerowana lub zmanipulowana**.

**Digital Omnibus tego nie przesunął.** Odroczono obowiązki dla systemów
wysokiego ryzyka (Aneks III → grudzień 2027, Aneks I → sierpień 2028) oraz
maszynowy watermarking z art. 50 ust. 2 dla systemów obecnych na rynku
2 sierpnia 2026 (→ 2 grudnia 2026). Sam art. 50 ust. 4 wszedł zgodnie z planem.

**Kto ma jaki obowiązek:**

| | Kto | Co |
|---|---|---|
| art. 50 ust. 2 | **dostawca** modelu (Higgsfield, ElevenLabs) | znakowanie maszynowe wyjścia |
| art. 50 ust. 4 | **podmiot stosujący** — czyli my | ujawnienie odbiorcy, że treść jest sztuczna |

Kara: do 15 mln EUR albo 3 % światowego obrotu.

## Ustalenie, które zmieniło plan

**Materiał z Higgsfielda przychodzi bez metadanych C2PA.** Sprawdzone `ffprobe`
na surowym `raw-kw-portal.mp4`: tylko standardowe tagi `major_brand`,
`encoder`. Żadnych Content Credentials.

Konsekwencja: **platformy nie oznaczą naszych spotów automatycznie.** TikTok,
Meta i YouTube wykrywają AI m.in. po C2PA i wtedy same doklejają etykietę —
u nas nie ma czego wykryć. Nie da się więc powiedzieć „platforma to załatwi";
przełącznik trzeba włączyć ręcznie przy każdej publikacji.

Do tego montaż w ffmpeg i tak zdejmuje metadane przy przekodowaniu — nawet
gdyby dostawca je wstawił, nie przetrwałyby naszego pipeline'u.

## Decyzja — trzy warstwy

**1. Przełącznik na platformie** (ręcznie, przy każdej publikacji) — TikTok
„AI-generated content", Instagram/Facebook „AI info", YouTube „zmienione lub
syntetyczne treści". To warstwa, którą widzi odbiorca i której platformy
pilnują. **Nie zastępuje oznaczenia „reklama" / „materiał sponsorowany".**

**2. Znak w kadrze — tylko przez pierwsze sekundy.** Pigułka „Materiał zawiera
treści AI", wejście 0,35 s, zejście 4,2 s (spoty narracyjne) albo 3,6 s (krótkie
warianty, gdzie to i tak jedna trzecia materiału).

Dlaczego nie na stałe: znak przez 20–30 s zaśmieca kadr, a przepis wymaga
ujawnienia **„najpóźniej przy pierwszej ekspozycji"** — start spełnia to
z zapasem. Dlaczego nie plansza przed spotem: zmierzone okno 0–3 s decyduje
o `hook_score`, plansza obniżyłaby wyniki wszystkich spotów.

Dlaczego **u góry, nie przy dolnej krawędzi**: dolne ~15 % kadru zasłania
w Reels i TikToku interfejs aplikacji (opis, nick, przyciski). Oznaczenie,
którego nie widać, nie jest oznaczeniem.

**3. Metadane pliku + rejestr.** `finalize.py` remuksuje spoty zamiast je
kopiować i wpisuje adnotację w `comment` / `description`, a z `AI_MAP` generuje
`final/OZNACZENIA-AI.md` — co w którym spocie jest AI. To nie jest watermark
w rozumieniu art. 50 ust. 2 (ten należy do dostawcy modelu), tylko nasz ślad:
plik oderwany od platformy nadal niesie informację.

## Co NIE jest treścią AI

Rozróżnienie ma znaczenie, bo oznaczanie wszystkiego jak leci osłabia przekaz:

- **ekrany produktu** w spotach 10–14 są napisane w HTML — to rekonstrukcja UI,
  nie wygenerowana treść;
- typografia, plansze, napisy, montaż i muzyka powstają lokalnie;
- **spoty 13–14 symulują nagranie telefonem** — to nie jest AI, ale **jest
  stylizacja** sugerująca nagranie użytkownika. Osobna kwestia uczciwości
  przekazu, poza zakresem art. 50; opisana w
  [`../memory/format-pov-nagrane-telefonem.md`](../memory/format-pov-nagrane-telefonem.md).

## Pułapki

1. **`AI_MAP` trzeba utrzymywać ręcznie.** Nie da się tego wyprowadzić z plików
   (brak C2PA). Spot bez wpisu pojawia się w rejestrze jako „⚠️ BRAK WPISU" —
   celowo głośno, bo cichy brak zamienia rejestr w fikcję.
2. **Znak nie może wejść w warstwę chrome.** Chrome stoi przez cały klip, a znak
   ma zniknąć — to musi być osobne wejście z własnym `enable=`.
3. **Grade POV degraduje znak razem z resztą.** W `pov.py` obraz schodzi do 540p
   i wraca; stopień pisma 30 px przeżywa to czytelnie, mniejszy już nie.

## Zastrzeżenie

To nie jest opinia prawna. Wdrożenie odpowiada na obowiązek z art. 50 ust. 4
w formie, którą da się obronić, ale przy kampanii płatnej — zwłaszcza gdyby
copy powoływało się na „prawdziwego użytkownika" — warto to potwierdzić
z prawnikiem.

## Powiązane

- Rejestr: `projects/adresflow/final/OZNACZENIA-AI.md` (generowany)
- Pamięć: [`../memory/oznaczanie-tresci-ai.md`](../memory/oznaczanie-tresci-ai.md)
- Implementacja: `tools/brand.py` (`ai_mark`), `tools/story.py`, `tools/render.py`,
  `tools/finalize.py`, `screens/assets/pov.css`
