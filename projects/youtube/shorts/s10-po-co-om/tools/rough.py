#!/usr/bin/env python3
"""Stage 1 — rough cuts of vertical shorts from the S-10 episode.

Cuts fragments from the edited 16:9 episode (word-timestamp boundaries from
build/work/episode.json), center-crops to 9:16 and concatenates per short.
Output: build/rough/<key>.mp4 — for ACCEPTANCE ONLY; captions/graphics are
stage 2 and must not start before stage 1 is approved (see shorts IG README).

Always re-encode at -ss (never -c copy: keyframe snapping,
.ai/memory/montaz-pulapki-synchronizacji).
"""
import subprocess, sys
from pathlib import Path

SOURCE = "/Users/mac/Youtube Projects/S-10 - czym jest OM/Postprodukcja/Odcinek-PO_CO_OPEN_MERCATO.mp4"
PROJECT = Path(__file__).resolve().parent.parent
ROUGH = PROJECT / "build" / "rough"
CUTS = PROJECT / "build" / "cuts"

# Source is 3840x2160, speaker horizontally centered -> center crop 1214x2160 (9:16).
CROP = "crop=1214:2160:1313:0,scale=1080:1920:flags=lanczos,fps=30"

# key -> (title, [(start, end), ...])  times in seconds of the SOURCE episode
SHORTS = {
    "s1-po-co-skoro-excel-dziala": (
        "Po co Ci Open Mercato, skoro Excel działa?",
        [(0.00, 36.90), (39.94, 62.55)],
    ),
    "s2-ten-sam-excel-w-kilku-wersjach": (
        "Wchodzę do firm i widzę Excela",
        [(175.16, 203.35), (237.30, 257.50)],
    ),
    "s3-komu-odradzam": (
        "Komu ODRADZAM Open Mercato",
        [(546.65, 595.85)],
    ),
    "s4-sto-procent-dostepu-do-kodu": (
        "Co tu jest wow? 100% dostępu do kodu",
        [(116.20, 146.95), (296.90, 310.78), (280.30, 287.30)],
    ),
}


def cut_fragment(start: float, end: float) -> Path:
    out = CUTS / f"{start:08.2f}-{end:08.2f}.mp4"
    if out.exists():
        return out
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{start:.2f}", "-to", f"{end:.2f}", "-i", SOURCE,
        "-vf", CROP,
        "-c:v", "h264_videotoolbox", "-b:v", "8M",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", str(out),
    ], check=True)
    return out


def main() -> None:
    only = set(sys.argv[1:])
    ROUGH.mkdir(parents=True, exist_ok=True)
    CUTS.mkdir(parents=True, exist_ok=True)
    for key, (title, fragments) in SHORTS.items():
        if only and not any(key.startswith(o) for o in only):
            continue
        parts = [cut_fragment(a, b) for a, b in fragments]
        concat_list = CUTS / f"{key}.txt"
        concat_list.write_text("".join(f"file '{p}'\n" for p in parts))
        out = ROUGH / f"{key}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
            "-i", str(concat_list), "-c", "copy", str(out),
        ], check=True)
        length = sum(b - a for a, b in fragments)
        print(f"{out.name}  ~{length:.1f}s  — {title}")


if __name__ == "__main__":
    main()
