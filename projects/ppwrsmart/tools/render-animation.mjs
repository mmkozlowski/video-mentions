// Render animation.html → MP4 z lektorem. Użycie (przez build-video.sh):
//   node render-animation.mjs <framesDir> <out.mp4> [--stills t1,t2,...]
import { createRequire } from 'module';
import { spawn, spawnSync } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath, pathToFileURL } from 'url';
const require = createRequire(import.meta.url);
const { chromium } = require('/Users/mac/Repo/ppwrsmart-demo/node_modules/playwright');

const dir = path.dirname(fileURLToPath(import.meta.url));
const [framesDir, out] = process.argv.slice(2);
const si = process.argv.indexOf('--stills');
const stills = si > 0 ? process.argv[si + 1].split(',').map(Number) : null;
const FPS = 30;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
const frames = pathToFileURL(framesDir).href.replace(/\/?$/, '/');
const counts = Object.fromEntries(fs.readdirSync(framesDir).map(d => [d, fs.readdirSync(path.join(framesDir, d)).length]));
await page.goto(pathToFileURL(path.join(dir, 'animation.html')).href + '?frames=' + encodeURIComponent(frames) + '&counts=' + encodeURIComponent(JSON.stringify(counts)));
await page.waitForTimeout(500);

if (stills) {
  for (const t of stills) { await page.evaluate(t => window.seek(t), t); await page.screenshot({ path: path.join(path.dirname(out), `still-${t}.jpg`), type: 'jpeg', quality: 80 }); }
  await browser.close(); process.exit(0);
}

const total = await page.evaluate(() => window.TOTAL);
const timeline = await page.evaluate(() => window.TIMELINE);
const silent = out.replace(/\.mp4$/, '.silent.mp4');
const nFrames = Math.ceil(total * FPS);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', silent], { stdio: ['pipe', 'inherit', 'inherit'] });
for (let f = 0; f < nFrames; f++) {
  await page.evaluate(t => window.seek(t), f / FPS);
  const buf = await page.screenshot({ type: 'jpeg', quality: 90 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (f % 300 === 0) console.log(`frame ${f}/${nFrames}`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();

// lektor: każda kwestia startuje VO_DELAY po początku swojej sceny
const vo = timeline.filter(s => s.vo);
const args = ['-y', '-loglevel', 'error', '-i', silent];
vo.forEach(s => args.push('-i', path.join(dir, '..', 'assets', 'voice', `${s.vo}.mp3`)));
const filt = vo.map((s, i) => `[${i + 1}:a]adelay=${Math.round(s.voAt * 1000)}|${Math.round(s.voAt * 1000)}[a${i}]`).join(';') +
  ';' + vo.map((_, i) => `[a${i}]`).join('') + `amix=inputs=${vo.length}:normalize=0,loudnorm=I=-16:TP=-1.5[aout]`;
args.push('-filter_complex', filt, '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', String(total), '-movflags', '+faststart', out);
const r = spawnSync('ffmpeg', args, { stdio: 'inherit' });
if (r.status) process.exit(r.status);
fs.unlinkSync(silent);
console.log(`done: ${out} (${total.toFixed(1)} s)`);
