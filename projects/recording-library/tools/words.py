#!/usr/bin/env python3
"""Wypis słów z transkrypcji w zakresie czasu — narzędzie do ustawiania cięć.

  python3 tools/words.py session 1110 1135     # słowa z czasami, przerwy > 0,45 s oznaczone ‖
"""
import sys

from sources import load_words

source, start, end = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
words = load_words(source)
previous_end = None
line = []
for w in words:
    if w["start"] < start or w["start"] > end:
        continue
    if previous_end is not None and w["start"] - previous_end > 0.45:
        print(" ".join(line))
        line = [f"‖{w['start'] - previous_end:.1f}s‖"]
    line.append(f"{w['start']:.2f}:{w['word'].strip()}")
    previous_end = w["end"]
print(" ".join(line))
