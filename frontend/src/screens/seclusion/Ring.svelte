<!-- The Incense ring. Python says whether it is counting down or overfilled; this only draws it and
     adds the seconds since the view arrived. Past the estimate the ring turns a brighter shade. -->
<script lang="ts">
  import SetOnce from '../../components/SetOnce.svelte';
  import { today, type Immediate } from '../../lib/api';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';
  import { leftText, useTimerDisplay } from '../../lib/timer.svelte';

  let { room, trial }: { room: SeclusionState; trial: Immediate } = $props();

  const running = $derived(trial.timer.running);
  const clock = useTimerDisplay(
    () => ({ elapsed_s: room.ring_elapsed_s, running, expected_s: null }),
    () => seclusion.receivedAt,
  );

  const incense = $derived(room.incense);
  const extra = $derived(clock.seconds - room.ring_elapsed_s);
  const left = $derived((incense?.remaining_s ?? 0) - extra);
  const over = $derived((incense?.over_s ?? 0) + extra);
  const overfilled = $derived(incense?.state === 'overfilled');
  const expected = $derived(trial.timer.expected_s);
  // The incense burns down: the colour is what remains and shrinks. Past the estimate the ring is
  // full again in the brighter shade. Only the angle of the arc is worked out here.
  const fill = $derived.by(() => {
    if (overfilled) return 100;
    if (!expected) return 0;
    return Math.max(0, 100 - (clock.seconds / expected) * 100);
  });

  // When the countdown reaches zero, ask the server: it says when the ring is overfilled.
  let askedAt = 0;
  $effect(() => {
    if (incense?.state !== 'remaining' || !running || left > 0) return;
    if (askedAt === seclusion.receivedAt) return;
    askedAt = seclusion.receivedAt;
    void seclusion.load();
  });

  const setEstimate = (estimate: string) =>
    seclusion.trial(() => today.update(trial.id, { estimate }));
</script>

<div
  class="ring"
  style:--fill={fill}
  data-over={overfilled || undefined}
  role="timer"
  aria-label={overfilled ? SECLUSION.pastEstimate(trial.expected_text) : SECLUSION.remaining}
>
  <div class="inner">
    {#if !incense}
      <p class="ask display">{SECLUSION.askEstimate}</p>
      <SetOnce
        kind="time"
        value=""
        label="Estimate for {trial.title}"
        confirm="Set the time for {trial.title}"
        onsave={setEstimate}
      />
    {:else if overfilled}
      <p class="big display">+{Math.floor(over / 60)}m</p>
      <p class="small">{SECLUSION.pastEstimate(trial.expected_text)}</p>
    {:else}
      <p class="big display digits">{leftText(left)}</p>
      <p class="word display">{SECLUSION.remaining}</p>
      <p class="small">{SECLUSION.ofEstimate(trial.expected_text)}</p>
    {/if}
    <p class="state display" class:hidden={running || room.ring_elapsed_s === 0 || !incense}>
      {SECLUSION.paused}
    </p>
  </div>
</div>

<style>
  .ring {
    --ring-fill: var(--gold);
    flex: none;
    display: grid;
    place-items: center;
    width: var(--size-ring);
    aspect-ratio: 1;
    border-radius: 50%;
    background: conic-gradient(var(--ring-fill) calc(var(--fill) * 1%), var(--inset) 0);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
  }

  .ring[data-over] {
    --ring-fill: var(--ring-over);
  }

  .inner {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-1);
    width: calc(100% - var(--size-ring-band) * 2);
    aspect-ratio: 1;
    padding: var(--space-4);
    border-radius: 50%;
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    text-align: center;
  }

  .inner p {
    margin: 0;
  }

  .big {
    color: var(--num);
    font-size: var(--text-numeral-ring);
    line-height: 1;
    text-shadow: var(--space-1) var(--space-1) 0 var(--num-shadow);
    text-transform: none;
  }

  .word {
    font-size: var(--text-display-md);
  }

  .ask {
    max-width: 14rem;
    font-size: var(--text-display-sm);
  }

  .small {
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }

  .state {
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
  }

  .hidden {
    visibility: hidden;
  }
</style>
