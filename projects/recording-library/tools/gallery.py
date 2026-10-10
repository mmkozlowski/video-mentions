#!/usr/bin/env python3
"""Galeria próbek do przeglądu: final/samples/index.html (otwórz w przeglądarce).

Każdy klip w jednym rzędzie: format × paleta A/B obok siebie — paletę wybiera się
na żywym materiale, nie na opisie.

  python3 tools/gallery.py && open final/samples/index.html
"""
import html
import json

NOTES = r'''<div id="notesbar" style="position:fixed;right:16px;bottom:16px;z-index:9;display:flex;gap:8px;align-items:center;background:#1A1916;border:1px solid #2E2C28;border-radius:12px;padding:10px 12px">
<span id="ncount" style="color:#9A938A;font-size:13px">0 uwag</span>
<button id="ncopy" style="font:600 13px system-ui;padding:8px 12px;border-radius:8px;border:0;background:#F5A623;color:#000;cursor:pointer">Kopiuj uwagi</button>
<button id="nclear" style="font:600 13px system-ui;padding:8px 12px;border-radius:8px;border:1px solid #2E2C28;background:none;color:#FAF8F0;cursor:pointer">Wyczyść</button></div>
<script>
const KEY="uwagi-montaz";
const load=()=>{try{return JSON.parse(localStorage.getItem(KEY)||"[]")}catch{return[]}};
const save=n=>{try{localStorage.setItem(KEY,JSON.stringify(n))}catch{}; draw()};
const fmt=t=>Math.floor(t/60)+":"+String(Math.floor(t%60)).padStart(2,"0");
function draw(){const n=load();document.getElementById("ncount").textContent=n.length+" uwag";
 document.querySelectorAll(".nlist").forEach(ul=>{const f=ul.dataset.file;ul.innerHTML="";
  n.map((x,i)=>[x,i]).filter(([x])=>x.file===f).forEach(([x,i])=>{const li=document.createElement("li");
   li.textContent=fmt(x.t)+" — "+x.text+" ";const b=document.createElement("button");b.textContent="×";b.style.cssText="background:none;border:0;color:#9A938A;cursor:pointer";
   b.onclick=()=>{const m=load();m.splice(i,1);save(m)};li.append(b);ul.append(li);});});}
document.querySelectorAll("figure").forEach(fig=>{const v=fig.querySelector("video");if(!v)return;const file=v.getAttribute("src").split("?")[0];
 const row=document.createElement("div");row.style.cssText="display:flex;gap:6px;margin-top:6px";
 const inp=document.createElement("input");inp.placeholder="co zmienić?";inp.style.cssText="flex:1;min-width:0;font:13px system-ui;padding:6px 8px;border-radius:6px;border:1px solid #2E2C28;background:#0A0A08;color:#FAF8F0";
 const btn=document.createElement("button");btn.textContent="Uwaga tutaj";btn.style.cssText="font:600 12px system-ui;padding:6px 10px;border-radius:6px;border:0;background:#F5A623;color:#000;cursor:pointer;white-space:nowrap";
 const add=()=>{if(!inp.value.trim())return inp.focus();const n=load();n.push({file,t:v.currentTime,text:inp.value.trim()});inp.value="";save(n)};
 btn.onclick=add;inp.onkeydown=e=>{if(e.key==="Enter")add()};
 const ul=document.createElement("ul");ul.className="nlist";ul.dataset.file=file;ul.style.cssText="margin:6px 0 0;padding-left:18px;color:#FAF8F0;font-size:13px;max-width:620px";
 row.append(inp,btn);fig.append(row,ul);});
document.getElementById("ncopy").onclick=async()=>{const n=load();const txt=n.map(x=>x.file.replace(".mp4","")+" "+fmt(x.t)+" — "+x.text).join("\n");
 try{await navigator.clipboard.writeText(txt);document.getElementById("ncount").textContent="skopiowano"}catch{prompt("Skopiuj:",txt)}};
document.getElementById("nclear").onclick=()=>{if(confirm("Usunąć wszystkie uwagi?"))save([])};
draw();
</script>'''

from package import FINAL, PACK, PALETTES, output_name, palettes_for
from sources import load_clips, DATA

FORMATS = [("reels", "Reels / TikTok 9:16 — organiczne, CTA w komentarzu"),
           ("ad", "Reklama Meta 9:16 — chip CTA + plansza końcowa"),
           ("youtube", "YouTube 16:9 — panel boczny, bez napisów")]


def main():
    clips = {c["id"]: c for c in load_clips()}
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
<p class="lead"><a href="odcinki-i-grafiki.html" style="color:#F5A623">→ odcinki YouTube i grafiki statyczne</a><br>Sesja 8.10.2026 · paleta A (bursztyn) · ujęcia oznaczone „AI” są generowane (art. 50 AI Act — przy publikacji włącz też przełącznik na platformie).</p>
{"".join(rows)}</main>'''+NOTES+'''</body></html>'''
    FINAL.mkdir(parents=True, exist_ok=True)
    (FINAL / "index.html").write_text(page)
    print(f"{len(rows)} klipów → {FINAL / 'index.html'}")
    print("odcinki i grafiki →", episodes_and_static(clips))


def episodes_and_static(clips):
    """Druga strona: długie odcinki YouTube (z rozdziałami) + wszystkie grafiki statyczne."""
    eps = []
    for path in sorted(PACK.glob("storyboards/ep-*.json")):
        clip = clips[json.load(open(path))["clip"]]
        f = FINAL / f"{clip['id']}__youtube-A.mp4"
        if not f.exists():
            continue
        chapters = FINAL / f"{clip['id']}__chapters.txt"
        chap = html.escape(chapters.read_text()) if chapters.exists() else ""
        eps.append(f'<section><h2>{html.escape(clip["title"])}</h2><code>{clip["id"]} · {int(clip["duration"] // 60)}:{int(clip["duration"] % 60):02d}</code>'
                   f'<div class="ep"><figure style="margin:0;width:min(900px,100%)"><video src="{f.name}?v={int(f.stat().st_mtime)}" controls preload="metadata" style="width:100%"></video></figure>'
                   f'<pre>{chap}</pre></div></section>')
    static = FINAL.parent / "static"
    shots = []
    for feed in sorted(static.glob("*__feed.png")):
        slug = feed.name.split("__")[0]
        story = static / f"{slug}__story.png"
        shots.append(f'<figure><a href="../static/{feed.name}"><img src="../static/{feed.name}?v={int(feed.stat().st_mtime)}" class="feed"></a>'
                     + (f'<a href="../static/{story.name}"><img src="../static/{story.name}?v={int(story.stat().st_mtime)}" class="story"></a>' if story.exists() else "")
                     + f'<figcaption>{html.escape(slug)}</figcaption></figure>')
    page = f'''<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Odcinki i grafiki</title><style>
:root{{--bg:#0A0A08;--fg:#FAF8F0;--mut:#9A938A;--acc:#F5A623;--line:#2E2C28}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}}
main{{max-width:1500px;margin:0 auto;padding:24px 16px 80px}} h1{{font-size:28px;margin:0 0 4px}} .lead{{color:var(--mut)}}
section{{border-top:1px solid var(--line);padding:24px 0}} h2{{margin:0 0 4px;font-size:22px}} code{{color:var(--mut)}}
.ep{{display:flex;gap:20px;flex-wrap:wrap;margin-top:12px}} .ep video{{width:min(900px,100%);aspect-ratio:16/9;background:#000;border-radius:10px}}
pre{{margin:0;color:var(--mut);font-size:14px;white-space:pre-wrap}}
.grid{{display:flex;flex-wrap:wrap;gap:24px}} figure{{margin:0;display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap}}
img.feed{{width:280px;border-radius:8px}} img.story{{width:180px;border-radius:8px}} figcaption{{width:100%;color:var(--mut);font-size:13px}}
nav a{{color:var(--acc)}}
</style></head><body><main><h1>Odcinki YouTube i grafiki statyczne</h1>
<p class="lead"><nav><a href="index.html">← krótkie klipy i reklamy wideo</a></nav></p>
<h2 style="margin-top:28px">Odcinki YouTube 16:9</h2>{"".join(eps) or "<p>jeszcze bez renderu</p>"}
<section><h2>Grafiki statyczne — feed 4:5 i story 9:16</h2><div class="grid">{"".join(shots)}</div></section>
</main>'''+NOTES+'''</body></html>'''
    out = FINAL / "odcinki-i-grafiki.html"
    out.write_text(page)
    return out


if __name__ == "__main__":
    main()
