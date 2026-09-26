// Stage 2: stairs walk (> / <) and auto-explore (p).
import { serve, open, screen, sleep } from './lib.mjs';
import { birth } from './birth.mjs';
const srv = await serve(8768);
const { browser, page, log } = await open(srv.url);
await birth(page, process.argv[3] || 'a');
const rows = async () => { const s = (await screen(page)).split('\n'); return { top: (s[0] || '').trim(), bot: (s.filter(l => /\S/.test(l)).pop() || '').trim() }; };
const hist = async () => page.evaluate(() => (window.__screen(1) || '').split('\n').filter(l => /\S/.test(l)).slice(-3).join(' / '));
async function press(k, wait = 2500) {
  await page.keyboard.press(k); await sleep(wait);
  const r = await rows();
  console.log(`[${k}]`, 'msg:', r.top.slice(0, 90), '| status:', r.bot.slice(-60));
}
await press('Escape', 300);
await press('>', 4000);                // walk to the town's down staircase and take it
await page.screenshot({ path: 'shots/stage2-after-down.png' });
let banished = 0;
for (let i = 0; i < +(process.argv[2] || 25); i++) {
  await press('p', 1500);
  if (/confused|afraid|blind/i.test((await rows()).top)) {   // rest it off
    for (const k of ['Escape', 'R', '&', 'Enter']) { await page.keyboard.press(k); await sleep(300); }
    await sleep(2000); console.log('   rested:', (await rows()).top);
  }
  // Debug banish (^A z) when a monster blocks explore, to test exploring itself
  if (/In view/.test((await rows()).top) && banished < 20) {
    banished++;
    for (const k of ['Control+a', 'z']) { await page.keyboard.press(k); await sleep(500); }
    if (/sure/.test((await rows()).top)) { await page.keyboard.press('y'); await sleep(500); }
    console.log('   banish prompt:', (await rows()).top);
    await page.keyboard.press('Enter'); await sleep(400);
    await page.keyboard.press('Escape'); await sleep(300);
  }
}
await page.screenshot({ path: 'shots/stage2-explored.png' });
console.log('messages:', await hist());
await press('<', 5000);                // walk back to a known up staircase
await page.screenshot({ path: 'shots/stage2-after-up.png' });
console.log('errors:', JSON.stringify(await page.evaluate(() => window.__errors)), log.filter(l => !/404/.test(l)).join('\n'));
await browser.close(); srv.stop();
