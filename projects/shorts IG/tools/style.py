#!/usr/bin/env python3
"""Warstwy graficzne shorta: napisy, plakietki z liczbami, tytuł i plansza końcowa.

Wszystko powstaje lokalnie w Pillow i wchodzi do montażu jako PNG z alfą.
Powód jest prozaiczny: ffmpeg z Homebrew jest zbudowany BEZ libass i bez
freetype, więc ani `subtitles`, ani `drawtext` nie istnieją w tej instalacji
(`ffmpeg -filters | grep drawtext` → pusto). Napisy trzeba narysować samemu.

Napisy powstają z CZASÓW SŁÓW z transkrypcji gotowej osi (`build/work/rough.json`),
nie z detekcji ciszy — pauza w środku zdania rozbijała je wcześniej na dwa okna
i przesuwała cały timeline o jedno (.ai/memory/montaz-pulapki-synchronizacji).

Napisy renderujemy jako WĄSKI PAS 1080x460, nie pełną klatkę: to ta sama treść,
a montaż dostaje jedną nakładkę zamiast trzystu, więc graf filtrów zostaje
czytelny i szybki.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BUILD = os.path.join(ROOT, "build")
OV = os.path.join(BUILD, "overlays")
FONTS = os.path.join(HERE, "fonts")

W, H, FPS = 1080, 1920, 30

# ── paleta FlowBiz (konfiguracja ciemna z brandbooka 2026) ────────────────
INK = (10, 10, 8)            # #0A0A08  tło plansz i podkładek
BOR = (24, 48, 40)           # #183028  zieleń belek
AMBER = (236, 171, 69)       # #ECAB45  akcent
LIGHT = (250, 248, 240)      # #FAF8F0  tekst

# ── napisy ────────────────────────────────────────────────────────────────
CAP_W, CAP_H = W, 460
CAP_Y = 1190                 # górna krawędź pasa na klatce 1080x1920
CAP_SIZE = 66
CAP_LINE = 88                # interlinia
CAP_MAX_CHARS = 30           # ile znaków mieści się w oknie (dwie linie)
CAP_MAX_LINE = 17            # ile w jednej linii
CAP_MAX_DUR = 2.4            # dłuższe okno czyta się jak plansza, nie jak napis
CAP_MAX_GAP = 0.60           # przerwa większa → nowe okno
PLATE_ALPHA = 205            # podkładka MUSI być kryjąca: materiał skacze
                             # z jasnego nieba na białą stronę www


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


# Whisper myli się tam, gdzie kontekstu nie zna: na nazwie klienta i na
# słowach zjedzonych przez wiatr. Napis idzie na ekran, więc literówka w nazwie
# firmy jest błędem merytorycznym, nie kosmetyką — poprawki są ZAMIERZONE
# i dotyczą wyłącznie zapisu, nie treści wypowiedzi.
FIXES = {
    "obernięty": "ogarnięty",
    "jakim": "jak",            # „zobaczmy jak tam dzisiaj poszło"
    "opak": "Opak",
    "krew": "Kreft",           # nazwa klienta: Opak Kreft
    "dodało": "dodane",
    "kolorystykę": "kolorystyka",   # wyliczenie, nie dopełnienie
}


SENTENCE_END = (".", "!", "?", "…")


def apply_fixes(words):
    """Poprawki zapisu + usunięcie powtórek, które Whisper dokleja na końcu."""
    out = []
    for w in words:
        raw = w["word"].strip()
        core = raw.strip(".,!?…„”\"()")
        tail = raw[len(core):] if raw.startswith(core) else ""
        fixed = FIXES.get(core.lower())
        if fixed:
            core = fixed if core[:1].islower() else fixed[:1].upper() + fixed[1:]
        text = core + tail
        # Ostatnie sekundy transkrypcji potrafią się zapętlić („zrobione.
        # zrobione. To To") — to artefakt dekodera, nie wypowiedź.
        if out and out[-1]["word"].lower() == text.lower() \
                and w["start"] - out[-1]["start"] < 0.45:
            continue
        out.append(dict(word=text, start=w["start"], end=w["end"]))
    # Ogon po ostatniej kropce to też halucynacja — pojedyncze „To" wisiałoby
    # na ekranie po ostatnim zdaniu.
    last_end = max((i for i, w in enumerate(out)
                    if w["word"].endswith(SENTENCE_END)), default=len(out) - 1)
    if len(out) - last_end - 1 <= 2:
        out = out[:last_end + 1]
    return out


def group_words(words):
    """Słowa → okna napisów. Jedno okno = jedna myśl mieszcząca się w kadrze.

    Okno nigdy nie przechodzi przez kropkę: napis „minut. Ale jestem" czyta się
    jak błąd składu, bo oko widzi początek nowego zdania doklejony do starego.
    """
    groups, cur = [], []
    for w in words:
        text = w["word"].strip()
        if not text:
            continue
        if cur:
            gap = w["start"] - cur[-1]["end"]
            span = w["end"] - cur[0]["start"]
            length = len(" ".join(x["word"] for x in cur)) + 1 + len(text)
            if (cur[-1]["word"].endswith(SENTENCE_END)
                    or gap > CAP_MAX_GAP or span > CAP_MAX_DUR
                    or length > CAP_MAX_CHARS):
                groups.append(cur)
                cur = []
        cur.append(dict(word=text, start=w["start"], end=w["end"]))
    if cur:
        groups.append(cur)
    return groups


def wrap(words):
    """Podział okna na dwie linie w miejscu, które wyrównuje ich długość.

    Zachłanne łamanie („dopychaj, aż się nie mieści") zostawiało sieroty typu
    „No dobra, bieg / już" — druga linia z jednym słowem wygląda na usterkę.
    """
    text = " ".join(w["word"] for w in words)
    if len(text) <= CAP_MAX_LINE:
        return [words]
    best, best_cost = None, None
    for k in range(1, len(words)):
        a = " ".join(w["word"] for w in words[:k])
        b = " ".join(w["word"] for w in words[k:])
        if max(len(a), len(b)) > CAP_MAX_LINE + 6:
            continue
        cost = abs(len(a) - len(b)) + 3 * max(0, max(len(a), len(b)) - CAP_MAX_LINE)
        if best_cost is None or cost < best_cost:
            best, best_cost = k, cost
    if best is None:
        best = (len(words) + 1) // 2
    return [words[:best], words[best:]]


def render_caption(lines, active_index):
    """Jedna klatka pasa napisów; słowo o indeksie `active_index` na bursztynowo."""
    img = Image.new("RGBA", (CAP_W, CAP_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fnt = font("Poppins-Bold.ttf", CAP_SIZE)
    space = d.textlength(" ", font=fnt)

    total_h = len(lines) * CAP_LINE
    y = (CAP_H - total_h) // 2
    idx = 0
    for ln in lines:
        widths = [d.textlength(w["word"], font=fnt) for w in ln]
        text_w = sum(widths) + space * (len(ln) - 1)
        x0 = (CAP_W - text_w) / 2
        pad_x, pad_y = 26, 12
        rounded(d, [x0 - pad_x, y - pad_y,
                    x0 + text_w + pad_x, y + CAP_SIZE + pad_y * 1.4],
                22, INK + (PLATE_ALPHA,))
        x = x0
        for w, ww in zip(ln, widths):
            fill = AMBER if idx == active_index else LIGHT
            d.text((x, y), w["word"], font=fnt, fill=fill + (255,))
            x += ww + space
            idx += 1
        y += CAP_LINE
    return img


def build_captions(transcript, out_dir, media_len=None):
    """Pas napisów jako sekwencja PNG + lista czasów (do concat demuxera).

    `media_len` odsiewa słowa, które Whisper dopisał ZA końcem materiału —
    dekoder domyka ostatnie zdanie jeszcze raz („…zrobione." → „jest dobrze.")
    i takie okno wisiałoby na zamrożonej klatce.
    """
    os.makedirs(out_dir, exist_ok=True)
    words = [w for s in json.load(open(transcript))["segments"]
             for w in s.get("words", []) if w["word"].strip()]
    # Whisper dokleja na końcu puste segmenty o zerowej długości — odsiewamy,
    # inaczej ostatnie okno trwa 0 s i miga.
    words = [w for w in words if w["end"] > w["start"]]
    if media_len:
        words = [w for w in words if w["start"] < media_len - 0.05]
    words = apply_fixes(words)

    blank = Image.new("RGBA", (CAP_W, CAP_H), (0, 0, 0, 0))
    blank_path = os.path.join(out_dir, "cap-blank.png")
    blank.save(blank_path)

    shots, n = [], 0
    cursor = 0.0
    for group in group_words(words):
        lines = wrap(group)
        g0, g1 = group[0]["start"], group[-1]["end"]
        if g0 - cursor > 0.04:
            shots.append((blank_path, g0 - cursor))
        for i, w in enumerate(group):
            t1 = group[i + 1]["start"] if i + 1 < len(group) else g1
            dur = max(t1 - w["start"], 1.0 / FPS)
            p = os.path.join(out_dir, f"cap-{n:04d}.png")
            render_caption(lines, i).save(p)
            shots.append((p, dur))
            n += 1
        cursor = g1
    return shots, cursor


# ── plakietki: liczby, które w mowie przelatują, a na ekranie zostają ─────
def badge(text_top, text_big, path, width=None):
    fnt_top = font("Poppins-SemiBold.ttf", 34)
    fnt_big = font("Poppins-Bold.ttf", 76)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = max(tmp.textlength(text_top, font=fnt_top),
             tmp.textlength(text_big, font=fnt_big))
    bw = int(width or tw + 76)
    bh = 176
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rounded(d, [0, 0, bw, bh], 26, INK + (222,))
    d.rounded_rectangle([0, 0, bw, bh], radius=26, outline=AMBER + (150,), width=3)
    d.text(((bw - tmp.textlength(text_top, font=fnt_top)) / 2, 24), text_top,
           font=fnt_top, fill=AMBER + (255,))
    d.text(((bw - tmp.textlength(text_big, font=fnt_big)) / 2, 66), text_big,
           font=fnt_big, fill=LIGHT + (255,))
    img.save(path)
    return path


# ── plansze ───────────────────────────────────────────────────────────────
def plate(lines, path, kicker=None, footer=None, logo=None):
    """Pełnoklatkowa plansza 1080x1920 na tuszu, z bursztynową kreską."""
    img = Image.new("RGBA", (W, H), INK + (255,))
    d = ImageDraw.Draw(img)

    # Delikatna poświata bór-em, żeby tło nie było płaskim prostokątem.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-320, 520, W + 320, 1500], fill=BOR + (120,))
    from PIL import ImageFilter
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(180)))
    d = ImageDraw.Draw(img)

    y = 700
    if kicker:
        fk = font("Poppins-SemiBold.ttf", 36)
        kw = d.textlength(kicker, font=fk)
        d.text(((W - kw) / 2, y), kicker, font=fk, fill=AMBER + (255,))
        y += 78

    d.rectangle([(W - 96) / 2, y, (W + 96) / 2, y + 6], fill=AMBER + (255,))
    y += 62

    fb = font("Poppins-Bold.ttf", 92)
    for ln in lines:
        lw = d.textlength(ln, font=fb)
        size = 92
        while lw > W - 150 and size > 54:
            size -= 4
            fb = font("Poppins-Bold.ttf", size)
            lw = d.textlength(ln, font=fb)
        d.text(((W - lw) / 2, y), ln, font=fb, fill=LIGHT + (255,))
        y += int(size * 1.22)
        fb = font("Poppins-Bold.ttf", 92)

    if footer:
        ff = font("Poppins-Medium.ttf", 40)
        fw = d.textlength(footer, font=ff)
        d.text(((W - fw) / 2, y + 46), footer, font=ff, fill=(150, 150, 142, 255))

    if logo and os.path.exists(logo):
        mark = Image.open(logo).convert("RGBA")
        scale = 360 / mark.width
        mark = mark.resize((360, int(mark.height * scale)), Image.LANCZOS)
        img.alpha_composite(mark, ((W - mark.width) // 2, y + 130))

    img.convert("RGB").save(path, quality=96)
    return path


def title_overlay(lines, path, kicker=None, y0=1300, band_h=380):
    """Tytuł otwierający — pas na obrazie, NIE pełnoklatkowa plansza.

    Czarna płachta na starcie kosztuje pierwsze sekundy, w których widz decyduje,
    czy zostaje. Napis kładziemy więc na pierwszym prawdziwym kadrze (dzielony
    ekran: twarz + kokpit agentów), a pas siada tam, gdzie normalnie idą napisy —
    dzięki temu nic się nie nakłada.
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rounded(d, [54, y0, W - 54, y0 + band_h], 30, INK + (232,))
    d.rounded_rectangle([54, y0, W - 54, y0 + band_h], radius=30,
                        outline=AMBER + (140,), width=3)

    y = y0 + 38
    if kicker:
        fk = font("Poppins-SemiBold.ttf", 32)
        kw = d.textlength(kicker, font=fk)
        d.text(((W - kw) / 2, y), kicker, font=fk, fill=AMBER + (255,))
        y += 62

    for ln in lines:
        size = 82
        fb = font("Poppins-Bold.ttf", size)
        while d.textlength(ln, font=fb) > W - 180 and size > 48:
            size -= 4
            fb = font("Poppins-Bold.ttf", size)
        lw = d.textlength(ln, font=fb)
        d.text(((W - lw) / 2, y), ln, font=fb, fill=LIGHT + (255,))
        y += int(size * 1.18)
    img.save(path)
    return path


def question_plate(lines, path, kicker=None, footer=None, logo=None):
    """Finał jako PYTANIE na żywym kadrze, nie napis na czarnym tle.

    Pełnoklatkowa nakładka RGBA: przyciemnienie całości (żeby cokolwiek dało się
    przeczytać na jasnej piaszczystej drodze) plus mocniejszy pas pod tekstem.
    Kadr pod spodem zostaje widoczny — o to chodzi, bo domknięcie ma wracać
    do miejsca, w którym short się zaczął.
    """
    img = Image.new("RGBA", (W, H), INK + (150,))
    d = ImageDraw.Draw(img)

    block_h = 150 + 118 * len(lines) + (150 if logo else 60)
    y0 = (H - block_h) // 2
    rounded(d, [54, y0, W - 54, y0 + block_h], 34, INK + (210,))
    d.rounded_rectangle([54, y0, W - 54, y0 + block_h], radius=34,
                        outline=AMBER + (150,), width=3)

    y = y0 + 46
    if kicker:
        fk = font("Poppins-SemiBold.ttf", 32)
        kw = d.textlength(kicker, font=fk)
        d.text(((W - kw) / 2, y), kicker, font=fk, fill=AMBER + (255,))
        y += 54
    d.rectangle([(W - 96) / 2, y, (W + 96) / 2, y + 5], fill=AMBER + (255,))
    y += 46

    for ln in lines:
        size = 80
        fb = font("Poppins-Bold.ttf", size)
        while d.textlength(ln, font=fb) > W - 170 and size > 46:
            size -= 3
            fb = font("Poppins-Bold.ttf", size)
        lw = d.textlength(ln, font=fb)
        d.text(((W - lw) / 2, y), ln, font=fb, fill=LIGHT + (255,))
        y += 118

    if footer:
        ff = font("Poppins-Medium.ttf", 38)
        fw = d.textlength(footer, font=ff)
        d.text(((W - fw) / 2, y + 4), footer, font=ff, fill=(168, 168, 158, 255))
        y += 62

    if logo and os.path.exists(logo):
        mark = Image.open(logo).convert("RGBA")
        mark = mark.resize((330, int(mark.height * 330 / mark.width)), Image.LANCZOS)
        img.alpha_composite(mark, ((W - mark.width) // 2, y + 10))

    img.save(path)
    return path


def main():
    os.makedirs(OV, exist_ok=True)
    caps = os.path.join(OV, "captions")
    import subprocess
    media_len = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", os.path.join(BUILD, "rough.mp4")],
        capture_output=True, text=True).stdout.strip())
    shots, end = build_captions(os.path.join(BUILD, "work", "rough.json"), caps,
                                media_len)

    lst = os.path.join(OV, "captions.txt")
    with open(lst, "w") as fh:
        for path, dur in shots:
            fh.write(f"file '{path}'\nduration {dur:.4f}\n")
        fh.write(f"file '{shots[-1][0]}'\n")   # concat wymaga powtórzenia ostatniej
    print(f"napisy: {len(shots)} okien, do {end:.2f}s → {lst}")

    badge("PRZEZ CAŁĄ NOC", "6 agentów", os.path.join(OV, "badge-agenci.png"))
    badge("MATERIAŁU ZE SPOTKAŃ", "5 godzin", os.path.join(OV, "badge-godziny.png"))
    badge("BIEGU", "20 minut", os.path.join(OV, "badge-bieg.png"))
    badge("PRZYGOTOWANE PRZEZ NOC", "3 odcinki", os.path.join(OV, "badge-odcinki.png"))

    title_overlay(["6 agentów AI.", "Jedna noc."], os.path.join(OV, "title.png"),
                  kicker="ROBOTA, KTÓRA DZIAŁA SIĘ BEZE MNIE")
    question_plate(["A co Twoja firma", "zrobiłaby przez noc?"],
                   os.path.join(OV, "outro-question.png"),
                   kicker="TAK WYGLĄDA PRACA Z AGENTAMI AI",
                   footer="flowbiz.pl",
                   logo=os.path.join(HERE, "flowbiz-white-notag.png"))
    print(f"plansze i plakietki → {OV}")


if __name__ == "__main__":
    main()
