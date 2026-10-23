/**
 * The way up to Seclusion and back down (owner, 2026-10-23). The dashboard is the foot of the mountain;
 * ↑ (or F, or the moon gate) climbs to the room, ↓ or Esc comes back. Only how it looks.
 *
 * The frequency rule (owner): a show seen recently is not shown again, since stepping out and back in
 * is often a quick check. The full rise, the scene painted upward, plays on the first way up of a visit
 * and again after FULL_AGAIN_MS without one; otherwise the window simply opens. Already meditating up
 * there: the window opens, nothing is painted. Under reduced motion, or without view transitions, the
 * screen just changes.
 */

import { tick } from 'svelte';

export type Way = 'rise' | 'open' | 'down' | 'none';

/** How long until the full rise is shown again. */
const FULL_AGAIN_MS = 30 * 60_000;

let lastRise = -Infinity;

const still = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches || !document.startViewTransition;

/** Which way up this one is: the full rise, the window opening, or no motion at all. */
export function wayUp(meditating: boolean): Way {
  if (still()) return 'none';
  if (meditating || performance.now() - lastRise < FULL_AGAIN_MS) return 'open';
  lastRise = performance.now();
  return 'rise';
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
