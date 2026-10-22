/** DRAFT, proposed 2026-10-21: the card that follows every conquest. */
export const QI_CARD = {
  title: 'How much qi did this take?',
  amount: (qi: number) => `${qi} qi`,
  hint: 'It starts at what you first estimated.',
  confirm: 'Done',
  back: 'Back',
  backDescription: 'Take the conquest back',
};

/** The three stretches of the Qi gauge, named where the reading reaches them (Python says which). */
export const QI_ZONE = {
  harmonious: 'Harmonious',
  igniting: 'Igniting the Blood',
  strain: 'Strain',
} as const;
