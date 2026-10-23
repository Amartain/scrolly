import { expect, test } from './fixtures';
import { sealDay } from './helpers';

// A trial postponed or let go today comes back with a double-click, or Enter on its name (owner,
// 2026-10-23). A single click brings nothing back.

const panel = (page: import('@playwright/test').Page, title: string) =>
  page.locator(`section[aria-label="${title}"]`);

async function trialId(page: import('@playwright/test').Page, title: string) {
  const view = await (await page.request.get('/api/view')).json();
  return view.planning.trials.find((t: { title: string }) => t.title === title).id as string;
}

test('a double-click summons a postponed trial back to Remaining', async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.request.post(`/api/trials/${await trialId(page, 'Tidy desk')}/postpone`);
  await page.goto('/');
  await page.keyboard.press('ArrowDown');
  const name = panel(page, 'Postponed Today').getByRole('button', { name: /Summon Tidy desk/ });
  await name.click();
  await expect(name).toBeVisible();
  await name.dblclick();
  await expect(panel(page, 'Postponed Today').getByText('Nothing was sent')).toBeVisible();
  await expect(panel(page, 'Remaining Trials').getByText('Tidy desk')).toBeVisible();
});

test('Enter on a fallen leaf brings it back too', async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.request.post(`/api/trials/${await trialId(page, 'Tidy desk')}/abandon`);
  await page.goto('/');
  await page.keyboard.press('ArrowDown');
  await panel(page, 'Fallen Leaves')
    .getByRole('button', { name: /Summon Tidy desk/ })
    .focus();
  await page.keyboard.press('Enter');
  await expect(panel(page, 'Fallen Leaves').getByText('No leaf has fallen')).toBeVisible();
});
