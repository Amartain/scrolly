<!-- One line of the run that goes on while "What next?" is shown: the cycle's focus or break, or the
     rest of a Flow break. Its countdown keeps moving, and when it ends the room is read again. -->
<script lang="ts">
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';
  import { ringClock, useCountdown } from '../../lib/timer.svelte';

  let { room }: { room: SeclusionState } = $props();

  const copy = SECLUSION.cycles;
  const cycles = $derived(room.cycles);
  const flow = $derived(room.flow);
  const live = $derived(cycles?.phase === 'focus' || cycles?.phase === 'break');
  const cycleCount = useCountdown(
    () => (cycles && live ? cycles : null),
    () => seclusion.receivedAt,
    () => void seclusion.settle(),
  );
  const restCount = useCountdown(
    () =>
      flow?.phase === 'break' ? { remaining_s: flow.break_left_s, running: flow.running } : null,
    () => seclusion.receivedAt,
    () => void seclusion.settle(),
  );
</script>

{#if cycles?.phase === 'done'}
  <p class="run">{copy.done}</p>
{:else if cycles && live}
  <p class="run">
    <span class="display">{cycles.phase === 'break' ? copy.break : copy.focus}</span>
    <span class="display digits">{ringClock(cycleCount.left)}</span>
    · {copy.cycleOf(cycles.cycle, cycles.cycles)}
  </p>
{:else if flow?.phase === 'break'}
  <p class="run">
    <span class="display">{SECLUSION.flow.rest}</span>
    <span class="display digits">{ringClock(restCount.left)}</span>
  </p>
{/if}

<style>
  .run {
    display: flex;
    gap: var(--space-2);
    align-items: baseline;
    justify-content: center;
    margin: 0;
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }

  .digits {
    color: var(--ink);
    font-size: var(--text-display-md);
  }
</style>
