# Index pamięci — video-mentions (.ai/memory)

Wiedza **cross-project** o produkcji wideo reklamowego. Rzeczy specyficzne dla
jednego klienta/produktu leżą w `projects/<nazwa>/ai/`, nie tutaj.

- [Higgsfield MCP: limity](memory/higgsfield-mcp-limity.md) — trial „unlimited" nie działa przez MCP (liczą się tylko kredyty); `veo3_1_lite` wymusza 8 s przy start+end frame; polski TTS tylko przez `text2speech_v2`/elevenlabs
- [Pipeline montażu](memory/pipeline-montazu.md) — kredyty wyłącznie na generacje, cały montaż lokalnie za darmo; zmiana copy nie kosztuje ani kredyta
- [Copy i hook](memory/copy-i-hook.md) — ból odbiorcy bije opis produktu, ruch w 1. s bije treść; narracja kupuje sustain kosztem hooka
- [Ekran produktu z HTML](memory/ekran-produktu-hyperframes.md) — UI renderujemy przez HyperFrames, nie modelem wideo; cztery rzeczy, które odrzuca `hyperframes check`
- [Format POV „nagrane telefonem"](memory/format-pov-nagrane-telefonem.md) — ekran laptopa filmowany telefonem symulujemy w HTML; sprzedaje go geometria kadru i celowa utrata jakości, `hyperframes check` tego formatu nie przepuszcza i tak ma być
- [Oznaczanie treści AI](memory/oznaczanie-tresci-ai.md) — od 2026-08-02 art. 50 ust. 4 AI Act; materiał z Higgsfielda nie ma C2PA, więc platformy nie oznaczą spotu automatycznie — przełącznik trzeba włączyć ręcznie
- [Lektor i muzyka](memory/audio-lektor-muzyka.md) — nie generuj fraz osobno (dryf barwy); podkłady mają ciche intro, trzeba startować od najgłośniejszego fragmentu
- [Wymowa PPWR u lektora](memory/wymowa-ppwr-lektor.md) — Callum połyka „wu”; Whisper tego nie wykrywa; wymowę wybiera ucho Mateusza na stronie z próbkami, przed renderem

- [Lip-sync AI po polsku nie działa](memory/lipsync-ai-nie-dziala-pl.md) — trzy podejścia, ~80 kredytów, wszystkie odrzucone; twarz mówiąca tylko z prawdziwego nagrania
- [Montaż: pułapki synchronizacji](memory/montaz-pulapki-synchronizacji.md) — `-c copy` tnie po klatkach kluczowych, ujęcie restartuje się po przebitce, `loudnorm` wydłuża ścieżkę, napisy z ciszy zamiast z treści
- [Shorty z telefonu: sześć pułapek](memory/shorty-z-telefonu-pulapki.md) — rotacja pionu siedzi w metadanych; próg ciszy per plik i zmierzony; 1,8 s wiatru to nie cisza; ffmpeg z Homebrew nie ma `libass` ani `drawtext`; nakładka dłuższa od materiału rozciąga obraz; dziura w numeracji `IMG_` to jedyny sygnał brakującego pliku
- [Autentyczność bije gładkość](memory/autentycznosc-bije-gladkosc.md) — przy własnym nagraniu potknięcia i oddechy zostają; próg cięcia pauz 1,10 s, nie 0,30 s; otwarcie i finał to kadr, nie czarna plansza; długość ustępuje kompletności dowodu
- [Opis do rolki: krótko i na luzie](memory/opis-do-rolki-pisz-krotko-i-na-luzie.md) — zaczynaj od dwóch zdań; pointa potrzebuje własnej linii; żadnej listy tego, co widać w materiale; zdanie o niedoskonałości zostaje zawsze
- [Prośby o głośność tłumacz na decybele](memory/prosby-o-glosnosc-tlumacz-na-decybele.md) — „ścisz o 2 %" to −0,18 dB, czyli poniżej progu słyszalności; procent = kierunek, nie mnożnik; raportuj w dB
- [Nigdy nie rozciągaj kadru](memory/nigdy-nie-rozciagaj-kadru.md) — `scale=W:H` na innych proporcjach deformuje; blur-fill albo czysty crop

- [Wstawki: alfa zamiast green screena](memory/wstawki-alfa-nie-green-screen.md) — key zawsze zostawia zielony rant na krawędziach liter; `ALPHA=1`, kodek qtrle (~9× mniejszy od ProRes), podkładki chromakeya wtedy wyłączone

- [Wstawki: układ lewy domyślny](memory/wstawki-uklad-lewy-domyslny.md) — scena tekstowa w dwóch wariantach; wyśrodkowany zakrywa twarz mówiącego, lewy idzie do montażu
- [Wstawki: karta, scrim czy poświata](memory/wstawki-czytelnosc-scrim-halo-karta.md) — tekst w dolnej tercji zawsze dostaje kartę; poświata rozmywa krawędzie i przy karcie jest zbędna
- [Wstawki: rozdzielczość pod projekt montażowy](memory/wstawki-rozdzielczosc-pod-projekt.md) — 1920x1080 na płótnie 720p pokazuje środkowe 66 %; renderuj W/H pod projekt

- [Nasycony kolor tekstu na materiale](memory/tekst-nasycony-kolor-na-materiale.md) — h.264 4:2:0 zabija krawędź bursztynu; mały kolorowy tekst na ciemną pigułkę, weryfikuj PO kompresji nie na PNG
- [HyperFrames check: zasłanianie](memory/hyperframes-check-zaslanianie.md) — `data-layout-allow-occlusion` tylko na zasłanianym tekście, nie na nakładce i bez dziedziczenia; scrim ≥ 0,6 krycia to zasłonięcie
- [Ekran produktu: nagranie z kursorem](memory/ekran-produktu-nagranie-z-kursorem.md) — gdy jest prototyp, nagraj prawdziwą pracę w dwóch oknach z kursorem (Playwright); zrzuty z najazdem odbierane są jako „slajdy”
- [Ilustracja AI ożywiona w Kling](memory/ilustracja-ai-ozywiona-kling.md) — Kling 3.0 Pro ożywia płaską ilustrację bez psucia napisów (8/8), jeśli prompt nazywa konkretny ruch; stopklatka z najazdem to nie animacja

## Decyzje (ADR)

- [Ekran produktu z HTML zamiast nagrań i generacji](decisions/2026-07-30-ekran-produktu-z-html.md) — 2026-07-30
- [Oznaczanie treści AI — trzy warstwy, znak tylko na starcie](decisions/2026-08-02-oznaczanie-tresci-ai.md) — 2026-08-02
- [Pipeline shortów z telefonu (ADR projektowy)](../projects/shorts%20IG/ai/decisions/2026-08-19-pipeline-shortow-z-telefonu.md) — 2026-08-19
