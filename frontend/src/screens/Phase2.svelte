<script lang="ts">
  import { onMount } from 'svelte';
  import Button from '../components/Button.svelte';
  import Panel from '../components/Panel.svelte';
  import ReorderList from '../components/ReorderList.svelte';
  import ScrollSheet from '../components/ScrollSheet.svelte';
  import { planning, type PlanTrial } from '../lib/api';
  import { view } from '../lib/view.svelte';
  import DaySummary from './plan/DaySummary.svelte';
  import EstimateRow from './plan/EstimateRow.svelte';
  import GoldenCoreInvite from './plan/GoldenCoreInvite.svelte';
  import Notice from './plan/Notice.svelte';

  const trials = $derived(view.planning?.trials ?? []);
  const qi = $derived(view.planning?.qi);

  // The new order shows at once, then the server's answer replaces it.
  let pending = $state<string[] | null>(null);
  const shown = $derived(
    pending ? pending.flatMap((id) => trials.filter((trial) => trial.id === id)) : trials,
  );
  let title = $state('');

  onMount(() => {
    view.notice = '';
  });

  async function reorder(ids: string[]) {
    pending = ids;
    await view.act(() => planning.reorder(ids));
    pending = null;
  }

  async function add(event?: Event) {
    event?.preventDefault();
    if (title.trim() && (await view.act(() => planning.add(title)))) title = '';
  }
</script>

{#snippet row(trial: PlanTrial)}
  <EstimateRow {trial} />
{/snippet}

<ScrollSheet title="Estimate the Journey" guide="estimate">
  <div class="phase">
    <div class="column">
      <form class="add" onsubmit={add}>
        <input
          bind:value={title}
          placeholder="A forgotten trial emerges…"
          aria-label="A forgotten trial"
        />
        <Button label="Add" onclick={() => add()} />
      </form>
      <div class="list">
        <Panel title="The Scroll" scroll striped>
          <ReorderList items={shown} label="Trials on the scroll" onreorder={reorder} {row} />
        </Panel>
      </div>
      {#if qi && !qi.invited}
        <GoldenCoreInvite />
      {/if}
      <Notice />
      <div class="actions">
        <Button label="◀ Back to Inscribing" onclick={() => view.act(planning.back)} />
        {#if qi?.enabled}
          <Button
            label="Proceed: Weigh the Qi"
            tone="primary"
            onclick={() => view.act(planning.proceed)}
          />
        {:else}
          <Button
            label="Seal Scroll and Commence"
            tone="primary"
            tour="seal"
            onclick={() => view.act(planning.seal)}
          />
        {/if}
      </div>
    </div>
    <div class="aside">
      <DaySummary />
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
    display: flex;
    flex-direction: column;
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

  .add {
    display: flex;
    gap: var(--space-3);
  }

  .list {
    flex: 1;
    display: grid;
    min-height: 0;
  }

  .add input {
    flex: 1;
    min-width: 0;
    height: var(--size-field);
    padding-inline: var(--space-3);
    background: var(--surface-raised);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    font-size: var(--text-body-md);
  }

  .actions {
    display: flex;
    justify-content: space-between;
  }
</style>
