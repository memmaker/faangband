// Stage 1: character creation, random keys, save, reload, restore.
import { serve, open, screen, sleep, waitFor } from './lib.mjs';
import { birth, reload } from './birth.mjs';
const seed = +(process.argv[2] || 1), N = +(process.argv[3] || 400);
let s = seed; const rnd = n => (s = (s * 1103515245 + 12345) & 0x7fffffff) % n;
const srv = await serve(8767);
const { browser, page, log } = await open(srv.url);
page.on('response', r => { if (r.status() >= 400) log.push('HTTP ' + r.status() + ' ' + r.url()); });
await birth(page);
console.log('birth ok');
const pool = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.<>;:!?/[]{}()=+-*~'.split('')
  .concat(['Enter', 'Escape', 'Escape', 'Escape', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Space', 'Tab']);
const banned = new Set(['Q', 'X']);  // Q = retire (kills the run), ^X handled separately
for (let i = 0; i < N; i++) {
  let k = pool[rnd(pool.length)];
  if (banned.has(k)) k = 'Escape';
  await page.keyboard.press(k); await sleep(20);
  if (i % 100 === 99) { for (let j = 0; j < 4; j++) await page.keyboard.press('Escape'); }
}
for (let j = 0; j < 6; j++) { await page.keyboard.press('Escape'); await sleep(100); }
const dead = /You die|Rest in peace|tombstone/i.test(await screen(page));
const before = (await screen(page)).split('\n').slice(0, 3).join('|');
await page.keyboard.press('Control+s'); await sleep(1500);
console.log('saved:', /Saving game\.\.\. done/.test(await screen(page)) || 'see screen', 'dead:', dead);
const after = await reload(page);
console.log('reloaded:', before, '=>', after.split('\n').slice(0, 3).join('|'));
await page.screenshot({ path: `shots/stage1-reload-${seed}.png` });
const errs = await page.evaluate(() => window.__errors);
console.log('page errors:', JSON.stringify(errs), '\nconsole:', log.filter(l => !/404 \(File/.test(l)).join('\n'));
await browser.close(); srv.stop();
