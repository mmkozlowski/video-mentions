#!/usr/bin/env python3
"""Dogrywki audio (sam głos z telefonu) → źródło biblioteki „dubs”.

Mateusz 16.11 nagrał 43 kwestie (06–43 ponownie 20.11 — patrz ORDER) z listy (vault marketing/content/youtube/2026-11-15-do-dogrania.md):
numer, potem zdanie 2–3 razy. Pliki m4a leżą poza repo w raw/2026-11-16-dogrywki-audio/.

1. Skleja pliki m4a w kolejności ORDER, 2 s ciszy między nimi, 48 kHz mono.
2. Głośność: łagodna kompresja + stałe wzmocnienie (do −16 LUFS albo sufitu −1,5 dBTP). Nie loudnorm: jednoprzebiegowy
   podbija ogony pokoju (20.11), a „liniowy” przy cichym nagraniu z wysokimi szczytami przechodzi w dynamiczny i trzeszczy (21.11).
3. Czarny obraz 1280×720 / 30 fps — cut.py tnie obraz i dźwięk jednym przebiegiem, a wstawki
   voice_only i tak zakrywają kadr planszami.
4. Transkrypcja z czasami słów (mlx Whisper large-v3-turbo) → data/transcripts/dubs.json.

  python3 tools/dubs_ingest.py            # wszystko
  python3 tools/dubs_ingest.py --no-asr   # bez transkrypcji
"""
import json
import subprocess
import sys

from sources import SOURCES, TRANSCRIPTS

RAW = SOURCES["dubs"].parent
# pierwszy plik (2 MB) nagrany wcześniej, drugi (17 MB) to główna sesja
# 20.11: drugi plik z 16.11 (nagrane-wstawki-audio.m4a) miał pogłos — wybrzmienie po frazie 130–140 ms zamiast 60 ms
# (zmienione ustawienie mikrofonu). Kwestie 06–43 nagrane ponownie 20.11 (lista vault 2026-11-20-do-dogrania-ponownie.md);
# z 16.11 zostaje tylko pierwszy plik (kwestie 01–05), więc oś 0–63,68 s i granice A1–A4 się nie zmieniają.
# 21.11: trzeci plik — przedstawienie 44h–47e, Open Mercato 48–62, reklamy 71–92, SaaS 120–127 (lista vault
# 2026-11-21-dogranie-przedstawienie.md); dołożony NA KOŃCU, więc offsety 01–43 się nie zmieniają.
ORDER = ["dogrywki-2026-11-16-pierwsze-dogrywki-audio.m4a", "dogrywki-2026-11-20-nowe-glosowe-nagranie.aifc",
         "dogrywki-2026-11-21.aifc"]
GAP = 2.0
MODEL = "mlx-community/whisper-large-v3-turbo"


def main(argv):
    files = [RAW / name for name in ORDER if (RAW / name).exists()]
    if not files:
        raise SystemExit(f"brak plików w {RAW}")
    inputs, graph = [], ""
    for i, f in enumerate(files):
        inputs += ["-i", str(f)]
        graph += f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,apad=pad_dur={GAP}[a{i}];"
    graph += "".join(f"[a{i}]" for i in range(len(files))) + f"concat=n={len(files)}:v=0:a=1[a]"
    wav = RAW / "dogrywki.wav"
    joined = RAW / "dogrywki-surowe.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[a]",
                    "-ar", "48000", str(joined)], check=True)
    # 21.11 (MK: „Pełna historia… mam wrażenie, że trzeszczy”): nagranie 20.11 ma −32 LUFS przy szczytach −10,9 dBTP —
    # do −16 LUFS trzeba +16 dB, a szczyty pozwalają na +9,4 dB. loudnorm wtedy PO CICHU przechodzi w tryb dynamiczny
    # z ogranicznikiem, który ścina mocne sylaby (trzask). Teraz: łagodna kompresja (zbija pojedyncze szczyty), potem
    # STAŁE wzmocnienie do −16 LUFS albo do sufitu −1,5 dBTP — co pierwsze. Bez ogranicznika; resztę robi finalize.
    comp = RAW / "dogrywki-kompresja.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(joined), "-af",
                    "acompressor=threshold=-28dB:ratio=3:attack=5:release=120:knee=4", str(comp)], check=True)
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(comp), "-af",
                            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    gain = min(-16.0 - float(m["input_i"]), -1.5 - float(m["input_tp"]))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(comp), "-af", f"volume={gain:.2f}dB", "-ar", "48000", str(wav)],
                   check=True)
    print(f"głośność: {m['input_i']} LUFS, szczyt {m['input_tp']} dBTP → +{gain:.1f} dB (bez ogranicznika)")
    comp.unlink()
    joined.unlink()
    out = SOURCES["dubs"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720:r=30",
                    "-i", str(wav), "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "30",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(out)], check=True)
    offsets, t = {}, 0.0
    for f in files:
        offsets[f.name] = round(t, 2)
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                 capture_output=True, text=True, check=True).stdout)
        t += d + GAP
    print(f"→ {out}  (początki plików: {offsets})")
    if "--no-asr" in argv:
        return
    subprocess.run(["mlx_whisper", str(wav), "--model", MODEL, "--language", "pl", "--word-timestamps", "True",
                    "--output-dir", str(RAW), "--output-format", "json"], check=True, capture_output=True)
    transcript = json.load(open(RAW / "dogrywki.json"))
    json.dump(transcript, open(TRANSCRIPTS / "dubs.json", "w"), ensure_ascii=False)
    print(f"→ {TRANSCRIPTS / 'dubs.json'}  {len(transcript['segments'])} segmentów")


if __name__ == "__main__":
    main(sys.argv[1:])
