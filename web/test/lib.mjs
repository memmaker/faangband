// Playwright helpers for the FAangband web build (RVIP W10, cloud run).
// Serves web/dist with python3 -m http.server, drives Chromium, and keeps a
// text shadow of every term by wrapping Module.fa.text/wipe/clear/pict.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
export const DIST = path.join(here, '..', 'dist');
export const SHOTS = path.join(here, '..', 'shots');

export async function serve(port = 8765) {
  const p = spawn('python3', ['-m', 'http.server', String(port), '-b', '127.0.0.1', '-d', DIST],
    { stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 800));
  return { url: `http://127.0.0.1:${port}/`, stop: () => p.kill() };
}

const SHADOW = () => {
  window.__errors = [];
  window.addEventListener('error', e => window.__errors.push(String(e.message)));
  const iv = setInterval(() => {
    if (!window.Module || !Module.fa || Module.fa.__wrapped) return;
    const fa = Module.fa; fa.__wrapped = true; clearInterval(iv);
    const S = window.__scr = {}; window.__tiles = {};
    const row = (t, y) => { S[t] = S[t] || []; S[t][y] = S[t][y] || []; return S[t][y]; };
    const o = { text: fa.text, wipe: fa.wipe, clear: fa.clear, pict: fa.pict };
    fa.text = function (t, x, y, n, a, s) {
      const H = Module.HEAP32, p = s >> 2, r = row(t, y);
      for (let j = 0; j < n; j++) r[x + j] = String.fromCharCode(H[p + j] || 32);
      return o.text.apply(this, arguments);
    };
    fa.wipe = function (t, x, y, n) { const r = row(t, y); for (let j = 0; j < n; j++) r[x + j] = ' '; return o.wipe.apply(this, arguments); };
    fa.clear = function (t) { S[t] = []; return o.clear.apply(this, arguments); };
    fa.pict = function (t, x, y, n, ap, cp) {
      const H = Module.HEAP32, r = row(t, y);
      for (let j = 0; j < n; j++) {
        const a = H[(ap >> 2) + j], k = H[(cp >> 2) + j];
        r[x + j] = (a & 0x80) && (k & 0x80) ? '█' : String.fromCharCode(k > 32 ? k : 32);
        if ((a & 0x80) && (k & 0x80)) window.__tiles[t] = (window.__tiles[t] || 0) + 1;
      }
      return o.pict.apply(this, arguments);
    };
    window.__screen = t => (S[t || 0] || []).map(r => (r || []).map(c => c || ' ').join('').replace(/\s+$/, '')).join('\n');
  }, 1);
};

export async function open(url, { headless = true, viewport = { width: 1440, height: 900 } } = {}) {
  const browser = await chromium.launch({ headless, executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await browser.newContext({ viewport });
  const page = await ctx.newPage();
  const log = [];
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') log.push(m.type() + ': ' + m.text()); });
  page.on('pageerror', e => log.push('pageerror: ' + e.message));
  await page.addInitScript(SHADOW);
  await page.goto(url);
  return { browser, ctx, page, log };
}

export const screen = (page, t = 0) => page.evaluate(t => window.__screen ? window.__screen(t) : '', t);
export const sleep = ms => new Promise(r => setTimeout(r, ms));

export async function waitFor(page, re, ms = 20000, t = 0) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    const s = await screen(page, t);
    if (re.test(s)) return s;
    await sleep(150);
  }
  throw new Error('timeout waiting for ' + re + '\n' + await screen(page, t));
}

export async function keys(page, seq, delay = 60) {
  for (const k of seq) { await page.keyboard.press(k); await sleep(delay); }
}
