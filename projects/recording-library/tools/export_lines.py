#!/usr/bin/env python3
"""Baza kwestii z dogrywek → wspólny folder Studia (21.11, MK: „zbudować z tych moich tekstów bazę, może być w Studio”).

Źródło: raw/2026-11-16-dogrywki-audio/kwestie/mapa.json (dubs_split.py) + edl.py (które wstawki używają kwestii)
+ assemble_episode.PLAN (w których odcinkach są te wstawki).
Wynik: <SHARED>/projects/recording-library/exports/lines.json + lines/<nr>.m4a (AAC 128k, kopiowane tylko gdy nowsze).

  python3 tools/export_lines.py
"""
import datetime
import json
import re
import subprocess
from pathlib import Path

import export_studio as E
from dubs_split import OUT as KWESTIE
from edl import RAW as EDL

LINES_DIR = E.OUT / "lines"
LINES_JSON = E.OUT / "exports" / "lines.json"


def section(nr):
    m = re.match(r"(\d+)", nr)
    n = int(m.group(1)) if m else None
    if nr.startswith("M"):
        return "moduły i branże"
    if nr.startswith("F"):
        return "ból abonamentu (SaaS)"
    if n is None:
        return "inne"
    if n <= 5:
        return "łączniki"
    if n <= 12:
        return "łączniki case'ów"
    if n <= 15:
        return "wstęp (stary)"
    if n <= 21:
        return "przejścia"
    if n in (27, 28, 29, 30, 26):
        return "haki rolek"
    if n in (31, 32, 33, 34, 35):
        return "zakończenia rolek"
    if n <= 43:
        return "zakończenia i typowe YouTube"
    if re.match(r"47[a-e]$", nr):
        return "powroty do tematu"
    if n <= 47:
        return "przedstawienie"
    if n <= 62:
        return "Open Mercato"
    if n <= 99:
        return "reklamy"
    return "inne"


def usage():
    """kwestia (oś dogrywek) → wstawki z edl, które biorą jej fragment; wstawka → odcinki z PLAN."""
    from assemble_episode import PLAN
    episodes = {}
    for episode, plan in PLAN.items():
        for _, insert in plan:
            episodes.setdefault(insert, []).append(episode)
    inserts = [(c["id"], [(r[0], r[1]) for r in c["ranges"]]) for c in EDL if c.get("source") == "dubs"]
    return inserts, episodes


def main():
    rows = json.load(open(KWESTIE / "mapa.json"))
    inserts, episodes = usage()
    LINES_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    for r in rows:
        nr = r["nr"]
        entry = {"nr": nr, "section": section(nr), "text": r["oczekiwany"], "heard": r["transkrypt"],
                 "match": r["zgodnosc"], "note": r["uwagi"], "audio": None, "duration": None, "usedIn": [], "episodes": []}
        if r["plik"]:
            s, e = float(r["start"]), float(r["koniec"])
            entry["duration"] = round(e - s, 2) if "sklejka" not in r["uwagi"] else None
            used = [iid for iid, ranges in inserts if any(a < e - 0.2 and b > s + 0.2 for a, b in ranges)]
            entry["usedIn"] = used
            entry["episodes"] = sorted({ep for iid in used for ep in episodes.get(iid, [])})
            src = KWESTIE.parent / r["plik"]
            dst = LINES_DIR / f"{nr}.m4a"
            if src.exists() and (not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime):
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", "loudnorm=I=-16:TP=-1.5:linear=true",
                                "-c:a", "aac", "-b:a", "128k", str(dst)], check=True)
            if dst.exists():
                entry["audio"] = f"lines/{dst.name}"
                if entry["duration"] is None:
                    entry["duration"] = round(float(subprocess.run(
                        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(dst)],
                        capture_output=True, text=True).stdout or 0), 2)
        out.append(entry)
    E.write_json(LINES_JSON, {"version": 1, "project": E.PROJECT.name, "name": "Baza kwestii (dogrywki)",
                              "generatedAt": datetime.datetime.now().isoformat(timespec="seconds"), "root": "..",
                              "lines": out})
    print(f"baza kwestii: {sum(1 for x in out if x['audio'])} nagranych z {len(out)} → {LINES_JSON}")
    return LINES_JSON


if __name__ == "__main__":
    main()
