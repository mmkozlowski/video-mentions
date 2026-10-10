#!/usr/bin/env python3
"""Grafiki reklamowe (Meta): feed 4:5 i story 9:16 — wzór SellWise, twarz Mateusza.

Pierwsza seria (7 komunikatów z liczbami, ikony 3D) była „mocno chaotyczna”: etykieta,
liczba, przekreślenie, ikony, tytuł i stopka naraz. Wzór z biblioteki reklam SellWise /
WiseGroup (10.10.2026): jedna myśl na grafikę, nagłówek w dwóch grubościach z kluczową
frazą w ramce, jeden mocny obraz (prawdziwy człowiek z imieniem i rolą), jeden wyraźny
przycisk, logo u góry, dużo powietrza.

Zdjęcia prawdziwe, nie AI: marynarka (ppwrsmart, tło wycięte w Higgsfield) dla flowbiz,
wycięcie z ratuszem (aislupsk.pl) dla AI Słupsk.

  python3 tools/static_ads.py          # → final/static/<slug>__feed.png, __story.png
"""
import json
import shutil
import sys

from package import BRAND, FINAL, GSAP, OUT, PALETTES, PROJECT, esc, hf

STATIC = FINAL.parent / "static"
FORMATS = {"feed": (1080, 1350), "story": (1080, 1920)}
PHOTOS = {"A": PROJECT / "packaging" / "brand" / "mateusz-marynarka.png",
          "S": BRAND / "aislupsk" / "mateusz-cutout.png"}

# Jedna myśl na grafikę. `light` + `bold` = nagłówek w dwóch grubościach; `mark` = fraza
# w ramce (fragment `bold`, albo `light` gdy mark_in="light"). Dowód tylko z nagranych wdrożeń.
ADS = [
    dict(slug="zamowienia-same", kicker="Firmy produkcyjne", light="Zamówienia z Excela",
         bold="wczytują się same.", mark="same.", sub="Człowiek tylko sprawdza.",
         proof="Producent mebli ogrodowych: z kilku dni do 10 minut", source="ep-doram"),
    dict(slug="wiedza-w-zeszycie", kicker="Firmy produkcyjne", light="Cała wiedza o produkcji",
         bold="w jednym zeszycie?", mark="jednym zeszycie?",
         sub="Przeniesiemy ją do systemu, zanim ta osoba odejdzie.", proof="", source="ad-12-r2"),
    dict(slug="plan-a-hala", kicker="Firmy produkcyjne", light="Plan w Excelu,",
         bold="a hala robi swoje.", mark="hala robi swoje.",
         sub="Widok produkcji, który kierownik opanował w godzinę.",
         proof="Producent sprzętu sportowego spod Słupska", source="ep-vacuactiv"),
    dict(slug="raport-zanim-dojedziesz", kicker="Właściciele firm", light="Wiesz, co dzieje się w firmie,",
         bold="zanim do niej dojedziesz.", mark="zanim",
         sub="Raport z produkcji co rano na telefonie.", proof="Agent AI dla właściciela firmy produkcyjnej",
         source="ep-vacuactiv"),
    dict(slug="etykiety-jednym-kliknieciem", kicker="Sklepy internetowe", light="Etykiety do wszystkich paczek",
         bold="jednym kliknięciem.", mark="jednym kliknięciem.",
         sub="Bez przeklejania zamówień do Excela.", proof="Sklep z paszą: ok. 100 godzin miesięcznie mniej",
         source="ch-marpasz-2"),
    dict(slug="oferta-5-minut", kicker="Firmy handlowe", light="Oferta w 5 minut,",
         bold="nie w dwa dni.", mark="5 minut,", mark_in="light",
         sub="Asystent czyta maila klienta i przygotowuje szkic.", proof="Producent maszyn sportowych",
         source="ch-offers-1"),
    dict(slug="aislupsk-twoi-ludzie", kicker="Warsztaty AI Słupsk · listopad", light="Twoi ludzie już używają AI.",
         bold="Wiesz, do czego?", mark="do czego?", sub="Zasady pracy z danymi i przykłady z firm z regionu.",
         proof="", cta="Zapisz się", web="aislupsk.pl", palette="S", source="ad-28-w1"),
]


def marked(text, mark):
    if not mark or mark not in text:
        return esc(text)
    a, b = text.split(mark, 1)
    return f'{esc(a)}<span class="mk">{esc(mark)}</span>{esc(b)}'


def card(ad):
    in_light = ad.get("mark_in") == "light"
    light = marked(ad["light"], ad["mark"]) if in_light else esc(ad["light"])
    bold = esc(ad["bold"]) if in_light else marked(ad["bold"], ad["mark"])
    proof = f'<div class="proof"><i></i>{esc(ad["proof"])}</div>' if ad.get("proof") else ""
    logo = ('<div class="brand-ai"><b>AI</b> Słupsk</div>' if ad.get("palette") == "S"
            else '<img class="logo" src="media/flowbiz-ai.png" alt="flowbiz AI">')
    return (f'<div class="glow"></div><img class="photo" src="media/photo.png" alt="">'
            f'<div class="top">{logo}</div>'
            f'<div class="copy"><div class="kicker">{esc(ad["kicker"])}</div>'
            f'<h1><span class="l">{light}</span> <span class="b">{bold}</span></h1>'
            f'<div class="sub">{esc(ad["sub"])}</div>{proof}</div>'
            f'<div class="who"><b>Mateusz Kozłowski</b><span>wdrożenia AI i automatyzacji · Pomorze</span></div>'
            f'<div class="cta"><span class="btn">{esc(ad.get("cta", "Umów rozmowę"))} →</span>'
            f'<span class="web">{esc(ad.get("web", "flowbiz.pl"))} · 536 507 701</span></div>')


def css(p, w, h, story):
    # story: górne ~250 px i dolne ~330 px zasłania interfejs Instagrama
    top, bottom = (250, 330) if story else (64, 64)
    return f"""
html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:{p['bg']};color:{p['text']};font-family:'{p['font']}',sans-serif;-webkit-font-smoothing:antialiased}}
#root{{position:relative;width:{w}px;height:{h}px;overflow:hidden}}
.slide{{position:absolute;inset:0;background:{p['bg_fill']};overflow:hidden}}
.glow{{position:absolute;right:-260px;bottom:-200px;width:1100px;height:1100px;border-radius:50%;background:radial-gradient(circle,{p['accent']}38,transparent 62%)}}
.photo{{position:absolute;right:{(-150 if p['heading_style'] == 'italic' else -120) if not story else (-110 if p['heading_style'] == 'italic' else -60)}px;bottom:0;height:{h * (0.74 if not story else 0.5):.0f}px;width:auto;filter:drop-shadow(0 30px 60px rgba(0,0,0,.55))}}
.top{{position:absolute;left:72px;top:{top}px}} .logo{{height:58px}}
.brand-ai{{font-size:44px;font-weight:800;font-style:italic}} .brand-ai b{{color:{p['accent']}}}
.copy{{position:absolute;left:72px;top:{top + 120}px;width:{590 if not story else 936}px;display:flex;flex-direction:column;gap:26px}}
.kicker{{font-size:30px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{p['accent']}}}
h1{{margin:0;font-size:{78 if not story else 92}px;line-height:1.1;letter-spacing:-.02em;font-style:{p['heading_style']}}}
h1 .l{{font-weight:400}} h1 .b{{font-weight:800}}
.mk{{white-space:nowrap;display:inline-block;line-height:1.05;margin:4px 0;background:{p['accent']};color:{p['on_accent']};padding:0 14px;border-radius:12px;box-decoration-break:clone;-webkit-box-decoration-break:clone;font-weight:800}}
.sub{{font-size:{34 if not story else 40}px;line-height:1.35;color:{p['muted']};max-width:{520 if not story else 900}px;text-shadow:0 2px 12px {p['bg']}}}
.proof{{align-self:flex-start;display:flex;align-items:center;gap:14px;font-size:26px;font-weight:700;padding:14px 22px;border-radius:14px;background:{p['raised']};max-width:{560 if not story else 900}px}}
.proof i{{flex:none;width:12px;height:12px;border-radius:50%;background:{p['accent']}}}
.who{{position:absolute;right:56px;bottom:{bottom + (150 if story else 120)}px;display:flex;flex-direction:column;align-items:flex-end;gap:2px;text-align:right;padding:14px 20px;border-radius:14px;background:{p['bg']}E6}}
.who b{{font-size:28px}} .who span{{font-size:20px;color:{p['muted']}}}
.cta{{position:absolute;left:72px;bottom:{bottom}px;display:flex;flex-direction:column;gap:14px}}
.btn{{align-self:flex-start;font-size:{38 if not story else 44}px;font-weight:800;padding:24px 40px;border-radius:18px;background:{p['accent']};color:{p['on_accent']};box-shadow:0 16px 40px rgba(0,0,0,.4)}}
.web{{font-size:24px;font-weight:600;color:{p['muted']}}}
"""


def document(fmt, ads, palette):
    w, h = FORMATS[fmt]
    slides = "".join(f'<div class="slide clip" id="s{i}" data-start="{i}" data-duration="1" data-track-index="0">{card(ad)}</div>'
                     for i, ad in enumerate(ads))
    style = (BRAND / "fonts" / "fonts.css").read_text() + css(PALETTES[palette], w, h, fmt == "story")
    return (f'<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width={w}, height={h}">'
            f'<style>{style}</style><script src="vendor/gsap.min.js"></script></head><body>'
            f'<div id="root" data-composition-id="static" data-start="0" data-width="{w}" data-height="{h}" data-duration="{len(ads)}">{slides}</div>'
            f'<script>window.__timelines=window.__timelines||{{}};var tl=gsap.timeline({{paused:true}});tl.set({{}},{{}},{len(ads)});'
            f'window.__timelines["static"]=tl;</script></body></html>')


def main(fmts):
    STATIC.mkdir(parents=True, exist_ok=True)
    failed = []
    for fmt in fmts or FORMATS:
        # jedna paleta na projekt — AI Słupsk ma inne kolory, kursywę i zdjęcie
        for palette in sorted({ad.get("palette", "A") for ad in ADS}):
            ads = [ad for ad in ADS if ad.get("palette", "A") == palette]
            folder = OUT / "_static" / f"{fmt}-{palette}"
            if folder.exists():
                shutil.rmtree(folder)
            for sub in ("media", "vendor", "fonts"):
                (folder / sub).mkdir(parents=True, exist_ok=True)
            shutil.copy(GSAP, folder / "vendor" / "gsap.min.js")
            for font in (BRAND / "fonts").glob("*.woff2"):
                shutil.copy(font, folder / "fonts" / font.name)
            shutil.copy(BRAND / "logos" / "flowbiz-ai.png", folder / "media")
            shutil.copy(PHOTOS[palette], folder / "media" / "photo.png")
            (folder / "index.html").write_text(document(fmt, ads, palette))
            r = hf(["snapshot", ".", "--at", ",".join(f"{i + 0.5}" for i in range(len(ads)))], folder)
            shots = sorted((folder / "snapshots").glob("frame-*.png"))
            if len(shots) < len(ads):
                print((r.stdout + r.stderr)[-800:])
                failed.append(f"{fmt}-{palette}")
                continue
            for ad, shot in zip(ads, shots):
                out = STATIC / f"{ad['slug']}__{fmt}.png"
                shutil.copy(shot, out)
                print("→", out.relative_to(PROJECT))
    json.dump([{k: ad.get(k, "") for k in ("slug", "source", "kicker", "light", "bold", "proof")} for ad in ADS],
              open(STATIC / "sources.json", "w"), ensure_ascii=False, indent=1)
    if failed:
        raise SystemExit(f"snapshot nie zwrócił wszystkich grafik: {', '.join(failed)}")


if __name__ == "__main__":
    main(sys.argv[1:])
