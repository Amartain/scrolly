import type { Guide } from './copy-guidance';

/** The `?` scrolls of the three planning phases (owner, 2026-10-23: the guidance boxes became pop-outs).
 *  The words are the boxes' own, moved as they were. */
export const PLAN_GUIDES = {
  inscribe: {
    name: 'Inscribe the Scroll',
    tip: 'Empty your mind first.',
    dao: "To bypass the mind's resistance, do not organize or estimate yet. Empty your thoughts below.",
    art: 'One trial per line. Waiting ideas and practices join the scroll when you summon them.',
    terms: [
      ['Brain Dump', 'one trial per line.'],
      ['The Horizon', 'summon future ideas waiting for their time.'],
      ['Arts', 'opt in to habits and energy recovery without the pressure of auto-adding.'],
    ],
  },
  estimate: {
    name: 'Estimate the Journey',
    tip: 'How long will each trial take?',
    dao: 'Time blindness is conquered through practice. Divine the essence each trial needs (45m, 2h, 1h30m). A forgotten estimate can be set later.',
    art: "Watch the light: a plan that fills every minute leaves no room for the unexpected. Drag a row, or press Alt with the arrow keys, to set the order. Click a trial's mark to switch it between the two.",
    terms: [
      ['Mortal Trials', 'let them go freely, they fade at 4 AM.'],
      ['Heavenly Mandates', 'postponing sends a copy back to the Horizon.'],
    ],
  },
  weigh: {
    name: 'Weigh the Qi',
    tip: 'What each trial takes from you.',
    dao: 'Equal minutes rarely cost equal energy. Weighing your Qi teaches you what a task takes from you, not only how long it takes.',
    art: 'Give each trial a Qi cost from 0 to 100. Nothing is calculated for you: a short errand may cost 40, a long focused session only 10. Restorative Arts give Qi back.',
    terms: [
      [
        'Your core',
        'it begins at 100 Qi on a rested day. Spending past it is allowed, but the next day begins lower, because the body keeps its own ledger. Rest comes first: when tired, begin with a Restorative Art.',
      ],
    ],
  },
} as const satisfies Record<string, Guide>;
