#!/usr/bin/env python3
"""Lista montażowa shorta „Agenci pracowali całą noc" (9:16, 1080x1920).

Jedno miejsce, w którym siedzi decyzja „co zostaje". Czasy są liczone w
sekundach ŹRÓDŁA — tak jak leżą w transkrypcji z Whispera
(`build/work/IMG_*.json`). Wycinanie pauz w środku zakresu robi już `cut.py`
na podstawie pomiaru `silencedetect`, nie na podstawie tych liczb.

Reguła: jeden wpis = jedna myśl. Jeśli myśl trzeba przyciąć, przytnij zakres,
nie dopisuj drugiego wpisu na ten sam fragment.
"""

W, H, FPS = 1080, 1920, 30

# Poziomy wejściowe zmierzone volumedetect (mean_volume):
#   IMG_1602 -29.3 dB, IMG_1603 -28.7 dB, IMG_1605 -24.0 dB
# Wyrównujemy statycznym wzmocnieniem — loudnorm dopiero na gotowej ścieżce,
# bo zmienia długość strumienia (patrz .ai/memory/montaz-pulapki-synchronizacji).
# `silence_db` jest ZMIERZONY na pauzach każdego pliku, nie przepisany z tutoriala.
# Na biegu wiatr i oddech podbijają podłogę szumu do ok. -29 dB w szczycie, więc
# domyślne -34 dB nie wykryłoby ani jednej pauzy (sprawdzone — wynik: zero cięć).
SOURCES = {
    # gain_db  poziom  |  silence_db  szczyt szumu w pauzie  |  mowa (szczyt)
    "IMG_1601": dict(gain_db=+5.0, outdoor=True,  silence_db=-27),  # ścieżka, cień — bez mowy
    "IMG_1602": dict(gain_db=+5.3, outdoor=True,  silence_db=-27),  # -28,3 dB / -9,1 dB
    "IMG_1603": dict(gain_db=+4.7, outdoor=True,  silence_db=-27),  # -29,0 dB
    "IMG_1605": dict(gain_db=+0.0, outdoor=False, silence_db=-36),  # -37,7 dB
    # 1606: w pauzach stuka klawiatura i mysz (szczyt -15 dB przy średniej
    # -31 dB), więc próg musi być wyżej niż w 1605 mimo tych samych warunków.
    "IMG_1606": dict(gain_db=-1.0, outdoor=False, silence_db=-30),  # -23,0 dB
}

# Pauza dłuższa niż PAUSE_MAX zostaje skrócona do PAUSE_KEEP.
#
# Progi są ŁAGODNE z premedytacją. Przy 0,30 s każde sekundowe przemilczenie
# i każde zacięcie robiło osobne cięcie — pod koniec materiału obraz przez to
# skakał, bo krótkie ujęcia szły jedno za drugim. Materiał ma być autentyczny,
# a nie wygładzony: oddech i potknięcie w kadrze kosztują sekundę, a nienaturalny
# przeskok kosztuje wiarygodność całego ujęcia.
PAUSE_MAX = 1.10
PAUSE_KEEP = 0.24
# Margines, żeby cięcie nie zjadło spółgłoski na początku/końcu frazy.
EDGE_PAD = 0.06

# ── AKT 1 — bieg: hook i zapowiedź ────────────────────────────────────────
# ── AKT 2 — dom: dowód, co agenci zrobili przez noc ───────────────────────
#
# key:   identyfikator (nazwa pliku w build/cuts/)
# src:   plik źródłowy
# tin/tout: czas w źródle
# say:   co pada (do kontroli, nie do napisów — napisy liczymy z gotowej osi)
# zoom:  statyczne zbliżenie kadru; sąsiednie ujęcia dostają różne wartości,
#        żeby cięcie czytało się jak zmiana kamery, a nie jak przeskok. Kadr
#        zostaje 1080x1920 — powiększamy i przycinamy, NIGDY nie rozciągamy.
# yshift: przesunięcie środka kadrowania w dół (+) lub w górę (-), w pikselach
#        kadru wyjściowego. Przy zbliżeniu na gadaną głowę trzyma twarz w kadrze.
# lift:  True → materiał ciemny (ekran nocą, kontra pod słońce); podbija jasność
#        i kontrast, żeby na telefonie dało się to odczytać.
# pause_max: własny próg skracania pauz dla tego ujęcia. Domyślne 0,30 s jest pod
#        mowę; ujęcie, w którym najważniejsze jest to, co widać (ręka sięgająca
#        po jabłko), trzeba ciąć łagodniej, inaczej gest ginie w cięciu.

EDL = [
    # ── AKT 1 · bieg (IMG_1602 / IMG_1603) ────────────────────────────────
    dict(key="a01", src="IMG_1602", tin=0.00,   tout=3.90, zoom=1.00,
         say="No dobra, bieg już pogarnięty."),
    dict(key="a02", src="IMG_1602", tin=5.20,   tout=6.95, zoom=1.14, yshift=-90,
         say="Krótko, bo krótko — 20 minut."),
    dict(key="a03", src="IMG_1602", tin=7.80,   tout=11.60, zoom=1.00,
         say="Ale jestem ciekawy, co tam się dzieje przy komputerze,"),
    # tin=15.50, nie 13.68: między „komputerze" a „całą noc" jest 1,8 s samego
    # wiatru. `silencedetect` tego nie widzi (podmuch ma szczyt -14 dB, głośniej
    # niż niejedna sylaba), więc granicę wyznacza brak SŁÓW w transkrypcji,
    # nie brak sygnału.
    dict(key="a04", src="IMG_1602", tin=15.50,  tout=22.60, zoom=1.10, yshift=-70,
         say="Całą noc pracuje łącznie chyba sześciu takich asystentów "
             "na różnych projektach."),
    dict(key="a05", src="IMG_1602", tin=22.60,  tout=24.70, zoom=1.00,
         say="I już dochodzę do domu, i za chwilę wam"),
    dict(key="a06", src="IMG_1602", tin=27.88,  tout=32.90, zoom=1.12, yshift=-80,
         say="pokażę, co tacy agenci potrafią zrobić przez całą noc."),
    # Zakres do 15,05 s, bo dopiero w 14,2 s ręka sięga po jabłko — samo zdanie
    # kończy się w 12,74 s i przycięcie na nim ucinało puentę ujęcia.
    dict(key="a07", src="IMG_1603", tin=8.70,   tout=15.05, zoom=1.00,
         pause_max=0.80,
         say="O, tu jeszcze coś na deserek. [sięga po papierówki]"),

    # ── AKT 2 · dom, dowód pracy (IMG_1605) ───────────────────────────────
    # Zakres do 9,05 s: „dwóch kierowników" to żart o plecakach dzieciaków,
    # które są w kadrze — bez tego zdania widz ogląda pusty pokój.
    dict(key="b01", src="IMG_1605", tin=0.55,   tout=9.05, zoom=1.00,
         say="No dobra, zobaczmy, jak tam dzisiaj poszło. Tutaj dwóch kierowników "
             "pilnuje całego zamieszania — dopiero co z podróży."),
    dict(key="b02", src="IMG_1605", tin=14.40,  tout=22.85, zoom=1.08,
         say="Tutaj widać wyzwalacze, jakie działają w firmie i w tych agentach."),
    dict(key="b03", src="IMG_1605", tin=43.55,  tout=49.15, zoom=1.16, lift=True,
         say="Widzimy, co dany agent robił, ile tego zrobił, w jakich plikach."),
    dict(key="b04", src="IMG_1605", tin=61.90,  tout=65.35, zoom=1.00, lift=True,
         say="Odpalmy sobie ten efekt, który on zrobił przez całą noc."),
    dict(key="b05", src="IMG_1605", tin=79.30,  tout=91.30, zoom=1.10,
         say="Przez całą noc udało się agentowi na podstawie wszystkich notatek "
             "i spotkań, a było ich ponad pięć godzin."),
    dict(key="b06", src="IMG_1605", tin=92.10,  tout=98.80, zoom=1.00,
         say="Wiedzy sporo — i nie jest wymyślona przez AI, tylko oparta "
             "na naszych transkrypcjach i notatkach."),
    dict(key="b07", src="IMG_1605", tin=98.98,  tout=109.80, zoom=1.06,
         say="Powstał dosyć długi landing page, który będzie nam służył, "
             "żeby to posprzedawać kolejnym klientom."),
    dict(key="b08", src="IMG_1605", tin=116.85, tout=120.65, zoom=1.00,
         say="Nie jest źle. Jako punkt wyjścia jest całkiem fajnie."),
    dict(key="b09", src="IMG_1605", tin=128.05, tout=131.85, zoom=1.12,
         say="…do mojej strony od razu dodał wpis."),
    dict(key="b10", src="IMG_1605", tin=163.62, tout=166.70, zoom=1.00,
         say="W produkcji — czyli zostało to zaktualizowane, to już jest produkcyjnie."),
    dict(key="b11", src="IMG_1605", tin=183.60, tout=190.70, zoom=1.10,
         say="I co ciekawe, zostało dodane też logo firmy, u której to wdrożyliśmy."),
    dict(key="b12", src="IMG_1605", tin=193.10, tout=198.70, zoom=1.00,
         say="O, jest Opak Kreft. To jest to wdrożenie, które zostało zrobione."),

    # ── AKT 3 · trzeci dowód: fundamenty pod montaż YouTube (IMG_1606) ────
    # Blok domyka short lepiej niż „Opak Kreft": kończy się na „efekty nie
    # takie złe, ale wszystko trzeba sprawdzić", czyli prowadzi wprost
    # do pytania na planszy końcowej.
    dict(key="c01", src="IMG_1606", tin=7.90,  tout=15.10, zoom=1.00,
         say="To jest przygotowanie fundamentów pod to, żeby szybciej obrabiać "
             "moje nagrania na YouTube."),
    dict(key="c02", src="IMG_1606", tin=15.90, tout=20.90, zoom=1.10,
         say="Na razie wygląda to w ten sposób — kolorystyka, sceny, efekty."),
    dict(key="c03", src="IMG_1606", tin=30.20, tout=32.25, zoom=1.00,
         say="Jak widzicie, mam trzy odcinki przygotowane."),
    dict(key="c04", src="IMG_1606", tin=45.35, tout=53.30, zoom=1.08,
         say="Od razu gotowe grafiki — na ciemnym tle i na tak zwanym green, "
             "co pozwala szybciej to wyciąć."),
    dict(key="c05", src="IMG_1606", tin=53.26, tout=61.10, zoom=1.00,
         say="To też zostało zrobione przez całą noc, więc efekty nie takie złe."),
    dict(key="c06", src="IMG_1606", tin=62.78, tout=72.35, zoom=1.12,
         say="Oczywiście wszystko trzeba przejrzeć, sprawdzić, zweryfikować, "
             "żeby mieć pewność, że jest dobrze zrobione."),
]

# Fragment świadomie NIEUŻYTY, gotowy do wstawienia jednym wpisem:
#   IMG_1606 [81.80–95.26] — „jak będziecie mieli ochotę, przejdę przez te
#   wszystkie wyzwalacze i komendy, bo one pozwalają wejść na kolejny poziom
#   zarządzania firmą". To naturalne CTA własnymi słowami (13,5 s); alternatywa
#   dla planszy z pytaniem, jeśli finał ma być zaproszeniem zamiast napisu.

# Przebitki bez mowy — NIE stoją na osi czasu, wchodzą na wierzch cudzego
# dźwięku w etapie 2 (`assemble.py`). Dzięki temu nic nie kosztują z budżetu
# długości, a dają oddech tam, gdzie gadana głowa trwa najdłużej.
INSERTS = [
    dict(over="a04", at=4.2, dur=1.9, src="IMG_1601", tin=0.70,
         say="[przebitka] ścieżka, cień biegacza"),
]
