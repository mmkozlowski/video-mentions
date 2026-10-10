#!/usr/bin/env python3
"""Grafiki reklamowe (Meta): pojedynczy hook (feed 4:5, story 9:16) + karuzela 4 slajdy (1:1).

Historia: (1) liczby, przekreślenia, ikony 3D — „tragiczne, chaotyczne”; (2) wzór SellWise:
twarz + nagłówek + przycisk — lepiej, ale środek pusty, a po dołożeniu punktów tekst
nachodził na głowę. Mateusz 10.10: „bardziej karuzele — pierwsze hasło to mocny slogan,
hook, a później rozwinięcie o szczegóły” i „teksty często są wyśrodkowane”.

Układ wyśrodkowany: na górze segment („AI W FIRMIE HANDLOWEJ”), pod nim slogan w dwóch
grubościach z frazą w ramce, Mateusz wyśrodkowany pod tekstem — tekst i twarz nigdy się
nie spotykają. Jeden wpis = dwa produkty:
- **pojedyncza grafika**: tylko hook + Mateusz + przycisk;
- **karuzela**: 1) hook, 2) problem (jak jest dziś), 3) jak to działa (3 kroki),
  4) efekt (wielka liczba) + Mateusz + przycisk.

Zdjęcia prawdziwe (marynarka — ppwrsmart, tło wycięte w Higgsfield; AI Słupsk — wycięcie
z ratuszem z aislupsk.pl), więc grafiki nie są treścią AI.

  python3 tools/static_ads.py     # → final/static/<slug>__feed.png, __story.png, __k1..k4.png
"""
import json
import shutil
import sys

from package import BRAND, FINAL, GSAP, OUT, PALETTES, PROJECT, esc, hf

STATIC = FINAL.parent / "static"
PHOTOS = {"A": PROJECT / "packaging" / "brand" / "mateusz-marynarka.png",
          "S": BRAND / "aislupsk" / "mateusz-cutout.png"}
FORMATS = {"feed": (1080, 1350), "story": (1080, 1920), "k": (1080, 1080)}

# segment = górna linia (woła odbiorcę); light + bold = slogan, mark = fraza w ramce
# (z `bold`, albo z `light` gdy mark_in="light"); problem: `*słowo` = akcent.
# Liczby tylko z nagranych wdrożeń.
ADS = [
    dict(slug="zamowienia-same", segment="AI w firmie produkcyjnej", light="Zamówienia z Excela", bold="wczytują się same.", mark="same.",
         problem="Zamówienie ze 100 pozycjami, każdy kontrahent nazywa produkt inaczej — *kilka *dni przepisywania.",
         points=["System wczytuje Excela kontrahenta", "AI rozpoznaje nazwy produktów", "Człowiek tylko zatwierdza"],
         effect="10 MIN", effect_sub="zamiast kilku dni · producent mebli ogrodowych", source="ep-doram"),
    dict(slug="wiedza-w-zeszycie", segment="AI w firmie produkcyjnej", light="Cała wiedza o produkcji", bold="w jednym zeszycie?", mark="jednym zeszycie?",
         problem="Jak robić wyroby specjalne, wie *jedna *osoba. A kiedyś pójdzie na emeryturę.",
         points=["Receptury i procedury w jednym systemie", "AI odczyta nawet odręczne notatki", "Każdy w zespole ma dostęp"],
         effect="W FIRMIE", effect_sub="wiedza zostaje w systemie, nie w zeszycie", source="ad-12-r2"),
    dict(slug="plan-a-hala", segment="AI w firmie produkcyjnej", light="Plan w Excelu,", bold="a hala robi swoje.", mark="hala robi swoje.",
         problem="Plan produkcji żyje w Excelu kierownika. *Szef *nie *wie, co jest opóźnione.",
         points=["Widok prawie jak Excel kierownika", "Historia każdego etapu", "Opóźnienia widać od razu"],
         effect="1 H", effect_sub="tyle trwała nauka kierownika produkcji", source="ep-vacuactiv"),
    dict(slug="raport-zanim-dojedziesz", segment="AI dla właściciela firmy", light="Wiesz, co dzieje się w firmie,", bold="zanim do niej dojedziesz.", mark="zanim",
         problem="Żeby wiedzieć, co się dzieje na produkcji, *dzwonisz *po *ludziach.",
         points=["Raport: etapy, opóźnienia, klienci", "Prosto na telefon, bez logowania", "Zamówienie w trzech kliknięciach"],
         effect="CO RANO", effect_sub="raport z firmy na telefonie · agent AI dla właściciela", source="ep-vacuactiv"),
    dict(slug="etykiety-jednym-kliknieciem", segment="AI w sklepie internetowym", light="Etykiety do wszystkich paczek", bold="jednym kliknięciem.", mark="jednym kliknięciem.",
         problem="Cztery worki po 25 kg to *cztery *etykiety — ręcznie, przy każdym zamówieniu.",
         points=["Podobne zamówienia w jednym koszyku", "Wszystkie etykiety naraz", "Prosto do drukarki"],
         effect="100 H", effect_sub="miesięcznie mniej ręcznej pracy · sklep z paszą", source="ch-marpasz-2"),
    dict(slug="oferta-5-minut", segment="AI w firmie handlowej", light="Oferta w 5 minut,", bold="nie w dwa dni.", mark="5 minut,", mark_in="light",
         problem="Oferta zaczynana w poniedziałek rano, *kończona *we *wtorek wieczorem.",
         points=["Asystent czyta maile z zapytaniami", "Szkic oferty z cenami z magazynu", "Akceptujesz jednym kliknięciem"],
         effect="5 MIN", effect_sub="szkic oferty zamiast kilkunastu godzin · producent maszyn sportowych", source="ch-offers-1"),
    # warianty ogólne od Mateusza — do testu A/B jako hook karuzeli
    dict(slug="jak-wyglada-ai-u-ciebie", segment="AI w firmie handlowej i produkcyjnej", light="Jak wygląda AI", bold="w Twojej firmie?", mark="w Twojej firmie?",
         problem="Licencje kupione, ludzie wklejają rzeczy do czata, a *praca *wygląda *tak *samo.",
         points=["Zaczynamy od jednego procesu, który boli", "Dane w jednym systemie", "AI pracuje na Twoich danych"],
         effect="1 PROCES", effect_sub="na start — ten, który wkurza wszystkich w biurze", source="ad-25-e5"),
    dict(slug="aislupsk-twoi-ludzie", segment="Warsztaty AI Słupsk · listopad", light="Twoi ludzie już używają AI.", bold="Wiesz, do czego?", mark="do czego?",
         problem="Maile klientów, umowy, cenniki trafiają do czata — *a *nikt *nie *ustalił *zasad.",
         points=["Co wolno wkleić do czatu, a czego nie", "Zasady pracy z danymi dla zespołu", "Przykłady z firm z regionu"],
         effect="LISTOPAD", effect_sub="warsztaty dla firm ze Słupska i okolic", cta="Zapisz się", web="aislupsk.pl",
         palette="S", source="ad-28-w1"),
]


def marked(text, mark):
    if not mark or mark not in text:
        return esc(text)
    a, b = text.split(mark, 1)
    return f'{esc(a)}<span class="mk">{esc(mark)}</span>{esc(b)}'


def accent(text):
    return " ".join(f'<span class="acc">{esc(w[1:])}</span>' if w.startswith("*") else esc(w) for w in text.split())


def slogan(ad):
    in_light = ad.get("mark_in") == "light"
    light = marked(ad["light"], ad["mark"]) if in_light else esc(ad["light"])
    bold = esc(ad["bold"]) if in_light else marked(ad["bold"], ad["mark"])
    return f'<h1><span class="l">{light}</span> <span class="b">{bold}</span></h1>'


def head(ad):
    logo = ('<div class="brand-ai"><b>AI</b> Słupsk</div>' if ad.get("palette") == "S"
            else '<img class="logo" src="media/flowbiz-ai.png" alt="flowbiz AI">')
    return f'<div class="top">{logo}</div><div class="segment">{esc(ad["segment"])}</div>'


def person(ad):
    return ('<div class="glow"></div><img class="photo" src="media/photo.png" alt="">'
            '<div class="who"><b>Mateusz Kozłowski</b><span>wdrożenia AI i automatyzacji · Pomorze</span></div>')


def cta(ad):
    return (f'<div class="cta"><span class="btn">{esc(ad.get("cta", "Umów rozmowę"))} →</span>'
            f'<span class="web">{esc(ad.get("web", "flowbiz.pl"))} · 536 507 701</span></div>')


def dots(i):
    return '<div class="dots">' + "".join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(4)) + "</div>"


def slide(ad, kind):
    if kind == "single":
        return person(ad) + head(ad) + f'<div class="hook">{slogan(ad)}</div>' + cta(ad)
    if kind == "k1":
        return person(ad) + head(ad) + f'<div class="hook">{slogan(ad)}</div><div class="swipe">Przesuń →</div>' + dots(0)
    if kind == "k2":
        return head(ad) + f'<div class="block"><div class="label">Dziś</div><div class="problem">{accent(ad["problem"])}</div></div>' + dots(1)
    if kind == "k3":
        steps = "".join(f'<div class="step"><b>{n}</b><span>{esc(t)}</span></div>' for n, t in enumerate(ad["points"], 1))
        return head(ad) + f'<div class="block"><div class="label">Jak to działa</div><div class="steps">{steps}</div></div>' + dots(2)
    return (person(ad) + head(ad) + f'<div class="effect"><b>{esc(ad["effect"])}</b><span>{esc(ad["effect_sub"])}</span></div>'
            + cta(ad) + dots(3))


def css(p, fmt, w, h):
    story, square = fmt == "story", fmt == "k"
    top = 250 if story else 56
    bottom = 330 if story else 56
    photo_h = {"feed": 0.62, "story": 0.52, "k": 0.6}[fmt]
    big = {"feed": 100, "story": 108, "k": 88}[fmt]
    eff = {"feed": 200, "story": 210, "k": 150}[fmt]
    return f"""
html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:{p['bg']};color:{p['text']};font-family:'{p['font']}',sans-serif;-webkit-font-smoothing:antialiased}}
#root{{position:relative;width:{w}px;height:{h}px;overflow:hidden}}
.slide{{position:absolute;inset:0;background:{p['bg_fill']};overflow:hidden;text-align:center}}
.glow{{position:absolute;left:50%;bottom:-420px;width:1100px;height:1100px;margin-left:-550px;border-radius:50%;background:radial-gradient(circle,{p['accent']}40,transparent 60%)}}
.photo{{position:absolute;left:50%;bottom:0;height:{h * photo_h:.0f}px;width:auto;transform:translateX(-50%);filter:drop-shadow(0 30px 60px rgba(0,0,0,.55))}}
.top{{position:absolute;left:0;right:0;top:{top}px;display:flex;justify-content:center}} .logo{{height:50px}}
.brand-ai{{font-size:40px;font-weight:800;font-style:italic}} .brand-ai b{{color:{p['accent']}}}
.segment{{position:absolute;left:60px;right:60px;top:{top + 86}px;font-size:{30 if not square else 26}px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:{p['accent']}}}
.hook{{position:absolute;left:70px;right:70px;top:{top + 150}px}}
h1{{margin:0;font-size:{big}px;line-height:1.07;letter-spacing:-.025em;font-style:{p['heading_style']}}}
h1 .l{{font-weight:400}} h1 .b{{font-weight:800}}
.mk{{white-space:nowrap;display:inline-block;line-height:1.02;margin:6px 0;background:{p['accent']};color:{p['on_accent']};padding:0 16px 4px;border-radius:14px;font-weight:800}}
.who{{position:absolute;left:50%;transform:translateX(-50%);bottom:{bottom + (150 if not square else 120)}px;white-space:nowrap;display:flex;flex-direction:column;align-items:center;gap:2px;padding:10px 18px;border-radius:14px;background:{p['bg']}E0}}
.who b{{font-size:24px}} .who span{{font-size:17px;color:{p['muted']}}}
.cta{{position:absolute;left:0;right:0;bottom:{bottom}px;display:flex;flex-direction:column;align-items:center;gap:10px}}
.btn{{font-size:{38 if not square else 32}px;font-weight:800;padding:22px 40px;border-radius:18px;background:{p['accent']};color:{p['on_accent']};box-shadow:0 16px 40px rgba(0,0,0,.45)}}
.web{{font-size:20px;font-weight:700;color:{p['text']};text-shadow:0 2px 10px #000}}
.swipe{{position:absolute;right:56px;bottom:56px;width:84px;height:84px;border-radius:50%;background:{p['text']};color:{p['bg']};font-size:0}}
.swipe::after{{content:"›";font-size:64px;line-height:80px;font-weight:700}}
.dots{{position:absolute;left:0;right:0;bottom:30px;display:flex;justify-content:center;gap:10px}} .dots i{{width:12px;height:12px;border-radius:50%;background:{p['line']}}} .dots i.on{{background:{p['accent']};width:36px;border-radius:6px}}
.block{{position:absolute;left:80px;right:80px;top:{top + 150}px;bottom:{bottom + 60}px;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:34px}}
.label{{font-size:30px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:{p['muted']}}}
.problem{{font-size:{68 if square else 80}px;font-weight:700;line-height:1.16;letter-spacing:-.02em;font-style:{p['heading_style']}}}
.problem .acc{{color:{p['accent']}}}
.steps{{display:flex;flex-direction:column;gap:26px;text-align:left}}
.step{{display:flex;align-items:center;gap:26px;font-size:{44 if square else 50}px;font-weight:700;line-height:1.15}}
.step b{{flex:none;width:88px;height:88px;border-radius:22px;background:{p['accent']};color:{p['on_accent']};display:flex;align-items:center;justify-content:center;font-size:52px;font-weight:900}}
.effect{{position:absolute;left:60px;right:60px;top:{top + 140}px;display:flex;flex-direction:column;align-items:center;gap:10px}}
.effect b{{font-size:{eff}px;font-weight:900;line-height:.95;letter-spacing:-.04em;color:{p['accent']};font-style:{p['heading_style']}}}
.effect span{{font-size:{30 if square else 34}px;font-weight:600;line-height:1.3;max-width:820px}}
"""


def document(fmt, slides, palette):
    w, h = FORMATS[fmt]
    body = "".join(f'<div class="slide clip" id="s{i}" data-start="{i}" data-duration="1" data-track-index="0">{html}</div>'
                   for i, html in enumerate(slides))
    style = (BRAND / "fonts" / "fonts.css").read_text() + css(PALETTES[palette], fmt, w, h)
    return (f'<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width={w}, height={h}">'
            f'<style>{style}</style><script src="vendor/gsap.min.js"></script></head><body>'
            f'<div id="root" data-composition-id="static" data-start="0" data-width="{w}" data-height="{h}" data-duration="{len(slides)}">{body}</div>'
            f'<script>window.__timelines=window.__timelines||{{}};var tl=gsap.timeline({{paused:true}});tl.set({{}},{{}},{len(slides)});'
            f'window.__timelines["static"]=tl;</script></body></html>')


def render(fmt, palette, jobs):
    """jobs: [(nazwa pliku, html slajdu)] → PNG w final/static/."""
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
    (folder / "index.html").write_text(document(fmt, [h for _, h in jobs], palette))
    r = hf(["snapshot", ".", "--at", ",".join(f"{i + 0.5}" for i in range(len(jobs)))], folder)
    shots = sorted((folder / "snapshots").glob("frame-*.png"))
    if len(shots) < len(jobs):
        print((r.stdout + r.stderr)[-800:])
        return False
    for (name, _), shot in zip(jobs, shots):
        shutil.copy(shot, STATIC / name)
        print("→", (STATIC / name).relative_to(PROJECT))
    return True


def main(argv):
    STATIC.mkdir(parents=True, exist_ok=True)
    failed = []
    for palette in sorted({ad.get("palette", "A") for ad in ADS}):
        ads = [ad for ad in ADS if ad.get("palette", "A") == palette]
        for fmt in ("feed", "story"):
            if not render(fmt, palette, [(f'{ad["slug"]}__{fmt}.png', slide(ad, "single")) for ad in ads]):
                failed.append(f"{fmt}-{palette}")
        carousel = [(f'{ad["slug"]}__{k}.png', slide(ad, k)) for ad in ads for k in ("k1", "k2", "k3", "k4")]
        if not render("k", palette, carousel):
            failed.append(f"k-{palette}")
    json.dump([{k: ad.get(k, "") for k in ("slug", "source", "segment", "light", "bold", "problem", "effect", "effect_sub")} for ad in ADS],
              open(STATIC / "sources.json", "w"), ensure_ascii=False, indent=1)
    if failed:
        raise SystemExit(f"snapshot nie zwrócił wszystkich grafik: {', '.join(failed)}")


if __name__ == "__main__":
    main(sys.argv[1:])
