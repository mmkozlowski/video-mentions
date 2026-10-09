#!/usr/bin/env python3
"""Przebitki z folderu Mateusza: Słupsk z telefonu + wcześniejsze b-rolle (stock i Veo).

Mateusz 9.10: „b-rolle nie mogą być azjatyckie, muszą być polskie, podobne do naszych
klimatów” — stąd jego własne ujęcia zamiast części Veo z projects/youtube.

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

# (plik, od s, ile s, nazwa[, przytnij znak wodny Veo]) — ratusz, ulice, deptak, park;
# dalej stock (prawdziwe ujęcia, "ai": false) i trzy klipy Veo ("ai": true, róg ze znakiem
# wodnym „Veo” obcięty)
CLIPS = [
    ("IMG_8641", 0, 12, "slupsk-ratusz"),
    ("IMG_8641", 24, 10, "slupsk-ratusz-2"),
    ("IMG_8636", 0, 7.1, "slupsk-ulica-ratusz"),
    ("IMG_8634", 0, 5.9, "slupsk-deptak"),
    ("IMG_8635", 0, 9.6, "slupsk-skrzyzowanie"),
    ("IMG_8638", 0, 12, "slupsk-park"),
    ("0_Office_Chaos_3840x2160.mov", 0, 6, "stock-chaos-biuro"),
    ("6070442_Exhausted_Working_3840x2160.mov", 0, 9, "stock-zmeczona-szefowa"),
    ("4826200_Business_Man_4096x2160.mov", 0, 6, "stock-przy-biurku"),
    ("0_Coding_Programming_3840x2160.mov", 2, 8, "stock-kod-laptop"),
    ("5114452_Workteam_Working_Team_3840x2160.mp4", 0, 8, "stock-zespol-laptop"),
    ("0_Woman_Laptop_3840x2020.mp4", 0, 7, "stock-telefon-stres"),
    ("Film_o_przepalaniu_pieniędzy_w_firmie.mp4", 0, 8, "veo-excel-stres", True),
    ("Generowanie_Wideo_Chaosu_Biurowego.mp4", 0, 8, "veo-stos-dokumentow", True),
    ("slide_video_szwalniamp_.mp4", 0, 8, "veo-szwalnia", True),
]


def sdr(name):
    """Cały plik źródłowy → SDR (avconvert), raz; dalej tniemy już kopię SDR.
    Pliki bez HDR idą prosto ze źródła."""
    src = SOURCE / name if "." in name else SOURCE / f"{name}.MOV"
    transfer = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                               "stream=color_transfer", "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout
    if "arib-std-b67" not in transfer and "smpte2084" not in transfer:
        return src
    out = OUT / "_sdr" / f"{Path(name).stem}.mov"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["avconvert", "-p", "Preset1920x1080", "-s", str(src),
                        "-o", str(out), "--replace"], check=True, capture_output=True)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, start, length, slug, *veo in CLIPS:
        out = OUT / f"{slug}.mp4"
        crop = "crop=iw*0.9:ih*0.9:0:0," if veo and veo[0] else ""
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-t", str(length),
                        "-i", str(sdr(name)), "-an",
                        "-vf", f"{crop}fps=30,scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,format=yuv420p",
                        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                        "-movflags", "+faststart", str(out)],
                       check=True)
        print("→", out.relative_to(PROJECT))


if __name__ == "__main__":
    main()
