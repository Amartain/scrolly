<!-- The peak behind Seclusion, one per theme: the Serene ink painting or the Pavilion on its cliff. A new
     visit, or another theme, paints the scene in (about 3.5 s); then only mist, clouds and ribbons move.
     The cultivator climbs and sits as lib/peak.svelte.ts says. -->
<script lang="ts">
  import { peak } from '../../lib/peak.svelte';
  import { view } from '../../lib/view.svelte';
  import PavilionPeak from './PavilionPeak.svelte';
  import SerenePeak from './SerenePeak.svelte';

  /** How long the painting takes, after which the room's cards are fully there. */
  const PAINT_MS = 4500;

  const theme = $derived(view.current?.appearance.theme ?? 'serene');

  let shown = '';
  $effect(() => {
    if (shown && shown !== theme) peak.repaint();
    shown = theme;
  });

  $effect(() => {
    if (!peak.painting) return;
    const id = setTimeout(peak.skip, PAINT_MS);
    return () => clearTimeout(id);
  });
</script>

<div class="peak" class:painting={peak.painting} data-scene={theme} aria-hidden="true">
  {#key theme}
    {#if theme === 'pavilion'}<PavilionPeak />{:else}<SerenePeak />{/if}
  {/key}
</div>
