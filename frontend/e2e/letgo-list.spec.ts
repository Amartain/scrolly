import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

test('Postponed Today and Fallen Leaves pop out with every item, and Esc closes', async ({
  page,
}) => {
  await sealDay(page, 'Keep', 'Drop one', 'Drop two', 'Delay one', 'Delay two');
  await page.goto('/');
  const remaining = section(page, 'Remaining Trials');
  for (const title of ['Drop one', 'Drop two']) {
    await remaining.getByRole('button', { name: `Abandon ${title}` }).click();
  }
  for (const title of ['Delay one', 'Delay two']) {
    await remaining.getByRole('button', { name: `Make ${title} a Heavenly Mandate` }).click();
    await remaining.getByRole('button', { name: `Postpone ${title} to the Horizon` }).click();
  }

  await section(page, 'Fallen Leaves')
    .getByRole('button', { name: 'Expand Fallen Leaves' })
    .press('Enter');
  const leaves = page.getByRole('dialog', { name: 'Fallen Leaves, expanded' });
  await expect(leaves.getByRole('listitem')).toHaveText([/Drop one/, /Drop two/]);
  await expect(leaves.getByRole('textbox')).toHaveCount(0);
  await page.keyboard.press('Escape');
  await expect(leaves).toHaveCount(0);

  await section(page, 'Postponed Today')
    .getByRole('button', { name: 'Expand Postponed Today' })
    .press('Enter');
  const postponed = page.getByRole('dialog', { name: 'Postponed Today, expanded' });
  await expect(postponed.getByRole('listitem')).toHaveText([/Delay one/, /Delay two/]);
  await page.keyboard.press('Escape');
  await expect(postponed).toHaveCount(0);
});
