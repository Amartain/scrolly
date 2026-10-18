<script lang="ts">
  import Panel from '../components/Panel.svelte';
  import RowList from '../components/RowList.svelte';
  import TrialLine from '../components/TrialLine.svelte';
  import type { PlanTrial } from '../lib/api';
  import { SCREEN_TWO_ID } from '../lib/screens';
  import { view } from '../lib/view.svelte';

  const remaining = $derived(
    (view.planning?.trials ?? []).filter((trial) => trial.state === 'remaining'),
  );
</script>

{#snippet row(trial: PlanTrial)}
  <TrialLine {trial} />
{/snippet}

<div class="screen" id={SCREEN_TWO_ID}>
  <div class="column left">
    <Panel title="Scribe Trial" empty="Write a trial here." />
    <Panel title="Remaining Trials" scroll>
      <RowList items={remaining} {row} empty="No trials waiting." />
    </Panel>
    <div class="pair">
      <Panel title="Postponed Today" empty="None." />
      <Panel title="Fallen Leaves" empty="None." />
    </div>
    <div class="pair">
      <Panel title="Foundational Arts" tone="foundational" empty="No Arts yet." scroll />
      <Panel title="Restorative Arts" tone="restorative" empty="No Arts yet." scroll />
    </div>
  </div>
  <div class="column right">
    <Panel title="The Horizon" tone="horizon" empty="The Horizon is clear." scroll />
  </div>
</div>

<style>
  .screen {
    height: 100dvh;
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
    gap: var(--space-5);
    padding: var(--space-4) var(--size-gutter);
  }

  .column {
    display: grid;
    gap: var(--space-4);
    min-height: 0;
    padding-right: var(--shadow-room);
    padding-bottom: var(--shadow-room);
  }

  .left {
    grid-template-rows: var(--size-short-panel) minmax(0, 3fr) var(--size-short-panel) minmax(
        0,
        2fr
      );
  }

  .right {
    grid-template-rows: minmax(0, 1fr);
  }

  .pair {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-5);
    min-height: 0;
  }
</style>
