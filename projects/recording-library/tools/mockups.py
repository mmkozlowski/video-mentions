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


def b2b(comp, ev, start, end):
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


MOCKUPS = {"match": match, "telegram": telegram, "b2b": b2b, "excels": excels, "labels": labels}

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
