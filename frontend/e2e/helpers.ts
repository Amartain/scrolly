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
  // Seclusion's side column is folded until opened (phase 9); the specs of its valves find it open.
  const side = await page.request.put('/api/seclusion/sidebar-hidden', { data: { hidden: false } });
  expect(side.ok(), 'open the Parallel sidebar').toBeTruthy();
  // The welcome scroll after the first way up (phase 11) would cover the room: seen already.
  const seen = await page.request.put('/api/travel', { data: { welcomed: true } });
  expect(seen.ok(), 'welcome seen').toBeTruthy();
}

export const section = (page: Page, name: string) => page.locator(`section[aria-label="${name}"]`);

/** An Art in the prototype's JSON format, for importing. */
export const art = { id: 'r_a1', description: 'Stretch', expected_time_mins: 15, mandate: false };

/** From the zero state into Phase 1. */
export async function begin(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Cultivate Your Focus' }).click();
  await expect(page.getByRole('heading', { name: 'Inscribe the Scroll' })).toBeVisible();
}

/** From the zero state into Phase 2 with one trial per given title. */
export async function toEstimate(page: Page, ...lines: string[]) {
  await begin(page);
  await page.locator('#dump').fill(lines.join('\n'));
  await page.getByRole('button', { name: 'Proceed: Divine the Time' }).click();
  await expect(page.getByRole('heading', { name: 'Estimate the Journey' })).toBeVisible();
}

export async function importFile(page: Page, name: string, content: object) {
  const reply = await page.request.post('/api/import', {
    multipart: {
      file: { name, mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(content)) },
    },
  });
  expect(reply.ok()).toBeTruthy();
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

/** Click Seal Scroll and Commence, then close the milestone that follows the day's first seal. */
export async function sealAndClose(page: Page) {
  await page.getByRole('button', { name: 'Seal Scroll and Commence' }).click();
  const milestone = page.getByRole('dialog', { name: 'Heavenly Cycles' });
  await expect(milestone).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(milestone).toHaveCount(0);
}

/** Close the finished-day ceremony that follows the conquest of a day's last trial. */
export async function sheathe(page: Page) {
  await page.getByRole('button', { name: 'Sheathe the Sword' }).click();
  await expect(
    page.getByRole('dialog', { name: /Tribulation Weathered|Another Day Conquered/ }),
  ).toHaveCount(0);
}
