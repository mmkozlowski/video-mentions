#!/usr/bin/env python3
"""Ranking głosów po EKSPRESJI, nie po barwie.

Ekspresja mierzalna: zakres dynamiki (LRA), rozrzut głośności między
sylabami i zmienność wysokości tonu. Płaski lektor ma niskie wszystkie trzy.
"""
import subprocess, re, sys, numpy as np

def analyse(path):
    # LRA — zakres dynamiki wg EBU R128
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af",
        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    lra = float(re.search(r'"input_lra"\s*:\s*"?(-?[\d.]+)', out).group(1))

    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1",
        "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    hop = 320                                    # 20 ms
    env = np.array([np.sqrt(np.mean(x[i:i+hop]**2) + 1e-12)
                    for i in range(0, len(x) - hop, hop)])
    voiced = env[env > env.max() * 0.08]          # pomiń ciszę
    db = 20 * np.log10(voiced + 1e-12)
    spread = float(db.std())                      # rozrzut głośności sylab

    # zmienność wysokości tonu — autokorelacja na głośnych ramkach
    f0 = []
    for i in range(0, len(x) - 1024, 1024):
        fr = x[i:i+1024]
        if np.sqrt(np.mean(fr**2)) < 0.02:
            continue
        fr = fr - fr.mean()
        ac = np.correlate(fr, fr, mode="full")[1023:]
        lo, hi = 16000 // 300, 16000 // 70        # 70–300 Hz
        if hi <= lo or hi >= len(ac):
            continue
        p = lo + int(np.argmax(ac[lo:hi]))
        if p > 0:
            f0.append(16000 / p)
    pitch_var = float(np.std(f0)) if len(f0) > 5 else 0.0
    return lra, spread, pitch_var

if __name__ == "__main__":
    rows = []
    for arg in sys.argv[1:]:
        name, path = arg.split("=", 1)
        lra, spread, pv = analyse(path)
        rows.append((name, lra, spread, pv, lra + spread * 0.5 + pv * 0.05))
    rows.sort(key=lambda r: -r[4])
    print(f"{'głos':14} {'LRA':>6} {'rozrzut':>9} {'zmienność tonu':>15} {'ekspresja':>10}")
    print("-" * 60)
    for n, lra, sp, pv, sc in rows:
        print(f"{n:14} {lra:6.1f} {sp:8.1f}dB {pv:14.1f}Hz {sc:10.1f}")
    print("\nWyżej = więcej emocji w głosie.")
