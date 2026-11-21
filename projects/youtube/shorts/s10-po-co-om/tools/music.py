#!/usr/bin/env python3
"""Etap 3 — podkład muzyczny, OSOBNO i na końcu. Adaptacja
`projects/shorts IG/tools/music.py` (tam pełny wywód o liczbach).

    python3 tools/music.py --pick               # ranking biblioteki
    python3 tools/music.py "the_mountain"       # ten podkład do WSZYSTKICH
    python3 tools/music.py "monume" s3 s4       # tylko wskazane shorty

Biblioteka: ~/Repo/video-mentions/music (główny checkout repo — pliki nie są
w gicie; worktree ich nie ma).
Gadana głowa, mowa prawie bez przerwy → MUS_VOL jak w shorts IG (0.187),
start od najgłośniejszego fragmentu utworu, ducking 0.12/4 bez pompowania.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BUILD = os.path.join(ROOT, "build")
FINAL = os.path.join(ROOT, "final")
LIB = "/Users/mac/Repo/video-mentions/music"

MUS_VOL = 0.187
FADE_OUT = 2.0

sys.path.insert(0, HERE)
from edl import SHORTS  # noqa: E402


def sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"padło: {' '.join(cmd[:8])}…\n{p.stderr[-1500:]}")
    return p


def dur(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip())


def rms_db(path, ss, length, band=None):
    af = (f"{band}," if band else "") + "astats=metadata=1:reset=0"
    out = subprocess.run(
        ["ffmpeg", "-v", "info", "-ss", str(ss), "-t", str(length), "-i", path,
         "-af", af, "-f", "null", "-"], capture_output=True, text=True).stderr
    vals = [float(m) for m in re.findall(r"RMS level dB:\s*(-?\d+\.?\d*)", out)]
    return sum(vals) / len(vals) if vals else -99.0


def music_offset(path, window=8.0):
    total = dur(path)
    best, best_db, t = 0.0, -99.0, 0.0
    while t + window < min(total, 90.0):
        db = rms_db(path, t, window)
        if db > best_db:
            best, best_db = t, db
        t += window
    return best


def pick():
    rows = []
    for name in sorted(os.listdir(LIB)):
        if not name.lower().endswith((".mp3", ".wav", ".m4a")):
            continue
        p = os.path.join(LIB, name)
        mid = max(dur(p) / 2 - 15, 0)
        full = rms_db(p, mid, 30)
        speech = rms_db(p, mid, 30, "highpass=f=300,lowpass=f=3000")
        rows.append((speech - full, name))
    rows.sort()
    print("kolizja z pasmem mowy (mniej = lepiej pod gadaną głowę):\n")
    for score, name in rows:
        print(f"  {score:+6.2f} dB   {name}")


def mix(track, keys):
    matches = [n for n in os.listdir(LIB) if track.lower() in n.lower()]
    if not matches:
        raise SystemExit(f"nie znam podkładu „{track}” — sprawdź --pick")
    path = os.path.join(LIB, matches[0])
    off = music_offset(path)
    os.makedirs(FINAL, exist_ok=True)
    print(f"podkład: {matches[0]} (od {off:.0f}s)")

    for key in keys:
        src = os.path.join(BUILD, "final-nomusic", f"{key}.mp4")
        out = os.path.join(FINAL, f"{key}.mp4")
        length = dur(src)
        fc = (
            f"[1:a]atrim=start={off:.2f},asetpts=PTS-STARTPTS,"
            f"aloop=loop=-1:size=2e9,atrim=duration={length:.3f},"
            f"volume={MUS_VOL},afade=t=in:st=0:d=0.8,"
            f"afade=t=out:st={length - FADE_OUT:.3f}:d={FADE_OUT}[bed];"
            f"[0:a]asplit=2[voice][key];"
            f"[bed][key]sidechaincompress=threshold=0.12:ratio=4:attack=12:"
            f"release=320[duck];"
            f"[voice][duck]amix=inputs=2:duration=first:normalize=0[mixed];"
            f"[mixed]alimiter=limit=0.94[a]"
        )
        wav = os.path.join(BUILD, "work", f"music-{key}.wav")
        sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", src, "-i", path, "-filter_complex", fc, "-map", "[a]",
            "-ar", "48000", "-ac", "2", wav])
        alen = dur(wav)
        if alen < length - 0.05:
            raise SystemExit(f"{key}: dźwięk krótszy od obrazu — nie muksuję")
        sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", src, "-i", wav, "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-ac", "2",
            "-t", f"{length:.3f}", "-movflags", "+faststart", out])
        print(f"  {out}  {dur(out):.2f}s")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--pick" in sys.argv or not args:
        pick()
    else:
        track, rest = args[0], args[1:]
        keys = [k for k in SHORTS
                if not rest or any(k.startswith(r) for r in rest)]
        mix(track, keys)
