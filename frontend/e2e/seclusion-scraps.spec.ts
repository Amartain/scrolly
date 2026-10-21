import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay } from './helpers';

const pad = (page: Page) => page.getByRole('textbox', { name: 'Bamboo Scraps' });

async function enter(page: Page) {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await expect(pad(page)).toBeVisible();
}

test('What is written saves itself, with a mark, and is there after a reload', async ({ page }) => {
  await enter(page);
  await expect(pad(page)).toHaveAttribute('placeholder', 'Loose thoughts rest here.');
  await pad(page).fill('ask Sam about the invoice');
  await expect(page.getByRole('status').filter({ hasText: 'Saved' })).toBeVisible();
  await page.reload();
  await expect(pad(page)).toHaveValue('ask Sam about the invoice');
});

test('Stepping out saves what was typed at once, and the next visit starts a fresh scrap', async ({
  page,
}) => {
  await enter(page);
  await pad(page).fill('typed and left at once');
  await page.getByRole('button', { name: 'Step out' }).click();
  const kept = await page.request.get('/api/scraps/current');
  expect(await kept.json()).toEqual({ text: '' }); // that visit's scrap is closed
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await expect(pad(page)).toHaveValue('');
});

test('Typing in the scrap does not start or stop the timer', async ({ page }) => {
  await enter(page);
  await pad(page).focus();
  await page.keyboard.type('a b c');
  await expect(pad(page)).toHaveValue('a b c');
  await expect(page.getByRole('button', { name: 'Pause timer' })).toHaveCount(0);
});
