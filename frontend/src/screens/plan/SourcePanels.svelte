<script lang="ts">
  import Button from '../../components/Button.svelte';
  import GlyphButton from '../../components/GlyphButton.svelte';
  import Panel from '../../components/Panel.svelte';
  import RowList from '../../components/RowList.svelte';
  import TrialMark from '../../components/TrialMark.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { planning, type Art, type HorizonItem } from '../../lib/api';
  import { view } from '../../lib/view.svelte';

  const horizon = $derived(view.planning?.horizon ?? []);
  const foundational = $derived(view.planning?.foundational ?? []);
  const restorative = $derived(view.planning?.restorative ?? []);

  const summon = (source: 'horizon' | 'art', id: string) =>
    view.act(() => planning.summon(source, id));
</script>

{#snippet horizonRow(item: HorizonItem)}
  <TrialMark trial={{ is_mandate: item.is_mandate, origin_type: 'horizon' }} />
  <span class="title">{item.title}</span>
  <span class="estimate digits">{item.expected_text}</span>
  <Button
    label="Summon"
    tone="horizon"
    description="Summon {item.title}"
    onclick={() => summon('horizon', item.id)}
  />
{/snippet}

{#snippet foundationalRow(art: Art)}
  <TrialMark trial={{ is_mandate: false, origin_type: 'foundational_art' }} />
  <span class="title">{art.title}</span>
  <span class="estimate digits">{art.expected_text}</span>
  <GlyphButton label="Summon {art.title}" onclick={() => summon('art', art.id)}>
    <GlyphIcon name="plus" />
  </GlyphButton>
{/snippet}

{#snippet restorativeRow(art: Art)}
  <TrialMark trial={{ is_mandate: false, origin_type: 'restorative_art' }} />
  <span class="title">{art.title}</span>
  <span class="estimate digits">{art.expected_text}</span>
  <GlyphButton label="Summon {art.title}" onclick={() => summon('art', art.id)}>
    <GlyphIcon name="plus" />
  </GlyphButton>
{/snippet}

<div class="sources">
  <Panel title="The Horizon" tone="horizon" scroll>
    <RowList items={horizon} row={horizonRow} empty="The Horizon is clear." />
  </Panel>
  <div class="pair">
    <Panel title="Foundational Arts" tone="foundational" scroll>
      <RowList items={foundational} row={foundationalRow} empty="No Arts yet." />
    </Panel>
    <Panel title="Restorative Arts" tone="restorative" scroll>
      <RowList items={restorative} row={restorativeRow} empty="No Arts yet." />
    </Panel>
  </div>
</div>

<style>
  .sources {
    display: grid;
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

  .title {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .estimate {
    color: var(--ink-muted);
  }
</style>
