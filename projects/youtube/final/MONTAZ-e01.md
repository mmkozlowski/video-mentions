# Odcinek 01 — arkusz montażowy

Gdzie wrzucić którą wstawkę. **Czasy zmierzone na nagraniu**, nie oszacowane ze skryptu —
Whisper ze znacznikami co słowo, dopasowanie przez `tools-kotwice.py`. Skrypt zakładał 11:45,
nagranie ma **16:09**, więc żaden timecode ze `skrypt.md` się nie zgadza.

## Tabela cięć — wszystko naraz

| Czas | Wstawka | Twoje zdanie |
|---|---|---|
| **00:34,9** | `e01-03-dostep` | „nie rozumiem, co tu jest takiego **wow**" |
| **00:39,9** | `e01-06-kod-agenta` | „i tak wchodzi w ten kod" |
| **01:00,3** | `e01-07-serwer-i-dostep` | „nie zajrzysz, jak to jest zrobione" |
| **01:43,5** | `e01-04-skad-przenosisz` | „z HubSpot, Salesforce albo po prostu z Excela" |
| **02:04,6** | `e01-08b-tytul-lewy` | „przenieść szybko i tanio? Czy nie?" |
| **02:57,7** | `e01-01-kopie` | „ten sam plik w kilku różnych wersjach" |
| **05:29,0** | `e01-05-czym-to-nie-jest` | „To nie jest Make, to nie jest n8n…" |
| **13:20,4** | `02-chaos` 🎬 | „Chaos, niewiedza, brak kontroli" |
| **13:24,9** | `01-nerwowka` 🎬 | „gaszenie pożarów, **nerwówka**" |
| **13:50,2** | `03-szukanie` 🎬 | „szukanie po różnych miejscach, kto to zrobił" |
| **14:01,8** | `04-spokoj` 🎬 | „Po prostu wiadomo, kto, co, kiedy" |
| **15:04,7** | `e01-02-cztery-branze` | „Cztery branże, jeden fundament" |

🎬 = przebitka **zamiast** obrazu. Reszta wchodzi **na** gadaną głowę.

## 🔴 Najpierw wybierz ujęcia — nagrywałeś wiele podejść

To jest ważniejsze od timecode'ów. W nagraniu **powtarzasz całe fragmenty** i montaż musi
najpierw zdecydować, które podejście zostaje. Miejsca, w których to widać:

| Fragment | Podejścia |
|---|---|
| payoff „przed i po" | **12:54,9** (urwane) · **13:10,9** (urwane) · **13:19,2 → 13:43,8 ✅ pełne** · 13:50,2 (powtórka) |
| „powiem, komu to odradzam" | 02:08,2 (trzy podejścia pod rząd) · **02:35,9 ✅** |
| „brak dostępu do infrastruktury bywa zaletą" | 05:47,1 (urwane) · **06:04,5 ✅** |
| „trzeci, najuczciwszy" | 11:12,9 (urwane) · **11:17,5 ✅** |
| „nie ukrywam tego, bo i tak sprawdzisz" | 12:21,9 · **12:40,1 ✅** |

Czasy w tabeli cięć wskazują **pełne podejścia**. Jeśli wybierzesz inne, przelicz je ponownie:

```bash
cd ~/Repo/video-mentions/projects/youtube
python3 tools-kotwice.py "/Users/mac/Youtube Projects/S-10 - czym jest OM/01 - czym jest OM.mov" final/kotwice-e01.tsv
```

Skrypt ostrzega ⚠️, gdy fraza pada w kilku miejscach — wtedy wydłuż kotwicę w `kotwice-e01.tsv`.

## 🔴 Payoff jest ciasny

Od „Chaos" (13:20,4) do „Po prostu wiadomo" (14:01,8) masz **41 sekund na cztery przebitki**,
a w pełnym podejściu (13:19–13:44) jeszcze mniej. Klipy mają po 8 s — **dotnij je do 3–5 s**,
inaczej przykryją całą pointę. To mają być szybkie uderzenia, nie sceny.

Kolumna „na czym" mówi, czy wstawka wchodzi **na** gadaną głowę (chromakey/alfa nakładką),
czy **zamiast** obrazu (przebitka pełnoekranowa).

---

## HOOK · 0:00 – ok. 0:40

| Kiedy (Twoje zdanie) | Wstawka | Na czym |
|---|---|---|
| „…nie rozumiem, co tu jest **wow**." | `e01/e01-03-dostep` | na głowie |
| „Claude i tak wchodzi w ten kod." | `e01/e01-06-kod-agenta` | na głowie |
| „w low-code i no-code **nie zajrzysz**… ani do infrastruktury pod spodem" | `e01/e01-07-serwer-i-dostep` | na głowie |

`e01-03` niesie zarówno „co tu jest wow", jak i odpowiedź o stuprocentowym dostępie —
nie tnij go w pół.

## OBIETNICA · po przerywniku z przedstawieniem się

| Kiedy | Wstawka | Na czym |
|---|---|---|
| „czy da się Twój proces przenieść **szybko i tanio** — czy nie" | `e01/e01-08b-tytul-lewy` | na głowie |
| „z HubSpota, z Salesforce'a, albo po prostu z Excela" | `e01/e01-04-skad-przenosisz` | na głowie |

**Bierz wariant `-08b` (lewy).** Wyśrodkowany `e01-08-tytul` zostaw jako zapas na ujęcia,
w których nie ma Cię w kadrze.

## SEGMENT 1 — gdzie dziś żyje proces

| Kiedy | Wstawka | Na czym |
|---|---|---|
| „często to jest **ten sam plik w kilku wersjach**" | `e01/e01-01-kopie` | na głowie |
| „a kto wprowadza te dane? …kilka osób" | arkusze z Drive (patrz niżej) | **zamiast** obrazu |

Arkusze: [folder na Drive](https://drive.google.com/drive/folders/1jT6yXeFu2vIdPkbbfT7a3zqZvdGKsm06).
Widok folderu z trzema nazwami plików obok siebie to najmocniejsze dwie sekundy tego segmentu.

## SEGMENT 3 — czym to NIE jest

| Kiedy | Wstawka | Na czym |
|---|---|---|
| „To nie jest Make. To nie jest n8n. To nie jest Zapier." | `e01/e01-05-czym-to-nie-jest` | na głowie |

## PAYOFF — „wtorek przed i po"

To jest jedyne miejsce, gdzie wchodzą **przebitki aktorskie**, i wchodzą **zamiast** obrazu.
Cztery ujęcia po 8 s, do docięcia — Twoje frazy są krótsze.

| Kiedy | Klip | Na czym |
|---|---|---|
| „Chaos. Niewiedza. Brak kontroli." | `assets/broll-gemini/02-chaos` | zamiast obrazu |
| „Szukanie po różnych miejscach: kto to zrobił, kiedy…" | `assets/broll-gemini/03-szukanie` | zamiast obrazu |
| „Gaszenie pożarów. **Nerwówka**." | `assets/broll-gemini/01-nerwowka` | zamiast obrazu |
| **„A po?"** → „Po prostu wiadomo." | `assets/broll-gemini/04-spokoj` | zamiast obrazu |

> **Czwarty klip jest obowiązkowy.** Bez niego trzy pierwsze są galerią stresu, a nie
> argumentem. Cała siła tego fragmentu siedzi w tym, że widz ogląda tę samą twarz przed i po.

| Kiedy | Wstawka | Na czym |
|---|---|---|
| „Cztery branże. Jeden fundament." | `e01/e01-02-cztery-branze` | na głowie |

`e01-02` wraca na gadaną głowę — po czterech przebitkach z rzędu potrzebujesz Ciebie w kadrze,
inaczej odcinek zaczyna wyglądać jak reklama.

---

## Czego NIE ma i trzeba dograć

| Brakuje | Gdzie | Uwaga |
|---|---|---|
| ujęcie jednego rekordu na demo | segment 5, „historia zmian" | nie weszło 16.08, bo demo nie wpuściło |
| cztery wdrożenia obok siebie | payoff | tylko na dummy danych, nigdy realne |

## Warianty `-long`

W `eNN/warianty-long/` leżą dłuższe wersje tych samych scen. Bierz je, gdy mówisz dany
fragment wolniej, niż zakładał skrypt — a przy 16:09 zamiast 11:45 to jest prawdopodobne.
Treść identyczna, różni się tylko tempo.

## Zanim zaczniesz

1. **Płótno projektu 1920×1080** — bez tego wszystko będzie miękkie (23 % ostrości).
2. Wstawki w skali **100 %**, bez auto-dopasowania.
3. Bierz `*_alpha.mov` — **nie dokładaj własnej blendy**, scrim siedzi w pliku.
4. Klipy B-roll mają 8 s, Twoje frazy są krótsze — dotnij, nie rozciągaj.

Reszta w `README.md` obok.
