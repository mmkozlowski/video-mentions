#!/usr/bin/env python3
"""Przegląd sklejonego odcinka (…__youtube-F--with-inserts.mp4) przed wystawieniem — 16.11.

Mateusz: „po zmontowaniu przejrzyj je jeszcze raz sam, oceń, znajdź błędy i zrób kolejną iterację”.
To narzędzie daje dwa dowody do oceny, oba z GOTOWEGO pliku (nie z planu):

1. arkusz klatek: każda wstawka na wejściu, w połowie i 0,4 s przed końcem + co 20 s treści
   → build/review/<odcinek>/klatki-N.jpg (po 12 klatek na arkusz, z czasem na klatce),
2. transkrypcja ±4 s wokół każdego łączenia (Whisper turbo) → urwane słowa, duble, cisza.

Punkty łączeń bierze z assemble_episode.plan_segments (te same, co poszło do sklejki).

  python3 tools/review_episode.py ep-open-mercato-offers
"""
import subprocess
import sys

import assemble_episode as A
from sources import BUILD

MODEL = "mlx-community/whisper-large-v3-turbo"


def joints(clip_id):
    _, segments, chapters = A.plan_segments(clip_id)
    t, out, marks = 0.0, [], []
    for seg in segments:
        length = seg[2] if seg[0] == "insert" else seg[2] - seg[1]
        name = seg[1] if seg[0] == "insert" else seg[0]
        out.append((round(t, 2), name))
        if seg[0] == "insert":
            marks += [(t + 0.3, name), (t + length / 2, name), (t + max(0.3, length - 0.4), name)]
        else:
            marks += [(x, name) for x in frange(t + 10, t + length - 2, 20)]
        t += length
    return out, sorted(marks), t


def frange(a, b, step):
    while a < b:
        yield a
        a += step


def main(clip_id):
    path = A.FINAL / f"{clip_id}__youtube-F--with-inserts.mp4"
    out = BUILD / "review" / clip_id
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*"):
        old.unlink()
    points, marks, total = joints(clip_id)
    frames = []
    for i, (t, name) in enumerate(marks):
        f = out / f"f{i:03d}.jpg"
        label = f"{int(t // 60)}\\:{t % 60:05.2f}  {name}"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(path), "-frames:v", "1", "-vf",
                        f"scale=640:-1,drawbox=y=0:w=iw:h=34:color=black@0.7:t=fill,"
                        f"drawtext=text='{label}':x=10:y=8:fontsize=20:fontcolor=white", str(f)],
                       check=False, capture_output=True)
        if not f.exists():   # ffmpeg bez drawtext (brak freetype) — klatka bez podpisu
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(path), "-frames:v", "1",
                            "-vf", "scale=640:-1", str(f)], check=True)
        frames.append(f)
    for n in range(0, len(frames), 12):
        chunk = frames[n:n + 12]
        while len(chunk) % 3:
            chunk.append(chunk[-1])
        rows = len(chunk) // 3
        inputs = sum((["-i", str(f)] for f in chunk), [])
        graph = "".join(f"[{3 * r}][{3 * r + 1}][{3 * r + 2}]hstack=3[r{r}];" for r in range(rows))
        graph += "".join(f"[r{r}]" for r in range(rows)) + (f"vstack={rows}" if rows > 1 else "null")
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph,
                        str(out / f"klatki-{n // 12 + 1}.jpg")], check=True)
    for f in frames:
        f.unlink()
    report = [f"{clip_id}: {total:.1f} s, {len(points)} kawałków"]
    for t, name in points[1:]:
        wav = out / "j.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, t - 4):.2f}", "-t", "8", "-i", str(path),
                        "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
        subprocess.run(["mlx_whisper", str(wav), "--model", MODEL, "--language", "pl", "--output-dir", str(out),
                        "--output-format", "txt"], check=True, capture_output=True)
        text = " ".join((out / "j.txt").read_text().split())
        report.append(f"{int(t // 60)}:{t % 60:05.2f} → {name:22} | {text}")
    for f in (out / "j.wav", out / "j.txt"):
        f.unlink(missing_ok=True)
    (out / "lacza.txt").write_text("\n".join(report) + "\n")
    print("\n".join(report))
    print(f"→ {out}")


if __name__ == "__main__":
    main(sys.argv[1])
