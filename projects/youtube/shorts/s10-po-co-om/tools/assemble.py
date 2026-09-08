#!/usr/bin/env python3
"""Etap 2c — kompozycja: picture + napisy + tytuł + animacje + plakietki
+ ogon z planszą pytania. Wyjście: build/final-nomusic/<key>.mp4.

Zasady z projects/shorts IG przeniesione wprost:
- oś dźwięku nie zmienia długości — wszystkie efekty są nakładkami na obraz,
- `-t` na wyjściu kompozycji jest obowiązkowe (nakładka dłuższa od materiału
  rozciąga wynik overlay, a dźwięk się nie rozciąga),
- loudnorm JEDNYM przebiegiem na całości, długość porównana przed muxem,
- finał to pytanie na żywym kadrze (ogon źródła), nie czarna plansza.
"""
import os
import subprocess
import sys

from edl import CROP_W, CROP_X, FPS, H, INTRO_DUR, SHORTS, SOURCE, STAMPS, W

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BUILD = os.path.join(ROOT, "build")
WORK = os.path.join(BUILD, "work")
OV = os.path.join(BUILD, "overlays")
OUT = os.path.join(BUILD, "final-nomusic")

TAIL_DUR = 2.80           # ogon: kadr ze źródła + plansza pytania
CAP_Y = 1190
SPEED = 1.01              # „podkręć delikatnie o 1%" — na całości, przed
                          # loudnorm; napisy są wypalone, więc jadą razem

VENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS)]
AENC = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]

# Nakładki animacji: (start na osi shorta, plik z build/anim)
ANIMS = {
    "s2-ten-sam-excel-w-kilku-wersjach": [(10.29, "kopie-9x16.mp4")],
    "s4-sto-procent-dostepu-do-kodu": [(17.09, "dostep-9x16.mp4")],
}
# Plakietki: (plik w overlays/<key>, start, koniec, y)
BADGES = {
    "s3-komu-odradzam": [
        ("badge-programista.png", 12.60, 17.30, 290),
        ("badge-wersja.png", 34.80, 39.90, 290),
    ],
}


def sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"padło: {' '.join(cmd[:12])}…\n{p.stderr[-2000:]}")
    return p


def dur(path, stream=None):
    sel = ["-select_streams", stream] if stream else []
    out = subprocess.run(
        ["ffprobe", "-v", "error", *sel, "-show_entries",
         ("stream=duration" if stream else "format=duration"),
         "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip().split(",")[0].rstrip(","))


def caption_track(key, length):
    out = os.path.join(WORK, f"captions-{key}.mov")
    lst = os.path.join(OV, key, "captions.txt")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", lst,
        "-vf", f"fps={FPS},format=rgba", "-t", f"{length:.3f}",
        "-c:v", "png", out])
    return out


def tail_clip(key, out):
    """Ogon: dalszy ciąg źródła po ostatnim fragmencie + plansza pytania.

    Kadr pod planszą zostaje żywy (plansza sama przyciemnia — alpha w PNG),
    dźwięk to cisza: podkład wejdzie w music.py i tu naturalnie wyjdzie
    na wierzch.
    """
    t0 = SHORTS[key]["fragments"][-1][1]
    vf = (f"crop={CROP_W}:2160:{CROP_X}:0,scale={W}:{H}:flags=lanczos,"
          f"fps={FPS},setsar=1")
    fc = (f"[0:v]{vf}[bg];[bg][1:v]overlay=0:0,"
          f"fade=t=in:st=0:d=0.30,"
          f"fade=t=out:st={TAIL_DUR - 0.55:.2f}:d=0.55,format=yuv420p[v]")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{t0:.2f}", "-t", f"{TAIL_DUR:.2f}", "-i", SOURCE,
        "-i", os.path.join(OV, key, "outro.png"),
        "-f", "lavfi", "-t", f"{TAIL_DUR:.2f}", "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-filter_complex", fc, "-map", "[v]", "-map", "2:a",
        *VENC, *AENC, "-shortest", out])
    return out


def compose(key):
    picture = os.path.join(BUILD, "picture", f"{key}.mp4")
    length = dur(picture, "v:0")
    caps = caption_track(key, length)

    inputs = ["-i", picture, "-i", caps]
    f = [f"[1:v]setpts=PTS-STARTPTS[cap];",
         f"[0:v][cap]overlay=0:{CAP_Y}:format=auto[c0];"]
    chain, n = "c0", 2

    for start, name in ANIMS.get(key, []):
        clip = os.path.join(BUILD, "anim", name)
        alen = dur(clip, "v:0")
        inputs += ["-i", clip]
        f.append(f"[{n}:v]format=yuva420p,"
                 f"fade=t=in:d=0.30:alpha=1,"
                 f"fade=t=out:st={alen - 0.35:.2f}:d=0.35:alpha=1,"
                 f"setpts=PTS-STARTPTS+{start:.2f}/TB[an{n}];")
        f.append(f"[{chain}][an{n}]overlay=0:0:"
                 f"enable='between(t,{start:.2f},{start + alen:.2f})'[c{n}];")
        chain = f"c{n}"
        n += 1

    for png, t0, t1, y in BADGES.get(key, []):
        inputs += ["-i", os.path.join(OV, key, png)]
        f.append(f"[{chain}][{n}:v]overlay=(W-w)/2:{y}:"
                 f"enable='between(t,{t0:.2f},{t1:.2f})'[c{n}];")
        chain = f"c{n}"
        n += 1

    # Stemple kinetyczne: fade na alfie + slide-up 28 px na wejściu.
    for i, (_text, t0, t1, y, _size, _rot) in enumerate(STAMPS.get(key, [])):
        stamp_len = t1 - t0
        inputs += ["-loop", "1", "-t", f"{stamp_len:.2f}",
                   "-i", os.path.join(OV, key, f"stamp-{i}.png")]
        f.append(f"[{n}:v]format=rgba,fade=t=in:d=0.25:alpha=1,"
                 f"fade=t=out:st={stamp_len - 0.30:.2f}:d=0.30:alpha=1,"
                 f"setpts=PTS-STARTPTS+{t0:.2f}/TB[st{n}];")
        f.append(f"[{chain}][st{n}]overlay=x=(W-w)/2:"
                 f"y='{y}+28*(1-min((t-{t0:.2f})/0.30,1))':"
                 f"enable='between(t,{t0:.2f},{t1:.2f})'[c{n}];")
        chain = f"c{n}"
        n += 1

    main = os.path.join(WORK, f"main-{key}.mp4")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
        "-filter_complex", "".join(f).rstrip(";"),
        "-map", f"[{chain}]", "-map", "0:a:0", *VENC, "-c:a", "copy",
        "-t", f"{length:.3f}", main])
    return main, length


def intro_clip(key, out):
    """Cold-open: pytanie-hook na rozmytym, przyciemnionym kadrze ZANIM
    zacznie się mowa. Wersja statyczna dawała hook 30–36 w virality_predictor
    (ruch w 1. sekundzie waży więcej niż treść — `.ai/memory/copy-i-hook`),
    więc intro jest ANIMOWANE: push-in na tle + kicker i pytanie wjeżdżają
    osobno (slide + fade). Po intro obraz „wyostrza się" w to samo ujęcie."""
    frames = round(INTRO_DUR * FPS)
    fc = (
        f"[0:v]gblur=sigma=22,eq=brightness=-0.18:saturation=0.85,"
        f"zoompan=z='1.03+0.10*on/{frames}':d=1:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}[bg];"
        f"[1:v]format=rgba,fade=t=in:d=0.18:alpha=1[kick];"
        f"[2:v]format=rgba,fade=t=in:st=0.28:d=0.28:alpha=1,"
        f"setpts=PTS-STARTPTS[q];"
        f"[bg][kick]overlay=0:'-30+30*min(t/0.20,1)'[b1];"
        f"[b1][q]overlay=0:'46*(1-min(max(t-0.28,0)/0.30,1))',"
        f"fade=t=in:st=0:d=0.10,format=yuv420p[v]")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-t", f"{INTRO_DUR:.2f}", "-i",
        os.path.join(BUILD, "picture", f"{key}.mp4"),
        "-loop", "1", "-t", f"{INTRO_DUR:.2f}",
        "-i", os.path.join(OV, key, "intro-kicker.png"),
        "-loop", "1", "-t", f"{INTRO_DUR:.2f}",
        "-i", os.path.join(OV, key, "intro-main.png"),
        "-f", "lavfi", "-t", f"{INTRO_DUR:.2f}", "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-filter_complex", fc, "-map", "[v]", "-map", "3:a",
        *VENC, *AENC, "-shortest", out])
    return out


def speed_up(video, out):
    """+1% tempa na całości, przed loudnorm — obraz i dźwięk OSOBNYMI
    przebiegami. ffmpeg 8.1 w jednym filter_complex z gałęzią setpts na wideo
    po cichu rozciąga audio z powrotem do osi wideo i atempo znika
    (zmierzone: 1.5x dawało wideo 35 s, audio 51,8 s)."""
    v = out + ".v.mp4"
    a = out + ".a.wav"
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", video,
        "-vf", f"setpts=PTS/{SPEED}", "-an", *VENC, v])
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", video,
        "-vn", "-af", f"atempo={SPEED}", "-ar", "48000", "-ac", "2", a])
    vlen, alen = dur(v, "v:0"), dur(a)
    if abs(vlen - alen) > 0.06:
        raise SystemExit(f"speed_up: obraz {vlen:.2f}s / dźwięk {alen:.2f}s")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", v, "-i", a, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", *AENC, "-t", f"{vlen:.3f}", out])
    os.remove(v), os.remove(a)
    return out


def finalize_audio(video, out):
    """loudnorm raz, na całości; kontrola długości przed muxem."""
    vlen = dur(video, "v:0")
    wav = os.path.join(WORK, "final-audio.wav")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", video,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "2", wav])
    alen = dur(wav)
    if alen < vlen - 0.05:
        raise SystemExit(f"dźwięk {alen:.2f}s krótszy od obrazu {vlen:.2f}s")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", video, "-i", wav, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", *AENC, "-t", f"{vlen:.3f}",
        "-movflags", "+faststart", out])
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[1:])
    for key in SHORTS:
        if only and not any(key.startswith(o) for o in only):
            continue
        print(f"· {key}")
        body, length = compose(key)
        intro = intro_clip(key, os.path.join(WORK, f"intro-{key}.mp4"))
        tail = tail_clip(key, os.path.join(WORK, f"tail-{key}.mp4"))

        lst = os.path.join(WORK, f"concat-{key}.txt")
        with open(lst, "w") as fh:
            fh.write(f"file '{intro}'\nfile '{body}'\nfile '{tail}'\n")
        joined = os.path.join(WORK, f"joined-{key}.mp4")
        sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", lst,
            "-c:v", "copy", *AENC, joined])
        sped = speed_up(joined, os.path.join(WORK, f"sped-{key}.mp4"))

        out = os.path.join(OUT, f"{key}.mp4")
        finalize_audio(sped, out)
        print(f"  {out}  {dur(out):.2f}s "
              f"(intro {INTRO_DUR}s + treść {length:.2f}s + ogon {TAIL_DUR}s, "
              f"tempo ×{SPEED})")


if __name__ == "__main__":
    main()
