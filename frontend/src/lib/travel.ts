/**
 * The way up to Seclusion and back down (owner, 2026-10-23). The room sits above the dashboard, as the
 * peak above its foot. Only how it looks.
 *
 * - climb (↑): the screen scrolls slowly up into the room while its painting washes in from the foot.
 * - summon (Enter Seclusion, F): "almost like a heavenly summon", the dashboard dissolves and the scene
 *   is painted in place.
 * - slide: like switching desktops, the room, already whole (card, timer, bars), scrolls into view.
 *   ↓ and Esc slide back down.
 *
 * The frequency rule (owner): a show seen lately is not shown again. The climb and the summon play
 * when the user's interval (Settings › Seclusion, 0 = every time) has passed since the last one, and
 * never while a focus started in the room goes on (a timer started on the dashboard still gets one).
 * Otherwise the slide. Under reduced motion, or without view transitions, the screen just changes.
 */

import { tick } from 'svelte';

export type Way = 'climb' | 'summon' | 'slide' | 'down' | 'none';

let lastFull = -Infinity;

const still = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches || !document.startViewTransition;

/** Which way up this one is. `by`: the ↑ key climbs, the gate (button or F) summons. */
export function wayUp(by: 'key' | 'gate', intervalMin: number, roomFocus: boolean): Way {
  if (still()) return 'none';
  const now = performance.now();
  if (roomFocus || now - lastFull < intervalMin * 60_000) return 'slide';
  lastFull = now;
  return by === 'key' ? 'climb' : 'summon';
}

export function wayDown(): Way {
  return still() ? 'none' : 'down';
}

/** Change the screen along that way: styles/travel.css draws it from `data-travel` on the root. */
export async function travel(way: Way, change: () => void): Promise<void> {
  if (way === 'none') {
    change();
    return;
  }
  const root = document.documentElement;
  root.dataset.travel = way;
  const transition = document.startViewTransition(async () => {
    change();
    await tick();
  });
  await transition.finished.catch(() => undefined); // a transition cut short still changed the screen
  delete root.dataset.travel;
}
