<script lang="ts">
  import Button from '../../components/Button.svelte';
  import Panel from '../../components/Panel.svelte';
  import ReorderList from '../../components/ReorderList.svelte';
  import { horizon, today, type HorizonItem } from '../../lib/api';
  import { EMPTY } from '../../lib/copy';
  import { useOrder } from '../../lib/order.svelte';
  import { view } from '../../lib/view.svelte';
  import HorizonRow from '../plan/HorizonRow.svelte';

  const order = useOrder(
    () => view.planning?.horizon ?? [],
    (ids) => horizon.reorder(ids),
  );
  let title = $state('');

  async function add(event?: Event) {
    event?.preventDefault();
    if (title.trim() && (await view.act(() => horizon.add(title)))) title = '';
  }
</script>

{#snippet row(item: HorizonItem)}
  <HorizonRow {item} editable onsummon={() => view.act(() => today.summon('horizon', item.id))} />
{/snippet}

<Panel title="The Horizon" tone="horizon" count={order.shown.length} scroll striped>
  <form class="add" onsubmit={add}>
    <input bind:value={title} placeholder="Scribe a future trial…" aria-label="A future trial" />
    <Button label="Add" tone="horizon" onclick={() => add()} />
  </form>
  {#if order.shown.length === 0}
    <p class="empty">{EMPTY.horizon}</p>
  {:else}
    <ReorderList items={order.shown} label="The Horizon" onreorder={order.reorder} {row} />
  {/if}
</Panel>

<style>
  /* Two row heights, so the bands below keep their rhythm. */
  .add {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    height: calc(var(--size-row) * 2);
    padding-inline: var(--space-4);
    background: var(--card-ink-head);
  }

  input {
    flex: 1;
    min-width: 0;
    height: var(--size-field);
    padding-inline: var(--space-3);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    font-family: var(--font-body);
    font-size: var(--text-body-md);
  }

  .empty {
    margin: 0;
    padding: var(--space-2) var(--space-4);
    background: var(--card-ink-row-a);
  }
</style>
