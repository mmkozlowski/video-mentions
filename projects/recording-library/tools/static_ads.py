#!/usr/bin/env python3
"""Grafiki statyczne pod sprzedaż automatyzacji i AI (flowbiz): feed 4:5 i story 9:16.

Każda grafika = jeden wynik z prawdziwego wdrożenia (liczby z nagrań, nie z głowy):
duża liczba albo przed → po, ikona/schemat (ikony z hook_art.py, logo narzędzi
oryginalne z logos.css), jedno zdanie, stopka z logo i CTA. Składane w HTML tymi
samymi fontami i paletą co wideo, zrzucane do PNG przez HyperFrames (snapshot).

  python3 tools/static_ads.py          # → final/static/<slug>__feed.png, __story.png
"""
import json
import shutil
import sys

from package import (BRAND, FINAL, GSAP, LOGO_COLORS, OUT, PALETTES, PROJECT, esc, fit, hf,
                     logo, logos_css, tokens)

STATIC = FINAL.parent / "static"
FORMATS = {"feed": (1080, 1350), "story": (1080, 1920)}

# Źródło każdej liczby: rozdział z biblioteki klipów (data/catalog.md).
ADS = [
    dict(slug="zamowienia-10-minut", source="ep-doram (2:02)",
         kicker="Producent mebli ogrodowych", before="kilka dni", after="10 min",
         visual=[{"art": "h-paper-stack"}, {"art": "h-stopwatch"}],
         title="Zamówienie z Excela kontrahenta wczytuje *system. Człowiek tylko sprawdza."),
    dict(slug="trafnosc-94", source="ch-doram-5-70-94",
         kicker="AI uczy się na Twoich poprawkach", meter=(70, 94),
         title="Po miesiącu AI sama dopasowuje *94% *pozycji zamówień."),
    dict(slug="100-godzin", source="ch-marpasz-2-100-godzin",
         kicker="Sklep internetowy z paszą", big="100 h", big_sub="miesięcznie mniej ręcznej pracy",
         visual=[{"art": "h-hourglass"}],
         title="Cztery worki to nie cztery etykiety. AI łączy zamówienia w *jeden *koszyk."),
    dict(slug="oferta-5-minut", source="ch-offers-1-oferta-5-minut",
         kicker="Producent maszyn sportowych", before="kilkanaście h", after="5 min",
         visual=[{"logo": "gmail"}, {"logo": "telegram"}],
         title="Asystent AI czyta maile i przygotowuje *szkic *oferty."),
    dict(slug="kody-15-minut", source="ch-doram-6-kody-15-minut",
         kicker="Bez AI. Zwykły program.", before="kilka dni", after="15 min",
         visual=[{"art": "h-calendar"}, {"logo": "adobeacrobatreader"}],
         title="Etykiety z kodami do całego zamówienia: *PDF *jednym *kliknięciem."),
    dict(slug="raport-7-00", source="ad-19-ra1",
         kicker="Agent AI dla zarządu", big="7:00", big_sub="raport z firmy na Telegramie",
         visual=[{"logo": "telegram"}, {"art": "h-factory"}],
         title="Wiesz, co dzieje się na produkcji, *zanim *dojedziesz do firmy."),
    dict(slug="konsultacja", source="ad-05-m1",
         kicker="Bezpłatna konsultacja", portrait=True,
         title="Przyjadę do *Twojej firmy.",
         sub="Zobaczę, jak pracuje zespół, i powiem, co warto zautomatyzować. Słupsk · Pomorze · Gdańsk · Koszalin."),
]


def words(text):
    return " ".join(f'<span class="{"acc" if w.startswith("*") else ""}">{esc(w.lstrip("*"))}</span>' for w in tokens(text))


def item(it, size):
    if it.get("art"):
        return f'<img class="art" style="width:{size}px;height:{size}px" src="media/{it["art"]}.png" alt="">'
    return f'<span class="tile" style="width:{size}px;height:{size}px">{logo(it["logo"], int(size * 0.55), LOGO_COLORS.get(it["logo"]))}</span>'


def card(ad, fmt, w, h):
    story = fmt == "story"
    icon = 230 if story else 190
    parts = [f'<div class="kicker">{esc(ad["kicker"])}</div>']
    if ad.get("before"):
        parts.append(f'<div class="ba"><span class="before">{esc(ad["before"])}</span>'
                     f'<span class="arrow">→</span><span class="after">{esc(ad["after"])}</span></div>')
    if ad.get("big"):
        parts.append(f'<div class="big">{esc(ad["big"])}</div><div class="big-sub">{esc(ad["big_sub"])}</div>')
    if ad.get("meter"):
        a, b = ad["meter"]
        parts.append(f'<div class="meter"><div class="bar"><i style="width:{b}%"></i><em style="left:{a}%"></em></div>'
                     f'<div class="scale"><span>start: {a}%</span><b>{b}%</b></div></div>')
    if ad.get("visual"):
        parts.append('<div class="row">' + '<span class="sign">→</span>'.join(item(i, icon) for i in ad["visual"]) + '</div>')
    if ad.get("portrait"):   # tekst obok sylwetki — węższa kolumna, większy tytuł
        size = fit(ad["title"], 600 if not story else 900, 110, 3, 60)
    else:
        size = fit(ad["title"], w - 160, 84 if story else 70, 4 if story else 3, 44)
    parts.append(f'<div class="title" style="font-size:{size}px">{words(ad["title"])}</div>')
    if ad.get("sub"):
        parts.append(f'<div class="sub">{esc(ad["sub"])}</div>')
    if ad.get("portrait"):
        parts.append('<img class="portrait" src="media/mateusz-cutout.png" alt="">')
    cta = ('<span class="btn">flowbiz.pl</span>' if ad.get("portrait")
           else '<span class="cta">Bezpłatna konsultacja · <b>flowbiz.pl</b></span>')
    foot = f'<div class="foot"><img class="mark" src="media/flowbiz-ai.png" alt="flowbiz AI">{cta}</div>'
    if ad.get("portrait"):
        parts.append(f'<div class="phone">tel. 536 507 701</div>')
    return f'<div class="ad{" has-portrait" if ad.get("portrait") else ""}">{"".join(parts)}</div>{foot}'


def document(fmt):
    w, h = FORMATS[fmt]
    p = PALETTES["A"]
    story = fmt == "story"
    # story: górne 250 px i dolne 340 px zasłania interfejs Instagrama
    pad_top, pad_bottom = (260, 360) if story else (90, 70)
    css = (BRAND / "fonts" / "fonts.css").read_text() + logos_css() + f"""
html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:{p['bg']};color:{p['text']};font-family:'{p['font']}',sans-serif;-webkit-font-smoothing:antialiased}}
#root{{position:relative;width:{w}px;height:{h}px;overflow:hidden}}
.slide{{position:absolute;inset:0;background:{p['bg']};background-image:linear-gradient({p['grid']} 1px,transparent 1px),linear-gradient(90deg,{p['grid']} 1px,transparent 1px);background-size:60px 60px}}
.ad{{position:absolute;left:80px;right:80px;top:{pad_top}px;bottom:{pad_bottom + 130}px;display:flex;flex-direction:column;justify-content:center;gap:{40 if story else 30}px}}
.kicker{{font-size:{36 if story else 32}px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{p['accent']}}}
.ba{{display:flex;align-items:baseline;gap:30px;flex-wrap:wrap}}
.before{{font-size:{70 if story else 60}px;font-weight:800;color:{p['muted']};text-decoration:line-through;text-decoration-thickness:6px}}
.arrow{{font-size:70px;font-weight:800;color:{p['accent']}}}
.after{{font-size:{190 if story else 160}px;font-weight:800;line-height:.95;letter-spacing:-.03em;color:{p['accent']}}}
.big{{font-size:{260 if story else 220}px;font-weight:800;line-height:.9;letter-spacing:-.04em;color:{p['accent']}}}
.big-sub{{font-size:{50 if story else 44}px;font-weight:700;color:{p['text']};margin-top:-10px}}
.meter{{display:flex;flex-direction:column;gap:18px}}
.bar{{position:relative;height:56px;border-radius:28px;background:{p['raised']};overflow:hidden}}
.bar i{{display:block;height:100%;background:{p['accent']};border-radius:28px}}
.bar em{{position:absolute;top:0;bottom:0;width:6px;background:{p['bg']}}}
.scale{{display:flex;justify-content:space-between;align-items:baseline;font-size:40px;font-weight:700;color:{p['muted']}}}
.scale b{{font-size:{200 if story else 170}px;line-height:.9;color:{p['accent']};letter-spacing:-.04em}}
.row{{display:flex;align-items:center;gap:26px}}
.art{{object-fit:contain;mix-blend-mode:lighten;-webkit-mask-image:radial-gradient(circle,#000 52%,transparent 71%);mask-image:radial-gradient(circle,#000 52%,transparent 71%)}}
.tile{{display:flex;align-items:center;justify-content:center;border-radius:48px;background:{p['raised']}}}
.sign{{font-size:64px;font-weight:800;color:{p['accent']}}}
.title{{font-weight:800;line-height:1.08;letter-spacing:-.02em}}
.title span{{display:inline-block}} .title .acc{{color:{p['accent']}}}
.sub{{font-size:{42 if story else 36}px;line-height:1.35;color:{p['muted']}}}
.has-portrait{{justify-content:flex-start;padding-top:{40 if story else 0}px}}
.has-portrait .title,.has-portrait .sub{{max-width:{620 if not story else 920}px}}
.portrait{{position:absolute;right:-90px;bottom:{-pad_bottom - 130}px;width:{640 if story else 600}px;height:auto;z-index:0}}
.has-portrait > *:not(.portrait){{position:relative;z-index:1}}
.has-portrait ~ .foot{{right:auto;border-top:0;gap:40px}}
.btn{{font-size:36px;font-weight:800;padding:18px 34px;border-radius:20px;background:{p['accent']};color:{p['on_accent']}}}
.phone{{font-size:40px;font-weight:700}}
.foot{{position:absolute;left:80px;right:80px;bottom:{pad_bottom}px;height:100px;display:flex;align-items:center;justify-content:space-between;border-top:2px solid {p['line']};padding-top:26px}}
.mark{{height:62px;width:auto}}
.cta{{font-size:{34 if story else 30}px;font-weight:600;color:{p['muted']}}} .cta b{{color:{p['accent']}}}
"""
    slides = "".join(f'<div class="slide clip" id="s{i}" data-start="{i}" data-duration="1" data-track-index="0">{card(ad, fmt, w, h)}</div>'
                     for i, ad in enumerate(ADS))
    return (f'<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width={w}, height={h}">'
            f'<style>{css}</style><script src="vendor/gsap.min.js"></script></head><body>'
            f'<div id="root" data-composition-id="static" data-start="0" data-width="{w}" data-height="{h}" data-duration="{len(ADS)}">{slides}</div>'
            f'<script>window.__timelines=window.__timelines||{{}};var tl=gsap.timeline({{paused:true}});tl.set({{}},{{}},{len(ADS)});'
            f'window.__timelines["static"]=tl;</script></body></html>')


def main(fmts):
    STATIC.mkdir(parents=True, exist_ok=True)
    failed = []
    for fmt in fmts or FORMATS:
        folder = OUT / "_static" / fmt
        if folder.exists():
            shutil.rmtree(folder)
        for sub in ("media", "vendor", "fonts"):
            (folder / sub).mkdir(parents=True, exist_ok=True)
        shutil.copy(GSAP, folder / "vendor" / "gsap.min.js")
        for font in (BRAND / "fonts").glob("*.woff2"):
            shutil.copy(font, folder / "fonts" / font.name)
        shutil.copy(BRAND / "logos" / "flowbiz-ai.png", folder / "media")
        shutil.copy(BRAND / "aislupsk" / "mateusz-cutout.png", folder / "media")
        for art in (PROJECT / "assets" / "hook-art").glob("*.png"):
            shutil.copy(art, folder / "media")
        (folder / "index.html").write_text(document(fmt))
        r = hf(["snapshot", ".", "--at", ",".join(f"{i + 0.5}" for i in range(len(ADS)))], folder)
        shots = sorted((folder / "snapshots").glob("frame-*.png"))
        if len(shots) < len(ADS):
            print((r.stdout + r.stderr)[-800:])
            failed.append(fmt)
            continue
        for ad, shot in zip(ADS, shots):
            out = STATIC / f"{ad['slug']}__{fmt}.png"
            shutil.copy(shot, out)
            print("→", out.relative_to(PROJECT))
    json.dump([{k: ad[k] for k in ("slug", "source", "kicker", "title")} for ad in ADS],
              open(STATIC / "sources.json", "w"), ensure_ascii=False, indent=1)
    if failed:
        raise SystemExit(f"snapshot nie zwrócił wszystkich grafik: {', '.join(failed)}")


if __name__ == "__main__":
    main(sys.argv[1:])
