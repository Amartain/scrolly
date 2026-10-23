<script lang="ts">
  import { onMount } from 'svelte';
  import Button from '../components/Button.svelte';
  import Panel from '../components/Panel.svelte';
  import QiGauge from '../components/QiGauge.svelte';
  import RowList from '../components/RowList.svelte';
  import ScrollSheet from '../components/ScrollSheet.svelte';
  import { planning, type PlanTrial } from '../lib/api';
  import { view } from '../lib/view.svelte';
  import CoreSlider from './plan/CoreSlider.svelte';
  import Notice from './plan/Notice.svelte';
  import QiRow from './plan/QiRow.svelte';

  const trials = $derived(view.planning?.trials ?? []);
  const qi = $derived(view.planning?.qi);

  onMount(() => {
    view.notice = '';
  });
</script>

{#snippet row(trial: PlanTrial)}
  <QiRow {trial} />
{/snippet}

<ScrollSheet title="Weigh the Qi" guide="weigh">
  <div class="phase">
    <div class="column">
      <Panel title="The Scroll" scroll striped>
        <RowList items={trials} {row} />
      </Panel>
      <Notice />
      <div class="actions">
        <Button label="◀ Back to Estimating" onclick={() => view.act(planning.back)} />
        <Button
          label="Seal Scroll and Commence"
          tone="primary"
          onclick={() => view.act(planning.seal)}
        />
      </div>
    </div>
    <div class="aside">
      {#if qi}
        <Panel title="The Golden Core">
          <div class="core">
            <QiGauge
              {qi}
              value={qi.planned}
              fill={qi.planned_fill}
              zone={qi.planned_zone}
              caption="planned today"
            />
            <CoreSlider {qi} />
            <p class="tomorrow">
              If today goes as planned, tomorrow's core begins at
              <span class="digits">{qi.tomorrow_start}</span> Qi. Restorative Arts give Qi back.
            </p>
          </div>
        </Panel>
      {/if}
    </div>
  </div>
</ScrollSheet>

<style>
  .phase {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
    gap: var(--space-5);
  }

  .column {
    display: grid;
    grid-template-rows: minmax(0, 1fr) auto auto;
    gap: var(--space-3);
    min-height: 0;
    padding-right: var(--shadow-room);
    padding-bottom: var(--shadow-room);
  }

  .aside {
    display: grid;
    align-content: start;
    gap: var(--space-4);
    min-height: 0;
    padding-right: var(--shadow-room);
    padding-bottom: var(--shadow-room);
  }

  .core {
    padding: var(--space-3) var(--space-4);
  }

  .tomorrow {
    margin: var(--space-3) 0 0;
    color: var(--ink-muted);
    font-size: var(--text-body-md);
  }

  .actions {
    display: flex;
    justify-content: space-between;
  }
</style>
