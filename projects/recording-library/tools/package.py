#!/usr/bin/env python3
"""Opakowanie klipu w grafikę: storyboard → kompozycja HyperFrames → MP4.

Jeden storyboard (packaging/storyboards/<clip>.json) daje wszystkie warianty:

  format   reels    9:16, twarz u góry, karty w dolnym panelu, napisy, CTA organiczne
           ad       9:16, jak reels + hook na starcie, stały chip CTA, plansza końcowa
           youtube  16:9, twarz pełnym kadrem, karty w panelu bocznym, bez napisów
  palette  A        kanał YouTube — #0A0A08 + bursztyn, DM Sans
           B        strona flowbiz.pl — ciemna zieleń + #1C9E7A, Plus Jakarta Sans

Zdarzenia w storyboardzie kotwiczą się na SŁOWACH (`"at": "lotnisku"`), nie na
sekundach — po przecięciu klipu grafika jedzie razem z wypowiedzią. Liczba
w `at` to sekundy osi klipu, "+1.5" to przesunięcie od poprzedniego zdarzenia.

  python3 tools/package.py ad-19-ra1                      # wszystkie formaty × palety
  python3 tools/package.py ad-19-ra1 --format reels --palette A
  python3 tools/package.py ad-19-ra1 --render             # + render MP4 do final/samples/
  python3 tools/package.py ad-19-ra1 --snapshot 3 12      # klatki kontrolne
"""
import argparse
import base64
import html
import json
import os
import random
import re
import shutil
import subprocess
from pathlib import Path

from sources import load_clips, BUILD, DATA, FACE_CENTER_X, LIBRARY, PROJECT, SOURCE_W

PACK = PROJECT / "packaging"
BRAND = PACK / "brand"
OUT = BUILD / "packaging"
FINAL = PROJECT / "final" / "samples"
GSAP = Path.home() / ".claude/skills/talking-head-recut/assets/vendor/gsap.min.js"
NODE22 = Path.home() / ".nvm/versions/node/v22.22.2/bin"
FPS = 30

PALETTES = {
    # Kanał YouTube — ta sama paleta co system wstawek (scene-shell.css).
    "A": dict(name="kanał YouTube", bg="#0A0A08", panel="#0D0D0B", raised="#16140F",
              line="#2E2C28", text="#FAF8F0", muted="#9A938A", accent="#F5A623",
              accent2="#6BAA6B", danger="#C0553A", on_accent="#0A0A08",
              font="DM Sans", grid="rgba(245,166,35,0.06)"),
    # Strona flowbiz.pl — tryb ciemny strony (hsl 165 40% 8%) + marka #1C9E7A.
    "B": dict(name="strona flowbiz.pl", bg="#0C1D18", panel="#10241E", raised="#163029",
              line="#24413A", text="#F4FAF7", muted="#8FB0A6", accent="#1C9E7A",
              accent2="#F5A623", danger="#E5604A", on_accent="#FFFFFF",
              font="Plus Jakarta Sans", grid="rgba(28,158,122,0.08)"),
    # AI Słupsk — tokeny ze strony aislupsk.pl (src/index.css): granat-fiolet, róż,
    # nagłówki pochyłe (Mateusz 9.10: „pod aislupsk idź w tym kierunku wizualnym”).
    "S": dict(name="AI Słupsk", bg="#160A2E", panel="#1A0D36", raised="#2C1F47",
              line="#392D53", text="#FFFFFF", muted="#ADA3C2", accent="#FF3388",
              accent2="#A219E6", danger="#FF5A5A", on_accent="#FFFFFF",
              font="Plus Jakarta Sans", grid="rgba(255,51,136,0.07)", heading_style="italic", word_gap="0.1em",
              bg_fill="linear-gradient(135deg,#160A2E 0%,#0F173D 50%,#261745 100%)"),
}
for palette in PALETTES.values():
    palette.setdefault("heading_style", "normal")
    palette.setdefault("bg_fill", palette["bg"])
    palette.setdefault("word_gap", "normal")   # kursywa z ujemnym trackingiem zlepia słowa

# Mateusz 9.10: zostajemy przy A (bursztyn) — zieleń B wygląda kiepsko na wideo.
# B zostaje w słowniku do ręcznego --palette B, ale nie renderuje się domyślnie.
ACTIVE_PALETTES = ["A"]


def output_name(clip, board):
    """Nazwa wyjścia: id klipu, a dla wariantu testu A/B id--wariant."""
    return clip["id"] + (f"--{board['variant']}" if board.get("variant") else "")


def palettes_for(board, clip):
    """Marka ma swoją paletę (AI Słupsk → S); flowbiz jedzie na ACTIVE_PALETTES."""
    brand = BRANDS[board.get("brand", clip["brand"])]
    return [brand["palette"]] if brand.get("palette") else ACTIVE_PALETTES

# Kolor marki w wersji czytelnej na ciemnym tle (jak w projects/youtube).
LOGO_COLORS = {
    "claude": "#D97757", "anthropic": "#D97757", "openmercato": "#F5A623", "github": "#FAF8F0",
    "hubspot": "#FF7A59", "salesforce": "#00A1E0", "n8n": "#EA4B71", "make": "#B36BFF",
    "zapier": "#FF4F00", "openai": "#FAF8F0", "excel": "#21A366", "googlesheets": "#34A853",
    "googledrive": "#4285F4", "shopify": "#7AB55C", "woocommerce": "#C285D6", "slack": "#FAF8F0",
    "notion": "#FAF8F0", "airtable": "#18BFFF", "retool": "#5B8AF5", "gmail": "#EA4335",
    "youtube": "#FF0000", "wordpress": "#5A9FC4", "telegram": "#26A5E4", "whatsapp": "#25D366", "obsidian": "#A88BFA",
    "googlegemini": "#8E9BFF", "allegro": "#FF5A00", "adobeacrobatreader": "#EC1C24",
    "googlecalendar": "#4285F4", "dropbox": "#0061FF",
}

BRANDS = {
    "flowbiz": dict(mark="flowbiz", tagline="systemy AI-first dla firm", web="flowbiz.pl",
                    phone="536 507 701", places=["Słupsk", "Pomorze", "Gdańsk", "Koszalin"]),
    "aislupsk": dict(mark="AI Słupsk", tagline="warsztaty AI dla firm z regionu", web="aislupsk.pl",
                     phone="536 507 701", places=["Słupsk", "Lębork", "Ustka", "Koszalin"],
                     palette="S", cutout="mateusz-cutout.png"),
}

FORMATS = {
    "reels": dict(w=1080, h=1920, face_h=1215),
    "ad": dict(w=1080, h=1920, face_h=1215),
    "youtube": dict(w=1920, h=1080, face_h=1080),
    # zajawka odcinka na LinkedIn / Facebook: pion 4:5 zajmuje feed, a nie jest ucinany jak 9:16
    "feed": dict(w=1080, h=1350, face_h=810),
}


# ── czas: kotwice na słowach ─────────────────────────────────────────────────

def norm(text):
    return re.sub(r"[^\wąćęłńóśźż0-9%]", "", text.lower())


class Clock:
    @staticmethod
    def match(word, target):
        """Dokładne słowo; prefiks tylko z tyldą („zapam~”) — „Po” nie może trafić w „początku”."""
        text, prefix = target
        return norm(word).startswith(text) if prefix else norm(word) == text

    def __init__(self, words, fixes):
        self.words = words
        self.fixes = fixes
        self.cursor = 0.0

    def at(self, value, base=None, floor=None):
        """'słowo' | 'słowo#2' | 12.3 | '+1.5' → sekundy osi klipu.

        Słowo szukane jest od `floor` w przód (domyślnie od bieżącego zdarzenia) —
        inaczej „Siedzi” trafia w pierwsze „siedzi” z hooka i czas wychodzi ujemny."""
        floor = self.cursor if floor is None else floor
        if isinstance(value, (int, float)):
            return float(value)
        if value.startswith("+"):
            return (base if base is not None else self.cursor) + float(value[1:])
        phrase, _, nth = value.partition("#")
        target = [(norm(p), p.endswith("~")) for p in phrase.split()]
        hits = []
        for i in range(len(self.words) - len(target) + 1):
            if all(self.match(self.words[i + k]["word"], target[k]) for k in range(len(target))):
                hits.append(self.words[i]["start"])
        hits = [h for h in hits if h >= floor - 0.01]
        if not hits:
            raise SystemExit(f"nie ma słowa „{value}” w klipie")
        return hits[int(nth or 1) - 1]


# ── zasoby ───────────────────────────────────────────────────────────────────

def logos_css():
    rows = [".logo{display:inline-block;flex:none;height:1em;background-color:currentColor;"
            "-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;-webkit-mask-position:center;"
            "mask-position:center;-webkit-mask-size:contain;mask-size:contain}"]
    for svg in sorted((BRAND / "logos").glob("*.svg")):
        text = svg.read_text()
        box = re.search(r'viewBox="\s*[\d.-]+\s+[\d.-]+\s+([\d.]+)\s+([\d.]+)', text)
        ratio = float(box.group(1)) / float(box.group(2)) if box else 1.0
        data = base64.b64encode(text.encode()).decode()
        color = LOGO_COLORS.get(svg.stem, "#FAF8F0")
        rows.append(f".logo-{svg.stem}{{width:{ratio:.3f}em;color:{color};"
                    f"-webkit-mask-image:url(data:image/svg+xml;base64,{data});"
                    f"mask-image:url(data:image/svg+xml;base64,{data})}}")
    return "\n".join(rows)


def logo_ratio(name):
    box = re.search(r'viewBox="\s*[\d.-]+\s+[\d.-]+\s+([\d.]+)\s+([\d.]+)', (BRAND / "logos" / f"{name}.svg").read_text())
    return float(box.group(1)) / float(box.group(2)) if box else 1.0


def logo_in_tile(name, size, tile_w):
    """Szeroki znak słowny (Open Mercato) nie może wyjść poza kafelek — liczymy wysokość z proporcji."""
    return logo(name, int(min(size, tile_w / logo_ratio(name))))


def logo(name, size=None, color=None):
    style = []
    if size:
        style.append(f"font-size:{size}px")
    if color:
        style.append(f"color:{color}")
    return f'<i class="logo logo-{name}" style="{";".join(style)}"></i>'


DIGIT_GROUP = re.compile(r"^\*?\+?\d[\d\u00a0]*%?$")


def tokens(text):
    """Słowa do złamania w linii — ciąg grup cyfr (numer telefonu „536 507 701”) i liczba
    z jednostką („3 miesiące”) to jeden token: nie rozjeżdżają się na dwie linie, a akcent
    z gwiazdki obejmuje całość."""
    out = []
    for word in text.split():
        if out and (word == "→" or out[-1].endswith("→")):
            # „70% → 94%” to jedna para — strzałka nie zaczyna ani nie kończy linii
            out[-1] += "\u00a0" + word.lstrip("*")
        elif out and DIGIT_GROUP.match(out[-1]) and (DIGIT_GROUP.match(word) or (word[:1].isalpha() and "\u00a0" not in out[-1])):
            # „3 miesiące”, „15 minut” — liczba nie zostaje sama na końcu linii
            out[-1] += "\u00a0" + word.lstrip("*")
        else:
            out.append(word)
    return out


def sentences(text):
    return [p for p in re.split(r"(?<=[.?!])\s+", text.strip()) if p]


def fit(text, width, largest, lines=1, smallest=34):
    """Rozmiar fontu, przy którym tekst mieści się w strefie: najdłuższe słowo w jednej
    linii i całość w `lines` liniach. Szacunek z szerokości znaku (0,68 em dla DM Sans 800),
    bo w kompozycji nie ma pomiaru przed renderem — sprawdza to potem hyperframes check."""
    clean = text.replace("*", "")
    longest = max((len(w) for w in tokens(clean)), default=1)
    size = min(largest, width / (0.68 * longest), width * lines / (0.64 * max(len(clean), 1)))
    return max(smallest, int(size))


def esc(text):
    return html.escape(text, quote=True)


# ── budowa kompozycji ────────────────────────────────────────────────────────

class Composition:
    def __init__(self, clip, board, fmt, palette):
        self.clip, self.board, self.fmt, self.pal = clip, board, fmt, PALETTES[palette]
        self.palette_key = palette
        self.geo = FORMATS[fmt]
        self.vertical = fmt != "youtube"
        self.brand = BRANDS[board.get("brand", clip["brand"])]
        words = json.load(open(LIBRARY / clip["id"] / "words.json"))
        self.splices_file = LIBRARY / clip["id"] / "splices.json"
        fixes = json.load(open(DATA / "caption-fixes.json"))
        self.words = [dict(w, word=self.fix(w["word"], fixes)) for w in words]
        self.clock = Clock(self.words, fixes)
        self.clip_len = round(clip["duration"], 3)
        self.end_len = board.get("endcard", {}).get(fmt, {"ad": 3.5, "reels": 2.6, "youtube": 2.5, "feed": 3.5}[fmt])
        self.total = round(self.clip_len + self.end_len, 3)
        self.html, self.js, self.media = [], [], {}
        self.n = 0
        self.ai_shown = False
        self.panel_busy = []
        self.side_windows = []
        self.hook_end = 0.0
        self.card_w = 888 if self.vertical else 700
        self.broll_html = []
        self.cards = []
        self.slates = []
        self.ai_until = 0.0

    @staticmethod
    def fix(word, fixes):
        for wrong, right in fixes.items():
            if wrong.startswith("_"):
                continue
            if word.strip(".,?!:;").lower() == wrong.lower():
                return word.replace(word.strip(".,?!:;"), right)
        return word

    def uid(self, prefix):
        self.n += 1
        return f"{prefix}{self.n}"

    def q(self, t):
        return round(round(t * FPS) / FPS, 4)

    # ── tło, wideo, panel ───────────────────────────────────────────────────
    def base(self):
        g, p = self.geo, self.pal
        face_x = FACE_CENTER_X[self.clip["source"]] / SOURCE_W * 100
        self.media["face.mp4"] = LIBRARY / self.clip["id"] / "master.mp4"
        if self.vertical:
            self.html.append(
                f'<div id="video-wrap" style="left:0;top:0;width:{g["w"]}px;height:{g["face_h"]}px">'
                f'<div id="face-zoom" style="transform-origin:50% 40%">'
                f'<video id="face" src="media/face.mp4" playsinline data-has-audio="true" data-start="0" '
                f'data-duration="{self.clip_len}" data-track-index="0" style="object-position:{face_x:.1f}% 50%"></video></div>'
                f'<!--BROLL--><div class="face-fade"></div></div>'
                f'<div id="panel" style="top:{g["face_h"]}px;height:{g["h"] - g["face_h"]}px">'
                f'<div class="panel-grid"></div><div class="panel-rule"></div>'
                f'</div>')
        else:
            self.html.append(
                f'<div id="video-wrap" style="left:0;top:0;width:{g["w"]}px;height:{g["h"]}px">'
                f'<div id="face-zoom" style="transform-origin:{face_x:.1f}% 40%">'
                f'<video id="face" src="media/face.mp4" playsinline data-has-audio="true" data-start="0" '
                f'data-duration="{self.clip_len}" data-track-index="0" style="object-position:{face_x:.1f}% 50%"></video></div>'
                f'<!--BROLL--></div>'
                f'<div id="side-plate"></div>')

    def brand_mark(self):
        if self.brand["mark"] == "flowbiz":
            return '<img src="media/flowbiz-ai.png" alt="flowbiz AI" class="mark-img">'
        return f'<span class="mark-text"><b>AI</b> Słupsk</span>'

    # ── karty ───────────────────────────────────────────────────────────────
    def host(self, start, end, inner, zone="panel", track=2):
        """Karta w strefie: panel (9:16 dół) / side (16:9 prawa) / full / top."""
        cid = self.uid("c")
        start, end = self.q(start), self.q(min(end, self.total))
        if zone == "panel":
            self.panel_busy.append((start, end))
        self.cards.append((start, end, re.sub(r"<[^>]+>", " ", inner)))
        self.html.append(f'<div class="card-host clip zone-{zone}" id="{cid}" data-start="{start}" '
                         f'data-duration="{round(end - start, 4)}" data-track-index="{track}">'
                         f'<div class="card" id="{cid}-in">{inner}</div></div>')
        rise = self.vertical or zone == "lower"
        self.js.append(f'tl.fromTo("#{cid}-in",{{opacity:0,y:{30 if rise else 0},x:{0 if rise else 60}}},'
                       f'{{opacity:1,y:0,x:0,duration:0.45,ease:"power3.out"}},{start});')
        self.js.append(f'tl.to("#{cid}-in",{{opacity:0,duration:0.3,ease:"power2.in"}},{round(end - 0.3, 4)});')
        if not self.vertical and zone == "side":
            self.side_windows.append((start, end))
        return cid

    def emit_side_windows(self):
        """16:9: sąsiednie okna panelu scalone — inaczej wyjazd i wjazd twarzy walczą o x."""
        if self.vertical:
            return
        self.js.insert(0, 'tl.set("#side-plate",{x:800},0);')
        merged = []
        for a, b in sorted(self.side_windows):
            if merged and a - merged[-1][1] < 1.4:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        for a, b in merged:
            self.side_window(max(a, 0.3), b)

    def side_window(self, start, end):
        # 16:9: twarz odjeżdża w lewo, z prawej wjeżdża płyta panelu
        self.js.append(f'tl.to("#video-wrap",{{x:-380,duration:0.6,ease:"power2.inOut"}},{round(start - 0.25, 4)});')
        self.js.append(f'tl.to("#side-plate",{{x:0,duration:0.6,ease:"power2.inOut"}},{round(start - 0.25, 4)});')
        self.js.append(f'tl.to("#video-wrap",{{x:0,duration:0.6,ease:"power2.inOut"}},{round(end - 0.1, 4)});')
        self.js.append(f'tl.to("#side-plate",{{x:800,duration:0.6,ease:"power2.inOut"}},{round(end - 0.1, 4)});')

    def stagger(self, selector, start, step=0.12, y=24):
        self.js.append(f'tl.fromTo("{selector}",{{opacity:0,y:{y},scale:0.92}},{{opacity:1,y:0,scale:1,'
                       f'duration:0.42,ease:"back.out(1.6)",stagger:{step}}},{self.q(start)});')

    def card_title(self, ev, start, end):
        """Kilka zdań: każde w swojej linii, kolejne dochodzi, gdy je mówię — nie wszystko naraz."""
        parts = sentences(ev["text"])
        largest = 92 if self.vertical else 76
        size = min([fit(ev["text"], self.card_w, largest, 3)] + [fit(p, self.card_w, largest, 2) for p in parts])
        body = "".join(f'<div class="sent">{self.words_html(p)}</div>' for p in parts)
        cid = self.host(start, end, f'<div class="kicker">{esc(ev.get("kicker", ""))}</div>'
                                    f'<div class="title" style="font-size:{size}px">{body}</div>'
                                    + (f'<div class="sub">{esc(ev["sub"])}</div>' if ev.get("sub") else ""),
                        ev.get("zone", self.default_zone()))
        times = self.sentence_times(parts, start + 0.15, end)
        for i, at in enumerate(times[:-1]):
            sel = f"#{cid} .sent:nth-child({i + 1}) .w"
            if i:
                self.js.append(f'tl.set("{sel}",{{opacity:0}},{self.q(start)});')
            self.stagger(sel, at, 0.06, 18)

    def card_logos(self, ev, start, end):
        """Pion: ikony narzędzi na osobnej planszy — w panelu pod twarzą giną.
        16:9: zostają w panelu bocznym (tam mają miejsce i się sprawdzają)."""
        if not self.vertical:
            items = self.logo_tiles(ev["items"], 84, 150, 600)
            cid = self.host(start, end, (f'<div class="kicker">{esc(ev["kicker"])}</div>' if ev.get("kicker") else "")
                            + f'<div class="logo-row">{items}</div>'
                            + (f'<div class="sub">{esc(ev["sub"])}</div>' if ev.get("sub") else ""),
                            ev.get("zone", self.default_zone()))
            self.stagger(f"#{cid} .logo-tile", start + 0.2, 0.14)
            return
        items = self.logo_tiles(ev["items"], 140, 240, 760)
        sid = self.slate(start, end, (f'<div class="kicker">{esc(ev["kicker"])}</div>' if ev.get("kicker") else "")
                         + f'<div class="logo-row">{items}</div>'
                         + (f'<div class="sub">{esc(ev["sub"])}</div>' if ev.get("sub") else ""))
        self.stagger(f"#{sid} .logo-tile", start + 0.2, 0.14)

    @staticmethod
    def logo_tiles(items, size, tile_w, row_w):
        """Kafelki logo; znak słowny (napis zamiast symbolu, np. Open Mercato) dostaje
        własny rząd na całą szerokość — w kwadratowym kafelku wychodzi nieczytelnie mały."""
        tiles = []
        for i in items:
            wide = logo_ratio(i["logo"]) > 2.5
            mark = logo_in_tile(i["logo"], size, row_w if wide else tile_w)
            name = "" if wide or not i.get("name") else f'<span>{esc(i["name"])}</span>'
            tiles.append(f'<div class="logo-tile{" wide" if wide else ""}">{mark}{name}</div>')
        return "".join(sorted(tiles, key=lambda t: ' wide"' in t))

    def cover(self):
        """Okładka: klip wyrwany z odcinka dostaje na pierwszym ekranie jedno zdanie kontekstu
        (Mateusz 9.10: „dobrze się słucha, ale musi być nadany kontekst na pierwszym ekranie”).
        Głos leci pod spodem, hook wchodzi po okładce. Ta klatka nadaje się też na okładkę rolki."""
        cover = self.board.get("cover")
        if not cover:
            return
        self.cover_end = cover.get("dur", 2.2)
        if cover.get("style") == "callout":
            # duże hasło na start (Mateusz 10.10: „AI W PRODUKCJI”, „AI SŁUPSK”) — 1,2 s,
            # potem od razu twarz z hookiem; test A/B wobec wersji bez hasła
            # hasło ma uderzać od krawędzi do krawędzi: rozmiar z najdłuższego słowa, każde w swojej linii
            longest = max(len(w.strip("*")) for w in cover["text"].split())
            size = int(min(300 if self.vertical else 260, (1000 if self.vertical else 1700) / (0.66 * longest)))
            sid = self.slate(0.0, self.cover_end,
                             (f'<div class="bt-label">{esc(cover["kicker"])}</div>' if cover.get("kicker") else "")
                             + f'<div class="callout" style="font-size:{size}px">{self.callout_lines(cover["text"])}</div>', instant=True)
            self.js.append(f'tl.fromTo("#{sid} .callout",{{scale:1.25,opacity:0}},{{scale:1,opacity:1,duration:0.35,ease:"power4.out"}},0);')
            self.flash(self.cover_end)
            return
        sid = self.slate(0.0, self.cover_end,
                         (f'<div class="kicker">{esc(cover["kicker"])}</div>' if cover.get("kicker") else "")
                         + f'<div class="slate-text" style="font-size:{fit(cover["text"], 900 if self.vertical else 1500, 104 if self.vertical else 110, 4)}px">{self.words_html(cover["text"])}</div>',
                         instant=True)
        self.js.append(f'tl.fromTo("#{sid} .slate-text .w",{{opacity:0.3}},{{opacity:1,duration:0.2,stagger:0.05}},0.05);')

    def callout_lines(self, text):
        """Każde słowo w swojej linii, ale krótkie (do 2 liter: „W”, „I”) dołącza do poprzedniego —
        samotne „W” w linii wygląda jak błąd."""
        lines = []
        for word in text.split():
            if lines and len(word.strip("*?")) <= 2:
                lines[-1] += " " + word
            else:
                lines.append(word)
        return "".join(f'<span class="w{" acc" if "*" in line else ""}">{esc(line.replace("*", ""))}</span>' for line in lines)

    def card_slate(self, ev, start, end):
        """Plansza: jedno zdanie na pełnym ekranie, głos leci pod spodem."""
        sid = self.slate(start, end, (f'<div class="kicker">{esc(ev["kicker"])}</div>' if ev.get("kicker") else "")
                         + f'<div class="slate-text" style="font-size:{fit(ev["text"], 900 if self.vertical else 1500, 110 if self.vertical else 120, 4)}px">{self.words_html(ev["text"])}</div>'
                         + (f'<div class="sub">{esc(ev["sub"])}</div>' if ev.get("sub") else ""), pip=ev.get("pip", False))
        self.stagger(f"#{sid} .slate-text .w", start + 0.12, 0.06, 18)

    def slate(self, start, end, inner, instant=False, pip=False):
        sid = self.uid("s")
        start, end = self.q(start), self.q(end)
        self.slates.append((start, end))
        self.panel_busy.append((start, end))   # plansza zakrywa panel — bez karty tematu pod spodem
        pip = pip and not self.vertical and end - start >= 2.5
        if pip:
            # 16:9: twarz nie znika pod makietą — zjeżdża do okienka w prawym dolnym rogu
            self.js.append(f'tl.set("#video-wrap",{{zIndex:8}},{start});')
            self.js.append(f'tl.fromTo("#video-wrap",{{scale:1,x:0,y:0,borderRadius:0}},{{scale:0.27,x:-48,y:-48,borderRadius:110,'
                           f'duration:0.5,ease:"power3.inOut"}},{start});')
            self.js.append(f'tl.to("#video-wrap",{{scale:1,x:0,y:0,borderRadius:0,duration:0.5,ease:"power3.inOut"}},{round(end - 0.5, 4)});')
            self.js.append(f'tl.set("#video-wrap",{{zIndex:1}},{end});')
        self.html.append(f'<div class="slate clip{" pip" if pip else ""}" id="{sid}" style="opacity:0" data-start="{start}" data-duration="{round(end - start, 4)}" '
                         f'data-track-index="8"><div class="end-grid"></div><div class="slate-body">{inner}</div></div>')
        self.js.append(f'tl.set("#{sid}",{{opacity:1}},{start});' if instant else
                       f'tl.fromTo("#{sid}",{{opacity:0}},{{opacity:1,duration:0.22}},{start});')
        self.js.append(f'tl.fromTo("#{sid} .slate-body",{{scale:0.94}},{{scale:1,duration:0.5,ease:"power3.out"}},{start});')
        self.js.append(f'tl.to("#{sid}",{{opacity:0,duration:0.22}},{round(end - 0.22, 4)});')
        return sid

    def card_mockup(self, ev, start, end):
        """Makieta systemu na pełnym ekranie (tools/mockups.py), głos leci pod spodem."""
        from mockups import MOCKUPS
        MOCKUPS[ev["name"]](self, ev, start, end)

    def card_beat(self, ev, start, end):
        """Uderzenie na pełnym ekranie — efekty z systemu wstawek YouTube
        (projects/youtube/…/design_handoff_flowbiz_animation): strike = s02 (liczba +
        przekreślenie po skosie), burst = s08 (liczba z poświatą + cząstki), slam = s10
        (trzy linie + belka z wstrząsem). Wejście przez błysk bieli jak w tamtym montażu."""
        style, q = ev["style"], self.q
        width = 900 if self.vertical else 1600
        label = f'<div class="bt-label">{esc(ev.get("label", ""))}</div>' if ev.get("label") else ""
        if style == "strike":
            big = fit(ev["main"], width, 280 if not self.vertical else 200, 1, 90)
            inner = (label + f'<div class="bt-main bt-acc" style="font-size:{big}px">{esc(ev["main"])}</div>'
                     + '<div class="bt-sub">' + "".join(f'<span class="w">{esc(w)}</span>' for w in ev.get("sub", [])) + '</div>'
                     + '<svg class="bt-strike" viewBox="0 0 100 100" preserveAspectRatio="none"><line x1="8" y1="64" x2="92" y2="36" '
                       'pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" vector-effect="non-scaling-stroke"/></svg>')
        elif style == "burst":
            big = fit(ev["num"], width, 420 if not self.vertical else 300, 1, 120)
            inner = (label + f'<div class="bt-num" style="font-size:{big}px">{esc(ev["num"])}<div class="bt-burst">'
                     + "".join('<i></i>' for _ in range(10)) + '</div></div>'
                     + (f'<div class="bt-bottom">{esc(ev["bottom"])}</div>' if ev.get("bottom") else ""))
        else:   # slam
            l1, l2, l3 = ev["lines"]
            sizes = [fit(l1, width, 230, 1, 80), fit(l2, width, 110, 1, 50), fit(l3, width, 230, 1, 80)]
            inner = (label + f'<div class="bt-l1" style="font-size:{sizes[0]}px">{esc(l1)}</div>'
                     f'<div class="bt-l2" style="font-size:{sizes[1]}px">{esc(l2)}</div><div class="bt-slam"></div>'
                     f'<div class="bt-l3" style="font-size:{sizes[2]}px">{esc(l3)}</div>')
        sid = self.slate(start, end, f'<div class="beat beat-{style}">{inner}</div>', pip=ev.get("pip", False))
        t = start + 0.1
        self.js.append(f'tl.fromTo("#{sid} .bt-label",{{opacity:0}},{{opacity:1,duration:0.3}},{q(t)});')
        if style == "strike":
            self.js.append(f'tl.fromTo("#{sid} .bt-main",{{opacity:0,x:120}},{{opacity:1,x:0,duration:0.45,ease:"back.out(1.7)"}},{q(t + 0.2)});')
            self.js.append(f'tl.fromTo("#{sid} .bt-sub .w",{{opacity:0,y:15}},{{opacity:1,y:0,duration:0.35,stagger:0.08}},{q(t + 0.7)});')
            self.js.append(f'tl.to("#{sid} .bt-strike line",{{strokeDashoffset:0,duration:0.25,ease:"power2.out"}},{q(t + 1.4)});')
        elif style == "burst":
            self.js.append(f'tl.fromTo("#{sid} .bt-num",{{opacity:0,scale:0}},{{opacity:1,scale:1.08,duration:0.55,ease:"power3.out"}},{q(t + 0.15)});')
            self.js.append(f'tl.to("#{sid} .bt-num",{{scale:1,duration:0.15}},{q(t + 0.7)});')
            self.js.append(f'tl.fromTo("#{sid} .bt-bottom",{{opacity:0,y:25}},{{opacity:1,y:0,duration:0.4}},{q(t + 0.85)});')
            for i in range(10):
                angle = i * 36
                self.js.append(f'tl.fromTo("#{sid} .bt-burst i:nth-child({i + 1})",{{opacity:1,x:0,y:0}},'
                               f'{{opacity:0,x:Math.cos({angle}*Math.PI/180)*260,y:Math.sin({angle}*Math.PI/180)*260,duration:0.6,ease:"power2.out"}},{q(t + 0.75 + i * 0.03)});')
        else:
            for k, line in enumerate(("l1", "l2", "l3")):
                self.js.append(f'tl.fromTo("#{sid} .bt-{line}",{{opacity:0,x:-100}},{{opacity:1,x:0,duration:0.42,ease:"back.out(1.6)"}},{q(t + 0.15 + k * 0.2)});')
            self.js.append(f'tl.fromTo("#{sid} .bt-slam",{{opacity:0,scaleX:0}},{{opacity:1,scaleX:1,duration:0.2,ease:"power4.out"}},{q(t + 0.95)});')
            for k, dx in enumerate((-6, 6, -3, 0)):
                self.js.append(f'tl.to("#{sid} .beat",{{x:{dx},duration:0.05,ease:"none"}},{q(t + 0.95 + k * 0.05)});')
        self.flash(start)

    def pick_zone(self):
        if not hasattr(self, "zone_rng"):
            self.zone_rng, self.zone_history = random.Random(self.clip["id"]), []
        options = ["side", "lower"]
        if self.zone_history[-2:] in (["side", "side"], ["lower", "lower"]):
            options.remove(self.zone_history[-1])   # nie trzy razy z rzędu
        zone = self.zone_rng.choice(options)
        self.zone_history.append(zone)
        return zone

    def flash(self, at):
        """Przejście przez błysk bieli (0,2 s) — jak w montażu wstawek YouTube."""
        fid = self.uid("f")
        self.html.append(f'<div class="flash clip" id="{fid}" data-start="{self.q(max(0, at - 0.1))}" data-duration="0.3" data-track-index="9"></div>')
        self.js.append(f'tl.fromTo("#{fid}",{{opacity:0}},{{opacity:0.85,duration:0.1,ease:"power2.in",yoyo:true,repeat:1}},{self.q(max(0, at - 0.1))});')

    def card_stat(self, ev, start, end):
        shown = f'{ev.get("prefix", "")}{ev["to"]}{ev.get("suffix", "")}'
        k = fit(shown, self.card_w, 260, 1, 120) / 260
        side = f'style="font-size:{int(84 * k)}px"'
        cid = self.host(start, end,
                        f'<div class="kicker">{esc(ev.get("kicker", ""))}</div>'
                        f'<div class="stat"><span class="pre" {side}>{esc(ev.get("prefix", ""))}</span>'
                        f'<span class="num" id="SID" style="font-size:{int(260 * k)}px">{ev["from"]}</span>'
                        f'<span class="suf" {side}>{esc(ev.get("suffix", ""))}</span></div>'
                        f'<div class="sub">{esc(ev.get("label", ""))}</div>', ev.get("zone", self.default_zone()))
        self.html[-1] = self.html[-1].replace('id="SID"', f'id="{cid}-num"')
        self.js.append(f'(function(){{var o={{v:{ev["from"]}}};tl.to(o,{{v:{ev["to"]},duration:{ev.get("dur", 1.2)},'
                       f'ease:"power2.out",onUpdate:function(){{var e=document.getElementById("{cid}-num");'
                       f'if(e)e.textContent=Math.round(o.v)}}}},{self.q(start + 0.3)});}})();')

    def card_compare(self, ev, start, end):
        left, right = ev["before"], ev["after"]
        cid = self.host(start, end,
                        f'<div class="kicker">{esc(ev.get("kicker", ""))}</div><div class="compare">'
                        f'<div class="side before"><span class="tag">PRZED</span><b style="font-size:{self.compare_px(left["value"])}px">{esc(left["value"])}</b><span>{esc(left["label"])}</span></div>'
                        f'<div class="arrow">{"→" if self.vertical else "↓"}</div>'
                        f'<div class="side after"><span class="tag">PO</span><b style="font-size:{self.compare_px(right["value"])}px">{esc(right["value"])}</b><span>{esc(right["label"])}</span></div></div>',
                        ev.get("zone", self.default_zone()))
        self.js.append(f'tl.fromTo("#{cid} .before",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:0.4}},{self.q(start + 0.15)});')
        self.js.append(f'tl.fromTo("#{cid} .after",{{opacity:0,x:40}},{{opacity:1,x:0,duration:0.4}},'
                       f'{self.q(self.clock.at(ev["after_at"]) if ev.get("after_at") else start + 0.9)});')
        self.js.append(f'tl.fromTo("#{cid} .before b",{{color:"{self.pal["text"]}"}},{{color:"{self.pal["danger"]}",'
                       f'textDecorationColor:"{self.pal["danger"]}",duration:0.3}},{self.q(start + 1.2)});')

    def compare_px(self, value):
        # pion: dwie kolumny po ~340 px; 16:9: karty jedna pod drugą, ~640 px
        return fit(value, 340 if self.vertical else 640, 74 if self.vertical else 90, 2 if self.vertical else 1, 40)

    def card_list(self, ev, start, end):
        # jeden rozmiar dla całej listy — punkty mają wyglądać tak samo (Mateusz 9.10);
        # długie zdanie to sygnał, że punkt trzeba skrócić do hasła
        for it in ev["items"]:
            if len(it["text"]) > 22:
                print(f"  ⚠ punkt listy „{it['text']}” ({len(it['text'])} zn.) — skróć do hasła")
        size = min(fit(it["text"], self.card_w - (200 if it.get("logo") else 140), 44 if self.vertical else 38, 1, 28)
                   for it in ev["items"])
        rows = "".join(f'<div class="li" data-i="{i}"><span class="n">{i + 1}</span>'
                       f'{logo(it["logo"], 40) if it.get("logo") else ""}<span class="t" style="font-size:{size}px">{esc(it["text"])}</span></div>'
                       for i, it in enumerate(ev["items"]))
        cid = self.host(start, end, f'<div class="kicker">{esc(ev.get("kicker", ""))}</div><div class="list">{rows}</div>',
                        ev.get("zone", self.default_zone()))
        for i, it in enumerate(ev["items"]):
            t = self.clock.at(it["at"]) if it.get("at") else start + 0.3 + i * 0.5
            self.js.append(f'tl.fromTo("#{cid} .li[data-i=\'{i}\']",{{opacity:0.22,x:-30}},{{opacity:1,x:0,duration:0.35,ease:"power3.out"}},{self.q(t)});')
            self.js.append(f'tl.to("#{cid} .li[data-i=\'{i}\'] .n",{{backgroundColor:"{self.pal["accent"]}",color:"{self.pal["on_accent"]}",duration:0.2}},{self.q(t)});')

    def card_chat(self, ev, start, end):
        app = ev.get("app", "telegram")
        msgs = "".join(f'<div class="msg {m["side"]}" data-i="{i}">{esc(m["text"])}'
                       + ('<div class="btns"><span>✓ Zatwierdź</span><span>Edytuj</span></div>' if m.get("buttons") else "")
                       + '</div>' for i, m in enumerate(ev["messages"]))
        cid = self.host(start, end,
                        f'<div class="phone"><div class="phone-head">{logo(app, 34)}<b>{esc(ev.get("bot", "Agent firmy"))}</b>'
                        f'<span>bot · online</span></div><div class="chat">{msgs}</div></div>',
                        ev.get("zone", self.default_zone()))
        for i, m in enumerate(ev["messages"]):
            t = self.clock.at(m["at"]) if m.get("at") else start + 0.4 + i * 0.9
            self.js.append(f'tl.fromTo("#{cid} .msg[data-i=\'{i}\']",{{opacity:0,y:20,scale:0.94}},'
                           f'{{opacity:1,y:0,scale:1,duration:0.35,ease:"back.out(1.7)"}},{self.q(t)});')

    def card_quote(self, ev, start, end):
        cid = self.host(start, end, f'<div class="quote" style="font-size:{fit(ev["text"] + "„”", self.card_w, 74, 4)}px">„{self.words_html(ev["text"])}”</div>'
                                    + (f'<div class="sub">{esc(ev["sub"])}</div>' if ev.get("sub") else ""),
                        ev.get("zone", self.default_zone()))
        self.stagger(f"#{cid} .quote .w", start + 0.1, 0.05, 14)

    def broll(self, ev, start, end):
        """Przebitka: w pionie zastępuje twarz (panel z kartami zostaje), w 16:9 pełny kadr.
        `full` + `src_v`: klocek animacji na cały ekran pionu (np. 9:16 z projects/flowbiz) —
        w ramce twarzy (1080×1215) zostałby obcięty."""
        src = ev.get("src_v", ev["src"]) if self.vertical else ev["src"]
        name = Path(src).name
        self.media[name] = (PROJECT / src).resolve() if not Path(src).is_absolute() else Path(src)
        if ev.get("full") and self.vertical:
            bid, start, end = self.uid("b"), self.q(start), self.q(end)
            self.slates.append((start, end))
            self.panel_busy.append((start, end))
            self.html.append(f'<div class="broll-full clip" id="{bid}" data-start="{start}" data-duration="{round(end - start, 4)}" data-track-index="8">'
                             f'<video id="{bid}-v" class="clip" src="media/{name}" muted playsinline data-start="{start}" '
                             f'data-duration="{round(end - start, 4)}" data-media-start="{ev.get("from", 0)}" data-track-index="10"></video></div>')
            self.flash(start)
            return
        bid = self.uid("b")
        start, end = self.q(start), self.q(end)
        # w ramce wideo: w pionie kurczy się razem z twarzą po hooku, w 16:9 odjeżdża pod panel boczny
        if name.lower().endswith((".jpg", ".jpeg", ".png")):
            # nieożywiony kadr (np. s08, s12) — ruch daje sam najazd Ken Burns niżej
            media = (f'<img id="{bid}-v" class="clip broll-still" src="media/{name}" alt="" data-start="{start}" '
                     f'data-duration="{round(end - start, 4)}" data-track-index="1">')
        else:
            media = (f'<video id="{bid}-v" class="clip" src="media/{name}" muted playsinline data-start="{start}" '
                     f'data-duration="{round(end - start, 4)}" data-media-start="{ev.get("from", 0)}" data-track-index="1"></video>')
        head = ""
        if ev.get("title"):
            # przebitka z nagłówkiem: dół z gradientem albo duże hasło na środku (center)
            cls = "broll-center" if ev.get("center") else "broll-head"
            size = fit(ev["title"], 1500 if not self.vertical else 900, 150 if ev.get("center") else 96, 2, 48)
            head = (f'<div class="{cls}">' + (f'<div class="kicker">{esc(ev["kicker"])}</div>' if ev.get("kicker") else "")
                    + f'<div class="broll-title" style="font-size:{size}px">{self.words_html(ev["title"])}</div></div>')
        self.broll_html.append(f'<div class="broll" id="{bid}">' + media + head
                         + (f'<div class="broll-label">{esc(ev["label"])}</div>' if ev.get("label") and not head else "") + '</div>')
        if head:
            self.js.append(f'tl.fromTo("#{bid} .broll-title .w",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.35,stagger:0.08,ease:"power3.out"}},{self.q(start + 0.25)});')
            self.cards.append((start, end, ev["title"]))   # napisy nie dublują nagłówka
        self.js.append(f'tl.set("#{bid}",{{opacity:1}},{start});tl.set("#{bid}",{{opacity:0}},{end});')
        zoom = (1.0, 1.1) if ev.get("ken", "in") == "in" else (1.1, 1.0)
        self.js.append(f'tl.fromTo("#{bid}",{{scale:{zoom[0]}}},{{scale:{zoom[1]},duration:{round(end - start, 3)},ease:"none"}},{start});')
        if ev.get("ai", True) and not self.ai_shown:
            self.ai_shown = True
            # znak AI dotyczy przebitki — nie może zostać na twarzy po jej końcu
            self.ai_until = start + min(3.2, end - start)
            self.ai_label(start, self.ai_until - start)
        if ev.get("label"):
            # podpis dopiero po znaku AI — dwa napisy u góry naraz to już natłok
            shown = max(start + 0.2, self.hook_end + 0.15, self.ai_until + 0.1)
            self.js.append(f'tl.set("#{bid} .broll-label",{{opacity:0}},0);')
            if end - shown > 0.8:
                self.js.append(f'tl.fromTo("#{bid} .broll-label",{{opacity:0,y:16}},{{opacity:1,y:0,duration:0.35}},{self.q(shown)});')

    def ai_label(self, start, dur):
        # art. 50 ust. 4 AI Act: przy pierwszej ekspozycji, u góry kadru (dół zasłania UI)
        place = "left:40px;top:318px" if self.vertical else "right:40px;top:40px"
        self.html.append(f'<div class="ai-label clip" id="{self.uid('ai')}" style="{place}" data-start="{start}" data-duration="{round(dur, 3)}" data-track-index="5">'
                         f'<span class="ai-dot">AI</span>Ujęcie wygenerowane przez AI</div>')

    # ── stałe warstwy formatu ───────────────────────────────────────────────
    def hook(self):
        hook = self.board.get("hook")
        if not hook or self.fmt == "youtube":
            return
        end = max(self.clock.at(hook.get("until", 3.0), floor=0), self.cover_end + 2.5)
        self.hook_end = end
        parts = sentences(hook["text"])
        times = self.sentence_times(parts, self.cover_end, end)
        # jeden rozmiar dla wszystkich zdań — bez przeskoku fontu przy zmianie
        size = min(fit(p, 830, 76, 3, 52) for p in parts)
        accent = hook.get("accent", [])
        cid = self.uid("h")
        # zdania leżą w jednej komórce siatki: karta ma wysokość najdłuższego, nic nie skacze
        text = "".join(f'<div class="hook-sent">{self.words_html(p, accent=accent)}</div>' for p in parts)
        self.hook_words = {norm(w) for w in hook["text"].replace("*", "").split() if len(norm(w)) >= 4}
        visual = self.hook_visual(hook.get("visual"))
        self.html.append(f'<div class="hook clip" id="{cid}" data-start="{self.q(self.cover_end)}" data-duration="{self.q(end - self.cover_end)}" data-track-index="4">'
                         f'<div class="hook-in">{visual}<div class="hook-text" style="font-size:{size}px">{text}</div></div></div>')
        self.js.append(f'tl.fromTo("#{cid} .hook-in",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.4,ease:"power3.out"}},{self.q(self.cover_end + 0.05)});')
        if visual:
            self.js.append(f'tl.fromTo("#{cid} .hv-pop",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.45,ease:"back.out(1.8)",stagger:0.22}},{self.q(self.cover_end + 0.2)});')
            self.js.extend(js.replace("#ID", f"#{cid}") for js in self.hook_visual_js(hook.get("visual"), end))
        for i, start in enumerate(times[:-1]):
            sel = f"#{cid} .hook-sent:nth-child({i + 1})"
            if i:
                self.js.append(f'tl.set("{sel}",{{opacity:0}},{self.q(self.cover_end)});')
                self.js.append(f'tl.to("#{cid} .hook-sent:nth-child({i})",{{opacity:0,duration:0.15}},{self.q(start - 0.15)});')
                self.js.append(f'tl.set("{sel}",{{opacity:1}},{self.q(start)});')
            self.js.append(f'tl.fromTo("{sel} .w",{{opacity:0.25}},{{opacity:1,duration:0.2,stagger:0.07}},{self.q(start + 0.15)});')
        self.js.append(f'tl.to("#{cid} .hook-in",{{opacity:0,duration:0.25}},{self.q(end - 0.25)});')

    def hook_visual(self, visual):
        """Grafika nad zdaniem hooka: ikona, A vs B, przepływ, logo narzędzi albo licznik."""
        if not visual:
            return ""
        kind = visual["kind"]
        if kind == "icon":
            return f'<div class="hv">{self.hook_item(visual)}</div>'
        if kind == "logos":
            return '<div class="hv">' + "".join(self.hook_item({"logo": name}) for name in visual["items"]) + '</div>'
        if kind == "meter":
            return (f'<div class="hv hv-meter hv-pop"><div class="hv-bar"><i style="width:{visual["from"]}%"></i></div>'
                    f'<b class="hv-val">{visual["from"]}{esc(visual.get("suffix", ""))}</b></div>')
        sign = visual.get("sign", "vs" if kind == "versus" else "→")
        items = [visual["left"], visual["right"]] if kind == "versus" else visual["items"]
        # etykieta, która powtarza słowo z hooka, to drugi raz ten sam tekst — wtedy
        # wypadają wszystkie (pół schematu z podpisem, pół bez wygląda na błąd)
        if any({norm(w) for w in it.get("label", "").split()} & self.hook_words for it in items):
            items = [dict(it, label="") for it in items]
        joiner = f'<span class="hv-sign hv-pop">{esc(sign)}</span>'
        return '<div class="hv">' + joiner.join(self.hook_item(it) for it in items) + '</div>'

    def hook_item(self, item):
        if item.get("art"):
            self.media[f'{item["art"]}.png'] = PROJECT / "assets" / "hook-art" / f'{item["art"]}.png'
            pic = f'<img class="hv-img" src="media/{item["art"]}.png" alt="">'
        else:
            pic = f'<span class="hv-logo">{logo(item["logo"], 150, LOGO_COLORS.get(item["logo"]))}</span>'
        label = (f'<span class="hv-label{" acc" if item.get("accent") else ""}{" strike" if item.get("strike") else ""}">'
                 f'{esc(item["label"])}</span>') if item.get("label") else ""
        return f'<div class="hv-item hv-pop">{pic}{label}</div>'

    def hook_visual_js(self, visual, end):
        """Licznik dobiega do wartości docelowej w pierwszej połowie hooka."""
        if not visual or visual["kind"] != "meter":
            return []
        a, b, suffix = visual["from"], visual["to"], visual.get("suffix", "")
        run = self.q(min(2.0, end / 2))
        return [f'tl.to("#ID .hv-bar i",{{width:"{b}%",duration:{run},ease:"power2.inOut"}},0.6);',
                f'(function(){{var o={{v:{a}}},el=document.querySelector("#ID .hv-val");'
                f'tl.to(o,{{v:{b},duration:{run},ease:"power2.inOut",onUpdate:function(){{el.textContent=Math.round(o.v)+"{suffix}";}}}},0.6);}})();']

    def sentence_times(self, parts, start, end):
        """Kiedy pokazać kolejne zdanie: gdy pada jego pierwsze słowo; gdy go nie słychać
        (tekst przepisany inaczej niż mowa), podział proporcjonalny do długości."""
        total = sum(len(p) for p in parts)
        times, done = [start], 0
        for prev, part in zip(parts, parts[1:]):
            done += len(prev)
            guess = start + (end - start) * done / total
            try:
                spoken = self.clock.at(norm(part.split()[0].lstrip("*")), floor=times[-1] + 0.6)
            except SystemExit:
                spoken = None
            ok = spoken is not None and times[-1] + 0.8 <= spoken <= end - 0.8
            times.append(spoken - 0.05 if ok else guess)
        return times + [end]

    def captions(self):
        if not self.vertical:
            return
        lines, cur = [], []
        for w in self.words:
            text = " ".join(x["word"] for x in cur + [w])
            if cur and (len(text) > 26 or w["start"] - cur[-1]["end"] > 0.6):
                lines.append(cur)
                cur = []
            cur.append(w)
            if re.search(r"[.?!]$", w["word"]):
                lines.append(cur)
                cur = []
        if cur:
            lines.append(cur)
        blocked = self.caption_blocks(lines)
        for i, line in enumerate(lines):
            start = self.q(line[0]["start"] - 0.05)
            end = self.q(lines[i + 1][0]["start"] - 0.05) if i + 1 < len(lines) else self.q(min(line[-1]["end"] + 0.6, self.clip_len))
            end = min(end, self.q(line[-1]["end"] + 1.2))
            for a, b in blocked:
                if a - 0.05 <= start < b:
                    start = b
                elif start < a < end:
                    end = a
            if end - start < 0.3:
                continue
            cid = self.uid("cap")
            spans = "".join(f'<span class="cw" id="{cid}-{k}">{esc(w["word"])}</span> ' for k, w in enumerate(line))
            self.html.append(f'<div class="cap clip" id="{cid}" data-start="{start}" data-duration="{round(end - start, 4)}" '
                             f'data-track-index="6"><div class="cap-in">{spans}</div></div>')
            for k, w in enumerate(line):
                self.js.append(f'tl.set("#{cid}-{k}",{{color:"{self.pal["accent"]}"}},{self.q(w["start"])});')

    def caption_blocks(self, lines):
        """Kiedy napisów nie ma: pod hookiem, pod planszą i pod kartą, która powtarza wypowiedź."""
        blocked = [(0.0, self.hook_end)] if self.hook_end else []
        blocked += self.slates
        for a, b, text in self.cards:
            said = {norm(w["word"]) for line in lines for w in line if a <= w["start"] < b}
            shown = {norm(w) for w in text.split()}
            if {w for w in said & shown if len(w) >= 4}:
                blocked.append((a, b))
        return sorted(blocked)

    def cta_chip(self):
        if self.fmt != "ad":
            return
        cta = self.board.get("cta", {})
        text = cta.get("chip", self.brand["web"])
        # dwa okna zamiast stałej obecności: po hooku i na finiszu
        first = self.q(max(5.0, self.hook_end + 3.0))
        last = self.q(max(first + 5.5, self.clip_len - 6.0))
        windows = [(first, min(first + 5.0, last)), (last, self.clip_len)] if last - first > 6 else [(first, self.clip_len)]
        # końcówka po „·” przewija miejscowości i kończy na adresie strony
        prefix = text.split(" · ")[0]
        cycle = cta.get("chip_cycle", self.brand["places"] + [self.brand["web"]])
        for a, b in windows:
            if b - a < 1.0:
                continue
            cid = self.uid("chip")
            words = "".join(f'<span class="chip-w" data-i="{i}">{esc(w)}</span>' for i, w in enumerate(cycle))
            self.html.append(f'<div class="cta-chip clip" id="{cid}" data-start="{a}" '
                             f'data-duration="{self.q(b - a)}" data-track-index="5">'
                             f'<span class="chip-dot"></span>{esc(prefix)} ·<span class="chip-cycle">{words}</span></div>')
            self.js.append(f'tl.fromTo("#{cid}",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.35,ease:"power3.out"}},{a});')
            step = min(1.1, (b - a - 0.4) / len(cycle))
            for i in range(len(cycle)):
                t = self.q(a + 0.2 + i * step)
                self.js.append(f'tl.fromTo("#{cid} .chip-w[data-i=\'{i}\']",{{opacity:0,y:18}},{{opacity:1,y:0,duration:0.22,ease:"power2.out"}},{t});')
                if i < len(cycle) - 1:
                    self.js.append(f'tl.to("#{cid} .chip-w[data-i=\'{i}\']",{{opacity:0,y:-18,duration:0.2,ease:"power2.in"}},{self.q(t + step - 0.2)});')

    def end_title(self, text):
        return f'<div class="end-title" style="font-size:{fit(text, 900, 124, 3, 72)}px">{self.words_html(text)}</div>'

    def endcard(self):
        if not self.end_len:
            return
        cta = self.board.get("cta", {})
        start = self.clip_len
        cid = self.uid("end")
        if self.fmt == "youtube":
            body = f'<div class="end-sub end-tag">{esc(self.brand["tagline"])} · {esc(self.brand["web"])}</div>'
        elif self.fmt == "feed":
            # zajawka: zaproszenie do pełnego odcinka z oryginalnym logo YouTube
            body = (f'<div class="end-yt">{logo("youtube", 120, "#FF0000")}<span>Cały odcinek na YouTube</span></div>'
                    + self.end_title(self.board.get("episode_title", "Obejrzyj cały odcinek")) +
                    f'<div class="end-sub">kanał flowbiz · Mateusz Kozłowski</div>')
        elif self.fmt == "ad":
            lines = cta.get("ad", {})
            body = (f'<div class="end-kicker">{esc(lines.get("kicker", "Bezpłatna konsultacja"))}</div>'
                    + self.end_title(lines.get("title", "Przyjadę do Twojej firmy")) +
                    f'<div class="end-sub">{esc(lines.get("sub", "Słupsk · Pomorze · Zachodniopomorskie"))}</div>'
                    f'<div class="end-btn">{esc(lines.get("button", self.brand["web"]))}</div>'
                    f'<div class="end-phone">tel. {esc(self.brand["phone"])}</div>')
        else:
            lines = cta.get("reels", {})
            body = (f'<div class="end-kicker">{esc(lines.get("kicker", "Chcesz to u siebie?"))}</div>'
                    + self.end_title(lines.get("title", "Napisz „AGENT” w komentarzu")) +
                    f'<div class="end-sub">{esc(lines.get("sub", "Wyślę Ci materiał, jak zacząć"))}</div>')
        cutout = ""
        if self.brand.get("cutout"):
            # sylwetka z ratuszem jak na aislupsk.pl — prawdziwe zdjęcie, nie AI
            self.media[self.brand["cutout"]] = BRAND / "aislupsk" / self.brand["cutout"]
            cutout = f'<img class="end-cutout" src="media/{self.brand["cutout"]}" alt="">'
        self.html.append(f'<div class="endcard clip{" end-cut" if cutout else ""}" id="{cid}" data-start="{self.q(start)}" data-duration="{self.q(self.end_len)}" '
                         f'data-track-index="7"><div class="end-grid"></div>{cutout}<div class="end-stack">'
                         f'<div class="end-mark">{self.brand_mark()}</div><div class="end-body">{body}</div></div></div>')
        self.js.append(f'tl.fromTo("#{cid} .end-mark",{{opacity:0,scale:0.9}},{{opacity:1,scale:1,duration:0.6,ease:"power3.out"}},{self.q(start)});')
        self.js.append(f'tl.fromTo("#{cid} .end-body > *",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.45,stagger:0.12,ease:"power3.out"}},{self.q(start + 0.1)});')
        if self.fmt == "ad":
            self.js.append(f'tl.fromTo("#{cid} .end-btn",{{scale:1}},{{scale:1.05,duration:0.5,yoyo:true,repeat:3,ease:"sine.inOut"}},{self.q(start + 0.9)});')

    def yt_badge(self):
        """Zajawka: znaczek „Cały odcinek na YouTube” od końca hooka do planszy końcowej."""
        if self.fmt != "feed":
            return
        start = self.q(max(self.hook_end or 0, 1.0) + 0.3)
        cid = self.uid("yt")
        self.html.append(f'<div class="yt-badge clip" id="{cid}" data-start="{start}" data-duration="{self.q(self.clip_len - start)}" data-track-index="5">'
                         f'{logo("youtube", 34, "#FF0000")}<span>Cały odcinek na YouTube</span></div>')
        self.js.append(f'tl.fromTo("#{cid}",{{opacity:0,y:-14}},{{opacity:1,y:0,duration:0.4,ease:"power3.out"}},{start});')

    def lower_third(self):
        if self.fmt != "youtube" or self.board.get("lower_third") is False:
            return
        cid = self.uid("lt")
        self.html.append(f'<div class="lower-third clip" id="{cid}" data-start="0.6" data-duration="4.2" data-track-index="5">'
                         f'<b>Mateusz Kozłowski</b><span>{esc(self.brand["mark"])} · {esc(self.brand["tagline"])}</span></div>')
        self.js.append(f'tl.fromTo("#{cid}",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:0.5,ease:"power3.out"}},0.6);')
        self.js.append(f'tl.to("#{cid}",{{opacity:0,duration:0.3}},4.5);')

    def intro(self):
        """Pion: pod hookiem twarz na całym ekranie, potem odjazd i wjazd dolnego panelu."""
        if not (self.vertical and self.hook_end):
            return
        g, t = self.geo, self.q(self.hook_end - 0.1)
        self.js.insert(0, f'tl.set("#video-wrap",{{height:{g["h"]}}},0);tl.set("#panel",{{y:{g["h"] - g["face_h"]}}},0);')
        self.js.append(f'tl.to("#video-wrap",{{height:{g["face_h"]},duration:0.7,ease:"power3.inOut"}},{t});')
        self.js.append(f'tl.to("#panel",{{y:0,duration:0.7,ease:"power3.inOut"}},{t});')

    def zooms(self):
        """Ruch kamery na twarzy: plan zmienia się skokiem na każdej sklejce (maskuje
        wycięte pauzy) i co kilka zdań, a między cięciami obraz powoli dryfuje.
        Pod hookiem mniejsze skoki — twarz na pełnym ekranie jest już mocno powiększona."""
        splices = json.load(open(self.splices_file)) if self.splices_file.exists() else []
        marks = [(t, "cut") for t in splices if 0.3 < t < self.clip_len - 0.3]
        last = 0.0
        for prev, w in zip(self.words, self.words[1:]):
            if w["start"] - last >= 3.0 and re.search(r"[.?!]$", prev["word"]):
                marks.append((w["start"] - 0.04, "sentence"))
                last = w["start"]
        if self.hook_end:
            marks.append((self.hook_end - 0.1, "hook"))
        marks.sort()
        bounds = [(0.0, "start")]
        for t, kind in marks:
            if t - bounds[-1][0] < 0.9:
                if kind in ("cut", "hook"):        # sklejka i koniec hooka mają pierwszeństwo
                    bounds[-1] = (max(t, bounds[-1][0]), kind) if bounds[-1][1] != "start" else bounds[-1]
                continue
            bounds.append((t, kind))
        bounds.append((self.clip_len, "end"))
        # 16:9: pełny kadr źródła pokazuje brzeg monitora i kable z lewej (Mateusz 10.10:
        # „nie może tego być w ogóle”) — baza +10%, środek przybliżenia na twarzy
        base = 1.0 if self.vertical else 1.10
        self.js.append(f'tl.set("#face-zoom",{{scale:{base}}},0);')
        close = False
        for (t0, kind), (t1, _) in zip(bounds, bounds[1:]):
            t0, t1 = self.q(t0), self.q(t1)
            in_hook = self.hook_end and t0 < self.hook_end - 0.2
            close = not close if kind != "start" else False
            near = 1.06 if in_hook else 1.13
            scale = round(base * (near if close else 1.0), 3)
            span = round(t1 - t0 - 0.04, 3)
            if span <= 0.1:
                continue
            if kind == "hook":   # odjazd razem z wjazdem panelu, potem dryf
                scale, close = base, False
                self.js.append(f'tl.to("#face-zoom",{{scale:{base},duration:0.7,ease:"power3.inOut"}},{t0});')
                if span > 0.8:
                    self.js.append(f'tl.to("#face-zoom",{{scale:{round(base * 1.03, 3)},duration:{round(span - 0.72, 3)},ease:"none"}},{self.q(t0 + 0.72)});')
                continue
            self.js.append(f'tl.fromTo("#face-zoom",{{scale:{scale}}},{{scale:{round(scale + 0.03, 3)},duration:{span},ease:"none"}},{t0});')

    def fill_panel_gaps(self):
        """Pion: w lukach między kartami panel nie stoi pusty — wraca karta tematu."""
        topic = self.board.get("topic")
        if not self.vertical or not topic:
            return
        busy = sorted(self.panel_busy)
        cursor, gaps = self.panel_from(), []
        for a, b in busy + [(self.clip_len, self.clip_len)]:
            if a - cursor >= 1.5:
                gaps.append((cursor, a))
            cursor = max(cursor, b)
        for a, b in gaps:
            self.card_title(dict(topic, zone="panel"), a + (0.05 if a else 0.0), b)

    def panel_from(self):
        return self.hook_end + 0.5 if self.vertical and self.hook_end else 0.0

    def default_zone(self):
        return "panel" if self.vertical else "side"

    def words_html(self, text, accent=()):
        out = []
        for word in tokens(text):
            cls = "w acc" if norm(word) in [norm(a) for a in accent] or word.startswith("*") else "w"
            out.append(f'<span class="{cls}">{esc(word.lstrip("*"))}</span>')
        return " ".join(out)

    # ── składanie ───────────────────────────────────────────────────────────
    def build(self):
        hook = self.board.get("hook")
        self.cover_end = self.board.get("cover", {}).get("dur", 2.2) if self.board.get("cover") else 0.0
        if hook and self.fmt != "youtube":
            self.hook_end = max(self.clock.at(hook.get("until", 3.0), floor=0), self.cover_end + 2.5)
            if self.hook_end > 4.0 * max(2, len(sentences(hook["text"]))):   # ~4 s na zdanie
                print(f"  ⚠ hook trwa {self.hook_end:.1f} s — skróć `until`")
            elif self.hook_end < 2.5:   # po wycięciu „yyy” kotwica potrafi wypaść za wcześnie
                print(f"  ⚠ hook trwa tylko {self.hook_end:.1f} s — przesuń `until`")
        self.base()
        self.cover()
        for ev in self.board["events"]:
            if self.fmt in ev.get("skip", []):
                continue
            start = self.clock.at(ev["at"], floor=ev.get("floor", self.clock.cursor))
            self.clock.cursor = start
            end = self.clock.at(ev["until"], base=start) if "until" in ev else start + ev.get("dur", 3.0)
            end = min(end, self.clip_len)
            if end - start < 0.5:
                raise SystemExit(f"zdarzenie {ev['type']} @ {ev['at']}: {start:.2f}–{end:.2f} — za krótkie")
            if ev["type"] not in ("broll", "logos", "slate", "mockup", "beat") and ev.get("zone", self.default_zone()) == "panel":
                start = max(start, self.panel_from())   # panel wjeżdża dopiero po hooku
                if end - start < 0.8:
                    continue
            # 16:9 ma kilka układów: panel boczny (700 px), pasek dolny na twarzy (1000 px).
            # Tytuł/cytat bez wskazanej strefy losuje układ (powtarzalnie, ziarno = klip),
            # żeby odcinek nie jechał w kółko tym samym (Mateusz 10.10: „nie raz losowo”)
            if not self.vertical and ev["type"] in ("title", "quote") and "zone" not in ev:
                ev = dict(ev, zone=self.pick_zone())
            self.card_w = 1000 if ev.get("zone") == "lower" else (888 if self.vertical else 700)
            getattr(self, "broll" if ev["type"] == "broll" else f"card_{ev['type']}")(ev, start, end)
        self.fill_panel_gaps()
        self.emit_side_windows()
        self.intro()
        self.zooms()
        self.hook()
        self.captions()
        self.cta_chip()
        self.yt_badge()
        self.lower_third()
        self.endcard()
        return self.document()

    def document(self):
        g, p = self.geo, self.pal
        from mockups import MOCKUP_STYLE
        css = (BRAND / "fonts" / "fonts.css").read_text() + logos_css() + (STYLE + MOCKUP_STYLE).format(
            W=g["w"], H=g["h"], FH=g["face_h"], SW=900 if self.vertical else 1500, EL=640 if self.vertical else 1000, ST=282 if self.vertical else 330, SF=110 if self.vertical else 120, LBL=404 if self.vertical else 60, PH=g["h"] - g["face_h"], CHIP=g["face_h"] - 250, CUT=760 if self.vertical else 900, **p,
            V="1" if self.vertical else "0")
        cls = ("fmt-v" if self.vertical else "fmt-h") + f" fmt-{self.fmt}"
        return (f'<!doctype html><html lang="pl"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width={g["w"]}, height={g["h"]}"><style>{css}</style></head>'
                f'<body><div id="root" class="{cls}" data-composition-id="pack" data-start="0" data-width="{g["w"]}" '
                f'data-height="{g["h"]}" data-duration="{self.total}">{"".join(self.html).replace("<!--BROLL-->", "".join(self.broll_html))}</div>'
                f'<script src="vendor/gsap.min.js"></script><script>'
                f'var tl=gsap.timeline({{paused:true}});{"".join(self.js)}window.__timelines["pack"]=tl;</script></body></html>')


STYLE = """
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:100%;height:100%;overflow:hidden;background:{bg};color:{text};font-family:'{font}',sans-serif;-webkit-font-smoothing:antialiased}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;background:{bg}}}
#video-wrap{{position:absolute;overflow:hidden;background:#000;z-index:1}}
#face-zoom{{position:absolute;inset:0}}
#video-wrap video,#video-wrap .broll-still{{width:100%;height:100%;object-fit:cover;display:block}}
.face-fade{{position:absolute;left:0;right:0;bottom:0;height:260px;background:linear-gradient(180deg,rgba(0,0,0,0),{bg})}}
#panel{{position:absolute;left:0;width:{W}px;background:{bg};overflow:hidden;z-index:2}}
.panel-grid{{position:absolute;inset:0;background-image:linear-gradient({grid} 1px,transparent 1px),linear-gradient(90deg,{grid} 1px,transparent 1px);background-size:54px 54px}}
.panel-rule{{position:absolute;left:0;top:0;height:6px;width:100%;background:{accent}}}
.brand-mark{{position:absolute;right:40px;top:236px;padding:10px 16px;border-radius:14px;background:rgba(0,0,0,.6)}}
.mark-img{{height:44px;display:block}}
.mark-text{{font-size:30px;font-weight:700;letter-spacing:.02em;color:{text}}}
.mark-text b{{color:{accent}}}
#side-plate{{position:absolute;right:0;top:0;width:800px;height:{H}px;background:{bg};border-left:6px solid {accent};z-index:2}}

.card-host{{position:absolute;pointer-events:none;z-index:3;overflow:hidden}}
.brand-mark,.cta-chip,.lower-third{{z-index:5}} .cap,.hook,.ai-label{{z-index:6}} .endcard{{z-index:9}}
.zone-panel{{left:44px;right:132px;top:{FH}px;height:500px;padding-top:46px}}
.zone-side{{right:40px;top:90px;width:700px;height:900px;display:flex;align-items:center}}
.zone-full{{inset:0}}
.callout{{font-weight:900;line-height:.92;letter-spacing:-.03em;text-transform:uppercase;color:{text};text-align:center;font-style:{heading_style}}}
.callout .w{{display:block}} .callout .acc{{color:{accent}}}
.fmt-feed .hook{{bottom:90px}} .fmt-feed .hv{{min-height:170px}} .fmt-feed .hv-img,.fmt-feed .hv-logo{{width:170px;height:170px}}
.yt-badge{{position:absolute;left:32px;top:32px;display:flex;align-items:center;gap:12px;padding:10px 18px 10px 14px;border-radius:40px;background:rgba(0,0,0,.72);color:#fff;font-size:26px;font-weight:700;z-index:6}}
.end-yt{{display:flex;align-items:center;gap:22px;font-size:40px;font-weight:800;color:{text}}}
.flash{{position:absolute;inset:0;background:#fff;opacity:0;z-index:10;pointer-events:none}}
.broll-full{{position:absolute;inset:0;z-index:7;background:#000}} .broll-full video{{width:100%;height:100%;object-fit:cover}}
.beat{{position:relative;width:100%;text-align:center;display:flex;flex-direction:column;align-items:center;gap:26px}}
.bt-label{{font-size:34px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:{accent}}}
.bt-main,.bt-num,.bt-l1,.bt-l3{{font-weight:900;line-height:1;letter-spacing:-.03em}}
.bt-acc,.bt-num{{color:{accent}}} .bt-l1{{color:{text}}} .bt-l2{{font-weight:700;color:{muted}}} .bt-l3{{color:{danger}}}
.bt-sub{{font-size:48px;font-weight:600;color:{muted};display:flex;gap:18px}} .bt-sub .w{{display:inline-block}}
.bt-strike{{position:absolute;inset:0;width:100%;height:100%;overflow:visible}} .bt-strike line{{stroke:{danger};stroke-width:10;stroke-linecap:round}}
.bt-num{{position:relative;filter:drop-shadow(0 0 70px {accent}55)}}
.bt-burst{{position:absolute;left:50%;top:50%;width:0;height:0}} .bt-burst i{{position:absolute;left:-7px;top:-7px;width:14px;height:14px;border-radius:50%;background:{accent};opacity:0}}
.bt-bottom{{font-size:46px;font-weight:600;color:{text}}}
.beat-slam{{align-items:flex-start;text-align:left;gap:10px}}
.bt-slam{{width:100%;height:8px;background:{danger};transform-origin:left center}}
.zone-lower{{left:70px;bottom:70px;width:1140px}}
.zone-lower .card{{background:{bg}F0;padding:30px 40px 34px;border-radius:26px;border-left:8px solid {accent};box-shadow:0 18px 50px rgba(0,0,0,.45)}}
.broll-head{{position:absolute;left:0;right:0;bottom:0;padding:180px 80px 70px;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.82))}}
.broll-center{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 120px;background:radial-gradient(circle,rgba(0,0,0,.55),rgba(0,0,0,.25))}}
.broll-head .kicker,.broll-center .kicker{{display:inline-block;background:{bg}E6;padding:8px 16px;border-radius:10px;letter-spacing:.12em}}
.fmt-h .kicker{{font-size:34px;letter-spacing:.12em}}
.broll-title{{font-weight:800;line-height:1.04;letter-spacing:-.02em;color:#fff;text-shadow:0 4px 30px rgba(0,0,0,.6)}}
.broll-title .w{{display:inline-block}} .broll-title .acc{{color:{accent}}}
#video-wrap{{transform-origin:100% 100%}}
.slate.pip .slate-body{{width:1240px;margin-right:560px}}
.card{{width:100%;color:{text}}}
.fmt-v .card{{padding:0 8px}}
.kicker{{font-size:30px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:{accent};margin-bottom:18px}}
.title{{font-size:92px;font-weight:800;line-height:1.02;letter-spacing:-.02em}}
.fmt-h .title{{font-size:76px}}
.fmt-h .msg{{font-size:32px}}
.fmt-h .li{{font-size:38px}}
.fmt-h .logo-tile{{min-width:200px}}
.title .w,.quote .w,.hook-in .w,.end-title .w{{display:inline-block}}
.acc{{color:{accent}}}
.sub{{font-size:38px;color:{muted};margin-top:20px;line-height:1.3;font-weight:500}}

.logo-row{{display:flex;gap:22px;flex-wrap:wrap}}
.logo-tile{{overflow:hidden;background:{panel};border:2px solid {line};border-radius:30px;padding:30px 26px 22px;display:flex;flex-direction:column;align-items:center;gap:16px;min-width:262px}}
.logo-tile.wide{{flex-basis:100%;width:auto;justify-content:center}}
.logo-tile span{{font-size:32px;font-weight:700;color:{text}}}
.fmt-h .logo-tile{{min-width:190px}}

.stat{{display:flex;align-items:baseline;gap:10px;font-weight:800;line-height:1}}
.stat .num{{font-size:260px;color:{accent};letter-spacing:-.04em}}
.stat .pre,.stat .suf{{font-size:84px}}

.compare{{display:flex;align-items:center;gap:22px}}
.fmt-h .compare{{flex-direction:column;align-items:stretch;gap:12px}}
.fmt-h .compare .arrow{{text-align:center;line-height:1}}
.compare .side{{flex:1;min-width:0;background:{panel};border:2px solid {line};border-radius:28px;padding:26px;display:flex;flex-direction:column;gap:6px}}
.compare .after{{border-color:{accent}}}
.compare .tag{{font-size:22px;font-weight:800;letter-spacing:.14em;color:{muted}}}
.compare .after .tag{{color:{accent}}}
.compare b{{font-size:74px;line-height:1.02;font-weight:800;overflow-wrap:normal}}
.compare .before b{{text-decoration:line-through;text-decoration-thickness:6px;text-decoration-color:transparent}}
.compare span{{font-size:26px;color:{muted}}}
.compare .arrow{{font-size:60px;color:{accent};font-weight:800}}

.list{{display:flex;flex-direction:column;gap:14px}}
.li{{display:flex;align-items:center;gap:22px;background:{panel};border:2px solid {line};border-radius:24px;padding:20px 26px;font-size:44px;font-weight:700}}
.li .n{{width:62px;height:62px;border-radius:50%;background:{raised};display:flex;align-items:center;justify-content:center;font-size:32px;flex:none}}

.phone{{background:{panel};border:2px solid {line};border-radius:34px;overflow:hidden;width:100%}}
.phone-head{{display:flex;align-items:center;gap:16px;padding:20px 28px;background:{raised};font-size:34px}}
.phone-head span{{font-size:26px;color:{muted};margin-left:auto}}
.chat{{padding:24px 26px;display:flex;flex-direction:column;gap:16px}}
.msg{{max-width:86%;padding:18px 24px;border-radius:26px;font-size:38px;line-height:1.25;font-weight:500}}
.msg.me{{align-self:flex-end;background:{accent};color:{on_accent};border-bottom-right-radius:6px}}
.msg.bot{{align-self:flex-start;background:{raised};border-bottom-left-radius:6px}}
.btns{{display:flex;gap:10px;margin-top:12px}}
.btns span{{font-size:32px;font-weight:700;padding:10px 22px;border-radius:14px;border:2px solid {accent};color:{accent}}}
.btns span:first-child{{background:{accent};color:{on_accent}}}

/* pion: panel ma 500 px — lista i czat w wersji zwartej */
.fmt-v .list{{gap:10px}}
.fmt-v .li{{padding:13px 22px;gap:18px}}
.fmt-v .li .n{{width:54px;height:54px;font-size:28px}}
.fmt-v .phone-head{{padding:14px 24px;font-size:30px}}
.fmt-v .chat{{padding:16px 20px;gap:12px}}
.fmt-v .msg{{font-size:33px;padding:14px 20px;max-width:92%}}
.fmt-v .btns span{{font-size:28px;padding:8px 18px}}
.fmt-h .card{{padding-right:12px}}
.quote{{font-size:74px;font-weight:800;line-height:1.08;letter-spacing:-.01em}}

.broll{{position:absolute;inset:0;overflow:hidden;opacity:0;transform-origin:50% 50%}}
.broll video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.broll-label{{position:absolute;left:40px;top:{LBL}px;font-size:34px;font-weight:700;padding:10px 18px;border-radius:12px;background:{bg};color:{text};border-left:6px solid {accent}}}

.ai-label{{position:absolute;display:flex;align-items:center;gap:12px;font-size:24px;font-weight:600;padding:10px 18px 10px 10px;border-radius:40px;background:rgba(0,0,0,.62);color:#fff}}
.ai-dot{{background:#fff;color:#000;font-weight:800;font-size:20px;padding:4px 10px;border-radius:20px}}

.hook{{position:absolute;left:44px;right:132px;bottom:430px}}
.hook-in{{display:flex;flex-direction:column;gap:22px;font-weight:800;line-height:1.06;letter-spacing:-.02em;color:{text};background:{bg}F2;padding:30px 34px 32px;border-radius:30px;border-left:8px solid {accent};box-shadow:0 18px 50px rgba(0,0,0,.45)}}
.hook-text{{display:grid}} .hook-sent{{grid-area:1/1}}
.hv{{display:flex;align-items:center;justify-content:center;gap:26px;min-height:230px}}
.hv-item{{display:flex;flex-direction:column;align-items:center;gap:10px}}
.hv-img{{width:220px;height:220px;object-fit:contain;mix-blend-mode:lighten;-webkit-mask-image:radial-gradient(circle,#000 52%,transparent 71%);mask-image:radial-gradient(circle,#000 52%,transparent 71%)}}
.hv-logo{{display:flex;align-items:center;justify-content:center;width:220px;height:220px;border-radius:48px;background:{raised}}}
.hv-label{{font-size:38px;font-weight:800;color:{muted}}} .hv-label.acc{{color:{accent}}} .hv-label.strike{{text-decoration:line-through;text-decoration-thickness:5px}}
.hv-sign{{font-size:64px;font-weight:800;color:{accent}}}
.hv-meter{{flex-direction:column;gap:14px;align-items:stretch;width:100%}}
.hv-bar{{height:44px;border-radius:22px;background:{raised};overflow:hidden}} .hv-bar i{{display:block;height:100%;background:{accent};border-radius:22px}}
.hv-val{{font-size:120px;line-height:1;color:{accent};text-align:center}}
.hook-in .acc{{color:{accent}}}
.slate{{position:absolute;inset:0;background:{bg};display:flex;align-items:center;justify-content:center;z-index:7}}
.slate-body{{position:relative;width:{SW}px;display:flex;flex-direction:column;gap:10px}}
.slate-text{{font-size:{SF}px;font-weight:800;line-height:1.04;letter-spacing:-.02em}}
.slate-text .w{{display:inline-block}}
.slate-body{{align-items:center;text-align:center}}
.slate .kicker{{font-size:40px;margin-bottom:34px}}
.slate .logo-row{{gap:26px;justify-content:center;flex-wrap:wrap}}
.slate .logo-tile{{min-width:0;width:{ST}px;padding:46px 20px 32px;gap:24px}}
.slate .logo-tile span{{font-size:38px}}
.slate .sub{{margin-top:40px}}

.cap{{position:absolute;left:40px;right:40px;top:{FH}px;transform:translateY(-150px);display:flex;justify-content:center}}
.cap-in{{font-size:52px;font-weight:800;text-align:center;line-height:1.12;color:#fff;background:rgba(0,0,0,.72);padding:10px 22px;border-radius:16px}}

.cta-chip{{position:absolute;left:40px;top:{CHIP}px;display:flex;align-items:center;gap:14px;font-size:30px;font-weight:700;padding:14px 24px;border-radius:40px;background:{accent};color:{on_accent}}}
.chip-cycle{{display:inline-grid;overflow:hidden;padding:8px 0;margin:-8px 0}}
.chip-w{{grid-area:1/1;opacity:0}}
.chip-dot{{width:14px;height:14px;border-radius:50%;background:{on_accent}}}

.lower-third{{position:absolute;left:70px;bottom:80px;display:flex;flex-direction:column;gap:4px;padding:18px 28px;background:{bg};border-left:8px solid {accent};border-radius:6px}}
.lower-third b{{font-size:40px}}
.lower-third span{{font-size:26px;color:{muted}}}

.endcard{{position:absolute;inset:0;background:{bg_fill};display:flex;align-items:center;justify-content:center}}
.end-cutout{{position:absolute;right:-30px;bottom:0;width:{CUT}px;height:auto}}
.fmt-v .end-cut{{align-items:flex-start;padding-top:170px}}
.fmt-h .end-cut .end-stack{{width:56%;margin-right:38%;align-items:flex-start}}
.hook-in,.title,.end-title,.slate-text,.quote,.end-mark .mark-text{{font-style:{heading_style};word-spacing:{word_gap}}}
.end-grid{{position:absolute;inset:0;background-image:linear-gradient({grid} 1px,transparent 1px),linear-gradient(90deg,{grid} 1px,transparent 1px);background-size:60px 60px}}
.end-stack{{position:relative;width:86%;display:flex;flex-direction:column;gap:70px}}
.fmt-h .end-stack{{align-items:center;gap:40px}}
.end-mark .mark-img{{width:{EL}px;height:auto;display:block}}
.end-mark .mark-text{{font-size:130px;font-weight:800}}
.end-body{{position:relative;display:flex;flex-direction:column;gap:34px}}
.end-tag{{font-size:40px;text-align:center}}
.end-kicker{{font-size:34px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{accent}}}
.end-title{{font-size:124px;font-weight:800;line-height:1.02;letter-spacing:-.02em}}
.end-sub{{font-size:44px;color:{muted};line-height:1.3}}
.end-btn{{align-self:flex-start;font-size:48px;font-weight:800;padding:26px 44px;border-radius:24px;background:{accent};color:{on_accent};transform-origin:left center}}
.end-phone{{font-size:40px;font-weight:700}}
"""


def reject_hdr(path):
    """Nagranie z iPhone'a w HLG przełącza HyperFrames na render HDR całego klipu (16 bit,
    x265 slow, kolory HDR na zwykłym telefonie) — najpierw tools/real_broll.py (SDR)."""
    if Path(path).suffix.lower() not in (".mp4", ".mov", ".m4v"):
        return
    transfer = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                               "stream=color_transfer", "-of", "csv=p=0", str(path)],
                              capture_output=True, text=True).stdout
    if "arib-std-b67" in transfer or "smpte2084" in transfer:
        raise SystemExit(f"{Path(path).name}: źródło HDR ({transfer.split(',')[0].strip()}) — przekonwertuj do SDR bt709")


def stage(comp, folder):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "media").mkdir(exist_ok=True)
    (folder / "vendor").mkdir(exist_ok=True)
    (folder / "fonts").mkdir(exist_ok=True)
    shutil.copy(GSAP, folder / "vendor" / "gsap.min.js")
    for font in (BRAND / "fonts").glob("*.woff2"):
        shutil.copy(font, folder / "fonts" / font.name)
    shutil.copy(BRAND / "logos" / "flowbiz-ai.png", folder / "media" / "flowbiz-ai.png")
    (folder / "index.html").write_text(comp.build())
    for name, src in comp.media.items():
        reject_hdr(src)
        link = folder / "media" / name
        if link.is_symlink() or link.exists():
            link.unlink()
        os.symlink(src, link)


def hf(args, cwd):
    env = dict(os.environ, PATH=f"{NODE22}:{os.environ['PATH']}", PRODUCER_BROWSER_GPU_MODE="hardware")
    return subprocess.run(["npx", "-y", "hyperframes@latest", *args], cwd=cwd, env=env,
                          capture_output=True, text=True)


def probe_duration(path, stream):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries",
                          "stream=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    # ffprobe potrafi dopisać pusty drugi wiersz/kolumnę („33.7,”) — bierzemy pierwszą liczbę
    found = re.search(r"\d+(?:\.\d+)?", out)
    return float(found.group()) if found else 0.0


def finalize(raw, out, target=-14.0):
    """Render → plik do publikacji: −14 LUFS (cel IG/TikTok), x264 CRF 20, a/v równe.

    Dwa przebiegi loudnorm (pomiar, potem liniowa korekta) — jednoprzebiegowy pompuje.
    loudnorm potrafi wydłużyć ścieżkę (.ai/memory/montaz-pulapki-synchronizacji),
    dlatego atrim do długości obrazu i kontrola na końcu.
    """
    video_len = probe_duration(raw, "v:0")
    measure = subprocess.run(["ffmpeg", "-v", "info", "-i", str(raw), "-vn", "-af",
                              f"loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
    m = json.loads(measure[measure.rindex("{"):measure.rindex("}") + 1])
    chain = (f"loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
             f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
             f"linear=true,aresample=48000,atrim=0:{video_len:.3f}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", chain, "-c:v", "libx264",
                    "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(out)], check=True)
    drift = abs(probe_duration(out, "a:0") - probe_duration(out, "v:0"))
    if drift > 0.1:
        raise SystemExit(f"{out.name}: dźwięk i obraz różnią się o {drift:.2f} s")
    return f"{out.name} ({out.stat().st_size / 1e6:.1f} MB, {m['input_i']} → {target} LUFS, a/v {drift:.3f} s)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("--format", action="append")
    ap.add_argument("--palette", action="append")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--snapshot", nargs="*", type=float)
    ap.add_argument("--finalize-only", action="store_true", help="tylko wykończ istniejące render.mp4")
    a = ap.parse_args()
    clips = load_clips()
    variant_file = PACK / "storyboards" / f"{a.clip}.json"
    if "--" in a.clip and variant_file.exists():
        # wariant do testu A/B (np. ad-11-r1--ai-w-produkcji): osobny storyboard, ten sam klip
        board = json.load(open(variant_file))
        clip = next(c for c in clips if c["id"] == board["clip"])
    else:
        clip = next(c for c in clips if c["id"].startswith(a.clip))
        board = json.load(open(PACK / "storyboards" / f"{clip['id']}.json"))
    name = output_name(clip, board)
    for fmt in a.format or board.get("formats", ["reels", "ad", "youtube"]):
        for pal in a.palette or palettes_for(board, clip):
            folder = OUT / name / f"{fmt}-{pal}"
            if a.finalize_only:
                if (folder / "render.mp4").exists():
                    FINAL.mkdir(parents=True, exist_ok=True)
                    print("  →", finalize(folder / "render.mp4", FINAL / f"{name}__{fmt}-{pal}.mp4"), flush=True)
                continue
            comp = Composition(clip, board, fmt, pal)
            stage(comp, folder)
            print(f"▣ {clip['id']} {fmt}-{pal}: {comp.total:.1f} s → {folder.relative_to(PROJECT)}", flush=True)
            if a.check:
                r = hf(["check", "."], folder)
                print((r.stdout + r.stderr)[-1500:])
            if a.snapshot:
                r = hf(["snapshot", ".", "--at", ",".join(str(t) for t in a.snapshot)], folder)
                print((r.stdout + r.stderr)[-600:])
            if a.render:
                raw = folder / "render.mp4"
                r = hf(["render", ".", "-o", str(raw), "--fps", str(FPS), "--quality", "high"], folder)
                if not raw.exists():
                    print((r.stdout + r.stderr)[-800:])
                    continue
                FINAL.mkdir(parents=True, exist_ok=True)
                out = FINAL / f"{name}__{fmt}-{pal}.mp4"
                print("  →", finalize(raw, out), flush=True)


if __name__ == "__main__":
    main()
