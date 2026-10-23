import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay } from './helpers';

// The player (owner, 2026-10-23): [ Yes ] on the Arise window makes a player; the first time the
// System rewards the quest (blue robes, blue glow) in the same window; Settings › Aura picks colours.

const system = (page: Page) => page.getByRole('dialog', { name: 'System notification' });
const header = (page: Page) => page.locator('.peak[data-frame="header"]');

async function arise(page: Page) {
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByLabel('Secret seal words').fill('arise');
  await page.keyboard.press('Enter');
  await expect(system(page)).toBeVisible();
}

test.beforeEach(async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
});

test('Yes makes a player: the System rewards the quest, and the robe turns blue', async ({
  page,
}) => {
  await arise(page);
  await system(page).getByRole('button', { name: '[ Yes ]' }).first().click();
  await expect(system(page)).toContainText('[ QUEST COMPLETED ]');
  await expect(system(page)).toContainText('Settings › Aura');
  await system(page).getByRole('button', { name: '[ Confirm ]' }).click();
  await expect(system(page)).toHaveCount(0);
  await expect(header(page)).toHaveAttribute('data-robe', 'own');
  await expect(header(page)).toHaveAttribute('data-shining', 'true');
});

test('Esc is not a Yes: no player, no Aura in Settings', async ({ page }) => {
  await arise(page);
  await page.keyboard.press('Escape');
  await expect(system(page)).toHaveCount(0);
  await page.getByRole('button', { name: 'Settings' }).click();
  await expect(page.getByRole('heading', { name: 'Aura' })).toHaveCount(0);
});

test('a player picks robe and glow orbs in Settings, and can let the theme dress them again', async ({
  page,
}) => {
  await page.request.post('/api/player/accept');
  await page.reload();
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByRole('button', { name: 'Robe: Jade' }).click();
  await expect(page.getByRole('button', { name: 'Robe: Jade' })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
  await page.getByRole('button', { name: "Robe: The theme's own" }).click();
  await page.getByLabel('Let the aura shine always').uncheck();
  await page.getByRole('button', { name: 'Settings' }).click();
  await expect(header(page)).not.toHaveAttribute('data-robe', 'own');
  await expect(header(page)).toHaveAttribute('data-glow', 'own'); // still the System's blue glow
  await expect(header(page)).toHaveAttribute('data-shining', 'false');
});
