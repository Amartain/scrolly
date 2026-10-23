<!-- The ring every tab shares: the drawing, and the middle where its words go. `tone` is the colour of
     the tab and of its state (a break and an overfilled ring are other shades of the same hue). -->
<script module lang="ts">
  export type Tone = 'incense' | 'over' | 'cycles' | 'cycles-break' | 'flow' | 'flow-break';
</script>

<script lang="ts">
  import type { Snippet } from 'svelte';
  import { seclusion } from '../../lib/seclusion.svelte';
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
  class:breathing={seclusion.running}
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

  /* A break fills the well with a shade of the hue; its words turn plain light ink. */
  .ring[data-tone='cycles-break'] {
    --ring-fill: var(--cycles-break);
    --ring-disc: var(--cycles-break-disc);
    --ring-words: var(--on-break-disc);
  }

  .ring[data-tone='flow'] {
    --ring-fill: var(--flow);
  }

  .ring[data-tone='flow-break'] {
    --ring-fill: var(--flow-break);
    --ring-disc: var(--flow-break-disc);
    --ring-words: var(--on-break-disc);
  }

  /* While the timer runs the ring breathes: a glow of its own colour swells and fades every 6 s
     (art-direction › Motion, exception). Opacity only; still when paused and under reduced motion. */
  .ring::before {
    content: '';
    position: absolute;
    inset: calc(-1 * var(--space-4));
    border-radius: 50%;
    background: radial-gradient(
      circle,
      transparent 58%,
      color-mix(in srgb, var(--ring-fill) 40%, transparent) 68%,
      transparent 74%
    );
    opacity: 0;
    pointer-events: none;
  }

  @media (prefers-reduced-motion: no-preference) {
    .ring.breathing::before {
      animation: ring-breathe 6s ease-in-out infinite;
    }
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
    color: var(--ring-words, inherit);
    text-align: center;
  }

  .inner :global(p) {
    margin: 0;
  }

  /* The numerals are ink, so they read on the frosted card; the colour lives on the arc (phase 9). */
  .inner :global(.big) {
    color: var(--ring-words, var(--ink));
    font-size: var(--text-numeral-ring);
    line-height: 1;
    text-shadow: var(--space-1) var(--space-1) 0 color-mix(in srgb, var(--line) 25%, transparent);
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
    color: var(--ring-words, var(--ink-muted));
    font-size: var(--text-body-sm);
  }

  .inner :global(.state) {
    color: var(--ring-words, var(--ink-muted));
    font-size: var(--text-display-sm);
  }

  .inner :global(.hidden) {
    visibility: hidden;
  }
</style>
