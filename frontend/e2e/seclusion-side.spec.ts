import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { section, sealDay } from './helpers';

// The three release valves share one quiet frame; Bamboo Scraps can be folded away.

const pad = (page: Page) => page.getByRole('textbox', { name: 'Bamboo Scraps' });
const column = (page: Page) =>
  page.locator('.column').filter({ has: section(page, 'Parallel Flow') });

async function enter(page: Page) {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await expect(pad(page)).toBeVisible();
}

test('the valves sit in one frame, and Bamboo Scraps takes the height that is left', async ({
  page,
}) => {
  await enter(page);
  await expect(column(page).locator('section')).toHaveCount(3);
  // No box and no loud header of their own: the labels are small, in the body face.
  await expect(page.locator('section.panel')).toHaveCount(0);
  const frame = (await column(page).boundingBox())!;
  const scraps = (await section(page, 'Bamboo Scraps').boundingBox())!;
  expect(Math.abs(frame.y + frame.height - (scraps.y + scraps.height))).toBeLessThan(8);
  // What is typed is in the pixel face like every other input, and fills the box.
  const font = await pad(page).evaluate((el) => getComputedStyle(el).fontFamily);
  expect(font).toContain('VT323');
  const box = (await pad(page).boundingBox())!;
  expect(box.height).toBeGreaterThan(scraps.height / 2);
});

test('Bamboo Scraps folds away, stays folded after a reload, and keeps what was written', async ({
  page,
}) => {
  await enter(page);
  await pad(page).fill('ask Sam about the invoice');
  await expect(page.getByRole('status').filter({ hasText: 'Saved' })).toBeVisible();

  const hide = page.getByRole('button', { name: 'Hide Bamboo Scraps' });
  await expect(hide).toHaveAttribute('aria-expanded', 'true');
  await hide.focus();
  await page.keyboard.press('Enter');
  await expect(pad(page)).toHaveCount(0);
  const show = page.getByRole('button', { name: 'Show Bamboo Scraps' });
  await expect(show).toHaveAttribute('aria-expanded', 'false');

  await page.reload();
  await expect(show).toBeVisible();
  await expect(pad(page)).toHaveCount(0);

  await show.click();
  await expect(pad(page)).toHaveValue('ask Sam about the invoice');
});
