/** DRAFT, proposed 2026-10-21: the card that follows every conquest. */
export const QI_CARD = {
  title: 'How much qi did this take?',
  /** The three choices; a Restorative Art's Qi is what it gave back. */
  choices: { lighter: 'Lighter', foreseen: 'As foreseen', heavier: 'Heavier' },
  restoreChoices: { lighter: 'Restored less', foreseen: 'As foreseen', heavier: 'Restored more' },
  exact: 'Qi it took',
  less: 'One Qi less',
  more: 'One Qi more',
  today: 'Today',
  move: (from: number, to: number) => (from === to ? `${to}` : `${from} → ${to}`),
  confirm: 'Done',
  back: 'Take it back',
  backDescription: 'Take the conquest back',
};

/** The three stretches of the Qi gauge, named where the reading reaches them (Python says which). */
export const QI_ZONE = {
  harmonious: 'Harmonious',
  igniting: 'Igniting the Blood',
  strain: 'Strain',
} as const;
