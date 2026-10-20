// Nagrywa prawdziwą pracę w prototypie TAGO revision-003: dwa okna obok siebie (TAGO + portal Folmar Flex),
// kursor i kliknięcia. Wynik: tago-revision-003-dwa-okna.webm (Playwright recordVideo) + markers.json (czasy scen).
// Wymaga serwera: python3 -m http.server 8099 w katalogu revision-003.
const { chromium } = require('/Users/mac/Repo/ppwrsmart-demo/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const OUT = process.argv[2] || path.join(__dirname, '..', 'assets', 'recordings');
const BASE = 'http://127.0.0.1:8099/index.html';
const DZIS = '2026-10-21';
const url = (q = '', hash = '') => BASE + '?' + (q ? q + '&' : '') + 'dzis=' + DZIS + hash;

const SPLIT = `<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0;padding:0}
body{width:1920px;height:1080px;background:#0c3b2e;font-family:"Helvetica Neue",Arial,sans-serif;overflow:hidden}
.pane{position:absolute;top:0;height:1080px;transition:none}
.lbl{height:54px;display:flex;align-items:center;gap:12px;padding-left:18px;color:#f5f0e7;font-size:22px;font-weight:700;letter-spacing:.5px}
.lbl i{width:12px;height:12px;border-radius:50%;background:#c8a55a;display:block}
iframe{border:0;background:#fff;border-radius:10px 10px 0 0;display:block}
#cur{position:absolute;left:960px;top:540px;width:34px;height:34px;z-index:10;pointer-events:none;transform:translate(-4px,-2px)}
.ripple{position:absolute;z-index:9;width:20px;height:20px;border-radius:50%;border:4px solid #c8a55a;pointer-events:none;transform:translate(-50%,-50%);animation:r .6s ease-out forwards}
@keyframes r{to{width:80px;height:80px;opacity:0}}
#cover{position:absolute;inset:0;background:#0c3b2e;z-index:20;pointer-events:none}
</style></head><body>
<div class="pane" id="pa" style="left:16px;width:936px"><div class="lbl"><i></i><span id="la">Okno TAGO · specjalistka PPWR</span></div><iframe id="fa" style="width:936px;height:1026px"></iframe></div>
<div class="pane" id="pb" style="left:968px;width:936px"><div class="lbl"><i></i><span>Okno dostawcy · Folmar Flex</span></div><iframe id="fb" style="width:936px;height:1026px"></iframe></div>
<svg id="cur" viewBox="0 0 24 24"><path d="M3 2l7.5 19 2.6-7.7L21 10.7z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>
<div id="cover"></div>
<script>
window.moveCursor=(x,y,ms)=>new Promise(res=>{const c=document.getElementById('cur');const x0=parseFloat(c.style.left)||960,y0=parseFloat(c.style.top)||540;const t0=performance.now();
 (function f(){const p=Math.min(1,(performance.now()-t0)/ms);const e=p<.5?2*p*p:1-Math.pow(-2*p+2,2)/2;c.style.left=(x0+(x-x0)*e)+'px';c.style.top=(y0+(y-y0)*e)+'px';p<1?requestAnimationFrame(f):res()})()});
window.ripple=(x,y)=>{const r=document.createElement('div');r.className='ripple';r.style.left=x+'px';r.style.top=y+'px';document.body.appendChild(r);setTimeout(()=>r.remove(),700)};
</script></body></html>`;

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, recordVideo: { dir: path.join(OUT, '_rec'), size: { width: 1920, height: 1080 } } });
  await ctx.route('http://127.0.0.1:8099/__split.html', r => r.fulfill({ contentType: 'text/html', body: SPLIT }));
  const page = await ctx.newPage();
  const t0 = Date.now();
  const markers = {};
  const mark = (k) => { markers[k] = (Date.now() - t0) / 1000; console.log('mark', k, markers[k]); };
  await page.goto('http://127.0.0.1:8099/__split.html');
  const frames = {};
  const fa = () => frames.fa;
  const fb = () => frames.fb;
  const setSrc = async (id, u) => { await page.evaluate(([id, u]) => { document.getElementById(id).src = u; }, [id, u]); await page.waitForTimeout(900); frames[id] = await (await page.$('#' + id)).contentFrame(); };
  const go = async (frame, hash) => { await frame.evaluate(h => { location.hash = h; }, hash); await page.waitForTimeout(350); };
  const sleep = ms => page.waitForTimeout(ms);
  const click = async (frame, sel, { move = 750, after = 500 } = {}) => {
    const loc = frame.locator(sel).first();
    await loc.scrollIntoViewIfNeeded();
    const b = await loc.boundingBox();
    const x = b.x + Math.min(b.width / 2, 60), y = b.y + b.height / 2;
    await page.evaluate(([x, y, ms]) => window.moveCursor(x, y, ms), [x, y, move]);
    await sleep(120);
    await page.evaluate(([x, y]) => window.ripple(x, y), [x, y]);
    await loc.click();
    await sleep(after);
  };
  const type = async (frame, sel, text) => { await click(frame, sel, { after: 200 }); for (const ch of text) { await frame.locator(sel).first().press(ch === ' ' ? 'Space' : ch).catch(() => frame.locator(sel).first().type(ch)); await sleep(55); } };

  // --- przygotowanie stanu (pod zasłoną): reset, wypraska i taśma już zaakceptowane, brakuje tylko folii Folmar
  await setSrc('fa', url());
  let A = fa();
  await A.click('[data-act="reset"]'); await sleep(400);
  await go(A, '#/components/K-102'); await A.click('.om-acts button:has-text("Akceptuj")'); await sleep(300);
  await setSrc('fb', url('dostawca=bugaj'));
  let B = fb();
  await B.fill('#pass1', 'tasmy-2026'); await B.fill('#pass2', 'tasmy-2026'); await B.click('button[type=submit]'); await sleep(300);
  await B.click('a:has-text("Taśma pakowa PP z logo TAGO")'); await sleep(200);
  await B.click('button:has-text("Wypełnij danymi przykładowymi")'); await B.click('button[type=submit]'); await sleep(300);
  await go(A, '#/components/K-111'); await A.click('.om-acts button:has-text("Akceptuj")'); await sleep(300);
  await setSrc('fb', url('dostawca=folmar'));
  B = fb();
  if (await B.locator('#pass1').count()) { await B.fill('#pass1', 'folie-2026'); await B.fill('#pass2', 'folie-2026'); }
  await B.click('button[type=submit]').catch(() => {}); await sleep(300);
  await go(A, '#/products/WG-2031'); await sleep(500);
  await page.evaluate(() => { document.getElementById('cover').style.display = 'none'; });
  await sleep(300);

  // --- scena 1: wyrób zablokowany → przypomnienie
  mark('blocked');
  await sleep(1800);
  await click(A, 'button:has-text("Przypomnij dostawcom")', { move: 900, after: 700 });
  mark('reminder');
  await click(A, '.modal button:has-text("Wyślij")', { after: 1800 });
  // --- scena 2: dostawca uzupełnia
  mark('supplier');
  await click(B, 'a:has-text("Folia flow-pack OPP 30 µm")', { move: 900, after: 700 });
  await click(B, 'button:has-text("Wypełnij danymi przykładowymi")', { after: 900 });
  await type(B, '#f-comment', 'Nowa specyfikacja folii');
  await sleep(400);
  await click(B, 'button[type=submit]', { after: 1500 });
  // --- scena 3: TAGO weryfikuje i akceptuje → wyrób odblokowany
  mark('review');
  await click(A, 'a[href="#/review"]', { move: 900, after: 1200 });
  await click(A, '.om-tbl a:has-text("Folia flow-pack OPP 30 µm")', { after: 1000 });
  await click(A, '.om-acts button:has-text("Akceptuj")', { after: 1500 });
  mark('unblocked');
  await go(A, '#/products/WG-2031'); await sleep(2800);
  mark('end-split');
  // --- scena 4: pełny ekran TAGO — nowa wersja deklaracji
  await page.evaluate(() => { const pb = document.getElementById('pb'); pb.style.display = 'none'; const pa = document.getElementById('pa'); pa.style.width = '1888px'; document.getElementById('fa').style.width = '1888px'; });
  await go(A, '#/declarations/group/' + encodeURIComponent('tekturix~PAP20~440g~n')); await sleep(400);
  mark('version');
  await sleep(1500);
  await click(A, 'button:has-text("Wystaw wersję")', { move: 900, after: 2200 });
  // --- scena 5: raport tygodniowy
  mark('report');
  await go(A, '#/board-report'); await sleep(3500);
  mark('end');
  const video = page.video();
  await ctx.close();
  await browser.close();
  const vp = await video.path();
  fs.renameSync(vp, path.join(OUT, 'tago-revision-003-dwa-okna.webm'));
  fs.writeFileSync(path.join(OUT, 'markers.json'), JSON.stringify(markers, null, 2));
  console.log('ok', markers);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
