import { fileURLToPath } from 'node:url';
import { expect, test } from './fixtures';
import { sealDay } from './helpers';

const fixture = (name: string) =>
  fileURLToPath(new URL(`../../tests/fixtures/${name}`, import.meta.url));

test('Restore Scroll adds an old backup once and skips it the second time', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  const status = page.getByRole('status');
  const picker = page.getByLabel('Scroll file');

  await picker.setInputFiles(fixture('prototype_backup.json'));
  await expect(status).toHaveText('Added 12, skipped 1 already there.');

  await picker.setInputFiles(fixture('prototype_backup.json'));
  await expect(status).toHaveText('Added 0, skipped 13 already there.');
});

test('Restore Scroll says plainly when a file is not understood', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByLabel('Scroll file').setInputFiles({
    name: 'notes.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('hello'),
  });
  await expect(page.getByRole('status')).toContainText('.json');
});

test('Restore Scroll can be reached with the keyboard', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  const restore = page.getByRole('button', { name: 'Restore Scroll' });
  for (let presses = 0; presses < 12; presses++) {
    if (await restore.evaluate((el) => el === document.activeElement)) break;
    await page.keyboard.press('Tab');
  }
  await expect(restore).toBeFocused();
});
