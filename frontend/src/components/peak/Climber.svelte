<!-- The cultivator on the scene's path: at its foot until the first Start, climbing while the timer
     runs (the climb halts with it), seated at its top after. `path` is the way up, ending at the seat.
     Where they stand is read off the path itself, so each scene only draws its own way. -->
<script lang="ts">
  import { peak } from '../../lib/peak.svelte';
  import { seclusion } from '../../lib/seclusion.svelte';
  import PeakFigure from './PeakFigure.svelte';

  let {
    path,
    scale = 1,
    sitScale = scale,
  }: { path: string; scale?: number; sitScale?: number } = $props();

  let guide: SVGPathElement | undefined = $state();
  // Sitting down after the climb fades the seated figure in; arriving to find them seated does not.
  let climbed = $state(false);

  const at = $derived.by(() => {
    if (!guide) return null;
    return guide.getPointAtLength(peak.progress * guide.getTotalLength());
  });
  const climbing = $derived(peak.stage === 'climbing');

  $effect(() => {
    if (climbing) climbed = true;
  });

  $effect(() => {
    if (!climbing || !seclusion.running) return;
    let last = performance.now();
    let frame = requestAnimationFrame(function step(now) {
      peak.advance(now - last);
      last = now;
      frame = requestAnimationFrame(step);
    });
    return () => cancelAnimationFrame(frame);
  });
</script>

<path bind:this={guide} class="guide" d={path} />
{#if at}
  <g
    class="climber"
    transform="translate({at.x} {at.y}) scale({peak.stage === 'seated' ? sitScale : scale})"
  >
    {#if peak.stage === 'seated'}
      <g class:sit-in={climbed}><PeakFigure pose="sit" /></g>
    {:else}
      <g class:bob={climbing && seclusion.running}><PeakFigure pose="walk" /></g>
    {/if}
  </g>
{/if}
