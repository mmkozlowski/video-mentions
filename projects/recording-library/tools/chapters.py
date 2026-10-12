#!/usr/bin/env python3
"""Rozdziały YouTube z storyboardu odcinka: "chapters": [["kotwica", "tytuł"], …].

Kotwice to słowa z transkrypcji (jak w zdarzeniach), więc rozdziały same przesuwają się,
gdy zmienia się cięcie. YouTube wymaga: pierwszy rozdział 0:00, co najmniej trzy,
każdy ≥ 10 s.

  python3 tools/chapters.py ep-doram     # → final/samples/ep-doram__chapters.txt
"""
import json
import sys

from package import FINAL, PACK, LIBRARY, Clock
from sources import DATA


def stamp(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def main(clip_id):
    board = json.load(open(PACK / "storyboards" / f"{clip_id}.json"))
    words = json.load(open(LIBRARY / clip_id / "words.json"))
    fixes = json.load(open(DATA / "caption-fixes.json"))
    clock = Clock(words, fixes)
    rows, cursor = [], 0.0
    for anchor, title in board["chapters"]:
        at = 0.0 if not rows else clock.at(anchor, floor=cursor)
        if rows and at - rows[-1][0] < 10:
            raise SystemExit(f"rozdział „{title}” krótszy niż 10 s po poprzednim — YouTube go odrzuci")
        rows.append((at, title))
        cursor = at
    if len(rows) < 3:
        raise SystemExit(f"{len(rows)} rozdziały — YouTube wymaga co najmniej trzech")
    text = "\n".join(f"{stamp(t)} {title}" for t, title in rows) + "\n"
    out = FINAL / f"{clip_id}__chapters.txt"
    out.write_text(text)
    print(text, end="")
    print("→", out)


if __name__ == "__main__":
    main(sys.argv[1])
