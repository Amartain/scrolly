<!-- The morning scene behind the zero state, one per theme: the Serene ink painting or the Pavilion city at
     dawn. `still` shows the last frame without moving (reduced motion, or a key or click to skip).
     `backdrop` lays it very faint behind Seclusion, without its seal and verse, only the mist drifting. -->
<script lang="ts">
  import { view } from '../../lib/view.svelte';
  import PavilionMorning from './PavilionMorning.svelte';
  import SereneMorning from './SereneMorning.svelte';

  let { still, backdrop = false }: { still: boolean; backdrop?: boolean } = $props();

  const theme = $derived(view.current?.appearance.theme ?? 'serene');
</script>

<div
  class="morning"
  class:still
  class:backdrop
  data-scene={theme}
  aria-hidden={backdrop || undefined}
>
  {#if theme === 'pavilion'}<PavilionMorning />{:else}<SereneMorning />{/if}
</div>

<style>
  .morning {
    position: absolute;
    inset: 0;
    overflow: hidden;
    background: var(--surface-canvas);
  }

  .backdrop {
    z-index: -1;
    background: none;
    opacity: var(--seclusion-scene-opacity);
    pointer-events: none;
  }
</style>
