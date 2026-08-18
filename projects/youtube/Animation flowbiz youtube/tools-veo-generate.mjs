/* Generator wstawek filmowych przez Veo (Gemini API).
 *
 *   GEMINI_API_KEY=… node tools-veo-generate.mjs --list        # jakie modele widzi klucz
 *   GEMINI_API_KEY=… node tools-veo-generate.mjs --dry         # co by poszło, bez wydawania
 *   GEMINI_API_KEY=… node tools-veo-generate.mjs               # generuje wszystko
 *   GEMINI_API_KEY=… node tools-veo-generate.mjs 03 07         # tylko wybrane ujęcia
 *
 * Wynik: assets/veo/<id>-<slug>.mp4
 *
 * DLACZEGO --list JEST PIERWSZY: nazwy modeli Veo zmieniają się między
 * wydaniami, a klucz widzi tylko te, do których ma dostęp. Zamiast zgadywać
 * i dostać 404 po opłaceniu joba, skrypt najpierw pyta API, co jest dostępne,
 * i sam wybiera najnowszy model `veo-*`.
 *
 * KOSZT: każde ujęcie to płatna generacja. --dry pokazuje listę bez wydawania.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT  = path.join(HERE, "assets", "veo");
const API  = "https://generativelanguage.googleapis.com/v1beta";
const KEY  = process.env.GEMINI_API_KEY || process.env.GOOGLE_GENERATIVE_AI_API_KEY;

// Wspólny sufiks stylu — trzyma ujęcia w jednej estetyce z animacjami:
// ciemne wnętrza, ciepłe światło praktyczne, płytka głębia ostrości.
const STYLE =
  "cinematic documentary b-roll, dark interior, warm practical lighting, " +
  "shallow depth of field, subtle handheld motion, muted amber and deep green tones, " +
  "no on-screen text, no captions, no logos, 16:9";

// Ujęcia. `ep` mówi, do którego odcinka pasuje; `where` — w które miejsce skryptu.
const SHOTS = [
  { id:"01", ep:"01", slug:"biuro-excele", where:"SEG 1 — „wchodzę do firmy i widzę Excele”",
    prompt:"over-the-shoulder shot of an office worker scrolling a dense spreadsheet on a desktop monitor, second monitor with another spreadsheet beside it, cluttered desk, evening office" },
  { id:"02", ep:"01", slug:"drukarka-zamowienie", where:"SEG 1 — papierowy obieg",
    prompt:"close-up of a laser printer pushing out a printed order sheet, a hand reaches in and takes the warm page, office background out of focus" },
  { id:"03", ep:"01", slug:"palce-klawiatura", where:"SEG 1 — „wszyscy trzej wprowadzają dane”",
    prompt:"macro shot of fingers typing quickly on a mechanical keyboard, blurred spreadsheet glow reflected on the keys, dark room" },
  { id:"04", ep:"01", slug:"magazyn-tablet", where:"PAYOFF — cztery branże",
    prompt:"warehouse worker walking between tall shelves holding a rugged tablet, scanning a carton label, industrial lighting, wide shot" },

  { id:"05", ep:"03", slug:"kartka-po-hali", where:"HOOK — „sześć godzin chodzę z nią po firmie”",
    prompt:"following shot from behind a person walking through a small manufacturing hall holding a single sheet of paper, machines and workbenches on both sides" },
  { id:"06", ep:"03", slug:"kartka-schemat", where:"HOOK — kartka ze schematem",
    prompt:"top-down close-up of a sheet of paper on a workbench covered in hand-drawn arrows and boxes, a hand adds another arrow with a pen, warm desk lamp" },
  { id:"07", ep:"03", slug:"warsztat-stol", where:"SEG 1 — warsztat, sześć godzin",
    prompt:"two people sitting at a table covered with printed notes and an open laptop, one gestures while explaining, meeting room, natural window light" },
  { id:"08", ep:"03", slug:"dyktafon", where:"SEG 3 — „nagrajcie tę rozmowę”",
    prompt:"close-up of a smartphone lying on a wooden table recording audio, waveform on screen, two blurred people talking in the background" },
  { id:"09", ep:"03", slug:"operator-karta", where:"SEG 2 — droga zamówienia przez produkcję",
    prompt:"machine operator in a small factory checking a printed technical sheet against a running machine, sparks of detail work, industrial ambience" },

  { id:"10", ep:"08", slug:"kod-okulary", where:"SEG 2 — agent pracuje",
    prompt:"extreme close-up of eyeglasses reflecting scrolling code on a monitor, face out of focus, dark room lit only by the screen" },
  { id:"11", ep:"08", slug:"noc-monitor", where:"HOOK — praca w nocy",
    prompt:"wide shot of a lone developer at a desk at night, monitor is the only light source in a dark apartment, city window behind" },
  { id:"12", ep:"08", slug:"terminal-logi", where:"SEG 3 — struktura odpowiada agentowi",
    prompt:"macro shot of a terminal window rapidly scrolling log lines on a dark screen, green and amber highlights, slight screen bloom" },
  { id:"13", ep:"08", slug:"zamkniecie-laptopa", where:"PAYOFF — koniec pracy",
    prompt:"close-up of hands slowly closing a laptop lid, room goes dark as the screen light disappears, quiet ending beat" },

  { id:"14", ep:"*", slug:"biurko-poranek", where:"przerywnik — przedstawienie się",
    prompt:"morning desk still life, steam rising from a coffee cup beside an open laptop, soft window light, slow push in" },
  { id:"15", ep:"*", slug:"serwerownia", where:"dowolne — metafora systemu",
    prompt:"slow dolly past server racks with blinking status lights in a dark data centre, shallow focus, cool light with warm accents" },
  { id:"16", ep:"*", slug:"tablica-rysunek", where:"SEG — projektowanie procesu",
    prompt:"person drawing boxes and arrows on a glass whiteboard with a marker, seen from the other side of the glass, meeting room, backlit" },
  { id:"17", ep:"*", slug:"podpis-dokument", where:"SEG — akceptacja, decyzja",
    prompt:"close-up of a hand signing a printed document with a fountain pen on a dark desk, warm lamp light from the side" },
  { id:"18", ep:"*", slug:"hala-timelapse", where:"przerywnik — upływ czasu",
    prompt:"time-lapse of a small production hall through a working day, people moving quickly, light shifting from morning to evening" },
];

// Klucz widzi trzy warianty Veo 3.1: pelny, `fast` i `lite`. Domyslnie bierzemy
// `fast` — do b-rolla pod narracje pelna jakosc nie robi roznicy, a kosztuje
// wielokrotnie wiecej. Nadpisanie: VEO_MODEL=veo-3.1-generate-preview
function pickModel(models){
  const veo = models.filter(m => /veo/i.test(m));
  if (process.env.VEO_MODEL) return process.env.VEO_MODEL;
  return veo.find(m => /fast/.test(m)) || veo.find(m => !/lite/.test(m)) || veo[0];
}

async function listModels(){
  const r = await fetch(`${API}/models?key=${KEY}&pageSize=200`);
  if (!r.ok) throw new Error(`models: ${r.status} ${await r.text()}`);
  const d = await r.json();
  return (d.models || []).map(m => m.name.replace(/^models\//, ""));
}

async function generate(model, shot){
  const body = {
    instances: [{ prompt: `${shot.prompt}. ${STYLE}` }],
    parameters: { aspectRatio: "16:9", resolution: process.env.VEO_RES || "1080p", durationSeconds: Number(process.env.VEO_SECONDS || 8) },
  };
  const r = await fetch(`${API}/models/${model}:predictLongRunning?key=${KEY}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${shot.id}: ${r.status} ${await r.text()}`);
  const op = await r.json();

  // Veo liczy się w minutach, nie sekundach — odpytujemy co 12 s, max 12 min.
  for (let i = 0; i < 60; i++) {
    await new Promise(res => setTimeout(res, 12000));
    const s = await fetch(`${API}/${op.name}?key=${KEY}`);
    const st = await s.json();
    if (st.error) throw new Error(`${shot.id}: ${JSON.stringify(st.error)}`);
    if (!st.done) { process.stdout.write("."); continue; }

    const vids = st.response?.generateVideoResponse?.generatedSamples
              || st.response?.generatedSamples || [];
    const uri = vids[0]?.video?.uri;
    if (!uri) throw new Error(`${shot.id}: brak URI w odpowiedzi: ${JSON.stringify(st.response).slice(0,400)}`);

    const dl = await fetch(uri.includes("key=") ? uri : `${uri}&key=${KEY}`);
    const buf = Buffer.from(await dl.arrayBuffer());
    const file = path.join(OUT, `${shot.id}-${shot.slug}.mp4`);
    fs.writeFileSync(file, buf);
    return file;
  }
  throw new Error(`${shot.id}: timeout`);
}

const args = process.argv.slice(2);
const dry  = args.includes("--dry");
const only = args.filter(a => /^\d+$/.test(a));
const want = only.length ? SHOTS.filter(s => only.includes(s.id)) : SHOTS;

if (args.includes("--list")) {
  if (!KEY) { console.error("Brak GEMINI_API_KEY"); process.exit(1); }
  const ms = await listModels();
  console.log("modeli widocznych dla klucza:", ms.length);
  console.log("veo:", ms.filter(m => /veo/i.test(m)).join(", ") || "— brak dostępu do Veo");
  process.exit(0);
}

if (dry) {
  console.log(`── ${want.length} ujęć (dry run, nic nie wydane)\n`);
  for (const s of want) console.log(`  ${s.id}  [odc. ${s.ep}]  ${s.slug}\n      ${s.where}\n      ${s.prompt}\n`);
  process.exit(0);
}

if (!KEY) {
  console.error("Brak GEMINI_API_KEY. Ustaw go i uruchom ponownie:");
  console.error("  GEMINI_API_KEY=… node tools-veo-generate.mjs --list");
  process.exit(1);
}

fs.mkdirSync(OUT, { recursive: true });
const model = pickModel(await listModels());
if (!model) { console.error("Klucz nie widzi żadnego modelu veo-*"); process.exit(1); }
console.log(`── model: ${model}, ujęć: ${want.length}\n`);

for (const shot of want) {
  process.stdout.write(`  ${shot.id} ${shot.slug} `);
  try { console.log(`\n     ✓ ${path.basename(await generate(model, shot))}`); }
  catch (e) { console.log(`\n     ✗ ${e.message}`); }
}
