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
import re
import shutil
import subprocess
from pathlib import Path

from sources import BUILD, DATA, FACE_CENTER_X, LIBRARY, PROJECT, SOURCE_W

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
}

# Kolor marki w wersji czytelnej na ciemnym tle (jak w projects/youtube).
LOGO_COLORS = {
    "claude": "#D97757", "anthropic": "#D97757", "openmercato": "#F5A623", "github": "#FAF8F0",
    "hubspot": "#FF7A59", "salesforce": "#00A1E0", "n8n": "#EA4B71", "make": "#B36BFF",
    "zapier": "#FF4F00", "openai": "#FAF8F0", "excel": "#21A366", "googlesheets": "#34A853",
    "googledrive": "#4285F4", "shopify": "#7AB55C", "woocommerce": "#C285D6", "slack": "#FAF8F0",
    "notion": "#FAF8F0", "airtable": "#18BFFF", "retool": "#5B8AF5", "gmail": "#EA4335",
    "wordpress": "#5A9FC4", "telegram": "#26A5E4", "whatsapp": "#25D366", "obsidian": "#A88BFA",
    "googlegemini": "#8E9BFF", "allegro": "#FF5A00", "adobeacrobatreader": "#EC1C24",
    "googlecalendar": "#4285F4", "dropbox": "#0061FF",
}

BRANDS = {
    "flowbiz": dict(mark="flowbiz", tagline="systemy AI-first dla firm", web="flowbiz.pl",
                    phone="536 507 701"),
    "aislupsk": dict(mark="AI Słupsk", tagline="warsztaty AI dla firm z regionu", web="aislupsk.pl",
                     phone="536 507 701"),
}

FORMATS = {
    "reels": dict(w=1080, h=1920, face_h=1215),
    "ad": dict(w=1080, h=1920, face_h=1215),
    "youtube": dict(w=1920, h=1080, face_h=1080),
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


def logo(name, size=None, color=None):
    style = []
    if size:
        style.append(f"font-size:{size}px")
    if color:
        style.append(f"color:{color}")
    return f'<i class="logo logo-{name}" style="{";".join(style)}"></i>'


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
        fixes = json.load(open(DATA / "caption-fixes.json"))
        self.words = [dict(w, word=self.fix(w["word"], fixes)) for w in words]
        self.clock = Clock(self.words, fixes)
        self.clip_len = round(clip["duration"], 3)
        self.end_len = board.get("endcard", {}).get(fmt, 3.5 if fmt == "ad" else 2.6 if fmt == "reels" else 0)
        self.total = round(self.clip_len + self.end_len, 3)
        self.html, self.js, self.media = [], [], {}
        self.n = 0
        self.ai_shown = False
        self.panel_busy = []
        self.side_windows = []
        self.hook_end = 0.0

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
                f'<video id="face" src="media/face.mp4" playsinline data-has-audio="true" data-start="0" '
                f'data-duration="{self.clip_len}" data-track-index="0" style="object-position:{face_x:.1f}% 50%"></video>'
                f'<div class="face-fade"></div></div>'
                f'<div id="panel" style="top:{g["face_h"]}px;height:{g["h"] - g["face_h"]}px">'
                f'<div class="panel-grid"></div><div class="panel-rule"></div>'
                f'</div>')
        else:
            self.html.append(
                f'<div id="video-wrap" style="left:0;top:0;width:{g["w"]}px;height:{g["h"]}px">'
                f'<video id="face" src="media/face.mp4" playsinline data-has-audio="true" data-start="0" '
                f'data-duration="{self.clip_len}" data-track-index="0" style="object-position:{face_x:.1f}% 50%"></video></div>'
                f'<div id="side-plate"></div>')

    def brand_corner(self):
        if not self.vertical:
            return
        start = self.q(self.hook_end + 0.2) if self.hook_end else 0
        self.html.append(f'<div class="brand-mark clip" id="{self.uid("mark")}" data-start="{start}" '
                         f'data-duration="{self.q(self.clip_len - start)}" data-track-index="5">{self.brand_mark()}</div>')

    def brand_mark(self):
        if self.brand["mark"] == "flowbiz":
            return '<img src="media/flowbiz.png" alt="flowbiz" class="mark-img">'
        return f'<span class="mark-text"><b>AI</b> Słupsk</span>'

    # ── karty ───────────────────────────────────────────────────────────────
    def host(self, start, end, inner, zone="panel", track=2):
        """Karta w strefie: panel (9:16 dół) / side (16:9 prawa) / full / top."""
        cid = self.uid("c")
        start, end = self.q(start), self.q(min(end, self.total))
        if zone == "panel":
            self.panel_busy.append((start, end))
        self.html.append(f'<div class="card-host clip zone-{zone}" id="{cid}" data-start="{start}" '
                         f'data-duration="{round(end - start, 4)}" data-track-index="{track}">'
                         f'<div class="card" id="{cid}-in">{inner}</div></div>')
        self.js.append(f'tl.fromTo("#{cid}-in",{{opacity:0,y:{30 if self.vertical else 0},x:{0 if self.vertical else 60}}},'
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
        cid = self.host(start, end, f'<div class="kicker">{esc(ev.get("kicker", ""))}</div>'
                                    f'<div class="title">{self.words_html(ev["text"])}</div>'
                                    + (f'<div class="sub">{esc(ev["sub"])}</div>' if ev.get("sub") else ""),
                        ev.get("zone", self.default_zone()))
        self.stagger(f"#{cid} .title .w", start + 0.15, 0.06, 18)

    def card_logos(self, ev, start, end):
        items = "".join(f'<div class="logo-tile">{logo(i["logo"], 96 if self.vertical else 84)}'
                        f'<span>{esc(i.get("name", ""))}</span></div>' for i in ev["items"])
        cid = self.host(start, end, (f'<div class="kicker">{esc(ev["kicker"])}</div>' if ev.get("kicker") else "")
                        + f'<div class="logo-row">{items}</div>'
                        + (f'<div class="sub">{esc(ev["sub"])}</div>' if ev.get("sub") else ""),
                        ev.get("zone", self.default_zone()))
        self.stagger(f"#{cid} .logo-tile", start + 0.2, 0.14)

    def card_stat(self, ev, start, end):
        cid = self.host(start, end,
                        f'<div class="kicker">{esc(ev.get("kicker", ""))}</div>'
                        f'<div class="stat"><span class="pre">{esc(ev.get("prefix", ""))}</span>'
                        f'<span class="num" id="SID">{ev["from"]}</span><span class="suf">{esc(ev.get("suffix", ""))}</span></div>'
                        f'<div class="sub">{esc(ev.get("label", ""))}</div>', ev.get("zone", self.default_zone()))
        self.html[-1] = self.html[-1].replace('id="SID"', f'id="{cid}-num"')
        self.js.append(f'(function(){{var o={{v:{ev["from"]}}};tl.to(o,{{v:{ev["to"]},duration:{ev.get("dur", 1.2)},'
                       f'ease:"power2.out",onUpdate:function(){{var e=document.getElementById("{cid}-num");'
                       f'if(e)e.textContent=Math.round(o.v)}}}},{self.q(start + 0.3)});}})();')

    def card_compare(self, ev, start, end):
        left, right = ev["before"], ev["after"]
        cid = self.host(start, end,
                        f'<div class="kicker">{esc(ev.get("kicker", ""))}</div><div class="compare">'
                        f'<div class="side before"><span class="tag">PRZED</span><b>{esc(left["value"])}</b><span>{esc(left["label"])}</span></div>'
                        f'<div class="arrow">→</div>'
                        f'<div class="side after"><span class="tag">PO</span><b>{esc(right["value"])}</b><span>{esc(right["label"])}</span></div></div>',
                        ev.get("zone", self.default_zone()))
        self.js.append(f'tl.fromTo("#{cid} .before",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:0.4}},{self.q(start + 0.15)});')
        self.js.append(f'tl.fromTo("#{cid} .after",{{opacity:0,x:40}},{{opacity:1,x:0,duration:0.4}},'
                       f'{self.q(self.clock.at(ev["after_at"]) if ev.get("after_at") else start + 0.9)});')
        self.js.append(f'tl.fromTo("#{cid} .before b",{{color:"{self.pal["text"]}"}},{{color:"{self.pal["danger"]}",'
                       f'textDecorationColor:"{self.pal["danger"]}",duration:0.3}},{self.q(start + 1.2)});')

    def card_list(self, ev, start, end):
        rows = "".join(f'<div class="li" data-i="{i}"><span class="n">{i + 1}</span>'
                       f'{logo(it["logo"], 40) if it.get("logo") else ""}<span class="t">{esc(it["text"])}</span></div>'
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
        cid = self.host(start, end, f'<div class="quote">„{self.words_html(ev["text"])}”</div>'
                                    + (f'<div class="sub">{esc(ev["sub"])}</div>' if ev.get("sub") else ""),
                        ev.get("zone", self.default_zone()))
        self.stagger(f"#{cid} .quote .w", start + 0.1, 0.05, 14)

    def broll(self, ev, start, end):
        """Przebitka: w pionie zastępuje twarz (panel z kartami zostaje), w 16:9 pełny kadr."""
        name = Path(ev["src"]).name
        self.media[name] = (PROJECT / ev["src"]).resolve() if not Path(ev["src"]).is_absolute() else Path(ev["src"])
        bid = self.uid("b")
        start, end = self.q(start), self.q(end)
        h = self.geo["face_h"] if self.vertical else self.geo["h"]
        self.html.append(f'<div class="broll" id="{bid}" style="height:{h}px">'
                         f'<video id="{bid}-v" class="clip" src="media/{name}" muted playsinline data-start="{start}" '
                         f'data-duration="{round(end - start, 4)}" data-media-start="{ev.get("from", 0)}" data-track-index="1"></video>'
                         + (f'<div class="broll-label">{esc(ev["label"])}</div>' if ev.get("label") else "") + '</div>')
        self.js.append(f'tl.set("#{bid}",{{opacity:1}},{start});tl.set("#{bid}",{{opacity:0}},{end});')
        zoom = (1.0, 1.1) if ev.get("ken", "in") == "in" else (1.1, 1.0)
        self.js.append(f'tl.fromTo("#{bid}",{{scale:{zoom[0]}}},{{scale:{zoom[1]},duration:{round(end - start, 3)},ease:"none"}},{start});')
        if ev.get("label"):
            shown = max(start + 0.2, self.hook_end + 0.15)
            self.js.append(f'tl.set("#{bid} .broll-label",{{opacity:0}},0);')
            if end - shown > 0.8:
                self.js.append(f'tl.fromTo("#{bid} .broll-label",{{opacity:0,y:16}},{{opacity:1,y:0,duration:0.35}},{self.q(shown)});')
        if ev.get("ai", True) and not self.ai_shown:
            self.ai_shown = True
            self.ai_label(start, min(3.2, max(2.0, end - start)))

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
        end = self.clock.at(hook.get("until", 3.0), floor=0)
        self.hook_end = end
        cid = self.uid("h")
        self.html.append(f'<div class="hook clip" id="{cid}" data-start="0" data-duration="{self.q(end)}" data-track-index="4">'
                         f'<div class="hook-in">{self.words_html(hook["text"], accent=hook.get("accent", []))}</div></div>')
        self.stagger(f"#{cid} .w", 0.05, 0.07, 30)
        self.js.append(f'tl.to("#{cid} .hook-in",{{opacity:0,duration:0.25}},{self.q(end - 0.25)});')

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
        for i, line in enumerate(lines):
            start = self.q(line[0]["start"] - 0.05)
            end = self.q(lines[i + 1][0]["start"] - 0.05) if i + 1 < len(lines) else self.q(min(line[-1]["end"] + 0.6, self.clip_len))
            end = min(end, self.q(line[-1]["end"] + 1.2))
            if end <= start:
                continue
            cid = self.uid("cap")
            spans = "".join(f'<span class="cw" id="{cid}-{k}">{esc(w["word"])}</span> ' for k, w in enumerate(line))
            self.html.append(f'<div class="cap clip" id="{cid}" data-start="{start}" data-duration="{round(end - start, 4)}" '
                             f'data-track-index="6"><div class="cap-in">{spans}</div></div>')
            for k, w in enumerate(line):
                self.js.append(f'tl.set("#{cid}-{k}",{{color:"{self.pal["accent"]}"}},{self.q(w["start"])});')

    def cta_chip(self):
        if self.fmt != "ad":
            return
        cta = self.board.get("cta", {})
        text = cta.get("chip", self.brand["web"])
        start = self.q(max(3.2, self.hook_end + 0.2))
        self.html.append(f'<div class="cta-chip clip" id="{self.uid("chip")}" data-start="{start}" '
                         f'data-duration="{self.q(self.clip_len - start)}" data-track-index="5">'
                         f'<span class="chip-dot"></span>{esc(text)}</div>')

    def endcard(self):
        if not self.end_len:
            return
        cta = self.board.get("cta", {})
        start = self.clip_len
        cid = self.uid("end")
        if self.fmt == "ad":
            lines = cta.get("ad", {})
            body = (f'<div class="end-kicker">{esc(lines.get("kicker", "Bezpłatna konsultacja"))}</div>'
                    f'<div class="end-title">{self.words_html(lines.get("title", "Przyjadę do Twojej firmy"))}</div>'
                    f'<div class="end-sub">{esc(lines.get("sub", "Słupsk · Pomorze · Zachodniopomorskie"))}</div>'
                    f'<div class="end-btn">{esc(lines.get("button", self.brand["web"]))}</div>'
                    f'<div class="end-phone">tel. {esc(self.brand["phone"])}</div>')
        else:
            lines = cta.get("reels", {})
            body = (f'<div class="end-kicker">{esc(lines.get("kicker", "Chcesz to u siebie?"))}</div>'
                    f'<div class="end-title">{self.words_html(lines.get("title", "Napisz „AGENT” w komentarzu"))}</div>'
                    f'<div class="end-sub">{esc(lines.get("sub", "Wyślę Ci materiał, jak zacząć"))}</div>')
        self.html.append(f'<div class="endcard clip" id="{cid}" data-start="{self.q(start)}" data-duration="{self.q(self.end_len)}" '
                         f'data-track-index="7"><div class="end-grid"></div><div class="end-mark">{self.brand_mark()}</div>'
                         f'<div class="end-body">{body}</div></div>')
        self.js.append(f'tl.fromTo("#{cid} .end-body > *",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.45,stagger:0.12,ease:"power3.out"}},{self.q(start + 0.1)});')
        if self.fmt == "ad":
            self.js.append(f'tl.fromTo("#{cid} .end-btn",{{scale:1}},{{scale:1.05,duration:0.5,yoyo:true,repeat:3,ease:"sine.inOut"}},{self.q(start + 0.9)});')

    def lower_third(self):
        if self.fmt != "youtube" or self.board.get("lower_third") is False:
            return
        cid = self.uid("lt")
        self.html.append(f'<div class="lower-third clip" id="{cid}" data-start="0.6" data-duration="4.2" data-track-index="5">'
                         f'<b>Mateusz Kozłowski</b><span>{esc(self.brand["mark"])} · {esc(self.brand["tagline"])}</span></div>')
        self.js.append(f'tl.fromTo("#{cid}",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:0.5,ease:"power3.out"}},0.6);')
        self.js.append(f'tl.to("#{cid}",{{opacity:0,duration:0.3}},4.5);')

    def fill_panel_gaps(self):
        """Pion: w lukach między kartami panel nie stoi pusty — wraca karta tematu."""
        topic = self.board.get("topic")
        if not self.vertical or not topic:
            return
        busy = sorted(self.panel_busy)
        cursor, gaps = 0.0, []
        for a, b in busy + [(self.clip_len, self.clip_len)]:
            if a - cursor >= 1.5:
                gaps.append((cursor, a))
            cursor = max(cursor, b)
        for a, b in gaps:
            self.card_title(dict(topic, zone="panel"), a + (0.05 if a else 0.0), b)

    def default_zone(self):
        return "panel" if self.vertical else "side"

    def words_html(self, text, accent=()):
        out = []
        for word in text.split():
            cls = "w acc" if norm(word) in [norm(a) for a in accent] or word.startswith("*") else "w"
            out.append(f'<span class="{cls}">{esc(word.lstrip("*"))}</span>')
        return " ".join(out)

    # ── składanie ───────────────────────────────────────────────────────────
    def build(self):
        hook = self.board.get("hook")
        if hook and self.fmt != "youtube":
            self.hook_end = self.clock.at(hook.get("until", 3.0), floor=0)
        self.base()
        for ev in self.board["events"]:
            if self.fmt in ev.get("skip", []):
                continue
            start = self.clock.at(ev["at"], floor=ev.get("floor", self.clock.cursor))
            self.clock.cursor = start
            end = self.clock.at(ev["until"], base=start) if "until" in ev else start + ev.get("dur", 3.0)
            end = min(end, self.clip_len)
            if end - start < 0.5:
                raise SystemExit(f"zdarzenie {ev['type']} @ {ev['at']}: {start:.2f}–{end:.2f} — za krótkie")
            getattr(self, "broll" if ev["type"] == "broll" else f"card_{ev['type']}")(ev, start, end)
        self.fill_panel_gaps()
        self.emit_side_windows()
        self.hook()
        self.brand_corner()
        self.captions()
        self.cta_chip()
        self.lower_third()
        self.endcard()
        return self.document()

    def document(self):
        g, p = self.geo, self.pal
        css = (BRAND / "fonts" / "fonts.css").read_text() + logos_css() + STYLE.format(
            W=g["w"], H=g["h"], FH=g["face_h"], LBL=404 if self.vertical else 60, PH=g["h"] - g["face_h"], **p,
            V="1" if self.vertical else "0")
        cls = "fmt-v" if self.vertical else "fmt-h"
        return (f'<!doctype html><html lang="pl"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width={g["w"]}, height={g["h"]}"><style>{css}</style></head>'
                f'<body><div id="root" class="{cls}" data-composition-id="pack" data-start="0" data-width="{g["w"]}" '
                f'data-height="{g["h"]}" data-duration="{self.total}">{"".join(self.html)}</div>'
                f'<script src="vendor/gsap.min.js"></script><script>'
                f'var tl=gsap.timeline({{paused:true}});{"".join(self.js)}window.__timelines["pack"]=tl;</script></body></html>')


STYLE = """
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:100%;height:100%;overflow:hidden;background:{bg};color:{text};font-family:'{font}',sans-serif;-webkit-font-smoothing:antialiased}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;background:{bg}}}
#video-wrap{{position:absolute;overflow:hidden;background:#000}}
#video-wrap video{{width:100%;height:100%;object-fit:cover;display:block}}
.face-fade{{position:absolute;left:0;right:0;bottom:0;height:260px;background:linear-gradient(180deg,rgba(0,0,0,0),{bg})}}
#panel{{position:absolute;left:0;width:{W}px;background:{bg};overflow:hidden}}
.panel-grid{{position:absolute;inset:0;background-image:linear-gradient({grid} 1px,transparent 1px),linear-gradient(90deg,{grid} 1px,transparent 1px);background-size:54px 54px}}
.panel-rule{{position:absolute;left:0;top:0;height:6px;width:100%;background:{accent}}}
.brand-mark{{position:absolute;right:40px;top:236px;padding:10px 16px;border-radius:14px;background:rgba(0,0,0,.6)}}
.mark-img{{height:44px;display:block}}
.mark-text{{font-size:30px;font-weight:700;letter-spacing:.02em;color:{text}}}
.mark-text b{{color:{accent}}}
#side-plate{{position:absolute;right:0;top:0;width:800px;height:{H}px;background:{bg};border-left:6px solid {accent}}}

.card-host{{position:absolute;pointer-events:none}}
.zone-panel{{left:44px;right:132px;top:{FH}px;height:500px;padding-top:46px}}
.zone-side{{right:40px;top:90px;width:700px;height:900px;display:flex;align-items:center}}
.zone-full{{inset:0}}
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
.logo-tile{{background:{panel};border:2px solid {line};border-radius:30px;padding:30px 26px 22px;display:flex;flex-direction:column;align-items:center;gap:16px;min-width:262px}}
.logo-tile span{{font-size:32px;font-weight:700;color:{text}}}
.fmt-h .logo-tile{{min-width:190px}}

.stat{{display:flex;align-items:baseline;gap:10px;font-weight:800;line-height:1}}
.stat .num{{font-size:260px;color:{accent};letter-spacing:-.04em}}
.stat .pre,.stat .suf{{font-size:84px}}

.compare{{display:flex;align-items:center;gap:22px}}
.compare .side{{flex:1;background:{panel};border:2px solid {line};border-radius:28px;padding:26px;display:flex;flex-direction:column;gap:6px}}
.compare .after{{border-color:{accent}}}
.compare .tag{{font-size:22px;font-weight:800;letter-spacing:.14em;color:{muted}}}
.compare .after .tag{{color:{accent}}}
.compare b{{font-size:74px;line-height:1;font-weight:800}}
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

.quote{{font-size:74px;font-weight:800;line-height:1.08;letter-spacing:-.01em}}

.broll{{position:absolute;left:0;top:0;width:{W}px;overflow:hidden;opacity:0;transform-origin:50% 50%}}
.broll video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.broll-label{{position:absolute;left:40px;top:{LBL}px;font-size:34px;font-weight:700;padding:10px 18px;border-radius:12px;background:{bg};color:{text};border-left:6px solid {accent}}}

.ai-label{{position:absolute;display:flex;align-items:center;gap:12px;font-size:24px;font-weight:600;padding:10px 18px 10px 10px;border-radius:40px;background:rgba(0,0,0,.62);color:#fff}}
.ai-dot{{background:#fff;color:#000;font-weight:800;font-size:20px;padding:4px 10px;border-radius:20px}}

.hook{{position:absolute;left:40px;right:40px;top:250px}}
.hook-in{{font-size:84px;font-weight:800;line-height:1.02;letter-spacing:-.02em;color:#fff;text-shadow:0 4px 24px rgba(0,0,0,.65)}}
.hook-in .w{{background:{bg};padding:2px 14px;margin:4px 0;border-radius:10px}}
.hook-in .acc{{background:{accent};color:{on_accent}}}

.cap{{position:absolute;left:40px;right:40px;top:{FH}px;transform:translateY(-150px);display:flex;justify-content:center}}
.cap-in{{font-size:52px;font-weight:800;text-align:center;line-height:1.12;color:#fff;background:rgba(0,0,0,.72);padding:10px 22px;border-radius:16px}}

.cta-chip{{position:absolute;left:40px;top:236px;display:flex;align-items:center;gap:14px;font-size:30px;font-weight:700;padding:14px 24px;border-radius:40px;background:{accent};color:{on_accent}}}
.chip-dot{{width:14px;height:14px;border-radius:50%;background:{on_accent}}}

.lower-third{{position:absolute;left:70px;bottom:80px;display:flex;flex-direction:column;gap:4px;padding:18px 28px;background:{bg};border-left:8px solid {accent};border-radius:6px}}
.lower-third b{{font-size:40px}}
.lower-third span{{font-size:26px;color:{muted}}}

.endcard{{position:absolute;inset:0;background:{bg};display:flex;align-items:center;justify-content:center}}
.end-grid{{position:absolute;inset:0;background-image:linear-gradient({grid} 1px,transparent 1px),linear-gradient(90deg,{grid} 1px,transparent 1px);background-size:60px 60px}}
.end-mark{{position:absolute;left:60px;top:250px}}
.end-mark .mark-img{{height:92px}}
.end-mark .mark-text{{font-size:52px}}
.end-body{{position:relative;width:86%;display:flex;flex-direction:column;gap:34px;margin-top:80px}}
.end-kicker{{font-size:34px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{accent}}}
.end-title{{font-size:124px;font-weight:800;line-height:1.02;letter-spacing:-.02em}}
.end-sub{{font-size:44px;color:{muted};line-height:1.3}}
.end-btn{{align-self:flex-start;font-size:48px;font-weight:800;padding:26px 44px;border-radius:24px;background:{accent};color:{on_accent};transform-origin:left center}}
.end-phone{{font-size:40px;font-weight:700}}
"""


def stage(comp, folder):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "media").mkdir(exist_ok=True)
    (folder / "vendor").mkdir(exist_ok=True)
    (folder / "fonts").mkdir(exist_ok=True)
    shutil.copy(GSAP, folder / "vendor" / "gsap.min.js")
    for font in (BRAND / "fonts").glob("*.woff2"):
        shutil.copy(font, folder / "fonts" / font.name)
    shutil.copy(BRAND / "logos" / "flowbiz.png", folder / "media" / "flowbiz.png")
    (folder / "index.html").write_text(comp.build())
    for name, src in comp.media.items():
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
    return float(out.strip() or 0)


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
    clip = next(c for c in json.load(open(DATA / "clips.json")) if c["id"].startswith(a.clip))
    board = json.load(open(PACK / "storyboards" / f"{clip['id']}.json"))
    for fmt in a.format or board.get("formats", ["reels", "ad", "youtube"]):
        for pal in a.palette or ["A", "B"]:
            folder = OUT / clip["id"] / f"{fmt}-{pal}"
            if a.finalize_only:
                if (folder / "render.mp4").exists():
                    FINAL.mkdir(parents=True, exist_ok=True)
                    print("  →", finalize(folder / "render.mp4", FINAL / f"{clip['id']}__{fmt}-{pal}.mp4"), flush=True)
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
                out = FINAL / f"{clip['id']}__{fmt}-{pal}.mp4"
                print("  →", finalize(raw, out), flush=True)


if __name__ == "__main__":
    main()
