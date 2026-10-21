import type { Guide } from './copy-guidance';

/** DRAFT, proposed 2026-10-21: the `?` scrolls of the dashboard's second screen. */
export const SCROLL_GUIDES = {
  scribe: {
    name: 'Scribe Trial',
    tip: 'Write down a sudden trial.',
    dao: 'Ideas arrive in the middle of work. Catching one in a single line lets the mind go back to what it was doing.',
    art: 'Type a title, add an estimate if you know one (45m, 2h, 1h30m), and press Enter. It lands on top of the Remaining Trials. Press N to jump here.',
    terms: [['Scribe', 'to write a trial onto today’s scroll.']],
  },
  remaining: {
    name: 'Remaining Trials',
    tip: 'Trials waiting for their turn.',
    dao: 'A visible queue means the mind need not hold it all. The order is yours, and it may change as the day does.',
    art: 'Drag a row, or press Alt with the arrow keys, to reorder. Each row has its own buttons: promote it to the front, send it to the Horizon, or let it go.',
    terms: [['Remaining', 'a trial that has not begun yet.']],
  },
  postponed: {
    name: 'Postponed Today',
    tip: 'Sent to the Horizon today.',
    dao: 'Moving a trial is a decision, not a failure. It waits where you can find it.',
    art: 'A postponed trial keeps the time already worked on it and rests on the Horizon until you summon it again.',
    terms: [['Postponed', 'sent to the Horizon for another day.']],
  },
  fallen: {
    name: 'Fallen Leaves',
    tip: 'Trials let go today.',
    dao: 'Some trials are not worth their hours. Letting them go keeps the scroll honest, and costs nothing.',
    art: 'A Mortal Trial you abandon, or leave unfinished at 4 AM, rests here for the day and then joins the Archives as lost to time. A Heavenly Mandate is never lost: it returns to the Horizon.',
    terms: [
      ['Mortal Trial', 'an ordinary trial that dissolves at the day’s end if unfinished.'],
      ['Heavenly Mandate', 'a trial that must not be lost; it comes back to the Horizon.'],
    ],
  },
  foundational: {
    name: 'Foundational Arts',
    tip: 'Habits that take energy.',
    dao: 'What you repeat builds who you are. Arts wait until you call them; nothing is added for you.',
    art: 'Press ↑ on an Art to summon a copy onto today’s scroll. Press + to add an Art, or to rename or delete one. The Art itself stays.',
    terms: [
      ['Foundational Art', 'a habit you practise that spends energy, such as study or exercise.'],
    ],
  },
  restorative: {
    name: 'Restorative Arts',
    tip: 'Habits that give energy back.',
    dao: 'Rest is a practice too, and deserves its place on the scroll like any other.',
    art: 'Press ↑ on an Art to summon a copy onto today’s scroll. Press + to add an Art, or to rename or delete one. The Art itself stays.',
    terms: [['Restorative Art', 'a habit that gives energy back, such as a walk or a nap.']],
  },
  horizon: {
    name: 'The Horizon',
    tip: 'Ideas waiting for their time.',
    dao: 'Not everything belongs to today. The Horizon holds it without asking anything of you.',
    art: 'Add an idea with a title and, if you wish, an estimate. SUMMON calls it down to today. A postponed Mandate comes back here by itself.',
    terms: [
      ['Horizon', 'the backlog: trials that wait for a day of their own.'],
      ['Summon', 'to call a trial down onto today’s scroll.'],
    ],
  },
} as const satisfies Record<string, Guide>;
