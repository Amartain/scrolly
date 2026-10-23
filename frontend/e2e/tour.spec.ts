import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay } from './helpers';
import { KEYS } from './tour-keys';

// Knowledge of the Dao (owner, 2026-10-23): a tour like a game. Step cards beside the thing to do,
// done by doing it; a "+1" for a find; one bar that fills and can be hidden.

test.use({ tour: true });

const card = (page: Page) => page.getByRole('note', { name: /Knowledge of the Dao/ });
const bar = (page: Page) => page.getByRole('progressbar', { name: 'Knowledge of the Dao' });

test('a newcomer walks Phase 1 by doing it, and the bar starts already a little full', async ({
  page,
}) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Cultivate Your Focus' }).click();
  await expect(bar(page)).toHaveAttribute('aria-valuenow', '2'); // opened, and the first step
  await expect(card(page)).toContainText('Empty your mind');
  await page.locator('#dump').fill('Write report');
  await expect(card(page)).toContainText('Choose your world');
  await page.getByRole('button', { name: /Hidden Pavilion teal/ }).click();
  await expect(card(page)).toContainText('All out of your head?');
  await page.getByRole('button', { name: 'Got it' }).click();
  await expect(card(page)).toHaveCount(0);
  await expect(bar(page)).toHaveAttribute('aria-valuenow', '4');
});

test('a find gets its +1 beside it, and Skip the tour leaves no card', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  // A step of Phase 1 not yet walked shows wherever its target is: the orbs are in the header too.
  await expect(card(page)).toContainText('Choose your world');
  await card(page).getByRole('button', { name: 'Got it' }).click();
  await expect(card(page)).toContainText('Begin');
  await page.getByRole('button', { name: 'Settings' }).click();
  await expect(
    page.getByRole('status').filter({ hasText: 'Scrolly, shaped to you' }),
  ).toBeVisible();
  await page.getByRole('button', { name: 'Settings' }).click();
  await card(page).getByRole('button', { name: 'Skip the tour' }).click();
  await expect(card(page)).toHaveCount(0);
});

test('the last lesson brings Enlightenment, once, and a golden cultivator after', async ({
  page,
}) => {
  await sealDay(page, 'Write report');
  const view = await (await page.request.get('/api/view')).json();
  const total: number = view.knowledge.total;
  const keys = KEYS.filter((k) => k !== 'settings');
  for (const key of keys) await page.request.post('/api/knowledge/learn', { data: { key } });
  expect(keys.length + 1).toBe(total);
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  const ceremony = page.getByRole('dialog', { name: 'Enlightenment' });
  await expect(ceremony).toBeVisible();
  await page.keyboard.press('Shift');
  await ceremony.getByRole('button', { name: 'Return to the path' }).click();
  await expect(ceremony).toHaveCount(0);
  await expect(page.locator('.peak[data-frame="header"]')).toHaveAttribute(
    'data-enlightened',
    'true',
  );
  // The path is walked: nothing of the tour stays on the plate, neither the bar nor a 悟 block.
  await expect(page.getByRole('group', { name: 'Knowledge of the Dao' })).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole('dialog', { name: 'Enlightenment' })).toHaveCount(0);
});

test('Settings walks the path again without unlearning anything', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.request.post('/api/knowledge/pass', { data: { key: 'orbs' } });
  await page.request.post('/api/knowledge/learn', { data: { key: 'timer' } });
  await page.request.put('/api/knowledge', { data: { tour: false } });
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByRole('button', { name: 'Walk the path again' }).click();
  const known = (await (await page.request.get('/api/view')).json()).knowledge;
  expect(known.tour).toBe(true);
  expect(known.learned).toContain('timer');
  expect(known.pending_steps).toContain('orbs');
});

test('a hidden bar shows only for a moment, when it moves', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.request.put('/api/knowledge', { data: { bar_hidden: true, tour: false } });
  await page.goto('/');
  await expect(bar(page)).toHaveCount(0);
  await page.getByRole('button', { name: 'Settings' }).click();
  await expect(bar(page)).toBeVisible();
  await expect(bar(page)).toHaveCount(0, { timeout: 6000 });
});
