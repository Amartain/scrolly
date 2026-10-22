<script lang="ts">
  import { untrack } from 'svelte';
  import ConquerButton from '../../components/ConquerButton.svelte';
  import GlyphButton from '../../components/GlyphButton.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { today, type Immediate } from '../../lib/api';
  import { conquer, toggleTimer } from '../../lib/immediate';
  import { useRoomClock } from '../../lib/room-clock.svelte';
  import { seclusion } from '../../lib/seclusion.svelte';
  import { clockText, flowText, useTimerDisplay } from '../../lib/timer.svelte';
  import { view } from '../../lib/view.svelte';

  let { trial }: { trial: Immediate } = $props();

  const display = useTimerDisplay(() => trial.timer);
  // The room's Cycles or Flow run goes on after stepping out: this card shows its clock and drives it.
  const room = $derived(seclusion.state?.run_under_way ? seclusion.state : null);
  const roomClock = useRoomClock(
    () => room,
    () => trial,
  );
  const running = $derived(room ? seclusion.running : trial.timer.running);
  // A conquest or a start here can move the room's run: read the room again after each new view.
  $effect(() => {
    void trial.id;
    void trial.timer;
    untrack(() => {
      if (seclusion.state?.run_under_way || seclusion.state?.parallel) void seclusion.load();
    });
  });
  const flow = $derived(flowText(display.seconds, trial.timer.expected_s));
</script>

<div class="controls">
  <button
    class="play"
    type="button"
    aria-label={running ? 'Pause timer' : 'Start timer'}
    onclick={() => toggleTimer(trial)}
  >
    <span class="big-glyph"><GlyphIcon name={running ? 'pause' : 'play'} /></span>
  </button>
  {#if room}
    <span
      class="clock digits"
      class:running
      style:border-color={roomClock.tone ? `var(--${roomClock.tone})` : undefined}
      role="timer"
      aria-label="The room's clock">{roomClock.text}</span
    >
    <span class="of">{roomClock.label}</span>
  {:else}
    <span class="clock digits" class:running role="timer" aria-label="Elapsed time"
      >{clockText(display.seconds)}</span
    >
    <GlyphButton label="Reset timer" onclick={() => view.act(() => today.resetTimer(trial.id))}>
      <GlyphIcon name="reset" />
    </GlyphButton>
    {#if trial.expected_text}<span class="of">of {trial.expected_text}</span>{/if}
    {#if flow}<span class="of">{flow}</span>{/if}
  {/if}
  <span class="spacer"></span>
  <ConquerButton label="Conquered!" title={trial.title} onclick={() => conquer(trial)} />
  <span class="postpone">
    <GlyphButton
      label="Postpone {trial.title} to the Horizon"
      onclick={() => view.act(() => today.postpone(trial.id))}
    >
      <GlyphIcon name="arrow" />
    </GlyphButton>
  </span>
  {#if !trial.is_mandate}
    <GlyphButton
      label="Abandon {trial.title}"
      onclick={() => view.act(() => today.abandon(trial.id))}
    >
      <GlyphIcon name="x" />
    </GlyphButton>
  {/if}
</div>

<style>
  .controls {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .play {
    flex: none;
    display: flex;
    align-items: center;
    justify-content: center;
    width: var(--size-icon-button);
    height: var(--size-icon-button);
    padding: 0;
    cursor: pointer;
    background: var(--growth);
    color: var(--on-growth);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
  }

  .play:active {
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }

  .big-glyph {
    display: flex;
    width: var(--size-icon);
    height: var(--size-icon);
  }

  .big-glyph :global(.glyph) {
    width: 100%;
    height: 100%;
  }

  /* The clock is the card's big number, gold with a hard shadow like the counters. Its frame turns gold
     while it runs: still, so it can be read at a glance without anything moving. */
  .clock {
    padding: var(--space-1) var(--space-3);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--num);
    font-family: var(--font-display);
    font-size: var(--text-display-xl);
    line-height: 1;
    text-shadow: var(--space-1) var(--space-1) 0 var(--num-shadow);
    white-space: nowrap;
  }

  .clock.running {
    border-color: var(--gold);
  }

  .of {
    color: var(--ink-muted);
    white-space: nowrap;
  }

  .spacer {
    flex: 1;
  }

  .postpone {
    --glyph-ink: var(--postponed);
    display: flex;
  }
</style>
