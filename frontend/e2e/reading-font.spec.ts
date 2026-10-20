import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, toEstimate } from './helpers';

const titleFamily = (page: Page) =>
  page
    .locator('.read')
    .first()
    .evaluate((el) => getComputedStyle(el).fontFamily);

test('saved titles use Atkinson, then OpenDyslexic once chosen, and keep it across reloads', async ({
  page,
}) => {
  await sealDay(page, 'Write the report');
  await page.goto('/');
  await expect(page.locator('.read').first()).toBeVisible();
  expect(await titleFamily(page)).toContain('Atkinson');

  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByRole('radio', { name: 'OpenDyslexic' }).check({ force: true });
  await expect(page.locator('html')).toHaveAttribute('data-reading-font', 'opendyslexic');

  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-reading-font', 'opendyslexic');
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await expect(page.locator('.read').first()).toBeVisible();
  expect(await titleFamily(page)).toContain('OpenDyslexic');
});

test('the pixel face is used for UI text and the reading face only for saved text', async ({
  page,
}) => {
  await sealDay(page, 'Write the report');
  await page.goto('/');
  await page.evaluate(() => document.fonts.ready);
  const face = (selector: string) =>
    page
      .locator(selector)
      .first()
      .evaluate((el) => getComputedStyle(el).fontFamily);
  expect(await face('h2.display, .display')).toContain('VT323');
  expect(await face('button.button')).toContain('VT323');
  expect(await face('.digits')).toContain('VT323');
  expect(await face('input')).toContain('VT323');
  expect(await face('.read')).toContain('Atkinson');
  // The faces are really loaded, not just named.
  const loaded = await page.evaluate(() => ({
    pixel: document.fonts.check('16px VT323'),
    reading: document.fonts.check('16px "Atkinson Hyperlegible Next"'),
  }));
  expect(loaded).toEqual({ pixel: true, reading: true });
});

test('OpenDyslexic is set smaller than Atkinson so saved text keeps its footprint', async ({
  page,
}) => {
  await sealDay(page, 'Write the report');
  await page.goto('/');
  const size = () =>
    page
      .locator('.read')
      .first()
      .evaluate((el) => parseFloat(getComputedStyle(el).fontSize));
  const atkinson = await size();
  await page.request.put('/api/reading-font', { data: { font: 'opendyslexic' } });
  await page.reload();
  expect(await size()).toBeLessThan(atkinson);
});

test('in Phases 1 to 3 a title in a list is readable and every input stays pixel', async ({
  page,
}) => {
  await toEstimate(page, 'Write the report');
  const face = (selector: string) =>
    page
      .locator(selector)
      .first()
      .evaluate((el) => getComputedStyle(el).fontFamily);
  expect(await face('li .read')).toContain('Atkinson');
  expect(await face('input')).toContain('VT323');
  await page.getByRole('button', { name: /Back to Inscribing/ }).click();
  await expect(page.locator('textarea')).toBeVisible();
  expect(await face('li .read')).toContain('Atkinson');
  expect(await face('textarea')).toContain('VT323');
});
