<script lang="ts">
  import GlyphButton from '../../components/GlyphButton.svelte';
  import Panel from '../../components/Panel.svelte';
  import ReorderList from '../../components/ReorderList.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { horizon, today, type Art, type ArtKind } from '../../lib/api';
  import { EMPTY } from '../../lib/copy';
  import { useOrder } from '../../lib/order.svelte';
  import { view } from '../../lib/view.svelte';
  import ArtRow from '../plan/ArtRow.svelte';
  import ArtsExpand from './ArtsExpand.svelte';

  const foundational = useOrder(
    () => view.planning?.foundational ?? [],
    (ids) => horizon.reorderArts('foundational', ids),
  );
  const restorative = useOrder(
    () => view.planning?.restorative ?? [],
    (ids) => horizon.reorderArts('restorative', ids),
  );

  const summon = (id: string) => view.act(() => today.summon('art', id));
  let expanded = $state<ArtKind | null>(null);
</script>

{#snippet foundationalRow(art: Art)}
  <ArtRow {art} kind="foundational" onsummon={() => summon(art.id)} />
{/snippet}

{#snippet restorativeRow(art: Art)}
  <ArtRow {art} kind="restorative" onsummon={() => summon(art.id)} />
{/snippet}

<div class="pair">
  <Panel title="Foundational Arts" tone="foundational" guide="foundational" scroll striped>
    {#snippet actions()}
      <GlyphButton label="Add a Foundational Art" onclick={() => (expanded = 'foundational')}>
        <GlyphIcon name="plus" />
      </GlyphButton>
    {/snippet}
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
  <Panel title="Restorative Arts" tone="restorative" guide="restorative" scroll striped>
    {#snippet actions()}
      <GlyphButton label="Add a Restorative Art" onclick={() => (expanded = 'restorative')}>
        <GlyphIcon name="plus" />
      </GlyphButton>
    {/snippet}
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

{#if expanded}
  <ArtsExpand kind={expanded} onclose={() => (expanded = null)} />
{/if}

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
