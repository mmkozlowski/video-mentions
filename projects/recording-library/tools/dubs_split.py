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
YT = Path.home() / "orca/workspaces/Obsidian Vault/team/marketing/content/youtube"
LIST = YT / "2026-11-15-do-dogrania.md"            # 01–05
LIST_RETAKE = YT / "2026-11-20-do-dogrania-ponownie.md"  # 06–43, nagrane ponownie 20.11
MODEL = "mlx-community/whisper-large-v3-mlx"
HEAD, TAIL = 0.12, 0.30

# audyt 17.11 (silencedetect −40 dB): na początku pliku urywek poprzedniej mowy na poziomie mowy → start
# przesunięty o tyle sekund (≈80 ms przed silence_end), licząc od startu z cięcia po ciszy
TRIM_START = {5: 0.71}

# 01–05: pierwszy plik z 16.11 (oś 0–63,68 s). 06–43: nagranie 20.11 (oś od 65,68 s), okna z ciszy w sygnale
# (pauzy > 0,2 s poniżej −45 dB), bo czasy Whispera są przesunięte, a kwestie idą jedna po drugiej.
TAKES = {
    1: (5.6, 10.6, "pierwszy plik; drugie podejście ma „…przedstawię szybko”"),
    2: (17.5, 20.8, "są też wersje „nie przedłużając, wracam do naszego głównego tematu”"),
    3: (33.3, 37.3, ""),
    4: (38.8, 42.7, ""),
    5: (47.8, 50.4, "wcześniej wersja „dobra, wracamy szybko”"),
    6: (67.10, 74.95, "20.11"),
    7: (74.95, 81.50, "20.11"),
    8: (81.50, 87.30, "20.11"),
    9: (87.30, 93.20, "20.11"),
    10: (93.20, 99.40, "20.11; „producent” zamiast „hurtownia” (lista 20.11)"),
    11: (99.40, 105.50, "20.11"),
    12: (105.50, 109.50, "20.11"),
    13: (109.50, 118.50, "20.11; „…a nie na prezentacjach”"),
    14: (118.50, 124.90, "20.11"),
    15: (124.90, 132.50, "20.11; „będzie o tym” powiedziane 2× — w EDL sklejka; dopowiedziane „w swojej firmie”"),
    16: (209.90, 215.20, "20.11; wcześniej porzucone „ale zanim… część druga”"),
    17: (215.20, 217.70, "20.11"),
    18: (217.70, 221.40, "20.11"),
    19: (221.40, 225.20, "20.11"),
    20: (225.20, 229.80, "20.11"),
    21: (229.80, 235.00, "20.11"),
    22: (261.00, 266.10, "20.11, drugie podejście (pierwsze 235,0–240,7: „jak to wygląda u Was”)"),
    23: (132.50, 138.50, "20.11"),
    24: (138.70, 144.20, "20.11"),
    25: (241.00, 244.80, "20.11, pierwsze z trzech podejść"),
    26: (253.00, 258.00, "20.11"),
    27: (144.20, 150.40, "20.11; „…A to jest zupełnie niepotrzebne”"),
    28: (150.40, 155.00, "20.11; „…Naprawdę, serio.”"),
    29: (155.00, 159.30, "20.11"),
    30: (159.30, 163.40, "20.11"),
    31: (165.00, 171.00, "20.11"),
    32: (171.30, 174.50, "20.11"),
    33: (174.50, 178.60, "20.11, pierwsze podejście (drugie: „ile podobny proces trwa u Ciebie”)"),
    34: (274.00, 280.20, "20.11; falstart „w następnym… ale w następnym tygodniu” — zapas, nieużyta"),
    35: (183.10, 187.30, "20.11; „Zapisz to sobie, mam nadzieję, że Ci się przyda”"),
    36: (280.20, 287.20, "20.11"),
    37: (187.80, 196.00, "20.11"),
    38: (287.20, 293.60, "20.11"),
    39: (196.30, 204.60, "20.11"),
    40: (293.60, 299.20, "20.11"),
    41: (299.20, 307.60, "20.11"),
    42: (307.60, 313.50, "20.11"),
    43: (314.40, 319.20, "20.11; DO ODSŁUCHU: Whisper słyszy „podeźdź mu koniecznie ten film”"),
}


def norm(text):
    text = unicodedata.normalize("NFC", text.lower())
    return re.sub(r"[^\w ]", "", re.sub(r"\s+", " ", text)).strip()


def expected():
    """Tekst kwestii z listy do-dogrania (vault): „N. „…”” albo „N. **…**”."""
    out = {}
    for path, keep in ((LIST, range(1, 6)), (LIST_RETAKE, range(6, 44))):
        for line in open(path, encoding="utf-8"):
            m = re.match(r"^(\d+)\.\s+[„\"](.+?)[”\"]", line.strip())
            if m and int(m.group(1)) in keep:
                out[int(m.group(1))] = m.group(2).replace("**", "")
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
        if nr in TRIM_START:
            s += TRIM_START[nr]
            note = (note + "; " if note else "") + (f"audyt 17.11: przycięty początek o {TRIM_START[nr]:.2f} s "
                                                    "(urywek poprzedniej mowy na starcie)")
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
