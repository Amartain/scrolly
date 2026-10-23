import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

// Finds that broke (owner, 2026-10-23): the Golden Core after its invitation was answered, and
// correcting a conquered time (the double-click replaced the element the tour looked up from).

const learned = async (page: Page): Promise<string[]> =>
  (await (await page.request.get('/api/view')).json()).knowledge.learned;

test('the Settings switch teaches the Golden Core once the invitation is answered', async ({
  page,
}) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByRole('checkbox', { name: 'Weigh Qi while planning' }).check();
  await expect.poll(() => learned(page)).toContain('golden-core');
});

async function conquerWithTime(page: Page) {
  await sealDay(page, 'Write report', 'Tidy desk');
  const view = await (await page.request.get('/api/view')).json();
  const id = view.dashboard.immediate.id;
  await page.request.patch(`/api/trials/${id}`, { data: { estimate: '27m' } });
  await page.request.post(`/api/trials/${id}/conquer`);
  await page.goto('/');
  return section(page, 'Conquered Today').getByRole('button', {
    name: 'Actual time of Write report',
  });
}

test('double-clicking a conquered time teaches correcting it', async ({ page }) => {
  const time = await conquerWithTime(page);
  await time.dblclick();
  await expect.poll(() => learned(page)).toContain('correct-time');
});

test('opening a conquered time with Enter teaches it too', async ({ page }) => {
  const time = await conquerWithTime(page);
  await time.focus();
  await page.keyboard.press('Enter');
  await expect.poll(() => learned(page)).toContain('correct-time');
});
