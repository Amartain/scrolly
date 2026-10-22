import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

const ceremony = (page: Page) =>
  page.getByRole('dialog', { name: /Tribulation Weathered|Another Day Conquered/ });
const close = (page: Page) => page.getByRole('button', { name: 'Sheathe the Sword' });

async function conquerTheOnlyTrial(page: Page, mandate = false) {
  await sealDay(page, 'Only one');
  if (mandate) {
    const view = await (await page.request.get('/api/view')).json();
    const id = view.dashboard.immediate.id;
    await page.request.patch(`/api/trials/${id}`, { data: { is_mandate: true } });
  }
  await page.goto('/');
  await page.getByRole('button', { name: 'Conquer Only one' }).click();
}

async function inscribe(page: Page, words: string) {
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByLabel('Secret seal words').fill(words);
  await page.keyboard.press('Enter');
}

test('a day that conquered a Mandate ends in thunder; Sheathe the Sword leaves the banner', async ({
  page,
}) => {
  await conquerTheOnlyTrial(page, true);
  await expect(page.getByRole('dialog', { name: 'Tribulation Weathered' })).toBeVisible();
  await expect(page.locator('.thunder-scene')).toBeVisible();
  await expect(ceremony(page).getByText('Trials conquered')).toBeVisible();
  await close(page).click();
  await expect(ceremony(page)).toHaveCount(0);
  await expect(page.getByRole('heading', { name: 'Tribulation Weathered' })).toBeVisible();
});

test('a day of Mortal trials gets Another Day Conquered, without the storm', async ({ page }) => {
  await conquerTheOnlyTrial(page);
  await expect(page.getByRole('dialog', { name: 'Another Day Conquered' })).toBeVisible();
  await expect(page.locator('.thunder-scene')).toHaveCount(0);
});

test('the ceremony does not come back on reload', async ({ page }) => {
  await conquerTheOnlyTrial(page);
  await close(page).click();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Another Day Conquered' })).toBeVisible();
  await expect(ceremony(page)).toHaveCount(0);
});

test('the seal tribulation previews the thunder on a day not yet won, and stores nothing', async ({
  page,
}) => {
  await sealDay(page, 'Still open');
  await page.goto('/');
  await inscribe(page, 'tribulation');
  await expect(page.getByRole('dialog', { name: 'Tribulation Weathered' })).toBeVisible();
  await expect(page.locator('.thunder-scene')).toBeVisible();
  await close(page).click();
  await expect(ceremony(page)).toHaveCount(0);
  await page.reload();
  await expect(ceremony(page)).toHaveCount(0);
  await expect(section(page, 'The Immediate Trial')).toContainText('Still open');
});

test('a key before the end skips to the last frame, and Esc closes', async ({ page }) => {
  await conquerTheOnlyTrial(page, true);
  await expect(ceremony(page)).toBeVisible();
  await page.keyboard.press('x');
  await expect(close(page)).toBeFocused();
  await expect(page.locator('.thunder-scene')).toHaveClass(/still/);
  await expect(ceremony(page).getByText('Lifetime conquered')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(ceremony(page)).toHaveCount(0);
});

test('under reduced motion the last frame shows at once', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await conquerTheOnlyTrial(page, true);
  await expect(close(page)).toBeFocused();
  await expect(page.locator('.thunder-scene')).toHaveClass(/still/);
});

test('the sunset poem waits for the ceremony', async ({ page }) => {
  await conquerTheOnlyTrial(page);
  await expect(page.getByRole('dialog', { name: 'Sunset Poem' })).toHaveCount(0);
  await close(page).click();
  await expect(page.getByRole('dialog', { name: 'Sunset Poem' })).toBeVisible();
});

test('the last trial conquered in Seclusion plays the ceremony over the room', async ({ page }) => {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  const room = section(page, 'Focus Scroll');
  await room.getByRole('button', { name: 'Start', exact: true }).click();
  await room.getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(ceremony(page)).toBeVisible();
  await close(page).click();
  await expect(page.getByText('closed-door cultivation is complete')).toBeVisible();
});
