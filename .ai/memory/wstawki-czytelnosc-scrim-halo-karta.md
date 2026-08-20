---
name: wstawki-czytelnosc-scrim-halo-karta
description: Trzy narzędzia czytelności wstawki na materiale — karta, scrim, poświata — i kiedy które; tekst w dolnej tercji zawsze dostaje kartę, nie gradient
metadata:
  type: reference
---

Wstawka leży na gadanej głowie: jasna ściana, książki, **jasny sweter i dłonie**. Sam tekst —
nawet biały — przegrywa z takim tłem. Trzy narzędzia, w kolejności od najmocniejszego:

| Narzędzie | Kiedy | Uwaga |
|---|---|---|
| **karta** (`background:#0D0D0B` + akcent) | tekst w **dolnej tercji** kadru, czyli na dłoniach i swetrze | jedyne, co tam działa |
| **`.scrim`** (gradient) | wstawka przejmuje **cały kadr** — karta tytułowa | wariant `.left` pod blok po lewej |
| **`.halo`** (poświata) | krótki podpis na spokojnym tle | **przy karcie zbędna** |

**Tekst w dolnej tercji dostaje kartę, nie gradient.** Werdykt `e01-07` przeszedł całą drogę:
goły tekst → jaśniejsza czerwień → poświata → pas-scrim, i dopiero karta z własnym solidnym
tłem rozwiązała problem. Przy okazji plik schudł ze 140 MB do 20 MB, bo scrim przestał być
potrzebny.

**Poświata rozmywa krawędzie.** To jest jej cena i przy karcie nie ma powodu jej płacić —
Mateusz zgłosił to jako „problem z ostrymi krawędziami". Karta + zero poświaty = czysty piksel.

**Nie łącz dwóch narzędzi naraz.** Scrim pod kartą to podwójne przyciemnienie i wygląda jak błąd.

**Pułapka animacji:** jeśli scrim zjeżdża wcześniej niż tekst, przez ostatnie klatki tekst zostaje
nagi na materiale. Scrim wchodzi **przed** treścią i schodzi **po** niej.

Powiązane: [[wstawki-alfa-nie-green-screen]], [[wstawki-uklad-lewy-domyslny]]
