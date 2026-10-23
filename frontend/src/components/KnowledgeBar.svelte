<!-- Knowledge of the Dao: how much of Scrolly has been learned (domain/knowledge.py). In the planning
     corner, or in the header's title plate under the tagline. The user may hide it: then it shows only
     for a moment, while it moves. All learned and the ceremony seen: nothing, the path is walked
     (owner, 2026-10-23; the gold 悟 block that once stood here "doesn't fit"). -->
<script lang="ts">
  import { KNOWLEDGE } from '../lib/copy-knowledge';
  import { knowledge } from '../lib/knowledge.svelte';
  import { view } from '../lib/view.svelte';

  let { place }: { place: 'corner' | 'plate' } = $props();

  const known = $derived(view.current?.knowledge);
  const shown = $derived(
    !!known && !known.enlightened && (!known.bar_hidden || knowledge.flashing),
  );
  const fill = $derived(known ? (known.count / known.total) * 100 : 0);
</script>

{#if known && shown}
  <div
    class="knowledge"
    class:flash={knowledge.flashing}
    data-place={place}
    role="group"
    aria-label={KNOWLEDGE.title}
  >
    <div class="label">
      <span class="name display">{KNOWLEDGE.title}</span>
      <span class="count digits">{KNOWLEDGE.count(known.count, known.total)}</span>
    </div>
    <div
      class="track"
      role="progressbar"
      aria-label={KNOWLEDGE.title}
      aria-valuemin={0}
      aria-valuemax={known.total}
      aria-valuenow={known.count}
    >
      <div class="fill" style:width="{fill}%"></div>
    </div>
  </div>
{/if}

<style>
  .knowledge {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    min-width: 0;
  }

  .knowledge[data-place='corner'] {
    width: var(--size-knowledge);
    padding: var(--space-2) var(--space-3);
    background: var(--surface-panel);
    background-image: var(--gloss-faint);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .label {
    display: flex;
    justify-content: space-between;
    gap: var(--space-3);
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }

  .name,
  .count {
    white-space: nowrap;
  }

  .name {
    font-size: var(--text-display-sm);
  }

  .track {
    height: var(--space-2);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
  }

  .fill {
    height: 100%;
    background: var(--gold);
    transition: width var(--motion-fast) ease-out;
  }

  .flash .fill {
    box-shadow: var(--shadow-glow-gold);
  }

  @media (prefers-reduced-motion: reduce) {
    .fill {
      transition: none;
    }
  }
</style>
