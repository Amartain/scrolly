<!-- Cumulative Momentum: all-time progress as one rising line. The series comes from Python. -->
<script lang="ts">
  import type { ChartSeries } from '../../lib/api';
  import { monotonePath } from '../../lib/curve';
  import { INVITE } from '../../lib/copy';
  import FoggedChart from './FoggedChart.svelte';

  let { series }: { series: ChartSeries } = $props();

  const WIDTH = 440;
  const HEIGHT = 130;
  const PAD_X = 8;
  const PAD_TOP = 14;
  const PAD_BOTTOM = 8;

  const points = $derived(series.momentum);
  const top = $derived(Math.max(...points.map((p) => p.value), 1));
  // A starting point at zero, so even one conquest draws a line. It has no date label.
  const xy = $derived<[number, number][]>(
    [0, ...points.map((p) => p.value)].map((value, i, all) => [
      PAD_X + (i * (WIDTH - 2 * PAD_X)) / Math.max(all.length - 1, 1),
      HEIGHT - PAD_BOTTOM - (value / top) * (HEIGHT - PAD_TOP - PAD_BOTTOM),
    ]),
  );
  const line = $derived(monotonePath(xy));
  const area = $derived(`${line} L${xy[xy.length - 1][0]},${HEIGHT} L${xy[0][0]},${HEIGHT} Z`);
  // First, middle and last dates, so the axis never crowds.
  const dates = $derived(
    [...new Set([0, Math.floor((points.length - 1) / 2), points.length - 1])]
      .filter((i) => i >= 0)
      .map((i) => points[i]),
  );
  const latest = $derived(points[points.length - 1]);
  const summary = $derived(
    `Cumulative ${series.metric} conquered, rising to ${latest?.value_text ?? 0} over ${points.length} active days`,
  );
</script>

<FoggedChart foggy={series.placeholder} invite={INVITE.momentum}>
  <div class="momentum">
    <p class="latest digits display">{latest?.value_text ?? ''}</p>
    <svg viewBox="0 0 {WIDTH} {HEIGHT}" preserveAspectRatio="none" role="img" aria-label={summary}>
      <defs>
        <linearGradient id="momentum-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" class="fill-top" />
          <stop offset="1" class="fill-bottom" />
        </linearGradient>
      </defs>
      <path class="grid" d="M0,32 H{WIDTH} M0,64 H{WIDTH} M0,96 H{WIDTH}" />
      <path d={area} fill="url(#momentum-fill)" />
      <path class="line" d={line} />
    </svg>
    <div class="dates">
      {#each dates as point (point.day)}<span>{point.label}</span>{/each}
    </div>
  </div>
</FoggedChart>

<style>
  .momentum {
    position: relative;
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    padding: var(--space-2) var(--space-4);
  }

  svg {
    flex: 1;
    min-height: 0;
    width: 100%;
  }

  .grid {
    fill: none;
    stroke: var(--grid);
    stroke-width: var(--border-width);
    vector-effect: non-scaling-stroke;
  }

  .line {
    fill: none;
    stroke: var(--growth-text);
    stroke-width: calc(var(--border-width) * 2);
    vector-effect: non-scaling-stroke;
  }

  .fill-top {
    stop-color: var(--growth-text);
    stop-opacity: 0.55;
  }

  .fill-bottom {
    stop-color: var(--growth-text);
    stop-opacity: 0.08;
  }

  .latest {
    position: absolute;
    top: var(--space-1);
    right: var(--space-4);
    margin: 0;
    color: var(--num-text);
    font-size: var(--text-display-md);
  }

  .dates {
    display: flex;
    justify-content: space-between;
    padding-top: var(--space-1);
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }
</style>
