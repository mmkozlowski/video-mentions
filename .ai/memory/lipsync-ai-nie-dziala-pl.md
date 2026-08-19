---
name: lipsync-ai-nie-dziala-pl
description: Syntetyczny lip-sync po polsku w Higgsfield MCP nie działa — trzy podejścia, trzy porażki; nie wydawać na to kredytów
metadata:
  type: reference
---

**Nie da się w Higgsfield MCP zrobić wiarygodnej gadającej głowy mówiącej po polsku.** Sprawdzone trzema metodami, każda odrzucona przez właściciela jako niezsynchronizowana:

1. `seedance_2_0` + `start_image` (zdjęcie portretowe) + `audio_references` — ~27 kr
2. To samo, dłuższe ujęcie i prompt opisujący ruch ust na samogłoskach/spółgłoskach — ~31 kr
3. `seedance_2_0` + **`video_references`** (prawdziwe nagranie jako wzorzec) + `audio_references` — ~23 kr

Metoda 3 była najlepsza **wizualnie** (zachowała prawdziwy pokój, koszulę, światło i kadr selfie, więc sceny AI wyglądały jak jedno ujęcie z materiałem prawdziwym), ale **synchronizacja i tak nie siadła**.

**Przyczyna:** w katalogu MCP nie ma dedykowanego modelu lip-sync. `seedance` to model spójności postaci — audio dostaje jako referencję *ruchu*, nie jako fonemy do odwzorowania. Modele trenowano głównie na angielskim, więc polskie głoski wypadają najgorzej. `dubbing` ma lip-sync w opisie, ale jest zrobiony do tłumaczenia i zsyntezowałby własny głos, kasując klon.

**Łączny koszt nauki: ~80 kredytów.** Nie powtarzać.

**Co robić zamiast:**
- **Twarz tylko z prawdziwego nagrania.** Mamy 15,8 s materiału Bartka (`Bartek - nagranie.mp4`) — zsynchronizowanego z definicji, bo to jego usta i jego głos. Wystarcza na hook (0–5,3 s) i ofertę (5,3–14,6 s).
- **Nowe kwestie = jego sklonowany głos na przebitkach**, bez twarzy. Zero problemu synchronizacji, zero kredytów na wideo.
- Każde kolejne zdanie, które ma paść z jego twarzy, wymaga **nowego nagrania telefonem** — nie generacji.

Klon głosu działa dobrze i zostaje: [[glos-bartka-klon]].
