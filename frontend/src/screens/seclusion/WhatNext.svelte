<!-- After a trial ends: the next one waits, idle. Start it, pick another from Remaining, or take it back. -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import type { Immediate } from '../../lib/api';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';
  import RunStatus from './RunStatus.svelte';

  let { room, trial }: { room: SeclusionState; trial: Immediate } = $props();

  let choosing = $state(false);
  const finished = $derived(seclusion.finished);

  const cycles = $derived(room.cycles);
  const flow = $derived(room.flow);
  const inRun = $derived(Boolean(cycles || flow));

  // What goes on: carry the run on with the next trial, or (Incense) a fresh timer on it.
  const carry = $derived.by(() => {
    if (cycles) {
      if (cycles.phase === 'focus') return SECLUSION.continueCycle;
      return cycles.phase === 'waiting' ? SECLUSION.start : null;
    }
    if (flow)
      return flow.phase === 'break'
        ? null
        : flow.phase === 'idle'
          ? SECLUSION.start
          : SECLUSION.continueFlow;
    return SECLUSION.startNewTimer;
  });
  const canBreak = $derived(cycles?.phase === 'focus' || (flow?.can_break ?? false));
</script>

<div class="card" role="group" aria-label={SECLUSION.whatNext}>
  <h2 class="heading display">{SECLUSION.whatNext}</h2>
  {#if choosing}
    <ul class="list">
      {#each room.remaining as waiting (waiting.id)}
        <li>
          <button
            class="row"
            type="button"
            aria-label="{SECLUSION.switchTo} {waiting.title}"
            onclick={() => seclusion.switchTo(waiting.id)}
          >
            <span class="mark"><TypeMark type={waiting.type} title={waiting.title} /></span>
            <span class="read">{waiting.title}</span>
          </button>
        </li>
      {/each}
    </ul>
    <button class="link display" type="button" onclick={() => (choosing = false)}
      >{SECLUSION.back}</button
    >
  {:else}
    <RunStatus {room} />
    <p class="next">
      <span class="label display">{SECLUSION.next}</span> <span class="read">{trial.title}</span>
    </p>
    <div class="actions">
      {#if carry}
        <Button
          label={carry}
          tone="primary"
          description="{carry}: {trial.title}"
          onclick={inRun ? seclusion.start : seclusion.newTimer}
        />
      {/if}
      {#if canBreak}
        <Button label={SECLUSION.takeBreakNow} onclick={seclusion.takeBreak} />
      {/if}
      {#if inRun}
        <Button label={SECLUSION.startNewCycle} onclick={seclusion.newTimer} />
      {/if}
      {#if room.remaining.length > 0}
        <Button label={SECLUSION.switchTrials} onclick={() => (choosing = true)} />
      {/if}
    </div>
    {#if finished?.how === 'conquered'}
      <button class="link display" type="button" onclick={() => seclusion.undo()}
        >{SECLUSION.undo}</button
      >
    {/if}
  {/if}
</div>

<style>
  .card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-4);
    width: min(32rem, 100%);
    padding: var(--space-5);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .heading {
    margin: 0;
    font-size: var(--text-display-lg);
  }

  .next {
    margin: 0;
    text-align: center;
  }

  .label {
    display: block;
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
  }

  .read {
    font-size: var(--text-read-lg);
  }

  .actions {
    display: flex;
    gap: var(--space-3);
  }

  .list {
    align-self: stretch;
    max-height: 14rem;
    margin: 0;
    padding: 0;
    overflow-y: auto;
    list-style: none;
    scrollbar-width: thin;
    scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
  }

  .row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    width: 100%;
    padding: var(--space-2) var(--space-3);
    background: none;
    border: 0;
    color: var(--ink);
    text-align: left;
    cursor: pointer;
  }

  .row:hover {
    background: var(--surface-stripe);
  }

  .mark {
    display: flex;
  }

  .link {
    padding: 0;
    background: none;
    border: 0;
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
    text-decoration: underline;
    cursor: pointer;
  }
</style>
