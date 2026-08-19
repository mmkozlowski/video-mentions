#!/usr/bin/env python3
"""Etap 1 montażu: z listy `edl.py` robi surowy skład bez pauz.

Co robi, po kolei:
  1. dla każdego wpisu EDL mierzy ciszę wewnątrz zakresu (`silencedetect`),
  2. rozbija zakres na podklipy tak, żeby pauzę dłuższą niż PAUSE_MAX skrócić
     do PAUSE_KEEP,
  3. renderuje każdy podklip osobno do 1080x1920/30 fps (obraz i dźwięk z tego
     SAMEGO punktu tego samego pliku — inaczej rozjedzie się synchronizacja),
  4. skleja wszystko concat demuxerem w `build/rough.mp4`.

Trzy rzeczy, których tu celowo NIE ma i nie wolno ich dokładać:
  - `-c copy` przy `-ss` — kopia strumienia tnie po klatkach kluczowych i
    ląduje nawet sekundę obok żądanego punktu,
  - `loudnorm` na podklipie — buforuje i wypuszcza dłuższy strumień niż
    wejście, więc audio przestaje pasować do obrazu; poziom wyrównujemy
    statycznym `volume`, a `loudnorm` idzie dopiero na gotową całość,
  - `scale=1080:1920` na materiale o innych proporcjach — deformuje. Źródło
    jest 1920x1080 z `rotation=-90`, więc po autoobrocie ma dokładnie 1080x1920
    i skalowanie jest tożsamościowe; skrypt to sprawdza i przerywa, gdy nie jest.

Użycie:
    python3 tools/cut.py            # cały skład
    python3 tools/cut.py a04 b05    # tylko wskazane wpisy (podgląd)
    python3 tools/cut.py --plan     # sam plan cięć, bez renderu
"""
import json
import os
import re
import subprocess
import sys

from edl import EDL, EDGE_PAD, FPS, H, PAUSE_KEEP, PAUSE_MAX, SOURCES, W

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BUILD = os.path.join(ROOT, "build")
CUTS = os.path.join(BUILD, "cuts")
WORK = os.path.join(BUILD, "work")

# Minimalna długość podklipu — krótszy czyta się jak usterka, nie jak cięcie.
MIN_PIECE = 0.22
# Mikrofade na stykach, żeby cięcie nie strzelało w słuchawkach.
CLICK_FADE = 0.008


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def src_path(name):
    for ext in (".mov", ".MOV", ".mp4"):
        for base in (ROOT, os.path.join(ROOT, "assets", "raw")):
            p = os.path.join(base, name + ext)
            if os.path.exists(p):
                return p
    raise SystemExit(f"brak pliku źródłowego: {name}")


def probe_display_size(path):
    """Rozmiar PO uwzględnieniu rotacji — czyli to, co zobaczy widz."""
    out = sh(["ffprobe", "-v", "error", "-select_streams", "v:0",
              "-show_entries", "stream=width,height",
              "-show_entries", "stream_side_data=rotation",
              "-of", "json", path]).stdout
    d = json.loads(out)["streams"][0]
    w, h = d["width"], d["height"]
    rot = 0
    for sd in d.get("side_data_list", []):
        if "rotation" in sd:
            rot = int(sd["rotation"])
    if abs(rot) % 180 == 90:
        w, h = h, w
    return w, h


def detect_silence(path, tin, tout, gain_db, outdoor, silence_db):
    """Cisza wewnątrz zakresu, zmierzona — nie zgadnięta.

    Filtr wejściowy jest ten sam co przy renderze (wzmocnienie + odcięcie
    dudnienia wiatru), bo próg liczony na innym sygnale wskazywałby ciszę
    w innych miejscach niż ta, którą finalnie usłyszymy. Próg jest per plik
    (`silence_db` w `edl.py`) — jedna wartość dla nagrania w biegu i w domu
    nie istnieje.
    """
    af = [f"volume={gain_db}dB"]
    if outdoor:
        af.append("highpass=f=110")
    af.append(f"silencedetect=noise={silence_db}dB:d=0.20")
    p = sh(["ffmpeg", "-hide_banner", "-nostats",
            "-ss", f"{tin:.3f}", "-to", f"{tout:.3f}", "-i", path,
            "-vn", "-af", ",".join(af), "-f", "null", os.devnull])
    spans, start = [], None
    for m in re.finditer(r"silence_(start|end): (-?[\d.]+)", p.stderr):
        kind, val = m.group(1), float(m.group(2))
        if kind == "start":
            start = val
        elif start is not None:
            spans.append((tin + start, tin + val))
            start = None
    if start is not None:
        spans.append((tin + start, tout))
    return spans


def plan_pieces(item):
    """Zakres EDL → lista podklipów po wycięciu zbyt długich pauz."""
    cfg = SOURCES[item["src"]]
    tin, tout = item["tin"], item["tout"]
    if item.get("cover"):
        return [(tin, tout)]

    path = src_path(item["src"])
    spans = detect_silence(path, tin, tout, cfg["gain_db"], cfg["outdoor"],
                           cfg["silence_db"])

    pause_max = item.get("pause_max", PAUSE_MAX)
    pieces, cursor = [], tin
    for s0, s1 in spans:
        if s1 - s0 <= pause_max:
            continue
        # Pauzę zostawiamy skróconą do PAUSE_KEEP, doklejoną do końca mowy.
        keep_to = min(s0 + PAUSE_KEEP + EDGE_PAD, s1)
        if keep_to - cursor >= MIN_PIECE:
            pieces.append((cursor, keep_to))
        cursor = max(s1 - EDGE_PAD, keep_to)
    if tout - cursor >= MIN_PIECE:
        pieces.append((cursor, tout))
    return pieces or [(tin, tout)]


def render_piece(item, idx, sub, t0, t1, out_path):
    cfg = SOURCES[item["src"]]
    path = src_path(item["src"])
    dur = t1 - t0

    vf = [f"scale={W}:{H}:force_original_aspect_ratio=decrease",
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black"]

    # Zbliżenie: powiększ i przytnij z powrotem do 1080x1920. Nigdy `scale=W:H`
    # na innych proporcjach — to deformuje twarz i widać to od razu
    # (.ai/memory/nigdy-nie-rozciagaj-kadru).
    zoom = float(item.get("zoom", 1.0))
    if zoom > 1.001:
        zw, zh = int(round(W * zoom / 2)) * 2, int(round(H * zoom / 2)) * 2
        dy = int(item.get("yshift", 0))
        # Środek kadrowania z ograniczeniem do wnętrza powiększonej klatki.
        y = max(0, min(zh - H, (zh - H) // 2 + dy))
        vf += [f"scale={zw}:{zh}", f"crop={W}:{H}:{(zw - W) // 2}:{y}"]

    if item.get("lift"):
        # Ekran filmowany w kontrze jest za ciemny na telefonie.
        vf.append("eq=brightness=0.06:contrast=1.16:saturation=1.06")

    vf += [f"fps={FPS}", "setsar=1", "format=yuv420p"]

    if item.get("mute"):
        af = ["volume=0"]
    else:
        af = [f"volume={cfg['gain_db']}dB"]
        if cfg["outdoor"]:
            af += ["highpass=f=110", "afftdn=nr=8:nf=-30"]
    fade = min(CLICK_FADE, dur / 4)
    af += [f"afade=t=in:st=0:d={fade:.3f}",
           f"afade=t=out:st={max(dur - fade, 0):.3f}:d={fade:.3f}",
           "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"]

    cmd = ["ffmpeg", "-y", "-hide_banner", "-nostats", "-loglevel", "error",
           "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}", "-i", path,
           "-map", "0:v:0", "-map", "0:a:0",
           "-vf", ",".join(vf), "-af", ",".join(af),
           "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           "-movflags", "+faststart", out_path]
    p = sh(cmd)
    if p.returncode != 0:
        raise SystemExit(f"render {out_path} padł:\n{p.stderr[-1500:]}")
    return out_path


def duration(path):
    out = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
              "-of", "csv=p=0", path]).stdout.strip()
    return float(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    plan_only = "--plan" in sys.argv
    items = [i for i in EDL if not args or i["key"] in args]

    os.makedirs(CUTS, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)

    # Kontrola założenia o kadrze — patrz docstring.
    for name in {i["src"] for i in items}:
        w, h = probe_display_size(src_path(name))
        if (w, h) != (W, H):
            print(f"⚠ {name}: kadr po rotacji {w}x{h}, nie {W}x{H} — "
                  f"wchodzi pad, nie rozciąganie")

    made, total_src, total_out = [], 0.0, 0.0
    timeline, cursor = [], 0.0
    for item in items:
        pieces = plan_pieces(item)
        src_len = item["tout"] - item["tin"]
        cut_len = sum(b - a for a, b in pieces)
        total_src += src_len
        total_out += cut_len
        drop = src_len - cut_len
        print(f"{item['key']}  {item['src']}  {src_len:5.2f}s → {cut_len:5.2f}s "
              f"(-{drop:4.2f}s, {len(pieces)} szt.)  {item['say'][:58]}")
        if plan_only:
            continue
        # Cache: podklip renderujemy tylko wtedy, gdy zmienił się jego przepis.
        # Bez tego każda poprawka jednej linijki w EDL kosztuje pełny przebieg.
        stamp = os.path.join(CUTS, f"{item['key']}.json")
        recipe = dict(pieces=[[round(a, 3), round(b, 3)] for a, b in pieces],
                      src=item["src"], mute=bool(item.get("mute")),
                      zoom=item.get("zoom", 1.0), yshift=item.get("yshift", 0),
                      pause_max=item.get("pause_max", PAUSE_MAX),
                      lift=bool(item.get("lift")), cfg=SOURCES[item["src"]])
        fresh = (os.path.exists(stamp)
                 and json.load(open(stamp)) == recipe
                 and all(os.path.exists(os.path.join(CUTS, f"{item['key']}-{n:02d}.mp4"))
                         for n in range(len(pieces))))
        for n, (a, b) in enumerate(pieces):
            out = os.path.join(CUTS, f"{item['key']}-{n:02d}.mp4")
            if not fresh:
                render_piece(item, item["key"], n, a, b, out)
            made.append(out)
        # Osierocone podklipy po skróceniu wpisu — inaczej concat wziąłby stare.
        for stale in sorted(os.listdir(CUTS)):
            if stale.startswith(f"{item['key']}-") and stale.endswith(".mp4"):
                if int(stale.split("-")[1][:2]) >= len(pieces):
                    os.remove(os.path.join(CUTS, stale))
        json.dump(recipe, open(stamp, "w"))
        span = sum(duration(os.path.join(CUTS, f"{item['key']}-{n:02d}.mp4"))
                   for n in range(len(pieces)))
        timeline.append(dict(key=item["key"], src=item["src"],
                             t0=round(cursor, 3), t1=round(cursor + span, 3),
                             say=item["say"]))
        cursor += span

    print(f"\nrazem: {total_src:.1f}s materiału → {total_out:.1f}s po wycięciu pauz "
          f"(-{total_src - total_out:.1f}s)")
    if plan_only:
        return

    # Mapa „gdzie na gotowej osi leży które ujęcie" — z niej korzysta etap 2
    # przy wstawianiu przebitek, plansz i dzielonego ekranu. Liczona z
    # ZMIERZONYCH długości plików, nie z planu, bo koder zaokrągla do klatki.
    json.dump(timeline, open(os.path.join(WORK, "timeline.json"), "w"),
              ensure_ascii=False, indent=1)

    lst = os.path.join(WORK, "concat.txt")
    with open(lst, "w") as fh:
        for p in made:
            fh.write(f"file '{p}'\n")

    rough = os.path.join(BUILD, "rough.mp4")
    p = sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", lst,
            "-c", "copy", "-movflags", "+faststart", rough])
    if p.returncode != 0:
        raise SystemExit(f"concat padł:\n{p.stderr[-1500:]}")

    # Kontrola z pamięci projektu: audio nie może być dłuższe niż obraz.
    va = sh(["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=duration", "-of", "csv=p=0", rough]).stdout.strip()
    aa = sh(["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=duration", "-of", "csv=p=0", rough]).stdout.strip()
    print(f"\n{rough}\n  obraz {va}s / dźwięk {aa}s / kontener {duration(rough):.2f}s")


if __name__ == "__main__":
    main()
