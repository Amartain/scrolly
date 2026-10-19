import { expect, test } from './fixtures';
import { sealDay } from './helpers';

const themes = [
  { theme: 'serene', day_variant: null },
  { theme: 'pavilion', day_variant: 'crimson' },
  { theme: 'pavilion', day_variant: 'teal' },
];

for (const appearance of themes) {
  test(`every panel header is one colour in ${appearance.theme} ${appearance.day_variant ?? ''}`, async ({
    page,
  }) => {
    await sealDay(page);
    const reply = await page.request.put('/api/appearance', { data: appearance });
    expect(reply.ok()).toBeTruthy();
    await page.goto('/');
    const heads = page.locator('section.panel > .head');
    await expect(heads.first()).toBeVisible();
    const colours = await heads.evaluateAll((nodes) =>
      nodes.map((node) => getComputedStyle(node).backgroundColor),
    );
    expect(colours.length).toBeGreaterThan(3);
    expect(new Set(colours).size).toBe(1);
  });
}
