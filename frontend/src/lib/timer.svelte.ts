import type { Timer } from './api';
import { view } from './view.svelte';

const TICK_MS = 250;

/**
 * The seconds to show for a timer. The server sends the elapsed time as of its view; while the timer
 * runs, this only adds the time since that view arrived. Nothing is counted or saved here, and every
 * new view replaces the figure, so a closed tab or a sleeping laptop loses nothing.
 */
export function useTimerDisplay(
  timer: () => Timer | null,
  receivedAt: () => number = () => view.receivedAt,
) {
  let sinceView = $state(0);

  $effect(() => {
    if (!timer()?.running) return;
    const id = setInterval(() => (sinceView = performance.now() - receivedAt()), TICK_MS);
    return () => clearInterval(id);
  });

  return {
    get seconds(): number {
      const current = timer();
      if (!current) return 0;
      const extra = current.running ? Math.floor((performance.now() - receivedAt()) / 1000) : 0;
      void sinceView;
      return current.elapsed_s + extra;
    },
  };
}

export function clockText(seconds: number): string {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${pad(Math.floor(seconds / 3600))}:${pad(Math.floor(seconds / 60) % 60)}:${pad(seconds % 60)}`;
}

/** Whole minutes ("27m"), for the time logged. */
export const minutesText = (seconds: number) => `${Math.floor(seconds / 60)}m`;

/** The clock on the Incense ring: 44:58, or 1:05:00 from an hour up. It moves every second. */
export function ringClock(seconds: number): string {
  const total = Math.max(0, Math.floor(seconds));
  const pad = (n: number) => String(n).padStart(2, '0');
  const hours = Math.floor(total / 3600);
  const clock = `${pad(Math.floor(total / 60) % 60)}:${pad(total % 60)}`;
  return hours > 0 ? `${hours}:${clock}` : clock;
}

/** The quiet "+12m flow" shown past the estimate. Empty until a whole minute over. */
export function flowText(seconds: number, expected: number | null): string {
  if (expected === null) return '';
  const over = Math.floor((seconds - expected) / 60);
  return over >= 1 ? `+${over}m flow` : '';
}
