#!/usr/bin/env python3
"""Etap 2b — warstwy graficzne czterech shortów: napisy, tytuły, plakietki,
plansze końcowe.

Adaptacja `projects/shorts IG/tools/style.py` (stamtąd idą też fonty i logo):
ta sama mechanika okien napisów liczonych z CZASÓW SŁÓW transkrypcji gotowej
osi (build/work/<key>.json), bursztynowe aktywne słowo, kryjąca podkładka.
Różnice: cztery shorty na raz, FIXES per short, tytuł siedzi NAD pasem napisów
(y≈1000 — napisy lecą od 1. sekundy równolegle z tytułem), finał to pytanie
na żywym kadrze (ogon źródła doklejany w assemble.py).
"""
import importlib.util
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BUILD = os.path.join(ROOT, "build")
WORK = os.path.join(BUILD, "work")
OV = os.path.join(BUILD, "overlays")
IG_TOOLS = os.path.abspath(os.path.join(ROOT, "..", "..", "..", "shorts IG", "tools"))
LOGO = os.path.join(IG_TOOLS, "flowbiz-white-notag.png")

# Mechanika napisów przychodzi z shorts IG bez kopiowania kodu.
spec = importlib.util.spec_from_file_location("ig_style",
                                              os.path.join(IG_TOOLS, "style.py"))
ig = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ig)

# Shorty studyjne ≠ reelsy z telefonu: typografia idzie za grafiką odcinka
# (DM Sans z systemu animacji FlowBiz), nie za Poppinsem z shorts IG.
# Mapowanie zamiast zmian w mechanice — ig.render_caption woła ig.font().
_DM = {
    "Poppins-Bold.ttf": "DMSans-ExtraBold.ttf",
    "Poppins-SemiBold.ttf": "DMSans-SemiBold.ttf",
    "Poppins-Medium.ttf": "DMSans-Medium.ttf",
}


def _dm_font(name, size):
    from PIL import ImageFont
    return ImageFont.truetype(
        os.path.join(HERE, "fonts", _DM.get(name, name)), size)


ig.font = _dm_font

# Interlinia i podkładka: wersja z shorts IG rysowała OSOBNY plate pod każdą
# linią przy interlinii 88 — plate'y na siebie nachodziły i okno wyglądało na
# „sklejone i nierówne" (uwaga Mateusza). Tu: JEDNA podkładka pod całe okno
# i interlinia 102.
CAP_LINE = 102


def _render_caption(lines, active_index):
    from PIL import Image as PILImage, ImageDraw as PILDraw
    img = PILImage.new("RGBA", (ig.CAP_W, ig.CAP_H), (0, 0, 0, 0))
    d = PILDraw.Draw(img)
    fnt = ig.font("Poppins-Bold.ttf", ig.CAP_SIZE)
    space = d.textlength(" ", font=fnt)

    widths_per_line = [[d.textlength(w["word"], font=fnt) for w in ln]
                      for ln in lines]
    line_w = [sum(ws) + space * (len(ws) - 1) for ws in widths_per_line]
    total_h = len(lines) * CAP_LINE
    y0 = (ig.CAP_H - total_h) // 2
    pad_x, pad_y = 30, 18
    box_w = max(line_w)
    d.rounded_rectangle(
        [(ig.CAP_W - box_w) / 2 - pad_x, y0 - pad_y,
         (ig.CAP_W + box_w) / 2 + pad_x,
         y0 + total_h - (CAP_LINE - ig.CAP_SIZE) + pad_y],
        radius=24, fill=ig.INK + (ig.PLATE_ALPHA,))

    idx, y = 0, y0
    for ln, ws, lw in zip(lines, widths_per_line, line_w):
        x = (ig.CAP_W - lw) / 2
        for w, ww in zip(ln, ws):
            fill = ig.AMBER if idx == active_index else ig.LIGHT
            d.text((x, y), w["word"], font=fnt, fill=fill + (255,))
            x += ww + space
            idx += 1
        y += CAP_LINE
    return img


ig.render_caption = _render_caption

from edl import INTRO, SHORTS, STAMPS  # noqa: E402  (sys.path: tools/)

W, H, FPS = 1080, 1920, 30
INK, AMBER, LIGHT = ig.INK, ig.AMBER, ig.LIGHT

# Poprawki zapisu per short — wyłącznie zapis, nie treść wypowiedzi.
# Klucz: słowo bez interpunkcji, lowercase (mechanika FIXES z shorts IG).
FIXES_COMMON = {
    "mercato": "Mercato",
    "merkato": "Mercato",
    "ai": "AI",
}

# Sklejki dwóch sąsiednich tokenów, których FIXES nie obsłuży: Whisper
# rozbił „AI też potrafi pisać aplikacje" na „a i też…".
MERGES = {
    "s1-po-co-skoro-excel-dziala": [("a", "i", "AI")],
}
FIXES = {
    "s1-po-co-skoro-excel-dziala": {
        "notecode": "no-code",
        "sase": "SaaS-y",
    },
    "s2-ten-sam-excel-w-kilku-wersjach": {
        "film": "firm",          # „wchodzę do firm" — Whisper usłyszał „film"
    },
    "s3-komu-odradzam": {
        "sasie": "SaaS-ie",
        "sprawdzić": "sprawdzicie",   # „i tak to pewnie sobie sprawdzicie"
    },
    "s4-sto-procent-dostepu-do-kodu": {
        "cloud": "Claude",       # kolega mówi o agencie Claude, nie o chmurze
        "make": "Make",
        "zapier": "Zapier",
        "open": "Open",
    },
}

OUTROS = {
    "s1-po-co-skoro-excel-dziala": dict(
        kicker="OPEN MERCATO",
        lines=["A Twoja firma ma system,", "czy tylko narzędzia?"]),
    "s2-ten-sam-excel-w-kilku-wersjach": dict(
        kicker="OPEN MERCATO",
        lines=["Ile wersji jednego", "Excela żyje u Ciebie?"]),
    "s3-komu-odradzam": dict(
        kicker="OPEN MERCATO",
        lines=["Masz w firmie jedną", "osobę techniczną?"]),
    "s4-sto-procent-dostepu-do-kodu": dict(
        kicker="KOD TWOJEGO SYSTEMU",
        lines=["Wolisz wynajmować,", "czy mieć na własność?"]),
}


def intro_card(cfg, ov_dir):
    """Cold-open w DWÓCH warstwach (kicker+kreska / pytanie), bo wjeżdżają
    na ekran osobno — statyczne intro dawało hook 30–36 w virality_predictor,
    a z `.ai/memory/copy-i-hook`: ruch w 1. sekundzie waży więcej niż treść."""
    single = len(cfg["lines"]) == 1
    sizes = [110 if single else 96] * len(cfg["lines"])
    block = 64 + 46 + sum(int(s * 1.18) for s in sizes)
    y0 = (H - block) // 2 - 60

    kick = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(kick)
    y = y0
    if cfg.get("kicker"):
        fk = ig.font("Poppins-SemiBold.ttf", 34)
        kw = d.textlength(cfg["kicker"], font=fk)
        d.text(((W - kw) / 2, y), cfg["kicker"], font=fk, fill=AMBER + (255,))
    y += 64
    d.rectangle([(W - 110) / 2, y, (W + 110) / 2, y + 7], fill=AMBER + (255,))
    kick.save(os.path.join(ov_dir, "intro-kicker.png"))

    main = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(main)
    y = y0 + 64 + 46
    for ln, size in zip(cfg["lines"], sizes):
        fb = ig.font("Poppins-Bold.ttf", size)
        while d.textlength(ln, font=fb) > W - 120 and size > 52:
            size -= 4
            fb = ig.font("Poppins-Bold.ttf", size)
        lw = d.textlength(ln, font=fb)
        d.text(((W - lw) / 2, y), ln, font=fb, fill=LIGHT + (255,),
               stroke_width=4, stroke_fill=INK + (200,))
        y += int(size * 1.18)
    main.save(os.path.join(ov_dir, "intro-main.png"))


def stamp(text, path, size, rot):
    """Stempel kinetyczny: duże hasło z grubym ciemnym obrysem, lekko
    przekręcone — wchodzi na obraz z fade+slide w assemble."""
    fb = ig.font("Poppins-Bold.ttf", size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    while tmp.textlength(text, font=fb) > W - 140 and size > 40:
        size -= 4
        fb = ig.font("Poppins-Bold.ttf", size)
    tw = int(tmp.textlength(text, font=fb))
    pad = 40
    img = Image.new("RGBA", (tw + pad * 2, size + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((pad, pad), text, font=fb, fill=AMBER + (255,),
           stroke_width=10, stroke_fill=INK + (235,))
    img = img.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.save(path)
    return path


def normalized_transcript(key):
    """Sklejka tokenów, których FIXES nie obsłuży: „1"+„.0"→„1.0", „100"+„%"→„100%".

    Whisper rozbija liczby na osobne słowa; w napisie „wersja 1 .0" czyta się
    jak literówka. Sklejamy PRZED mechaniką okien, żeby czasy słowa objęły
    całą liczbę.
    """
    src = os.path.join(WORK, f"{key}.json")
    data = json.load(open(src))
    merges = list(MERGES.get(key, []))
    for seg in data["segments"]:
        words = seg.get("words", [])
        out = []
        for w in words:
            token = w["word"].strip()
            if out and token in {".0", "%"}:
                out[-1]["word"] = out[-1]["word"].rstrip() + token
                out[-1]["end"] = w["end"]
                continue
            prev = out[-1]["word"].strip().strip(".,!?…") if out else None
            hit = next((m for m in merges
                        if m[0] == (prev or "").lower()
                        and m[1] == token.strip(".,!?…").lower()), None)
            if hit:
                out[-1]["word"] = hit[2]
                out[-1]["end"] = w["end"]
                merges.remove(hit)
                continue
            out.append(w)
        seg["words"] = out
    dst = os.path.join(WORK, f"{key}-caps.json")
    json.dump(data, open(dst, "w"))
    return dst


def media_len(key):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
         "stream=duration", "-of", "csv=p=0",
         os.path.join(BUILD, "rough", f"{key}.mp4")],
        capture_output=True, text=True).stdout.strip().rstrip(","))


def main():
    only = set(sys.argv[1:])
    for key in SHORTS:
        if only and not any(key.startswith(o) for o in only):
            continue
        ov = os.path.join(OV, key)
        os.makedirs(ov, exist_ok=True)

        ig.FIXES.clear()
        ig.FIXES.update(FIXES_COMMON)
        ig.FIXES.update(FIXES.get(key, {}))
        shots, end = ig.build_captions(normalized_transcript(key),
                                       os.path.join(ov, "captions"),
                                       media_len(key))
        lst = os.path.join(ov, "captions.txt")
        with open(lst, "w") as fh:
            for path, dur_ in shots:
                fh.write(f"file '{path}'\nduration {dur_:.4f}\n")
            fh.write(f"file '{shots[-1][0]}'\n")
        print(f"{key}: {len(shots)} okien napisów do {end:.2f}s")

        intro_card(INTRO[key], ov)
        for i, (text, _t0, _t1, _y, size, rot) in enumerate(STAMPS.get(key, [])):
            stamp(text, os.path.join(ov, f"stamp-{i}.png"), size, rot)
        ig.question_plate(OUTROS[key]["lines"], os.path.join(ov, "outro.png"),
                          kicker=OUTROS[key]["kicker"], footer="flowbiz.pl",
                          logo=LOGO)

    # Plakietki s3: liczby, które w mowie przelatują, na ekranie zostają.
    s3 = os.path.join(OV, "s3-komu-odradzam")
    if not only or any("s3".startswith(o) or o.startswith("s3") for o in only):
        ig.badge("WYSTARCZY", "1 programista", os.path.join(s3, "badge-programista.png"))
        ig.badge("MŁODY PROJEKT", "wersja 0.x", os.path.join(s3, "badge-wersja.png"))
    print(f"warstwy → {OV}")


if __name__ == "__main__":
    main()
