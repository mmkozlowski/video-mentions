#!/usr/bin/env python3
"""Karta ocen wszystkich filmów — do planszy decyzji (co publikujemy, co testujemy, co poprawiamy).

Mateusz 12.10: „dodaj do wszystkich nagrań współczynniki konwersji hooku etc., żebym ocenił,
który siądzie, a który nie”. Prawdziwej konwersji jeszcze nie ma (nic nie jest opublikowane),
więc karta zbiera PREDYKTORY, każdy z jawnym źródłem:

  hook_ed, delivery_ed  ocena redakcyjna 1–5 (tools/edl.py)
  first_word_s          po ilu sekundach pada pierwsze słowo (dłużej niż 0,5 s = ucieczka)
  words_3s              ile słów słychać w pierwszych 3 s (hook bez słów = sama grafika)
  syl_s                 tempo mowy (sylaby na sekundę mowy)
  events_per_min        ile wstawek na minutę (dynamika obrazu)
  length_fit            czy długość pasuje do formatu (rolka 20–50 s, reklama ≤ 40 s, zajawka 60–100 s)
  cta                   czy jest jasne wezwanie (komentarz / przycisk / link)
  predictor             Higgsfield Virality Predictor na pierwszych 15 s (gdy policzony) — model
                        aktywności mózgu widza; liczby względne, nie gwarancja

score (0–100) = ważona suma składników — przepis w WEIGHTS, żeby było widać, skąd liczba.

  python3 tools/scorecard.py          # → data/scorecard.json
"""
import json
import re
from pathlib import Path

from package import FINAL, PACK, output_name
from sources import DATA, LIBRARY, load_clips

PREDICTOR = DATA / "predictor.json"     # wyniki Higgsfield Virality Predictor (dopisywane ręcznie/skryptem)
WEIGHTS = {"hook": 30, "delivery": 10, "opening": 15, "specific": 10, "length": 10, "dynamics": 10, "cta": 15}
VOWELS = "aąeęioóuy"


def syllables(word):
    word = re.sub(r"i(?=[aąeęoóuy])", "", word.lower())   # „i” przed samogłoską tylko zmiękcza
    return len(re.findall(f"[{VOWELS}]+", word))


def tempo(words):
    talk, syl = 0.0, 0
    for a, b in zip(words, words[1:] + [None]):
        talk += (min(a["end"], b["start"]) if b and b["start"] - a["end"] < 0.25 else a["end"]) - a["start"]
        syl += syllables(a["word"])
    return syl / talk if talk else 0


def kind_of(clip, board, fmt):
    if fmt == "feed":
        return "zajawka"
    if fmt == "youtube":
        return "odcinek"
    return "reklama" if board.get("variant") or fmt == "ad" else "rolka"


def length_score(kind, seconds):
    ideal = {"rolka": (20, 50), "reklama": (15, 40), "zajawka": (60, 100), "odcinek": (300, 1200)}[kind]
    lo, hi = ideal
    if lo <= seconds <= hi:
        return 1.0
    off = (lo - seconds) / lo if seconds < lo else (seconds - hi) / hi
    return max(0.0, 1 - off * 2)


def main():
    clips = {c["id"]: c for c in load_clips()}
    predictor = json.load(open(PREDICTOR)) if PREDICTOR.exists() else {}
    rows = []
    for path in sorted(PACK.glob("storyboards/*.json")):
        board = json.load(open(path))
        clip = clips[board["clip"]]
        name = output_name(clip, board)
        fmts = board.get("formats", ["reels", "ad", "youtube"])
        fmt = "ad" if board.get("variant") and "ad" in fmts else fmts[0]
        if not list(FINAL.glob(f"{name}__{fmt}-*.mp4")):
            continue
        words = json.load(open(LIBRARY / clip["id"] / "words.json"))
        kind = kind_of(clip, board, fmt)
        cover = board.get("cover", {}).get("dur", 2.2) if board.get("cover") and board["cover"].get("style") != "callout" else 0
        first = words[0]["start"] if words else 0
        events = len(board.get("events", []))
        epm = events / (clip["duration"] / 60)
        cta = board.get("cta", {})
        has_cta = bool(cta.get("reels") or cta.get("ad")) or kind in ("zajawka", "odcinek")
        scores = clip.get("scores", {})
        hook_ed = scores.get("hook") or (4 if kind in ("zajawka", "odcinek") else 3)
        delivery_ed = scores.get("delivery") or 3
        if board.get("variant") and board.get("cover", {}).get("style") == "callout":
            hook_ed = min(5, hook_ed + 0.5)    # hasło na start: test A/B, z założenia mocniejsze otwarcie
        # otwarcie: słowa w pierwszych 3 s (7+ = pełny hook głosem) minus spóźnione pierwsze słowo
        opening = min(1.0, sum(1 for w in words if w["start"] < 3.0) / 7) * (1.0 if first <= 0.5 else max(0.0, 1 - (first - 0.5) / 1.5))
        hook_text = board.get("hook", {}).get("text", "") + " " + board.get("cover", {}).get("text", "")
        # konkret w hooku (.ai/memory/copy-i-hook: ból + liczba biją opis): cyfra albo procent/godziny/minuty
        specific = 1.0 if re.search(r"\d", hook_text) else 0.5 if re.search(r"(?i)godzin|minut|dni|tysi|setk", hook_text) else 0.0
        parts = {
            "hook": (hook_ed - 1) / 4,
            "delivery": (delivery_ed - 1) / 4,
            "opening": opening,
            "length": length_score(kind, clip["duration"]),
            "specific": specific,
            "dynamics": min(1.0, epm / 8),
            "cta": 1.0 if has_cta else 0.0,
        }
        score = round(sum(WEIGHTS[k] * v for k, v in parts.items()))
        p = predictor.get(name)
        rows.append({
            "id": name, "clip": clip["id"], "title": clip["title"], "kind": kind, "format": fmt,
            "brand": board.get("brand", clip["brand"]), "duration": round(clip["duration"], 1),
            "series": clip.get("parent") or clip.get("block") or clip["source"],
            "hook_text": board.get("hook", {}).get("text", "").replace("*", ""),
            "cover_text": board.get("cover", {}).get("text", "").replace("*", ""),
            "cta_text": (cta.get("reels") or cta.get("ad") or {}).get("title", "").replace("*", ""),
            "hook_ed": hook_ed, "delivery_ed": delivery_ed,
            "first_word_s": round(first, 2), "cover_s": cover,
            "words_3s": sum(1 for w in words if w["start"] < 3.0),
            "syl_s": round(tempo(words), 2), "events": events, "events_per_min": round(epm, 1),
            "parts": {k: round(v, 2) for k, v in parts.items()}, "score": score,
            "predictor": p,
            "file": f"{name}__{fmt}-{'S' if board.get('brand', clip['brand']) == 'aislupsk' else 'A'}.mp4",
        })
    ranked = sorted(rows, key=lambda r: -r["score"])
    for i, r in enumerate(ranked):
        r["rank"] = i + 1
        r["grade"] = "A" if i < len(ranked) / 3 else "B" if i < 2 * len(ranked) / 3 else "C"
    json.dump({"weights": WEIGHTS, "rows": rows}, open(DATA / "scorecard.json", "w"), ensure_ascii=False, indent=1)
    rows.sort(key=lambda r: -r["score"])
    for r in rows[:10]:
        print(f"{r['score']:3d}  {r['kind']:<8} {r['id']}")
    print(f"… {len(rows)} filmów → data/scorecard.json")


if __name__ == "__main__":
    main()
