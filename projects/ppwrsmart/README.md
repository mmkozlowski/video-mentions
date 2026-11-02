# ppwrsmart — filmy PPWR Smart

Filmy sprzedażowe i reklamowe dla PPWR Smart (system dokumentacji zgodności PPWR dla firm
pakujących i producentów opakowań). **Styl: [`ai/styl-wideo.md`](ai/styl-wideo.md)** — przeczytaj przed
każdym nowym filmem.

## Filmy

| Data | Film | Dla kogo | Gdzie MP4 |
|---|---|---|---|
| 2026-10-21 | TAGO „chaos → system”, 100,8 s, lektor PL | spotkanie z zarządem TAGO | vault: `sales/tago/prezentacje/2026-10-21-animacja-chaos-system/animacja-chaos-system.mp4` (MP4 poza gitem tego repo — `.gitignore` z 10.10) |

## Co gdzie

| Katalog | Co |
|---|---|
| `assets/frames/` | 8 klatek AI (GPT Image 2.5) — wzorzec stylu grafik |
| `assets/voice/` | 15 kwestii lektora (ElevenLabs v4, Callum); `8.mp3` = przejście „z PPWR Smart” |
| `assets/recordings/` | nagranie prototypu TAGO revision-003, dwa okna z kursorem (WebM) |
| `assets/brand/` | logo PPWRsmart (lockup jasny i ciemny) |
| `tools/` | `animation.html` (kompozycja, napisy), `render-animation.mjs`, `record-prototype.js`, `build-video.sh` |
| `ai/decisions/` | ADR-y filmów |

Klipy Kling (`*.mp4`) są poza gitem — leżą w vaulcie, `build-video.sh` bierze je z `CLIPS_DIR`.

## Odtworzenie filmu TAGO

```bash
cd tools
./build-video.sh                      # ~6 min → ../final/2026-10-21-tago-chaos-system.mp4
# nowe nagranie prototypu (gdy zmieni się UI):
(cd ~/Repo/tago-ppwr-prototype/.ai/prototypes/discovery/tago-ppwr/revision-003 && python3 -m http.server 8099 --bind 127.0.0.1) &
node record-prototype.js              # → ../assets/recordings/tago-revision-003-dwa-okna.webm
```

Playwright z `~/Repo/ppwrsmart-demo/node_modules`. Zmiana napisu = edycja `scenes` w `animation.html`
i ponowny render, bez kredytów.
