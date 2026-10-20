<!-- The trial at hand: its type mark (the Mandate/Mortal switch), title, estimate, time logged, notes. -->
<script lang="ts">
  import TypeMark from '../../components/TypeMark.svelte';
  import { today, type Immediate } from '../../lib/api';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import { minutesText, useTimerDisplay } from '../../lib/timer.svelte';
  import { view } from '../../lib/view.svelte';

  let { trial, note }: { trial: Immediate; note: string } = $props();

  let noteOpen = $state(false);

  // The time logged on the trial itself (the ring may have been zeroed since).
  const logged = useTimerDisplay(
    () => trial.timer,
    () => seclusion.receivedAt,
  );

  const meta = $derived(
    [
      trial.expected_text ? SECLUSION.expected(trial.expected_text) : '',
      view.current?.legend.types[trial.type]?.label ?? '',
      SECLUSION.logged(minutesText(logged.seconds)),
    ]
      .filter(Boolean)
      .join(' · '),
  );

  const toggleMandate = () =>
    seclusion.trial(() => today.update(trial.id, { is_mandate: !trial.is_mandate }));
</script>

<div class="header">
  <span class="mark"
    ><TypeMark type={trial.type} title={trial.title} onToggle={toggleMandate} /></span
  >
  <div class="text">
    <span class="label display">{SECLUSION.atHand}</span>
    <span class="title read">{trial.title}</span>
    <span class="meta digits">{meta}</span>
  </div>
  {#if note}
    <button
      class="note-button display"
      type="button"
      aria-expanded={noteOpen}
      onclick={() => (noteOpen = !noteOpen)}>{SECLUSION.note}</button
    >
    {#if noteOpen}<p class="note read">{note}</p>{/if}
  {/if}
</div>

<style>
  .header {
    position: relative;
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-3) var(--space-5);
  }

  .mark {
    --size-icon: var(--size-icon-large);
    display: flex;
  }

  .text {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .label {
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
  }

  .title {
    font-size: var(--text-read-lg);
    line-height: 1.1;
  }

  .meta {
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }

  .note-button {
    flex: none;
    padding: var(--space-1) var(--space-3);
    background: var(--surface-raised);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-sm);
    cursor: pointer;
  }

  /* The note opens over the ring's area, so nothing below it moves. */
  .note {
    position: absolute;
    top: 100%;
    right: var(--space-5);
    z-index: 1;
    max-width: 28rem;
    margin: 0;
    padding: var(--space-3) var(--space-4);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
    white-space: pre-wrap;
  }
</style>
