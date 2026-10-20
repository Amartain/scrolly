import { expect, test } from './fixtures';
import { sealDay } from './helpers';

test.use({ permissions: ['clipboard-read', 'clipboard-write'] });

test('Dispatch previews the scroll live, and Clip to Scroll copies it', async ({ page }) => {
  await sealDay(page, 'Write the report', 'Tidy the desk');
  await page.goto('/');
  await page.getByRole('button', { name: 'DISPATCH' }).click();

  const preview = page.getByLabel('Scroll text');
  await expect(preview).toContainText('# :scroll: Scroll of Heavenly Tribulations');
  await expect(preview).toContainText(':droplet: :white_circle: Write the report');
  await expect(preview).not.toContainText('NO CHECK IN DND');

  await page.getByLabel('DND header').check();
  await expect(preview).toContainText('NO CHECK IN DND');

  await page.getByRole('button', { name: 'Clip to Scroll' }).click();
  await expect(page.getByRole('status')).toContainText('Clipped');
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  expect(copied).toContain(':cloud: :white_circle: Tidy the desk');
  expect(copied).toContain('NO CHECK IN DND');

  await page.keyboard.press('Escape');
  await expect(page.getByRole('heading', { name: 'Scroll of Heavenly Tribulations' })).toHaveCount(
    0,
  );
});

test('a symbol chosen in Settings shows in the scroll and on the dashboard', async ({ page }) => {
  await sealDay(page, 'Write the report');
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByLabel('Symbol for Next in flow').fill('🔥');
  await page.getByLabel('Shortcode for Next in flow').fill('fire');
  await page.getByLabel('Shortcode for Next in flow').press('Enter');
  await expect(page.getByLabel('Shortcode for Next in flow')).toHaveValue(':fire:');

  await page.getByLabel('Symbol for Remaining').fill('🍃');
  await page.getByLabel('Symbol for Remaining').press('Enter');
  await expect(page.getByLabel('Symbol for Remaining')).toHaveValue('☁️');
  await expect(page.getByText('already stands for Conquered')).toBeVisible();

  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByRole('button', { name: 'DISPATCH' }).click();
  await expect(page.getByLabel('Scroll text')).toContainText(':fire: :white_circle: Write');
});
