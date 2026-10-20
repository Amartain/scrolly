import { expect, test } from './fixtures';
import { sealDay } from './helpers';

const inscribe = async (page: import('@playwright/test').Page, words: string) => {
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByLabel('Secret seal words').fill(words);
  await page.keyboard.press('Enter');
};

const phase = (page: import('@playwright/test').Page) =>
  page.evaluate(() => document.documentElement.dataset.phase);

test('words that name no seal do nothing, with one quiet line', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  await inscribe(page, 'open sesame');
  await expect(page.getByText('The scroll does not answer to those words.')).toBeVisible();
  await expect(page.getByLabel('Secret seal words')).toHaveValue('open sesame');
});

test('a day number shows that days milestone on the dashboard', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  await inscribe(page, 'day 10');
  const dialog = page.getByRole('dialog', { name: 'Heavenly Cycles' });
  await expect(dialog).toContainText('Day 10 Milestone: Foundation Established!');
  await page.keyboard.press('Escape');
  await expect(dialog).toHaveCount(0);
});

test('dusk turns the palette and opens the poem; sunrise turns it back', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  expect(await phase(page)).toBe('day');
  await inscribe(page, 'dusk');
  await expect.poll(() => phase(page)).toBe('dusk');
  const poem = page.getByRole('dialog', { name: 'Sunset Poem' });
  await expect(poem).toBeVisible();
  await poem.getByRole('button', { name: 'Settle Qi' }).click();

  await inscribe(page, 'sunrise');
  await expect.poll(() => phase(page)).toBe('day');
});

test('restart-today starts the day over at the Serene Peak', async ({ page }) => {
  await sealDay(page, 'Write the report', 'Tidy the desk');
  await page.goto('/');
  await inscribe(page, 'restart-today');
  await expect(page.getByRole('button', { name: 'Cultivate Your Focus' })).toBeVisible();
  // And the day can begin again.
  await sealDay(page, 'Second try');
  await page.goto('/');
  await expect(page.getByText('Second try').first()).toBeVisible();
});
