import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

// fileURLToPath, nie .pathname — katalog projektu ma spacje w nazwie.
const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT  = path.join(HERE, "..", "..", "..", "final", "logos");

// Ta sama tablica co w build-logos-css.mjs: kolory CZYTELNE NA CIEMNYM TLE.
// GitHub #181717, Notion #000000 i OpenAI #412991 gina na ciemnym kadrze,
// wiec dostaja jasne zamienniki — to celowe, nie pomylka.
const BRAND = {
  claude:"#D97757", openmercato:"#F5A623", github:"#FAF8F0", hubspot:"#FF7A59",
  salesforce:"#00A1E0", n8n:"#EA4B71", make:"#B36BFF", zapier:"#FF4F00",
  openai:"#FAF8F0", excel:"#21A366", googlesheets:"#34A853", googledrive:"#4285F4",
  shopify:"#7AB55C", woocommerce:"#C285D6", slack:"#FAF8F0", notion:"#FAF8F0",
  airtable:"#18BFFF", wordpress:"#5A9FC4",
};

// Trzy warianty, bo montaz kladzie logo na roznych tlach:
//   marka  — kolor firmowy, gdy logo ma byc rozpoznawalne samo z siebie
//   white  — na ciemnym kadrze albo na zdjeciu, gdy kolor marki gryzie sie z tlem
//   amber  — kolor akcentu scen, gdy logo ma nalezec do naszej planszy
const VARIANTS = [
  { suffix: "",       color: null },      // null = kolor marki z BRAND
  { suffix: "-white", color: "#FAF8F0" },
  { suffix: "-amber", color: "#F5A623" },
];

const LONG_EDGE = 512;   // dluzszy bok w pikselach — z zapasem na skalowanie w 1080p

function aspect(svg) {
  const vb = svg.match(/viewBox="\s*[\d.-]+\s+[\d.-]+\s+([\d.]+)\s+([\d.]+)/);
  if (vb) return Number(vb[1]) / Number(vb[2]);
  const w = svg.match(/\bwidth="([\d.]+)"/), h = svg.match(/\bheight="([\d.]+)"/);
  if (w && h) return Number(w[1]) / Number(h[1]);
  return 1;
}

fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(path.join(OUT, "svg"), { recursive: true });

const files = fs.readdirSync(HERE).filter(f => f.endsWith(".svg")).sort();

// Kopia wektorow obok PNG-ow: montaz ma miec wszystko w jednym folderze, a program,
// ktory umie SVG (After Effects, Motion), skaluje go bez utraty ostrosci.
// Kopiowane skryptem, nie recznie — inaczej rozjezdzaja sie z zrodlem.
for (const f of files) fs.copyFileSync(path.join(HERE, f), path.join(OUT, "svg", f));
const browser = await chromium.launch();
const page = await browser.newPage();
const sheet = [];

for (const f of files) {
  const name = path.basename(f, ".svg");
  const svg  = fs.readFileSync(path.join(HERE, f), "utf8");
  const b64  = Buffer.from(svg, "utf8").toString("base64");
  const ar   = aspect(svg);

  const w = ar >= 1 ? LONG_EDGE : Math.round(LONG_EDGE * ar);
  const h = ar >= 1 ? Math.round(LONG_EDGE / ar) : LONG_EDGE;

  for (const v of VARIANTS) {
    const color = v.color || BRAND[name] || "#FAF8F0";
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(
      `<style>html,body{margin:0;padding:0;background:transparent}
       div{width:${w}px;height:${h}px;background-color:${color};
           -webkit-mask:url("data:image/svg+xml;base64,${b64}") center/contain no-repeat;
                   mask:url("data:image/svg+xml;base64,${b64}") center/contain no-repeat}</style>
       <div></div>`
    );
    await page.screenshot({
      path: path.join(OUT, `${name}${v.suffix}.png`),
      omitBackground: true,
    });
  }
  sheet.push({ name, w, h, color: BRAND[name] || "#FAF8F0" });
  console.log(`  ✓ ${name.padEnd(14)} ${w}×${h}  ×3 warianty`);
}

// Arkusze pogladowe — zebys widzial cala paczke naraz, zamiast otwierac 54 pliki.
// Renderowane tym samym Chromium co PNG-i, wiec nie wymagaja ImageMagicka.
for (const v of VARIANTS) {
  const label = v.suffix === "" ? "kolor marki" : v.suffix.slice(1);
  const cells = sheet.map(s => {
    const file = `${s.name}${v.suffix}.png`;
    const b64  = fs.readFileSync(path.join(OUT, file)).toString("base64");
    return `<figure><img src="data:image/png;base64,${b64}"><figcaption>${file}</figcaption></figure>`;
  }).join("");

  await page.setViewportSize({ width: 1400, height: 300 });  // fullPage doleje reszte — nizsza wartosc nie zostawia pustego pasa na dole
  await page.setContent(
    `<style>
       @font-face{font-family:x;src:local("Helvetica Neue"),local("Arial")}
       body{margin:0;background:#0A0A08;font:500 15px/1.3 x,system-ui,sans-serif;color:#8A837C}
       h1{margin:0;padding:34px 40px 10px;font-size:22px;font-weight:700;color:#F5A623;letter-spacing:0.04em}
       .grid{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;padding:16px 40px 40px}
       figure{margin:0;background:#13110D;border:1px solid rgba(245,166,35,0.18);
              border-radius:12px;padding:20px 12px 12px;text-align:center}
       img{height:74px;width:auto;max-width:100%;object-fit:contain;display:block;margin:0 auto 14px}
       figcaption{font-size:12px;word-break:break-all;color:#6E6862}
     </style>
     <h1>Logotypy do montażu — ${label}</h1><div class="grid">${cells}</div>`
  );
  await page.screenshot({
    path: path.join(OUT, `_przeglad-${v.suffix === "" ? "kolor-marki" : v.suffix.slice(1)}.png`),
    fullPage: true,
  });
  console.log(`  ✓ _przeglad-${v.suffix === "" ? "kolor-marki" : v.suffix.slice(1)}.png`);
}

await browser.close();

// Sciagawka obok plikow — zebys nie musial otwierac kazdego PNG-a, zeby wiedziec, co jest.
const readme =
`# Logotypy do montażu — przezroczyste PNG

Wygenerowane: \`assets/logos/export-png.mjs\` (\`node export-png.mjs\`). Ręczne poprawki przepadną
przy następnym eksporcie — źródłem są SVG-e w \`assets/logos/\`.

Każdy znak w trzech wariantach, dłuższy bok **${LONG_EDGE} px**, kanał alfa:

| Plik | Kiedy |
|---|---|
| \`<marka>.png\` | kolor firmowy — gdy logo ma być rozpoznawalne samo z siebie |
| \`<marka>-white.png\` | na ciemnym kadrze albo na zdjęciu, gdy kolor marki gryzie się z tłem |
| \`<marka>-amber.png\` | \`#F5A623\` — gdy logo ma należeć do naszej planszy, nie stać obok niej |

**Kolory firmowe są celowo nieoficjalne tam, gdzie oryginał jest za ciemny.** GitHub to \`#181717\`,
Notion \`#000000\`, OpenAI \`#412991\` — na ciemnym kadrze wszystkie znikają, więc dostały jasne
zamienniki. Jeśli kładziesz logo na jasnym tle, weź wariant firmowy i sprawdź kontrast okiem.

**Znak jest jednobarwny.** Maska nie zna kolorów źródła, więc Slack i Google Drive tracą swoją
paletę. Dla nich, jeśli potrzeba oryginału, weź plik z \`svg/\` obok — wektory leżą w tym samym
folderze i skalują się bez utraty ostrości w programach, które je czytają (After Effects, Motion).

**Wnętrza są przezroczyste, nie białe.** Siatka w Excelu, litera N w Notion, kotek GitHuba —
to dziury w masce. Na ciemnym kadrze czytają się dobrze, na jasnym znak zrobi się pusty.

Podgląd całej paczki bez otwierania 54 plików: \`_przeglad-kolor-marki.png\`,
\`_przeglad-white.png\`, \`_przeglad-amber.png\`.

## Co jest

| Marka | Rozmiar | Kolor firmowy |
|---|---|---|
${sheet.map(s => `| \`${s.name}\` | ${s.w}×${s.h} | \`${s.color}\` |`).join("\n")}
`;

fs.writeFileSync(path.join(OUT, "README.md"), readme);
console.log(`\n→ ${files.length} marek × ${VARIANTS.length} warianty = ${files.length * VARIANTS.length} plików`);
console.log(`→ projects/youtube/final/logos/`);
