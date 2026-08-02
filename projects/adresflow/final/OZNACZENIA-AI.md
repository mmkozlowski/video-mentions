# Oznaczenie treści AI — rejestr

Podstawa: **art. 50 ust. 4 AI Act** (rozporządzenie 2024/1689), stosowany od **2 sierpnia 2026 r.** Podmiot stosujący system AI, który generuje lub modyfikuje obraz, dźwięk albo wideo wyglądające na autentyczne, ujawnia, że treść została sztucznie wygenerowana lub zmanipulowana.

> **Materiał z Higgsfielda przychodzi bez metadanych C2PA** (sprawdzone `ffprobe`), a przekodowanie w ffmpeg i tak by je zdjęło. Platformy nie oznaczą tych spotów automatycznie — **oznaczenie przy publikacji trzeba włączyć ręcznie za każdym razem**.

| Spot | Składniki AI |
|---|---|
| `01-ugc-agentka-gadajaca-glowa.mp4` | ujęcia wideo wygenerowane przez Higgsfield (seedance / veo); mowa postaci zdubbingowana z angielskiego na polski; lektor syntetyczny (ElevenLabs przez text2speech_v2); zdjęcia przekształcone przez AdresFlow (home staging / rzut 3D) |
| `02-rzut-3d-z-kartki.mp4` | ujęcia wideo wygenerowane przez Higgsfield (seedance / veo); lektor syntetyczny (ElevenLabs przez text2speech_v2); zdjęcia przekształcone przez AdresFlow (home staging / rzut 3D) |
| `03-home-staging.mp4` | ujęcia wideo wygenerowane przez Higgsfield (seedance / veo); lektor syntetyczny (ElevenLabs przez text2speech_v2); zdjęcia przekształcone przez AdresFlow (home staging / rzut 3D) |
| `04-zabudowa-dzialki.mp4` | ujęcia wideo wygenerowane przez Higgsfield (seedance / veo); lektor syntetyczny (ElevenLabs przez text2speech_v2); zdjęcia przekształcone przez AdresFlow (home staging / rzut 3D) |
| `05-studio-ai-przekrojowy.mp4` | ujęcia wideo wygenerowane przez Higgsfield (seedance / veo); lektor syntetyczny (ElevenLabs przez text2speech_v2); zdjęcia przekształcone przez AdresFlow (home staging / rzut 3D) |
| `06-krotki-znowu-czekasz.mp4` | ujęcia wideo wygenerowane przez Higgsfield (seedance / veo); lektor syntetyczny (ElevenLabs przez text2speech_v2); zdjęcia przekształcone przez AdresFlow (home staging / rzut 3D) |
| `07-krotki-nikt-nie-kupi.mp4` | ujęcia wideo wygenerowane przez Higgsfield (seedance / veo); lektor syntetyczny (ElevenLabs przez text2speech_v2); zdjęcia przekształcone przez AdresFlow (home staging / rzut 3D) |
| `08-krotki-cena-u-grafika.mp4` | ujęcia wideo wygenerowane przez Higgsfield (seedance / veo); lektor syntetyczny (ElevenLabs przez text2speech_v2); zdjęcia przekształcone przez AdresFlow (home staging / rzut 3D) |
| `09-krotki-karta-lokalu.mp4` | ujęcia wideo wygenerowane przez Higgsfield (seedance / veo); lektor syntetyczny (ElevenLabs przez text2speech_v2); zdjęcia przekształcone przez AdresFlow (home staging / rzut 3D) |
| `10-ksiega-wieczysta.mp4` | ujęcia wideo wygenerowane przez Higgsfield (seedance / veo); lektor syntetyczny (ElevenLabs przez text2speech_v2) |
| `11-wycena-rciwn.mp4` | ujęcia wideo wygenerowane przez Higgsfield (seedance / veo); lektor syntetyczny (ElevenLabs przez text2speech_v2) |
| `12-kreator-oferty.mp4` | ujęcia wideo wygenerowane przez Higgsfield (seedance / veo); lektor syntetyczny (ElevenLabs przez text2speech_v2) |
| `13-pov-rzut-3d.mp4` | zdjęcia przekształcone przez AdresFlow (home staging / rzut 3D) |
| `14-pov-home-staging.mp4` | zdjęcia przekształcone przez AdresFlow (home staging / rzut 3D) |

## Co zrobić przy publikacji

1. **Włącz oznaczenie na platformie** przy każdym wrzuceniu — TikTok „AI-generated content”, Instagram/Facebook „AI info”, YouTube „zmienione lub syntetyczne treści”. To jest warstwa, którą widzi odbiorca i której platformy pilnują.
2. **W kampaniach płatnych** zadeklaruj to również w menedżerze reklam — oznaczenie AI **nie zastępuje** oznaczenia „reklama” / „materiał sponsorowany”.
3. Metadane pliku niosą adnotację automatycznie (wpisuje je `finalize.py`), ale **nie licz na to, że platforma je odczyta**.

## Czego to NIE obejmuje

- Ekrany produktu w spotach 10–14 są **napisane w HTML**, nie wygenerowane — to rekonstrukcja UI, nie treść AI.
- Typografia, plansze, napisy, montaż i muzyka powstają lokalnie.
- Spoty 13–14 symulują nagranie telefonem. To nie jest treść AI, ale **jest stylizacja** sugerująca nagranie użytkownika — osobna kwestia uczciwości przekazu, poza zakresem art. 50.

> Ten plik generuje `tools/finalize.py` ze słownika `AI_MAP`. Nowy spot bez wpisu zostanie tu oznaczony jako brakujący.
