// Stage 3: Enter menu (letters in menus and submenus) and inventory browser.
import { serve, open, screen, sleep, waitFor } from './lib.mjs';
import { birth } from './birth.mjs';
const srv = await serve(8769);
const { browser, page, log } = await open(srv.url);
await birth(page, 'a');
const k = async (key, w = 500) => { await page.keyboard.press(key); await sleep(w); };
const top = async () => ((await screen(page)).split('\n')[0] || '').trim();
const box = async () => (await screen(page)).split('\n').slice(0, 26).join('\n');
await k('Escape', 300);
// Enter menu: top level, then b = Action commands, submenu letter picks explore
await k('Enter');
let s = await box(); console.log('--- Enter menu\n' + s);
if (!/Wizard and debug/.test(s) || /Hidden/.test(s)) throw new Error('groups');
await page.screenshot({ path: 'shots/stage3-menu.png' });
await k('b');
s = await box(); console.log('--- Action commands\n' + s);
await page.screenshot({ path: 'shots/stage3-action.png' });
if (!/Start exploring \(p\)/.test(s)) throw new Error('explore missing');
await k('Escape'); await k('d');                       // Information
s = await box(); if (!/Version info/.test(s)) throw new Error('info'); console.log('--- Information ok');
await k('Escape'); await k('f');                       // Wizard and debug
s = await box(); console.log('--- Wizard\n' + s.split('\n').filter(l => /[a-z]\) /.test(l)).join('\n'));
await k('Escape'); await k('Escape');
// Letter in a submenu runs the command: Enter c (Manage items) b (inventory)
await k('Enter'); await k('c'); await k('b', 800);
s = await box(); console.log('--- inventory via menu\n' + s);
await page.screenshot({ path: 'shots/stage3-inven.png' });
if (!/a\) /.test(s)) throw new Error('inventory not shown');
// Ctrl+letter = inspect, back to the list
await k('Control+a', 800); s = await box(); console.log('--- ctrl-a (inspect)\n' + s.split('\n').slice(0, 6).join('\n'));
await k('Escape', 600); s = await box(); console.log('after inspect, list shown:', /a\) /.test(s));
// Enter = action menu on the cursor item
await k('Enter', 800); s = await box(); console.log('--- action menu\n' + s.split('\n').slice(0, 14).join('\n'));
await page.screenshot({ path: 'shots/stage3-objmenu.png' });
await k('Escape', 500); await k('Escape', 500);
// letter = main action: find a potion/food/scroll letter in the inventory
await k('i', 800); s = await screen(page);
const m = s.match(/([a-z])\) [^\n]*(Potion|Ration|Scroll|Flask|Torch|Cure)/);
console.log('main-action item:', m && m[0]);
if (m) { await k(m[1], 1500); console.log('after letter:', await top()); s = await box(); console.log('reopened:', /Select Item|a\) /.test(s)); }
await page.screenshot({ path: 'shots/stage3-after-use.png' });
await k('Escape'); await k('Escape');
// Shift+letter = drop
await k('i', 800); await k('Shift+A', 800); console.log('shift-a:', await top());
await k('Enter', 1000); console.log('after drop:', await top());
await page.screenshot({ path: 'shots/stage3-drop.png' });
console.log('errors:', JSON.stringify(await page.evaluate(() => window.__errors)), log.filter(l => !/404/.test(l)).join('\n'));
await browser.close(); srv.stop();
