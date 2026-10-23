import { DAY_GUIDES } from './copy-guidance-day';
import { PLAN_GUIDES } from './copy-guidance-plan';
import { SCROLL_GUIDES } from './copy-guidance-scroll';
import { SECLUSION_GUIDES } from './copy-guidance-seclusion';

/** One `?` scroll: a short tip on hover, then why (the Dao), how (the Art) and the words in plain
 *  language; where a screen has shortcuts, its keys. */
export interface Guide {
  name: string;
  tip: string;
  dao: string;
  art: string;
  terms: readonly (readonly [string, string])[];
  keys?: readonly (readonly [string, string])[];
}

/** DRAFT, proposed 2026-10-21: the words around every `?` scroll. */
export const GUIDANCE = {
  dao: 'The Dao of Practice',
  art: 'Artisan Execution',
  terms: 'In plain words',
  keys: 'Keys',
  close: 'Roll Up Guidance Scroll',
  button: (name: string) => `Guidance: ${name}`,
  title: (name: string) => `${name}: Guidance`,
} as const;

const OTHER_GUIDES = {
  archives: {
    name: 'The Grand Archives',
    tip: 'Every day that has passed.',
    dao: 'The past is proof. Looking back at what you did is evidence that your effort counts.',
    art: 'Days come newest first, fourteen at a time. Conquered trials show their estimate and the time they took; a sprig line marks days of rest. Nothing here can be changed.',
    terms: [
      ['Lost to time', 'a Mortal Trial that was let go.'],
      ['Sent to the Horizon', 'a trial postponed, or a Mandate returned, to wait there.'],
    ],
  },
} as const satisfies Record<string, Guide>;

export const GUIDE = {
  ...DAY_GUIDES,
  ...SCROLL_GUIDES,
  ...OTHER_GUIDES,
  ...SECLUSION_GUIDES,
  ...PLAN_GUIDES,
};
export type GuideKey = keyof typeof GUIDE;
