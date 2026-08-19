#!/usr/bin/env python3
"""Etap 2 montażu: surowy skład → gotowy short.

Wejście: `build/rough.mp4` (z `cut.py`) i warstwy z `style.py`.
Wyjście: `build/final-nomusic.mp4` — komplet obrazu i mowy, bez podkładu.
Muzyka wchodzi osobnym krokiem (`music.py`), na końcu, świadomie.

Zasada, na której stoi cały etap: **ścieżka dźwiękowa nie zmienia długości**.
Wszystkie efekty są wyłącznie obrazowe i wchodzą jako nakładki na istniejącą oś,
a nie jako przejścia typu `xfade`, które by ją skróciły. Dzięki temu napisy
policzone z transkrypcji `rough.mp4` pasują co do klatki i nie trzeba ich
przeliczać po każdej zmianie efektu.

Otwarcie jest NAKŁADKĄ na pierwsze sekundy materiału (dzielony ekran twarz +
kokpit, tytuł na wierzchu), a nie doklejoną planszą — czarna płachta na starcie
kosztuje dokładnie te sekundy, w których widz decyduje, czy zostaje. Domknięcie
(zdjęcie + plansza) doklejamy dopiero po skompletowaniu obrazu; przesuwa tylko
ogon, więc też niczego nie rozjeżdża.

Kolejność:
  1. pas napisów (PNG-i → film z alfą),
  2. łatki pełnoklatkowe: dzielony ekran, przebitka, zdjęcie na koniec,
  3. kompozycja: rough + łatki + napisy + plakietki + błyski,
  4. domknięcie: zdjęcie z biurka + plansza końcowa,
  5. dźwięk: loudnorm JEDNYM przebiegiem na całości + kontrola długości.
"""
import json
import os
import subprocess
import sys

from edl import FPS, H, W
from style import CAP_H, CAP_Y

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BUILD = os.path.join(ROOT, "build")
WORK = os.path.join(BUILD, "work")
OV = os.path.join(BUILD, "overlays")

ROUGH = os.path.join(BUILD, "rough.mp4")
# Otwarcie NIE jest doklejoną planszą, tylko pierwszymi sekundami materiału
# pokazanymi w dzielonym ekranie (twarz + kokpit) z tytułem na wierzchu.
# Czarna płachta na starcie kosztuje sekundy, w których widz decyduje, czy zostaje.
TITLE_DUR = 2.20
OUTRO_DUR = 3.20
PHOTO_DUR = 1.30          # zdjęcie „kciuk w górę" jako domknięcie przed planszą

VENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS)]
AENC = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def sh(cmd, quiet=True):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"padło: {' '.join(cmd[:9])}…\n{p.stderr[-2000:]}")
    return p


def dur(path, stream=None):
    sel = ["-select_streams", stream] if stream else []
    out = subprocess.run(
        ["ffprobe", "-v", "error", *sel, "-show_entries",
         ("stream=duration" if stream else "format=duration"),
         "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip().split(",")[0].rstrip(","))


def timeline():
    return {r["key"]: r for r in json.load(open(os.path.join(WORK, "timeline.json")))}


def src(name):
    for base in (ROOT, os.path.join(ROOT, "assets", "raw")):
        p = os.path.join(base, name + ".mov")
        if os.path.exists(p):
            return p
    raise SystemExit(f"brak {name}")


def photo(name):
    for base in (ROOT, os.path.join(ROOT, "assets", "photos")):
        p = os.path.join(base, name + ".HEIC")
        if os.path.exists(p):
            return p
    raise SystemExit(f"brak zdjęcia {name}")


# ── 1. pas napisów ────────────────────────────────────────────────────────
def build_caption_track(length):
    """Pas napisów przycięty DOKŁADNIE do długości obrazu.

    Lista dla concat demuxera musi kończyć się powtórzeniem ostatniego pliku
    (inaczej ostatnie okno nie zdąży się wyświetlić) — i to powtórzenie dostaje
    czas trwania poprzedniego wpisu. Pas wychodził przez to ~0,9 s dłuższy niż
    materiał, a `overlay` rozciągał do jego długości cały obraz i na końcu
    zostawała zamrożona klatka bez dźwięku.
    """
    out = os.path.join(WORK, "captions.mov")
    lst = os.path.join(OV, "captions.txt")
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(lst):
        return out
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", lst,
        "-vf", f"fps={FPS},format=rgba", "-t", f"{length:.3f}", "-c:v", "png", out])
    return out


# ── 2. łatki pełnoklatkowe ────────────────────────────────────────────────
def patch_split(t0, t1, out, top_y=60, bot_start=16.00):
    """Dzielony ekran: u góry gadana głowa, u dołu kokpit z agentami.

    Wzorzec z Granitu: zamiast przecinać ujęcie z twarzą, dokładamy drugie
    źródło pod spodem — nie ma czego rozjechać, bo nie ma czego ciąć
    (.ai/memory/montaz-pulapki-synchronizacji).

    Oba kadry to czysty `crop` bez skalowania — jedyny wariant z zerowym
    ryzykiem deformacji (.ai/memory/nigdy-nie-rozciagaj-kadru).
    """
    length = t1 - t0
    fc = (
        f"[0:v]trim=start={t0:.3f}:duration={length:.3f},setpts=PTS-STARTPTS,"
        f"crop={W}:{H // 2}:0:{top_y}[top];"
        f"[1:v]trim=start={bot_start:.2f}:duration={length:.3f},setpts=PTS-STARTPTS,"
        f"crop={W}:{H // 2}:0:470,eq=brightness=0.04:contrast=1.10[bot];"
        f"[top][bot]vstack=inputs=2[stk];"
        # Bursztynowa kreska na styku — bez niej dwa kadry zlewają się w jeden.
        f"color=c=0xECAB45:s={W}x6:d={length:.3f}[rule];"
        f"[stk][rule]overlay=0:{H // 2 - 3}[v]"
    )
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", ROUGH, "-i", src("IMG_1605"),
        "-filter_complex", fc, "-map", "[v]", "-an", *VENC, out])
    return out


def patch_broll(t0, t1, out):
    """Przebitka: ścieżka i cień biegacza pod zdanie „już dochodzę do domu"."""
    length = t1 - t0
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", "0.70", "-t", f"{length:.3f}", "-i", src("IMG_1601"),
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
               f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p",
        "-an", *VENC, out])
    return out


def patch_photo(out, length=PHOTO_DUR):
    """Zdjęcie z biurka jako domknięcie — powolny najazd, żeby nie stało."""
    jpg = os.path.join(WORK, "photo-outro.jpg")
    subprocess.run(["sips", "-s", "format", "jpeg", "-Z", "2600",
                    photo("IMG_1608"), "--out", jpg],
                   capture_output=True)
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-t", f"{length:.3f}", "-i", jpg,
        # Kadr z lewej: twarz jest przy lewej krawędzi zdjęcia, więc wycinek
        # ze środka zostawiłby sam kciuk i biurko.
        "-vf", f"scale=-2:{int(H * 1.14)},crop={W}:{H}:(iw-{W})*0.22:0,"
               f"zoompan=z='1.0+0.045*on/{int(length * FPS)}':d=1:"
               f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
               f"setsar=1,format=yuv420p",
        "-an", *VENC, out])
    return out


# ── 3. kompozycja ─────────────────────────────────────────────────────────
def compose(tl):
    length = dur(ROUGH, "v:0")
    caps = build_caption_track(length)

    # Otwarcie: te same dwa źródła co w haku, ale na pierwszych sekundach
    # materiału — żeby pierwszy kadr shorta był kadrem, a nie planszą.
    p_open = patch_split(0.0, TITLE_DUR, os.path.join(WORK, "patch-open.mp4"),
                         top_y=40, bot_start=17.20)

    split_t0, split_t1 = tl["a04"]["t0"], tl["a04"]["t1"]
    broll_t0, broll_t1 = tl["a05"]["t0"], tl["a05"]["t1"]
    p_split = patch_split(split_t0, split_t1, os.path.join(WORK, "patch-split.mp4"))
    p_broll = patch_broll(broll_t0, broll_t1, os.path.join(WORK, "patch-broll.mp4"))

    # Plakietki: liczba, która w mowie przelatuje, na ekranie zostaje.
    badges = [
        (os.path.join(OV, "badge-bieg.png"), tl["a02"]["t0"] + 0.15, tl["a02"]["t1"], 300),
        # Nad dzielonym ekranem plakietka siada wyżej, żeby nie wchodzić
        # w twarz zajmującą górną połowę kadru.
        (os.path.join(OV, "badge-agenci.png"), split_t0 + 0.45, split_t1 - 0.2, 130),
        (os.path.join(OV, "badge-godziny.png"), tl["b05"]["t0"] + 4.2,
         tl["b06"]["t1"] - 0.3, 250),
        (os.path.join(OV, "badge-odcinki.png"), tl["c03"]["t0"], tl["c04"]["t1"], 250),
    ]
    # Błysk na granicy aktów — dwie klatki, bez zmiany długości ścieżki.
    flashes = [tl["b01"]["t0"], tl["b05"]["t0"]]

    inputs = ["-i", ROUGH, "-i", caps, "-i", p_split, "-i", p_broll,
              "-i", p_open, "-i", os.path.join(OV, "title.png")]
    for b, *_ in badges:
        inputs += ["-i", b]
    BADGE0 = 6          # numer pierwszego wejścia z plakietką

    f = []
    f.append(f"[0:v][4:v]overlay=0:0:enable='between(t,0,{TITLE_DUR:.3f})'[op];")
    f.append(f"[2:v]setpts=PTS-STARTPTS+{split_t0:.3f}/TB[sp];")
    f.append(f"[op][sp]overlay=0:0:enable='between(t,{split_t0:.3f},{split_t1:.3f})'[c0];")
    f.append(f"[3:v]setpts=PTS-STARTPTS+{broll_t0:.3f}/TB[br];")
    f.append(f"[c0][br]overlay=0:0:enable='between(t,{broll_t0:.3f},{broll_t1:.3f})'[c1];")
    f.append(f"[c1][1:v]overlay=0:{CAP_Y}:format=auto[cap];")
    f.append(f"[cap][5:v]overlay=0:0:enable='between(t,0,{TITLE_DUR:.3f})'[c2];")

    chain = "c2"
    for i, (_, t0, t1, y) in enumerate(badges):
        nxt = f"c{3 + i}"
        f.append(f"[{chain}][{BADGE0 + i}:v]overlay=(W-w)/2:{y}:"
                 f"enable='between(t,{t0:.3f},{t1:.3f})'[{nxt}];")
        chain = nxt

    for i, t in enumerate(flashes):
        nxt = f"fl{i}"
        f.append(f"[{chain}]eq=brightness=0.62:contrast=1.25:"
                 f"enable='between(t,{t:.3f},{t + 2.0 / FPS:.3f})'[{nxt}];")
        chain = nxt

    out = os.path.join(WORK, "main.mp4")
    # `-t` na wyjściu jest OBOWIĄZKOWE: każda nakładka dłuższa od materiału
    # rozciąga wynik `overlay`, a dźwięk idzie tu kopią z `rough` i się nie
    # rozciągnie. Bez tego na końcu zostaje niema, zamrożona klatka.
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
        "-filter_complex", "".join(f)[:-1] if "".join(f).endswith(";") else "".join(f),
        "-map", f"[{chain}]", "-map", "0:a:0", *VENC, "-c:a", "copy",
        "-t", f"{length:.3f}", out])
    return out


# ── 4. plansze ────────────────────────────────────────────────────────────
def outro_over_video(png, length, out, src_name="IMG_1601", ss=2.30,
                     fade_in=0.25, fade_out=0.55):
    """Plansza końcowa NA UJĘCIU, nie na czarnym tle.

    W tle biegacz (cień na drodze) — domknięcie wraca tam, gdzie short się
    zaczął. Czarna płachta czyta się jak koniec pliku; kadr z ruchem czyta się
    jak koniec myśli.
    """
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1")
    fc = (f"[0:v]{vf}[bg];[bg][1:v]overlay=0:0,"
          f"fade=t=in:st=0:d={fade_in},"
          f"fade=t=out:st={length - fade_out:.3f}:d={fade_out},"
          f"format=yuv420p[v]")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{ss:.2f}", "-t", f"{length:.3f}", "-i", src(src_name),
        "-i", png,
        "-f", "lavfi", "-t", f"{length:.3f}", "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-filter_complex", fc, "-map", "[v]", "-map", "2:a", *VENC, *AENC,
        "-shortest", out])
    return out


def plate_clip(png, length, out, fade_in=0.0, fade_out=0.25):
    vf = [f"scale={W}:{H}", f"fps={FPS}", "setsar=1", "format=yuv420p"]
    if fade_in:
        vf.append(f"fade=t=in:st=0:d={fade_in}")
    if fade_out:
        vf.append(f"fade=t=out:st={length - fade_out:.3f}:d={fade_out}")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-t", f"{length:.3f}", "-i", png,
        "-f", "lavfi", "-t", f"{length:.3f}", "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-vf", ",".join(vf), *VENC, *AENC, "-shortest", out])
    return out


def silent(video, out):
    """Klip bez ścieżki → ta sama długość, ale z ciszą; concat wymaga kompletu."""
    length = dur(video)
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", video, "-f", "lavfi", "-t", f"{length:.3f}", "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", *AENC, "-shortest", out])
    return out


# ── 5. dźwięk na końcu, jednym przebiegiem ────────────────────────────────
def finalize_audio(video, out):
    """`loudnorm` liczymy RAZ, na całości, i sprawdzamy długość przed muxem.

    Filtr buforuje i potrafi wypuścić strumień dłuższy niż wejście — `-t` na
    wyjściu tego nie ucina (.ai/memory/montaz-pulapki-synchronizacji, pkt 3).
    Dlatego dźwięk idzie osobnym przebiegiem do pliku, porównujemy długości
    i dopiero wtedy sklejamy.
    """
    vlen = dur(video, "v:0")
    wav = os.path.join(WORK, "final-audio.wav")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", video,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "2", wav])
    alen = dur(wav)
    print(f"  długość obraz {vlen:.3f}s / dźwięk po loudnorm {alen:.3f}s "
          f"(różnica {abs(alen - vlen) * 1000:.0f} ms)")
    if alen < vlen - 0.05:
        raise SystemExit("dźwięk krótszy od obrazu — nie muksuję")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", video, "-i", wav, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", *AENC, "-t", f"{vlen:.3f}",
        "-movflags", "+faststart", out])
    return out


def main():
    os.makedirs(WORK, exist_ok=True)
    tl = timeline()

    print("· kompozycja obrazu")
    main_v = compose(tl)

    print("· domknięcie")
    photo_v = silent(patch_photo(os.path.join(WORK, "patch-photo.mp4")),
                     os.path.join(WORK, "photo.mp4"))
    outro = outro_over_video(os.path.join(OV, "outro-question.png"), OUTRO_DUR,
                             os.path.join(WORK, "outro.mp4"))

    lst = os.path.join(WORK, "final-concat.txt")
    with open(lst, "w") as fh:
        for p in (main_v, photo_v, outro):
            fh.write(f"file '{p}'\n")
    joined = os.path.join(WORK, "joined.mp4")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", lst,
        "-c:v", "copy", *AENC, joined])

    print("· dźwięk")
    out = os.path.join(BUILD, "final-nomusic.mp4")
    finalize_audio(joined, out)
    print(f"\n{out}\n  {dur(out):.2f}s  (treść {dur(main_v):.2f}s "
          f"+ zdjęcie {dur(photo_v):.2f}s + outro {dur(outro):.2f}s; "
          f"tytuł na pierwszych {TITLE_DUR}s obrazu)")


if __name__ == "__main__":
    main()
