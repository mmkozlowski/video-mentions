#!/usr/bin/env python3
"""Kadry 1:1 i 16:9 z gotowego pionu — rozmyte tło z tego samego ujęcia.

Cały materiał źródłowy jest PIONOWY (720x1280 albo 1440x2560); nie mamy ani
jednego ujęcia poziomego. Przycięcie 9:16 do 16:9 zostawia 31 % wysokości
i ucina głowy, więc zamiast tego wkładamy cały pionowy kadr na rozmyte tło
zrobione z niego samego.

Świadomy kompromis: napisy, plansze i znak AI są już wypalone w pionie, więc
w kwadracie i poziomie wychodzą mniejsze. Wersja „idealna" wymagałaby
przebudowy każdego spotu natywnie pod kadr — nie robimy tego, bo zysk nie
uzasadnia utrzymywania trzech układów graficznych.

Wejście: gotowe spoty z ../final/ (te, które przeszły finalize.py).
Wyjście: ../final/1x1/ i ../final/16x9/ — te same nazwy plików.

Użycie:
    python3 reframe.py                # wszystkie spoty, oba kadry
    python3 reframe.py 11-wycena-rciwn.mp4
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
FINAL = os.path.join(ROOT, "final")

FORMATS = {
    "1x1":  (1080, 1080),
    "16x9": (1920, 1080),
}


def dur(p):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip())


def reframe(src, dst, w, h):
    """Ostry pion na środku, rozmyte tło z tego samego materiału.

    `gblur` idzie na kopii rozciągniętej do wypełnienia kadru — dzięki temu tło
    ma kolory ujęcia i nie wygląda jak czarne pasy. Przyciemnienie i lekkie
    podbicie nasycenia oddzielają tło od ostrego kadru.
    """
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex",
        f"[0:v]split[b][f];"
        f"[b]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
        f"gblur=sigma=42,eq=brightness=-0.24:saturation=1.22[bg];"
        f"[f]scale=-2:{h}[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30[v]",
        "-map", "[v]", "-map", "0:a?", "-c:a", "copy",
        "-r", "30", "-fps_mode", "cfr",
        "-c:v", "libx264", "-crf", "19", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst], check=True)


def main(names):
    src_files = sorted(f for f in os.listdir(FINAL)
                       if f.endswith(".mp4") and (not names or f in names))
    if not src_files:
        raise SystemExit(f"Brak spotów w {FINAL} — najpierw python3 finalize.py")

    for fmt, (w, h) in FORMATS.items():
        out_dir = os.path.join(FINAL, fmt)
        os.makedirs(out_dir, exist_ok=True)
        print(f"\n— {fmt} ({w}x{h}):")
        for f in src_files:
            dst = os.path.join(out_dir, f)
            reframe(os.path.join(FINAL, f), dst, w, h)
            print(f"   {f:42} {dur(dst):5.1f}s")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
