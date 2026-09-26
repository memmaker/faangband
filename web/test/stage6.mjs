// Stage 6: sound off by default, no .prf/.cfg fetched, Sound on -> samples
// fetched on game events, Music at depth 0, Help guide, no 404s.
import { serve, open, screen, sleep } from './lib.mjs';
import { birth } from './birth.mjs';
const srv = await serve(8773);
const { browser, page, log } = await open(srv.url);
const reqs = [], bad = [];
page.on('request', r => reqs.push(r.url().replace(srv.url, '')));
page.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url()); });
await birth(page, 'd');
const k = async (key, w = 600) => { await page.keyboard.press(key); await sleep(w); };
await k('Escape', 300);
console.log('buttons:', await page.evaluate(() => [document.getElementById('btn-sound').textContent, document.getElementById('btn-music').textContent]));
await k('>', 3000);
console.log('sound requests while off:', reqs.filter(u => /sounds\/|music\//.test(u)).length);
await page.click('#btn-sound'); await page.click('#btn-music'); await sleep(300);
console.log('buttons:', await page.evaluate(() => [document.getElementById('btn-sound').textContent, document.getElementById('btn-music').textContent]));
await k('<', 4000); await k('>', 4000);                                  // stairs -> events
for (const key of ['R', '&', 'Enter']) await k(key, 400); await sleep(1500);
console.log('sample requests:', [...new Set(reqs.filter(u => /sounds\/|music\//.test(u)))].join(' '));
console.log('prf/cfg fetched:', reqs.filter(u => /\.(prf|cfg)$/.test(u)));
await page.click('#btn-help'); await sleep(1500);
const help = await page.evaluate(() => document.getElementById('help-body').innerText.slice(0, 300));
console.log('help:', help.replace(/\n+/g, ' | '));
await page.screenshot({ path: 'shots/stage6-help.png' });
console.log('bad responses:', bad);
console.log('errors:', JSON.stringify(await page.evaluate(() => window.__errors)), log.filter(l => !/willReadFrequently/.test(l)).join('\n'));
await browser.close(); srv.stop();
