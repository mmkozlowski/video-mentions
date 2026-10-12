#!/usr/bin/env python3
"""Wynik Higgsfield Virality Predictor (strona HTML z wyniku joba) → data/predictor.json.

  python3 tools/predictor_fetch.py <id-filmu> <result_url>
"""
import json
import re
import sys
import urllib.request

from sources import DATA

FILE = DATA / "predictor.json"


def fetch(url):
    page = urllib.request.urlopen(url, timeout=60).read().decode("utf-8", "replace")
    m = re.search(r'"scores":(\{[^}]*\})', page)
    if not m:
        raise SystemExit("brak bloku scores w wyniku")
    return json.loads(m.group(1))


if __name__ == "__main__":
    video, url = sys.argv[1], sys.argv[2]
    data = json.load(open(FILE)) if FILE.exists() else {}
    data[video] = dict(fetch(url), source="Higgsfield Virality Predictor, pierwsze 15 s")
    json.dump(data, open(FILE, "w"), ensure_ascii=False, indent=1)
    print(video, {k: data[video][k] for k in ("overall_score", "hook_score", "brain_engagement", "viral_potential", "sustain")})
