#!/usr/bin/env python3
"""Tnie bibliotekę klipów z data/clips.json → build/library/<id>/.

Każdy klip dostaje:
  master.mp4    16:9, kadr źródła 1:1 (do HyperFrames i montażu poziomego)
  vertical.mp4  9:16, twarz u góry + wolny panel na grafikę u dołu
  words.json    słowa z transkrypcji przeliczone na oś klipu (pod napisy)
  thumb.jpg     klatka z pierwszej sekundy hooka

Zasady z .ai/memory: przy -ss zawsze przekodowanie (nigdy -c copy — tnie po
klatkach kluczowych), obraz i dźwięk z tego samego punktu jednym przebiegiem,
żadnego scale=W:H na innych proporcjach (crop, nie rozciąganie).

  python3 tools/cut.py                # wszystko, co nie jest jeszcze wycięte
  python3 tools/cut.py --force        # od nowa
  python3 tools/cut.py ad-m1 ep-doram # tylko wskazane id (prefiks wystarczy)
  python3 tools/cut.py --no-vertical  # same mastery (szybciej)
  python3 tools/cut.py --words-only   # tylko words.json i splices.json (bez kodowania)
"""
import json
import subprocess
import sys

from sources import DATA, FACE_CENTER_X, LIBRARY, SOURCE_W, SOURCES, VERTICAL, load_words


def words_in(words, ranges):
    """Słowa z przedziałów źródła przeliczone na oś sklejonego klipu.

    Słowo trafia do przedziału, z którym ma największą część wspólną, i jest do niego
    przycinane. Czasy Whispera bywają przesunięte w ciszę („Jestem” zaczyna się 0,6 s
    przed głosem) — gdy tę ciszę wycina fillers.py, słowo liczone po samym początku
    wypadało z napisów i z kotwic storyboardu, choć jego dźwięk w klipie został."""
    offsets, total = [], 0.0
    for a, b in ranges:
        offsets.append(total)
        total += b - a
    out = []
    for w in words:
        overlaps = [(min(w["end"], b) - max(w["start"], a), i) for i, (a, b) in enumerate(ranges)]
        best, i = max(overlaps)
        if best > 0:
            a, b = ranges[i]
            out.append({"word": w["word"].strip(), "start": round(max(w["start"], a) - a + offsets[i], 3),
                        "end": round(min(w["end"], b) - a + offsets[i], 3)})
            continue
        # słowo w całości w wyciętej luce: przesunięte w ciszę („Na” 0,5 s przed głosem)
        # — jeśli luka jest krótka i ma najwyżej dwa takie słowa, dźwięk jest tuż za nią
        # luka liczona po czasie ŹRÓDŁA — w odcinkach zakresy nie zawsze idą po kolei
        after = [(a, j) for j, (a, _) in enumerate(ranges) if a >= w["end"]]
        before = [b for _, b in ranges if b <= w["start"]]
        if not after or not before:
            continue
        gap_to, nxt = min(after)
        gap_from = max(before)
        if gap_to - gap_from > 2.0:
            continue
        if sum(1 for x in words if x["start"] >= gap_from and x["end"] <= gap_to) > 2:
            continue
        at = round(offsets[nxt], 3)
        out.append({"word": w["word"].strip(), "start": at, "end": round(at + 0.1, 3)})
    return out


def vertical_filter(source):
    v = VERTICAL
    x = FACE_CENTER_X[source] - v["face_crop_w"] // 2
    x = max(0, min(SOURCE_W - v["face_crop_w"], x))
    return (
        f"crop={v['face_crop_w']}:{v['face_crop_h']}:{x}:0,"
        f"scale={v['w']}:{v['face_h']}:flags=lanczos,setsar=1,"
        f"pad={v['w']}:{v['h']}:0:0:color={v['panel_color']}"
    )


def splice_graph(ranges, offset, vertical_of=None):
    """Sklejka dubli jednym przebiegiem: trim/atrim per przedział + concat.

    Na każdej sklejce 12 ms fade dźwięku — bez tego cięcie w środku fali trzaska.
    """
    parts, labels = [], ""
    for i, (a, b) in enumerate(ranges):
        s, e = a - offset, b - offset
        parts.append(f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{i}]")
        parts.append(f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.012,afade=t=out:st={max(0, e - s - 0.012):.3f}:d=0.012[a{i}]")
        labels += f"[v{i}][a{i}]"
    post = f",{vertical_filter(vertical_of)}" if vertical_of else ""
    parts.append(f"{labels}concat=n={len(ranges)}:v=1:a=1[vc][a];[vc]null{post}[v]")
    return ";".join(parts)


def render(clip, kind, out):
    offset = max(0.0, clip["ranges"][0][0] - 1.0)
    span = clip["ranges"][-1][1] - offset + 0.5
    graph = splice_graph(clip["ranges"], offset, clip["source"] if kind == "vertical" else None)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", f"{offset:.3f}", "-t", f"{span:.3f}",
         "-i", str(SOURCES[clip["source"]]), "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", "30",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)],
        check=True)


def main(argv):
    force = "--force" in argv
    vertical = "--no-vertical" not in argv
    words_only = "--words-only" in argv
    wanted = [a for a in argv if not a.startswith("--")]
    clips = json.load(open(DATA / "clips.json"))
    words_cache = {}

    for clip in clips:
        if wanted and not any(clip["id"].startswith(w) for w in wanted):
            continue
        folder = LIBRARY / clip["id"]
        folder.mkdir(parents=True, exist_ok=True)
        master = folder / "master.mp4"
        recipe = {"source": clip["source"], "ranges": clip["ranges"]}
        recipe_file = folder / "recipe.json"
        fresh = recipe_file.exists() and json.load(open(recipe_file)) == recipe
        wants_vertical = vertical and clip["kind"] != "episode"
        complete = master.exists() and (not wants_vertical or (folder / "vertical.mp4").exists())
        if fresh and complete and not force and not words_only:
            continue

        print(f"✂  {clip['id']:<40} {clip['source']:<9} {clip['start']:8.2f}  "
              f"{clip['duration']:6.1f} s  sklejek {clip['splices']}", flush=True)
        if words_only:
            pass
        elif not (fresh and master.exists()) or force:
            render(clip, "master", master)
        if wants_vertical and not words_only:
            render(clip, "vertical", folder / "vertical.mp4")
        if clip["source"] not in words_cache:
            words_cache[clip["source"]] = load_words(clip["source"])
        json.dump(words_in(words_cache[clip["source"]], clip["ranges"]),
                  open(folder / "words.json", "w"), ensure_ascii=False, indent=0)
        # sklejki na osi klipu — package.py maskuje na nich skok obrazu zoomem
        joins = [round(sum(b - a for a, b in clip["ranges"][:i]), 3) for i in range(1, len(clip["ranges"]))]
        json.dump(joins, open(folder / "splices.json", "w"))
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "0.6", "-i", str(master),
                        "-frames:v", "1", "-vf", "scale=640:-1", str(folder / "thumb.jpg")],
                       check=True)
        if not words_only:   # bez kodowania przepis nie jest jeszcze wykonany
            json.dump(recipe, open(recipe_file, "w"))


if __name__ == "__main__":
    main(sys.argv[1:])
