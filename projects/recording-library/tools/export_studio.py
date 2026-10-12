#!/usr/bin/env python3
"""Spis filmów dla panelu FlowBiz Studio (~/Repo/flowbiz-ads-studio, zakładka „Filmy”).

Mateusz 12.10: panel ma czytać filmy z tego repo, bez kopiowania plików. Kontrakt ma dwa
poziomy, oba w formacie `version: 1`:

  studio-index.json (katalog główny repo)       mapa: projekty, ich serie i formaty, ścieżka do spisu
  projects/<p>/exports/studio-manifest.json     filmy projektu: plik, miniatura, ocena, hook, historia

Ścieżki w spisie są względne wobec katalogu projektu (`root`), studio podaje wyłącznie pliki
wymienione w spisie. Decyzje i uwagi zapisuje studio u siebie (data/videos/) — to repo ich nie
dotyka. Oba pliki są odtwarzalne i lokalne (poza gitem), jak final/samples, z którego czytają.

  python3 tools/export_studio.py      # po renderze albo scorecard.py
"""
import datetime
import json
import subprocess

from sources import DATA, PROJECT

REPO = PROJECT.parent.parent
FINAL = PROJECT / "final"
THUMBS = FINAL / "thumbs"
MANIFEST = PROJECT / "exports" / "studio-manifest.json"
INDEX = REPO / "studio-index.json"
VERSION = 1
KIND_ORDER = ["rolka", "reklama", "zajawka", "odcinek"]


def thumbnail(video, row, target):
    """Klatka po hooku (tam widać już układ z panelem), nie czarny pierwszy kadr."""
    if target.exists() and target.stat().st_mtime >= video.stat().st_mtime:
        return
    at = min(row["duration"] * 0.4, 6.0)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.2f}", "-i", str(video), "-frames:v", "1",
                    "-vf", "scale=-2:360", "-q:v", "5", str(target)], check=True, stdin=subprocess.DEVNULL)


def video_entry(row, history):
    return {
        "id": row["id"],
        "title": row["title"],
        "group": row["seriesName"],
        "kind": row["kind"],
        "format": row["format"],
        "brand": row["brand"],
        "duration": row["duration"],
        "file": f"final/samples/{row['file']}",
        "thumb": f"final/thumbs/{row['id']}.jpg",
        "hook": row["hook_text"],
        "cover": row["cover_text"],
        "cta": row["cta_text"],
        "score": row["score"],
        "grade": row["grade"],
        "rank": row["rank"],
        "scoreParts": row["parts"],
        "signals": {"firstWordSeconds": row["first_word_s"], "wordsIn3s": row["words_3s"],
                    "syllablesPerSecond": row["syl_s"], "eventsPerMinute": row["events_per_min"]},
        "predictor": row.get("predictor"),
        "history": history.get(row["id"]) or history.get(row["clip"]) or [],
    }


def main():
    rows = json.load(open(DATA / "scorecard.json"))["rows"]
    history = json.load(open(DATA / "video-history.json")) if (DATA / "video-history.json").exists() else {}
    THUMBS.mkdir(parents=True, exist_ok=True)
    videos = []
    for row in sorted(rows, key=lambda r: (r["seriesName"], KIND_ORDER.index(r["kind"]), r["id"])):
        video = FINAL / "samples" / row["file"]
        if not video.exists():
            print(f"  brak pliku: {row['file']}")
            continue
        thumbnail(video, row, THUMBS / f"{row['id']}.jpg")
        videos.append(video_entry(row, history))
    now = datetime.datetime.now().isoformat(timespec="seconds")
    MANIFEST.parent.mkdir(exist_ok=True)
    json.dump({"version": VERSION, "project": PROJECT.name, "name": "Rolki i odcinki YouTube", "generatedAt": now,
               "root": "..", "videos": videos}, open(MANIFEST, "w"), ensure_ascii=False, indent=1)
    groups = list(dict.fromkeys(v["group"] for v in videos))
    project = {"id": PROJECT.name, "name": "Rolki i odcinki YouTube",
               "description": "Klipy z sesji nagraniowych i starszych odcinków kanału: rolki, reklamy, zajawki, odcinki 16:9",
               "groups": groups, "formats": [k for k in KIND_ORDER if any(v["kind"] == k for v in videos)],
               "manifest": str(MANIFEST.relative_to(REPO)), "updated": now, "videos": len(videos)}
    index = json.load(open(INDEX)) if INDEX.exists() else {"version": VERSION, "repo": "video-mentions", "projects": []}
    index["projects"] = [p for p in index["projects"] if p["id"] != project["id"]] + [project]
    index["generatedAt"] = now
    json.dump(index, open(INDEX, "w"), ensure_ascii=False, indent=1)
    print(f"{len(videos)} filmów w {len(groups)} seriach → {MANIFEST.relative_to(REPO)}, {INDEX.name}")


if __name__ == "__main__":
    main()
