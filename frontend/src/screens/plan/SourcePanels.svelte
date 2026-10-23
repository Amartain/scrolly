<script lang="ts">
  import Panel from '../../components/Panel.svelte';
  import RowList from '../../components/RowList.svelte';
  import { planning, type Art, type HorizonItem } from '../../lib/api';
  import { EMPTY } from '../../lib/copy';
  import { view } from '../../lib/view.svelte';
  import ArtRow from './ArtRow.svelte';
  import HorizonRow from './HorizonRow.svelte';

  const horizon = $derived(view.planning?.horizon ?? []);
  const foundational = $derived(view.planning?.foundational ?? []);
  const restorative = $derived(view.planning?.restorative ?? []);

  const summon = (source: 'horizon' | 'art', id: string) =>
    view.act(() => planning.summon(source, id));
</script>

{#snippet horizonRow(item: HorizonItem)}
  <HorizonRow {item} onsummon={() => summon('horizon', item.id)} />
{/snippet}

{#snippet foundationalRow(art: Art)}
  <ArtRow {art} kind="foundational" onsummon={() => summon('art', art.id)} />
{/snippet}

{#snippet restorativeRow(art: Art)}
  <ArtRow {art} kind="restorative" onsummon={() => summon('art', art.id)} />
{/snippet}

<!-- Only what holds something is shown (owner, 2026-10-23): an empty list does not clutter planning. -->
<div class="sources">
  {#if horizon.length > 0}
    <Panel title="The Horizon" tone="horizon" scroll striped>
      <RowList items={horizon} row={horizonRow} empty={EMPTY.horizon} />
    </Panel>
  {/if}
  {#if foundational.length > 0 || restorative.length > 0}
    <div class="pair">
      {#if foundational.length > 0}
        <Panel title="Foundational Arts" tone="foundational" scroll striped>
          <RowList items={foundational} row={foundationalRow} empty={EMPTY.foundational} />
        </Panel>
      {/if}
      {#if restorative.length > 0}
        <Panel title="Restorative Arts" tone="restorative" scroll striped>
          <RowList items={restorative} row={restorativeRow} empty={EMPTY.restorative} />
        </Panel>
      {/if}
    </div>
  {/if}
</div>

<style>
  /* The Horizon takes three parts of the height, the Arts two; whichever is alone takes it all. */
  .sources {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    min-height: 0;
    padding-right: var(--shadow-room);
    padding-bottom: var(--shadow-room);
  }

  .sources > :global(:first-child) {
    flex: 3 1 0;
    min-height: 0;
  }

  .pair {
    flex: 2 1 0;
    display: grid;
    grid-auto-flow: column;
    grid-auto-columns: minmax(0, 1fr);
    gap: var(--space-5);
    min-height: 0;
  }
</style>
