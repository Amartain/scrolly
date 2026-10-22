import { expect, test } from './fixtures';
import { panelBoxes, sealDay } from './helpers';

test('panel headers are a lacquer plaque by default; the scroll rod is chosen in Settings and moves nothing', async ({
  page,
}) => {
  await sealDay(page);
  await page.goto('/');
  const root = page.locator('html');
  await expect(root).toHaveAttribute('data-panel-style', 'plaque');
  const before = await panelBoxes(page);
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByLabel('Scroll rod').check();
  await expect(root).toHaveAttribute('data-panel-style', 'rod');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  expect(await panelBoxes(page)).toEqual(before);
  await page.reload();
  await expect(root).toHaveAttribute('data-panel-style', 'rod');
});
