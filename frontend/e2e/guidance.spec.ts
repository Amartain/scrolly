import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

const open = (page: import('@playwright/test').Page, panel: string) =>
  section(page, panel).getByRole('button', { name: `Guidance: ${panel}` });

test('the ? gives a short tip on focus, and Enter opens the scroll', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  const mark = open(page, 'The Immediate Trial');
  await mark.focus();
  const tip = page.getByRole('tooltip', { name: 'The one trial to do now.' });
  await expect(tip).toHaveCSS('opacity', '1');
  await page.keyboard.press('Enter');

  const scroll = page.getByRole('dialog', { name: 'The Immediate Trial: Guidance' });
  await expect(scroll).toBeVisible();
  await expect(scroll).toContainText('The Dao of Practice');
  await expect(scroll).toContainText('Artisan Execution');
  await expect(scroll).toContainText('In plain words');
  await page.keyboard.press('Escape');
  await expect(scroll).toHaveCount(0);
  await expect(mark).toBeFocused();
});

test('the scroll rolls up with its button or a click outside it', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  const scroll = page.getByRole('dialog', { name: 'Essence: Guidance' });
  await open(page, 'Essence').click();
  await scroll.getByRole('button', { name: 'Roll Up Guidance Scroll' }).click();
  await expect(scroll).toHaveCount(0);

  await open(page, 'Essence').click();
  await expect(scroll).toBeVisible();
  await page.mouse.click(4, 4);
  await expect(scroll).toHaveCount(0);
});

test('the second screen, the Archives and Seclusion each have one', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  for (const panel of [
    'Scribe Trial',
    'Remaining Trials',
    'The Horizon',
    'Foundational Arts',
    'Restorative Arts',
    'Postponed Today',
    'Fallen Leaves',
    'Conquered Today',
    'Momentum',
    'Rhythm',
  ]) {
    await expect(open(page, panel)).toHaveCount(1);
  }
  await page.getByRole('button', { name: 'ARCHIVES' }).click();
  await page.getByRole('button', { name: 'Guidance: The Grand Archives' }).click();
  await expect(page.getByRole('dialog', { name: 'The Grand Archives: Guidance' })).toBeVisible();
  await page.keyboard.press('Escape');
  await page.getByRole('button', { name: 'Return to Peak' }).click();

  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await page.getByRole('button', { name: 'Guidance: Seclusion' }).click();
  await expect(page.getByRole('dialog', { name: 'Seclusion: Guidance' })).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog', { name: 'Seclusion: Guidance' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Step out' })).toBeVisible();
});
