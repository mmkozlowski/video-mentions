#!/usr/bin/env python3
"""Generowanie lektora do spotów — jeden plik audio na spot.

NIGDY nie generuj fraz osobnymi wywołaniami. Każde wywołanie to niezależny
sampling: barwa i akcent dryfują, a w odsłuchu słychać dwie różne osoby.
Cały tekst idzie jednym strzałem, a granice fraz wykrywa potem `silencedetect`
w `story.py`.

Skrypt nie woła API sam — wypisuje gotowe wywołania i sprawdza, czy pobrane
pliki zgadzają się ze scenariuszami. Generacja idzie przez MCP Higgsfielda
(`generate_audio`, model `text2speech_v2`, wariant `elevenlabs`), bo tam siedzi
rozliczanie kredytów.

Użycie:
    python3 voice.py            # pokaż teksty i stan plików
    python3 voice.py --check    # sprawdź zgodność liczby fraz ze scenariuszem
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import story  # noqa: E402

# Harrison — wybrany po pomiarze ekspresji (voice_test.py). Zmiana głosu zmienia
# pauzowanie, więc po niej trzeba przejrzeć wszystkie scenariusze na nowo.
VOICE_ID = "573e5163-59b3-4926-aab1-951ef2985f81"
MODEL, VARIANT = "text2speech_v2", "elevenlabs"


def status():
    print(f"Głos: Harrison {VOICE_ID}  ({MODEL} / {VARIANT})\n")
    for key, txt in story.VO_TEXT.items():
        path = os.path.join(story.VOICE, f"vo-{key}.mp3")
        mark = "✓" if os.path.exists(path) else "BRAK"
        print(f"── {key}  [{mark}]  {len(story.STORIES[key]['script'])} fraz w scenariuszu")
        print(f"   {txt}\n")


def check():
    ok = True
    for key in story.VO_TEXT:
        path = os.path.join(story.VOICE, f"vo-{key}.mp3")
        if not os.path.exists(path):
            print(f"⚠️  {key}: brak {path}")
            ok = False
            continue
        want = len(story.STORIES[key]["script"])
        got = len(story.detect_phrases(path, want))
        flag = "OK " if want == got else "ROZJAZD"
        if want != got:
            ok = False
        print(f"{flag} {key:8} scenariusz {want:2}  lektor {got:2}")
    if not ok:
        print("\nPrzy rozjeździe: dopasuj listę `script` w STORIES do frazowania "
              "lektora (taniej niż regeneracja) albo przepisz tekst tak, żeby "
              "pauzy wypadły tam, gdzie mają.")
    return ok


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    status()
