#!/usr/bin/env python3
"""Odcinek YouTube ze wstawkami o usługach: gotowy render + przerywniki → jeden plik.

Przerywniki (ins-intro, ins-mid, ins-mid-long, ins-outro) są nagrane raz i opakowane osobno
(packaging/storyboards/ins-*.json). Tu wklejamy je do gotowych renderów youtube-F:

- przedstawienie się i zaproszenie wchodzą PRZED wskazanym rozdziałem, w przerwie po najbliższym
  końcu zdania — granice słów z transkrypcji gotowego renderu (build/work/final-words/),
- zamknięcie wchodzi po treści odcinka, przed planszą końcową (2,5 s z package.py).

Plan miejsc: vault marketing/content/youtube/_wstawki-uslugi-plan.md. Wynik:
final/samples/<odcinek>__youtube-F--with-inserts.mp4 + data/assembly.json (segmenty i rozdziały
po przesunięciu — do opisu odcinka w Studiu).

  python3 tools/assemble_episode.py                 # wszystkie odcinki z PLAN
  python3 tools/assemble_episode.py ep-doram        # jeden
  python3 tools/assemble_episode.py --dry ep-doram  # tylko punkty cięcia i rozdziały
"""
import json
import subprocess
import sys
from pathlib import Path

import package as P
from sources import BUILD, DATA, LIBRARY, load_clips

FINAL_WORDS = BUILD / "work" / "final-words"   # transkrypcja GOTOWEGO renderu (mlx, czasy słów)

FINAL = P.FINAL
ENDCARD = 2.5

# Jingiel otwarcia (Mateusz 05.11: „na początku jako wstawka Miniaturki Youtube.mp4 z maską — został
# tylko dolny i boczny pasek; sensowne wejście i przejście, tzw. jingiel, że zaczyna się odcinek”).
# 1,2 s sama plansza z paskami + wejście muzyki → plansza się rozpuszcza, odcinek na pełnym ekranie
# pod maską z paskiem bocznym i dolnym → po ~6,5 s paski zjeżdżają z kadru. Muzyka: ten sam utwór i pozycja
# co podkład odcinka (package.MUSIC_*), więc wejście przechodzi w niego bez szwu.
JINGLE = Path.home() / "Youtube Projects" / "Miniaturki Youtube.mp4"
JINGLE_LEAD = 1.2        # sama plansza, zanim pojawi się obraz odcinka
JINGLE_BARS = (150, 130)    # szerokość paska z logo, wysokość dolnego paska z CTA (px przy 1920×1080)
JINGLE_EXPAND = 6.5      # od tej sekundy (osi wyjścia) paski zjeżdżają z kadru
JINGLE_FADE = 0.6
JINGLE_SPLIT = 8.0       # ile sekund odcinka idzie przez kompozycję jingla (cięcie w przerwie między słowami)          # plansza końcowa youtube (package.py, end_len)
FADE = 0.012
ABBREVIATIONS = {"np.", "tzn.", "itp.", "itd.", "m.in.", "ok.", "tj.", "pt.", "ul.", "nr.", "tzw."}

# odcinek → [(tytuł rozdziału, przed którym wchodzi wstawka | "END"), klip wstawki]
PLAN = {
    "ep-open-mercato-offers": [("END", "ins-outro")],
    "ep-8-wdrozen": [("word:tworzenie ofert", "ins-intro"), ("Panel klienta B2B", "ins-mid-long"), ("END", "ins-outro")],
    "ep-doram": [("Zamówienia w Excelu od kontrahentów z Niemiec", "ins-intro"), ("Jak uczy się zwykły czat", "ins-mid"), ("before:Dzięki i do usłyszenia", "ins-outro")],
    "ep-rezon": [("Kontrola po fakcie", "ins-intro"), ("Nadprodukcja", "ins-mid"), ("END", "ins-outro")],
    "ep-marpasz": [("Paczki do 25 kg: cztery worki, cztery etykiety", "ins-intro"), ("Katalog AI: faktura → produkty → opisy", "ins-mid"), ("END", "ins-outro")],
    "ep-vacuactiv": [("ChatGPT zapomina i halucynuje", "ins-intro"), ("Obsidian + Hermes + Codex", "ins-mid"), ("before:No dobra", "ins-outro")],
    "ep-module": [("Ludzie zaczynają od drugiej strony", "ins-intro"), ("Słownik pojęć", "ins-mid-long"), ("END", "ins-outro")],
}


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def render_words(clip_id):
    """Słowa z transkrypcji gotowego renderu. Czasy z transkrypcji surówki bywają przesunięte
    o 0,5–1,5 s, przez co cięcie trafiało w „katalog… | wstawka | AI.” — tu liczy się render."""
    path = FINAL_WORDS / f"{clip_id}.json"
    if not path.exists():
        raise SystemExit(f"brak {path} — przetranskrybuj render (mlx_whisper --word-timestamps True)")
    return [w for seg in json.load(open(path))["segments"] for w in seg.get("words", [])]


def cut_after_sentence(words, t, back=12.0, ahead=8.0):
    """Cięcie w przerwie po najbliższym końcu zdania wokół t: środek luki między słowem z . ? !
    a następnym słowem (granice słów z renderu, nie z surówki)."""
    best = None
    for i, w in enumerate(words[:-1]):
        # „np.” to nie koniec zdania (Vacu Activ: „wybranie np. | wstawka | do tego wszystkiego”)
        if w["word"].strip().lower() in ABBREVIATIONS:
            continue
        if w["word"].strip()[-1:] in ".?!" and t - back <= w["end"] <= t + ahead:
            gap = (w["end"], words[i + 1]["start"])
            if best is None or abs(gap[0] - t) < abs(best[0] - t):
                best = gap
    if best is None:
        return t
    return round((best[0] + best[1]) / 2 if best[1] - best[0] < 1.2 else best[0] + 0.35, 3)


def chapter_times(clip_id):
    board = json.load(open(P.PACK / "storyboards" / f"{clip_id}.json"))
    words = json.load(open(LIBRARY / clip_id / "words.json"))
    clock = P.Clock(words, json.load(open(DATA / "caption-fixes.json")), 1.0)
    times = []
    for anchor, title in board.get("chapters", []):
        t = clock.at(anchor, floor=times[-1][0] if times else 0.0)
        times.append((t, title))
    if times:
        times[0] = (0.0, times[0][1])
    return times


def word_gap_near(words, t):
    """środek najbliższej przerwy między słowami (≥ 80 ms) — tam szew jingla nie przetnie głoski"""
    gaps = [((a["end"] + b["start"]) / 2, b["start"] - a["end"]) for a, b in zip(words, words[1:])]
    return round(min((g for g in gaps if g[1] >= 0.08), key=lambda g: abs(g[0] - t))[0], 3)


def jingle_graph(split):
    """[0:v][0:a] odcinka (0…split) + plik jingla → [jv][ja] o długości split + JINGLE_LEAD.

    Maska, nie okno: odcinek leci na pełnym ekranie, a z pliku jingla zostaje tylko pasek boczny
    (logo) i dolny (CTA) — miętowy kształt L nałożony na obraz. Przenikanie pomniejszonego okna
    w pełną klatkę dawało podwójny obraz (05.11), więc na wyjściu paski po prostu zjeżdżają z kadru."""
    lead, total = JINGLE_LEAD, split + JINGLE_LEAD
    side, bottom = JINGLE_BARS
    out_at, slide = JINGLE_EXPAND, JINGLE_FADE
    music = P.MUSIC_DIR / P.MUSIC_DEFAULT
    pos = P.MUSIC_OFFSET.get(P.MUSIC_DEFAULT, 0.0) - lead          # ta sama pozycja utworu co podkład odcinka
    ease = f"pow(min(1,max(0,(t-{out_at})/{slide})),2)"
    graph = (
        f"[J:v]fps=30,scale=1920:1080,setsar=1,tpad=stop_mode=clone:stop_duration={total},"
        f"trim=0:{total:.3f},setpts=PTS-STARTPTS,split[jfull][jbar];"
        # cała plansza jingla przez JINGLE_LEAD, potem rozpuszcza się i odsłania odcinek
        f"[jfull]trim=0:{lead + 0.5:.3f},format=yuva420p,fade=t=out:st={lead:.3f}:d=0.45:alpha=1,setpts=PTS-STARTPTS[jcover];"
        # maska: zostaje tylko pasek boczny i dolny
        f"[jbar]trim=0:{out_at + slide + 0.1:.3f},format=yuva420p,"
        f"geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='if(lt(X,{side})+gt(Y,{1080 - bottom}),255,0)',setpts=PTS-STARTPTS[jL];"
        f"[0:v]trim=0:{split},setpts=PTS-STARTPTS,fps=30,scale=1920:1080,setsar=1,"
        f"tpad=start_mode=clone:start_duration={lead}[jbase];"
        f"[jbase][jcover]overlay=0:0:eof_action=pass[j1];"
        f"[j1][jL]overlay=x='-{side + 40}*{ease}':y='{bottom + 40}*{ease}':eof_action=pass,format=yuv420p,setsar=1[jv];"
        f"[0:a]atrim=0:{split},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
        f"adelay={int(lead * 1000)}:all=1,apad=whole_dur={total}[jvoice];"
        f"[M:a]atrim={pos:.3f}:{pos + lead + 0.8:.3f},asetpts=PTS-STARTPTS,aresample=48000,"
        f"aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-25:TP=-3:LRA=7,volume=-4dB,"
        f"afade=t=in:d=0.15,afade=t=out:st={lead:.3f}:d=0.8,apad=whole_dur={total}[jmus];"
        f"[jvoice][jmus]amix=inputs=2:normalize=0:duration=first,atrim=0:{total:.3f}[ja];")
    return graph, music


def plan_segments(clip_id):
    render = FINAL / f"{clip_id}__youtube-F.mp4"
    content_end = round(duration(LIBRARY / clip_id / "master.mp4"), 3)
    chapters = chapter_times(clip_id)
    rw = render_words(clip_id)
    by_title = {title: t for t, title in chapters}
    cuts = []
    for where, insert in PLAN[clip_id]:
        if where == "END":
            cuts.append((content_end, insert))
        elif where.startswith("before:"):
            # zamknięcie przed własnym pożegnaniem w nagraniu („Dzięki i do usłyszenia”): przerwa przed
            # ostatnim wystąpieniem pierwszego słowa frazy
            first = P.norm(where[7:].split()[0])
            idx = [i for i, w in enumerate(rw) if P.norm(w["word"]) == first]
            if not idx or idx[-1] == 0:
                raise SystemExit(f"{clip_id}: nie ma „{where[7:]}” w renderze")
            i = idx[-1]
            cuts.append((round((rw[i - 1]["end"] + rw[i]["start"]) / 2, 3), insert))
        elif where.startswith("word:"):
            # wstawka przed konkretnym zdaniem (gdy granica nie jest rozdziałem składanki)
            words = json.load(open(LIBRARY / clip_id / "words.json"))
            clock = P.Clock(words, json.load(open(DATA / "caption-fixes.json")), 1.0)
            cuts.append((cut_after_sentence(rw, clock.at(where[5:])), insert))
        else:
            if where not in by_title:
                raise SystemExit(f"{clip_id}: nie ma rozdziału „{where}” w storyboardzie")
            cuts.append((cut_after_sentence(rw, by_title[where]), insert))
    cuts.sort()
    pinned = {}   # tytuł rozdziału → cięcie, po którym rozdział faktycznie się zaczyna
    for (where, insert), (t, _) in zip(PLAN[clip_id], sorted(cuts, key=lambda c: [i for w, i in PLAN[clip_id]].index(c[1]))):
        if where in by_title:
            pinned[where] = t
    segments, cursor = [], 0.0
    for t, insert in cuts:
        segments.append(("episode", cursor, t))
        segments.append(("insert", insert, duration(FINAL / f"{insert}__youtube-F.mp4")))
        cursor = t
    segments.append(("episode", cursor, duration(render)))
    # jingiel: pierwsze JINGLE_SPLIT s odcinka idzie przez kompozycję z paskami
    split = word_gap_near(rw, JINGLE_SPLIT)
    if segments[0][0] == "episode" and segments[0][2] > split + 1:
        segments[0:1] = [("jingle", 0.0, split), ("episode", split, segments[0][2])]
    # rozdziały po przesunięciu: każdy dostaje sumę długości wstawek wklejonych przed nim
    shifted = []
    for t, title in chapters:
        t = pinned.get(title, t)
        # wstawka przesuwa rozdział, gdy fragment odcinka przed nią kończy się najpóźniej w punkcie rozdziału
        extra = sum(seg[2] for i, seg in enumerate(segments) if seg[0] == "insert" and segments[i - 1][2] <= t + 0.05)
        if t > 0 and segments[0][0] == "jingle":
            extra += JINGLE_LEAD
        shifted.append((round(t + extra, 1), title))
    return render, segments, shifted


def build(clip_id, dry=False):
    render, segments, chapters = plan_segments(clip_id)
    for seg in segments:
        print(f"   {seg[0]:8} {seg[1] if seg[0] == 'insert' else f'{seg[1]:8.2f}'} → {seg[2]:8.2f}")
    has_jingle = segments[0][0] == "jingle"
    if dry:
        return chapters
    inputs, graph, labels = ["-i", str(render)], "", []
    insert_inputs = {}
    for seg in segments:
        if seg[0] == "insert" and seg[1] not in insert_inputs:
            insert_inputs[seg[1]] = len(insert_inputs) + 1
            inputs += ["-i", str(FINAL / f"{seg[1]}__youtube-F.mp4")]
    if has_jingle:
        j_index, m_index = len(insert_inputs) + 1, len(insert_inputs) + 2
        jgraph, music = jingle_graph(segments[0][2])
        graph += jgraph.replace("[J:", f"[{j_index}:").replace("[M:", f"[{m_index}:")
        inputs += ["-i", str(JINGLE), "-i", str(music)]
        labels.append("[jv][ja]")
    for i, seg in enumerate(segments):
        if seg[0] == "jingle":
            continue
        if seg[0] == "episode":
            n, a, b = 0, seg[1], seg[2]
        else:
            n, a, b = insert_inputs[seg[1]], 0.0, seg[2]
        length = b - a
        graph += (f"[{n}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30,scale=1920:1080,setsar=1[v{i}];"
                  f"[{n}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
                  f"afade=t=in:d={FADE},afade=t=out:st={max(0.0, length - FADE):.3f}:d={FADE}[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    graph += "".join(labels) + f"concat=n={len(segments)}:v=1:a=1[v][a]"
    out = FINAL / f"{clip_id}__youtube-F--with-inserts.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
    print(f"   → {out.name}  {duration(out):.1f} s")
    return chapters


def main(argv):
    dry = "--dry" in argv
    wanted = [a for a in argv if not a.startswith("--")] or list(PLAN)
    known = {c["id"] for c in load_clips()}
    report_file = DATA / "assembly.json"
    report = json.load(open(report_file)) if report_file.exists() else {}
    for clip_id in wanted:
        if clip_id not in known:
            raise SystemExit(f"nie ma klipu {clip_id}")
        print(f"== {clip_id}")
        chapters = build(clip_id, dry)
        text = "\n".join(f"{int(t // 60)}:{int(t % 60):02d} {title}" for t, title in chapters)
        print(text)
        if not dry:
            report[clip_id] = {"plan": PLAN[clip_id], "chapters": text}
    if not dry:
        json.dump(report, open(report_file, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
