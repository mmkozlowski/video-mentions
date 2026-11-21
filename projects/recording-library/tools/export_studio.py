#!/usr/bin/env python3
"""Spis filmów dla panelu FlowBiz Studio (~/Repo/flowbiz-ads-studio, zakładka „Filmy”).

Mateusz 12.10: panel ma czytać filmy z tego repo, bez kopiowania plików. Kontrakt ma dwa
poziomy, oba w formacie `version: 1`:

  studio-index.json (katalog główny repo)       mapa: projekty, ich serie i formaty, ścieżka do spisu
  projects/<p>/exports/studio-manifest.json     filmy projektu: plik, miniatura, ocena, hook, historia

Ścieżki w spisie są względne wobec katalogu projektu (`root`), studio podaje wyłącznie pliki
wymienione w spisie. Od 21.11 wszystko leży we WSPÓLNYM folderze (`STUDIO_SHARED`, domyślnie ~/Media/flowbiz-wideo),
nie w repo: każdy worktree/gałąź publikuje tam swoje rendery, poprzednia wersja pliku idzie do `versions/`. Decyzje i uwagi zapisuje studio u siebie (data/videos/) — to repo ich nie
dotyka. Oba pliki są odtwarzalne i lokalne (poza gitem), jak final/samples, z którego czytają.

  python3 tools/export_studio.py      # po renderze albo scorecard.py
"""
import datetime
import json
import os
import shutil
import subprocess
from pathlib import Path

from assemble_short import PLAN as SHORTS_WITH_DUBS
from sources import DATA, PROJECT

REPO = PROJECT.parent.parent
FINAL = PROJECT / "final"
# 21.11 (MK: „Studio czyta z jednego miejsca, my tworzymy nowe wersje, w Studiu zaznaczam, co do usunięcia”):
# gotowe filmy wychodzą do WSPÓLNEGO folderu poza gitem, niezależnie od gałęzi i worktree. Studio czyta tylko stąd.
SHARED = Path(os.path.expanduser(os.environ.get("STUDIO_SHARED", "~/Media/flowbiz-wideo")))
OUT = SHARED / "projects" / PROJECT.name          # podział na projekty (recording-library, ppwrsmart, …)
THUMBS = OUT / "final" / "thumbs"
SAMPLES = OUT / "final" / "samples"
VERSIONS = OUT / "versions"
MANIFEST = OUT / "exports" / "studio-manifest.json"
INDEX = SHARED / "studio-index.json"


def git_origin():
    """Skąd pochodzi render: gałąź + commit worktree, w którym go zrobiono (do historii wersji w Studiu)."""
    def run(*args):
        return subprocess.run(["git", "-C", str(PROJECT), *args], capture_output=True, text=True).stdout.strip()
    return {"branch": run("rev-parse", "--abbrev-ref", "HEAD"), "commit": run("rev-parse", "--short", "HEAD"),
            "worktree": str(REPO)}


def publish(video, origin):
    """Kopia do wspólnego folderu (APFS clone: bez dodatkowego miejsca). Poprzednia wersja → versions/<film>/."""
    target = SAMPLES / video.name
    if target.exists():
        same = target.stat().st_size == video.stat().st_size and target.stat().st_mtime >= video.stat().st_mtime
        if same:
            return None
        stamp = datetime.datetime.fromtimestamp(target.stat().st_mtime).strftime("%Y%m%d-%H%M")
        archive = VERSIONS / video.stem / f"{stamp}{video.suffix}"
        archive.parent.mkdir(parents=True, exist_ok=True)
        os.replace(target, archive)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp" + target.suffix)
    if subprocess.run(["cp", "-c", "-p", str(video), str(tmp)], capture_output=True).returncode != 0:
        shutil.copy2(video, tmp)
    os.replace(tmp, target)
    return dict(origin, file=video.name, at=datetime.datetime.now().isoformat(timespec="seconds"))


def write_json(path, data):
    """Zapis atomowy — Studio może czytać spis w trakcie eksportu z innego worktree."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    json.dump(data, open(tmp, "w"), ensure_ascii=False, indent=1)
    os.replace(tmp, path)
VERSION = 1
KIND_ORDER = ["rolka", "reklama", "zajawka", "odcinek"]


def thumbnail(video, row, target):
    """Klatka po hooku (tam widać już układ z panelem), nie czarny pierwszy kadr."""
    if target.exists() and target.stat().st_mtime >= video.stat().st_mtime:
        return
    at = min(row["duration"] * 0.4, 6.0)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.2f}", "-i", str(video), "-frames:v", "1",
                    "-vf", "scale=-2:360", "-q:v", "5", str(target)], check=True, stdin=subprocess.DEVNULL)


def video_entry(row, history, versions):
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
        # wersje pliku we wspólnym folderze: bieżąca (gałąź, commit, data) + zarchiwizowane poprzednie
        "versions": versions.get(Path(row["file"]).stem, []),
    }


def main():
    # 21.11: spis filmów z karty ocen — liczona na nowo przy każdym eksporcie (0,1 s), inaczej nowe/przemianowane
    # klipy nie trafiały do Studia (stara „kody-15-minut” zamiast „kody-od-generowania”)
    import contextlib, io, scorecard
    with contextlib.redirect_stdout(io.StringIO()):
        scorecard.main()
    rows = json.load(open(DATA / "scorecard.json"))["rows"]
    history = json.load(open(DATA / "video-history.json")) if (DATA / "video-history.json").exists() else {}
    THUMBS.mkdir(parents=True, exist_ok=True)
    ledger_file = OUT / "exports" / "versions.json"
    ledger = json.load(open(ledger_file)) if ledger_file.exists() else {}
    origin = git_origin()
    removed_file = OUT / "exports" / "removed.json"
    removed = set(json.load(open(removed_file))) if removed_file.exists() else set()   # usunięte w studio_cleanup.py
    published = 0
    videos = []
    for row in sorted(rows, key=lambda r: (r["seriesName"], KIND_ORDER.index(r["kind"]), r["id"])):
        # odcinek sklejony z przerywnikami o usługach (assemble_episode.py) ma pierwszeństwo przed gołym renderem
        with_inserts = row["file"].replace(".mp4", "--with-inserts.mp4")
        if row["kind"] == "odcinek" and (FINAL / "samples" / with_inserts).exists():
            row = dict(row, file=with_inserts)
        # 17.11 (Agata recenzowała shorty bez dogrywek): short z hakiem i zakończeniem z dogrywek
        # (assemble_short.py) jest wersją do publikacji — Studio pokazuje ją zamiast gołego renderu. Tylko shorty
        # z bieżącego planu: stare `--with-dubs` (np. kody-15-minut sprzed przemianowania) zostają na dysku
        with_dubs = row["file"].replace(".mp4", "--with-dubs.mp4")
        if row["id"] in SHORTS_WITH_DUBS and (FINAL / "samples" / with_dubs).exists():
            row = dict(row, file=with_dubs)
        if row["id"] in removed:
            continue
        # wstawki (ins-*) i gagi to klocki do sklejania odcinków/rolek, nie filmy do przeglądu (21.11: zaśmiecały Studio)
        if row["id"].startswith(("ins-", "gag-")):
            continue
        video = FINAL / "samples" / row["file"]
        if not video.exists():
            print(f"  brak pliku: {row['file']}")
            continue
        entry = publish(video, origin)
        if entry:
            published += 1
            ledger.setdefault(video.stem, []).insert(0, entry)
        thumbnail(SAMPLES / video.name, row, THUMBS / f"{row['id']}.jpg")
        videos.append(video_entry(row, history, ledger))
    now = datetime.datetime.now().isoformat(timespec="seconds")
    write_json(ledger_file, ledger)
    write_json(MANIFEST, {"version": VERSION, "project": PROJECT.name, "name": "Rolki i odcinki YouTube", "generatedAt": now,
                          "root": "..", "source": origin, "videos": videos})
    groups = list(dict.fromkeys(v["group"] for v in videos))
    project = {"id": PROJECT.name, "name": "Rolki i odcinki YouTube",
               "description": "Klipy z sesji nagraniowych i starszych odcinków kanału: rolki, reklamy, zajawki, odcinki 16:9",
               "groups": groups, "formats": [k for k in KIND_ORDER if any(v["kind"] == k for v in videos)],
               "manifest": str(MANIFEST.relative_to(SHARED)), "updated": now, "videos": len(videos)}
    index = json.load(open(INDEX)) if INDEX.exists() else {"version": VERSION, "repo": "video-mentions", "projects": []}
    index["projects"] = [p for p in index["projects"] if p["id"] != project["id"]] + [project]
    index["generatedAt"] = now
    write_json(INDEX, index)
    print(f"{len(videos)} filmów w {len(groups)} seriach ({published} nowych wersji) → {INDEX} [{origin['branch']} {origin['commit']}]")


if __name__ == "__main__":
    main()
