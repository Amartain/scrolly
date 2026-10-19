import { expect, test } from './fixtures';
import { art, importFile, sealDay, section, toEstimate } from './helpers';

test('Scribe refuses a title that is already on the scroll', async ({ page }) => {
  await sealDay(page, 'First', 'Second');
  await page.goto('/');
  await page.getByLabel('Trial to scribe').fill('second');
  await page.getByRole('button', { name: 'Inscribe' }).click();
  await expect(page.getByRole('status').first()).toContainText("Already on today's scroll");
  await expect(section(page, 'Remaining Trials').getByLabel('Estimate for Second')).toHaveCount(1);
});

test('the same Art can be summoned twice', async ({ page }) => {
  await importFile(page, 'rituals.json', [art]);
  await sealDay(page, 'First');
  await page.goto('/');
  const summon = section(page, 'Foundational Arts').getByRole('button', { name: 'Summon Stretch' });
  await summon.click();
  await expect(section(page, 'Remaining Trials').getByText('Stretch')).toHaveCount(1);
  await summon.click();
  await expect(section(page, 'Remaining Trials').getByText('Stretch')).toHaveCount(2);
});

test('Phase 1 blocks a repeated line and names it', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Cultivate Your Focus' }).click();
  await page.locator('#dump').fill('Walk\nwalk');
  await page.getByRole('button', { name: 'Proceed: Divine the Time' }).click();
  await expect(page.getByRole('status')).toContainText('Written twice: walk');
  await expect(page.locator('#dump')).toHaveValue('Walk\nwalk');
});

test('a title that names an Art is an Art instance, even written twice', async ({ page }) => {
  await importFile(page, 'rituals.json', [art]);
  await toEstimate(page, 'Stretch', 'stretch', 'Walk');
  const rows = page.getByRole('listitem');
  await expect(
    rows.filter({ hasText: 'Stretch' }).getByRole('img', { name: 'Foundational Art' }),
  ).toHaveCount(2);
  await expect(
    rows.filter({ hasText: 'Walk' }).getByRole('img', { name: 'Foundational Art' }),
  ).toHaveCount(0);
});

test('Scribe and the Horizon take an Art name again and again', async ({ page }) => {
  await importFile(page, 'rituals.json', [art]);
  await sealDay(page, 'First');
  await page.goto('/');
  for (const title of ['Stretch', 'Stretch']) {
    await page.getByLabel('Trial to scribe').fill(title);
    await page.getByLabel('Trial to scribe').press('Enter');
  }
  await expect(
    section(page, 'Remaining Trials').getByRole('img', { name: 'Foundational Art' }),
  ).toHaveCount(2);
  const horizon = section(page, 'The Horizon');
  for (const title of ['Stretch', 'Stretch']) {
    await horizon.getByLabel('A future trial').fill(title);
    await horizon.getByLabel('A future trial').press('Enter');
  }
  await expect(horizon.getByRole('img', { name: 'Foundational Art' })).toHaveCount(2);
});
