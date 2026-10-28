// Screenshots of the TAGO prototype with client identity stripped (for public PPWR Smart ads).
const { chromium } = require('/Users/mac/Repo/ppwrsmart-demo/node_modules/playwright');
const out = process.argv[2];
const BASE = 'http://127.0.0.1:8099/';
const { neutralize, LEAK } = require('./neutralize-prototype.cjs');
const scrub = () => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) { n.nodeValue = n.nodeValue.replace(/[Ss]ymfoni[a-zęą]*/g, 'ERP').replace(/tago\.example/g, 'twojafirma.pl').replace(/\btago\b/gi, 'twojafirma'); } document.querySelectorAll('input,textarea').forEach(i => { i.value = i.value.replace(/[Ss]ymfoni[a-zęą]*/g, 'ERP').replace(/tago/gi, 'twojafirma'); }); };
const logo = `<svg xmlns="http://www.w3.org/2000/svg" width="180" height="82" viewBox="0 0 180 82"><rect x="4" y="17" width="48" height="48" rx="12" fill="#0c3b2e"/><path d="M17 41l8 8 15-17" stroke="#c8a55a" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><text x="62" y="38" font-family="Helvetica Neue,Arial" font-weight="700" font-size="19" fill="#0c3b2e">TWOJA</text><text x="62" y="60" font-family="Helvetica Neue,Arial" font-weight="700" font-size="19" fill="#c8a55a">FIRMA</text></svg>`;
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1.2 });
  await neutralize(ctx);
  const pg = await ctx.newPage();
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  const leaks = [];
  const shots = [
    ['01-pulpit', '?#/dashboard'], ['02-wyrob-blokada', '?#/products/WG-2031'], ['03-do-weryfikacji', '?#/review'],
    ['04-deklaracje', '?#/declarations'], ['05-regula', '?#/rules'], ['06-import-erp', '?#/import'],
    ['08-wyrob-lista', '?#/products'],
  ];
  for (const [n, h] of shots) {
    await pg.goto(BASE + 'index.html' + h); await pg.waitForTimeout(1200);
    await pg.addStyleTag({ content: '.proto-bar,.om-ex{display:none!important}' });
    await pg.evaluate(scrub); await pg.waitForTimeout(200);
    const txt = await pg.evaluate(() => document.body.innerText);
    const hit = txt.match(LEAK);
    if (hit) leaks.push(n + ': ' + [...new Set(hit)].join(','));
    await pg.screenshot({ path: `${out}/${n}.png` });
  }
  // a declaration detail: click first link to a declaration version
  await pg.goto(BASE + 'index.html?#/declarations'); await pg.waitForTimeout(1000);
  const link = await pg.$('a[href^="#/declarations/group/"]');
  if (link) { await link.click(); await pg.waitForTimeout(1000); await pg.addStyleTag({ content: '.proto-bar,.om-ex{display:none!important}' }); await pg.evaluate(scrub);
    const txt = await pg.evaluate(() => document.body.innerText); const hit = txt.match(/TAGO|Kardyna|Symfoni|ALDI|0100357/gi); if (hit) leaks.push('09: ' + [...new Set(hit)]);
    await pg.screenshot({ path: `${out}/09-deklaracja-grupa.png` }); }
  await pg.goto(BASE + 'index.html?#/declarations'); await pg.waitForTimeout(900);
  await pg.evaluate(() => { const t = [...document.querySelectorAll('[role=tab],button,a')].find(e => /Rejestr wersji/.test(e.textContent)); if (t) t.click(); });
  await pg.waitForTimeout(700);
  const href = await pg.evaluate(() => { const r = document.querySelector('[data-href^="#/declarations/v/"]'); return r && r.getAttribute('data-href'); });
  if (href) { await pg.goto(BASE + 'index.html?' + href); await pg.waitForTimeout(1200); await pg.addStyleTag({ content: '.proto-bar,.om-ex{display:none!important}' }); await pg.evaluate(scrub);
    const txt = await pg.evaluate(() => document.body.innerText); const hit = txt.match(LEAK); if (hit) leaks.push('10: ' + [...new Set(hit)]);
    await pg.screenshot({ path: `${out}/10-deklaracja-dokument.png` }); } else leaks.push('no version link');
  const pg2 = await ctx.newPage(); await pg2.goto(BASE + 'index.html?dostawca=folmar#/portal'); await pg2.waitForTimeout(1200);
  await pg2.addStyleTag({ content: '.proto-bar,.om-ex{display:none!important}' }); await pg2.evaluate(scrub);
  { const txt = await pg2.evaluate(() => document.body.innerText); const hit = txt.match(LEAK); if (hit) leaks.push('07: ' + [...new Set(hit)]); }
  await pg2.screenshot({ path: `${out}/07-portal-dostawcy.png` });
  console.log('errors:', JSON.stringify(errs)); console.log('leaks:', JSON.stringify(leaks)); await b.close();
})();
