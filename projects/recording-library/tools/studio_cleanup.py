#!/usr/bin/env python3
"""Sprzątanie wspólnego folderu Studia na polecenie Mateusza („posprzątaj”).

21.11 (MK): „Studio czyta z jednego miejsca, my tworzymy nowe wersje, w Studiu zaznaczam, co do usunięcia”.
Do usunięcia = sekcja „odrzucone” w Studiu (decyzje w <Studio>/data/videos/<klucz>.json).

Co robi:
  - filmy w sekcji „odrzucone”: usuwa plik, miniaturę i archiwalne wersje ze wspólnego folderu
    i dopisuje film do `exports/removed.json` — export_studio.py już go nie publikuje (nie wróci przy renderze),
  - archiwum wersji pozostałych filmów: zostawia KEEP najnowszych, starsze usuwa.

Domyślnie tylko pokazuje, co by usunął. Usuwa dopiero z `--tak`. Pliki w repo/worktree (final/samples, build/)
nie są ruszane — tylko wspólny folder.

  python3 tools/studio_cleanup.py            # podgląd
  python3 tools/studio_cleanup.py --tak      # usuń
  KEEP=3 python3 tools/studio_cleanup.py --tak
"""
import json
import os
import sys
from pathlib import Path

import export_studio as E

STUDIO_DECISIONS = Path(os.path.expanduser(os.environ.get("STUDIO_DECISIONS", "~/Repo/flowbiz-ads-studio-cmo/data/videos")))
SOURCE_ID = "video-mentions"
KEEP = int(os.environ.get("KEEP", "2"))
REMOVED = E.OUT / "exports" / "removed.json"


def size(paths):
    return sum(p.stat().st_size for p in paths if p.exists()) / 1e6


def main(apply):
    manifest = json.load(open(E.MANIFEST))
    removed = json.load(open(REMOVED)) if REMOVED.exists() else []
    to_delete, rejected = [], []
    for video in manifest["videos"]:
        decision = STUDIO_DECISIONS / f"{SOURCE_ID}--{manifest['project']}--{video['id']}.json"
        section = json.load(open(decision)).get("section") if decision.exists() else None
        stem = Path(video["file"]).stem
        versions = sorted((E.VERSIONS / stem).glob("*"), reverse=True) if (E.VERSIONS / stem).exists() else []
        if section == "odrzucone":
            rejected.append(video["id"])
            to_delete += [E.OUT / video["file"], E.OUT / video.get("thumb", "")] + versions
        else:
            to_delete += versions[KEEP:]
    to_delete = [p for p in to_delete if p.exists() and p.is_file()]
    print(f"odrzucone w Studiu: {len(rejected)} → {', '.join(rejected) or '—'}")
    print(f"plików do usunięcia: {len(to_delete)} ({size(to_delete):.0f} MB), archiwum: zostaje {KEEP} najnowszych wersji")
    if not apply:
        print("podgląd — nic nie usunięto; usuń: python3 tools/studio_cleanup.py --tak")
        return
    for p in to_delete:
        p.unlink()
    E.write_json(REMOVED, sorted(set(removed) | set(rejected)))
    E.main()   # spis bez usuniętych
    print(f"usunięto {len(to_delete)} plików; wykluczone z publikacji: {len(set(removed) | set(rejected))}")


if __name__ == "__main__":
    main("--tak" in sys.argv)
