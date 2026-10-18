import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';

for (const size of [
  { width: 1280, height: 720 },
  { width: 1440, height: 900 },
]) {
  for (const theme of ['serene', 'pavilion']) {
    test(`planning screens fit one viewport at ${size.width}x${size.height} ${theme}`, async ({
      page,
    }) => {
      await page.request.put('/api/appearance', { data: { theme, day_variant: 'teal' } });
      await page.setViewportSize(size);
      const fits = () =>
        page.evaluate(() => {
          const root = document.documentElement;
          return root.scrollHeight <= innerHeight && root.scrollWidth <= root.clientWidth;
        });
      await page.goto('/');
      await expect(page.getByRole('heading', { name: 'The Peak is Serene' })).toBeVisible();
      expect(await fits(), 'zero state').toBe(true);
      await toEstimateFromZero(page);
      expect(await fits(), 'phase 2').toBe(true);
      await page.getByRole('button', { name: '◀ Back to Inscribing' }).click();
      expect(await fits(), 'phase 1').toBe(true);
    });
  }
}

async function toEstimateFromZero(page: Page) {
  await page.getByRole('button', { name: 'Cultivate Your Focus' }).click();
  await page.locator('#dump').fill('A\nB\nC');
  await page.getByRole('button', { name: 'Proceed: Divine the Time' }).click();
  await expect(page.getByRole('heading', { name: 'Estimate the Journey' })).toBeVisible();
}
