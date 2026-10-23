/** DRAFT, proposed 2026-10-22: quiet lines of the dashboard. Listed in docs/copy-queue.md › Proposed. */
export const DASHBOARD = {
  /** The Essence panel before anything is estimated or spent, in place of "0m / 0m". */
  essenceBlank: 'Estimates fill this scroll as you set them.',
  essence: 'Essence',
  qi: 'Qi',
  /** The Essence bar's numbers, shown on hover or focus: done, still planned, and the light left. */
  essenceTip: (done: string, toGo: string, light: string | null) =>
    [`${done} done`, `${toGo} to go`, light ? `${light} of light left` : null]
      .filter(Boolean)
      .join(' · '),
  /** The Qi bar's numbers: spent of the day's Qi, what the scroll plans, and the zone reached. */
  qiTip: (spent: number, start: number, planned: number, zone: string) =>
    `${spent} of ${start} spent · ${planned} planned · ${zone}`,
} as const;

/** DRAFT, proposed 2026-10-23: a trial postponed or let go today, summoned back by a double-click. */
export const LET_GO = {
  hint: 'Double-click to summon it back',
  back: (title: string) => `Summon ${title} back to the scroll`,
} as const;
