import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

const momentum = (page: import('@playwright/test').Page) => section(page, 'Momentum');
const rhythm = (page: import('@playwright/test').Page) => section(page, 'Rhythm');

test('before the first conquest both charts are fogged with an invitation and no toggle', async ({
  page,
}) => {
  await sealDay(page, 'First', 'Second');
  await page.goto('/');
  await expect(momentum(page)).toContainText(
    'Conquer your first trial to reveal your cultivation momentum.',
  );
  await expect(rhythm(page)).toContainText(
    'Conquer your first trial to reveal your cultivation rhythm.',
  );
  await expect(momentum(page).getByRole('group', { name: 'Show' })).toHaveCount(0);
  // The placeholder is hidden from assistive tech; it is only a shape under fog.
  await expect(rhythm(page).locator('li')).toHaveCount(7);
});

test('after a conquest the charts are real and the toggle switches both by keyboard', async ({
  page,
}) => {
  await sealDay(page, 'First', 'Second');
  await page.goto('/');
  await page.getByRole('button', { name: 'Conquer First' }).click();
  await expect(momentum(page)).not.toContainText('Conquer your first trial');
  await expect(rhythm(page)).not.toContainText('Conquer your first trial');
  await expect(
    momentum(page).getByRole('img', { name: /Cumulative trials conquered/ }),
  ).toBeVisible();

  const days = rhythm(page).getByRole('listitem');
  await expect(days).toHaveCount(7);
  await expect(rhythm(page).getByText('rest')).toHaveCount(6);
  await expect(days.last().locator('.bar')).toBeVisible();

  const essence = momentum(page).getByRole('button', { name: 'Essence' });
  await essence.focus();
  await essence.press('Enter');
  await expect(essence).toHaveAttribute('aria-pressed', 'true');
  // One choice for both charts.
  await expect(rhythm(page).getByRole('button', { name: 'Essence' })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
  await expect(momentum(page).getByRole('button', { name: 'Qi' })).toHaveCount(0);
});

test('the charts carry no numbers; hover shows one day, and so do the arrow keys', async ({
  page,
}) => {
  await sealDay(page, 'First', 'Second');
  await page.goto('/');
  await page.getByRole('button', { name: 'Conquer First' }).click();
  const today = rhythm(page).getByRole('listitem').last();
  await expect(today).toHaveText(/^\D+$/); // a weekday and a bar, no figure
  await expect(momentum(page).getByRole('status')).toHaveCount(0);
  await expect(rhythm(page).getByRole('status')).toHaveCount(0);

  await today.hover();
  await expect(rhythm(page).getByRole('status')).toHaveText(/ · 1$/);
  await page.mouse.move(0, 0);
  await expect(rhythm(page).getByRole('status')).toHaveCount(0);
  await momentum(page)
    .getByRole('group', { name: /Momentum/ })
    .hover();
  await expect(momentum(page).getByRole('status')).toHaveText(/ · 1$/);

  // One tab stop for each chart; the keys read a day at a time and Esc puts the tip away.
  const days = rhythm(page).getByRole('list', { name: /Rhythm/ });
  await days.focus();
  await page.keyboard.press('ArrowLeft');
  await expect(rhythm(page).getByRole('status')).toHaveText(/ · rest$/);
  await page.keyboard.press('End');
  await expect(rhythm(page).getByRole('status')).toHaveText(/ · 1$/);
  await page.keyboard.press('Escape');
  await expect(rhythm(page).getByRole('status')).toHaveCount(0);
});

test('Qi joins the toggle only when the Golden Core is on', async ({ page }) => {
  await sealDay(page, 'First', 'Second');
  await page.request.put('/api/golden-core', { data: { enabled: true } });
  await page.goto('/');
  await page.getByRole('button', { name: 'Conquer First' }).click();
  await expect(momentum(page).getByRole('button', { name: 'Qi' })).toBeVisible();
  await expect(rhythm(page).getByRole('button', { name: 'Qi' })).toBeVisible();
});
