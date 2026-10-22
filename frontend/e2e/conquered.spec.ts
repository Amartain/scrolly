import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section, sheathe } from './helpers';

const view = async (page: Page) => (await page.request.get('/api/view')).json();

/** Plan two trials, give the first a 45m estimate and seal, all through the API. */
async function sealWithEstimate(page: Page) {
  await page.request.post('/api/planning/start');
  await page.request.put('/api/planning/text', { data: { text: 'Write report\nTidy desk' } });
  await page.request.post('/api/planning/proceed');
  const first = (await view(page)).planning.trials[0].id;
  await page.request.patch(`/api/planning/trials/${first}`, { data: { estimate: '45m' } });
  await page.request.post('/api/planning/seal');
  await page.goto('/');
}

const conquered = (page: Page) => section(page, 'Conquered Today');
const immediate = (page: Page) => section(page, 'The Immediate Trial');

test('conquering lists the trial with its minutes and promotes the next', async ({ page }) => {
  await sealWithEstimate(page);
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(conquered(page).getByRole('heading')).toHaveText(/Conquered Today · 1/i);
  await expect(conquered(page).getByText('Write report')).toBeVisible();
  await expect(conquered(page).getByRole('listitem')).toContainText('45m');
  await expect(immediate(page).getByText('Tidy desk')).toBeVisible();
  await expect(section(page, 'Essence').getByRole('meter')).toHaveAttribute(
    'aria-valuetext',
    /^45m done · 0m to go/,
  );
});

test('a conquered row offers its time to correct and Revive, and no field until asked', async ({
  page,
}) => {
  await sealWithEstimate(page);
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  const row = conquered(page).getByRole('listitem');
  await expect(row).toContainText('45m');
  await expect(row.getByRole('textbox')).toHaveCount(0);
  await expect(row.getByRole('button')).toHaveText(['45m', 'Revive']);
});

test('reviving puts the trial back on the scroll', async ({ page }) => {
  await sealWithEstimate(page);
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await page.getByRole('button', { name: 'Revive Write report' }).click();
  await expect(conquered(page).getByText(/No trial conquered yet/)).toBeVisible();
  await expect(immediate(page).getByText('Tidy desk')).toBeVisible();
  await expect(section(page, 'Remaining Trials').getByText('Write report')).toBeVisible();
});

test('postponing sends the trial to the Horizon and promotes the next', async ({ page }) => {
  await sealWithEstimate(page);
  await page.getByRole('button', { name: 'Postpone Write report to the Horizon' }).click();
  await expect(immediate(page).getByText('Tidy desk')).toBeVisible();
  // The Horizon panel on Screen 2 is step 5; for now the server's view proves it arrived.
  const horizon = (await view(page)).planning.horizon;
  expect(horizon.map((item: { title: string }) => item.title)).toEqual(['Write report']);
});

test('a Mandate cannot be abandoned, a Mortal Trial can', async ({ page }) => {
  await sealWithEstimate(page);
  const abandon = page.getByRole('button', { name: 'Abandon Write report' });
  await page.getByRole('button', { name: 'Make Write report a Heavenly Mandate' }).click();
  await expect(abandon).toHaveCount(0);
  await page.getByRole('button', { name: 'Make Write report a Mortal Trial' }).click();
  await abandon.click();
  await expect(immediate(page).getByText('Tidy desk')).toBeVisible();
  await expect(conquered(page).getByText('Write report')).toHaveCount(0);
});

test('conquering the last trial brings the victory banner', async ({ page }) => {
  await sealDay(page, 'Only one');
  await page.goto('/');
  await page.getByRole('button', { name: 'Conquer Only one' }).click();
  await sheathe(page);
  await expect(page.getByRole('heading', { name: 'Another Day Conquered' })).toBeVisible();
  await expect(conquered(page).getByText('Only one')).toBeVisible();
});

test('Lifetime Conquered goes up on conquer and back down on revive; Cycles stay', async ({
  page,
}) => {
  await sealWithEstimate(page);
  const lifetime = section(page, 'Lifetime Conquered');
  const cycles = section(page, 'Heavenly Cycles');
  await expect(lifetime).toContainText('0');
  await expect(cycles).toContainText('1');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(lifetime).toContainText('1');
  await page.getByRole('button', { name: 'Revive Write report' }).click();
  await expect(lifetime).toContainText('0');
  await expect(cycles).toContainText('1');
});
