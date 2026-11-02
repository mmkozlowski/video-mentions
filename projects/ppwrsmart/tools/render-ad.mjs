// Renders a PPWR Smart ad from a scene spec (JSON) into MP4 with voice-over.
//   node render-ad.mjs <spec.json> <out.mp4> [--stills t1,t2,...]
// Spec: { format: "16x9"|"9x16", scenes: [...] } — see ads/2026-10-23-youtube/specs/*.json and README there.
// Scene length = max(minD, voice length + 1.0 s), so the cut follows the voice, never the other way round.
// Paths in the spec are relative to the spec file.
import { createRequire } from 'module';
import { spawn, spawnSync, execFileSync } from 'child_process';
import path from 'path';
import fs from 'fs';
import os from 'os';
import { fileURLToPath, pathToFileURL } from 'url';
const require = createRequire(import.meta.url);
const { chromium } = require('/Users/mac/Repo/ppwrsmart-demo/node_modules/playwright');

const toolsDir = path.dirname(fileURLToPath(import.meta.url));
const [specPath, out] = process.argv.slice(2);
const si = process.argv.indexOf('--stills');
const stills = si > 0 ? process.argv[si + 1].split(',').map(Number) : null;
const FPS = 30, VO_DELAY = 0.35, TAIL = 0.75;
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const base = path.dirname(path.resolve(specPath));
const abs = p => path.resolve(base, p);
const probe = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());

const work = fs.mkdtempSync(path.join(os.tmpdir(), 'ppwr-ad-'));
const jobs = [];
for (const [i, s] of spec.scenes.entries()) {
  if (s.vo) { s.voPath = abs(s.vo); s.voLen = probe(s.voPath); }
  s.d = Math.max(s.minD || 4, s.voLen ? s.voLen + VO_DELAY + TAIL : 0);
  if (!s.src) continue;
  const dir = path.join(work, String(i)); fs.mkdirSync(dir);
  const src = abs(s.src);
  if (s.kind === 'still') {
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', src, '-vf', 'scale=1920:-2', '-q:v', '2', path.join(dir, '0001.jpg')]);
    s.srcH = parseInt(execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=height', '-of', 'csv=p=0', path.join(dir, '0001.jpg')]).toString());
  } else if (s.kind === 'rec') {
    jobs.push(new Promise((res, rej) => spawn('ffmpeg', ['-v', 'error', '-y', '-ss', String(s.from), '-to', String(s.to), '-i', src, '-vf', 'fps=30,scale=1920:1080', '-q:v', '2', path.join(dir, '%04d.jpg')], { stdio: 'inherit' }).on('close', c => c ? rej(new Error('ffmpeg rec ' + i)) : res())));
  } else {
    // clip: stretch in time to the scene length (motion interpolation), never in space
    const len = probe(src), k = Math.max(1, s.d / len);
    const vf = (k > 1.02 ? `setpts=${k.toFixed(4)}*PTS,minterpolate=fps=30:mi_mode=mci,` : 'fps=30,') + 'scale=1920:1080:flags=lanczos';
    jobs.push(new Promise((res, rej) => spawn('ffmpeg', ['-v', 'error', '-y', '-i', src, '-vf', vf, '-q:v', '3', path.join(dir, '%04d.jpg')], { stdio: 'inherit' }).on('close', c => c ? rej(new Error('ffmpeg clip ' + i)) : res())));
  }
}
await Promise.all(jobs);
for (const [i, s] of spec.scenes.entries()) if (s.src && s.kind !== 'still') s.frames = fs.readdirSync(path.join(work, String(i))).length;

const F9 = spec.format === '9x16';
const W = F9 ? 1080 : 1920, H = F9 ? 1920 : 1080;
const pageSpec = { format: spec.format, logoInverse: pathToFileURL(path.join(toolsDir, '../assets/brand/lockup-inverse.svg')).href,
  scenes: spec.scenes.map(({ voPath, voLen, vo, src, ...rest }) => rest) };
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: W, height: H } });
await page.goto(pathToFileURL(path.join(toolsDir, 'ad-composer.html')).href + '?frames=' + encodeURIComponent(pathToFileURL(work).href) + '&spec=' + encodeURIComponent(JSON.stringify(pageSpec)));
await page.waitForTimeout(600);
const total = await page.evaluate(() => window.TOTAL);

if (stills) {
  for (const t of stills) { await page.evaluate(t => window.seek(t), t); await page.screenshot({ path: out.replace(/\.mp4$/, `.still-${t}.jpg`), type: 'jpeg', quality: 82 }); }
  await browser.close(); fs.rmSync(work, { recursive: true }); process.exit(0);
}

const silent = out.replace(/\.mp4$/, '.silent.mp4');
const nFrames = Math.ceil(total * FPS);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', silent], { stdio: ['pipe', 'inherit', 'inherit'] });
for (let f = 0; f < nFrames; f++) {
  await page.evaluate(t => window.seek(t), f / FPS);
  const buf = await page.screenshot({ type: 'jpeg', quality: 90 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();

// voice: each line starts VO_DELAY after its scene starts (same timeline as the page: start += d - FADE)
let t0 = 0; const vo = [];
for (const s of spec.scenes) { if (s.voPath) vo.push({ file: s.voPath, at: t0 + VO_DELAY }); t0 += s.d - 0.5; }
const args = ['-y', '-loglevel', 'error', '-i', silent];
vo.forEach(v => args.push('-i', v.file));
const filt = vo.map((v, i) => `[${i + 1}:a]adelay=${Math.round(v.at * 1000)}|${Math.round(v.at * 1000)}[a${i}]`).join(';') +
  ';' + vo.map((_, i) => `[a${i}]`).join('') + `amix=inputs=${vo.length}:normalize=0,loudnorm=I=-16:TP=-1.5[aout]`;
args.push('-filter_complex', filt, '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-t', String(total), '-movflags', '+faststart', out);
const r = spawnSync('ffmpeg', args, { stdio: 'inherit' });
if (r.status) process.exit(r.status);
fs.unlinkSync(silent);
fs.rmSync(work, { recursive: true });
console.log(`done: ${out} (${total.toFixed(1)} s)`);
