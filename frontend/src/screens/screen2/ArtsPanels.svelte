<script lang="ts">
  import Panel from '../../components/Panel.svelte';
  import ReorderList from '../../components/ReorderList.svelte';
  import { horizon, today, type Art } from '../../lib/api';
  import { EMPTY } from '../../lib/copy';
  import { useOrder } from '../../lib/order.svelte';
  import { view } from '../../lib/view.svelte';
  import ArtRow from '../plan/ArtRow.svelte';

  const foundational = useOrder(
    () => view.planning?.foundational ?? [],
    (ids) => horizon.reorderArts('foundational', ids),
  );
  const restorative = useOrder(
    () => view.planning?.restorative ?? [],
    (ids) => horizon.reorderArts('restorative', ids),
  );

  const summon = (id: string) => view.act(() => today.summon('art', id));
</script>

{#snippet foundationalRow(art: Art)}
  <ArtRow {art} kind="foundational" onsummon={() => summon(art.id)} />
{/snippet}

{#snippet restorativeRow(art: Art)}
  <ArtRow {art} kind="restorative" onsummon={() => summon(art.id)} />
{/snippet}

<div class="pair">
  <Panel title="Foundational Arts" tone="foundational" scroll striped>
    {#if foundational.shown.length === 0}
      <p class="empty">{EMPTY.foundational}</p>
    {:else}
      <ReorderList
        items={foundational.shown}
        label="Foundational Arts"
        onreorder={foundational.reorder}
        row={foundationalRow}
      />
    {/if}
  </Panel>
  <Panel title="Restorative Arts" tone="restorative" scroll striped>
    {#if restorative.shown.length === 0}
      <p class="empty">{EMPTY.restorative}</p>
    {:else}
      <ReorderList
        items={restorative.shown}
        label="Restorative Arts"
        onreorder={restorative.reorder}
        row={restorativeRow}
      />
    {/if}
  </Panel>
</div>

<style>
  .pair {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: var(--space-5);
    min-height: 0;
  }

  .empty {
    margin: 0;
    padding: var(--space-2) var(--space-4);
    background: var(--card-ink-row-a);
  }
</style>
