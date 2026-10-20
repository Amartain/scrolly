<!-- Harmonious Cycles, under way. Python says the phase and the seconds left in it; this draws them and
     adds the seconds since the view arrived. Focus and break drain the ring; the break is a shade of the
     same hue. Between cycles it waits for Start, and after the last one nothing counts on. -->
<script lang="ts">
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';
  import { ringClock, useTimerDisplay } from '../../lib/timer.svelte';
  import RingFrame from './RingFrame.svelte';

  let { cycles }: { cycles: NonNullable<SeclusionState['cycles']> } = $props();

  const copy = SECLUSION.cycles;
  const live = $derived(cycles.phase === 'focus' || cycles.phase === 'break');
  const since = useTimerDisplay(
    () => ({ elapsed_s: 0, running: cycles.running && live, expected_s: null }),
    () => seclusion.receivedAt,
  );
  const left = $derived(
    live ? Math.max(0, cycles.remaining_s - since.seconds) : cycles.remaining_s,
  );
  const fill = $derived(live ? (left / cycles.total_s) * 100 : 100);
  const label = $derived(cycles.phase === 'break' ? copy.break : copy.focus);

  // When the countdown reaches zero, ask the server: it moves the run on (break, waiting or done).
  let askedAt = 0;
  $effect(() => {
    if (!live || !cycles.running || left > 0) return;
    if (askedAt === seclusion.receivedAt) return;
    askedAt = seclusion.receivedAt;
    void seclusion.load();
  });
</script>

<RingFrame
  {fill}
  tone={cycles.phase === 'break' ? 'cycles-break' : 'cycles'}
  label={cycles.phase === 'done' ? copy.done : label}
>
  {#if cycles.phase === 'done'}
    <p class="ask display">{copy.done}</p>
    <p class="small">{copy.doneHint}</p>
  {:else}
    <p class="big display digits">{ringClock(left)}</p>
    <p class="word display">{cycles.phase === 'waiting' ? copy.ready : label}</p>
    <p class="small">{copy.cycleOf(cycles.cycle, cycles.cycles)}</p>
    <p class="state display" class:hidden={cycles.running || !live}>{SECLUSION.paused}</p>
  {/if}
</RingFrame>
