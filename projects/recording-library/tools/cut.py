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
"""
import json
import subprocess
import sys

from sources import DATA, FACE_CENTER_X, LIBRARY, SOURCE_W, SOURCES, VERTICAL, load_words


def words_in(words, ranges):
    """Słowa z przedziałów źródła przeliczone na oś sklejonego klipu."""
    out, offset = [], 0.0
    for a, b in ranges:
        for w in words:
            if w["start"] >= a and w["end"] <= b + 0.05:
                out.append({"word": w["word"].strip(), "start": round(w["start"] - a + offset, 3),
                            "end": round(min(w["end"], b) - a + offset, 3)})
        offset += b - a
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
        if fresh and complete and not force:
            continue

        print(f"✂  {clip['id']:<40} {clip['source']:<9} {clip['start']:8.2f}  "
              f"{clip['duration']:6.1f} s  sklejek {clip['splices']}", flush=True)
        if not (fresh and master.exists()) or force:
            render(clip, "master", master)
        if wants_vertical:
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
        json.dump(recipe, open(recipe_file, "w"))


if __name__ == "__main__":
    main(sys.argv[1:])
