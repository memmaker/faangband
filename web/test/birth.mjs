// Shared birth sequence: Standard Wilderness, Easterling Warrior, defaults.
import { waitFor, sleep } from './lib.mjs';
export async function birth(page) {
  await waitFor(page, /Press any key/);
  for (const k of ['Enter', 'a', 'Enter', 'Enter', 'Enter', 'Enter', 'Enter', 'Enter', 'Enter']) {
    await page.keyboard.press(k); await sleep(300);
  }
  return waitFor(page, /Town|LEVEL/);
}
// Reload and load the saved character
export async function reload(page) {
  await page.reload();
  await waitFor(page, /Press any key/);
  await page.keyboard.press('Enter');
  return waitFor(page, /LEVEL/);
}
