import { expect, test } from './fixtures';
import { sealAndClose, sealDay, section, toEstimate } from './helpers';

const phase = (page: import('@playwright/test').Page) =>
  page.evaluate(() => document.documentElement.dataset.phase);

test('the Day Summary asks for a sunset once; Not now retires it and keeps totals only', async ({
  page,
}) => {
  await toEstimate(page, 'Write', 'Tidy');
  const summary = section(page, 'Day Summary');
  await expect(summary.getByLabel('Sunset time')).toBeVisible();
  await summary.getByRole('button', { name: 'Not now' }).click();
  await expect(summary.getByRole('button', { name: 'Not now' })).toHaveCount(0);
  await expect(summary).not.toContainText('of light left');
  await expect(summary).toContainText('2 trials');
  await page.reload();
  await expect(summary.getByLabel('Sunset time')).toHaveCount(0);
});

test('a sunset time answers the question, and Settings can change it', async ({ page }) => {
  await toEstimate(page, 'Write');
  const summary = section(page, 'Day Summary');
  await summary.getByLabel('Sunset time').fill('9pm');
  await summary.getByRole('button', { name: 'Set' }).click();
  await expect(summary.getByLabel('Sunset time')).toBeVisible(); // refused: still asking
  // 03:59 is just before the 04:00 rollover, so at any hour of the day the sunset is still ahead.
  await summary.getByLabel('Sunset time').fill('03:59');
  await page.keyboard.press('Enter');
  await expect(summary.getByLabel('Sunset time')).toHaveCount(0);
  await expect(summary).toContainText('of light left until sunset');

  await sealAndClose(page);
  await page.getByRole('button', { name: 'Settings' }).click();
  const panel = section(page, 'Sunset');
  await expect(panel.getByLabel('Sunset time')).toHaveValue('03:59');
  await panel.getByLabel('Sunset time').fill('03:30');
  await panel.getByRole('button', { name: 'Set' }).click();
  await page.reload();
  await page.getByRole('button', { name: 'Settings' }).click();
  await expect(section(page, 'Sunset').getByLabel('Sunset time')).toHaveValue('03:30');
});

test('finishing the day brings dusk, even with no sunset kept', async ({ page }) => {
  await page.request.put('/api/sunset', { data: { enabled: false } });
  await sealDay(page, 'Only trial');
  await page.goto('/');
  expect(await phase(page)).toBe('day');
  await page.getByRole('button', { name: 'Conquer Only trial' }).click();
  await expect.poll(() => phase(page)).toBe('dusk');
  await page.reload();
  await expect.poll(() => phase(page)).toBe('dusk');
});
