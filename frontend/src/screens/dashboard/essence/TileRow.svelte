<!-- One row of the Essence panel: the day's trials as tiles, sized by Python. The plan is a pale ink wash,
     the trial at hand is outlined in gold, a conquered trial is inked solid. Qi's zones lie faintly
     behind its tiles. Pointing at a tile puts that trial's numbers in the reading; nothing floats. -->
<script lang="ts">
  import type { components } from '../../../lib/api-types';

  type Tile = components['schemas']['TileOut'];

  let {
    label,
    tiles,
    reading,
    describe,
    tone = 'essence',
    bands,
  }: {
    label: string;
    tiles: Tile[];
    reading: string;
    describe: (tile: Tile) => string;
    tone?: 'essence' | 'qi';
    /** Qi only: where Harmonious and Igniting the Blood end, as % of the row. */
    bands?: { harmonious: number; igniting: number };
  } = $props();

  let pointed = $state<Tile | null>(null);
  const valueText = $derived(`${reading}. ${tiles.map(describe).join('; ')}`);
  // How much of the row is inked: the done tiles' shares.
  const inked = $derived(
    Math.round(tiles.filter((t) => t.state === 'done').reduce((sum, t) => sum + t.share_pct, 0)),
  );
</script>

<div class="row" data-tone={tone}>
  <span class="label display">{label}</span>
  <div
    class="track"
    role="meter"
    aria-label={label}
    aria-valuemin={0}
    aria-valuemax={100}
    aria-valuenow={inked}
    aria-valuetext={valueText}
  >
    {#if bands}
      <span class="band harmonious" style:width="{bands.harmonious}%"></span>
      <span
        class="band igniting"
        style:left="{bands.harmonious}%"
        style:width="{bands.igniting - bands.harmonious}%"
      ></span>
      <span class="band strain" style:left="{bands.igniting}%"></span>
    {/if}
    {#each tiles as tile, i (i)}
      <!-- svelte-ignore a11y_no_static_element_interactions (pointing only shows numbers the meter already reads out) -->
      <span
        class="tile {tile.state}"
        style:flex-basis="{tile.share_pct}%"
        onpointerenter={() => (pointed = tile)}
        onpointerleave={() => (pointed = null)}
      ></span>
    {/each}
  </div>
  <span class="reading digits">{pointed ? describe(pointed) : reading}</span>
</div>

<style>
  .row {
    --ink-fill: var(--gold);
    display: grid;
    grid-template-columns: var(--size-tile-label) minmax(0, 1fr) var(--size-tile-reading);
    align-items: center;
    gap: var(--space-3);
    /* Two rows share a short panel: the text sits on the tile row's own height. */
    line-height: 1;
  }

  .row[data-tone='qi'] {
    --ink-fill: var(--qi-calm);
  }

  .label {
    font-size: var(--text-display-sm);
  }

  .track {
    position: relative;
    display: flex;
    gap: var(--border-width);
    height: var(--size-tile);
    overflow: hidden;
    background: var(--inset);
    border: var(--border-width) solid var(--line);
  }

  .band {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    opacity: 0.18;
  }

  .harmonious {
    background: var(--qi-calm);
  }

  .igniting {
    background: var(--qi-surge);
  }

  .strain {
    right: 0;
    background: var(--qi-redline);
  }

  .tile {
    position: relative;
    flex: 0 1 auto;
    min-width: var(--border-width);
  }

  /* The plan: a pale wash with a faint brush hatch. */
  .waiting,
  .now {
    background:
      repeating-linear-gradient(
        135deg,
        transparent 0 var(--space-1),
        color-mix(in srgb, var(--ink-fill) 22%, transparent) var(--space-1) var(--space-2)
      ),
      color-mix(in srgb, var(--ink-fill) 24%, transparent);
  }

  .now {
    outline: var(--border-width) solid var(--gold);
    outline-offset: calc(-1 * var(--border-width));
  }

  /* What is done: solid ink. */
  .done {
    background: var(--ink-fill);
    background-image: var(--gloss);
  }

  .reading {
    overflow: hidden;
    color: var(--num-text);
    font-size: var(--text-body-sm);
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
