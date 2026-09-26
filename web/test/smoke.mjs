import { serve, open, screen, sleep, waitFor, keys } from './lib.mjs';
const srv = await serve();
const { browser, page, log } = await open(srv.url);
await sleep(8000);
console.log(await screen(page));
await page.screenshot({ path: 'shots/smoke.png' });
console.log(log.join('\n'));
await browser.close(); srv.stop();
