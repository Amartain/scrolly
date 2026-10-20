import { expect, test } from './fixtures';
import { sealDay } from './helpers';

// A 1x1 PNG.
const PNG = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGP4z8DwHwAFAAH/q842iQAAAABJRU5ErkJggg==',
  'base64',
);

const picture = (page: import('@playwright/test').Page) =>
  page.locator('header.header').evaluate((el) => getComputedStyle(el).backgroundImage);

test('a built-in picture can be chosen for the header, and the theme default restored', async ({
  page,
}) => {
  await sealDay(page);
  await page.goto('/');
  const themed = await picture(page);
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByText('Serene Dusk', { exact: true }).click();
  await expect.poll(() => picture(page)).toContain('serene-dusk');
  await page.reload();
  await page.getByRole('button', { name: 'Settings' }).click();
  await expect.poll(() => picture(page)).toContain('serene-dusk');

  await page.getByText('Match the theme').click();
  await expect.poll(() => picture(page)).toBe(themed);
});

test('your own picture is uploaded, shown, and a wrong file is refused', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  await expect(page.getByLabel('My own picture')).toBeDisabled();

  await page.getByLabel('Header picture').setInputFiles({
    name: 'notes.gif',
    mimeType: 'image/gif',
    buffer: Buffer.from('GIF89a....'),
  });
  await expect(page.getByText('Use a PNG, JPEG or WebP picture')).toBeVisible();
  await expect(page.getByLabel('My own picture')).toBeDisabled();

  await page.getByLabel('Header picture').setInputFiles({
    name: 'mine.png',
    mimeType: 'image/png',
    buffer: PNG,
  });
  await expect(page.getByLabel('My own picture')).toBeChecked();
  await expect.poll(() => picture(page)).toContain('/api/header-image?v=1');
  const served = await page.request.get('/api/header-image');
  expect(served.headers()['content-type']).toBe('image/png');
});

test('the feedback links open in a new tab and nothing is requested until clicked', async ({
  page,
}) => {
  const outside: string[] = [];
  page.on('request', (request) => {
    if (!request.url().startsWith('http://127.0.0.1')) outside.push(request.url());
  });
  await sealDay(page);
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  const bug = page.getByRole('link', { name: 'Report a bug' });
  await expect(bug).toHaveAttribute('target', '_blank');
  await expect(bug).toHaveAttribute('href', /forms\.gle/);
  await expect(page.getByRole('link')).toHaveCount(3);
  expect(outside).toEqual([]);
});
