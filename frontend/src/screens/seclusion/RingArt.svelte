<!-- The drawing of the ring: track, outline, hard shadow, and the arc with round ends and a sheen.
     Shapes are in a 100-unit box, so they scale with the ring. `fill` is how much of the ring is coloured. -->
<script lang="ts">
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
</script>

<svg class="art" viewBox="0 0 100 100" aria-hidden="true">
  <circle class="shadow" cx={50 + SHADOW} cy={50 + SHADOW} r={R} stroke-width={BAND + EDGE * 2} />
  <circle class="edge" cx="50" cy="50" r={R} stroke-width={BAND + EDGE * 2} />
  <circle class="track" cx="50" cy="50" r={R} stroke-width={BAND} />
  <circle class="well" cx="50" cy="50" r={R - BAND / 2} stroke-width={EDGE} />
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
          stroke-dasharray="{fill} 100"
        />
      {/each}
    </g>
  {/if}
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

  .shadow {
    stroke: var(--shadow);
  }

  .edge {
    stroke: var(--line);
  }

  .track {
    stroke: var(--inset);
  }

  .well {
    fill: var(--surface-raised);
    stroke: var(--line);
  }

  .fill {
    stroke: var(--ring-fill);
  }

  .shine {
    stroke: var(--icon-highlight);
  }
</style>
