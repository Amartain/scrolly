import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

const body = (page: import('@playwright/test').Page, name: string) =>
  section(page, name).locator('.body');

test('an empty list is one quiet line on a plain surface; rows bring the stripes back', async ({
  page,
}) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await expect(body(page, 'Remaining Trials')).toHaveCSS('background-image', 'none');
  await page.request.post('/api/trials', { data: { title: 'Tidy desk' } });
  await page.reload();
  await expect(body(page, 'Remaining Trials')).not.toHaveCSS('background-image', 'none');
});

test('Essence says what fills it before anything is estimated, then shows the figures', async ({
  page,
}) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  const essence = section(page, 'Essence');
  await expect(essence).toContainText('Estimates fill this scroll as you set them.');
  await expect(essence.getByRole('meter')).toHaveCount(0);
  const view = await (await page.request.get('/api/view')).json();
  await page.request.patch(`/api/trials/${view.dashboard.immediate.id}`, {
    data: { estimate: '30m' },
  });
  await page.reload();
  await expect(essence).toContainText('0m of 30m');
  await expect(essence.getByRole('meter')).toBeVisible();
});

test('the clock of the Immediate Trial wears a gold frame while it runs', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  const clock = section(page, 'The Immediate Trial').getByRole('timer');
  await expect(clock).not.toHaveClass(/running/);
  await page.getByRole('button', { name: 'Start timer' }).click();
  await expect(clock).toHaveClass(/running/);
});

test('Essence and Qi: one tile per trial, the conquered ones solid', async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.request.put('/api/golden-core', { data: { enabled: true } });
  const view = await (await page.request.get('/api/view')).json();
  const first = view.dashboard.immediate.id;
  await page.request.patch(`/api/trials/${first}`, { data: { estimate: '30m', qi: '20' } });
  await page.request.post(`/api/trials/${first}/conquer`);
  await page.request.put(`/api/trials/${first}/actual`, { data: { text: '25m' } });
  await page.goto('/');
  const time = section(page, 'Essence').getByRole('meter', { name: 'Essence' });
  await expect(time.locator('.tile')).toHaveCount(2);
  await expect(time.locator('.tile.done')).toHaveCount(1);
  await expect(time.locator('.tile.now')).toHaveCount(1);
  const qi = section(page, 'Essence').getByRole('meter', { name: 'Qi' });
  await expect(qi).toHaveAttribute('aria-valuetext', /20 of 20 · Harmonious/);
  await time.locator('.tile.done').hover();
  await expect(section(page, 'Essence')).toContainText('Write report · 25m (planned 30m)');
});
