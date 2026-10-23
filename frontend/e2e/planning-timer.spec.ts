import { expect, test } from './fixtures';
import { begin, sealAndClose, toEstimate } from './helpers';

const clock = (page: import('@playwright/test').Page) =>
  page.getByRole('timer', { name: 'Time spent planning' });

test('no planning clock on the zero state or in Phase 1 (Knowledge of the Dao sits there); Phase 2 has it, at zero', async ({
  page,
}) => {
  await page.goto('/');
  await expect(page.getByRole('group', { name: 'Time spent planning' })).toHaveCount(0);
  await begin(page);
  await expect(page.getByRole('group', { name: 'Time spent planning' })).toHaveCount(0);
  await expect(page.getByRole('progressbar', { name: 'Knowledge of the Dao' })).toBeVisible();
  await page.locator('#dump').fill('Write the report');
  await page.getByRole('button', { name: 'Proceed: Divine the Time' }).click();
  await expect(clock(page)).toHaveText('00:00:00');
  await expect(page.getByRole('button', { name: 'Start planning time' })).toBeVisible();
});

test('it counts from a click, survives a reload, and a reset zeroes it', async ({ page }) => {
  await toEstimate(page, 'Write the report');
  await page.getByRole('button', { name: 'Start planning time' }).click();
  await expect(clock(page)).not.toHaveText('00:00:00');
  await page.reload();
  await expect(page.getByRole('button', { name: 'Pause planning time' })).toBeVisible();
  await expect(clock(page)).not.toHaveText('00:00:00');

  await page.getByRole('button', { name: 'Pause planning time' }).click();
  const paused = (await clock(page).textContent()) ?? '';
  await page.waitForTimeout(1500);
  await expect(clock(page)).toHaveText(paused);

  await page.getByRole('button', { name: 'Reset planning time' }).click();
  await expect(clock(page)).toHaveText('00:00:00');
});

test('it is on in Phase 2 as well, and sealing banks it without a fuss', async ({ page }) => {
  await toEstimate(page, 'Write the report');
  await expect(clock(page)).toBeVisible();
  await page.getByRole('button', { name: 'Start planning time' }).click();
  await expect(clock(page)).not.toHaveText('00:00:00');
  await sealAndClose(page);
  await expect(page.getByRole('group', { name: 'Time spent planning' })).toHaveCount(0);
  const view = await (await page.request.get('/api/view')).json();
  expect(view.planning.timer.running).toBe(false);
  expect(view.planning.timer.elapsed_s).toBeGreaterThanOrEqual(0);
});
