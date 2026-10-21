<!-- The trial at hand, centred over the ring: its type mark (the Mandate/Mortal switch) and title, then
     the estimate, type and time logged, and its note behind a small button. -->
<script lang="ts">
  import TypeMark from '../../components/TypeMark.svelte';
  import { today, type Immediate } from '../../lib/api';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import { minutesText, useTimerDisplay } from '../../lib/timer.svelte';
  import { view } from '../../lib/view.svelte';

  let { trial, note }: { trial: Immediate; note: string } = $props();

  let noteOpen = $state(false);

  // The time logged on the trial itself (the ring may have been restarted since).
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

<div class="header" aria-label={SECLUSION.atHand} role="group">
  <div class="name">
    <span class="mark"
      ><TypeMark type={trial.type} title={trial.title} onToggle={toggleMandate} /></span
    >
    <span class="title read">{trial.title}</span>
  </div>
  <div class="meta">
    <span class="digits">{meta}</span>
    {#if note}
      <button
        class="note-button display"
        type="button"
        aria-expanded={noteOpen}
        onclick={() => (noteOpen = !noteOpen)}>{SECLUSION.note}</button
      >
    {/if}
  </div>
  {#if note && noteOpen}<p class="note read">{note}</p>{/if}
</div>

<style>
  .header {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-4) var(--space-5) var(--space-2);
    text-align: center;
  }

  .name {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-3);
    max-width: 100%;
  }

  .mark {
    --size-icon: var(--size-icon-large);
    flex: none;
    display: flex;
  }

  .title {
    min-width: 0;
    overflow: hidden;
    font-size: var(--text-read-lg);
    line-height: 1.1;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .meta {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }

  .note-button {
    padding-block: 0;
    padding-inline: var(--space-2);
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
    left: 50%;
    z-index: 1;
    width: max-content;
    max-width: min(28rem, 90%);
    margin: 0;
    padding: var(--space-3) var(--space-4);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
    text-align: left;
    white-space: pre-wrap;
    transform: translateX(-50%);
  }
</style>
