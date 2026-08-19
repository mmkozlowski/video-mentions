#!/usr/bin/env python3
"""Etap 3: podkład muzyczny pod gotowy montaż. Uruchamiany OSOBNO i na końcu.

Muzyka jest ostatnia z premedytacją: dopóki trwa strojenie cięć i napisów,
każdy przebieg musiałby ją przeliczać, a i tak ocenia się ją dopiero na
gotowym obrazie.

    python3 tools/music.py --pick          # ranking podkładów z biblioteki
    python3 tools/music.py "Frequency"     # wmiksuj wybrany, w final/

Trzy rzeczy zmierzone wcześniej na spotach AdresFlow, przeniesione tutaj
(.ai/memory/audio-lektor-muzyka):

  1. Biblioteczne podkłady mają CICHE INTRO — średnio kilka dB poniżej środka
     utworu. Startujemy od najgłośniejszego fragmentu, nie od zera, inaczej
     pierwsze sekundy shorta brzmią jak brak muzyki.
  2. Zbyt agresywny ducking (`threshold=0.05, ratio=8`) wycisza podkład pod
     każdą sylabą i słychać pompowanie. Działa `0.12 / 4`.
  3. Za nisko ustawiony poziom to trzecia, niezależna przyczyna „nie słychać
     podkładu". Tu jednak mowa leci prawie bez przerwy i ma być naturalnie —
     dlatego MUS_VOL jest wyraźnie niższy niż w reklamie (0,40).

Kryterium doboru: im MNIEJ energii utwór ma w paśmie mowy (300 Hz – 3 kHz),
tym mniej walczy z głosem.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BUILD = os.path.join(ROOT, "build")
FINAL = os.path.join(ROOT, "final")
LIB = os.path.abspath(os.path.join(ROOT, "..", "adresflow", "assets", "music", "library"))

SRC = os.path.join(BUILD, "final-nomusic.mp4")
MUS_VOL = 0.187         # podkład ma podpierać rytm, nie prowadzić — to vlog
                        # Droga do tej liczby: 0,16 → 0,21 („podgłośnij o kilka
                        # procent", +2,4 dB) → 0,187 („ścisz o 2 %", -1,0 dB).
                        # Uwaga na jednostki: dosłowne 2 % to -0,18 dB, czyli
                        # poniżej progu słyszalności (~1 dB dla szerokiego pasma).
                        # Prośby o „kilka procent" traktuj jako kierunek, nie
                        # mnożnik, i raportuj zmianę w dB.
                        # W reklamie z lektorem ten sam parametr stoi na 0,40.
PLATE_VOL = 0.42        # na planszach nie ma mowy, więc może wyjść na wierzch
FADE_OUT = 2.0


def sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"padło: {' '.join(cmd[:8])}…\n{p.stderr[-1500:]}")
    return p


def dur(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip())


def rms_db(path, ss, length, band=None):
    af = (f"{band}," if band else "") + "astats=metadata=1:reset=0"
    out = subprocess.run(
        ["ffmpeg", "-v", "info", "-ss", str(ss), "-t", str(length), "-i", path,
         "-af", af, "-f", "null", "-"], capture_output=True, text=True).stderr
    vals = [float(m) for m in re.findall(r"RMS level dB:\s*(-?\d+\.?\d*)", out)]
    return sum(vals) / len(vals) if vals else -99.0


def music_offset(path, window=8.0):
    """Sekunda, od której utwór jest już „w środku", a nie w cichym intro."""
    total = dur(path)
    best, best_db = 0.0, -99.0
    t = 0.0
    while t + window < min(total, 90.0):
        db = rms_db(path, t, window)
        if db > best_db:
            best, best_db = t, db
        t += window
    return best


def pick():
    rows = []
    for name in sorted(os.listdir(LIB)):
        if not name.lower().endswith((".mp3", ".wav", ".m4a")):
            continue
        p = os.path.join(LIB, name)
        mid = max(dur(p) / 2 - 15, 0)
        full = rms_db(p, mid, 30)
        speech = rms_db(p, mid, 30, "highpass=f=300,lowpass=f=3000")
        rows.append((speech - full, name))
    rows.sort()
    print("kolizja z pasmem mowy (mniej = lepiej pod gadaną głowę):\n")
    for score, name in rows:
        print(f"  {score:+6.2f} dB   {name}")


def mix(track, out=None):
    matches = [n for n in os.listdir(LIB) if track.lower() in n.lower()]
    if not matches:
        raise SystemExit(f'nie znam podkładu „{track}” — sprawdź --pick')
    path = os.path.join(LIB, matches[0])
    off = music_offset(path)
    length = dur(SRC)
    if out is None:
        os.makedirs(FINAL, exist_ok=True)
        out = os.path.join(FINAL, "agenci-cala-noc-9x16-v2.mp4")

    fc = (
        f"[1:a]atrim=start={off:.2f},asetpts=PTS-STARTPTS,"
        f"aloop=loop=-1:size=2e9,atrim=duration={length:.3f},"
        f"volume={MUS_VOL},afade=t=in:st=0:d=0.8,"
        f"afade=t=out:st={length - FADE_OUT:.3f}:d={FADE_OUT}[bed];"
        # Ducking: podkład ustępuje mowie, ale nie „pompuje" pod każdą sylabą.
        f"[0:a]asplit=2[voice][key];"
        f"[bed][key]sidechaincompress=threshold=0.12:ratio=4:attack=12:"
        f"release=320[duck];"
        f"[voice][duck]amix=inputs=2:duration=first:normalize=0[mixed];"
        f"[mixed]alimiter=limit=0.94[a]"
    )
    # Dźwięk renderujemy OSOBNYM przebiegiem i porównujemy długości przed
    # muxem — `amix` potrafi wydłużyć strumień, a `-t` na wyjściu tego nie
    # ucina (.ai/memory/montaz-pulapki-synchronizacji, pkt 3).
    wav = os.path.join(BUILD, "work",
                       "with-music-" + os.path.basename(out) + ".wav")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", SRC, "-i", path, "-filter_complex", fc, "-map", "[a]",
        "-ar", "48000", "-ac", "2", wav])
    alen, vlen = dur(wav), length
    print(f"  podkład: {matches[0]}  (od {off:.0f}s)")
    print(f"  obraz {vlen:.3f}s / dźwięk {alen:.3f}s "
          f"(różnica {abs(alen - vlen) * 1000:.0f} ms)")
    if alen < vlen - 0.05:
        raise SystemExit("dźwięk krótszy od obrazu — nie muksuję")

    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", SRC, "-i", wav, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-t", f"{vlen:.3f}", "-movflags", "+faststart", out])
    print(f"\n{out}  {dur(out):.2f}s")


def try_out(tracks):
    """Wersje próbne obok siebie — podkład ocenia się POD GŁOSEM, nie solo.

    Surowy plik z biblioteki brzmi zupełnie inaczej niż ten sam plik ściszony
    do 16 %, wystartowany od najgłośniejszego fragmentu i duckowany pod mowę.
    """
    out_dir = os.path.join(BUILD, "music-try")
    os.makedirs(out_dir, exist_ok=True)
    for t in tracks:
        slug = t.lower().replace(" ", "-")
        print(f"\n— {t}")
        mix(t, os.path.join(out_dir, f"v2-{slug}.mp4"))


if __name__ == "__main__":
    if "--try" in sys.argv:
        try_out([a for a in sys.argv[1:] if not a.startswith("--")]
                or ["March to Victory", "Monks", "Frequency"])
    elif "--pick" in sys.argv or len(sys.argv) < 2:
        pick()
    else:
        mix(sys.argv[1])
