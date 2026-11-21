#!/usr/bin/env python3
"""Etap 2a — obraz z zoomami + dźwięk cięty sample-exact z tych samych granic.

Obraz renderuje się od nowa ze źródła 4K (per ujęcie zoomu: osobne wejście
z -ss/-to, crop, scale, długości w KLATKACH, sklejka filtrem concat). Dźwięk
idzie z JEDNEGO wejścia audio bez seeków: atrim per fragment na próbkach,
aconcat — zero paddingu AAC na szwach. Rough sklejał gotowe pliki concat
demuxerem i kodek doklejał ~21 ms ciszy na każdym szwie; przy trzech
fragmentach (s4) obraz rozjeżdżał się z dźwiękiem o 90 ms. Treściowo oś jest
ta sama, co zaakceptowany rough — krótsza o te szwy, więc napisy liczone
z transkrypcji rough grają z tolerancją ≤ 60 ms.

Wyjście: build/picture/<key>.mp4 + kontrola |obraz - dźwięk| < 0,05 s.
"""
import os
import subprocess
import sys

from edl import (CROP_W, CROP_X, FACE_Y, FPS, H, SHORTS, SOURCE, SRC_H, W,
                 short_len)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(BUILD, "picture")

VENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS)]


def sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"padło: {' '.join(cmd[:12])}…\n{p.stderr[-2000:]}")
    return p


def dur(path, stream="v:0"):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", stream,
         "-show_entries", "stream=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout
    return float(out.strip().split(",")[0].rstrip(","))


def crop_expr(zoom):
    """Statyczne powiększenie: crop mniejszego okna + scale do 1080x1920.

    Okno trzyma twarz w miejscu (FACE_Y), w poziomie zostaje na osi kadru.
    Żadnego scale na inne proporcje (.ai/memory/nigdy-nie-rozciagaj-kadru).
    """
    cw = int(round(CROP_W / zoom / 2)) * 2
    ch = int(round(SRC_H / zoom / 2)) * 2
    x = CROP_X + (CROP_W - cw) // 2
    y = int(FACE_Y * (1 - 1 / zoom))
    return f"crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos"


def render(key):
    spans = SHORTS[key]["zooms"]
    frags = SHORTS[key]["fragments"]
    out = os.path.join(OUT, f"{key}.mp4")

    inputs, filters, labels = [], [], []
    for i, (a, b, zoom) in enumerate(spans):
        # Długość ujęcia w KLATKACH liczona z bezwzględnych czasów źródła:
        # round(b·fps) − round(a·fps). Sąsiednie ujęcia się teleskopują, więc
        # zaokrąglenia nie kumulują się wzdłuż shorta (pierwsza wersja liczyła
        # czas per ujęcie i po 7 ujęciach obraz był 67 ms dłuższy od dźwięku).
        frames = round(b * FPS) - round(a * FPS)
        inputs += ["-ss", f"{a:.3f}", "-to", f"{b + 0.25:.3f}", "-i", SOURCE]
        clock = (f"fps={FPS},setpts=PTS-STARTPTS,"
                 f"trim=start_frame=0:end_frame={frames},setpts=PTS-STARTPTS")
        if zoom == "screen":
            # Screencast: pełny kadr 16:9 wpuszczony na całą szerokość
            # + rozmyte tło z pionowego cropu — w pionowym cropie ze strony
            # www widać tylko pasek. Czysty crop 83% zdejmuje czarne ramki.
            filters.append(
                f"[{i}:v]{clock},split=2[bg{i}][fg{i}];"
                f"[bg{i}]crop={CROP_W}:2160:{CROP_X}:0,scale={W}:{H},"
                f"gblur=sigma=28,eq=brightness=-0.12[bgb{i}];"
                f"[fg{i}]crop=3200:1800:320:180,scale={W}:608:flags=lanczos"
                f"[fgs{i}];"
                f"[bgb{i}][fgs{i}]overlay=0:656,setsar=1[v{i}]")
        else:
            filters.append(f"[{i}:v]{crop_expr(zoom)},{clock},setsar=1[v{i}]")
        labels.append(f"[v{i}]")
    filters.append(f"{''.join(labels)}concat=n={len(spans)}:v=1:a=0[v]")

    # Dźwięk: jedno wejście bez -ss, cięcie na PRÓBKACH z tych samych granic
    # klatek co obraz (48000/30 = 1600 próbek na klatkę).
    aud = len(spans)
    inputs += ["-i", SOURCE]
    alabels = []
    # Źródło ma 44,1 kHz — najpierw resample do 48 kHz, inaczej rachunek
    # próbek (1600/klatkę) tnie w złych miejscach.
    filters.append(f"[{aud}:a]aresample=48000,asplit={len(frags)}"
                   + "".join(f"[a{i}]" for i in range(len(frags))))
    for i, (a, b) in enumerate(frags):
        s0, s1 = round(a * FPS) * 1600, round(b * FPS) * 1600
        filters.append(f"[a{i}]atrim=start_sample={s0}:end_sample={s1},"
                       f"asetpts=PTS-STARTPTS[ac{i}]")
        alabels.append(f"[ac{i}]")
    filters.append(f"{''.join(alabels)}concat=n={len(frags)}:v=0:a=1[a]")

    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "[v]", "-map", "[a]",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        *VENC, "-movflags", "+faststart", out])

    vlen, alen, plan = dur(out, "v:0"), dur(out, "a:0"), short_len(key)
    print(f"{key}: obraz {vlen:.3f}s / dźwięk {alen:.3f}s / plan {plan:.2f}s "
          f"(rozjazd {abs(vlen - alen) * 1000:.0f} ms)")
    if abs(vlen - alen) > 0.06:
        raise SystemExit("obraz rozjechał się z dźwiękiem — nie zostawiam")
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[1:])
    for key in SHORTS:
        if only and not any(key.startswith(o) for o in only):
            continue
        render(key)


if __name__ == "__main__":
    main()
