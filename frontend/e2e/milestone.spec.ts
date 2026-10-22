import { expect, test } from './fixtures';
import { sealDay, toEstimate } from './helpers';

const seal = async (page: import('@playwright/test').Page) => {
  await toEstimate(page, 'Write the report');
  await page.getByRole('button', { name: 'Seal Scroll and Commence' }).click();
};

test('sealing the first day shows the milestone once; Esc closes it', async ({ page }) => {
  await seal(page);
  const overlay = page.getByRole('dialog', { name: 'Heavenly Cycles' });
  await expect(overlay).toBeVisible();
  await expect(overlay).toContainText('1');
  await expect(overlay).toContainText('day sealed upon the scroll');
  await expect(overlay.locator('blockquote')).not.toBeEmpty();
  await page.keyboard.press('Escape');
  await expect(overlay).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole('button', { name: 'Settings' })).toBeVisible();
  await expect(page.getByRole('dialog', { name: 'Heavenly Cycles' })).toHaveCount(0);
});

test('the milestone closes with its button or a click outside it', async ({ page }) => {
  await seal(page);
  const overlay = page.getByRole('dialog', { name: 'Heavenly Cycles' });
  await overlay.getByRole('button', { name: 'Onward' }).click();
  await expect(overlay).toHaveCount(0);
});

const arise = async (page: import('@playwright/test').Page) => {
  await sealDay(page);
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByLabel('Secret seal words').fill('arise');
  await page.keyboard.press('Enter');
  return page.getByRole('dialog', { name: 'System notification' });
};

test('Day 100 breaks into a system window; either Yes closes it', async ({ page }) => {
  const window = await arise(page);
  await expect(window).toContainText('[ SYSTEM NOTIFICATION ]');
  await expect(window).toContainText('100');
  await expect(window).toContainText('Dimensional Distortion Detected');
  await expect(window).toContainText('Arise.');
  await expect(window.getByRole('button', { name: '[ Yes ]' })).toHaveCount(2);
  await window.getByRole('button', { name: '[ Yes ]' }).last().click();
  await expect(window).toHaveCount(0);
  await expect(page.getByRole('dialog', { name: 'Heavenly Cycles' })).toHaveCount(0);
});

test('the Day 100 window closes with Esc, and is a plain fade when motion is reduced', async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const window = await arise(page);
  await expect(window).toBeVisible();
  const animation = await window
    .locator('.window')
    .evaluate((node) => getComputedStyle(node).animationName);
  expect(animation).toMatch(/fade$/); // Svelte prefixes keyframe names
  await page.keyboard.press('Escape');
  await expect(window).toHaveCount(0);
});

test('a click on the backdrop closes the milestone', async ({ page }) => {
  await seal(page);
  const overlay = page.getByRole('dialog', { name: 'Heavenly Cycles' });
  await expect(overlay).toBeVisible();
  await page.mouse.click(4, 4);
  await expect(overlay).toHaveCount(0);
});

test('the milestone is a card to read, not a list: no row stripes behind it', async ({ page }) => {
  await seal(page);
  const overlay = page.getByRole('dialog', { name: 'Heavenly Cycles' });
  await expect(overlay.locator('.body')).toHaveCSS('background-image', 'none');
});
