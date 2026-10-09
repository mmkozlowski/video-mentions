#!/usr/bin/env python3
"""Ikony do hooków: jeden przedmiot 3D na ciemnym tle, bez tekstu.

Hook to nie sam tekst — nad zdaniem stoi ikona albo schemat (A vs B, przepływ),
złożony w package.py z tych ikon i z ORYGINALNYCH logo narzędzi (logos.css).
Logo narzędzi nigdy nie generujemy — model przekręca znaki towarowe.

Tło ikony = tło karty hooka (#0A0A08), a w karcie obraz ma mix-blend-mode:lighten,
więc kwadrat znika i zostaje sam przedmiot.

  python3 tools/hook_art.py            # brakujące
  python3 tools/hook_art.py h-notebook # wybrane, nadpisuje

Wynik: assets/hook-art/<id>.png (w gicie, jak b-rolle). Koszty: data/broll-ledger.json.
"""
import base64
import sys

from broll_gen import API, COST, IMAGE_MODEL, call, ledger
from sources import PROJECT

ART = PROJECT / "assets" / "hook-art"

STYLE = ("a single glossy 3D icon, soft clay render, centered, filling about 70% of the frame, "
         "isolated on a perfectly flat solid near-black background (#0A0A08) with no gradient, no floor, no shadow plane, "
         "warm amber (#F5A623) rim light and accents, the rest in neutral off-white and graphite, "
         "absolutely no text, no letters, no numbers, no logos, square 1:1")

ICONS = {
    "h-skyscraper": "one single tall corporate skyscraper tower, same clay material as the rest, no second building",
    "h-pin": "a map location pin standing on a small cozy town with a lighthouse by the sea",
    "h-paper-stack": "a tall messy stack of printed paper order sheets with a paperclip",
    "h-notebook": "an old worn handwritten notebook, open, with a pencil lying on it",
    "h-dashboard": "a computer monitor showing an abstract business dashboard with bar charts, everything green and tidy",
    "h-factory": "a small factory hall building with a sawtooth roof and a chimney",
    "h-plane": "a passenger airplane taking off, seen from the side",
    "h-warning-gear": "a cog wheel with a cracked tooth and a small warning triangle leaning on it",
    "h-pizza": "a pizza in an open cardboard box",
    "h-robot": "a friendly small AI assistant robot head with glowing amber eyes",
    "h-developer": "a programmer at a laptop seen from behind, wearing headphones, stylized figurine",
    "h-money-bin": "banknotes falling into a waste bin",
    "h-contract": "a signed paper contract with a fountain pen and a wax seal",
    "h-calendar": "a desk calendar with many pages torn off and flying away",
    "h-stopwatch": "a stopwatch with the hand near the start",
    "h-hourglass": "an hourglass with sand running",
}


def generate(icon_id):
    ART.mkdir(parents=True, exist_ok=True)
    body = {"contents": [{"parts": [{"text": f"{ICONS[icon_id]}. {STYLE}"}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1", "imageSize": "1K"}}}
    data = call(f"{API}/models/{IMAGE_MODEL}:generateContent", body)
    image = next(p for p in data["candidates"][0]["content"]["parts"] if "inlineData" in p)["inlineData"]
    out = ART / f"{icon_id}.png"
    out.write_bytes(base64.b64decode(image["data"]))
    ledger(dict(id=icon_id, kind="hook-icon", model=IMAGE_MODEL, file=str(out.relative_to(PROJECT)),
                est_usd=COST["still"], prompt=ICONS[icon_id]))
    return out


def main(ids):
    for icon_id in ids or ICONS:
        if not ids and (ART / f"{icon_id}.png").exists():
            continue
        print(f"🖼  {icon_id} …", flush=True)
        try:
            print("   →", generate(icon_id).name, flush=True)
        except Exception as error:   # jedna nieudana ikona nie zatrzymuje reszty
            print("   ✗", type(error).__name__, str(error)[:160], flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
