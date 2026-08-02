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

# Co w którym spocie jest wygenerowane przez AI — podstawa oznaczenia wymaganego
# od 2026-08-02 (art. 50 ust. 4 AI Act) i dowód należytej staranności.
#
# UTRZYMUJ RĘCZNIE. Nie da się tego wyprowadzić z plików: materiał z Higgsfielda
# przychodzi BEZ metadanych C2PA (sprawdzone), a montaż w ffmpeg i tak by je zdjął.
# Nowy spot = nowy wpis, inaczej rejestr cicho przestaje być prawdziwy.
AI_COMPONENTS = {
    "ujecia":   "ujęcia wideo wygenerowane przez Higgsfield (seedance / veo)",
    "lektor":   "lektor syntetyczny (ElevenLabs przez text2speech_v2)",
    "dubbing":  "mowa postaci zdubbingowana z angielskiego na polski",
    "zdjecia":  "zdjęcia przekształcone przez AdresFlow (home staging / rzut 3D)",
}
# spot → lista składników AI. Ekrany produktu (HTML) i typografia NIE są AI.
AI_MAP = {
    "01-ugc-agentka-gadajaca-glowa.mp4": ["ujecia", "dubbing", "lektor", "zdjecia"],
    "02-rzut-3d-z-kartki.mp4":           ["ujecia", "lektor", "zdjecia"],
    "03-home-staging.mp4":               ["ujecia", "lektor", "zdjecia"],
    "04-zabudowa-dzialki.mp4":           ["ujecia", "lektor", "zdjecia"],
    "05-studio-ai-przekrojowy.mp4":      ["ujecia", "lektor", "zdjecia"],
    "06-krotki-znowu-czekasz.mp4":       ["ujecia", "lektor", "zdjecia"],
    "07-krotki-nikt-nie-kupi.mp4":       ["ujecia", "lektor", "zdjecia"],
    "08-krotki-cena-u-grafika.mp4":      ["ujecia", "lektor", "zdjecia"],
    "09-krotki-karta-lokalu.mp4":        ["ujecia", "lektor", "zdjecia"],
    "10-ksiega-wieczysta.mp4":           ["ujecia", "lektor"],
    "11-wycena-rciwn.mp4":               ["ujecia", "lektor"],
    "12-kreator-oferty.mp4":             ["ujecia", "lektor"],
    # POV nie ma ani generowanych ujęć, ani lektora — AI siedzi wyłącznie
    # w zdjęciach wynikowych produktu pokazanych na ekranie.
    "13-pov-rzut-3d.mp4":                ["zdjecia"],
    "14-pov-home-staging.mp4":           ["zdjecia"],
}

DISCLOSURE = ("Materiał zawiera treści wygenerowane przez sztuczną inteligencję "
              "(art. 50 AI Act).")

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
        # Remux zamiast kopii: przy okazji wpisujemy oznaczenie AI do metadanych.
        # To NIE jest watermark w rozumieniu art. 50 ust. 2 (ten jest obowiązkiem
        # dostawcy modelu) — to nasz ślad, żeby plik oderwany od kontekstu nadal
        # niósł informację, kto i czym go zrobił.
        parts = [AI_COMPONENTS[k] for k in AI_MAP.get(dst, [])]
        note = DISCLOSURE + (" Składniki AI: " + "; ".join(parts) + "." if parts else "")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", sp, "-c", "copy",
                        "-map_metadata", "0",
                        "-metadata", f"comment={note}",
                        "-metadata", "description=AdresFlow — reklama. " + note,
                        "-metadata", "copyright=AdresFlow",
                        "-movflags", "+faststart",
                        os.path.join(FINAL, dst)], check=True)
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
              "- **15 kredytów** zgodne z produkcją (`signup_credits_30`); "
              "uwaga: `apps/web/src/lib/data.ts:322` ma nieaktualne „5 kredytów”.",
              "- Muzyka: YouTube Audio Library, licencja bez atrybucji.\n"]

    if skipped:
        lines.append("## Pominięte\n")
        for s, why in skipped:
            lines.append(f"- `{s}` — {why}")
        lines.append("")

    open(os.path.join(FINAL, "README.md"), "w").write("\n".join(lines))

    # ── Rejestr oznaczeń AI ────────────────────────────────────────────────
    reg = ["# Oznaczenie treści AI — rejestr\n",
           "Podstawa: **art. 50 ust. 4 AI Act** (rozporządzenie 2024/1689), "
           "stosowany od **2 sierpnia 2026 r.** Podmiot stosujący system AI, "
           "który generuje lub modyfikuje obraz, dźwięk albo wideo wyglądające "
           "na autentyczne, ujawnia, że treść została sztucznie wygenerowana "
           "lub zmanipulowana.\n",
           "> **Materiał z Higgsfielda przychodzi bez metadanych C2PA** "
           "(sprawdzone `ffprobe`), a przekodowanie w ffmpeg i tak by je zdjęło. "
           "Platformy nie oznaczą tych spotów automatycznie — **oznaczenie przy "
           "publikacji trzeba włączyć ręcznie za każdym razem**.\n",
           "| Spot | Składniki AI |", "|---|---|"]
    for dst, _, _, _, _, _ in rows:
        keys = AI_MAP.get(dst)
        if keys is None:
            reg.append(f"| `{dst}` | ⚠️ **BRAK WPISU — uzupełnij `AI_MAP`** |")
        elif not keys:
            reg.append(f"| `{dst}` | brak treści AI |")
        else:
            reg.append(f"| `{dst}` | " + "; ".join(AI_COMPONENTS[k] for k in keys) + " |")
    reg += ["\n## Co zrobić przy publikacji\n",
            "1. **Włącz oznaczenie na platformie** przy każdym wrzuceniu — "
            "TikTok „AI-generated content”, Instagram/Facebook „AI info”, "
            "YouTube „zmienione lub syntetyczne treści”. To jest warstwa, którą "
            "widzi odbiorca i której platformy pilnują.",
            "2. **W kampaniach płatnych** zadeklaruj to również w menedżerze reklam — "
            "oznaczenie AI **nie zastępuje** oznaczenia „reklama” / „materiał sponsorowany”.",
            "3. Metadane pliku niosą adnotację automatycznie (wpisuje je `finalize.py`), "
            "ale **nie licz na to, że platforma je odczyta**.\n",
            "## Czego to NIE obejmuje\n",
            "- Ekrany produktu w spotach 10–14 są **napisane w HTML**, nie wygenerowane — "
            "to rekonstrukcja UI, nie treść AI.",
            "- Typografia, plansze, napisy, montaż i muzyka powstają lokalnie.",
            "- Spoty 13–14 symulują nagranie telefonem. To nie jest treść AI, ale "
            "**jest stylizacja** sugerująca nagranie użytkownika — osobna kwestia "
            "uczciwości przekazu, poza zakresem art. 50.\n",
            "> Ten plik generuje `tools/finalize.py` ze słownika `AI_MAP`. "
            "Nowy spot bez wpisu zostanie tu oznaczony jako brakujący.\n"]
    open(os.path.join(FINAL, "OZNACZENIA-AI.md"), "w").write("\n".join(reg))

    print(f"— FINAL/ ({len(rows)} spotów):")
    for dst, tool, d, _, _, a in rows:
        print(f"   {dst:42} {d:5.1f}s  {'audio ✓' if a else 'BRAK AUDIO'}")
    for s, why in skipped:
        print(f"   ⚠️  pominięto {s}: {why}")


if __name__ == "__main__":
    main()
