"""Źródła biblioteki nagrań — jedyne miejsce, w którym siedzą ścieżki do surówki.

Surówka (7 GB z MacBooka, 1280×720, 30 fps, mono 48 kHz) leży POZA repo,
w Downloads. Wszystko inne liczy się względem katalogu projektu.
"""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / "data"
BUILD = PROJECT / "build"
WORK = BUILD / "work"
TRANSCRIPTS = DATA / "transcripts"   # Whisper large-v3-turbo, czasy słów — podstawa wszystkich cięć
LIBRARY = BUILD / "library"          # wycięte klipy — odtwarzalne z clips.json

RAW_DIR = Path.home() / "Downloads" / "nagrywki pazdziernik 2026"

SOURCES = {
    "session": RAW_DIR / "nagrywki reklamy i pozniej spokojne flow .mov",
    "doram": RAW_DIR / "doram.mov",
    "vacuactiv": RAW_DIR / "vacuactiv.mov",
}

# Kadr źródła: 1280×720, kamera statyczna, twarz w okolicy x≈700–720.
SOURCE_W, SOURCE_H = 1280, 720

# Pion z miejscem na grafikę: górne 1215 px to twarz (crop 640×720 → ×1,6875),
# dolne 705 px to wolny panel na napisy, wstawki i mockupy systemu.
# Pełnoekranowy pion (crop 405×720 → ×2,67) jest za miękki z 720p.
VERTICAL = {
    "w": 1080, "h": 1920,
    "face_crop_w": 640, "face_crop_h": 720,
    "face_h": 1215,
    "panel_color": "0x0A0A08",
}

# Środek kadru twarzy w źródle, per plik i per zakres czasu (sekundy).
# Zmierzone na klatkach kontrolnych; do zastąpienia śledzeniem twarzy.
FACE_CENTER_X = {
    "session": 720,
    "doram": 700,
    "vacuactiv": 720,
}


def load_words(source):
    """Płaska lista słów z transkrypcji Whispera danego źródła."""
    transcript = json.load(open(TRANSCRIPTS / f"{source}.json"))
    return [w for seg in transcript["segments"] for w in seg.get("words", [])]
