#!/usr/bin/env python3
"""Kontrola układu wszystkich wariantów przed renderem: storyboard × format × paleta.

Strefy kart, plansze i hook przycinają zawartość (overflow:hidden), więc każdy tekst,
który się nie zmieścił, `hyperframes check` zgłasza jako container_overflow — tu
zbieramy te zgłoszenia razem z błędami układu (✗) w jedną listę.

  python3 tools/layout_audit.py              # wszystko, 4 równolegle
  python3 tools/layout_audit.py ad-11 ad-28
"""
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from package import FORMATS, OUT, PACK, PALETTES, Composition, hf, stage
from sources import DATA

# przebitka i twarz celowo wystają poza ramkę przy zoomie — to nie jest błąd tekstu
IGNORED = re.compile(r"#(face-zoom|b\d+)\b")


def audit(clip, board, fmt, pal):
    folder = OUT / clip["id"] / f"{fmt}-{pal}"
    try:
        stage(Composition(clip, board, fmt, pal), folder)
    except SystemExit as error:
        return [f"storyboard: {error}"]
    out = hf(["check", "."], folder)
    text = out.stdout + out.stderr
    issues = [line.strip() for line in text.splitlines()
              if ("✗" in line or "container_overflow" in line) and not IGNORED.search(line)]
    if "Check failed" in text and not issues:
        issues.append("check failed: " + text.strip().splitlines()[-1][:160])
    return issues


def main(argv):
    clips = {c["id"]: c for c in json.load(open(DATA / "clips.json"))}
    boards = [json.load(open(p)) for p in sorted(PACK.glob("storyboards/*.json"))
              if not argv or any(p.stem.startswith(a) for a in argv)]
    jobs = [(clips[b["clip"]], b, fmt, pal) for b in boards
            for fmt in b.get("formats", FORMATS) for pal in PALETTES]
    with ThreadPoolExecutor(4) as pool:
        results = list(pool.map(lambda job: (job, audit(*job)), jobs))
    bad = 0
    for (clip, _, fmt, pal), issues in results:
        if issues:
            bad += 1
            print(f"✗ {clip['id']} {fmt}-{pal}")
            for issue in issues[:8]:
                print("   ", issue[:220])
    print(f"{len(jobs) - bad}/{len(jobs)} wariantów bez problemów układu")


if __name__ == "__main__":
    main(sys.argv[1:])
