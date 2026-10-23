<!-- The morning scene behind the zero state, one per theme: the Serene ink painting or the Pavilion city at
     dawn. `still` shows the last frame without moving (reduced motion, or a key or click to skip).
     Another theme is painted in from the start. -->
<script lang="ts">
  import { view } from '../../lib/view.svelte';
  import PavilionMorning from './PavilionMorning.svelte';
  import SereneMorning from './SereneMorning.svelte';

  let { still }: { still: boolean } = $props();

  const theme = $derived(view.current?.appearance.theme ?? 'serene');
</script>

<div class="morning" class:still data-scene={theme}>
  {#key theme}
    {#if theme === 'pavilion'}<PavilionMorning />{:else}<SereneMorning />{/if}
  {/key}
</div>

<style>
  .morning {
    position: absolute;
    inset: 0;
    overflow: hidden;
    background: var(--surface-canvas);
  }
</style>
