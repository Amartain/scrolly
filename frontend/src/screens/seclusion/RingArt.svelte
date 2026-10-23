<!-- The drawing of the ring: a soft band with a soft offset shadow, the arc on an ink edge with round ends
     and a sheen, and a companion walking at the arc's head (a crane in Serene, a lantern in Pavilion).
     Shapes are in a 100-unit box, so they scale with the ring. `fill` is how much of the ring is coloured. -->
<script lang="ts">
  import { view } from '../../lib/view.svelte';

  let { fill }: { fill: number } = $props();

  const R = 45;
  const BAND = 7;
  const EDGE = 0.6;
  const SHADOW = 1.2;

  // Outline, colour and sheen share one arc, each a little different in width and radius.
  const PARTS = [
    { cls: 'edge', r: R, w: BAND + EDGE * 2 },
    { cls: 'fill', r: R, w: BAND },
    { cls: 'shine', r: R - BAND * 0.2, w: BAND * 0.22 },
  ];

  // A round end reaches half the stroke past the dash, on both ends. Drawn as is, a full ring that
  // has begun to drain still looks closed until the two ends part (52 s of a 30m trial). So the dash
  // is shortened by the widest end, and starts that far in: the arc shows exactly `fill`.
  const CAP = ((BAND + EDGE * 2) / 2 / (2 * Math.PI * R)) * 100;
  const dash = $derived(fill >= 100 ? 'none' : `${Math.max(fill - 2 * CAP, 0.01)} 100`);
  const offset = $derived(fill >= 100 ? 0 : -CAP);

  // The companion stands where the arc ends, or at the top when the ring is whole or empty.
  const turn = $derived(fill > 0 && fill < 100 ? (fill / 100) * 2 * Math.PI : 0);
  const headX = $derived(50 + R * Math.sin(turn));
  const headY = $derived(50 - R * Math.cos(turn));
  const lantern = $derived(view.current?.appearance.theme === 'pavilion');
</script>

<svg class="art" viewBox="0 0 100 100" aria-hidden="true">
  <circle class="shadow" cx={50 + SHADOW} cy={50 + SHADOW} r={R} stroke-width={BAND} />
  <circle class="track" cx="50" cy="50" r={R} stroke-width={BAND} />
  <circle class="well" cx="50" cy="50" r={R - BAND / 2} />
  {#if fill > 0}
    <g transform="rotate(-90 50 50)" stroke-linecap="round">
      {#each PARTS as part (part.cls)}
        <circle
          class={part.cls}
          cx="50"
          cy="50"
          r={part.r}
          stroke-width={part.w}
          pathLength="100"
          stroke-dasharray={dash}
          stroke-dashoffset={offset}
        />
      {/each}
    </g>
  {/if}
  <g class="companion" transform="translate({headX} {headY}) scale(0.34)">
    <circle class="glow" r="18" />
    {#if lantern}
      <path class="lantern-line" d="M0,-14 L0,-10 M-4,-10 L4,-10 M-4,11 L4,11" />
      <rect class="lantern" x="-8" y="-10" width="16" height="21" rx="6" />
    {:else}
      <path class="crane" d="M-17,2 Q-8,-11 0,-1 Q8,-11 17,2 Q8,-3 0,4 Q-8,-3 -17,2 Z" />
      <circle class="crest" cy="-1" r="2.6" />
    {/if}
  </g>
</svg>

<style>
  .art {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    fill: none;
    overflow: visible;
  }

  /* A soft band on the frosted card, its shadow still a hard offset, only fainter. */
  .shadow {
    stroke: color-mix(in srgb, var(--line) 22%, transparent);
  }

  .track {
    stroke: color-mix(in srgb, var(--ink) 14%, transparent);
  }

  /* On a break the well fills with a shade of the ring's hue (`--ring-disc`, set by RingFrame). */
  .well {
    fill: var(--ring-disc, transparent);
  }

  .edge {
    stroke: var(--line);
  }

  .fill {
    stroke: var(--ring-fill);
  }

  .shine {
    stroke: var(--icon-highlight);
  }

  .glow {
    fill: var(--ring-fill);
    opacity: 0.35;
  }

  .crane {
    fill: var(--ink);
    stroke: var(--surface-panel);
    stroke-width: 1.5;
  }

  .crest {
    fill: var(--morning-seal);
  }

  .lantern {
    fill: var(--peak-lantern);
    stroke: var(--peak-outline);
    stroke-width: 2.5;
  }

  .lantern-line {
    stroke: var(--peak-outline);
    stroke-width: 2.5;
  }
</style>
