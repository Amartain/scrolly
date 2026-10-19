import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

test('Qi is set on the Immediate card and shown as plain text once conquered', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.request.put('/api/golden-core', { data: { enabled: true } });
  await page.goto('/');
  const field = page.getByLabel('Qi expected of Write report');
  await field.fill('35');
  await field.press('Enter');
  await expect(field).toHaveValue('35');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  const row = section(page, 'Conquered Today').getByRole('listitem');
  await expect(row).toContainText('35 Qi');
  await expect(row.getByRole('textbox')).toHaveCount(0);
  await expect(section(page, 'Essence')).toContainText('35');
});

test('Qi fields stay hidden while the Golden Core is off', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await expect(page.getByLabel('Qi expected of Write report')).toHaveCount(0);
});
