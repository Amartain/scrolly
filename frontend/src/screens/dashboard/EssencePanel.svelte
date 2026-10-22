<!-- Essence over Qi, two slim rows of ink on wash: the whole day's plan in a pale wash, what is done in
     solid ink. The Qi row shows only with the Golden Core on. Before anything is estimated or spent
     (Python says so), the Essence row is one quiet line. -->
<script lang="ts">
  import GuidanceButton from '../../components/GuidanceButton.svelte';
  import Panel from '../../components/Panel.svelte';
  import type { components } from '../../lib/api-types';
  import { DASHBOARD } from '../../lib/copy-dashboard';
  import { QI_ZONE } from '../../lib/copy-qi';
  import { view } from '../../lib/view.svelte';
  import TileRow from './essence/TileRow.svelte';

  type Tile = components['schemas']['TileOut'];

  const dashboard = $derived(view.current?.dashboard);
  const essence = $derived(dashboard?.essence);
  const qi = $derived(view.planning?.qi);

  const describeTime = (tile: Tile) => DASHBOARD.tile(tile.title, tile.taken, tile.planned);
  const qiText = (value: string | null) => (value === null ? null : `${value} Qi`);
  const describeQi = (tile: Tile) =>
    DASHBOARD.tile(tile.title, qiText(tile.taken), qiText(tile.planned));
</script>

<Panel title="Essence" bare>
  <div class="rows" class:single={!qi?.enabled}>
    <span class="guide"><GuidanceButton topic="essence" /></span>
    {#if essence?.blank}
      <p class="hint">{DASHBOARD.essenceBlank}</p>
    {:else if essence && dashboard}
      <TileRow
        label={DASHBOARD.essence}
        tiles={dashboard.essence_tiles}
        reading={DASHBOARD.of(essence.actual_text, essence.expected_text)}
        describe={describeTime}
      />
    {/if}
    {#if qi?.enabled}
      <TileRow
        label={DASHBOARD.qi}
        tone="qi"
        tiles={qi.tiles}
        reading="{DASHBOARD.of(String(qi.spent), String(qi.planned))} · {QI_ZONE[qi.spent_zone]}"
        describe={describeQi}
        bands={{ harmonious: qi.harmonious_pct, igniting: qi.igniting_pct }}
      />
    {/if}
  </div>
</Panel>

<style>
  .rows {
    position: relative;
    display: grid;
    align-content: center;
    gap: var(--space-3);
    height: 100%;
    padding: var(--space-2) var(--space-12) var(--space-2) var(--space-4);
  }

  .guide {
    position: absolute;
    top: 50%;
    right: var(--space-4);
    translate: 0 -50%;
  }

  .single {
    --size-tile: var(--size-tile-tall);
  }

  .hint {
    margin: 0;
    color: var(--ink-muted);
  }
</style>
