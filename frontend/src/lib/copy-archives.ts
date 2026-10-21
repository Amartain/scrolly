/** DRAFT, proposed 2026-10-21: the Grand Archives. Listed in docs/copy-queue.md › Proposed. */
export const ARCHIVES = {
  title: 'The Grand Archives',
  open: 'ARCHIVES',
  back: 'Return to Peak',
  older: 'Older days',
  empty: 'The Archives are quiet. Each day you seal and let rest is kept here.',
  essence: (actual: string, expected: string) => `${actual} of ${expected}`,
  rest: (days: number) => `rest · ${days} ${days === 1 ? 'day' : 'days'}`,
  lost: 'Lost to time',
  sentBack: 'Sent to the Horizon',
  conquered: 'Conquered',
} as const;
