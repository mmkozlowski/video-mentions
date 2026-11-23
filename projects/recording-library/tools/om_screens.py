"""Ekrany systemu w wyglądzie Open Mercato — zamiast „zabawkowych” kart (MK 23.11: „jak mówię o programach,
systemach, nie mogą wyglądać jak zabawka, tylko poważny system, taki jak realnie zrobiliśmy”).

Wspólna powłoka jak w OM 0.7 (skill makiety-open-mercato): sidebar z nazwą firmy, szukajką, grupami
i ikonami lucide, pasek z okruszkami, lista w karcie (tytuł + akcje, szukajka + Filtry, tabela), statusy
jak status-badge, panel boczny (Sheet) i komunikat w prawym górnym rogu. Dane wymyślone — bez nazw
klientów, osób i cen. Okno 1200×600 jak plan produkcji (miejsce na okienko kamery w prawym dolnym rogu).
"""
from mockups import esc, own_slate, when

ICON = {
    "home": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    "dashboard": '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/>'
                 '<rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
    "cart": '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/>'
            '<path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>'
             '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "package": '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>'
               '<path d="M3.27 6.96 12 12.01l8.73-5.05"/><path d="M12 22.08V12"/>',
    "file": '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><path d="M14 2v6h6"/>'
            '<path d="M16 13H8"/><path d="M16 17H8"/>',
    "factory": '<path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/>'
               '<path d="M17 18h1"/><path d="M12 18h1"/><path d="M7 18h1"/>',
    "tag": '<path d="M12.59 2.59A2 2 0 0 0 11.17 2H4a2 2 0 0 0-2 2v7.17a2 2 0 0 0 .59 1.42l8.7 8.7a2.43 2.43 0 0 0 3.42 0l6.58-6.58a2.43 2.43 0 0 0 0-3.42z"/>'
           '<circle cx="7.5" cy="7.5" r="1"/>',
    "printer": '<path d="M6 9V2h12v7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>'
               '<rect x="6" y="14" width="12" height="8"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
    "warehouse": '<path d="M22 8.35V20a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8.35A2 2 0 0 1 3.26 6.5l8-3.2a2 2 0 0 1 1.48 0l8 3.2A2 2 0 0 1 22 8.35Z"/>'
                 '<path d="M6 18h12"/><path d="M6 14h12"/><rect x="6" y="10" width="12" height="12"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "filter": '<path d="M22 3H2l8 9.46V19l4 2v-8.54z"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
    "plus": '<path d="M5 12h14"/><path d="M12 5v14"/>',
    "refresh": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/>'
               '<path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    "chevdown": '<path d="m6 9 6 6 6-6"/>',
    "chevright": '<path d="m9 18 6-6-6-6"/>',
    "bell": '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "sparkles": '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/>'
             '<path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.62L18.3 9.38a1 1 0 0 0-.78-.38H14"/>'
             '<circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "more": '<circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>',
    "image": '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/>',
    "message": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "book": '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>',
    "history": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
    "list": '<path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/>',
    "store": '<path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"/><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>'
             '<path d="M2 7h20v3a3 3 0 0 1-6 0 3 3 0 0 1-4 0 3 3 0 0 1-4 0 3 3 0 0 1-6 0z"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
}


def icon(name, cls="omx-i"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg>')


# status-badge z @open-mercato/ui: success / warning / info / error / neutral
def status(text, kind, cls=""):
    return f'<span class="omx-st {kind}{" " + cls if cls else ""}">{esc(text)}</span>'


OM_CSS = """
.slate.omx .slate-body{align-items:center}
.omx-win{position:relative;width:1200px;height:600px;background:#fff;border-radius:16px;overflow:hidden;text-align:left;
  box-shadow:0 40px 90px rgba(0,0,0,.55);display:grid;grid-template-columns:224px 1fr;
  font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;color:#0a0a0a;font-size:15px;line-height:1.35}
.omx-i{width:17px;height:17px;flex:none}
.omx-side{background:#fafafa;border-right:1px solid #e5e5e5;padding:14px 12px;display:flex;flex-direction:column;gap:10px}
.omx-org{display:flex;align-items:center;gap:10px;padding:8px;border-radius:12px;background:#fff;border:1px solid #e5e5e5}
.omx-org i{width:32px;height:32px;border-radius:9px;background:#171717;color:#fff;display:flex;align-items:center;justify-content:center;font:700 14px/1 system-ui;font-style:normal;flex:none}
.omx-org>div{min-width:0}
.omx-org b{display:block;font-size:14px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.omx-org span{display:block;font-size:12px;color:#737373}
.omx-find{display:flex;align-items:center;gap:8px;height:34px;padding:0 10px;border:1px solid #e5e5e5;border-radius:8px;background:#fff;color:#a3a3a3;font-size:14px}
.omx-find .omx-i{width:15px;height:15px}
.omx-grp{display:flex;justify-content:space-between;align-items:center;margin:8px 8px 2px;font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:.04em;color:#737373}
.omx-grp .omx-i{width:13px;height:13px}
.omx-link{position:relative;display:flex;align-items:center;gap:10px;height:34px;padding:0 10px;border-radius:9px;font-size:14.5px;font-weight:500;color:#404040}
.omx-link .omx-i{color:#737373}
.omx-link.on{background:#ececec;color:#0a0a0a} .omx-link.on .omx-i{color:#0a0a0a}
.omx-link.on:before{content:"";position:absolute;left:-12px;top:7px;width:4px;height:20px;border-radius:0 3px 3px 0;background:#0a0a0a}
.omx-sep{height:1px;background:#e5e5e5;margin:4px 6px}
.omx-main{position:relative;display:flex;flex-direction:column;min-width:0;background:#fff}
.omx-top{height:52px;flex:none;display:flex;align-items:center;gap:8px;padding:0 20px;border-bottom:1px solid #e5e5e5;font-size:14px;color:#737373}
.omx-top .omx-i{width:15px;height:15px} .omx-top b{color:#0a0a0a;font-weight:500}
.omx-top .r{margin-left:auto;display:flex;align-items:center;gap:14px}
.omx-ai{height:30px;padding:0 10px;border:1px solid #e5e5e5;border-radius:8px;display:flex;align-items:center;gap:6px;color:#404040;font-weight:500}
.omx-ai kbd{font:12px system-ui;color:#a3a3a3}
.omx-who{display:flex;align-items:center;gap:8px;color:#404040;font-weight:500}
.omx-who i{width:28px;height:28px;border-radius:50%;background:#e5e5e5;display:flex;align-items:center;justify-content:center;font:600 12px system-ui;font-style:normal;color:#404040}
.omx-body{flex:1;padding:18px 20px;min-height:0;display:flex;flex-direction:column;gap:14px;background:#fafafa}
.omx-card{background:#fff;border:1px solid #e5e5e5;border-radius:14px;display:flex;flex-direction:column;min-height:0;overflow:hidden}
.omx-ch{display:flex;align-items:flex-start;gap:10px;padding:14px 16px 10px}
.omx-ch h3{margin:0;font-size:18px;font-weight:600} .omx-ch p{margin:2px 0 0;font-size:13.5px;color:#737373}
.omx-ch .r{margin-left:auto;display:flex;gap:8px;align-items:center}
.omx-btn{height:34px;padding:0 13px;border:1px solid #e5e5e5;border-radius:8px;background:#fff;display:inline-flex;align-items:center;gap:7px;font-size:14px;font-weight:500;color:#0a0a0a;white-space:nowrap}
.omx-btn .omx-i{width:15px;height:15px}
.omx-btn.pri{background:#171717;border-color:#171717;color:#fff}
.omx-btn.ico{width:34px;padding:0;justify-content:center}
.omx-bar{display:flex;gap:8px;padding:0 16px 12px}
.omx-q{flex:1;max-width:300px;height:34px;padding:0 10px;border:1px solid #e5e5e5;border-radius:8px;display:flex;align-items:center;gap:8px;font-size:14px;color:#a3a3a3}
.omx-q .omx-i{width:15px;height:15px}
.omx-t{width:100%;border-collapse:collapse;table-layout:fixed;font-size:14.5px}
.omx-t th{height:36px;padding:0 12px;text-align:left;font-size:13.5px;font-weight:500;color:#737373;background:#fafafa;border-top:1px solid #e5e5e5;border-bottom:1px solid #e5e5e5;white-space:nowrap;overflow:hidden}
.omx-t th + th{border-left:1px solid #f0f0f0}
.omx-t td{height:46px;padding:0 12px;border-bottom:1px solid #f0f0f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.omx-t td.mut,.omx-t .mut{color:#737373} .omx-t td.num{font-variant-numeric:tabular-nums}
.omx-t .cb{width:40px} .omx-t .cb i{display:block;width:15px;height:15px;border:1.5px solid #d4d4d4;border-radius:4px}
.omx-t .act{width:44px;color:#a3a3a3} .omx-t .act .omx-i{width:16px;height:16px}
.omx-t tr.hl td{background:#fffbeb}
.omx-foot{display:flex;justify-content:space-between;align-items:center;padding:10px 16px;font-size:13px;color:#737373;margin-top:auto}
.omx-pg{display:flex;gap:4px} .omx-pg span{width:28px;height:28px;border:1px solid #e5e5e5;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#404040}
.omx-pg span.on{background:#171717;color:#fff;border-color:#171717}
.omx-st{display:inline-flex;align-items:center;height:24px;padding:0 9px;border-radius:999px;font-size:12.5px;font-weight:500;border:1px solid transparent;white-space:nowrap}
.omx-st.success{background:#ecfdf3;color:#067647;border-color:#abefc6} .omx-st.warning{background:#fffaeb;color:#b54708;border-color:#fedf89}
.omx-st.info{background:#eff8ff;color:#175cd3;border-color:#b2ddff} .omx-st.error{background:#fef3f2;color:#b42318;border-color:#fecdca}
.omx-st.neutral{background:#f5f5f5;color:#404040;border-color:#e5e5e5}
.omx-thumb{display:inline-flex;width:30px;height:30px;border-radius:7px;background:#f5f5f5;border:1px solid #e5e5e5;align-items:center;justify-content:center;color:#a3a3a3;vertical-align:middle;margin-right:10px}
.omx-thumb .omx-i{width:15px;height:15px}
.omx-sku{display:block;font-size:12.5px;color:#737373}
.omx-cell2{display:inline-flex;flex-direction:column;vertical-align:middle;line-height:1.25}
.omx-flash{position:absolute;top:64px;right:18px;z-index:5;display:flex;align-items:flex-start;gap:10px;width:340px;padding:12px 14px;border-radius:12px;
  background:#fff;border:1px solid #abefc6;box-shadow:0 12px 30px rgba(0,0,0,.14);font-size:14px;opacity:0}
.omx-flash .omx-i{color:#067647;margin-top:1px} .omx-flash b{display:block;font-weight:600} .omx-flash span{color:#525252;font-size:13px}
.omx-sheet{position:absolute;top:0;right:0;bottom:0;width:400px;z-index:4;background:#fff;border-left:1px solid #e5e5e5;box-shadow:-24px 0 50px rgba(0,0,0,.12);
  padding:18px 20px;display:flex;flex-direction:column;gap:12px;opacity:0}
.omx-sheet h4{margin:0;font-size:18px;font-weight:600;display:flex;align-items:center} .omx-sheet h4 .omx-i{margin-left:auto;color:#a3a3a3}
.omx-sheet .sub{font-size:13.5px;color:#737373;margin-top:-6px}
.omx-kv{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.omx-kv div{background:#fff;border:1px solid #e5e5e5;border-radius:12px;padding:12px 14px}
.omx-kv span{display:block;font-size:12.5px;color:#737373} .omx-kv b{display:block;font-size:17px;font-weight:600;margin-top:4px}
.omx-tabs{display:flex;gap:22px;padding:0 16px;border-bottom:1px solid #e5e5e5;font-size:14.5px;color:#737373}
.omx-tabs span{display:flex;align-items:center;gap:7px;height:40px;border-bottom:2px solid transparent}
.omx-tabs span.on{color:#0a0a0a;font-weight:600;border-color:#4f46e5} .omx-tabs .omx-i{width:15px;height:15px}
.omx-tabs em{font-style:normal;font-size:12px;background:#f5f5f5;border-radius:999px;padding:1px 7px;color:#525252}
.omx-eyebrow{font-size:12.5px;font-weight:500;color:#737373;text-transform:uppercase;letter-spacing:.05em}
.omx-head{display:flex;align-items:flex-end;gap:12px}
.omx-head h2{margin:2px 0 0;font-size:24px;font-weight:600;display:flex;align-items:center;gap:12px}
.omx-head .r{margin-left:auto;display:flex;gap:8px}
.omx-note{display:flex;align-items:center;gap:8px;font-size:13.5px;color:#525252}
.omx-note .omx-i{width:15px;height:15px;color:#7c3aed}
.omx-ai-tag{display:inline-flex;align-items:center;gap:4px;height:22px;padding:0 7px;border-radius:999px;background:#f5f3ff;color:#6d28d9;font-size:12px;font-weight:500;border:1px solid #ddd6fe}
.omx-ai-tag .omx-i{width:12px;height:12px}
.omx-ch-chip{display:inline-flex;align-items:center;height:24px;padding:0 8px;margin-right:5px;border-radius:6px;border:1px solid #e5e5e5;font-size:12.5px;font-weight:500;color:#404040;background:#fff}
"""


def shell(tenant, role, groups, active, crumbs, body, who="", extra=""):
    """Powłoka OM: sidebar (firma, szukajka, grupy z ikonami), pasek z okruszkami, treść."""
    nav = ""
    for i, (title, links) in enumerate(groups):
        if i:
            nav += '<div class="omx-sep"></div>'
        if title:
            nav += f'<div class="omx-grp">{esc(title)}{icon("chevdown")}</div>'
        nav += "".join(f'<div class="omx-link{" on" if label == active else ""}">{icon(ic)}{esc(label)}</div>' for ic, label in links)
    trail = icon("home") + "".join(f'{icon("chevright")}{"<b>" if k == len(crumbs) - 1 else ""}{esc(c)}{"</b>" if k == len(crumbs) - 1 else ""}'
                                   for k, c in enumerate(crumbs))
    initials = "".join(w[0] for w in who.split()[:2]).upper() if who else ""
    person = f'<span class="omx-who"><i>{esc(initials)}</i>{esc(who)}</span>' if who else ""
    return (f'<div class="omx-win"><div class="omx-side"><div class="omx-org"><i>{esc(tenant[0])}</i><div><b>{esc(tenant)}</b>'
            f'<span>{esc(role)}</span></div></div><div class="omx-find">{icon("search")}Szukaj…</div>{nav}</div>'
            f'<div class="omx-main"><div class="omx-top">{trail}<span class="r"><span class="omx-ai">{icon("sparkles")}AI <kbd>⌘L</kbd></span>'
            f'{icon("bell")}{person}</span></div><div class="omx-body">{body}</div>{extra}</div></div>')


def table(head, rows, widths, cls=""):
    th = "".join(f'<th style="width:{w}">{h}</th>' for h, w in zip(head, widths))
    return f'<table class="omx-t {cls}"><tr>{th}</tr>{"".join(rows)}</table>'


def card_head(title, sub, actions):
    return f'<div class="omx-ch"><div><h3>{title}</h3><p>{sub}</p></div><div class="r">{actions}</div></div>'


def btn(text, ic=None, primary=False, cls=""):
    return f'<span class="omx-btn{" pri" if primary else ""}{" " + cls if cls else ""}">{icon(ic) if ic else ""}{esc(text)}</span>'


def search_bar(placeholder, extra=""):
    return f'<div class="omx-bar"><div class="omx-q">{icon("search")}{esc(placeholder)}</div>{btn("Filtry", "filter")}{extra}</div>'


def flash(title, text):
    return f'<div class="omx-flash">{icon("check")}<div><b>{esc(title)}</b><span>{esc(text)}</span></div></div>'


def slate(comp, ev, start, end, inner):
    return own_slate(comp, start, end, "omx", OM_CSS, inner, pip=ev.get("pip", True))


def press(comp, selector, at):
    comp.js.append(f'tl.to("{selector}",{{scale:0.93,duration:0.12,yoyo:true,repeat:1}},{comp.q(at)});')


def show(comp, selector, at, frm="{opacity:0,y:12}", to="{opacity:1,y:0,duration:0.3}", stagger=None):
    to = to[:-1] + (f",stagger:{stagger}}}" if stagger else "}")
    comp.js.append(f'tl.fromTo("{selector}",{frm},{to},{comp.q(at)});')


# ── Panel klienta B2B (ep-rezon ~6:56, ep-8-wdrozen): „klient sam się loguje, sam może złożyć zamówienie,
# sam widzi statusy… pracownik w biurze dostaje powiadomienie”. Każda miejscowość ma swoje wzory.
B2B_CATALOG = [("Magnes ceramiczny", "MG-114", "latarnia", "24 szt.", 120), ("Kubek 300 ml", "KB-031", "herb miasta", "6 szt.", 36),
               ("Brelok drewniany", "BR-207", "mewa", "20 szt.", 80), ("Pocztówka", "PC-501", "molo", "50 szt.", 0),
               ("Otwieracz z magnesem", "OT-012", "kotwica", "12 szt.", 0), ("Muszelka z napisem", "MU-088", "muszla", "30 szt.", 0),
               ("Kubek emaliowany", "KE-019", "statek", "6 szt.", 0)]
B2B_HISTORY = [("#1042", "12.11", "W produkcji", "warning"), ("#1037", "04.11", "Wysłane", "info"), ("#1029", "21.10", "Dostarczone", "success")]


def b2b_portal(comp, ev, start, end):
    if ev.get("mode") == "rep":
        return b2b_rep(comp, ev, start, end)
    rows = [f'<tr class="omx-p"><td><span class="omx-thumb">{icon("image")}</span><span class="omx-cell2">{esc(n)}<span class="omx-sku">{sku}</span></span></td>'
            f'<td>Ustka · {esc(pattern)}</td><td class="mut">{pack}</td><td class="num"><b>{qty or "—"}</b></td></tr>'
            for n, sku, pattern, pack, qty in B2B_CATALOG]
    cat = (f'<div class="omx-card" style="flex:1">{card_head("Katalog · wzory „Ustka”", "Wzory przypisane do Twojej miejscowości · 48 produktów", btn("Pobierz katalog PDF", "download"))}'
           f'{search_bar("Szukaj produktu lub kodu…")}{table(["Produkt", "Wzór", "Opakowanie", "Ilość"], rows, ["40%", "26%", "17%", "17%"])}</div>')
    orders = (f'<div class="omx-card omx-ord">{card_head("Moje zamówienia", "Statusy na bieżąco", "")}'
              + table(["Nr", "Data", "Status"],
                      [f'<tr class="omx-new"><td><b>#1049</b></td><td class="mut">dziś</td><td>{status("Nowe", "info", "omx-new-st")}</td></tr>']
                      + [f'<tr><td><b>{n}</b></td><td class="mut">{d}</td><td>{status(s, k)}</td></tr>' for n, d, s, k in B2B_HISTORY],
                      ["28%", "26%", "46%"]) + '</div>')
    cart = (f'<div class="omx-card">{card_head("Koszyk", "3 pozycje · 236 szt.", "")}'
            f'<div style="padding:0 16px 14px">{btn("Złóż zamówienie", "cart", True, "omx-go")}</div></div>')
    body = f'<div style="display:grid;grid-template-columns:1fr 330px;gap:14px;flex:1;min-height:0">{cat}<div style="display:flex;flex-direction:column;gap:14px">{cart}{orders}</div></div>'
    inner = shell("Hurtownia pamiątek", "Portal klienta",
                  [(None, [("dashboard", "Pulpit"), ("package", "Katalog"), ("cart", "Moje zamówienia"), ("file", "Faktury"), ("message", "Reklamacje")])],
                  "Katalog", ["Katalog", "Wzory „Ustka”"], body, who="Sklep z pamiątkami",
                  extra=flash("Zamówienie #1049 złożone", "Biuro dostało powiadomienie o nowym zamówieniu"))
    sid = slate(comp, ev, start, end, inner)
    S, span = f"#{sid}", end - start
    if span < 4.0:
        raise SystemExit(f"makieta b2b @ {start:.1f}: {span:.1f} s — za krótko na zamówienie i zmianę statusu (min. 4 s)")
    show(comp, f"{S} .omx-p", start + 0.3, "{opacity:0,x:24}", "{opacity:1,x:0,duration:0.3}", 0.12)
    click = start + max(1.8, span * 0.4)
    comp.js.append(f'tl.set("{S} .omx-new",{{opacity:0}},{comp.q(start)});')
    press(comp, f"{S} .omx-go", click)
    show(comp, f"{S} .omx-new", click + 0.3, "{opacity:0,x:30}", "{opacity:1,x:0,duration:0.35}")
    show(comp, f"{S} .omx-flash", click + 0.7, "{opacity:0,y:-14}", "{opacity:1,y:0,duration:0.35}")
    flip = max(click + 0.9, min(end - 0.8, click + 2.4))
    comp.js.append(f'tl.call(function(){{var b=document.querySelector("{S} .omx-new-st");if(b){{b.textContent="Nowe";b.className="omx-st info omx-new-st";}}}},null,{comp.q(click + 0.3)});')
    comp.js.append(f'tl.call(function(){{var b=document.querySelector("{S} .omx-new-st");if(b){{b.textContent="W produkcji";b.className="omx-st warning omx-new-st";}}}},null,{comp.q(flip)});')


# ── Panel handlowca (ep-rezon ~7:36, ep-8-wdrozen): „handlowiec widzi zamówienia swoich klientów… wprowadza
# za klienta zamówienie”.
REP_CLIENTS = [("Sklep z pamiątkami", "Ustka", "#1049 · dziś", "W produkcji", "warning"), ("Pamiątki „Bursztyn”", "Łeba", "#1050 · dziś", "Nowe", "info"),
               ("Kiosk przy plaży", "Rowy", "#1044 · 3 dni temu", "Wysłane", "info"), ("Sklep „Latarnia”", "Jarosławiec", "#1039 · 8 dni temu", "Dostarczone", "success"),
               ("Galanteria nadmorska", "Darłowo", "#1031 · 15 dni temu", "Dostarczone", "success"),
               ("Pamiątki „Mewa”", "Dąbki", "#1027 · 18 dni temu", "Dostarczone", "success"),
               ("Sklep przy promenadzie", "Mielno", "#1022 · 22 dni temu", "Dostarczone", "success")]


def b2b_rep(comp, ev, start, end):
    rows = [f'<tr class="omx-p{" hl omx-pick" if i == 2 else ""}"><td class="cb"><i></i></td><td><b style="font-weight:500">{esc(c)}</b></td><td>{esc(town)}</td>'
            f'<td class="mut">{esc(last)}</td><td>{status(st, k)}</td><td class="act">{icon("more")}</td></tr>'
            for i, (c, town, last, st, k) in enumerate(REP_CLIENTS)]
    lst = (f'<div class="omx-card" style="flex:1">{card_head("Moi klienci", "Region: wybrzeże środkowe · 18 klientów", btn("", "refresh", cls="ico") + btn("Eksportuj", "download") + btn("Zamów za klienta", "plus", True, "omx-go"))}'
           f'{search_bar("Szukaj klienta lub miejscowości…")}'
           f'{table(["", "Klient", "Miejscowość", "Ostatnie zamówienie", "Status", ""], rows, ["40px", "30%", "19%", "27%", "19%", "44px"])}'
           f'<div class="omx-foot">Wyświetlanie 1 do 7 z 18<span class="omx-pg"><span>‹</span><span class="on">1</span><span>2</span><span>3</span><span>4</span><span>›</span></span></div></div>')
    lines = "".join(f'<tr><td>{esc(n)}<span class="omx-sku">{sku} · Rowy · {esc(p)}</span></td><td class="num">{q}</td></tr>'
                    for n, sku, p, _, q in [r for r in B2B_CATALOG if r[4]])
    sheet = (f'<div class="omx-sheet"><h4>Nowe zamówienie{icon("x")}</h4><div class="sub">W imieniu klienta: Kiosk przy plaży, Rowy</div>'
             f'<div class="omx-note">{icon("history")}Na podstawie ostatniego zamówienia #1044</div>'
             f'<div class="omx-card">{table(["Produkt", "Ilość"], [lines], ["75%", "25%"])}</div>'
             f'<div class="omx-kv" style="grid-template-columns:1fr 1fr"><div><span>Razem</span><b>236 szt.</b></div><div><span>Realizacja</span><b>5 dni roboczych</b></div></div>'
             f'<div class="omx-note">{icon("bell")}Klient zobaczy zamówienie w swoim portalu</div>'
             f'<div style="margin-top:auto;display:flex;gap:8px;justify-content:flex-end">{btn("Anuluj")}{btn("Zapisz zamówienie", "check", True, "omx-save")}</div></div>')
    inner = shell("Hurtownia pamiątek", "Panel handlowca",
                  [(None, [("dashboard", "Pulpit"), ("users", "Klienci"), ("cart", "Zamówienia"), ("package", "Katalog")]),
                   ("Teren", [("truck", "Trasy"), ("list", "Wizyty")])],
                  "Klienci", ["Klienci", "Moi klienci"], lst, who="Handlowiec", extra=sheet)
    sid = slate(comp, ev, start, end, inner)
    S, span = f"#{sid}", end - start
    show(comp, f"{S} .omx-p", start + 0.3, "{opacity:0,x:24}", "{opacity:1,x:0,duration:0.3}", 0.15)
    click = start + max(1.8, span * 0.38)
    press(comp, f"{S} .omx-go", click)
    show(comp, f"{S} .omx-sheet", click + 0.25, "{opacity:0,x:80}", "{opacity:1,x:0,duration:0.4,ease:'power3.out'}")
    press(comp, f"{S} .omx-save", min(end - 0.9, click + 2.6))


# ── Import zamówienia z dopasowaniem (ep-doram ~6:08): „mogło być w kilku różnych kolorach — nie dopasowałem,
# na 80% to ten produkt albo na 100%”. Jedną pozycję poprawia człowiek i system ją zapamiętuje.
MATCH_ROWS = [
    ("Gartenstuhl Alu, grau", "Krzesło ogrodowe aluminiowe, szare", "KR-ALU-01-SZ", 40, 100),
    ("Sitzkissen 45×45 anthrazit", "Poduszka na siedzisko 45×45, antracyt", "PS-4545-ANT", 80, 100),
    ("Bench cushion 120 beige", "Poduszka na ławkę 120 cm, beżowa", "PL-120-BEZ", 12, 80),
    ("Auflage Hochlehner Dessin 42", "Poduszka na krzesło z wysokim oparciem, wzór 42", "PW-HL-W42", 24, 0),
    ("Sonnenschirm 3 m", "Parasol ogrodowy 3 m", "PA-300", 6, 100),
]


def match_import(comp, ev, start, end):
    def score(s):
        return status(f"{s}%", "success" if s >= 100 else "warning") if s else status("brak dopasowania", "error", "omx-miss")
    rows = []
    for theirs, ours, sku, qty, s in MATCH_ROWS:
        fix = s == 0
        product = (f'<span class="omx-ours"><span class="omx-empty mut">— wybierz produkt —</span><span class="omx-fixed">{esc(ours)}</span></span>' if fix
                   else esc(ours))
        rows.append(f'<tr class="omx-p{" omx-fix" if fix else ""}"><td class="mut" style="font-style:italic">{esc(theirs)}</td><td>{product}</td>'
                    f'<td class="mut">{sku if not fix else "<span class=omx-fixed>" + sku + "</span>"}</td><td class="num">{qty}</td>'
                    f'<td><span class="omx-sc">{score(s)}{status("100% · zapamiętane", "success", "omx-ok") if fix else ""}</span></td></tr>')
    card = (f'<div class="omx-card" style="flex:1">{card_head("Import zamówienia", "zamowienie_kontrahenta.xlsx · Kontrahent A · 5 pozycji", btn("Anuluj") + btn("Utwórz zamówienie", "check", True))}'
            f'{table(["Pozycja kontrahenta", "Produkt w systemie", "Kod", "Ilość", "Dopasowanie"], rows, ["25%", "33%", "15%", "8%", "19%"])}'
            f'<div class="omx-foot"><span class="omx-note">{icon("sparkles")}<b style="color:#0a0a0a;font-weight:600">4 z 5</b>&nbsp;dopasowane automatycznie'
            f'<span class="omx-memo">&nbsp;· 1 poprawka zapisana w słowniku nazw</span></span><span>Kontrahent A · 214 znanych nazw</span></div></div>')
    css = (".omx-t td{height:60px}.omx-ours{display:grid}.omx-ours>*{grid-area:1/1}.omx-sc{display:grid}.omx-sc>*{grid-area:1/1;justify-self:start}"
           ".omx-t tr.omx-fix td{transition:none}")
    inner = shell("Meble ogrodowe", "Biuro obsługi zamówień",
                  [("Sprzedaż", [("cart", "Zamówienia"), ("users", "Kontrahenci")]),
                   ("Produkcja", [("factory", "Zlecenia"), ("tag", "Etykiety")]),
                   ("Katalog", [("package", "Produkty"), ("book", "Słownik nazw")])],
                  "Zamówienia", ["Zamówienia", "Import z pliku"], f"<style>{css}</style>{card}", who="Biuro")
    sid = slate(comp, ev, start, end, inner)
    S, span = f"#{sid}", end - start
    if span < 4.0:
        raise SystemExit(f"makieta match @ {start:.1f}: {span:.1f} s — za krótko, żeby pokazać poprawkę (min. 4 s)")
    show(comp, f"{S} .omx-p", start + 0.3, "{opacity:0,x:-24}", "{opacity:1,x:0,duration:0.3}", 0.16)
    show(comp, f"{S} .omx-sc .omx-st:first-child", start + 0.6, "{scale:0}", "{scale:1,duration:0.3,ease:'back.out(2)'}", 0.16)
    fix = min(start + max(2.5, span * 0.55), end - 1.6)
    q = comp.q
    comp.js.append(f'tl.set("{S} .omx-fix .omx-fixed, {S} .omx-ok, {S} .omx-memo",{{opacity:0}},{q(start)});')
    comp.js.append(f'tl.to("{S} .omx-fix td",{{backgroundColor:"#fffbeb",duration:0.25}},{q(fix)});')
    comp.js.append(f'tl.to("{S} .omx-fix .omx-empty, {S} .omx-miss",{{opacity:0,duration:0.2}},{q(fix)});')
    comp.js.append(f'tl.to("{S} .omx-fix .omx-fixed",{{opacity:1,duration:0.3}},{q(fix + 0.2)});')
    comp.js.append(f'tl.fromTo("{S} .omx-ok",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.35,ease:"back.out(2)"}},{q(fix + 0.5)});')
    comp.js.append(f'tl.to("{S} .omx-memo",{{opacity:1,duration:0.3}},{q(fix + 0.9)});')


# ── Etykiety (ep-doram ~9:40, ep-8-wdrozen): „system bierze cztery numery, generuje PDF od razu gotowy,
# po minucie masz PDF z 40 stronami etykiet”.
LABEL_CSS = """
.omx-lb{position:relative;height:270px;margin:14px 0 0 6px}
.omx-lb-page{position:absolute;left:0;top:0;width:220px;height:240px;background:#fff;border:1px solid #d4d4d4;border-radius:6px;box-shadow:0 8px 20px rgba(0,0,0,.12);padding:14px;font-size:13px;color:#404040}
.omx-lb-page b{display:block;font-size:16px;color:#0a0a0a;margin-bottom:8px}
.omx-lb-bars{display:flex;gap:2px;height:70px;margin:10px 0} .omx-lb-bars i{display:block;background:#0a0a0a;height:100%}
.omx-lb-page small{display:block;color:#737373;margin-top:4px}
"""


def labels_order(comp, ev, start, end):
    bars = "".join(f'<i style="width:{w}px"></i>' for w in (4, 2, 5, 2, 3, 5, 2, 4, 2, 5, 3, 2, 5, 2, 4, 3, 5, 2, 3, 2, 4, 3, 2, 5))
    pages = "".join(f'<div class="omx-lb-page" style="z-index:{10 - i}"><b>ZAM-2026-0418</b>PROD 114 · CZ 07<div class="omx-lb-bars">{bars}</div>'
                    f'Paczka {5 - i}/40<small>Poduszka na siedzisko 45×45</small></div>' for i in range(5))
    lines = [f'<tr><td>{esc(n)}<span class="omx-sku">{sku}</span></td><td class="num">{q}</td><td class="num">{p}</td><td>{status("Gotowe", "success") if d else status("W produkcji", "warning")}</td></tr>'
             for n, sku, q, p, d in [("Poduszka na siedzisko 45×45, antracyt", "PS-4545-ANT", 80, 16, True),
                                     ("Poduszka na ławkę 120 cm, beżowa", "PL-120-BEZ", 12, 12, True),
                                     ("Poduszka na krzesło, wzór 42", "PW-HL-W42", 24, 12, False)]]
    body = (f'<div class="omx-head"><div><div class="omx-eyebrow">Zamówienie</div><h2>ZAM-2026-0418 {status("W produkcji", "warning")}</h2></div>'
            f'<div class="r">{btn("Edytuj")}{btn("Generuj etykiety", "printer", True, "omx-go")}</div></div>'
            f'<div class="omx-kv"><div><span>Kontrahent</span><b>Kontrahent A</b></div><div><span>Zlecenie produkcyjne</span><b>PROD 114</b></div>'
            f'<div><span>Część dostawy</span><b>CZ 07</b></div><div><span>Paczki</span><b>40</b></div></div>'
            f'<div class="omx-card" style="flex:1"><div class="omx-tabs"><span class="on">{icon("list")}Pozycje<em>3</em></span>'
            f'<span>{icon("tag")}Etykiety<em>0</em></span><span>{icon("history")}Historia</span></div>'
            f'{table(["Produkt", "Ilość", "Paczki", "Status"], lines, ["52%", "13%", "13%", "22%"])}</div>')
    sheet = (f'<div class="omx-sheet"><h4>Etykiety · ZAM-2026-0418{icon("x")}</h4><div class="sub">40 paczek · format 100×150 mm</div>'
             f'<div class="omx-lb">{pages}</div>'
             f'<div class="omx-note omx-done" style="color:#067647;font-weight:600">{icon("check")}PDF gotowy · 40 stron · 54 s</div>'
             f'<div style="margin-top:auto;display:flex;gap:8px;justify-content:flex-end">{btn("Drukuj", "printer")}{btn("Pobierz PDF", "download", True)}</div></div>')
    inner = shell("Meble ogrodowe", "Produkcja",
                  [("Sprzedaż", [("cart", "Zamówienia"), ("users", "Kontrahenci")]),
                   ("Produkcja", [("factory", "Zlecenia"), ("tag", "Etykiety")]),
                   ("Katalog", [("package", "Produkty"), ("book", "Słownik nazw")])],
                  "Zamówienia", ["Zamówienia", "ZAM-2026-0418"], f"<style>{LABEL_CSS}</style>{body}", who="Produkcja", extra=sheet)
    sid = slate(comp, ev, start, end, inner)
    S, span = f"#{sid}", end - start
    click = start + max(1.2, min(2.0, span * 0.3))
    show(comp, f"{S} .omx-kv div", start + 0.25, "{opacity:0,y:14}", "{opacity:1,y:0,duration:0.3}", 0.1)
    press(comp, f"{S} .omx-go", click)
    show(comp, f"{S} .omx-sheet", click + 0.25, "{opacity:0,x:80}", "{opacity:1,x:0,duration:0.4,ease:'power3.out'}")
    comp.js.append(f'tl.set("{S} .omx-lb-page, {S} .omx-done",{{opacity:0}},{comp.q(start)});')
    comp.js.append(f'tl.fromTo("{S} .omx-lb-page",{{opacity:0,x:-60,rotation:-6}},{{opacity:1,x:function(i){{return (4-i)*20}},'
                   f'y:function(i){{return (4-i)*5}},rotation:function(i){{return -3+(4-i)*1.5}},duration:0.35,stagger:-0.15,ease:"power3.out"}},{comp.q(click + 0.6)});')
    show(comp, f"{S} .omx-done", min(end - 0.8, click + 1.9), "{opacity:0,y:10}", "{opacity:1,y:0,duration:0.3}")


# ── Katalog z faktury (ep-marpasz ~6:14, ep-8-wdrozen): „AI odczytuje fakturę od dostawcy, zakłada produkty
# i pisze opisy pod każdą platformę”.
CATALOG_ROWS = [("Karma dla psa, jagnięcina", "5901234123457", "15 kg", "Psy · karma sucha"),
                ("Pasza dla kur niosek", "5901234567892", "25 kg", "Drób · pasze"),
                ("Przysmaki dla kota, łosoś", "5907771234561", "0,5 kg", "Koty · przysmaki")]
CATALOG_CSS = """
.omx-inv{width:250px;flex:none;padding:14px;display:flex;flex-direction:column;gap:9px}
.omx-inv-doc{flex:1;border:1px solid #e5e5e5;border-radius:8px;padding:14px;background:#fff;display:flex;flex-direction:column;gap:9px}
.omx-inv-doc b{font-size:13px} .omx-inv-doc i{display:block;height:7px;border-radius:3px;background:#ececec}
.omx-inv-doc i.hl{background:#ede9fe}
.omx-desc{margin:12px 16px 0;padding:0 14px 12px;border:1px solid #e5e5e5;border-radius:10px;background:#fcfcfc}
.omx-desc p{margin:10px 0 0;font-size:14px;line-height:1.5;color:#404040} .omx-desc b{color:#0a0a0a;font-weight:600}
"""


def catalog_invoice(comp, ev, start, end):
    rows = [f'<tr class="omx-p"><td><span class="omx-thumb">{icon("image")}</span><span class="omx-cell2">{esc(n)}<span class="omx-sku">EAN {ean}</span></span></td>'
            f'<td class="num">{w}</td><td class="mut">{esc(cat)}</td>'
            f'<td><span class="omx-chans"><span class="omx-ch-chip">Allegro</span><span class="omx-ch-chip">Sklep</span><span class="omx-ch-chip">Erli</span></span></td></tr>'
            for n, ean, w, cat in CATALOG_ROWS]
    doc_lines = "".join(f'<i class="{"hl" if k in (3, 4, 5) else ""}" style="width:{w}%"></i>' for k, w in enumerate([60, 90, 40, 95, 88, 92, 70, 50, 80, 35]))
    inv = (f'<div class="omx-card omx-inv"><div style="display:flex;align-items:center;gap:8px;font-weight:600;font-size:14px">{icon("file")}FV/2026/11/082</div>'
           f'<div class="omx-inv-doc"><b>Faktura VAT · dostawca karm</b>{doc_lines}</div><span class="mut" style="font-size:12.5px;color:#737373">PDF · 3 pozycje · wgrany 09:14</span></div>')
    lst = (f'<div class="omx-card" style="flex:1">{card_head("Produkty z faktury", "<span class=omx-ai-tag>" + icon("sparkles") + "rozpoznane przez AI</span>&nbsp; nazwy, kategorie i opisy pod kanały sprzedaży", "")}'
           f'{table(["Produkt", "Waga", "Kategoria", "Opisy gotowe"], rows, ["35%", "10%", "21%", "34%"])}'
           f'<div class="omx-desc"><div class="omx-tabs" style="padding:0"><span class="on">{icon("store")}Allegro</span><span>Sklep</span><span>Erli</span></div>'
           f'<p><b>Karma dla psa z jagnięciną 15 kg</b> — pełnoporcjowa karma sucha dla psów dorosłych średnich i dużych ras. '
           f'Jagnięcina jako pierwsze źródło białka, bez sztucznych barwników. Worek 15 kg wystarcza na ok. 6 tygodni.</p></div>'
           f'<div class="omx-foot"><span class="omx-note">{icon("sparkles")}Opisy przygotowane osobno pod Allegro, sklep i Erli</span>'
           f'{btn("Dodaj do magazynu (3)", "warehouse", True, "omx-go")}</div></div>')
    body = f'<div style="display:flex;gap:14px;flex:1;min-height:0">{inv}{lst}</div>'
    inner = shell("Hurtownia karm", "Biuro",
                  [("Katalog", [("package", "Produkty"), ("upload", "Import z faktury")]),
                   ("Sprzedaż", [("cart", "Zamówienia"), ("store", "Kanały sprzedaży")]),
                   ("Magazyn", [("warehouse", "Stany"), ("truck", "Przesyłki")])],
                  "Import z faktury", ["Katalog", "Import z faktury"], f"<style>{CATALOG_CSS}</style>{body}", who="Biuro")
    sid = slate(comp, ev, start, end, inner)
    S = f"#{sid}"
    show(comp, f"{S} .omx-inv", start + 0.2, "{opacity:0,y:20}", "{opacity:1,y:0,duration:0.35}")
    show(comp, f"{S} .omx-inv-doc i.hl", start + 0.6, "{backgroundColor:'#ececec'}", "{backgroundColor:'#ddd6fe',duration:0.3}", 0.12)
    show(comp, f"{S} .omx-p", start + 1.0, "{opacity:0,x:24}", "{opacity:1,x:0,duration:0.3}", 0.25)
    show(comp, f"{S} .omx-ch-chip", start + 2.1, "{opacity:0,scale:0.7}", "{opacity:1,scale:1,duration:0.2}", 0.07)
    show(comp, f"{S} .omx-desc", start + 2.6, "{opacity:0,y:14}", "{opacity:1,y:0,duration:0.35}")
    show(comp, f"{S} .omx-go", start + 3.0, "{opacity:0,scale:0.85}", "{opacity:1,scale:1,duration:0.3,ease:'back.out(2)'}")
    press(comp, f"{S} .omx-go", min(end - 0.8, start + 3.8))


SCREENS = {"b2b": b2b_portal, "match": match_import, "labels": labels_order, "catalog": catalog_invoice}
