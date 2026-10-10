#!/usr/bin/env python3
"""Odcinek-składanka z gotowych klipów biblioteki (bez nowego nagrania).

Mateusz 10.10: „8 wdrożeń Open Mercato — oferty” ma 3:17 i obiecuje osiem wdrożeń, a mówi
o jednym. Przegląd skleja ep-offers z rozdziałami innych case'ów (doram, marpasz, rezon,
vacuactiv) — jedna korzyść na rozdział. Te same fragmenty żyją też w pełnych odcinkach:
przegląd to wejście, pełne odcinki to rozwinięcie (linki na kartach).

Wynik jak każdy klip biblioteki — build/library/<id>/master.mp4 + words.json + splices.json —
plus wpis w data/compilations.json (build_clips.py go nie nadpisze).

  python3 tools/compile_episode.py
"""
import json
import subprocess

from sources import DATA, LIBRARY

COMPILATIONS = {
    "ep-8-wdrozen": dict(
        title="8 wdrożeń Open Mercato — co dały firmom",
        brand="flowbiz",
        parts=["ep-open-mercato-offers", "ch-doram-5-70-94", "ch-doram-6-kody-15-minut", "ch-marpasz-2-100-godzin",
               "ch-marpasz-3-katalog-ai", "ch-rezon-3-panel-klienta", "ch-vacu-5-kierownik-w-godzine", "ch-marpasz-4-srubki"],
    ),
}


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout
    return float(out.strip().split(",")[0])


def build(cid, spec):
    folder = LIBRARY / cid
    folder.mkdir(parents=True, exist_ok=True)
    words, splices, starts, offset = [], [], [], 0.0
    for part in spec["parts"]:
        master = LIBRARY / part / "master.mp4"
        length = duration(master)
        starts.append((part, round(offset, 3)))
        for w in json.load(open(LIBRARY / part / "words.json")):
            words.append(dict(w, start=round(w["start"] + offset, 3), end=round(w["end"] + offset, 3)))
        for s in json.load(open(LIBRARY / part / "splices.json")):
            splices.append(round(s + offset, 3))
        if offset:
            splices.append(round(offset, 3))   # łączenie części maskuje skok zoomu jak każda sklejka
        offset += length
    inputs = sum((["-i", str(LIBRARY / p / "master.mp4")] for p in spec["parts"]), [])
    n = len(spec["parts"])
    graph = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(folder / "master.mp4")],
                   check=True)
    json.dump(words, open(folder / "words.json", "w"), ensure_ascii=False, indent=0)
    json.dump(sorted(splices), open(folder / "splices.json", "w"))
    total = round(duration(folder / "master.mp4"), 2)
    print(f"{cid}: {total} s, {n} części")
    for part, at in starts:
        print(f"  {int(at // 60)}:{int(at % 60):02d}  {part}")
    return dict(id=cid, title=spec["title"], brand=spec["brand"], kind="episode", source="session", duration=total,
                priority="A", scores=dict(total=0), parts=[dict(clip=p, start=a) for p, a in starts])


def main():
    entries = [build(cid, spec) for cid, spec in COMPILATIONS.items()]
    json.dump(entries, open(DATA / "compilations.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
