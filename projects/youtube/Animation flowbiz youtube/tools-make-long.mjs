/* Buduje długą wersję istniejącej sceny.
 *
 *   node tools-make-long.mjs e01-02-cztery-branze "CZTERY BRANŻE. JEDEN FUNDAMENT." 0.62 3.90 2.0
 *                            ^scena              ^tytuł                            ^slow ^lead ^ogon
 *
 * Sztuczka: NIE przepisujemy czasów w scenie. Oryginalne tweeny lądują
 * w podrzędnej osi `beats`, którą spowalniamy timeScale i doklejamy do
 * osi głównej po karcie tytułowej. Dzięki temu długa wersja nie rozjeżdża
 * się z oryginałem przy każdej poprawce w scenie.
 */
import fs from "node:fs";
import path from "node:path";

const [scene, title, slowRaw, leadRaw, tailRaw, headRaw] = process.argv.slice(2);
const HEAD = headRaw ?? "eyebrow";
const SLOW = Number(slowRaw ?? 0.62);
const LEAD = Number(leadRaw ?? 3.90);
const TAIL = Number(tailRaw ?? 2.0);

const dir = "compositions";
let s = fs.readFileSync(path.join(dir, scene + ".html"), "utf8");

// 1. nagłówek sceny zastępuje karta tytułowa — usuwamy stary eyebrow i jego tweeny
{
  // element nagłówka bywa łamany na kilka linii — kasujemy od <div id="…"> do </div>
  const open = new RegExp('^[ \\t]*<div class="[^"]*" id="' + HEAD + '">', 'm');
  const m = s.match(open);
  if (m) {
    const start = m.index;
    let i = s.indexOf('</div>', start);
    i = s.indexOf('\n', i) + 1;
    s = s.slice(0, start) + s.slice(i);
  }
  const q = "['\"]#" + HEAD + "['\"]";
  const tw = new RegExp("^\\s*tl\\.(to|from|fromTo)\\((\\[[^\\]]*" + q + "[^\\]]*\\]|" + q + ").*$\\n", "gm");
  s = s.replace(tw, "");
}

// 2. oryginalne tweeny idą na oś podrzędną
s = s.replace(/const tl = gsap\.timeline\(\{\s*paused:\s*true\s*\}\);/, "const beats = gsap.timeline();");
s = s.replace(/\btl\./g, "beats.");
s = s.replace(/\(tl,/g, "(beats,");          // helpery typu countTo(tl, …)
s = s.replace(/\{ tl,/g, "{ beats,");

// 3. oś główna: karta tytułowa + spowolnione beaty
// Część scen deklaruje `const DURATION = …`, część podaje liczbę wprost
// w init({ duration: … }). Obsługujemy oba zapisy.
if (!/const DURATION = /.test(s)) {
  const init = s.match(/flowbizScene\.init\(\{[\s\S]*?\n\s*\}\);/);
  if (!init) throw new Error("nie znalazłem init() w " + scene);
  const m = init[0].match(/duration:\s*([0-9.]+),/);
  if (!m) throw new Error("nie znalazłem długości sceny w " + scene);
  const fixed = init[0].replace(/duration:\s*[0-9.]+,/, "duration: DURATION,");
  s = s.replace(init[0], `const DURATION = ${m[1]};\n\n  ` + fixed);
}
s = s.replace(/const DURATION = ([^;]+);/,
`const BEATS_DUR = $1;
  beats.timeScale(${SLOW});

  // oś główna: najpierw karta tytułowa, potem spowolnione beaty oryginału
  const tl = gsap.timeline({ paused:true });
  flowbizScene.titleCard({ tl, text:${JSON.stringify(title)} });
  tl.add(beats, ${LEAD});

  const DURATION = ${LEAD} + BEATS_DUR / ${SLOW} + ${TAIL};`);

// 4. identyfikatory i etykieta
s = s.replace(/id: "([^"]+)",/, 'id: "$1-long",');
s = s.replace(/label: "([^"]+?) ·/, 'label: "$1 LONG ·');
s = s.replace(/<title>([^<]*?) ·/, "<title>$1 LONG ·");

const out = path.join(dir, scene + "-long.html");
fs.writeFileSync(out, s);
console.log(`  ✓ ${scene}-long  (slow ${SLOW}, lead ${LEAD}s, ogon ${TAIL}s)`);
