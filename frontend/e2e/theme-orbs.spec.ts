import { expect, test } from './fixtures';
import type { Page } from '@playwright/test';
import { begin, sealDay, toEstimate } from './helpers';

const crimson = 'Hidden Pavilion crimson theme';
const teal = 'Hidden Pavilion teal theme';
const serene = 'Serene Peak theme';

const root = (page: Page) => page.locator('html');

test('the zero state and every planning phase show three unlabelled orbs', async ({ page }) => {
  await page.goto('/');
  for (const name of [serene, teal, crimson]) {
    await expect(page.getByRole('button', { name })).toBeVisible();
  }
  await page.getByRole('button', { name: 'Cultivate Your Focus' }).click();
  await expect(page.getByRole('button', { name: crimson })).toBeVisible();
  await page.locator('#dump').fill('Write the report');
  await page.getByRole('button', { name: 'Proceed: Divine the Time' }).click();
  await expect(page.getByRole('heading', { name: 'Estimate the Journey' })).toBeVisible();
  await expect(page.getByRole('button', { name: serene })).toBeVisible();
  await expect(page.getByRole('button', { name: serene })).toHaveText('');
});

test('clicking an orb switches the theme at once', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: crimson }).click();
  await expect(root(page)).toHaveAttribute('data-theme', 'pavilion');
  await expect(root(page)).toHaveAttribute('data-day-variant', 'crimson');
  await expect(page.getByRole('button', { name: crimson })).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('button', { name: teal }).click();
  await expect(root(page)).toHaveAttribute('data-day-variant', 'teal');
  await page.getByRole('button', { name: serene }).click();
  await expect(root(page)).toHaveAttribute('data-theme', 'serene');
});

test('an orb can be reached and used with the keyboard', async ({ page }) => {
  await begin(page);
  const orb = page.getByRole('button', { name: teal });
  await orb.focus();
  await page.keyboard.press('Enter');
  await expect(root(page)).toHaveAttribute('data-day-variant', 'teal');
});

test('the orbs stay inside the viewport and keep typed text', async ({ page }) => {
  await begin(page);
  await page.locator('#dump').fill('Keep this line');
  await page.getByRole('button', { name: crimson }).click();
  await expect(page.locator('#dump')).toHaveValue('Keep this line');
  const box = await page.getByRole('button', { name: crimson }).boundingBox();
  const size = page.viewportSize();
  expect(box && size && box.x + box.width <= size.width && box.y + box.height <= size.height).toBe(
    true,
  );
});

test('the dashboard and Settings have no orbs', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  await expect(page.getByRole('banner')).toBeVisible();
  await expect(page.getByRole('button', { name: serene })).toHaveCount(0);
  await page.getByRole('button', { name: 'Settings' }).click();
  await expect(page.getByRole('button', { name: serene })).toHaveCount(0);
});

test('Phase 2 has the orbs too', async ({ page }) => {
  await toEstimate(page, 'One trial');
  await expect(page.getByRole('button', { name: teal })).toBeVisible();
});
