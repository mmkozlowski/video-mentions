"""Lista cięć biblioteki — JEDYNE miejsce, w którym zapada decyzja, co zostaje.

Każdy wpis to jeden klip. `ranges` to przedziały [od, do) w sekundach źródła
(albo [od, do, dokładny_start, dokładny_koniec], gdy granicę trzeba wziąć z ciszy w sygnale):
do klipu wchodzą słowa, których start leży w przedziale; granice dociąga
build_clips.py do słów (z marginesem na oddech). Kilka przedziałów = wycięte
powtórki w środku ujęcia — wybieramy dobry dubel, NIE wygładzamy oddechów
(.ai/memory/autentycznosc-bije-gladkosc).

Oceny (1–5, redakcyjne, do weryfikacji predyktorem):
  hook      siła pierwszych 3 s — ból, pytanie, prowokacja, liczba
  delivery  płynność dubla — ile sklejek, przejęzyczenia, urwane CTA
kind:
  ad        reklama z prompteru (36 nagrań), docelowo 9:16 z panelem na grafikę
  chapter   rozdział wycięty z case study — kandydat na rolkę
  episode   pełny odcinek case study (YouTube 16:9, później grafiki i mockupy)
  raw       materiał roboczy (freestyle), bez obróbki
brand: flowbiz | aislupsk
cta: phone | web | youtube | aislupsk | comment | none — co faktycznie pada na nagraniu
"""

# ── Blok 1 — rolki Open Mercato (koszula w kratę) ────────────────────────────
ADS = [
    dict(n=1, code="01-3", title="AI zobaczy wypłaty", brand="flowbiz", block="open-mercato",
         ranges=[(121.4, 145.7), (157.3, 190.0)], hook=5, delivery=3, cta="youtube",
         notes="Dubel 3. W środku przejęzyczenie „systemie ERP AI”. CTA na YouTube, rozbudowane."),
    dict(n=2, code="01-1", title="Kto zmienił cenę", brand="flowbiz", block="open-mercato",
         ranges=[(231.6, 249.0), (263.4, 272.0), (282.8, 307.0)], hook=5, delivery=3, cta="youtube",
         notes="Hook z wulgaryzmem + „przepraszam za kolokwializm”. Organicznie świetne; w płatnej "
               "reklamie Meta może obciąć zasięg — do tego wersja z wypikanym słowem."),
    dict(n=3, code="02-3", title="AI nie zna Twojej firmy", brand="flowbiz", block="open-mercato",
         ranges=[(309.2, 313.5), (331.8, 390.0)], hook=4, delivery=4, cta="youtube",
         notes="„Clouda” = Claude'a — poprawić w napisach."),
    dict(n=4, code="02-4", title="AI skasuje mi pół bazy", brand="flowbiz", block="open-mercato",
         ranges=[(394.4, 400.0), (420.6, 470.0)], hook=5, delivery=4, cta="youtube",
         notes="Hook z pierwszego dubla, reszta z trzeciego. „cerem” = CRM w napisach."),

    # ── Blok 2 — reklamy miejskie ────────────────────────────────────────────
    dict(n=5, code="M1", title="Słupsk", brand="flowbiz", block="city",
         ranges=[(470.3, 505.0)], hook=4, delivery=4, cta="phone",
         notes="Jedno ujęcie. Wtrącenie „tak zwane quick winy”. Geo: Słupsk."),
    dict(n=6, code="M2", title="Pomorze — 40 minut od Ciebie", brand="flowbiz", block="city",
         ranges=[(518.5, 570.0)], hook=3, delivery=4, cta="phone",
         notes="Zamiast Ustki wyszła wersja regionalna (pomorskie + zachodniopomorskie). "
               "Mocne zdanie: „kilkadziesiąt godzin tygodniowo”. Ustki brak w materiale."),
    dict(n=7, code="M3", title="Lębork", brand="flowbiz", block="city",
         ranges=[(574.1, 595.5)], hook=4, delivery=4, cta="none",
         notes="Kończy się na nazwie firmy — telefon i www dołożyć grafiką."),
    dict(n=8, code="M4", title="Bytów", brand="flowbiz", block="city",
         ranges=[(607.0, 644.5)], hook=4, delivery=3, cta="web",
         notes="Przejęzyczenie „porozmawianym”. CTA: flowbiz.pl + krótka notka."),
    dict(n=9, code="M5", title="Koszalin", brand="flowbiz", block="city",
         ranges=[(644.6, 675.0)], hook=4, delivery=3, cta="none",
         notes="Wtrącenie o S6 jest niewyraźne. Telefon dołożyć grafiką."),
    dict(n=10, code="M6", title="Trójmiasto", brand="flowbiz", block="city",
         ranges=[(684.1, 725.0)], hook=4, delivery=3, cta="none",
         notes="Dubel z Sopotem. CTA ogólne „porozmawiajmy” — kontakt grafiką."),

    # ── Blok 3 — reklamy produkcyjne ─────────────────────────────────────────
    dict(n=11, code="R1", title="Zamówienie na 11 stron", brand="flowbiz", block="production",
         ranges=[(730.5, 733.9, None, 734.24), (737.0, 784.0)], hook=5, delivery=4, cta="none",
         notes="Mateusz poprawił się na nagraniu: 6 godzin, nie 3 — zostawiony dubel z 6 h. "
               "Zaproszenie bez telefonu. 16.10 (Agata): koniec 1. przedziału po sygnale — Whisper kończył "
               "„Excelu” 0,25 s za wcześnie i cięcie urywało końcówkę „-lu” (zamknięcie „trzy” od 734,21)."),
    dict(n=12, code="R2", title="Zeszyt i emerytura", brand="flowbiz", block="production",
         ranges=[(784.0, 802.6, None, 802.58), (803.6, 838.0, 803.78, None)], hook=5, delivery=4, cta="web",
         # 17.11 (Agata, Studio 0:16): falstart „jest w zzz…” (802,58–803,78) przed „jest w zeszytach” — wycięty
         notes="Jedno ujęcie, najmocniejsza emocja w bloku. CTA: bezpłatna konsultacja na flowbiz.pl."),
    dict(n=13, code="R3", title="Przepisy o opakowaniach (PPWR)", brand="flowbiz", block="production",
         ranges=[(840.0, 872.0), (882.1, 885.3), (890.0, 903.1), (912.0, 955.0)],
         hook=4, delivery=3, cta="web",
         notes="Wersja z panelem klienta zamiast archiwum. Dygresja o komunikacji 927–935 s "
               "do rozważenia. Niszowe: branża opakowań, PPWR."),
    dict(n=14, code="R4", title="ERP kontra hala", brand="flowbiz", block="production",
         ranges=[(957.1, 964.3, None, 964.85), (966.0, 1008.0, 970.55, None)], hook=5, delivery=3, cta="web",
         notes="Czasy słów Whispera przesunięte w 964–971 s (trzy próby „A na hali”) — sklejka ustawiona po transkrypcji samego wycinka i ciszy w sygnale (970,55 s)."),
    dict(n=15, code="R5", title="Produkcja z Pomorza", brand="flowbiz", block="production",
         ranges=[(1009.7, 1025.8), (1031.0, 1037.8), (1046.1, 1056.0), (1061.7, 1085.0)],
         hook=3, delivery=2, cta="none",
         notes="Najwięcej sklejek w całej sesji. Zapasowy — treść pokrywa R1."),
    dict(n=16, code="R6", title="Kontrahent z Niemiec", brand="flowbiz", block="production",
         ranges=[(1096.4, 1116.8), (1131.0, 1150.0)], hook=4, delivery=4, cta="web"),
    dict(n=17, code="R7", title="Nie rok wdrożenia", brand="flowbiz", block="production",
         ranges=[(1153.0, 1161.3), (1166.8, 1194.6), (1198.4, 1219.0)], hook=4, delivery=3,
         cta="web", notes="CTA kieruje na openmercato.com, nie na flowbiz."),
    dict(n=18, code="R8", title="Każde zlecenie inne", brand="flowbiz", block="production",
         ranges=[(1220.9, 1245.0), (1256.5, 1310.0)], hook=4, delivery=4, cta="none",
         notes="Mocny argument: „używasz 20% systemu, płacisz dziesiątki tysięcy rocznie”."),

    # ── Blok 3b — agent AI dla CEO ───────────────────────────────────────────
    dict(n=19, code="RA1", title="Prezes na lotnisku", brand="flowbiz", block="ceo-agent",
         ranges=[(1321.8, 1370.0)], hook=5, delivery=5, cta="none",
         notes="Jedno czyste ujęcie. Bez CTA — kontakt grafiką."),
    dict(n=20, code="RA2", title="Odpowiedź w pięć sekund", brand="flowbiz", block="ceo-agent",
         ranges=[(1377.9, 1401.7), (1408.2, 1430.0)], hook=4, delivery=3, cta="web"),
    dict(n=21, code="RA3", title="Asystent, który nie śpi", brand="flowbiz", block="ceo-agent",
         ranges=[(1432.0, 1450.0)], hook=4, delivery=2, cta="none",
         notes="Dwa przejęzyczenia: „i NIE siedzi w Twoim Telegramie”, „Nic się wysyła sam”. "
               "Do ponownego nagrania albo tylko pierwsze zdanie jako bumper."),

    # ── Blok 4 — reelsy edukacyjne ───────────────────────────────────────────
    dict(n=22, code="E2", title="Co AI daje produkcji — 4 rzeczy", brand="flowbiz", block="education",
         ranges=[(1481.2, 1555.7)], hook=4, delivery=4, cta="phone",
         notes="Pauzy po punktach = miejsce na wstawki. Telefon wspomniany, numer nie pada."),
    dict(n=23, code="E1", title="5 rzeczy bez licencji", brand="flowbiz", block="education",
         ranges=[(1555.7, 1626.0)], hook=4, delivery=4, cta="web"),
    dict(n=24, code="E7", title="Agent AI dla prezesa — co robi", brand="aislupsk", block="education",
         ranges=[(1632.5, 1697.6)], hook=4, delivery=4, cta="aislupsk",
         notes="Most Flowbiz → warsztaty. Adres strony brzmi niewyraźnie — w napisach aislupsk.pl."),
    dict(n=25, code="E5", title="4 błędy przy wdrożeniu AI", brand="flowbiz", block="education",
         ranges=[(1697.6, 1760.0)], hook=5, delivery=4, cta="comment",
         notes="CTA na komentarz — najlepszy kandydat na zasięg organiczny."),

    # ── Blok 5 — warsztaty AI Słupsk (zielone polo) ──────────────────────────
    dict(n=26, code="W10", title="Agent w telefonie — warsztat", brand="aislupsk", block="workshop",
         ranges=[(1844.6, 1885.6), (1890.8, 1904.0)], hook=4, delivery=3, cta="aislupsk",
         notes="Doszły narzędzia: Claude, Grok-bot. Pizza i ludzie z regionu."),
    dict(n=27, code="W11", title="Pizza i networking", brand="aislupsk", block="workshop",
         ranges=[(1907.8, 1918.0), (1924.6, 1952.0)], hook=4, delivery=4, cta="aislupsk"),
    dict(n=28, code="W1", title="Szefie, Twoi ludzie już używają AI", brand="aislupsk", block="workshop",
         # 17.11 (Agata, Studio 0:22/0:30): bez falstartu „War-” (1982,55–1983,17) przed „Warsztaty są w Słupsku”;
         # koniec w ciszy po „ai.slupsk.pl” (1990,45) — wcześniej wchodziło „i-” z „i zapisz się na listę” i urywało
         ranges=[(1955.8, 1982.0), (1983.0, 1990.9, 1983.18, 1990.45)], hook=5, delivery=4, cta="aislupsk",
         notes="Region w nagraniu: Słupsk, Lębork, Koszalin."),
    dict(n=29, code="W4", title="Śniadanie dla szefów", brand="aislupsk", block="workshop",
         ranges=[(2000.0, 2050.0, 2006.6, None)], hook=4, delivery=3, cta="aislupsk",
         notes="Pierwszy start („osoby decyzyjne”, 2000,6–2004,4 s) wycięty po ciszy — Whisper go pominął. Format śniadaniowy, bezpłatne, ograniczona liczba miejsc."),

    # ── Blok 6 — dodatkowe ───────────────────────────────────────────────────
    dict(n=30, code="L5", title="Trzy wersje Excela", brand="flowbiz", block="extra",
         ranges=[(2066.4, 2108.0)], hook=4, delivery=4, cta="web"),
    dict(n=31, code="L9", title="ChatGPT dla pracowników", brand="flowbiz", block="extra",
         ranges=[(2109.4, 2126.1), (2137.5, 2161.0)], hook=5, delivery=3, cta="web"),
    dict(n=32, code="L1", title="Najlepsza osoba przepisuje maile", brand="flowbiz", block="extra",
         ranges=[(2162.5, 2182.6), (2189.3, 2220.0)], hook=4, delivery=3, cta="none"),
    dict(n=33, code="G1", title="Programista kontra ChatGPT", brand="flowbiz", block="extra",
         ranges=[(2225.9, 2249.6), (2254.7, 2267.0, None, 2267.40), (2272.3, 2278.0, 2273.18, None)], hook=5, delivery=3, cta="web",
         notes="16.10 (Agata, 0:30–0:34): wycięta powtórka „co można uzyskać po kilku tygodniach z nas z nami” — "
               "zostaje „…po kilku tygodniach pracy, daj znać”. Granice po ciszy w sygnale (Whisper dokleja „daj” do pauzy)."),
    dict(n=34, code="E4", title="Gdzie AI ma sens — 3 na tak, 3 na nie", brand="flowbiz", block="extra",
         ranges=[(2282.8, 2319.0)], hook=4, delivery=5, cta="none",
         notes="Jedno czyste ujęcie, pointa „AI przygotowuje, człowiek decyduje”."),
    dict(n=35, code="W9", title="Umowa w ChatGPT", brand="aislupsk", block="extra",
         ranges=[(2324.2, 2342.4, None, 2342.62), (2351.4, 2371.0, 2351.62, None)], hook=5, delivery=4, cta="aislupsk",
         notes="16.10 (Agata, 0:17–0:23): „plus konkretne zastosowania, które oszczędzają” padało 3 razy — "
               "zostaje trzeci, pełny dubel (od 2351,7). Whisper zgubił dwa pierwsze w jednym słowie — czasy "
               "słów 2342–2356 w transkrypcji poprawione ponownym przebiegiem na krótkich odcinkach."),
    dict(n=36, code="W7", title="Przynieś swój problem", brand="aislupsk", block="extra",
         ranges=[(2377.4, 2415.0)], hook=4, delivery=4, cta="aislupsk",
         notes="Region w nagraniu: Słupsk, Gdańsk i okolice."),
]

# ── Pełne odcinki case study (16:9, YouTube) ────────────────────────────────
# Nazwy klientów tylko tu, wewnętrznie. Na nagraniach nazwy nie padają.
EPISODES = [
    # 17.11 (odsłuch MK, pkt 14 + anonimowość): „od klienta z Podsłupska” → „od klienta” (cisza 81,98 / 83,04,
    # sprawdzone Whisperem sklejki); „Dlaczego?” sklejało dwa podejścia („Czego? Bo robiły…”) — koniec po „wykonywały.”
    # (92,42, cisza z sygnału), start na początku drugiego „Dlaczego?” (97,30, przed nim cisza 96,44–97,42)
    dict(id="ep-doram", source="doram", client="Doram", title="Meble ogrodowe: zamówienia z Niemiec",
         # Mateusz 12.10: drugie „Dlaczego?” (restart 92,9–97,5 s) wycięte, zostaje pierwsze + dokończona próba
         # 16.11: bez „No dobra, lecimy z kolejnymi praktycznymi użyciami AI w firmach.” (zostało ze składanki) —
         # start od „Teraz na warsztat…” (cisza w sygnale 13,80–15,12, czasy Whispera ~0,9 s za wcześnie)
         # 21.11 (MK: „początek odcinka = wycinek tego, co mówię, przedstawienie po 15–20 s”): bez meta-wstępu
         # „Teraz na warsztat… jak wygląda teraz” — start od „Klient dostawał…” (cisza w sygnale 33,12–33,68; 29,5 s to pauza wewnątrz wstępu)
         ranges=[(33.3, 82.0, 33.55, 81.98), (82.9, 92.95, 83.04, 92.42), (93.0, 688.0, 97.30, None)], hook=3, delivery=3, brand="flowbiz",
         notes="Zamówienia od niemieckich kontrahentów w Excelu, dopasowanie AI 70% → 94% "
               "po miesiącu, kody kreskowe z kilku dni do 15 minut. Restart zdania w 92 s."),
    dict(id="ep-vacuactiv", source="vacuactiv", client="Vacuactiv", title="Agent AI dla właściciela firmy",
         # 05.11 wieczór (uwagi Mateusza w Studiu): bez 21× „po prostu”, falstartu „nagle… cyfryzacja”,
         # „do jednego… do jednego tutaj…”, „żeby… żeby”, „Kolejne statu…, tak”, „i… i itd., tak”, „do tego… jak, jak… tutaj”
         # i przeciągniętego „z…” przed „związane”.
         # Granice z sygnału (RMS co 20 ms) + kontrola Whisperem sklejki — czasy słów w tym nagraniu
         # są przesunięte nawet o 0,8 s. Po „…czy to przymiotnik” wchodzi gag (assemble_episode.PLAN).
         ranges=[(7.00, 46.30, None, 46.30),
                (47.18, 78.27, 47.18, 78.27),
                (79.32, 87.55, 79.32, 87.55),
                (87.95, 89.12, 87.95, 89.12),
                (89.36, 181.82, 89.36, 181.82),
                (182.52, 194.60, 182.52, 194.60),
                (197.44, 220.02, 197.44, 220.02),
                (221.08, 241.76, 221.08, 241.76),
                (242.16, 249.60, 242.16, 249.60),
                (250.22, 292.18, 250.22, 292.18),
                (293.96, 301.75, 293.96, 301.75),
                (307.02, 320.68, 307.02, 320.68),
                (323.52, 427.42, 323.52, 427.42),
                (427.84, 521.70, 427.84, 521.70),
                (522.20, 786.33, 522.20, 786.33),
                (786.74, 788.38, 786.74, 788.38),
                (788.86, 793.44, 788.86, 793.44),
                (793.94, 833.04, 793.94, 833.04),
                (833.82, 899.96, 833.82, 899.96),
                (900.54, 909.80, 900.54, 909.80),
                (910.38, 980.04, 910.38, 980.04),
                (981.14, 991.12, 981.14, 991.12),
                (992.18, 1039.28, 992.18, 1039.28),
                (1040.90, 1068.42, 1040.90, 1068.42),
                (1069.14, 1090.70, 1069.14, 1090.70),
                (1091.28, 1095.45, 1091.28, 1095.45),
                (1098.10, 1103.00, 1098.10, 1103.00),
                (1110.60, 1112.06, 1110.60, 1112.06),
                (1113.48, 1114.32, 1113.48, 1114.32),
                (1115.20, 1116.05, 1115.20, 1116.05),
                (1116.85, 1126.00, 1116.85, None)], hook=3, delivery=3, brand="flowbiz",
         notes="Sprzęt sportowy z okolic Słupska. ChatGPT gubi kontekst → mózg firmy "
               "(100–150 GB danych), Open Mercato na produkcji, brief w Telegramie, "
               "Obsidian + Hermes + Codex. Najdłuższy, do skrócenia w montażu."),
    dict(id="ep-open-mercato-offers", source="session", client="(wiele)",
         title="Oferta w 5 minut zamiast dwóch dni",
         # 16.11 (Mateusz: „to nie jest o 8 wdrożeniach”): bez wstępu składanki „Cześć. Zrobiłem już 8 wdrożeń…
         # Już Wam o tym mówię. Pierwsza rzecz to jest” — start od „tworzenie ofert.” (cisza w sygnale 2581,50–2581,92,
         # sprawdzone Whisperem wycinka). Wstęp robi głos z dogrywek na planszy (ins-hello, assemble_episode.PLAN).
         # koniec 2768,65 (było 2768,20): przy cięciu wstawek END (−0,35 s) „pójdzie.” urywało się w połowie;
         # następna wypowiedź („Ok, kolejny temat”) zaczyna się dopiero w 2770,3
         ranges=[(2581.2, 2657.4, 2581.70, 2657.30), (2659.4, 2716.2, 2659.50, 2716.10), (2719.3, 2767.6, 2719.42, 2768.65)], hook=3, delivery=3,   # ten sam dubel co ch-offers-1
         brand="flowbiz",
         notes="Krótki odcinek: chaos w ofertach, konwersja handlowców, asystent czytający maile "
               "(producent sprzętu sportowego) — oferta w 5 min zamiast kilkunastu godzin."),
    dict(id="ep-rezon", source="session", client="Rezon",
         title="Pamiątki znad morza: system B2B",
         # noc 04.11 (kontrola transkrypcją gotowego pliku): start bez ogona „pójdzie” z ep-offers
         # („Ok” od 2770,32 z sygnału), bez falstartu „Włożyliśmy,” (2911,04–2912,2), bez dubli
         # „na pace, czyli na naszym / na naszym dostawcach. Dostawczaku.” (3024,0–3029,44).
         # Czasy Whispera przesunięte tu o ~1,5 s — granice z ciszy w sygnale, sprawdzone sklejką.
         # 16.11: bez „Ok, kolejny temat.” (składanka) — start od „Firma produkująca…” (cisza 2774,28–2775,64)
         # 17.11 (decyzja MK: klienci anonimowo): „pamiątki w Kołobrzegu przyszła” → „pamiątki przyszła” (cisza 2778,52 / 2780,95)
         ranges=[(2774.6, 2778.6, 2775.30, 2778.52), (2780.8, 2910.5, 2780.95, 2910.55), (2912.5, 3022.5, 2912.60, 3022.40),
                 (3022.9, 3023.95, 3023.00, 3023.90), (3032.3, 3226.0, 3032.44, None)], hook=3, delivery=3,
         brand="flowbiz",
         notes="Firma z Kołobrzegu, proces na kartkach, integracja z PC Business, handlowiec "
               "z tabletem, produkcja na zamówienie, panel klienta na Open Mercato."),
    dict(id="ep-marpasz", source="session", client="Marpasz", title="Pasza dla zwierząt: etykiety i katalog AI",
         ranges=[(3249.0, 3740.0)], hook=3, delivery=3, brand="flowbiz",
         notes="Sklep internetowy ze Słupska. Paczki po 25 kg = 4 etykiety na zamówienie w Apilo, "
               "teraz jedno kliknięcie — ok. 100 h/mies. Katalog AI z faktur do Nexo i opisy "
               "na Allegro/Erli/sklep. „Dokręcanie śrubek”."),
]

# ── Rozdziały z case study — kandydaci na rolki ─────────────────────────────
CHAPTERS = [
    dict(id="ch-doram-1-nazwy", source="doram", parent="ep-doram",
         title="Ten sam produkt na kilkanaście sposobów", ranges=[(33.3, 79.3)], hook=4, delivery=4),
    dict(id="ch-doram-2-kilka-dni-10-minut", source="doram", parent="ep-doram",
         title="Kilka dni klepania → 10 minut", ranges=[(79.2, 92.1), (96.8, 145.7)], hook=4, delivery=3),
    dict(id="ch-doram-3-przeklejala-drukowala", source="doram", parent="ep-doram",
         title="Przeklejała, drukowała, przeklejała…", ranges=[(215.3, 292.2)], hook=5, delivery=4,
         notes="Rytm „przeklejała, drukowała” ×3 to gotowy hook — można zacząć od niego (264 s)."),
    dict(id="ch-doram-4-fundamenty", source="doram", parent="ep-doram",
         title="Bez fundamentów AI nie wie, jak pracujesz", ranges=[(292.1, 342.2)], hook=3, delivery=4),
    dict(id="ch-doram-5-70-94", source="doram", parent="ep-doram",
         title="Pamięć dla AI: 70% → 94% w miesiąc", ranges=[(521.5, 602.2)], hook=5, delivery=3),
    dict(id="ch-doram-6-kody-15-minut", source="doram", parent="ep-doram",
         title="Kody kreskowe: z kilku dni do 15 minut", ranges=[(602.1, 637.3)], hook=5, delivery=4,
         notes="„Żadnej magii, żadnego AI” — wiarygodność."),
    # noc 04.11: wersja do składanki ep-8-wdrozen — domyka zdanie „więc to by było na razie na tyle.”
    # (rozdział kończył się na „więc”). Rolki i reklamy miejskie zostają na ch-doram-6-kody-15-minut.
    dict(id="ch-doram-6-kody-15-minut-full", source="doram", parent="ep-doram",
         title="Kody kreskowe: z kilku dni do 15 minut (pełne zdanie)", ranges=[(602.1, 639.0)], hook=5, delivery=4),
    dict(id="ch-vacu-1-chatgpt-zapomina", source="vacuactiv", parent="ep-vacuactiv",
         title="ChatGPT przestaje pamiętać Twoje wytyczne", ranges=[(38.5, 124.6)], hook=5, delivery=3),
    dict(id="ch-vacu-2-dane-w-glowach", source="vacuactiv", parent="ep-vacuactiv",
         title="Dane w głowach, na kartkach, w mailach", ranges=[(131.8, 210.1)], hook=4, delivery=3),
    dict(id="ch-vacu-3-mozg-firmy", source="vacuactiv", parent="ep-vacuactiv",
         title="Mózg firmy ze 150 GB danych", ranges=[(210.1, 284.3)], hook=4, delivery=4),
    dict(id="ch-vacu-4-duze-systemy", source="vacuactiv", parent="ep-vacuactiv",
         title="Dlaczego duże systemy się nie wdrażają", ranges=[(344.5, 438.4)], hook=4, delivery=3),
    dict(id="ch-vacu-5-kierownik-w-godzine", source="vacuactiv", parent="ep-vacuactiv",
         title="Kierownik produkcji nauczył się w godzinę",
         # 17.11 (odsłuch, pkt 1): bez falstartu „Kierownik produkcji miał swój sposób, a miał go na tyle ten sposób,”
         # → „…ale miał swój sposób. Miał na tyle ten sposób ułożony” (tylko składanka ep-8-wdrozen używa tego klipu)
         ranges=[(438.4, 452.3, None, 452.30), (456.35, 457.8, 457.22, 457.75), (458.2, 563.8, 458.40, None)], hook=4, delivery=3),
    dict(id="ch-vacu-6-brief-telegram", source="vacuactiv", parent="ep-vacuactiv",
         title="Zamówienie z Telegrama w trzy kliknięcia", ranges=[(563.8, 678.1)], hook=4, delivery=3),
    dict(id="ch-vacu-7-narzedzie-to-nie-wdrozenie", source="vacuactiv", parent="ep-vacuactiv",
         title="Licencja to nie wdrożenie", ranges=[(1063.9, 1100.1)], hook=4, delivery=3),
    # 16.11: część „oferty” składanki ep-8-wdrozen Z WSTĘPEM „Zrobiłem już 8 wdrożeń…” — tam ten wstęp pasuje,
    # a sam odcinek ep-open-mercato-offers od 16.11 zaczyna się od „tworzenie ofert.” (compile_episode.py)
    dict(id="ch-offers-0-z-wstepem-8-wdrozen", source="session", parent="ep-open-mercato-offers",
         title="Oferty — z wstępem składanki „8 wdrożeń”",
         ranges=[(2557.1, 2657.4, None, 2657.30), (2659.4, 2716.2, 2659.50, 2716.10), (2719.3, 2767.6, 2719.42, 2768.20)], hook=3, delivery=3),
    dict(id="ch-offers-1-oferta-5-minut", source="session", parent="ep-open-mercato-offers",
         title="Oferta w 5 minut zamiast kilkunastu godzin",
         # 12.10 uwagi Mateusza ze studia: start łapał „…chwili” i ucinał „A”; dubel „zbiera z nich informacje
         # na temat wycen” — pierwsze podejście urwane na „na temat”, zostaje drugie od 2719,42; koniec ucinał „pójdzie”
         ranges=[(2703.0, 2716.2, 2703.56, 2716.10), (2719.3, 2767.6, 2719.42, 2768.20)], hook=5, delivery=4),
    dict(id="ch-rezon-1-ksiegowosc-po-fakcie", source="session", parent="ep-rezon",
         title="Dane z księgowości to dane po fakcie", ranges=[(2803.5, 2877.1)], hook=4, delivery=3),
    dict(id="ch-rezon-2-ustka-rowy", source="session", parent="ep-rezon",
         title="Tysiące sztuk z napisem „Ustka”", ranges=[(3052.8, 3116.4)], hook=4, delivery=3),
    dict(id="ch-rezon-3-panel-klienta", source="session", parent="ep-rezon",
         title="Klient sam składa zamówienie",
         # 17.11 (pkt 4): bez „Co tu jeszcze zmieniliśmy… Zmieniliśmy to, że” — łącznik 10 przedstawia case, „jeszcze”
         # nie miało kontekstu; start od „Klient przestaje zamawiać mailowo” (tylko składanka ep-8-wdrozen)
         ranges=[(3116.1, 3227.0, 3121.30, None)], hook=3, delivery=3),
    dict(id="ch-marpasz-1-cztery-worki", source="session", parent="ep-marpasz",
         title="Cztery worki paszy = cztery etykiety", ranges=[(3279.6, 3428.6)], hook=4, delivery=3),
    dict(id="ch-marpasz-2-100-godzin", source="session", parent="ep-marpasz",
         title="100 godzin miesięcznie mniej", ranges=[(3444.5, 3547.6)], hook=5, delivery=3),
    dict(id="ch-marpasz-3-katalog-ai", source="session", parent="ep-marpasz",
         title="Katalog AI: z faktury do Allegro", ranges=[(3557.2, 3679.6)], hook=4, delivery=3),
    # noc 04.11: wersja do składanki ep-8-wdrozen — rozdział kończył się na „firmę handlową i”,
    # tu domknięty do „…spokój po wprowadzeniu takich rzeczy.”
    dict(id="ch-marpasz-3-katalog-ai-full", source="session", parent="ep-marpasz",
         title="Katalog AI: z faktury do Allegro (pełne zdanie)", ranges=[(3557.2, 3697.0)], hook=4, delivery=3),
    # 16.11: warianty tylko do składanki ep-8-wdrozen (rolki zostają na starych klipach). Cięcia z listy
    # „co zrobię bez nagrywania” (vault 2026-11-15-do-dogrania.md); granice z sygnału, sklejki sprawdzone Whisperem.
    # Każdy case otwiera łącznik z dogrywek (ins-case-6…12), więc zdania „kolejny przykład…” wypadają.
    dict(id="ch-doram-5-70-94--8w", source="doram", parent="ep-doram",
         title="Pamięć dla AI: 70% → 94% (do składanki, bez „już wracając znowu do brzegu”)",
         # + kontekst z poprawek studia 02.11 (941f34f, niescalone; uwaga MK 15.11 w Studiu „3:36 dalej ucięte”):
         # „Klient dostawał od swoich kontrahentów niemieckich zamówienia w Excelu.” (33,40–40,75) przed „I w tym przypadku…”
         ranges=[(33.0, 40.5, 33.40, 40.75), (521.5, 523.1, 521.85, 523.22), (525.65, 561.6, 525.70, 561.51),
                 # 17.11 (pkt 2–3): bez „dlatego mówiłem też o tych kilkunastu kliknięciach” — w składance i zajawce nic o tym nie padło
                 (564.2, 602.2, 564.40, None)], hook=5, delivery=3),
    # 17.11 (Agata, zajawka 0:09: „nie wiadomo, co »polegało« ani skąd miernik”): po „zamówienia w Excelu” zdanie
    # z odcinka „Kontrahent, który zamawiał, potrafił tą samą rzecz nazwać na kilkanaście różnych sposobów. Potrafił raz
    # napisać po niemiecku, raz po angielsku.” (62,05–73,45); wątek „więc nawet jeżeli zrobiliśmy miernik i wyliczaliśmy…
    # to powodowało, że” wycięty (533,42–543,30) → „…nazwany w różnych momentach. Z początku … 70%”
    dict(id="ch-doram-5-70-94--zajawka", source="doram", parent="ep-doram",
         title="Pamięć dla AI: 70% → 94% (zajawka mebli 26.11)",
         ranges=[(33.0, 40.5, 33.40, 40.75), (61.9, 73.4, 62.05, 73.45), (521.5, 523.1, 521.85, 523.22),
                 (525.65, 533.3, 525.70, 533.42), (542.9, 561.6, 543.30, 561.51), (564.2, 602.2, 564.40, None)],
         hook=5, delivery=3,
         # napisy na sklejkach (czasy z sygnału i Whispera gotowego wycinka)
         caption_words=[(40.5, 40.7, []), (60.8, 61.0, [("Kontrahent,", 62.05, 62.5)]), (73.25, 73.4, []), (521.6, 521.95, [("I", 521.85, 521.94), ("w", 521.94, 521.98), ("tym", 521.98, 522.08),
                                                             ("przypadku", 522.08, 522.36)]),
                        (523.1, 523.3, []), (533.35, 543.4, [("Z", 543.32, 543.5), ("początku", 543.5, 543.86)])]),
    # 17.11 (pkt 7): rolka o kodach i zajawka 8 wdrożeń — start bez „Jeżeli chodzi o tą część taką jeszcze bardzo
    # czasochłoną, czy” (widz nie wiedział, jaką część): od „generowanie samych kodów kreskowych” (cisza 606,64–606,80)
    dict(id="ch-doram-6-kody-od-generowania", source="doram", parent="ep-doram",
         title="Kody kreskowe: z kilku dni do 15 minut (od „generowanie kodów”)", # 17.11 (Agata, zaj-8 0:04): „no to tutaj to nie było tutaj” → „no to nie było tutaj” (610,49–610,82 wycięte)
         ranges=[(606.6, 610.4, 606.76, 610.49), (610.6, 637.3, 610.82, None)], hook=5, delivery=4,
         caption_words=[(609.7, 611.05, [("no", 610.36, 610.45), ("to", 610.45, 610.49), ("nie", 610.82, 610.94), ("było", 610.94, 611.12), ("tutaj", 611.12, 611.5)])]),
    dict(id="ch-doram-6-kody-od-generowania--15-minut", source="doram", parent="ep-doram",
         title="Kody kreskowe (zajawka 8 wdrożeń: od „generowanie kodów”, koniec na „15 minut pracy”)",
         ranges=[(606.6, 610.4, 606.76, 610.49), (610.6, 637.15, 610.82, 637.30)], hook=5, delivery=4,
         caption_words=[(609.7, 611.05, [("no", 610.36, 610.45), ("to", 610.45, 610.49), ("nie", 610.82, 610.94), ("było", 610.94, 611.12), ("tutaj", 611.12, 611.5)])]),
    # 17.11 (pkt 8): zajawka pamiątek z hakiem z samego odcinka („I nagle produkujemy tego dziesiątki tysięcy sztuk…”),
    # potem od „Każdy wzór, każda miejscowość ma swój napis” — bez „Ta branża też…” (zlepione, nie da się wyciąć samego „też”)
    dict(id="ch-rezon-2-ustka-rowy--hak", source="session", parent="ep-rezon",
         title="Tysiące sztuk z napisem „Ustka” (hak z odcinka)",
         ranges=[(3044.3, 3052.6, 3044.60, 3052.45), (3066.3, 3116.4, 3066.55, None)], hook=4, delivery=3),
    dict(id="ch-doram-6-kody-15-minut--8w", source="doram", parent="ep-doram",
         title="Kody kreskowe (do składanki, koniec na „15 minut pracy”)",
         ranges=[(602.1, 637.15, None, 637.30)], hook=5, delivery=4),
    dict(id="ch-marpasz-2-100-godzin--8w", source="session", parent="ep-marpasz",
         title="100 godzin miesięcznie mniej (do składanki: z kontekstem 4 worków, domknięte „na to.”)",
         # kontekst z poprawek studia 02.11 (commit 941f34f na gałęzi mmkozlowski/poprawki-studia-02-11, niescalonej):
         # „Klient zamawiał cztery worki paszy po 25 kilo … cztery różne etykiety,” + „I o tyle to teraz się zmieniło…”
         ranges=[(3321.0, 3332.0, 3321.30, 3332.80), (3440.4, 3547.7, 3440.65, 3548.10)], hook=5, delivery=3),
    dict(id="ch-marpasz-3-katalog-ai--8w", source="session", parent="ep-marpasz",
         title="Katalog AI (do składanki, od „Katalog AI, jak to wygląda?”)",
         ranges=[(3560.3, 3697.0, 3560.60, None)], hook=4, delivery=3),
    dict(id="ch-marpasz-4-srubki", source="session", parent="ep-marpasz",
         title="AI to dokręcanie śrubek", ranges=[(3697.5, 3740.0)], hook=4, delivery=4),
]

RAW = [
    dict(id="raw-freestyle-workshop", source="session", title="Freestyle: bańka AI i strach",
         ranges=[(2424.6, 2548.0)], hook=3, delivery=2, brand="aislupsk",
         notes="Zaproszenie na warsztaty bez prompteru, urwane na fakturach. Do przebrania na cytaty."),
]

# ── Przerywniki o usługach (openmerxat-wstawki.mov) — dołożone 04.11.2026 ────
# Nagrane raz, wklejane do odcinków (vault: marketing/content/youtube/_przerywniki.md i
# _wstawki-uslugi-plan.md). Granice z ciszy w sygnale, każda sklejka sprawdzona transkrypcją.
# Zdanie „u Ciebie w filmie jest dokładnie tak samo” (99–108 s, 164–171 s) pominięte: dwa modele
# słyszą „w filmie”, nie „w firmie” — zaproszenie zaczyna się od „Poczekaj…” i przechodzi
# od razu do „Robię konsultacje…”.
RAW += [
    dict(id="ins-intro", source="inserts", title="Przerywnik: przedstawienie się",
         ranges=[(3.9, 14.3, 3.96, 14.26), (65.5, 74.6, 65.56, 74.55)], hook=3, delivery=4,
         notes="„A ja nazywam się Mateusz Kozłowski…” + branże, do „…miałem okazję już dotknąć”. Bez „to nie jest odcinek "
               "sponsorowany” (Mateusz 05.11: „po co mam się tłumaczyć”), cięcie w ciszy 74,38–74,76. Po hooku."),
    dict(id="ins-mid", source="inserts", title="Przerywnik: zaproszenie na konsultację",
         ranges=[(95.8, 99.4, 96.85, 99.36), (171.6, 175.95, 172.10, 175.95), (179.3, 198.6, 179.40, 198.58)], hook=3, delivery=4,
         # 05.11: bez „zzzz” przed „Poczekaj” (95,83–96,71), szumu przed „Robię” (171,77–172,04, whisper: „dziękuję”)
         # i falstartu „i wychodzisz z… odpowiem…” (176,0–179,4) — whisper chował powtórkę w 3 s dziury przed „czy”
         notes="„Poczekaj, zatrzymam Cię…” + konsultacja, „bez zobowiązań”, WhatsApp/LinkedIn/strona. 60–70% filmu."),
    dict(id="ins-mid-long", source="inserts", title="Przerywnik: zaproszenie na warsztat (Open Mercato)",
         ranges=[(95.8, 99.4, 96.85, 99.36), (108.7, 118.6, 108.79, 118.55), (133.3, 156.1, 133.38, 156.02),
                 (183.1, 198.6, 183.18, 198.58)], hook=3, delivery=4,
         notes="Wersja z warsztatem na miejscu i „Open Mercato przetworzy to na specyfikację” — tylko odcinki o OM."),
    dict(id="ins-outro", source="inserts", title="Przerywnik: zamknięcie",
         ranges=[(206.3, 222.35, 206.40, 222.30)], hook=3, delivery=4,
         notes="„Jeśli chcesz, żebym przeszedł z Tobą przez Twój proces…” + pytania w komentarzu. Po CTA odcinka."),
]

# ── Wstawki z dogrywek audio 16.11 (raw/2026-11-16-dogrywki-audio, tools/dubs_ingest.py + dubs_split.py) ──
# 20.11: kwestie 06–43 z ponownego nagrania (stare miało pogłos); granice z mapa.json, 15 = sklejka bez dubla „będzie o tym”.
# Sam głos na planszach kinetycznych (mockups.kinetic). Granice = kwestie/mapa.json (cisza w sygnale),
# numery kwestii z vault marketing/content/youtube/2026-11-15-do-dogrania.md.
RAW += [
    dict(id="ins-hello-offers", source="dubs", title="Dogrywka: wstęp (13+14) — oferty",
         ranges=[(109.93, 118.26, 109.98, 118.26), (118.75, 125.10, 118.80, 125.10)], hook=3, delivery=4),
    dict(id="ins-lead-doram", source="dubs", title="Dogrywka: wstęp (14+15) — meble",
         ranges=[(118.75, 125.10, 118.80, 125.10), (125.13, 126.58, 125.18, 126.58), (128.25, 132.46, 128.30, 132.46)], hook=3, delivery=4),
    dict(id="ins-lead-rezon", source="dubs", title="Dogrywka: wstęp (14+15) — pamiątki",
         ranges=[(118.75, 125.10, 118.80, 125.10), (125.13, 126.58, 125.18, 126.58), (128.25, 132.46, 128.30, 132.46)], hook=3, delivery=4),
    dict(id="ins-a1", source="dubs", title="Dogrywka: łącznik przed przedstawieniem (1)",
         ranges=[(6.97, 10.72, 7.02, 10.72)], hook=3, delivery=4),
    dict(id="ins-a2", source="dubs", title="Dogrywka: łącznik po przedstawieniu (2)",
         ranges=[(18.11, 20.98, 18.16, 20.98)], hook=3, delivery=4),
    dict(id="ins-a3", source="dubs", title="Dogrywka: łącznik po zaproszeniu (3)",
         ranges=[(34.33, 37.50, 34.38, 37.50)], hook=3, delivery=4),
    dict(id="ins-a4", source="dubs", title="Dogrywka: łącznik przed zamknięciem (4)",
         ranges=[(39.91, 42.90, 39.96, 42.90)], hook=3, delivery=4),
    dict(id="ins-bye", source="dubs", title="Dogrywka: do zobaczenia w następnym odcinku (24)",
         ranges=[(139.15, 144.06, 139.20, 144.06)], hook=3, delivery=4),
    dict(id="ins-contact", source="dubs", title="Dogrywka: kontakt w opisie (23)",
         ranges=[(132.77, 138.56, 132.82, 138.56)], hook=3, delivery=4),
    dict(id="ins-g27", source="dubs", title="Dogrywka shortów — hak: większość firm robi to ręcznie (27)",
         ranges=[(144.39, 150.28, 144.44, 150.28)], hook=3, delivery=4),
    dict(id="ins-g28", source="dubs", title="Dogrywka shortów — hak: do tego nie potrzebujesz AI (28)",
         ranges=[(150.77, 155.02, 150.82, 155.02)], hook=3, delivery=4),
    dict(id="ins-g29", source="dubs", title="Dogrywka shortów — hak: przed i po (29)",
         ranges=[(154.95, 159.22, 155.00, 159.22)], hook=3, delivery=4),
    dict(id="ins-g30", source="dubs", title="Dogrywka shortów — hak: to nie jest magia (30)",
         ranges=[(159.35, 163.54, 159.40, 163.54)], hook=3, delivery=4),
    dict(id="ins-h31", source="dubs", title="Dogrywka shortów — koniec: cały odcinek, link w bio (31)",
         ranges=[(164.95, 170.80, 165.00, 170.80)], hook=3, delivery=4),
    dict(id="ins-h32", source="dubs", title="Dogrywka shortów — koniec: pełna historia na YouTube (32)",
         ranges=[(171.25, 174.38, 171.30, 174.38)], hook=3, delivery=4),
    dict(id="ins-h33", source="dubs", title="Dogrywka shortów — koniec: ile to trwało u Ciebie (33)",
         ranges=[(175.03, 178.62, 175.08, 178.62)], hook=3, delivery=4),
    dict(id="ins-h35", source="dubs", title="Dogrywka shortów — koniec: zapisz sobie (35)",
         ranges=[(183.47, 187.10, 183.52, 187.10)], hook=3, delivery=4),
    dict(id="ins-yt-sub", source="dubs", title="Dogrywka: subskrypcja (37) — plansza z logo YouTube i kliknięciem",
         ranges=[(188.09, 195.98, 188.14, 195.98)], hook=3, delivery=4),
    dict(id="ins-case-6", source="dubs", title="Dogrywka: łącznik case'u (6)",
         ranges=[(67.67, 75.00, 67.72, 75.00)], hook=3, delivery=4),
    dict(id="ins-case-7", source="dubs", title="Dogrywka: łącznik case'u (7)",
         ranges=[(75.46, 81.51, 75.51, 81.51)], hook=3, delivery=4),
    dict(id="ins-case-8", source="dubs", title="Dogrywka: łącznik case'u (8)",
         ranges=[(81.95, 87.42, 82.00, 87.42)], hook=3, delivery=4),
    dict(id="ins-case-9", source="dubs", title="Dogrywka: łącznik case'u (9)",
         ranges=[(87.47, 93.06, 87.52, 93.06)], hook=3, delivery=4),
    dict(id="ins-case-10", source="dubs", title="Dogrywka: łącznik case'u (10)",
         ranges=[(94.35, 99.40, 94.40, 99.40)], hook=3, delivery=4),
    dict(id="ins-case-11", source="dubs", title="Dogrywka: łącznik case'u (11)",
         ranges=[(99.51, 105.52, 99.56, 105.52)], hook=3, delivery=4),
    dict(id="ins-case-12", source="dubs", title="Dogrywka: łącznik case'u (12)",
         ranges=[(105.65, 109.38, 105.70, 109.38)], hook=3, delivery=4),
]

# ── Starsze odcinki kanału (Youtube Projects) — dołożone 11.10.2026 ─────────
# Te same warunki nagrania (zielone polo, 720p), ale osobne pliki. Decyzje dubli po transkrypcji.
# S12 „Jak składam moduł” istnieje w dwóch plikach: budowanie (cz. 1, od 8:00 obraz rozmyty)
# i dogrywka (cz. 2) — pełny odcinek skleja compile_episode.py z ep-module-1 + ep-module-2.
# S11 „Claude vs Open Mercato”: czysta wersja to „odcinek-cloud vs openmerrcaot.mov”;
# stary plik ma rozmyty obraz 7:19–13:39 i zostaje poza biblioteką.
EPISODES += [
    dict(id="ep-vibecoding", source="vibecoding", client="(kanał)",
         title="Vibe coding vs framework: dlaczego system z agentem sypie się na produkcji",
         # poprawki Mateusza 12.10: drugi dubel „bo dowolna zmiana” (161,5), czysta druga próba
         # „o cokolwiek go poprosisz” (226,4), trzecia próba „architektonicznych” (250,55), bez ciszy
         # przed „Open Mercato”, bez „Druga rzecz.” (wycieranie twarzy), „gliniane, | ale są to mocne”,
         # bez ogona porzuconej próby przed „Pomogę zrozumieć”, zakończenie „do usłyszenia” z 697 s;
         # 22.10 (uwagi 3:18/3:19): po „rzecz,” od razu „prze…” falstartu (268,95), druga próba od dołka
         # przed „przez” (270,57, nie w środku głoski), „odcinek.” z wybrzmieniem (272,95)
         ranges=[(27.5, 85.0), (89.8, 156.4, None, 156.48), (156.4, 211.6, 161.50, None), (212.7, 214.85, None, 215.15),
                 (221.4, 249.5, 226.40, 249.08), (249.5, 264.0, 250.55, None), (267.5, 268.95, None, 268.95), (270.4, 272.95, 270.57, 272.95), (279.3, 388.2, 279.62, None),
                 (415.2, 442.6, None, 442.55), (450.4, 462.3), (464.0, 469.9), (502.4, 512.5),
                 (523.3, 528.9), (539.8, 574.5), (577.7, 592.6), (637.2, 673.3, None, 673.30), (677.5, 687.4, 677.58, None),
                 (697.0, 716.2)],
         hook=4, delivery=3, brand="flowbiz",
         notes="Kolega zrobił system z Codexem — dane w pamięci przeglądarki. Magiczne pierwsze sesje, "
               "paczki, które ze sobą nie gadają, AI przyznaje Ci rację, framework we frameworku, "
               "trzy uczciwe zastrzeżenia, puenta: AI obniżyło barierę budowania, nie projektowania."),
    # noc 04.11: druga część „…w głowie właściciela” kończy się w 253,4 — start od „bo” (253,48),
    # inaczej w gotowym pliku zostaje „właściciela. Właściciela.” (sprawdzone sklejką + transkrypcją)
    dict(id="ep-module-1", source="module-build", client="(kanał)", title="Jak składam moduł — cz. 1",
         ranges=[(65.9, 92.0), (104.0, 108.2), (128.4, 161.5), (185.3, 226.3), (226.8, 250.0, None, 249.95), (253.1, 267.3, 253.48, None),
                 (293.4, 304.3), (306.3, 360.9), (365.4, 380.3), (384.9, 404.8), (456.4, 468.4)],
         hook=4, delivery=3, brand="flowbiz",
         notes="Kartka papieru zamiast kodu, warsztat 6 h z ~70 pytaniami po rolach, droga zamówienia "
               "przez firmę, nagrana rozmowa z programistą → specyfikacja."),
    dict(id="ep-module-2", source="module-retake", client="(kanał)", title="Jak składam moduł — cz. 2",
         ranges=[(71.6, 93.5), (94.7, 98.2), (105.1, 131.3), (202.9, 241.6), (256.2, 400.6)],
         hook=3, delivery=3, brand="flowbiz",
         notes="Trzy warstwy specyfikacji (40 minut dziennie, 3 faktury), słownik pojęć, checklista, "
               "trafność 70–90%, granice modułu, wzorce vs wyjątki, powtarzalność, CTA w komentarzu."),
]

CHAPTERS += [
    # Claude vs Open Mercato
    dict(id="ch-vibe-1-baza-danych", source="vibecoding", parent="ep-vibecoding",
         title="Wyczyści cache i system znika", ranges=[(27.5, 68.3)], hook=5, delivery=4, cta="none"),
    dict(id="ch-vibe-2-magiczne-sesje", source="vibecoding", parent="ep-vibecoding",
         title="Dwie magiczne sesje z agentem", ranges=[(109.1, 156.4, None, 156.48), (156.4, 173.0, 161.50, None)], hook=4, delivery=4, cta="none"),
    dict(id="ch-vibe-3-przyznaje-racje", source="vibecoding", parent="ep-vibecoding",
         title="AI zawsze przyzna Ci rację", ranges=[(210.3, 214.85, None, 215.15), (221.4, 249.5, 226.40, 249.08), (249.5, 264.0, 250.55, None)], hook=5, delivery=3,
         cta="none"),
    dict(id="ch-vibe-4-framework", source="vibecoding", parent="ep-vibecoding",
         title="Framework we frameworku", ranges=[(279.3, 327.2, 279.62, None)], hook=3, delivery=4, cta="none"),
    dict(id="ch-vibe-5-gliniane-nogi", source="vibecoding", parent="ep-vibecoding",
         title="System na glinianych nogach", ranges=[(415.2, 442.6, None, 442.55), (450.4, 462.3)], hook=4, delivery=4,
         cta="none"),
    dict(id="ch-vibe-6-puenta", source="vibecoding", parent="ep-vibecoding",
         title="Bariera budowania spadła, projektowania nie", ranges=[(539.8, 574.5)], hook=5, delivery=4,
         cta="none"),
    dict(id="ch-vibe-7-nie-dla-kazdego", source="vibecoding", parent="ep-vibecoding",
         title="Czego nie powie Ci sprzedawca oprogramowania",
         ranges=[(366.4, 388.2), (464.0, 469.9), (502.4, 512.5)], hook=4, delivery=3, cta="none"),
    # Jak składam moduł
    dict(id="ch-module-1-kartka", source="module-build", parent="ep-module",
         title="Zanim napiszę linię kodu, biorę kartkę",
         # 17.11 (Agata, 0:01): „Zanim, zanim napiszę” — start od drugiego „Zanim” (cisza 66,84–66,94)
         ranges=[(65.9, 92.0, 66.90, None), (104.0, 108.2)],
         caption_words=[(65.9, 67.0, [("Zanim", 66.92, 67.26), ("napiszę", 67.26, 67.76)])],
         hook=5, delivery=4, cta="none"),
    dict(id="ch-module-2-druga-strona", source="module-build", parent="ep-module",
         title="Warsztat: 70 pytań po rolach", ranges=[(145.0, 160.7), (189.4, 220.5)], hook=4, delivery=4,
         cta="none"),
    dict(id="ch-module-3-wtorek-rano", source="module-build", parent="ep-module",
         title="Co robisz rękami we wtorek rano?", ranges=[(220.6, 250.0, None, 249.95), (253.1, 267.3), (293.4, 304.3)], hook=4, delivery=3,
         cta="none"),
    dict(id="ch-module-4-droga-kartki", source="module-build", parent="ep-module",
         title="Jedną kartkę dotyka kilkanaście osób", ranges=[(306.3, 360.9)], hook=4, delivery=4, cta="none"),
    dict(id="ch-module-5-nagraj-rozmowe", source="module-build", parent="ep-module",
         title="Nagraj rozmowę z programistą", ranges=[(365.4, 380.3), (384.9, 404.8)], hook=4, delivery=3,
         cta="none"),
    dict(id="ch-module-6-40-minut", source="module-retake", parent="ep-module",
         title="Problem w liczbach: 40 minut dziennie", ranges=[(105.1, 131.3), (202.9, 217.4)],
         hook=4, delivery=3, cta="none"),
    dict(id="ch-module-7-slownik", source="module-retake", parent="ep-module",
         title="Zamówienie u handlowca ≠ zamówienie na produkcji", ranges=[(218.7, 241.6)],
         hook=4, delivery=4, cta="none"),
    dict(id="ch-module-8-70-90", source="module-retake", parent="ep-module",
         title="Dobra specyfikacja = 70–90% trafności", ranges=[(256.2, 314.0)], hook=4, delivery=3,
         cta="none"),
    dict(id="ch-module-9-wyjatki", source="module-retake", parent="ep-module",
         title="On zna wzorce, Ty znasz wyjątki", ranges=[(314.4, 344.5)], hook=5, delivery=4, cta="none"),
    dict(id="ch-module-10-powtarzalnosc", source="module-retake", parent="ep-module",
         title="Jedno słowo: powtarzalność", ranges=[(346.4, 400.6)], hook=4, delivery=4, cta="comment"),
    # Po co Open Mercato (S-10, odcinek już opublikowany)
    dict(id="ch-om-1-co-tu-wow", source="om-intro", parent="ep-om-intro",
         title="„Co tu jest takiego wow?”", ranges=[(30.3, 57.2), (66.1, 76.2)], hook=5, delivery=4, cta="none"),
    dict(id="ch-om-2-excel-wersje", source="om-intro", parent="ep-om-intro",
         title="Ten sam Excel w kilku wersjach", ranges=[(168.0, 202.9), (220.1, 227.3), (235.4, 256.9)],
         hook=5, delivery=3, cta="none"),
    dict(id="ch-om-3-dwa-zdania", source="om-intro", parent="ep-om-intro",
         title="Dwa zdania dla właściciela", ranges=[(261.0, 268.4), (282.6, 315.8)], hook=4, delivery=3,
         cta="none"),
    dict(id="ch-om-4-nie-zapier", source="om-intro", parent="ep-om-intro",
         title="To nie jest Make, n8n ani Zapier", ranges=[(325.4, 342.5), (364.3, 371.2)], hook=4, delivery=4,
         cta="none"),
    dict(id="ch-om-5-erp-lat-90", source="om-intro", parent="ep-om-intro",
         title="ERP z lat 90. i jedno pole za duże pieniądze",
         # 17.11 (Agata, 0:00): start był w połowie zdania („…były systemy klasy ERP”) — od „A drugą stroną były systemy” (469,06)
         ranges=[(468.6, 509.1, 469.06, None), (519.9, 532.7)],
         caption_words=[(468.5, 469.3, [("A", 469.06, 469.24), ("drugą", 469.24, 469.48)])],
         hook=4, delivery=3, cta="none"),
    dict(id="ch-om-6-najtrudniejsze", source="om-intro", parent="ep-om-intro",
         title="Najtrudniejsze rzeczy w programowaniu już są", ranges=[(550.6, 579.3), (588.8, 593.9)],
         hook=4, delivery=3, cta="none"),
    dict(id="ch-om-7-trzy-zarzuty", source="om-intro", parent="ep-om-intro",
         title="Po co framework, skoro AI pisze kod?", ranges=[(626.3, 667.5)], hook=5, delivery=4, cta="none"),
    dict(id="ch-om-8-komu-odradzam", source="om-intro", parent="ep-om-intro",
         title="Komu odradzam Open Mercato",
         # 17.11 (pkt 9): bez „Nie masz ograniczeń na użytkowników.” — zaleta wciśnięta w listę powodów, żeby nie wdrażać
         ranges=[(697.2, 732.4, None, 732.29), (734.5, 746.5, 734.70, None)], hook=5, delivery=4, cta="none"),
    dict(id="ch-om-9-cztery-branze", source="om-intro", parent="ep-om-intro",
         title="Cztery branże, jeden fundament", ranges=[(850.0, 871.95), (887.7, 906.1)], hook=3, delivery=3,
         cta="none"),
    dict(id="ch-om-10-excel-dziala", source="om-retake", parent="ep-om-intro",
         title="Excel działa. Po co mi Open Mercato?", ranges=[(314.1, 357.4)], hook=5, delivery=4,
         cta="youtube"),
    dict(id="ch-om-11-spolecznosc", source="om-retake", parent="ep-om-intro",
         title="WMS i kalendarz w dwa tygodnie", ranges=[(448.0, 481.0), (490.5, 499.5), (532.7, 543.0)],
         hook=4, delivery=3, cta="none"),
]
