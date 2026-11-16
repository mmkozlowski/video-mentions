#!/usr/bin/env python3
"""Short / rolka / zajawka + głos z dogrywek (16.11): hak na początku, zakończenie przed planszą końcową.

Mateusz 16.11: „przerób też shorty i reelsy”. Dogrywki G (haki na pierwsze 2 s) i H (zakończenia)
są nagrane raz; tu wklejamy je do gotowych renderów pionowych (reels 9:16, feed 4:5):

  [hak z dogrywki] → [short od pierwszej klatki] → [zakończenie z dogrywki] → [plansza końcowa shorta]

Zakończenie wchodzi po OSTATNIM słowie treści (Whisper na ogonie gotowego renderu), przed planszą
końcową z CTA — nigdy w środku słowa; plansza końcowa wraca już w pełni widoczna.

Dobór kwestii (prawda o treści shorta, vault marketing/content/youtube/2026-11-15-do-dogrania.md):
kwestia 26 („traciła kilka dni w miesiącu”) nie jest użyta — żadna liczba w shortach jej nie potwierdza.

  python3 tools/assemble_short.py                       # wszystkie z PLAN
  python3 tools/assemble_short.py ch-module-1-kartka    # jeden
"""
import json
import subprocess
import sys
from pathlib import Path

import package as P

FINAL = P.FINAL
MODEL = "mlx-community/whisper-large-v3-turbo"
FADE = 0.012

# short (storyboard) → (format, hak, zakończenie); None = bez wstawki
PLAN = {
    "ch-offers-1-oferta-5-minut--zajawka": ("feed", "ins-g29--offers", "ins-h32--feed"),     # 19.11
    "ch-doram-6-kody-15-minut": ("reels", "ins-g28--reels", "ins-h33--reels"),              # 22.11 — „żadnej magii, żadnego AI”
    "ch-doram-5-70-94--zajawka": ("feed", "ins-g30--doram", "ins-h32--feed"),               # 26.11
    "ch-module-1-kartka": ("reels", "ins-g30--module", "ins-h35--reels"),                   # 29.11
    "ch-rezon-2-ustka-rowy--zajawka": ("feed", "ins-g27--feed", "ins-h32--feed"),           # 03.12
    "ch-om-8-komu-odradzam": ("reels", None, "ins-h31--reels"),                             # 06.12 — hak tekstowy zostaje
    "ch-marpasz-2-100-godzin--zajawka": ("feed", "ins-g27--feed", "ins-h32--feed"),         # 10.12
    "zaj-8-wdrozen": ("feed", "ins-g28--feed", "ins-h32--feed"),                            # kody bez AI
}


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def end_card_len(board, fmt):
    return board.get("endcard", {}).get(fmt, {"ad": 3.5, "ad45": 3.5, "reels": 3.5, "youtube": 2.5, "feed": 3.5}[fmt])


def last_word_end(render, content_end, work):
    """Koniec ostatniego słowa treści (Whisper na ostatnich 8 s przed planszą końcową)."""
    start = max(0.0, content_end - 8.0)
    wav = work / "tail.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-t", f"{content_end - start:.3f}", "-i", str(render),
                    "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    subprocess.run(["mlx_whisper", str(wav), "--model", MODEL, "--language", "pl", "--word-timestamps", "True",
                    "--output-dir", str(work), "--output-format", "json"], check=True, capture_output=True)
    words = [w for s in json.load(open(work / "tail.json"))["segments"] for w in s.get("words", [])]
    return start + max(w["end"] for w in words) if words else content_end - 0.4


def insert_file(board_name, fmt):
    """Render wstawki nazywa się po KLIPIE (package.py), a plan wskazuje storyboard (ten sam klip, różne plansze)."""
    clip = json.load(open(P.PACK / "storyboards" / f"{board_name}.json"))["clip"]
    return FINAL / f"{clip}__{fmt}-F.mp4"


def build(name):
    fmt, hook, outro = PLAN[name]
    board = json.load(open(P.PACK / "storyboards" / f"{name}.json"))
    geo = P.FORMATS[fmt]
    render = FINAL / f"{name}__{fmt}-F.mp4"
    total = duration(render)
    content_end = total - end_card_len(board, fmt)
    work = P.BUILD / "work" / "shorts" / name
    work.mkdir(parents=True, exist_ok=True)
    spoken_end = last_word_end(render, content_end, work)
    # treść do końca (najwcześniej 0,05 s po ostatnim słowie, najpóźniej do startu planszy końcowej), potem wstawka,
    # a plansza końcowa wraca od momentu, gdy jest już w pełni widoczna (bez 0,35 s przenikania z treścią) —
    # w zajawkach mowa ciągnie się praktycznie do samej planszy („…dobrze pójdzie.” do 56,3 s przy końcu 56,33 s)
    cut = round(min(content_end, max(spoken_end + 0.05, content_end - 0.3)), 3)
    resume = round(content_end + 0.35, 3)
    segments = ([("file", insert_file(hook, fmt), 0.0, None)] if hook else []) + [("file", render, 0.0, cut)]
    if outro:
        segments.append(("file", insert_file(outro, fmt), 0.0, None))
    segments.append(("file", render, resume if outro else cut, total))
    inputs, graph, labels = [], "", []
    for i, (_, path, a, b) in enumerate(segments):
        b = duration(path) if b is None else b
        inputs += ["-i", str(path)]
        graph += (f"[{i}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30,scale={geo['w']}:{geo['h']},setsar=1[v{i}];"
                  f"[{i}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
                  f"afade=t=in:d={FADE},afade=t=out:st={max(0.0, b - a - FADE):.3f}:d={FADE}[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    graph += "".join(labels) + f"concat=n={len(segments)}:v=1:a=1[v][a]"
    out = FINAL / f"{name}__{fmt}-F--with-dubs.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
    print(f"{name}: hak {hook or '—'}, ostatnie słowo {spoken_end:.2f} s → cięcie {cut:.2f} s (plansza od {resume:.2f}), {outro or '—'} → {out.name} "
          f"({duration(out):.1f} s)")
    return out


if __name__ == "__main__":
    for name in (sys.argv[1:] or PLAN):
        build(name)
