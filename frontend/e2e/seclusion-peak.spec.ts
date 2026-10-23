import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay } from './helpers';

// The peak behind Seclusion (owner, 2026-10-23): painted in on entering, the cultivator at the foot of
// the path until Start, a climb while the timer runs, then seated. Coming back while it runs: seated,
// nothing painted again. Another theme repaints, here and on the landing page.

const scene = (page: Page) => page.locator('.peak');
const figure = (page: Page) => scene(page).locator('.figure');

async function enter(page: Page) {
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await expect(scene(page)).toBeVisible();
}

test('the cultivator waits at the foot, climbs once Start is pressed, then sits', async ({
  page,
}) => {
  await page.clock.install();
  await sealDay(page, 'Write report');
  await page.goto('/');
  await enter(page);
  await expect(scene(page)).toHaveClass(/rising/);
  await expect(figure(page)).toHaveAttribute('data-pose', 'walk');
  await page.getByRole('button', { name: 'Start', exact: true }).click();
  // The climb begins once the server says the timer runs; wait for that before moving the clock.
  await expect(page.getByRole('button', { name: 'Pause timer' })).toBeVisible();
  await page.clock.runFor(5_000);
  await expect(figure(page)).toHaveAttribute('data-pose', 'walk');
  await expect(scene(page)).not.toHaveClass(/rising/);
  await page.clock.runFor(11_000);
  await expect(figure(page)).toHaveAttribute('data-pose', 'sit');
});

test('stepping out and back finds them seated, in the header too, with nothing painted', async ({
  page,
}) => {
  await page.clock.install();
  await sealDay(page, 'Write report');
  await page.goto('/');
  await enter(page);
  await page.getByRole('button', { name: 'Start', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Pause timer' })).toBeVisible();
  await page.clock.runFor(16_000);
  await page.getByRole('button', { name: 'Pause timer' }).click();
  await page.getByRole('button', { name: 'Step out' }).click();
  await expect(page.locator('.peak[data-frame="header"] .figure')).toHaveAttribute(
    'data-pose',
    'sit',
  );
  await enter(page);
  await expect(figure(page)).toHaveAttribute('data-pose', 'sit');
  await expect(scene(page)).not.toHaveClass(/painting/);
});

test('in the header the dashboard timer sends them up, and the last conquest walks them down', async ({
  page,
}) => {
  const header = page.locator('.peak[data-frame="header"]');
  await page.clock.install();
  await sealDay(page, 'Write report');
  await page.goto('/');
  await expect(header).toHaveAttribute('data-stage', 'foot');
  await page.locator('body').click({ position: { x: 5, y: 5 } });
  await page.keyboard.press('Space');
  await expect(header).toHaveAttribute('data-stage', 'climbing');
  await page.clock.runFor(16_000);
  await expect(header).toHaveAttribute('data-stage', 'seated');
  await page.keyboard.press('Space');
  await page.keyboard.press('Enter');
  await expect(header).toHaveAttribute('data-stage', 'descending');
  await page.clock.runFor(11_000);
  await expect(header).toHaveAttribute('data-stage', 'foot');
});

test('↑ climbs to Seclusion painted upward, ↓ comes back, and soon after ↑ only opens', async ({
  page,
}) => {
  await page.clock.install();
  await sealDay(page, 'Write report');
  await page.goto('/');
  await expect(page.locator('.peak[data-frame="header"]')).toBeVisible();
  await page.locator('body').click({ position: { x: 5, y: 5 } });
  await page.keyboard.press('ArrowUp');
  await expect(scene(page)).toHaveAttribute('data-frame', 'room');
  await expect(scene(page)).toHaveClass(/rising/);
  await page.clock.runFor(5_000);
  await page.keyboard.press('ArrowDown');
  await expect(scene(page)).toHaveAttribute('data-frame', 'header');
  await page.keyboard.press('ArrowUp');
  await expect(scene(page)).toHaveAttribute('data-frame', 'room');
  await expect(scene(page)).not.toHaveClass(/rising|painting/);
});

test('a key shows the painting at once; another theme paints its own peak', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await enter(page);
  await expect(scene(page)).toHaveClass(/rising/);
  await page.keyboard.press('Shift');
  await expect(scene(page)).not.toHaveClass(/rising|painting/);
  await page.getByRole('button', { name: 'Hidden Pavilion teal theme' }).click();
  await expect(scene(page)).toHaveAttribute('data-scene', 'pavilion');
  await expect(scene(page)).toHaveClass(/painting/);
});

test('on the landing page another theme paints its own morning, even after a skip', async ({
  page,
}) => {
  await page.goto('/');
  const morning = page.locator('.morning');
  await expect(page.getByRole('button', { name: 'Cultivate Your Focus' })).toBeVisible();
  await page.keyboard.press('Shift');
  await expect(morning).toHaveClass(/still/);
  await page.getByRole('button', { name: 'Hidden Pavilion teal theme' }).click();
  await expect(morning).toHaveAttribute('data-scene', 'pavilion');
  await expect(morning).not.toHaveClass(/still/);
});
