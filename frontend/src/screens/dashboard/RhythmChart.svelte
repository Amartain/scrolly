<!-- Rhythm: the last seven days. Bars use a compressed scale from Python; a quiet day is a sprig. -->
<script lang="ts">
  import SprigIcon from '../../icons/SprigIcon.svelte';
  import type { ChartSeries } from '../../lib/api';
  import { INVITE } from '../../lib/copy';
  import FoggedChart from './FoggedChart.svelte';

  let { series }: { series: ChartSeries } = $props();
</script>

<FoggedChart foggy={series.placeholder} invite={INVITE.rhythm}>
  <ul class="rhythm" aria-label="The last seven days">
    {#each series.rhythm as bar, i (bar.day)}
      <li class="day" class:today={i === series.rhythm.length - 1}>
        <div class="plot">
          {#if bar.is_rest}
            <span class="rest"><SprigIcon /><span class="note">rest</span></span>
          {:else}
            <span class="value digits" style:bottom="calc({bar.height_pct}% + var(--space-1))"
              >{bar.value_text}</span
            >
            <span class="bar" style:height="{bar.height_pct}%"></span>
          {/if}
        </div>
        <span class="label">{bar.label}</span>
      </li>
    {/each}
  </ul>
</FoggedChart>

<style>
  .rhythm {
    flex: 1;
    min-height: 0;
    display: flex;
    gap: var(--space-3);
    margin: 0;
    padding: var(--space-2) var(--space-4) var(--space-2);
    list-style: none;
  }

  .day {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-1);
  }

  /* Room above the tallest bar for its figure. */
  .plot {
    position: relative;
    flex: 1;
    width: 100%;
    min-height: 0;
    --value-room: calc(var(--text-body-md) + var(--space-1));
    margin-top: var(--value-room);
  }

  .bar {
    position: absolute;
    inset-inline: 0;
    bottom: 0;
    box-sizing: border-box;
    background: color-mix(in srgb, var(--gold) 55%, var(--surface-panel));
    background-image: var(--gloss-side);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
  }

  .today .bar {
    background-color: var(--gold);
  }

  .value {
    position: absolute;
    inset-inline: 0;
    text-align: center;
    color: var(--ink-muted);
    font-size: var(--text-body-md);
  }

  .rest {
    position: absolute;
    inset-inline: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .note,
  .label {
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }
</style>
