import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay } from './helpers';

const card = (page: Page) => page.getByRole('dialog', { name: 'Welcome back' });

// The server's clock cannot be moved here, so the view is told a silence was found. The server side
// is tested in tests/api/test_ghost.py; this checks the question and both answers reach it.
async function awayFor2h(page: Page) {
  const answers: string[] = [];
  let answered = false;
  await page.route('**/api/view', async (route) => {
    const reply = await route.fetch();
    const body = await reply.json();
    if (!answered) body.ghost = { left_text: '13:22', gap_text: '2h' };
    await route.fulfill({ response: reply, json: body });
  });
  for (const path of ['keep', 'cut']) {
    await page.route(`**/api/ghost/${path}`, async (route) => {
      answers.push(path);
      answered = true;
      const reply = await page.request.get('/api/view');
      await route.fulfill({ response: reply, json: await reply.json() });
    });
  }
  return answers;
}

test('A timer left running while away asks whether the time counts', async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  const answers = await awayFor2h(page);
  await page.goto('/');
  await expect(card(page)).toContainText('You were last here at 13:22, 2h ago');
  await card(page).getByRole('button', { name: 'Keep all of it' }).click();
  await expect(card(page)).toHaveCount(0);
  expect(answers).toEqual(['keep']);
});

test('Counting only until the user left is the other answer', async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  const answers = await awayFor2h(page);
  await page.goto('/');
  await card(page).getByRole('button', { name: 'Count only until I left' }).click();
  await expect(card(page)).toHaveCount(0);
  expect(answers).toEqual(['cut']);
});

test('Closing the card puts the question off without answering it', async ({ page }) => {
  await sealDay(page, 'Write report', 'Tidy desk');
  const answers = await awayFor2h(page);
  await page.goto('/');
  await expect(card(page)).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(card(page)).toHaveCount(0);
  expect(answers).toEqual([]);
});
