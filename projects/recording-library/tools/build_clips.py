#!/usr/bin/env python3
"""edl.py + transkrypcje → data/clips.json (baza klipów) + data/catalog.md (ranking).

Granice przedziałów dociągane są do słów z Whispera: przed pierwszym słowem
zostaje oddech, po ostatnim — wybrzmienie, ale nigdy nie wchodzimy na sąsiednie
słowo (to byłby kawałek wyciętej powtórki).

  python3 tools/build_clips.py
"""
import json

import edl
from sources import DATA, load_words

PAD_HEAD = 0.35      # oddech przed pierwszym słowem klipu
PAD_SPLICE = 0.18    # na sklejce między dublami
PAD_TAIL = 0.80      # wybrzmienie po ostatnim słowie klipu
GUARD = 0.04         # minimalny odstęp od słowa, które ma NIE wejść


def snap(words, ranges):
    """Przedziały [od, do) → przedziały dociągnięte do słów + tekst."""
    resolved, text = [], []
    for index, entry in enumerate(ranges):
        a, b = entry[0], entry[1]
        # (od, do, dokładny_start, dokładny_koniec) — granica zmierzona ciszą w sygnale,
        # gdy czasy słów Whispera są przesunięte (None = dociągnij do słów jak zwykle)
        exact_start, exact_end = (entry[2], entry[3]) if len(entry) == 4 else (None, None)
        inside = [i for i, w in enumerate(words) if a - 0.05 <= w["start"] < b]
        if exact_start is not None:
            inside = [i for i in inside if words[i]["end"] > exact_start] or inside
        if not inside:
            raise SystemExit(f"pusty przedział {a}–{b}")
        first, last = inside[0], inside[-1]
        head = PAD_HEAD if index == 0 else PAD_SPLICE
        tail = PAD_TAIL if index == len(ranges) - 1 else PAD_SPLICE
        start = words[first]["start"] - head
        end = words[last]["end"] + tail
        if first > 0:
            start = max(start, words[first - 1]["end"] + GUARD)
        if last + 1 < len(words):
            end = min(end, words[last + 1]["start"] - GUARD)
        start = exact_start if exact_start is not None else start
        end = exact_end if exact_end is not None else end
        resolved.append([round(max(0.0, start), 3), round(end, 3)])
        text.append(" ".join(w["word"].strip() for w in words[first:last + 1]))
    return resolved, text


def placement(kind, brand, block, duration):
    """Gdzie klip ma sens — wynika z rodzaju, marki i długości."""
    uses = []
    if kind == "episode":
        return ["youtube-16x9"]
    if brand == "aislupsk":
        uses.append("aislupsk-listopad")
    if block in ("city", "production", "ceo-agent"):
        uses.append("meta-ads")
    if kind in ("ad", "chapter"):
        uses.append("reels-organic")
    if duration > 60:
        uses.append("needs-cutdown")
    return uses


def priority(hook, delivery):
    score = hook * 2 + delivery          # hook waży podwójnie: decyduje o 3 pierwszych sekundach
    return score, "A" if score >= 13 else "B" if score >= 11 else "C"


def main():
    words = {s: load_words(s) for s in ("session", "doram", "vacuactiv")}
    clips = []

    def add(entry, kind, source, clip_id):
        ranges, text = snap(words[source], entry["ranges"])
        duration = round(sum(b - a for a, b in ranges), 2)
        score, prio = priority(entry["hook"], entry["delivery"])
        brand = entry.get("brand", "flowbiz")
        clips.append({
            "id": clip_id, "kind": kind, "source": source,
            "n": entry.get("n"), "code": entry.get("code"), "block": entry.get("block"),
            "parent": entry.get("parent"), "client": entry.get("client"),
            "title": entry["title"], "brand": brand,
            "ranges": ranges, "start": ranges[0][0], "end": ranges[-1][1],
            "duration": duration, "splices": len(ranges) - 1,
            "hook_line": " ".join(text[0].split()[:14]),
            "transcript": " ".join(text),
            "scores": {"hook": entry["hook"], "delivery": entry["delivery"], "total": score},
            "priority": prio, "cta": entry.get("cta"),
            "uses": placement(kind, brand, entry.get("block"), duration),
            "notes": entry.get("notes", ""),
        })

    for ad in edl.ADS:
        add(ad, "ad", "session", f"ad-{ad['n']:02d}-{ad['code'].lower()}")
    for chapter in edl.CHAPTERS:
        add(chapter, "chapter", chapter["source"], chapter["id"])
    for episode in edl.EPISODES:
        add(episode, "episode", episode["source"], episode["id"])
    for raw in edl.RAW:
        add(raw, "raw", raw["source"], raw["id"])

    json.dump(clips, open(DATA / "clips.json", "w"), ensure_ascii=False, indent=1)
    write_catalog(clips)
    print(f"{len(clips)} klipów → data/clips.json, data/catalog.md")


def write_catalog(clips):
    lines = ["# Katalog klipów — sesja 8.10.2026", "",
             "Generowany przez `tools/build_clips.py` z `tools/edl.py`. Nie edytuj ręcznie.", "",
             "Ranking: `hook × 2 + delivery` (max 15). A ≥ 13, B ≥ 11. Oceny redakcyjne — "
             "do zweryfikowania predyktorem przed wydaniem budżetu.", ""]

    def table(title, rows, columns):
        lines.extend([f"## {title}", "", "| " + " | ".join(c[0] for c in columns) + " |",
                      "|" + "---|" * len(columns)])
        for c in rows:
            lines.append("| " + " | ".join(str(f(c)) for _, f in columns) + " |")
        lines.append("")

    ranked = lambda kind: sorted((c for c in clips if c["kind"] == kind),
                                 key=lambda c: (-c["scores"]["total"], c["duration"]))
    base = [("#", lambda c: c["priority"]), ("pkt", lambda c: c["scores"]["total"]),
            ("id", lambda c: f"`{c['id']}`"), ("tytuł", lambda c: c["title"]),
            ("s", lambda c: round(c["duration"])),
            ("hook (pierwsze słowa)", lambda c: c["hook_line"])]
    table("Reklamy i rolki z promptera — ranking", ranked("ad"),
          base[:4] + [("marka", lambda c: c["brand"]), base[4], ("cta", lambda c: c["cta"]),
                      ("sklejki", lambda c: c["splices"]),
                      ("gdzie", lambda c: ", ".join(c["uses"])), base[5]])
    aislupsk = [c for c in ranked("ad") + ranked("chapter") + ranked("raw") if c["brand"] == "aislupsk"]
    table("Kampania AI Słupsk (listopad) — materiał", aislupsk, base[:5])
    table("Rozdziały case study — kandydaci na rolki", ranked("chapter"),
          base[:4] + [("odcinek", lambda c: c["parent"]), base[4], base[5]])
    table("Pełne odcinki (YouTube 16:9)", ranked("episode"),
          [("id", lambda c: f"`{c['id']}`"), ("klient (wewn.)", lambda c: c["client"]),
           ("tytuł", lambda c: c["title"]), ("min", lambda c: round(c["duration"] / 60, 1)),
           ("o czym", lambda c: c["notes"])])
    table("Uwagi do poszczególnych klipów", [c for c in clips if c["notes"]],
          [("id", lambda c: f"`{c['id']}`"), ("uwaga", lambda c: c["notes"])])
    (DATA / "catalog.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
