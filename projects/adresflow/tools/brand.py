#!/usr/bin/env python3
"""Generator warstw brandingowych AdresFlow do reklam 9:16 (1080x1920)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
F = os.path.join(HERE, "fonts")
OUT = os.path.join(ROOT, "build", "overlays")   # warstwy są odtwarzalne → build/
os.makedirs(OUT, exist_ok=True)

# --- paleta AdresFlow (z apps/web/src/styles/legacy.css) ---
BG      = (10, 11, 16)          # #0a0b10
ACCENT  = (139, 92, 246)        # #8b5cf6
ACC_HI  = (167, 139, 250)       # #a78bfa
MAGENTA = (217, 70, 239)        # #d946ef
TEXT    = (241, 245, 249)       # #f1f5f9
TEXT2   = (148, 163, 184)       # #94a3b8

def font(name, size):
    return ImageFont.truetype(os.path.join(F, name), size)

def measure(draw, text, fnt, tracking=0):
    if not tracking:
        b = draw.textbbox((0, 0), text, font=fnt)
        return b[2] - b[0], b[3] - b[1], b
    w = sum(draw.textlength(ch, font=fnt) + tracking for ch in text) - tracking
    b = draw.textbbox((0, 0), text, font=fnt)
    return int(w), b[3] - b[1], b

def draw_tracked(draw, xy, text, fnt, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking

def gradient_text(text, fnt, size_wh, c1=ACCENT, c2=MAGENTA):
    """Tekst wypełniony gradientem brandowym, zwraca RGBA."""
    w, h = size_wh
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((0, 0), text, font=fnt, fill=255)
    grad = Image.new("RGBA", (w, h))
    gd = ImageDraw.Draw(grad)
    for x in range(w):
        t = x / max(w - 1, 1)
        gd.line([(x, 0), (x, h)], fill=(
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t), 255))
    grad.putalpha(mask)
    return grad

def pill(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)

def eyebrow(img, text, y=54, margin=54):
    """Mały nagłówek w kapitalikach — lewy górny róg, para dla znaku po prawej."""
    d = ImageDraw.Draw(img)
    fnt = font("Poppins-SemiBold.ttf", 32)
    tracking = 5
    tw, th, _ = measure(d, text, fnt, tracking)
    pad_x = 34
    bw, bh = tw + pad_x * 2, 126  # bh zrównane z watermarkiem
    x0 = margin
    pill(d, [x0, y, x0 + bw, y + bh], bh // 2, BG + (200,))
    d.rounded_rectangle([x0, y, x0 + bw, y + bh], radius=bh // 2,
                        outline=ACCENT + (120,), width=2)
    draw_tracked(d, (x0 + pad_x, y + bh // 2 - 24), text, fnt, ACC_HI + (255,), tracking)
    return img

def headline(img, lines, y_base, accent_line=None, size=86, max_w=930):
    """Główny napis: białe linie na ciemnych pigułkach, jedna linia w gradiencie.

    Stopień pisma zjeżdża automatycznie, gdy najdłuższa linia nie mieści się
    w kadrze — dzięki temu copy można zmieniać bez ręcznego strojenia layoutu.
    """
    d = ImageDraw.Draw(img)
    while size > 44:
        fnt = font("Poppins-Bold.ttf", size)
        if max(d.textlength(l, font=fnt) for l in lines) <= max_w:
            break
        size -= 2
    fnt = font("Poppins-Bold.ttf", size)
    line_h = int(size * 1.30)
    y = y_base
    for i, line in enumerate(lines):
        tw = int(d.textlength(line, font=fnt))
        pad_x, pad_y = 36, 18
        bw = tw + pad_x * 2
        bh = line_h + pad_y
        x0 = (W - bw) // 2
        pill(d, [x0, y, x0 + bw, y + bh], 26, BG + (225,))
        if accent_line is not None and i == accent_line:
            g = gradient_text(line, fnt, (tw + 8, bh))
            img.alpha_composite(g, (x0 + pad_x, y + pad_y // 2 - int(size * 0.12)))
        else:
            d.text((x0 + pad_x, y + pad_y // 2 - int(size * 0.12)), line,
                   font=fnt, fill=TEXT + (255,))
        y += bh + 16
    return img

def logo_mark(size):
    p = os.path.join(HERE, "logo-brand.png")
    lg = Image.open(p).convert("RGBA")
    r = size / lg.width
    return lg.resize((size, int(lg.height * r)), Image.LANCZOS)

def watermark(img, size=92, margin=54):
    """Dyskretny znak w prawym górnym rogu + nazwa."""
    lg = logo_mark(size)
    d = ImageDraw.Draw(img)
    fnt = font("Poppins-Bold.ttf", 38)
    name = "AdresFlow"
    tw = int(d.textlength(name, font=fnt))
    bw = size + 14 + tw + 56
    bh = max(lg.height, 46) + 34
    x0 = W - margin - bw
    y0 = margin
    pill(d, [x0, y0, x0 + bw, y0 + bh], bh // 2, BG + (200,))
    img.alpha_composite(lg, (x0 + 28, y0 + (bh - lg.height) // 2))
    d.text((x0 + 28 + size + 14, y0 + (bh - 52) // 2), name, font=fnt, fill=TEXT + (255,))
    return img

def ai_mark(y=208):
    """Warstwa z oznaczeniem treści AI — art. 50 ust. 4 AI Act.

    Osobna warstwa, nie część chrome: chrome stoi przez cały klip, a to ma
    zniknąć po kilku sekundach. Ustawienie: wyśrodkowane pod pigułkami chrome
    (eyebrow po lewej, znak po prawej kończą się na y=180).

    Dlaczego NIE przy dolnej krawędzi, mimo że tam mniej przeszkadza: dolne
    ~15 % kadru zasłania w Reels i TikToku interfejs aplikacji (opis, nick,
    przyciski). Oznaczenie, którego nie widać, nie jest oznaczeniem.
    """
    img = blank()
    d = ImageDraw.Draw(img)
    fnt = font("Poppins-SemiBold.ttf", 30)
    txt = "Materiał zawiera treści AI"
    tw = int(d.textlength(txt, font=fnt))
    dot = 16
    pad_x, bh = 30, 66
    bw = pad_x * 2 + dot + 14 + tw
    x0 = (W - bw) // 2
    pill(d, [x0, y, x0 + bw, y + bh], bh // 2, BG + (215,))
    d.rounded_rectangle([x0, y, x0 + bw, y + bh], radius=bh // 2,
                        outline=ACC_HI + (140,), width=2)
    cy = y + bh // 2
    d.ellipse([x0 + pad_x, cy - dot // 2, x0 + pad_x + dot, cy + dot // 2],
              fill=ACC_HI + (255,))
    d.text((x0 + pad_x + dot + 14, cy - 21), txt, font=fnt, fill=TEXT + (255,))
    return img


def progress_bar(img, frac, y=None, h=10):
    """Pasek postępu w gradiencie brandu — typowy element rolek."""
    d = ImageDraw.Draw(img)
    y = y if y is not None else H - 130
    m = 70
    d.rounded_rectangle([m, y, W - m, y + h], radius=h // 2, fill=(255, 255, 255, 45))
    w = int((W - 2 * m) * frac)
    if w > h:
        bar = gradient_text_bar(w, h)
        img.alpha_composite(bar, (m, y))
    return img

def gradient_text_bar(w, h):
    bar = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    for x in range(w):
        t = x / max(w - 1, 1)
        bd.line([(x, 0), (x, h)], fill=(
            int(ACCENT[0] + (MAGENTA[0] - ACCENT[0]) * t),
            int(ACCENT[1] + (MAGENTA[1] - ACCENT[1]) * t),
            int(ACCENT[2] + (MAGENTA[2] - ACCENT[2]) * t), 255))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=255)
    bar.putalpha(mask)
    return bar

def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def price_shock(old_price="899 zł", new_price="ZA DARMO", caption="rzut 3D u grafika"):
    """Plansza otwierająca: stara cena przekreślona, nowa w gradiencie.

    Hook oparty na liczbie — predictor pokazał, że statyczny start
    materiału daje hook_score 27/100, więc pierwszy kadr musi nieść bodziec.
    """
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(600, 0, -6):
        gd.ellipse([W // 2 - r, H // 2 - r, W // 2 + r, H // 2 + r],
                   fill=(ACCENT[0], ACCENT[1], ACCENT[2], int(26 * (1 - r / 600))))
    img.alpha_composite(glow)

    f_cap = font("Poppins-Medium.ttf", 48)
    tw = int(d.textlength(caption, font=f_cap))
    d.text(((W - tw) // 2, 620), caption, font=f_cap, fill=TEXT2 + (255,))

    # stara cena — przekreślona
    f_old = font("Poppins-Bold.ttf", 150)
    tw_o = int(d.textlength(old_price, font=f_old))
    x_o, y_o = (W - tw_o) // 2, 720
    d.text((x_o, y_o), old_price, font=f_old, fill=(120, 130, 150, 255))
    d.line([x_o - 20, y_o + 105, x_o + tw_o + 20, y_o + 95],
           fill=(239, 68, 68, 255), width=12)

    # strzałka rysowana wektorowo — Poppins nie ma glifu U+2193 (wychodzi tofu)
    cx, ay = W // 2, 950
    d.rounded_rectangle([cx - 7, ay, cx + 7, ay + 46], radius=6, fill=ACC_HI + (255,))
    d.polygon([(cx - 30, ay + 40), (cx + 30, ay + 40), (cx, ay + 84)],
              fill=ACC_HI + (255,))

    # nowa cena — gradient marki, stopień dopasowany do szerokości kadru
    size_n = 200
    while size_n > 90:
        f_new = font("Poppins-Bold.ttf", size_n)
        if d.textlength(new_price, font=f_new) <= 880:
            break
        size_n -= 6
    f_new = font("Poppins-Bold.ttf", size_n)
    tw_n = int(d.textlength(new_price, font=f_new))
    img.alpha_composite(gradient_text(new_price, f_new, (tw_n + 12, int(size_n * 1.45))),
                        ((W - tw_n) // 2, 1050 + (200 - size_n) // 2))

    watermark(img)
    return img

def endcard(headline_txt, sub, cta, url="adresflow.com"):
    """Pełna plansza końcowa: ciemne tło, logo, nazwa, CTA."""
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    # poświata brandowa
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(520, 0, -6):
        a = int(30 * (1 - r / 520))
        gd.ellipse([W // 2 - r, 640 - r, W // 2 + r, 640 + r],
                   fill=(ACCENT[0], ACCENT[1], ACCENT[2], a))
    img.alpha_composite(glow)

    lg = logo_mark(300)
    img.alpha_composite(lg, ((W - lg.width) // 2, 470))

    fnt = font("Poppins-Bold.ttf", 92)
    tw = int(d.textlength(headline_txt, font=fnt))
    g = gradient_text(headline_txt, fnt, (tw + 10, 140))
    img.alpha_composite(g, ((W - tw) // 2, 900))

    f2 = font("Poppins-Medium.ttf", 44)
    tw2 = int(d.textlength(sub, font=f2))
    d.text(((W - tw2) // 2, 1060), sub, font=f2, fill=TEXT2 + (255,))

    # CTA pill
    f3 = font("Poppins-Bold.ttf", 52)
    tw3 = int(d.textlength(cta, font=f3))
    bw, bh = tw3 + 110, 118
    x0 = (W - bw) // 2
    y0 = 1240
    bar = gradient_text_bar(bw, bh)
    img.alpha_composite(bar, (x0, y0))
    d.text(((W - tw3) // 2, y0 + 28), cta, font=f3, fill=(255, 255, 255, 255))

    # adres — bez niego reklama nie ma dokąd kierować
    f4 = font("Poppins-SemiBold.ttf", 46)
    tw4 = int(d.textlength(url, font=f4))
    d.text(((W - tw4) // 2, y0 + bh + 46), url, font=f4, fill=ACC_HI + (255,))
    return img


# Trzy kierunki perswazji — do testu A/B, nie do wyboru „w ciemno":
#   v1 = kontrast cenowy (ile to kosztuje w branży)
#   v2 = brak pośrednika (deweloper / karta lokalu)
#   v3 = efekt + szybkość (najmocniejsza animacja)
# Liczby: 30 kr startowych = migracja signup_credits_30; rzut 3D = 2 kr/etap (data.ts)
VERSIONS = {
    "v1": {
        "eyebrow": "RZUT 3D Z KARTKI",
        "hook": ["Rzut 3D u grafika?", "899 zł i tydzień."],
        "payoff": ["Tu: 60 sekund.", "Za darmo."],
        "end": ("AdresFlow", "Pierwsze rzuty 3D za darmo", "Odbierz 30 kredytów"),
        "vo": "Rzut trzy de u grafika? Osiemset dziewięćdziesiąt dziewięć złotych i tydzień "
              "czekania. Tutaj zrobisz go w sześćdziesiąt sekund. Wejdź na Adres Flow "
              "i odbierz trzydzieści darmowych kredytów.",
    },
    "v2": {
        "eyebrow": "RZUT 3D Z KARTKI",
        "hook": ["Masz kartę lokalu.", "Nie masz wizualizacji."],
        "payoff": ["Zrób ją sam.", "Za darmo."],
        "end": ("AdresFlow", "Pierwsze rzuty 3D za darmo", "Odbierz 30 kredytów"),
        "vo": "Masz kartę lokalu, ale nie masz wizualizacji? Zrób ją sam, bez grafika. "
              "Wejdź na Adres Flow i odbierz trzydzieści darmowych kredytów.",
    },
    "v3": {
        "eyebrow": "RZUT 3D Z KARTKI",
        "hook": ["Twój szkic.", "Nasz render 3D rzutu."],
        "payoff": ["W 60 sekund.", "Za darmo."],
        "end": ("AdresFlow", "Pierwsze rzuty 3D za darmo", "Odbierz 30 kredytów"),
        "vo": "Twój szkic. Nasz render trzy de rzutu. W sześćdziesiąt sekund. "
              "Wejdź na Adres Flow i odbierz trzydzieści darmowych kredytów.",
    },
    # --- warianty hooka do testu A/B (ten sam materiał co v3) ---
    # Powód: predictor dał v3 hook_score 27/100 przy sustain 97 — problem jest
    # wyłącznie w pierwszych 3 s. Każdy wariant otwiera innym bólem agenta.
    #
    # v3d — ból: czekanie
    "v3d": {
        "eyebrow": "RZUT 3D Z KARTKI",
        "hook": ["Znowu czekasz", "na rzut 3D?"],
        "payoff": ["Masz go w minutę.", "Za darmo."],
        "end": ("AdresFlow", "Pierwsze rzuty 3D za darmo", "Odbierz 30 kredytów"),
        "vo": "Znowu czekasz na rzut trzy de? Tydzień, osiemset dziewięćdziesiąt dziewięć złotych. "
              "Tutaj masz go w minutę, za dziewięć dziewięćdziesiąt. AdresFlow.",
    },
    # v3e — ból: oferta się nie sprzedaje
    "v3e": {
        "eyebrow": "RZUT 3D Z KARTKI",
        "hook": ["Rzut na kartce.", "Nikt tego nie kupi."],
        "payoff": ["Pokaż render 3D.", "Za darmo."],
        "end": ("AdresFlow", "Pierwsze rzuty 3D za darmo", "Odbierz 30 kredytów"),
        "vo": "Dostałeś rzut na kartce? Nikt tego nie kupi. Pokaż klientowi render trzy de. "
              "Wejdź na Adres Flow i odbierz trzydzieści darmowych kredytów.",
    },
    # v3b — ból: koszt, otwierany planszą price_shock
    "v3b": {
        "eyebrow": "RZUT 3D Z KARTKI",
        "hook": ["Rzut 3D u grafika?", "899 zł i tydzień."],
        "payoff": ["Tu: 60 sekund.", "Za darmo."],
        "end": ("AdresFlow", "Pierwsze rzuty 3D za darmo", "Odbierz 30 kredytów"),
        "vo": "Rzut trzy de u grafika? Osiemset dziewięćdziesiąt dziewięć złotych i tydzień "
              "czekania. Tutaj zrobisz go w sześćdziesiąt sekund, za darmo. "
              "Wejdź na Adres Flow i odbierz trzydzieści kredytów.",
    },
}

def line_layer(text, size, accent, y_center):
    """Pojedyncza linia jako osobna warstwa — żeby animować ją niezależnie.

    Zwraca (obraz przycięty do pigułki, metadane pozycji). Animacja skali
    działa tylko wtedy, gdy każda linia jest osobnym plikiem.
    """
    probe = Image.new("RGBA", (10, 10))
    d0 = ImageDraw.Draw(probe)
    fnt = font("Poppins-Bold.ttf", size)
    tw = int(d0.textlength(text, font=fnt))
    pad_x, pad_y = 36, 18
    line_h = int(size * 1.30)
    bw, bh = tw + pad_x * 2, line_h + pad_y

    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=26, fill=BG + (225,))
    ty = pad_y // 2 - int(size * 0.12)
    if accent:
        img.alpha_composite(gradient_text(text, fnt, (tw + 8, bh)), (pad_x, ty))
    else:
        d.text((pad_x, ty), text, font=fnt, fill=TEXT + (255,))
    return img, {"w": bw, "h": bh, "cx": W // 2, "cy": y_center}


def fit_size(lines, start=86, max_w=930):
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    s = start
    while s > 44:
        f = font("Poppins-Bold.ttf", s)
        if max(probe.textlength(l, font=f) for l in lines) <= max_w:
            return s
        s -= 2
    return s


def build(vk):
    import json
    v = VERSIONS[vk]
    meta = {"lines": {}}

    # chrome — eyebrow + znak, statyczne przez cały klip
    ch = blank()
    eyebrow(ch, v["eyebrow"])
    watermark(ch)
    ch.save(f"{OUT}/{vk}-chrome.png")
    ai_mark().save(f"{OUT}/ai-mark.png")   # wspólna warstwa oznaczenia AI

    # linie hooka i payoffu jako osobne warstwy
    for block, accent_idx, y0 in (("hook", 1, 1330), ("payoff", 0, 1330)):
        lines = v[block]
        size = fit_size(lines)
        line_h = int(size * 1.30) + 18 + 16
        for i, txt in enumerate(lines):
            img, m = line_layer(txt, size, accent=(i == accent_idx),
                                y_center=y0 + i * line_h)
            img.save(f"{OUT}/{vk}-{block}{i}.png")
            meta["lines"][f"{block}{i}"] = m

    endcard(*v["end"]).save(f"{OUT}/{vk}-end.png")
    price_shock().save(f"{OUT}/{vk}-shock.png")
    json.dump(meta, open(f"{OUT}/{vk}.json", "w"))
    print("ok", vk)

if __name__ == "__main__":
    for k in VERSIONS:
        build(k)
