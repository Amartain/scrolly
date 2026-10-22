<!-- Momentum: all-time progress as one rising line. The series comes from Python. There are no numbers on
     it: hover or focus shows one day's figure. -->
<script lang="ts">
  import type { ChartSeries } from '../../lib/api';
  import { useReader } from '../../lib/chart-reader.svelte';
  import { CHART } from '../../lib/copy-charts';
  import { monotonePath } from '../../lib/curve';
  import { INVITE } from '../../lib/copy';
  import ChartTip from './ChartTip.svelte';
  import FoggedChart from './FoggedChart.svelte';

  let { series }: { series: ChartSeries } = $props();

  const WIDTH = 440;
  const HEIGHT = 130;
  const PAD_X = 8;
  const PAD_TOP = 14;
  const PAD_BOTTOM = 8;
  const EDGE = 20; // a tip this close (in %) to a side grows away from it
  const ROOM_ABOVE = 35; // a dot higher than this (% from the top) has no room for a tip above it

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

  // Where each real point sits, as a share of the plot (the line's own coordinates, so a dot lands on it).
  const spots = $derived(
    points.map((_, i) => ({ x: (xy[i + 1][0] / WIDTH) * 100, y: (xy[i + 1][1] / HEIGHT) * 100 })),
  );
  const live = $derived(!series.placeholder && points.length > 0);
  const reader = useReader(
    () => points.length,
    () => live,
  );
  const point = $derived(reader.shown === null ? undefined : points[reader.shown]);
  const spot = $derived(reader.shown === null ? undefined : spots[reader.shown]);
  const align = $derived(
    spot === undefined
      ? 'center'
      : spot.x < EDGE
        ? 'start'
        : spot.x > 100 - EDGE
          ? 'end'
          : 'center',
  );
  // Near the top of the plot there is no room above the dot, so the tip goes below it.
  const above = $derived(spot === undefined || spot.y > ROOM_ABOVE);

  function near(event: PointerEvent) {
    if (!live) return;
    const box = (event.currentTarget as HTMLElement).getBoundingClientRect();
    const at = ((event.clientX - box.left) / box.width) * 100;
    reader.shown = spots.reduce(
      (best, s, i) => (Math.abs(s.x - at) < Math.abs(spots[best].x - at) ? i : best),
      0,
    );
  }
</script>

<FoggedChart foggy={series.placeholder} invite={INVITE.momentum}>
  <!-- Each series has its own colour: Trials gold, Essence and Qi per theme (--chart-*). -->
  <div class="momentum" style:--series="var(--chart-{series.metric})">
    <!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions -->
    <div
      class="plot"
      role="group"
      aria-label={CHART.hint('Momentum')}
      tabindex={live ? 0 : undefined}
      onpointermove={near}
      onpointerleave={reader.clear}
      onkeydown={reader.onkeydown}
      onfocus={reader.onfocus}
      onblur={reader.clear}
    >
      <svg
        viewBox="0 0 {WIDTH} {HEIGHT}"
        preserveAspectRatio="none"
        role="img"
        aria-label={summary}
      >
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
      {#if point && spot}
        <span class="dot" style:left="{spot.x}%" style:top="{spot.y}%"></span>
        <ChartTip
          text="{point.label} · {point.value_text}"
          x="{spot.x}%"
          y="calc({above ? 100 - spot.y : spot.y}% + var(--space-3))"
          {align}
          {above}
        />
      {/if}
    </div>
    <div class="dates">
      {#each dates as d (d.day)}<span>{d.label}</span>{/each}
    </div>
  </div>
</FoggedChart>

<style>
  .momentum {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    padding: var(--space-2) var(--space-4);
  }

  .plot {
    position: relative;
    flex: 1;
    min-height: 0;
  }

  svg {
    display: block;
    width: 100%;
    height: 100%;
  }

  .grid {
    fill: none;
    stroke: var(--grid);
    stroke-width: var(--border-width);
    vector-effect: non-scaling-stroke;
  }

  .line {
    fill: none;
    stroke: var(--series);
    stroke-width: calc(var(--border-width) * 2);
    vector-effect: non-scaling-stroke;
  }

  .fill-top {
    stop-color: var(--series);
    stop-opacity: 0.55;
  }

  .fill-bottom {
    stop-color: var(--series);
    stop-opacity: 0.08;
  }

  .dot {
    position: absolute;
    width: var(--space-3);
    height: var(--space-3);
    background: var(--gold);
    border: var(--border-width) solid var(--line);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
  }

  .dates {
    display: flex;
    justify-content: space-between;
    padding-top: var(--space-1);
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }
</style>
