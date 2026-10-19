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

<div class="sources">
  <Panel title="The Horizon" tone="horizon" scroll striped>
    <RowList items={horizon} row={horizonRow} empty={EMPTY.horizon} />
  </Panel>
  <div class="pair">
    <Panel title="Foundational Arts" tone="foundational" scroll striped>
      <RowList items={foundational} row={foundationalRow} empty={EMPTY.foundational} />
    </Panel>
    <Panel title="Restorative Arts" tone="restorative" scroll striped>
      <RowList items={restorative} row={restorativeRow} empty={EMPTY.restorative} />
    </Panel>
  </div>
</div>

<style>
  .sources {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    grid-template-rows: minmax(0, 3fr) minmax(0, 2fr);
    gap: var(--space-4);
    min-height: 0;
    padding-right: var(--shadow-room);
    padding-bottom: var(--shadow-room);
  }

  .pair {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: var(--space-5);
    min-height: 0;
  }
</style>
