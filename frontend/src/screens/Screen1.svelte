<script lang="ts">
  import Panel from '../components/Panel.svelte';
  import MetricToggle from '../components/MetricToggle.svelte';
  import { chartChoice } from '../lib/charts.svelte';
  import { EMPTY } from '../lib/copy';
  import { conquer, toggleTimer } from '../lib/immediate';
  import { onControl, typing } from '../lib/keys';
  import { onScreenTwo, showScreen } from '../lib/screens';
  import { view } from '../lib/view.svelte';
  import ConqueredList from './dashboard/ConqueredList.svelte';
  import EssencePanel from './dashboard/EssencePanel.svelte';
  import ImmediateCard from './dashboard/ImmediateCard.svelte';
  import MomentumChart from './dashboard/MomentumChart.svelte';
  import RhythmChart from './dashboard/RhythmChart.svelte';
  import StatCard from './dashboard/StatCard.svelte';
  import VictoryBanner from './dashboard/VictoryBanner.svelte';

  let { onseclusion }: { onseclusion?: () => void } = $props();

  const dashboard = $derived(view.current?.dashboard);
  const charts = $derived(dashboard?.charts ?? []);
  const series = $derived(chartChoice.pick(charts));
  // The toggle waits until something has been conquered: before that the charts are only a hint.
  const live = $derived(charts.some((c) => !c.placeholder));

  // Space starts or pauses the timer, Enter conquers. A focused button already does both itself.
  function onkeydown(event: KeyboardEvent) {
    const trial = dashboard?.immediate;
    const modified = event.altKey || event.ctrlKey || event.metaKey || event.shiftKey;
    if (!trial || modified || typing(event.target) || onControl(event.target) || onScreenTwo())
      return;
    if (event.key === ' ') toggleTimer(trial);
    else if (event.key === 'Enter') conquer(trial);
    else return;
    event.preventDefault();
  }
</script>

<svelte:window {onkeydown} />

<div class="grid">
  <div class="column left">
    <EssencePanel />
    <div class="immediate">
      {#if dashboard?.victory}
        <VictoryBanner victory={dashboard.victory} />
      {:else if dashboard?.immediate}
        <ImmediateCard trial={dashboard.immediate} {onseclusion} />
      {:else}
        <Panel title="The Immediate Trial" guide="immediate" empty={EMPTY.immediate} />
      {/if}
    </div>
    <ConqueredList />
  </div>
  <div class="column right">
    <div class="stats">
      <StatCard title="Lifetime Conquered" value={dashboard?.lifetime_conquered ?? 0} />
      <StatCard title="Heavenly Cycles" value={dashboard?.heavenly_cycles ?? 0} />
    </div>
    {#if series}
      <Panel title="Momentum" guide="momentum">
        {#snippet actions()}
          {#if live}
            <MetricToggle
              metrics={charts.map((c) => c.metric)}
              value={series.metric}
              tone="growth"
              onpick={(metric) => (chartChoice.metric = metric)}
            />
          {/if}
        {/snippet}
        <MomentumChart {series} />
      </Panel>
      <Panel title="Rhythm" guide="rhythm">
        {#snippet actions()}
          {#if live}
            <MetricToggle
              metrics={charts.map((c) => c.metric)}
              value={series.metric}
              tone="gold"
              onpick={(metric) => (chartChoice.metric = metric)}
            />
          {/if}
        {/snippet}
        <RhythmChart {series} />
      </Panel>
    {:else}
      <Panel title="Momentum" />
      <Panel title="Rhythm" />
    {/if}
  </div>
</div>
<button class="fold display" type="button" onclick={() => showScreen('two')}>
  The planning peak <kbd>↓</kbd>
</button>

<style>
  .grid {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
    gap: var(--space-5);
    padding: var(--space-4) var(--size-gutter) 0;
  }

  .column {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: var(--space-4);
    min-height: 0;
  }

  .left {
    grid-template-rows: var(--size-short-panel) var(--size-immediate) minmax(0, 1fr);
  }

  .right {
    grid-template-rows: var(--size-stat) minmax(0, 1fr) minmax(0, 1fr);
  }

  .immediate {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    min-height: 0;
  }

  .stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-5);
  }

  .fold {
    flex: none;
    height: var(--size-fold);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-3);
    margin: var(--space-4) 0 0;
    padding: 0;
    border: 0;
    border-top: var(--border-width) solid var(--line);
    background: var(--head-bg);
    color: var(--head-ink);
    font-size: var(--text-display-sm);
    cursor: pointer;
  }

  /* The band is a button: it wears the panel headers' colours, so it reads as one (a hover dims it). */
  .fold:hover {
    opacity: 0.9;
  }

  kbd {
    padding-inline: var(--space-2);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    color: var(--ink);
    font: inherit;
  }
</style>
