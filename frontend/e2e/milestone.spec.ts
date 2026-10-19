import { expect, test } from './fixtures';
import { toEstimate } from './helpers';

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

test('a click on the backdrop closes the milestone', async ({ page }) => {
  await seal(page);
  const overlay = page.getByRole('dialog', { name: 'Heavenly Cycles' });
  await expect(overlay).toBeVisible();
  await page.mouse.click(4, 4);
  await expect(overlay).toHaveCount(0);
});
