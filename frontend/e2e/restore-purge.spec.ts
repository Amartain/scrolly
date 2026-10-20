import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

test('backup, purge, then restore the zip brings the trials back', async ({ page }, info) => {
  await sealDay(page, 'Write the report', 'Tidy the desk');
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();

  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Backup Scroll' }).click();
  const zipPath = info.outputPath('backup.zip');
  await (await download).saveAs(zipPath);

  await page.getByRole('button', { name: "Purge Today's Scroll" }).click();
  const purge = page.getByRole('dialog', { name: "Purge Today's Scroll?" });
  await purge.getByRole('button', { name: 'Cancel' }).click();
  await expect(purge).toHaveCount(0);
  await page.getByRole('button', { name: "Purge Today's Scroll" }).click();
  await purge.getByRole('button', { name: 'Purge', exact: true }).click();
  await expect(page.getByRole('status')).toHaveText("Today's scroll is clear.");
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await expect(section(page, 'The Immediate Trial')).not.toContainText('Write the report');

  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByLabel('Scroll file').setInputFiles(zipPath);
  const replace = page.getByRole('dialog', { name: 'Replace everything?' });
  await expect(replace).toBeVisible();
  await replace.getByRole('button', { name: 'Replace', exact: true }).click();
  await expect(page.getByRole('status')).toContainText('Restored');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await expect(section(page, 'The Immediate Trial')).toContainText('Write the report');
  await expect(section(page, 'Remaining Trials')).toContainText('Tidy the desk');
});

test('a zip waits for a yes, and Esc leaves the data as it was', async ({ page }, info) => {
  await sealDay(page, 'Only trial');
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Backup Scroll' }).click();
  const zipPath = info.outputPath('backup.zip');
  await (await download).saveAs(zipPath);

  await page.getByLabel('Scroll file').setInputFiles(zipPath);
  const replace = page.getByRole('dialog', { name: 'Replace everything?' });
  await expect(replace).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(replace).toHaveCount(0);
  await expect(page.getByRole('status')).not.toContainText('Restored');
});
