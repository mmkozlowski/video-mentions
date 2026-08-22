#!/usr/bin/env python3
"""
Zgrubny montaz: nagranie + wstawki na zmierzonych czasach, jednym poleceniem.

    python3 tools-sklej.py <nagranie.mov> <plan.tsv> <wynik.mp4> [--od SEK] [--do SEK]

Plan (TSV, trzy kolumny):
    czas    plik                                    tryb
    13:20.4 assets/broll-gemini/02-chaos.mp4        przebitka
    00:34.9 final/e01/e01-03-dostep-v6-...mov       nakladka

  nakladka  — wstawka z alfa wchodzi NA gadana glowe (obraz spod spodu zostaje)
  przebitka — klip zastepuje obraz na czas swojego trwania (dzwiek zostaje z nagrania)

PO CO TO JEST: nie zastepuje montazu, tylko usuwa jego najnudniejsza czesc.
Dostajesz plik, w ktorym wszystko juz stoi na swoim miejscu — ogladasz go raz
i wiesz, ktore rozstawienie nie gra, ZANIM zaczniesz klikac w edytorze.
Poprawki nanosisz w planie i skladasz ponownie; to sekundy, nie przeciaganie klipow.

PULAPKA: przebitka zabiera obraz, ale NIE dzwiek — mowisz dalej. Jesli klip
jest dluzszy niz fraza, przykryje pointe. Skrypt przycina przebitki do podanej
dlugosci (czwarta kolumna, opcjonalna, w sekundach).
"""
import sys, os, subprocess, json

def sek(t):
    t = t.strip().replace(",", ".")
    if ":" in t:
        m, s = t.split(":"); return int(m) * 60 + float(s)
    return float(t)

def dlugosc(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", p], capture_output=True, text=True)
    return float(r.stdout.strip())

def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(1)
    baza, plan_p, wynik = sys.argv[1], sys.argv[2], sys.argv[3]
    od = do = None
    if "--od" in sys.argv: od = float(sys.argv[sys.argv.index("--od") + 1])
    if "--do" in sys.argv: do = float(sys.argv[sys.argv.index("--do") + 1])
    root = os.path.dirname(os.path.abspath(plan_p))

    pozycje = []
    for line in open(plan_p, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"): continue
        p = line.split("\t")
        czas, plik, tryb = sek(p[0]), p[1].strip(), p[2].strip()
        przytnij = float(p[3]) if len(p) > 3 and p[3].strip() else None
        if not os.path.isabs(plik):
            plik = os.path.normpath(os.path.join(root, "..", plik))
        if not os.path.exists(plik):
            print(f"  ⚠️  pomijam, brak pliku: {plik}"); continue
        d = przytnij or dlugosc(plik)
        pozycje.append((czas, plik, tryb, d))
    # Przy wycinku (--od/--do) odrzucamy wstawki spoza okna. Bez tego setpts
    # przesuwa je na oryginalne sekundy i wynik rozciaga sie do dlugosci
    # calego nagrania, mimo ze baza jest przycieta.
    if od is not None or do is not None:
        a = od or 0; b = do if do is not None else 10**9
        pozycje = [x for x in pozycje if a - x[3] < x[0] < b]
    pozycje.sort()
    if not pozycje:
        print("  plan pusty — nie ma czego skladac"); sys.exit(1)

    przes = od or 0
    args = ["ffmpeg", "-v", "error", "-stats"]
    if od is not None: args += ["-ss", str(od)]
    if do is not None: args += ["-to", str(do)]
    args += ["-i", baza]
    for _, plik, _, d in pozycje:
        args += ["-t", str(d), "-i", plik]

    f, ostatni = [], "[0:v]"
    f.append("[0:v]scale=1920:1080,setsar=1[base]")
    ostatni = "[base]"
    for n, (czas, plik, tryb, d) in enumerate(pozycje, start=1):
        t0 = czas - przes; t1 = t0 + d
        if t0 < 0: continue
        # setpts przesuwa klip na wlasciwa sekunde osi czasu
        f.append(f"[{n}:v]scale=1920:1080,setsar=1,setpts=PTS-STARTPTS+{t0}/TB[k{n}]")
        wy = f"[v{n}]"
        if tryb.startswith("prze"):   # przebitka — zastepuje obraz
            f.append(f"{ostatni}[k{n}]overlay=0:0:enable='between(t,{t0},{t1})'{wy}")
        else:                          # nakladka — alfa na gadana glowe
            f.append(f"{ostatni}[k{n}]overlay=0:0:format=auto:enable='between(t,{t0},{t1})'{wy}")
        ostatni = wy
    args += ["-filter_complex", ";".join(f), "-map", ostatni, "-map", "0:a?",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
             "-c:a", "aac", "-b:a", "192k", wynik, "-y"]

    print(f"  skladam {len(pozycje)} wstawek → {wynik}")
    subprocess.run(args, check=True)
    print(f"  gotowe: {wynik}  ({dlugosc(wynik):.1f}s)")

if __name__ == "__main__":
    main()
