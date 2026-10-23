// Strips the client's identity from the TAGO prototype on the fly (Playwright routes), for public PPWR Smart ads.
// The prototype itself is untouched. Usage: await neutralize(ctx); after each navigation: await page.evaluate(SCRUB_SOURCE).
const replacements = [
  // no proper names at all in ads (decision 23.10): fictional suppliers, people, chains and cities become roles
  [/Tekturix Sp\. z o\.o\.|Tekturix/g, 'Dostawca kartonów'],
  [/Folmar Flex Sp\. z o\.o\.|Folmar Flex|Folmar/g, 'Dostawca folii'],
  [/Termoform Wola Sp\. z o\.o\.|Termoform Wola|Termoform/g, 'Dostawca wyprasek'],
  [/Etykiety Narew Druk Sp\. j\.|Narew Druk|Narew/g, 'Dostawca etykiet'],
  [/Taśmy Bugaj s\.c\.|Taśmy Bugaj|Bugaj/g, 'Dostawca taśm'],
  [/Palety Serock Eko Sp\. z o\.o\.|Palety Serock/g, 'Dostawca palet'],
  [/Stretch-Pol Mazowsze Sp\. z o\.o\.|Stretch-Pol/g, 'Dostawca folii stretch'],
  [/Hotmelt Serwis Sp\. z o\.o\.|Hotmelt Serwis/g, 'Dostawca klejów'],
  [/Ewa Malinowska/g, 'Specjalistka PPWR'], [/Piotr Lewandowski/g, 'Biuro techniczne'],
  [/Agnieszka Wróbel/g, 'Kontrola jakości'], [/Tomasz Bugajski/g, 'Właściciel'],
  [/Złoty Kłos/g, 'Sieć handlowa'],
  [/city: '[^']*'/g, "city: ''"],
  [/@[a-z]+\.example/g, '@dostawca.example'],
  [/WYPRASKI - 333 C RURKI 150G AUTOMAT RPET BRĄZ/g, 'Wypraska RPET — wafle 150 g'],
  [/FOLIA - RURKA KAKAOWA 150 G PL v4 08\/25r/g, 'Folia flow-pack — wafle kakaowe 150 g v4'],
  [/PUDŁO DISPLAY EKSPOZYCJA WĄSKI SPÓD \(215x215x300\) \(OWSIANE \/ RURKI 150g\) \(FSC\)/g, 'Display ekspozycyjny — spód (FSC)'],
  [/WIEKO - UNIWERSALNE NA DISPLAY EKSPOZYCJA WĄSKI TAGO, ALDI, POLO, ANATOL \(215x215x300\)/g, 'Display ekspozycyjny — wieko uniwersalne'],
  [/ETYKIETY - PAPIER \(NOWA\)/g, 'Etykieta papierowa (nowa)'],
  [/FOLIA - STRETCH ; ręczna 23 mic rozciągliwość 200 % \/ maszynowa 23 mic 250 power/g, 'Folia stretch 23 µm'],
  [/CZAPY \/ PRZEKŁADKI PALETOWE/g, 'Przekładki paletowe'],
  [/Rurka waflowa z kremem kakaowym \(14×150 g\)/g, 'Wafle z kremem kakaowym 150 g'],
  [/\bTAGO\b(?!_)/g, 'Twoja Firma'],
  [/Kardynał\w*/g, 'Herbatniki'],
  [/Symfoni[aięą]/g, 'ERP'],
  [/TWOJA FIRMA, ALDI, POLO, ANATOL|Twoja Firma, ALDI, POLO, ANATOL/g, '4 MARKI'],
  [/ALDI|ANATOL/g, 'MARKA'],
  [/sourceUrl: '[^']*'/g, "sourceUrl: ''"],
  [/0100357-0150/g, 'WG-2100'],
  [/'03211030'/g, "'OP-WYP-0410'"], [/'0308840'/g, "'OP-FOL-0412'"], [/'0302281'/g, "'OP-KAR-0415'"],
  [/'0312033'/g, "'OP-KAR-0416'"], [/'0303070'/g, "'OP-ETK-0418'"], [/'0308041'/g, "'OP-STR-0420'"], [/'0316003'/g, "'OP-PRZ-0421'"],
];
const placeholder = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400"><rect width="400" height="400" fill="#f5f0e7"/><rect x="110" y="130" width="180" height="140" rx="10" fill="#c8a55a"/><rect x="110" y="130" width="180" height="40" rx="10" fill="#0c3b2e"/></svg>`;
const scrub = () => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) { n.nodeValue = n.nodeValue.replace(/[Ss]ymfoni[a-zęą]*/g, 'ERP').replace(/tago\.example/g, 'twojafirma.pl').replace(/\btago\b/gi, 'twojafirma'); } document.querySelectorAll('input,textarea').forEach(i => { i.value = i.value.replace(/[Ss]ymfoni[a-zęą]*/g, 'ERP').replace(/tago/gi, 'twojafirma'); }); };
const logo = `<svg xmlns="http://www.w3.org/2000/svg" width="180" height="82" viewBox="0 0 180 82"><rect x="4" y="17" width="48" height="48" rx="12" fill="#0c3b2e"/><path d="M17 41l8 8 15-17" stroke="#c8a55a" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><text x="62" y="38" font-family="Helvetica Neue,Arial" font-weight="700" font-size="19" fill="#0c3b2e">TWOJA</text><text x="62" y="60" font-family="Helvetica Neue,Arial" font-weight="700" font-size="19" fill="#c8a55a">FIRMA</text></svg>`;

async function neutralize(ctx) {
  await ctx.route('**/*.js', async r => {
    const res = await r.fetch(); let body = await res.text();
    for (const [re, to] of replacements) body = body.replace(re, to);
    r.fulfill({ response: res, body });
  });
  await ctx.route('**/assets/products/**', r => r.fulfill({ contentType: 'image/svg+xml', body: placeholder }));
  await ctx.route('**/assets/tago-logo.png', r => r.fulfill({ contentType: 'image/svg+xml', body: logo }));
  await ctx.route('**/assets/tago-favicon.png', r => r.fulfill({ contentType: 'image/svg+xml', body: logo }));
  // hide the prototype's demo bar and "dane TAGO / przykład" badges, then keep scrubbing text as the app re-renders
  await ctx.addInitScript(`(${scrubLoop.toString()})()`);
}
function scrubLoop() {
  const fix = s => s.replace(/[Ss]ymfoni[a-zęą]*/g, 'ERP').replace(/tago\.example/g, 'twojafirma.pl').replace(/\bTAGO\b/g, 'Twoja Firma').replace(/\btago\b/gi, 'twojafirma').replace(/\?dostawca=[a-z]+/g, '').replace(/Dzień dobry, [A-ZŁŚŻ][a-ząęółśżźćń]+/g, 'Dzień dobry');
  const run = () => {
    if (!document.body) return;
    if (!document.getElementById('neutral-css')) { const st = document.createElement('style'); st.id = 'neutral-css'; st.textContent = '.proto-bar,.om-ex{display:none!important}'; document.head.appendChild(st); }
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
    while ((n = w.nextNode())) { const v = fix(n.nodeValue); if (v !== n.nodeValue) n.nodeValue = v; }
  };
  new MutationObserver(run).observe(document, { childList: true, subtree: true, characterData: true });
  document.addEventListener('DOMContentLoaded', run);
}
const LEAK = /TAGO|tago\.com|Kardyna|Symfoni|ALDI|ANATOL|0100357|Gołęb|RURKA KAKAOWA|RURKI 150|Tekturix|Folmar|Termoform|Narew|Bugaj|Serock|Stretch-Pol|Hotmelt Serwis|Malinowsk|Lewandowsk|Wróbel|Złoty Kłos|Piotr|Ewa |Agnieszk|Tomasz/gi;
module.exports = { neutralize, LEAK };
