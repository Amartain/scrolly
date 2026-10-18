<script lang="ts">
  import { onMount } from 'svelte';
  import Button from '../components/Button.svelte';
  import Panel from '../components/Panel.svelte';
  import ReorderList from '../components/ReorderList.svelte';
  import { planning, type PlanTrial } from '../lib/api';
  import { view } from '../lib/view.svelte';
  import EstimateRow from './plan/EstimateRow.svelte';
  import Notice from './plan/Notice.svelte';

  const trials = $derived(view.planning?.trials ?? []);

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

<div class="phase">
  <div class="column">
    <h1 class="display heading">Estimate the Journey</h1>
    <form class="add" onsubmit={add}>
      <input
        bind:value={title}
        placeholder="A forgotten trial emerges…"
        aria-label="A forgotten trial"
      />
      <Button label="Add" onclick={() => add()} />
    </form>
    <Panel title="The Scroll" scroll>
      <ReorderList items={shown} label="Trials on the scroll" onreorder={reorder} {row} />
    </Panel>
    <Notice />
    <div class="actions">
      <Button label="◀ Back to Inscribing" onclick={() => view.act(planning.back)} />
      <Button
        label="Seal Scroll and Commence"
        tone="primary"
        onclick={() => view.act(planning.seal)}
      />
    </div>
  </div>
  <Panel title="Guidance">
    <div class="copy">
      <p>
        Time blindness is conquered through practice. Divine the essence required (for example 60m
        or 1.5h). If you forget an estimate, you can set it later.
      </p>
      <p>
        Drag a row, or press Alt with the arrow keys, to set the order. The top trial begins first.
      </p>
      <p><strong>Mortal Trials:</strong> let them go freely, they fade at 4 AM.</p>
      <p><strong>Heavenly Mandates:</strong> postpone to send a copy back to the Horizon.</p>
    </div>
  </Panel>
</div>

<style>
  .phase {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
    gap: var(--space-5);
    padding: var(--space-4) var(--size-gutter);
  }

  .column {
    display: grid;
    grid-template-rows: auto auto minmax(0, 1fr) auto auto;
    gap: var(--space-3);
    min-height: 0;
    padding-right: var(--shadow-room);
    padding-bottom: var(--shadow-room);
  }

  .heading {
    margin: 0;
    font-size: var(--text-display-lg);
  }

  .add {
    display: flex;
    gap: var(--space-3);
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

  .copy {
    padding: var(--space-3) var(--space-4);
    font-size: var(--text-body-md);
  }

  .copy p {
    margin-top: 0;
    margin-bottom: var(--space-3);
  }
</style>
