import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { section, sealDay } from './helpers';

// The Parallel sidebar: three cards on one scroll. It folds as a whole, as VS Code's side bar does.

const pad = (page: Page) => page.getByRole('textbox', { name: 'Bamboo Scraps' });
const sidebar = (page: Page) => page.getByRole('complementary', { name: 'Parallel sidebar' });
const strip = (page: Page) => page.getByRole('navigation', { name: 'Parallel sidebar' });

async function enter(page: Page) {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await expect(pad(page)).toBeVisible();
}

test('three cards with header bands sit on one scroll; Bamboo Scraps takes the height left', async ({
  page,
}) => {
  await enter(page);
  await expect(sidebar(page).locator('section')).toHaveCount(3);
  for (const name of ['Parallel Flow', 'Scribe Trial', 'Bamboo Scraps']) {
    await expect(sidebar(page).getByRole('heading', { name })).toBeVisible();
  }
  // Headers are in capitals, as every other header.
  const head = sidebar(page).getByRole('heading', { name: 'Scribe Trial' });
  expect(await head.evaluate((el) => getComputedStyle(el).textTransform)).toBe('uppercase');
  const frame = (await sidebar(page).boundingBox())!;
  const scraps = (await section(page, 'Bamboo Scraps').boundingBox())!;
  expect(frame.y + frame.height - (scraps.y + scraps.height)).toBeLessThan(24);
  const font = await pad(page).evaluate((el) => getComputedStyle(el).fontFamily);
  expect(font).toContain('VT323');
});

test('the whole sidebar folds to a strip, stays folded after a reload, and keeps the scrap', async ({
  page,
}) => {
  await enter(page);
  await pad(page).fill('ask Sam about the invoice');
  await expect(page.getByRole('status').filter({ hasText: 'Saved' })).toBeVisible();
  const card = (await section(page, 'Focus Scroll').boundingBox())!;

  const hide = page.getByRole('button', { name: /Hide the Parallel sidebar/ });
  await expect(hide).toHaveAttribute('aria-expanded', 'true');
  await hide.click();
  await expect(sidebar(page)).toHaveCount(0);
  for (const name of ['Parallel Flow', 'Scribe Trial', 'Bamboo Scraps']) {
    await expect(section(page, name)).toHaveCount(0);
  }
  await expect(strip(page)).toBeVisible();
  // The card stays where it was: the sidebar floats beside it, so folding moves nothing.
  expect(await section(page, 'Focus Scroll').boundingBox()).toEqual(card);

  await page.reload();
  await expect(strip(page)).toBeVisible();
  await page.keyboard.press('Control+b');
  await expect(pad(page)).toHaveValue('ask Sam about the invoice');
  await page.keyboard.press('Control+b');
  await expect(strip(page)).toBeVisible();
});

test('a mark on the strip opens the sidebar on its section; N opens it at Scribe', async ({
  page,
}) => {
  await enter(page);
  await page.getByRole('button', { name: /Hide the Parallel sidebar/ }).click();
  await strip(page).getByRole('button', { name: 'Open Scribe Trial' }).click();
  await expect(page.getByRole('textbox', { name: 'Scribe a sudden trial' })).toBeFocused();

  await page.getByRole('button', { name: /Hide the Parallel sidebar/ }).click();
  await page.keyboard.press('n');
  await expect(page.getByRole('textbox', { name: 'Scribe a sudden trial' })).toBeFocused();
});
