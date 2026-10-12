#!/usr/bin/env python3
"""Katalog układów — prawdziwa klatka z gotowego filmu dla każdego rodzaju wstawki.

Mateusz 12.10: „mamy też różne układy przejść, tekstów i b-rolli” — wytyczne montażu
(WYTYCZNE-MONTAZU.md) opisują zasady, ten katalog pokazuje, jak każdy układ wygląda.
Przechodzi storyboardy z gotowym renderem, liczy czasy zdarzeń tak samo jak package.py
(bez renderu) i wycina klatkę ze środka zdarzenia.

  python3 tools/layout_catalog.py          # → final/catalog/<układ>.jpg + catalog.json
"""
import json
import subprocess

from package import FINAL, PACK, Composition, output_name, palettes_for
from sources import PROJECT, load_clips

OUT = PROJECT / "final" / "catalog"
PREFERRED = ["ep-open-mercato-offers", "ep-vibecoding", "ep-module", "ch-module", "ch-vibe", "ch-om"]   # wzorcowe najpierw


class Recorder(Composition):
    """Composition, która zapamiętuje czas każdego zdarzenia zamiast tylko budować HTML."""

    def __init__(self, *args):
        super().__init__(*args)
        self.seen = []
        for name in [n for n in dir(self) if n.startswith("card_")] + ["broll"]:
            self.wrap(name)

    def wrap(self, name):
        original = getattr(self, name)

        def recorded(ev, start, end):
            self.seen.append((ev, start, end))
            return original(ev, start, end)
        setattr(self, name, recorded)


def layout_key(ev, fmt):
    kind = ev["type"]
    if kind == "beat":
        return f"beat-{ev['style']}"
    if kind == "mockup":
        return f"mockup-{ev['name']}"
    if kind == "broll":
        return f"broll-{'full' if ev.get('full') and fmt != 'youtube' else fmt}"
    zone = ev.get("zone", "panel")
    return f"{kind}-{fmt}" + ("-lower" if zone == "lower" else "")


def priority(board_name):
    return next((i for i, p in enumerate(PREFERRED) if board_name.startswith(p)), len(PREFERRED))


def grab(video, at, target):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.2f}", "-i", str(video), "-frames:v", "1",
                    "-vf", "scale=640:-2", "-q:v", "4", str(target)], check=True, stdin=subprocess.DEVNULL)


def main():
    clips = load_clips()
    found = {}
    for path in sorted(PACK.glob("storyboards/*.json"), key=lambda p: priority(p.stem)):
        board = json.load(open(path))
        clip = next((c for c in clips if c["id"] == board["clip"]), None)
        if not clip:
            continue
        name = output_name(clip, board)
        for fmt in board.get("formats", ["reels", "ad", "youtube"]):
            pal = palettes_for(board, clip)[0]
            if pal != "A":   # katalog pokazuje markę FlowBiz; AI Słupsk ma własną paletę
                continue
            video = FINAL / f"{name}__{fmt}-{pal}.mp4"
            if not video.exists():
                continue
            try:
                comp = Recorder(clip, board, fmt, pal)
                comp.build()
            except (SystemExit, Exception) as error:   # stary storyboard z kotwicą sprzed przecięcia
                print(f"  pomijam {name} {fmt}: {error}")
                continue
            moments = [(layout_key(ev, fmt), s + min(1.4, (e - s) / 2), ev) for ev, s, e in comp.seen if "type" in ev]   # karty dopełniające panel nie są zdarzeniem storyboardu
            if comp.board.get("cover") and fmt != "youtube":
                moments.append((f"cover-{fmt}", min(1.0, comp.cover_end / 2), {}))
            if comp.hook_end:
                moments.append((f"hook-{fmt}", (comp.cover_end + comp.hook_end) / 2, {}))
            moments.append((f"endcard-{fmt}", comp.clip_len + comp.end_len * 0.7, {}))
            opening = max(comp.cover_end, comp.hook_end) + 0.3   # pod okładką i hookiem wstawki nie widać
            for key, at, ev in moments:
                if key not in found and (at >= opening or key.startswith(("cover", "hook"))):
                    found[key] = {"video": video.name, "at": round(at, 2), "board": path.stem,
                                  "label": ev.get("text") or ev.get("main") or ev.get("label") or ev.get("title") or ""}
    OUT.mkdir(parents=True, exist_ok=True)
    for key, item in sorted(found.items()):
        grab(FINAL / item["video"], item["at"], OUT / f"{key}.jpg")
        print(f"{key:<28} {item['video']} @ {item['at']}")
    json.dump(found, open(OUT / "catalog.json", "w"), ensure_ascii=False, indent=1)
    print(f"… {len(found)} układów → {OUT.relative_to(PROJECT)}")


if __name__ == "__main__":
    main()
