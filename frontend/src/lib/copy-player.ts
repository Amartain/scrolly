/** The player's words: the System's reward after the Arise window, and Settings › Aura.
 *  DRAFT (owner to approve; docs/copy-queue.md › Player). */
import type { AuraColour } from './player-api';

export const REWARD = {
  header: '[ QUEST COMPLETED ]',
  quest: 'Hidden Quest: The Courage to Become a Player',
  granted: 'Rewards granted',
  items: ['Cultivation Robes of the System (blue)', 'Aura of the Awakened (blue)'],
  hint: 'The Player may now choose their own aura. Settings › Aura.',
  confirm: '[ Confirm ]',
} as const;

export const AURA = {
  title: 'Aura',
  note: 'Player privilege: choose the colours your cultivator wears.',
  robe: 'Robe',
  glow: 'Glow',
  own: "The theme's own",
  shine: 'Let the aura shine always',
  names: {
    'system-blue': 'System blue',
    gold: 'Gold',
    jade: 'Jade',
    teal: 'Teal',
    crimson: 'Crimson',
    violet: 'Violet',
    cream: 'Cream',
  } satisfies Record<AuraColour, string>,
} as const;
