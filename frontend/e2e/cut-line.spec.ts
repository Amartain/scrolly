import { expect, test } from './fixtures';
import { begin } from './helpers';

// Ctrl+X with nothing selected cuts the whole line, as in VS Code (brain dump and Bamboo Scraps).

async function dumpWith(page: import('@playwright/test').Page, text: string, caret: number) {
  await begin(page);
  const dump = page.locator('#dump');
  await dump.fill(text);
  await dump.evaluate((el, at) => (el as HTMLTextAreaElement).setSelectionRange(at, at), caret);
  return dump;
}

test('Ctrl+X cuts the line the caret is on, and Ctrl+Z brings it back', async ({ page }) => {
  const dump = await dumpWith(page, 'one\ntwo\nthree', 5);
  await page.keyboard.press('Control+x');
  await expect(dump).toHaveValue('one\nthree');
  // The draft is saved like any other edit.
  await expect
    .poll(async () => (await (await page.request.get('/api/view')).json()).planning.text)
    .toBe('one\nthree');
  await page.keyboard.press('Control+z');
  await expect(dump).toHaveValue('one\ntwo\nthree');
});

test('cutting from the bottom leaves no blank line behind', async ({ page }) => {
  const dump = await dumpWith(page, 'one\ntwo\nthree', 11);
  await page.keyboard.press('Control+x');
  await expect(dump).toHaveValue('one\ntwo');
  await page.keyboard.press('Control+x');
  await expect(dump).toHaveValue('one');
  await page.keyboard.press('Control+x');
  await expect(dump).toHaveValue('');
});

test('the first line goes with its newline, and a selection is cut as usual', async ({ page }) => {
  const dump = await dumpWith(page, 'one\ntwo\nthree', 0);
  await page.keyboard.press('Control+x');
  await expect(dump).toHaveValue('two\nthree');
  await dump.evaluate((el) => (el as HTMLTextAreaElement).setSelectionRange(1, 3));
  await page.keyboard.press('Control+x');
  await expect(dump).toHaveValue('t\nthree');
});
