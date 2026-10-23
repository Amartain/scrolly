import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay } from './helpers';

// The peak behind Seclusion (owner, 2026-10-23): the gate summons it (painted in), ↑ climbs to it
// (washed in from the foot), the cultivator at the foot of the path until a timer starts, a climb
// while it runs, then seated. A focus started in the room, or a way up within the interval: no show.
// Another theme repaints, here and on the landing page.

const scene = (page: Page) => page.locator('.peak');
const figure = (page: Page) => scene(page).locator('.figure');

async function enter(page: Page) {
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await expect(page.locator('.peak[data-frame="room"]')).toBeVisible();
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

test('a timer started on the dashboard still gets the summon; with the interval at 0 ↑ climbs again', async ({
  page,
}) => {
  await sealDay(page, 'Write report');
  await page.request.put('/api/travel', { data: { interval_min: 0 } });
  await page.goto('/');
  await page.locator('body').click({ position: { x: 5, y: 5 } });
  await page.keyboard.press('Space');
  await expect(page.getByRole('button', { name: 'Pause timer' })).toBeVisible();
  await page.keyboard.press('f');
  await expect(scene(page)).toHaveClass(/painting/);
  await page.keyboard.press('Shift');
  await page.getByRole('button', { name: 'Pause timer' }).click();
  await expect(page.getByRole('button', { name: 'Pause timer' })).toHaveCount(0);
  await page.keyboard.press('ArrowDown');
  await expect(scene(page)).toHaveAttribute('data-frame', 'header');
  await page.keyboard.press('ArrowUp');
  await expect(scene(page)).toHaveClass(/rising/);
});

test('the first full way up ends with the welcome scroll, once', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.request.put('/api/travel', { data: { welcomed: false } });
  await page.goto('/');
  await enter(page);
  await page.keyboard.press('Shift');
  const welcome = page.getByRole('dialog', { name: /Seclusion · 閉關/ });
  await expect(welcome).toBeVisible();
  await welcome.getByRole('button', { name: 'Roll Up Guidance Scroll' }).click();
  await page.keyboard.press('Escape');
  await expect(scene(page)).toHaveAttribute('data-frame', 'header');
  await page.request.put('/api/travel', { data: { interval_min: 0 } });
  await page.reload();
  await enter(page);
  await page.keyboard.press('Shift');
  await expect(page.getByRole('dialog')).toHaveCount(0);
});

test('a key shows the painting at once; another theme paints its own peak', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await enter(page);
  await expect(scene(page)).toHaveClass(/painting/);
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
