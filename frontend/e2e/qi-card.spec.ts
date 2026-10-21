import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

// These tests are about the card itself, so it is not answered for them.
test.use({ autoQi: false });

const card = (page: Page) => page.getByRole('dialog', { name: 'How much qi did this take?' });
const slider = (page: Page) => card(page).getByRole('slider');

async function estimated(page: Page, qi: string) {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.request.put('/api/golden-core', { data: { enabled: true } });
  await page.goto('/');
  const field = page.getByLabel('Qi expected of Write report');
  await field.fill(qi);
  await field.press('Enter');
}

test('A conquest asks how much qi it took, starting at the estimate; Done records the answer', async ({
  page,
}) => {
  await estimated(page, '35');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(card(page)).toBeVisible();
  await expect(slider(page)).toHaveValue('35');
  await slider(page).fill('60');
  await expect(card(page)).toContainText('60 qi');
  await card(page).getByRole('button', { name: 'Done' }).click();
  await expect(card(page)).toHaveCount(0);
  await expect(section(page, 'Conquered Today').getByRole('listitem')).toContainText('60 Qi');
});

test('Closing the card keeps the estimate', async ({ page }) => {
  await estimated(page, '35');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await slider(page).fill('80');
  await page.keyboard.press('Escape');
  await expect(card(page)).toHaveCount(0);
  await expect(section(page, 'Conquered Today').getByRole('listitem')).toContainText('35 Qi');
});

test('The back arrow takes the conquest back', async ({ page }) => {
  await estimated(page, '35');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await card(page).getByRole('button', { name: 'Take the conquest back' }).click();
  await expect(card(page)).toHaveCount(0);
  await expect(section(page, 'Conquered Today').getByRole('listitem')).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Conquer Write report' })).toBeVisible();
});

test('The card asks even when no qi was estimated, starting at zero', async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.goto('/');
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(slider(page)).toHaveValue('0');
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
