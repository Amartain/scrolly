import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { art, begin, importFile, section, toEstimate } from './helpers';

const trialRows = (page: Page) =>
  page.getByRole('list', { name: 'Trials on the scroll' }).getByRole('listitem');
const titles = (page: Page) => trialRows(page).locator('.title').allTextContents();

const horizonItem = {
  id: 'q_h1',
  description: 'Plan the garden',
  status: 'Remaining',
  logical_date: '2026-10-01',
  expected_time_mins: 45,
  mandate: true,
};

test('a day with nothing on the scroll starts in the quiet zero state', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'The Peak is Serene' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Cultivate Your Focus' })).toBeVisible();
  await expect(page.locator('[inert]')).toHaveCount(1);
  const fits = await page.evaluate(() => document.documentElement.scrollHeight <= innerHeight);
  expect(fits).toBe(true);
});

test('plan a day from the first click to the sealed dashboard', async ({ page }) => {
  await toEstimate(page, 'Write report', '', 'Tidy desk');
  expect(await titles(page)).toEqual(['Write report', 'Tidy desk']);

  const estimate = page.getByLabel('Estimate for Write report');
  await estimate.fill('1h15m');
  await estimate.press('Enter');
  await expect(estimate).toHaveValue('1h15m');
  const mandate = page.getByRole('button', { name: 'Make Write report a Heavenly Mandate' });
  await mandate.click();
  await expect(
    page.getByRole('button', { name: 'Make Write report a Mortal Trial' }),
  ).toHaveAttribute('aria-pressed', 'true');

  await trialRows(page).first().focus();
  await page.keyboard.press('Alt+ArrowDown');
  await expect.poll(() => titles(page)).toEqual(['Tidy desk', 'Write report']);

  await page.getByRole('button', { name: 'Seal Scroll and Commence' }).click();
  await expect(section(page, 'The Immediate Trial')).toContainText('Tidy desk');
  await expect(section(page, 'Remaining Trials')).toContainText('Write report');
  await expect(page.getByLabel('Estimate for Write report')).toHaveValue('1h15m');
});

test('Alt+Home and Alt+End move a trial to either end', async ({ page }) => {
  await toEstimate(page, 'One', 'Two', 'Three');
  await trialRows(page).nth(1).focus();
  await page.keyboard.press('Alt+End');
  await expect.poll(() => titles(page)).toEqual(['One', 'Three', 'Two']);
  await page.keyboard.press('Alt+Home');
  await expect.poll(() => titles(page)).toEqual(['Two', 'One', 'Three']);
});

test('a row can be dragged to a new place with the mouse', async ({ page }) => {
  await toEstimate(page, 'One', 'Two', 'Three');
  const grab = (await trialRows(page).nth(0).locator('.title').boundingBox())!;
  const last = (await trialRows(page).nth(2).boundingBox())!;
  await page.mouse.move(grab.x + 4, grab.y + grab.height / 2);
  await page.mouse.down();
  await page.mouse.move(grab.x + 4, last.y + last.height - 2, { steps: 8 });
  await expect(page.locator('.drop')).toBeVisible();
  await page.mouse.up();
  await expect.poll(() => titles(page)).toEqual(['Two', 'Three', 'One']);
});

test('a bad estimate shows the format and the field goes back', async ({ page }) => {
  await toEstimate(page, 'Walk');
  const estimate = page.getByLabel('Estimate for Walk');
  for (const bad of ['90', '1.5h', '0m', '17h', '1h75m', '²', 'soon']) {
    await estimate.fill(bad);
    await estimate.press('Enter');
    await expect(page.getByRole('status')).toContainText('Use 45m, 2h or 1h30m');
    await expect(estimate).toHaveValue('');
  }
});

test('a forgotten trial can be added, and a mandate can be postponed to the Horizon', async ({
  page,
}) => {
  await toEstimate(page, 'Taxes');
  await page.getByLabel('A forgotten trial').fill('Call mum');
  await page.getByLabel('A forgotten trial').press('Enter');
  await expect.poll(() => titles(page)).toEqual(['Taxes', 'Call mum']);
  await page.getByRole('button', { name: 'Make Taxes a Heavenly Mandate' }).click();
  await page.getByRole('button', { name: 'Postpone Taxes to the Horizon' }).click();
  await expect.poll(() => titles(page)).toEqual(['Call mum']);
  await page.getByRole('button', { name: '◀ Back to Inscribing' }).click();
  await expect(section(page, 'The Horizon')).toContainText('Taxes');
});

test('Back to Inscribing keeps every trial and estimate', async ({ page }) => {
  await toEstimate(page, 'Write report');
  const estimate = page.getByLabel('Estimate for Write report');
  await estimate.fill('45m');
  await estimate.press('Enter');
  await page.getByRole('button', { name: '◀ Back to Inscribing' }).click();
  await expect(section(page, 'On the Scroll')).toContainText('Write report');
  await expect(section(page, 'On the Scroll')).toContainText('45m');
  await page.locator('#dump').fill('Second');
  await page.getByRole('button', { name: 'Proceed: Divine the Time' }).click();
  await expect.poll(() => titles(page)).toEqual(['Write report', 'Second']);
  await expect(page.getByLabel('Estimate for Write report')).toHaveValue('45m');
});

test('summoning moves a Horizon item and copies an Art, and Abandon gives it all back', async ({
  page,
}) => {
  await importFile(page, 'future_trials.json', [horizonItem]);
  await importFile(page, 'rituals.json', [art]);
  await begin(page);

  await page.getByRole('button', { name: 'Summon Plan the garden' }).click();
  await expect(section(page, 'On the Scroll')).toContainText('Plan the garden');
  await expect(section(page, 'The Horizon')).not.toContainText('Plan the garden');

  await page.getByRole('button', { name: 'Return Plan the garden to the Horizon' }).click();
  await expect(section(page, 'The Horizon')).toContainText('Plan the garden');

  await page.getByRole('button', { name: 'Summon Plan the garden' }).click();
  await page.getByRole('button', { name: 'Summon Stretch' }).click();
  await expect(section(page, 'On the Scroll')).toContainText('Stretch');
  await expect(section(page, 'Foundational Arts')).toContainText('Stretch');

  await page.getByRole('button', { name: 'Abandon' }).click();
  await expect(page.getByRole('heading', { name: 'The Peak is Serene' })).toBeVisible();
  const view = await (await page.request.get('/api/view')).json();
  expect(view.planning.horizon.map((item: { title: string }) => item.title)).toEqual([
    'Plan the garden',
  ]);
});

test('proceeding with nothing written says so and stays put', async ({ page }) => {
  await begin(page);
  await page.getByRole('button', { name: 'Proceed: Divine the Time' }).click();
  await expect(page.getByRole('status')).toContainText('at least one trial');
  await expect(page.getByRole('heading', { name: 'Inscribe the Scroll' })).toBeVisible();
});

test('a reload in the middle of planning loses nothing', async ({ page }) => {
  await begin(page);
  await page.locator('#dump').fill('Typed before the reload');
  await expect
    .poll(async () => (await (await page.request.get('/api/view')).json()).planning.text)
    .toBe('Typed before the reload');
  await page.reload();
  await expect(page.locator('#dump')).toHaveValue('Typed before the reload');

  await page.getByRole('button', { name: 'Proceed: Divine the Time' }).click();
  const estimate = page.getByLabel('Estimate for Typed before the reload');
  await estimate.fill('20m');
  await estimate.press('Enter');
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Estimate the Journey' })).toBeVisible();
  await expect(estimate).toHaveValue('20m');
});
