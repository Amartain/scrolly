import type { Page } from '@playwright/test';

export interface Box {
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

/** Put the app back to Serene Peak so tests do not depend on each other. */
export async function resetTheme(page: Page) {
  await page.request.put('/api/appearance', { data: { theme: 'serene', day_variant: 'teal' } });
}

/** Bounding box of every panel, keyed by its accessible name. */
export async function panelBoxes(page: Page): Promise<Box[]> {
  return page.locator('section.panel').evaluateAll((panels) =>
    panels.map((panel) => {
      const rect = panel.getBoundingClientRect();
      return {
        name: panel.getAttribute('aria-label') ?? '',
        x: Math.round(rect.x),
        y: Math.round(rect.y + window.scrollY),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
      };
    }),
  );
}

export async function canvasColor(page: Page): Promise<string> {
  return page.evaluate(() => {
    const value = getComputedStyle(document.documentElement).getPropertyValue('--surface-canvas');
    return value.trim().toUpperCase();
  });
}
