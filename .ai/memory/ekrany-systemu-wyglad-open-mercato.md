---
name: ekrany-systemu-wyglad-open-mercato
description: Makieta systemu w odcinku ma wyglądać jak prawdziwe Open Mercato (powłoka z tools/om_screens.py), nie jak karta z kaflami
metadata:
  type: feedback
---

Gdy Mateusz w odcinku mówi o systemie, który realnie zrobiliśmy (panel klienta B2B, import zamówień,
etykiety, katalog z faktury, plan produkcji), ekran w kadrze musi wyglądać jak poważny system:
powłoka Open Mercato z `tools/om_screens.py` (sidebar z firmą i ikonami lucide, okruszki, lista w karcie,
status-badge, panel boczny, komunikat w rogu). Wzorzec: `shell()` + `table()` + `slate()` w tym pliku,
okno 1200×600 jak `production_plan`.

**Why:** MK 23.11: „jak mówię o programach, systemach, nie mogą wyglądać jak zabawka, tylko poważny
system, taki jak realnie zrobiliśmy”. Stare karty (`.mk-window`, duże kafle z literą, 3 pigułki) czytały się
jak szablon, mimo że mechanizm był pokazany dobrze.

**How to apply:**
- Nowy ekran systemu → funkcja w `om_screens.py` i wpis w `SCREENS`, nie nowa karta w `mockups.py`.
- Schematy pojęciowe (stos ofert, 3 z 20, droga kartki, mapa) mogą zostać kartami — nie udają systemu.
- Dane wymyślone, bez nazw klientów, osób i cen; firma w sidebarze opisowo („Hurtownia pamiątek”).
- Podgląd bez renderu: `package.py <ep> --format youtube --palette F --snapshot <s> …`, klatki
  w `build/packaging/<ep>/youtube-F/.hyperframes/artifacts/snapshots/`.
- Długa nazwa w komórce z `.omx-cell2` zamienia się w samo „…” — skracaj nazwę, nie polegaj na ellipsis.

Powiązane: [[ekran-produktu-hyperframes]], [[ffmpeg-wspolne-wejscie-zjada-ram]].
