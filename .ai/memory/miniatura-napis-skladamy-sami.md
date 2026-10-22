---
name: miniatura-napis-skladamy-sami
description: Napis na miniaturze z generatora obrazów nie jest w foncie marki — składamy go sami w Plus Jakarta Sans 800 na belkach
metadata:
  type: feedback
---

22.10.2026 miniatura „SZEF PROGRAMUJE Z AI?” (ep-vibecoding) przyszła z generatora z napisem
narysowanym przez AI: dwa różne kroje (szeroki „SZEF”, wąski jak Impact „PROGRAMUJE”).
Mateusz: „ten font na miniaturce jest zgodny ze specyfikacją marki?”. Nie był.

**Why:** brandbook (repo marki, `docs/brand/wideo-i-reklamy.md`) każe Plus Jakarta Sans 800,
a generator zawsze dobiera krój po swojemu i nie da się go wymusić poleceniem.
**How to apply:** z generatora bierzemy tylko obraz (ludzie, rekwizyt, tło). Napis, etykiety
i odznaki narzędzi składamy w HTML (Plus Jakarta 800, belki biała/mięta `#2FD3A0`, tekst
`#0E1F1A`, oryginalne logo z `packaging/brand/logos/`) i zrzucamy headless Chrome w 1280×720.
Gdy obraz ma już napis, zakrywamy go podkładem w kolorze tła i nowymi belkami, potem sprawdzamy
w powiększeniu, czy nie wystają resztki starych krawędzi. Zasady miniatur: `WYTYCZNE-MONTAZU.md` §13,
[[miniatury-bez-obcych-skilli]].
