---
name: wstawki-uklad-lewy-domyslny
description: Wstawki tekstowe na gadaną głowę robimy w dwóch wariantach, a domyślny do montażu jest blok po lewej — wyśrodkowany zakrywa twarz mówiącego
metadata:
  type: feedback
---

**Każda wstawka, w której tekst jest treścią** (karta tytułowa, teza, cytat, werdykt na pełnym
kadrze), powstaje w **dwóch wariantach**: wyrównanym do lewej i wyśrodkowanym. **Domyślny
do montażu jest lewy.** Wyśrodkowany zostaje jako zapasowy — do momentów, w których w kadrze
nie ma mówiącego.

Wariant lewy: blok przy `left:132px`, stopień pisma ~18 % mniejszy niż w wersji wyśrodkowanej,
`.scrim.left` zamiast pełnego radialnego, belka i znacznik rozjeżdżające się od lewej krawędzi.
Wzorzec: `projects/youtube/Animation flowbiz youtube/compositions/e01-08b-tytul-lewy.html` —
kopiuj z niego zamiast wymyślać układ od nowa.

**Why:** wstawka wchodzi na gadaną głowę, w której mówiący siedzi **pośrodku kadru**.
Wyśrodkowany tekst ląduje dokładnie na jego twarzy, a radialny scrim jest tam najciemniejszy —
materiał zaczyna wyglądać jak plansza przyklejona na wideo i traci jedyną rzecz, którą odcinek
ma: człowieka, który to mówi. Wariant lewy zostawia prawą połowę kadru odsłoniętą, więc tekst
i mówiący działają równocześnie. Mateusz zatwierdził to 20.08 słowami „wygląda bardzo pro"
po porównaniu obu wariantów na kompozycie z realnym nagraniem.

**How to apply:** przy nowej scenie tekstowej **nie pytaj, który układ** — zrób oba i oddaj
lewy jako rekomendowany, wyśrodkowany jako alternatywę. Zawsze weryfikuj kompozytem na
prawdziwej klatce z nagrania, nie na podglądzie sceny.

Powiązane: [[wstawki-alfa-nie-green-screen]], [[wstawki-czytelnosc-scrim-halo-karta]]
