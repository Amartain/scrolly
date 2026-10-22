import { expect, test } from './fixtures';
import { sealDay } from './helpers';

const look = (page: import('@playwright/test').Page) =>
  page.evaluate(() => {
    const root = document.documentElement;
    const token = getComputedStyle(root).getPropertyValue('--surface-canvas').trim();
    const probe = document.createElement('div');
    probe.style.color = token;
    document.body.append(probe);
    const expected = getComputedStyle(probe).color;
    probe.remove();
    return {
      fading: 'fading' in root.dataset,
      phase: root.dataset.phase,
      matches: getComputedStyle(document.body).backgroundColor === expected,
    };
  });

async function atDusk(page: import('@playwright/test').Page) {
  await sealDay(page, 'One', 'Two');
  await page.request.post('/api/seal-inscription', { data: { text: 'dusk' } });
  await page.request.post('/api/sunset/poem-seen');
  await page.goto('/');
}

test('opening the app at dusk shows the dusk palette at once, with no fade', async ({ page }) => {
  await atDusk(page);
  await expect.poll(() => look(page)).toEqual({ fading: false, phase: 'dusk', matches: true });
});

test('a theme chosen at dusk shows at once', async ({ page }) => {
  await atDusk(page);
  await page.getByRole('button', { name: 'Settings' }).click();
  for (const theme of ['Hidden Pavilion', 'Serene Peak']) {
    await page.getByText(theme, { exact: true }).click();
    // Well under the old 60 second fade: the new canvas is there straight away.
    await expect.poll(() => look(page), { timeout: 1000 }).toMatchObject({ matches: true });
  }
});

test('no Settings panel is squeezed: each shows all of its content', async ({ page }) => {
  await sealDay(page);
  await page.goto('/');
  await page.getByRole('button', { name: 'Settings' }).click();
  const clipped = await page.locator('section.panel').evaluateAll((panels) =>
    panels
      .filter((panel) => {
        const body = panel.querySelector('.body');
        return body !== null && body.scrollHeight > body.clientHeight + 1;
      })
      .map((panel) => panel.getAttribute('aria-label')),
  );
  expect(clipped).toEqual([]);
});

test('finishing the day turns canvas and panels to dusk together, with no slow canvas', async ({
  page,
}) => {
  await sealDay(page, 'Only one');
  await page.goto('/');
  await page.getByRole('button', { name: 'Conquer Only one' }).click();
  await expect
    .poll(() => look(page), { timeout: 1000 })
    .toEqual({
      fading: false,
      phase: 'dusk',
      matches: true,
    });
});
