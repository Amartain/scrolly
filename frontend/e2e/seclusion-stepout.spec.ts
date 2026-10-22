import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

// Stepping out leaves the room's run going (owner, 2026-10-23): the dashboard shows its clock and
// drives it, and the gate says Return.

const room = (page: Page) => section(page, 'Focus Scroll');
const card = (page: Page) => section(page, 'The Immediate Trial');
const roomClock = (page: Page) => card(page).getByRole('timer', { name: "The room's clock" });

async function startCycles(page: Page) {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await room(page).getByRole('tab', { name: 'Harmonious Cycles' }).click();
  await expect(room(page).getByRole('slider')).toBeFocused();
  await page.keyboard.press('Enter');
  await page.keyboard.press('Enter');
  await page.keyboard.press('Enter');
  await expect(room(page)).toContainText('cycle 1 of 3');
}

test('after stepping out the dashboard shows the cycle counting down, and pauses it', async ({
  page,
}) => {
  await startCycles(page);
  await page.getByRole('button', { name: 'Step out' }).click();
  await expect(roomClock(page)).toHaveText(/^4[45]:\d\d$/);
  await expect(card(page)).toContainText('focus · cycle 1 of 3');
  await expect(card(page).getByRole('button', { name: 'Reset timer' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: /^Return to Seclusion/ })).toBeVisible();

  await card(page).getByRole('button', { name: 'Pause timer' }).click();
  await expect(card(page).getByRole('button', { name: 'Start timer' })).toBeVisible();
  await page.getByRole('button', { name: /^Return to Seclusion/ }).click();
  await expect(room(page)).toContainText('cycle 1 of 3');
  await expect(room(page).getByRole('tab', { name: 'Harmonious Cycles' })).toHaveAttribute(
    'aria-selected',
    'true',
  );
});

test('Space on the dashboard pauses and resumes the room’s run', async ({ page }) => {
  await startCycles(page);
  await page.getByRole('button', { name: 'Step out' }).click();
  await expect(roomClock(page)).toBeVisible();
  await page.keyboard.press('Space');
  await expect(card(page).getByRole('button', { name: 'Start timer' })).toBeVisible();
  await page.keyboard.press('Space');
  await expect(card(page).getByRole('button', { name: 'Pause timer' })).toBeVisible();
});

test('a trial run beside keeps running and shows on the gate', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  const search = page.getByRole('textbox', { name: 'Parallel Flow' });
  await search.fill('Tend the tea');
  await search.press('Enter');
  await page.getByRole('button', { name: 'Start the trial beside' }).click();
  await expect(page.getByRole('button', { name: 'Pause the trial beside' })).toBeVisible();
  await page.getByRole('button', { name: 'Step out' }).click();
  await expect(page.getByRole('button', { name: /^Return to Seclusion/ })).toContainText(
    'Tend the tea',
  );
});
