import { expect, test } from './fixtures';
import { sealDay } from './helpers';

test('Backup Scroll downloads a timestamped zip of CSVs', async ({ page }) => {
  await sealDay(page, 'Write the report');
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Backup Scroll' }).click();
  expect((await download).suggestedFilename()).toMatch(/^scrolly-\d{8}-\d{6}\.zip$/);
});
