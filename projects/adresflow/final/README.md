# AdresFlow — gotowe reklamy

Wszystkie 1080×1920 (9:16), pod Reels, TikTok i YouTube Shorts.

Dwa formaty:

- **01–12 — narracyjne**: lektor PL + podkład, plansze brandowe, konstrukcja ból → koszt starej metody → rozwiązanie → CTA.
- **13–14 — POV „jak to robię”**: bez lektora, ekran laptopa filmowany telefonem, jedna przyklejona plansza. Wygląda jak film użytkownika — mocniejsze organicznie, słabsze jako klasyczna reklama.

| Plik | Narzędzie | Czas | Co pokazuje | Gdzie użyć |
|---|---|---|---|---|
| `01-ugc-agentka-gadajaca-glowa.mp4` | całe Studio AI | 31 s | Agentka mówi do kamery, przebitki narzędzi między frazami | Reels / TikTok — format UGC, najbardziej „ludzki” |
| `02-rzut-3d-z-kartki.mp4` | Rzut 3D z kartki | 24 s | Kartka → grafik nocą w CAD → fioletowa transformacja → mieszkanie | Kampania na rzut 3D; najmocniejsza wizualnie transformacja |
| `03-home-staging.mp4` | Home staging | 23 s | Stare wnętrze → sprzątanie i wynoszenie rzeczy → jedno zdjęcie | Kampania na home staging |
| `04-zabudowa-dzialki.mp4` | Zabudowa działek | 18 s | Pusta działka → koparka → dom wyrastający na parceli | Kampania na działki — dom powstaje w kadrze |
| `05-studio-ai-przekrojowy.mp4` | całe Studio AI | 27 s | Dzień agenta → wszystkie narzędzia po kolei | Prezentacja produktu, strona www, dłuższe formaty |
| `06-krotki-znowu-czekasz.mp4` | Rzut 3D | 12 s | „Znowu czekasz na rzut 3D?” — najlepszy zmierzony hook (42/100) | Zimny ruch — łapanie uwagi nieznających marki |
| `07-krotki-nikt-nie-kupi.mp4` | Rzut 3D | 10 s | „Rzut na kartce. Nikt tego nie kupi.” — hook 40/100 | Zimny ruch, wariant do testu A/B z 06 |
| `08-krotki-cena-u-grafika.mp4` | Rzut 3D | 12 s | „Rzut 3D u grafika? 899 zł i tydzień.” | Wariant cenowy |
| `09-krotki-karta-lokalu.mp4` | Rzut 3D | 10 s | „Masz kartę lokalu. Nie masz wizualizacji.” | Pod deweloperów i karty lokali |
| `10-ksiega-wieczysta.mp4` | Księga wieczysta | 20 s | Agent nocą przy portalu EKW → jedno wklejenie → cała księga na ekranie (hook 37, sustain 95) | Kampania na KW; najlepszy hook wśród spotów narracyjnych |
| `11-wycena-rciwn.mp4` | Wycena nieruchomości | 20 s | „Ile to warte?” → adres → mediana, rozkład i transakcje z RCiWN (hook 34, sustain 92) | Najmocniejszy przekaz — twardy dowód i funkcja za 0 kredytów |
| `12-kreator-oferty.mp4` | Kreator oferty | 20 s | Biurko w wydrukach → cztery kroki kreatora → gotowe ogłoszenie (hook 34, sustain 92) | Kampania na kreator oferty; kontrast objętości pracy |
| `13-pov-rzut-3d.mp4` | Rzut 3D z kartki | 30 s | POV: wgranie rzutu → wybór stylu → licznik → izometria. Bez lektora (hook 37, sustain 100 — najwyższy w bibliotece) | Organiczne Reels/TikTok — format „jak to robię”, wygląda jak film użytkownika |
| `14-pov-home-staging.mp4` | Home Staging | 30 s | POV: zagracony pokój → wariant światła → licznik → gotowe zdjęcie. Bez lektora (hook 40, sustain 97 — najlepszy hook wśród długich spotów) | Organiczne Reels/TikTok; najmocniejsza transformacja przed/po |

## Skąd to pochodzi

Spoty buduje `../tools/` — `brand.py` (plansze), `story.py` (montaż pod lektora), `render.py` (krótkie warianty), `pov.py` (grade „nagrane telefonem”). Teksty siedzą w słownikach `STORIES` / `VERSIONS`; zmiana copy nie wymaga generowania niczego na nowo.

Ujęcia i lektorzy leżą w `../assets/` — są wielokrotnego użytku, nowy spot zwykle nie potrzebuje nowych generacji. Ekrany produktu renderuje `../screens/` (HTML → wideo, 0 kredytów).

## Przed publikacją

- **899 zł u grafika** to roszczenie porównawcze — mieć na nie źródło.
- **30 kredytów** zgodne z produkcją (`signup_credits_30`); uwaga: `apps/web/src/lib/data.ts:322` ma nieaktualne „5 kredytów”.
- Muzyka: YouTube Audio Library, licencja bez atrybucji.
