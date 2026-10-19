<script lang="ts">
  import Panel from '../components/Panel.svelte';
  import { EMPTY } from '../lib/copy';
  import { conquer, toggleTimer } from '../lib/immediate';
  import { onControl, typing } from '../lib/keys';
  import { onScreenTwo, showScreen } from '../lib/screens';
  import { view } from '../lib/view.svelte';
  import ConqueredList from './dashboard/ConqueredList.svelte';
  import EssencePanel from './dashboard/EssencePanel.svelte';
  import ImmediateCard from './dashboard/ImmediateCard.svelte';
  import StatCard from './dashboard/StatCard.svelte';
  import VictoryBanner from './dashboard/VictoryBanner.svelte';

  const dashboard = $derived(view.current?.dashboard);

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
        <VictoryBanner />
      {:else if dashboard?.immediate}
        <ImmediateCard trial={dashboard.immediate} />
      {:else}
        <Panel title="The Immediate Trial" empty={EMPTY.immediate} />
      {/if}
    </div>
    <ConqueredList />
  </div>
  <div class="column right">
    <div class="stats">
      <StatCard title="Lifetime Conquered" value={dashboard?.lifetime_conquered ?? 0} />
      <StatCard title="Heavenly Cycles" value={dashboard?.heavenly_cycles ?? 0} />
    </div>
    <Panel title="Cumulative Momentum" empty={EMPTY.momentum} />
    <Panel title="Rhythm" empty={EMPTY.rhythm} />
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
    background: var(--surface-stripe);
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
    cursor: pointer;
  }

  .fold:hover {
    color: var(--ink);
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
