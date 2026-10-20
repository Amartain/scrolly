import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

// A 16 hour plan runs past a 23:59 sunset at any time of the logical day, except 00:00-03:59,
// when 23:59 has already passed for it.
test.skip(new Date().getHours() < 4, 'the logical day has not turned yet');

async function overrun(page: import('@playwright/test').Page) {
  await page.request.put('/api/sunset', { data: { at: '23:59' } });
  await sealDay(page, 'Long climb');
  const view = await (await page.request.get('/api/view')).json();
  const reply = await page.request.patch(`/api/trials/${view.dashboard.immediate.id}`, {
    data: { estimate: '16h' },
  });
  expect(reply.ok()).toBeTruthy();
  await page.goto('/');
}

test('the advisor speaks once; Dismiss hides it until a reload', async ({ page }) => {
  await overrun(page);
  const dialog = page.getByRole('dialog', { name: 'The Light Grows Short' });
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: 'Dismiss' }).click();
  await expect(dialog).toHaveCount(0);
  await page.reload();
  await expect(dialog).toBeVisible();
});

test('Not again today keeps it quiet through a reload, until Settings wakes it', async ({
  page,
}) => {
  await overrun(page);
  const dialog = page.getByRole('dialog', { name: 'The Light Grows Short' });
  await dialog.getByRole('button', { name: 'Not again today' }).click();
  await expect(dialog).toHaveCount(0);
  await page.reload();
  await expect(section(page, 'The Immediate Trial')).toBeVisible();
  await expect(dialog).toHaveCount(0);

  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByRole('button', { name: 'Let the advisor speak again today' }).click();
  await page.getByRole('button', { name: 'Back' }).click();
  await expect(dialog).toBeVisible();
});
