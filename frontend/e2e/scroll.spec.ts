import { expect, test } from '@playwright/test';
import { resetTheme } from './helpers';

const SIZES = [
  { width: 1280, height: 720 },
  { width: 1440, height: 900 },
];
const THEMES = [
  { theme: 'serene', day_variant: 'teal' },
  { theme: 'pavilion', day_variant: 'teal' },
];

const QUIET = [
  'Essence',
  'Lifetime Conquered',
  'Heavenly Cycles',
  'Cumulative Momentum',
  'Rhythm',
  'Scribe Trial',
  'Postponed Today',
  'Fallen Leaves',
];
const LISTS = [
  'The Immediate Trial',
  'Conquered Today',
  'Remaining Trials',
  'Foundational Arts',
  'Restorative Arts',
  'The Horizon',
];

test.afterEach(async ({ page }) => resetTheme(page));

for (const size of SIZES) {
  for (const choice of THEMES) {
    test(`scrolling only in list panels at ${size.width}x${size.height} ${choice.theme}`, async ({
      page,
    }) => {
      await page.request.put('/api/appearance', { data: choice });
      await page.setViewportSize(size);
      await page.goto('/');
      await expect(page.getByRole('button', { name: 'Settings' })).toBeVisible();

      const body = (name: string) => page.locator(`section[aria-label="${name}"] > .body`);
      for (const name of QUIET) {
        const el = body(name);
        await expect(el).toHaveCSS('overflow-y', 'hidden');
        const fits = await el.evaluate((node) => node.scrollHeight <= node.clientHeight);
        expect(fits, `${name} overflows its frame`).toBe(true);
      }
      for (const name of LISTS) await expect(body(name)).toHaveCSS('overflow-y', 'auto');
    });
  }
}

test('fold button and arrow keys move between the two screens', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  const scrollY = () => page.evaluate(() => Math.round(window.scrollY));

  await page.getByRole('button', { name: /the planning peak/i }).click();
  await expect.poll(scrollY).toBe(900);

  await page.keyboard.press('ArrowUp');
  await expect.poll(scrollY).toBe(0);

  await page.keyboard.press('ArrowDown');
  await expect.poll(scrollY).toBe(900);
});

test('fold button also works with motion allowed', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.goto('/');
  await page.getByRole('button', { name: /the planning peak/i }).click();
  await expect.poll(() => page.evaluate(() => Math.round(window.scrollY))).toBe(900);
});
