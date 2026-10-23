<!-- The cultivator on the scene's path: at its foot, climbing while a timer runs (the climb halts with
     it), seated at its top, or walking back down (lib/peak.svelte.ts). `path` is the way up, ending at
     the seat. Where they stand is read off the path itself, so each scene only draws its own way; `at`
     hands it back to the scene, whose header window follows them. -->
<script lang="ts">
  import { peak } from '../../lib/peak.svelte';
  import PeakFigure from './PeakFigure.svelte';

  let {
    path,
    scale = 1,
    sitScale = scale,
    at = $bindable(),
  }: { path: string; scale?: number; sitScale?: number; at?: DOMPoint } = $props();

  let guide: SVGPathElement | undefined = $state();
  // Sitting down after the climb fades the seated figure in; arriving to find them seated does not.
  let climbed = $state(false);

  $effect(() => {
    if (guide) at = guide.getPointAtLength(peak.progress * guide.getTotalLength());
  });

  const moving = $derived(
    (peak.stage === 'climbing' && peak.running) || peak.stage === 'descending',
  );

  $effect(() => {
    if (peak.stage === 'climbing') climbed = true;
  });

  $effect(() => {
    if (!moving) return;
    let last = performance.now();
    let frame = requestAnimationFrame(function step(now) {
      peak.advance(now - last);
      last = now;
      frame = requestAnimationFrame(step);
    });
    return () => cancelAnimationFrame(frame);
  });

  // Walking down, they face the way they go.
  const facing = $derived(peak.stage === 'descending' ? -1 : 1);
</script>

<path bind:this={guide} class="guide" d={path} />
{#if at}
  <g class="climber" transform="translate({at.x} {at.y})">
    {#if peak.stage === 'seated'}
      <g class:sit-in={climbed} transform="scale({sitScale})"><PeakFigure pose="sit" /></g>
    {:else}
      <g transform="scale({scale * facing} {scale})">
        <g class:bob={moving}><PeakFigure pose="walk" /></g>
      </g>
    {/if}
  </g>
{/if}
