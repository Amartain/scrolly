import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

const room = (page: Page) => section(page, 'Focus Scroll');
const card = (page: Page) => page.getByRole('group', { name: 'What next?' });

async function enter(page: Page, ...titles: string[]) {
  await sealDay(page, ...titles);
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await expect(room(page)).toBeVisible();
}

test('Scribe: Enter writes a sudden trial on top of Remaining, clears the input and says so', async ({
  page,
}) => {
  await enter(page, 'Write report', 'Tidy desk');
  const input = page.getByLabel('Scribe a sudden trial');
  await input.fill('Water the plants');
  await input.press('Enter');
  await expect(input).toHaveValue('');
  await expect(page.getByRole('status').filter({ hasText: 'Inscribed' })).toBeVisible();
  await expect(room(page)).not.toContainText('Water the plants');
  await page.getByRole('button', { name: 'Step out' }).click();
  const remaining = section(page, 'Remaining Trials');
  await expect(remaining).toContainText('Water the plants');
  const titles = await remaining.locator('.read').allTextContents();
  expect(titles.findIndex((t) => t.includes('Water the plants'))).toBe(0);
});

test('N jumps to the Scribe box', async ({ page }) => {
  await enter(page, 'Write report');
  await page.keyboard.press('n');
  await expect(page.getByLabel('Scribe a sudden trial')).toBeFocused();
});

test('conquering shows What next with the next trial idle; Undo takes it back', async ({
  page,
}) => {
  await enter(page, 'Write report', 'Tidy desk');
  await room(page).getByRole('button', { name: 'Start', exact: true }).click();
  await room(page).getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(card(page)).toContainText('Tidy desk');
  await expect(room(page).getByRole('button', { name: 'Start', exact: true })).toBeVisible();
  await card(page).getByRole('button', { name: 'Undo' }).click();
  await expect(card(page)).toHaveCount(0);
  await expect(room(page)).toContainText('Write report');
  await expect(room(page)).not.toContainText('Tidy desk');
});

test('Light new incense runs the next trial', async ({ page }) => {
  await enter(page, 'Write report', 'Tidy desk');
  await room(page).getByRole('button', { name: 'Start', exact: true }).click();
  await room(page).getByRole('button', { name: 'Conquer Write report' }).click();
  await card(page)
    .getByRole('button', { name: /Light new incense/ })
    .click();
  await expect(card(page)).toHaveCount(0);
  await expect(room(page).getByRole('button', { name: 'Pause timer' })).toBeVisible();
});

test('Switch trials lists Remaining and the chosen trial becomes the one at hand', async ({
  page,
}) => {
  await enter(page, 'Write report', 'Tidy desk', 'Water plants');
  await room(page).getByRole('button', { name: 'Start', exact: true }).click();
  await room(page).getByRole('button', { name: 'Conquer Write report' }).click();
  await card(page).getByRole('button', { name: 'Switch trials' }).click();
  await card(page).getByRole('button', { name: 'Switch to Water plants' }).click();
  await expect(card(page)).toHaveCount(0);
  await expect(room(page)).toContainText('Water plants');
});

test('abandoning shows What next too, without an Undo', async ({ page }) => {
  await enter(page, 'Write report', 'Tidy desk');
  await room(page).getByRole('button', { name: 'Abandon Write report' }).click();
  await expect(card(page)).toContainText('Tidy desk');
  await expect(card(page).getByRole('button', { name: 'Undo' })).toHaveCount(0);
});

test('the last trial ends in rest: dusk comes, and Undo brings the trial back', async ({
  page,
}) => {
  await enter(page, 'Write report');
  await room(page).getByRole('button', { name: 'Start', exact: true }).click();
  await room(page).getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(page.getByText('Well done, time to rest.')).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('data-phase', 'dusk');
  await page.getByRole('button', { name: 'Undo' }).click();
  await expect(room(page)).toContainText('Write report');
});
