// Stage 5: windows (content per term), resize, layout after reload, game end.
import { serve, open, screen, sleep, waitFor } from './lib.mjs';
import { birth, reload } from './birth.mjs';
const srv = await serve(8771);
const { browser, page, log } = await open(srv.url);
await birth(page, 'd');
const k = async (key, w = 600) => { await page.keyboard.press(key); await sleep(w); };
await k('Escape', 300);
await k('>', 4000);                                   // DL1: monsters / items lists fill
const names = ['main', 'Messages', 'Inventory', 'Visible monsters', 'Visible items', 'Recall', 'Equipment'];
for (let t = 1; t < 7; t++) {
  const s = (await screen(page, t)).split('\n').filter(l => /\S/.test(l));
  console.log(`term ${t} (${names[t]}): ${s.length} lines | ${s.slice(0, 2).join(' / ').slice(0, 110)}`);
}
// Visible windows and canvas sizes at several viewport sizes
for (const [w, h] of [[1000, 650], [1440, 900], [1200, 750], [760, 500], [1440, 900]]) {
  await page.setViewportSize({ width: w, height: h }); await sleep(900);
  const r = await page.evaluate(() => [...document.querySelectorAll('[id^="t-"]')].filter(e => e.offsetParent)
    .map(e => { const c = e.querySelector('canvas'); return e.id + ':' + (c ? c.width + 'x' + c.height : '-'); }).join(' '));
  console.log(`${w}x${h}: ${r}`);
}
await page.screenshot({ path: 'shots/stage5-windows.png' });
// ^S, reload: character and layout back
await k('Control+s', 1500);
await reload(page); console.log('reloaded:', /LEVEL/.test(await screen(page)));
// Quit: ^X -> overlay, Play again -> character loads
await k('Control+x', 2500);
console.log('^X:', (await screen(page)).split('\n')[0]);
for (let i = 0; i < 6 && await page.evaluate(() => document.getElementById('overlay').hidden); i++) {
  console.log('  end screen:', (await screen(page)).split('\n').filter(l => /\S/.test(l)).slice(0, 2).join(' / ').slice(0, 120)); await k('Escape', 1500); }
let ov = await page.evaluate(() => !document.getElementById('overlay').hidden && document.getElementById('overlay-msg').textContent);
console.log('quit overlay:', JSON.stringify(ov));
await page.screenshot({ path: 'shots/stage5-quit.png' });
await page.click('#btn-restart'); await waitFor(page, /Press any key/); await k('Enter', 1500);
console.log('after play again:', /LEVEL/.test(await screen(page)) ? 'character loaded' : (await screen(page)).slice(0, 200));
// Death: retire (Q y @) is the real death path (tombstone), then the overlay
await k('Escape', 300); await k('Q', 800);
console.log('Q:', (await screen(page)).split('\n')[0]);
await k('y', 800); await k('@', 1500);
for (let i = 0; i < 8; i++) {
  const s = await screen(page);
  ov = await page.evaluate(() => !document.getElementById('overlay').hidden);
  if (ov) break;
  console.log('death screen:', s.split('\n').filter(l => /\S/.test(l)).slice(0, 3).join(' / ').slice(0, 150));
  await k(/want to quit/.test(s) ? 'y' : 'Escape', 1500);
}
ov = await page.evaluate(() => !document.getElementById('overlay').hidden && document.getElementById('overlay-msg').textContent);
console.log('death overlay:', JSON.stringify(ov));
await page.screenshot({ path: 'shots/stage5-death.png' });
if (ov !== false) { await page.click('#btn-restart'); await waitFor(page, /Press any key/); await k('Enter', 1500);
  console.log('after death, play again:', (await screen(page)).split('\n').filter(l => /\S/.test(l)).slice(0, 2).join(' / ')); }
console.log('errors:', JSON.stringify(await page.evaluate(() => window.__errors)), log.filter(l => !/404|willReadFrequently/.test(l)).join('\n'));
await browser.close(); srv.stop();
