import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { section } from './helpers';

async function seal(page: Page) {
  await page.request.post('/api/planning/start');
  await page.request.put('/api/planning/text', { data: { text: 'Write report\nTidy desk' } });
  await page.request.post('/api/planning/proceed');
  await page.request.post('/api/planning/seal');
  await page.goto('/');
}

test('states lead the row and the type mark sits at the end', async ({ page }) => {
  await seal(page);
  const immediate = section(page, 'The Immediate Trial');
  await expect(immediate.getByRole('img', { name: 'Next in flow' })).toHaveText('💧');
  await expect(
    immediate.getByRole('button', { name: 'Make Write report a Heavenly Mandate' }),
  ).toHaveText('⚪');

  const remaining = section(page, 'Remaining Trials');
  await expect(remaining.getByRole('img', { name: 'Remaining' })).toHaveText('☁️');
  const row = remaining.getByRole('listitem').filter({ hasText: 'Tidy desk' });
  const box = async (locator: ReturnType<Page['locator']>) => (await locator.boundingBox())!;
  const title = await box(row.getByText('Tidy desk'));
  const mark = await box(row.getByRole('button', { name: /Make Tidy desk/ }));
  expect(mark.x).toBeGreaterThan(title.x);
});

test('clicking a type mark switches Mandate and Mortal, and a conquered row keeps its leaf', async ({
  page,
}) => {
  await seal(page);
  const remaining = section(page, 'Remaining Trials');
  await remaining.getByRole('button', { name: 'Make Tidy desk a Heavenly Mandate' }).click();
  await expect(remaining.getByRole('button', { name: 'Make Tidy desk a Mortal Trial' })).toHaveText(
    '🪷',
  );

  await page.getByRole('button', { name: 'Conquer Write report' }).click();
  const conquered = section(page, 'Conquered Today');
  await expect(conquered.getByRole('img', { name: 'Conquered' })).toHaveText('🍃');
  await expect(
    conquered.getByRole('button', { name: 'Make Write report a Heavenly Mandate' }),
  ).toHaveText('⚪');
});
