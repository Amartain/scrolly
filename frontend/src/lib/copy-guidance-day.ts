import type { Guide } from './copy-guidance';

/** DRAFT, proposed 2026-10-21: the `?` scrolls of the dashboard's first screen. */
export const DAY_GUIDES = {
  immediate: {
    name: 'The Immediate Trial',
    tip: 'The one trial to do now.',
    dao: 'Attention rests when there is one thing to hold. The Immediate Trial is the only trial that asks anything of you now; the rest of the scroll can wait.',
    art: 'Press the play button to start its timer, or ENTER SECLUSION (F) for a quiet room. Press Conquered! when it is done, ➔ to send it to the Horizon, ✖ to let it go.',
    terms: [['Immediate Trial', 'the trial you are on now, at the front of the scroll.']],
  },
  conquered: {
    name: 'Conquered Today',
    tip: 'What you have finished today.',
    dao: 'Seeing what is done is fuel. Nothing here is ever taken away, and nothing here is graded.',
    art: 'Each row shows the time the trial really took. If you marked one done by mistake, Revive it, run its timer again and conquer it for the true time.',
    terms: [['Conquered', 'finished, and kept on the scroll for the day.']],
  },
  essence: {
    name: 'Essence',
    tip: 'Minutes done against minutes planned.',
    dao: 'Time is easy to misjudge. Setting the plan beside what happened trains the eye, and gives no verdict.',
    art: 'The bar fills as conquered time meets the time planned. Going past it only keeps counting, quietly.',
    terms: [['Essence', 'the minutes a trial takes, as planned and as lived.']],
  },
  momentum: {
    name: 'Momentum',
    tip: 'Your progress, always rising.',
    dao: 'A line that only climbs shows the whole road, not one bad week. Every conquest raises it.',
    art: 'Switch between Trials, Essence and, with the Golden Core on, Qi. Days with nothing new are left out, so the line never falls.',
    terms: [['Momentum', 'your progress added up over every day you have used Scrolly.']],
  },
  rhythm: {
    name: 'Rhythm',
    tip: 'The last seven days.',
    dao: 'Rhythm matters more than intensity. A day of rest is part of the pattern, not a hole in it.',
    art: 'Each bar is one day. The scale is squeezed so one huge day never hides the others, and a sprig marks a day of rest.',
    terms: [['Rest', 'a day with nothing conquered, drawn as a sprig.']],
  },
} as const satisfies Record<string, Guide>;
