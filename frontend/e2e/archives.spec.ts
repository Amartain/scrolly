import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { importFile, sealDay } from './helpers';

const past = (id: string, description: string, status: string, date: string, more = {}) => ({
  id,
  description,
  status,
  logical_date: date,
  expected_time_mins: 0,
  ...more,
});

async function openArchives(page: Page) {
  await page.goto('/');
  const open = page.getByRole('button', { name: 'ARCHIVES' });
  await open.focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'The Grand Archives' })).toBeVisible();
}

test('the Archives show each past day, newest first, with what became of its trials', async ({
  page,
}) => {
  await sealDay(page, 'Write the report');
  await importFile(page, 'history.json', {
    history: [
      past('h1', 'Write chapter', 'Done', '2025-06-10', {
        expected_time_mins: 60,
        actual_time_mins: 75,
        completed_at: Date.parse('2025-06-10T12:00:00Z'),
      }),
      past('h2', 'Tidy desk', 'Cancelled', '2025-06-10'),
      past('h3', 'Call back', 'Postponed', '2025-06-10', { mandate: true }),
      past('h4', 'Older trial', 'Done', '2025-06-05', {
        expected_time_mins: 30,
        actual_time_mins: 30,
        completed_at: Date.parse('2025-06-05T12:00:00Z'),
      }),
    ],
  });
  await openArchives(page);

  const days = page.getByRole('article');
  await expect(days).toHaveCount(2);
  await expect(days.nth(0)).toHaveAccessibleName('Tuesday, 10 June 2025');
  await expect(days.nth(1)).toHaveAccessibleName('Thursday, 5 June 2025');
  await expect(days.nth(0)).toContainText('1h15m of 1h');
  await expect(days.nth(0)).toContainText('Write chapter');
  await expect(days.nth(0)).toContainText('Tidy desk');
  await expect(days.nth(0)).toContainText('Lost to time');
  await expect(days.nth(0)).toContainText('Call back');
  await expect(days.nth(0)).toContainText('Sent to the Horizon');
  await expect(page.getByText('rest · 4 days')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Older days' })).toHaveCount(0);

  await page.keyboard.press('Escape');
  await expect(page.getByRole('heading', { name: 'The Grand Archives' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'ARCHIVES' })).toBeVisible();
});

test('Return to Peak goes back, and an empty archive says so', async ({ page }) => {
  await sealDay(page);
  await openArchives(page);
  await expect(page.getByText('The Archives are quiet.')).toBeVisible();
  await page.getByRole('button', { name: 'Return to Peak' }).click();
  await expect(page.getByRole('heading', { name: 'The Grand Archives' })).toHaveCount(0);
});

test('fourteen days come first, and Older days brings the rest', async ({ page }) => {
  await sealDay(page);
  const day = (n: number) => `2025-03-${String(n).padStart(2, '0')}`;
  await importFile(page, 'history.json', {
    history: Array.from({ length: 16 }, (_, i) =>
      past(`d${i + 1}`, `Trial ${i + 1}`, 'Done', day(i + 1), { actual_time_mins: 10 }),
    ),
  });
  await openArchives(page);
  await expect(page.getByRole('article')).toHaveCount(14);
  await page.getByRole('button', { name: 'Older days' }).click();
  await expect(page.getByRole('article')).toHaveCount(16);
  await expect(page.getByRole('button', { name: 'Older days' })).toHaveCount(0);
  await expect(page.getByRole('article').last()).toContainText('Trial 1');
});
