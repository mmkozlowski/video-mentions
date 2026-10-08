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
         ranges=[(730.5, 733.9), (737.0, 784.0)], hook=5, delivery=4, cta="none",
         notes="Mateusz poprawił się na nagraniu: 6 godzin, nie 3 — zostawiony dubel z 6 h. "
               "Zaproszenie bez telefonu."),
    dict(n=12, code="R2", title="Zeszyt i emerytura", brand="flowbiz", block="production",
         ranges=[(784.0, 838.0)], hook=5, delivery=4, cta="web",
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
         ranges=[(1955.8, 1990.9)], hook=5, delivery=4, cta="aislupsk",
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
         ranges=[(2225.9, 2249.6), (2254.7, 2278.0)], hook=5, delivery=3, cta="web"),
    dict(n=34, code="E4", title="Gdzie AI ma sens — 3 na tak, 3 na nie", brand="flowbiz", block="extra",
         ranges=[(2282.8, 2319.0)], hook=4, delivery=5, cta="none",
         notes="Jedno czyste ujęcie, pointa „AI przygotowuje, człowiek decyduje”."),
    dict(n=35, code="W9", title="Umowa w ChatGPT", brand="aislupsk", block="extra",
         ranges=[(2324.2, 2371.0)], hook=5, delivery=4, cta="aislupsk"),
    dict(n=36, code="W7", title="Przynieś swój problem", brand="aislupsk", block="extra",
         ranges=[(2377.4, 2415.0)], hook=4, delivery=4, cta="aislupsk",
         notes="Region w nagraniu: Słupsk, Gdańsk i okolice."),
]

# ── Pełne odcinki case study (16:9, YouTube) ────────────────────────────────
# Nazwy klientów tylko tu, wewnętrznie. Na nagraniach nazwy nie padają.
EPISODES = [
    dict(id="ep-doram", source="doram", client="Doram", title="Meble ogrodowe: zamówienia z Niemiec",
         ranges=[(6.0, 688.0)], hook=3, delivery=3, brand="flowbiz",
         notes="Zamówienia od niemieckich kontrahentów w Excelu, dopasowanie AI 70% → 94% "
               "po miesiącu, kody kreskowe z kilku dni do 15 minut. Restart zdania w 92 s."),
    dict(id="ep-vacuactiv", source="vacuactiv", client="Vacuactiv", title="Agent AI dla właściciela firmy",
         ranges=[(7.0, 1126.0)], hook=3, delivery=3, brand="flowbiz",
         notes="Sprzęt sportowy z okolic Słupska. ChatGPT gubi kontekst → mózg firmy "
               "(100–150 GB danych), Open Mercato na produkcji, brief w Telegramie, "
               "Obsidian + Hermes + Codex. Najdłuższy, do skrócenia w montażu."),
    dict(id="ep-open-mercato-offers", source="session", client="(wiele)",
         title="8 wdrożeń Open Mercato — oferty", ranges=[(2557.1, 2767.6)], hook=3, delivery=3,
         brand="flowbiz",
         notes="Krótki odcinek: chaos w ofertach, konwersja handlowców, asystent czytający maile "
               "(producent sprzętu sportowego) — oferta w 5 min zamiast kilkunastu godzin."),
    dict(id="ep-rezon", source="session", client="Rezon",
         title="Pamiątki znad morza: system B2B", ranges=[(2767.6, 3226.0)], hook=3, delivery=3,
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
    dict(id="ch-vacu-1-chatgpt-zapomina", source="vacuactiv", parent="ep-vacuactiv",
         title="ChatGPT przestaje pamiętać Twoje wytyczne", ranges=[(38.5, 124.6)], hook=5, delivery=3),
    dict(id="ch-vacu-2-dane-w-glowach", source="vacuactiv", parent="ep-vacuactiv",
         title="Dane w głowach, na kartkach, w mailach", ranges=[(131.8, 210.1)], hook=4, delivery=3),
    dict(id="ch-vacu-3-mozg-firmy", source="vacuactiv", parent="ep-vacuactiv",
         title="Mózg firmy ze 150 GB danych", ranges=[(210.1, 284.3)], hook=4, delivery=4),
    dict(id="ch-vacu-4-duze-systemy", source="vacuactiv", parent="ep-vacuactiv",
         title="Dlaczego duże systemy się nie wdrażają", ranges=[(344.5, 438.4)], hook=4, delivery=3),
    dict(id="ch-vacu-5-kierownik-w-godzine", source="vacuactiv", parent="ep-vacuactiv",
         title="Kierownik produkcji nauczył się w godzinę", ranges=[(438.4, 563.8)], hook=4, delivery=3),
    dict(id="ch-vacu-6-brief-telegram", source="vacuactiv", parent="ep-vacuactiv",
         title="Zamówienie z Telegrama w trzy kliknięcia", ranges=[(563.8, 678.1)], hook=4, delivery=3),
    dict(id="ch-vacu-7-narzedzie-to-nie-wdrozenie", source="vacuactiv", parent="ep-vacuactiv",
         title="Licencja to nie wdrożenie", ranges=[(1063.9, 1100.1)], hook=4, delivery=3),
    dict(id="ch-offers-1-oferta-5-minut", source="session", parent="ep-open-mercato-offers",
         title="Oferta w 5 minut zamiast kilkunastu godzin", ranges=[(2703.0, 2767.6)], hook=5, delivery=4),
    dict(id="ch-rezon-1-ksiegowosc-po-fakcie", source="session", parent="ep-rezon",
         title="Dane z księgowości to dane po fakcie", ranges=[(2803.5, 2877.1)], hook=4, delivery=3),
    dict(id="ch-rezon-2-ustka-rowy", source="session", parent="ep-rezon",
         title="Tysiące sztuk z napisem „Ustka”", ranges=[(3052.8, 3116.4)], hook=4, delivery=3),
    dict(id="ch-rezon-3-panel-klienta", source="session", parent="ep-rezon",
         title="Klient sam składa zamówienie", ranges=[(3116.1, 3227.0)], hook=3, delivery=3),
    dict(id="ch-marpasz-1-cztery-worki", source="session", parent="ep-marpasz",
         title="Cztery worki paszy = cztery etykiety", ranges=[(3279.6, 3428.6)], hook=4, delivery=3),
    dict(id="ch-marpasz-2-100-godzin", source="session", parent="ep-marpasz",
         title="100 godzin miesięcznie mniej", ranges=[(3444.5, 3547.6)], hook=5, delivery=3),
    dict(id="ch-marpasz-3-katalog-ai", source="session", parent="ep-marpasz",
         title="Katalog AI: z faktury do Allegro", ranges=[(3557.2, 3679.6)], hook=4, delivery=3),
    dict(id="ch-marpasz-4-srubki", source="session", parent="ep-marpasz",
         title="AI to dokręcanie śrubek", ranges=[(3697.5, 3740.0)], hook=4, delivery=4),
]

RAW = [
    dict(id="raw-freestyle-workshop", source="session", title="Freestyle: bańka AI i strach",
         ranges=[(2424.6, 2548.0)], hook=3, delivery=2, brand="aislupsk",
         notes="Zaproszenie na warsztaty bez prompteru, urwane na fakturach. Do przebrania na cytaty."),
]
