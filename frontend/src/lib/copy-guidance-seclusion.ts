import type { Guide } from './copy-guidance';

/** DRAFT, proposed 2026-10-21: the `?` scrolls of the focus room and its Parallel sidebar. Plain, modern
 *  words: every button and key is named. Listed in docs/copy-queue.md › Proposed. */
export const SECLUSION_GUIDES = {
  seclusion: {
    name: 'Seclusion',
    tip: 'One trial, three kinds of timer.',
    dao: 'A narrow room makes work easier to begin. Only the trial at hand is shown, so nothing else pulls at you. Pick the timer that suits how you work today.',
    art: 'Trial of the Incense counts down to your estimate; past it the ring overfills and counts up, with a soft gong every 30 minutes. Harmonious Cycles is a Pomodoro timer: focus, then a short break, for as many rounds as you set on the dial. River Flow is a Flowmodoro: it counts up while you work and banks rest at the ratio you choose (3 : 1 banks a minute of rest for every three of work), to spend when you like.',
    terms: [
      [
        '↻ Restart',
        'the timer starts again from zero, at once. Its minutes come off the trial; you are asked first.',
      ],
      [
        '⏮ Zero out',
        'Cycles and Flow: only the stretch under way goes back to zero (cycle 2 stays cycle 2). Its minutes come off the trial; you are asked first.',
      ],
      ['⏸ Pause, ▶ Start', 'stop or start the clock.'],
      ['⏭ Break', 'take a break now, or skip the one under way.'],
      ['■ Stop', 'end the Cycles or Flow run and set it up again. Your time is kept.'],
      [
        '⇄ Switch',
        'pick another waiting trial. This one steps back, paused, to the top of Remaining.',
      ],
      ['➔ and ✖', 'postpone a Heavenly Mandate to the Horizon, or let a Mortal Trial go.'],
    ],
    keys: [
      ['Space', 'start or pause'],
      ['Enter', 'Conquered!'],
      ['N', 'write a sudden trial'],
      ['Ctrl+B', 'hide or show the Parallel sidebar'],
      ['Esc', 'step out (the trial pauses)'],
    ],
  },
  sidebar: {
    name: 'Parallel sidebar',
    tip: 'Side work, sudden trials, loose notes.',
    dao: 'Your mind keeps handing you things while you focus. Give each one a place to land, and the trial at hand keeps your attention.',
    art: 'Parallel Flow runs a second, simpler trial beside this one (laundry while you write) with its own count-up and its own time. Scribe Trial puts a sudden trial on top of Remaining without leaving the room. Bamboo Scraps is a notepad for loose thoughts: it saves itself, and each visit keeps its own scrap on the Bamboo Scraps page.',
    terms: [
      ['Parallel Flow', 'a second trial with its own timer. It never adds to the trial at hand.'],
      ['Scribe', 'write down. The trial waits on top of Remaining.'],
      ['Bamboo Scraps', 'the notes of one visit to Seclusion.'],
    ],
    keys: [
      ['N', 'jump to Scribe Trial'],
      ['Ctrl+B', 'hide or show this sidebar'],
      ['Ctrl+X', 'with nothing selected, cut the whole line in Bamboo Scraps'],
    ],
  },
} as const satisfies Record<string, Guide>;
