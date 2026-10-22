/**
 * DRAFT, proposed 2026-10-22: the finished-day ceremony and its banner. Listed in
 * docs/copy-queue.md › Proposed. The day's line comes from Python (`content/victory.json`), and so does
 * the scene: thunder when a Heavenly Mandate was conquered, wind otherwise.
 */
export const SCENES = {
  thunder: {
    title: 'Tribulation Weathered',
    seal: '劫',
    lead: 'Nine bolts of heavenly lightning fell upon the peak, and still you stand.',
  },
  wind: {
    title: 'Another Day Conquered',
    seal: '日',
    lead: 'The wind sweeps the courtyard clean, and the sun rises gold upon the peak.',
  },
} as const;

export const VICTORY = {
  close: 'Sheathe the Sword',
  labels: {
    conquered: 'Trials conquered',
    mandates: 'Heavenly Mandates fulfilled',
    essence: 'Essence cultivated',
    lifetime: 'Lifetime conquered',
  },
  /** The compact tally under the banner's line. */
  row: (conquered: number, mandates: number, essence: string) =>
    [
      `${conquered} ${conquered === 1 ? 'trial' : 'trials'}`,
      ...(mandates > 0 ? [`${mandates} ${mandates === 1 ? 'Mandate' : 'Mandates'}`] : []),
      essence,
    ].join(' · '),
  arenaEmpty:
    'The arena stands empty; the last challenger has fallen. Only the wind still duels with the pines.',
} as const;
