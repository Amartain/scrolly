import { expect, test } from './fixtures';
import { art, importFile, sealDay, section } from './helpers';

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
