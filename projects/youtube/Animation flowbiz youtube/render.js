/* render.js — frame-perfect MP4 renderer for the flowbiz scenes (Open Mercato cut).
 *
 * What it does:
 *   1. Launches headless Chromium at 1920×1080 via Playwright.
 *   2. For each scene HTML, pauses the GSAP timeline, then steps it
 *      frame-by-frame (default 60fps) and screenshots each frame to PNG.
 *   3. Pipes the PNG sequence through ffmpeg into an H.264 MP4
 *      (yuv420p, CRF 16) — pixel-perfect, no display capture needed.
 *   4. Concatenates the per-scene MPS into one final MP4 with optional
 *      flash-through-white transitions between them (xfade filter).
 *
 * Usage:
 *   node render.js                   # render every scene + final concat
 *   node render.js s01-pol-roku      # render a single scene
 *   FPS=30 node render.js            # override framerate
 *   KEEP_FRAMES=1 node render.js     # keep PNG frame folders
 *   NO_FLASH=1 node render.js        # skip white-flash transition, hard cut
 */

const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const FPS = parseInt(process.env.FPS || '60', 10);
const W = 1920;
const H = 1080;
const ROOT = __dirname;
const OUT = path.join(ROOT, 'out');
const FRAMES = path.join(OUT, 'frames');
const FLASH_DURATION = 0.2;
// Chromakey background — domyślnie WŁĄCZONY (broadcast green #00B140).
// Wyłącz: NO_CHROMA=1 node render.js   → ciemne tło #0A0A08 (jak w przeglądarce).
// Inny kolor: CHROMA=greenpure|blue|magenta|%23FF1493 node render.js
// ALPHA=1 → render z prawdziwym kanalem alfa (ProRes 4444 .mov), bez green screena.
// To jest tryb PREFEROWANY do montazu: nie ma keyowania, wiec nie ma zielonej
// obwodki na antyaliasowanych krawedziach liter. Green zostaje dla narzedzi,
// ktore alfy nie przyjmuja.
const ALPHA = process.env.ALPHA === '1';
// Domyslny kodek alfy: qtrle (QuickTime Animation) — bezstratny, ~9x mniejszy
// niz ProRes 4444 na plaskiej grafice (11 MB vs 106 MB na karcie tytulowej),
// czytany natywnie przez QuickTime, Final Cut i CapCut na macOS.
// ALPHA_CODEC=prores → ProRes 4444, gdy narzedzie docelowe nie przyjmuje qtrle.
const ALPHA_CODEC = process.env.ALPHA_CODEC || 'qtrle';
const CHROMA = ALPHA ? null : (process.env.NO_CHROMA === '1'
  ? null
  : (process.env.CHROMA || (process.env.GREENSCREEN === '0' ? null : 'green')));
const OUT_NAME = CHROMA ? 'open-mercato-chromakey.mp4' : 'open-mercato.mp4';

// Scene list is now AUTO-DISCOVERED from compositions/*.html (alphabetical order).
// Duration is read from window.__sceneTimeline.duration() after the page loads
// — every scene exposes that handle, regardless of whether it uses scene-shell.js
// or has its own inline chrome.
//
// You don't need to edit this list when adding/removing scenes — just drop the
// .html file into compositions/ and it gets picked up.
function discoverScenes() {
  const dir = path.join(ROOT, 'compositions');
  return fs.readdirSync(dir)
    .filter(f => f.endsWith('.html'))
    .sort()
    .map(f => f.replace(/\.html$/, ''));
}

function ensureDir(p) { fs.mkdirSync(p, { recursive: true }); }
function rmrf(p) { fs.rmSync(p, { recursive: true, force: true }); }

async function renderScene(browser, id) {
  const qs = ['native=1'];
  if (CHROMA) qs.push('bg=' + encodeURIComponent(CHROMA));
  const url = 'file://' + path.join(ROOT, 'compositions', `${id}.html`) + '?' + qs.join('&');
  const suffix = ALPHA ? '_alpha' : (CHROMA ? '_chroma' : '');
  const frameDir = path.join(FRAMES, id + suffix);
  ensureDir(frameDir);

  const ctx = await browser.newContext({
    viewport: { width: W, height: H },
    deviceScaleFactor: 1,
    reducedMotion: 'no-preference',
  });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });

  // Wait for fonts + GSAP timeline to be attached.
  await page.waitForFunction(() => !!window.__sceneTimeline && document.fonts.status === 'loaded');

  // Read duration directly from the GSAP timeline.
  const duration = await page.evaluate(() => {
    // Prefer the explicit __sceneDuration set by flowbizScene.init — it's
    // the intended cut-point. tl.duration() can be Infinity when the
    // timeline contains a repeat:-1 tween (continuous pulse/loop).
    if (typeof window.__sceneDuration === 'number' && isFinite(window.__sceneDuration)) {
      return window.__sceneDuration;
    }
    const d = window.__sceneTimeline.duration();
    if (!isFinite(d)) {
      throw new Error('Timeline duration is Infinity (repeat:-1 tween) and __sceneDuration is not set. Add duration to flowbizScene.init().');
    }
    return d;
  });
  const totalFrames = Math.round(duration * FPS);

  console.log(`\n▶ ${id}  —  ${duration.toFixed(2)}s · ${totalFrames} frames @ ${FPS}fps`);

  // Force the native 1:1 layout (no transform scale), strip all chrome,
  // and pause the timeline.
  await page.evaluate((isAlpha) => {
    document.body.classList.add('native');
    document.body.classList.add('export');

    // Tryb alfa: zdejmujemy tlo sceny i dekoracje tla, zeby PNG mial realna
    // przezroczystosc. Plate'ow chromakeya tu NIE chcemy — istnieja wylacznie
    // po to, zeby tekst przetrwal wycinanie zieleni; przy alfie robia brzydkie
    // czarne prostokaty na materiale.
    if (isAlpha) {
      const a = document.createElement('style');
      a.textContent = `
        html, body, .wrap, .stage { background: transparent !important; }
        .grid, .rays, .watermark, .vignette { display: none !important; }
        .chroma-plate { background: transparent !important; box-shadow: none !important; }
      `;
      document.head.appendChild(a);
    }
    // Belt-and-suspenders: nuke the player bar + "Build with Matt · …" header.
    const css = `
      .controls, .corner-brand { display: none !important; }
      /* .watermark { display: none !important; }   ← uncomment to hide watermark */
    `;
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);

    if (typeof window.fit === 'function') window.fit();
    const tl = window.__sceneTimeline;
    tl.pause(0);
  }, ALPHA);

  // Step through frames, scrubbing the timeline deterministically.
  for (let f = 0; f < totalFrames; f++) {
    const t = f / FPS;
    await page.evaluate((t) => {
      const tl = window.__sceneTimeline;
      const dur = tl.duration();
      tl.time(Math.min(t, dur), false);
    }, t);

    await page.waitForTimeout(0);
    const name = String(f).padStart(5, '0') + '.png';
    await page.screenshot({
      path: path.join(frameDir, name),
      clip: { x: 0, y: 0, width: W, height: H },
      omitBackground: ALPHA,
    });

    if (f % 30 === 0) process.stdout.write(`\r  frame ${f}/${totalFrames}`);
  }
  process.stdout.write(`\r  frame ${totalFrames}/${totalFrames}\n`);

  await ctx.close();

  // Grupowanie po odcinku: eNN-* → out/eNN/, reszta → out/
  const epMatch = id.match(/^(e\d{2})-/);
  const epDir = epMatch ? path.join(OUT, epMatch[1]) : OUT;
  ensureDir(epDir);
  const ext = ALPHA ? 'mov' : 'mp4';
  await encode(frameDir, path.join(epDir, `${id}${suffix}.${ext}`));
  if (process.env.KEEP_FRAMES !== '1') rmrf(frameDir);

  return { id, duration };
}

function encode(frameDir, outFile) {
  return new Promise((resolve, reject) => {
    console.log(`  ↳ ffmpeg → ${path.basename(outFile)}`);
    const alphaArgs = ALPHA_CODEC === 'prores'
      ? ['-c:v', 'prores_ks', '-profile:v', '4444',
         '-pix_fmt', 'yuva444p10le', '-alpha_bits', '16', '-vendor', 'ap4h']
      : ['-c:v', 'qtrle', '-pix_fmt', 'argb'];
    const args = ALPHA
      ? [
          '-y',
          '-framerate', String(FPS),
          '-i', path.join(frameDir, '%05d.png'),
          ...alphaArgs,
          outFile,
        ]
      : [
      '-y',
      '-framerate', String(FPS),
      '-i', path.join(frameDir, '%05d.png'),
      '-c:v', 'libx264',
      '-pix_fmt', 'yuv420p',
      '-preset', 'slow',
      '-crf', '16',
      '-movflags', '+faststart',
      outFile,
    ];
    const ff = spawn('ffmpeg', args, { stdio: ['ignore', 'inherit', 'inherit'] });
    ff.on('exit', code => code === 0 ? resolve() : reject(new Error('ffmpeg exit ' + code)));
  });
}

/* Concat with optional flash-through-white xfade transitions between every pair. */
function concatWithFlash(mp4s, outFile, rendered) {
  return new Promise((resolve, reject) => {
    console.log(`\n▶ concat (xfade=fadewhite) → ${path.basename(outFile)}`);
    const inputs = [];
    mp4s.forEach(f => { inputs.push('-i', f); });

    // Build chained xfade filter:
    //   [0][1]xfade=transition=fadewhite:duration=0.2:offset=<d0-0.2>[v01];
    //   [v01][2]xfade=…:offset=<d0+d1-0.4>[v02]; …
    const parts = [];
    let offset = 0;
    let prev = '[0:v]';
    for (let i = 1; i < mp4s.length; i++) {
      offset += rendered[i-1].duration - FLASH_DURATION;
      const out = (i === mp4s.length - 1) ? '[vout]' : `[v${i}]`;
      parts.push(`${prev}[${i}:v]xfade=transition=fadewhite:duration=${FLASH_DURATION}:offset=${offset.toFixed(3)}${out}`);
      prev = out;
    }
    const filter = parts.join(';');

    const args = [
      '-y',
      ...inputs,
      '-filter_complex', filter,
      '-map', '[vout]',
      '-c:v', 'libx264',
      '-pix_fmt', 'yuv420p',
      '-preset', 'slow',
      '-crf', '16',
      '-movflags', '+faststart',
      outFile,
    ];
    const ff = spawn('ffmpeg', args, { stdio: ['ignore', 'inherit', 'inherit'] });
    ff.on('exit', code => code === 0 ? resolve() : reject(new Error('ffmpeg exit ' + code)));
  });
}

function concatHard(mp4s, outFile) {
  return new Promise((resolve, reject) => {
    const listFile = path.join(OUT, 'concat.txt');
    fs.writeFileSync(listFile, mp4s.map(f => `file '${f}'`).join('\n'));
    console.log(`\n▶ concat (hard cut) → ${path.basename(outFile)}`);
    const args = ['-y','-f','concat','-safe','0','-i',listFile,'-c','copy',outFile];
    const ff = spawn('ffmpeg', args, { stdio: ['ignore', 'inherit', 'inherit'] });
    ff.on('exit', code => {
      fs.unlinkSync(listFile);
      code === 0 ? resolve() : reject(new Error('ffmpeg exit ' + code));
    });
  });
}

(async () => {
  ensureDir(OUT);
  ensureDir(FRAMES);

  const all = discoverScenes();
  const only = process.argv[2];
  const scenes = only ? all.filter(id => id === only) : all;
  if (only && !scenes.length) {
    console.error(`No such scene: ${only}\nKnown: ${all.join(', ')}`);
    process.exit(1);
  }

  console.log(`Discovered ${all.length} scene(s) in compositions/:`);
  all.forEach(id => console.log('  · ' + id));
  if (only) console.log(`\nRendering only: ${only}`);

  const browser = await chromium.launch();
  const rendered = [];
  try {
    for (const id of scenes) {
      const r = await renderScene(browser, id);
      rendered.push(r);
    }
  } finally {
    await browser.close();
  }

  if (!only && rendered.length > 1) {
    const mp4s = rendered.map(r => path.join(OUT, `${r.id}${CHROMA ? '_chroma' : ''}.mp4`));
    const finalFile = path.join(OUT, OUT_NAME);
    if (process.env.NO_FLASH === '1' || CHROMA) {
      // For chromakey output, hard-cut concat is better — the white flash
      // would key out as a hole. Use hard cuts.
      await concatHard(mp4s, finalFile);
    } else {
      await concatWithFlash(mp4s, finalFile, rendered);
    }
  }

  console.log('\n✓ done. Files in ./out/');
})().catch(err => { console.error(err); process.exit(1); });
