<!-- The ring every tab shares: the drawing, and the middle where its words go. `tone` is the colour of
     the tab and of its state (a break and an overfilled ring are other shades of the same hue). -->
<script module lang="ts">
  export type Tone = 'incense' | 'over' | 'cycles' | 'cycles-break' | 'flow' | 'flow-break';
</script>

<script lang="ts">
  import type { Snippet } from 'svelte';
  import RingArt from './RingArt.svelte';

  let {
    fill,
    tone,
    label,
    role = 'timer',
    children,
  }: { fill: number; tone: Tone; label: string; role?: string; children: Snippet } = $props();
</script>

<div
  class="ring"
  style:--fill={fill}
  data-tone={tone}
  data-over={tone === 'over' || undefined}
  {role}
  aria-label={label}
>
  <RingArt {fill} />
  <div class="inner">{@render children()}</div>
</div>

<style>
  .ring {
    --ring-fill: var(--gold);
    position: relative;
    flex: none;
    display: grid;
    place-items: center;
    width: var(--size-ring);
    aspect-ratio: 1;
  }

  .ring[data-tone='over'] {
    --ring-fill: var(--ring-over);
  }

  .ring[data-tone='cycles'] {
    --ring-fill: var(--cycles);
  }

  .ring[data-tone='cycles-break'] {
    --ring-fill: var(--cycles-break);
  }

  .ring[data-tone='flow'] {
    --ring-fill: var(--flow);
  }

  .ring[data-tone='flow-break'] {
    --ring-fill: var(--flow-break);
  }

  .inner {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-1);
    width: 70%;
    padding: var(--space-2);
    text-align: center;
  }

  .inner :global(p) {
    margin: 0;
  }

  .inner :global(.big) {
    color: var(--num);
    font-size: var(--text-numeral-ring);
    line-height: 1;
    text-shadow: var(--space-1) var(--space-1) 0 var(--num-shadow);
    text-transform: none;
    white-space: nowrap;
  }

  .inner :global(.word) {
    font-size: var(--text-display-md);
  }

  .inner :global(.ask) {
    max-width: 14rem;
    font-size: var(--text-display-sm);
  }

  .inner :global(.small) {
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }

  .inner :global(.state) {
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
  }

  .inner :global(.hidden) {
    visibility: hidden;
  }
</style>
