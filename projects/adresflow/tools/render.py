#!/usr/bin/env python3
"""Montaż reklam AdresFlow 9:16 — animacja napisów linia po linii.

Każda linia wjeżdża osobno z efektem "pop": skala 0.86 → 1.06 → 1.00
(przeskoczenie), do tego szybki fade i mikro-slide. Linie wchodzą kaskadowo
z opóźnieniem 0.13 s, co daje rytm typowy dla rolek.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SHOTS_DIR = os.path.join(ROOT, "assets", "shots")
VOICE     = os.path.join(ROOT, "assets", "voice")
MUSIC     = os.path.join(ROOT, "assets", "music", "music.mp3")
BUILD     = os.path.join(ROOT, "build")
OV        = os.path.join(BUILD, "overlays")
os.makedirs(os.path.join(BUILD, "cache"), exist_ok=True)

# wersja: (plik źródłowy, długość, crop treści lub None, opcje)
# v3 jedzie z materiału podbitego do 2K przez upscale_video (preset aigc)
#
# opcje:
#   ramp  — przyspiesza początek materiału, żeby ruch był od 1. sekundy
#           (predictor: statyczny start = hook_score 27/100)
#   shock — wstawia planszę z kwotą przed materiałem
JOBS = {
    "v1":  ("rzut3d-8s-raw.mp4", 8.00, "720:839:0:220", {}),
    "v2":  ("raw-v2-karta.mp4",  8.00, None, {}),
    "v3":  ("raw-v3-2k.mp4",     6.00, None, {}),
    "v3d": ("raw-v3-2k.mp4",     6.00, None, {"ramp": (2.6, 2.6)}),
    "v3e": ("raw-v3-2k.mp4",     6.00, None, {"ramp": (2.6, 2.6)}),
    "v3b": ("raw-v3-2k.mp4",     6.00, None, {"ramp": (2.6, 2.6), "shock": 1.1}),
}


def ramped_duration(dur, ramp):
    """Długość materiału po przyspieszeniu początku."""
    head, factor = ramp
    return head / factor + (dur - head)

POP_D    = 0.34   # czas trwania efektu pop
CASCADE  = 0.13   # opóźnienie między linią 1 a 2
END_MIN  = 2.4    # minimalna długość endcarda (gdy nie ma lektora)
TAIL     = 0.40   # cisza po lektorze przed końcem


def _music_mix(music, total, vo_idx, mus_idx):
    """Podkład z duckingiem — ta sama logika co w story.py.

    Start od najgłośniejszego fragmentu (biblioteczne podkłady mają ciche
    intro), łagodny ducking, całość do -14 LUFS.
    """
    import story  # noqa: E402 — współdzielone stałe i music_offset
    off = story.music_offset(music, total)
    return (f";[{mus_idx}:a]atrim={off:.2f},asetpts=PTS-STARTPTS,"
            f"aloop=loop=-1:size=2e9,atrim=0:{total:.3f},"
            f"volume={story.MUS_VOL},afade=t=in:st=0:d=0.35,"
            f"afade=t=out:st={max(0.1, total - 0.6):.3f}:d=1.0[mus];"
            f"[{vo_idx}]asplit[vo1][vosc];"
            f"[mus][vosc]sidechaincompress=threshold={story.MUS_THRESH}:"
            f"ratio={story.MUS_RATIO}:attack=8:release=260[duck];"
            f"[vo1][duck]amix=inputs=2:duration=first:normalize=0,"
            f"loudnorm=I=-14:TP=-1.5:LRA=11[aout]")


def probe_dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out) if out else 0.0


def pop_expr(st, base):
    """Skala z przeskoczeniem: 0.86 → 1.06 → 1.00, potem stała."""
    u = f"(t-{st:.3f})/{POP_D}"
    return (f"'{base}*if(lt(t,{st:.3f}),0.86,"
            f"if(lt({u},0.6),0.86+0.20*(({u})/0.6),"
            f"if(lt({u},1),1.06-0.06*((({u})-0.6)/0.4),1)))'")


def layer(idx, m, st, fade_out, tag):
    """Filtry dla jednej animowanej linii: skala + fade + overlay wyśrodkowany."""
    w, h, cx, cy = m["w"], m["h"], m["cx"], m["cy"]
    sw = pop_expr(st, w)
    sh = pop_expr(st, h)
    f = (f"[{idx}:v]format=rgba,"
         f"scale=eval=frame:w={sw}:h={sh},"
         f"fade=t=in:st={st:.3f}:d=0.16:alpha=1,"
         f"fade=t=out:st={fade_out:.3f}:d=0.25:alpha=1[{tag}];")
    # slide-up gaśnie razem z popem
    y = (f"'{cy}-h/2+if(lt(t,{st + POP_D:.3f}),"
         f"({st + POP_D:.3f}-t)*90,0)'")
    o = f"overlay=x='({cx})-w/2':y={y}:enable='between(t,{st:.3f},{fade_out + 0.25:.3f})'"
    return f, o


def build(ver):
    src, src_dur, crop, opts = JOBS[ver]
    meta = json.load(open(f"{OV}/{ver}.json"))["lines"]
    ramp = opts.get("ramp")
    shock = opts.get("shock", 0.0)
    dur = ramped_duration(src_dur, ramp) if ramp else src_dur
    dur += shock

    # lektor (opcjonalny) wyznacza długość endcarda — plansza końcowa czeka,
    # aż głos skończy, zamiast ucinać zdanie w połowie
    vo = os.path.join(VOICE, f"vo-{ver}.mp3")
    has_vo = os.path.exists(vo)
    if has_vo:
        vo_d = probe_dur(vo)
        end_d = max(END_MIN, vo_d + TAIL - dur + 0.45)
    else:
        vo_d, end_d = 0.0, END_MIN

    # napisy wchodzą po planszy cenowej (jeśli jest), inaczej od razu
    h_in  = shock + 0.35 if shock else 0.40
    h_out = shock + (dur - shock) * 0.46
    p_in  = h_out + 0.28
    p_out = dur - 0.55

    if crop:
        pre = (f"[0:v]crop={crop},split[bgs][fgs];"
               f"[bgs]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
               f"gblur=sigma=45,eq=brightness=-0.20:saturation=1.25[bgb];"
               f"[fgs]scale=1080:-2[fgv];"
               f"[bgb][fgv]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,"
               f"eq=saturation=1.06:contrast=1.04[norm];")
    else:
        pre = ("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
               "crop=1080:1920,setsar=1,fps=30,"
               "eq=saturation=1.06:contrast=1.04[norm];")

    # speed ramp: pierwsze `head` sekund leci `factor` razy szybciej
    if ramp:
        head, factor = ramp
        pre += (f"[norm]split[rh][rt];"
                f"[rh]trim=0:{head},setpts=(PTS-STARTPTS)/{factor}[fast];"
                f"[rt]trim={head},setpts=PTS-STARTPTS[slow];"
                f"[fast][slow]concat=n=2:v=1[sped];")
        cur = "sped"
    else:
        cur = "norm"

    # plansza z kwotą doklejona PRZED materiałem
    shock_in = []
    if shock:
        shock_in = ["-loop", "1", "-t", f"{shock}", "-i", f"{OV}/{ver}-shock.png"]
        pre += (f"[SHOCKIDX:v]scale=1080:1920,setsar=1,fps=30,"
                f"trim=0:{shock},setpts=PTS-STARTPTS[shk];"
                f"[shk][{cur}]concat=n=2:v=1[base];")
    else:
        pre += f"[{cur}]null[base];"

    inputs = ["-i", os.path.join(SHOTS_DIR, src)] + shock_in
    # 1 = chrome, potem kolejne linie
    order = [("chrome", None, None)]
    for i in (0, 1):
        order.append((f"hook{i}", h_in + i * CASCADE, h_out))
    for i in (0, 1):
        order.append((f"payoff{i}", p_in + i * CASCADE, p_out))

    for name, _, _ in order:
        inputs += ["-loop", "1", "-t", f"{dur}", "-i", f"{OV}/{ver}-{name}.png"]

    # plansza cenowa (gdy jest) zajmuje wejście 1 i przesuwa resztę
    first = 2 if shock else 1
    pre = pre.replace("SHOCKIDX", "1")

    filters = [pre]
    chain = "base"
    for idx, (name, st, fo) in enumerate(order, start=first):
        if name == "chrome":
            filters.append(f"[{idx}:v]format=rgba,fade=t=in:st=0.15:d=0.4:alpha=1,"
                           f"fade=t=out:st={dur - 0.5:.3f}:d=0.35:alpha=1[chr];")
            filters.append(f"[{chain}][chr]overlay=0:0[c{idx}];")
        else:
            f, o = layer(idx, meta[name], st, fo, f"L{idx}")
            filters.append(f)
            filters.append(f"[{chain}][L{idx}]{o}[c{idx}];")
        chain = f"c{idx}"

    fc = "".join(filters).rstrip(";").replace(f"[{chain}];", f"[{chain}]")
    if not fc.endswith(f"[{chain}]"):
        fc += ""

    body = f"{BUILD}/cache/.tmp-{ver}-body.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs,
                    "-filter_complex", fc, "-map", f"[{chain}]",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-pix_fmt", "yuv420p", body], check=True)

    endm = f"{BUILD}/cache/.tmp-{ver}-end.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", f"{end_d:.3f}",
                    "-i", f"{OV}/{ver}-end.png", "-filter_complex",
                    f"[0:v]scale=2160:3840,zoompan=z='min(1.06,1+0.06*on/(30*{end_d:.3f}))':d=1:"
                    f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,setsar=1[v]",
                    "-map", "[v]", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-pix_fmt", "yuv420p", endm], check=True)

    final = os.path.join(BUILD, f"adresflow-{ver}.mp4")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", body, "-i", endm]
    if has_vo:
        cmd += ["-i", vo]
        total = dur + end_d - 0.45
        fc = (f"[0:v][1:v]xfade=transition=fade:duration=0.45:offset={dur - 0.45:.3f},"
              f"format=yuv420p[v];"
              f"[2:a]adelay=200|200,afade=t=in:st=0:d=0.25,"
              f"afade=t=out:st={vo_d - 0.25:.3f}:d=0.25,"
              f"loudnorm=I=-16:TP=-1.5:LRA=11,apad,atrim=0:{total:.3f}[a]")
        music = MUSIC
        if os.path.exists(music):
            cmd += ["-i", music]
            fc += _music_mix(music, total, "a", 3)
            cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[aout]",
                    "-c:a", "aac", "-b:a", "192k"]
        else:
            cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-filter_complex",
                f"[0:v][1:v]xfade=transition=fade:duration=0.45:offset={dur - 0.45:.3f},"
                f"format=yuv420p[v]", "-map", "[v]"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-preset", "medium",
            "-movflags", "+faststart", final]
    subprocess.run(cmd, check=True)
    os.remove(body); os.remove(endm)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", final], capture_output=True, text=True).stdout.strip()
    print(f"== {ver}: {d}s")


if __name__ == "__main__":
    for v in (sys.argv[1:] or JOBS.keys()):
        build(v)
