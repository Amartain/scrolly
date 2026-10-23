<!-- Below the Hidden Pavilion (owner, 2026-10-23): "a hidden, secret, magical thing beside the city". A
     small lacquered gate where the path leaves the plain, its plaque 隱 (hidden), and at the bottom right
     the city, its windows lit more as the day goes (by day a few, at dusk most). Colours are the
     scene's tokens (styles/peak-tokens.css). -->
<svelte:options namespace="svg" />

<script lang="ts">
  /** The city stands behind the cliff; the gate in front of the path, `away` once they set off. */
  let { part, away = false }: { part: 'city' | 'gate'; away?: boolean } = $props();

  // Each tower: left edge, top, width. They stand on the plain below the frame's foot.
  const TOWERS = [
    [640, 806, 70],
    [722, 764, 92],
    [826, 796, 62],
    [900, 732, 112],
    [1024, 784, 80],
    [1116, 748, 96],
    [1224, 794, 70],
    [1306, 722, 120],
    [1438, 772, 80],
    [1530, 744, 110],
  ] as const;
  const WINDOW = { width: 10, height: 14, gapX: 12, gapY: 12, inset: 12 };

  const windows = TOWERS.flatMap(([x, top, width], t) => {
    const cols = Math.floor((width - WINDOW.inset) / (WINDOW.width + WINDOW.gapX));
    const rows = Math.floor((900 - top - WINDOW.inset) / (WINDOW.height + WINDOW.gapY));
    return Array.from({ length: cols * rows }, (_, i) => ({
      key: `${t}-${i}`,
      x: x + WINDOW.inset + (i % cols) * (WINDOW.width + WINDOW.gapX),
      y: top + WINDOW.inset + Math.floor(i / cols) * (WINDOW.height + WINDOW.gapY),
      // Not every window at once: a city lit everywhere looks painted, not lived in.
      lit: (i * 7 + t * 3) % 4 !== 0,
    }));
  });
</script>

{#if part === 'city'}
  <g class="city paint-far-3">
    {#each TOWERS as [x, top, width] (x)}
      <rect class="tower" {x} y={top} {width} height={960 - top} />
    {/each}
    {#each windows as w (w.key)}
      <rect
        class="window"
        class:lit={w.lit}
        x={w.x}
        y={w.y}
        width={WINDOW.width}
        height={WINDOW.height}
      />
    {/each}
  </g>
{:else}
  <g class="foot-gate paint-pine" class:away>
    <!-- Tall enough that the cultivator passes under the lintel; the plaque sits on the roof. -->
    <rect class="wood" x="156" y="776" width="12" height="134" />
    <rect class="wood" x="232" y="776" width="12" height="134" />
    <rect class="wood" x="144" y="772" width="112" height="10" />
    <path
      class="wood"
      d="M124,768 Q148,764 158,744 L242,744 Q252,764 276,768 Q248,750 246,734 L154,734 Q152,750 124,768 Z"
    />
    <rect class="gate-plaque" x="187" y="738" width="26" height="26" />
    <text class="gate-word" x="200" y="757">隱</text>
  </g>
{/if}
