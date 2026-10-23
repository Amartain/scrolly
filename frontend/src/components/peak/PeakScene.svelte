<!-- The peak, one per theme: the Serene ink painting or the Pavilion on its cliff. Behind Seclusion it
     fills the room; in the dashboard header it is a window that follows the cultivator. A new visit, or
     another theme, paints the scene in (about 3.5 s); then only mist, clouds and ribbons move. The
     cultivator climbs, sits and walks down as lib/peak.svelte.ts says. -->
<script lang="ts">
  import { peak, type Frame } from '../../lib/peak.svelte';
  import { view } from '../../lib/view.svelte';
  import PavilionPeak from './PavilionPeak.svelte';
  import SerenePeak from './SerenePeak.svelte';

  let { frame = 'room' }: { frame?: Frame } = $props();

  /** How long the painting takes, after which the room's cards are fully there. */
  const PAINT_MS = 5000;

  const theme = $derived(view.current?.appearance.theme ?? 'serene');

  let shown = '';
  $effect(() => {
    if (shown && shown !== theme) peak.repaint();
    shown = theme;
  });

  $effect(() => {
    if (!peak.arriving) return;
    const id = setTimeout(peak.skip, PAINT_MS);
    return () => clearTimeout(id);
  });
</script>

<div
  class="peak"
  class:painting={peak.painting}
  class:rising={peak.rising}
  data-scene={theme}
  data-frame={frame}
  data-stage={peak.stage}
  aria-hidden="true"
>
  {#key theme}
    {#if theme === 'pavilion'}<PavilionPeak {frame} />{:else}<SerenePeak {frame} />{/if}
  {/key}
</div>
