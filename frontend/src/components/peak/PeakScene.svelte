<!-- The peak, one per theme: the Serene ink painting or the Pavilion on its cliff. Behind Seclusion it
     fills the room; in the dashboard header it is a window that follows the cultivator. A new visit, or
     another theme, paints the scene in (about 3.5 s); then only mist, clouds and ribbons move. The
     cultivator climbs, sits and walks down as lib/peak.svelte.ts says. -->
<script lang="ts">
  import { peak, type Frame } from '../../lib/peak.svelte';
  import { auraToken } from '../../lib/player-api';
  import { view } from '../../lib/view.svelte';
  import PavilionPeak from './PavilionPeak.svelte';
  import SerenePeak from './SerenePeak.svelte';

  let { frame = 'room' }: { frame?: Frame } = $props();

  /** How long the painting takes, after which the room's cards are fully there. */
  const PAINT_MS = 5000;

  const theme = $derived(view.current?.appearance.theme ?? 'serene');
  // A player's own robe and glow (domain/player.py); without a choice, the theme's own.
  const player = $derived(view.current?.player);
  const robe = $derived(player?.is_player && player.robe ? auraToken(player.robe) : undefined);
  const glow = $derived(player?.is_player && player.glow ? auraToken(player.glow) : undefined);
  const shining = $derived(!!(player?.is_player && player.glow_on));

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
  data-enlightened={view.current?.knowledge.enlightened ?? false}
  data-robe={robe ? 'own' : undefined}
  data-glow={glow ? 'own' : undefined}
  data-shining={shining}
  style:--robe={robe}
  style:--glow={glow}
  aria-hidden="true"
>
  {#key theme}
    {#if theme === 'pavilion'}<PavilionPeak {frame} />{:else}<SerenePeak {frame} />{/if}
  {/key}
</div>
