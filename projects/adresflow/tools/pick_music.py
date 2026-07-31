#!/usr/bin/env python3
"""Ranking podkładów muzycznych pod lektora.

Kryterium: ile energii utwór ma w paśmie mowy (300 Hz – 3 kHz). Im więcej,
tym mocniej walczy z lektorem i tym agresywniejszy ducking trzeba włączyć,
co słychać jako „pompowanie". Drugie kryterium to LRA (zakres dynamiki) —
utwór o dużych skokach głośności wyskakuje między frazami.

Mierzy 30 s wycięte ze środka utworu (intro bywa niereprezentatywne).
"""
import json, os, re, subprocess, sys

MUSIC = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "assets", "music", "library"))
SAMPLE = 30.0


def dur(p):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip())


def mean_db(path, ss, filt=""):
    """Średni poziom RMS w wycinku, opcjonalnie po filtrze pasmowym."""
    af = (filt + "," if filt else "") + "astats=metadata=1:reset=0"
    out = subprocess.run(
        ["ffmpeg", "-v", "info", "-ss", f"{ss}", "-t", f"{SAMPLE}", "-i", path,
         "-af", af, "-f", "null", "-"], capture_output=True, text=True).stderr
    vals = [float(m) for m in re.findall(r"RMS level dB:\s*(-?\d+\.?\d*)", out)]
    return sum(vals) / len(vals) if vals else None


def loudness(path, ss):
    out = subprocess.run(
        ["ffmpeg", "-v", "info", "-ss", f"{ss}", "-t", f"{SAMPLE}", "-i", path,
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
         "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"\{[^{}]*input_i[\s\S]*?\}", out)
    if not m:
        return None, None
    d = json.loads(m.group(0))
    return float(d["input_i"]), float(d["input_lra"])


def main():
    rows = []
    files = sorted(f for f in os.listdir(MUSIC) if f.lower().endswith(".mp3"))
    for f in files:
        p = os.path.join(MUSIC, f)
        ss = max(0.0, dur(p) / 2 - SAMPLE / 2)
        full = mean_db(p, ss)
        speech = mean_db(p, ss, "bandpass=f=1200:width_type=h:width=2700")
        i, lra = loudness(p, ss)
        if None in (full, speech, i, lra):
            continue
        # ile energii siedzi w paśmie mowy względem całości (dB, mniej = lepiej)
        rows.append({"file": f, "speech_ratio": speech - full, "lra": lra, "i": i})

    # ranking: głównie pasmo mowy, dynamika jako drugie kryterium
    rows.sort(key=lambda r: r["speech_ratio"] + 0.25 * r["lra"])
    print(f"{'utwór':46} {'pasmo mowy':>11} {'LRA':>6} {'LUFS':>7}")
    print("-" * 74)
    for r in rows:
        print(f"{r['file'][:45]:46} {r['speech_ratio']:>10.1f}dB "
              f"{r['lra']:>5.1f} {r['i']:>6.1f}")
    print("\nNiżej = mniej walczy z lektorem (mniej energii w paśmie mowy,")
    print("równiejsza dynamika). Ostateczny wybór i tak na słuch.")


if __name__ == "__main__":
    main()
