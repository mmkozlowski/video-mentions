# Moduły systemu ze strony flowbiz.pl — kopia do wstawek

Sekcja „Z tych klocków składamy Twój system” ze strony głównej flowbiz.pl (`#modules`):
9 kart modułów i okno aplikacji w języku Open Mercato ze scenami klikanymi przez kursor.
Wstawka `ins-intro` używa jej jako makiety `modules` (`tools/mockups.py`): klocki wlatują
i wpinają się w okno, a potem kursor klika ekrany modułów w rytm wymienianych branż.

- `section.html` — wynik `systemModulesSection()` z `src/components/home-v2/systemModules.ts`
  z polskimi tekstami z `src/messages/pl.json` (`home.modules.*`).
- `section.css` — wycinek `src/components/home-v2/home-v2.css`: tokeny `.fbv2`, blok
  „MODUŁY SYSTEMU” i tokeny `.ad-dark`.

Dane na ekranach są zmyślone, bez nazw klientów (tak samo jak na stronie). Przed podmianą
plików sprawdź to jeszcze raz: `grep -ciE "baltona|tago|dreno|marpasz|vacu|społem" section.html` → `0`.

## Odświeżenie po zmianie na stronie

Strona żyje w repo `flowbiz-automation-unlocked` (stan z 05.11.2026: worktree `porcupinefish`,
zmiana jeszcze niezacommitowana). Silnik pokazu ze strony (`initModuleShowcase`) NIE jest
kopiowany: liczy czas zegarem przeglądarki, a render wideo wymaga osi GSAP przewijanej
klatka po klatce. Ruch dla wideo jest w `mockups.py` → `modules()`.

```bash
SITE=~/orca/workspaces/flowbiz-automation-unlocked/porcupinefish   # albo inny worktree strony
OUT=$(pwd)/packaging/brand/site-modules
TMP=$(mktemp -d)
cp $SITE/src/components/home-v2/systemModules.ts $TMP/
sed -i '' 's#from "./markup"#from "./markup.ts"#' $TMP/systemModules.ts
echo 'export type HomeHrefs = any;' > $TMP/markup.ts
cat > $TMP/render.mts <<EOF
import { readFileSync, writeFileSync } from "node:fs";
import { systemModulesSection } from "./systemModules.ts";
const pl = JSON.parse(readFileSync("$SITE/src/messages/pl.json", "utf8"));
const get = (k: string) => k.split(".").reduce((o: any, p) => o?.[p], pl.home);
const t = (k: string) => { const v = get(k); if (typeof v !== "string") throw new Error(k); return v; };
writeFileSync("$OUT/section.html", systemModulesSection(t, { booking: "#" } as any, pl.home.modules.mock));
EOF
npx esbuild $TMP/render.mts --bundle --platform=node --format=esm --outfile=$TMP/render.mjs && node $TMP/render.mjs
```

CSS wycinasz po nagłówkach komentarzy w `home-v2.css` (blok `MODUŁY SYSTEMU` do
`prefers-reduced-motion` włącznie, plus `.fbv2 .ad-dark{…}`). Po odświeżeniu przejrzyj klatki
wstawki (`package.py ins-intro --format youtube --snapshot`). Geometria łączników jest liczona
w `modules()` ze stałych wymiarów siatki, więc zmiana szerokości kart na stronie jej nie rusza.
