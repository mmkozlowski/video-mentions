#!/usr/bin/env python3
"""Kontrola wyciętych klipów: transkrypcja GOTOWEGO pliku kontra oczekiwany tekst.

Skład ocenia się wypisem słów, nie odsłuchem (.ai/memory/shorty-z-telefonu-pulapki).
Dla każdego klipu sprawdza:
  - długość audio = długość wideo (±0,1 s),
  - pokrycie słów: ile słów z clips.json słychać w gotowym pliku,
  - powtórzone n-gramy (ślad niewyciętego dubla),
  - zbyt długą ciszę na sklejce.
Wynik → data/verify.json + wypis odchyleń. Długie (episode) pomija bez --all.

  python3 tools/verify.py            # klipy bez wyniku kontroli
  python3 tools/verify.py --all      # także pełne odcinki
  python3 tools/verify.py ad-02      # wskazane
"""
import json
import re
import subprocess
import sys
from collections import Counter

from sources import DATA, LIBRARY, WORK


def tokens(text):
    return re.findall(r"\w+", text.lower())


def duration(path, stream):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries",
                          "stream=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def transcribe(path):
    wav = WORK / "verify.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar",
                    "16000", str(wav)], check=True)
    subprocess.run(["mlx_whisper", str(wav), "--model", "mlx-community/whisper-large-v3-turbo",
                    "--language", "pl", "--condition-on-previous-text", "False",
                    "--output-format", "txt", "--output-dir", str(WORK), "--output-name", "verify"],
                   check=True, capture_output=True)
    return (WORK / "verify.txt").read_text()


def repeated_trigrams(words):
    grams = Counter(tuple(words[i:i + 3]) for i in range(len(words) - 2))
    return [" ".join(g) for g, n in grams.items() if n > 1 and len(set(g)) == 3]


def main(argv):
    everything = "--all" in argv
    wanted = [a for a in argv if not a.startswith("--")]
    results_file = DATA / "verify.json"
    results = json.load(open(results_file)) if results_file.exists() else {}
    for clip in json.load(open(DATA / "clips.json")):
        if wanted and not any(clip["id"].startswith(w) for w in wanted):
            continue
        if not wanted and (clip["id"] in results or (clip["kind"] == "episode" and not everything)):
            continue
        master = LIBRARY / clip["id"] / "master.mp4"
        if not master.exists():
            continue
        heard = transcribe(master)
        expected, got = tokens(clip["transcript"]), tokens(heard)
        coverage = sum((Counter(expected) & Counter(got)).values()) / max(1, len(expected))
        drift = abs(duration(master, "a:0") - duration(master, "v:0"))
        repeats = [g for g in repeated_trigrams(got) if g not in repeated_trigrams(expected)]
        verdict = "ok" if coverage >= 0.9 and drift <= 0.1 and not repeats else "check"
        results[clip["id"]] = {"verdict": verdict, "coverage": round(coverage, 3),
                               "av_drift": round(drift, 3), "new_repeats": repeats, "heard": heard}
        print(f"{verdict:5} {clip['id']:<40} pokrycie {coverage:5.1%}  a/v {drift:.2f}s"
              + (f"  powtórki: {repeats}" if repeats else ""), flush=True)
        json.dump(results, open(results_file, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
