# Poprawki ze Studia 02.11: kontekst w składance, muzyka, lista 4 punktów

**Data:** 2026-11-02
**Status:** ✅ wdrożone (6 filmów do ponownego przeglądu); ad-35-w9 czeka na odpowiedź na pytanie montażysty

Uwagi Mateusza ze Studia do 7 filmów: ep-8-wdrozen, ad-35-w9, ad-35-w9--ai-slupsk,
ch-marpasz-2-100-godzin--zajawka, ad-19-ra1, ad-25-e5, ad-33-g1.

## Problem / diagnoza

| Uwaga | Przyczyna |
|---|---|
| ep-8 3:17 „ucina początek zdania, nie wiadomo, do czego nawiązuje” | składanka zaczynała część Doram od „I w tym przypadku do tego klienta…”. Po części o ofertach nie wiadomo, o jakiego klienta chodzi. Start 521,62 (z czasów Whispera) łapał też końcówkę „…uczymy.” |
| ep-8 5:07, zajawka marpasz 0:00 „od pół słowa, nie wiadomo, o co chodzi” | klip `ch-marpasz-2-100-godzin` zaczynał się 0,4 s końcówką słowa „kliknięcie” (3444,4–3444,8). Whisper zgubił też „że to wszystko jest na jedno” |
| ad-35-w9 / --ai-slupsk 0:26–0:27 „dwa razy skontaktuj się — zostaw drugie” | w nagraniu „a skontaktuj się z osobami, którymi, a skontaktuj się z Wami…”. Whisper scalił oba podejścia w jedno, więc cięcie ich nie widziało |
| ad-33-g1 0:21 „nagle się ucina” | przedział kończył się 2249,62, a „pracy.” brzmi do 2249,78 — słowo urwane w pełnym brzmieniu (−13 dB tuż przed sklejką) |
| ad-25-e5 „4. błąd nie jest widoczny, obcina go” | panel pionu ma 500 px. Od 13.10 nad listą jest etykieta serii, więc etykieta + nadtytuł + 4 wiersze ≈ 530 px — czwarty wiersz wypadał poza `overflow:hidden` |
| muzyka 3–4% ciszej (ep-8, ad-19, ad-25) | prośba w procentach = kierunek, nie mnożnik (pamięć `prosby-o-glosnosc-tlumacz-na-decybele`) |

## Decyzja

- **Kontekst z tego samego nagrania, nie nowe nagranie.** Doram: osobny klip `ch-doram-5-70-94-with-context`
  tylko do składanki — przed nim zdanie z początku nagrania „Klient dostawał od swoich kontrahentów
  niemieckich zamówienia w Excelu.”. Rolka `ch-doram-5-70-94` zostaje bez zmian, bo nikt jej nie zgłaszał
  i ma okładkę. Marpasz: poprawka w samym klipie, bo korzystają z niego oba zgłoszone filmy. Na
  początku „Klient zamawiał cztery worki paszy po 25 kilo … cztery różne etykiety,” + pełne
  „I o tyle to teraz się zmieniło, że to wszystko jest na jedno kliknięcie.”. Granice po ciszy w sygnale.
- **Składanka przebudowana tylko dla ep-8** (`compile_episode.build`), czasy rozdziałów i plansz
  w storyboardzie przesunięte o +7,19 s / +22,86 s (od 4:33 / 6:39).
- **Muzyka: pole `musicGainDb` w storyboardzie** (−3 dB) zamiast zmiany globalnego `MUSIC_LUFS`.
  Zmienia tylko filmy, których dotyczy prośba.
- **Lista w pionie od 4 punktów — wersja zwarta** (`.list.dense`: mniejszy padding i interlinia).
  Panelu nie powiększamy, bo pod nim jest strefa zakazana. Dotyczy też innych pionowych list z 4 punktami
  (marpasz-2, ch-module-5/6, ch-om-9), ale wejdzie u nich dopiero przy następnym renderze.
- **`musicOffset` w storyboardzie ep-8 (30,5 s).** Po wydłużeniu odcinka pętla utworu kładła planszę
  końcową na jego naturalnym wyciszeniu (−45 LUFS zamiast −23). Pamięć `muzyka-petla-plansza-na-wyciszeniu`.

## Pułapki

- **Nieudany render udawał nowy.** HyperFrames padł na brakującym assecie (worktree bez ignorowanych
  `assets/broll/hf/video/`), a `package.py` widział stary `render.mp4` i go wykończył. Wynik: stary obraz
  z nową muzyką. Wyłapała to dopiero transkrypcja wycinka gotowego pliku. Od teraz `render.mp4` jest
  kasowany przed renderem.
- **Studio czyta z worktree `cerith`** (zmienna `STUDIO_SOURCE_VIDEO_MENTIONS`), nie z `~/Repo/video-mentions`.
  Rendery szły tam przez symlinki. W `cerith` leży niezacommitowana praca innej sesji (ch-vibe, `package.py`
  z nową geometrią formatu `ad`), więc renderowane było z kodu tej gałęzi, a manifest Studia podmieniony
  tylko we wpisach 7 filmów. Pamięć `render-studio-czyta-z-worktree`.
- Czasy słów Whispera w miejscach dubli były przesunięte o 0,2–0,8 s. Transkrypcja `session` w zakresach
  3440–3446 i 2360–2366 poprawiona ponownym przebiegiem na krótkim odcinku.
