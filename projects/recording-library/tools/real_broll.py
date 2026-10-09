#!/usr/bin/env python3
"""Prawdziwe przebitki (nie AI) — Słupsk nagrany telefonem przez Mateusza.

Źródła leżą poza repo (~/Youtube Projects/b-rolle), więc tu jest tylko przepis:
fragment → build/broll-real/<nazwa>.mp4, 1080p 30 kl./s, BEZ DŹWIĘKU (na IMG_8641
słychać dzieci), w SDR bt709.

iPhone nagrywa w HDR (HLG, bt2020). HyperFrames po wykryciu takiego źródła przełącza CAŁY
klip na tryb HDR (16 bit, x265 slow) — render kilka razy wolniejszy, a kolory HDR na
zwykłym telefonie wyglądają źle. Ten ffmpeg nie ma zscale, więc tonemapping robi systemowy
avconvert (preset H.264 1920×1080 → bt709). W storyboardzie: {"type": "broll", "src": "build/broll-real/…", "ai": false}
— prawdziwe ujęcie nie dostaje znaku „wygenerowane przez AI”.

  python3 tools/real_broll.py
"""
import subprocess
from pathlib import Path

from sources import PROJECT

SOURCE = Path.home() / "Youtube Projects" / "b-rolle"
OUT = PROJECT / "build" / "broll-real"

# (plik, od s, ile s, nazwa) — ratusz, ulice z ratuszem w tle, deptak, park
CLIPS = [
    ("IMG_8641", 0, 12, "slupsk-ratusz"),
    ("IMG_8641", 24, 10, "slupsk-ratusz-2"),
    ("IMG_8636", 0, 7.1, "slupsk-ulica-ratusz"),
    ("IMG_8634", 0, 5.9, "slupsk-deptak"),
    ("IMG_8635", 0, 9.6, "slupsk-skrzyzowanie"),
    ("IMG_8638", 0, 12, "slupsk-park"),
]


def sdr(name):
    """Cały plik źródłowy → SDR (avconvert), raz; dalej tniemy już kopię SDR."""
    out = OUT / "_sdr" / f"{name}.mov"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["avconvert", "-p", "Preset1920x1080", "-s", str(SOURCE / f"{name}.MOV"),
                        "-o", str(out), "--replace"], check=True, capture_output=True)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, start, length, slug in CLIPS:
        out = OUT / f"{slug}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-t", str(length),
                        "-i", str(sdr(name)), "-an",
                        "-vf", "fps=30,scale=1920:1080:flags=lanczos,format=yuv420p",
                        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                        "-movflags", "+faststart", str(out)],
                       check=True)
        print("→", out.relative_to(PROJECT))


if __name__ == "__main__":
    main()
