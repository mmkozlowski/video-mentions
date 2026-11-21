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
    main_v2(rows, history, ledger, origin, removed)
    write_json(ledger_file, ledger)




# ── v2: jedna karta na film, w niej warianty × formaty × wersje (21.11, MK: „karta danego odcinka,
#    a pod nią wszystkie wersje”; „szybciej, bez zacinania”) — podglądy robione PRZY EKSPORCIE ──────────
import re as _re
from concurrent.futures import ThreadPoolExecutor

MANIFEST_V2 = OUT / "exports" / "studio-manifest-v2.json"
PREVIEWS = OUT / "final" / "previews"
STUDIO_DECISIONS = Path(os.path.expanduser(os.environ.get("STUDIO_DECISIONS", "~/Repo/flowbiz-ads-studio-cmo/data/videos")))
# przemianowane klipy → karta, pod którą mają się pokazać (decyzje Mateusza wisiały na starych id)
CARD_ALIASES = {"ch-doram-6-kody-od-generowania": "ch-doram-6-kody-15-minut"}
FORMAT_LABEL = {"reels": "9:16 rolka", "feed": "4:5 feed", "ad": "9:16 reklama", "ad45": "4:5 reklama",
                "youtube": "16:9", "master1440": "16:9 · 1440p"}
MASTERS = {"ep-doram": "26-11-meble-zamowienia-z-excela", "ep-open-mercato-offers": "19-11-oferta-w-5-minut",
           "ep-rezon": "03-12-pamiatki-b2b", "ep-8-wdrozen": "10-12-8-wdrozen"}
MASTER_DIR = Path.home() / "tailnet-pliki" / "odcinki-2026-11-21"
FILE_RE = _re.compile(r"^(?P<variant>.+?)__(?P<fmt>[a-z0-9]+)-F(?P<pub>--with-dubs|--with-inserts)?\.mp4$")


def rejected_ids(project=None):
    """Id filmów/wariantów oznaczonych w Studiu jako „odrzucone” (montaż i eksport je pomijają)."""
    project = project or PROJECT.name
    out = set()
    for f in STUDIO_DECISIONS.glob(f"video-mentions--{project}--*.json"):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        vid = f.stem.split(f"--{project}--", 1)[1]
        if d.get("section") == "odrzucone":
            out.add(vid)
        for variant, mark in (d.get("variants") or {}).items():
            if (mark or {}).get("mark") == "odrzucony":
                out.add(variant)
    return out


def build_preview(src, dst):
    """Lekki podgląd do przeglądarki: krótszy bok 720 px, ~2 Mb/s, faststart — Studio go tylko podaje."""
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".tmp.mp4")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(src),
                    "-vf", "scale='if(gt(iw,ih),-2,720)':'if(gt(iw,ih),720,-2)'", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "28", "-maxrate", "2500k", "-bufsize", "5000k", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(tmp)], check=True)
    os.replace(tmp, dst)
    return True


def main_v2(rows, history, ledger, origin, removed):
    rejected = rejected_ids() | removed
    by_variant = {}
    for f in sorted((FINAL / "samples").glob("*.mp4")):
        m = FILE_RE.match(f.name)
        if m:
            by_variant.setdefault(m["variant"], {}).setdefault(m["fmt"], []).append((bool(m["pub"]), f))
    cards, jobs = {}, []
    for row in sorted(rows, key=lambda r: (r["seriesName"], KIND_ORDER.index(r["kind"]), r["id"])):
        vid = row["id"]
        if vid.startswith(("ins-", "gag-")) or vid in rejected or vid not in by_variant:
            continue
        card_id = CARD_ALIASES.get(vid, vid.split("--")[0])
        card = cards.setdefault(card_id, {"id": card_id, "title": row["title"], "group": row["seriesName"],
                                          "kind": row["kind"], "brand": row["brand"], "variants": []})
        formats = []
        for fmt, files in sorted(by_variant[vid].items()):
            pub = [f for p, f in files if p]
            src = (pub or [f for p, f in files])[0]   # wersja do publikacji (z dogrywkami / wstawkami) ma pierwszeństwo
            entry = publish(src, origin)
            if entry:
                ledger.setdefault(src.stem, []).insert(0, entry)
            preview = PREVIEWS / f"{src.stem}.mp4"
            jobs.append((SAMPLES / src.name, preview))
            thumb = THUMBS / f"{src.stem}.jpg"
            thumbnail(SAMPLES / src.name, row, thumb)
            formats.append({"format": fmt, "label": FORMAT_LABEL.get(fmt, fmt), "file": f"final/samples/{src.name}",
                            "preview": f"final/previews/{src.stem}.mp4", "thumb": f"final/thumbs/{src.stem}.jpg",
                            "duration": row["duration"], "versions": ledger.get(src.stem, [])})
        if vid in MASTERS and (MASTER_DIR / f"{MASTERS[vid]}-1440p.mp4").exists():
            master = MASTER_DIR / f"{MASTERS[vid]}-1440p.mp4"
            entry = publish(master, origin)
            if entry:
                ledger.setdefault(master.stem, []).insert(0, entry)
            formats.append({"format": "master1440", "label": FORMAT_LABEL["master1440"], "file": f"final/samples/{master.name}",
                            "preview": formats[0]["preview"] if formats else None, "duration": row["duration"],
                            "versions": ledger.get(master.stem, [])})
        label = "bazowy" if vid == card_id else vid.replace(card_id + "--", "").replace("-", " ")
        card["variants"].append({"id": vid, "label": label, "hook": row["hook_text"], "score": row["score"],
                                 "history": history.get(vid) or [], "formats": formats})
    with ThreadPoolExecutor(max_workers=4) as pool:
        built = sum(pool.map(lambda j: build_preview(*j), jobs))
    for card in cards.values():   # wariant główny: bazowy, a jeśli go nie ma — pierwszy
        base = next((v for v in card["variants"] if v["id"] == card["id"]), card["variants"][0])
        card["primary"] = {"variant": base["id"], "format": base["formats"][0]["format"] if base["formats"] else None}
    now = datetime.datetime.now().isoformat(timespec="seconds")
    write_json(MANIFEST_V2, {"version": 2, "project": PROJECT.name, "name": "Rolki i odcinki YouTube", "generatedAt": now,
                             "root": "..", "source": origin, "cards": list(cards.values())})
    print(f"v2: {len(cards)} kart, {sum(len(c['variants']) for c in cards.values())} wariantów, "
          f"{len(jobs)} plików, {built} nowych podglądów, pominięte odrzucone: {len(rejected)}")


if __name__ == "__main__":
    main()
