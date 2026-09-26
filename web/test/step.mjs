// node test/step.mjs "key1 key2 ..." : fresh browser, send keys, print screen
import { serve, open, screen, sleep, waitFor, keys } from './lib.mjs';
const srv = await serve(8766);
const { browser, page, log } = await open(srv.url);
page.on('response', r => { if (r.status() >= 400) log.push('HTTP ' + r.status() + ' ' + r.url()); });
await waitFor(page, /Press any key/);
for (const k of (process.argv[2] || '').split(' ').filter(Boolean)) {
  if (k.startsWith('wait')) { await sleep(+k.slice(4) || 1000); continue; }
  await page.keyboard.press(k); await sleep(250);
}
await sleep(1000);
console.log(await screen(page));
await page.screenshot({ path: 'shots/step.png' });
console.log(log.join('\n'));
await browser.close(); srv.stop();
