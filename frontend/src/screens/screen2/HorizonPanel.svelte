<script lang="ts">
  import Button from '../../components/Button.svelte';
  import ExpandButton from '../../components/ExpandButton.svelte';
  import Panel from '../../components/Panel.svelte';
  import ReorderList from '../../components/ReorderList.svelte';
  import { horizon, today, type HorizonItem } from '../../lib/api';
  import { EMPTY } from '../../lib/copy';
  import { useOrder } from '../../lib/order.svelte';
  import { view } from '../../lib/view.svelte';
  import HorizonRow from '../plan/HorizonRow.svelte';
  import HorizonExpand from './HorizonExpand.svelte';

  const order = useOrder(
    () => view.planning?.horizon ?? [],
    (ids) => horizon.reorder(ids),
  );
  let title = $state('');
  let estimate = $state('');
  let expanded = $state(false);

  async function add(event?: Event) {
    event?.preventDefault();
    if (!title.trim()) return;
    if (await view.act(() => horizon.add(title, estimate))) {
      title = '';
      estimate = '';
    }
  }
</script>

{#snippet row(item: HorizonItem)}
  <HorizonRow {item} onsummon={() => view.act(() => today.summon('horizon', item.id))} />
{/snippet}

<Panel title="The Horizon" tone="horizon" guide="horizon" count={order.shown.length} scroll striped>
  {#snippet actions()}
    <ExpandButton label="Expand The Horizon" onclick={() => (expanded = true)} />
  {/snippet}
  <form class="add" onsubmit={add}>
    <input bind:value={title} placeholder="Scribe a future trial…" aria-label="A future trial" />
    <input
      class="estimate digits"
      bind:value={estimate}
      placeholder="30m"
      aria-label="Estimate of the future trial"
    />
    <Button label="Add" tone="horizon" onclick={() => add()} />
    <!-- Two fields: a hidden submit lets Enter add from either. -->
    <button type="submit" hidden tabindex="-1" aria-hidden="true"></button>
  </form>
  {#if order.shown.length === 0}
    <p class="empty">{EMPTY.horizon}</p>
  {:else}
    <ReorderList items={order.shown} label="The Horizon" onreorder={order.reorder} {row} />
  {/if}
</Panel>

{#if expanded}
  <HorizonExpand onclose={() => (expanded = false)} />
{/if}

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

  input.estimate {
    flex: none;
    width: var(--size-estimate);
    text-align: right;
  }

  .empty {
    margin: 0;
    padding: var(--space-2) var(--space-4);
    background: var(--card-ink-row-a);
  }
</style>
