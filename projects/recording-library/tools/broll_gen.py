#!/usr/bin/env python3
"""B-rolle generowane: najpierw GRAFIKA (kadr), potem OŻYWIENIE (wideo z kadru).

Dwa etapy, bo grafikę ocenia się w sekundę i kosztuje grosze, a ruch kosztuje
dużo i trwa minuty — ożywiamy tylko kadry, które przeszły ocenę.

  python3 tools/broll_gen.py --list
  python3 tools/broll_gen.py --stills              # brakujące kadry (Nano Banana Pro)
  python3 tools/broll_gen.py --stills s01 s04      # wybrane, nadpisuje
  python3 tools/broll_gen.py --animate s01 s04     # wideo 8 s z kadru (Veo 3.1)

Dostawca: Gemini API (klucz w ~/Repo/GEMINI_API, nigdy nie wypisywany).
Docelowo Higgsfield — ten sam podział na etapy, inne wywołanie.
Wynik: assets/broll/stills/<id>.png, assets/broll/video/<id>.mp4 (W GICIE —
płatne i generatywne, drugi raz nie wyjdą identycznie). Rejestr kosztów i
oznaczeń AI: data/broll-ledger.json.
"""
import base64
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

from sources import DATA, PROJECT

API = "https://generativelanguage.googleapis.com/v1beta"
IMAGE_MODEL = os.environ.get("IMAGE_MODEL", "gemini-3-pro-image")
VIDEO_MODEL = os.environ.get("VEO_MODEL", "veo-3.1-fast-generate-preview")
STILLS = PROJECT / "assets" / "broll" / "stills"
VIDEOS = PROJECT / "assets" / "broll" / "video"
LEDGER = DATA / "broll-ledger.json"

# Szacunki do budżetu nocy (cennik Gemini API, październik 2026 — do weryfikacji
# na fakturze): kadr Nano Banana Pro ~0,13 USD, Veo 3.1 fast ~0,15 USD/s.
COST = {"still": 0.134, "video_per_s": 0.15}

# Wspólny styl z 18 ujęciami Veo z projects/youtube — ta sama estetyka w całej bibliotece.
STYLE = ("cinematic documentary still, dark interior, warm practical lighting, shallow depth of field, "
         "muted amber and deep green tones, 35mm film look, realistic Polish small-business setting, Central European (Polish) people only, "
         "main subject in the CENTER third of the frame (the frame will be cropped to vertical), "
         "absolutely no readable text, no letters, no logos, no watermarks, 16:9")

SHOTS = [
    dict(id="s01", slug="prezes-lotnisko", used_by=["ad-19-ra1", "ad-20-ra2", "ad-24-e7"],
         prompt="a businessman in his fifties sitting in a quiet airport lounge at dusk, looking at his smartphone with a calm, satisfied expression, large windows with an airplane on the tarmac behind him",
         motion="slow push-in towards the man, he glances at the phone and slightly nods, airplane lights blink outside"),
    dict(id="s02", slug="telefon-czat-dlon", used_by=["ad-19-ra1", "ad-20-ra2", "ad-26-w10"],
         prompt="close-up of a hand holding a smartphone with an abstract messaging app on screen (soft colored chat bubbles, nothing readable), dark office, screen glow on the fingers",
         motion="thumb taps the screen, new chat bubble slides in, gentle handheld drift"),
    dict(id="s03", slug="umowa-do-czatu", used_by=["ad-28-w1", "ad-35-w9", "ad-25-e5"],
         prompt="one single continuous shot: a woman office employee seen from the side at her desk, her laptop screen shows an abstract glowing chat interface (nothing readable), a printed contract with a signature lies next to the laptop, evening office, one camera angle only, no split screen",
         motion="slow lateral dolly, the employee hesitates, then clicks, screen light flickers on the face"),
    dict(id="s04", slug="wydruk-zamowienia", used_by=["ad-11-r1", "ad-15-r5", "ad-16-r6", "ch-doram-1-nazwy"],
         prompt="a thick stack of printed order pages fanned out on a desk next to a laptop with a spreadsheet, tired hands sorting the pages under a warm desk lamp",
         motion="hands flip pages one after another, slow top-down push-in"),
    dict(id="s05", slug="zeszyt-na-hali", used_by=["ad-12-r2", "ad-22-e2"],
         prompt="a single photograph, one frame, no panels, no collage: close-up of an old worn handwritten notebook lying open on a wooden workbench, an elderly worker's hand resting on the page, blurred furniture workshop behind",
         motion="a page is turned slowly, dust in the light beam, subtle push-in"),
    dict(id="s06", slug="worki-paszy-etykiety", used_by=["ch-marpasz-1-cztery-worki", "ch-marpasz-2-100-godzin", "ep-marpasz"],
         prompt="a small e-commerce warehouse with stacked 25 kg animal feed sacks, a worker sticking shipping labels onto four identical sacks, a label printer on the table",
         motion="worker sticks a label, a new label comes out of the printer, slow pan along the sacks"),
    dict(id="s07", slug="pamiatki-tablet", used_by=["ch-rezon-2-ustka-rowy", "ch-rezon-3-panel-klienta", "ep-rezon"],
         prompt="a sales representative showing a tablet catalogue to a shop owner in a seaside souvenir shop, shelves with colorful magnets, mugs and wooden souvenirs, daylight through the window",
         motion="the shop owner points at the tablet, the rep swipes, slow orbit"),
    dict(id="s08", slug="szwalnia-meble-ogrodowe", used_by=["ep-doram", "ch-doram-2-kilka-dni-10-minut"],
         prompt="an upholstery workshop sewing cushions for garden furniture, rolls of outdoor fabric, a worker at an industrial sewing machine",
         motion="the sewing machine runs, fabric moves forward, slow push-in"),
    dict(id="s09", slug="warsztat-pizza", used_by=["ad-27-w11", "ad-26-w10", "ad-36-w7", "ad-29-w4"],
         prompt="a small group of business owners around a workshop table with laptops and open pizza boxes, a presenter gestures at a screen, friendly evening atmosphere",
         motion="people laugh and lean towards the screen, slow lateral dolly"),
    dict(id="s10", slug="poranny-raport-kawa", used_by=["ad-19-ra1", "ad-24-e7", "ch-vacu-6-brief-telegram"],
         prompt="a business owner at home in the morning holding a coffee cup and reading a short report on his phone, kitchen window light",
         motion="steam rises from the cup, he scrolls and smiles, slow push-in"),
    dict(id="s11", slug="hala-sprzet-sportowy", used_by=["ep-vacuactiv", "ch-vacu-5-kierownik-w-godzine"],
         prompt="a small factory assembling high-end fitness equipment, metal frames on stands, a worker welding with sparks",
         motion="sparks fly, camera glides past the frames"),
    dict(id="s12", slug="etykiety-kody-kreskowe", used_by=["ch-doram-6-kody-15-minut", "ep-doram"],
         prompt="a label printer quickly printing a long strip of barcode labels, a hand peels a label and sticks it onto a cardboard box",
         motion="labels stream out of the printer, hand sticks one on a box"),
]


def key():
    raw = (Path.home() / "Repo" / "GEMINI_API").read_text()
    return re.match(r"\s*[A-Z_]+\s*[=:]\s*[\"']?([^\"'\s]+)", raw).group(1)


def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"content-type": "application/json", "x-goog-api-key": key()})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def ledger(entry):
    rows = json.load(open(LEDGER)) if LEDGER.exists() else []
    rows.append(dict(entry, at=time.strftime("%Y-%m-%d %H:%M"), ai_generated=True))
    json.dump(rows, open(LEDGER, "w"), ensure_ascii=False, indent=1)


def still(shot):
    STILLS.mkdir(parents=True, exist_ok=True)
    body = {"contents": [{"parts": [{"text": f"{shot['prompt']}. {STYLE}"}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"}}}
    data = call(f"{API}/models/{IMAGE_MODEL}:generateContent", body)
    parts = data["candidates"][0]["content"]["parts"]
    image = next(p for p in parts if "inlineData" in p)["inlineData"]
    ext = "jpg" if "jpeg" in image.get("mimeType", "") else "png"   # model zwraca JPEG mimo prośby o kadr
    out = STILLS / f"{shot['id']}-{shot['slug']}.{ext}"
    out.write_bytes(base64.b64decode(image["data"]))
    ledger(dict(id=shot["id"], kind="still", model=IMAGE_MODEL, file=str(out.relative_to(PROJECT)),
                est_usd=COST["still"], prompt=shot["prompt"]))
    return out


def animate(shot, seconds=8):
    VIDEOS.mkdir(parents=True, exist_ok=True)
    src = next(STILLS.glob(f"{shot['id']}-*.*"))
    body = {"instances": [{"prompt": f"{shot['motion']}. Keep the exact framing and look of the image. "
                                     "Cinematic, realistic motion, no text appears.",
                           "image": {"bytesBase64Encoded": base64.b64encode(src.read_bytes()).decode(),
                                     "mimeType": "image/jpeg" if src.suffix == ".jpg" else "image/png"}}],
            "parameters": {"aspectRatio": "16:9", "resolution": "1080p", "durationSeconds": seconds}}
    op = call(f"{API}/models/{VIDEO_MODEL}:predictLongRunning", body)
    for _ in range(80):
        time.sleep(12)
        st = call(f"{API}/{op['name']}")
        if st.get("error"):
            raise SystemExit(f"{shot['id']}: {st['error']}")
        if not st.get("done"):
            continue
        res = st.get("response", {})
        samples = res.get("generateVideoResponse", {}).get("generatedSamples") or res.get("generatedSamples") or []
        if not samples:
            raise SystemExit(f"{shot['id']}: brak wideo — {json.dumps(res)[:400]}")
        uri = samples[0]["video"]["uri"]
        req = urllib.request.Request(uri, headers={"x-goog-api-key": key()})
        out = VIDEOS / f"{shot['id']}-{shot['slug']}.mp4"
        with urllib.request.urlopen(req, timeout=300) as r:
            out.write_bytes(r.read())
        ledger(dict(id=shot["id"], kind="video", model=VIDEO_MODEL, file=str(out.relative_to(PROJECT)),
                    est_usd=round(COST["video_per_s"] * seconds, 2), seconds=seconds, motion=shot["motion"]))
        return out
    raise SystemExit(f"{shot['id']}: timeout")


def main(argv):
    ids = [a for a in argv if not a.startswith("--")]
    pick = [s for s in SHOTS if not ids or s["id"] in ids]
    if "--list" in argv:
        for s in SHOTS:
            have = "kadr" if list(STILLS.glob(f"{s['id']}-*.*")) else "    "
            vid = "wideo" if list(VIDEOS.glob(f"{s['id']}-*.mp4")) else "     "
            print(f"{s['id']} {have} {vid} {s['slug']:<26} → {', '.join(s['used_by'])}")
    if "--stills" in argv:
        for s in pick:
            if not ids and list(STILLS.glob(f"{s['id']}-*.*")):
                continue
            print(f"🖼  {s['id']} {s['slug']} …", flush=True)
            print("   →", still(s).name, flush=True)
    if "--animate" in argv:
        for s in pick:
            print(f"🎬 {s['id']} {s['slug']} …", flush=True)
            print("   →", animate(s).name, flush=True)
    if LEDGER.exists():
        rows = json.load(open(LEDGER))
        print(f"Σ szacunek: {sum(r['est_usd'] for r in rows):.2f} USD ({len(rows)} pozycji)")


if __name__ == "__main__":
    main(sys.argv[1:])
