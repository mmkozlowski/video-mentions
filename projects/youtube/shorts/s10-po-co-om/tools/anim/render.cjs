/* Renderer pionowych plansz 1080×1920 — uproszczony wariant render.js
 * z „Animation flowbiz youtube": Playwright kroczy po osi GSAP klatka po
 * klatce i zrzuca PNG prosto w stdin ffmpeg (bez folderu klatek).
 *
 * Playwright nie jest instalowany w tym projekcie — bierzemy moduł z
 * ~/.claude/tools/flowbiz-docgen (chromium siedzi we wspólnym cache
 * ~/Library/Caches/ms-playwright).
 *
 *   node render.cjs kopie-9x16 dostep-9x16     # → build/anim/<name>.mp4
 */
const { chromium } = require('/Users/mac/.claude/tools/flowbiz-docgen/node_modules/playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const FPS = 30;
const W = 1080, H = 1920;
const HERE = __dirname;
const OUT = path.join(HERE, '..', '..', 'build', 'anim');

async function renderScene(browser, id) {
  const url = 'file://' + path.join(HERE, `${id}.html`);
  const ctx = await browser.newContext({
    viewport: { width: W, height: H },
    deviceScaleFactor: 1,
  });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForFunction(
    () => !!window.__sceneTimeline && document.fonts.status === 'loaded');

  const duration = await page.evaluate(() => window.__sceneDuration);
  const totalFrames = Math.round(duration * FPS);
  const outFile = path.join(OUT, `${id}.mp4`);
  console.log(`▶ ${id} — ${duration.toFixed(2)}s · ${totalFrames} klatek`);

  const ff = spawn('ffmpeg', [
    '-y', '-hide_banner', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
    '-pix_fmt', 'yuv420p', '-r', String(FPS), outFile,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });

  for (let f = 0; f < totalFrames; f++) {
    await page.evaluate((t) => {
      const tl = window.__sceneTimeline;
      tl.time(Math.min(t, tl.duration()), false);
    }, f / FPS);
    const png = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(png)) {
      await new Promise((res) => ff.stdin.once('drain', res));
    }
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close',
    (c) => (c === 0 ? res() : rej(new Error(`ffmpeg exit ${c}`)))));
  await ctx.close();
  console.log(`  → ${outFile}`);
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const ids = process.argv.slice(2);
  if (!ids.length) throw new Error('podaj nazwy kompozycji');
  const browser = await chromium.launch();
  for (const id of ids) await renderScene(browser, id);
  await browser.close();
})();
