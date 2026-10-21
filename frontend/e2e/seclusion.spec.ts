import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

const room = (page: Page) => section(page, 'Focus Scroll');
const ring = (page: Page) => room(page).getByRole('timer');

async function enter(page: Page) {
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await expect(room(page)).toBeVisible();
}

test.beforeEach(async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  await page.goto('/');
});

test('F opens Seclusion with only the trial at hand, and Step out pauses it', async ({ page }) => {
  await expect(page.getByRole('button', { name: /Enter Seclusion/ })).toBeVisible();
  await page.keyboard.press('f');
  await expect(room(page)).toContainText('Write report');
  await expect(room(page)).not.toContainText('Tidy desk');
  await room(page).getByRole('button', { name: 'Start', exact: true }).click();
  await expect(room(page).getByRole('button', { name: 'Pause timer' })).toBeVisible();
  await page.getByRole('button', { name: 'Step out' }).click();
  await expect(page.getByRole('button', { name: 'Start timer' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Enter Seclusion/ })).toBeVisible();
});

test('Escape steps out too', async ({ page }) => {
  await enter(page);
  await page.keyboard.press('Escape');
  await expect(page.getByRole('button', { name: /Enter Seclusion/ })).toBeVisible();
});

test('a reload keeps Seclusion open', async ({ page }) => {
  await enter(page);
  await page.reload();
  await expect(room(page)).toContainText('Write report');
});

test('Idle shows only Start; running shows Conquered and Abandon for a Mortal Trial', async ({
  page,
}) => {
  await enter(page);
  await expect(room(page).getByRole('button', { name: 'Conquer Write report' })).toHaveCount(0);
  await room(page).getByRole('button', { name: 'Start', exact: true }).click();
  await expect(room(page).getByRole('button', { name: 'Conquer Write report' })).toBeVisible();
  await expect(room(page).getByRole('button', { name: 'Abandon Write report' })).toBeVisible();
  await expect(room(page).getByRole('button', { name: /Postpone/ })).toHaveCount(0);
});

test('a Heavenly Mandate shows the postpone arrow, not Abandon', async ({ page }) => {
  await enter(page);
  await room(page).getByRole('button', { name: 'Make Write report a Heavenly Mandate' }).click();
  await expect(room(page).getByRole('button', { name: /Postpone Write report/ })).toBeVisible();
  await expect(room(page).getByRole('button', { name: /Abandon/ })).toHaveCount(0);
});

test('a trial with no estimate asks for one, then the ring counts it down', async ({ page }) => {
  await enter(page);
  await expect(ring(page)).toContainText('How long will this take?');
  await ring(page).getByLabel('Estimate for Write report').fill('45m');
  await ring(page).getByRole('button', { name: 'Set the time for Write report' }).click();
  await expect(ring(page)).toContainText('45m');
  await expect(ring(page)).toContainText('remaining');
  await expect(ring(page)).toContainText('of your 45m estimate');
});

test('the ring drains: full before the start, shrinking while it runs', async ({ page }) => {
  await enter(page);
  await room(page).getByLabel('Estimate for Write report').fill('2m');
  await room(page).getByRole('button', { name: 'Set the time for Write report' }).click();
  const fill = () => ring(page).evaluate((el) => Number(el.style.getPropertyValue('--fill')));
  await expect(ring(page)).toContainText('remaining');
  expect(await fill()).toBe(100);
  await room(page).getByRole('button', { name: 'Start', exact: true }).click();
  await expect.poll(fill).toBeLessThan(100);
  expect(await fill()).toBeGreaterThan(80);
});

test('the icon row: Incense has restart, start and sound; Cycles adds zero out, break and stop', async ({
  page,
}) => {
  await enter(page);
  const icons = room(page).getByRole('toolbar', { name: 'Timer' }).getByRole('button');
  await expect(icons).toHaveCount(3);
  await room(page).getByRole('tab', { name: 'Harmonious Cycles' }).click();
  await expect(icons).toHaveCount(6);
  // On the dial nothing has begun: the buttons wait, dimmed, in their places.
  const breakButton = room(page).getByRole('button', { name: 'Take a break' });
  await expect(breakButton).toHaveAttribute('aria-disabled', 'true');
});

test('Restart asks before it scraps a minute or more; Keep and Esc change nothing', async ({
  page,
}) => {
  await page.clock.install();
  await page.reload();
  await enter(page);
  await room(page).getByLabel('Estimate for Write report').fill('45m');
  await room(page).getByRole('button', { name: 'Set the time for Write report' }).click();
  await room(page).getByRole('button', { name: 'Start', exact: true }).click();
  await page.clock.runFor(125_000); // the screen counts two minutes on
  const restart = room(page).getByRole('button', { name: 'Restart' });
  await restart.click();
  // The browser's clock is faked and the server's is not, so only the shape of the question is fixed.
  const ask = room(page).getByRole('group', { name: /^Scrap \d+m from this trial\?$/ });
  await expect(ask.getByRole('button', { name: 'Keep' })).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(ask).toHaveCount(0);
  await expect(restart).toBeFocused();
  await expect(room(page)).toBeVisible(); // Esc closed the question, not the room
  await restart.click();
  await ask.getByRole('button', { name: 'Scrap' }).click();
  await expect(ring(page)).toContainText('45:00');
  await expect(room(page).getByRole('button', { name: 'Pause timer' })).toBeVisible();
});

test('Switch puts another waiting trial at hand; this one steps back, paused', async ({ page }) => {
  await enter(page);
  await room(page).getByRole('button', { name: 'Start', exact: true }).click();
  await room(page).getByRole('button', { name: 'Switch trial' }).click();
  await room(page).getByRole('button', { name: 'Switch to Tidy desk' }).click();
  await expect(room(page).getByRole('group', { name: 'Trial at hand' })).toContainText('Tidy desk');
  const state = await (await page.request.get('/api/seclusion')).json();
  expect(state.remaining[0].title).toBe('Write report');
  expect(state.trial.timer.running).toBe(false);
});

test('conquering in Seclusion brings the next trial, idle', async ({ page }) => {
  await enter(page);
  await room(page).getByRole('button', { name: 'Start', exact: true }).click();
  await room(page).getByRole('button', { name: 'Conquer Write report' }).click();
  await expect(room(page)).toContainText('Tidy desk');
  await expect(room(page).getByRole('button', { name: 'Start', exact: true })).toBeVisible();
});

test('on a narrow screen the utility column stacks below the focus scroll', async ({ page }) => {
  await page.setViewportSize({ width: 640, height: 900 });
  await enter(page);
  const scroll = await room(page).boundingBox();
  const parallel = await section(page, 'Parallel Flow').boundingBox();
  expect(scroll && parallel && parallel.y >= scroll.y + scroll.height).toBeTruthy();
});
