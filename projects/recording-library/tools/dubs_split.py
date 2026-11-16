#!/usr/bin/env python3
"""Dogrywki 16.11 → kwestie 01–43: raw/2026-11-16-dogrywki-audio/kwestie/NN.wav + mapa.csv.

Mateusz nie mówił numerów (czytał nazwy sekcji), więc wybór podejścia jest ręczny: TAKES niżej
(okno w osi dogrywki.wav z tools/dubs_ingest.py, czasy z transkrypcji large-v3-turbo). Granice
dociągane do ciszy w sygnale (RMS co 20 ms): start = początek pierwszego odcinka mowy w oknie
minus oddech, koniec = koniec ostatniego plus wybrzmienie, nigdy w środku mowy.

Każdy wycięty plik jest transkrybowany OSOBNO (Whisper large-v3, nie turbo) — ta transkrypcja
idzie do mapy i to ona jest podstawą audytu, nie okno z listy.

Zgodność: OK (te same słowa co na liście, poza interpunkcją), różnica (sens ten sam, inne
słowa — opisane w uwagach), brak (kwestii nie ma w nagraniu). Kwestii nie podmieniamy innymi.

  python3 tools/dubs_split.py          # wszystkie
  python3 tools/dubs_split.py 33 36    # tylko wskazane (reszta mapy bez zmian)
"""
import csv
import json
import re
import subprocess
import unicodedata
from pathlib import Path

from sources import SOURCES

RAW = SOURCES["dubs"].parent
WAV = RAW / "dogrywki.wav"
OUT = RAW / "kwestie"
LIST = Path.home() / "orca/workspaces/Obsidian Vault/team/marketing/content/youtube/2026-11-15-do-dogrania.md"
MODEL = "mlx-community/whisper-large-v3-mlx"
HEAD, TAIL = 0.12, 0.30

# nr → (od, do, uwaga) w osi dogrywki.wav; None = kwestii nie ma w nagraniu
TAKES = {
    1: (5.6, 10.6, "pierwszy plik; drugie podejście ma „…przedstawię szybko”"),
    2: (17.5, 20.8, "są też wersje „nie przedłużając, wracam do naszego głównego tematu”"),
    3: (33.3, 37.3, ""),
    4: (38.8, 42.7, ""),
    5: (47.8, 50.4, "wcześniej wersja „dobra, wracamy szybko”"),
    6: (66.7, 74.2, "główny plik, drugie podejście (pierwsze urwane na końcu pierwszego pliku)"),
    7: (74.2, 81.4, "drugie podejście: „ta sama firma i drugi case… generowanie dziesiątek kodów jednym kliknięciem”"),
    8: (99.0, 104.8, ""),
    9: (104.8, 111.3, "w nagraniu ciągnie dalej: „z ulotek i z dowolnego materiału… odczytywanie kodów kreskowych, składów…” — ucięte na „z faktur”"),
    10: (140.4, 147.0, "„z nadmorza” = „znad morza” (pisownia Whispera); w nagraniu ciągnie dalej: „a kilkudziesięciu handlowców musiało jeździć z pełnym dostawczakiem…” — ucięte (liczba handlowców do potwierdzenia)"),
    11: (158.2, 165.85, "drugie podejście: „…w swoim ukochanym Excelu. Najlepszy system ERP w naszych czasach, czyli Excel.”"),
    12: (179.9, 184.0, ""),
    13: (188.3, 197.2, "turbo słyszy „filmach”, large-v3 i medium: „firmach”"),
    14: (198.2, 203.4, ""),
    15: (204.2, 210.1, ""),
    16: (215.3, 220.2, "pierwsze podejście urwane („ale zanim do tego”)"),
    17: (222.0, 224.9, ""),
    18: (227.1, 231.0, ""),
    19: (232.8, 237.1, "dalej dopowiedziane „zapraszam Cię do mojego ekranu” — ucięte"),
    20: (241.0, 246.8, ""),
    21: (249.0, 255.9, ""),
    22: (271.5, 277.3, "DO ODSŁUCHU: large-v3 „w filmie”, medium „w firmie”"),
    23: (277.1, 284.5, ""),
    24: (285.4, 290.5, "drugie podejście dłuższe: „…kolejne wdrożenie, które w praktyce oszczędziło kilkadziesiąt godzin miesięcznie”"),
    25: (312.4, 317.3, "drugie podejście; pierwsze: „i to by było na tyle na dzisiaj…”"),
    26: (323.2, 327.0, "później improwizacja „firmy tracą kilkadziesiąt tysięcy, nawet do dziesięciu tysięcy miesięcznie” — NIE użyta (liczby się gryzą)"),
    27: (328.2, 332.3, ""),
    28: (333.4, 336.5, ""),
    29: (337.5, 340.9, "drugie podejście: „zobacz, jak wygląda AI przed i po, na konkretnych przykładach”"),
    30: (354.4, 359.8, ""),
    31: (378.9, 383.9, ""),
    32: (384.9, 388.7, "drugie podejście dłuższe: „a jeżeli zaciekawiła Cię ta zajawka…”"),
    33: (397.55, 403.0, "start za „…na YouTube” poprzedniej kwestii"),
    34: (415.4, 420.0, ""),
    35: (428.4, 431.8, ""),
    36: (450.1, 459.1, "DO ODSŁUCHU: large-v3 „w polskiej filmie”; pierwsze podejście dłuższe („…która przechodzi transformację i potrzebuje uporządkowania”)"),
    37: (467.6, 475.6, ""),
    38: (475.4, 481.4, ""),
    39: (481.2, 491.5, ""),
    40: (510.4, 515.6, "pierwsze podejście z dopowiedzeniem „bez przysypiania… halo halo, nie śpimy”"),
    41: (515.4, 523.5, "DO ODSŁUCHU: oba modele słyszą „nazwy film nie podaję” (lista: „nazw firm nie podaję”)"),
    42: (526.8, 531.9, ""),
    43: (533.1, 538.1, ""),
}


def norm(text):
    text = unicodedata.normalize("NFC", text.lower())
    return re.sub(r"[^\w ]", "", re.sub(r"\s+", " ", text)).strip()


def expected():
    """Tekst kwestii z listy do-dogrania (vault): „N. „…”” albo „N. **…**”."""
    out = {}
    for line in open(LIST, encoding="utf-8"):
        m = re.match(r"^(\d+)\.\s+[„\"](.+?)[”\"]", line.strip())
        if m:
            out[int(m.group(1))] = m.group(2)
    return out


def levels(start, end):
    cmd = ["ffmpeg", "-hide_banner", "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}", "-i", str(WAV), "-ac", "1",
           "-af", "asetnsamples=n=960,astats=metadata=1:reset=1:measure_perchannel=RMS_level:measure_overall=none,"
           "ametadata=print:file=-", "-f", "null", "-"]
    rows, t = [], None
    for line in subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines():
        m = re.match(r"frame:\d+\s+pts:\d+\s+pts_time:([\d.]+)", line)
        if m:
            t = float(m.group(1)) + start
            continue
        m = re.match(r"lavfi\.astats\.1\.RMS_level=(\S+)", line)
        if m and t is not None:
            rows.append((t, -120.0 if "inf" in m.group(1) else float(m.group(1))))
    return rows


def snap(a, b):
    """Okno → granice z ciszy: pierwsza i ostatnia ramka mowy (> -42 dB) w oknie."""
    rows = levels(a, b)
    loud = [t for t, db in rows if db > -42]
    if not loud:
        return a, b
    return max(a, loud[0] - HEAD), min(b + 0.2, loud[-1] + 0.02 + TAIL)


def transcribe(path):
    subprocess.run(["mlx_whisper", str(path), "--model", MODEL, "--language", "pl", "--output-dir", str(path.parent),
                    "--output-format", "txt"], check=True, capture_output=True)
    txt = path.with_suffix(".txt")
    text = " ".join(txt.read_text().split())
    txt.unlink()
    return text


def main(only=()):
    OUT.mkdir(exist_ok=True)
    previous = {r["nr"]: r for r in json.load(open(OUT / "mapa.json"))} if only and (OUT / "mapa.json").exists() else {}
    want = expected()
    rows = []
    for nr in range(1, 44):
        if only and nr not in only and f"{nr:02d}" in previous:
            rows.append(previous[f"{nr:02d}"])
            continue
        take = TAKES.get(nr)
        exp = want.get(nr, "")
        if take is None:
            rows.append(dict(nr=f"{nr:02d}", plik="", start="", koniec="", transkrypt="", oczekiwany=exp,
                             zgodnosc="brak", uwagi="nie ma w nagraniu"))
            continue
        a, b, note = take
        s, e = snap(a, b)
        path = OUT / f"{nr:02d}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-t", f"{e - s:.3f}", "-i", str(WAV),
                        "-af", "afade=t=in:d=0.01,areverse,afade=t=in:d=0.04,areverse", "-ar", "48000", "-ac", "1",
                        str(path)], check=True)
        heard = transcribe(path)
        status = "OK" if norm(heard) == norm(exp) else "różnica"
        if note.startswith("DO ODSŁUCHU"):
            status = "do odsłuchu"
        rows.append(dict(nr=f"{nr:02d}", plik=f"kwestie/{path.name}", start=f"{s:.2f}", koniec=f"{e:.2f}",
                         transkrypt=heard, oczekiwany=exp, zgodnosc=status, uwagi=note))
        print(f"{nr:02d} {status:12} {e - s:5.2f} s  {heard}")
    with open(OUT / "mapa.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    json.dump(rows, open(OUT / "mapa.json", "w"), ensure_ascii=False, indent=1)
    print(f"→ {OUT / 'mapa.csv'}")


if __name__ == "__main__":
    import sys
    main({int(a) for a in sys.argv[1:]})
