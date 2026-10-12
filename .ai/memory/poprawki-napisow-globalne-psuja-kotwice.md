---
name: poprawki-napisow-globalne-psuja-kotwice
description: caption-fixes.json działa na KAŻDE wystąpienie słowa we wszystkich klipach — poprawka pod jeden klip psuje napisy i kotwice storyboardu w innych; używaj kontekstu „poprzednie|słowo”
metadata:
  type: feedback
---

`data/caption-fixes.json` poprawia słowo w napisach **i** w osi, na której szukają kotwice
storyboardu (`Composition.words` → `Clock`). Klucz bez kontekstu działa na każde wystąpienie
we wszystkich klipach. 12.10 „Programista” → „programiści” (dodane pod „jako programiści” w module)
wywróciło render ad-33-g1 („nie ma słowa „Programista” w klipie” — tam naprawdę pada
„Programista mówi”) i dało błędny napis „jeden programiści” w ch-om-8.

**Why:** Whisper myli formy fleksyjne kontekstowo, a słownik jest płaski i globalny.
**How to apply:** poprawka zwykłego słowa (nie nazwy własnej) → klucz z kontekstem
`"jako|Programista"` (tylko po słowie „jako”). Przed dodaniem przeszukaj `build/library/*/words.json`,
gdzie jeszcze pada to słowo. Klucze ze spacją („AI Subsk”) nigdy nie działały — fix porównuje
pojedyncze słowa. Błąd „nie ma słowa” przy słowie, które widać w words.json = najpierw sprawdź słownik.
Powiązane: [[montaz-pulapki-synchronizacji]], [[pipeline-montazu]].
