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
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
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
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
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
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
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
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
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
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
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
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
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
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
    q = comp.q
    comp.js.append(f'tl.fromTo("#{sid} .sy-box",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.4,stagger:0.2}},{q(start + 0.2)});')
    comp.js.append(f'tl.fromTo("#{sid} .sy-line",{{scaleX:0}},{{scaleX:1,duration:0.5,ease:"power2.out"}},{q(start + 0.8)});')
    comp.js.append(f'tl.fromTo("#{sid} .sy-chip",{{opacity:0,x:-160}},{{opacity:1,x:0,duration:0.5,stagger:0.3,ease:"power2.out"}},{q(start + 1.1)});')
    comp.js.append(f'tl.fromTo("#{sid} .sy-clock",{{opacity:0}},{{opacity:1,duration:0.3}},{q(start + 2.0)});')
    comp.js.append(f'tl.fromTo("#{sid} .sy-user",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.35,stagger:0.15}},{q(start + max(2.6, (end - start) * 0.5))});')


# Trasa handlowca z ep-rezon (~2:45): „objechać z towarem całe wybrzeże albo zimą południe
# Polski” — stylizowane wybrzeże Bałtyku, bus jedzie od miasta do miasta.
COAST_TOWNS = [("Kołobrzeg", 120, 300), ("Ustka", 560, 200), ("Rowy", 700, 175), ("Łeba", 900, 150)]


def coast(comp, ev, start, end):
    path = "M 40 330 C 200 300, 380 230, 560 200 S 820 160, 1000 135 L 1180 120"
    towns = "".join(f'<g class="co-town" data-i="{i}"><circle cx="{x}" cy="{y}" r="12"/><text x="{x}" y="{y + 52}">{esc(n)}</text></g>'
                    for i, (n, x, y) in enumerate(COAST_TOWNS))
    inner = (f'<div class="co"><div class="co-kicker">Sezon w trasie</div><svg viewBox="0 0 1220 420" class="co-map">'
             f'<path class="co-sea" d="{path} L 1220 0 L 0 0 Z"/><path class="co-shore" d="{path}"/>'
             f'<path class="co-route" d="M 120 300 C 300 260, 430 225, 560 200 S 820 160, 900 150" pathLength="1"/>{towns}'
             f'<g class="co-van"><rect x="-26" y="-16" width="52" height="30" rx="6"/></g></svg>'
             f'<div class="co-note">Towar wyprodukowany „na zapas” — <b>dowiadujesz się o nadwyżce na końcu sezonu</b></div></div>')
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
    q, run = comp.q, max(2.0, (end - start) - 2.0)
    comp.js.append(f'tl.fromTo("#{sid} .co-route",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{run},ease:"none"}},{q(start + 0.4)});')
    comp.js.append(f'tl.fromTo("#{sid} .co-town",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.3,stagger:{run / 4}}},{q(start + 0.4)});')
    comp.js.append(f'tl.fromTo("#{sid} .co-van",{{x:120,y:300}},{{keyframes:[{{x:560,y:200}},{{x:700,y:175}},{{x:900,y:150}}],duration:{run},ease:"none"}},{q(start + 0.4)});')
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
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
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
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
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
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
    comp.js.append(f'tl.fromTo("#{sid} .pf",{{opacity:0,y:-200,rotation:0}},{{opacity:1,y:0,rotation:function(i,el){{return getComputedStyle(el).getPropertyValue("--r")}},duration:0.45,stagger:0.22,ease:"back.out(1.4)"}},{comp.q(start + 0.3)});')
    comp.js.append(f'tl.fromTo("#{sid} .xl-foot",{{opacity:0}},{{opacity:1,duration:0.3}},{comp.q(start + 1.8)});')


# Lejek z ep-open-mercato-offers (~1:35): „na 20 wystawionych ofert 3 stały się zamówieniem”.
def funnel(comp, ev, start, end):
    dots = "".join(f'<i class="fn-dot{" fn-win" if i in (3, 11, 17) else ""}" data-i="{i}"></i>' for i in range(20))
    inner = (f'<div class="fn"><div class="co-kicker">Wystawione oferty</div><div class="fn-dots">{dots}</div>'
             f'<div class="fn-result"><b class="fn-num">3</b><span>zamówienia z 20 ofert — <b>dlaczego?</b></span></div></div>')
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
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
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
    q, span = comp.q, end - start
    comp.js.append(f'tl.fromTo("#{sid} .cx-msg",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.25,stagger:{min(0.5, span / 14)}}},{q(start + 0.3)});')
    comp.js.append(f'tl.fromTo("#{sid} .cx-meter i",{{width:"20%"}},{{width:"100%",duration:{q(span * 0.55)},ease:"none"}},{q(start + 0.3)});')
    comp.js.append(f'tl.to("#{sid} .cx-track",{{y:-230,duration:{q(span * 0.35)},ease:"power1.in"}},{q(start + span * 0.35)});')
    comp.js.append(f'tl.to("#{sid} .cx-meter i",{{backgroundColor:"{comp.pal["danger"]}",duration:0.3}},{q(start + span * 0.55)});')
    comp.js.append(f'tl.fromTo("#{sid} .cx-warn",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.4}},{q(start + span * 0.62)});')


# Źródła danych z ep-vacuactiv (~2:05): „dane są w głowach, na kartkach, na mailach i agent AI
# nie ma skąd tych danych pobierać”.
def sources(comp, ev, start, end):
    srcs = "".join(f'<div class="sr-src" data-i="{i}"><b>{icon}</b>{esc(t)}</div>' for i, (icon, t) in enumerate([("🧠", "w głowach"), ("📝", "na kartkach"), ("✉️", "w mailach")]))
    inner = (f'<div class="sr"><div class="sr-srcs">{srcs}</div><div class="sr-gap">✕ brak połączenia</div>'
             f'<div class="sr-agent"><div class="tg-msg tg-me">Ile mamy opóźnionych zleceń?</div><div class="tg-msg tg-bot">Nie wiem. Nie mam dostępu do tych danych.</div></div></div>')
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
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
    sid = comp.slate(start, end, inner, pip=ev.get("pip", True))
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
.co-sea{{fill:#16324A}} .co-shore{{fill:none;stroke:#7FA8C9;stroke-width:4}}
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
