#!/usr/bin/env python3
"""„Yyyy” i milczenie w środku słowa — tego transkrypcja nie widzi.

Whisper dokleja przeciągnięte „yyy” i pauzę do sąsiedniego słowa („wycen.” trwa 4,8 s),
więc cięcie po lukach między słowami (build_clips.tighten) ich nie łapie. Tu czytamy
samo audio co 20 ms:

- cisza: RMS poniżej SILENCE_DB przez co najmniej MIN_SILENCE,
- „yyy”: głos bez ani jednego spadku głośności (granicy sylaby) przez MIN_FILLER —
  normalna mowa ma takie spadki co 0,15–0,25 s, przeciągnięta samogłoska nie ma.

  python3 tools/fillers.py session 2717.8 2723     # podgląd wykrytych fragmentów
"""
import re
import subprocess
import sys

from sources import SOURCES

SILENCE_DB = -42.0
VOICE_DB = -35.0
SYLLABLE_DIP_DB = 5.0
MIN_SILENCE = 0.55     # jak MAX_PAUSE w build_clips — krótsza cisza to naturalny oddech
MIN_FILLER = 0.5
MARGIN = 0.08          # zostaje na brzegu wyciętego „yyy”, żeby nie uciąć spółgłoski
SILENCE_KEEP = 0.15    # z wyciętej ciszy zostaje oddech z obu stron


def levels(source, start, end):
    """[(czas, RMS dB)] co 20 ms dla przedziału źródła."""
    cmd = ["ffmpeg", "-hide_banner", "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}", "-i", str(SOURCES[source]),
           "-vn", "-ac", "1", "-ar", "16000", "-af",
           "aresample=16000,asetnsamples=n=320,astats=metadata=1:reset=1:measure_perchannel=RMS_level:measure_overall=none,"
           "ametadata=print:file=-", "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    rows, t = [], None
    for line in out.splitlines():
        m = re.match(r"frame:\d+\s+pts:\d+\s+pts_time:([\d.]+)", line)
        if m:
            t = float(m.group(1)) + start
            continue
        m = re.match(r"lavfi\.astats\.1\.RMS_level=(\S+)", line)
        if m and t is not None:
            rows.append((t, -120.0 if "inf" in m.group(1) else float(m.group(1))))
            t = None
    return rows


def runs(rows, inside):
    """Ciągłe odcinki, dla których inside(i) jest prawdą → [(od, do)]."""
    out, begin = [], None
    for i, (t, _) in enumerate(rows):
        if inside(i):
            begin = t if begin is None else begin
        elif begin is not None:
            out.append((begin, t))
            begin = None
    if begin is not None and rows:
        out.append((begin, rows[-1][0]))
    return out


def filler_spans(source, start, end):
    """Fragmenty do wycięcia (czas źródła), już z marginesem na brzegach."""
    rows = levels(source, start, end)
    db = [r[1] for r in rows]
    spans = [(a + SILENCE_KEEP - MARGIN, b - SILENCE_KEEP + MARGIN)
             for a, b in runs(rows, lambda i: db[i] < SILENCE_DB) if b - a >= MIN_SILENCE]
    # głos bez granicy sylaby: od ostatniego spadku głośność nie zjechała o SYLLABLE_DIP_DB
    begin, peak = None, None
    for i, (t, level) in enumerate(rows):
        if level < VOICE_DB or (peak is not None and level < peak - SYLLABLE_DIP_DB):
            if begin is not None and t - begin >= MIN_FILLER:
                spans.append((begin, t))
            begin, peak = None, None
            continue
        if begin is None:
            begin, peak = t, level
        peak = max(peak, level)
    if begin is not None and rows and rows[-1][0] - begin >= MIN_FILLER:
        spans.append((begin, rows[-1][0]))
    return sorted((round(a + MARGIN, 3), round(b - MARGIN, 3)) for a, b in spans if b - a > 2 * MARGIN)


MIN_PIECE = 0.3        # krótszy kawałek mowy między cięciami brzmi jak trzask — wtedy nie tniemy


def subtract(parts, spans):
    """Przedziały [od, do] minus wycinane fragmenty. Cięcie, które zostawiłoby kawałek
    krótszy niż MIN_PIECE, jest pomijane (lepsza krótka pauza niż urwana sylaba)."""
    out = []
    for a, b in parts:
        cursor = a
        for x, y in spans:
            x, y = max(x, a, cursor), min(y, b)   # nakładające się wycięcia (cisza + „yyy”) się sklejają
            if y <= x:
                continue
            if (0 < x - cursor < MIN_PIECE and x > a) or (b - y < MIN_PIECE and y < b):
                continue
            if x > cursor:
                out.append([round(cursor, 3), round(x, 3)])
            cursor = y
        if b > cursor:
            out.append([round(cursor, 3), round(b, 3)])
    return out


if __name__ == "__main__":
    src, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    for x, y in filler_spans(src, a, b):
        print(f"{x:9.2f} – {y:9.2f}  ({y - x:.2f} s)")
