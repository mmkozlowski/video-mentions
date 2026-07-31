# Index pamięci — video-mentions (.ai/memory)

Wiedza **cross-project** o produkcji wideo reklamowego. Rzeczy specyficzne dla
jednego klienta/produktu leżą w `projects/<nazwa>/ai/`, nie tutaj.

- [Higgsfield MCP: limity](memory/higgsfield-mcp-limity.md) — trial „unlimited" nie działa przez MCP (liczą się tylko kredyty); `veo3_1_lite` wymusza 8 s przy start+end frame; polski TTS tylko przez `text2speech_v2`/elevenlabs
- [Pipeline montażu](memory/pipeline-montazu.md) — kredyty wyłącznie na generacje, cały montaż lokalnie za darmo; zmiana copy nie kosztuje ani kredyta
- [Copy i hook](memory/copy-i-hook.md) — ból odbiorcy bije opis produktu, ruch w 1. s bije treść; narracja kupuje sustain kosztem hooka
- [Ekran produktu z HTML](memory/ekran-produktu-hyperframes.md) — UI renderujemy przez HyperFrames, nie modelem wideo; cztery rzeczy, które odrzuca `hyperframes check`
- [Lektor i muzyka](memory/audio-lektor-muzyka.md) — nie generuj fraz osobno (dryf barwy); podkłady mają ciche intro, trzeba startować od najgłośniejszego fragmentu

## Decyzje (ADR)

- [Ekran produktu z HTML zamiast nagrań i generacji](decisions/2026-07-30-ekran-produktu-z-html.md) — 2026-07-30
