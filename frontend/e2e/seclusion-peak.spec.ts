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
  await expect(scene(page)).toHaveClass(/painting/);
  await expect(figure(page)).toHaveAttribute('data-pose', 'walk');
  await page.getByRole('button', { name: 'Start', exact: true }).click();
  // The climb begins once the server says the timer runs; wait for that before moving the clock.
  await expect(page.getByRole('button', { name: 'Pause timer' })).toBeVisible();
  await page.clock.runFor(5_000);
  await expect(figure(page)).toHaveAttribute('data-pose', 'walk');
  await expect(scene(page)).not.toHaveClass(/painting/);
  await page.clock.runFor(11_000);
  await expect(figure(page)).toHaveAttribute('data-pose', 'sit');
});

test('stepping out and back while the timer runs finds them seated, with nothing painted', async ({
  page,
}) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await enter(page);
  await page.getByRole('button', { name: 'Start', exact: true }).click();
  await page.getByRole('button', { name: 'Step out' }).click();
  await enter(page);
  await expect(figure(page)).toHaveAttribute('data-pose', 'sit');
  await expect(scene(page)).not.toHaveClass(/painting/);
});

test('a key shows the painting at once; another theme paints its own peak', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await enter(page);
  await page.keyboard.press('Shift');
  await expect(scene(page)).not.toHaveClass(/painting/);
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
