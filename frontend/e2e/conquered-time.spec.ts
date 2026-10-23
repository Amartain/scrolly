import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

// A conquered trial's time can be corrected in place: double-click it (or Enter on it), and a small
// boxed field with a check mark takes its place, as for a late estimate.

const conquered = (page: Page) => section(page, 'Conquered Today');
const time = (page: Page) =>
  conquered(page).getByRole('button', { name: 'Actual time of Write report' });
const field = (page: Page) =>
  conquered(page).getByRole('textbox', { name: 'Actual time of Write report' });

test.beforeEach(async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  const view = await (await page.request.get('/api/view')).json();
  const id = view.dashboard.immediate.id;
  await page.request.patch(`/api/trials/${id}`, { data: { estimate: '27m' } });
  await page.request.post(`/api/trials/${id}/conquer`);
  await page.goto('/');
});

test('double-click the time, write another, Enter: the row and Essence follow', async ({
  page,
}) => {
  await expect(time(page)).toHaveText('27m');
  await time(page).dblclick();
  // A boxed field, like a late estimate's.
  await expect(field(page)).not.toHaveCSS('border-top-width', '0px');
  await field(page).fill('45m');
  await page.keyboard.press('Enter');
  await expect(time(page)).toHaveText('45m');
  await expect(section(page, 'Essence')).toContainText('45m');
});

test('the check mark saves too', async ({ page }) => {
  await time(page).dblclick();
  await field(page).fill('1h');
  await conquered(page).getByRole('button', { name: 'Save the time of Write report' }).click();
  await expect(time(page)).toHaveText('1h');
});

test('Esc keeps the old time, and a time that cannot be used is refused', async ({ page }) => {
  await time(page).focus();
  await page.keyboard.press('Enter');
  await field(page).fill('1h');
  await page.keyboard.press('Escape');
  await expect(time(page)).toHaveText('27m');

  await time(page).dblclick();
  await field(page).fill('soon');
  await page.keyboard.press('Enter');
  // Refused: the field stays open with the hint, so the time can be written again.
  await expect(conquered(page).getByText('Use 45m, 2h or 1h30m')).toBeVisible();
  await expect(field(page)).toHaveValue('soon');
  await page.keyboard.press('Escape');
  await expect(time(page)).toHaveText('27m');
});
