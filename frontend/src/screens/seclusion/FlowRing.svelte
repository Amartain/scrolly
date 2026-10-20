<!-- River Flow. Before the first Start the ratio is set here (work : rest). Then it counts up and banks
     rest as the focus goes on; a break counts the bank down, in the break shade. Python holds the bank;
     this adds the seconds since the view arrived. -->
<script lang="ts">
  import { untrack } from 'svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';
  import { ringClock, useCountdown, useTimerDisplay } from '../../lib/timer.svelte';
  import RingFrame from './RingFrame.svelte';
  import Stepper from './Stepper.svelte';

  let { room, flow }: { room: SeclusionState; flow: NonNullable<SeclusionState['flow']> } =
    $props();

  const copy = SECLUSION.flow;
  // The ratio is kept here while it is being set, so two quick changes cannot undo each other.
  let work = $state(untrack(() => flow.work));
  let rest = $state(untrack(() => flow.rest));
  function setRatio(nextWork: number, nextRest: number) {
    work = nextWork;
    rest = nextRest;
    void seclusion.setRatio(nextWork, nextRest);
  }
  const resting = $derived(flow.phase === 'break');
  const since = useTimerDisplay(
    () => ({ elapsed_s: 0, running: flow.running, expected_s: null }),
    () => seclusion.receivedAt,
  );
  const elapsed = $derived(flow.focus_s + (resting ? 0 : since.seconds));
  // The bank grows as the focus does; the server holds the real figure and says when a break can start.
  const banked = $derived(flow.banked_s + Math.floor((since.seconds * flow.rest) / flow.work));
  // When the rest runs out, the room is read again: focus then waits for Start.
  const count = useCountdown(
    () => (resting ? { remaining_s: flow.break_left_s, running: flow.running } : null),
    () => seclusion.receivedAt,
    () => void seclusion.settle(),
  );
  const left = $derived(count.left);
  const fill = $derived(resting ? (left / flow.break_total_s) * 100 : 100);

  // The server says when a break can first start; the browser only asks again then.
  $effect(() => {
    const due = flow.break_in_s;
    if (due == null || !flow.running || flow.can_break) return;
    const wait = due * 1000 - (performance.now() - seclusion.receivedAt);
    const id = setTimeout(() => void seclusion.load(), Math.max(0, wait));
    return () => clearTimeout(id);
  });
</script>

<RingFrame {fill} tone={resting ? 'flow-break' : 'flow'} label={resting ? copy.rest : copy.elapsed}>
  {#if flow.phase === 'idle'}
    <p class="ask display">{copy.ratio}</p>
    <div class="ratio">
      <span class="tag display">{copy.work}</span>
      <Stepper
        value={work}
        min={1}
        max={room.limits.ratio_max}
        label={copy.work}
        onchange={(next) => setRatio(next, rest)}
      />
      <span class="tag display">{copy.rest}</span>
      <Stepper
        value={rest}
        min={1}
        max={room.limits.ratio_max}
        label={copy.rest}
        onchange={(next) => setRatio(work, next)}
      />
    </div>
    <p class="small">{copy.idleHint}</p>
  {:else if resting}
    <p class="big display digits">{ringClock(left)}</p>
    <p class="word display">{copy.rest}</p>
    <p class="small">{copy.ofBanked(Math.floor(flow.break_total_s / 60))}</p>
  {:else}
    <p class="big display digits">{ringClock(elapsed)}</p>
    <p class="word display">{copy.elapsed}</p>
    <p class="small">{copy.banked(Math.floor(banked / 60))}</p>
    <p class="state display" class:hidden={flow.running}>{SECLUSION.paused}</p>
  {/if}
</RingFrame>

<style>
  .ratio {
    display: grid;
    grid-template-columns: auto auto;
    align-items: center;
    gap: var(--space-2) var(--space-3);
  }

  .tag {
    font-size: var(--text-display-sm);
    text-align: right;
  }
</style>
