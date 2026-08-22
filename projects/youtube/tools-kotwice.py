#!/usr/bin/env python3
"""
Dopasowanie kotwic montazowych do nagrania.

Zamienia "szukaj zdania w 16-minutowym nagraniu" na "tnij na 13:20,4".
Whisper daje znaczniki czasu CO SLOWO; ten skrypt szuka w nich fraz z arkusza
montazowego i wypisuje sekunde, w ktorej padaja.

    python3 tools-kotwice.py <nagranie.mov|.wav> <kotwice.tsv>

Format kotwic (TSV, dwie kolumny): nazwa_wstawki <TAB> fraza do znalezienia.
Fraza nie musi byc doslowna — dopasowanie jest rozmyte, bo Whisper przekreca
koncowki, a Ty i tak nie mowisz slowo w slowo za prompterem.

DLACZEGO ROZMYTE, A NIE DOSLOWNE: na nagraniu 01 fraza ze skryptu "nie rozumiem,
co tu jest wow" brzmi realnie "nie rozumiem co tu jest takiego wow". Doslowne
szukanie nie znajduje nic i wyglada na blad nagrania, a nie na roznice slowa.

PULAPKA: krotkie i pospolite frazy trafiaja w zle miejsce. Slowo "chaos" na
nagraniu 01 pada i w segmencie 2, i w payoffie — dopasowanie wybralo pierwsze.
Kotwica ma byc na tyle dluga, zeby wystapila raz. Skrypt ostrzega, gdy znajdzie
kilka trafien o zblizonej jakosci.
"""
import json, re, sys, os, subprocess, unicodedata, difflib, tempfile

def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", s)

def hms(t):
    return f"{int(t//60):02d}:{t%60:05.2f}"

def transkrybuj(media, cache_dir):
    baza = os.path.join(cache_dir, os.path.splitext(os.path.basename(media))[0])
    js = baza + ".json"
    if os.path.exists(js):
        return js
    wav = baza + ".wav"
    if not os.path.exists(wav):
        subprocess.run(["ffmpeg", "-v", "error", "-i", media, "-vn",
                        "-ar", "16000", "-ac", "1", wav, "-y"], check=True)
    subprocess.run(["whisper", wav, "--language", "pl", "--model", "small",
                    "--word_timestamps", "True", "--output_format", "json",
                    "--output_dir", cache_dir], check=True)
    return js

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    media, plik_kotwic = sys.argv[1], sys.argv[2]
    cache = os.path.join(tempfile.gettempdir(), "kotwice-cache")
    os.makedirs(cache, exist_ok=True)

    d = json.load(open(transkrybuj(media, cache)))
    words = [(w["word"].strip(), w["start"])
             for seg in d["segments"] for w in seg.get("words", [])]
    toks = [norm(w) for w, _ in words]

    kotwice = []
    for line in open(plik_kotwic, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        nazwa, fraza = line.split("\t", 1)
        kotwice.append((nazwa.strip(), fraza.strip()))

    print(f"{'wstawka':<28} {'traf':>5}  czas       kontekst")
    print("-" * 100)
    for nazwa, fraza in kotwice:
        p = norm(fraza).split(); n = len(p); cel = " ".join(p)
        oceny = []
        for i in range(len(toks) - n + 1):
            r = difflib.SequenceMatcher(None, cel, " ".join(toks[i:i+n])).ratio()
            if r > 0.5:
                oceny.append((r, i))
        if not oceny:
            print(f"{nazwa:<28} {'BRAK':>5}  —          nie znaleziono: „{fraza}”")
            continue
        oceny.sort(reverse=True)
        r, i = oceny[0]
        frag = " ".join(w for w, _ in words[max(0, i-2):i+n+3])
        print(f"{nazwa:<28} {r*100:>4.0f}%  {hms(words[i][1])}   …{frag[:60]}…")
        rywale = [o for o in oceny[1:6] if o[0] > r - 0.08]
        if rywale:
            czasy = ", ".join(hms(words[j][1]) for _, j in rywale[:3])
            print(f"{'':<28} {'':>5}  ⚠️  podobne trafienia: {czasy} — wydluz kotwicę")

if __name__ == "__main__":
    main()
