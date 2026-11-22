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
BARS_ON = ("ins-outro", "ins-contact", "ins-yt-sub")   # 16.11: Doram kończy się kontaktem (23) zamiast przerywnika zamknięcia
# Mateusz 05.11 wieczór: „plansza z maską powinna być pod koniec mojego gadania, ostatnie 20 sekund —
# to tylko taki baner”. Paski idą więc na ostatnie BARS_LEAD s treści odcinka PRZED zamknięciem
# (i przed gagiem, jeśli jest), a plansze zamknięcia lecą już bez nich.
BARS_LEAD = 20.0
END_GUARD = 0.35
BARS_SLIDE = 0.6
GAGS_DIR = P.PACK / "brand" / "gags"
# Gag = stopklatka z ostatniej klatki przed cięciem + kartka z dziennika i ocena „1” + dzwonek/pieczątka
# (własna grafika i dźwięk — fragment cudzego filmu na kanale firmowym = roszczenie Content ID).
GAGS = {
    "gag-przymiotnik": dict(card="przymiotnik-nograde.png", grade="przymiotnik-onlygrade.png",
                            sfx="przymiotnik-sfx.wav", length=3.4, card_in=0.15, grade_at=1.2),
}
# 22.11 MK: „dalej nie ma jingla” + urwane zdanie zimnego otwarcia. Przed przedstawieniem: stopklatka ostatniej
# klatki i SAM jingle (bez głosu) przez STING_LEN s; ins-intro gra jingle dalej od tej sekundy (storyboard jingle_offset),
# więc brzmi jak jeden ciąg — jingle słychać, a cięcie w pół zdania staje się świadomym przejściem.
# 22.11 MK: „początek może powinien być »w tym odcinku« i kilka mocnych fragmentów” — zamiast jednego ciągłego
# kawałka urwanego w pół zdania: 3–4 zamknięte zdania z całego odcinka (problem → ból → liczba → wynik), potem
# łącznik, jingle, przedstawienie, powrót i odcinek OD POCZĄTKU. Czasy w gotowym renderze youtube-F, granice
# w przerwach między słowami (build/work/final-words/<odcinek>.json).
TEASERS = {
    "ep-doram": [(26.36, 33.20),     # „kontrahent… potrafił tą samą rzecz nazwać na kilkanaście różnych sposobów”
                 (215.68, 219.74),   # „przeklejała, drukowała, przeklejała, drukowała…”
                 (487.96, 495.20),   # „było na poziomie 70%. Po miesiącu osiągnęliśmy 94%.”
                 (567.33, 570.70)],  # „z kilku dni pracy dostajemy 15 minut pracy”
}
TEASER_FADE = 0.05
STING = "jingle-sting"
STING_LEN = 1.6
STING_FILE = P.MUSIC_DIR / "jingle-przedstawienie.mp3"
STING_DB = -3.0
FADE = 0.012
ABBREVIATIONS = {"np.", "tzn.", "itp.", "itd.", "m.in.", "ok.", "tj.", "pt.", "ul.", "nr.", "tzw."}

# odcinek → [(tytuł rozdziału, przed którym wchodzi wstawka | "END"), klip wstawki]
PLAN = {
    # 16.11: wstęp z dogrywek zamiast „Zrobiłem już 8 wdrożeń…”, zakończenie: łącznik → zamknięcie → subskrypcja
    # i ekran końcowy (37+39, prawa połowa wolna) → „do zobaczenia” (24)
    # 17.11 (odsłuch, pkt 5): treść kończy się stanem PRZED („…o ile wszystko dobrze pójdzie”) — domknięcie kwestią 30
    # („To nie jest magia, to porządek plus trochę automatyzacji.”) przed łącznikiem A4
    # 21.11 (MK): odcinek otwiera treść (15–20 s), przedstawienie dopiero potem — wstawki z przedstawieniem po pierwszym
    # akapicie; po dograniu 44–47 podmienić tylko id wstawki, miejsce zostaje
    # 21.11 wieczór: dograne — ins-intro = 44h + 46b + 47 (bez „prowadzę Flowbiz”), powrót do tematu per odcinek
    # (ins-back-*, 47a–d) zamiast ogólnego ins-a2; w ofertach przedstawienie zastępuje ins-hello-offers (13 „tu Mateusz z Flowbiz”)
    "ep-open-mercato-offers": [("word:trudne", STING), ("word:trudne", "ins-intro"), ("word:trudne", "ins-back-offers"), ("END", "ins-g30"), ("END", "ins-a4"), ("END", "ins-outro"),
                               ("END", "ins-yt-sub"), ("END", "ins-bye")],
    # 16.11: łączniki case'ów z dogrywek (6–12) — głos na planszy z nazwą case'u PRZED każdym rozdziałem
    "ep-8-wdrozen": [("word:tworzenie ofert", "ins-a1"), ("word:tworzenie ofert", STING), ("word:tworzenie ofert", "ins-intro"), ("word:tworzenie ofert", "ins-back-8"),
                     ("Zamówienia z Excela: 70% → 94%", "ins-case-6"),
                     ("Kody kreskowe: kilka dni → 15 minut", "ins-case-7"),
                     ("Etykiety: ok. 100 godzin miesięcznie", "ins-case-8"),
                     ("Katalog AI z faktur", "ins-case-9"),
                     ("Panel klienta B2B", "ins-mid-long"), ("Panel klienta B2B", "ins-case-10"),
                     ("Kierownik produkcji w godzinę", "ins-case-11"),
                     ("AI to dokręcanie śrubek", "ins-case-12"),
                     # własne CTA na końcu („zapraszam Cię na flowbiz.pl…”) — bez przerywnika zamknięcia (dubel)
                     ("END", "ins-yt-sub"), ("END", "ins-bye")],
    # 16.11: wstęp i łączniki z dogrywek; zakończenie przed własnym „Dzięki i do usłyszenia” z nagrania
    # 22.11: otwarcie = TEASERS (fragmenty), potem łącznik, jingle, przedstawienie, powrót i odcinek od początku
    "ep-doram": [("START", "ins-a1"), ("START", STING), ("START", "ins-intro"), ("START", "ins-back-doram"),
                 ("Jak uczy się zwykły czat", "ins-mid"), ("Jak uczy się zwykły czat", "ins-a3"),
                 # Doram ma własne zakończenie (subskrypcja + komentarze + „Dzięki i do usłyszenia”) — brakuje w nim tylko
                 # kontaktu, więc przed „więc dziękuję Wam” wchodzi łącznik A4 i kwestia 23, bez dubli subskrypcji
                 ("before:więc dziękuję", "ins-a4"), ("before:więc dziękuję", "ins-contact")],
    "ep-rezon": [("before:Aktualnie", "ins-a1"), ("before:Aktualnie", STING), ("before:Aktualnie", "ins-intro"), ("before:Aktualnie", "ins-back-rezon"),
                 ("Nadprodukcja", "ins-mid"), ("Nadprodukcja", "ins-a3"),
                 ("END", "ins-a4"), ("END", "ins-outro"), ("END", "ins-yt-sub"), ("END", "ins-bye")],
    "ep-marpasz": [("Paczki do 25 kg: cztery worki, cztery etykiety", "ins-intro"), ("Katalog AI: faktura → produkty → opisy", "ins-mid"), ("END", "ins-outro")],
    "ep-vacuactiv": [("ChatGPT zapomina i halucynuje", "ins-intro"), ("Obsidian + Hermes + Codex", "ins-mid"),
                     ("before:No dobra", "gag-przymiotnik"), ("before:No dobra", "ins-outro")],
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
    render = FINAL / f"{clip_id}__youtube-F.mp4"
    # 21.11: transkrypcja leżała w cache po zmianie cięcia (meble bez wstępu) i kotwice trafiały 16 s obok —
    # odświeżamy, gdy render jest nowszy niż transkrypcja
    if not path.exists() or (render.exists() and render.stat().st_mtime > path.stat().st_mtime):
        FINAL_WORDS.mkdir(parents=True, exist_ok=True)
        wav = FINAL_WORDS / f"{clip_id}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(render), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
        subprocess.run(["mlx_whisper", str(wav), "--model", "mlx-community/whisper-large-v3-turbo", "--language", "pl",
                        "--word-timestamps", "True", "--condition-on-previous-text", "False",
                        "--output-dir", str(FINAL_WORDS), "--output-format", "json"], check=True, capture_output=True)
        print(f"   (transkrypcja renderu odświeżona: {path.name})")
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


def bars_graph(source, length, start=0.0):
    """[source:v] (start…start+length) + plik pasków → [bv]. OKNO, nie maska: obraz odcinka zmniejsza się
    do ramki obok paska z logo i nad dolnym paskiem CTA (tło = mięta z pliku pasków), potem wraca na cały
    kadr. Maska nakładana NA obraz ucinała dolne napisy (05.11 wieczór, wszystkie odcinki). Bez przenikania
    dwóch skal — to dawało podwójny obraz; skala zmienia się klatka po klatce."""
    side, bottom = BARS_SIZE
    win_h = 1080 - bottom
    win_w = round(win_h * 16 / 9 / 2) * 2
    x0 = side + (1920 - side - win_w) // 2
    slide_in = f"pow(1-min(1,max(0,t-0.3)/{BARS_SLIDE}),2)"
    slide_out = f"pow(min(1,max(0,(t-{length - BARS_SLIDE - 0.4:.3f})/{BARS_SLIDE})),2)"
    p = f"(1-max({slide_in},{slide_out}))"
    return (f"[B:v]fps=30,scale=1920:1080,setsar=1,tpad=stop_mode=clone:stop_duration={length:.3f},"
            f"trim=0:{length:.3f},setpts=PTS-STARTPTS[bmask];"
            f"[{source}:v]trim={start:.3f}:{start + length:.3f},setpts=PTS-STARTPTS,fps=30,"
            f"scale=w='trunc((1920-{1920 - win_w}*{p})/2)*2':h='trunc((1080-{1080 - win_h}*{p})/2)*2':eval=frame,"
            f"setsar=1[bbase];"
            f"[bmask][bbase]overlay=x='{x0}*{p}':y=0:eval=frame:eof_action=pass,"
            f"format=yuv420p,setsar=1[bv];")

def split_for_bars(segments, words):
    """Ostatnie BARS_LEAD s treści przed zamknięciem (BARS_ON) → osobny kawałek „bars”; szew w przerwie
    między słowami. Gag stojący tuż przed zamknięciem nie przesuwa banera — baner kończy się przed gagiem."""
    for i, seg in enumerate(segments):
        if seg[0] == "insert" and seg[1] in BARS_ON:
            j = i - 1
            while j >= 0 and segments[j][0] == "insert":
                j -= 1
            if j < 0:
                return segments
            _, a, b = segments[j]
            seam = max(a, word_gap_near(words, b - BARS_LEAD)) if b - a > BARS_LEAD + 1 else a
            parts = ([("episode", a, seam)] if seam > a + 0.01 else []) + [("bars", seam, b)]
            return segments[:j] + parts + segments[j + 1:]
    return segments


def gag_graph(n_card, n_grade, n_sfx, t, spec, i):
    """Stopklatka ostatniej klatki przed t (lekko przyciemniona) + kartka wjeżdżająca z góry + ocena."""
    L, cin, gat = spec["length"], spec["card_in"], spec["grade_at"]
    slide = f"if(lt(t,{cin}),-H,if(lt(t,{cin + 0.3}),-H+H*pow((t-{cin})/0.3,0.6),0))"
    return (f"[0:v]trim={max(0.0, t - 0.07):.3f}:{t:.3f},setpts=PTS-STARTPTS,fps=30,scale=1920:1080,setsar=1,"
            f"tpad=stop_mode=clone:stop_duration={L},trim=0:{L},setpts=PTS-STARTPTS,eq=brightness=-0.08[gb{i}];"
            f"[{n_card}:v]format=rgba,setpts=PTS-STARTPTS[gc{i}];"
            f"[{n_grade}:v]format=rgba,fade=t=in:st={gat}:d=0.08:alpha=1,setpts=PTS-STARTPTS[gg{i}];"
            f"[gb{i}][gc{i}]overlay=x=0:y='{slide}':eof_action=repeat[gx{i}];"
            f"[gx{i}][gg{i}]overlay=0:0:eof_action=repeat,trim=0:{L},format=yuv420p,setsar=1[v{i}];"
            f"[{n_sfx}:a]atrim=0:{L},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
            f"apad=whole_dur={L}[a{i}];")


def sting_graph(n_video, t, n_audio, i):
    """Stopklatka ostatniej klatki poprzedniego kawałka (odcinek albo łącznik), lekko przyciemniona, z delikatnym
    najazdem + początek jingla."""
    L = STING_LEN
    return (f"[{n_video}:v]trim={max(0.0, t - 0.07):.3f}:{t:.3f},setpts=PTS-STARTPTS,fps=30,scale=1920:1080,setsar=1,"
            f"tpad=stop_mode=clone:stop_duration={L},trim=0:{L},setpts=PTS-STARTPTS,eq=brightness=-0.06,"
            f"scale=w='1920*(1+0.03*t/{L})':h='1080*(1+0.03*t/{L})':eval=frame,crop=1920:1080,format=yuv420p,setsar=1[v{i}];"
            f"[{n_audio}:a]atrim=0:{L},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
            f"volume={STING_DB}dB,afade=t=in:d=0.03,apad=whole_dur={L}[a{i}];")


def plan_segments(clip_id):
    render = FINAL / f"{clip_id}__youtube-F.mp4"
    content_end = round(duration(LIBRARY / clip_id / "master.mp4"), 3)
    chapters = chapter_times(clip_id)
    rw = render_words(clip_id)
    by_title = {title: t for t, title in chapters}
    cuts = []
    for where, insert in PLAN[clip_id]:
        if where == "START":
            # wstęp z dogrywek (16.11): głos na planszy przed pierwszym słowem odcinka
            cuts.append((0.0, insert))
        elif where == "END":
            # plansza końcowa renderu wchodzi przenikaniem ~0,3 s PRZED końcem treści — cięcie dokładnie
            # w content_end pokazywało mignięcie logo flowbiz przed zamknięciem (Rezon, Marpasz…)
            cut = round(content_end - END_GUARD, 3)
            last_word_end = max((w["end"] for w in rw), default=0.0)
            if last_word_end + 0.05 > cut:
                # 16.11: „…dobrze pójdzie.” urywało się w połowie — klip ma za krótkie wybrzmienie; popraw koniec w EDL
                raise SystemExit(f"{clip_id}: cięcie END {cut:.2f} s ucina ostatnie słowo (kończy się {last_word_end:.2f} s) — "
                                 f"wydłuż koniec klipu w edl.py")
            cuts.append((cut, insert))
        elif where.startswith("before:"):
            # zamknięcie przed własnym pożegnaniem w nagraniu („Dzięki i do usłyszenia”): przerwa przed
            # ostatnim wystąpieniem pierwszego słowa frazy
            first = P.norm(where[7:].split()[0])
            idx = [i for i, w in enumerate(rw) if P.norm(w["word"]) == first]
            if not idx or idx[-1] == 0:
                raise SystemExit(f"{clip_id}: nie ma „{where[7:]}” w renderze")
            i = idx[-1]
            cuts.append((round((rw[i - 1]["end"] + rw[i]["start"]) / 2, 3), insert))
        elif where.startswith("first:"):
            # 21.11: otwarcie z treści — wstawka w przerwie przed PIERWSZYM wystąpieniem słowa (before: bierze ostatnie)
            first = P.norm(where[6:].split()[0])
            idx = [i for i, w in enumerate(rw) if P.norm(w["word"]) == first]
            if not idx or idx[0] == 0:
                raise SystemExit(f"{clip_id}: nie ma „{where[6:]}” w renderze")
            i = idx[0]
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
    # sortowanie STABILNE po czasie: kilka wstawek w jednym miejscu (łącznik → przerywnik → łącznik)
    # idzie w kolejności z PLAN, a nie alfabetycznie po nazwie klipu
    cuts.sort(key=lambda c: c[0])
    pinned = {}   # tytuł rozdziału → cięcie, po którym rozdział faktycznie się zaczyna
    for (where, insert), (t, _) in zip(PLAN[clip_id], sorted(cuts, key=lambda c: [i for w, i in PLAN[clip_id]].index(c[1]))):
        if where in by_title:
            pinned[where] = t
    segments, cursor = [], 0.0
    for t, insert in cuts:
        if t > cursor + 0.01:   # dwie wstawki w jednym miejscu (gag + zamknięcie) — bez pustego kawałka
            segments.append(("episode", cursor, t))
        length = (STING_LEN if insert == STING else GAGS[insert]["length"] if insert in GAGS
                  else duration(FINAL / f"{insert}__youtube-F.mp4"))
        segments.append(("insert", insert, length, t))
        cursor = t
    # 17.11: po wstawkach END wracał ogon treści (0,35 s twarzy z planszą) przed logo — po „Do zobaczenia” mignięcie
    # twarzy. Jak w shortach: plansza końcowa wraca od chwili, gdy jest już w pełni widoczna (content_end + 0,35 s)
    ends_with_end = any(where == "END" for where, _ in PLAN[clip_id])
    segments.append(("episode", round(content_end + 0.35, 3) if ends_with_end else cursor, duration(render)))
    segments = split_for_bars(segments, rw)
    teaser = [("teaser", a, b) for a, b in TEASERS.get(clip_id, [])]
    teaser_len = sum(b - a for _, a, b in teaser)
    segments = teaser + segments
    # rozdziały po przesunięciu: każdy dostaje sumę długości wstawek wklejonych przed nim
    shifted = []
    for t, title in chapters:
        t = pinned.get(title, t)
        # wstawka przesuwa rozdział, gdy fragment odcinka przed nią kończy się najpóźniej w punkcie rozdziału;
        # łącznik case'u (ins-case-*, 16.11) otwiera rozdział — rozdział startuje NA nim, nie po nim
        extra = 0.0
        for seg in segments:
            if seg[0] != "insert" or seg[3] > t + 0.05:
                continue
            if abs(seg[3] - t) <= 0.05 and seg[1].startswith("ins-case"):
                break
            extra += seg[2]
        shifted.append((round(t + extra + teaser_len, 1), title))
    if any(where == "START" for where, _ in PLAN[clip_id]):
        # YouTube wymaga rozdziału od 0:00 — wstęp z dogrywek dostaje własny
        shifted.insert(0, (round(teaser_len, 1), "Wstęp") if teaser else (0.0, "Wstęp"))
    if teaser:
        shifted.insert(0, (0.0, "W tym odcinku"))
    return render, segments, shifted


INSERT_LABELS = {"ins-intro": "przedstawienie", "ins-back-offers": "powrót do tematu", "ins-back-doram": "powrót do tematu",
                 "ins-back-rezon": "powrót do tematu", "ins-back-8": "powrót do tematu", "ins-a1": "łącznik przed przedstawieniem", "ins-a2": "powrót do tematu",
                 "ins-yt-sub": "plansza Subskrybuj", "ins-hello-offers": "wstęp", "ins-mid": "wstawka w środku",
                 "ins-mid-long": "wstawka w środku", "ins-outro": "zakończenie", STING: "jingle (stopklatka)"}


def insert_marks(segments):
    """21.11 (MK: „daj mi rozdziały, żebym mógł sprawdzać wstawki”) — gdzie w gotowym odcinku stoi każda wstawka."""
    marks, out = [], 0.0
    for seg in segments:
        if seg[0] == "teaser" and out == 0.0:
            marks.append({"t": 0.0, "id": "teaser", "label": "w tym odcinku (fragmenty)", "length": round(
                sum(x[2] - x[1] for x in segments if x[0] == "teaser"), 1)})
        if seg[0] == "insert":
            label = INSERT_LABELS.get(seg[1], "łącznik case'u" if seg[1].startswith("ins-case") else
                                      "gag" if seg[1] in GAGS else seg[1])
            marks.append({"t": round(out, 1), "id": seg[1], "label": label, "length": round(seg[2], 1)})
            out += seg[2]
        else:
            out += seg[2] - seg[1]
    return marks


def build(clip_id, dry=False):
    render, segments, chapters = plan_segments(clip_id)
    for seg in segments:
        print(f"   {seg[0]:8} {seg[1] if seg[0] == 'insert' else f'{seg[1]:8.2f}'} → {seg[2]:8.2f}")
    if dry:
        return chapters, insert_marks(segments)
    inputs, graph, labels = ["-i", str(render)], "", []
    insert_inputs = {}
    for seg in segments:
        if seg[0] == "insert" and seg[1] not in insert_inputs and seg[1] not in GAGS and seg[1] != STING:
            insert_inputs[seg[1]] = len(insert_inputs) + 1
            inputs += ["-i", str(FINAL / f"{seg[1]}__youtube-F.mp4")]
    bars_input = len(insert_inputs) + 1
    if any(seg[0] == "bars" for seg in segments):
        inputs += ["-i", str(BARS_SOURCE)]
    gag_inputs = {}
    for seg in segments:
        if seg[0] == "insert" and seg[1] in GAGS and seg[1] not in gag_inputs:
            spec, first = GAGS[seg[1]], inputs.count("-i")
            gag_inputs[seg[1]] = (first, first + 1, first + 2)
            inputs += ["-loop", "1", "-t", str(spec["length"]), "-i", str(GAGS_DIR / spec["card"]),
                       "-loop", "1", "-t", str(spec["length"]), "-i", str(GAGS_DIR / spec["grade"]),
                       "-i", str(GAGS_DIR / spec["sfx"])]
    sting_input = None
    if any(seg[0] == "insert" and seg[1] == STING for seg in segments):
        sting_input = inputs.count("-i")
        inputs += ["-i", str(STING_FILE)]
    for i, seg in enumerate(segments):
        if seg[0] == "insert" and seg[1] == STING:
            prev = segments[i - 1]
            if prev[0] == "insert" and prev[1] in insert_inputs:
                n_video, t_end = insert_inputs[prev[1]], prev[2] - 0.5   # łącznik gaśnie pod koniec — klatka sprzed wygaszenia
            else:
                n_video, t_end = 0, seg[3]
            graph += sting_graph(n_video, t_end, sting_input, i)
            labels.append(f"[v{i}][a{i}]")
            continue
        if seg[0] == "bars":
            a, b = seg[1], seg[2]
            graph += (bars_graph(0, b - a, a).replace("[B:", f"[{bars_input}:")
                      .replace("[bv]", f"[v{i}]").replace("[bmask]", f"[bmask{i}]").replace("[bbase]", f"[bbase{i}]"))
            graph += (f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
                      f"afade=t=in:d={FADE},afade=t=out:st={max(0.0, b - a - FADE):.3f}:d={FADE}[a{i}];")
            labels.append(f"[v{i}][a{i}]")
            continue
        if seg[0] == "insert" and seg[1] in GAGS:
            graph += gag_graph(*gag_inputs[seg[1]], seg[3], GAGS[seg[1]], i)
            labels.append(f"[v{i}][a{i}]")
            continue
        fade = TEASER_FADE if seg[0] == "teaser" else FADE
        if seg[0] in ("episode", "teaser"):
            n, a, b = 0, seg[1], seg[2]
        else:
            n, a, b = insert_inputs[seg[1]], 0.0, seg[2]
        length = b - a
        graph += (f"[{n}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30,scale=1920:1080,setsar=1[v{i}];"
                  f"[{n}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
                  f"afade=t=in:d={fade},afade=t=out:st={max(0.0, length - fade):.3f}:d={fade}[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    graph += "".join(labels) + f"concat=n={len(segments)}:v=1:a=1[v][a]"
    out = FINAL / f"{clip_id}__youtube-F--with-inserts.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
    print(f"   → {out.name}  {duration(out):.1f} s")
    return chapters, insert_marks(segments)


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
        chapters, marks = build(clip_id, dry)
        text = "\n".join(f"{int(t // 60)}:{int(t % 60):02d} {title}" for t, title in chapters)
        print(text)
        if not dry:
            report[clip_id] = {"plan": PLAN[clip_id], "chapters": text,
                               "chapter_list": [{"t": t, "title": title} for t, title in chapters], "inserts": marks}
    if not dry:
        json.dump(report, open(report_file, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
    from package import auto_export
    auto_export()
