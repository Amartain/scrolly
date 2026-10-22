import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

// These tests are about the card itself, so it is not answered for them.
test.use({ autoQi: false });

const card = (page: Page) => page.getByRole('dialog', { name: 'How much qi did this take?' });
const choice = (page: Page, name: RegExp) => card(page).getByRole('radio', { name });
const number = (page: Page) => card(page).getByRole('textbox', { name: 'Qi it took' });
const conquered = (page: Page) => section(page, 'Conquered Today').getByRole('listitem');

async function estimated(page: Page, qi: string) {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.request.put('/api/golden-core', { data: { enabled: true } });
  await page.goto('/');
  const field = page.getByLabel('Qi expected of Write report');
  await field.fill(qi);
  await field.press('Enter');
}

test('The card opens on As foreseen, so Enter alone keeps the estimate', async ({ page }) => {
  await estimated(page, '40');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(choice(page, /As foreseen/)).toBeChecked();
  await expect(choice(page, /As foreseen/)).toBeFocused();
  // Each choice carries its number: half the estimate and half again.
  await expect(card(page)).toContainText(/Lighter\s*20/);
  await expect(card(page)).toContainText(/Heavier\s*60/);
  await page.keyboard.press('Enter');
  await expect(card(page)).toHaveCount(0);
  await expect(conquered(page)).toContainText('40 Qi');
});

test('Heavier is one press, and the day shows where it lands before Done', async ({ page }) => {
  await estimated(page, '40');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await choice(page, /Heavier/).check();
  await expect(number(page)).toHaveValue('60');
  await expect(card(page)).toContainText('40 → 60 · Harmonious');
  await card(page).getByRole('button', { name: 'Done' }).click();
  await expect(conquered(page)).toContainText('60 Qi');
});

test('A number can be typed and entered by hand', async ({ page }) => {
  await estimated(page, '40');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await number(page).fill('73');
  await expect(card(page)).toContainText('40 → 73');
  await expect(card(page).getByRole('radio', { checked: true })).toHaveCount(0);
  await number(page).press('Enter');
  await expect(card(page)).toHaveCount(0);
  await expect(conquered(page)).toContainText('73 Qi');
});

test('Closing the card keeps the estimate', async ({ page }) => {
  await estimated(page, '35');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await number(page).fill('80');
  await page.keyboard.press('Escape');
  await expect(card(page)).toHaveCount(0);
  await expect(conquered(page)).toContainText('35 Qi');
});

test('Take it back undoes the conquest', async ({ page }) => {
  await estimated(page, '35');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await card(page).getByRole('button', { name: 'Take the conquest back' }).click();
  await expect(card(page)).toHaveCount(0);
  await expect(conquered(page)).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Conquer Write report' })).toBeVisible();
});

test('The card asks even when no qi was estimated, starting at zero', async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.goto('/');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(number(page)).toHaveValue('0');
  await card(page).getByRole('button', { name: 'Done' }).click();
  await expect(card(page)).toHaveCount(0);
});

test('In Seclusion the card comes first, then What next', async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  const room = section(page, 'Focus Scroll');
  await room.getByRole('button', { name: 'Start', exact: true }).click();
  await room.getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(card(page)).toBeVisible();
  await card(page).getByRole('button', { name: 'Done' }).click();
  await expect(card(page)).toHaveCount(0);
  await expect(room.getByRole('group', { name: 'What next?' })).toBeVisible();
});
