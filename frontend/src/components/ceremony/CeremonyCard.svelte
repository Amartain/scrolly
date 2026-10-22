<!-- The card of the finished-day ceremony, risen out of the golden light: a lacquer tablet framed in
     gold, the scene's seal and title, the day's tally as four tiles, then the day's line and the
     button. The parent says how far the tally has come (`rows`) and when it has settled. -->
<script lang="ts">
  import type { Victory } from '../../lib/api';
  import { SCENES, VICTORY } from '../../lib/copy-victory';
  import Button from '../Button.svelte';
  import TallyCount from '../TallyCount.svelte';

  let {
    victory,
    lifetime,
    rows,
    settled,
    still,
    onclose,
  }: {
    victory: Victory;
    lifetime: number;
    rows: number;
    settled: boolean;
    still: boolean;
    onclose: () => void;
  } = $props();

  const scene = $derived(SCENES[victory.scene]);
  const CORNERS = ['tl', 'tr', 'bl', 'br'];
</script>

<!-- The storm brings its own golden light; without it the card glows by itself. -->
{#if victory.scene !== 'thunder'}<div class="glow" aria-hidden="true"></div>{/if}
<article class="card" class:still>
  {#each CORNERS as corner (corner)}
    <svg class="corner {corner}" viewBox="0 0 48 48" aria-hidden="true">
      <path d="M4,44 V20 A16,16 0 0 1 20,4 H44" />
      <path d="M14,30 a7,7 0 1,1 7,-7 a3.5,3.5 0 1,1 -3.5,3.5" />
    </svg>
  {/each}
  <!-- The pixel font draws its own blocky 日; the reading font leaves the character to the system's CJK face. -->
  <p class="seal read" lang="zh" aria-hidden="true">{scene.seal}</p>
  <h2 class="title display">{scene.title}</h2>
  <p class="lead read">{scene.lead}</p>
  <div class="tiles">
    <TallyCount
      label={VICTORY.labels.conquered}
      value={victory.conquered}
      shown={rows >= 1}
      {settled}
    />
    <TallyCount
      label={VICTORY.labels.mandates}
      value={victory.mandates}
      shown={rows >= 2}
      {settled}
      mandate
    />
    <TallyCount
      label={VICTORY.labels.essence}
      value={victory.essence_text}
      shown={rows >= 3}
      {settled}
    />
    <TallyCount label={VICTORY.labels.lifetime} value={lifetime} shown={rows >= 4} {settled} />
  </div>
  <p class="line read" class:shown={settled}>{victory.line}</p>
  <div class="close" class:shown={settled}>
    <Button label={VICTORY.close} tone="gold" onclick={onclose} />
  </div>
</article>

<style>
  .glow {
    position: absolute;
    inset: 0;
    background: radial-gradient(
      circle at 50% 50%,
      color-mix(in srgb, var(--scene-gold) 38%, transparent),
      transparent 55%
    );
    pointer-events: none;
  }

  .card {
    --lotus-ink: var(--scene-mandate);
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-4);
    width: min(var(--size-ceremony-card), 92vw);
    padding: var(--space-8) var(--space-8) var(--space-6);
    background: radial-gradient(ellipse at 50% 0%, var(--scene-card-raised), var(--scene-card) 70%);
    border: var(--space-1) solid var(--scene-card-line);
    box-shadow:
      inset 0 0 0 var(--space-2) var(--scene-card),
      inset 0 0 0 var(--space-3) var(--scene-card-line),
      var(--space-3) var(--space-3) 0 var(--scene-ink);
    color: var(--scene-card-ink);
    text-align: center;
    animation: card-rise var(--scene-card-rise) ease-out both;
  }

  .card.still {
    animation: none;
  }

  .corner {
    position: absolute;
    width: var(--size-icon-large);
    height: var(--size-icon-large);
    fill: none;
    stroke: var(--scene-card-line);
    stroke-width: 3;
    stroke-linecap: round;
  }

  .tl {
    top: var(--space-4);
    left: var(--space-4);
  }

  .tr {
    top: var(--space-4);
    right: var(--space-4);
    transform: scaleX(-1);
  }

  .bl {
    bottom: var(--space-4);
    left: var(--space-4);
    transform: scaleY(-1);
  }

  .br {
    right: var(--space-4);
    bottom: var(--space-4);
    transform: scale(-1);
  }

  p,
  h2 {
    margin: 0;
  }

  .seal {
    display: grid;
    place-items: center;
    width: 2.2em;
    height: 2.2em;
    background: var(--scene-gold);
    color: var(--scene-ink);
    border: var(--border-width) solid var(--scene-ink);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-xl);
  }

  .title {
    color: var(--scene-card-num);
    font-size: var(--text-display-lg);
    text-shadow: var(--space-1) var(--space-1) 0 var(--scene-card-num-shadow);
  }

  .lead {
    max-width: 30rem;
  }

  .tiles {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3);
    align-self: stretch;
  }

  .line {
    max-width: 32rem;
    color: var(--scene-card-muted);
    font-style: italic;
  }

  .line,
  .close {
    opacity: 0;
    transition: opacity var(--glitch-fade) linear;
  }

  .shown {
    opacity: 1;
  }

  /* Not reachable (by key or by click) until it shows. */
  .close:not(.shown) {
    visibility: hidden;
  }
</style>
