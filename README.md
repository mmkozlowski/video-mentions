# video-mentions

Produkcja wideo reklamowego — pipeline, materiał i wiedza. Jedno repo na wszystkie
projekty, żeby to, czego nauczyliśmy się na jednym kliencie, działało od razu na
następnym.

## Struktura

```
video-mentions/
├── .ai/                      ← WIEDZA CROSS-PROJECT
│   ├── MEMORY.md             indeks
│   ├── memory/               pułapki i ustalenia (jeden fakt na plik)
│   └── decisions/            ADR-y dotyczące metody, nie klienta
└── projects/
    ├── adresflow/            ← JEDEN PROJEKT
    ├── shorts IG/            ← shorty z telefonu; własny pipeline, patrz jego README
    └── granit/
        ├── ai/               decyzje i plany TEGO projektu
        ├── assets/           ŹRÓDŁA — nieodtwarzalne
        ├── screens/          ekrany produktu jako HTML (HyperFrames)
        ├── tools/            pipeline montażu (Python + ffmpeg)
        ├── build/            ROBOCZE — poza gitem
        └── final/            GOTOWE SPOTY — deliverable
```

## Co gdzie leży — reguła

Trzy kategorie, jedna zasada podziału: **czy da się to odtworzyć jednym poleceniem?**

| Katalog | Co tam jest | W gicie? | Dlaczego |
|---|---|---|---|
| `assets/` | ujęcia z generatora, lektorzy, zdjęcia, muzyka | **tak** | kosztowało kredyty albo przyszło od klienta — nie odtworzysz |
| `final/` | gotowe spoty z indeksem | **tak** | to jest produkt; ktoś ma je wziąć i wrzucić na TikToka |
| `build/` | złożone spoty, warstwy, cache ffmpeg, wyrenderowane ekrany | **nie** | odtwarzalne, ~400 MB, nadpisywane przy każdym renderze |

`build/` odtwarza się w całości:

```bash
cd projects/adresflow
./screens/render.sh          # ekrany produktu z HTML → build/screens/
python3 tools/brand.py       # plansze i warstwy napisów → build/overlays/
python3 tools/story.py       # montaż spotów → build/
python3 tools/finalize.py    # gotowe → final/ + README z indeksem
```

## Wiedza: ogólna kontra projektowa

Podział, który się utrzymuje, gdy dojdzie drugi klient:

- **`.ai/`** — rzeczy prawdziwe niezależnie od produktu: limity API generatora,
  jak nie zabić hooka, dlaczego lektor musi być jednym plikiem, jak renderować
  UI z HTML zamiast generować.
- **`projects/<nazwa>/ai/`** — rzeczy prawdziwe tylko tutaj: plan kampanii,
  realia branży klienta, ADR-y konkretnych spotów.

Reguła kciuka: jeśli zdanie zaczyna się od nazwy klienta, idzie do projektu.

## Nowy projekt

```bash
mkdir -p projects/<nazwa>/{ai/{decisions,plans},assets/{shots,voice,music,photos,reference},screens,tools,build,final}
cp -R projects/adresflow/tools/* projects/<nazwa>/tools/
```

Pipeline jest przenośny — wszystkie ścieżki liczą się względem katalogu projektu.
Do podmiany: paleta i fonty w `tools/brand.py`, słowniki `SHOTS` i `STORIES`
w `tools/story.py`.

## Projekty

| Projekt | Klient | Co to jest |
|---|---|---|
| `adresflow` | AdresFlow | wizualizacje nieruchomości — rzut 3D z kartki, home staging |
| `granit` | Granit Kończewo × FlowBiz AI | kampania sponsorska klubu; sponsor dostaje bezpłatny audyt AI |
| `shorts IG` | FlowBiz (kanał Mateusza) | pionowe shorty z nagrań telefonem — gadana głowa, przebitki, filmowany ekran |

## Powiązane repo

- `~/Repo/adresflow-v2` — aplikacja, której dotyczą spoty w `projects/adresflow/`.
  Tokeny marki (`apps/web/src/styles/legacy.css`) są tam źródłem prawdy; kopie
  w `screens/assets/app.css` trzeba synchronizować ręcznie po redesignie.
