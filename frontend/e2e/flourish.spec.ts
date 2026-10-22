import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { panelBoxes, sealDay, section } from './helpers';

const effect = (page: Page, kind: string) => page.locator(`[data-flourish="${kind}"]`);
const card = (page: Page) => section(page, 'The Immediate Trial');

test('the first start of a trial lights the incense; going on after a pause does not', async ({
  page,
}) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.goto('/');
  await card(page).getByRole('button', { name: 'Start timer' }).click();
  await expect(effect(page, 'ignite')).toHaveCount(1);
  await expect(effect(page, 'ignite')).toHaveCount(0); // gone by itself
  await card(page).getByRole('button', { name: 'Pause timer' }).click();
  await card(page).getByRole('button', { name: 'Start timer' }).click();
  await expect(card(page).getByRole('button', { name: 'Pause timer' })).toBeVisible();
  await expect(effect(page, 'ignite')).toHaveCount(0);
});

test('a conquest stamps the seal, sends a spark to its row and moves nothing', async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.goto('/');
  const before = await panelBoxes(page);
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(effect(page, 'seal')).toHaveCount(1);
  await expect(effect(page, 'comet')).toHaveCount(1);
  await expect(section(page, 'Conquered Today').getByText('Write report')).toBeVisible();
  // The dashboard's own panels only: under load the Qi card (a pop-up panel) may already be open.
  const after = (await panelBoxes(page)).filter((box) => before.some((b) => b.name === box.name));
  expect(after).toEqual(before);
});

test('the day’s last conquest has the ceremony, not the flourish', async ({ page }) => {
  await sealDay(page, 'Only one');
  await page.goto('/');
  await page.getByRole('button', { name: 'Conquer Only one' }).click();
  await expect(page.getByRole('dialog', { name: 'Another Day Conquered' })).toBeVisible();
  await expect(effect(page, 'seal')).toHaveCount(0);
});

test('under reduced motion nothing flourishes', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.goto('/');
  await card(page).getByRole('button', { name: 'Start timer' }).click();
  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(section(page, 'Conquered Today').getByText('Write report')).toBeVisible();
  await expect(page.locator('[data-flourish]')).toHaveCount(0);
});

test('a conquest in Seclusion stamps the seal on the ring', async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  const room = section(page, 'Focus Scroll');
  await room.getByRole('button', { name: 'Start', exact: true }).click();
  await expect(effect(page, 'ignite')).toHaveCount(1);
  await room.getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(effect(page, 'seal')).toHaveCount(1);
});
