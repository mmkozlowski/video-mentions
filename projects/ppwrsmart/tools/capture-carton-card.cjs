// Screenshots of the PPWR Smart technical card (ppwrsmart-demo/.ai/preview) with every proper name removed,
// for the carton-producer ads. Usage: node capture-carton-card.cjs <outDir>
const { chromium } = require('/Users/mac/Repo/ppwrsmart-demo/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const SRC = '/Users/mac/Repo/ppwrsmart-demo/.ai/preview';
const out = process.argv[2];
const replacements = [
  [/Przedsiębiorstwo OPAK KREFT Adrian Kreft, Jacek Kreft s\.c\.|OPAK KREFT Adrian Kreft, Jacek Kreft s\.c\./g, 'Twoja Firma'],
  [/OPAK KREFT/g, 'Twoja Firma'], [/\bOPAK\b/g, 'producenta'], [/Kreft/g, ''],
  [/ul\. [^<|,]*\d+[A-Za-z]?, \d{2}-\d{3} [A-ZŁŚŻ][a-ząęółśżźćń]+/g, 'ul. Przykładowa 1, 00-000 Miasto'],
  [/Jolanta Puzdrowska|Aleksandra Witanowska/g, 'Dział jakości'], [/Karolina Jarosz/g, 'Dział zakupów'],
  [/[a-z]+@opakkreft\.com/g, 'jakosc@twojafirma.pl'], [/biuro@przyklad\.pl/g, 'zakupy@odbiorca.pl'],
  [/\d{3} \d{3} \d{3}/g, '000 000 000'], [/\b\d{10}\b/g, '000-000-00-00'],
  [/Przykładowy Odbiorca Sp\. z o\.o\./g, 'Odbiorca (marka spożywcza)'],
  [/Indeks IBiz/g, 'Indeks ERP'], [/IBIZ-/g, 'ERP-'], [/\bIBiz\b/g, 'ERP'],
  [/AQL-/g, 'TEK-'], [/>AQL</g, '>Dostawca tektury<'], [/\bAQL\b/g, 'Dostawca tektury'], [/Czeczewo/g, 'Miasto'],
];
const LEAK = /\bOPAK\b|Kreft|AQL|IBiz|IBIZ|Puzdrowsk|Witanowsk|Jarosz|Kieleńsk|Czeczew|Gdańsk|przyklad\.pl/g;
const mark = `<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128"><rect x="8" y="8" width="112" height="112" rx="26" fill="#0c3b2e"/><path d="M38 66l18 18 34-38" stroke="#c8a55a" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1.2 });
  for (const f of ['karta-wystawiona', 'karta-robocza-maksymalna']) {
    let html = fs.readFileSync(path.join(SRC, f + '.html'), 'utf8');
    for (const [re, to] of replacements) html = html.replace(re, to);
    await p.setContent(html, { waitUntil: 'load' });
    await p.evaluate(svg => document.querySelectorAll('img.brand-mark').forEach(i => { i.src = 'data:image/svg+xml;base64,' + btoa(svg); }), mark);
    // rendered text (CSS uppercase, split spans) can still carry names — scrub the DOM as well
    await p.evaluate(() => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
      while ((n = w.nextNode())) n.nodeValue = n.nodeValue.replace(/opak kreft/gi, 'Twoja Firma').replace(/\bopak\b/gi, 'producenta').replace(/kreft/gi, '')
        .replace(/[0-9]{2}-[0-9]{3} [A-ZŁŚŻ][a-ząęółśżźćń]+/g, '00-000 Miasto').replace(/ul\. [A-ZŁŚŻ][a-ząęółśżźćń]+ [0-9]+[A-Za-z]?/g, 'ul. Przykładowa 1'); });
    await p.waitForTimeout(300);
    const hit = (await p.evaluate(() => document.body.innerText)).match(LEAK);
    console.log(f, 'leaks:', JSON.stringify(hit ? [...new Set(hit)] : [])); if (hit) { const t = await p.evaluate(() => document.body.innerText); for (const m of t.matchAll(/.{0,40}(OPAK|Czeczew).{0,30}/g)) console.log('  ctx:', m[0]); }
    await p.screenshot({ path: path.join(out, `card-${f}.png`), fullPage: true });
  }
  await b.close();
})();
