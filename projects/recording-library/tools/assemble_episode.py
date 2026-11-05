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
ENDCARD = 2.5          # plansza końcowa youtube (package.py, end_len)

# Paski z „Miniaturki Youtube.mp4” jako maska L (pasek z logo z boku, dolny z CTA „Umów się na
# bezpłatną konsultację”). Mateusz 05.11: najpierw „na początku, tzw. jingiel”, po obejrzeniu: „nie może
# być od pierwszej sekundy — ewentualnie przy końcu”. Więc: na planszach zamknięcia (ins-outro, sam głos
# „Jeśli chcesz, żebym przeszedł z Tobą przez Twój proces…”) — paski wjeżdżają z brzegów, animacja pliku
# leci, przed końcem zjeżdżają. Na ostatnim ujęciu odcinka zasłaniały dolne napisy („Pokażę, jak…”).
BARS_SOURCE = Path.home() / "Youtube Projects" / "Miniaturki Youtube.mp4"
BARS_SIZE = (150, 130)    # szerokość paska z logo, wysokość dolnego paska z CTA (px przy 1920×1080)
BARS_ON = "ins-outro"
BARS_SLIDE = 0.6
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
    """środek najbliższej przerwy między słowami (≥ 80 ms) — tam szew pasków nie przetnie głoski"""
    gaps = [((a["end"] + b["start"]) / 2, b["start"] - a["end"]) for a, b in zip(words, words[1:])]
    return round(min((g for g in gaps if g[1] >= 0.08), key=lambda g: abs(g[0] - t))[0], 3)


def bars_graph(source, length):
    """[source:v] (0…length) + plik pasków → [bv]. Maska, nie okno: obraz odcinka bez zmian,
    na nim tylko pasek boczny i dolny. (Pomniejszone okno + przenikanie dawało podwójny obraz.)"""
    side, bottom = BARS_SIZE
    slide_in = f"pow(1-min(1,max(0,t-0.3)/{BARS_SLIDE}),2)"
    slide_out = f"pow(min(1,max(0,(t-{length - BARS_SLIDE - 0.4:.3f})/{BARS_SLIDE})),2)"
    away = f"max({slide_in},{slide_out})"
    return (f"[B:v]fps=30,scale=1920:1080,setsar=1,tpad=stop_mode=clone:stop_duration={length:.3f},"
            f"trim=0:{length:.3f},setpts=PTS-STARTPTS,format=yuva420p,"
            f"geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='if(lt(X,{side})+gt(Y,{1080 - bottom}),255,0)'[bmask];"
            f"[{source}:v]trim=0:{length:.3f},setpts=PTS-STARTPTS,fps=30,scale=1920:1080,setsar=1[bbase];"
            f"[bbase][bmask]overlay=x='-{side + 40}*{away}':y='{bottom + 40}*{away}':eof_action=pass,"
            f"format=yuv420p,setsar=1[bv];")


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
    # rozdziały po przesunięciu: każdy dostaje sumę długości wstawek wklejonych przed nim
    shifted = []
    for t, title in chapters:
        t = pinned.get(title, t)
        # wstawka przesuwa rozdział, gdy fragment odcinka przed nią kończy się najpóźniej w punkcie rozdziału
        extra = sum(seg[2] for i, seg in enumerate(segments) if seg[0] == "insert" and segments[i - 1][2] <= t + 0.05)
        shifted.append((round(t + extra, 1), title))
    return render, segments, shifted


def build(clip_id, dry=False):
    render, segments, chapters = plan_segments(clip_id)
    for seg in segments:
        print(f"   {seg[0]:8} {seg[1] if seg[0] == 'insert' else f'{seg[1]:8.2f}'} → {seg[2]:8.2f}")
    if dry:
        return chapters
    inputs, graph, labels = ["-i", str(render)], "", []
    insert_inputs = {}
    for seg in segments:
        if seg[0] == "insert" and seg[1] not in insert_inputs:
            insert_inputs[seg[1]] = len(insert_inputs) + 1
            inputs += ["-i", str(FINAL / f"{seg[1]}__youtube-F.mp4")]
    bars_input = len(insert_inputs) + 1
    if BARS_ON in insert_inputs:
        inputs += ["-i", str(BARS_SOURCE)]
    for i, seg in enumerate(segments):
        if seg[0] == "insert" and seg[1] == BARS_ON:
            graph += (bars_graph(insert_inputs[seg[1]], seg[2]).replace("[B:", f"[{bars_input}:")
                      .replace("[bv]", f"[v{i}]").replace("[bmask]", f"[bmask{i}]").replace("[bbase]", f"[bbase{i}]"))
            graph += (f"[{insert_inputs[seg[1]]}:a]atrim=0:{seg[2]},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
                      f"afade=t=in:d={FADE},afade=t=out:st={max(0.0, seg[2] - FADE):.3f}:d={FADE}[a{i}];")
            labels.append(f"[v{i}][a{i}]")
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
