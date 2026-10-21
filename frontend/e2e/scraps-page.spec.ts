import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay } from './helpers';

const pad = (page: Page) => page.getByRole('textbox', { name: 'Bamboo Scraps' });

async function writeOneScrap(page: Page, text: string) {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  const room = page.locator('section[aria-label="Focus Scroll"]');
  await room.getByRole('button', { name: 'Start', exact: true }).click();
  await pad(page).fill(text);
  await page.getByRole('button', { name: 'Step out' }).click();
}

async function openPage(page: Page) {
  await page.keyboard.press('ArrowDown'); // the second screen, where the link lives
  await page.getByRole('button', { name: 'Bamboo Scraps' }).click();
}

test('The page shows each kept scrap with its day, hours, trials and text, and nothing to edit', async ({
  page,
}) => {
  await writeOneScrap(page, 'ask Sam about the invoice');
  await openPage(page);
  await expect(page.getByRole('heading', { name: 'Bamboo Scraps', level: 1 })).toBeVisible();
  const scrap = page.getByRole('article');
  await expect(scrap).toHaveCount(1);
  await expect(scrap.getByRole('heading', { level: 2 })).toContainText(/\w+day, \d+ \w+ \d{4}/);
  await expect(scrap.getByRole('list', { name: 'Trials worked' })).toContainText('Write report');
  await expect(scrap).toContainText('ask Sam about the invoice');
  await expect(page.getByRole('textbox')).toHaveCount(0);
});

test('A scrap that was left empty is not on the page', async ({ page }) => {
  await writeOneScrap(page, '   ');
  await openPage(page);
  await expect(page.getByText('No scraps yet.')).toBeVisible();
  await expect(page.getByRole('article')).toHaveCount(0);
});

test('Export as Markdown downloads one file', async ({ page }) => {
  await writeOneScrap(page, 'for my notes');
  await openPage(page);
  const download = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Export as Markdown' }).click();
  expect((await download).suggestedFilename()).toMatch(/^bamboo-scraps-\d{4}-\d{2}-\d{2}\.md$/);
});

test('Back returns to the dashboard', async ({ page }) => {
  await writeOneScrap(page, 'x');
  await openPage(page);
  await page.getByRole('button', { name: 'Back' }).click();
  await expect(page.getByRole('heading', { name: 'Bamboo Scraps', level: 1 })).toHaveCount(0);
});
