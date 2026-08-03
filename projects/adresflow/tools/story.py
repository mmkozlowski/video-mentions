#!/usr/bin/env python3
"""Spot narracyjny AdresFlow ~20 s — obraz i napisy sterowane lektorem.

Problem, który to rozwiązuje: przy jednym pliku lektora napisy miały timing
procentowy i nie trafiały w słowa. Tutaj lektor jest pocięty na frazy, każda
mierzona osobno — a napisy i cięcia montażowe wynikają z JEJ długości.
Kolejność jest odwrotna niż zwykle: najpierw głos, potem obraz pod głos.
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
# assets/ = materiał nieodtwarzalny (kupiony za kredyty albo dostarczony),
# build/  = wszystko, co skrypty potrafią wytworzyć od nowa (poza gitem).
SHOTS_DIR = os.path.join(ROOT, "assets", "shots")
VOICE     = os.path.join(ROOT, "assets", "voice")
MUSIC     = os.path.join(ROOT, "assets", "music", "music.mp3")
BUILD     = os.path.join(ROOT, "build")
SCREENS   = os.path.join(BUILD, "screens")
OV        = os.path.join(BUILD, "overlays")
TMP       = os.path.join(BUILD, "cache")
for d in (BUILD, OV, TMP):
    os.makedirs(d, exist_ok=True)


def shot_path(name):
    """Ujęcia źródłowe leżą w assets/shots/, ekrany renderowane z HTML w build/screens/."""
    for base in (SHOTS_DIR, SCREENS):
        p = os.path.join(base, name)
        if os.path.exists(p):
            return p
    raise SystemExit(
        f"Brak ujęcia '{name}'. Szukałem w assets/shots/ i build/screens/.\n"
        f"Ekrany produktu renderuje: cd ../screens && ./render.sh")

sys.path.insert(0, HERE)
import brand  # noqa: E402  (paleta, fonty, komponenty plansz)

W, H = 1080, 1920
MAX_SLOW = 1.15   # powyżej tego spowolnienie widać jako slow motion i gasi hook
ZOOM = 1.30       # zbliżenie w drugiej części ujęcia (zamiast spowalniania)
TAIL = 3.20       # endcard po ostatniej frazie
AI_MARK_IN  = 0.35  # oznaczenie treści AI — wchodzi od razu…
AI_MARK_OUT = 4.20  # …i znika, żeby nie siedzieć w kadrze przez cały spot
MUS_VOL = 0.40    # poziom podkładu przed duckingiem
MUS_THRESH = 0.12 # próg duckingu — niżej = agresywniej ścisza pod lektorem
MUS_RATIO = 4     # stopień ścisznięcia (8 brzmiało jak wyciszenie)

# Ujęcia, w których postać MÓWI — ich obraz jest zsynchronizowany z audio,
# więc nie wolno ich rozciągać ani przyspieszać (rozjechałby się lip-sync).
# Zamiast tego wycinamy z oryginału fragment odpowiadający czasowi w timeline.
SYNC_SHOTS = {"agentka"}


def music_offset(path, need):
    """Najgłośniejszy fragment utworu o długości `need`.

    Podkłady z bibliotek zwykle mają CICHE INTRO — start od 0 s daje efekt
    „muzyki nie słychać, dopiero potem się rozkręca". Mierzone: Magic Marker
    i Monks są na starcie o 5,4 dB cichsze niż w środku.
    """
    total = dur(path)
    if total <= need + 1:
        return 0.0
    best, best_rms = 0.0, -999.0
    step = max(5.0, (total - need) / 8)
    ss = 0.0
    while ss + need <= total:
        out = subprocess.run(
            ["ffmpeg", "-v", "info", "-ss", f"{ss}", "-t", "8", "-i", path,
             "-af", "astats=metadata=1:reset=0", "-f", "null", "-"],
            capture_output=True, text=True).stderr
        vals = [float(m) for m in re.findall(r"RMS level dB:\s*(-?\d+\.?\d*)", out)]
        if vals:
            r = sum(vals) / len(vals)
            if r > best_rms:
                best_rms, best = r, ss
        ss += step
    return best
SIL_DB = "-32dB"  # próg ciszy przy wykrywaniu granic fraz
SIL_MIN = 0.22    # minimalna pauza uznawana za granicę frazy


def _silence_bounds(path, db, d):
    out = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", path,
         "-af", f"silencedetect=noise={db}:d={d}", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    starts, ends = [], []
    for line in out.splitlines():
        if "silence_start:" in line:
            starts.append(float(line.split("silence_start:")[1].strip()))
        elif "silence_end:" in line:
            ends.append(float(line.split("silence_end:")[1].split("|")[0].strip()))
    total = dur(path)
    bounds, prev = [], 0.0
    for s, e in zip(starts, ends):
        if s > prev + 0.25:          # pomiń mikroprzerwy wewnątrz słowa
            bounds.append((prev, s))
            prev = e
    bounds.append((prev, total))
    return bounds


def detect_phrases(path, want=None):
    """Granice fraz z JEDNEGO pliku lektora (silencedetect).

    Kluczowe dla spójności głosu: generowanie każdej frazy osobno daje
    niezależny sampling — barwa i akcent potrafią się zmienić w połowie
    spotu (słychać dwie różne osoby, nazwa marki raz po polsku, raz po
    angielsku). Jeden plik + cięcie po ciszy rozwiązuje to definitywnie.

    Nagrania różnią się dynamiką, więc jeden sztywny próg nie działa dla
    wszystkich — gdy znamy oczekiwaną liczbę fraz, dobieramy próg
    automatycznie zamiast strojenia ręcznego przy każdym nowym lektorze.
    """
    grid = [(SIL_DB, SIL_MIN), ("-35dB", 0.20), ("-38dB", 0.18), ("-30dB", 0.16),
            ("-42dB", 0.15), ("-30dB", 0.12), ("-45dB", 0.15), ("-28dB", 0.10)]
    best = None
    for db, d in grid:
        b = _silence_bounds(path, db, d)
        if want is None:
            return b
        if len(b) == want:
            return b
        if best is None or abs(len(b) - want) < abs(len(best) - want):
            best = b
    return best

# Napis + ujęcie dla KOLEJNYCH fraz wykrytych w vo-full.mp3.
# Liczba wpisów musi zgadzać się z liczbą fraz (skrypt to weryfikuje).
# Retoryka: kontrast z ceną u grafika, ale o naszej cenie nie mówimy —
# zamiast kwoty prowadzimy do darmowych kredytów startowych.
# Teksty lektora — JEDEN plik audio na spot, generowany z tego stringa.
#
# Trzymamy je tutaj, bo przy zmianie „30 → 15 kredytów" okazało się, że nigdzie
# ich nie było i trzeba było odtwarzać nagrania Whisperem. Liczby i skróty pisz
# fonetycznie („trzy de", „piętnaście"), inaczej lektor je przekręca.
#
# Regeneracja: tools/voice.py <klucz>. Po każdej zmianie sprawdź, czy liczba
# fraz wykrytych w audio zgadza się ze scenariuszem — skrypt to weryfikuje.
VO_TEXT = {
    "story": "Znowu dostajesz rzut na kartce? U grafika zapłacisz osiemset "
             "dziewięćdziesiąt dziewięć złotych i poczekasz tydzień. Tutaj wrzucasz "
             "zdjęcie kartki. I masz gotowy render trzy de w sześćdziesiąt sekund. "
             "Pokaż klientowi, jak naprawdę wygląda mieszkanie. Wejdź na Adres Flow "
             "i odbierz piętnaście darmowych kredytów.",
    "hs":    "Mieszkanie do sprzedaży wygląda jak sprzed dekady. Sprzątanie. "
             "Wynoszenie rzeczy. Cały dzień pracy, a zdjęcia i tak wychodzą słabo. "
             "Albo jedno zdjęcie i home staging w sztucznej inteligencji. "
             "Wejdź na Adres Flow i odbierz piętnaście darmowych kredytów.",
    "dz":    "Sprzedajesz działkę. Klient patrzy na trawę i nie widzi swojego domu. "
             "Zamiast czekać na projekt i budowę, pokaż mu wizualizację zabudowy "
             "w minutę. Wejdź na Adres Flow i odbierz piętnaście darmowych kredytów.",
    # UWAGA: „ugc" NIE MA lektora w zwykłym sensie. Ścieżka dźwiękowa to własny,
    # zdubbingowany głos agentki wycięty z `raw-ugc-agentka.mp4` — dlatego
    # vo-ugc.mp3 ma dokładnie tyle samo co ujęcie (27,12 s). Wygenerowanie tu
    # lektora rozwala synchronizację ust i wkłada męski głos pod kobietę
    # na ekranie. Odtworzenie:
    #   ffmpeg -i assets/shots/raw-ugc-agentka.mp4 -vn -c:a libmp3lame -q:a 2 \
    #          assets/voice/vo-ugc.mp3
    # Zmiana treści tego spotu wymaga PONOWNEGO DUBBINGU ujęcia, nie nowego TTS.
    "ugc":   None,
    "full":  "Jesteś agentem nieruchomości. Jeździsz, fotografujesz, sprzątasz. "
             "Potem walczysz z programem graficznym. Adres Flow robi to za ciebie. "
             "Home staging ze zwykłego zdjęcia. Rzut trzy de z odręcznej kartki. "
             "Wizualizacja zabudowy działki. Wszystko w minutę, w jednym miejscu. "
             "Wejdź na Adres Flow i odbierz piętnaście darmowych kredytów.",
    "kw":    "Znowu przepisujesz numer księgi wieczystej? Portal, captcha, cztery "
             "działy. Jedno wklejenie. Zamiast dziesięciu kliknięć. Powierzchnia, "
             "właściciel, hipoteka. Wszystko na jednym ekranie. Wejdź na Adres Flow. "
             "Piętnaście kredytów za darmo.",
    "wycena": "Klient pyta, ile warte jest jego mieszkanie. Zgadujesz albo dzwonisz "
              "po kolegach. Wpisujesz adres. Ceny z aktów notarialnych. Nie z ogłoszeń. "
              "Mediana, rozkład, transakcje z okolicy. Za zero kredytów. Odbierz "
              "piętnaście kredytów na start.",
    "oferta": "Oferta w Wordzie, zdjęcia osobno. Opis pisany od zera. Godzina roboty "
              "na jedno mieszkanie. Cztery kroki. Adres, dane, zdjęcia, opis. Gotowe "
              "ogłoszenie do wysłania. Wejdź na Adres Flow. Piętnaście kredytów za darmo.",
}

SHOTS = {
    "agent":      "raw-agent.mp4",       # klient podaje odręczny szkic
    "grafik":     "raw-grafik.mp4",      # stara metoda: grafik nocą w CAD
    "morph":      "raw-v3-2k.mp4",       # kartka → render 3D (2K)
    "mieszkanie": "raw-mieszkanie.mp4",  # klienci oglądają mieszkanie
    "tablet":     "raw-tablet.mp4",      # render na tablecie
    "ekipa":      "raw-sprzatanie.mp4",  # agent sprząta i porządkuje (NIE remont —
                                         # agenci rzadko remontują, raczej odświeżają)
    "budowa":     "raw-budowa.mp4",      # stara metoda: koparka na działce
    "hs":         "raw-hs-morph.mp4",    # pokój przed → po (home staging)
    "dzialka":    "raw-dz-morph.mp4",    # działka → dom (zabudowa)
    "spacer":     "raw-dzialka-spacer.mp4",  # klienci oglądają dom Z ZEWNĄTRZ
    "agentka":    "raw-ugc-agentka.mp4",  # gadająca głowa (EN → dubbing PL)
    # Ból proceduralny — funkcje ekranowe (KW, wycena, oferta) nie mają
    # widowiskowego „przed/po", więc bohaterem ujęcia jest stara metoda.
    "portal":     "raw-kw-portal.mp4",       # agent nocą przy portalu, stos wydruków
    "niewiem":    "raw-agent-nie-wiem.mp4",  # agent rozkłada ręce przy klientach
    "wydruki":    "raw-biurko-wydruki.mp4",  # biurko zawalone ofertami
    # Ekrany produktu renderowane z HTML przez HyperFrames (../screens/).
    # NIE generujemy ich modelem wideo — UI wychodzi wtedy nieczytelną papką,
    # a polskie napisy bełkotem. Zmiana danych na ekranie = edycja HTML, 0 kredytów.
    "ekran-kw":   "screen-kw.mp4",
    "ekran-wyc":  "screen-wycena.mp4",
    "ekran-of":   "screen-oferta.mp4",
}

# Scenariusze kampanii. Każdy: własny plik lektora `vo-<klucz>.mp3` w assets/voice/
# + lista fraz (napis + ujęcie). Kolejność wpisów musi odpowiadać kolejności
# fraz wykrytych w pliku lektora — skrypt to weryfikuje.
STORIES = {
    # Rzut 3D z kartki — pełny łuk narracyjny
    "story": {
     "eyebrow": "RZUT 3D Z KARTKI",
     "end": ("AdresFlow", "Pierwsze rzuty 3D za darmo", "Odbierz 15 kredytów"),
     "script": [
        {"lines": ["Znowu rzut", "na kartce?"],          "accent": 1, "shot": "agent"},
        {"lines": ["899 zł u grafika.", "Tydzień."],     "accent": 0, "shot": "grafik"},
        {"lines": ["Wrzuć zdjęcie."],                    "accent": 0, "shot": "morph"},
        {"lines": ["Render 3D", "w 60 sekund."],         "accent": 1, "shot": "morph"},
        {"lines": ["Pokaż, jak", "naprawdę wygląda."],   "accent": 0, "shot": "mieszkanie"},
        # CTA i kredyty w jednej frazie — nowy lektor mówi to jednym zdaniem,
        # więc `silencedetect` nie ma gdzie ciąć.
        {"lines": ["Wejdź na AdresFlow.", "15 kredytów za darmo."], "accent": 1, "shot": "tablet"},
    ]},
    # Home staging — ekipa remontowa kontra jedno zdjęcie
    "hs": {
     "eyebrow": "HOME STAGING AI",
     "end": ("AdresFlow", "Home staging w minutę", "Odbierz 15 kredytów"),
     "script": [
        {"lines": ["Mieszkanie", "jak sprzed dekady?"],   "accent": 1, "shot": "hs"},
        {"lines": ["Sprzątanie."],                        "accent": 0, "shot": "ekipa"},
        {"lines": ["Wynoszenie rzeczy."],                 "accent": 0, "shot": "ekipa"},
        {"lines": ["Cały dzień.", "A zdjęcia i tak słabe."], "accent": 1, "shot": "ekipa"},
        {"lines": ["Jedno zdjęcie.", "Home staging AI."], "accent": 1, "shot": "hs"},
        {"lines": ["Za darmo.", "15 kredytów."],          "accent": 0, "shot": "mieszkanie"},
    ]},
    # Działka — klient nie widzi domu na trawie
    "dz": {
     "eyebrow": "ZABUDOWA DZIAŁEK AI",
     "end": ("AdresFlow", "Pokaż potencjał działki", "Odbierz 15 kredytów"),
     "script": [
        {"lines": ["Sprzedajesz", "działkę?"],           "accent": 1, "shot": "dzialka"},
        {"lines": ["Klient widzi trawę.", "Nie dom."],   "accent": 0, "shot": "dzialka"},
        {"lines": ["Zamiast czekać", "na budowę."],      "accent": 0, "shot": "budowa"},
        {"lines": ["Pokaż zabudowę", "w minutę."],       "accent": 1, "shot": "dzialka"},
        {"lines": ["Wejdź na AdresFlow."],               "accent": 0, "shot": "spacer"},
        {"lines": ["15 kredytów", "za darmo."],          "accent": 0, "shot": "spacer"},
    ]},
    # UGC talking head — agentka opisuje to, co widać na przebitkach.
    #
    # KWESTIE PISZ W CZASIE TERAŹNIEJSZYM I TRYBIE ROZKAZUJĄCYM.
    # Angielski czas przeszły („I took") jest bezrodzajowy, ale polski już nie —
    # dubbing musi wtedy wybrać rodzaj i wybiera MĘSKI, co przy kobiecie na
    # ekranie dyskwalifikuje materiał. „Biorę / przeciągam / mam / skończ"
    # nie mają rodzaju i przechodzą przez tłumaczenie bezpiecznie.
    "ugc": {
     "eyebrow": "STUDIO AI",
     "end": ("AdresFlow", "Pierwsze generacje za darmo", "Odbierz 15 kredytów"),
     "script": [
        {"lines": ["Ile razy czekasz", "na rzut 3D?"],      "accent": 1, "shot": "agentka"},
        {"lines": ["Robię zdjęcie.", "Mam rzut 3D."],       "accent": 1, "shot": "morph"},
        {"lines": ["Zagracony pokój..."],                    "accent": 0, "shot": "hs"},
        {"lines": ["...wygląda jak nowy."],                  "accent": 0, "shot": "hs"},
        {"lines": ["Pusta działka?", "Już widzisz dom."],   "accent": 1, "shot": "dzialka"},
    ]},
    # Przekrojowy — cały dzień agenta i całe Studio AI w jednym spocie
    "full": {
     "eyebrow": "STUDIO AI",
     "end": ("AdresFlow", "Studio AI dla agentów nieruchomości", "Odbierz 15 kredytów"),
     "script": [
        {"lines": ["Jesteś agentem", "nieruchomości."],   "accent": 1, "shot": "mieszkanie"},
        {"lines": ["Jeździsz.", "Fotografujesz."],        "accent": 0, "shot": "agent"},
        {"lines": ["I walczysz", "z grafiką."],           "accent": 1, "shot": "grafik"},
        {"lines": ["AdresFlow", "robi to za Ciebie."],    "accent": 0, "shot": "tablet"},
        {"lines": ["Home staging", "ze zdjęcia."],        "accent": 0, "shot": "hs"},
        {"lines": ["Rzut 3D", "z kartki."],               "accent": 0, "shot": "morph"},
        {"lines": ["Zabudowa", "działki."],               "accent": 0, "shot": "dzialka"},
        {"lines": ["Wszystko", "w minutę."],              "accent": 1, "shot": "mieszkanie"},
        {"lines": ["Za darmo.", "15 kredytów."],          "accent": 0, "shot": "tablet"},
    ]},
    # ── Funkcje ekranowe ─────────────────────────────────────────────────────
    # Trzy spoty poniżej różnią się konstrukcją od powyższych: nie ma tu
    # transformacji obrazu (przed/po), więc dowodem nie jest ładny wynik, tylko
    # LICZBA KROKÓW. Ujęcie bólu (stara metoda) → ekran produktu → CTA.
    "kw": {
     "eyebrow": "KSIĘGA WIECZYSTA",
     "end": ("AdresFlow", "Księga wieczysta w jednym wklejeniu", "Odbierz 15 kredytów"),
     "script": [
        # Lektor pauzuje na przecinkach, więc „Portal, captcha, cztery działy"
        # rozpada się na trzy frazy — napisy idą za tym, staccato bije zdanie.
        {"lines": ["Znowu przepisujesz", "numer księgi?"],   "accent": 1, "shot": "portal"},
        {"lines": ["Portal."],                               "accent": 0, "shot": "portal"},
        {"lines": ["Captcha."],                              "accent": 0, "shot": "portal"},
        {"lines": ["Cztery działy."],                        "accent": 1, "shot": "portal"},
        {"lines": ["Jedno wklejenie."],                      "accent": 1, "shot": "ekran-kw"},
        {"lines": ["Zamiast dziesięciu", "kliknięć."],       "accent": 1, "shot": "ekran-kw"},
        {"lines": ["Powierzchnia,", "właściciel, hipoteka."], "accent": 0, "shot": "ekran-kw"},
        {"lines": ["Wszystko", "na jednym ekranie."],        "accent": 1, "shot": "ekran-kw"},
        {"lines": ["Wejdź na AdresFlow."],                   "accent": 0, "shot": "tablet"},
        {"lines": ["15 kredytów", "za darmo."],              "accent": 0, "shot": "tablet"},
    ]},
    "wycena": {
     "eyebrow": "WYCENA NIERUCHOMOŚCI",
     "end": ("AdresFlow", "Wycena z rejestru — za 0 kredytów", "Odbierz 15 kredytów"),
     "script": [
        {"lines": ["Klient pyta,", "ile warte jest mieszkanie."], "accent": 1, "shot": "niewiem"},
        {"lines": ["Zgadujesz albo", "dzwonisz po kolegach."],    "accent": 0, "shot": "niewiem"},
        {"lines": ["Wpisujesz adres."],                          "accent": 0, "shot": "ekran-wyc"},
        {"lines": ["Ceny z aktów", "notarialnych."],             "accent": 1, "shot": "ekran-wyc"},
        {"lines": ["Nie z ogłoszeń."],                           "accent": 1, "shot": "ekran-wyc"},
        {"lines": ["Mediana, rozkład,", "transakcje z okolicy."], "accent": 0, "shot": "ekran-wyc"},
        {"lines": ["Za zero kredytów."],                         "accent": 1, "shot": "ekran-wyc"},
        {"lines": ["Odbierz 15 kredytów", "na start."],          "accent": 0, "shot": "tablet"},
    ]},
    "oferta": {
     "eyebrow": "KREATOR OFERTY",
     "end": ("AdresFlow", "Gotowe ogłoszenie w cztery kroki", "Odbierz 15 kredytów"),
     "script": [
        {"lines": ["Oferta w Wordzie,", "zdjęcia osobno."],  "accent": 1, "shot": "wydruki"},
        {"lines": ["Opis pisany", "od zera."],               "accent": 0, "shot": "wydruki"},
        {"lines": ["Godzina roboty", "na jedno mieszkanie."], "accent": 1, "shot": "wydruki"},
        {"lines": ["Cztery kroki."],                         "accent": 1, "shot": "ekran-of"},
        {"lines": ["Adres, dane,", "zdjęcia…"],              "accent": 0, "shot": "ekran-of"},
        {"lines": ["…opis."],                                "accent": 0, "shot": "ekran-of"},
        {"lines": ["Gotowe ogłoszenie", "do wysłania."],     "accent": 1, "shot": "ekran-of"},
        {"lines": ["Wejdź na AdresFlow."],                   "accent": 0, "shot": "tablet"},
        {"lines": ["15 kredytów", "za darmo."],              "accent": 0, "shot": "tablet"},
    ]},
}


def dur(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip())


def build_timeline(vo_path, script):
    """Timeline z granic fraz wykrytych w pliku lektora."""
    phrases = detect_phrases(vo_path, want=len(script))
    if len(phrases) != len(script):
        raise SystemExit(
            f"Wykryto {len(phrases)} fraz, a scenariusz ma {len(script)} wpisów.\n"
            f"Granice: {[(round(a,2), round(b,2)) for a, b in phrases]}\n"
            f"Dostrój SIL_DB / SIL_MIN albo dopasuj scenariusz.")
    tl = [{**seg, "start": a, "end": b, "dur": b - a}
          for seg, (a, b) in zip(script, phrases)]
    total = dur(vo_path) + TAIL
    tl.append({"lines": [], "accent": 0, "shot": "end",
               "start": dur(vo_path), "end": total, "dur": TAIL})
    return tl, total


def make_brand(key, cfg):
    """Chrome (eyebrow + znak) i endcard w wariancie danego narzędzia.

    Bez tego wszystkie spoty dziedziczyłyby eyebrow „RZUT 3D Z KARTKI"
    i planszę końcową rzutu 3D, niezależnie od reklamowanej funkcji.
    """
    ch = brand.blank()
    brand.eyebrow(ch, cfg["eyebrow"])
    brand.watermark(ch)
    ch.save(f"{OV}/{key}-chrome.png")
    brand.endcard(*cfg["end"]).save(f"{OV}/{key}-end.png")
    brand.ai_mark().save(f"{OV}/ai-mark.png")   # wspólna dla wszystkich spotów


def make_line_overlays(tl, key):
    """Napisy jako osobne warstwy — rozmiar dobrany do najdłuższej linii."""
    meta = {}
    for i, seg in enumerate(tl):
        if not seg["lines"]:
            continue
        size = brand.fit_size(seg["lines"])
        line_h = int(size * 1.30) + 18 + 16
        for j, txt in enumerate(seg["lines"]):
            img, m = brand.line_layer(txt, size, accent=(j == seg["accent"]),
                                      y_center=1330 + j * line_h)
            img.save(f"{TMP}/{key}-seg{i}-{j}.png")
            meta[f"{i}-{j}"] = m
    return meta


def build_video(tl, total, key):
    """Każde ujęcie rozciągane/skracane do sumy przypisanych mu fraz."""
    groups, cur = [], None
    for seg in tl:
        if cur and cur["shot"] == seg["shot"]:
            cur["end"] = seg["end"]
        else:
            cur = {"shot": seg["shot"], "start": seg["start"], "end": seg["end"]}
            groups.append(cur)
    # ujęcia muszą się stykać — luka między frazami należy do ujęcia z lewej
    for i in range(len(groups) - 1):
        groups[i]["end"] = groups[i + 1]["start"]
    groups[0]["start"] = 0.0
    groups[-1]["end"] = total

    parts = []
    for gi, g in enumerate(groups):
        want = g["end"] - g["start"]
        out = f"{TMP}/{key}-shot{gi}.mp4"
        if g["shot"] == "end":
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", f"{want:.3f}",
                "-i", f"{OV}/{key}-end.png", "-filter_complex",
                f"[0:v]scale=2160:3840,zoompan=z='min(1.06,1+0.06*on/(30*{want:.3f}))':d=1:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps=30,setsar=1[v]",
                "-map", "[v]", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                "-pix_fmt", "yuv420p", out], check=True)
        elif g["shot"] in SYNC_SHOTS:
            # mówiąca postać — wycinamy 1:1 z oryginału, bez zmiany tempa
            src = shot_path(SHOTS[g["shot"]])
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{g['start']:.3f}",
                "-t", f"{want:.3f}", "-i", src, "-filter_complex",
                f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"fps=30,setsar=1,eq=saturation=1.06:contrast=1.04,setpts=PTS-STARTPTS[v]",
                "-map", "[v]", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                "-pix_fmt", "yuv420p", out], check=True)
        else:
            src = shot_path(SHOTS[g["shot"]])
            have = dur(src)
            pts = want / have
            base_v = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                      f"fps=30,setsar=1,eq=saturation=1.06:contrast=1.04")
            if pts <= MAX_SLOW:
                # mieści się w dopuszczalnym spowolnieniu — jedno ujęcie
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                    "-filter_complex",
                    f"[0:v]{base_v},setpts={pts:.5f}*PTS,trim=0:{want:.3f}[v]",
                    "-map", "[v]", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-pix_fmt", "yuv420p", out], check=True)
            else:
                # Za mało materiału: zamiast slow motion (zabija dynamikę i hook)
                # tniemy na zbliżenie — druga część to ten sam materiał w zoomie.
                a = min(have / MAX_SLOW, want * 0.55)
                b = want - a
                pa, pb = a / (have * 0.55), b / (have * 0.45)
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-i", src,
                    "-filter_complex",
                    f"[0:v]{base_v},trim=0:{have * 0.55:.3f},setpts={pa:.5f}*(PTS-STARTPTS)"
                    f",trim=0:{a:.3f}[p1];"
                    f"[1:v]{base_v},trim={have * 0.55:.3f},setpts=PTS-STARTPTS,"
                    f"scale={int(W * ZOOM)}:{int(H * ZOOM)},crop={W}:{H},"
                    f"setpts={pb:.5f}*PTS,trim=0:{b:.3f}[p2];"
                    f"[p1][p2]concat=n=2:v=1[v]",
                    "-map", "[v]", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-pix_fmt", "yuv420p", out], check=True)
        parts.append(out)

    with open(f"{TMP}/{key}-concat.txt", "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    base = f"{TMP}/{key}-base.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", f"{TMP}/{key}-concat.txt", "-c", "copy", base], check=True)
    return base


def build_audio(vo_path, total, key):
    """Lektor jest JEDNYM plikiem — dokładamy tylko ciszę pod endcard."""
    out = f"{TMP}/{key}-voice.m4a"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vo_path,
                    "-af", f"loudnorm=I=-16:TP=-1.5:LRA=11,apad,atrim=0:{total:.3f}",
                    "-c:a", "aac", "-b:a", "192k", out], check=True)
    return out


def compose(tl, meta, base, audio, total, key, music=None):
    """Nakłada chrome + napisy zsynchronizowane z frazami; opcjonalnie muzykę."""
    inputs = ["-i", base]
    chrome_idx = 1
    inputs += ["-loop", "1", "-t", f"{total + 0.6}", "-i", f"{OV}/{key}-chrome.png"]
    ai_idx = 2
    inputs += ["-loop", "1", "-t", f"{total + 0.6}", "-i", f"{OV}/ai-mark.png"]

    layers, idx = [], 3
    for i, seg in enumerate(tl):
        for j, _ in enumerate(seg["lines"]):
            inputs += ["-loop", "1", "-t", f"{total + 0.6}",
                       "-i", f"{TMP}/{key}-seg{i}-{j}.png"]
            layers.append((idx, meta[f"{i}-{j}"], seg["start"] + j * 0.10, seg["end"]))
            idx += 1

    f = [f"[0:v]fps=30,setsar=1[base];"]
    end_start = tl[-1]["start"] - 0.3
    f.append(f"[{chrome_idx}:v]format=rgba,fade=t=in:st=0.15:d=0.4:alpha=1,"
             f"fade=t=out:st={end_start:.3f}:d=0.3:alpha=1[chr];")
    f.append(f"[base][chr]overlay=0:0[c0];")
    # Oznaczenie treści AI (art. 50 ust. 4 AI Act) — tylko na starcie.
    # „Najpóźniej przy pierwszej ekspozycji" jest spełnione, a znak nie siedzi
    # w kadrze przez cały spot. Wchodzi po chrome, żeby nie kolidowało z fade-in.
    f.append(f"[{ai_idx}:v]format=rgba,"
             f"fade=t=in:st={AI_MARK_IN:.2f}:d=0.35:alpha=1,"
             f"fade=t=out:st={AI_MARK_OUT:.2f}:d=0.5:alpha=1[aim];")
    f.append(f"[c0][aim]overlay=0:0:"
             f"enable='between(t,{AI_MARK_IN:.2f},{AI_MARK_OUT + 0.6:.2f})'[c1];")
    chain = "c1"

    for k, (ii, m, st, en) in enumerate(layers, start=2):
        sw = brand_pop(st, m["w"])
        sh = brand_pop(st, m["h"])
        f.append(f"[{ii}:v]format=rgba,scale=eval=frame:w={sw}:h={sh},"
                 f"fade=t=in:st={st:.3f}:d=0.14:alpha=1,"
                 f"fade=t=out:st={en - 0.10:.3f}:d=0.22:alpha=1[L{k}];")
        y = f"'{m['cy']}-h/2+if(lt(t,{st + 0.30:.3f}),({st + 0.30:.3f}-t)*80,0)'"
        f.append(f"[{chain}][L{k}]overlay=x='{m['cx']}-w/2':y={y}:"
                 f"enable='between(t,{st:.3f},{en + 0.12:.3f})'[c{k}];")
        chain = f"c{k}"

    fc = "".join(f).rstrip(";")
    final = os.path.join(BUILD, f"adresflow-{key}.mp4")

    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-i", audio]
    a_idx = idx
    if music and os.path.exists(music):
        cmd += ["-i", music]
        m_idx = a_idx + 1
        # ducking: podkład ścisza się pod lektorem (sidechaincompress)
        off = music_offset(music, total + 0.6)
        fc += (f";[{m_idx}:a]atrim={off:.2f},asetpts=PTS-STARTPTS,"
               f"aloop=loop=-1:size=2e9,atrim=0:{total + 0.6:.3f},"
               f"volume={MUS_VOL},afade=t=in:st=0:d=0.35,"
               f"afade=t=out:st={total - 0.6:.3f}:d=1.0[mus];"
               f"[{a_idx}:a]asplit[vo1][vosc];"
               f"[mus][vosc]sidechaincompress=threshold={MUS_THRESH}:ratio={MUS_RATIO}:"
               f"attack=8:release=260[duck];"
               f"[vo1][duck]amix=inputs=2:duration=first:normalize=0,"
               f"loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
        cmd += ["-filter_complex", fc, "-map", f"[{chain}]", "-map", "[aout]"]
    else:
        cmd += ["-filter_complex", fc, "-map", f"[{chain}]", "-map", f"{a_idx}:a"]

    # CFR wymuszony jawnie. Bez tego wyjście wychodzi VFR: przy kilkunastu
    # wejściach `-loop 1` (chrome + linie napisów) ffmpeg dobiera klatkaż tak,
    # że obraz robi się dłuższy od lektora — napisy, wypalone na sztywnych
    # czasach, rozjeżdżają się ze słowami, a endcard puchnie z 3,2 s do kilku.
    cmd += ["-r", "30", "-fps_mode", "cfr", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final]
    subprocess.run(cmd, check=True)
    return final


def brand_pop(st, base, d=0.30):
    u = f"(t-{st:.3f})/{d}"
    return (f"'{base}*if(lt(t,{st:.3f}),0.88,"
            f"if(lt({u},0.6),0.88+0.18*(({u})/0.6),"
            f"if(lt({u},1),1.06-0.06*((({u})-0.6)/0.4),1)))'")


def build_story(key):
    # zabezpieczenie: patrz komentarz przy VO_TEXT["ugc"]
    if VO_TEXT.get(key) is None and key == "ugc":
        pass  # dźwięk pochodzi z ujęcia, nie z TTS — nic nie generujemy
    music = MUSIC
    vo_path = os.path.join(VOICE, f"vo-{key}.mp3")
    if not os.path.exists(vo_path):
        raise SystemExit(f"Brak lektora {vo_path} — wygeneruj go najpierw.")
    cfg = STORIES[key]
    make_brand(key, cfg)
    tl, total = build_timeline(vo_path, cfg["script"])
    print(f"\n— {key} ({total:.2f}s):")
    for s in tl:
        print(f"   {s['start']:5.2f}–{s['end']:5.2f}  {s['shot']:10}  "
              f"{' / '.join(s['lines']) or '(endcard)'}")
    meta = make_line_overlays(tl, key)
    base = build_video(tl, total, key)
    audio = build_audio(vo_path, total, key)
    out = compose(tl, meta, base, audio, total, key,
                  music if os.path.exists(music) else None)
    print(f"== {key}: {out} ({dur(out):.2f}s)"
          + ("  [z muzyką]" if os.path.exists(music) else "  [bez muzyki]"))


if __name__ == "__main__":
    keys = sys.argv[1:] or list(STORIES)
    for k in keys:
        if k not in STORIES:
            raise SystemExit(f"Nieznany scenariusz '{k}'. Dostępne: {', '.join(STORIES)}")
        build_story(k)
