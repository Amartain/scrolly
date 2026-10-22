/**
 * Empty-state lines. DRAFT copy for the owner to review: short, wuxia-flavoured, our own words
 * (nothing here is a quote or a poem).
 */
export const EMPTY = {
  immediate: 'The sword rests across your knees; no trial stands before you.',
  conquered: 'No trial conquered yet. The day waits for your first step.',
  remaining:
    'No disciple waits at the mountain gate. Scribe a trial, or call one down from beyond the Horizon.',
  postponed: 'Nothing was sent to the Horizon today.',
  fallen: 'No leaf has fallen today.',
  foundational: 'No foundational art practised here yet.',
  restorative: 'No restorative art gathered yet.',
  horizon: 'The Horizon is clear. Mist hangs over distant peaks.',
  onScroll: 'The scroll is blank. Summon a trial, or scribe one.',
} as const;

/** A line of a note; `em` marks a user's title, shown in italics. */
export interface Segment {
  text: string;
  em?: boolean;
}

/** The facts behind a refused title (the server reports them; the words are ours). */
export interface TitleRefusal {
  repeated: string[];
  horizon: string[];
  today: string[];
  art: string[];
}

const em = (text: string): Segment => ({ text, em: true });
const plain = (text: string): Segment => ({ text });

function titles(names: string[]): Segment[] {
  return names.flatMap((name, i) => (i === 0 ? [em(name)] : [plain(', '), em(name)]));
}

/**
 * DRAFT, accepted 2026-10-19: the notes for a title that is already taken. One title gets the full
 * explanation; a Phase 1 dump with several names every offender.
 */
export function refusalNote(refusal: TitleRefusal): Segment[] {
  const { repeated, horizon, today, art } = refusal;
  const total = repeated.length + horizon.length + today.length;
  if (total === 0 && art.length > 0)
    return [plain('That Art is already in this list: '), ...titles(art)];
  if (total === 1 && today.length === 1) {
    const [title] = today;
    return [
      plain('Already on this scroll: '),
      em(title),
      plain(
        '. Repeat practices belong in the Arts, where the same name can come round again. ' +
          'For a one-time trial, give each its own name: ',
      ),
      em(`${title}, Second Pot`),
      plain('.'),
    ];
  }
  if (total === 1 && horizon.length === 1) {
    const [title] = horizon;
    return [
      plain('Already on the Horizon: '),
      em(title),
      plain(
        '. Trials are one-time. Summon that Horizon item instead, or give this one its own name, like ',
      ),
      em(`${title}, Second Pot`),
      plain('.'),
    ];
  }
  const sentences: [string, string[]][] = [
    ['Written twice: ', repeated],
    ['Already on the Horizon: ', horizon],
    ['Already on this scroll: ', today],
  ];
  return sentences
    .filter(([, names]) => names.length > 0)
    .flatMap(([lead, names], i) => [plain(i === 0 ? lead : `. ${lead}`), ...titles(names)]);
}

/** DRAFT, proposed 2026-10-19: said over the fogged charts until the first trial is conquered. */
export const INVITE = {
  momentum: 'Conquer your first trial to reveal your cultivation momentum.',
  rhythm: 'Conquer your first trial to reveal your cultivation rhythm.',
} as const;

/** Names on the chart toggle. */
export const METRIC_LABEL = { trials: 'Trials', essence: 'Essence', qi: 'Qi' } as const;

/** DRAFT: the overlay after the day's first seal. The count is Heavenly Cycles, never "consecutive". */
export const MILESTONE = {
  title: 'Heavenly Cycles',
  one: 'day sealed upon the scroll',
  many: 'days sealed upon the scroll',
  close: 'Onward',
} as const;

/** DRAFT: how much of a Horizon item's time was already worked, shown small beside its estimate. */
export const workedNote = (text: string) => `· ${text} worked`;

/** DRAFT: the one-time sunset question in the Day Summary, and its quiet states. */
export const SUNSET = {
  ask: 'Your sunset?',
  set: 'Set',
  later: 'Not now',
  hint: 'Use a time like 21:00',
  off: 'No sunset kept. The Day Summary shows totals only.',
  kept: (at: string) => `Sunset at ${at}`,
  none: 'No sunset kept',
} as const;

/** DRAFT: the overrun advisor, one gentle word when the open trials would run past sunset. */
export const ADVISOR = {
  title: 'The Light Grows Short',
  body: 'The trials still open reach past the sunset. You may send the waiting Heavenly Mandates to the Horizon, or carry on as you are.',
  bodyNoMandates:
    'The trials still open reach past the sunset. Carry on as you are, or let some go as the day asks.',
  postpone: 'Postpone Mandates to Horizon',
  dismiss: 'Dismiss',
  never: 'Not again today',
  wake: 'Let the advisor speak again today',
} as const;

/** DRAFT: the sunset poem. */
export const POEM = {
  title: 'Sunset Poem',
  close: 'Settle Qi',
} as const;

/** DRAFT: Settings › Data. */
export const DATA = {
  hint: 'Reads a Scrolly backup (.zip), a table (.csv), an old backup (.json) or a Discord Dispatch (.md).',
  replaceTitle: 'Replace everything?',
  replaceBody:
    'This backup takes the place of everything Scrolly holds now. A copy of the current data is saved first, in the backups folder.',
  replace: 'Replace',
  purgeTitle: "Purge Today's Scroll?",
  purgeBody:
    "Today's open trials are cleared. Conquered trials stay, and Heavenly Mandates and trials called down from the Horizon go back to it with the time worked.",
  purge: 'Purge',
  cancel: 'Cancel',
  purged: "Today's scroll is clear.",
} as const;

/** DRAFT: the Dispatch screen and the Symbols settings. */
export const DISPATCH = {
  title: 'Scroll of Heavenly Tribulations',
  open: 'DISPATCH',
  clip: 'Clip to Scroll',
  clipped: 'Clipped. Paste it where your companions gather.',
  unclipped: 'The clipboard would not open. Select the text and copy it by hand.',
  dnd: 'DND header',
  postponed: 'Include postponed',
  abandoned: 'Include abandoned',
  back: 'Back',
} as const;

export const SYMBOLS = {
  title: 'Symbols',
  note: 'Your own emoji and Discord shortcodes for the Legend of the Scrolls. Each one stands for a single meaning.',
  reset: 'Default',
} as const;

/** DRAFT: Settings › Header and the feedback links. */
export const HEADER = {
  title: 'Header',
  auto: 'Match the theme',
  custom: 'My own picture',
  choose: 'Choose a picture',
  hint: 'PNG, JPEG or WebP, up to 5 MB. It stays on this computer.',
} as const;

export const FEEDBACK = {
  title: 'Feedback',
  note: 'These open a short form in your browser.',
  links: [
    { label: 'Report a bug', href: 'https://forms.gle/fsEJDygF3FCKrstu7' },
    { label: 'Share a thought', href: 'https://forms.gle/BbMjJ7xN1BJtFb7q9' },
    { label: 'Write to the developer', href: 'https://forms.gle/haR4N5k7npJTWMLi9' },
  ],
} as const;

/** DRAFT: Settings › Secret Seal Inscription. */
export const SEAL = {
  title: 'Secret Seal Inscription',
  placeholder: 'Inscribe a word…',
  inscribe: 'Inscribe',
  unknown: 'The scroll does not answer to those words.',
} as const;

/** DRAFT: the planning timer. */
export const PLANNING_TIME = {
  start: 'Start planning time',
  pause: 'Pause planning time',
  reset: 'Reset planning time',
  label: 'Time spent planning',
} as const;
