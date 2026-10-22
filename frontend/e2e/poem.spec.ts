import { expect, test } from './fixtures';
import { sealDay, sheathe } from './helpers';

async function finishTheDay(page: import('@playwright/test').Page) {
  await sealDay(page, 'Only trial');
  await page.goto('/');
  await page.getByRole('button', { name: 'Conquer Only trial' }).click();
  await sheathe(page);
}

test('finishing the day opens the sunset poem once; Settle Qi closes it for the day', async ({
  page,
}) => {
  await finishTheDay(page);
  const dialog = page.getByRole('dialog', { name: 'Sunset Poem' });
  await expect(dialog).toBeVisible();
  await expect(dialog.locator('[lang="zh"] p')).toHaveCount(2);
  await dialog.getByRole('button', { name: 'Settle Qi' }).click();
  await expect(dialog).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole('heading', { name: /Conquered Today/i })).toBeVisible();
  await expect(dialog).toHaveCount(0);
});

test('Esc also settles the poem, and Settings can test the chime without a sound file', async ({
  page,
}) => {
  await finishTheDay(page);
  const dialog = page.getByRole('dialog', { name: 'Sunset Poem' });
  await expect(dialog).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(dialog).toHaveCount(0);

  const requests: string[] = [];
  page.on('request', (request) => requests.push(request.url()));
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByRole('button', { name: 'Test chime' }).click();
  expect(requests.filter((url) => /\.(mp3|wav|ogg)/.test(url))).toEqual([]);
});
