import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

// fileURLToPath, nie .pathname — katalog projektu ma spacje w nazwie,
// a .pathname zwraca je jako %20 i readdirSync leci ENOENT.
const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, "..", "..", "compositions", "logos.css");

// Kolor marki w wersji BEZPIECZNEJ NA CIEMNYM TLE.
// Kilka marek ma oficjalny kolor prawie czarny (GitHub #181717, Notion #000000)
// albo bardzo ciemny fiolet (OpenAI #412991) — na scenie #0A0A08 znikają,
// więc dostają jasny zamiennik. Reszta trzyma oryginał.
const BRAND = {
  claude:       "#D97757",
  openmercato:  "#F5A623",  // wordmark w bursztynie palety — spójny z resztą sceny
  github:       "#FAF8F0",  // oficjalny #181717 nie istnieje na ciemnym
  hubspot:      "#FF7A59",
  salesforce:   "#00A1E0",
  n8n:          "#EA4B71",
  make:         "#B36BFF",  // oficjalny #6D00CC za ciemny
  zapier:       "#FF4F00",
  openai:       "#FAF8F0",  // oficjalny #412991 za ciemny
  excel:        "#21A366",
  googlesheets: "#34A853",
  googledrive:  "#4285F4",
  shopify:      "#7AB55C",
  woocommerce:  "#C285D6",  // oficjalny #96588A za ciemny
  slack:        "#FAF8F0",  // logo wielokolorowe, maska i tak spłaszcza do jednego
  notion:       "#FAF8F0",
  airtable:     "#18BFFF",
  retool:       "#5B8AF5",   // oficjalny #3D3D3D ginie na ciemnym
  gmail:        "#EA4335",
  wordpress:    "#5A9FC4",
};

function aspect(svg) {
  const vb = svg.match(/viewBox="\s*[\d.-]+\s+[\d.-]+\s+([\d.]+)\s+([\d.]+)/);
  if (vb) return Number(vb[1]) / Number(vb[2]);
  const w = svg.match(/\bwidth="([\d.]+)"/), h = svg.match(/\bheight="([\d.]+)"/);
  if (w && h) return Number(w[1]) / Number(h[1]);
  return 1;
}

const files = fs.readdirSync(HERE).filter(f => f.endsWith(".svg")).sort();
const rows = [];

for (const f of files) {
  const name = path.basename(f, ".svg");
  const svg = fs.readFileSync(path.join(HERE, f), "utf8");
  const b64 = Buffer.from(svg, "utf8").toString("base64");
  rows.push({ name, ar: aspect(svg), b64, color: BRAND[name] || "#FAF8F0" });
}

const head = `/* WYGENEROWANE — nie edytuj ręcznie.
   Źródło: assets/logos/*.svg  →  ./build-logos-css.sh
   Znaki marek jako maski CSS: sylwetka bierze kolor z \`color\`, więc jedno
   logo działa i w barwie marki, i w kolorze sceny.

   Użycie:
     <i class="logo logo-claude"></i>                     kolor marki
     <i class="logo logo-github" style="color:#F5A623"></i>  narzucony kolor
     <span class="logo-lockup"><i class="logo logo-n8n"></i> n8n</span>

   Rozmiar ustawia \`font-size\` rodzica (logo ma 1em wysokości) albo własne \`height\`.
   Szerokość liczy się sama z proporcji oryginału — wordmark OpenMercato jest
   ~3,9× szerszy niż wysoki i tak też się wyrenderuje.

   CHROMAKEY: logo to maska pokolorowana \`background-color\`, więc zachowuje się
   jak zwykły tekst — ciemne warianty poza kartą wymagają \`.chroma-plate\`,
   tak samo jak reszta ciemnych elementów. */

.logo{
  display:inline-block; flex:none; vertical-align:middle;
  height:1em; width:1em;
  background-color:currentColor;
  -webkit-mask-repeat:no-repeat; mask-repeat:no-repeat;
  -webkit-mask-position:center;  mask-position:center;
  -webkit-mask-size:contain;     mask-size:contain;
}
/* wymuszenie koloru sceny zamiast koloru marki */
.logo.mono{ color:inherit !important }

/* logo + nazwa w jednej linii */
.logo-lockup{ display:inline-flex; align-items:center; gap:0.42em; white-space:nowrap }

/* kafel z logo — do siatek narzędzi */
.logo-tile{
  display:flex; align-items:center; justify-content:center;
  background:#0A0A08; border:2px solid rgba(245,166,35,0.28);
  border-radius:18px;
}
`;

const body = rows.map(r =>
  `.logo-${r.name}{\n` +
  `  color:${r.color};\n` +
  `  width:calc(1em * ${r.ar.toFixed(4)});\n` +
  `  -webkit-mask-image:url("data:image/svg+xml;base64,${r.b64}");\n` +
  `          mask-image:url("data:image/svg+xml;base64,${r.b64}");\n}`
).join("\n");

fs.writeFileSync(OUT, head + "\n" + body + "\n");

console.log(`── logos.css: ${rows.length} znaków marek`);
for (const r of rows) {
  console.log(`  ${r.name.padEnd(14)} ${r.color}  ar=${r.ar.toFixed(2)}`);
}
console.log(`→ ${path.relative(path.join(HERE, "..", ".."), OUT)}  (${(fs.statSync(OUT).size/1024).toFixed(1)} kB)`);
