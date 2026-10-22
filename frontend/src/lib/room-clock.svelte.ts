import type { Immediate } from './api';
import { SECLUSION } from './copy-seclusion';
import { seclusion } from './seclusion.svelte';
import type { SeclusionState } from './seclusion-api';
import { clockText, ringClock, useCountdown, useTimerDisplay } from './timer.svelte';
import { view } from './view.svelte';

/**
 * The room's run as the dashboard shows it after stepping out (owner, 2026-10-23): the cycle's focus or
 * break counting down, Flow's rest counting down, or the trial's own time while Flow banks. When a
 * countdown ends the room and the day are read again, and the sound the new phase calls for rings here.
 */
export function useRoomClock(room: () => SeclusionState | null, trial: () => Immediate) {
  const settle = async () => {
    await seclusion.settle();
    await view.refresh();
  };
  const cycleCount = useCountdown(
    () => {
      const cycles = room()?.cycles;
      return cycles && (cycles.phase === 'focus' || cycles.phase === 'break') ? cycles : null;
    },
    () => seclusion.receivedAt,
    () => void settle(),
  );
  const restCount = useCountdown(
    () => {
      const flow = room()?.flow;
      return flow?.phase === 'break'
        ? { remaining_s: flow.break_left_s, running: flow.running }
        : null;
    },
    () => seclusion.receivedAt,
    () => void settle(),
  );
  const worked = useTimerDisplay(() => trial().timer);

  const cycles = $derived(room()?.cycles ?? null);
  const flow = $derived(room()?.flow ?? null);
  const text = $derived(
    cycles
      ? ringClock(cycleCount.left)
      : flow?.phase === 'break'
        ? ringClock(restCount.left)
        : clockText(worked.seconds),
  );
  const label = $derived.by(() => {
    const copy = SECLUSION.cycles;
    if (cycles) {
      const phase = cycles.phase === 'break' ? copy.break : copy.focus;
      return `${phase} · ${copy.cycleOf(cycles.cycle, cycles.cycles)}`;
    }
    if (flow?.phase === 'break') return SECLUSION.flow.rest;
    return flow ? SECLUSION.flow.banked(Math.floor(flow.banked_s / 60)) : '';
  });
  /** The colour token of a break, which frames the clock in the shade of its tab. */
  const tone = $derived(
    cycles?.phase === 'break' ? 'cycles-break' : flow?.phase === 'break' ? 'flow-break' : null,
  );

  return {
    get text() {
      return text;
    },
    get label() {
      return label;
    },
    get tone() {
      return tone;
    },
  };
}
