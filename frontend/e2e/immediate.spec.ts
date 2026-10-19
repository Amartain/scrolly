import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

const immediate = (page: import('@playwright/test').Page) => section(page, 'The Immediate Trial');
const clock = (page: import('@playwright/test').Page) => immediate(page).getByRole('timer');

test.beforeEach(async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.goto('/');
});

test('the timer starts, pauses and keeps its time across a reload', async ({ page }) => {
  await expect(clock(page)).toHaveText('00:00:00');
  await immediate(page).getByRole('button', { name: 'Start timer' }).click();
  await expect(clock(page)).not.toHaveText('00:00:00');
  await immediate(page).getByRole('button', { name: 'Pause timer' }).click();
  const paused = (await clock(page).textContent()) ?? '';
  await page.waitForTimeout(1500);
  await expect(clock(page)).toHaveText(paused);
  await page.reload();
  await expect(clock(page)).toHaveText(paused);
});

test('a running timer keeps counting while the page is reloaded', async ({ page }) => {
  await immediate(page).getByRole('button', { name: 'Start timer' }).click();
  await page.reload();
  await expect(immediate(page).getByRole('button', { name: 'Pause timer' })).toBeVisible();
  await expect(clock(page)).not.toHaveText('00:00:00');
});

test('a postponed trial keeps its worked time when it is summoned again', async ({ page }) => {
  await immediate(page).getByRole('button', { name: 'Start timer' }).click();
  await expect(clock(page)).not.toHaveText('00:00:00');
  await page.getByRole('button', { name: 'Postpone Write report to the Horizon' }).click();
  await expect(immediate(page)).toContainText('Tidy desk');

  await page.getByRole('button', { name: 'Summon Write report' }).click();
  await page.getByRole('button', { name: 'Promote Write report' }).click();
  await expect(immediate(page)).toContainText('Write report');
  await expect(clock(page)).not.toHaveText('00:00:00');
});

test('reset stops and zeroes the timer', async ({ page }) => {
  await immediate(page).getByRole('button', { name: 'Start timer' }).click();
  await expect(clock(page)).not.toHaveText('00:00:00');
  await immediate(page).getByRole('button', { name: 'Reset timer' }).click();
  await expect(clock(page)).toHaveText('00:00:00');
  await expect(immediate(page).getByRole('button', { name: 'Start timer' })).toBeVisible();
});

test('Space starts and pauses, Enter conquers', async ({ page }) => {
  await page.locator('body').click({ position: { x: 5, y: 5 } });
  await page.keyboard.press('Space');
  await expect(immediate(page).getByRole('button', { name: 'Pause timer' })).toBeVisible();
  await page.keyboard.press('Space');
  await expect(immediate(page).getByRole('button', { name: 'Start timer' })).toBeVisible();
  await page.keyboard.press('Enter');
  await expect(section(page, 'Conquered Today').getByText('Write report')).toBeVisible();
  await expect(immediate(page).getByText('Tidy desk')).toBeVisible();
});

test('the title is renamed by double-click or from the keyboard', async ({ page }) => {
  await immediate(page).getByText('Write report').dblclick();
  const field = immediate(page).getByLabel('Trial title');
  await field.fill('Write the README');
  await field.press('Enter');
  await expect(immediate(page).getByText('Write the README')).toBeVisible();

  await immediate(page).getByRole('button', { name: 'Write the README', exact: true }).focus();
  await page.keyboard.press('Enter');
  await immediate(page).getByLabel('Trial title').fill('Ship it');
  await page.keyboard.press('Escape');
  await expect(immediate(page).getByText('Write the README')).toBeVisible();
});
