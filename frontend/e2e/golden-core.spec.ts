import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealAndClose, sealDay, toEstimate } from './helpers';

const view = async (page: Page) => (await page.request.get('/api/view')).json();

async function toWeigh(page: Page, ...lines: string[]) {
  await toEstimate(page, ...lines);
  await page.getByRole('button', { name: 'Awaken the Golden Core' }).click();
  await page.getByRole('button', { name: 'Proceed: Weigh the Qi' }).click();
  await expect(page.getByRole('heading', { name: 'Weigh the Qi' })).toBeVisible();
}

async function setQi(page: Page, title: string, qi: string) {
  const field = page.getByLabel(`Qi cost of ${title}`);
  await field.fill(qi);
  await field.press('Enter');
  await expect(field).toHaveValue(qi);
}

test('the invitation is offered once and "Perhaps later" retires it for good', async ({ page }) => {
  await toEstimate(page, 'Write report');
  await expect(page.getByRole('button', { name: 'Seal Scroll and Commence' })).toBeVisible();
  await page.getByRole('button', { name: 'Perhaps later' }).click();
  await expect(page.getByRole('button', { name: 'Perhaps later' })).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Estimate the Journey' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Awaken the Golden Core' })).toHaveCount(0);
  expect((await view(page)).planning.qi).toMatchObject({ enabled: false, invited: true });
});

test('awakening the Golden Core adds a phase to weigh the Qi, then seals', async ({ page }) => {
  await toWeigh(page, 'Write report', 'Tidy desk');
  await expect(page.getByRole('banner')).toHaveCount(0);
  await setQi(page, 'Write report', '60');
  await setQi(page, 'Tidy desk', '30');
  const gauge = page.getByRole('meter');
  await expect(gauge).toHaveAttribute('aria-valuenow', '90');
  // 10 Qi unspent comes back as a bonus.
  await expect(page.getByText("tomorrow's core begins at")).toContainText('110 Qi');
  await sealAndClose(page);
  await expect(page.getByRole('heading', { name: 'The Immediate Trial' })).toBeVisible();
  expect((await view(page)).planning.qi.start).toBe(100);
});

test('the core slider lowers the start with the keyboard', async ({ page }) => {
  await toWeigh(page, 'Write report');
  const slider = page.getByRole('slider');
  await slider.focus();
  await page.keyboard.press('ArrowLeft');
  await page.keyboard.press('ArrowLeft');
  await expect.poll(async () => (await view(page)).planning.qi.start).toBe(98);
  await expect(page.getByText('Your core begins at')).toContainText('98');
});

test('a bad Qi is explained quietly and the field goes back', async ({ page }) => {
  await toWeigh(page, 'Write report');
  const field = page.getByLabel('Qi cost of Write report');
  await field.fill('lots');
  await field.press('Enter');
  await expect(page.getByRole('status')).toContainText('whole number');
  await expect(field).toHaveValue('');
});

test('planning past the redline is allowed and says how tomorrow begins', async ({ page }) => {
  await toWeigh(page, 'One', 'Two', 'Three');
  await setQi(page, 'One', '100');
  await setQi(page, 'Two', '100');
  await setQi(page, 'Three', '5');
  await expect(page.getByText("tomorrow's core begins at")).toContainText('10 Qi');
  await sealAndClose(page);
  await expect(page.getByRole('heading', { name: 'The Immediate Trial' })).toBeVisible();
});

test('Back to Estimating keeps the Qi, and Settings switches the Golden Core off', async ({
  page,
}) => {
  await toWeigh(page, 'Write report');
  await setQi(page, 'Write report', '40');
  await page.getByRole('button', { name: '◀ Back to Estimating' }).click();
  await expect(page.getByRole('heading', { name: 'Estimate the Journey' })).toBeVisible();
  await page.getByRole('button', { name: 'Proceed: Weigh the Qi' }).click();
  await expect(page.getByLabel('Qi cost of Write report')).toHaveValue('40');
  await sealAndClose(page);
  await expect(page.getByRole('heading', { name: 'The Immediate Trial' })).toBeVisible();
  await page.getByRole('button', { name: 'Settings' }).click();
  const toggle = page.getByLabel('Weigh Qi while planning');
  await expect(toggle).toBeChecked();
  await toggle.uncheck();
  await expect.poll(async () => (await view(page)).planning.qi.enabled).toBe(false);
});

test('Settings can awaken the Golden Core', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByLabel('Weigh Qi while planning').check();
  await expect.poll(async () => (await view(page)).planning.qi.enabled).toBe(true);
});

for (const size of [
  { width: 1280, height: 720 },
  { width: 1440, height: 900 },
]) {
  for (const theme of ['serene', 'pavilion']) {
    test(`Phase 3 fits one viewport at ${size.width}x${size.height} ${theme}`, async ({ page }) => {
      await page.request.put('/api/appearance', { data: { theme, day_variant: 'crimson' } });
      await page.setViewportSize(size);
      await toWeigh(page, 'A', 'B', 'C');
      const fits = await page.evaluate(() => {
        const root = document.documentElement;
        return root.scrollHeight <= innerHeight && root.scrollWidth <= root.clientWidth;
      });
      expect(fits).toBe(true);
      const sheet = await page.locator('section[aria-label="Weigh the Qi"]').boundingBox();
      expect(sheet!.y).toBeGreaterThan(0);
      expect(sheet!.y + sheet!.height).toBeLessThanOrEqual(size.height);
    });
  }
}

test('conquered Qi fills the gauge on the dashboard', async ({ page }) => {
  await toWeigh(page, 'Write report', 'Tidy desk');
  await setQi(page, 'Write report', '60');
  await sealAndClose(page);
  const gauge = page.locator('section[aria-label="Essence"]').getByRole('meter', { name: 'Qi' });
  await expect(gauge).toHaveAttribute('aria-valuetext', /^0 of \d+/);
  const body = page.locator('section[aria-label="Essence"] .body');
  expect(await body.evaluate((node) => node.scrollHeight <= node.clientHeight)).toBe(true);
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(gauge).toHaveAttribute('aria-valuetext', /^60 of \d+/);
  await page.getByRole('button', { name: 'Revive Write report' }).click();
  await expect(gauge).toHaveAttribute('aria-valuetext', /^0 of \d+/);
});
