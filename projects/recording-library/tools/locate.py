#!/usr/bin/env python3
"""Gdzie w surowym nagraniu jest moment z gotowego filmu — do poprawek Mateusza.

Uwaga z galerii wygląda tak: `ep-doram__youtube-A 4:12 — urywa słowo`. Czas filmu ≠ czas
źródła (wycięte pauzy, sklejki, składanki, plansza końcowa po klipie), więc przed zmianą
cięcia przeliczamy: który klip, który przedział EDL, sekunda źródła i słowa wokół.

  python3 tools/locate.py ep-doram 4:12
  python3 tools/locate.py ad-14-r4 0:15
  python3 tools/locate.py ep-8-wdrozen 6:50        # składanka → klip składowy
"""
import json
import sys

from sources import LIBRARY, load_clips


def seconds(text):
    m, _, s = text.rpartition(":")
    return int(m or 0) * 60 + float(s)


def locate(clip_id, t):
    clips = {c["id"]: c for c in load_clips()}
    clip = clips[clip_id.split("--")[0].split("__")[0]]
    if clip.get("parts"):     # składanka: zejdź do klipu składowego
        part = max((p for p in clip["parts"] if p["start"] <= t), key=lambda p: p["start"])
        print(f"składanka → {part['clip']} @ {t - part['start']:.2f} s")
        return locate(part["clip"], t - part["start"])
    if t > clip["duration"]:
        print(f"{t:.2f} s to plansza końcowa (klip ma {clip['duration']:.2f} s)")
        return
    offset = 0.0
    for i, (a, b) in enumerate(clip["ranges"]):
        if t <= offset + (b - a):
            src = a + (t - offset)
            print(f"{clip['id']}: przedział {i} [{a:.2f}–{b:.2f}] źródła „{clip['source']}”, sekunda źródła {src:.2f}")
            break
        offset += b - a
    words = json.load(open(LIBRARY / clip["id"] / "words.json"))
    near = [w for w in words if t - 4 <= w["start"] <= t + 4]
    print("słowa:", " ".join(("▶" if abs(w["start"] - t) < 0.4 else "") + w["word"] for w in near))
    splices = json.load(open(LIBRARY / clip["id"] / "splices.json"))
    close = [s for s in splices if abs(s - t) < 2]
    if close:
        print("sklejki w pobliżu (czas filmu):", ", ".join(f"{s:.2f}" for s in close))


if __name__ == "__main__":
    locate(sys.argv[1], seconds(sys.argv[2]))
