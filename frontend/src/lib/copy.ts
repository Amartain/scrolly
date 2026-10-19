/**
 * Empty-state lines. DRAFT copy for the owner to review: short, wuxia-flavoured, our own words
 * (nothing here is a quote or a poem).
 */
export const EMPTY = {
  immediate: 'The path lies quiet. No trial is underway.',
  conquered: 'No trial conquered yet. The day waits for your first step.',
  remaining: 'The queue rests. Scribe a trial, or call one down from the Horizon.',
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
