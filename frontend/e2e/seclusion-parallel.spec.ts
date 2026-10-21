import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

const room = (page: Page) => section(page, 'Focus Scroll');
const search = (page: Page) => page.getByRole('textbox', { name: 'Parallel Flow' });
const beside = (page: Page) => page.getByRole('group', { name: 'Parallel Flow' });

async function enter(page: Page, ...titles: string[]) {
  await sealDay(page, ...titles);
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await expect(search(page)).toBeVisible();
}

test('A waiting trial found by the search runs beside, on a clock of its own', async ({ page }) => {
  await enter(page, 'Write report', 'Tend the tea');
  await search(page).fill('tea');
  await page.getByRole('button', { name: /Tend the tea/ }).click();
  await expect(beside(page)).toContainText('Tend the tea');
  await expect(beside(page)).toContainText('00:00:00'); // nothing starts on its own
  await beside(page).getByRole('button', { name: 'Start the trial beside' }).click();
  await expect(beside(page).getByRole('button', { name: 'Pause the trial beside' })).toBeVisible();
  await expect(beside(page)).toContainText(/00:00:0[1-9]/);
  await expect(room(page)).toContainText('Write report'); // the main trial is untouched
  await expect(room(page).getByRole('button', { name: 'Start', exact: true })).toBeVisible();
});

test('Enter on a new title makes a trial to run beside', async ({ page }) => {
  await enter(page, 'Write report');
  await search(page).fill('Water the plants');
  await search(page).press('Enter');
  await expect(beside(page)).toContainText('Water the plants');
  await expect(search(page)).toHaveCount(0); // only one at a time
});

test('The search is reachable by keyboard alone', async ({ page }) => {
  await enter(page, 'Write report', 'Tend the tea');
  await search(page).fill('tea');
  await expect(page.getByRole('button', { name: /Tend the tea/ })).toBeVisible();
  await page.keyboard.press('ArrowDown');
  await expect(page.getByRole('button', { name: /Tend the tea/ })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(beside(page)).toContainText('Tend the tea');
});

test('Conquering the parallel trial asks its qi and leaves the main trial alone', async ({
  page,
}) => {
  await enter(page, 'Write report');
  await search(page).fill('Water the plants');
  await search(page).press('Enter');
  await beside(page).getByRole('button', { name: 'Conquer Water the plants' }).click();
  await expect(beside(page)).toHaveCount(0);
  await expect(search(page)).toBeVisible(); // the next one may run beside
  await expect(room(page)).toContainText('Write report');
  await page.getByRole('button', { name: 'Step out' }).click();
  await expect(section(page, 'Conquered Today')).toContainText('Water the plants');
});

test('When the main trial ends, the unfinished parallel one takes the ring ahead of the queue', async ({
  page,
}) => {
  await enter(page, 'Write report', 'Tend the tea', 'Sweep the pavilion');
  await search(page).fill('sweep');
  await page.getByRole('button', { name: /Sweep the pavilion/ }).click();
  await room(page).getByRole('button', { name: 'Start', exact: true }).click();
  await room(page).getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(room(page).getByRole('group', { name: 'What next?' })).toContainText(
    'Sweep the pavilion',
  );
  await expect(beside(page)).toHaveCount(0);
  await expect(search(page)).toBeVisible();
});

test('The mark switches the parallel trial between Mortal and Mandate; a Mandate offers postpone', async ({
  page,
}) => {
  await enter(page, 'Write report');
  await search(page).fill('Call the bank');
  await search(page).press('Enter');
  await expect(beside(page).getByRole('button', { name: /Abandon Call the bank/ })).toBeVisible();
  await beside(page)
    .getByRole('button', { name: /Make Call the bank a Heavenly Mandate/ })
    .click();
  await expect(beside(page).getByRole('button', { name: /Postpone Call the bank/ })).toBeVisible();
  await expect(beside(page).getByRole('button', { name: /Abandon/ })).toHaveCount(0);
});
