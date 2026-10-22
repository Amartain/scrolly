/** DRAFT, proposed 2026-10-22: quiet lines of the dashboard. Listed in docs/copy-queue.md › Proposed. */
export const DASHBOARD = {
  /** The Essence panel before anything is estimated or spent, in place of "0m / 0m". */
  essenceBlank: 'Estimates fill this scroll as you set them.',
  essence: 'Time',
  qi: 'Qi',
  /** A row's reading: what is done of what the scroll holds. */
  of: (done: string, planned: string) => `${done} of ${planned}`,
  /** The reading while the pointer is on a tile: that trial's own numbers. */
  tile: (title: string, taken: string | null, planned: string | null) => {
    const plan = planned ? `planned ${planned}` : 'no estimate';
    return taken ? `${title} · ${taken} (${plan})` : `${title} · ${plan}`;
  },
} as const;
