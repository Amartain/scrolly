<!-- Switches the chart between Trials, Essence and (with the Golden Core) Qi. -->
<script lang="ts">
  import type { Metric } from '../lib/api';
  import { METRIC_LABEL } from '../lib/copy';

  let {
    metrics,
    value,
    tone,
    onpick,
  }: {
    metrics: Metric[];
    value: Metric;
    tone: 'growth' | 'gold';
    onpick: (metric: Metric) => void;
  } = $props();
</script>

<span class="toggle display" role="group" aria-label="Show">
  {#each metrics as metric (metric)}
    <button
      type="button"
      class:on={metric === value}
      data-tone={tone}
      aria-pressed={metric === value}
      onclick={() => onpick(metric)}>{METRIC_LABEL[metric]}</button
    >
  {/each}
</span>

<style>
  .toggle {
    display: inline-flex;
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-sm);
  }

  button {
    padding: var(--space-1) var(--space-3);
    cursor: pointer;
    background: var(--btn);
    background-image: var(--gloss-btn);
    color: var(--ink);
    border: 0;
    font: inherit;
    text-transform: uppercase;
  }

  button.on[data-tone='growth'] {
    background: var(--growth);
    background-image: none;
    color: var(--on-growth);
  }

  button.on[data-tone='gold'] {
    background: var(--gold);
    background-image: none;
    color: var(--on-gold);
  }
</style>
