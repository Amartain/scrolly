<!-- Rhythm: the last seven days. Bars use a compressed scale from Python; a quiet day is a sprig. There are
     no numbers on it: hover or focus shows one day's figure. -->
<script lang="ts">
  import SprigIcon from '../../icons/SprigIcon.svelte';
  import type { ChartSeries } from '../../lib/api';
  import { useReader } from '../../lib/chart-reader.svelte';
  import { INVITE } from '../../lib/copy';
  import { CHART } from '../../lib/copy-charts';
  import ChartTip from './ChartTip.svelte';
  import FoggedChart from './FoggedChart.svelte';

  let { series }: { series: ChartSeries } = $props();

  const live = $derived(!series.placeholder && series.rhythm.length > 0);
  const reader = useReader(
    () => series.rhythm.length,
    () => live,
  );

  // The first and last days grow their tip inward, so it stays inside the panel.
  const sideOf = (i: number) =>
    i === 0 ? 'start' : i === series.rhythm.length - 1 ? 'end' : 'center';
  const leftOf = (side: string) => (side === 'start' ? '0%' : side === 'end' ? '100%' : '50%');
</script>

<FoggedChart foggy={series.placeholder} invite={INVITE.rhythm}>
  <!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions -->
  <ul
    class="rhythm"
    style:--series="var(--chart-{series.metric})"
    aria-label={CHART.hint('Rhythm, the last seven days')}
    tabindex={live ? 0 : undefined}
    onkeydown={reader.onkeydown}
    onfocus={reader.onfocus}
    onblur={reader.clear}
  >
    {#each series.rhythm as bar, i (bar.day)}
      {@const side = sideOf(i)}
      <li
        class="day"
        class:today={i === series.rhythm.length - 1}
        onpointerenter={() => live && (reader.shown = i)}
        onpointerleave={reader.clear}
      >
        <div class="plot">
          {#if bar.is_rest}
            <span class="rest"><SprigIcon /><span class="note">{CHART.rest}</span></span>
          {:else}
            <span class="bar" style:height="{bar.height_pct}%"></span>
          {/if}
          {#if reader.shown === i}
            <ChartTip
              text="{bar.label} · {bar.is_rest ? CHART.rest : bar.value_text}"
              x={leftOf(side)}
              y={bar.is_rest
                ? 'calc(var(--size-icon) + var(--text-body-sm) + var(--space-2))'
                : `calc(${bar.height_pct}% + var(--space-2))`}
              align={side}
            />
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

  /* Room above the tallest bar for the tip. */
  .plot {
    position: relative;
    flex: 1;
    width: 100%;
    min-height: 0;
    margin-top: var(--space-10);
  }

  .bar {
    position: absolute;
    inset-inline: 0;
    bottom: 0;
    box-sizing: border-box;
    background: color-mix(in srgb, var(--series) 55%, var(--surface-panel));
    background-image: var(--gloss-side);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
  }

  .today .bar {
    background-color: var(--series);
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
