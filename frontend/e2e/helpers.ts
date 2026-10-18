import { expect, type Page } from '@playwright/test';

export interface Box {
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

/** Plan and seal a day through the API, so a test can start on the dashboard. */
export async function sealDay(page: Page, ...titles: string[]) {
  const lines = titles.length > 0 ? titles : ['Write the report', 'Tidy the desk'];
  const steps: [string, string, object?][] = [
    ['post', 'start'],
    ['put', 'text', { text: lines.join('\n') }],
    ['post', 'proceed'],
    ['post', 'seal'],
  ];
  for (const [method, path, data] of steps) {
    const url = `/api/planning/${path}`;
    const reply =
      method === 'put' ? await page.request.put(url, { data }) : await page.request.post(url);
    expect(reply.ok(), `${method} ${url}`).toBeTruthy();
  }
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
