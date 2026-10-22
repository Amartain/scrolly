import { expect, test } from './fixtures';

const scene = (page: import('@playwright/test').Page) => page.locator('.morning');
const begin = (page: import('@playwright/test').Page) =>
  page.getByRole('button', { name: 'Cultivate Your Focus' });

test('the Serene theme opens on the ink painting, the Pavilion on the city at dawn', async ({
  page,
}) => {
  await page.goto('/');
  await expect(scene(page)).toHaveAttribute('data-scene', 'serene');
  await expect(page.locator('.serene-morning')).toBeVisible();
  await page.getByRole('button', { name: 'Hidden Pavilion teal theme' }).click();
  await expect(scene(page)).toHaveAttribute('data-scene', 'pavilion');
  await expect(page.locator('.pavilion-morning')).toBeVisible();
});

test('a key shows the last frame at once and puts the focus on the button', async ({ page }) => {
  await page.goto('/');
  await expect(scene(page)).not.toHaveClass(/still/);
  await page.keyboard.press('x');
  await expect(scene(page)).toHaveClass(/still/);
  await expect(begin(page)).toBeFocused();
});

test('the button works while the scene still plays', async ({ page }) => {
  await page.goto('/');
  await begin(page).click();
  await expect(page.getByRole('heading', { name: 'Inscribe the Scroll' })).toBeVisible();
});

test('under reduced motion the scene is still from the start', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  await expect(scene(page)).toHaveClass(/still/);
});
