"""Makiety systemu do odcinków — ekran produktu z HTML zamiast nagrania ekranu.

Makieta pokazuje MECHANIZM, o którym właśnie mowa, nie dekorację; nazwy klientów nie
padają (na nagraniach też nie). W storyboardzie:

  {"type": "mockup", "name": "match", "at": "…", "until": "…"}

Każda funkcja dostaje kompozycję (paleta, format, uid) i okno czasu, zwraca HTML wnętrza
planszy, a animacje dopisuje do comp.js. CSS makiet jest w MOCKUP_STYLE (format STYLE).
"""
import html


def esc(text):
    return html.escape(text, quote=True)

# Ekran dopasowania z ep-doram (~7:00): „mogło być pokazywane w kilku różnych kolorach —
# nie dopasowałem, na 80% to ten produkt albo na 100%”. Jedną pozycję poprawia człowiek
# i system ją zapamiętuje na następne zamówienie.
MATCH_ROWS = [
    ("Gartenstuhl Alu, grau", "Krzesło ogrodowe aluminiowe, szare", 100),
    ("Sitzkissen 45×45 anthrazit", "Poduszka na siedzisko 45×45, antracyt", 100),
    ("Bench cushion 120 beige", "Poduszka na ławkę 120 cm, beżowa", 80),
    ("Auflage Hochlehner Dessin 42", "Poduszka na krzesło z wysokim oparciem, wzór 42", 0),
    ("Sonnenschirm 3 m", "Parasol ogrodowy 3 m", 100),
]


def badge(score):
    if score >= 100:
        return '<span class="mk-badge ok">100%</span>'
    if score:
        return f'<span class="mk-badge mid">{score}%</span>'
    return '<span class="mk-badge no">brak</span>'


def mock_slate(comp, *args, **kwargs):
    """Plansza makiety — klasa „mock”: w palecie forest makieta stoi na jasnej karcie (13.10)."""
    return comp.slate(*args, cls="mock", **kwargs)

def match(comp, ev, start, end):
    rows = []
    for i, (theirs, ours, score) in enumerate(MATCH_ROWS):
        fixed = score == 0
        product = ('<span class="mk-empty">nie dopasowano</span>'
                   f'<span class="mk-fixed">{esc(ours)}</span>') if fixed else esc(ours)
        rows.append(f'<div class="mk-row{" mk-fix" if fixed else ""}" data-i="{i}">'
                    f'<span class="mk-theirs">{esc(theirs)}</span><span class="mk-ours">{product}</span>'
                    f'<span class="mk-score">{badge(score)}{badge(100) if fixed else ""}'
                    f'{"<span class=mk-memo>zapamiętane</span>" if fixed else ""}</span></div>')
    inner = (f'<div class="mk-window"><div class="mk-bar"><i></i><i></i><i></i>'
             f'<span>Import zamówienia · zamowienie_kontrahenta.xlsx</span></div>'
             f'<div class="mk-head"><span>Pozycja od kontrahenta</span><span>Produkt w systemie</span><span>Pewność</span></div>'
             f'{"".join(rows)}'
             f'<div class="mk-foot"><b>4 z 5</b> dopasowane automatycznie · <b class="mk-foot-fix">1 poprawka → zapamiętana</b></div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .mk-row",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.35,stagger:0.18,ease:"power2.out"}},{q(start + 0.3)});')
    comp.js.append(f'tl.fromTo("#{sid} .mk-badge",{{scale:0}},{{scale:1,duration:0.3,stagger:0.18,ease:"back.out(2)"}},{q(start + 0.6)});')
    # poprawka człowieka w drugiej połowie planszy: brak → produkt, czerwony → zielony, „zapamiętane”
    if end - start < 4.0:
        raise SystemExit(f"makieta match @ {start:.1f}: {end - start:.1f} s — za krótko, żeby pokazać poprawkę (min. 4 s)")
    fix_at = q(min(start + max(2.5, (end - start) * 0.55), end - 1.6))
    comp.js.append(f'tl.set("#{sid} .mk-fix .mk-fixed, #{sid} .mk-fix .mk-badge.ok, #{sid} .mk-memo, #{sid} .mk-foot-fix",{{opacity:0}},{q(start)});')
    comp.js.append(f'tl.to("#{sid} .mk-fix",{{backgroundColor:"rgba(245,166,35,0.10)",duration:0.25}},{fix_at});')
    comp.js.append(f'tl.to("#{sid} .mk-fix .mk-empty, #{sid} .mk-fix .mk-badge.no",{{opacity:0,duration:0.2}},{fix_at});')
    comp.js.append(f'tl.to("#{sid} .mk-fix .mk-fixed, #{sid} .mk-fix .mk-badge.ok",{{opacity:1,duration:0.3}},{q(fix_at + 0.2)});')
    comp.js.append(f'tl.fromTo("#{sid} .mk-memo",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.35,ease:"back.out(2)"}},{q(fix_at + 0.6)});')
    comp.js.append(f'tl.to("#{sid} .mk-foot-fix",{{opacity:1,duration:0.3}},{q(fix_at + 0.9)});')


# Telegram z ep-vacuactiv (~9:50 i ~10:40): „właściciel dostaje codziennie powiadomienie
# na temat etapów, postępów produkcji, opóźnień, kluczowych klientów” oraz „utwórz mi
# zamówienie dla tego klienta → zduplikować czy nowe? → w trzech kliknięciach gotowe”.
TELEGRAM = {
    # ep-open-mercato-offers (~2:20): „asystent czyta maile… w locie przygotowuje szkic oferty…
    # powiadomienie na Telegrama, możesz zaakceptować albo poprosić o korektę”
    "offer": [
        ("bot", "📩 Nowe zapytanie z maila: <b>3 bieżnie, 2 atlasy</b>"),
        ("bot", "📝 Szkic oferty gotowy · <b>5 pozycji</b>, ceny z magazynu"),
        ("buttons", ["Zatwierdź", "Popraw"]),
        ("me", "Zatwierdź"),
        ("bot", "✅ <b>Oferta wysłana.</b> Czas: 5 minut."),
    ],
    "brief": [
        ("bot", "<b>Raport poranny · 7:00</b>"),
        ("bot", "🏭 Produkcja: <b>14 zleceń</b> w toku, 3 na etapie montażu"),
        ("bot", "⚠️ Opóźnione: <b>2 zlecenia</b> · brak ram stalowych"),
        ("bot", "📦 Dziś wysyłka: <b>6 zamówień</b>"),
        ("bot", "⭐ Kluczowi klienci: wszystkie zamówienia w terminie"),
        ("buttons", ["Szczegóły", "Opóźnienia"]),
    ],
    "order": [
        ("me", "Utwórz zamówienie dla klienta z Gdańska"),
        ("bot", "Ostatnie zamówienie tego klienta: <b>12 pozycji</b>, 3 tygodnie temu."),
        ("buttons", ["Zduplikuj", "Nowe zamówienie"]),
        ("me", "Zduplikuj"),
        ("bot", "✅ <b>Zamówienie utworzone.</b> Wysłać ofertę do klienta?"),
        ("buttons", ["Wyślij ofertę", "Popraw"]),
    ],
}


def telegram(comp, ev, start, end):
    from package import logo
    lines = TELEGRAM[ev.get("mode", "brief")]
    bubbles = []
    for i, (who, body) in enumerate(lines):
        if who == "buttons":
            bubbles.append(f'<div class="tg-msg tg-buttons" data-i="{i}">' + "".join(f"<span>{esc(b)}</span>" for b in body) + "</div>")
        else:
            bubbles.append(f'<div class="tg-msg tg-{who}" data-i="{i}">{body}</div>')
    inner = (f'<div class="tg-phone"><div class="tg-top">{logo("telegram", 46, "#26A5E4")}'
             f'<div><b>Asystent firmy</b><span>bot · online</span></div></div>'
             f'<div class="tg-chat">{"".join(bubbles)}</div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    step = min(1.1, max(0.45, (end - start - 1.2) / len(lines)))
    for i in range(len(lines)):
        comp.js.append(f'tl.fromTo("#{sid} .tg-msg[data-i=\'{i}\']",{{opacity:0,y:24,scale:0.96}},'
                       f'{{opacity:1,y:0,scale:1,duration:0.3,ease:"power2.out"}},{comp.q(start + 0.4 + i * step)});')


# Panel klienta B2B z ep-rezon (~5:50): „klient sam się loguje, sam może złożyć zamówienie,
# sam widzi statusy… pracownik w biurze dostaje powiadomienie, że wpadło nowe zamówienie”.
# Każda miejscowość ma swój wzór — stąd „· Ustka” przy każdym produkcie.
B2B_PRODUCTS = [("Magnes", "Ustka", 120), ("Kubek", "Ustka", 36), ("Brelok", "Ustka", 80)]
B2B_ORDERS = [("#1042", "W produkcji", "mid"), ("#1037", "Wysłane", "ok")]


B2B_REP = [("Sklep z pamiątkami, Ustka", "#1049", "W produkcji", "mid"), ("Pamiątki, Łeba", "#1050", "Nowe", "no"),
           ("Kiosk przy plaży, Rowy", "#1044", "Wysłane", "ok")]


def b2b_rep(comp, ev, start, end):
    """Panel handlowca z ep-rezon (~6:40): „handlowiec widzi zamówienia swoich klientów,
    a klient dalej widzi tylko swoje” + „wprowadza za klienta zamówienie”."""
    rows = "".join(f'<div class="b2b-order" data-i="{i}"><span>{esc(c)}</span><b>{n}</b><span class="mk-badge {cls}">{esc(st)}</span></div>'
                   for i, (c, n, st, cls) in enumerate(B2B_REP))
    inner = (f'<div class="mk-window b2b"><div class="mk-bar"><i></i><i></i><i></i><span>Panel handlowca · moi klienci</span></div>'
             f'<div class="b2b-side b2b-rep">{rows}<div class="b2b-btn">+ Zamów za klienta</div></div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    comp.js.append(f'tl.fromTo("#{sid} .b2b-order",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:0.35,stagger:0.25}},{comp.q(start + 0.3)});')
    comp.js.append(f'tl.fromTo("#{sid} .b2b-btn",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.35,ease:"back.out(2)"}},{comp.q(start + 1.4)});')


def b2b(comp, ev, start, end):
    if ev.get("mode") == "rep":
        return b2b_rep(comp, ev, start, end)
    tiles = "".join(f'<div class="b2b-tile" data-i="{i}"><div class="b2b-pic">{esc(name[0])}</div>'
                    f'<b>{esc(name)} · {esc(town)}</b><span class="b2b-qty">{qty} szt.</span></div>'
                    for i, (name, town, qty) in enumerate(B2B_PRODUCTS))
    orders = "".join(f'<div class="b2b-order"><b>{num}</b><span class="mk-badge {cls}">{esc(status)}</span></div>'
                     for num, status, cls in B2B_ORDERS)
    inner = (f'<div class="mk-window b2b"><div class="mk-bar"><i></i><i></i><i></i><span>Panel klienta · Sklep z pamiątkami, Ustka</span></div>'
             f'<div class="b2b-body"><div class="b2b-cat"><div class="b2b-h">Katalog · wzory „Ustka”</div><div class="b2b-tiles">{tiles}</div>'
             f'<div class="b2b-btn">Złóż zamówienie</div></div>'
             f'<div class="b2b-side"><div class="b2b-h">Moje zamówienia</div>'
             f'<div class="b2b-order b2b-new"><b>#1049</b><span class="mk-badge no b2b-new-badge">Nowe</span></div>{orders}</div></div>'
             f'<div class="b2b-toast">🔔 Biuro: wpadło nowe zamówienie #1049</div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q, span = comp.q, end - start
    if span < 4.0:
        raise SystemExit(f"makieta b2b @ {start:.1f}: {span:.1f} s — za krótko na zamówienie i zmianę statusu (min. 4 s)")
    comp.js.append(f'tl.fromTo("#{sid} .b2b-tile",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.35,stagger:0.2}},{q(start + 0.3)});')
    click = q(start + max(1.8, span * 0.4))
    comp.js.append(f'tl.set("#{sid} .b2b-new, #{sid} .b2b-toast",{{opacity:0}},{q(start)});')
    comp.js.append(f'tl.to("#{sid} .b2b-btn",{{scale:0.94,duration:0.12,yoyo:true,repeat:1}},{click});')
    comp.js.append(f'tl.fromTo("#{sid} .b2b-new",{{opacity:0,x:40}},{{opacity:1,x:0,duration:0.35}},{q(click + 0.3)});')
    comp.js.append(f'tl.fromTo("#{sid} .b2b-toast",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.35}},{q(click + 0.9)});')
    # status rusza: Nowe → W produkcji
    comp.js.append(f'tl.call(function(){{var b=document.querySelector("#{sid} .b2b-new-badge");if(b){{b.textContent="Nowe";b.className="mk-badge no b2b-new-badge";}}}},null,{q(click + 0.3)});')
    comp.js.append(f'tl.call(function(){{var b=document.querySelector("#{sid} .b2b-new-badge");if(b){{b.textContent="W produkcji";b.className="mk-badge mid b2b-new-badge";}}}},null,{q(max(click + 0.8, min(end - 0.8, click + 2.2)))});')


# Trzy Excele z ep-doram (~2:30): „klient ma trzech kontrahentów głównych i każdy z nich
# trochę inaczej te Excele przygotowywał” — ta sama pozycja, inne kolumny i nazwy.
EXCELS = [
    ("kontrahent_A.xlsx", ["Art.-Nr.", "Bezeichnung", "Menge"], ["GS-114", "Gartenstuhl Alu, grau", "40"]),
    ("kontrahent_B.xlsx", ["Item", "Description", "Qty", "Price"], ["114", "Garden chair alu", "40", "€38"]),
    ("kontrahent_C.xlsx", ["Pos.", "Menge", "Artikel"], ["7", "40", "Stuhl Alu grau"]),
]


def excels(comp, ev, start, end):
    sheets = []
    for i, (name, head, row) in enumerate(EXCELS):
        cols = "".join(f"<span>{esc(h)}</span>" for h in head)
        cells = "".join(f"<span>{esc(c)}</span>" for c in row)
        # kolumna z nazwą produktu szersza — to ją porównujemy między kontrahentami
        grid = " ".join("2.2fr" if len(c) > 8 else "1fr" for c in row)
        sheets.append(f'<div class="xl" data-i="{i}" style="--grid:{grid}"><div class="xl-name">{esc(name)}</div>'
                      f'<div class="xl-row xl-head">{cols}</div><div class="xl-row xl-hit">{cells}</div>'
                      f'<div class="xl-row"><span></span></div><div class="xl-row"><span></span></div></div>')
    inner = f'<div class="xl-wrap">{"".join(sheets)}</div><div class="xl-foot">ta sama pozycja · <b>3 układy kolumn</b> · 3 nazwy</div>'
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .xl",{{opacity:0,y:50,rotation:-2}},{{opacity:1,y:0,rotation:0,duration:0.45,stagger:0.25,ease:"back.out(1.5)"}},{q(start + 0.3)});')
    comp.js.append(f'tl.fromTo("#{sid} .xl-hit",{{backgroundColor:"rgba(245,166,35,0)"}},{{backgroundColor:"rgba(245,166,35,0.22)",duration:0.3,stagger:0.25}},{q(start + 1.4)});')
    comp.js.append(f'tl.fromTo("#{sid} .xl-foot",{{opacity:0}},{{opacity:1,duration:0.3}},{q(start + 2.2)});')


# Etykiety z ep-doram (~9:40): „system bierze cztery numery, generuje PDF od razu gotowy,
# po minucie masz PDF z 40 stronami etykiet”.
def labels(comp, ev, start, end):
    bars = "".join(f'<i style="width:{w}px"></i>' for w in (4, 2, 6, 2, 3, 5, 2, 4, 2, 6, 3, 2, 5, 2, 4, 3, 6, 2, 3, 2, 5, 4, 2, 6))
    pages = "".join(f'<div class="lb-page" data-i="{i}"><b>ZAM-2026-0{418 + i}</b><div class="lb-bars">{bars}</div>'
                    f'<span>Paczka {i + 1}/40</span></div>' for i in range(5))
    inner = (f'<div class="lb-wrap"><div class="lb-panel"><div class="b2b-h">Zamówienie · 4 numery</div>'
             f'<div class="lb-nums"><span>ZAM 0418</span><span>PROD 114</span><span>CZ 07</span><span>PACZ 40</span></div>'
             f'<div class="b2b-btn lb-btn">Generuj etykiety</div><div class="lb-done">✓ PDF gotowy · 40 stron</div></div>'
             f'<div class="lb-stack">{pages}</div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q, click = comp.q, start + 1.2
    comp.js.append(f'tl.set("#{sid} .lb-page, #{sid} .lb-done",{{opacity:0}},{q(start)});')
    comp.js.append(f'tl.to("#{sid} .lb-btn",{{scale:0.94,duration:0.12,yoyo:true,repeat:1}},{q(click)});')
    comp.js.append(f'tl.fromTo("#{sid} .lb-page",{{opacity:0,x:-160,rotation:-8}},{{opacity:1,x:function(i){{return i*26}},y:function(i){{return i*-18}},rotation:function(i){{return -4+i*2}},'
                   f'duration:0.4,stagger:0.18,ease:"power3.out"}},{q(click + 0.3)});')
    comp.js.append(f'tl.fromTo("#{sid} .lb-done",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.35}},{q(click + 1.5)});')


# Synchronizacja z ep-rezon (~2:05): „integracja z PC Business… synchronizujemy codziennie…
# ceny, zamówienia, ile rzeczy na magazynie… handlowcy, osoby z produkcji mają dostęp”.
def sync(comp, ev, start, end):
    from package import logo
    chips = "".join(f'<span class="sy-chip" data-i="{i}">{esc(c)}</span>' for i, c in enumerate(["Ceny", "Zamówienia", "Stany magazynu"]))
    users = "".join(f'<div class="sy-user" data-i="{i}"><i>{esc(u[0])}</i>{esc(u)}</div>' for i, u in enumerate(["Handlowcy", "Produkcja", "Biuro"]))
    inner = (f'<div class="sy"><div class="sy-row"><div class="sy-box"><b>PC Business</b><span>księgowość i sprzedaż</span></div>'
             f'<div class="sy-pipe"><div class="sy-line"></div>{chips}<div class="sy-clock">↻ raz na dobę</div></div>'
             f'<div class="sy-box sy-om">{logo("openmercato", 64)}<span>jedno źródło prawdy</span></div></div>'
             f'<div class="sy-users">{users}</div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .sy-box",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.4,stagger:0.2}},{q(start + 0.2)});')
    comp.js.append(f'tl.fromTo("#{sid} .sy-line",{{scaleX:0}},{{scaleX:1,duration:0.5,ease:"power2.out"}},{q(start + 0.8)});')
    comp.js.append(f'tl.fromTo("#{sid} .sy-chip",{{opacity:0,x:-160}},{{opacity:1,x:0,duration:0.5,stagger:0.3,ease:"power2.out"}},{q(start + 1.1)});')
    comp.js.append(f'tl.fromTo("#{sid} .sy-clock",{{opacity:0}},{{opacity:1,duration:0.3}},{q(start + 2.0)});')
    comp.js.append(f'tl.fromTo("#{sid} .sy-user",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.35,stagger:0.15}},{q(start + max(2.6, (end - start) * 0.5))});')


# Trasa handlowca z ep-rezon (~2:45): „objechać z towarem całe wybrzeże albo zimą południe
# Polski”. 05.11 Mateusz: „ta mapka to lipa — to musi być mapa wybrzeża Polski”, więc zamiast
# krzywej: prawdziwy zarys brzegu (uproszczone współrzędne lon/lat, Świnoujście → Hel → Mierzeja
# Wiślana), rzut równoodległościowy z cos(54,4°), bus jedzie wzdłuż brzegu od miasta do miasta.
COAST_LONLAT = [
    (14.22, 53.93), (14.45, 53.93), (14.77, 54.03), (14.93, 54.06), (15.07, 54.10), (15.27, 54.15),
    (15.57, 54.18), (15.75, 54.22), (16.06, 54.26), (16.40, 54.44), (16.53, 54.54), (16.85, 54.59),
    (17.05, 54.67), (17.55, 54.76), (17.97, 54.80), (18.30, 54.83), (18.42, 54.79), (18.68, 54.70),
    (18.82, 54.60), (18.79, 54.605), (18.66, 54.685), (18.46, 54.765), (18.41, 54.72), (18.50, 54.63),
    (18.55, 54.52), (18.57, 54.44), (18.63, 54.41), (18.78, 54.37), (19.11, 54.33), (19.45, 54.38),
    (19.63, 54.45),
]
# (nazwa, lon, lat, przesunięcie podpisu x) — Ustka i Rowy leżą 15 km od siebie, podpisy rozsunięte
COAST_TOWNS = [("Kołobrzeg", 15.57, 54.18, 0), ("Ustka", 16.85, 54.59, -62), ("Rowy", 17.05, 54.67, 50), ("Łeba", 17.55, 54.76, 30)]
COAST_LANDMARKS = [("Świnoujście", 14.25, 53.91, 70, 26), ("Gdańsk", 18.64, 54.36, 0, 44)]
COAST_W, COAST_H = 1220, 420


def coast_xy(lon, lat):
    k = 352.0
    return round(30 + (lon - 14.15) * 0.582 * k, 1), round(40 + (54.90 - lat) * k, 1)


def coast(comp, ev, start, end):
    shore = [coast_xy(*p) for p in COAST_LONLAT]
    line = "M " + " L ".join(f"{x} {y}" for x, y in shore)
    sea = line + f" L {COAST_W} {shore[-1][1]} L {COAST_W} 0 L 0 0 L 0 {shore[0][1]} Z"
    land = line + f" L {COAST_W} {shore[-1][1]} L {COAST_W} {COAST_H} L 0 {COAST_H} L 0 {shore[0][1]} Z"
    # trasa: brzegiem, kilkanaście pikseli w głąb lądu, od Kołobrzegu do Łeby
    leg = [(x, y + 14) for (lon, lat), (x, y) in zip(COAST_LONLAT, shore) if 15.57 <= lon <= 17.55]
    route = "M " + " L ".join(f"{x} {y}" for x, y in leg)
    towns = "".join(f'<g class="co-town" data-i="{i}"><circle cx="{x}" cy="{y + 14}" r="12"/><text x="{x + dx}" y="{y + 66}">{esc(n)}</text></g>'
                    for i, (n, x, y, dx) in enumerate((n, *coast_xy(lon, lat), dx) for n, lon, lat, dx in COAST_TOWNS))
    marks = "".join(f'<text class="co-mark" x="{x + dx}" y="{y + dy}">{esc(n)}</text>'
                    for n, x, y, dx, dy in ((n, *coast_xy(lon, lat), dx, dy) for n, lon, lat, dx, dy in COAST_LANDMARKS))
    inner = (f'<div class="co"><div class="co-kicker">Sezon w trasie · wybrzeże</div><svg viewBox="0 0 {COAST_W} {COAST_H}" class="co-map">'
             f'<path class="co-sea" d="{sea}"/><path class="co-land" d="{land}"/><path class="co-shore" d="{line}"/>'
             f'<text class="co-sea-label" x="560" y="70">Morze Bałtyckie</text>{marks}'
             f'<path class="co-route" d="{route}" pathLength="1"/>{towns}'
             f'<g class="co-van"><rect x="-26" y="-16" width="52" height="30" rx="6"/></g></svg>'
             f'<div class="co-note">Towar wyprodukowany „na zapas” — <b>dowiadujesz się o nadwyżce na końcu sezonu</b></div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q, run = comp.q, max(2.0, (end - start) - 2.0)
    frames = ",".join(f"{{x:{x},y:{y}}}" for x, y in leg[1:])
    comp.js.append(f'tl.fromTo("#{sid} .co-route",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{run},ease:"none"}},{q(start + 0.4)});')
    comp.js.append(f'tl.fromTo("#{sid} .co-town",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.3,stagger:{run / 4}}},{q(start + 0.4)});')
    comp.js.append(f'tl.fromTo("#{sid} .co-van",{{x:{leg[0][0]},y:{leg[0][1]}}},{{keyframes:[{frames}],duration:{run},ease:"none"}},{q(start + 0.4)});')
    comp.js.append(f'tl.fromTo("#{sid} .co-note",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.4}},{q(start + run * 0.6)});')


# Paczki z ep-marpasz (~1:35 i ~3:10): wcześniej komentarz → Excel → etykieta po kolei dla
# każdego z czterech worków; teraz AI łączy podobne zamówienia w koszyk i „wygeneruj etykiety”.
def parcels(comp, ev, start, end):
    after = ev.get("mode") == "after"
    sacks = "".join(f'<div class="pc-sack" data-i="{i}"><b>25 kg</b><span class="pc-label">etykieta {i + 1}</span></div>' for i in range(4))
    if after:
        side = ('<div class="pc-flow"><div class="pc-step pc-on">AI łączy podobne zamówienia</div>'
                '<div class="pc-step pc-on">1 koszyk · 4 paczki</div><div class="b2b-btn pc-btn">Wygeneruj etykiety</div></div>')
        title = "Teraz · jedno kliknięcie"
    else:
        side = ('<div class="pc-flow"><div class="pc-step">Komentarz w zamówieniu</div><div class="pc-step">Przeklej do Excela</div>'
                '<div class="pc-step">Drukuj etykietę</div><div class="pc-loop">↻ × 4 na jedno zamówienie</div></div>')
        title = "Wcześniej · ręcznie"
    inner = (f'<div class="pc"><div class="co-kicker">{title}</div><div class="pc-row"><div class="pc-sacks">{sacks}</div>{side}</div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .pc-sack",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.35,stagger:0.15}},{q(start + 0.2)});')
    comp.js.append(f'tl.set("#{sid} .pc-label",{{opacity:0}},{q(start)});')
    if after:
        comp.js.append(f'tl.fromTo("#{sid} .pc-step",{{opacity:0,x:40}},{{opacity:1,x:0,duration:0.35,stagger:0.3}},{q(start + 0.8)});')
        click = start + 2.0
        comp.js.append(f'tl.to("#{sid} .pc-btn",{{scale:0.94,duration:0.12,yoyo:true,repeat:1}},{q(click)});')
        comp.js.append(f'tl.to("#{sid} .pc-label",{{opacity:1,duration:0.25,stagger:0.08}},{q(click + 0.3)});')
    else:
        comp.js.append(f'tl.fromTo("#{sid} .pc-step",{{opacity:0,x:40}},{{opacity:1,x:0,duration:0.3,stagger:0.35}},{q(start + 0.8)});')
        step = max(0.6, (end - start - 3.0) / 4)
        comp.js.append(f'tl.to("#{sid} .pc-label",{{opacity:1,duration:0.2,stagger:{step}}},{q(start + 2.2)});')
        comp.js.append(f'tl.fromTo("#{sid} .pc-loop",{{opacity:0}},{{opacity:1,duration:0.3}},{q(start + 2.0)});')


# Katalog AI z ep-marpasz (~6:00): „AI odczytuje faktury, buduje listę produktów, przygotowuje
# opisy pod każdą platformę, sprawdza magazyn i jednym kliknięciem dodaje wszystko”.
def catalog(comp, ev, start, end):
    from package import logo, LOGO_COLORS
    items = "".join(f'<div class="ct-item" data-i="{i}">{esc(n)}</div>'
                    for i, n in enumerate(["Karma dla psa 15 kg", "Pasza dla kur 25 kg", "Przysmaki dla kota"]))
    chans = "".join(f'<div class="ct-chan" data-i="{i}">{logo(l, 40, LOGO_COLORS.get(l)) if l else "<b>E</b>"}<span>{esc(n)}</span></div>'
                    for i, (l, n) in enumerate([("allegro", "Allegro"), ("wordpress", "Sklep"), ("", "Erli")]))
    inner = (f'<div class="ct"><div class="ct-col"><div class="b2b-h">Faktura od dostawcy</div><div class="ct-doc"><i></i><i></i><i></i><i></i></div></div>'
             f'<div class="sy-line ct-arrow"></div>'
             f'<div class="ct-col"><div class="b2b-h">AI · lista produktów</div>{items}</div>'
             f'<div class="sy-line ct-arrow"></div>'
             f'<div class="ct-col"><div class="b2b-h">Opisy pod platformy</div>{chans}<div class="b2b-btn ct-btn">Dodaj do magazynu</div></div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .ct-doc",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.4}},{q(start + 0.2)});')
    comp.js.append(f'tl.fromTo("#{sid} .ct-arrow",{{scaleX:0}},{{scaleX:1,duration:0.4,stagger:1.4}},{q(start + 0.7)});')
    comp.js.append(f'tl.fromTo("#{sid} .ct-item",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.3,stagger:0.25}},{q(start + 1.0)});')
    comp.js.append(f'tl.fromTo("#{sid} .ct-chan",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.3,stagger:0.25}},{q(start + 2.4)});')
    comp.js.append(f'tl.fromTo("#{sid} .ct-btn",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.35,ease:"back.out(2)"}},{q(start + 3.4)});')


# Oferty z ep-open-mercato-offers (~0:45): „każdy ma swoją wersję PDF-a, z takim logiem,
# z innym logotypem… każdy ma jakiś system wyceny, wszystko rozmyte”.
def pdfs(comp, ev, start, end):
    looks = [("#2B6CB0", "OFERTA", -9), ("#C05621", "Wycena", 6), ("#2F855A", "Oferta handlowa", -3), ("#6B46C1", "PROPOZYCJA", 10), ("#B7791F", "oferta_v3_final", -6)]
    docs = "".join(f'<div class="pf" data-i="{i}" style="--c:{c};--r:{r}deg;left:{80 + i * 200}px;top:{60 + (i % 2) * 70}px">'
                   f'<div class="pf-head"><i></i><b>{esc(t)}</b></div><div class="pf-lines"><i></i><i></i><i></i><i></i><i></i></div></div>'
                   for i, (c, t, r) in enumerate(looks))
    inner = f'<div class="pfs"><div class="co-kicker">Każdy ma swoją wersję oferty</div><div class="pf-table">{docs}</div><div class="xl-foot">5 handlowców · <b>5 szablonów</b> · 5 sposobów wyceny</div></div>'
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    comp.js.append(f'tl.fromTo("#{sid} .pf",{{opacity:0,y:-200,rotation:0}},{{opacity:1,y:0,rotation:function(i,el){{return getComputedStyle(el).getPropertyValue("--r")}},duration:0.45,stagger:0.22,ease:"back.out(1.4)"}},{comp.q(start + 0.3)});')
    comp.js.append(f'tl.fromTo("#{sid} .xl-foot",{{opacity:0}},{{opacity:1,duration:0.3}},{comp.q(start + 1.8)});')


# Lejek z ep-open-mercato-offers (~1:35): „na 20 wystawionych ofert 3 stały się zamówieniem”.
def funnel(comp, ev, start, end):
    dots = "".join(f'<i class="fn-dot{" fn-win" if i in (3, 11, 17) else ""}" data-i="{i}"></i>' for i in range(20))
    inner = (f'<div class="fn"><div class="co-kicker">Wystawione oferty</div><div class="fn-dots">{dots}</div>'
             f'<div class="fn-result"><b class="fn-num">3</b><span>zamówienia z 20 ofert — <b>dlaczego?</b></span></div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .fn-dot",{{opacity:0,scale:0}},{{opacity:1,scale:1,duration:0.2,stagger:0.05}},{q(start + 0.3)});')
    comp.js.append(f'tl.to("#{sid} .fn-dot:not(.fn-win)",{{opacity:0.18,duration:0.4}},{q(start + 1.8)});')
    comp.js.append(f'tl.fromTo("#{sid} .fn-result",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.4}},{q(start + 2.2)});')


# Okno kontekstu z ep-vacuactiv (~1:05): „ten Chat przestaje pamiętać moje wytyczne…
# kontekst to pamięć, która się kończy… zaczyna halucynować”.
def context(comp, ev, start, end):
    msgs = ["Wytyczne firmy: ceny netto, rabat max 8%", "Klient A — warunki specjalne", "Oferta dla hali B",
            "Poprawka: dostawa 14 dni", "Nowe zamówienie — 6 pozycji", "Pytanie o termin produkcji",
            "Raport tygodniowy", "Zestawienie kosztów"]
    rows = "".join(f'<div class="cx-msg{" cx-rule" if i == 0 else ""}" data-i="{i}">{esc(m)}</div>' for i, m in enumerate(msgs))
    inner = (f'<div class="cx"><div class="cx-win"><div class="mk-bar"><i></i><i></i><i></i><span>Czat AI · ta sama rozmowa od miesięcy</span></div>'
             f'<div class="cx-feed"><div class="cx-track">{rows}</div></div>'
             f'<div class="cx-meter"><span>Pamięć rozmowy</span><div class="hv-bar"><i></i></div></div></div>'
             f'<div class="cx-warn">⚠ „Rabat 15%? Oczywiście!” — wytyczne wypadły z pamięci</div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q, span = comp.q, end - start
    comp.js.append(f'tl.fromTo("#{sid} .cx-msg",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.25,stagger:{min(0.5, span / 14)}}},{q(start + 0.3)});')
    comp.js.append(f'tl.fromTo("#{sid} .cx-meter i",{{width:"20%"}},{{width:"100%",duration:{q(span * 0.55)},ease:"none"}},{q(start + 0.3)});')
    comp.js.append(f'tl.to("#{sid} .cx-track",{{y:-230,duration:{q(span * 0.35)},ease:"power1.in"}},{q(start + span * 0.35)});')
    comp.js.append(f'tl.to("#{sid} .cx-meter i",{{backgroundColor:"{comp.mock_pal["danger"]}",duration:0.3}},{q(start + span * 0.55)});')
    comp.js.append(f'tl.fromTo("#{sid} .cx-warn",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.4}},{q(start + span * 0.62)});')


# Źródła danych z ep-vacuactiv (~2:05): „dane są w głowach, na kartkach, na mailach i agent AI
# nie ma skąd tych danych pobierać”.
def sources(comp, ev, start, end):
    srcs = "".join(f'<div class="sr-src" data-i="{i}"><b>{icon}</b>{esc(t)}</div>' for i, (icon, t) in enumerate([("🧠", "w głowach"), ("📝", "na kartkach"), ("✉️", "w mailach")]))
    inner = (f'<div class="sr"><div class="sr-srcs">{srcs}</div><div class="sr-gap">✕ brak połączenia</div>'
             f'<div class="sr-agent"><div class="tg-msg tg-me">Ile mamy opóźnionych zleceń?</div><div class="tg-msg tg-bot">Nie wiem. Nie mam dostępu do tych danych.</div></div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .sr-src",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.35,stagger:0.25}},{q(start + 0.2)});')
    comp.js.append(f'tl.fromTo("#{sid} .sr-gap",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.35,ease:"back.out(2)"}},{q(start + 1.2)});')
    comp.js.append(f'tl.fromTo("#{sid} .sr-agent .tg-msg",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.3,stagger:0.8}},{q(start + 1.7)});')


# Excel kierownika vs widok w systemie z ep-vacuactiv (~7:10): „widoki były bardzo bliskie temu
# Excelowi… zapisywały historię etapów… nauka zajęła godzinę”.
BOARD_ROWS = [("ZL-231", "Bieżnia X2", "Spawanie", "ok"), ("ZL-232", "Atlas Pro", "Malowanie", "mid"), ("ZL-233", "Ławka 3D", "Montaż", "ok"), ("ZL-234", "Bieżnia X2", "Opóźnione", "no")]


def board(comp, ev, start, end):
    xl = "".join(f'<div class="xl-row"><span>{a}</span><span>{b}</span><span>{c}</span></div>' for a, b, c, _ in BOARD_ROWS)
    sysr = "".join(f'<div class="bd-row" data-i="{i}"><span>{a}</span><span>{b}</span><span class="mk-badge {cls}">{esc(c)}</span></div>'
                   for i, (a, b, c, cls) in enumerate(BOARD_ROWS))
    inner = (f'<div class="bd"><div class="xl" style="--grid:1fr 1.6fr 1.3fr;width:440px"><div class="xl-name">plan_produkcji.xlsx</div>'
             f'<div class="xl-row xl-head"><span>Zlecenie</span><span>Produkt</span><span>Etap</span></div>{xl}</div>'
             f'<div class="bd-arrow">→</div>'
             f'<div class="mk-window bd-sys"><div class="mk-bar"><i></i><i></i><i></i><span>Tablica produkcji</span></div>{sysr}'
             f'<div class="bd-foot">✓ historia każdego etapu · nauka: <b>1 godzina</b></div></div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .xl",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:0.4}},{q(start + 0.2)});')
    comp.js.append(f'tl.fromTo("#{sid} .bd-arrow",{{opacity:0}},{{opacity:1,duration:0.3}},{q(start + 0.9)});')
    comp.js.append(f'tl.fromTo("#{sid} .bd-row",{{opacity:0,x:40}},{{opacity:1,x:0,duration:0.3,stagger:0.2}},{q(start + 1.2)});')
    comp.js.append(f'tl.fromTo("#{sid} .bd-foot",{{opacity:0}},{{opacity:1,duration:0.3}},{q(start + 2.3)});')


MOCKUPS = {"context": context, "sources": sources, "board": board, "pdfs": pdfs, "funnel": funnel, "match": match, "telegram": telegram, "b2b": b2b, "excels": excels, "labels": labels,
           "sync": sync, "coast": coast, "parcels": parcels, "catalog": catalog}

MOCKUP_STYLE = """
.mk-window{{width:100%;background:{panel};border:2px solid {line};border-radius:28px;overflow:hidden;text-align:left;box-shadow:0 30px 80px rgba(0,0,0,.5)}}
.mk-bar{{display:flex;align-items:center;gap:12px;padding:22px 30px;background:{raised};font-size:26px;color:{muted};font-weight:600}}
.mk-bar i{{width:16px;height:16px;border-radius:50%;background:{line}}} .mk-bar span{{margin-left:16px}}
.mk-head,.mk-row{{display:grid;grid-template-columns:1fr 1.4fr 300px;gap:28px;align-items:center;padding:0 34px}}
.mk-head{{height:70px;font-size:22px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:{muted};border-bottom:2px solid {line}}}
.mk-row{{min-height:96px;font-size:32px;border-bottom:1px solid {line}}}
.mk-theirs{{color:{muted};font-style:italic}} .mk-ours{{font-weight:700;display:grid}} .mk-ours > *{{grid-area:1/1}}
.mk-empty{{color:{danger};font-weight:600}}
.mk-score{{display:grid;justify-items:start;align-items:center;grid-template-columns:auto auto;gap:12px}} .mk-score .mk-badge{{grid-area:1/1}}
.mk-badge{{display:inline-block;padding:8px 18px;border-radius:30px;font-size:26px;font-weight:800}}
.mk-badge.ok{{background:{accent2};color:#0A0A08}} .mk-badge.mid{{background:{accent};color:{on_accent}}} .mk-badge.no{{background:{danger};color:#fff}}
.mk-memo{{grid-column:2;font-size:22px;font-weight:700;color:{accent};border:2px solid {accent};border-radius:20px;padding:4px 12px}}
.mk-foot{{padding:24px 34px;font-size:28px;color:{muted}}} .mk-foot b{{color:{text}}} .mk-foot .mk-foot-fix{{color:{accent}}}
.b2b-body{{display:grid;grid-template-columns:1.5fr 1fr;gap:0}}
.b2b-cat{{padding:30px 34px;border-right:2px solid {line};display:flex;flex-direction:column;gap:24px}}
.b2b-side{{padding:30px 34px;display:flex;flex-direction:column;gap:16px}}
.b2b-h{{font-size:22px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:{muted}}}
.b2b-tiles{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}
.b2b-tile{{background:{raised};border-radius:20px;padding:18px;display:flex;flex-direction:column;gap:10px;font-size:26px}}
.b2b-pic{{height:120px;border-radius:14px;background:linear-gradient(135deg,{accent},{accent2});display:flex;align-items:center;justify-content:center;font-size:64px;font-weight:800;color:#0A0A08}}
.b2b-qty{{color:{muted};font-size:24px}}
.b2b-btn{{align-self:flex-start;padding:18px 34px;border-radius:18px;background:{accent};color:{on_accent};font-size:28px;font-weight:800}}
.b2b-order{{display:flex;justify-content:space-between;align-items:center;padding:18px 22px;border-radius:16px;background:{raised};font-size:28px}}
.b2b-toast{{margin:0 34px 30px;padding:18px 24px;border-radius:16px;border:2px solid {accent};color:{text};font-size:26px;font-weight:600}}
.fmt-v .b2b-body{{grid-template-columns:1fr}} .fmt-v .b2b-cat{{border-right:0;border-bottom:2px solid {line}}}
.sy{{display:flex;flex-direction:column;gap:60px;align-items:center}}
.sy-row{{display:flex;align-items:center;gap:30px}}
.sy-box{{width:330px;height:210px;border-radius:24px;background:{panel};border:2px solid {line};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;font-size:42px;font-weight:700}}
.sy-box span{{font-size:22px;color:{muted}}} .sy-om{{border-color:{accent}}}
.sy-pipe{{position:relative;width:520px;height:200px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px}}
.sy-line{{position:absolute;left:0;right:0;top:50%;height:4px;background:{accent};transform-origin:left center}}
.sy-chip{{position:relative;padding:10px 24px;border-radius:22px;background:{raised};border:2px solid {accent};font-size:30px;font-weight:700}}
.sy-clock{{position:absolute;bottom:-46px;font-size:26px;color:{accent};font-weight:700}}
.sy-users{{display:flex;gap:40px}} .sy-user{{display:flex;align-items:center;gap:14px;font-size:36px;font-weight:700}}
.sy-user i{{width:56px;height:56px;border-radius:50%;background:{accent};color:{on_accent};display:flex;align-items:center;justify-content:center;font-style:normal}}
.co{{width:100%;display:flex;flex-direction:column;align-items:center;gap:20px}}
.co-kicker{{font-size:30px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:{accent}}}
.co-map{{width:100%;max-width:1200px;overflow:visible}}
.co-sea{{fill:#16324A}} .co-land{{fill:#E4ECE7}} .co-shore{{fill:none;stroke:#7FA8C9;stroke-width:4;stroke-linejoin:round}}
.co-sea-label{{fill:#7FA8C9;font-size:28px;font-style:italic;text-anchor:middle;letter-spacing:.08em}} .co-mark{{fill:#8A9A93;font-size:24px;text-anchor:middle}}
.co-route{{fill:none;stroke:{accent};stroke-width:8;stroke-dasharray:1;stroke-linecap:round}}
.co-town circle{{fill:{text}}} .co-town text{{fill:{text};font-size:34px;font-weight:700;text-anchor:middle}}
.co-van rect{{fill:{accent}}}
.co-note{{font-size:32px;color:{muted}}} .co-note b{{color:{text}}}
.b2b-rep .b2b-order{{display:grid;grid-template-columns:1fr 120px 200px;gap:20px}}
.pc{{display:flex;flex-direction:column;align-items:center;gap:40px}}
.pc-row{{display:flex;align-items:center;gap:70px}}
.pc-sacks{{display:grid;grid-template-columns:repeat(2,190px);gap:24px}}
.pc-sack{{height:210px;border-radius:30px 30px 20px 20px;background:linear-gradient(180deg,#C9A66B,#9C7B45);color:#2A1F10;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;font-size:36px}}
.pc-label{{background:#fff;color:#111;font-size:20px;font-weight:700;padding:8px 14px;border-radius:8px}}
.pc-flow{{display:flex;flex-direction:column;gap:16px;width:470px}}
.pc-step{{padding:20px 26px;border-radius:18px;background:{raised};font-size:30px;font-weight:700}} .pc-on{{border:2px solid {accent}}}
.pc-loop{{font-size:30px;font-weight:800;color:{danger}}}
.ct{{display:flex;align-items:flex-start;gap:26px}} .ct-col{{display:flex;flex-direction:column;gap:14px;width:330px}}
.ct-doc{{height:300px;border-radius:12px;background:#fff;padding:30px 24px;display:flex;flex-direction:column;gap:22px}} .ct-doc i{{height:14px;border-radius:7px;background:#D5D5D5}}
.ct-item,.ct-chan{{padding:16px 20px;border-radius:14px;background:{raised};font-size:26px;font-weight:700;display:flex;align-items:center;gap:14px}}
.ct-chan b{{width:40px;text-align:center;color:{accent}}}
.ct-arrow{{position:relative;width:70px;margin-top:170px}}
.fmt-v .pc-row,.fmt-v .ct{{flex-direction:column;align-items:center}}
.pfs{{display:flex;flex-direction:column;align-items:center;gap:20px;width:100%}}
.pf-table{{position:relative;width:1240px;height:560px}}
.pf{{position:absolute;width:300px;height:400px;background:#fff;border-radius:8px;box-shadow:0 20px 50px rgba(0,0,0,.5);transform:rotate(var(--r));overflow:hidden}}
.pf-head{{height:90px;background:var(--c);display:flex;align-items:center;gap:14px;padding:0 20px;color:#fff;font-size:26px}} .pf-head i{{width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.6)}}
.pf-lines{{padding:26px 22px;display:flex;flex-direction:column;gap:18px}} .pf-lines i{{height:14px;border-radius:7px;background:#DDD}} .pf-lines i:nth-child(odd){{width:70%}}
.fn{{display:flex;flex-direction:column;align-items:center;gap:40px}}
.fn-dots{{display:grid;grid-template-columns:repeat(10,70px);gap:22px}}
.fn-dot{{width:70px;height:90px;border-radius:10px;background:{text};display:block}} .fn-win{{background:{accent}}}
.fn-result{{display:flex;align-items:center;gap:30px;font-size:40px;color:{muted}}} .fn-result b{{color:{text}}} .fn-num{{font-size:150px;font-weight:900;color:{accent} !important;line-height:1}}
.cx{{display:flex;flex-direction:column;align-items:center;gap:26px}}
.cx-win{{width:900px;background:{panel};border:2px solid {line};border-radius:24px;overflow:hidden}}
.cx-feed{{height:420px;overflow:hidden;padding:20px 26px}} .cx-track{{display:flex;flex-direction:column;gap:12px}}
.cx-msg{{padding:14px 20px;border-radius:16px;background:{raised};font-size:26px;text-align:left}} .cx-rule{{border:2px solid {accent};color:{accent};font-weight:700}}
.cx-meter{{display:flex;align-items:center;gap:20px;padding:18px 26px;border-top:2px solid {line};font-size:22px;color:{muted}}} .cx-meter .hv-bar{{flex:1;height:22px}}
.cx-warn{{font-size:34px;font-weight:800;color:{danger}}}
.sr{{display:flex;flex-direction:column;align-items:center;gap:40px}}
.sr-srcs{{display:flex;gap:30px}} .sr-src{{width:260px;padding:30px;border-radius:24px;background:{raised};display:flex;flex-direction:column;align-items:center;gap:14px;font-size:32px;font-weight:700}} .sr-src b{{font-size:70px}}
.sr-gap{{font-size:36px;font-weight:800;color:{danger}}}
.sr-agent{{width:760px;display:flex;flex-direction:column;gap:14px}}
.bd{{display:flex;align-items:center;gap:22px}} .bd-arrow{{font-size:80px;color:{accent};font-weight:800}}
.bd-sys{{width:560px}} .bd-row{{display:grid;grid-template-columns:120px 1fr 190px;gap:16px;align-items:center;padding:16px 26px;border-bottom:1px solid {line};font-size:26px;text-align:left}}
.bd-foot{{padding:20px 26px;font-size:24px;color:{muted};text-align:left}} .bd-foot b{{color:{accent}}}
.fmt-v .bd{{flex-direction:column}}
.xl-wrap{{display:flex;gap:22px;justify-content:center;align-items:flex-start}}
.xl{{width:380px;background:#F4F6F4;border-radius:14px;overflow:hidden;color:#1D1D1D;text-align:left;box-shadow:0 24px 60px rgba(0,0,0,.5)}}
.xl-name{{background:#21A366;color:#fff;font-size:22px;font-weight:700;padding:12px 18px}}
.xl-row{{display:grid;grid-template-columns:var(--grid);border-bottom:1px solid #D5DAD5;min-height:52px}}
.xl-row span{{padding:10px 10px;font-size:21px;border-right:1px solid #D5DAD5;overflow-wrap:anywhere;line-height:1.2}}
.xl-head span{{font-weight:800;background:#E3E8E3;font-size:20px}}
.xl-foot{{margin-top:34px;font-size:32px;color:{muted};text-align:center}} .xl-foot b{{color:{accent}}}
.fmt-v .xl-wrap{{flex-direction:column;align-items:center;gap:18px}} .fmt-v .xl{{width:820px}}
.lb-wrap{{display:flex;gap:70px;align-items:center;justify-content:center}}
.lb-panel{{background:{panel};border:2px solid {line};border-radius:24px;padding:30px;display:flex;flex-direction:column;gap:20px;width:440px;text-align:left}}
.lb-nums{{display:grid;grid-template-columns:1fr 1fr;gap:10px}} .lb-nums span{{background:{raised};border-radius:12px;padding:12px;font-size:24px;font-weight:700}}
.lb-done{{font-size:28px;font-weight:700;color:{accent2}}}
.lb-stack{{position:relative;width:420px;height:520px}}
.lb-page{{position:absolute;left:0;top:40px;width:340px;height:440px;background:#fff;border-radius:10px;color:#111;padding:26px;display:flex;flex-direction:column;gap:18px;box-shadow:0 20px 50px rgba(0,0,0,.45);text-align:left}}
.lb-page b{{font-size:26px}} .lb-page span{{font-size:22px;color:#555}}
.lb-bars{{display:flex;gap:3px;height:150px;align-items:stretch}} .lb-bars i{{background:#111;display:block}}
.fmt-v .lb-wrap{{flex-direction:column;gap:40px}}
.tg-phone{{width:760px;margin:0 auto;border-radius:56px;border:10px solid #23232A;background:#0E1621;overflow:hidden;text-align:left;box-shadow:0 30px 90px rgba(0,0,0,.6)}}
.fmt-v .tg-phone{{width:820px}}
.tg-top{{display:flex;align-items:center;gap:20px;padding:30px 30px 22px;background:#17212B;color:#fff;font-size:30px}}
.tg-top div{{display:flex;flex-direction:column}} .tg-top span{{font-size:22px;color:#6C8EAD}}
.tg-chat{{display:flex;flex-direction:column;gap:14px;padding:26px 24px 34px;min-height:640px;justify-content:flex-end}}
.tg-msg{{max-width:86%;padding:18px 24px;border-radius:24px;font-size:32px;line-height:1.3;color:#fff}}
.tg-msg b{{color:#fff}}
.tg-bot{{align-self:flex-start;background:#182533;border-bottom-left-radius:8px}}
.tg-me{{align-self:flex-end;background:#2B5278;border-bottom-right-radius:8px}}
.tg-buttons{{align-self:flex-start;display:flex;gap:10px;padding:0;background:none}}
.tg-buttons span{{padding:14px 24px;border-radius:18px;background:#22303F;color:#6AB3F3;font-weight:700;font-size:26px}}
.fmt-v .mk-head,.fmt-v .mk-row{{grid-template-columns:1fr 170px;column-gap:20px;padding:0 24px}} .fmt-v .mk-head span:nth-child(1){{display:none}}
.fmt-v .mk-row{{grid-template-areas:"t s" "o s";padding-top:14px;padding-bottom:14px;row-gap:4px}}
.fmt-v .mk-theirs{{grid-area:t;font-size:24px}} .fmt-v .mk-ours{{grid-area:o;font-size:28px}} .fmt-v .mk-score{{grid-area:s;grid-template-columns:auto;justify-items:center}}
.fmt-v .mk-memo{{grid-column:1;grid-row:2;font-size:18px;margin-top:8px}}
"""


# ── Makiety do starszych odcinków kanału (11.10.2026): vibe coding, moduł, Open Mercato ──

def appear(comp, sid, selector, at, step=0.18, y=24):
    comp.js.append(f'tl.fromTo("#{sid} {selector}",{{opacity:0,y:{y}}},{{opacity:1,y:0,duration:0.35,stagger:{step},ease:"power2.out"}},{comp.q(at)});')


# Kolega z ep-vibecoding (~0:45): „wyczyści cache przeglądarki, cała jego praca pójdzie na marne,
# wszystkie dane pracowników, historia” — aplikacja na localhost, dane tylko w pamięci przeglądarki.
STAFF = [("Anna Nowak", "urlop 12–16.10"), ("Piotr Wiśniewski", "zadanie: inwentaryzacja"), ("Kasia Lewandowska", "urlop 3 dni"),
         ("Marek Zieliński", "zadanie: dostawa Gdańsk"), ("Ola Kamińska", "L4 do piątku")]


def storage(comp, ev, start, end):
    rows = "".join(f'<div class="st-row" data-i="{i}"><i>{esc(n[0])}</i><b>{esc(n)}</b><span>{esc(s)}</span></div>' for i, (n, s) in enumerate(STAFF))
    inner = (f'<div class="mk-window st"><div class="mk-bar"><i></i><i></i><i></i><span>localhost:3000 · Pracownicy i urlopy</span></div>'
             f'<div class="st-list">{rows}<div class="st-empty">0 pracowników</div></div>'
             f'<div class="st-dialog">Wyczyść dane przeglądania<small>pliki cookie i dane witryn</small><b>Wyczyść</b></div>'
             f'<div class="mk-foot st-foot">dane były zapisane <b>tylko w przeglądarce</b> — bez bazy danych</div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q, span = comp.q, end - start
    wipe = start + max(2.2, span * 0.45)
    appear(comp, sid, ".st-row", start + 0.3, 0.15)
    comp.js.append(f'tl.set("#{sid} .st-dialog, #{sid} .st-empty, #{sid} .st-foot",{{opacity:0}},{q(start)});')
    comp.js.append(f'tl.fromTo("#{sid} .st-dialog",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)"}},{q(wipe - 0.9)});')
    comp.js.append(f'tl.to("#{sid} .st-dialog b",{{scale:0.92,duration:0.1,yoyo:true,repeat:1}},{q(wipe - 0.25)});')
    comp.js.append(f'tl.to("#{sid} .st-dialog",{{opacity:0,duration:0.2}},{q(wipe)});')
    comp.js.append(f'tl.to("#{sid} .st-row",{{opacity:0,x:80,duration:0.25,stagger:0.08,ease:"power2.in"}},{q(wipe + 0.1)});')
    comp.js.append(f'tl.to("#{sid} .st-empty",{{opacity:1,duration:0.3}},{q(wipe + 0.6)});')
    comp.js.append(f'tl.to("#{sid} .st-foot",{{opacity:1,duration:0.3}},{q(wipe + 0.9)});')


# „Zainstalowały się paczki i moduły, które ze sobą nie gadają… na lokalnym komputerze działa
# pięknie, produkcyjnie już nie” (ep-vibecoding ~2:10).
DEPS = ["Pracownicy", "Urlopy", "Zadania", "Faktury", "Magazyn", "Raporty"]


def deps(comp, ev, start, end):
    tiles = "".join(f'<div class="dp-tile" data-i="{i}">{esc(n)}<i class="dp-x">✕</i></div>' for i, n in enumerate(DEPS))
    errors = ["TypeError: Cannot read properties of undefined", "Error: module 'invoices' not found", "500 Internal Server Error"]
    log = "".join(f'<div class="dp-err">{esc(e)}</div>' for e in errors)
    inner = (f'<div class="dp"><div class="dp-grid">{tiles}</div>'
             f'<div class="dp-env"><span class="dp-local">laptop: <b>działa ✓</b></span><span class="dp-prod">produkcja: <b>✕</b></span></div>'
             f'<div class="dp-log">{log}</div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q, span = comp.q, end - start
    brk = start + max(2.0, span * 0.45)
    comp.js.append(f'tl.fromTo("#{sid} .dp-tile",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.3,stagger:0.22,ease:"back.out(2)"}},{q(start + 0.2)});')
    comp.js.append(f'tl.set("#{sid} .dp-x, #{sid} .dp-prod, #{sid} .dp-err",{{opacity:0}},{q(start)});')
    comp.js.append(f'tl.fromTo("#{sid} .dp-local",{{opacity:0}},{{opacity:1,duration:0.3}},{q(start + 1.6)});')
    comp.js.append(f'tl.to("#{sid} .dp-tile",{{borderColor:"{{danger}}",duration:0.2,stagger:0.1}},{q(brk)});'.replace("{danger}", comp.mock_pal["danger"]))
    comp.js.append(f'tl.to("#{sid} .dp-x",{{opacity:1,duration:0.2,stagger:0.1}},{q(brk)});')
    comp.js.append(f'tl.to("#{sid} .dp-prod",{{opacity:1,duration:0.3}},{q(brk + 0.4)});')
    comp.js.append(f'tl.to("#{sid} .dp-err",{{opacity:1,duration:0.2,stagger:0.25}},{q(brk + 0.6)});')
    for k, dx in enumerate((-8, 8, -4, 0)):
        comp.js.append(f'tl.to("#{sid} .dp-grid",{{x:{dx},duration:0.05,ease:"none"}},{q(brk + k * 0.05)});')


# Warstwy z ep-vibecoding (~5:40) i S-10 (~9:30): „są użytkownicy, jeśli użytkownicy, to role,
# jeśli role, to uprawnienia, a za uprawnieniami stoją moduły — cała ta siatka od razu”.
LAYERS = [("Użytkownicy", "Anna · Piotr · Kasia"), ("Role", "handlowiec · produkcja · biuro"),
          ("Uprawnienia", "widzi ceny · edytuje · zatwierdza"), ("Moduły", "zamówienia · oferty · magazyn")]


def layers(comp, ev, start, end):
    rows = "".join(f'<div class="ly-row" data-i="{i}"><b>{esc(n)}</b><span>{esc(d)}</span></div>'
                   + ('<div class="ly-arrow">↓</div>' if i < len(LAYERS) - 1 else "") for i, (n, d) in enumerate(LAYERS))
    inner = f'<div class="ly">{rows}<div class="ly-foot">powstaje razem z modułem — <b>od razu, nie po roku</b></div></div>'
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    step = min(0.9, max(0.35, (end - start - 1.5) / 5))
    appear(comp, sid, ".ly-row", start + 0.2, step)
    appear(comp, sid, ".ly-arrow", start + 0.2 + step * 0.6, step, 0)
    appear(comp, sid, ".ly-foot", start + 0.4 + step * 4, 0)


# Droga kartki z ep-module (~5:10): handlowiec → administracja → produkcja → pakowanie →
# faktury, „tej jednej kartki dotyka kilka, czasem kilkadziesiąt osób”.
ROUTE = [("Handlowiec", "przyjmuje"), ("Administracja", "przepisuje"), ("Produkcja", "realizuje"),
         ("Pakowanie", "wysyła · status"), ("Faktury", "dokumenty · status")]


def route(comp, ev, start, end):
    nodes = "".join(f'<div class="rt-node" data-i="{i}"><i>{i + 1}</i><b>{esc(n)}</b><span>{esc(d)}</span></div>' for i, (n, d) in enumerate(ROUTE))
    inner = (f'<div class="rt"><div class="rt-line"></div>{nodes}<div class="rt-card">ZAM 0418</div></div>'
             f'<div class="rt-count">osoby przy jednej kartce: <b class="rt-n">1</b></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q, span = comp.q, end - start
    step = min(1.6, max(0.6, (span - 2.0) / len(ROUTE)))
    appear(comp, sid, ".rt-node", start + 0.2, 0.12)
    comp.js.append(f'tl.fromTo("#{sid} .rt-line",{{scaleY:0,scaleX:0}},{{scaleY:1,scaleX:1,duration:0.6}},{q(start + 0.2)});')
    for i in range(len(ROUTE)):
        t = q(start + 0.9 + i * step)
        comp.js.append(f'tl.to("#{sid} .rt-card",{{"--i":{i},duration:0.45,ease:"power2.inOut"}},{t});')
        comp.js.append(f'tl.to("#{sid} .rt-node[data-i=\'{i}\'] i",{{backgroundColor:"{comp.mock_pal["accent"]}",color:"{comp.mock_pal["on_accent"]}",duration:0.2}},{t});')
        comp.js.append(f'tl.call(function(){{var e=document.querySelector("#{sid} .rt-n");if(e)e.textContent="{(1, 2, 4, 6, 8)[i]}";}},null,{t});')
    comp.js.append(f'tl.call(function(){{var e=document.querySelector("#{sid} .rt-n");if(e)e.textContent="kilkanaście";}},null,{q(start + 0.9 + len(ROUTE) * step)});')


# Specyfikacja z ep-module (~9:50): „trzy warstwy i nie miesza się ich ze sobą — problem biznesowy,
# reguły biznesowe, specyfikacja techniczna… nie »handlowiec traci dużo czasu«, tylko 40 minut dziennie”.
def spec(comp, ev, start, end):
    secs = [("1", "Problem biznesowy", ["Handlowiec traci <b>40 min dziennie</b>", "<b>3 faktury</b> ze złą stawką"]),
            ("2", "Reguły biznesowe", ["Rabat powyżej 8% zatwierdza szef", "Zamówienie bez karty → nie idzie na produkcję"]),
            ("3", "Specyfikacja techniczna", ["Moduł: zamówienia · role: handlowiec, biuro", "Poza zakresem: magazyn"])]
    body = "".join(f'<div class="sp-sec" data-i="{i}"><div class="sp-h"><i>{n}</i>{esc(t)}</div>'
                   + "".join(f'<div class="sp-li">{li}</div>' for li in lis) + '</div>' for i, (n, t, lis) in enumerate(secs))
    inner = f'<div class="mk-window sp"><div class="mk-bar"><i></i><i></i><i></i><span>specyfikacja · moduł zamówień.md</span></div><div class="sp-body">{body}</div></div>'
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    step = min(1.4, max(0.5, (end - start - 1.2) / 3))
    appear(comp, sid, ".sp-sec", start + 0.3, step)
    comp.js.append(f'tl.fromTo("#{sid} .sp-sec[data-i=\'0\'] b",{{color:"{comp.mock_pal["text"]}"}},{{color:"{comp.mock_pal["accent"]}",duration:0.3}},{comp.q(start + 0.9)});')


# Słownik pojęć z ep-module (~11:30): „zamówienie u handlowca to jedno, zamówienie na produkcji
# to co innego — jak tego nie spiszesz, każdy zbuduje coś innego”.
def glossary(comp, ev, start, end):
    cards = [("u handlowca", ["klient i rabat", "termin dostawy", "cena netto"]),
             ("na produkcji", ["karta technologiczna", "materiał i wymiary", "etap i stanowisko"])]
    body = "".join(f'<div class="gl-card" data-i="{i}"><div class="gl-word">Zamówienie</div><div class="gl-where">{esc(w)}</div>'
                   + "".join(f'<div class="gl-f">{esc(f)}</div>' for f in fs) + '</div>' for i, (w, fs) in enumerate(cards))
    inner = f'<div class="gl"><div class="gl-row">{body}<div class="gl-ne">≠</div></div><div class="gl-foot">to samo słowo · <b>inne pola</b> · spisz to w słowniku pojęć</div></div>'
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    appear(comp, sid, ".gl-card", start + 0.2, 0.6, 40)
    comp.js.append(f'tl.fromTo("#{sid} .gl-ne",{{opacity:0,scale:0.3}},{{opacity:1,scale:1,duration:0.4,ease:"back.out(2.5)"}},{comp.q(start + 1.4)});')
    appear(comp, sid, ".gl-foot", start + 2.0, 0)


# Checklista z ep-module (~12:20): „bezpieczeństwo, wydajność, ryzyka, przegląd tego, czego nie
# wzięliśmy pod uwagę… przy dobrej specyfikacji trafność 70–90%”.
def checklist(comp, ev, start, end):
    items = ["Bezpieczeństwo", "Wydajność", "Ryzyka", "Uprawnienia: kto i dlaczego", "Czego nie wzięliśmy pod uwagę"]
    rows = "".join(f'<div class="ck-row" data-i="{i}"><i>✓</i>{esc(t)}</div>' for i, t in enumerate(items))
    inner = (f'<div class="ck"><div class="mk-window ck-list"><div class="mk-bar"><i></i><i></i><i></i><span>checklista specyfikacji</span></div>{rows}</div>'
             f'<div class="ck-gauge"><span>trafność modułu</span><div class="hv-bar"><i></i></div><b>70–90%</b></div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q, span = comp.q, end - start
    step = min(0.7, max(0.3, (span - 2.5) / 6))
    appear(comp, sid, ".ck-row", start + 0.3, step, 0)
    comp.js.append(f'tl.fromTo("#{sid} .ck-row i",{{scale:0}},{{scale:1,duration:0.25,stagger:{step},ease:"back.out(2.5)"}},{q(start + 0.5)});')
    g = start + 0.5 + step * 5
    comp.js.append(f'tl.fromTo("#{sid} .ck-gauge",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.35}},{q(g)});')
    comp.js.append(f'tl.fromTo("#{sid} .ck-gauge .hv-bar i",{{width:"0%"}},{{width:"85%",duration:0.9,ease:"power2.out"}},{q(g + 0.2)});')


# Kopie Excela z S-10 (~3:00): „ten sam plik w kilku wersjach… jedna osoba widzi tę kolumnę,
# druga inną… nie chcemy, żeby ktoś widział marżę, za ile kupiliśmy”.
COPIES = [("zamowienia_SZEF.xlsx", ["Klient", "Ilość", "Cena", "Zakup", "Marża"], []),
          ("zamowienia_handlowcy.xlsx", ["Klient", "Ilość", "Cena", "Zakup", "Marża"], [3, 4]),
          ("zamowienia_produkcja.xlsx", ["Klient", "Ilość", "Cena", "Zakup", "Marża"], [2, 3, 4])]


def copies(comp, ev, start, end):
    sheets = "".join(f'<div class="xc" data-i="{i}"><div class="xl-name">{esc(n)}</div><div class="xc-cols">'
                     + "".join(f'<span class="{"xc-hid" if k in hidden else ""}">{esc(c)}</span>' for k, c in enumerate(cols))
                     + '</div></div>' for i, (n, cols, hidden) in enumerate(COPIES))
    inner = f'<div class="xc-wrap">{sheets}</div><div class="xl-foot">1 proces · <b>3 kopie pliku</b> · 3 wersje prawdy</div>'
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .xc",{{opacity:0,y:50,rotation:-2}},{{opacity:1,y:0,rotation:0,duration:0.45,stagger:0.35,ease:"back.out(1.5)"}},{q(start + 0.3)});')
    comp.js.append(f'tl.fromTo("#{sid} .xc-hid",{{opacity:1}},{{opacity:0.12,duration:0.3,stagger:0.12}},{q(start + 1.7)});')
    appear(comp, sid, ".xl-foot", start + 2.5, 0)


# Historia zmian z S-10 (~13:40): „wiadomo, kto, co, kiedy i na czym pracuje” — zamiast szukania
# po różnych miejscach, kto zmienił i dlaczego.
HISTORY = [("Anna K.", "handlowiec", "cena 120 → 98 zł", "wt 09:14"), ("Piotr W.", "produkcja", "status → w produkcji", "wt 10:02"),
           ("Biuro", "biuro", "faktura FV/10/418", "wt 13:47"), ("System", "automat", "mail do klienta: wysłane", "wt 13:48")]


def history(comp, ev, start, end):
    rows = "".join(f'<div class="hs-row" data-i="{i}"><b>{esc(w)}</b><span class="mk-badge mid">{esc(r)}</span><span>{esc(a)}</span><em>{esc(t)}</em></div>'
                   for i, (w, r, a, t) in enumerate(HISTORY))
    inner = (f'<div class="mk-window hs"><div class="mk-bar"><i></i><i></i><i></i><span>Zamówienie ZAM 0418 · historia zmian</span></div>'
             f'{rows}<div class="mk-foot">kto · co · kiedy — <b>bez szukania po mailach</b></div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    appear(comp, sid, ".hs-row", start + 0.3, min(0.7, max(0.25, (end - start - 1.5) / 5)), 0)
    appear(comp, sid, ".mk-foot", start + 2.4, 0)


# Warsztat z ep-module (~3:10): „około 70 pytań, ułożone nie tematycznie, tylko po ludziach —
# właściciel, handlowiec, produkcja, biuro, obsługa zamówień; na końcu otwarte decyzje”.
ROLES_Q = [("Właściciel", 12), ("Handlowiec", 14), ("Produkcja", 16), ("Biuro", 11), ("Obsługa zamówień", 12), ("Otwarte decyzje", 5)]


def questions(comp, ev, start, end):
    rows = "".join(f'<div class="qs-row" data-i="{i}"><b>{esc(r)}</b><span>{n} pytań</span></div>' for i, (r, n) in enumerate(ROLES_Q))
    inner = (f'<div class="qs"><div class="co-kicker">Warsztat · 6 godzin · 1 dzień</div><div class="qs-list">{rows}</div>'
             f'<div class="qs-total"><b class="qs-n">0</b> pytań — po ludziach, nie po tematach</div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    step = min(0.6, max(0.25, (end - start - 2) / 7))
    appear(comp, sid, ".qs-row", start + 0.3, step, 0)
    total = sum(n for _, n in ROLES_Q)
    comp.js.append(f'(function(){{var o={{v:0}};tl.to(o,{{v:{total},duration:{q(step * 6)},ease:"none",onUpdate:function(){{var e=document.querySelector("#{sid} .qs-n");if(e)e.textContent=Math.round(o.v);}}}},{q(start + 0.3)});}})();')


# Moduły Open Mercato z S-10 (~9:55) i dogrywki (~7:30): „zamówienia, oferty, pipeline, kontrahenci,
# użytkownicy, role, portal klienta… 80% masz gotowe” + WMS i kalendarz od społeczności.
OM_MODULES = ["Zamówienia", "Oferty", "Pipeline", "Kontrahenci", "Użytkownicy i role", "Portal klienta", "Historia zmian", "Katalog"]


def modules(comp, ev, start, end):
    from package import logo
    fresh = ev.get("fresh", [])
    tiles = "".join(f'<div class="om-tile" data-i="{i}">{esc(n)}</div>' for i, n in enumerate(OM_MODULES))
    tiles += "".join(f'<div class="om-tile om-new">{esc(n)}<i>nowe</i></div>' for n in fresh)
    own = '<div class="om-tile om-own">Twój proces<i>dopisujesz</i></div>'
    inner = (f'<div class="om"><div class="om-head">{logo("openmercato", 56)}<span>{esc(ev.get("title", "gotowe moduły"))}</span></div>'
             f'<div class="om-grid">{tiles}{own}</div>'
             f'<div class="om-foot"><b>~80%</b> gotowe · resztę dopisujesz pod swoją firmę</div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .om-tile",{{opacity:0,scale:0.7}},{{opacity:1,scale:1,duration:0.3,stagger:0.12,ease:"back.out(2)"}},{q(start + 0.3)});')
    if fresh:
        comp.js.append(f'tl.fromTo("#{sid} .om-new",{{boxShadow:"0 0 0 0 rgba(245,166,35,0)"}},{{boxShadow:"0 0 0 8px rgba(245,166,35,0.35)",duration:0.4,yoyo:true,repeat:3}},{q(start + 1.8)});')
    appear(comp, sid, ".om-foot", start + 2.2, 0)


# Repozytorium z ep-vibecoding (~6:00): „struktura ma w repozytorium konkretne miejsce, specyfikacja
# powstaje, zanim powstanie kod, a każdy moduł ma osobny plik z zasadami dla agenta”.
REPO = [("modules/", 0, ""), ("orders/", 1, ""), ("spec.md", 2, "specyfikacja — przed kodem"), ("AGENTS.md", 2, "zasady dla agenta"),
        ("acl.ts", 2, "role i uprawnienia"), ("data/", 2, "baza danych"), ("offers/", 1, ""), ("AGENTS.md", 2, "zasady dla agenta")]


def repo(comp, ev, start, end):
    rows = "".join(f'<div class="rp-row" data-i="{i}" style="padding-left:{40 + d * 52}px"><b>{esc(n)}</b>'
                   + (f'<span>{esc(note)}</span>' if note else "") + '</div>' for i, (n, d, note) in enumerate(REPO))
    inner = f'<div class="mk-window rp"><div class="mk-bar"><i></i><i></i><i></i><span>repozytorium · Open Mercato</span></div>{rows}</div>'
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    appear(comp, sid, ".rp-row", start + 0.3, min(0.45, max(0.18, (end - start - 1.5) / 9)), 0)


MOCKUPS.update({"storage": storage, "deps": deps, "layers": layers, "route": route, "spec": spec, "glossary": glossary,
                "checklist": checklist, "copies": copies, "history": history, "questions": questions, "modules": modules, "repo": repo})

MOCKUP_STYLE += """
.st-list{{position:relative;min-height:520px}} .st-empty{{position:absolute;left:0;right:0;top:45%;text-align:center;font-size:54px;font-weight:800;color:{danger}}}
.st-row{{display:grid;grid-template-columns:70px 1fr 1fr;gap:24px;align-items:center;padding:0 34px;min-height:96px;font-size:32px;border-bottom:1px solid {line}}}
.st-row i{{width:58px;height:58px;border-radius:50%;background:{raised};display:flex;align-items:center;justify-content:center;font-style:normal;font-weight:800;color:{accent}}}
.st-row span{{color:{muted}}} .st{{position:relative}}
.st-dialog{{position:absolute;left:50%;top:44%;transform:translate(-50%,-50%);width:620px;padding:34px 40px;border-radius:24px;background:{raised};border:2px solid {line};display:flex;flex-direction:column;gap:10px;font-size:36px;font-weight:800;box-shadow:0 30px 80px rgba(0,0,0,.6)}}
.st-dialog small{{font-size:24px;color:{muted};font-weight:500}} .st-dialog b{{align-self:flex-end;margin-top:14px;padding:14px 30px;border-radius:14px;background:{danger};color:#fff;font-size:28px}}
.fmt-v .st-row{{grid-template-columns:76px 1fr;row-gap:4px;font-size:40px;padding:22px 34px}} .fmt-v .st-row i{{grid-row:1/3;width:66px;height:66px}} .fmt-v .st-row span{{grid-column:2;font-size:30px}} .fmt-v .st-list{{min-height:820px}} .fmt-v .mk-bar{{font-size:30px}} .fmt-v .mk-foot{{font-size:32px}}
.dp{{display:flex;flex-direction:column;gap:40px;align-items:center;width:100%}}
.dp-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;width:100%}}
.dp-tile{{position:relative;height:150px;border-radius:24px;background:{panel};border:3px solid {accent};display:flex;align-items:center;justify-content:center;font-size:38px;font-weight:800}}
.dp-x{{position:absolute;top:-18px;right:-18px;width:52px;height:52px;border-radius:50%;background:{danger};color:#fff;display:flex;align-items:center;justify-content:center;font-style:normal;font-size:30px}}
.dp-env{{display:flex;gap:60px;font-size:40px;font-weight:700}} .dp-local b{{color:{accent2}}} .dp-prod b{{color:{danger}}}
.dp-log{{width:100%;background:#050504;border-radius:20px;padding:24px 30px;font-family:ui-monospace,Menlo,monospace;font-size:26px;color:{danger};text-align:left;display:flex;flex-direction:column;gap:8px}}
.fmt-v .dp-grid{{grid-template-columns:repeat(2,1fr)}} .fmt-v .dp-tile{{height:120px;font-size:34px}} .fmt-v .dp-env{{flex-direction:column;gap:10px}} .fmt-v .dp-log{{font-size:22px}}
.ly{{display:flex;flex-direction:column;align-items:center;gap:14px;width:100%}}
.ly-row{{width:100%;display:flex;justify-content:space-between;align-items:center;padding:28px 44px;border-radius:24px;background:{panel};border:2px solid {line};border-left:10px solid {accent}}}
.ly-row b{{font-size:48px;font-weight:800}} .ly-row span{{font-size:30px;color:{muted}}}
.ly-arrow{{font-size:44px;color:{accent};font-weight:800;line-height:1}}
.ly-foot{{margin-top:18px;font-size:34px;color:{muted}}} .ly-foot b{{color:{text}}}
.fmt-v .ly-row{{flex-direction:column;align-items:flex-start;gap:6px;padding:22px 34px}} .fmt-v .ly-row b{{font-size:44px}} .fmt-v .ly-row span{{font-size:28px}}
.rt{{position:relative;width:100%;display:grid;grid-template-columns:repeat(5,1fr);gap:16px;padding-top:120px}}
.rt-line{{position:absolute;left:10%;right:10%;top:174px;height:6px;background:{line};transform-origin:left center}}
.rt-node{{position:relative;display:flex;flex-direction:column;align-items:center;gap:12px;text-align:center}}
.rt-node i{{width:110px;height:110px;border-radius:50%;background:{raised};border:3px solid {line};display:flex;align-items:center;justify-content:center;font-style:normal;font-size:44px;font-weight:800}}
.rt-node b{{font-size:32px;font-weight:800}} .rt-node span{{font-size:24px;color:{muted}}}
.rt-card{{--i:0;position:absolute;top:0;left:calc(10% - 85px + var(--i) * 20%);width:170px;padding:16px 0;border-radius:14px;background:#FAF8F0;color:#0A0A08;font-size:26px;font-weight:800;text-align:center;box-shadow:0 14px 30px rgba(0,0,0,.5)}}
.rt-count{{margin-top:60px;font-size:44px;font-weight:700}} .rt-count b{{color:{accent}}}
.fmt-v .rt{{grid-template-columns:1fr;padding-top:0;padding-left:230px;gap:22px}}
.fmt-v .rt-line{{left:284px;right:auto;top:6%;bottom:6%;width:6px;height:auto;transform-origin:center top}}
.fmt-v .rt-node{{flex-direction:row;text-align:left;gap:24px}} .fmt-v .rt-node i{{width:96px;height:96px;flex:none}}
.fmt-v .rt-node b{{font-size:36px}} .fmt-v .rt-node span{{display:block;font-size:26px}}
.fmt-v .rt-card{{left:0;top:calc(var(--i) * 118px + 24px);width:180px}}
.sp-body{{padding:24px 34px 34px;display:flex;flex-direction:column;gap:24px}}
.sp-sec{{padding:22px 28px;border-radius:20px;background:{raised}}}
.sp-h{{display:flex;align-items:center;gap:16px;font-size:36px;font-weight:800;margin-bottom:10px}}
.sp-h i{{width:50px;height:50px;border-radius:12px;background:{accent};color:{on_accent};display:flex;align-items:center;justify-content:center;font-style:normal}}
.sp-li{{font-size:30px;color:{muted};padding:6px 0 6px 66px}} .sp-li b{{color:{text}}}
.fmt-v .sp-li{{padding-left:0;font-size:28px}}
.gl{{display:flex;flex-direction:column;align-items:center;gap:40px;width:100%}}
.gl-row{{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:110px;width:100%}}
.gl-card{{padding:34px 36px;border-radius:26px;background:{panel};border:2px solid {line};text-align:left;display:flex;flex-direction:column;gap:14px}}
.gl-word{{font-size:54px;font-weight:900}} .gl-where{{font-size:28px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{accent}}}
.gl-f{{font-size:32px;padding:12px 18px;border-radius:14px;background:{raised}}}
.gl-ne{{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);font-size:120px;font-weight:900;color:{danger}}}
.gl-foot{{font-size:34px;color:{muted}}} .gl-foot b{{color:{text}}}
.fmt-v .gl-row{{grid-template-columns:1fr;gap:90px}} .fmt-v .gl-word{{font-size:46px}} .fmt-v .gl-f{{font-size:28px;padding:8px 16px}} .fmt-v .gl-card{{padding:24px 30px;gap:10px}}
.ck{{display:flex;flex-direction:column;gap:40px;width:100%}}
.ck-row{{display:flex;align-items:center;gap:24px;padding:0 34px;min-height:92px;font-size:36px;font-weight:700;border-bottom:1px solid {line}}}
.ck-row i{{width:56px;height:56px;border-radius:50%;background:{accent2};color:#0A0A08;display:flex;align-items:center;justify-content:center;font-style:normal;font-weight:900}}
.ck-gauge{{display:grid;grid-template-columns:auto 1fr auto;gap:30px;align-items:center;font-size:32px;color:{muted}}} .ck-gauge b{{font-size:64px;color:{accent};font-weight:900}}
.ck-gauge .hv-bar{{height:24px;border-radius:12px;background:{raised};overflow:hidden}} .ck-gauge .hv-bar i{{display:block;height:100%;background:{accent}}}
.fmt-v .ck-gauge{{grid-template-columns:1fr auto}} .fmt-v .ck-gauge span{{grid-column:1/3}} .fmt-v .ck-row{{font-size:32px}}
.xc-wrap{{display:flex;flex-direction:column;gap:24px;width:100%}}
.xc{{background:#F4F6F2;border-radius:18px;overflow:hidden;color:#1D3A26;text-align:left}}
.xc .xl-name{{background:#1D6F42;color:#fff}}
.xc-cols{{display:grid;grid-template-columns:repeat(5,1fr)}} .xc-cols span{{padding:22px 18px;font-size:30px;font-weight:700;border-right:1px solid #CFD8CF}}
.fmt-v .xc-cols span{{font-size:24px;padding:18px 10px}}
.hs-row{{display:grid;grid-template-columns:200px 200px 1fr 140px;gap:20px;align-items:center;padding:0 34px;min-height:96px;font-size:30px;border-bottom:1px solid {line}}}
.hs-row em{{font-style:normal;color:{muted}}} .hs-row .mk-badge{{font-size:22px;justify-self:start}}
.fmt-v .hs-row{{grid-template-columns:1fr auto;row-gap:2px;padding:14px 28px}} .fmt-v .hs-row span:not(.mk-badge){{grid-column:1/3;color:{muted}}} .fmt-v .hs-row em{{display:none}}
.qs{{display:flex;flex-direction:column;align-items:center;gap:30px;width:100%}}
.qs-list{{display:grid;grid-template-columns:1fr 1fr;gap:18px;width:100%}}
.qs-row{{display:flex;justify-content:space-between;align-items:center;padding:24px 30px;border-radius:20px;background:{panel};border:2px solid {line};font-size:34px}}
.qs-row span{{color:{accent};font-weight:800;font-size:30px}}
.qs-total{{font-size:40px;color:{muted}}} .qs-total b{{font-size:72px;color:{accent};font-weight:900;margin-right:10px}}
.fmt-v .qs-list{{grid-template-columns:1fr;gap:12px}} .fmt-v .qs-row{{padding:18px 26px;font-size:32px}}
.om{{display:flex;flex-direction:column;align-items:center;gap:34px;width:100%}}
.om-head{{display:flex;align-items:center;gap:20px;font-size:34px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{muted}}}
.om-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;width:100%}}
.om-tile{{position:relative;height:130px;border-radius:20px;background:{panel};border:2px solid {line};display:flex;align-items:center;justify-content:center;text-align:center;padding:0 14px;font-size:30px;font-weight:800}}
.om-tile i{{position:absolute;top:-14px;right:14px;padding:4px 12px;border-radius:12px;background:{accent};color:{on_accent};font-style:normal;font-size:20px}}
.om-own{{border:3px dashed {accent};color:{accent}}}
.om-foot{{font-size:36px;color:{muted}}} .om-foot b{{color:{accent};font-size:50px}}
.fmt-v .om-grid{{grid-template-columns:repeat(2,1fr)}} .fmt-v .om-tile{{height:110px;font-size:30px}}
.rp-row{{display:flex;align-items:center;gap:30px;min-height:80px;font-family:ui-monospace,Menlo,monospace;font-size:32px;border-bottom:1px solid {line}}}
.rp-row b{{font-weight:700}} .rp-row span{{font-family:{font},sans-serif;font-size:26px;color:{accent};font-weight:700}}
.fmt-v .rp-row{{font-size:28px;gap:18px}} .fmt-v .rp-row span{{font-size:22px}}
.fmt-v .dp,.fmt-v .ly,.fmt-v .sp,.fmt-v .gl,.fmt-v .ck,.fmt-v .xc-wrap,.fmt-v .hs,.fmt-v .qs,.fmt-v .om,.fmt-v .rp{{zoom:1.3;width:692px;align-self:center}}
.fmt-v .rt{{zoom:1.25;width:720px;align-self:center}} .fmt-v .rt-count{{font-size:52px}} .fmt-v .xl-foot{{font-size:40px}}
"""


# Panel zamówień i produkcji — „widok systemu” do reklam (Agata 15.10, ad-11-r1 0:29 i ad-19-ra1 0:12):
# zamiast zdjęcia spawacza przy „budujemy systemy … dla firm produkcyjnych” — jasne okno systemu
# z przykładowymi danymi (ADR flowbiz-automation-unlocked 2026-10-12-reklamy-widok-systemu-jasny).
# Kontrahenci, numery i ilości są FIKCYJNE — bez nazw prawdziwych klientów.
ORDERS_KPI = [("4", "nowe dziś"), ("9", "w produkcji"), ("3", "do wysyłki")]
ORDERS = [("ZAM 0412", "Nordwind GmbH", "48 szt.", "W produkcji", "mid", "24.10"),
          ("ZAM 0413", "Gartenhaus Weber", "120 szt.", "Nowe · z maila", "ok", "31.10"),
          ("ZAM 0414", "Studio Lato", "16 szt.", "Do wysyłki", "mid", "jutro"),
          ("ZAM 0415", "Meble Brzoza", "30 szt.", "Opóźnione 2 dni", "no", "22.10")]


def orders(comp, ev, start, end):
    kpis = "".join(f'<div class="or-kpi"><b>{esc(n)}</b><span>{esc(t)}</span></div>' for n, t in ORDERS_KPI)
    rows = "".join(f'<div class="or-row" data-i="{i}"><b>{esc(no)}</b><span class="or-client">{esc(c)}</span><span class="or-qty">{esc(q)}</span>'
                   f'<span class="mk-badge {cls}">{esc(st)}</span><em>{esc(due)}</em></div>'
                   for i, (no, c, q, st, cls, due) in enumerate(ORDERS))
    inner = (f'<div class="mk-window or"><div class="mk-bar"><i></i><i></i><i></i><span>{esc(ev.get("title", "Panel firmy · zamówienia i produkcja"))}</span></div>'
             f'<div class="or-kpis">{kpis}</div>'
             f'<div class="or-row or-head"><b>Zamówienie</b><span class="or-client">Kontrahent</span><span class="or-qty">Ilość</span><span>Status</span><em>Termin</em></div>{rows}'
             f'<div class="mk-foot">przykładowe dane · <b>wszystko w jednym miejscu</b></div></div>')
    sid = mock_slate(comp, start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .or-kpi",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.3,stagger:0.1,ease:"power2.out"}},{q(start + 0.2)});')
    appear(comp, sid, ".or-row[data-i]", start + 0.5, min(0.3, max(0.12, (end - start - 1.5) / 6)), 0)
    comp.js.append(f'tl.fromTo("#{sid} .or-row .mk-badge",{{scale:0.6}},{{scale:1,duration:0.25,stagger:0.12,ease:"back.out(2.5)"}},{q(start + 0.6)});')
    appear(comp, sid, ".mk-foot", start + min(1.6, end - start - 0.8), 0)


MOCKUPS["orders"] = orders

MOCKUP_STYLE += """
.or-kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;padding:26px 34px 10px}}
.or-kpi{{background:{raised};border-radius:20px;padding:18px 24px;display:flex;align-items:baseline;gap:16px;text-align:left}}
.or-kpi b{{font-size:58px;font-weight:900;color:{accent};line-height:1}} .or-kpi span{{font-size:26px;color:{muted};font-weight:600}}
.or-row{{display:grid;grid-template-columns:170px 1.4fr 130px 280px 110px;gap:20px;align-items:center;padding:0 34px;min-height:88px;font-size:28px;border-bottom:1px solid {line};text-align:left}}
.or-row em{{font-style:normal;color:{muted}}} .or-row .mk-badge{{font-size:22px;justify-self:start;white-space:nowrap}}
.or-head{{min-height:60px;font-size:20px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:{muted};border-bottom:2px solid {line}}}
.or-head b{{font-weight:700}} .or-qty{{color:{muted}}}
.fmt-v .or{{width:860px;align-self:center}} .fmt-v .mk-window.or .mk-bar{{font-size:30px}} .fmt-v .or .mk-foot{{font-size:30px}}
.fmt-v .or-row{{grid-template-columns:1fr auto;row-gap:4px;padding:18px 32px;font-size:38px}} .fmt-v .or-row .mk-badge{{font-size:28px;grid-column:2;grid-row:1;justify-self:end}}
.fmt-v .or-row .or-client{{grid-column:1/3;color:{muted};font-size:32px}} .fmt-v .or-row .or-qty,.fmt-v .or-row em,.fmt-v .or-head{{display:none}}
.fmt-v .or-kpis{{padding:22px 24px 8px;gap:12px}} .fmt-v .or-kpi{{flex-direction:column;gap:4px;padding:16px 18px}} .fmt-v .or-kpi b{{font-size:64px}} .fmt-v .or-kpi span{{font-size:26px}}
"""


# ── Panel „jak Apilo” do ep-marpasz (noc 04.11) ─────────────────────────────
# Mateusz: „na screenach odwzoruj Apilo — dane anonimowe, przykładowe”. Układ i kolory wzięte
# ze zrzutów panelu (ciemne menu, fioletowe akcenty, pastylki statusów, jasna treść), znak
# Apilo z oficjalnej strony. Żadnych prawdziwych zamówień, klientów ani nazwy sklepu.
# mode "orders"   — lista zamówień: jedno zamówienie = 4 worki po 25 kg (~0:35–1:30)
# mode "shipment" — „Wyślij przesyłkę”: 4 paczki, 4 pola „Komentarz” (05.11 zastąpiony przez "comment" —
#                   tak to nie wyglądało; zostaje dla innych odcinków)
APILO_MENU = ["Pulpit", "Zamówienia", "Lista zamówień", "Przesyłki", "Dokumenty kurierów", "Towary i usługi", "Raporty"]
APILO_ORDERS = [
    ("ZAM-10418", "Pasza i ziarno 25 kg", "× 4", "4 paczki", "warn"),
    ("ZAM-10419", "Karma dla psa 20 kg", "× 1", "1 paczka", "ok"),
    ("ZAM-10420", "Pasza królik 25 kg", "× 2", "2 paczki", "warn"),
    ("ZAM-10421", "Ziarno gołąb 25 kg", "× 3", "3 paczki", "warn"),
]


def apilo_shell(title, body, crumbs):
    from package import logo
    menu = "".join(f'<div class="ap-mi{" ap-on" if m in crumbs else ""}{" ap-sub" if m in ("Lista zamówień", "Przesyłki", "Dokumenty kurierów") else ""}">{esc(m)}</div>'
                   for m in APILO_MENU)
    return (f'<div class="mk-window ap"><div class="ap-side"><div class="ap-logo">{logo("apilo", 44, "#FFFFFF")}</div>{menu}</div>'
            f'<div class="ap-main"><div class="ap-top"><b>{esc(title)}</b><span>Zamówienia · {esc(title)}</span>'
            f'<div class="ap-search">Szukaj zamówienia/klienta</div></div>{body}</div></div>')


def apilo_orders(comp, ev, start, end):
    rows = "".join(f'<div class="ap-row" data-i="{i}"><b class="ap-num">{n}</b><span>{esc(p)} <em>{q}</em></span>'
                   f'<span class="ap-pill {cls}">{esc(pk)}</span></div>' for i, (n, p, q, pk, cls) in enumerate(APILO_ORDERS))
    body = (f'<div class="ap-body"><div class="ap-stat"><div class="ap-st-h">Statusy</div>'
            f'<div class="ap-st"><span>BIEŻĄCE</span><i>214</i></div><div class="ap-st"><span>DO WYSŁANIA</span><i>38</i></div>'
            f'<div class="ap-st"><span>WIADOMOŚCI</span><i>8</i></div><div class="ap-st ap-st-red"><span>PROBLEMOWE</span><i>3</i></div></div>'
            f'<div class="ap-card"><div class="ap-tools"><span>Drukuj</span><span>Status</span><span>Przesyłki</span></div>'
            f'<div class="ap-row ap-head"><b>Zamówienie</b><span>Dane produktu</span><span>Dostawa</span></div>{rows}</div></div>')
    sid = mock_slate(comp, start, end, apilo_shell("Lista zamówień", body, ("Zamówienia", "Lista zamówień")), pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .ap-row[data-i]",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.3,stagger:0.18}},{q(start + 0.3)});')
    comp.js.append(f'tl.to("#{sid} .ap-row[data-i=\\"0\\"]",{{backgroundColor:"#EEEBFF",duration:0.3}},{q(start + min(1.6, (end - start) * 0.4))});')
    comp.js.append(f'tl.fromTo("#{sid} .ap-row[data-i=\\"0\\"] .ap-pill",{{scale:1}},{{scale:1.18,duration:0.2,yoyo:true,repeat:3}},{q(start + min(1.9, (end - start) * 0.45))});')


def apilo_shipment(comp, ev, start, end):
    boxes = "".join(f'<div class="ap-pkg" data-i="{i}"><b>Paczka {i + 1}/4</b><div class="ap-f"><label>Waga (kg)</label><div>25,00</div></div>'
                    f'<div class="ap-f ap-com"><label>Komentarz</label><div class="ap-in"><span class="ap-typed">{i + 1}/4 · ZAM-10418 · pasza 25 kg</span><i class="ap-caret"></i></div></div></div>'
                    for i in range(4))
    body = (f'<div class="ap-body ap-ship"><div class="ap-form"><div class="ap-f2"><label>Rodzaj przesyłki</label><div>Paczka</div></div>'
            f'<div class="ap-f2"><label>Ilość paczek</label><div><b>4</b></div></div></div>'
            f'<div class="ap-pkgs">{boxes}</div><div class="ap-actions"><span class="ap-send">Wyślij</span><span class="ap-cancel">Anuluj</span>'
            f'<span class="ap-note">każda etykieta osobno · ręcznie</span></div></div>')
    sid = mock_slate(comp, start, end, apilo_shell("Wyślij przesyłkę", body, ("Zamówienia", "Przesyłki")), pip=ev.get("pip", True))
    q, span = comp.q, end - start
    step = max(0.7, (span - 2.5) / 4)
    comp.js.append(f'tl.set("#{sid} .ap-typed",{{clipPath:"inset(0 100% 0 0)"}},{q(start)});')
    comp.js.append(f'tl.fromTo("#{sid} .ap-pkg",{{opacity:0,y:24}},{{opacity:1,y:0,duration:0.3,stagger:0.12}},{q(start + 0.2)});')
    for i in range(4):
        t = start + 0.9 + i * step
        comp.js.append(f'tl.to("#{sid} .ap-pkg[data-i=\\"{i}\\"] .ap-in",{{borderColor:"#5B4FE9",duration:0.15}},{q(t)});')
        comp.js.append(f'tl.set("#{sid} .ap-pkg[data-i=\\"{i}\\"] .ap-caret",{{opacity:1}},{q(t)});')
        comp.js.append(f'tl.set("#{sid} .ap-pkg[data-i=\\"{i}\\"] .ap-caret",{{opacity:0}},{q(t + step * 0.9)});')
        comp.js.append(f'tl.to("#{sid} .ap-pkg[data-i=\\"{i}\\"] .ap-typed",{{clipPath:"inset(0 0% 0 0)",duration:{min(0.9, step * 0.75):.2f},ease:"steps(18)"}},{q(t + 0.05)});')
        comp.js.append(f'tl.to("#{sid} .ap-pkg[data-i=\\"{i}\\"] .ap-in",{{borderColor:"#D9DCE6",duration:0.15}},{q(t + step * 0.9)});')
    click = start + 0.9 + 4 * step
    if click < end - 0.4:
        comp.js.append(f'tl.to("#{sid} .ap-send",{{scale:0.92,duration:0.12,yoyo:true,repeat:1}},{q(click)});')


# mode "comment" — jak to naprawdę wyglądało (Mateusz 05.11): JEDNO pole „Komentarz” z kilkoma
# pozycjami po przecinku. Usuń resztę → przeklej do Excela → drukuj → wklej z powrotem → zostaw
# drugą pozycję → drukuj… i tak dla każdego zamówienia. Kroki przypięte do słów (ev["beats"]).
APILO_ITEMS = ["Pasza dla niosek 25 kg", "Pszenica 25 kg", "Kukurydza 25 kg", "Mieszanka dla gołębi 25 kg"]
APILO_STEPS = ["Usuń resztę z komentarza", "Przeklej resztę do Excela", "Drukuj etykietę", "Wklej komentarz z powrotem"]


def apilo_comment(comp, ev, start, end):
    items = "".join(f'<span class="ap-it" data-i="{i}">{esc(t)}</span>'
                    + (f'<span class="ap-sep" data-i="{i}">, </span>' if i < len(APILO_ITEMS) - 1 else "")
                    for i, t in enumerate(APILO_ITEMS))
    counter = "".join(f'<span class="ap-cnt" data-n="{n}">Etykiety: <b>{n}/4</b></span>' for n in range(5))
    cells = "".join(f'<div class="ap-xr" data-i="{i}"><i>{i + 1}</i><span>{esc(t)}</span></div>' for i, t in enumerate(APILO_ITEMS[1:]))
    steps = "".join(f'<div class="ap-step" data-i="{i}"><i>{i + 1}</i>{esc(t)}</div>' for i, t in enumerate(APILO_STEPS))
    body = (f'<div class="ap-body ap-cm"><div class="ap-card ap-cmcard">'
            f'<div class="ap-cmhead"><b class="ap-num">ZAM-10418</b><span>InPost Kurier · 4 paczki po 25 kg</span></div>'
            f'<div class="ap-form"><div class="ap-f2"><label>Rodzaj przesyłki</label><div>Paczka</div></div>'
            f'<div class="ap-f2"><label>Waga (kg)</label><div>25,00</div></div></div>'
            f'<div class="ap-f ap-com ap-combig"><label>Komentarz</label><div class="ap-in">{items}<i class="ap-caret"></i></div></div>'
            f'<div class="ap-actions"><span class="ap-print">Drukuj etykietę</span><span class="ap-cnts">{counter}</span></div>'
            f'<div class="ap-toast">Etykieta wydrukowana</div></div>'
            f'<div class="ap-right"><div class="ap-xl"><div class="ap-xlbar">Excel · schowek.xlsx</div>{cells}</div>'
            f'<div class="ap-steps">{steps}<div class="ap-loop">↻ i tak dla każdego zamówienia</div></div></div></div>')
    sid = mock_slate(comp, start, end, apilo_shell("Wyślij przesyłkę", body, ("Zamówienia", "Przesyłki")), pip=ev.get("pip", False))
    q, js = comp.q, comp.js
    beats = ev.get("beats", {})

    def beat(key, fallback):
        if key not in beats:
            return start + fallback * (end - start)
        return min(max(comp.clock.at(beats[key], floor=start), start + 0.5), end - 0.6)

    others = lambda k: ",".join(f'#{sid} .ap-it[data-i=\\"{i}\\"]' for i in range(4) if i != k)
    def step_on(i, t):
        js.append(f'tl.to("#{sid} .ap-step[data-i=\\"{i}\\"]",{{opacity:1,backgroundColor:"#EEEBFF",duration:0.2}},{q(t)});')
        if i:
            js.append(f'tl.to("#{sid} .ap-step[data-i=\\"{i - 1}\\"]",{{backgroundColor:"rgba(0,0,0,0)",duration:0.2}},{q(t)});')
    def keep_only(k, t):
        """zaznacz wszystko poza pozycją k (jak myszką) i skasuj"""
        js.append(f'tl.set("{others(k)}",{{backgroundColor:"#B4D5FE"}},{q(t)});')
        js.append(f'tl.set("{others(k)}",{{display:"none",backgroundColor:"rgba(0,0,0,0)"}},{q(t + 0.4)});')
        js.append(f'tl.set("#{sid} .ap-sep",{{display:"none"}},{q(t + 0.4)});')
    def restore(t):
        js.append(f'tl.set("#{sid} .ap-it,#{sid} .ap-sep",{{display:"inline",backgroundColor:"rgba(0,0,0,0)"}},{q(t)});')
    def press(n, t):
        js.append(f'tl.to("#{sid} .ap-print",{{scale:0.92,duration:0.1,yoyo:true,repeat:1}},{q(t)});')
        js.append(f'tl.set("#{sid} .ap-cnt",{{display:"none"}},{q(t + 0.2)});')
        js.append(f'tl.set("#{sid} .ap-cnt[data-n=\\"{n}\\"]",{{display:"inline"}},{q(t + 0.2)});')
        js.append(f'tl.fromTo("#{sid} .ap-toast",{{opacity:0,y:10}},{{opacity:1,y:0,duration:0.15}},{q(t + 0.2)});')
        js.append(f'tl.to("#{sid} .ap-toast",{{opacity:0,duration:0.2}},{q(t + 0.75)});')

    js.append(f'tl.set("#{sid} .ap-cnt",{{display:"none"}},{q(start)});')
    js.append(f'tl.set("#{sid} .ap-cnt[data-n=\\"0\\"]",{{display:"inline"}},{q(start)});')
    js.append(f'tl.set("#{sid} .ap-xr,#{sid} .ap-loop,#{sid} .ap-toast",{{opacity:0}},{q(start)});')
    js.append(f'tl.set("#{sid} .ap-step",{{opacity:0.35}},{q(start)});')
    js.append(f'tl.to("#{sid} .ap-in",{{borderColor:"#5B4FE9",duration:0.2}},{q(start + 0.6)});')
    t_del, t_xl, t_print = beat("delete", 0.25), beat("excel", 0.42), beat("print", 0.52)
    t_back, t_loop = beat("restore", 0.62), beat("loop", 0.92)
    step_on(0, t_del)
    keep_only(0, t_del + 0.3)
    step_on(1, t_xl)
    js.append(f'tl.to("#{sid} .ap-xr",{{opacity:1,duration:0.25,stagger:0.15}},{q(t_xl + 0.2)});')
    t_print = max(t_print, t_xl + 1.0)
    step_on(2, t_print)
    press(1, t_print + 0.2)
    t_back = max(t_back, t_print + 1.2)
    step_on(3, t_back)
    js.append(f'tl.fromTo("#{sid} .ap-xr",{{backgroundColor:"#D9F2E3"}},{{backgroundColor:"rgba(0,0,0,0)",duration:0.6}},{q(t_back)});')
    restore(t_back + 0.3)
    # druga, trzecia, czwarta pozycja: ten sam cykl coraz szybciej (mówię „drugi człon, trzeci, czwarty”)
    t = max(beat("second", 0.75), t_back + 1.2)
    for k in (1, 2, 3):
        if k > 1:
            restore(t)
        keep_only(k, t + 0.15)
        press(k + 1, t + 0.6)
        t += 1.0
    js.append(f'tl.to("#{sid} .ap-loop",{{opacity:1,duration:0.3}},{q(max(t_loop, t))});')
    js.append(f'tl.fromTo("#{sid} .ap-loop",{{scale:1}},{{scale:1.08,duration:0.25,yoyo:true,repeat:1}},{q(max(t_loop, t) + 0.3)});')


def apilo(comp, ev, start, end):
    mode = ev.get("mode")
    return {"shipment": apilo_shipment, "comment": apilo_comment}.get(mode, apilo_orders)(comp, ev, start, end)


MOCKUPS["apilo"] = apilo

# Kolory panelu Apilo celowo stałe (nie z palety kanału) — makieta ma przypominać prawdziwy panel.
MOCKUP_STYLE += """
.ap{{display:grid;grid-template-columns:270px 1fr;background:#F3F4F8;color:#2B2B33;border-color:#2A2A33}}
.ap-side{{background:#26262E;padding:22px 0;display:flex;flex-direction:column;gap:4px}}
.ap-logo{{padding:4px 26px 22px;color:#fff}} .ap-logo .logo{{color:#fff}}
.ap-mi{{padding:14px 26px;font-size:24px;color:#C9C9D4}} .ap-mi.ap-sub{{padding-left:46px;font-size:22px}}
.ap-mi.ap-on{{background:#5B4FE9;color:#fff;font-weight:700}}
.ap-main{{display:flex;flex-direction:column;min-width:0}}
.ap-top{{display:flex;align-items:center;gap:22px;padding:20px 28px;background:#fff;border-bottom:1px solid #E3E5EE}}
.ap-top b{{font-size:30px;font-weight:600;white-space:nowrap}} .ap-top span{{font-size:20px;color:#8A8DA0}}
.ap-search{{margin-left:auto;border:1px solid #D9DCE6;border-radius:10px;padding:10px 18px;font-size:20px;color:#9A9DB0}}
.ap-body{{display:grid;grid-template-columns:250px 1fr;gap:20px;padding:22px}}
.ap-stat{{background:#fff;border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:10px}}
.ap-st-h{{font-size:22px;font-weight:600;margin-bottom:6px}}
.ap-st{{display:flex;justify-content:space-between;align-items:center;font-size:18px;color:#3B3B46}}
.ap-st i{{font-style:normal;background:#5B4FE9;color:#fff;border-radius:8px;padding:4px 12px;font-size:18px;font-weight:700}}
.ap-st-red i{{background:#E0483B}}
.ap-card{{background:#fff;border-radius:14px;padding:14px 18px;display:flex;flex-direction:column}}
.ap-tools{{display:flex;gap:10px;margin-bottom:10px}} .ap-tools span{{background:#8F86F2;color:#fff;border-radius:8px;padding:8px 16px;font-size:18px}}
.ap-row{{display:grid;grid-template-columns:150px 1fr 130px;white-space:nowrap;gap:16px;align-items:center;padding:16px 10px;border-bottom:1px solid #ECEEF4;font-size:22px;border-radius:10px}}
.ap-row em{{font-style:normal;font-weight:800;color:#5B4FE9}} .ap-num{{color:#5B4FE9;font-weight:700}}
.ap-head{{font-size:18px;color:#8A8DA0;padding-top:6px}} .ap-head b{{font-weight:600}}
.ap-pill{{justify-self:start;border-radius:20px;padding:6px 14px;font-size:18px;font-weight:700;color:#fff;background:#2B2B33}}
.ap-pill.warn{{background:#E0483B}} .ap-pill.ok{{background:#3BAA74}}
.ap-ship{{grid-template-columns:1fr;gap:16px}}
.ap-form{{display:flex;gap:18px}} .ap-f2{{background:#fff;border-radius:12px;padding:12px 18px;font-size:22px;display:flex;gap:16px;align-items:center}}
.ap-f2 label,.ap-f label{{color:#8A8DA0;font-size:18px}}
.ap-pkgs{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}}
.ap-pkg{{background:#fff;border-radius:14px;padding:14px 18px;display:flex;flex-direction:column;gap:8px;font-size:22px}}
.ap-f{{display:flex;flex-direction:column;gap:4px}} .ap-f > div{{border:1px solid #D9DCE6;border-radius:8px;padding:8px 12px;font-size:20px}}
.ap-in{{display:flex;align-items:center;white-space:nowrap;overflow:hidden}} .ap-caret{{width:2px;height:22px;background:#5B4FE9;margin-left:2px;opacity:0}}
.ap-actions{{display:flex;gap:12px;align-items:center}} .ap-send{{background:#3BAA74;color:#fff;border-radius:8px;padding:10px 26px;font-size:22px;font-weight:700}}
.ap-cancel{{border:1px solid #D9DCE6;border-radius:8px;padding:10px 22px;font-size:22px;color:#6A6D80;background:#fff}}
.ap-note{{margin-left:auto;font-size:20px;color:#E0483B;font-weight:700}}
.ap-cm{{grid-template-columns:1fr 430px;gap:20px}}
.ap-cmcard{{gap:18px;padding:22px 26px;position:relative}}
.ap-cmhead{{display:flex;gap:18px;align-items:baseline;font-size:26px}} .ap-cmhead span{{color:#8A8DA0;font-size:22px}}
.ap-combig label{{font-size:22px;font-weight:700;color:#2B2B33}}
.ap-combig .ap-in{{font-size:27px;padding:16px 18px;min-height:74px;border:2px solid #D9DCE6;border-radius:10px;white-space:normal;line-height:1.35;display:block}}
.ap-it{{border-radius:4px}}
.ap-print{{background:#5B4FE9;color:#fff;border-radius:8px;padding:12px 28px;font-size:24px;font-weight:700}}
.ap-cnts{{margin-left:auto;font-size:24px;color:#3B3B46}} .ap-cnts b{{color:#5B4FE9}}
.ap-toast{{position:absolute;right:26px;bottom:84px;background:#3BAA74;color:#fff;border-radius:8px;padding:8px 16px;font-size:20px;font-weight:700}}
.ap-right{{display:flex;flex-direction:column;gap:16px}}
.ap-xl{{background:#fff;border-radius:12px;overflow:hidden;border:1px solid #CFE3D6}}
.ap-xlbar{{background:#1D6F42;color:#fff;font-size:20px;font-weight:700;padding:10px 16px}}
.ap-xr{{display:flex;gap:12px;align-items:center;border-bottom:1px solid #E3E8E5;font-size:21px;padding:8px 12px;white-space:nowrap}}
.ap-xr i{{font-style:normal;color:#8A8DA0;width:22px;font-size:18px}}
.ap-steps{{background:#fff;border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:6px}}
.ap-step{{display:flex;gap:12px;align-items:center;font-size:22px;padding:8px 10px;border-radius:8px}}
.ap-step i{{font-style:normal;background:#5B4FE9;color:#fff;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;flex:none}}
.ap-loop{{font-size:22px;font-weight:800;color:#E0483B;padding:8px 10px}}
.fmt-v .ap{{grid-template-columns:1fr}} .fmt-v .ap-side{{display:none}} .fmt-v .ap-body{{grid-template-columns:1fr}} .fmt-v .ap-stat{{display:none}}
"""


# ── Moduły systemu ze strony flowbiz.pl (wstawka „przedstawienie się”, 05.11) ─────────────
# Mateusz: „zamiast samego dużego tekstu leciała też animacja klikania się mockupu — ale
# składania klocków z modułów w jeden system”. Markup i CSS to kopia sekcji #modules ze strony
# (packaging/brand/site-modules, README tam). Silnika pokazu ze strony nie bierzemy — liczy czas
# zegarem przeglądarki; tu ruch idzie po osi GSAP, żeby render klatka po klatce był powtarzalny.
#
#   Excel w oknie → 9 klocków wlatuje i wpina się łącznikiem w okno (menu systemu rośnie)
#   → przy każdej wymienianej branży zapala się jej moduł, a kursor klika jego ekran
#   → na finale świeci cały system.
import json
import re
from pathlib import Path

SITE_MODULES = Path(__file__).resolve().parent.parent / "packaging" / "brand" / "site-modules"
MODULE_KEYS = ["b2b", "service", "production", "quotes", "crm", "warehouse", "compliance", "catalog", "margin"]
MODULE_LANDING = ["b2b", "warehouse", "service", "compliance", "production", "catalog", "quotes", "margin", "crm"]
# Plansza w układzie 1480 px (skala do 1920): karta 240, przerwa 56, okno 780 (płótno strony
# 1:1), padding 30. Stałe wymiary, bo z nich liczymy łączniki — bez mierzenia DOM-u przy starcie.
MV_W, MV_H = 1480, 832
MV_PAD, MV_CARD, MV_GAP, MV_WIN = 30, 240, 56, 780
MV_BODY_W = 2 + 2 * MV_PAD + 2 * MV_CARD + 2 * MV_GAP + MV_WIN
MV_BODY_H, MV_WIN_H = 640, 504        # okno = pasek 32 + płótno 470 + ramka 2

MV_EXCEL = [("Klient", "Produkt", "Ilość", "Status", "Uwagi"),
            ("Firma A", "Paleta 120×80", "40", "?", "dzwonić"),
            ("Firma B", "Karton 5W", "1 200", "wysłane", ""),
            ("Firma A", "Paleta 120×80", "40", "DUPLIKAT", "!!"),
            ("Firma C", "Folia stretch", "#ARG!", "", "cena?"),
            ("Firma D", "Karton 3W", "800", "w toku", "v2"),
            ("Firma B", "Taśma 48 mm", "60", "", "kto?"),
            ("Firma E", "Narożnik", "2 000", "czeka", "")]


def elbow(x1, y1, xm, x2, y2):
    """Łamana jak drawWires() na stronie: poziomo od karty, pionowo w szczelinie, poziomo do okna."""
    dy = y2 - y1
    if abs(dy) < 2:
        return f"M{x1:.1f},{y1:.1f} H{x2:.1f}"
    dx = 1 if x2 > x1 else -1
    r = min(12, abs(dy) / 2, abs(xm - x1), abs(x2 - xm))
    sy = 1 if dy > 0 else -1
    return (f"M{x1:.1f},{y1:.1f} H{xm - dx * r:.1f} Q{xm:.1f},{y1:.1f} {xm:.1f},{y1 + sy * r:.1f} "
            f"V{y2 - sy * r:.1f} Q{xm:.1f},{y2:.1f} {xm + dx * r:.1f},{y2:.1f} H{x2:.1f}")


def module_wires():
    inner_h = MV_BODY_H - 2 - 2 * MV_PAD
    row = inner_h / 10                      # siatka strony: 10 wierszy, karta zajmuje dwa
    win_x = MV_PAD + MV_CARD + MV_GAP
    win_y = MV_PAD + (inner_h - MV_WIN_H) / 2
    groups = []
    for i, key in enumerate(MODULE_KEYS):
        left = i < 5
        k, count = (i, 5) if left else (i - 5, 4)
        y1 = MV_PAD + row * (2 * k + 1 if left else 2 * k + 2)
        x1 = MV_PAD + MV_CARD if left else win_x + MV_WIN + MV_GAP
        x2 = win_x - 7 if left else win_x + MV_WIN + 7
        y2 = win_y + MV_WIN_H * (0.2 + 0.6 * (k + 0.5) / count)
        center = (count - 1) / 2
        xm = x1 + (x2 - x1) * (0.3 + 0.45 * abs(k - center) / center)
        d = elbow(x1, y1, xm, x2, y2)
        groups.append(f'<g class="msx-wire" data-k="{key}"><path class="msx-wire-base" d="{d}" pathLength="100"/>'
                      f'<path class="msx-wire-draw" d="{d}" pathLength="100"/>'
                      f'<circle class="msx-port" cx="{x2 + (3 if left else -3):.1f}" cy="{y2:.1f}" r="3.5"/>'
                      f'<circle class="msx-dot" cx="{x1:.1f}" cy="{y1:.1f}" r="3"/></g>')
    return f'<svg class="msx-wires" viewBox="0 0 {MV_BODY_W - 2} {MV_BODY_H - 2}" aria-hidden="true">{"".join(groups)}</svg>'


def accent(text):
    """„Systemy dla firm, które *wyrosły z Excela” — od gwiazdki mięta, jak na planszach."""
    head, _, acc = text.partition("*")
    return esc(head) + (f'<span class="mv-acc">{esc(acc)}</span>' if acc else "")


def module_markup(headlines):
    src = (SITE_MODULES / "section.html").read_text()
    body = re.search(r'<div class="msx-body" data-msx-body>(.*)</div>\s*</div>\s*</section>', src, re.S).group(1)
    body = body.replace(" is-on", "").replace("<span data-msx-url>b2b</span>", "")
    body = re.sub(r'<svg class="msx-wires"[^>]*></svg>', module_wires(), body)
    side = re.search(r'<div class="msx-side">.*?</ul>\s*</div>', body, re.S).group(0).replace(' class="on"', "")
    icons = re.findall(r'<span class="msx-item-ic">(<svg.*?</svg>)</span>', body, re.S)
    xls = "".join("<tr>" + "".join(
        f'<{"th" if r == 0 else "td"}{" class=y" if (r, c) in ((1, 3), (5, 4)) else " class=r" if (r, c) in ((3, 3), (4, 2)) else ""}>{esc(v)}</{"th" if r == 0 else "td"}>'
        for c, v in enumerate(row)) + "</tr>" for r, row in enumerate(MV_EXCEL))
    counter = "".join(f'<span class="mv-cnt" data-n="{n}">{n} / 9 modułów</span>' for n in range(10))
    tiles = "".join(f'<span class="mv-tile" data-k="{k}">{icons[i]}</span>' for i, k in enumerate(MODULE_KEYS))
    assembly = (f'<div class="msx-screen mv-asm">{side}<div class="msx-main mv-asm-main">'
                f'<div class="mv-xls"><div class="mv-xls-bar">zamowienia_FINAL_v7 (2).xlsx</div><table>{xls}</table></div>'
                f'<div class="mv-build"><div class="mv-build-k">Składamy Twój system</div>'
                f'<div class="mv-build-n">{counter}</div><div class="mv-tiles">{tiles}</div></div></div></div>')
    body = body.replace('<div class="msx-screen"', assembly + '<div class="msx-screen"', 1)
    heads = []
    for i, h in enumerate(headlines):
        kicker = f'<div class="mv-k">{esc(h["kicker"])}</div>' if h.get("kicker") else ""
        if h.get("words"):
            words = '<i>·</i>'.join(f'<span class="mv-w">{esc(label)}</span>' for _, label in h["words"])
            heads.append(f'<div class="mv-h" data-h="{i}">{kicker}<h2 class="mv-words">{words}</h2></div>')
        else:
            heads.append(f'<div class="mv-h" data-h="{i}">{kicker}<h2>{accent(h["text"])}</h2></div>')
    css = (SITE_MODULES / "section.css").read_text()
    return (f'<style>{css}{MV_CSS}</style><div class="fbv2 mv-root"><div class="ad-dark msx-dark mv">'
            f'<div class="mv-head">{"".join(heads)}</div><div class="msx-body">{body}</div></div></div>')


def modules(comp, ev, start, end):
    at = lambda v, base: base + float(v[1:]) if isinstance(v, str) and v.startswith("+") else comp.clock.at(v, floor=start)
    heads = ev["headlines"]
    head_at = [max(start, at(h["at"], start)) for h in heads]
    asm = at(ev["assemble"], start)
    scenes = []
    for s in ev["scenes"]:
        t0 = at(s["at"], start)
        scenes.append({"k": s["key"], "at": comp.q(t0), "steps": [comp.q(at(o, t0)) for o in s["steps"]]})
    first = scenes[0]["at"]
    span = (first - 0.75) - (asm + 0.15)
    if span < 2.5:
        raise SystemExit(f"makieta modules @ {start:.1f}: {span:.1f} s na wpięcie 9 modułów — za mało (min. 2,5 s)")
    land = [{"k": k, "left": MODULE_KEYS.index(k) < 5, "i": MODULE_KEYS.index(k), "n": n + 1,
             "t": comp.q(asm + 0.15 + n * span / (len(MODULE_LANDING) - 1))} for n, k in enumerate(MODULE_LANDING)]
    words = [comp.q(at(w, start)) for h in heads for w, _ in h.get("words", [])]
    data = {"start": comp.q(start), "asm": comp.q(asm), "fin": comp.q(at(ev["finale"], start)), "words": words,
            "heads": [{"at": comp.q(t), "end": comp.q(head_at[i + 1]) if i + 1 < len(heads) else None} for i, t in enumerate(head_at)],
            "land": land, "scenes": scenes}
    sid = comp.slate(start, end, module_markup(heads), pip=False, cls="msxv")
    comp.js.append(MV_JS.replace("__SID__", sid).replace("__DATA__", json.dumps(data)))


MOCKUPS["modules"] = modules

MV_CSS = """
.slate.msxv{background:#0E1F1A}
.slate.msxv .slate-body{position:absolute;inset:0;width:auto;display:block;gap:0;text-align:left}
.slate.msxv .series-tag{display:none}
.fbv2.mv-root{position:absolute;inset:0;background:transparent;color:#F2FBF7}
.fbv2 .ad-dark.mv{position:absolute;left:0;top:0;width:1480px;height:832px;transform:scale(1.297297);transform-origin:0 0;
  background:radial-gradient(55% 50% at 50% 60%,rgba(47,211,160,.13),transparent 70%)}
.mv,.mv *{transition:none!important;animation:none!important}
.mv-head{position:absolute;left:0;right:0;top:18px;height:150px}
.mv-h{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;opacity:0}
.fbv2 .mv-h h2{font-size:54px;font-weight:800;letter-spacing:-.025em;line-height:1.05;color:#fff;margin:0}
.mv-acc{color:#2FD3A0;text-shadow:0 0 28px rgba(47,211,160,.35)}
.mv-k{font-size:15px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#8FE6C8;margin-bottom:14px}
.fbv2 .mv-h h2.mv-words{display:flex;gap:14px;align-items:baseline;font-size:38px;white-space:nowrap}
.mv-w{color:rgba(255,255,255,.32)}
.mv-words i{font-style:normal;color:rgba(47,211,160,.55)}
.fbv2 .mv .msx-body{position:absolute;left:23px;top:178px;width:1434px;height:640px;margin:0;padding:30px;
  grid-template-columns:240px 780px 240px;column-gap:56px;grid-template-rows:repeat(10,minmax(0,1fr))}
.fbv2 .mv .msx-chrome{height:32px;padding:0 12px}
.fbv2 .mv .msx-under,.fbv2 .mv .msx-note{display:none}
.fbv2 .mv .msx-li{opacity:0}
.fbv2 .mv .msx-wire-draw{opacity:0}
.fbv2 .mv .mv-asm{display:block}
.fbv2 .mv-asm-main{display:flex;align-items:center;justify-content:center}
.mv-xls{position:absolute;inset:14px 18px;border:1px solid #d9e2dd;border-radius:6px;overflow:hidden;background:#fff;font-size:12px;color:#27302d}
.mv-xls-bar{background:#1D6F42;color:#fff;font-weight:700;padding:7px 12px;font-size:12px}
.mv-xls table{border-collapse:collapse;width:100%}
.mv-xls td,.mv-xls th{border:1px solid #e3e8e5;padding:6px 9px;text-align:left;white-space:nowrap}
.mv-xls th{background:#f3f5f4;color:#5a6b65;font-weight:700}
.mv-xls .y{background:#FFF3B0}
.mv-xls .r{background:#FDE2E1;color:#B42318;font-weight:700}
.mv-build{text-align:center;opacity:0}
.mv-build-k{font-size:24px;font-weight:800;color:#13211D;letter-spacing:-.01em}
.mv-build-n{margin-top:6px;font-size:14px;font-weight:700;color:#0F7D60}
.mv-cnt{display:none}
.mv-tiles{display:grid;grid-template-columns:repeat(3,52px);gap:10px;justify-content:center;margin-top:20px}
.mv-tile{width:52px;height:52px;border-radius:12px;border:1.5px dashed #c9d8d1;display:flex;align-items:center;justify-content:center;color:#0F7D60}
.mv-tile svg{width:22px;height:22px;opacity:0}
"""

# Oś pokazu. Pozycje celów kursora mierzone leniwie (wartości-funkcje GSAP liczą się przy
# pierwszym renderze tweena, czyli już po załadowaniu fontów), offsetami — transform planszy
# (skala 1,297 i wejście slate-body) ich nie zmienia.
MV_JS = """(function(){
var R=document.getElementById("__SID__"),D=__DATA__;
function $(s){return R.querySelector(s)}function $$(s){return R.querySelectorAll(s)}
var canvas=$(".msx-canvas"),cur=$(".msx-cursor"),rip=$(".msx-ripple"),memo={};
function scr(k){return k==="asm"?$(".mv-asm"):$('[data-msx-screen="'+k+'"]')}
function card(k){return $('[data-msx-item="'+k+'"]')}
function wire(k,p){return $('.msx-wire[data-k="'+k+'"] '+p)}
function cls(n){var c="msx-screen is-on";for(var i=1;i<=n;i++)c+=" st-"+i;return c}
function point(k,n){var id=k+n;if(memo[id])return memo[id];var s=scr(k),keep=s.getAttribute("class");s.setAttribute("class",cls(n-1));
 var el=s.querySelector('[data-msx-step="'+n+'"]'),w=el.offsetWidth,h=el.offsetHeight,x=0,y=0;
 while(el&&el!==canvas){x+=el.offsetLeft;y+=el.offsetTop;el=el.offsetParent}
 s.setAttribute("class",keep);return memo[id]={x:x+w*0.55,y:y+h*0.6}}
tl.set(cur,{opacity:0,x:690,y:410},D.start);
tl.set(rip,{opacity:0},D.start);
tl.set($$(".mv-cnt"),{display:"none"},D.start);tl.set($('.mv-cnt[data-n="0"]'),{display:"inline"},D.start);
D.heads.forEach(function(h,i){var el=$('.mv-h[data-h="'+i+'"]');
 tl.fromTo(el,{opacity:0,y:18},{opacity:1,y:0,duration:0.4,ease:"power3.out"},h.at);
 if(h.end!==null)tl.to(el,{opacity:0,y:-14,duration:0.25},h.end-0.25)});
var ws=$$(".mv-w");D.words.forEach(function(t,i){tl.to(ws[i],{color:"#2FD3A0",duration:0.2},t)});
tl.to($(".mv-xls"),{opacity:0,scale:0.96,duration:0.35},D.asm-0.1);
tl.fromTo($(".mv-build"),{opacity:0,y:10},{opacity:1,y:0,duration:0.3},D.asm+0.15);
var nav=$$(".mv-asm .msx-side li");
D.land.forEach(function(L){var li=card(L.k).parentNode,t=L.t;
 tl.fromTo(li,{opacity:0,x:L.left?-170:170,scale:0.85},{opacity:1,x:0,scale:1,duration:0.5,ease:"back.out(1.6)"},t);
 tl.fromTo(wire(L.k,".msx-wire-base"),{opacity:0},{opacity:1,duration:0.2},t+0.35);
 tl.fromTo(wire(L.k,".msx-wire-draw"),{opacity:1,strokeDashoffset:100},{strokeDashoffset:0,duration:0.45,ease:"power2.inOut"},t+0.35);
 tl.to(wire(L.k,".msx-wire-draw"),{opacity:0,duration:0.4},t+0.95);
 tl.fromTo(wire(L.k,".msx-port"),{attr:{r:3.5}},{attr:{r:7},duration:0.18,yoyo:true,repeat:1},t+0.75);
 tl.fromTo(nav[L.i],{opacity:0,x:-10},{opacity:1,x:0,duration:0.25},t+0.8);
 var tile=$('.mv-tile[data-k="'+L.k+'"]');
 tl.to(tile,{backgroundColor:"#EAF6F1",borderColor:"#1C9E7A",borderStyle:"solid",duration:0.2},t+0.8);
 tl.to(tile.querySelector("svg"),{opacity:1,duration:0.2},t+0.8);
 tl.set($$(".mv-cnt"),{display:"none"},t+0.8);tl.set($('.mv-cnt[data-n="'+L.n+'"]'),{display:"inline"},t+0.8)});
var prev=null;
D.scenes.forEach(function(S){var s=scr(S.k);
 tl.set(scr(prev||"asm"),{attr:{class:prev?"msx-screen":"msx-screen mv-asm"}},S.at);
 if(!prev)tl.set(scr("asm"),{display:"none"},S.at);
 tl.set(s,{attr:{class:cls(0)}},S.at);
 tl.fromTo(s.querySelector(".msx-main"),{opacity:0,y:8},{opacity:1,y:0,duration:0.3,immediateRender:false},S.at);
 if(prev){tl.set(card(prev),{attr:{class:"msx-item"}},S.at);tl.to(wire(prev,".msx-wire-draw"),{opacity:0,duration:0.2},S.at);
  tl.to(wire(prev,".msx-port"),{fill:"#0E1F1A",duration:0.2},S.at)}
 tl.set(card(S.k),{attr:{class:"msx-item is-on"}},S.at);
 tl.fromTo(wire(S.k,".msx-wire-draw"),{opacity:1,strokeDashoffset:100},{strokeDashoffset:0,duration:0.4,immediateRender:false},S.at);
 tl.to(wire(S.k,".msx-port"),{fill:"#2FD3A0",duration:0.2},S.at+0.35);
 S.steps.forEach(function(t,j){var n=j+1,k=S.k,tg=s.querySelector('[data-msx-step="'+n+'"]');
  tl.to(cur,{opacity:1,duration:0.15},Math.max(S.at,t-0.45));
  tl.to(cur,{x:function(){return point(k,n).x},y:function(){return point(k,n).y},duration:0.38,ease:"power2.inOut"},t-0.42);
  tl.fromTo(rip,{opacity:0.9,scale:0.3,x:function(){return point(k,n).x},y:function(){return point(k,n).y}},{opacity:0,scale:1.4,duration:0.45,immediateRender:false},t);
  tl.to(tg,{scale:0.94,duration:0.08,yoyo:true,repeat:1},t);
  tl.set(s,{attr:{class:cls(n)}},t+0.1);
  var on=s.querySelectorAll(".on-"+n),hl=s.querySelectorAll(".hl-"+n);
  if(on.length)tl.fromTo(on,{opacity:0,y:6},{opacity:1,y:0,duration:0.35,immediateRender:false},t+0.1);
  if(hl.length)tl.fromTo(hl,{backgroundColor:"rgba(47,211,160,0.30)"},{backgroundColor:"rgba(47,211,160,0)",duration:1.1,immediateRender:false},t+0.1)});
 prev=S.k});
tl.to(cur,{opacity:0,duration:0.25},D.fin);
$$(".msx-wire").forEach(function(g,i){var k=g.getAttribute("data-k"),t=D.fin+i*0.08;
 tl.to(g.querySelector(".msx-wire-draw"),{opacity:1,strokeDashoffset:0,duration:0.3},t);
 tl.to(g.querySelector(".msx-port"),{fill:"#2FD3A0",duration:0.2},t);
 tl.set(card(k),{attr:{class:"msx-item is-on"}},t)});
})();"""
