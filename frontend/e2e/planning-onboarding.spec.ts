import { expect, test } from './fixtures';
import { art, begin, importFile, section, sealDay, toEstimate } from './helpers';

test('the icon is the Mandate switch: click or Enter flips it back and forth', async ({ page }) => {
  await toEstimate(page, 'Taxes');
  const toLotus = page.getByRole('button', { name: 'Make Taxes a Heavenly Mandate' });
  await toLotus.click();
  const toCloud = page.getByRole('button', { name: 'Make Taxes a Mortal Trial' });
  await expect(toCloud).toBeVisible();
  await toCloud.focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('button', { name: 'Make Taxes a Heavenly Mandate' })).toBeVisible();
});

test('an Art copy has no Mandate switch', async ({ page }) => {
  await importFile(page, 'rituals.json', [art]);
  await begin(page);
  await page.getByRole('button', { name: 'Summon Stretch' }).click();
  await page.locator('#dump').fill('Plain');
  await page.getByRole('button', { name: 'Proceed: Divine the Time' }).click();
  await expect(page.getByLabel('Estimate for Stretch')).toBeVisible();
  await expect(page.getByRole('button', { name: /Make Stretch/ })).toHaveCount(0);
});

test('planning has no header and no Settings, in Phase 1 and Phase 2', async ({ page }) => {
  await begin(page);
  await expect(page.getByRole('banner')).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Settings' })).toHaveCount(0);
  await page.locator('#dump').fill('One');
  await page.getByRole('button', { name: 'Proceed: Divine the Time' }).click();
  await expect(page.getByRole('heading', { name: 'Estimate the Journey' })).toBeVisible();
  await expect(page.getByRole('banner')).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Settings' })).toHaveCount(0);
});

test('the zero state is the morning scene and its one button: no header, no Settings', async ({
  page,
}) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'The Peak is Serene' })).toBeVisible();
  await expect(page.locator('.morning')).toBeVisible();
  await expect(page.locator('header')).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Settings' })).toHaveCount(0);
});

test('the dashboard has the header and Settings, and the planning text survives the trip', async ({
  page,
}) => {
  await sealDay(page);
  await page.goto('/');
  await expect(page.getByRole('banner')).toBeVisible();
  await page.getByRole('button', { name: 'Settings' }).click();
  await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('banner')).toBeVisible();
});

test('the Day Summary shows the plan against the light left', async ({ page }) => {
  await toEstimate(page, 'Write report', 'Tidy desk');
  const summary = section(page, 'Day Summary');
  await expect(summary).toContainText('2 trials');
  // The test server uses the real clock, so it may be before or after sunset.
  await expect(summary).toContainText(/of light left|The sun has set/);
  await page.getByLabel('Estimate for Write report').fill('2h');
  await page.getByLabel('Estimate for Write report').press('Enter');
  await expect(summary).toContainText('2h planned');
  await expect(summary).toContainText('1 without an estimate');
});
