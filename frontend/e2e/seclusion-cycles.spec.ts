import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

const room = (page: Page) => section(page, 'Focus Scroll');
const ring = (page: Page) => room(page).locator('.ring[data-tone]');
const button = (page: Page, name: string) => room(page).getByRole('button', { name, exact: true });
const field = (page: Page, name: string) => room(page).getByRole('textbox', { name, exact: true });

async function enterOn(page: Page, tab: string, ...titles: string[]) {
  await sealDay(page, ...titles);
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await room(page).getByRole('tab', { name: tab }).click();
  await expect(room(page).getByRole('tab', { name: tab })).toHaveAttribute('aria-selected', 'true');
}

test('Cycles: the ring is a dial, set by keys, then the break, then the cycles, then Start', async ({
  page,
}) => {
  await enterOn(page, 'Harmonious Cycles', 'Write report');
  const focus = room(page).getByRole('slider', { name: 'How long shall you cultivate?' });
  await expect(focus).toHaveValue('45');
  await expect(ring(page)).toHaveAttribute('data-tone', 'cycles');
  await focus.focus();
  await page.keyboard.press('PageUp');
  await page.keyboard.press('ArrowLeft');
  await expect(focus).toHaveValue('49');
  await button(page, 'Next').click();

  const rest = room(page).getByRole('slider', { name: 'How long shall the Qi settle?' });
  await expect(rest).toHaveValue('15');
  await expect(ring(page)).toHaveAttribute('data-tone', 'cycles-break');
  await room(page)
    .getByRole('button', { name: /press to type/ })
    .click();
  await room(page).getByLabel('Type the min').fill('10');
  await page.keyboard.press('Enter');
  await expect(rest).toHaveValue('10');
  await button(page, 'Next').click();

  await expect(room(page)).toContainText('How many cycles?');
  await room(page).getByRole('button', { name: 'More cycles' }).click();
  await expect(field(page, 'cycles')).toHaveValue('4');
  await button(page, 'Start').click();

  await expect(room(page)).toContainText('cycle 1 of 4');
  await expect(ring(page)).toHaveAttribute('data-tone', 'cycles');
  await expect(ring(page)).toContainText(/(48|49):\d\d/);
  await expect(room(page).getByRole('button', { name: 'Pause timer' })).toBeVisible();
});

test('Cycles: Enter does what Next and Start do', async ({ page }) => {
  await enterOn(page, 'Harmonious Cycles', 'Write report');
  await expect(room(page).getByRole('slider')).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(ring(page)).toHaveAttribute('data-tone', 'cycles-break');
  await page.keyboard.press('Enter');
  await page.keyboard.press('Enter');
  await expect(room(page)).toContainText('cycle 1 of 3');
});

test('Cycles: a time typed over the limit stops at the limit', async ({ page }) => {
  await enterOn(page, 'Harmonious Cycles', 'Write report');
  await room(page)
    .getByRole('button', { name: /press to type/ })
    .click();
  await room(page).getByLabel('Type the min').fill('500');
  await page.keyboard.press('Enter');
  await expect(room(page).getByRole('slider')).toHaveValue('120');
});

test('Cycles: dragging round the ring sets the minutes', async ({ page }) => {
  await enterOn(page, 'Harmonious Cycles', 'Write report');
  await expect(room(page).getByRole('slider')).toBeVisible();
  const box = await ring(page).boundingBox();
  if (!box) throw new Error('no ring');
  // A quarter turn round from the top is a quarter of the longest focus (120 min).
  await page.mouse.move(box.x + box.width * 0.95, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.up();
  await expect(room(page).getByRole('slider')).toHaveValue('30');
});

test('the Cycles tab is its own colour, and the tabs switch the room', async ({ page }) => {
  await enterOn(page, 'Trial of the Incense', 'Write report');
  await button(page, 'Start').click();
  await expect(room(page).getByRole('button', { name: 'Pause timer' })).toBeVisible();
  await room(page).getByRole('tab', { name: 'Harmonious Cycles' }).click();
  await expect(room(page).getByRole('tab', { name: 'Harmonious Cycles' })).toHaveAttribute(
    'aria-selected',
    'true',
  );
  // The Incense segment closed where it was; nothing runs until Start.
  await expect(room(page).getByRole('button', { name: 'Pause timer' })).toHaveCount(0);
  await room(page).getByRole('tab', { name: 'River Flow' }).click();
  await expect(room(page)).toContainText('Work to rest');
});

test('Flow: set the ratio, bank rest from focus, take the break, skip it', async ({ page }) => {
  await enterOn(page, 'River Flow', 'Write report');
  await field(page, 'work').fill('1');
  await page.keyboard.press('Enter');
  await field(page, 'rest').fill('11');
  await page.keyboard.press('Enter');
  await expect(field(page, 'rest')).toHaveValue('10');
  await button(page, 'Start').click();
  await expect(ring(page)).toContainText('elapsed');
  await expect(room(page).getByRole('button', { name: 'Take a break' })).toHaveCount(0);

  // One focused minute banks ten, so after a few seconds a break can start.
  await expect(room(page).getByRole('button', { name: 'Take a break' })).toBeVisible({
    timeout: 15_000,
  });
  await room(page).getByRole('button', { name: 'Take a break' }).click();
  await expect(ring(page)).toHaveAttribute('data-tone', 'flow-break');
  await expect(ring(page)).toContainText('rest');
  await room(page).getByRole('button', { name: 'Skip break' }).click();
  await expect(ring(page)).toHaveAttribute('data-tone', 'flow');
  await expect(room(page).getByRole('button', { name: 'Resume timer' })).toBeVisible();
});
