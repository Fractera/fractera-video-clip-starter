// Deterministic renderer: drives window.renderAt(t) in headless Chrome (WebGL via SwiftShader)
// and pipes JPEG frames straight into ffmpeg (no PNG per frame on disk).
//   node render.mjs frames 0.6 2.6 5.8            → frames/t*.jpg (look before a full render)
//   node render.mjs video <t0> <t1> <out.mp4> [fps] → frames [t0*fps, t1*fps) into one mp4
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import fs from 'node:fs';
import path from 'node:path';
// Playwright: from engine/node_modules if installed (npm i --no-save playwright), else the sandbox's global copy.
const { chromium } = await import('playwright')
  .catch(() => import(process.env.PLAYWRIGHT_MJS || '/opt/npm-tools/node_modules/playwright/index.mjs'));

const ROOT = path.dirname(new URL(import.meta.url).pathname);
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg' };
const [mode, ...args] = process.argv.slice(2);

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('[page]', m.type(), m.text().slice(0, 300)); });
page.on('pageerror', e => console.log('[pageerror]', e.message));
await page.route('http://local/**', async route => {
  const p = path.join(ROOT, decodeURIComponent(new URL(route.request().url()).pathname));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) return route.fulfill({ status: 404, body: 'not found' });
  return route.fulfill({ status: 200, contentType: TYPES[path.extname(p)] || 'application/octet-stream', body: fs.readFileSync(p) });
});
await page.goto('http://local/index.html');
await page.waitForFunction(() => window.__ready === true || !!window.__error, null, { timeout: 300000 });
const err = await page.evaluate(() => window.__error);
if (err) { console.error('INIT ERROR\n' + err); await browser.close(); process.exit(1); }

if (mode === 'frames') {
  fs.mkdirSync(path.join(ROOT, 'frames'), { recursive: true });
  for (const s of args) {
    const t = Number(s), t0 = Date.now();
    await page.evaluate(x => window.renderAt(x), t);
    await page.screenshot({ path: path.join(ROOT, 'frames', `t${t.toFixed(2)}.jpg`), type: 'jpeg', quality: 92 });
    console.log('frame', t, Date.now() - t0, 'ms');
  }
} else if (mode === 'video') {
  const [startS, endS, out, fpsS = '30'] = args;
  const fps = Number(fpsS), f0 = Math.round(Number(startS) * fps), f1 = Math.round(Number(endS) * fps);
  const tmp = out.replace(/\.mp4$/, '.tmp.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(fps), tmp], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    await page.evaluate(x => window.renderAt(x), f / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await once(ff.stdin, 'drain');
    if ((f - f0) % 30 === 0) console.log('frame', f, ((Date.now() - t0) / (f - f0 + 1)).toFixed(0), 'ms/frame');
  }
  ff.stdin.end();
  const [code] = await once(ff, 'exit');
  if (code === 0) fs.renameSync(tmp, out);
  console.log('done', out, 'exit', code, ((Date.now() - t0) / 1000).toFixed(1), 's');
}
await browser.close();
