---
name: copy-i-hook
description: Zmierzone virality_predictor lekcje o copy reklam — ból bije opis produktu, ruch bije treść, nie mówimy o własnej cenie
metadata:
  type: reference
---

Wnioski z produkcji spotów AdresFlow (2026-07-30), **zmierzone `virality_predictor`**, nie wydedukowane.

**Co realnie podnosi `hook_score` (okno 0–3 s):**

| Otwarcie | hook | viral |
|---|---|---|
| „Znowu czekasz na rzut 3D?" (ból + ruch od 1. s) | **42** | 53 |
| „Rzut na kartce. Nikt tego nie kupi." (ból) | 40 | 52 |
| statyczna plansza z kwotą | 31 | 44 |
| opis produktu („Twój szkic. Nasz render.") | 27 | 39 |
| realistyczna scena biurowa (spokojna) | 26 | 50 |

1. **Ból odbiorcy bije opis produktu** o kilkanaście punktów.
2. **Ruch w 1. sekundzie waży więcej niż treść** — statyczna plansza z mocną liczbą przegrała z ujęciem, które od razu się rusza. Pomaga *speed ramp* (`ramp` w `JOBS`).
3. **Abstrakcyjny kolorowy efekt bije realistyczną scenę** na otwarcie: przy scenie biurowej aktywność kory wzrokowej *spada* (0,41 → 0,35), przy fioletowej transformacji skacze (0,67).
4. **Hipoteza, która się NIE potwierdziła:** że hook psuje slow motion. Przebudowa na cięcie na zbliżenie dała wynik identyczny. Nie zgaduj przyczyny — mierz.
5. **Narracja kupuje `sustain` kosztem `hook`.** Spot 20 s z pełnym łukiem: sustain 98, hook 26. Krótki z mocnym otwarciem: hook 42, sustain 91. To dwa narzędzia — krótki do zimnego ruchu, długi do remarketingu.

**Retoryka (decyzja właściciela):** kontrast z ceną u konkurencji tak, **własnej ceny nie podajemy**. Trudno ją obronić przy modelu kredytowym i trzeba by ją aktualizować. Prowadzimy do darmowego progu wejścia:

> „Znowu rzut na kartce? **899 zł u grafika. Tydzień.** … **Za darmo — 30 kredytów.**"

CTA wszędzie: „Odbierz 30 kredytów", endcard: „Pierwsze rzuty 3D za darmo".

**Liczby i ich źródła:**
- **30 kredytów** — `signup_credits_30` (migracja 2026-05-20), potwierdzone w `adresflow-v2 → internal-metrics.repository.ts`. Uwaga: `adresflow-v2/apps/web/src/lib/data.ts:322` ma nieaktualne „5 kredytów na start" — **bug do poprawy w produkcie**.
- **899 zł u grafika** — wiedza domenowa właściciela, **nie dane z repo**. Roszczenie porównawcze w płatnej kampanii musi być prawdziwe i weryfikowalne — trzymaj źródło.

**Why:** te wnioski kosztowały kilkanaście generacji i cztery przebiegi predictora; bez nich łatwo wrócić do „opisu produktu" jako hooka.

**How to apply:** nowy spot otwieraj bólem agenta i ruchem, nie opisem funkcji. Przed kampanią puść `virality_predictor` (max 16 s wideo, limit 2 równoległych zadań). Pipeline: [[pipeline-montazu]].
