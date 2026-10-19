import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { art, importFile, sealDay, section } from './helpers';

const remaining = (page: Page) => section(page, 'Remaining Trials');
const titles = async (page: Page) => remaining(page).locator('li .read').allTextContents();

const horizonItem = {
  id: 'q_h1',
  description: 'Plan the garden',
  status: 'Remaining',
  logical_date: '2026-10-01',
  expected_time_mins: 45,
  mandate: true,
};

test('Scribe Trial adds to the queue, and N jumps to the form', async ({ page }) => {
  await sealDay(page, 'First', 'Second');
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Settings' })).toBeVisible();
  await page.keyboard.press('n');
  await expect(page.getByLabel('Trial to scribe')).toBeFocused();
  await page.getByLabel('Trial to scribe').fill('Pay rent');
  await page.getByLabel('Estimate', { exact: true }).fill('20m');
  await page.getByRole('button', { name: 'Inscribe' }).click();
  await expect(remaining(page).getByText('Pay rent')).toBeVisible();
  await expect(page.getByLabel('Estimate for Pay rent')).toHaveValue('20m');
  await expect(page.getByLabel('Trial to scribe')).toHaveValue('');
});

test('Promote swaps a waiting trial with the Immediate one', async ({ page }) => {
  await sealDay(page, 'First', 'Second', 'Third');
  await page.goto('/');
  await page.getByRole('button', { name: 'Promote Third' }).click();
  await expect(section(page, 'The Immediate Trial').getByText('Third')).toBeVisible();
  expect(await titles(page)).toEqual(['First', 'Second']);
});

test('a waiting trial reorders with Alt+Arrow from the keyboard', async ({ page }) => {
  await sealDay(page, 'Now', 'A', 'B', 'C');
  await page.goto('/');
  await remaining(page).getByRole('listitem').filter({ hasText: 'A' }).first().focus();
  await page.keyboard.press('Alt+ArrowDown');
  await expect.poll(() => titles(page)).toEqual(['B', 'A', 'C']);
});

test('the Horizon takes new ideas, summons them and lets them go', async ({ page }) => {
  await importFile(page, 'future_trials.json', [horizonItem]);
  await sealDay(page, 'First');
  await page.goto('/');
  const horizon = section(page, 'The Horizon');
  await horizon.getByLabel('A future trial').fill('Call mum');
  await horizon.getByRole('button', { name: 'Add' }).click();
  await expect(horizon.getByText('Call mum')).toBeVisible();
  await expect(horizon.getByRole('textbox')).toHaveCount(1);
  await horizon.getByRole('button', { name: 'Summon Plan the garden' }).click();
  await expect(horizon.getByText('Plan the garden')).toHaveCount(0);
  await expect(remaining(page).getByText('Plan the garden')).toBeVisible();
});

test('an Art is summoned with +, and the template stays', async ({ page }) => {
  await importFile(page, 'rituals.json', [art]);
  await sealDay(page, 'First');
  await page.goto('/');
  await section(page, 'Foundational Arts').getByRole('button', { name: 'Summon Stretch' }).click();
  await expect(remaining(page).getByText('Stretch')).toBeVisible();
  await expect(section(page, 'Foundational Arts').getByText('Stretch')).toBeVisible();
});

test('a waiting Mortal Trial can be abandoned, a Mandate postponed', async ({ page }) => {
  await sealDay(page, 'First', 'Second', 'Third');
  await page.goto('/');
  await remaining(page).getByRole('button', { name: 'Make Third a Heavenly Mandate' }).click();
  await remaining(page).getByRole('button', { name: 'Abandon Second' }).click();
  await remaining(page).getByRole('button', { name: 'Postpone Third to the Horizon' }).click();
  await expect(section(page, 'Fallen Leaves')).toContainText('Second');
  await expect(section(page, 'Postponed Today')).toContainText('Third');
  await expect(section(page, 'The Horizon').getByText('Third')).toBeVisible();
});

test('conquered trials read in the order they were conquered, under counters', async ({ page }) => {
  await sealDay(page, 'A', 'B');
  await page.goto('/');
  await page.getByRole('button', { name: 'Conquer A' }).click();
  await page.getByRole('button', { name: 'Conquer B' }).click();
  await expect(section(page, 'Conquered Today').locator('li .read')).toHaveText(['A', 'B']);
  await expect(section(page, 'Lifetime Conquered')).toContainText('2');
  await expect(section(page, 'Heavenly Cycles')).toContainText('1');
});
