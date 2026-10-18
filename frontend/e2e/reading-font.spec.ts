import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay } from './helpers';

const titleFamily = (page: Page) =>
  page
    .locator('.title.read')
    .first()
    .evaluate((el) => getComputedStyle(el).fontFamily);

test('saved titles use Atkinson, then OpenDyslexic once chosen, and keep it across reloads', async ({
  page,
}) => {
  await sealDay(page, 'Write the report');
  await page.goto('/');
  await expect(page.locator('.title.read').first()).toBeVisible();
  expect(await titleFamily(page)).toContain('Atkinson');

  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByRole('radio', { name: 'OpenDyslexic' }).check({ force: true });
  await expect(page.locator('html')).toHaveAttribute('data-reading-font', 'opendyslexic');

  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-reading-font', 'opendyslexic');
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByRole('button', { name: 'Back' }).click();
  await expect(page.locator('.title.read').first()).toBeVisible();
  expect(await titleFamily(page)).toContain('OpenDyslexic');
});
