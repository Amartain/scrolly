import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

test('Qi is edited on the Immediate card and recorded as the actual when conquered', async ({
  page,
}) => {
  await sealDay(page, 'Write report');
  await page.request.put('/api/golden-core', { data: { enabled: true } });
  await page.goto('/');
  const field = page.getByLabel('Qi expected of Write report');
  await field.fill('35');
  await field.press('Enter');
  await expect(field).toHaveValue('35');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  const actual = section(page, 'Conquered Today').getByLabel('Qi spent on Write report');
  await expect(actual).toHaveValue('35');
  await actual.fill('60');
  await actual.press('Enter');
  await expect(actual).toHaveValue('60');
  await expect(section(page, 'Essence')).toContainText('60');
});

test('Qi fields stay hidden while the Golden Core is off', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await expect(page.getByLabel('Qi expected of Write report')).toHaveCount(0);
});
