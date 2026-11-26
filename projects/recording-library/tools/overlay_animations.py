#!/usr/bin/env python3
"""Klikane animacje (animations/<odcinek>/build/*.mp4) na pełnym ekranie gotowego odcinka + twarz w okienku.

MK 26.11: „Ok dodaj do video” — animacje ep-doram wchodzą do finału wg animations/doram/README.md.
Wklejamy je do GOTOWEGO pliku …--with-inserts.mp4 (czasy z jego transkrypcji), a nie do surówki
(.ai/memory/ciecie-wstawek-po-renderze-nie-po-surowce). Głos zostaje bez zmian.

Okienko twarzy bierzemy z czystego master.mp4 (bez plansz i paneli), bo pod częścią animacji w finale
leżą już plansze z własnym okienkiem — przeskalowanie finału dałoby miniaturę planszy zamiast twarzy.
Kadr jak w package.py: baza przybliżenia ×1,10 (+ dryf) ze środkiem w FACE_CENTER_X / 40% wysokości;
tu stałe ×1,15. Okienko w tym samym miejscu co slate(pip=True): skala 0,27, 48 px od prawego i dolnego brzegu.

Jakość pod YouTube (MK 26.11 „już w pełnej rozdzielczości”): 1920×1080, H.264 ~12 Mb/s (CRF 18 dawał
na tym materiale tylko ~3,5 Mb/s), AAC 320k. Jedno wywołanie ffmpeg, każdy kawałek mastera osobnym
wejściem z -ss/-t i osobna maska na każde okienko — wspólne wejście rozdzielane `split` buforowałoby
w RAM klatki aż do ostatniej wstawki (por. source_slice w assemble_episode.py).

  python3 tools/overlay_animations.py animations/doram/inserts.json --base <final.mp4> \
      --master <build/library/ep-doram/master.mp4> --out <wynik.mp4>
"""
import argparse
import json
import subprocess
from pathlib import Path

from sources import FACE_CENTER_X, SOURCE_H, SOURCE_W

WIDTH, HEIGHT, FPS = 1920, 1080, 30
PIP_SCALE, PIP_MARGIN, PIP_RADIUS = 0.27, 48, 30
PIP_W, PIP_H = round(WIDTH * PIP_SCALE), round(HEIGHT * PIP_SCALE)
PIP_X, PIP_Y = WIDTH - PIP_MARGIN - PIP_W, HEIGHT - PIP_MARGIN - PIP_H
FACE_ZOOM = 1.15
FADE = 0.3


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def face_crop(source):
    """Prostokąt mastera (1280×720) widoczny w kadrze 16:9 przy przybliżeniu FACE_ZOOM."""
    origin_x, origin_y = FACE_CENTER_X[source], 0.40 * SOURCE_H
    w, h = SOURCE_W / FACE_ZOOM, SOURCE_H / FACE_ZOOM
    x = origin_x - origin_x / FACE_ZOOM
    y = origin_y - origin_y / FACE_ZOOM
    return round(w), round(h), round(x), round(y)


def rounded_mask(path):
    r = PIP_RADIUS
    inside = (f"lte(pow(max(0,max({r}-X,X-(W-1-{r}))),2)+pow(max(0,max({r}-Y,Y-(H-1-{r}))),2),{r * r})")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={PIP_W}x{PIP_H}",
                    "-frames:v", "1", "-vf", f"format=gray,geq=lum='255*{inside}'", str(path)], check=True)


def master_time(t, offsets):
    for span in offsets:
        if t < span["until"]:
            return t - span["offset"]
    raise SystemExit(f"{t} s poza przedziałami master_offsets")


def build(plan_path, base, master, out, source):
    plan = json.loads(Path(plan_path).read_text())
    anim_dir = Path(plan_path).parent / "build"
    mask = Path(out).with_suffix(".pip-mask.png")
    rounded_mask(mask)
    crop_w, crop_h, crop_x, crop_y = face_crop(source)
    inputs, graph, last = ["-i", str(base)], "", "0:v"
    for i, insert in enumerate(plan["inserts"]):
        anim = anim_dir / insert["file"]
        start, length = insert["start"], duration(anim)
        fade_out = length - FADE
        inputs +=["-i", str(anim),
                   "-ss", f"{master_time(start, plan['master_offsets']):.3f}", "-t", f"{length:.3f}", "-i", str(master),
                   "-loop", "1", "-t", f"{length:.3f}", "-i", str(mask)]
        # inputs zawiera też -ss/-t/-loop — indeksy wejść liczymy po „-i”
        a, m, k = inputs.count("-i") - 3, inputs.count("-i") - 2, inputs.count("-i") - 1
        shift = f"setpts=PTS-STARTPTS+{start:.3f}/TB"
        graph += (f"[{a}:v]fps={FPS},scale={WIDTH}:{HEIGHT},format=yuva420p,"
                  f"fade=t=in:d={FADE}:alpha=1,fade=t=out:st={fade_out:.3f}:d={FADE}:alpha=1,{shift}[an{i}];"
                  f"[{m}:v]fps={FPS},crop={crop_w}:{crop_h}:{crop_x}:{crop_y},scale={PIP_W}:{PIP_H}:flags=lanczos,setsar=1[pf{i}];"
                  f"[{k}:v]fps={FPS},format=gray[mk{i}];"
                  f"[pf{i}][mk{i}]alphamerge,format=yuva420p,"
                  f"fade=t=in:d={FADE}:alpha=1,fade=t=out:st={fade_out:.3f}:d={FADE}:alpha=1,{shift}[pp{i}];"
                  f"[{last}][an{i}]overlay=0:0:eof_action=pass[ov{i}];"
                  f"[ov{i}][pp{i}]overlay={PIP_X}:{PIP_Y}:eof_action=pass[v{i}];")
        last = f"v{i}"
        print(f"   {insert['file']:24} {start:7.2f} → {start + length:7.2f}  (master {master_time(start, plan['master_offsets']):.2f})")
    graph = graph.rstrip(";")
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", "-threads", "4", "-filter_complex_threads", "2",
                    *inputs, "-filter_complex", graph, "-map", f"[{last}]", "-map", "0:a",
                    "-c:v", "libx264", "-preset", "medium", "-b:v", "12M", "-maxrate", "16M", "-bufsize", "24M",
                    "-pix_fmt", "yuv420p", "-r", str(FPS), "-profile:v", "high",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out)], check=True)
    mask.unlink()
    print(f"   → {out}  {duration(out):.1f} s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--base", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--source", default="doram", help="klucz FACE_CENTER_X (nagranie źródłowe)")
    args = ap.parse_args()
    build(args.plan, args.base, args.master, args.out, args.source)
