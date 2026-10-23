<!-- A quiet count-up of the time spent planning, bottom-left in Phases 2 and 3 (Phase 1 has Knowledge
     of the Dao there instead, owner 2026-10-23). It never nags: no target, no alarm. The time is kept
     for each day and survives a reload, a sleep or a crash. -->
<script lang="ts">
  import GlyphIcon from '../icons/GlyphIcon.svelte';
  import { planningTimer } from '../lib/api';
  import { PLANNING_TIME } from '../lib/copy';
  import { clockText, useTimerDisplay } from '../lib/timer.svelte';
  import { view } from '../lib/view.svelte';
  import GlyphButton from './GlyphButton.svelte';

  const timer = $derived(view.planning?.timer ?? null);
  const display = useTimerDisplay(() => timer);
  const running = $derived(timer?.running ?? false);
</script>

<div class="timer" role="group" aria-label={PLANNING_TIME.label}>
  <GlyphButton
    tour="planning-clock"
    label={running ? PLANNING_TIME.pause : PLANNING_TIME.start}
    onclick={() => view.act(running ? planningTimer.pause : planningTimer.start)}
  >
    <GlyphIcon name={running ? 'pause' : 'play'} />
  </GlyphButton>
  <span class="clock digits" role="timer" aria-label={PLANNING_TIME.label}
    >{clockText(display.seconds)}</span
  >
  <GlyphButton label={PLANNING_TIME.reset} onclick={() => view.act(planningTimer.reset)}>
    <GlyphIcon name="reset" />
  </GlyphButton>
</div>

<style>
  /* In the planning corner (PlanningCorner.svelte), so nothing moves when it ticks. */
  .timer {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-3);
    background: var(--surface-panel);
    background-image: var(--gloss-faint);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .clock {
    min-width: 5em;
    text-align: center;
    color: var(--ink-muted);
    font-size: var(--text-body-lg);
  }
</style>
