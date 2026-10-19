import { expect, test } from './fixtures';
import { importFile, sealDay, section } from './helpers';

const item = (id: string, description: string, mandate = false) => ({
  id,
  description,
  status: 'Remaining',
  logical_date: '2026-10-01',
  expected_time_mins: 45,
  mandate,
});

test('the expanded Horizon renames, switches Mandate and deletes, by keyboard', async ({
  page,
}) => {
  await importFile(page, 'future_trials.json', [
    item('q_a', 'Plan the garden'),
    item('q_b', 'Taxes'),
  ]);
  await sealDay(page, 'First');
  await page.goto('/');
  const expand = section(page, 'The Horizon').getByRole('button', { name: 'Expand The Horizon' });
  await expand.focus();
  await page.keyboard.press('Enter');
  const dialog = page.getByRole('dialog', { name: 'The Horizon, expanded' });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('textbox')).toHaveCount(0); // no duration input anywhere

  await expect(dialog.getByRole('button', { name: /^Edit / })).toHaveCount(0); // no pencils
  await dialog.getByRole('button', { name: 'Taxes', exact: true }).press('Enter');
  await dialog.getByLabel('Rename Taxes').fill('Pay taxes');
  await page.keyboard.press('Enter');
  await expect(dialog.getByText('Pay taxes')).toBeVisible();

  await dialog.getByRole('button', { name: 'Make Pay taxes a Heavenly Mandate' }).press('Enter');
  await expect(dialog.getByRole('button', { name: 'Make Pay taxes a Mortal Trial' })).toBeVisible();
  await dialog.getByRole('button', { name: 'Discard Plan the garden' }).press('Enter');
  await expect(dialog.getByText('Plan the garden')).toHaveCount(0);

  await page.keyboard.press('Escape');
  await expect(dialog).toHaveCount(0);
  await expect(expand).toBeFocused();
  await expect(section(page, 'The Horizon')).toContainText('Pay taxes');
  await expect(section(page, 'The Horizon')).not.toContainText('Plan the garden');
});
