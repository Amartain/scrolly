import { expect, test } from './fixtures';
import { begin, importFile, panelBoxes, sealDay, type Box } from './helpers';

const LONG =
  'fix the cumulative essence so it works like the long wide chart on the other side of the peak, and then some';

const overlaps = (a: Box, b: Box) =>
  a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;

/** Every pair of panels that share any area. */
function collisions(boxes: Box[]): string[] {
  const found: string[] = [];
  boxes.forEach((a, i) =>
    boxes.slice(i + 1).forEach((b) => {
      if (overlaps(a, b)) found.push(`${a.name} / ${b.name}`);
    }),
  );
  return found;
}

for (const size of [
  { width: 1440, height: 900 },
  { width: 2000, height: 1160 },
]) {
  test(`Phase 1 panels never overlap, even with a very long Horizon title (${size.width}x${size.height})`, async ({
    page,
  }) => {
    await page.setViewportSize(size);
    const items = Array.from({ length: 6 }, (_, i) => ({
      id: `q_long${i}`,
      description: `${LONG} ${i}`,
      status: 'Remaining',
      logical_date: '2026-10-01',
      expected_time_mins: 30,
      mandate: i % 2 === 0,
    }));
    await importFile(page, 'future_trials.json', items);
    await begin(page);
    expect(collisions(await panelBoxes(page))).toEqual([]);
  });
}

for (const size of [
  { width: 1440, height: 900 },
  { width: 2000, height: 1160 },
]) {
  for (const goldenCore of [false, true]) {
    test(`dashboard panels never overlap (${size.width}x${size.height}, Golden Core ${goldenCore ? 'on' : 'off'})`, async ({
      page,
    }) => {
      await page.setViewportSize(size);
      await sealDay(page, LONG, 'Tidy the desk');
      await page.request.put('/api/golden-core', { data: { enabled: goldenCore } });
      await page.goto('/');
      expect(collisions(await panelBoxes(page))).toEqual([]);
      await page.reload();
      expect(collisions(await panelBoxes(page))).toEqual([]);
    });
  }
}
