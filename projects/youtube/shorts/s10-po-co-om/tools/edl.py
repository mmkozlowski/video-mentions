#!/usr/bin/env python3
"""EDL etapu 2 — fragmenty, plan zoomów i nakładki czterech shortów.

Czasy fragmentów i zoomów są w sekundach ODCINKA ŹRÓDŁOWEGO (granice na
znacznikach słów z build/work/episode.json). Nakładki (plansze, plakietki,
tytuł) są w sekundach OSI SHORTA — przelicza je src_to_short().

Zoom: statyczny, różny w sąsiednich ujęciach — cięcie czyta się jak zmiana
kamery, nie jak przeskok (reguła z `projects/shorts IG`). Przełączenia siedzą
na początkach zdań. Na wypalonych plancszach/przebitkach odcinka zoom stoi
na 1.0 — tam kadr komponował już montaż odcinka.
"""

SOURCE = ("/Users/mac/Youtube Projects/S-10 - czym jest OM/Postprodukcja/"
          "Odcinek-PO_CO_OPEN_MERCATO.mp4")

SRC_W, SRC_H = 3840, 2160
W, H, FPS = 1080, 1920, 30
FACE_Y = 680          # środek twarzy w pionie źródła — zoom trzyma go w miejscu
CROP_W = 1214         # 9:16 z pełnej wysokości 2160
CROP_X = 1313         # (3840-1214)/2 — mówca siedzi na osi kadru

WIDE, CLOSE, TIGHT = 1.0, 1.18, 1.30
SCREEN = "screen"     # spany ze screencastem: pełny kadr 16:9 + blur-fill,
                      # nie pionowy crop — w cropie ze strony widać pasek
                      # (.ai/memory/shorty-studyjne-vs-reelsy-ig)

# key -> dict(title, fragments, zooms)
# fragments: [(start, end)]              — co wchodzi i w jakiej kolejności
# zooms:     [(start, end, zoom)]        — muszą dokładnie pokrywać fragmenty
SHORTS = {
    "s1-po-co-skoro-excel-dziala": dict(
        title="Po co Ci Open Mercato, skoro Excel działa?",
        fragments=[(0.00, 36.90), (39.94, 62.55)],
        zooms=[
            (0.00, 12.68, WIDE),    # hook: pochwała konkurencji
            (12.68, 17.40, CLOSE),  # „więc po co Wam i mi Open Mercato?"
            (17.40, 25.64, WIDE),   # odpowiedź
            (25.64, 36.90, CLOSE),  # „systemu, który jest dopasowany…"
            (39.94, 47.76, WIDE),   # „nie jest magicznym przyciskiem"
            (47.76, 54.56, CLOSE),  # „to jest fundament…"
            (54.56, 62.55, TIGHT),  # finał: „dla Twojego biznesu"
        ],
    ),
    "s2-ten-sam-excel-w-kilku-wersjach": dict(
        title="Wchodzę do firm i widzę Excela",
        fragments=[(175.16, 203.35), (237.30, 257.50)],
        zooms=[
            (175.16, 181.76, WIDE),   # „wchodzę do firm…"
            (181.76, 185.45, CLOSE),  # „ten sam plik w kilku wersjach"
            (185.45, 203.35, WIDE),   # wypalona plansza → nasza animacja
            (237.30, 248.74, CLOSE),  # „to nie jest wina ludzi…"
            (248.74, 257.50, TIGHT),  # „te dane trzeba scentralizować"
        ],
    ),
    "s3-komu-odradzam": dict(
        title="Komu ODRADZAM Open Mercato",
        fragments=[(546.65, 595.85)],
        zooms=[
            (546.65, 551.25, CLOSE),  # hook „komu to odradzam?"
            (551.25, 559.15, WIDE),   # wypalona przebitka (biuro, klawiatura)
            (559.15, 566.66, CLOSE),  # „wystarczy jeden programista…"
            (566.66, 576.52, WIDE),   # „utrzymanie po Twojej stronie"
            (576.52, 580.15, CLOSE),  # „płacisz mniej i martwisz się sam"
            (580.15, 593.95, SCREEN),  # screencast: pełny kadr 16:9 + blur-fill
            (593.95, 595.85, CLOSE),  # „nie na ryzykownym etapie"
        ],
    ),
    "s4-sto-procent-dostepu-do-kodu": dict(
        title="Co tu jest wow? 100% dostępu do kodu",
        fragments=[(116.20, 146.95), (296.90, 310.78), (280.30, 287.30)],
        zooms=[
            (116.20, 129.06, WIDE),   # anegdota (tytuł na wierzchu)
            (129.06, 133.29, CLOSE),  # „bardzo dobre pytanie…"
            (133.29, 140.82, WIDE),   # wypalona plansza → nasza animacja
            (140.82, 146.95, CLOSE),  # „nie zajrzysz, nie nadpiszesz…"
            (296.90, 310.78, WIDE),   # wypalone plansze Make/n8n — zostają
            (280.30, 287.30, TIGHT),  # finał: „kupują własność kodu"
        ],
    ),
}


# ── Cold-open: pytanie-hook na rozmytym kadrze ZANIM zacznie się mowa ─────
# (uwaga Mateusza: tytuł równoległy do napisów się zlewał; wzór = otwarcie s4)
INTRO_DUR = 1.35
INTRO = {
    "s1-po-co-skoro-excel-dziala": dict(
        kicker="SZCZERZE O OPEN MERCATO",
        lines=["Po co Ci to,", "skoro Excel działa?"]),
    "s2-ten-sam-excel-w-kilku-wersjach": dict(
        kicker="WCHODZĘ DO FIRM I WIDZĘ",
        lines=["Ten sam Excel.", "Kilka wersji."]),
    "s3-komu-odradzam": dict(
        kicker="UCZCIWIE",
        lines=["Komu ODRADZAM", "Open Mercato?"]),
    "s4-sto-procent-dostepu-do-kodu": dict(
        kicker="KOLEGA PROGRAMISTA PYTA",
        lines=["„Co tu jest wow?”"]),
}

# ── Stemple kinetyczne: duże hasła w różnych miejscach/rozmiarach ─────────
# (czas na OSI SHORTA sprzed intro; assemble dolicza intro sam)
# (tekst, t0, t1, y, rozmiar, rotacja stopni)
STAMPS = {
    "s1-po-co-skoro-excel-dziala": [
        ("WŁASNY SYSTEM", 23.00, 25.60, 330, 96, -2),
        ("FUNDAMENT", 44.80, 48.30, 330, 110, 2),
    ],
    "s2-ten-sam-excel-w-kilku-wersjach": [
        ("KILKANAŚCIE EXCELI", 2.40, 6.10, 330, 84, -2),
        ("SCENTRALIZOWAĆ", 44.80, 48.20, 330, 88, 2),
    ],
    "s3-komu-odradzam": [
        ("UTRZYMANIE? TWOJE.", 23.40, 27.00, 290, 84, -2),
    ],
    "s4-sto-procent-dostepu-do-kodu": [
        ("„Claude i tak wchodzi w kod”", 8.00, 12.60, 310, 64, -2),
        ("WŁASNOŚĆ KODU", 44.90, 47.80, 330, 100, 2),
    ],
}


def src_to_short(key, t):
    """Sekunda źródła → sekunda osi shorta (t musi leżeć w którymś fragmencie)."""
    offset = 0.0
    for a, b in SHORTS[key]["fragments"]:
        if a - 1e-6 <= t <= b + 1e-6:
            return offset + (t - a)
        offset += b - a
    raise ValueError(f"{t}s poza fragmentami {key}")


def short_len(key):
    return sum(b - a for a, b in SHORTS[key]["fragments"])


def validate():
    for key, s in SHORTS.items():
        frags = s["fragments"]
        zooms = s["zooms"]
        zi = 0
        for a, b in frags:
            cursor = a
            while cursor < b - 1e-6:
                za, zb, _ = zooms[zi]
                assert abs(za - cursor) < 1e-6, \
                    f"{key}: zoom zaczyna się w {za}, fragment czeka w {cursor}"
                assert zb <= b + 1e-6, f"{key}: zoom {za}-{zb} wystaje poza {b}"
                cursor = zb
                zi += 1
        assert zi == len(zooms), f"{key}: nadmiarowe zoomy od {zooms[zi]}"


validate()

if __name__ == "__main__":
    for key in SHORTS:
        n = len(SHORTS[key]["zooms"])
        print(f"{key}  {short_len(key):5.1f}s  {n} ujęć zoomu")
