import { expect, test } from './fixtures';
import { canvasColor, panelBoxes, sealDay, section } from './helpers';

test.use({ viewport: { width: 1440, height: 900 } });

const CANVAS = {
  'serene-day': '#F3EED0',
  'serene-dusk': '#3B4F5E',
  'pavilion-teal': '#007A6F',
  'pavilion-crimson': '#8E001D',
  'pavilion-purple': '#4A3766',
};

test('all five token sets resolve to the art-direction canvas colors', async ({ page }) => {
  await page.goto('/');
  // The first view re-applies the theme attributes; wait for it so it cannot undo the ones set below.
  await expect(page.locator('html')).toHaveAttribute('data-reading-font', /.+/);
  const attributes: Record<string, [string, string | null, string]> = {
    'serene-day': ['serene', null, 'day'],
    'serene-dusk': ['serene', null, 'dusk'],
    'pavilion-teal': ['pavilion', 'teal', 'day'],
    'pavilion-crimson': ['pavilion', 'crimson', 'day'],
    'pavilion-purple': ['pavilion', 'teal', 'dusk'],
  };
  for (const [name, [theme, variant, phase]] of Object.entries(attributes)) {
    await page.evaluate(
      ([t, v, p]) => {
        const root = document.documentElement;
        root.dataset.theme = t!;
        root.dataset.phase = p!;
        if (v) root.dataset.dayVariant = v;
        else delete root.dataset.dayVariant;
      },
      [theme, variant, phase],
    );
    expect(await canvasColor(page), name).toBe(CANVAS[name as keyof typeof CANVAS]);
  }
});

test('theme changes in Settings re-paint without moving any panel', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  await expect(section(page, 'The Immediate Trial')).toBeVisible();
  const before = await panelBoxes(page);
  const serene = await canvasColor(page);

  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByText('Hidden Pavilion').click();
  await page.getByText('Crimson').click();
  await page.getByRole('button', { name: 'Settings' }).click();

  const root = page.locator('html');
  await expect(root).toHaveAttribute('data-theme', 'pavilion');
  await expect(root).toHaveAttribute('data-day-variant', 'crimson');
  expect(await canvasColor(page)).toBe(CANVAS['pavilion-crimson']);
  expect(await canvasColor(page)).not.toBe(serene);

  const after = await panelBoxes(page);
  expect(after.map((box) => box.name)).toEqual(before.map((box) => box.name));
  for (const [index, box] of after.entries()) {
    expect(box.x, box.name).toBe(before[index].x);
    expect(box.y, box.name).toBe(before[index].y);
    expect(box.width, box.name).toBe(before[index].width);
    expect(box.height, box.name).toBe(before[index].height);
  }
});

test('the choice is kept after a reload', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByText('Hidden Pavilion').click();
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'pavilion');
});

test('theme can be changed with the keyboard alone, and Escape goes back', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
  await page.getByRole('radio', { name: 'Serene Peak' }).focus();
  await page.keyboard.press('ArrowDown');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'pavilion');
  await page.keyboard.press('Escape');
  await expect(page.getByRole('heading', { name: 'Settings' })).toHaveCount(0);
});

test('settings stay reachable and the theme editable in both themes', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  for (const theme of ['Hidden Pavilion', 'Serene Peak']) {
    await page.getByRole('button', { name: 'Settings' }).click();
    await page.getByText(theme, { exact: true }).click();
    await page.getByRole('button', { name: 'Settings' }).click();
  }
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'serene');
});

test('nothing leaves localhost and fonts are bundled', async ({ page }) => {
  const external: string[] = [];
  page.on('request', (request) => {
    const url = new URL(request.url());
    if (!['127.0.0.1', 'localhost'].includes(url.hostname) && url.protocol.startsWith('http')) {
      external.push(request.url());
    }
  });
  await sealDay(page);
  await page.goto('/');
  // Fonts load when text first uses them, so wait for a saved title (reading face) to draw.
  await expect(page.locator('.read').first()).toBeVisible();
  await page.evaluate(() => document.fonts.ready);
  const fonts = await page.evaluate(() =>
    [...document.fonts].filter((font) => font.status === 'loaded').map((font) => font.family),
  );
  expect(fonts.join(' ')).toContain('VT323');
  expect(fonts.join(' ')).toContain('Atkinson Hyperlegible Next');
  expect(external).toEqual([]);
});
