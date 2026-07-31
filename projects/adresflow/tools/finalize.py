#!/usr/bin/env python3
"""Zbiera gotowe spoty z ../build/ do ../final/ z czytelnymi nazwami i indeksem.

Kopiuje tylko materiały nadające się do publikacji, weryfikuje każdy plik
(brak błędów dekodera, obecność ścieżki audio) i generuje README z opisem,
gdzie którego spotu użyć.
"""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BUILD = os.path.join(ROOT, "build")   # tu ląduje to, co złoży story.py / render.py
FINAL = os.path.join(ROOT, "final")   # deliverable — gotowe do publikacji

# (plik źródłowy, nazwa docelowa, narzędzie, opis, gdzie użyć)
SPOTS = [
    ("adresflow-ugc.mp4", "01-ugc-agentka-gadajaca-glowa.mp4", "całe Studio AI",
     "Agentka mówi do kamery, przebitki narzędzi między frazami",
     "Reels / TikTok — format UGC, najbardziej „ludzki”"),
    ("adresflow-story.mp4", "02-rzut-3d-z-kartki.mp4", "Rzut 3D z kartki",
     "Kartka → grafik nocą w CAD → fioletowa transformacja → mieszkanie",
     "Kampania na rzut 3D; najmocniejsza wizualnie transformacja"),
    ("adresflow-hs.mp4", "03-home-staging.mp4", "Home staging",
     "Stare wnętrze → sprzątanie i wynoszenie rzeczy → jedno zdjęcie",
     "Kampania na home staging"),
    ("adresflow-dz.mp4", "04-zabudowa-dzialki.mp4", "Zabudowa działek",
     "Pusta działka → koparka → dom wyrastający na parceli",
     "Kampania na działki — dom powstaje w kadrze"),
    ("adresflow-full.mp4", "05-studio-ai-przekrojowy.mp4", "całe Studio AI",
     "Dzień agenta → wszystkie narzędzia po kolei",
     "Prezentacja produktu, strona www, dłuższe formaty"),
    ("adresflow-v3d.mp4", "06-krotki-znowu-czekasz.mp4", "Rzut 3D",
     "„Znowu czekasz na rzut 3D?” — najlepszy zmierzony hook (42/100)",
     "Zimny ruch — łapanie uwagi nieznających marki"),
    ("adresflow-v3e.mp4", "07-krotki-nikt-nie-kupi.mp4", "Rzut 3D",
     "„Rzut na kartce. Nikt tego nie kupi.” — hook 40/100",
     "Zimny ruch, wariant do testu A/B z 06"),
    ("adresflow-v1.mp4", "08-krotki-cena-u-grafika.mp4", "Rzut 3D",
     "„Rzut 3D u grafika? 899 zł i tydzień.”",
     "Wariant cenowy"),
    ("adresflow-v2.mp4", "09-krotki-karta-lokalu.mp4", "Rzut 3D",
     "„Masz kartę lokalu. Nie masz wizualizacji.”",
     "Pod deweloperów i karty lokali"),
    # Funkcje ekranowe — ekran produktu renderowany z HTML (ads/hyperframes/),
    # nie generowany modelem wideo.
    ("adresflow-kw.mp4", "10-ksiega-wieczysta.mp4", "Księga wieczysta",
     "Agent nocą przy portalu EKW → jedno wklejenie → cała księga na ekranie "
     "(hook 37, sustain 95)",
     "Kampania na KW; najlepszy hook wśród spotów narracyjnych"),
    ("adresflow-wycena.mp4", "11-wycena-rciwn.mp4", "Wycena nieruchomości",
     "„Ile to warte?” → adres → mediana, rozkład i transakcje z RCiWN "
     "(hook 34, sustain 92)",
     "Najmocniejszy przekaz — twardy dowód i funkcja za 0 kredytów"),
    ("adresflow-oferta.mp4", "12-kreator-oferty.mp4", "Kreator oferty",
     "Biurko w wydrukach → cztery kroki kreatora → gotowe ogłoszenie "
     "(hook 34, sustain 92)",
     "Kampania na kreator oferty; kontrast objętości pracy"),
    # POV „nagrane telefonem" — inny format niż 01–12: bez lektora, cała
    # narracja w przyklejonej planszy, ekran filmowany zamiast nagrywanego.
    ("adresflow-pov-rzut.mp4", "13-pov-rzut-3d.mp4", "Rzut 3D z kartki",
     "POV: wgranie rzutu → wybór stylu → licznik → izometria. Bez lektora "
     "(hook 37, sustain 100 — najwyższy w bibliotece)",
     "Organiczne Reels/TikTok — format „jak to robię”, wygląda jak film użytkownika"),
    ("adresflow-pov-staging.mp4", "14-pov-home-staging.mp4", "Home Staging",
     "POV: zagracony pokój → wariant światła → licznik → gotowe zdjęcie. Bez lektora "
     "(hook 40, sustain 97 — najlepszy hook wśród długich spotów)",
     "Organiczne Reels/TikTok; najmocniejsza transformacja przed/po"),
]


def dur(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True).stdout.strip()
    return float(o) if o else 0.0


def check(p):
    """Zwraca (liczba błędów dekodera, czy ma audio)."""
    err = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    n = sum(1 for l in err.splitlines()
            if "Invalid NAL" in l or "Error splitting" in l)
    streams = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                              "stream=codec_type", "-of", "csv=p=0", p],
                             capture_output=True, text=True).stdout
    return n, "audio" in streams


def main():
    os.makedirs(FINAL, exist_ok=True)
    rows, skipped = [], []
    for src, dst, tool, desc, use in SPOTS:
        sp = os.path.join(BUILD, src)
        if not os.path.exists(sp):
            skipped.append((src, "brak pliku"))
            continue
        errs, has_audio = check(sp)
        if errs:
            skipped.append((src, f"{errs} błędów dekodera — NIE kopiuję"))
            continue
        shutil.copy2(sp, os.path.join(FINAL, dst))
        rows.append((dst, tool, dur(sp), desc, use, has_audio))

    lines = ["# AdresFlow — gotowe reklamy\n",
             "Wszystkie 1080×1920 (9:16), pod Reels, TikTok i YouTube Shorts.\n",
             "Dwa formaty:\n",
             "- **01–12 — narracyjne**: lektor PL + podkład, plansze brandowe, "
             "konstrukcja ból → koszt starej metody → rozwiązanie → CTA.",
             "- **13–14 — POV „jak to robię”**: bez lektora, ekran laptopa "
             "filmowany telefonem, jedna przyklejona plansza. Wygląda jak film "
             "użytkownika — mocniejsze organicznie, słabsze jako klasyczna reklama.\n",
             "| Plik | Narzędzie | Czas | Co pokazuje | Gdzie użyć |",
             "|---|---|---|---|---|"]
    for dst, tool, d, desc, use, _ in rows:
        lines.append(f"| `{dst}` | {tool} | {d:.0f} s | {desc} | {use} |")

    lines += ["\n## Skąd to pochodzi\n",
              "Spoty buduje `../tools/` — `brand.py` (plansze), `story.py` "
              "(montaż pod lektora), `render.py` (krótkie warianty), "
              "`pov.py` (grade „nagrane telefonem”). Teksty siedzą w słownikach "
              "`STORIES` / `VERSIONS`; zmiana copy nie wymaga generowania "
              "niczego na nowo.\n",
              "Ujęcia i lektorzy leżą w `../assets/` — są wielokrotnego użytku, "
              "nowy spot zwykle nie potrzebuje nowych generacji. Ekrany produktu "
              "renderuje `../screens/` (HTML → wideo, 0 kredytów).\n",
              "## Przed publikacją\n",
              "- **899 zł u grafika** to roszczenie porównawcze — mieć na nie źródło.",
              "- **30 kredytów** zgodne z produkcją (`signup_credits_30`); "
              "uwaga: `apps/web/src/lib/data.ts:322` ma nieaktualne „5 kredytów”.",
              "- Muzyka: YouTube Audio Library, licencja bez atrybucji.\n"]

    if skipped:
        lines.append("## Pominięte\n")
        for s, why in skipped:
            lines.append(f"- `{s}` — {why}")
        lines.append("")

    open(os.path.join(FINAL, "README.md"), "w").write("\n".join(lines))

    print(f"— FINAL/ ({len(rows)} spotów):")
    for dst, tool, d, _, _, a in rows:
        print(f"   {dst:42} {d:5.1f}s  {'audio ✓' if a else 'BRAK AUDIO'}")
    for s, why in skipped:
        print(f"   ⚠️  pominięto {s}: {why}")


if __name__ == "__main__":
    main()
