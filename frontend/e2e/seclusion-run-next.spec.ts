import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

const room = (page: Page) => section(page, 'Focus Scroll');
const card = (page: Page) => page.getByRole('group', { name: 'What next?' });

/** Seal two trials, open Seclusion on a tab and start its run through the API, then reload into it. */
async function underway(page: Page, discipline: string, start: object | null, ratio?: object) {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await expect(room(page)).toBeVisible();
  await page.request.post('/api/seclusion/discipline', { data: { discipline } });
  if (ratio) await page.request.put('/api/seclusion/flow/ratio', { data: ratio });
  await page.request.post('/api/seclusion/timer/start', { data: start ?? undefined });
  await page.reload();
}

test('Cycles: conquering keeps the focus counting; Continue puts the next trial in the same cycle', async ({
  page,
}) => {
  await underway(page, 'cycles', { focus_min: 5, break_min: 1, cycles: 2 });
  await expect(room(page)).toContainText('cycle 1 of 2');
  await room(page).getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(card(page)).toContainText('Tidy desk');
  await expect(card(page)).toContainText('focus');
  const clock = card(page).locator('.run .digits');
  const first = await clock.textContent();
  await expect.poll(() => clock.textContent(), { timeout: 5000 }).not.toBe(first);

  await card(page)
    .getByRole('button', { name: /Continue the cycle/ })
    .click();
  await expect(card(page)).toHaveCount(0);
  await expect(room(page)).toContainText('Tidy desk');
  await expect(room(page)).toContainText('cycle 1 of 2');
  await expect(room(page).getByRole('button', { name: 'Pause timer' })).toBeVisible();
});

test('Cycles: Take a break now starts the break on the ring', async ({ page }) => {
  await underway(page, 'cycles', { focus_min: 5, break_min: 1, cycles: 2 });
  await room(page).getByRole('button', { name: 'Conquer Write report' }).click();
  await card(page).getByRole('button', { name: 'Take a break now' }).click();
  await expect(card(page)).toHaveCount(0);
  await expect(room(page).locator('.ring[data-tone="cycles-break"]')).toContainText('break');
});

test('Cycles: Start new cycle begins cycle 1 at once, with the last settings', async ({ page }) => {
  await underway(page, 'cycles', { focus_min: 7, break_min: 2, cycles: 2 });
  await room(page).getByRole('button', { name: 'Conquer Write report' }).click();
  await card(page).getByRole('button', { name: 'Start new cycle' }).click();
  await expect(room(page).getByRole('timer')).toContainText('cycle 1 of 2');
  await expect(room(page).getByRole('timer')).toContainText('06:');
  await expect(room(page).getByRole('button', { name: 'Pause timer' })).toBeVisible();
});

test('Flow: Continue keeps the same bank, and the bank stops while nothing is worked on', async ({
  page,
}) => {
  await underway(page, 'flow', null, { work: 1, rest: 1 });
  await expect(room(page)).toContainText('elapsed');
  await room(page).getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(card(page)).toContainText('Tidy desk');
  await card(page).getByRole('button', { name: 'Continue the flow' }).click();
  await expect(card(page)).toHaveCount(0);
  await expect(room(page)).toContainText('Tidy desk');
  await expect(room(page).locator('.ring[data-tone="flow"]')).toContainText('elapsed');
  await expect(room(page).getByRole('button', { name: 'Pause timer' })).toBeVisible();
});
