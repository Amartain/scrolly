import { expect, test } from '@playwright/test';
import { panelBoxes, resetTheme } from './helpers';

const SIZES = [
  { width: 1280, height: 720 },
  { width: 1366, height: 768 },
  { width: 1440, height: 900 },
  { width: 1920, height: 1080 },
  { width: 2256, height: 1504 },
  { width: 2560, height: 1440 },
  { width: 3440, height: 1440 },
];

test.beforeEach(async ({ page }) => resetTheme(page));

for (const size of SIZES) {
  test(`same layout at ${size.width}x${size.height}`, async ({ page }, info) => {
    await page.setViewportSize(size);
    await page.goto('/');
    await expect(page.getByRole('button', { name: 'Settings' })).toBeVisible();

    const metrics = await page.evaluate(() => ({
      scrollHeight: document.documentElement.scrollHeight,
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));
    expect(metrics.scrollHeight).toBe(size.height * 2);
    expect(metrics.scrollWidth).toBeLessThanOrEqual(metrics.clientWidth);

    const boxes = await panelBoxes(page);
    const byName = Object.fromEntries(boxes.map((box) => [box.name, box]));
    const ordered = (left: string, right: string) =>
      expect(byName[left].x).toBeLessThan(byName[right].x);

    // Left column above right column positions, top to bottom, are the same at every size.
    ordered('The Immediate Trial', 'Cumulative Momentum');
    expect(byName['Essence'].y).toBeLessThan(byName['The Immediate Trial'].y);
    expect(byName['The Immediate Trial'].y).toBeLessThan(byName['Conquered Today'].y);
    expect(byName['Scribe Trial'].y).toBeLessThan(byName['Remaining Trials'].y);
    expect(byName['Remaining Trials'].y).toBeLessThan(byName['Foundational Arts'].y);
    expect(byName['Foundational Arts'].x).toBeLessThan(byName['Restorative Arts'].x);
    ordered('Remaining Trials', 'The Horizon');

    // Screen 2 starts exactly one viewport down.
    expect(byName['Scribe Trial'].y).toBeGreaterThanOrEqual(size.height);
    // Nothing is wider than the page.
    for (const box of boxes) expect(box.x + box.width).toBeLessThanOrEqual(size.width);

    await page.screenshot({
      path: info.outputPath(`scaling-${size.width}x${size.height}.png`),
      fullPage: true,
    });
  });
}

test('panel text never overflows its frame', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.goto('/');
  const overflowing = await page
    .locator('section.panel')
    .evaluateAll((panels) =>
      panels
        .filter((panel) => panel.scrollWidth > panel.clientWidth + 1)
        .map((panel) => panel.getAttribute('aria-label')),
    );
  expect(overflowing).toEqual([]);
});
