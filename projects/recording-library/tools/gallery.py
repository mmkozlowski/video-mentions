#!/usr/bin/env python3
"""Galeria próbek do przeglądu: final/samples/index.html (otwórz w przeglądarce).

Każdy klip w jednym rzędzie: format × paleta A/B obok siebie — paletę wybiera się
na żywym materiale, nie na opisie.

  python3 tools/gallery.py && open final/samples/index.html
"""
import html
import json

from package import FINAL, PACK, PALETTES, output_name, palettes_for
from sources import DATA

FORMATS = [("reels", "Reels / TikTok 9:16 — organiczne, CTA w komentarzu"),
           ("ad", "Reklama Meta 9:16 — chip CTA + plansza końcowa"),
           ("youtube", "YouTube 16:9 — panel boczny, bez napisów")]


def main():
    clips = {c["id"]: c for c in json.load(open(DATA / "clips.json"))}
    boards = sorted(PACK.glob("storyboards/*.json"))
    rows = []
    for path in boards:
        board = json.load(open(path))
        clip = clips[board["clip"]]
        cells = []
        for fmt, label in FORMATS:
            vids = []
            for pal in palettes_for(board, clip):
                f = FINAL / f"{output_name(clip, board)}__{fmt}-{pal}.mp4"
                if f.exists():
                    # ?v=czas zmiany: przeglądarka trzyma wideo w cache'u i po nowym renderze
                    # pokazywała starą wersję (ten sam błąd co cache edytora z ADR e01)
                    vids.append(f'<figure><video src="{f.name}?v={int(f.stat().st_mtime)}" controls preload="metadata" playsinline></video>'
                                f'<figcaption>{pal} · {html.escape(PALETTES[pal]["name"])}</figcaption></figure>')
            if vids:
                cells.append(f'<div class="fmt fmt-{fmt}"><h4>{label}</h4><div class="pair">{"".join(vids)}</div></div>')
        cta = board.get("cta", {})
        rows.append(f'''<section><header><span class="prio prio-{clip["priority"]}">{clip["priority"]} · {clip["scores"]["total"]}</span>
<h2>{html.escape(clip["title"])}</h2><code>{clip["id"]}</code>{f'<span class="brand">test A/B: hasło {html.escape(board["cover"]["text"].replace("*", ""))}</span>' if board.get("variant") else ""}<span class="brand">{board.get("brand", clip["brand"])}</span></header>
<p class="hook">Hook: „{html.escape(board.get("hook", {}).get("text", "").replace("*", ""))}”</p>
<p class="cta">CTA reels: {html.escape(cta.get("reels", {}).get("title", "—").replace("*", ""))} — {html.escape(cta.get("reels", {}).get("sub", ""))}<br>
CTA reklama: {html.escape(cta.get("ad", {}).get("title", "—").replace("*", ""))} → {html.escape(cta.get("ad", {}).get("button", ""))}</p>
{"".join(cells) or '<p class="none">jeszcze bez renderu</p>'}</section>''')
    page = f'''<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Próbki opakowania</title><style>
:root{{--bg:#0A0A08;--fg:#FAF8F0;--mut:#9A938A;--acc:#F5A623;--line:#2E2C28}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}}
main{{max-width:1500px;margin:0 auto;padding:24px 16px 80px}}
h1{{font-size:28px;margin:0 0 4px}} .lead{{color:var(--mut);margin:0 0 28px}}
section{{border-top:1px solid var(--line);padding:24px 0}}
header{{display:flex;flex-wrap:wrap;align-items:center;gap:12px}} h2{{margin:0;font-size:22px}}
code{{color:var(--mut)}} .brand{{border:1px solid var(--line);border-radius:20px;padding:2px 10px;color:var(--mut)}}
.prio{{font-weight:800;border-radius:6px;padding:2px 8px;background:#2E2C28}} .prio-A{{background:var(--acc);color:#000}}
.hook{{font-size:18px;margin:10px 0 4px}} .cta{{color:var(--mut);margin:0 0 14px}}
.fmt{{margin:14px 0}} h4{{margin:0 0 8px;font-size:14px;color:var(--acc);font-weight:600}}
.pair{{display:flex;gap:14px;flex-wrap:wrap}} figure{{margin:0}} figcaption{{color:var(--mut);font-size:13px;margin-top:4px}}
.fmt-reels video,.fmt-ad video{{width:300px;aspect-ratio:9/16;background:#000;border-radius:10px}}
.fmt-youtube video{{width:min(620px,100%);aspect-ratio:16/9;background:#000;border-radius:10px}}
.none{{color:var(--mut)}}
</style></head><body><main><h1>Próbki opakowania klipów</h1>
<p class="lead">Sesja 8.10.2026 · paleta A (bursztyn) · ujęcia oznaczone „AI” są generowane (art. 50 AI Act — przy publikacji włącz też przełącznik na platformie).</p>
{"".join(rows)}</main></body></html>'''
    FINAL.mkdir(parents=True, exist_ok=True)
    (FINAL / "index.html").write_text(page)
    print(f"{len(rows)} klipów → {FINAL / 'index.html'}")


if __name__ == "__main__":
    main()
