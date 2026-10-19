import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

test('the expanded Arts add, edit and delete by keyboard, and the main panel has no inputs', async ({
  page,
}) => {
  await sealDay(page, 'First');
  await page.goto('/');
  const main = section(page, 'Foundational Arts');
  await expect(main.getByRole('textbox')).toHaveCount(0);

  await main.getByRole('button', { name: 'Expand Foundational Arts' }).press('Enter');
  const dialog = page.getByRole('dialog', { name: 'Foundational Arts, expanded' });
  await dialog.getByLabel('A new Art').fill('Stretch');
  await dialog.getByLabel('Duration of the new Art').fill('15m');
  await page.keyboard.press('Enter');
  await expect(dialog.getByText('Stretch')).toBeVisible();
  await expect(dialog.getByLabel('Duration of Stretch')).toHaveValue('15m');

  await dialog.getByLabel('A new Art').fill('stretch');
  await page.keyboard.press('Enter');
  await expect(dialog.getByRole('status')).toContainText('already in this list');

  await dialog.getByLabel('Duration of Stretch').fill('90');
  await page.keyboard.press('Enter');
  await expect(dialog.getByRole('status')).toContainText('Use 45m, 2h or 1h30m');
  await expect(dialog.getByLabel('Duration of Stretch')).toHaveValue('15m');
  await dialog.getByLabel('Duration of Stretch').fill('1h');
  await page.keyboard.press('Enter');
  await expect(dialog.getByLabel('Duration of Stretch')).toHaveValue('1h');

  await dialog.getByRole('button', { name: 'Edit Stretch' }).press('Enter');
  await dialog.getByLabel('Rename Stretch').fill('Warm up');
  await page.keyboard.press('Enter');
  await expect(dialog.getByText('Warm up')).toBeVisible();

  await page.keyboard.press('Escape');
  await expect(main).toContainText('Warm up');
  await expect(main.getByRole('textbox')).toHaveCount(0);
  await expect(main.getByRole('button', { name: 'Summon Warm up' })).toBeVisible();

  await main.getByRole('button', { name: 'Expand Foundational Arts' }).press('Enter');
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: 'Delete Warm up' }).press('Enter');
  await expect(dialog.getByText('Warm up')).toHaveCount(0);
});

test('Restorative Arts have their own expanded list', async ({ page }) => {
  await sealDay(page, 'First');
  await page.goto('/');
  await section(page, 'Restorative Arts')
    .getByRole('button', { name: 'Expand Restorative Arts' })
    .click();
  const dialog = page.getByRole('dialog', { name: 'Restorative Arts, expanded' });
  await dialog.getByLabel('A new Art').fill('Nap');
  await dialog.getByRole('button', { name: 'Add' }).click();
  await page.keyboard.press('Escape');
  await expect(section(page, 'Restorative Arts')).toContainText('Nap');
  await expect(section(page, 'Foundational Arts')).not.toContainText('Nap');
});
