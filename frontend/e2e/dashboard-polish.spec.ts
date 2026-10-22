import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

const body = (page: import('@playwright/test').Page, name: string) =>
  section(page, name).locator('.body');

// The rem rounds to whole pixels, so the Immediate Trial's slack moves with the window: it once ran
// over by 6px at 1920x950 and showed a scrollbar.
test('the Immediate Trial fits without a scrollbar at every common window size', async ({
  page,
}) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.request.put('/api/golden-core', { data: { enabled: true } });
  const view = await (await page.request.get('/api/view')).json();
  await page.request.patch(`/api/trials/${view.dashboard.immediate.id}`, {
    data: { estimate: '45m', qi: '99', is_mandate: true },
  });
  for (const [width, height] of [
    [1440, 900],
    [1920, 950],
    [1920, 1080],
    [2560, 1300],
  ]) {
    await page.setViewportSize({ width, height });
    await page.goto('/');
    const over = await body(page, 'The Immediate Trial').evaluate(
      (node) => node.scrollHeight - node.clientHeight,
    );
    expect(over, `${width}x${height}`).toBe(0);
  }
});

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
  await expect(essence.getByRole('meter')).toHaveAttribute(
    'aria-valuetext',
    /^0m done · 30m to go/,
  );
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

test('Essence and Qi: done solid, the plan faint, the sunset marked, numbers on hover', async ({
  page,
}) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.request.put('/api/golden-core', { data: { enabled: true } });
  // 03:59 is still ahead at any hour of the logical day (04:00 to 03:59), so the mark always shows.
  await page.request.put('/api/sunset', { data: { enabled: true, at: '03:59' } });
  const view = await (await page.request.get('/api/view')).json();
  const [first, second] = view.planning.trials.map((t: { id: string }) => t.id);
  await page.request.patch(`/api/trials/${first}`, { data: { estimate: '30m', qi: '20' } });
  await page.request.patch(`/api/trials/${second}`, { data: { estimate: '1h', qi: '15' } });
  await page.request.post(`/api/trials/${first}/conquer`);
  await page.request.put(`/api/trials/${first}/actual`, { data: { text: '25m' } });
  await page.goto('/');

  const time = section(page, 'Essence').getByRole('meter', { name: 'Essence' });
  await expect(time).toHaveAttribute('aria-valuetext', /^25m done · 1h to go · .+ of light left$/);
  await expect(time.locator('.sunset')).toHaveCount(1);
  const tip = time.locator('.tip');
  await expect(tip).toHaveCSS('opacity', '0');
  await time.hover();
  await expect(tip).toHaveCSS('opacity', '1');

  const qi = section(page, 'Essence').getByRole('meter', { name: 'Qi' });
  await expect(qi).toHaveAttribute('aria-valuetext', /^20 of \d+ spent · 35 planned · Harmonious$/);
  await expect(qi.locator('.fill')).toHaveAttribute('data-tone', 'harmonious');
  await expect(qi.locator('.plan')).toHaveCount(1);
  await expect(qi.locator('.tick')).toHaveCount(2);

  await page.request.put('/api/sunset', { data: { enabled: false } });
  await page.reload();
  await expect(time.locator('.sunset')).toHaveCount(0);
});
