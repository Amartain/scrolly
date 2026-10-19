import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

test('a missing estimate is set once with Enter or the check mark, then it is a number', async ({
  page,
}) => {
  await sealDay(page, 'First', 'Second');
  await page.goto('/');
  const first = page.getByLabel('Estimate for First');
  await first.fill('90');
  await first.press('Enter');
  await expect(page.getByRole('status').first()).toContainText('Use 45m, 2h or 1h30m');
  await expect(first).toHaveValue('90');
  await first.fill('1h30m');
  await first.press('Enter');
  await expect(section(page, 'The Immediate Trial')).toContainText('(1h30m)');
  await expect(page.getByLabel('Estimate for First')).toHaveCount(0);

  const second = page.getByLabel('Estimate for Second');
  await second.fill('20m');
  await page.getByRole('button', { name: 'Set the time for Second' }).click();
  await expect(section(page, 'Remaining Trials')).toContainText('(20m)');
  await expect(page.getByLabel('Estimate for Second')).toHaveCount(0);
});
