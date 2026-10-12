#!/usr/bin/env python3
"""Historia zmian per film — co, kiedy i dlaczego zmieniło się w danym wideo.

Mateusz 12.10: „prowadź też historię tych zmian dla danego video”. Wpis dopisuje się przy
każdej poprawce (uwaga z galerii, kontrola transkrypcją, zmiana stylu), zanim pójdzie render.
Galeria pokazuje historię pod filmem (tools/gallery.py).

  python3 tools/history.py ep-vibecoding "2:00 — drugi dubel „bo dowolna zmiana”" --by Mateusz
  python3 tools/history.py ep-vibecoding                    # wypis historii
"""
import argparse
import datetime
import json

from sources import DATA

FILE = DATA / "video-history.json"


def load():
    return json.load(open(FILE)) if FILE.exists() else {}


def add(video, changes, by="Mateusz", date=None):
    """Jeden wpis = jedna runda zmian (data + kto zgłosił + lista zmian)."""
    history = load()
    history.setdefault(video, []).append({"date": date or datetime.date.today().isoformat(), "by": by, "changes": changes})
    json.dump(history, open(FILE, "w"), ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("changes", nargs="*")
    ap.add_argument("--by", default="Mateusz", help="kto zgłosił: Mateusz | kontrola | Claude")
    a = ap.parse_args()
    if a.changes:
        add(a.video, a.changes, a.by)
    for entry in load().get(a.video, []):
        print(f"{entry['date']} · {entry['by']}")
        for change in entry["changes"]:
            print(f"  - {change}")


if __name__ == "__main__":
    main()
