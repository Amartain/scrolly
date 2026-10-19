import { expect, test } from './fixtures';
import { art, importFile, sealDay, section, toEstimate } from './helpers';

test('Scribe refuses a title that is already on the scroll', async ({ page }) => {
  await sealDay(page, 'First', 'Second');
  await page.goto('/');
  await page.getByLabel('Trial to scribe').fill('second');
  await page.getByRole('button', { name: 'Inscribe' }).click();
  await expect(page.getByRole('status').first()).toContainText('Already on this scroll: second');
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
  const remaining = section(page, 'Remaining Trials').getByRole('img', {
    name: 'Foundational Art',
  });
  const horizon = section(page, 'The Horizon');
  const listed = horizon.getByRole('img', { name: 'Foundational Art' });
  // Wait for each add to land: the field clears when it does, and would wipe the next fill.
  for (const count of [1, 2]) {
    await page.getByLabel('Trial to scribe').fill('Stretch');
    await page.getByLabel('Trial to scribe').press('Enter');
    await expect(remaining).toHaveCount(count);
  }
  for (const count of [1, 2]) {
    await horizon.getByLabel('A future trial').fill('Stretch');
    await horizon.getByLabel('A future trial').press('Enter');
    await expect(listed).toHaveCount(count);
  }
});

test('Scribe a Horizon title: the note says where it is and offers a way out', async ({ page }) => {
  await sealDay(page, 'First');
  await page.goto('/');
  const horizon = section(page, 'The Horizon');
  await horizon.getByLabel('A future trial').fill('Brew Tea');
  await horizon.getByLabel('A future trial').press('Enter');
  await page.getByLabel('Trial to scribe').fill('brew tea');
  await page.getByLabel('Trial to scribe').press('Enter');
  const note = section(page, 'Remaining Trials').getByRole('status');
  await expect(note).toContainText('Already on the Horizon: brew tea. Trials are one-time.');
  await expect(note).toContainText('like brew tea, Second Pot.');
  await expect(note.locator('em')).toHaveCount(2);
});
