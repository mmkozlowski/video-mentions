#!/usr/bin/env python3
"""Spoty POV „nagrane telefonem" — grade + muzyka.

Format skopiowany z inspiracji (`assets/reference/inspieracja-*.mp4`): ktoś
filmuje telefonem swój laptop i pokazuje, jak coś robi. Bez lektora, cała
narracja siedzi w przyklejonej planszy i w tym, co widać na ekranie.

Podział pracy jest taki sam jak w reszcie pipeline'u:
  - HyperFrames (`screens/pov-*`) robi geometrię — laptop, perspektywę,
    dryf ręki, refleks na szkle, winietę;
  - ten skrypt dokłada to, co w przeglądarce byłoby drogie albo niemożliwe:
    utratę rozdzielczości, szum sensora i cast barwny.

Dlaczego zejście do 540p i powrót: oryginał ma 360p i ta miękkość jest
częścią stylu. Czysty render 1080p wygląda jak zapis ekranu, nie jak film
z telefonu — a to zabija cały format.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCREENS = os.path.join(ROOT, "build", "screens")
MUSIC = os.path.join(ROOT, "assets", "music", "music.mp3")
BUILD = os.path.join(ROOT, "build")

sys.path.insert(0, HERE)
import story  # noqa: E402 — music_offset i stałe podkładu

# Bez lektora podkład może iść głośniej niż w spotach narracyjnych (tam 0.40,
# bo musiał zejść pod głos).
MUS_VOL = 0.85

SPOTS = {
    "pov-rzut":    "Tak robię rzut 3D w półtorej minuty",
    "pov-staging": "Tak robię home staging w 60 sekund",
}

# Kolejność ma znaczenie: szum sypiemy w NISKIEJ rozdzielczości, żeby po
# powiększeniu zlał się w ziarno, a nie leżał na wierzchu jako piksele.
GRADE = (
    "scale=540:960:flags=bicubic,"
    "noise=alls=7:allf=t+u,"
    "scale=1080:1920:flags=bicubic,"
    "eq=contrast=1.05:saturation=1.06:gamma=0.99,"
    "colorbalance=rs=-0.015:gs=0.004:bs=0.028,"
    "unsharp=5:5:0.35,"          # tekst nie może zniknąć w miękkości
    "fps=30,setsar=1"
)


def dur(p):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip())


def build(key):
    src = os.path.join(SCREENS, f"{key}-raw.mp4")
    if not os.path.exists(src):
        raise SystemExit(
            f"Brak {src}\nWyrenderuj najpierw: cd ../screens && "
            f"npx hyperframes render {key} --fps 30 --quality high "
            f"--output ../build/screens/{key}-raw.mp4")

    total = dur(src)
    out = os.path.join(BUILD, f"adresflow-{key}.mp4")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", src]

    if os.path.exists(MUSIC):
        off = story.music_offset(MUSIC, total)
        cmd += ["-i", MUSIC]
        fc = (f"[0:v]{GRADE}[v];"
              f"[1:a]atrim={off:.2f},asetpts=PTS-STARTPTS,"
              f"aloop=loop=-1:size=2e9,atrim=0:{total:.3f},"
              f"volume={MUS_VOL},afade=t=in:st=0:d=0.4,"
              f"afade=t=out:st={max(0.1, total - 1.6):.3f}:d=1.5,"
              f"loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                "-c:a", "aac", "-b:a", "192k"]
    else:
        print("  (brak music.mp3 — spot wyjdzie niemy)")
        cmd += ["-filter_complex", f"[0:v]{GRADE}[v]", "-map", "[v]"]

    cmd += ["-r", "30", "-fps_mode", "cfr", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-crf", "20", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(f"== {key}: {out} ({dur(out):.2f}s) — {SPOTS[key]}")


if __name__ == "__main__":
    keys = sys.argv[1:] or list(SPOTS)
    for k in keys:
        if k not in SPOTS:
            raise SystemExit(f"Nieznany spot '{k}'. Dostępne: {', '.join(SPOTS)}")
        build(k)
