// Stage 4: Shockbolt tiles on the map: count tile cells vs text cells
// (text in the map area = unmapped entry), sample canvas pixels, shots.
import { serve, open, screen, sleep } from './lib.mjs';
import { birth } from './birth.mjs';
const world = process.argv[2] || 'a';
const srv = await serve(8770);
const { browser, page, log } = await open(srv.url);
await birth(page, world);
const k = async (key, w = 600) => { await page.keyboard.press(key); await sleep(w); };
async function census(tag) {
  const s = (await screen(page)).split('\n');
  let tile = 0, text = {}, n = 0;
  for (let y = 1; y < s.length - 1; y++) for (let x = 13; x < s[y].length; x++) {
    const c = s[y][x]; if (c === '█') tile++; else if (c !== ' ') { text[c] = (text[c] || 0) + 1; n++; }
  }
  // nearest-neighbour + non-black check on the main canvas
  const px = await page.evaluate(() => {
    const cv = document.querySelector('canvas'); const c = cv.getContext('2d');
    const d = c.getImageData(0, 0, cv.width, cv.height).data; let lit = 0;
    for (let i = 0; i < d.length; i += 4 * 97) if (d[i] + d[i + 1] + d[i + 2] > 60) lit++;
    return { w: cv.width, h: cv.height, smooth: c.imageSmoothingEnabled, lit };
  });
  console.log(`[${tag}] tile cells ${tile}, text cells ${n}`, JSON.stringify(text), JSON.stringify(px));
  await page.screenshot({ path: `shots/stage4-${tag}.png` });
}
await k('Escape', 300);
await census(world + '-start');
if (world === 'a') {
  for (let i = 0; i < 3; i++) await k('>', 3000);    // walk to a path, next wilderness level
  await census('a-wild');
} else {
  await k('>', 4000); await census('d-dl1');
  // debug: jump to DL 15, detect + map, wizard light
  for (const key of ['Control+a', 'j']) await k(key, 500);
  await page.keyboard.type('15'); await k('Enter', 3000);
  if (/sure/i.test(await screen(page))) await k('y', 2000);
  for (const key of ['Control+a', 'w']) await k(key, 800);
  for (const key of ['Control+a', 'd']) await k(key, 800);
  await k('Escape', 400);
  await census('d-dl15');
}
console.log('errors:', JSON.stringify(await page.evaluate(() => window.__errors)), log.filter(l => !/404/.test(l)).join('\n'));
await browser.close(); srv.stop();
